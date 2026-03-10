from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from store import STORE, Chunk

_EMBED_MODEL = None

def get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL

def chunk_text(text: str, chunk_size_words: int = 800, overlap_words: int = 120) -> List[str]:
    if not text:
        return []
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size_words)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = max(0, end - overlap_words)
        if end == len(words):
            break
    return chunks

def index_document(doc_id: str, full_text: str) -> None:
    texts = chunk_text(full_text)
    if not texts:
        STORE.embeddings[doc_id] = np.zeros((0, 384), dtype=np.float32)
        STORE.chunks[doc_id] = []
        return

    embed_model = get_embed_model()
    vectors = embed_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    STORE.embeddings[doc_id] = vectors
    STORE.chunks[doc_id] = [
        Chunk(doc_id=doc_id, chunk_id=str(i), text=t) for i, t in enumerate(texts)
    ]

def retrieve(doc_ids: List[str], query: str, top_k: int = 6) -> List[Tuple[str, str, float]]:
    embed_model = get_embed_model()
    qv = embed_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)[0]

    results = []

    for doc_id in doc_ids:
        vecs = STORE.embeddings.get(doc_id)
        chunks = STORE.chunks.get(doc_id, [])
        if vecs is None or vecs.shape[0] == 0:
            continue

        scores = vecs @ qv
        idxs = np.argsort(scores)[::-1][:top_k]
        for idx in idxs:
            results.append((doc_id, chunks[int(idx)].text, float(scores[int(idx)])))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]