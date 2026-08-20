# Vocalis AI - Business Loan Voice Agent

Vocalis AI is a unified full-stack platform featuring a Knowledge-Grounded Business Loan Voice Agent and a Text-based RAG Search. It seamlessly integrates a FastAPI backend with a custom Vapi AI voice assistant to automate loan qualification, answer policy questions, and store CRM leads.

## 🚀 Architecture & Pipeline Stack

### The Tech Stack
* **Frontend:** Vanilla HTML/JS styled with Tailwind CSS (Single Page Application)
* **Backend:** Python / FastAPI
* **Voice AI:** Vapi (OpenAI `gpt-4o`, Deepgram `nova-2` STT)
* **LLM / Generation:** Google Gemini (`gemini-3.5-flash-lite`) via Google Generative AI
* **Vector Database:** ChromaDB
* **Embeddings:** BAAI/bge-small-en-v1.5 (Sentence Transformers)
* **Reranker:** BAAI/bge-reranker-base (CrossEncoder)
* **Data Extraction:** Unstructured (PDFs), BeautifulSoup (Web), Pandas (CSV/Excel)
* **CRM Database:** SQLite

### The RAG Pipeline (Retrieval-Augmented Generation)
1. **Ingestion:** Files (PDF, TXT, CSV) are uploaded via the UI to `data/raw/`.
2. **Processing:** Data is parsed, PII is redacted (spaCy + regex), and content is deduplicated.
3. **Chunking & Embedding:** Text is semantically chunked and embedded using the BGE model.
4. **Storage:** Vectors are stored locally in ChromaDB.
5. **Retrieval:** User queries undergo Hybrid Retrieval (Vector + TF-IDF) to fetch the top documents.
6. **Reranking:** The BGE Cross-Encoder reranks the results for maximum relevance.
7. **Synthesis:** Gemini evaluates the context. If it's grounded, it synthesizes an answer. If not, it safely escalates to a human.

---

## 🛠️ Local Setup Instructions

### 1. Environment & Dependencies
Clone the repository and install the dependencies:
```bash
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configuration
Create a `.env` file in the root directory and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: Your Vapi Public Key and Assistant IDs are configured securely inside the `index.html` file.)*

### 3. Run the Application
Start the FastAPI server (which also serves the frontend UI):
```bash
python -m uvicorn api.main:app --port 8000
```
Open your browser and navigate to: `http://localhost:8000`

---

## 🌍 Deployment Guide (Render vs Vercel)

> **⚠️ CRITICAL WARNING FOR VERCEL:** Vercel uses a **Serverless, Read-Only File System**. Because this application uses local SQLite and ChromaDB to save uploaded knowledge base files, **Vercel will block database writes and uploads will fail.** 
> **It is highly recommended to deploy this stateful Python app on [Render.com](https://render.com) (as a Web Service) or Railway** so the database and file uploads work properly!

### Deploying on Render (Recommended)
1. Push this repository to GitHub.
2. Go to Render.com and create a new **Web Service**.
3. Connect your GitHub repository.
4. **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
5. **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
6. Click Deploy!

### Updating Vapi Custom Tools (Post-Deployment)
Once your app is live on the internet (e.g., `https://vocalis-ai.onrender.com`):
1. Go to your **Vapi Dashboard** -> **Assistants**.
2. Click your **Q1 Voice Agent** and scroll down to the **Tools** section.
3. Edit the `search_knowledge` tool and set the Server URL to: `https://your-app-url.com/vapi/search`
4. Edit the `create_lead` tool and set the Server URL to: `https://your-app-url.com/vapi/create-lead`
5. Save the assistant! Your Voice AI is now fully connected to your live database.
