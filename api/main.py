import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ingestion.loader import load
from ingestion.chunker import chunk
from ingestion.embedder import embed
from ingestion.store import init_collection, store
from retrieval.bm25 import build_index
from agent.agent import answer

app = FastAPI()
_chunks = []

class IngestRequest(BaseModel):
    filepath: str

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def index():
    return FileResponse("api/index.html")

@app.on_event("startup")
def startup():
    global _chunks
    init_collection()
    if os.path.exists("corpus"):
        for filename in os.listdir("corpus"):
            if filename.endswith(".txt"):
                doc = load(f"corpus/{filename}")
                chunks = chunk(doc)
                _chunks.extend(chunks)
        build_index(_chunks)
        print(f"loaded {len(_chunks)} chunks into BM25 index")

@app.post("/ingest")
def ingest(req: IngestRequest):
    global _chunks
    doc = load(req.filepath)
    _chunks = chunk(doc)
    embeddings = embed([c["text"] for c in _chunks])
    store(_chunks, embeddings)
    build_index(_chunks)
    return {"status": "ok", "chunks": len(_chunks)}

@app.post("/query")
def query(req: QueryRequest):
    result = answer(req.query, _chunks)
    return result
