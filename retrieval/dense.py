from ingestion.embedder import embed
from ingestion.store import search

def dense_search(query: str, top_k: int = 5) -> list[dict]:
    query_vector = embed([query])[0]
    return search(query_vector, top_k)
