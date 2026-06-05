from agent.router import route
from agent.generator import generate
from agent.critique import critique
from retrieval.hybrid import hybrid_search
from retrieval.bm25 import build_index
from ingestion.loader import load
from ingestion.chunker import chunk
import anthropic

client = anthropic.Anthropic()

def answer(query: str, chunks: list[dict], max_iterations: int = 3) -> dict:
    route_label = route(query)

    if route_label == "direct":
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": query}]
        )
        return {
            "answer": message.content[0].text.strip(),
            "route": "direct",
            "iterations": 0,
            "critique": None
        }

    retrieved = hybrid_search(query)
    
    for i in range(max_iterations):
        response = generate(query, retrieved)
        result = critique(response, retrieved)
        
        if result["passed"]:
            return {
                "answer": response,
                "route": route_label,
                "iterations": i + 1,
                "critique": result["results"]
            }
        
        unsupported = [r["sentence"] for r in result["results"] if r["score"] == "not_supported"]
        refined_query = unsupported[0] if unsupported else query
        extra = hybrid_search(refined_query)
        retrieved = retrieved + extra

    return {
        "answer": response,
        "route": route_label,
        "iterations": max_iterations,
        "critique": result["results"]
    }
