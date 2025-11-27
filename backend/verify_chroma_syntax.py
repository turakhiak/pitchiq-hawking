
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
VECTOR_DB_DIR = "./chroma_db"

def test_filtering():
    print("Initializing ChromaDB...")
    vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    
    # We need a document ID that exists. 
    # Based on previous logs, we uploaded 'test_pitchbook.pdf' and 'Jazz-Pharmaceuticals-Investment-Banking-Pitch-Book.pdf'
    # Let's try to find *any* document first to get a valid source ID
    print("Fetching any document to get a valid source ID...")
    try:
        results = vectordb.similarity_search("company", k=1)
        if not results:
            print("No documents found in DB. Cannot test filtering.")
            return
            
        valid_source = results[0].metadata.get("source")
        print(f"Found valid source: {valid_source}")
        
        print(f"\n--- Testing Filter Syntax 1: filter={{'source': '{valid_source}'}} ---")
        try:
            results = vectordb.similarity_search(
                query="company",
                k=1,
                filter={"source": valid_source}
            )
            print(f"Syntax 1 Success! Found {len(results)} docs.")
            print(f"Metadata: {results[0].metadata}")
        except Exception as e:
            print(f"Syntax 1 Failed: {e}")

        print(f"\n--- Testing Filter Syntax 2: where={{'source': '{valid_source}'}} ---")
        try:
            results = vectordb.similarity_search(
                query="company",
                k=1,
                where={"source": valid_source}
            )
            print(f"Syntax 2 Success! Found {len(results)} docs.")
        except Exception as e:
            print(f"Syntax 2 Failed: {e}")
            
    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    test_filtering()
