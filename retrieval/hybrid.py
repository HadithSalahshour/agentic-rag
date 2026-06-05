from retrieval.dense import dense_search
from retrieval.bm25 import bm25_search

def rrf(dense_hits: list[dict], bm25_hits: list[dict], k: int = 60) -> list[dict]:
    scores = {}
    all_chunks = {}

    for rank, chunk in enumerate(dense_hits):
        key = chunk["text"]
        scores[key] = scores.get(key, 0) + 1 / (rank + k)
        all_chunks[key] = chunk

    for rank, chunk in enumerate(bm25_hits):
        key = chunk["text"]
        scores[key] = scores.get(key, 0) + 1 / (rank + k)
        all_chunks[key] = chunk

    ranked = sorted(scores, key=scores.get, reverse=True)
    return [all_chunks[key] for key in ranked]

def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    dense_hits = dense_search(query, top_k)
    bm25_hits = bm25_search(query, top_k)
    return rrf(dense_hits, bm25_hits)[:top_k]
