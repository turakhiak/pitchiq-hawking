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

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

class AnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str  # company, market, financial, risk

class Citation(BaseModel):
    text: str
    explanation: str

class CompanyAnalysis(BaseModel):
    reasoning: str
    overview: str
    founding_year: Optional[str]
    headquarters: Optional[str]
    key_management: List[dict]
    founders_background: Optional[List[dict]]
    products: List[dict]
    business_model: str
    citations: List[Citation]

class MarketAnalysis(BaseModel):
    reasoning: str
    tam: str
    sam: str
    som: str
    cagr: str
    competitors: List[dict]
    market_drivers: List[str]
    citations: List[Citation]

class FinancialAnalysis(BaseModel):
    reasoning: str
    revenue_data: List[dict]
    ebitda_margins: Optional[str]
    valuation: str
    monthly_burn_rate: Optional[str]
    runway_months: Optional[str]
    unit_economics: Optional[List[dict]]
    key_metrics: List[dict]
    verification_notes: str
    citations: List[Citation]

class RiskAnalysis(BaseModel):
    reasoning: str
    risks: List[dict]
    overall_risk_score: str
    citations: List[Citation]

@router.post("/analyze")
async def analyze_document(request: AnalysisRequest):
    try:
        document_id = unquote(request.document_id)
        
        # Initialize Vector DB
        try:
            vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=get_embeddings())
            # Search with filter
            results = vectordb.similarity_search(
                query=f"Information about {request.analysis_type}",
                k=10,
                filter={"source": document_id}
            )
        except Exception as e:
            print(f"DEBUG: Search failed: {e}")
            results = []

        context = "\n\n".join([doc.page_content for doc in results])
        
        if not context:
            # Fallback to general search if specific ID fails (maybe ID changed?)
            results = vectordb.similarity_search(f"Information about {request.analysis_type}", k=10)
            context = "\n\n".join([doc.page_content for doc in results])
            
        if not context:
            raise HTTPException(status_code=404, detail="No document context found for analysis.")

        # Shared prompt parts
        generation_config = {"response_mime_type": "application/json"}
        
        # Determine prompt based on type
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

        if request.analysis_type == "company":
            schema = CompanyAnalysis
            prompt = f"""
            {system_instruction}
            
            TASK: Analyze the COMPANY OVERVIEW, MANAGEMENT TEAM, and PRODUCT PORTFOLIO.
            CONTEXT: {context}
            
            SPECIFIC INSTRUCTIONS:
            - 'overview': Summarize the core mission and value proposition.
            - 'key_management': Extract names, roles, and 2-sentence bios highlighting relevant experience.
            - 'products': Group into logical product lines. Describe what they solve.
            - 'business_model': How do they make money? (B2B SaaS, Marketplace, etc.)
            
            Return ONLY valid JSON matching the CompanyAnalysis schema.
            """
        elif request.analysis_type == "market":
            schema = MarketAnalysis
            prompt = f"""
            {system_instruction}
            
            TASK: Analyze MARKET SIZE (TAM/SAM/SOM), GROWTH (CAGR), and COMPETITION.
            CONTEXT: {context}
            
            SPECIFIC INSTRUCTIONS:
            - 'tam', 'sam', 'som': Extract specific dollar amounts. If unavailable, provide a calculated estimate based on the industry context.
            - 'cagr': Find the industry growth rate.
            - 'competitors': Identify 3-5 key competitors. List their relative strengths and weaknesses compared to this company.
            - 'market_drivers': List macro/micro trends driving demand.
            
            Return ONLY valid JSON matching the MarketAnalysis schema.
            """
        elif request.analysis_type == "financial":
            schema = FinancialAnalysis
            prompt = f"""
            {system_instruction}
            
            TASK: Extract FINANCIAL PERFORMANCE, METRICS, and VALUATION.
            CONTEXT: {context}
            
            SPECIFIC INSTRUCTIONS:
            - 'revenue_data': Extract yearly or quarterly revenue. Mark projected years as 'is_projected': true.
            - 'valuation': Find the post-money or pre-money valuation referenced. 
            - 'key_metrics': Extract metrics like LTV/CAC, ARR, Gross Margin, or burn rate.
            - 'verification_notes': Add a paragraph explaining the reliability of this financial data (e.g., 'Audited', 'Management Estimates', 'Fragmentary').
            
            Return ONLY valid JSON matching the FinancialAnalysis schema.
            """
        elif request.analysis_type == "risk":
            schema = RiskAnalysis
            prompt = f"""
            {system_instruction}
            
            TASK: Identify KEY RISKS and potential MITIGANTS.
            CONTEXT: {context}
            
            SPECIFIC INSTRUCTIONS:
            - Categorize risks into: Market Risk, Operational Risk, Financial Risk, or Regulatory Risk.
            - For each risk, provide a plausible 'mitigant' (how the company manages this risk).
            - 'overall_risk_score': Return 'Low', 'Medium', 'High', or 'Critical'.
            
            Return ONLY valid JSON matching the RiskAnalysis schema.
            """
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

        # Call Gemini
        try:
            response = model.generate_content(prompt, generation_config=generation_config)
            if not response.candidates:
                 raise Exception("No AI candidates returned")
                
            json_text = response.text
            # Final cleanup of markdown if any remains
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            # Use Pydantic to validate and enforce the schema
            raw_data = json.loads(json_text)
            validated_data = schema.model_validate(raw_data)
            
            return {"analysis": validated_data.model_dump()}
        except Exception as e:
            print(f"AI ERROR: {e}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"AI Data Validation Failure: {str(e)}")

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
