from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ScrapedDataInput
from database import collection
from datetime import datetime

app = FastAPI(title="Web Scraper API")

# Enable CORS so the Chrome extension can send requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific origins if necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Web Scraper API is running. Send POST requests to /api/data"}

@app.post("/api/data")
async def save_scraped_data(data: ScrapedDataInput):
    try:
        # Prepare the document for MongoDB insertion
        document = data.model_dump()
        document["timestamp"] = datetime.utcnow()
        
        # Insert into MongoDB
        result = await collection.insert_one(document)
        

        return {
            "message": "Data saved successfully",
            "inserted_id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")
