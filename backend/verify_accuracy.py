import asyncio
import os
from embedding_pipeline import model as embedding_model
from chroma_store import query_chroma
from dotenv import load_dotenv

load_dotenv()

async def verify_final_accuracy():
    print("Testing Smart Retrieval for 'MU02LSPRHKAFKP1 CPU'...")
    
    question = "What is the CPU utilization and Uptime of MU02LSPRHKAFKP1?"
    embedding = embedding_model.encode([question]).tolist()[0]
    
    # Try to find it
    results = query_chroma(embedding, n_results=1, where={"hostname": "MU02LSPRHKAFKP1"})
    
    docs = results.get('documents', [[]])[0]
    if docs:
        print("\nRetrieved Narrative Context:")
        print("-" * 30)
        print(docs[0])
        print("-" * 30)
        
        if "CPU usage is 7.94%" in docs[0] and "Uptime: 56 day(s)" in docs[0]:
            print("\nSUCCESS: The smart extraction correctly found the CPU and Uptime in the narrative!")
        else:
            print("\nWARNING: Metrics might be missing or formatted differently. Check the narrative output above.")
    else:
        print("No documents found for MU02LSPRHKAFKP1.")

if __name__ == "__main__":
    asyncio.run(verify_final_accuracy())
