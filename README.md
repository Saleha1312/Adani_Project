<<<<<<< HEAD
# Web Scraper Plugin & RAG Chatbot

This project consists of three main components:
1. A **Chrome Extension** (plugin) that extracts structured monitoring data from web pages.
2. A **FastAPI Backend** that receives this JSON data, stores it in **MongoDB Atlas**, and serves a RAG-based AI chatbot using **ChromaDB** and **Ollama**.
3. A **Chat UI Frontend** that lets you ask questions to an AI assistant about your saved server metrics.

---

## 🚀 1. Backend & Chatbot Setup

### Prerequisites
- Python 3 installed
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster account
  - **Important Note:** Both the web scraper and chatbot use the `scraper_db` database and `scraped_data` collection by default.
- [Ollama](https://ollama.com/) installed locally to run the LLM

### Instructions
1. Navigate to the `backend` directory in your terminal:
   ```bash
   cd backend
   ```
2. Create and activate a Virtual Environment (Recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate # Mac/Linux
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your Environment Variables:
   - Create a `.env` file in the `backend/` folder.
   - Add your connection string:
     ```
     MONGODB_URI="mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?appName=Cluster0"
     ```
5. Ensure Ollama is running and has the `llama3` model pulled:
   ```bash
   ollama serve
   # In another terminal:
   ollama pull llama3
   ```
6. **Initialize the Vector Database**: Run the embedding pipeline once to load data from MongoDB into ChromaDB.
   ```bash
   python embedding_pipeline.py
   ```
7. Run the FastAPI Server:
   ```bash
   uvicorn main:app --reload
   ```
   *The API should now be running locally at `http://localhost:8000`.*

---

## 🧩 2. Extension Setup (Web Scraper)

1. Open **Google Chrome**.
2. Type `chrome://extensions/` in the URL bar and press Enter.
3. Turn on **Developer mode** (top right corner).
4. Click **Load unpacked** (top left).
5. Select the `extension` folder located inside this project.
6. Open any monitoring page, click the extension icon, and click **Extract & Send Data**. It will automatically save to your MongoDB collection!

---

## 🤖 3. Using the AI Chatbot

1. Ensure the Python backend (`uvicorn main:app`) and Ollama (`ollama serve`) are both running.
2. Open the file `frontend/index.html` in any web browser.
3. You will see the **System Monitor AI** chat interface.
4. Ask it questions about your scraped monitoring data, for example:
   - *"What is the CPU usage status?"*
   - *"Show me the disk partition details."*
5. The AI will retrieve the most relevant data from your MongoDB database and provide an answer!
=======
# Adani_Project
AI-powered web intelligence system that extracts webpage data via a browser extension (HTML, CSS, JS). Data is processed with FastAPI and stored in MongoDB Atlas. ChromaDB converts data into vector embeddings for semantic analysis. A trained LLM detects anomalies from historical and real-time data, visualized through a time-based dashboard.
>>>>>>> 7ec89c3ddb0f71c30684102725e5740aee349269
