
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_chroma import Chroma
from shared_utils import get_embeddings
from dotenv import load_dotenv
import datetime

load_dotenv()

router = APIRouter()

# Use open-source embeddings (lazy loaded)
# Use persistent storage: env var > /mnt/data > local fallback
VECTOR_DB_DIR = os.getenv("CHROMA_DB_PATH") or ("/mnt/data/chroma_db" if os.path.exists("/mnt/data") else "./chroma_db")

# Ensure directory exists
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

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

@router.get("/documents/stats", response_model=DashboardStats)
async def get_stats():
    try:
        docs = await get_documents()
        unique_industries = set(d.industry for d in docs if d.industry != 'Unknown')
        return DashboardStats(
            total_documents=len(docs),
            industries_covered=len(unique_industries),
            avg_deal_size="$--M",
            risk_flags=0
        )
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return DashboardStats(total_documents=0, industries_covered=0, avg_deal_size="-", risk_flags=0)

@router.get("/documents", response_model=List[Document])
async def get_documents():
    try:
        vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=get_embeddings())
        collection_data = vectordb.get()
        metadatas = collection_data['metadatas']

        unique_docs = {}
        for meta in metadatas:
            if not meta: continue
            source = meta.get('source')
            if source and source not in unique_docs:
                unique_docs[source] = Document(
                    id=source,
                    name=source,
                    date=meta.get('upload_date', 'Recently'),
                    industry=meta.get('industry', 'Unknown'),
                    geography=meta.get('geography', 'Unknown'),
                    deal_type=meta.get('deal_type', 'Unknown')
                )

        return list(unique_docs.values())

    except Exception as e:
        print(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")
