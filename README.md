# ADBOT - AI Monitoring Assistant

ADBOT is a high-performance RAG (Retrieval-Augmented Generation) chatbot system integrated with a web scraping engine. It extracts structured monitoring data via a Chrome extension, processes it with FastAPI, and enables semantic querying using local LLMs.

## 🌟 Key Features
- **Intelligent RAG Chatbot**: Uses ChromaDB and Ollama to answer questions based on your system metrics.
- **Customized ADBOT UI**: Features a modern, blue-to-pink gradient interface with real-time "searching" animations.
- **Web Scraper (Chrome Extension)**: Extract server data and save directly to MongoDB Atlas.
- **Backend Response Timer**: Logs the exact time taken to generate an answer directly in your terminal.
- **Persistent Knowledge**: Data is embedded once into a vector database for instant retrieval.

---

## 🚀 1. Backend & Chatbot Setup

### Prerequisites
- **Python 3.10+** installed
- **[MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)** account (uses `scraper_db.scraped_data` by default)
- **[Ollama](https://ollama.com/)** installed locally

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
   ```

---

## 🧠 2. Running the AI Pipeline

### A. Ollama Configuration (Important)
If your **C: drive is full**, move your AI models to another drive (e.g., E:):
1. Create `E:\OllamaModels`.
2. Set Environment Variable: `OLLAMA_MODELS = "E:\OllamaModels"`.
3. Restart Ollama and run:
   ```bash
   ollama pull llama3
   ```

### B. Embedding Data (Run Once)
You only need to run this command when you have **new data** in MongoDB. It generates semantic embeddings and stores them in ChromaDB.
```bash
python embedding_pipeline.py
```

### C. Start the Backend API
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

## 🛠 Troubleshooting
- **Speed Optimization**: If answers take too long (e.g., several minutes), we use **`llama3.2:1b`**, which is optimized for fast performance on standard consumer hardware.
- **Memory Errors**: If you get "unable to allocate CPU buffer," ensure you follow the E: drive workaround or use the lightweight 1B model.
- **Page Refresh**: The chat interface uses form-submission handling to prevent the page from refreshing when you press Enter.
- **Disk Space**: Ensure you have at least 5GB free on the drive where Ollama models are stored.
