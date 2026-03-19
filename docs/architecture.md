# Architecture

## System overview

The Eye Opener is a Flask application that executes a LangGraph claim-verification pipeline and streams state updates to the frontend through Server-Sent Events.

Primary flow:
- input ingestion
- staged verification
- retrieval and critique
- scoring and summary
- live UI updates during execution

## Graph topology

Runtime graph nodes:
- preprocessor
- surgeon
- diver
- skeptic
- scorer
- error_handler

Node routing:
- entry: preprocessor
- success path: preprocessor -> surgeon -> diver -> skeptic -> scorer -> end
- failure path: any stage with error -> error_handler -> end

Terminology:
- worker agents: surgeon, diver, skeptic, scorer
- execution stages: preprocessor plus 4 workers
- architect: orchestration code that compiles and routes the graph

## State contract

State model is defined in [services/state.py](../services/state.py).

Key fields:
- raw_input
- cleaned_text
- claims
- research_logs
- critiques
- verdicts
- truth_score
- active_agent
- retrieval_method
- error

The retrieval_method field is one of:
- rag
- live_search
- hybrid

## LLM architecture

LLM provider selection is centralized in [services/llm.py](../services/llm.py).

Current provider policy:
1. Primary: local Ollama model when `USE_LOCAL_LLM` is true and Ollama is reachable
2. Fallback 1: Cerebras
3. Fallback 2: Groq
4. Quality fallback: GitHub Models when `prefer_quality=True` and no local or cloud provider is available

Retry behavior:
- `get_llm_with_retry()` applies staged waits for rate-limit-like errors
- non-rate errors are raised immediately

## Retrieval architecture

Retriever implementation is in [services/retriever.py](../services/retriever.py).

Core strategy:
- run semantic retrieval against the local Chroma index
- compute confidence from the top distance
- return `rag` if confidence threshold is met
- otherwise run live search and return `live_search` or `hybrid`

Source strategy:
- RAG-backed domain list for indexed sources
- live-only domain list for domains intentionally not indexed
- deduplicated live source list assembled at runtime

Live enrichments:
- deep legal search on IndianKanoon for legal-style claims
- dedicated PIB search path for government press-release coverage

Evidence prioritization:
- RAG results are sorted to prioritize legal and government categories

## Indexing architecture

Indexer implementation is in [services/indexer.py](../services/indexer.py).

Current behavior:
- source registry with category tags
- per-source selector and optional fallback selector
- per-source skip controls with explicit skip_reason
- static fetch and extraction pipeline
- chunking with overlap
- embedding generation through `OllamaEmbeddings` with `nomic-embed-text`
- upsert into Chroma with source metadata and category

Operational note:
- multiple sources are intentionally skipped due to blocking, dynamic rendering, or non-static content constraints

## API and stream architecture

Flask routes in [app.py](../app.py):
- GET /
- GET /api/health
- GET /api/ollama-models
- GET /api/settings
- POST /api/settings
- POST /api/verify
- GET /api/stream

Runner behavior in [services/runner.py](../services/runner.py):
- step events streamed as state transitions occur
- final event emitted after graph completion
- handled validation errors still currently finish with `event_type: complete` and a populated `state.error`

## Frontend architecture

UI files:
- [static/index.html](../static/index.html)
- [static/css/style.css](../static/css/style.css)
- [static/js/main.js](../static/js/main.js)
- [static/js/truth-graph.js](../static/js/truth-graph.js)

Frontend behavior:
- captures user input and opens an EventSource stream
- updates active stage label and status pill live
- highlights graph nodes as stages change
- renders result summary after completion
- shows inline error text when `state.error` is present

## Current risks and constraints

1. Contract consistency:
- terminal SSE error semantics for empty input are still normalized through `state.error`, not a dedicated terminal error event

2. Index coverage:
- source ingestion is intentionally partial for blocked or JS-rendered sources

3. Quality stability:
- verdict quality can still vary claim to claim depending on retrieval depth and live-source quality

4. Test maturity:
- integration and regression automation is still limited
