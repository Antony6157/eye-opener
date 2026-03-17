# The Eye Opener

The Eye Opener is a Flask + LangGraph fact-checking pipeline for political claims.
It accepts plain text or a YouTube URL, extracts verifiable claims, retrieves evidence using a hybrid strategy (ChromaDB RAG first, live search fallback), critiques reasoning, and returns per-claim verdicts with a truth score.

## Current Implementation Status (March 18, 2026)

Implemented:
- Flask app with health, verify, and SSE stream endpoints.
- LangGraph pipeline: preprocessor -> surgeon -> diver -> skeptic -> scorer.
- Shared LLM routing with provider fallbacks.
- Offline indexer for trusted Indian sources into ChromaDB.
- Hybrid retrieval policy in diver flow (rag/live_search/hybrid state tracking).
- Frontend dashboard with interactive submit flow and SSE client (`static/js/main.js`).
- D3 truth graph rendering + active-node highlight hook (`static/js/truth-graph.js`).
- Results panel rendering for `truth_score`, `retrieval_method`, and verdict output.

Not implemented yet:
- Automated tests.
- Strict startup fail-fast config errors (health/verify currently report warnings, not hard-stop startup).

## Architecture

See [docs/architecture.md](docs/architecture.md).

## API

See [docs/api.md](docs/api.md).

## Quick Start

1. Create a virtual environment and install dependencies.
2. Configure environment variables using `.env.example`.
3. (Optional but recommended) build the local retrieval index.
4. Start Flask app.

Example commands:

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python services/indexer.py
python app.py
```

App URLs:
- UI: `http://localhost:5000/`
- Health: `http://localhost:5000/api/health`

## Environment Variables

- `CEREBRAS_API_KEY`
- `GROQ_API_KEY`
- `GITHUB_TOKEN`
- `FLASK_ENV` (default: `development`)
- `FLASK_PORT` (default: `5000`)
- `CHROMA_DB_PATH` (default: `./chroma_db`)

At least one LLM credential should be configured:
- `GROQ_API_KEY` or `CEREBRAS_API_KEY` for normal agent execution.
- `GITHUB_TOKEN` is additionally used when scorer requests quality-first routing.

## Trusted Retrieval Sources

- pib.gov.in
- altnews.in
- factly.in
- boomlive.in
- vishvasnews.com

## Known Limitations

- LLM/provider rate limiting can degrade verdict quality in skeptic/scorer stages.
- Some source adapters need hardening (PIB 403 headers and stale selectors for BoomLive/VishvasNews).
- Empty-input SSE event semantics still need verification/fix (`complete` vs explicit `error`).
- No test suite in repository yet.
- Diver currently logs per-claim retrieval exceptions and continues; downstream failure is surfaced at skeptic stage when logs are empty.
- YouTube transcript extraction depends on upstream transcript availability.

For active handoff tasks and exact next-session resume prompt, see [NEXT_SESSION.md](NEXT_SESSION.md).
