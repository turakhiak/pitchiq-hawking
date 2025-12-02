import os
import shutil
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-flash-latest')

# Configure Vector Store (using same embeddings as agents.py)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Use persistent storage: env var > /mnt/data > local fallback
VECTOR_DB_DIR = os.getenv("CHROMA_DB_PATH") or ("/mnt/data/chroma_db" if os.path.exists("/mnt/data") else "./chroma_db")

# Ensure directory exists
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    industry: str = Form(...),
    geography: str = Form(...),
    deal_type: Optional[str] = Form(None)
):
    try:
        print(f"Received upload request: {file.filename}, industry={industry}, geo={geography}")
        # 1. Save file temporarily
        print("DEBUG: Step 1 - Saving temp file")
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # 2. Upload PDF directly to Gemini (removes need for Poppler/pdf2image)
        if not tmp_path.lower().endswith(".pdf"):
             raise HTTPException(status_code=400, detail="Please upload a PDF version of the pitchbook.")

        # Upload the file to Gemini
        print(f"DEBUG: Step 2 - Uploading file to Gemini: {file.filename}")
        uploaded_file = genai.upload_file(tmp_path, mime_type="application/pdf")
        
        # Wait for processing (usually instant for small PDFs, but good practice)
        import time
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_file = genai.get_file(uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise ValueError("Gemini failed to process the PDF file.")

        print(f"File uploaded: {uploaded_file.name}")

        # 3. Call Gemini 1.5 Pro with the uploaded file
        print("DEBUG: Step 3 - Generating content with Gemini")
        prompt = """
        Analyze this pitchbook and split it into logical sections.
        
        Return a JSON object with a "sections" key, containing a list of sections.
        Each section should have:
        - "title": The section title (e.g., "Executive Summary", "Financial Overview", "Risk Factors", "Market Analysis").
        - "content": The full markdown content of that section (preserve all data, bullets, and tables).
        - "page_range": The approximate page range (e.g., "1-2").
        
        Example JSON structure:
        {
          "sections": [
            {
              "title": "Executive Summary",
              "content": "...",
              "page_range": "1-2"
            }
          ]
        }
        """
        
        generation_config = {"response_mime_type": "application/json"}
        response = model.generate_content([prompt, uploaded_file], generation_config=generation_config)
        
        try:
            import json
            response_data = json.loads(response.text)
            sections = response_data.get("sections", [])
            
            if not sections:
                # Fallback if no sections found
                print("WARNING: No sections found in JSON, using raw text")
                sections = [{"title": "Full Document", "content": response.text, "page_range": "All"}]
                
        except json.JSONDecodeError:
            print("ERROR: Failed to parse JSON from Gemini, using raw text")
            sections = [{"title": "Full Document", "content": response.text, "page_range": "All"}]
        
        # Create Document objects for each section
        documents = []
        for section in sections:
            doc = Document(
                page_content=f"# {section.get('title', 'Section')}\n\n{section.get('content', '')}",
                metadata={
                    "source": file.filename,
                    "page": section.get('page_range', 'Unknown'),
                    "industry": industry,
                    "geography": geography,
                    "deal_type": deal_type or "N/A",
                    "section": section.get('title', 'Unknown')
                }
            )
            documents.append(doc)

        # 4. Store in ChromaDB
        print(f"DEBUG: Step 4 - Storing {len(documents)} chunks in ChromaDB")
        vectordb = Chroma.from_documents(
            documents=documents, 
            embedding=embeddings,
            persist_directory=VECTOR_DB_DIR
        )
        # vectordb.persist() # Chroma 0.4+ persists automatically

        # Cleanup
        print("DEBUG: Step 5 - Cleanup")
        os.unlink(tmp_path)
        # Optional: genai.delete_file(uploaded_file.name) to clean up cloud storage

        return {
            "filename": file.filename, 
            "status": "Ingested successfully", 
            "chunks_created": len(documents),
            "metadata": {"industry": industry, "geography": geography}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
