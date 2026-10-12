def chunk(doc: dict, size: int = 512, overlap: int = 64) -> list[dict]:
    if size <= 0:
        raise ValueError("size must be greater than zero")

    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be non-negative and smaller than size")

    words = doc["text"].split()
    chunks = []
    step = size - overlap
    i = 0

    while i < len(words):
        window = words[i : i + size]
        chunks.append(
            {
                "text": " ".join(window),
                "source": doc["source"],
                "filename": doc["filename"],
                "chunk_index": len(chunks),
            }
        )
        i += step

    return chunks
