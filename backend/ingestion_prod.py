# Simplified ingestion for production deployment (no ChromaDB)
# Documents are stored in-memory only

import os
import google.generativeai as genai
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import json

router = APIRouter()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# In-memory storage (will reset on deployment restart)
DOCUMENTS_STORE = {}

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    deal_type: str = Form("M&A"),
    industry: str = Form("Technology")
):
    try:
        # Upload to Gemini
        uploaded_file = genai.upload_file(file.file, mime_type=file.content_type)
        
        # Wait for processing
        import time
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
        
        if uploaded_file.state.name == "FAILED":
            raise ValueError("File processing failed")
        
        # Generate document ID
        document_id = uploaded_file.name.split('/')[-1]
        
        # Extract text using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            uploaded_file,
            "Extract all text content from this pitch deck document. Preserve structure and formatting."
        ])
        
        # Store in memory
        DOCUMENTS_STORE[document_id] = {
            "text": response.text,
            "deal_type": deal_type,
            "industry": industry,
            "filename": file.filename
        }
        
        return {
            "message": "PDF uploaded successfully",
            "document_id": document_id,
            "deal_type": deal_type,
            "industry": industry
        }
        
    except Exception as e:
        return {"error": str(e)}, 500

@router.get("/documents")
async def get_documents():
    """Get list of uploaded documents"""
    docs = []
    for doc_id, data in DOCUMENTS_STORE.items():
        docs.append({
            "id": doc_id,
            "title": data.get("filename", "Untitled"),
            "uploadDate": "2024-01-01",  # Simplified
            "dealType": data.get("deal_type", "M&A"),
            "industry": data.get("industry", "Technology")
        })
    return {"documents": docs, "totalDocuments": len(docs)}
