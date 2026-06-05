import anthropic

client = anthropic.Anthropic()

GENERATE_PROMPT = """You are a precise technical assistant answering questions about FastAPI.
Use ONLY the provided context. Be concise and direct.

Rules:
- Answer in 3-5 sentences maximum for explanations
- Include ONE focused code example if relevant
- No lengthy introductions or summaries
- No "Based on the provided context" — just answer directly

Context:
{context}

Query: {query}

Answer:"""

def generate(query: str, chunks: list[dict]) -> str:
    context = "\n\n".join([c["text"] for c in chunks])
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": GENERATE_PROMPT.format(
            context=context,
            query=query
        )}]
    )
    return message.content[0].text.strip()
