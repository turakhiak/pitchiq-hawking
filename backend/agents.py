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
from industry_knowledge.saas_tech.benchmarks import get_industry_benchmarks
from research_agent import get_competitive_research

router = APIRouter()

# Persistent storage path
VECTOR_DB_DIR = os.getenv("CHROMA_DB_PATH") or (
    "/mnt/data" if os.path.exists("/mnt/data") else "./chroma_db"
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
        if request.analysis_type == "company":
            schema = CompanyAnalysis
            prompt = f"Analyze this company's overview, management, and products based on this context: {context}\nReturn JSON matching schema."
        elif request.analysis_type == "market":
            schema = MarketAnalysis
            prompt = f"Analyze market size (TAM/SAM/SOM), CAGR, and competitors based on this context: {context}\nReturn JSON matching schema."
        elif request.analysis_type == "financial":
            schema = FinancialAnalysis
            prompt = f"Extract revenue data, margins, valuation, and metrics based on this context: {context}\nReturn JSON matching schema."
        elif request.analysis_type == "risk":
            schema = RiskAnalysis
            prompt = f"Identify key risks (Market, Tech, Financial) and mitigants based on this context: {context}\nReturn JSON matching schema."
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

        # Call Gemini
        try:
            response = model.generate_content(prompt, generation_config=generation_config)
            if not response.candidates:
                 raise Exception("No AI candidates returned")
                
            json_text = response.text
            # Cleanup Markdown
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(json_text)
            return {"analysis": data}
        except Exception as e:
            print(f"AI ERROR: {e}")
            raise HTTPException(status_code=500, detail=f"AI failure: {str(e)}")

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
