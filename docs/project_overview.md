# Project Overview

## Purpose

The Eye Opener is a Flask-based fact-checking application for Indian political claims. It accepts plain text or a YouTube URL, runs the input through a LangGraph pipeline, gathers evidence from local and live sources, and renders the results in a browser UI.

This document summarizes the repository structure and the current runtime design.

## Repository Layout

### Root files
- `app.py` - Flask application entrypoint, API routes, SSE streaming, settings persistence, and Ollama model proxy.
- `config.py` - Environment loading and runtime configuration.
- `requirements.txt` - Python dependencies.
- `.env.example` - Sample environment variables.
- `README.md` - User-facing setup and project summary.
- `implementation_plan.md`, `implementation_checklist.md`, `phase_wise_implementation_plan.md` - Planning and status tracking.
- `architecture_notes.md`, `changes.md`, `merge_analysis.md`, `NEXT_SESSION.md` - Supporting project notes and history.

### Backend package: `services/`
- `state.py` - Shared `AgentState` TypedDict and initial state factory.
- `preprocessor.py` - Input normalization and YouTube transcript extraction.
- `llm.py` - Centralized LLM provider selection and retry handling.
- `agents.py` - Surgeon, Diver, Skeptic, and Scorer agent implementations.
- `architect.py` - LangGraph `StateGraph` construction and routing.
- `runner.py` - Pipeline execution and SSE event generation.
- `retriever.py` - Hybrid retrieval logic for RAG and live search.
- `indexer.py` - Offline indexing of trusted sources into ChromaDB.

### Frontend assets: `static/`
- `index.html` - Single-page dashboard UI.
- `css/style.css` - Layout, theming, workflow timeline, and result panel styling.
- `js/main.js` - SSE client, results rendering, and UI interactions.
- `js/truth-graph.js` - D3 workflow graph visualization.
- `js/settings.js` - Settings drawer and API-backed configuration UI.

### Documentation: `docs/`
- `architecture.md` - System architecture reference.
- `api.md` - HTTP and SSE API reference.
- `agent_orchestration_clarification.md` - Canonical explanation of pipeline counting and orchestration terminology.
- `project_overview.md` - This document.

## Runtime Architecture

### Request flow
1. The browser submits a claim or YouTube URL.
2. `app.py` receives the request.
3. `services/preprocessor.py` cleans the input or extracts a transcript.
4. `services/agents.py` runs the four worker stages in order.
5. `services/retriever.py` provides RAG-first retrieval with live fallback.
6. `services/runner.py` streams state transitions through SSE.
7. The frontend updates the workflow graph and renders the final results.

### Pipeline stages
The canonical processing flow is:

`preprocessor -> surgeon -> diver -> skeptic -> scorer`

Roles:
- `preprocessor` - prepares input and resolves YouTube transcripts.
- `surgeon` - extracts verifiable factual claims.
- `diver` - collects evidence from ChromaDB and live sources.
- `skeptic` - challenges framing, omissions, and unsupported assertions.
- `scorer` - produces verdicts and an aggregate truth score.

The graph also includes `error_handler` as the terminal failure node.

## Retrieval Model

The retriever uses a hybrid policy:
- RAG search queries the local ChromaDB collection `indian_political_facts`.
- Live search falls back to DuckDuckGo for trusted domains when RAG confidence is insufficient.
- Legal claims can trigger additional IndianKanoon search.
- Government claims can trigger additional PIB search.

The `retrieval_method` field records which path was used:
- `rag`
- `live_search`
- `hybrid`

## LLM Routing

`services/llm.py` selects the active model provider.

Current routing order:
1. Local Ollama when `USE_LOCAL_LLM=true` and Ollama is reachable.
2. Cerebras as the first cloud fallback.
3. Groq as the second cloud fallback.
4. GitHub Models when `prefer_quality=True` and no other provider is available.

This allows the app to run locally when possible while keeping cloud-based fallbacks available.

## API Surface

Main routes in `app.py`:
- `GET /` - serves the frontend.
- `GET /api/health` - returns config and runtime status.
- `GET /api/ollama-models` - lists models from the local Ollama server.
- `GET /api/settings` - returns the current editable settings.
- `POST /api/settings` - saves settings back to `.env`.
- `POST /api/verify` - runs the pipeline once and returns JSON.
- `GET /api/stream` - streams pipeline state changes via SSE.

## Frontend Notes

The UI combines two visual layers:
- A workflow timeline that shows the current stage.
- A D3 graph that highlights the active node during streaming.

The results area includes:
- truth score
- verdict summary
- sources used
- score explanation
- retrieval method badge

The settings drawer allows runtime configuration of:
- Ollama base URL and model
- Cerebras credentials and model
- Groq credentials and model
- GitHub token and quality model

## Data and Storage

- ChromaDB is used as the persistent local vector store.
- The database path comes from `CHROMA_DB_PATH`.
- Indexed source chunks are stored with source metadata and category tags.

## Environment Variables

Important variables include:
- `FLASK_ENV`
- `FLASK_PORT`
- `CHROMA_DB_PATH`
- `USE_LOCAL_LLM`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `CEREBRAS_API_KEY`
- `CEREBRAS_MODEL`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `GITHUB_TOKEN`
- `GITHUB_QUALITY_MODEL`

## Current Constraints

- Some source sites remain intentionally skipped in the indexer because they are blocked, dynamic, or JS-heavy.
- Empty-input runs still complete through the handled failure path and emit a terminal `complete` event carrying `state.error`.
- Integration coverage is still limited, so API and stream contract changes should be validated carefully.

## Quick Start

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and configure keys.
4. Start Ollama if using local inference.
5. Run `python -m services.indexer` to refresh the local index.
6. Start the app with `python app.py`.
7. Open `http://localhost:5000/`.