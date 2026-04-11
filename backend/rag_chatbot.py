import requests
from embedding_pipeline import model as embedding_model
from chroma_store import query_chroma
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LLM_API_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:11434/api/generate")
LLM_API_KEY = os.getenv("OLLAMA_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.1")

def get_answer(question: str) -> str:
    """
    Takes a user question, retrieves context from ChromaDB using smart filtering, 
    and generates an accurate answer using an LLM API.
    """
    print(f"Question: {question}")
    
    # 1. Detect Terminal for Smart Filtering
    terminal_filter = None
    for term in ["SPRH", "CT2", "CT3", "CT4"]:
        if term in question.upper():
            terminal_filter = term
            print(f"Detected filter for Terminal: {terminal_filter}")
            break
            
    # 2. Embed the question
    question_embedding = embedding_model.encode([question]).tolist()[0]
    
    # 3. Search ChromaDB with optional filtering
    print("Searching ChromaDB...")
    
    # Use metadata filter if a terminal was detected
    where_clause = {"terminal": terminal_filter} if terminal_filter else None
    
    # If filtered, we can afford more results (up to 10) for better accuracy.
    # If not filtered, we keep it lower to avoid token overflow.
    n_results = 10 if terminal_filter else 5
    
    results = query_chroma(question_embedding, n_results=n_results, where=where_clause)
    
    # Extract the retrieved document texts and metadatas
    retrieved_documents = results.get('documents', [[]])[0]
    retrieved_metadatas = results.get('metadatas', [[]])[0]
    
    if not retrieved_documents:
         context_text = "No relevant context found."
    else:
         context_chunks = []
         for doc, meta in zip(retrieved_documents, retrieved_metadatas):
             timestamp = meta.get("timestamp", "Unknown Date")
             context_chunks.append(f"--- Data Point ({timestamp}) ---\n{doc}")
         
         context_text = "\n\n".join(context_chunks)
         # Truncate context if it's too long
         if len(context_text) > 4000:
             context_text = context_text[:4000] + "... [Context Truncated]"
         
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. Construct the Prompt Template
    prompt = f"""You are a system monitoring assistant for the Adani terminals.
Current Server Time: {current_time}

Use the following monitoring data context to answer the user's question accurately.

Monitoring Data Context:
{context_text}

User Question:
{question}

Provide a clear and accurate answer based only on the monitoring data provided."""

    # 5. Query LLM API
    print(f"Querying LLM API ({MODEL_NAME})...")
    
    # Check if we are using an OpenAI-compatible endpoint
    is_openai_compatible = "/v1/chat/completions" in LLM_API_URL
    
    if is_openai_compatible:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant specialized in system monitoring."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }
    else:
        # Default to Ollama format if not OpenAI-compatible
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        headers = {}
    
    start_time = time.time()
    try:
        response = requests.post(LLM_API_URL, json=payload, headers=headers)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code != 200:
            print(f"API error {response.status_code}: {response.text}")
            return f"Error from LLM API ({response.status_code}): {response.text}"
            
        print(f"Chatbot answered in {duration:.2f} seconds")
        data = response.json()
        
        if is_openai_compatible:
            return data.get("choices", [{}])[0].get("message", {}).get("content", "Error: No response content.")
        else:
            return data.get("response", "Error: No response from model.")
            
    except Exception as e:
        print(f"Connection error: {e}")
        return f"Sorry, I encountered an error connecting to the language model: {str(e)}"
