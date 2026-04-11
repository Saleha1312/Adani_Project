import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def find_metric_patterns():
    MONGO_URI = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["scraper_db"]
    collection = db["scraped_data"]
    
    # Check 5 documents to see if patterns are consistent
    cursor = collection.find({}).limit(5)
    
    async for doc in cursor:
        print(f"\n--- Server: {doc.get('system', {}).get('hostname', 'Unknown')} ---")
        raw = doc.get("raw_content", [])
        
        # Look for CPU value
        for i, val in enumerate(raw):
            if val == "CPU" and i > 1 and raw[i-1] == "%":
                print(f"Found CPU Value: {raw[i-2]} (at index {i-2})")
            if val == "Memory" and i > 1 and raw[i-1] == "%":
                print(f"Found Memory Value: {raw[i-2]} (at index {i-2})")
            if val == "Disk" and i > 1 and raw[i-1] == "%":
                print(f"Found Disk Value: {raw[i-2]} (at index {i-2})")
            if "Uptime" in val:
                print(f"Found Uptime String: {val}")
            if "NICs" in val or "Processes" in val:
                 print(f"Server Stats: {raw[i-1]} {val}")

if __name__ == "__main__":
    asyncio.run(find_metric_patterns())
