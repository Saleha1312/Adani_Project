# Web Scraper Plugin and FastAPI Backend

This project consists of two components:
1. A **Chrome Extension** (plugin) that extracts structured data (URL, titles, headings, and links) from any active web page.
2. A **FastAPI Backend** that receives this JSON data and stores it in a **MongoDB Atlas** database.

---

## 🚀 1. Backend Setup

### Prerequisites
You will need Python installed on your machine and a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster account.

### Instructions
1. Navigate to the `backend` directory in your terminal:
   ```bash
   cd c:\Users\caelumpirata\Desktop\Adani_project\web_scraper_project\backend
   ```
2. (Optional but recommended) Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your Environment Variables:
   - Rename the `.env.example` file to `.env` (or create a new `.env` file).
   - Get the connection string from your MongoDB Atlas dashboard.
   - Edit the `.env` file and set the `MONGODB_URI` variable:
     ```
     MONGODB_URI="mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/myDatabase?retryWrites=true&w=majority"
     ```
5. Run the FastAPI Server:
   ```bash
   uvicorn main:app --reload
   ```
   *The API should now be running locally at `http://localhost:8000`.*

---

## 🧩 2. Extension Setup

1. Open **Google Chrome**.
2. Type `chrome://extensions/` in the URL bar and press Enter.
3. Turn on **Developer mode** (the toggle switch in the top right corner).
4. Click the **Load unpacked** button in the top left.
5. In the file dialog, select the `extension` folder located inside this project:
   `c:\Users\caelumpirata\Desktop\Adani_project\web_scraper_project\extension`

---

## 🎯 Usage

1. Ensure your FastAPI server is running (`uvicorn main:app`).
2. Open any webpage you want to scrape in Google Chrome.
3. Click the **Web Scraper** extension icon in your Chrome toolbar (it might be shaped like a puzzle piece if you haven't pinned it).
4. Click the **Extract & Send Data** button.
5. You should see a "Success" message in the popup.
6. Check your FastAPI terminal console and your MongoDB Atlas database collection to see the saved data!
