import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List

from store import STORE
from parsers import parse_by_extension
from rag import index_document, retrieve
from llm_providers import available_models, call_llm


app = FastAPI(title="Document Reader API")

def parse_allowed_origins() -> List[str]:
    frontend_urls = os.getenv("FRONTEND_URLS", "")
    configured_urls = [origin.strip() for origin in frontend_urls.split(",") if origin.strip()]

    legacy_frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if legacy_frontend_url:
        configured_urls.append(legacy_frontend_url)

    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://index-8c1d0.web.app",
        "https://index-8c1d0.firebaseapp.com"
        *configured_urls,
    ]

allowed_origins = parse_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MIME_MAP = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "html": "text/html",
    "xml": "application/xml",
    "md": "text/markdown",
    "rtf": "application/rtf",
}

class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    filetype: str

class DocListItem(BaseModel):
    doc_id: str
    filename: str
    filetype: str

class ChatRequest(BaseModel):
    question: str
    model: str
    doc_ids: List[str]

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]

@app.get("/")
def root(request: Request):
    return {"ok": True, "docs": str(request.base_url) + "docs"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/models")
def get_models():
    return {"models": available_models()}

@app.post("/upload", response_model=List[UploadResponse])
async def upload_files(files: List[UploadFile] = File(...)):
    out = []
    for f in files:
        file_bytes = await f.read()
        filetype, text = parse_by_extension(f.filename, file_bytes)
        mime_type = MIME_MAP.get(filetype, "application/octet-stream")

        doc_id = STORE.add_document(
            filename=f.filename,
            filetype=filetype,
            full_text=text,
            raw_bytes=file_bytes,
            mime_type=mime_type,
        )
        index_document(doc_id, text)
        out.append(UploadResponse(doc_id=doc_id, filename=f.filename, filetype=filetype))
    return out

@app.get("/documents", response_model=List[DocListItem])
def list_docs():
    return [
        DocListItem(doc_id=d.doc_id, filename=d.filename, filetype=d.filetype)
        for d in STORE.documents.values()
    ]

@app.get("/documents/{doc_id}/preview")
def preview_doc(doc_id: str):
    d = STORE.documents.get(doc_id)
    if not d:
        return {"error": "not found"}
    return {"doc_id": doc_id, "filename": d.filename, "preview": d.full_text[:20000]}

@app.get("/documents/{doc_id}/file")
def get_file(doc_id: str):
    d = STORE.documents.get(doc_id)
    if not d:
        return {"error": "not found"}
    return Response(content=d.raw_bytes, media_type=d.mime_type)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    contexts = retrieve(req.doc_ids, req.question, top_k=6)
    context_text = "\n\n".join([f"[{i+1}] {c[1]}" for i, c in enumerate(contexts)])

    system = (
        "You are Document Reader. Answer using ONLY the provided context. "
        "If the answer is not in the context, say you don't have enough information."
    )
    user = f"CONTEXT:\n{context_text}\n\nQUESTION:\n{req.question}\n\nAnswer clearly."

    try:
        answer = call_llm(req.model, system, user)
    except RuntimeError as e:
        msg = str(e).encode("utf-8", "replace").decode("utf-8")
        raise HTTPException(status_code=500, detail=msg)
    except Exception as e:
        msg = str(e)
        msg = msg.encode("utf-8", "replace").decode("utf-8")
        raise HTTPException(status_code=500, detail=msg)

    sources = [{"doc_id": doc_id, "score": score, "snippet": txt[:260]} for doc_id, txt, score in contexts]
    return ChatResponse(answer=answer, sources=sources)
