import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
"""FastAPI backend — RAG operations and Vapi webhooks."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv
import re
from urllib.parse import urlparse

from voice.tools import search_knowledge, create_lead
from ingestion.build_kb import main as build_kb_func
from ingestion.website_loader import load_website
from retrieval.retriever import retrieve
from generation.rag import answer
from retrieval.vector_store import reset as reset_db
from api.q4_router import router as q4_router

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vocalis API", version="1.0")

# Allow all origins so the HTML page can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(q4_router, prefix="/api/q4", tags=["Q4"])

class SearchRequest(BaseModel):
    question: str

class LeadRequest(BaseModel):
    qualification: dict

class UrlRequest(BaseModel):
    url: str

# ─── FRONTEND ──────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def get_index():
    index_path = Path("index.html")
    if not index_path.exists():
        return "<h1>Error: index.html not found</h1>"
    return index_path.read_text(encoding="utf-8")


@app.post("/")
def vapi_unified_root_webhook(request: dict):
    """Fallback handler for Vapi webhook calls hitting the root domain.
    
    If the user configured Vapi's Server URL to just the base domain (e.g. https://xxxx.ngrok-free.dev/),
    Vapi will POST to the root '/'. This route intercepts the payload, inspects the tool name,
    routes it to the correct function, and returns Vapi's required results schema.
    """
    logger.info(f"[VAPI ROOT POST] Received: {request}")
    try:
        message = request.get("message", request)
        msg_type = message.get("type")
        
        # If it's a tool-calls request, route dynamically based on function name
        if msg_type == "tool-calls":
            tool_call_list = message.get("toolCallList", [])
            results = []
            
            for tool_call in tool_call_list:
                tool_call_id = tool_call.get("id", "")
                func = tool_call.get("function", {})
                name = func.get("name", "")
                args = func.get("arguments", {})
                
                if name == "search_knowledge":
                    question = args.get("question", "")
                    if question:
                        response = search_knowledge(question)
                        result_text = response.get("answer", "I could not find an answer.")
                    else:
                        result_text = "No question was provided."
                        
                elif name == "create_lead":
                    qualification = args.get("qualification", args)
                    response = create_lead(qualification)
                    result_text = f"Lead saved successfully with ID {response.get('lead_id', 'unknown')}."
                    
                else:
                    result_text = f"Unknown tool: {name}"
                
                results.append({
                    "toolCallId": tool_call_id,
                    "result": result_text
                })
            
            return {"results": results}
        
        # Fallback for direct testing or non-tool call webhooks
        return {"status": "ignored", "message_type": msg_type}
    except Exception as e:
        logger.error(f"[VAPI ROOT POST] Error: {e}")
        return {"error": str(e)}


# ─── KNOWLEDGE BASE MGMT ───────────────────────────────────────

@app.post("/api/upload")
def upload_files(files: List[UploadFile] = File(...)):
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    for file in files:
        dest = raw_dir / file.filename
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    return {"message": f"Successfully uploaded {len(files)} files."}


@app.get("/api/files")
def list_files():
    import datetime
    raw_dir = Path("data/raw")
    if not raw_dir.exists():
        return {"files": []}
    files = []
    for f in raw_dir.iterdir():
        if f.is_file():
            stat = f.stat()
            time_str = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            files.append({"filename": f.name, "ingested_at": time_str})
    return {"files": files}


@app.post("/api/fetch-url")
def fetch_url(req: UrlRequest):
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    try:
        content = load_website(req.url)
        parsed = urlparse(req.url)
        domain = parsed.netloc
        path = parsed.path.strip('/').replace('/', '_')
        safe_name = f"web_{domain}_{path}.txt" if path else f"web_{domain}.txt"
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '', safe_name)
        
        dest = raw_dir / safe_name
        dest.write_text(content, encoding="utf-8")
        return {"message": f"URL Scraped & Saved as {safe_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/build")
def build_knowledge_base():
    try:
        build_kb_func()
        return {"message": "Knowledge base built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
def clear_data():
    raw_dir = Path("data/raw")
    if raw_dir.exists():
        for item in raw_dir.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except Exception:
                    pass
    try:
        reset_db()
    except Exception:
        pass
    
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        for item in processed_dir.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except Exception:
                    pass
    return {"message": "Data cleared"}


# ─── TEXT RAG CHAT ─────────────────────────────────────────────

@app.post("/api/chat")
def chat_rag(req: SearchRequest):
    kb_path = Path("data/processed/kb_records.json")
    if not kb_path.exists():
        raise HTTPException(status_code=400, detail="Knowledge base not built yet.")
    
    result = retrieve(req.question)
    if not result["grounded"]:
        return {
            "answer": "No sufficiently relevant verified information was found. Please contact human support.",
            "sources": []
        }
    
    response = answer(req.question, result["results"])
    return {
        "answer": response["answer"],
        "sources": response["sources"]
    }


# ─── VAPI WEBHOOKS ─────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/vapi/search")
def vapi_search(request: dict):
    """Handle Vapi's tool-call webhook for search_knowledge."""
    logger.info(f"[VAPI /vapi/search] Received: {request}")
    try:
        message = request.get("message", request)
        tool_call_list = message.get("toolCallList", [])
        
        results = []
        for tool_call in tool_call_list:
            tool_call_id = tool_call.get("id", "")
            args = tool_call.get("function", {}).get("arguments", {})
            question = args.get("question", "")
            
            if question:
                response = search_knowledge(question)
                result_text = response.get("answer", "I could not find an answer.")
            else:
                result_text = "No question was provided."
            
            results.append({
                "toolCallId": tool_call_id,
                "result": result_text
            })
        
        return {"results": results}
    except Exception as e:
        question = request.get("question", "")
        if question:
            return search_knowledge(question)
        return {"error": str(e)}
 
 
@app.post("/vapi/create-lead")
def vapi_create_lead(request: dict):
    """Handle Vapi's tool-call webhook for create_lead."""
    try:
        message = request.get("message", request)
        tool_call_list = message.get("toolCallList", [])
        
        results = []
        for tool_call in tool_call_list:
            tool_call_id = tool_call.get("id", "")
            args = tool_call.get("function", {}).get("arguments", {})
            qualification = args.get("qualification", args)
            
            response = create_lead(qualification)
            results.append({
                "toolCallId": tool_call_id,
                "result": f"Lead saved successfully with ID {response.get('lead_id', 'unknown')}."
            })
        
        return {"results": results}
    except Exception as e:
        qualification = request.get("qualification", {})
        if qualification:
            return create_lead(qualification)
        return {"error": str(e)}
