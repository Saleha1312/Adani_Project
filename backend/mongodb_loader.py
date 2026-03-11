import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["scraper_db"]
collection = db["scraped_data"]

async def load_all_documents():
    """
    Load all documents from the monitoring_db.monitors_data collection.
    Returns a list of dictionaries.
    """
    cursor = collection.find({})
    documents = []
    async for doc in cursor:
        documents.append(doc)
    return documents

async def load_recent_documents(limit=100):
    """
    Load the most recent documents.
    """
    cursor = collection.find({}).sort("timestamp", -1).limit(limit)
    documents = []
    async for doc in cursor:
        documents.append(doc)
    return documents
