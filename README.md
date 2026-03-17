# 👁 The Eye Opener

AI-powered political fact-checking for India — built with LangGraph, ChromaDB, and D3.js

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey) ![LangGraph](https://img.shields.io/badge/LangGraph-latest-purple)
![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-teal) ![D3.js](https://img.shields.io/badge/D3.js-v7-orange) ![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active_Development-yellow)

## What it does

| 🔍 Input | ⚙️ Pipeline | 📊 Output |
| --- | --- | --- |
| Plain text claim or YouTube URL | 5-agent LangGraph chain | Truth score 1–100 + per-claim verdicts |

## Architecture

```text
Input -> [Preprocessor] -> [Surgeon] -> [Diver] -> [Skeptic] -> [Scorer] -> Results
										 ^
							 ChromaDB RAG + DuckDuckGo Live Search
```

## Tech stack

| Category | Technology |
| --- | --- |
| Backend | Flask 3.x |
| AI Orchestration | LangGraph |
| LLM (Primary) | Cerebras (OpenAI-compatible API) |
| LLM (Fallback 1) | Groq |
| LLM (Fallback 2) | GitHub Models |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Frontend | HTML + CSS + Vanilla JavaScript |
| Visualization | D3.js v7 |

## Quick start

1. Clone the repository.

```bash
git clone https://github.com/meamritanshu/eye-opener.git
cd eye-opener
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Copy environment template.

```bash
copy .env.example .env
```

5. Add API keys to `.env`.

```bash
# Required (at least one for worker execution)
CEREBRAS_API_KEY=...
GROQ_API_KEY=...

# Used by quality-first scorer path
GITHUB_TOKEN=...
```

6. Run the indexer.

```bash
python -m services.indexer
```

7. Run the app.

```bash
python app.py
```

8. Open the browser.

```bash
http://localhost:5000/
```

## Agent pipeline

| Agent | Role | Input | Output |
| --- | --- | --- | --- |
| Preprocessor | Normalizes user input and resolves transcript text | Raw claim text or YouTube URL | `cleaned_text`, `error` (if any) |
| Surgeon | Extracts precise, testable factual claims | `cleaned_text` | `claims[]` |
| Diver | Retrieves evidence via RAG-first with live-search fallback | `claims[]` | `research_logs[]`, `retrieval_method` |
| Skeptic | Critiques evidence quality, framing, and missing context | `research_logs[]` | `critiques[]` |
| Scorer | Produces claim-level verdicts and aggregate trust score | Claims + evidence + critiques | `verdicts[]`, `truth_score` |

## Project status

### ✅ Implemented
- End-to-end SSE pipeline with ordered agent progression.
- Hybrid retrieval path tracking (`rag`, `live_search`, `hybrid`).
- Frontend SSE client and live status updates.
- D3 truth graph rendering with active-node highlighting.
- Results panel rendering for score, retrieval method, and verdicts.

### 🔧 In Progress
- Fixing 429 rate-limit handling so runs do not degrade to `truth_score = 0`.
- Improving scorer reliability to avoid blanket `Unverifiable (0%)` outcomes.
- Hardening indexer source access (PIB 403 headers; BoomLive/VishvasNews selectors).
- Verifying and fixing empty-input SSE behavior (`event_type: error` vs `complete`).
- Stabilizing retrieval/evidence quality under load.

## Team

| Role | Branch |
| --- | --- |
| AI Pipeline Lead | feat/ai-pipeline |
| RAG & Retrieval Lead | feat/rag-retrieval |
| Frontend Lead | feat/frontend |

## Contributing

```text
Branch rules:
- main: protected, release-ready only
- develop: integration branch
- feature branches: feat/*
```

Commit format guide:
- `feat: add hybrid retrieval fallback logic`
- `fix: handle 429 retry in scorer path`
- `docs: update next-session handoff notes`

PR process:
1. Create a feature branch from `develop` and keep changes scoped.
2. Open a PR to `develop` with test notes, screenshots (if UI), and risk summary.
3. After review + checks pass, squash-merge; promote to `main` via release PR.

MIT License — built for educational and research purposes
