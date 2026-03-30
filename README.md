# ADBOT - AI Monitoring Assistant

ADBOT is a high-performance RAG (Retrieval-Augmented Generation) chatbot system integrated with a web scraping engine. It extracts structured monitoring data via a Chrome extension, processes it with FastAPI, and enables semantic querying using **Groq Cloud API** and **Llama 3.1**.

## 🌟 Key Features
- **High-Speed RAG Chatbot**: Powered by **Groq Cloud** for near-instant responses (sub-second latency).
- **Llama 3.1 8B/70B**: Uses the latest state-of-the-art Meta models for accurate system analysis.
- **Customized ADBOT UI**: Features a modern, blue-to-pink gradient interface with real-time "searching" animations.
- **Web Scraper (Chrome Extension)**: Extract server data and save directly to MongoDB Atlas.
- **Backend Response Timer**: Logs the exact time taken to generate an answer directly in your terminal.
- **Persistent Knowledge**: Data is embedded once into a vector database (ChromaDB) for instant retrieval.

---

## 🚀 1. Backend & Chatbot Setup

### Prerequisites
- **Python 3.10+** installed
- **[MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)** account (uses `scraper_db.scraped_data` by default)
- **[Groq Cloud API Key](https://console.groq.com/keys)** (Free tier available)

### Setup Instructions
1. **Navigate to the Backend**:
   ```bash
   cd backend
   ```
2. **Setup Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Create a `.env` file in the `backend/` folder:
   ```env
   MONGODB_URI="mongodb+srv://<username>:<password>@cluster0.ftgbsda.mongodb.net/?appName=Cluster0"
   LLM_API_BASE_URL="https://api.groq.com/openai/v1/chat/completions"
   OLLAMA_API_KEY="your_gsk_api_key_here"
   MODEL_NAME="llama-3.1-8b-instant"
   ```

---

## 🧠 2. Running the AI Pipeline

### A. Embedding Data (Run Once)
You only need to run this command when you have **new data** in MongoDB. It generates semantic embeddings and stores them in ChromaDB.
```bash
python embedding_pipeline.py
```

### B. Start the Backend API
```bash
uvicorn main:app --reload
```
*The API runs at `http://localhost:8000`.*

---

## 🎨 3. Using the ADBOT Dashboard

1. **Open the UI**: Open `frontend/index.html` in your browser.
2. **ADBOT Interface**: You will see the new gradient header and white chat bubbles for your questions.
3. **Ask Questions**: Ask about CPU, Memory, or Disk metrics.
4. **Interaction**: The "Send" button will show an animated searching symbol while the AI generates its answer.

---

## 🧩 4. Extension Setup (Web Scraper)

1. Open **Chrome Extensions** (`chrome://extensions/`).
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `extension` folder.
4. Click the extension icon on any monitoring webpage to **Extract & Send Data**.

---

## 🛠 Tech Stack Details
- **Frontend**: HTML5, Vanilla CSS, JavaScript.
- **Backend**: FastAPI (Python).
- **LLM**: Meta Llama 3.1 via **Groq Cloud API**.
- **Vector DB**: ChromaDB for semantic retrieval.
- **Main DB**: MongoDB Atlas for raw monitoring data.
- **Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2).

---

## 🧹 Managing the Repository
- **Security**: The `.env` file is ignored by Git to prevent API key leaks.
- **Logs**: Backend logs are stored in `debug_chatbot.log`.
