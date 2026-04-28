from fastapi import FastAPI, HTTPException # v1.0.1
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

from parsers import parse_dashboard_monitors

@app.post("/api/data")
async def save_scraped_data(data: ScrapedDataInput):
    try:
        # Prepare the document for MongoDB insertion
        new_document = data.model_dump()
        current_time = datetime.utcnow()
        new_document["timestamp"] = current_time
        
        # Parse dashboard monitors from the raw scraped content if present
        monitors = parse_dashboard_monitors(data.raw_content)
        new_document["dashboard_monitors"] = monitors
        
        # DE-DUPLICATION CHECK:
        # Find the most recent document with the same URL
        last_doc = await collection.find_one(
            {"url": data.url},
            sort=[("timestamp", -1)]
        )
        
        if last_doc:
            last_timestamp = last_doc.get("timestamp")
            # If the data is identical and saved less than 60 seconds ago, skip it
            # We compare raw_content and dashboard_monitors as primary indicators of change
            is_identical = (
                last_doc.get("raw_content") == data.raw_content and 
                last_doc.get("dashboard_monitors") == [m.model_dump() for m in monitors]
            )
            
            if is_identical and last_timestamp:
                time_diff = (current_time - last_timestamp).total_seconds()
                if time_diff < 60:
                    print(f"Duplicate data detected for {data.url} (saved {time_diff:.1f}s ago). Skipping insertion.")
                    return {
                        "message": "Duplicate data ignored (already saved recently)",
                        "inserted_id": str(last_doc["_id"]),
                        "status": "skipped"
                    }

        # Insert into MongoDB
        result = await collection.insert_one(new_document)
        
        print(f"Data extracted and saved successfully to MongoDB! Inserted ID: {result.inserted_id}")
        inserted_id = str(result.inserted_id)
        message = "Data saved as a new record successfully"

        return {
            "message": message,
            "inserted_id": inserted_id,
            "status": "saved"
        }
    except Exception as e:
        print(f"Error saving extracted data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")

from pydantic import BaseModel
from rag_chatbot import get_answer

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        answer = get_answer(request.question)
        return {"answer": answer}
    except Exception as e:
        print(f"Error generating chat response: {e}")
        raise HTTPException(status_code=500, detail="Error generating chat response.")
