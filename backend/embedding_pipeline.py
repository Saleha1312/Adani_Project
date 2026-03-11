import json
from sentence_transformers import SentenceTransformer
from mongodb_loader import load_all_documents
from chroma_store import add_documents_to_chroma
import asyncio

# Load the Sentence-Transformer model
print("Loading encoding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def process_document(doc):
    """
    Extracts and combines text fields from a MongoDB document.
    """
    title = doc.get("title", "")
    raw_content_list = doc.get("raw_content", [])
    raw_content = " ".join(raw_content_list) if isinstance(raw_content_list, list) else str(raw_content_list)
    
    performance = json.dumps(doc.get("performance", {}))
    resources = json.dumps(doc.get("resources", {}))
    system = json.dumps(doc.get("system", {}))

    document_text = f"{title}\n{raw_content}\n{performance}\n{resources}\n{system}"
    return document_text

def process_and_store_all_documents(documents):
    """
    Processes all documents, generates embeddings, and stores them in ChromaDB.
    """
    if not documents:
        print("No documents to process.")
        return

    ids = []
    documents_texts = []
    metadatas = []

    for doc in documents:
        doc_id = str(doc.get("_id"))
        ids.append(doc_id)
        
        # Process text
        doc_text = process_document(doc)
        documents_texts.append(doc_text)
        
        # Create metadata
        metadatas.append({
            "title": doc.get("title", "Unknown"),
            "url": doc.get("url", "Unknown"),
            "timestamp": str(doc.get("timestamp", ""))
        })

    print(f"Generating embeddings for {len(documents_texts)} documents...")
    # Generate embeddings
    embeddings = model.encode(documents_texts).tolist()

    print("Adding to ChromaDB...")
    # Store in Chroma
    add_documents_to_chroma(ids=ids, embeddings=embeddings, documents=documents_texts, metadatas=metadatas)
    print("Done!")

async def run_pipeline():
    """
    Main function to run the full extraction and embedding pipeline.
    """
    print("Fetching documents from MongoDB...")
    docs = await load_all_documents()
    process_and_store_all_documents(docs)

if __name__ == "__main__":
    # Can be run standalone to initialize the database
    asyncio.run(run_pipeline())
