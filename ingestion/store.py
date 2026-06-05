from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid

client = QdrantClient(host="localhost", port=6333)
COLLECTION = "agentic_rag"

def init_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

def store(chunks: list[dict], embeddings: list[list[float]]):
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings[i],
            payload=chunks[i]
        )
        for i in range(len(chunks))
    ]
    client.upsert(collection_name=COLLECTION, points=points)

def search(query_vector: list[float], top_k: int = 5) -> list[dict]:
    results = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k
    ).points
    return [r.payload for r in results]
