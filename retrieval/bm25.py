from rank_bm25 import BM25Okapi
from ingestion.loader import load
from ingestion.chunker import chunk

_index = None
_chunks = []

def build_index(chunks: list[dict]):
    global _index, _chunks
    _chunks = chunks
    tokenized = [c["text"].lower().split() for c in chunks]
    _index = BM25Okapi(tokenized)

def bm25_search(query: str, top_k: int = 5) -> list[dict]:
    if _index is None:
        raise RuntimeError("BM25 index not built. Call build_index first.")
    tokens = query.lower().split()
    scores = _index.get_scores(tokens)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [_chunks[i] for i in top_indices]
