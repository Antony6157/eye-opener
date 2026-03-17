# Architecture

## Pipeline Overview

The backend is a LangGraph state machine executed per request.

Node order:
1. `preprocessor`
2. `surgeon`
3. `diver`
4. `skeptic`
5. `scorer`
6. `error_handler` (terminal on failure)

The state contract is defined in `services/state.py` as `AgentState`.

## State Model

Key fields:
- `raw_input`: Original user input.
- `cleaned_text`: Normalized text or transcript.
- `claims`: Verifiable claims extracted from text.
- `research_logs`: Evidence grouped by claim.
- `critiques`: Skeptic outputs.
- `verdicts`: Structured scoring outputs by claim.
- `truth_score`: Integer aggregate score.
- `active_agent`: Current node for stream consumers.
- `retrieval_method`: `rag`, `live_search`, or `hybrid`.
- `error`: Error message or `None`.

## LLM Routing

LLM clients are centralized in `services/llm.py` via `get_llm(prefer_quality=False)`.

Routing policy:
- If `prefer_quality=True` and `GITHUB_TOKEN` exists, quality model is preferred first.
- Otherwise normal routing prefers available providers in this order:
  1. Groq (`llama-3.3-70b-versatile`)
  2. Cerebras (`llama3.3-70b`)
- Fallback chains are applied when multiple candidates exist.

## Retrieval Design

`services/retriever.py` implements hybrid retrieval:
- `rag_search(query)` queries local Chroma collection `indian_political_facts`.
- Confidence is computed as `1 - distance` from top match.
- If confidence >= 0.75 and results exist, method is `rag`.
- Otherwise it executes trusted-source DuckDuckGo search and returns either:
  - `live_search` if no RAG results existed, or
  - `hybrid` with merged RAG + live evidence.

## Data Indexing

`services/indexer.py` performs offline ingestion:
- Fetches source pages.
- Extracts source-specific article text using CSS selectors.
- Chunks text (500 chars with 100 overlap).
- Embeds chunks with `sentence-transformers/all-MiniLM-L6-v2`.
- Upserts vectors and metadata into ChromaDB persistent storage.

## Streaming and API Wiring

- `services/runner.py` streams step-level state events.
- `app.py` exposes:
  - POST `/api/verify` for single-response execution.
  - GET `/api/stream` for SSE event streaming.
  - GET `/api/health` for readiness/config visibility.

## Frontend Status

Current frontend includes live SSE wiring and graph rendering:
- `static/index.html` includes claim input, pipeline stream panel, graph container, and results snapshot panel.
- `static/css/style.css` provides responsive visuals.
- `static/js/main.js` submits claims to `/api/stream`, updates active agent state, handles errors, and renders final results.
- `static/js/truth-graph.js` renders a D3 graph and exposes `window.truthGraph.activateNode(...)` for active-node updates.

Known frontend caveat:
- Very fast stage transitions (especially `preprocessor`) can be difficult to capture in automated sampling even when visible during run.
