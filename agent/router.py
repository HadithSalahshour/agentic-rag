import anthropic

client = anthropic.Anthropic()

ROUTER_PROMPT = """You are an assistant with access to FastAPI documentation.
Classify this query into exactly one of: direct, retrieve, multi_hop

direct     → general programming knowledge, not specific to FastAPI docs
retrieve   → requires looking up specific FastAPI documentation
multi_hop  → requires chaining across multiple FastAPI doc sections

Query: {query}

Return only the label, nothing else."""

def route(query: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=10,
        messages=[{"role": "user", "content": ROUTER_PROMPT.format(query=query)}]
    )
    label = message.content[0].text.strip().lower()
    if label not in ["direct", "retrieve", "multi_hop"]:
        return "retrieve"
    return label
