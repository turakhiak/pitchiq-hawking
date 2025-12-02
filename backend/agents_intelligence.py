"""
Enhanced Agents with Industry Intelligence
Integrates industry benchmarks and competitive research into analysis.
"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-flash-latest')

# Vector DB
# Use persistent disk if available (production on Render), fallback to local (development)
VECTOR_DB_DIR = "/mnt/data/chroma_db" if os.path.exists("/mnt/data") else "./chroma_db"
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

router = APIRouter()


# --- Helper: Get Industry Benchmarks ---
def get_industry_benchmarks(industry: str, query: str = None) -> str:
    """
    Retrieve relevant industry benchmarks from the knowledge base.
    """
    try:
        # Access industry knowledge collection
        knowledge_db = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings,
            collection_name="industry_knowledge"
        )
        
        # If no specific query, get general benchmarks
        if not query:
            query = f"What are the key benchmarks and metrics for {industry}?"
        
        # Search with industry filter
        results = knowledge_db.similarity_search(
            query=query,
            k=5,
            filter={"industry": industry.lower().replace(" ", "_")}
        )
        
        if not results:
            return "No industry benchmarks available."
        
        # Combine results
        benchmarks = "\n\n".join([doc.page_content for doc in results])
        return benchmarks
        
    except Exception as e:
        print(f"Error retrieving benchmarks: {e}")
        return "Industry benchmarks unavailable."


# --- Helper: Get Competitive Research ---
def get_competitive_research(document_id: str) -> Optional[str]:
    """
    Retrieve competitive research if available for this document.
    """
    try:
        # Access main ChromaDB for research reports
        vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
        
        # Search for research reports
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


# Keep existing Pydantic models and /analyze endpoint code...
# (The rest of agents.py remains the same, but prompts will be enhanced below)
