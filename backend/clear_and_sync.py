import asyncio
from chroma_store import clear_collection
from embedding_pipeline import run_pipeline

async def deep_clean_and_sync():
    """
    Clears the entire ChromaDB collection and performs a fresh sync from MongoDB.
    This ensures that all documents are re-indexed with the latest narrative format and terminal metadata.
    """
    print("Starting Deep Clean of Chatbot Database...")
    
    # 1. Clear the local vector collection
    clear_collection()
    
    # 2. Run the full embedding pipeline to re-fetch from MongoDB Atlas
    print("Re-indexing current data from MongoDB Atlas...")
    await run_pipeline()
    
    print("\nDeep Clean Complete! Your chatbot now contains highly accurate semantically enriched data.")

if __name__ == "__main__":
    asyncio.run(deep_clean_and_sync())
