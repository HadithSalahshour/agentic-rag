def chunk(doc: dict, size: int = 512, overlap: int = 64) -> list[dict]:
    words = doc["text"].split()
    chunks = []
    i = 0

    while i < len(words):
        window = words[i:i + size]
        chunks.append({
            "text": " ".join(window),
            "source": doc["source"],
            "filename": doc["filename"],
            "chunk_index": len(chunks)
        })
        i += size - overlap

    return chunks
