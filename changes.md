# The Eye Opener: Changelog

This document tracks the project-level changes that are currently reflected in the repository.

## Backend and orchestration
- Added a LangGraph pipeline with `preprocessor`, `surgeon`, `diver`, `skeptic`, `scorer`, and `error_handler` nodes.
- Added a central `services/llm.py` router with local-first Ollama support and Cerebras/Groq/GitHub fallback paths.
- Added `services/retriever.py` with RAG-first search, live DuckDuckGo fallback, and legal/PIB enrichments.
- Added `services/indexer.py` with source categories, skip reasons, and local Ollama embeddings.
- Added `services/runner.py` SSE streaming behavior for step and terminal events.
- Added Flask settings and Ollama model proxy endpoints in `app.py`.

## Frontend
- Added a responsive dashboard with a workflow timeline, a D3 workflow graph, a results panel, a sources panel, and a score explanation panel.
- Added active-stage highlighting and SSE-driven status updates in `static/js/main.js`.
- Added D3 node activation and responsive resizing in `static/js/truth-graph.js`.

## Current notes
- The app now runs with local-first Ollama when available and falls back to cloud providers when configured.
- Empty-input SSE runs still finish with a terminal `complete` event carrying `state.error` instead of a dedicated terminal error event.
- Some sources remain skipped in the indexer because they are blocked or too dynamic for the static fetch path.
