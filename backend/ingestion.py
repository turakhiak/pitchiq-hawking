import os
import shutil
import tempfile
import uuid
import time
import json
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks

import google.generativeai as genai
from langchain_chroma import Chroma
from langchain_core.documents import Document
from shared_utils import get_embeddings
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# Persistent storage path
VECTOR_DB_DIR = os.getenv("CHROMA_DB_PATH") or (
    "/mnt/data/chroma_db" if os.path.exists("/mnt/data") else "./chroma_db"
)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# In-memory job status store
# Format: { job_id: { "status": "pending|processing|done|error", "result": {...}, "error": "..." } }
JOB_STORE: dict = {}


@router.get("/health")
async def health_check():
    """Debug endpoint to check backend status and environment"""
    chroma_path = VECTOR_DB_DIR
    exists = os.path.exists(chroma_path)
    return {
        "status": "ok",
        "chroma_path": chroma_path,
        "chroma_exists": exists,
        "contents": os.listdir(chroma_path) if exists else []
    }


def _run_ingestion(job_id: str, tmp_path: str, filename: str, industry: str, geography: str, deal_type: Optional[str]):
    """Background task: does the heavy lifting after the HTTP response is sent."""
    try:
        JOB_STORE[job_id]["status"] = "processing"
        JOB_STORE[job_id]["step"] = "Uploading to Gemini..."

        # Step 1: Upload to Gemini
        uploaded_file = genai.upload_file(tmp_path, mime_type="application/pdf")

        while uploaded_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_file = genai.get_file(uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise ValueError("Gemini failed to process the PDF file.")

        JOB_STORE[job_id]["step"] = "Analysing with Gemini..."

        # Step 2: Call Gemini to extract sections
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
            response_data = json.loads(response.text)
            sections = response_data.get("sections", [])
            if not sections:
                sections = [{"title": "Full Document", "content": response.text, "page_range": "All"}]
        except json.JSONDecodeError:
            sections = [{"title": "Full Document", "content": response.text, "page_range": "All"}]

        # Step 3: Create Document objects
        documents = []
        for section in sections:
            doc = Document(
                page_content=f"# {section.get('title', 'Section')}\n\n{section.get('content', '')}",
                metadata={
                    "source": filename,
                    "page": section.get("page_range", "Unknown"),
                    "industry": industry,
                    "geography": geography,
                    "deal_type": deal_type or "N/A",
                    "section": section.get("title", "Unknown"),
                },
            )
            documents.append(doc)

        JOB_STORE[job_id]["step"] = "Storing embeddings..."

        # Step 4: Store in ChromaDB
        Chroma.from_documents(
            documents=documents,
            embedding=get_embeddings(),
            persist_directory=VECTOR_DB_DIR,
        )

        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        JOB_STORE[job_id]["status"] = "done"
        JOB_STORE[job_id]["step"] = "Complete"
        JOB_STORE[job_id]["result"] = {
            "filename": filename,
            "status": "Ingested successfully",
            "chunks_created": len(documents),
            "metadata": {"industry": industry, "geography": geography},
        }

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print(f"[Job {job_id}] Ingestion error: {e}\n{trace}")
        JOB_STORE[job_id]["status"] = "error"
        JOB_STORE[job_id]["error"] = str(e)
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    industry: str = Form(...),
    geography: str = Form(...),
    deal_type: Optional[str] = Form(None),
):
    """
    Accepts the upload, saves the file, kicks off a background job,
    and immediately returns a job_id for the client to poll.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    # Save file to temp location before returning
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    job_id = str(uuid.uuid4())
    JOB_STORE[job_id] = {"status": "pending", "step": "Queued", "result": None, "error": None}

    background_tasks.add_task(
        _run_ingestion, job_id, tmp_path, file.filename, industry, geography, deal_type
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/ingest/status/{job_id}")
async def ingest_status(job_id: str):
    """Poll this endpoint to check ingestion progress."""
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {
        "job_id": job_id,
        "status": job["status"],        # pending | processing | done | error
        "step": job.get("step", ""),
        "result": job.get("result"),
        "error": job.get("error"),
    }
