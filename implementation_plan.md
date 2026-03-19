# The Eye Opener Implementation Plan

Date: March 19, 2026

## Goal

Build and harden an AI-powered political claim verification platform for India with:
- local-first inference when available
- hybrid retrieval
- real-time stage streaming
- transparent result presentation

## Current architecture baseline

Pipeline stages:
- preprocessor
- surgeon
- diver
- skeptic
- scorer

Graph orchestration:
- architect compiles and routes the LangGraph
- error_handler is the terminal failure path

Serving model:
- Flask backend
- SSE stream endpoint for live stage updates
- static frontend with D3 workflow graph and a settings drawer

## Completed implementation scope

Backend:
- app routes for health, verify, stream, ollama-models, and settings
- CORS enabled
- state contract defined and used across pipeline
- preprocess path supports text and YouTube transcript extraction

LLM layer:
- Ollama local primary provider when enabled and reachable
- Cerebras and Groq fallbacks
- GitHub Models quality mode fallback
- retry wrapper for rate-limit-like errors

Retrieval:
- Chroma RAG path implemented
- live fallback path implemented
- legal enrichment via IndianKanoon deep search
- PIB dedicated live search enrichment
- category-aware ordering for RAG evidence

Indexer:
- expanded source catalog with category metadata
- selector and fallback_selector support
- skip controls with skip_reason
- selector verification helper via Playwright
- Ollama-based local embeddings

Frontend:
- input, status, stream panel, workflow graph, result panels, and settings drawer
- active stage updates and graph highlighting
- completion rendering and inline error handling

## Remaining gap list

1. SSE terminal semantics for empty input:
- currently terminal event is complete with error state
- target behavior is a dedicated terminal error event type

2. Fail-fast config policy:
- config_errors channel exists, but strict blocking validation remains limited

3. Source ingestion completeness:
- blocked or JS-heavy sources remain live-only or skipped for indexing

4. Automated verification:
- integration and regression suite coverage is still limited

5. Doc and release hygiene:
- maintain strict sync between implementation and docs after each hardening cycle

## Execution plan from current state

### Phase A: Contract hardening
- normalize terminal error semantics for invalid or empty input stream runs
- add explicit runner-level edge-case tests for stream semantics

### Phase B: Retrieval quality hardening
- tune confidence threshold based on sampled claim set
- add retrieval diagnostics to help identify weak evidence runs
- improve scoring prompt robustness for sparse evidence

### Phase C: Indexer reliability hardening
- continue selector refresh for dynamic domains
- classify each source as indexed, live-only, or blocked with rationale
- optionally add JS-rendered fetch workflow for selected high-value sources

### Phase D: Test and release readiness
- add API contract tests for health, verify, stream, and settings
- add pipeline smoke tests for text and YouTube input
- add retriever unit tests for source split and dedupe behavior
- add release checklist and rollback notes

## Verification matrix (current target)

Core runtime:
- app boots
- health endpoint stable
- non-empty claim stream reaches terminal event

Pipeline behavior:
- ordered stage progression
- retrieval_method consistently populated
- verdicts and truth score rendered in UI

Edge cases:
- empty input stream emits a terminal failure state
- upstream provider unavailability has clear fallback behavior

Retriever:
- RAG-first path for indexed claims
- live fallback for novel claims and skipped domains
- legal and PIB enrichments produce additive, deduped URLs

Indexer:
- skip controls honored
- selector fallback works when primary selector misses
- metadata includes source category

## Acceptance criteria

1. Contract correctness:
- stream terminal semantics are deterministic and documented

2. Reliability:
- repeated runs do not collapse due to avoidable rate-limit handling gaps

3. Evidence quality:
- legal and policy claims receive authoritative source coverage often enough to avoid frequent unverifiable artifacts

4. Testability:
- key API and pipeline behaviors are covered by repeatable tests

5. Documentation fidelity:
- implementation docs match shipping code at all times
