from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import time
import uuid

@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    text: str

@dataclass
class Document:
    doc_id: str
    filename: str
    filetype: str
    uploaded_at: float
    full_text: str
    raw_bytes: bytes
    mime_type: str

class InMemoryStore:
    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, List[Chunk]] = {}
        self.embeddings: Dict[str, np.ndarray] = {}  # doc_id -> (num_chunks, dim)

    def add_document(self, filename: str, filetype: str, full_text: str, raw_bytes: bytes, mime_type: str) -> str:
        doc_id = str(uuid.uuid4())
        self.documents[doc_id] = Document(
            doc_id=doc_id,
            filename=filename,
            filetype=filetype,
            uploaded_at=time.time(),
            full_text=full_text,
            raw_bytes=raw_bytes,
            mime_type=mime_type,
        )
        self.chunks[doc_id] = []
        return doc_id

STORE = InMemoryStore()
