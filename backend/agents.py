from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from google.generativeai import GenerativeModel
import google.generativeai as genai
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from urllib.parse import unquote
from shared_utils import get_embeddings
from agents_intelligence import get_industry_benchmarks, get_competitive_research

router = APIRouter()

# Persistent storage path
VECTOR_DB_DIR = os.getenv("CHROMA_DB_PATH") or (
    "/mnt/data/chroma_db" if os.path.exists("/mnt/data") else "./chroma_db"
)
ANALYSIS_CACHE_DIR = os.getenv("ANALYSIS_CACHE_PATH") or (
    "/mnt/data/analyses" if os.path.exists("/mnt/data") else "./analyses"
)
os.makedirs(ANALYSIS_CACHE_DIR, exist_ok=True)

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

class AnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str  # company, market, financial, risk
    force_rerun: Optional[bool] = False

class Citation(BaseModel):
    text: str
    explanation: str

class CompanyAnalysis(BaseModel):
    reasoning: str
    overview: str = "No overview available."
    founding_year: Optional[str] = "N/A"
    headquarters: Optional[str] = "N/A"
    key_management: List[dict] = []
    founders_background: Optional[List[dict]] = []
    products: List[dict] = []
    business_model: str = "TBD"
    citations: List[Citation] = []

class MarketAnalysis(BaseModel):
    reasoning: str
    tam: Optional[str] = "N/A"
    sam: Optional[str] = "N/A"
    som: Optional[str] = "N/A"
    cagr: Optional[str] = "N/A"
    competitors: List[dict] = []
    market_drivers: List[str] = []
    citations: List[Citation] = []

class FinancialAnalysis(BaseModel):
    reasoning: str
    revenue_data: List[dict] = []
    ebitda_margins: Optional[str] = "N/A"
    valuation: Optional[str] = "N/A"
    monthly_burn_rate: Optional[str] = "N/A"
    runway_months: Optional[str] = "N/A"
    unit_economics: Optional[List[dict]] = []
    key_metrics: List[dict] = []
    verification_notes: str = "Verification in progress."
    citations: List[Citation] = []

class RiskAnalysis(BaseModel):
    reasoning: str
    risks: List[dict] = []
    overall_risk_score: str = "Medium"
    citations: List[Citation] = []

@router.post("/analyze")
async def analyze_document(request: AnalysisRequest):
    try:
        document_id = unquote(request.document_id)
        cache_filename = f"{document_id.replace(' ', '_').replace('/', '_')}_{request.analysis_type}.json"
        cache_path = os.path.join(ANALYSIS_CACHE_DIR, cache_filename)

        # 1. Check Cache
        if not request.force_rerun and os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                    print(f"DEBUG: Returning cached analysis for {document_id}")
                    return {"analysis": cached_data, "cached": True}
            except Exception as e:
                print(f"DEBUG: Cache read failed: {e}")

        # 2. Extract Context (Pass 1)
        k_value = 10
        try:
            vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=get_embeddings())
            results = vectordb.similarity_search(
                query=f"Detailed information about {request.analysis_type}",
                k=k_value,
                filter={"source": document_id}
            )
        except Exception as e:
            print(f"DEBUG: Search failed: {e}")
            results = []

        context = "\n\n".join([doc.page_content for doc in results])
        if not context:
            results = vectordb.similarity_search(f"Detailed information about {request.analysis_type}", k=10)
            context = "\n\n".join([doc.page_content for doc in results])
            
        if not context:
            raise HTTPException(status_code=404, detail="No document context found for analysis.")

        # Shared prompt parts
        generation_config = {"response_mime_type": "application/json"}
        system_instruction = """
        You are 'PitchIQ', an elite Investment Analyst at a Tier-1 Venture Capital and Private Equity firm. 
        Your task is to analyze documents with extreme precision, identifying deep insights that a junior analyst might miss.
        
        GUIDELINES:
        1. Always start your response by populating the 'reasoning' field with your step-by-step logical approach.
        2. Be concise but data-driven. Use specific numbers, dates, and names found in the document.
        3. If data is missing, don't hallucinate. Instead, use the 'reasoning' field to explain it's missing and provide a conservative estimate in the result fields while citing it as an AI-based estimate.
        4. Focus on 'Quality over Quantity' for lists like products and management.
        5. Citations must include EXACT quotes and explain WHY that quote supports the data point.
        """

        def perform_analysis(analysis_context, attempt_num=1):
            if request.analysis_type == "company":
                current_schema = CompanyAnalysis
                prompt = f"{system_instruction}\n\nTASK: Analyze COMPANY OVERVIEW, TEAM, and PRODUCTS.\nCONTEXT: {analysis_context}\nReturn JSON matching CompanyAnalysis schema."
            elif request.analysis_type == "market":
                current_schema = MarketAnalysis
                prompt = f"{system_instruction}\n\nTASK: Analyze MARKET SIZE (TAM/SAM/SOM), CAGR, and COMPETITION.\nCONTEXT: {analysis_context}\nReturn JSON matching MarketAnalysis schema."
            elif request.analysis_type == "financial":
                current_schema = FinancialAnalysis
                prompt = f"{system_instruction}\n\nTASK: Extract FINANCIAL PERFORMANCE and VALUATION.\nCONTEXT: {analysis_context}\nReturn JSON matching FinancialAnalysis schema."
            elif request.analysis_type == "risk":
                current_schema = RiskAnalysis
                prompt = f"{system_instruction}\n\nTASK: Identify KEY RISKS and MITIGANTS.\nCONTEXT: {analysis_context}\nReturn JSON matching RiskAnalysis schema."
            else:
                raise HTTPException(status_code=400, detail="Invalid analysis type")

            response = model.generate_content(prompt, generation_config=generation_config)
            if not response.candidates:
                raise Exception("No AI candidates returned")
            
            json_text = response.text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            raw_data = json.loads(json_text)
            if isinstance(raw_data, dict):
                if "analysis" in raw_data: raw_data = raw_data["analysis"]
                elif "data" in raw_data: raw_data = raw_data["data"]
            
            # --- START ADVANCED SANITIZATION ---
            if isinstance(raw_data, dict):
                # Normalize keys to lowercase for internal checks
                keys = list(raw_data.keys())
                for key in keys:
                    val = raw_data[key]
                    lower_key = key.lower()

                    # 1. Stringify fields that MUST be strings
                    if lower_key in ["tam", "sam", "som", "cagr", "valuation", "overview", "business_model", "founding_year", "headquarters", "overall_risk_score"]:
                        if not isinstance(val, str):
                            raw_data[key] = json.dumps(val) if isinstance(val, (dict, list)) else str(val)

                    # 2. Heal Lists: If a list is expected but AI wrapped it in a single-key dict
                    # Common with 'products', 'key_management', 'competitors', etc.
                    if lower_key in ["products", "key_management", "founders_background", "competitors", "market_drivers", "revenue_data", "key_metrics", "unit_economics", "risks", "citations"]:
                        if isinstance(val, dict) and len(val) == 1:
                            # Extract the first list found inside the dict
                            inner_val = next(iter(val.values()))
                            if isinstance(inner_val, list):
                                raw_data[key] = inner_val
                        elif not isinstance(val, list):
                            # Ensure it's at least an empty list to satisfy Pydantic
                            raw_data[key] = []
            # --- END ADVANCED SANITIZATION ---
            
            if isinstance(raw_data, dict) and "reasoning" not in raw_data:
                raw_data["reasoning"] = f"Extraction Pass {attempt_num}"
                
            return current_schema.model_validate(raw_data)

        # 3. First Pass Analysis
        validated_data = perform_analysis(context, 1)

        # 4. AI Judge Logic (Self-Correction)
        # We judge 'Quality' by checking if key fields are missing or 'N/A' 
        # while the reasoning suggests information should be present.
        low_quality = False
        if request.analysis_type == "market" and validated_data.tam == "N/A": low_quality = True
        if request.analysis_type == "company" and validated_data.overview == "No overview available.": low_quality = True
        
        if low_quality:
            print(f"DEBUG: AI Judge detected low quality for {document_id}. Retrying with expanded context...")
            # Retry with k=20 for a more holistic view
            results_expanded = vectordb.similarity_search(
                query=f"Detailed holistic view for {request.analysis_type} including all specific data points",
                k=20,
                filter={"source": document_id}
            )
            context_expanded = "\n\n".join([doc.page_content for doc in results_expanded])
            validated_data = perform_analysis(context_expanded, 2)

        # 5. Save to Cache
        try:
            with open(cache_path, 'w') as f:
                json.dump(validated_data.model_dump(), f)
        except Exception as e:
            print(f"DEBUG: Cache write failed: {e}")

        return {"analysis": validated_data.model_dump(), "cached": False}

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
