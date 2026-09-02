# Agentic RAG

A retrieval-augmented generation system built from scratch. No LangChain. No LlamaIndex. Every component implemented directly so the architecture is transparent and the tradeoffs are explicit.

Deployed on the FastAPI official documentation as a working demo: ask any question about FastAPI and get a grounded, verified answer with citations back to the source.

---

## Why this is different from most RAG projects

Most RAG implementations are wrappers. Query goes in, vector search runs, LLM generates, answer comes out. There is no awareness of retrieval quality, no routing logic, no self-correction, and no measurement.

This system treats retrieval as a decision problem, not a fixed pipeline.

The agent decides whether to retrieve at all, how to retrieve, whether the answer it generated is actually supported by what it retrieved, and whether to try again. Every decision is measurable and the eval harness proves it.

---

## Architecture

```
Query
  │
  ▼
Query Router ──── direct (general knowledge, skip retrieval)
  │           ├── retrieve (document lookup, single pass)
  │           └── multi_hop (chained retrieval across sources)
  │
  ▼
Hybrid Retrieval Engine
  ├── Dense search (sentence-transformers embeddings + Qdrant)
  ├── BM25 keyword search (rank_bm25)
  └── Reciprocal Rank Fusion (merges both lists without score tuning)
  │
  ▼
Generator (Claude API, grounded prompt)
  │
  ▼
SELF-RAG Critique Loop
  ├── Score each claim against retrieved chunks
  ├── Flag: fully_supported / partially_supported / not_supported
  ├── Re-retrieve for unsupported claims
  └── Loop up to 3 iterations, then output with transparency
  │
  ▼
Answer + grounding score + route + iteration count
```

---

## Eval results

Measured on a 30-question ground truth dataset across all three routing classes.

| Metric | Score |
|---|---|
| Routing accuracy | 100% |
| Average answer quality | 4.3 / 5 |
| Faithfulness (retrieve queries) | fully grounded on 1 iteration |

Baseline comparison (naive RAG, no router, no critique) scores 3.1 / 5 on the same dataset. The agentic loop accounts for the difference.

---

## Current limitations

- Evaluation currently uses a 30-question dataset focused on FastAPI documentation.
- The reported results should not be generalized to every knowledge base.
- Running the complete pipeline requires Qdrant and an external LLM.
- Retrieval quality depends on the coverage and quality of the indexed documents.

## Components

### Ingestion pipeline
`ingestion/loader.py` handles PDF and plaintext. `ingestion/chunker.py` splits by word count with configurable overlap to prevent context loss at boundaries. `ingestion/embedder.py` uses `all-MiniLM-L6-v2` locally, no external embedding API required. `ingestion/store.py` manages the Qdrant collection.

### Retrieval
`retrieval/dense.py` runs semantic search via cosine similarity. `retrieval/bm25.py` builds a keyword index at startup. `retrieval/hybrid.py` implements Reciprocal Rank Fusion from scratch in 15 lines, merging both result lists into a single ranked output without needing to tune score weights.

### Agent
`agent/router.py` classifies query intent before any retrieval runs. `agent/generator.py` generates grounded answers from retrieved context only. `agent/critique.py` scores the generated answer against source chunks in a single batched API call, returning per-sentence grounding labels.

### Eval
`eval/harness.py` runs the full pipeline against a ground truth dataset and reports routing accuracy, answer quality via LLM-as-judge, and faithfulness. The harness is designed to benchmark any retrieval configuration, not just this one.

---

## Stack

| Component | Choice | Reason |
|---|---|---|
| Vector store | Qdrant | Production-grade, runs locally via Docker |
| Embeddings | sentence-transformers | Local, free, no per-query cost |
| Keyword search | rank_bm25 | Direct BM25Okapi implementation |
| LLM | Claude API (claude-sonnet-4-5) | Router, generator, and critique |
| API layer | FastAPI | Matches the demo corpus |
| Frontend | Vanilla HTML/CSS/JS | No framework overhead |

LangChain and LlamaIndex are absent by design. Both frameworks abstract the retrieval mechanics that matter most for understanding and debugging a RAG system.

---

## Running locally

**Requirements:** Python 3.11, Docker

```bash
# Clone and set up
git clone https://github.com/HadithSalahshour/agentic-rag.git
cd agentic-rag
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Add your Anthropic API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Scrape the FastAPI docs corpus
python3 scripts/scrape_fastapi.py

# Ingest into the vector store
python3 -c "
import os
from ingestion.loader import load
from ingestion.chunker import chunk
from ingestion.embedder import embed
from ingestion.store import init_collection, store
from retrieval.bm25 import build_index

init_collection()
all_chunks = []
for filename in os.listdir('corpus'):
    if filename.endswith('.txt'):
        doc = load(f'corpus/{filename}')
        chunks = chunk(doc)
        store(chunks, embed([c['text'] for c in chunks]))
        all_chunks.extend(chunks)
build_index(all_chunks)
print(f'{len(all_chunks)} chunks indexed')
"

# Start the server
uvicorn api.main:app --reload
```

Open `http://localhost:8000`

---

## Querying via API

```bash
# Single query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I implement JWT authentication in FastAPI?"}'

# Response shape
{
  "answer": "...",
  "route": "retrieve",
  "iterations": 1,
  "critique": [
    { "sentence": "...", "score": "fully_supported" }
  ]
}
```

---

## Extending this

The corpus is swappable. Replace the FastAPI scraper with any document source and the rest of the system works without modification. The eval harness accepts any `answer_fn` that takes a query and chunk list, so benchmarking a new retrieval strategy requires one function swap.

Planned additions: cross-encoder re-ranking, multi-hop query decomposition, streaming responses with inline source highlights.

---

## Background

Built as a deep dive into production RAG patterns after finding that most public implementations skip the parts that matter in practice: retrieval quality measurement, routing logic, and grounding verification. The SELF-RAG critique loop is adapted from [Asai et al., 2023](https://arxiv.org/abs/2310.11511).
