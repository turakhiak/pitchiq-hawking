import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
VECTOR_DB_DIR = "./chroma_db"

try:
    print("Loading ChromaDB...")
    vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    
    print("\nTesting similarity search with where filter...")
    results = vectordb.similarity_search(
        query="company information",
        k=5,
        where={"source": "Jazz-Pharmaceuticals-Investment-Banking-Pitch-Book.pdf"}
    )
    
    print(f"\nFound {len(results)} results")
    for i, doc in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Source: {doc.metadata.get('source', 'N/A')}")
        print(f"Content preview: {doc.page_content[:200]}...")
        
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
