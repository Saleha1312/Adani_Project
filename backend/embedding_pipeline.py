import json
from sentence_transformers import SentenceTransformer
from mongodb_loader import load_all_documents
from chroma_store import add_documents_to_chroma
import asyncio

# Load the Sentence-Transformer model
print("Loading encoding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def smart_extract_metrics(raw_content):
    """
    Heuristically extracts metrics from the raw_content list where structured performance data is missing/broken.
    """
    metrics = {
        "cpu": "N/A",
        "memory": "N/A",
        "disk": "N/A",
        "uptime": "N/A",
        "processes": "N/A",
        "nics": "N/A",
        "status": "Healthy"
    }
    
    for i, val in enumerate(raw_content):
        val_str = str(val).strip()
        
        # CPU/Memory/Disk often follow the pattern: [Number, "%", "MetricName"]
        if val_str == "%" and i > 0 and i + 1 < len(raw_content):
            next_val = str(raw_content[i+1]).strip()
            prev_val = str(raw_content[i-1]).strip()
            if next_val == "CPU": metrics["cpu"] = f"{prev_val}%"
            elif next_val == "Memory": metrics["memory"] = f"{prev_val}%"
            elif next_val == "Disk": metrics["disk"] = f"{prev_val}%"
            
        # Uptime is usually a standalone string "Uptime : ..."
        if "Uptime :" in val_str:
            metrics["uptime"] = val_str.replace("Uptime :", "").strip()
            
        # Counts often precede the label
        if val_str == "Processes" and i > 0: metrics["processes"] = str(raw_content[i-1]).strip()
        if val_str == "NICs" and i > 0: metrics["nics"] = str(raw_content[i-1]).strip()
        
        # Status detection
        if val_str in ["Down", "Critical", "Trouble", "Maintenance"]:
             metrics["status"] = val_str

    return metrics

def process_document(doc):
    """
    Extracts and combines text fields from a MongoDB document into a descriptive narrative.
    """
    title = doc.get("title", "Unknown Monitor")
    raw_content = doc.get("raw_content", [])
    
    # Extract Terminal Name from title (e.g. SPRH, CT2, CT3, CT4)
    terminal = "Unknown"
    for term in ["SPRH", "CT2", "CT3", "CT4"]:
         if term in title.upper():
              terminal = term
              break
              
    system = doc.get("system", {})
    hostname = system.get("hostname", "Unknown Server")
    
    # Use Smart Extraction to get real metrics from raw_content
    metrics = smart_extract_metrics(raw_content)
    
    res = doc.get("resources", {})
    ram = res.get("ram_size", "N/A")
    cores = res.get("cpu_cores", "N/A")
    
    # Create a highly accurate narrative for the AI to read
    narrative = f"Status report for server {hostname} in the {terminal} terminal. "
    narrative += f"Current State: {metrics['status']}. Uptime: {metrics['uptime']}. "
    narrative += f"Hardware: {cores} CPU cores, {ram} total RAM, and {metrics['nics']} network interfaces (NICs). "
    narrative += f"Utilization: CPU usage is {metrics['cpu']}, memory usage is {metrics['memory']}, and disk usage is {metrics['disk']}. "
    narrative += f"Processes: {metrics['processes']} processes are currently running. "
    narrative += f"Operating System: {system.get('os_name', 'N/A')} {system.get('os_version', 'N/A')}. "
    narrative += f"Full Title: {title}."
    
    return narrative, terminal, hostname

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
        
        # Process text and metadata
        doc_text, terminal, hostname = process_document(doc)
        documents_texts.append(doc_text)
        
        # Create enhanced metadata
        metadatas.append({
            "title": doc.get("title", "Unknown"),
            "terminal": terminal,
            "hostname": hostname,
            "url": doc.get("url", "Unknown"),
            "timestamp": str(doc.get("timestamp", ""))
        })

    print(f"Generating semantic embeddings for {len(documents_texts)} documents...")
    # Generate embeddings
    embeddings = model.encode(documents_texts).tolist()

    print(f"Adding to ChromaDB (Terminal tagging: {[m['terminal'] for m in metadatas[:1]]})...")
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
