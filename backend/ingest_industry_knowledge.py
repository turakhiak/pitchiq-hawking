"""
Industry Knowledge Base Ingestion
Ingests industry benchmark documents into ChromaDB for semantic search during analysis.
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Constants
INDUSTRY_KNOWLEDGE_DIR = "./industry_knowledge"
VECTOR_DB_DIR = "./chroma_db"

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def simple_chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Simple text chunking without external dependencies."""
    chunks = []
    # Split by double newlines (paragraphs) first
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def ingest_industry_knowledge():
    """
    Ingest all industry benchmark documents into ChromaDB.
    Creates a separate collection for industry knowledge.
    """
    print("[INFO] Starting Industry Knowledge Base ingestion...")
    
    # Initialize vectorDB
    vectordb = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name="industry_knowledge"  # Separate collection
    )
    
    documents_ingested = 0
    
    # Walk through industry knowledge directory
    for root, dirs, files in os.walk(INDUSTRY_KNOWLEDGE_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                
                # Extract industry from path
                # e.g., industry_knowledge/saas_tech/benchmarks.md -> "saas_tech"
                path_parts = file_path.split(os.sep)
                industry = path_parts[-2] if len(path_parts) > 1 else "unknown"
                
                print(f"[FILE] Ingesting: {file_path}")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split into chunks
                chunks = simple_chunk_text(content)
                
                # Create metadata
                metadatas = [
                    {
                        "source": "industry_knowledge",
                        "industry": industry,
                        "file": file,
                        "chunk_index": i,
                        "type": "benchmark"
                    }
                    for i in range(len(chunks))
                ]
                
                # Add to vectorDB
                vectordb.add_texts(
                    texts=chunks,
                    metadatas=metadatas
                )
                
                documents_ingested += 1
                print(f"   [OK] Added {len(chunks)} chunks from {industry}/{file}")
    
    print(f"\n[DONE] Industry knowledge ingestion complete! Processed {documents_ingested} documents.")
    return vectordb


def test_knowledge_retrieval():
    """Test retrieval from industry knowledge base."""
    print("\n[TEST] Testing industry knowledge retrieval...")
    
    vectordb = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name="industry_knowledge"
    )
    
    # Test queries
    queries = [
        "What is the typical CAC for SaaS companies?",
        "What is the average conversion rate for e-commerce?",
        "How long does drug development take for biotech companies?",
        "What is a good payment success rate for fintech?"
    ]
    
    for query in queries:
        print(f"\n[Q] Query: {query}")
        results = vectordb.similarity_search(query, k=2)
        
        for i, doc in enumerate(results, 1):
            print(f"\n   Result {i} ({doc.metadata.get('industry', 'unknown')}):")
            print(f"   {doc.page_content[:200]}...")


if __name__ == "__main__":
    # Ingest industry knowledge
    ingest_industry_knowledge()
    
    # Test retrieval
    test_knowledge_retrieval()
