import chromadb
import os

def test_chroma():
    CHROMA_DATA_PATH = r"e:\OLD DESKTOP FILES AND FOLDERS\Adani_Project_Kashish_Github\backend\chroma_data"
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    COLLECTION_NAME = "monitor_embeddings"
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        count = collection.count()
        print(f"Collection '{COLLECTION_NAME}' exists with {count} documents.")
        
        # Try a dummy query
        print("Running dummy query...")
        results = collection.query(
            query_embeddings=[[0.1] * 384], # MiniLM is 384 dims
            n_results=1
        )
        print("Query successful!")
        print(results)
    except Exception as e:
        print(f"ChromaDB Error: {e}")

if __name__ == "__main__":
    test_chroma()
