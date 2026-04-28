from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")

if not MONGO_URI or "<db_password>" in MONGO_URI:
    print("WARNING: MONGODB_URI is not set correctly in .env or still contains '<db_password>' placeholder.")
    # Fallback to local only if absolutely necessary, but we want the user to fix the URI
    if not MONGO_URI:
        MONGO_URI = "mongodb://localhost:27017"

try:
    # Use a longer timeout for Atlas connections
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.scraper_db
    collection = db.scraped_data
    
    # Test connection
    print(f"Connecting to MongoDB: {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI}")
except Exception as e:
    print(f"Error initializing MongoDB client: {e}")
