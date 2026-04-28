import requests
from embedding_pipeline import model as embedding_model
from chroma_store import query_chroma
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LLM_API_URL = os.getenv("LLM_API_BASE_URL")
LLM_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

if not LLM_API_URL or not LLM_API_KEY:
    print("Warning: LLM_API_BASE_URL or GROQ_API_KEY not set in .env")

def preprocess_query(query: str) -> dict:
    """
    Detects the language and provides an English translation for better RAG retrieval.
    """
    try:
        print(f"Detecting language for: {query}")
    except UnicodeEncodeError:
        print(f"Detecting language for: {query.encode('ascii', 'ignore').decode('ascii')} (Non-ASCII characters ignored for terminal)")
    
    # Check if we are using an OpenAI-compatible endpoint
    is_openai_compatible = "/v1/chat/completions" in LLM_API_URL
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system", 
                "content": "You are a language detection assistant. Respond ONLY with a JSON object containing 'language' (the name of the language) and 'english_translation' (an accurate English translation of the query for search purposes). If the query is already in English, the translation should be the same as the query."
            },
            {"role": "user", "content": query}
        ],
        "response_format": { "type": "json_object" } if is_openai_compatible else None,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    } if is_openai_compatible else {}

    try:
        response = requests.post(LLM_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if is_openai_compatible:
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            else:
                content = data.get("response", "{}")
            
            # Extract JSON from content if it's a string
            if isinstance(content, str):
                try:
                    # Strip markdown code blocks if present
                    if content.startswith("```json"):
                        content = content.replace("```json", "").replace("```", "").strip()
                    elif content.startswith("```"):
                        content = content.replace("```", "").strip()
                    result = json.loads(content)
                except:
                    result = {"language": "English", "english_translation": query}
            else:
                result = content
            
            print(f"Detected Language: {result.get('language')}, Translation: {result.get('english_translation')}")
            return result
    except Exception as e:
        print(f"Error in preprocessing: {e}")
    
    return {"language": "English", "english_translation": query}

def get_answer(question: str) -> str:
    """
    Takes a user question, retrieves context from ChromaDB using smart filtering, 
    and generates an accurate answer using an LLM API.
    """
    try:
        print(f"Original Question: {question}")
    except UnicodeEncodeError:
        print(f"Original Question: [Contains non-ASCII characters]")
    
    # 0. Preprocess Query (Language Detection & Translation)
    processed = preprocess_query(question)
    detected_lang = processed.get("language", "English")
    search_query = processed.get("english_translation", question)

    # 1. Detect Terminal for Smart Filtering
    terminal_filter = None
    for term in ["SPRH", "CT2", "CT3", "CT4", "T2"]:
        if term in search_query.upper():
            terminal_filter = term
            print(f"Detected filter for Terminal: {terminal_filter}")
            break
            
    # 2. Smart Scaling for n_results
    # If the user asks for counts or listings, we need to see more data points.
    n_results = 5
    if terminal_filter:
        n_results = 10
        
    summary_keywords = ["how many", "list", "total", "count", "all", "summary", "how much"]
    if any(kw in search_query.lower() for kw in summary_keywords):
        n_results = 50 # Increase to see the entire fleet
        print(f"Summary query detected. Increasing n_results to {n_results}")

    # 3. Embed the translation for search
    question_embedding = embedding_model.encode([search_query]).tolist()[0]
    
    # 4. Search ChromaDB with optional filtering
    print(f"Searching ChromaDB (n_results={n_results})...")
    
    # Use metadata filter if a terminal was detected
    where_clause = {"terminal": terminal_filter} if terminal_filter else None
    
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

The user is asking in {detected_lang}. You MUST respond in {detected_lang}.

Use the following monitoring data context to answer the user's question accurately. 
Note: The context is in English, but you must translate your findings into {detected_lang} for the user.

Monitoring Data Context:
{context_text}

User Question (Original):
{question}

User Question (English Translation for your reference):
{search_query}

Provide a clear and accurate answer based only on the monitoring data provided. Respond in {detected_lang}."""

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
