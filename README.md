# arXiv Paper Digest Agent v2

> **An agentic AI system that reads arXiv papers so you don't have to.**
> Fetches, parses, summarizes, compares, and answers questions — all running locally with zero API costs.

**Built by: Shriram Dawange**

---

## What It Does

```
┌──────────────────────────────────────────────────────────────────────┐
│                     arXiv Paper Digest Agent v2                      │
│                   11-Node LangGraph Pipeline                         │
│                  Powered by Ollama (Offline AI)                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   INPUT                                                              │
│   ┌─────────────────────────────────────────────────────┐           │
│   │  "1706.03762"    Single paper analysis              │           │
│   │  "KV-cache"      Topic search + auto-select         │           │
│   │  "compare A B"   Side-by-side comparison            │           │
│   │  "synthesize X"  Multi-paper synthesis              │           │
│   └─────────────────────────┬───────────────────────────┘           │
│                             │                                        │
│                             ▼                                        │
│   ┌─────────────────────────────────────────────────────┐           │
│   │              11-NODE PIPELINE                        │           │
│   │                                                      │           │
│   │  Node 1:  Query Understanding                       │           │
│   │  Node 2:  arXiv Retrieval                           │           │
│   │  Node 3:  Selection/Ranking (LLM)                   │           │
│   │  Node 4:  Fetch & Parse PDF                         │           │
│   │  Node 5:  Chunk & Embed (ChromaDB)                  │           │
│   │  Node 6:  Summarize (Structured JSON)               │           │
│   │  Node 7:  Author Tracking                           │           │
│   │  Node 8:  Paper Recommendations                     │           │
│   │  Node 9:  QA Loop (RAG-powered)                     │           │
│   │  Node 10: Paper Comparison                          │           │
│   │  Node 11: Multi-Paper Synthesis                     │           │
│   │                                                      │           │
│   └─────────────────────────┬───────────────────────────┘           │
│                             │                                        │
│                             ▼                                        │
│   OUTPUT                                                             │
│   ┌─────────────────────────────────────────────────────┐           │
│   │  Structured Briefing:                                │           │
│   │  • Summary          • Problem Statement              │           │
│   │  • Method           • Key Results                    │           │
│   │  • Limitations      • Suggested Questions            │           │
│   │  • Author Info      • Similar Papers                 │           │
│   │  • Interactive Q&A  • Paper Comparison               │           │
│   └─────────────────────────────────────────────────────┘           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `<arxiv_id>` | Analyze single paper | `1706.03762` |
| `<topic>` | Search by topic, auto-select best | `KV-cache compression` |
| `compare <id1> <id2>` | Compare two papers side-by-side | `compare 1706.03762 2010.11930` |
| `synthesize <topic>` | Synthesize findings across papers | `synthesize transformer attention` |
| `quit` | Exit the agent | `quit` |

---

## Features

### Single Paper Analysis
```
Enter command: 1706.03762

============================================================
  Attention Is All You Need
  Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar
  arXiv: 1706.03762 | 2017-06-12
============================================================

SUMMARY
This paper introduces the Transformer...

PROBLEM
  >> Dependence on RNNs limits parallelism
  >> Sequential computation hinders scalability

METHOD
  >> Transformer architecture with self-attention
  >> Scaled dot-product and multi-head attention

RESULTS
  >> 28.4 BLEU on WMT 2014 English-to-German
  >> 41.8 BLEU on WMT 2014 English-to-French

LIMITATIONS
  >> Quadratic complexity with sequence length
  >> Requires substantial GPU memory

AUTHORS
  Fields: Machine Learning, NLP, Transformers
  Papers: 12 publications
  Recent: Efficient Transformers (2023)

RECOMMENDATIONS
  1. Efficient Attention in Transformers (2020)
  2. FlashAttention (2022)
  3. ...

Ask about the paper (or 'quit'): What is scaled dot-product attention?
```

### Paper Comparison
```
Enter command: compare 1706.03762 2010.11930

+-----------------------------------------+-----------------------------------------+
|  Attention Is All You Need              |  An Image is Worth 16x16 Words         |
+-----------------------------------------+-----------------------------------------+
| arXiv: 1706.03762                       | arXiv: 2010.11930                       |
| Date: 2017-06-12                        | Date: 2020-10-22                        |
+-----------------------------------------+-----------------------------------------+
| SIMILARITIES:                           |                                         |
| - Both use attention mechanisms         |                                         |
| - Both achieve state-of-the-art results |                                         |
|                                         |                                         |
| DIFFERENCES:                            |                                         |
| - NLP vs Computer Vision domain         |                                         |
| - Sequence-to-sequence vs classification|                                         |
|                                         |                                         |
| RECOMMENDATION: Read Attention first... |                                         |
+-----------------------------------------+-----------------------------------------+
```

### Multi-Paper Synthesis
```
Enter command: synthesize transformer attention

============================================================
  SYNTHESIS: Transformer Attention Mechanisms
============================================================

COMMON THEMES
  >> Self-attention is foundational for modern NLP
  >> Efficiency is key concern (quadratic complexity)
  >> Extensions to vision, speech, etc. are promising

FIELD EVOLUTION
  2017: Transformers introduced
  2018-2019: BERT, GPT scale up
  2020-2021: Vision Transformers, efficient variants
  2022-2023: Multimodal attention, hardware optimization

KEY FINDINGS
  >> Attention mechanisms outperform RNNs on most tasks
  >> Parallelization enables faster training
  >> Self-attention captures long-range dependencies

OPEN QUESTIONS
  >> How to handle very long sequences (>100K tokens)?
  >> Can attention be made more interpretable?

FUTURE DIRECTIONS
  >> Hybrid attention mechanisms
  >> Retrieval-augmented attention
  >> Neuromorphic implementations
```

---

## Architecture — 11-Node Pipeline

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        arXiv Paper Digest Agent v2                      ║
║                     LangGraph + Ollama (Offline AI)                     ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  USER INPUT                                                              ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  "1706.03762" OR "compare A B"          │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║                     ▼                                                    ║
║  ┌──────────────────────────────────────────┐                           ║
║  │  NODE 1: Query Understanding             │                           ║
║  │  • Detect: arXiv ID / topic / compare    │                           ║
║  │  • Detect: synthesize command            │                           ║
║  └──────────────────┬───────────────────────┘                           ║
║                     │                                                    ║
║         ┌───────────┼───────────┬──────────────┐                        ║
║         ▼           ▼           ▼              ▼                        ║
║  ┌────────────┐ ┌────────┐ ┌─────────┐ ┌────────────┐                  ║
║  │ arXiv ID   │ │ Topic  │ │Compare  │ │ Synthesize │                  ║
║  │ Direct     │ │ Search │ │Two papers│ │ Findings   │                  ║
║  └─────┬──────┘ └───┬────┘ └────┬────┘ └─────┬──────┘                  ║
║        │            │           │              │                         ║
║        ▼            ▼           │              │                         ║
║  ┌──────────┐ ┌──────────┐     │              │                         ║
║  │ Node 2   │ │ Node 3   │     │              │                         ║
║  │ Fetch    │ │ Rank     │     │              │                         ║
║  └────┬─────┘ └────┬─────┘     │              │                         ║
║       │             │           │              │                         ║
║       ▼             ▼           │              │                         ║
║  ┌──────────────────────────┐   │              │                         ║
║  │  NODE 4: Fetch & Parse   │   │              │                         ║
║  │  PDF download + PyPDF2   │   │              │                         ║
║  └──────────────┬───────────┘   │              │                         ║
║                 │               │              │                         ║
║                 ▼               │              │                         ║
║  ┌──────────────────────────┐   │              │                         ║
║  │  NODE 5: Chunk & Embed   │   │              │                         ║
║  │  ChromaDB vector store   │   │              │                         ║
║  └──────────────┬───────────┘   │              │                         ║
║                 │               │              │                         ║
║                 ▼               │              │                         ║
║  ┌──────────────────────────┐   │              │                         ║
║  │  NODE 6: Summarize       │   │              │                         ║
║  │  Multi-pass extraction   │   │              │                         ║
║  └──────────────┬───────────┘   │              │                         ║
║                 │               │              │                         ║
║                 ▼               │              │                         ║
║  ┌──────────────────────────┐   │              │                         ║
║  │  NODE 7: Author Tracking │   │              │                         ║
║  │  Fields, papers, recent  │   │              │                         ║
║  └──────────────┬───────────┘   │              │                         ║
║                 │               │              │                         ║
║                 ▼               │              │                         ║
║  ┌──────────────────────────┐   │              │                         ║
║  │  NODE 8: Recommendations │   │              │                         ║
║  │  Find similar papers     │   │              │                         ║
║  └──────────────┬───────────┘   │              │                         ║
║                 │               │              │                         ║
║                 ▼               │              │                         ║
║  ┌──────────────────────────┐   │              │                         ║
║  │  NODE 9: QA Loop (RAG)   │   │              │                         ║
║  │  Interactive Q&A         │   │              │                         ║
║  └──────────────────────────┘   │              │                         ║
║                                 │              │                         ║
║  ┌──────────────────────────┐   │              │                         ║
║  │  NODE 10: Compare        │◄──┘              │                         ║
║  │  Side-by-side analysis   │                  │                         ║
║  └──────────────────────────┘                  │                         ║
║                                                │                         ║
║  ┌──────────────────────────┐                  │                         ║
║  │  NODE 11: Synthesize     │◄─────────────────┘                        ║
║  │  Multi-paper synthesis   │                                           ║
║  └──────────────────────────┘                                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Graph Framework** | LangGraph | State machine with conditional routing |
| **LLM (Primary)** | Ollama + qwen2.5-coder:3b | 100% offline, zero cost |
| **LLM (Fallback)** | Groq free tier | Backup when Ollama unavailable |
| **Vector Database** | ChromaDB | Embedded, zero-config, persistent |
| **PDF Parser** | PyPDF2 | Lightweight, pure Python |
| **arXiv API** | arxiv Python package | Official arXiv API wrapper |
| **CLI** | Rich | Beautiful terminal UI with panels, tables |
| **Web UI** | Streamlit | Interactive web interface |

---

## Installation & Setup

### Step 1: Install Python 3.10+

Download from: https://www.python.org/downloads/

```bash
python --version  # Should show: Python 3.10.x or higher
```

### Step 2: Install Ollama

Download from: https://ollama.com/download

```bash
ollama --version
ollama pull qwen2.5-coder:3b-instruct-q4_K_M  # 1.9 GB download
ollama list  # Verify model installed
```

### Step 3: Clone & Setup

```bash
git clone https://github.com/shriramdawange/arXiv----Shriram-Dawange.git
cd arXiv----Shriram-Dawange

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run the agent
python src/main.py
```

### Step 5: Run Web UI (Optional)

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

---

### Optional: Groq Fallback

```bash
# Get free API key from https://console.groq.com
$env:GROQ_API_KEY="gsk_your_key_here"   # Windows PowerShell
export GROQ_API_KEY="gsk_your_key_here"  # Linux/Mac
```

---

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `ollama: command not found` | Restart terminal after installing Ollama |
| `Connection refused` | Run `ollama serve` in a separate terminal |
| `ModuleNotFoundError` | Activate venv: `venv\Scripts\activate` |
| `pip install` fails | `pip install --upgrade pip` |
| Model not found | `ollama pull qwen2.5-coder:3b-instruct-q4_K_M` |
| `No LLM available` | Start Ollama: `ollama serve` |

---

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10+ | 3.11+ |
| RAM | 4 GB | 8 GB+ |
| Disk | 5 GB free | 10 GB+ (for model) |
| GPU | None (CPU works) | Any CUDA GPU |
| Internet | Required for setup | Not needed after setup |

---

## Project Structure

```
arXiv----Shriram-Dawange/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── app.py                          # Streamlit web UI
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # Rich CLI entry point
│   ├── state.py                    # AgentState + models
│   ├── graph.py                    # LangGraph wiring (11 nodes)
│   │
│   ├── nodes/                      # One file per pipeline node
│   │   ├── __init__.py
│   │   ├── query_understanding.py  # Node 1: Command detection
│   │   ├── arxiv_retrieval.py      # Node 2: Fetch from arXiv API
│   │   ├── selection_ranking.py    # Node 3: LLM-based ranking
│   │   ├── fetch_parse_pdf.py      # Node 4: PDF download + extract
│   │   ├── chunk_embed.py          # Node 5: ChromaDB storage
│   │   ├── summarize.py            # Node 6: Multi-pass extraction
│   │   ├── author_tracking.py      # Node 7: Author info
│   │   ├── recommendations.py      # Node 8: Similar papers
│   │   ├── qa_loop.py              # Node 9: RAG-powered Q&A
│   │   ├── compare_papers.py       # Node 10: Side-by-side compare
│   │   └── synthesis.py            # Node 11: Multi-paper synthesis
│   │
│   └── utils/                      # Shared utilities
│       ├── __init__.py
│       ├── llm_client.py           # Ollama primary / Groq fallback
│       ├── pdf_parser.py           # PDF download + PyPDF2
│       └── embeddings.py           # ChromaDB chunking + storage
│
├── examples/                       # Example outputs
└── tests/                          # Test files
```

---

## State Shape

```python
AgentState = {
    # Input
    "user_input": str,
    "query_type": "arxiv_id" | "topic_search" | "compare" | "synthesize" | "invalid",
    "arxiv_id": str | None,
    "compare_ids": list[str],

    # After retrieval
    "search_results": list[dict],
    "selected_paper": dict | None,

    # After PDF parsing
    "raw_pdf_text": str,
    "sections": dict,

    # After embedding
    "chunks": list[dict],
    "vector_store_path": str,

    # After summarization
    "briefing": PaperBriefing,

    # After author tracking
    "author_info": list[dict],

    # After recommendations
    "recommendations": list[dict],

    # After comparison
    "comparison_papers": list[dict],
    "comparison_result": dict,

    # After synthesis
    "synthesis": dict,

    # After QA
    "conversation_history": list[QAExchange],

    # Error handling
    "error": str | None,
}
```

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

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM (Primary) | Ollama + qwen2.5-coder:3b | 100% offline, zero cost, fast |
| LLM (Fallback) | Groq free tier | Backup when Ollama unavailable |
| Graph Framework | LangGraph | Clean state machine, conditional routing |
| Vector DB | ChromaDB | Embedded, persistent, no external server |
| PDF Parser | PyPDF2 | Pure Python, no system dependencies |
| CLI | Rich | Beautiful terminal UI with panels, tables |
| Web UI | Streamlit | Interactive web interface, easy to share |
| Chunking | 800 chars, 150 overlap | Balance between context and precision |
| Summarization | Multi-call approach | Works reliably with small local models |
| QA | RAG with chunk retrieval | Grounded answers, no hallucination |

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
      "grounded_answer": "The paper introduces the Transformer..."
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
- **Rich** — Beautiful terminal output
- **Streamlit** — Web interface framework
- **arXiv** — Open access to scientific papers
- **PyPDF2** — PDF text extraction

---

## Contact

**Shriram Dawange**
GitHub: [shriramdawange](https://github.com/shriramdawange)

---

> *Built with offline AI — your data stays on your machine.*
