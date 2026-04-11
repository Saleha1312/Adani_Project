import chromadb
from chromadb.config import Settings
import os

# Initialize ChromaDB client. 
# We'll use a persistent client to store embeddings locally.
CHROMA_DATA_PATH = os.path.join(os.path.dirname(__file__), "chroma_data")
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

COLLECTION_NAME = "monitor_embeddings"

def get_or_create_collection():
    """
    Gets the existing collection or creates a new one.
    """
    # Create the collection if it doesn't exist.
    # We use a default embedding function here, but we will explicitly pass embeddings later.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity
    )
    return collection

collection = get_or_create_collection()

def add_documents_to_chroma(ids, embeddings, documents, metadatas):
    """
    Adds documents, their embeddings, and metadata to ChromaDB.
    """
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

def query_chroma(query_embedding, n_results=5, where=None):
    """
    Queries ChromaDB to find the most similar documents.
    """
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where
    )
    return results

def clear_collection():
    """
    Deletes the current collection and recreates it to ensure a fresh sync.
    """
    global collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Collection '{COLLECTION_NAME}' not found or already deleted: {e}")
    
    collection = get_or_create_collection()
    print(f"Collection '{COLLECTION_NAME}' recreated.")
