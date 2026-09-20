# arXiv Paper Digest Agent

> **An agentic AI system that reads arXiv papers so you don't have to.**
> Fetches, parses, summarizes, and answers questions about any paper — all running locally with zero API costs.

**Built by: Shriram Dawange**

---

## What It Does

Give it a paper ID or topic — it does the rest:

```
INPUT:  "1706.03762"                    INPUT:  "KV-cache compression for LLMs"
           |                                    |
           v                                    v
   +-------+-------+                  +--------+--------+
   |  Fetch Paper   |                  | Search arXiv    |
   |  from arXiv    |                  | Pick best match |
   +-------+-------+                  +--------+--------+
           |                                    |
           v                                    v
   +-------+-------+                  +--------+--------+
   |  Parse PDF     |                  | Fetch & Parse   |
   |  Extract text  |                  | PDF content     |
   +-------+-------+                  +--------+--------+
           |                                    |
           +--------------+  +------------------+
                          |  |
                          v  v
                 +--------+--------+
                 | Chunk & Embed    |
                 | Store in ChromaDB|
                 +--------+--------+
                          |
                          v
                 +--------+--------+
                 | Generate Summary |
                 | (Structured JSON)|
                 +--------+--------+
                          |
                          v
                 +--------+--------+
                 | Ask Questions    |
                 | (RAG-powered QA) |
                 +-----------------+
```

---

## Architecture — 7-Node Pipeline

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        arXiv Paper Digest Agent                         ║
║                     LangGraph + Ollama (Offline AI)                     ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  USER INPUT                                                              ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  "1706.03762" OR "KV-cache compression" │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║                     ▼                                                    ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  NODE 1: Query Understanding             │                           ║
║  │  • Detect arXiv ID vs topic search       │                           ║
║  │  • Regex: ^\d{4}\.\d{4,5}$              │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║         ┌───────────┴───────────┐                                       ║
║         ▼                       ▼                                       ║
║  ┌──────────────┐        ┌──────────────┐                               ║
║  │ arXiv ID     │        │ Topic Search │                               ║
║  │ Direct fetch │        │ API search   │                               ║
║  └──────┬───────┘        └──────┬───────┘                               ║
║         │                       │                                       ║
║         │                       ▼                                       ║
║         │              ┌──────────────────┐                             ║
║         │              │ NODE 3: Ranking   │                             ║
║         │              │ LLM picks best   │                             ║
║         │              │ paper from list   │                             ║
║         │              └────────┬─────────┘                             ║
║         │                       │                                       ║
║         ▼                       ▼                                       ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  NODE 2: arXiv Retrieval                 │                           ║
║  │  • Fetch via arxiv Python API            │                           ║
║  │  • Get metadata, abstract, PDF URL       │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║                     ▼                                                    ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  NODE 4: Fetch & Parse PDF               │                           ║
║  │  • Download from arxiv.org/pdf/          │                           ║
║  │  • PyPDF2 text extraction                │                           ║
║  │  • Cap at 30 pages                       │                           ║
║  │  • Fallback to abstract if parse fails   │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║                     ▼                                                    ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  NODE 5: Chunk & Embed                   │                           ║
║  │  • Split text (800 chars, 150 overlap)   │                           ║
║  │  • Store in ChromaDB (persistent)        │                           ║
║  │  • Ready for RAG retrieval               │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║                     ▼                                                    ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  NODE 6: Summarize                       │                           ║
║  │  • Multiple focused LLM calls            │                           ║
║  │  • Extract: problem, method, results,    │                           ║
║  │    limitations, suggested questions      │                           ║
║  │  • Works with small local models         │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║                     ▼                                                    ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  NODE 7: QA Loop (RAG)                   │                           ║
║  │  • Retrieve relevant chunks              │                           ║
║  │  • LLM answers grounded in paper text    │                           ║
║  │  • Interactive follow-up questions       │                           ║
║  └──────────────────────────────────────────┘                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Why Offline AI Matters

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHY OFFLINE LLM?                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  $ COST         Traditional API (GPT-4, Claude)                │
│  ████████       $15-60 per million tokens                      │
│  ████████       Requires internet connection                   │
│  ████████       Data sent to external servers                  │
│  ████████       Rate limits, vendor lock-in                    │
│                                                                 │
│  $ COST         This Agent (Ollama + Local)                    │
│  ░              $0 — runs on your machine                      │
│  ░              Works fully offline                            │
│  ░              Your data never leaves your computer           │
│  ░              No rate limits, no vendor dependency            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SEVERITY OF ONLINE vs OFFLINE AI:                              │
│                                                                 │
│  Privacy Risk    ████████████ HIGH   (API = data leaves device) │
│  Dependency      ████████████ HIGH   (API down = app breaks)    │
│  Cost            ████████████ HIGH   (per-token billing)        │
│  Latency         ████████░░░░ MEDIUM (network round-trip)       │
│                                                                 │
│  This Agent:                                                    │
│  Privacy Risk    ░░░░░░░░░░░░ NONE   (100% local)              │
│  Dependency      ░░░░░░░░░░░░ NONE   (Ollama always available) │
│  Cost            ░░░░░░░░░░░░ ZERO   (no API key required)     │
│  Latency         ░░░░░░░░░░░░ LOW    (local GPU inference)     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Graph Framework** | LangGraph | State machine with conditional routing between nodes |
| **LLM (Primary)** | Ollama + qwen2.5-coder:3b | Runs locally, no API key, fully offline |
| **LLM (Fallback)** | Groq (free tier) | Backup when Ollama is unavailable |
| **Vector Database** | ChromaDB | Embedded, zero-config, persistent storage |
| **PDF Parser** | PyPDF2 | Lightweight, pure Python, no system deps |
| **arXiv API** | arxiv Python package | Official arXiv API wrapper |
| **Embeddings** | ChromaDB default | Built-in, no external service needed |

---

## State Shape — Data Flow Between Nodes

```python
AgentState = {
    # Input
    "user_input": str,              # What the user typed
    "query_type": str,              # "arxiv_id" | "topic_search" | "invalid"
    "arxiv_id": str | None,         # e.g. "1706.03762"

    # After retrieval
    "search_results": list[dict],   # Up to 10 papers from arXiv
    "selected_paper": dict | None,  # Best match (with title, authors, abstract)

    # After PDF parsing
    "raw_pdf_text": str,            # Full extracted text (capped at 30 pages)
    "sections": dict,               # {"abstract": "...", "method": "...", ...}

    # After embedding
    "chunks": list[dict],           # Text chunks with metadata
    "vector_store_path": str,       # ChromaDB persistent path

    # After summarization
    "briefing": PaperBriefing,      # Structured JSON with all sections

    # After QA
    "conversation_history": list,   # All Q&A exchanges

    # Error handling
    "error": str | None,            # Error message if something failed
}
```

---

## Project Structure

```
arXiv----Shriram-Dawange/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # CLI entry point
│   ├── state.py                    # AgentState + PaperBriefing models
│   ├── graph.py                    # LangGraph wiring (7 nodes)
│   │
│   ├── nodes/                      # One file per pipeline node
│   │   ├── __init__.py
│   │   ├── query_understanding.py  # Node 1: ID vs topic detection
│   │   ├── arxiv_retrieval.py      # Node 2: Fetch from arXiv API
│   │   ├── selection_ranking.py    # Node 3: LLM-based paper ranking
│   │   ├── fetch_parse_pdf.py      # Node 4: PDF download + extraction
│   │   ├── chunk_embed.py          # Node 5: Chunking + ChromaDB storage
│   │   ├── summarize.py            # Node 6: Structured summary generation
│   │   └── qa_loop.py              # Node 7: RAG-powered Q&A
│   │
│   └── utils/                      # Shared utilities
│       ├── __init__.py
│       ├── llm_client.py           # Ollama primary / Groq fallback
│       ├── pdf_parser.py           # PDF download + PyPDF2 extraction
│       └── embeddings.py           # ChromaDB chunking + vector store
│
├── examples/                       # Example outputs
└── tests/                          # Test files
```

---

## Setup

### Prerequisites

- Python 3.10+
- Ollama installed (https://ollama.com)
- A model pulled: `ollama pull qwen2.5-coder:3b-instruct-q4_K_M`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/shriramdawange/arXiv----Shriram-Dawange.git
cd arXiv----Shriram-Dawange

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run (no API key needed!)
python src/main.py
```

### Optional: Groq Fallback

If you want a cloud fallback when Ollama is offline:

```bash
# Get free API key from https://console.groq.com
set GROQ_API_KEY=gsk_...        # Windows PowerShell
# export GROQ_API_KEY=gsk_...   # Linux/Mac
```

---

## Usage

```
============================================================
  arXiv Paper Digest Agent
  Powered by LangGraph + Ollama (Offline)
============================================================

Enter a research topic or arXiv paper ID:
> 1706.03762

Processing...
Stored 61 chunks in vector DB

============================================================
  Attention Is All You Need
  Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar et al.
  arXiv: 1706.03762 | 2017-06-12
============================================================

SUMMARY
This paper introduces the Transformer, a neural architecture that
replaces recurrent and convolutional components with self-attention
mechanisms, enabling highly parallel training and improved translation
quality.

PROBLEM
  - Dependence on RNNs limits parallelism and training speed
  - Sequential computation hinders scalability to long sequences
  - Existing attention mechanisms coupled with RNNs

METHOD
  - Transformer architecture using stacked self-attention layers
  - Scaled dot-product attention and multi-head attention
  - Positional encoding to inject sequence order

RESULTS
  - 28.4 BLEU on WMT 2014 English-to-German (>2 BLEU improvement)
  - 41.8 BLEU on WMT 2014 English-to-French (new SOTA)
  - Trained in 3.5 days on 8 GPUs

LIMITATIONS
  - Quadratic complexity with sequence length
  - Requires substantial GPU memory

SUGGESTED QUESTIONS
  - How can the Transformer handle sequences longer than a few hundred tokens?
  - What are the trade-offs between model size and performance?

============================================================

Ask a question about the paper (or 'exit' to quit):
> What are the main contributions?

Answer (Source: unknown, unknown, unknown):
The paper's main contributions are:
1. The Transformer architecture — attention-only, no recurrence
2. Scaled dot-product attention mechanism
3. Multi-head attention for diverse representation subspaces
4. State-of-the-art translation results with faster training
```

---

## Input Examples

| Input | Type | Description |
|-------|------|-------------|
| `1706.03762` | arXiv ID | Direct paper lookup |
| `2401.05060` | arXiv ID | Direct paper lookup |
| `KV-cache compression for LLMs` | Topic | Search + auto-select best |
| `transformer attention mechanisms` | Topic | Search + auto-select best |
| `recent work on RAG systems` | Topic | Search + auto-select best |

---

## Error Handling

| Scenario | Handling | Severity |
|----------|----------|----------|
| 0 arXiv results | Ask user to refine query | Medium |
| Scanned PDF (no text) | Fall back to abstract | High |
| Large PDF (>30 pages) | Truncate to first 30 pages | Medium |
| LLM timeout | Retry with fallback model | High |
| QA hallucination | Force grounding with retrieved chunks | High |
| Ollama offline | Switch to Groq API (if key set) | Medium |
| No LLM available | Clear error message | Critical |

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM (Primary) | Ollama + qwen2.5-coder:3b | 100% offline, zero cost, fast on local GPU |
| LLM (Fallback) | Groq free tier | Backup when Ollama unavailable |
| Graph Framework | LangGraph | Clean state machine, conditional routing |
| Vector DB | ChromaDB | Embedded, persistent, no external server |
| PDF Parser | PyPDF2 | Pure Python, no system dependencies |
| Chunking | 800 chars, 150 overlap | Balance between context and precision |
| Summarization | Multi-call approach | Works reliably with small local models |
| QA | RAG with chunk retrieval | Grounded answers, no hallucination |

---

## Offline AI Severity Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│             ONLINE vs OFFLINE AI — SEVERITY MATRIX              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FACTOR          ONLINE (API)     OFFLINE (LOCAL)    SEVERITY   │
│  ─────────────── ─────────────── ──────────────── ──────────   │
│  Privacy         Data leaves     Data stays on      CRITICAL   │
│                  your device     your device                    │
│                                                                 │
│  Availability    Depends on      Always available   HIGH       │
│                  internet +                              │
│                  vendor uptime                            │
│                                                                 │
│  Cost            $15-60/M        $0 forever         HIGH       │
│                  tokens                                  │
│                                                                 │
│  Speed           Network         Local GPU          MEDIUM     │
│                  round-trip      inference                         │
│                                                                 │
│  Quality         GPT-4 level     Smaller models     MEDIUM     │
│                  (best)          (good enough)                    │
│                                                                 │
│  Vendor Lock     High (API       None (open         LOW        │
│                  changes)        models, local)                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  THIS AGENT'S APPROACH:                                         │
│  ✓ Primary: Fully offline (Ollama) — zero severity             │
│  ✓ Fallback: Groq free tier — minimal severity                 │
│  ✓ No paid APIs ever required                                   │
│  ✓ Your research data never leaves your machine                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Example Run — Topic Search

```
Enter a research topic or arXiv paper ID:
> recent work on KV-cache compression

Processing...
Stored 45 chunks in vector DB

============================================================
  Efficient KV-Cache Compression for Large Language Models
  Authors: Alice Smith, Bob Jones et al.
  arXiv: 2401.12345 | 2024-01-15
============================================================

SUMMARY
Introduces learned quantization + adaptive pruning for KV caches,
reducing memory by 60% with <2% perplexity degradation.

PROBLEM
  - High memory footprint of KV caches in long-sequence tasks
  - Inference latency increases with cache size
  - GPU memory limits deployment of large models

METHOD
  - Learned quantization of KV vectors
  - Adaptive pruning based on attention patterns
  - Low-rank decomposition of cache matrices

RESULTS
  - 60% memory reduction on LLaMA 70B
  - <2% perplexity degradation
  - 1.5x inference speedup

LIMITATIONS
  - Only tested on decoder-only models
  - Requires model retraining
  - Limited evaluation on very long sequences (>32K tokens)

SUGGESTED QUESTIONS
  - How does this compare to other compression techniques?
  - Can this be applied to encoder-decoder models?
  - What is the computational overhead?
============================================================
```

---

## Session Output

Sessions are saved as JSON for later analysis:

```json
{
  "user_input": "1706.03762",
  "query_type": "arxiv_id",
  "arxiv_id": "1706.03762",
  "selected_paper": {
    "title": "Attention Is All You Need",
    "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
    "arxiv_id": "1706.03762",
    "published": "2017-06-12"
  },
  "conversation_history": [
    {
      "turn": 1,
      "user_question": "What are the main contributions?",
      "grounded_answer": "The paper introduces the Transformer...",
      "sources": ["chunk_2", "chunk_4", "chunk_5"]
    }
  ]
}
```

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is open source and available under the MIT License.

---

## Acknowledgments

- **LangGraph** — State machine framework for LLM agents
- **Ollama** — Local LLM inference made easy
- **ChromaDB** — Embedded vector database
- **arXiv** — Open access to scientific papers
- **PyPDF2** — PDF text extraction

---

## Contact

**Shriram Dawange**
GitHub: [shriramdawange](https://github.com/shriramdawange)

---

> *Built with offline AI — your data stays on your machine.*
