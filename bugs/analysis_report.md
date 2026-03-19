# Eye Opener — Issue Analysis Report

This is an updated issue archive for the current repository state.

## Issues that are already resolved
- The live search path now returns results and includes a `text` field.
- PIB and legal deep-search helpers now return results.
- The D3 workflow graph is present in the current frontend.
- The frontend now includes sources and score explanation panels.

## Remaining issues worth tracking

### 1. Empty input terminal semantics
- Empty input still completes through the handled failure path and yields a terminal `complete` event with `state.error`.
- Current fix target: normalize this to a dedicated terminal error event if the API contract needs that distinction.

### 2. LLM cost and latency
- The pipeline still performs multiple LLM calls per run.
- The largest latency and memory cost comes from the local Ollama model when it is enabled.
- Current mitigation: local-first routing plus cloud fallback paths; further optimization would require smaller models, caching, or lower concurrency.

### 3. Verdict quality variance
- Hard factual claims can still vary from run to run depending on retrieval depth and live-source quality.
- Current mitigation: RAG-first retrieval, legal/PIB enrichment, and JSON-based scorer output.

### 4. Source coverage gaps
- Several sites remain intentionally skipped in the indexer because they are blocked, dynamic, or JS-heavy.
- That means some claims still rely on live search snippets rather than full indexed source documents.

## Current priority matrix

| Priority | Issue | Impact |
|----------|-------|--------|
| 🟠 P1 | Empty input terminal semantics | Contract ambiguity in SSE output |
| 🟠 P1 | LLM latency and cost | Slow runs and memory pressure |
| 🟡 P2 | Verdict quality variance | Inconsistent fact-check outcomes |
| 🟡 P2 | Source coverage gaps | Some claims still lack authoritative evidence |
