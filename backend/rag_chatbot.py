import requests
from embedding_pipeline import model as embedding_model
from chroma_store import query_chroma
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

def get_answer(question: str) -> str:
    """
    Takes a user question, retrieves context from ChromaDB, and generates an answer using Ollama.
    """
    print(f"Question: {question}")
    
    # 1. Embed the question
    question_embedding = embedding_model.encode([question]).tolist()[0]
    
    # 2. Search ChromaDB
    print("Searching ChromaDB...")
    # Reduced n_results to 3 to prevent potential OOM/runner crashes
    results = query_chroma(question_embedding, n_results=3)
    
    # Extract the retrieved document texts
    retrieved_documents = results.get('documents', [[]])[0]
    
    if not retrieved_documents:
         context_text = "No relevant context found."
    else:
         context_text = "\n\n---\n\n".join(retrieved_documents)
         # Truncate context if it's too long to prevent runner crashes
         if len(context_text) > 8000:
             context_text = context_text[:8000] + "... [Context Truncated]"
         
    # 3. Construct the Prompt Template
    prompt = f"""You are a system monitoring assistant.

Use the following monitoring data to answer the user's question.

Monitoring Data Context:
{context_text}

User Question:
{question}

Provide a clear and accurate answer based only on the monitoring data."""

    # 4. Query Ollama
    print("Querying Ollama...")
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    start_time = time.time()  # Start the timer
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        end_time = time.time()  # End the timer
        duration = end_time - start_time
        
        if response.status_code != 200:
            print(f"Ollama error {response.status_code}: {response.text}")
            print(f"Time taken (failed): {duration:.2f} seconds")
            return f"Error from Ollama ({response.status_code}): {response.text}"
            
        # Display the timing in the terminal
        if duration >= 60:
            minutes = duration // 60
            seconds = duration % 60
            print(f"Chatbot give answer in {int(minutes)} min {int(seconds)} sec")
        else:
            print(f"Chatbot give answer in {duration:.2f} seconds")

        data = response.json()
        return data.get("response", "Error: No response from model.")
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"Connection error: {e}")
        print(f"Time taken (error): {duration:.2f} seconds")
        return f"Sorry, I encountered an error connecting to the language model: {str(e)}"
