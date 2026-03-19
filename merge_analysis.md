# Merge Analysis & Strategy

This repository is already the merged baseline. Keep this note as an archival reminder of what was resolved during the merge.

## What this repo currently reflects
- Local-first Ollama routing with Cerebras/Groq/GitHub fallbacks.
- Hybrid retrieval with ChromaDB, live DuckDuckGo fallback, and legal/PIB enrichment.
- A D3 workflow graph plus timeline-based UI, results panels, and source/explanation panels.
- SSE streaming with step events and terminal completion events.

## Archived merge takeaways
- The backend side of the merge won: `config.py`, `llm.py`, `indexer.py`, `retriever.py`, and `agents.py` now reflect the more advanced implementation.
- The frontend side of the merge also landed: the current UI keeps the workflow graph, sources panel, and score explanation panel together.
- Historical notes about missing `text` fields, missing returns, or D3 removal no longer apply to the shipped code.

## Current maintenance rule
- If a new doc or prompt disagrees with the live code, update the doc to match the code rather than copying older merge assumptions back into the repo.
