import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# --- Industry Intelligence Helpers ---

def get_industry_benchmarks(industry: str, analysis_type: str = None) -> str:
    """
    Retrieve relevant industry benchmarks from the knowledge base.
    """
    try:
        knowledge_db = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings,
            collection_name="industry_knowledge"
        )
        
        # Build query based on analysis type
        if analysis_type == "financial":
            query = f"financial metrics benchmarks for {industry} companies including CAC LTV burn rate margins"
        elif analysis_type == "market":
            query = f"market metrics benchmarks for {industry} including market size growth rates"
        elif analysis_type == "company":
            query = f"company structure team metrics for {industry}"
        else:
            query = f"key benchmarks and metrics for {industry}"
        
        # Search with industry filter
        results = knowledge_db.similarity_search(
            query=query,
            k=3,
            filter={"industry": industry.lower().replace(" ", "_").replace("/", "_")}
        )
        
        if not results:
            return "No industry benchmarks available."
        
        benchmarks = "\n".join([doc.page_content for doc in results])
        return benchmarks
        
    except Exception as e:
        print(f"Error retrieving benchmarks: {e}")
        return "Industry benchmarks unavailable."


def get_competitive_research(document_id: str) -> Optional[str]:
    """
    Retrieve competitive research if available for this document.
    """
    try:
        vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
        
        results = vectordb.similarity_search(
            query="competitive intelligence research",
            k=2,
            filter={"source": f"{document_id}_research"}
        )
        
        if results:
            return "\n\n".join([doc.page_content for doc in results])
        return None
        
    except Exception as e:
        print(f"Error retrieving research: {e}")
        return None

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-flash-latest')

# Use open-source embeddings for ChromaDB
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Use persistent storage: env var > /mnt/data > local fallback
VECTOR_DB_DIR = os.getenv("CHROMA_DB_PATH") or ("/mnt/data/chroma_db" if os.path.exists("/mnt/data") else "./chroma_db")

# Ensure directory exists
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

class AnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str # company, market, financial, risk

# --- Structured Output Schemas ---

class Citation(BaseModel):
    text: str = Field(description="The exact quote from the document supporting this point")
    explanation: Optional[str] = Field(description="Brief explanation of why this quote is relevant")

class CompanyAnalysis(BaseModel):
    reasoning: str = Field(description="Chain-of-thought reasoning process used to derive this analysis")
    overview: str
    founding_year: Optional[str]
    headquarters: Optional[str]
    key_management: List[dict] = Field(description="List of {name, role, bio}")
    founders_background: Optional[List[dict]] = Field(description="Detailed background of founders (specific for startups)")
    products: List[dict] = Field(description="List of {name, description}")
    business_model: str
    citations: List[Citation]

class MarketAnalysis(BaseModel):
    reasoning: str = Field(description="Chain-of-thought reasoning process used to derive this analysis")
    tam: str = Field(description="Total Addressable Market value")
    sam: str = Field(description="Serviceable Available Market value")
    som: str = Field(description="Serviceable Obtainable Market value")
    cagr: str = Field(description="Compound Annual Growth Rate")
    competitors: List[dict] = Field(description="List of {name, description, strength, weakness}")
    market_drivers: List[str]
    citations: List[Citation]

class FinancialAnalysis(BaseModel):
    reasoning: str = Field(description="Chain-of-thought reasoning process used to derive this analysis")
    revenue_data: List[dict] = Field(description="List of {year, value, is_projected}")
    ebitda_margins: Optional[str] = Field(description="EBITDA Margins (standard deals)")
    valuation: str
    monthly_burn_rate: Optional[str] = Field(description="Monthly cash burn rate (VC/Startup)")
    runway_months: Optional[str] = Field(description="Estimated runway in months (VC/Startup)")
    unit_economics: Optional[List[dict]] = Field(description="List of {metric, value} e.g. CAC, LTV, Payback (VC/Startup)")
    key_metrics: List[dict] = Field(description="List of {metric, value}")
    verification_notes: str
    citations: List[Citation]

class RiskAnalysis(BaseModel):
    reasoning: str = Field(description="Chain-of-thought reasoning process used to derive this analysis")
    risks: List[dict] = Field(description="List of {category, description, severity, mitigant}")
    overall_risk_score: str = Field(description="Low, Medium, or High")
    citations: List[Citation]

@router.post("/analyze")
async def analyze_document(request: AnalysisRequest):
    try:
        # 1. Retrieve relevant chunks from ChromaDB
        vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
        
        # Search for documents matching the document_id
        results = vectordb.similarity_search(
            query=f"Information about {request.analysis_type}",
            k=10, # Increased context for better extraction
            filter={"source": request.document_id}
        )
        
        # Combine retrieved context
        context = "\n\n".join([doc.page_content for doc in results])
        
        if not context:
            return {"analysis": None, "error": "No documents found", "document_id": request.document_id, "type": request.analysis_type}
            
        # Extract metadata
        deal_type = results[0].metadata.get("deal_type", "M&A")
        industry = results[0].metadata.get("industry", "Technology")
        is_vc = deal_type in ["Venture Capital", "Angel Investing"]
        
        # --- INDUSTRY INTELLIGENCE INTEGRATION ---
        # Get industry benchmarks
        try:
            benchmarks = get_industry_benchmarks(industry, request.analysis_type)
            if benchmarks and benchmarks != "No industry benchmarks available.":
                context += f"\n\n--- INDUSTRY BENCHMARKS ({industry}) ---\n{benchmarks}"
        except Exception as e:
            print(f"Could not load benchmarks: {e}")
        
        # Get competitive research if available
        try:
            competitive_intel = get_competitive_research(request.document_id)
            if competitive_intel:
                context += f"\n\n--- COMPETITIVE INTELLIGENCE ---\n{competitive_intel}"
        except Exception as e:
            print(f"Could not load competitive research: {e}")
        
        # 2. Define Prompts and Schemas based on Agent Type
        generation_config = {"response_mime_type": "application/json"}
        
        if request.analysis_type == "company":
            if is_vc:
                prompt = f"""
                You are a Venture Capital Analyst. Analyze this startup's team and product.
                
                Context:
                {context}
                
                Instructions:
                1. Identify the company and its mission.
                2. Deeply analyze the FOUNDERS. Look for previous exits, domain expertise, and technical background.
                3. Analyze the product/solution and its uniqueness (IP, patents).
                4. Explain the business model (SaaS, Marketplace, etc.).
                5. CRITICAL: Extract EXACT QUOTES from the context for citations. Each citation must include:
                   - The exact text from the document (as a direct quote)
                   - An explanation of why it's relevant
                
                EXAMPLE CITATION FORMAT:
                {{
                    "text": "Founded in 2020, Acme has raised $5M in seed funding",
                    "explanation": "Confirms founding date and funding stage"
                }}
                
                You MUST provide at least 2-3 citations with real quotes from the context above.
                
                Return a JSON object matching this schema:
                {{
                    "reasoning": "Step-by-step logic...",
                    "overview": "Startup summary",
                    "founding_year": "Year",
                    "headquarters": "Location",
                    "key_management": [{{ "name": "Name", "role": "Role", "bio": "Bio" }}],
                    "founders_background": [{{ "name": "Founder Name", "role": "Role", "bio": "Detailed background, exits, expertise" }}],
                    "products": [{{ "name": "Product", "description": "Description" }}],
                    "business_model": "Monetization strategy",
                    "citations": [
                        {{ "text": "EXACT quote from context", "explanation": "Why relevant" }},
                        {{ "text": "Another EXACT quote", "explanation": "Why relevant" }}
                    ]
                }}
                """
            else:
                prompt = f"""
                You are a Senior Company Analyst. Extract key company details from the pitchbook context with precision.
                
                Context:
                {context}
                
                Instructions:
                1. Identify the company name, founding date, and HQ location.
                2. Extract the full list of management team members and their specific roles.
                3. Analyze the product section to list distinct products/services.
                4. Synthesize the business model from revenue stream descriptions.
                5. CRITICAL: Extract EXACT QUOTES from the context for citations. Each citation must include:
                   - The exact text from the document (as a direct quote)
                   - An explanation of why it's relevant
                
                EXAMPLE CITATION FORMAT:
                {{
                    "text": "The company was founded in January 2015 by John Smith",
                    "explanation": "Provides founding date and founder information"
                }}
                
                You MUST provide at least 2-3 citations with real quotes from the context above.
                
                Return a JSON object matching this schema:
                {{
                    "reasoning": "Step-by-step logic used to extract this info",
                    "overview": "Brief company summary",
                    "founding_year": "Year",
                    "headquarters": "Location",
                    "key_management": [{{"name": "Name", "role": "Role", "bio": "Brief bio"}}],
                    "products": [{{"name": "Product Name", "description": "Description"}}],
                    "business_model": "How they make money",
                    "citations": [
                        {{"text": "EXACT quote from context", "explanation": "Why this is relevant"}},
                        {{"text": "Another EXACT quote", "explanation": "Why this is relevant"}}
                    ]
                }}
                """
        elif request.analysis_type == "market":
            # Market analysis is similar for VC/PE, but VC focuses more on TAM/SAM/SOM and growth potential
            prompt = f"""
            You are a Senior Market Analyst. Extract market sizing and competitor info with precision.
            
            Context:
            {context}
            
            Instructions:
            1. Search for specific market size numbers (TAM, SAM, SOM) and currency/units.
            2. Identify the CAGR percentage and the time period it applies to.
            3. List all mentioned competitors and categorize their strengths/weaknesses if stated.
            4. Summarize market drivers.
            5. Select exact quotes for citations.
            
            Return a JSON object matching this schema:
            {{
                "reasoning": "Step-by-step logic used to extract this info",
                "tam": "Value (e.g. $5B)",
                "sam": "Value",
                "som": "Value",
                "cagr": "Percentage (e.g. 12%)",
                "competitors": [{{"name": "Competitor Name", "description": "Desc", "strength": "Key strength", "weakness": "Key weakness"}}],
                "market_drivers": ["Driver 1", "Driver 2"],
                "citations": [{{"text": "Exact quote from text", "explanation": "Why this is relevant"}}]
            }}
            """
        elif request.analysis_type == "financial":
            if is_vc:
                prompt = f"""
                You are a Venture Capital Financial Analyst specializing in EARLY-STAGE startups (Pre-revenue to Series A).
                
                Context:
                {context}
                
                CRITICAL UNDERSTANDING: Many startups at this stage have MINIMAL or NO revenue. Focus on TRACTION and GROWTH indicators instead.
                
                Instructions:
                1. **Revenue/ARR/MRR**: Extract if available, but if NOT found, explicitly state "Pre-revenue" or "Not disclosed"
                2. **Traction Metrics** (PRIORITIZE THESE for early-stage):
                   - User/customer count (e.g., "10K active users", "500 paying customers")
                   - Downloads, sign-ups, waitlist size
                   - Month-over-month (MoM) growth rates
                   - Engagement metrics (DAU/MAU, retention %)
                   - Product milestones ("MVP launched Q1 2023", "Beta testing with 50 companies")
                3. **Burn Rate & Runway**: Extract monthly cash burn and months of runway remaining
                4. **Unit Economics** (even if projections):
                   - CAC (Customer Acquisition Cost)
                   - LTV (Lifetime Value) - even if estimated
                   - Payback period
                5. **Funding History**: Extract previous raises (pre-seed, seed amounts) and current valuation
                6. **Key Milestones**: Product launches, partnerships, pilot programs, LOIs (Letters of Intent)
                7. CRITICAL: Extract EXACT QUOTES from the context for citations. Each citation must include:
                   - The exact text from the document (as a direct quote)
                   - An explanation of why it's relevant
                
                EXAMPLE CITATION FORMAT:
                {{
                    "text": "Achieved 15,000 active users with 40% MoM growth",
                    "explanation": "Demonstrates strong early traction and growth velocity"
                }}
                
                You MUST provide at least 2-3 citations with real quotes from the context above.
                
                Return a JSON object matching this schema:
                {{
                    "reasoning": "Step-by-step logic explaining traction assessment for this early-stage company",
                    "revenue_data": [{{ "year": "2024", "value": 0, "is_projected": true, "note": "Pre-revenue" }}],
                    "monthly_burn_rate": "Value (e.g. $75k/mo) or 'Not disclosed'",
                    "runway_months": "Value (e.g. 18 months) or 'Not disclosed'",
                    "unit_economics": [
                        {{ "metric": "CAC", "value": "$500 (estimated)" }}, 
                        {{ "metric": "LTV", "value": "$2000 (projected)" }},
                        {{ "metric": "Payback Period", "value": "12 months" }}
                    ],
                    "valuation": "Value (e.g. $10M pre-money) or 'Not disclosed'",
                    "key_metrics": [
                        {{ "metric": "Active Users", "value": "10,000" }},
                        {{ "metric": "MoM Growth", "value": "25%" }},
                        {{ "metric": "User Retention (30-day)", "value": "65%" }},
                        {{ "metric": "Pilot Customers", "value": "15 enterprise clients" }}
                    ],
                    "verification_notes": "For pre-revenue companies, focus on traction indicators: user growth, engagement, and product-market fit signals. Note any revenue projections or pilot conversion rates.",
                    "citations": [
                        {{ "text": "EXACT quote from context", "explanation": "Why relevant" }},
                        {{ "text": "Another EXACT quote", "explanation": "Why relevant" }}
                    ]
                }}
                """
            else:
                prompt = f"""
                You are a Senior Financial Analyst. Extract and verify financial metrics with extreme precision.
                
                Context:
                {context}
                
                Instructions:
                1. Extract all revenue figures and map them to their respective years.
                2. Identify EBITDA margins and Valuation if present.
                3. Calculate the CAGR based on the extracted revenue (Ending/Beginning)^(1/n) - 1.
                4. Compare your calculated CAGR with any stated CAGR in the text. Note discrepancies in 'verification_notes'.
                5. CRITICAL: Extract EXACT QUOTES from the context for citations. Each citation must include:
                   - The exact text from the document (as a direct quote)
                   - An explanation of why it's relevant
                
                EXAMPLE CITATION FORMAT:
                {{
                    "text": "Revenue grew from $100M in 2021 to $150M in 2023",
                    "explanation": "Demonstrates revenue growth trajectory"
                }}
                
                You MUST provide at least 2-3 citations with real quotes from the context above.
                
                Return a JSON object matching this schema:
                {{
                    "reasoning": "Step-by-step logic used to extract this info, including CAGR verification",
                    "revenue_data": [{{"year": "2023", "value": 100, "is_projected": false}}],
                    "ebitda_margins": "Value (e.g. 20%)",
                    "valuation": "Value (e.g. $500M)",
                    "key_metrics": [{{"metric": "Metric Name", "value": "Value"}}],
                    "verification_notes": "Notes on data consistency and CAGR check",
                    "citations": [
                        {{"text": "EXACT quote from context", "explanation": "Why this is relevant"}},
                        {{"text": "Another EXACT quote", "explanation": "Why this is relevant"}}
                    ]
                }}
                """
        elif request.analysis_type == "risk":
            if is_vc:
                prompt = f"""
                You are a Venture Capital Risk Analyst. Assess startup risks.
                
                Context:
                {context}
                
                Instructions:
                1. Assess PRODUCT-MARKET FIT risk (Is there demand?).
                2. Assess FUNDING RISK (Will they run out of cash?).
                3. Assess TEAM RISK (Do they have the right skills?).
                4. Assess COMPETITIVE MOAT (Can big tech copy them?).
                5. CRITICAL: Extract EXACT QUOTES from the context for citations. Each citation must include:
                   - The exact text from the document (as a direct quote)
                   - An explanation of why it's relevant
                
                EXAMPLE CITATION FORMAT:
                {{
                    "text": "The market is highly competitive with established players",
                    "explanation": "Highlights competitive risk factor"
                }}
                
                You MUST provide at least 2-3 citations with real quotes from the context above.
                
                Return a JSON object matching this schema:
                {{
                    "reasoning": "Step-by-step logic...",
                    "risks": [{{ "category": "Product/Funding/Team", "description": "Risk details", "severity": "High/Medium/Low", "mitigant": "Proposed solution" }}],
                    "overall_risk_score": "High/Medium/Low",
                    "citations": [
                        {{ "text": "EXACT quote from context", "explanation": "Why relevant" }},
                        {{ "text": "Another EXACT quote", "explanation": "Why relevant" }}
                    ]
                }}
                """
            else:
                prompt = f"""
                You are a Senior Risk Analyst. Identify risks and mitigants with critical thinking.
                
                Context:
                {context}
                
                Instructions:
                1. Identify explicit risk factors mentioned in the 'Risks' section.
                2. Infer implicit risks based on the company's stage and market (e.g., 'High competition').
                3. Look for mitigating factors for each risk.
                4. Assign a severity score (High/Medium/Low) based on the potential impact.
                5. CRITICAL: Extract EXACT QUOTES from the context for citations. Each citation must include:
                   - The exact text from the document (as a direct quote)
                   - An explanation of why it's relevant
                
                EXAMPLE CITATION FORMAT:
                {{
                    "text": "Regulatory changes could impact market access",
                    "explanation": "Identifies regulatory risk"
                }}
                
                You MUST provide at least 2-3 citations with real quotes from the context above.
                
                Return a JSON object matching this schema:
                {{
                    "reasoning": "Step-by-step logic used to assess risks",
                    "risks": [{{"category": "Market/Operational/Financial", "description": "Risk details", "severity": "High/Medium/Low", "mitigant": "Proposed solution"}}],
                    "overall_risk_score": "High/Medium/Low",
                    "citations": [
                        {{"text": "EXACT quote from context", "explanation": "Why this is relevant"}},
                        {{"text": "Another EXACT quote", "explanation": "Why this is relevant"}}
                    ]
                }}
                """
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

        # 3. Call Gemini directly
        response = model.generate_content(prompt, generation_config=generation_config)
        result_text = response.text
        
        # Parse JSON to ensure it's valid before returning
        try:
            result_json = json.loads(result_text)
            return {"analysis": result_json, "document_id": request.document_id, "type": request.analysis_type}
        except json.JSONDecodeError:
            # Fallback if JSON is malformed (rare with generation_config)
            return {"analysis": {"error": "Failed to parse structured data", "raw_text": result_text}, "document_id": request.document_id, "type": request.analysis_type}

    except Exception as e:
        print(f"Error in analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
