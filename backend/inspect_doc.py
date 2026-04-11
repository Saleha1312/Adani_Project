import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def inspect_document():
    MONGO_URI = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["scraper_db"]
    collection = db["scraped_data"]
    
    doc = await collection.find_one({})
    print(f"Document Structure:\n{json.dumps(doc, indent=2, default=str)}")

if __name__ == "__main__":
    asyncio.run(inspect_document())
