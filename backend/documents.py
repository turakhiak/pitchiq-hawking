
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import datetime

load_dotenv()

router = APIRouter()

# Use open-source embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
VECTOR_DB_DIR = "./chroma_db"

class Document(BaseModel):
    id: str
    name: str
    date: str
    industry: str
    geography: Optional[str] = None
    deal_type: Optional[str] = None

class DashboardStats(BaseModel):
    total_documents: int
    industries_covered: int
    avg_deal_size: str # Placeholder for now
    risk_flags: int # Placeholder for now

@router.get("/documents", response_model=List[Document])
async def get_documents():
    try:
        vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
        # ChromaDB doesn't have a simple "list all documents" method that returns unique metadata.
        # We have to fetch all data and deduplicate. This is inefficient for large datasets
        # but acceptable for this prototype.
        
        # Fetch all data (limit to a reasonable number if needed, but for now fetch all)
        # get() returns a dict with 'ids', 'embeddings', 'metadatas', 'documents'
        collection_data = vectordb.get() 
        metadatas = collection_data['metadatas']
        
        unique_docs = {}
        
        for meta in metadatas:
            if not meta: continue
            source = meta.get('source')
            if source and source not in unique_docs:
                # Try to infer date from file stats if possible, otherwise use "Unknown" or current date
                # For now, we'll just say "Recently" or try to parse if we stored it.
                # We didn't store upload date in metadata, so we'll use a placeholder.
                
                unique_docs[source] = Document(
                    id=source, # Using filename as ID for now
                    name=source,
                    date="Recently", # We should add upload_date to metadata in ingestion.py
                    industry=meta.get('industry', 'Unknown'),
                    geography=meta.get('geography', 'Unknown'),
                    deal_type=meta.get('deal_type', 'Unknown')
                )
        
        return list(unique_docs.values())
        
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []

@router.get("/documents/stats", response_model=DashboardStats)
async def get_stats():
    try:
        docs = await get_documents()
        
        unique_industries = set(d.industry for d in docs if d.industry != 'Unknown')
        
        return DashboardStats(
            total_documents=len(docs),
            industries_covered=len(unique_industries),
            avg_deal_size="$--M", # Placeholder
            risk_flags=0 # Placeholder
        )
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return DashboardStats(total_documents=0, industries_covered=0, avg_deal_size="-", risk_flags=0)
