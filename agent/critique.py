import anthropic

client = anthropic.Anthropic()

CRITIQUE_PROMPT = """Given this context and sentence, is the sentence supported by the context?

Context: {context}
Sentence: {sentence}

Answer with only one of: fully_supported, partially_supported, not_supported"""

def critique_sentence(sentence: str, chunks: list[dict]) -> str:
    context = "\n\n".join([c["text"] for c in chunks])
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=10,
        messages=[{"role": "user", "content": CRITIQUE_PROMPT.format(
            context=context,
            sentence=sentence
        )}]
    )
    return message.content[0].text.strip().lower()

def critique(answer: str, chunks: list[dict]) -> dict:
    sentences = [s.strip() for s in answer.split(".") if s.strip() and len(s.strip()) > 20]
    if not sentences:
        return {"passed": True, "results": []}
    
    context = "\n\n".join([c["text"] for c in chunks])
    
    # Batch all sentences in one API call instead of one per sentence
    batch_prompt = f"""For each sentence below, check if it is supported by the context.
Context: {context}

Sentences:
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(sentences))}

Reply with one line per sentence: fully_supported, partially_supported, or not_supported.
Format: 1. label, 2. label, 3. label ..."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=100,
        messages=[{"role": "user", "content": batch_prompt}]
    )
    
    raw = message.content[0].text.strip()
    labels = []
    for part in raw.split(","):
        part = part.strip()
        for label in ["fully_supported", "partially_supported", "not_supported"]:
            if label in part:
                labels.append(label)
                break
        else:
            labels.append("fully_supported")
    
    results = []
    all_supported = True
    for i, sentence in enumerate(sentences):
        score = labels[i] if i < len(labels) else "fully_supported"
        results.append({"sentence": sentence, "score": score})
        if score == "not_supported":
            all_supported = False
    
    return {"passed": all_supported, "results": results}

