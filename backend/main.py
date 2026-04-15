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
        document = data.model_dump()
        document["timestamp"] = datetime.utcnow()
        
        # Parse dashboard monitors from the raw scraped content if present
        monitors = parse_dashboard_monitors(data.raw_content)
        document["dashboard_monitors"] = monitors
        
        # Insert into MongoDB as a new separate document every time
        result = await collection.insert_one(document)
        
        print(f"Data extracted and saved successfully to MongoDB! Inserted ID: {result.inserted_id}")
        inserted_id = str(result.inserted_id)
        message = "Data saved as a new record successfully"

        return {
            "message": message,
            "inserted_id": inserted_id
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
