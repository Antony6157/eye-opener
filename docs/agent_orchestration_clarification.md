# Agent and Orchestrator Clarification

Date: 2026-03-19

## Why this note exists
Different files used to describe the pipeline using slightly different terms ("4 worker agents", "5-agent chain", "Architect orchestrator"), which can sound contradictory. This document defines the canonical interpretation based on the actual runtime code paths.

## Canonical answer
1. Worker agents: **4**
   - `surgeon`
   - `diver`
   - `skeptic`
   - `scorer`

2. Additional processing node before workers: **1**
   - `preprocessor`

3. Orchestrator: **Yes, in use**
   - The Architect exists as orchestration logic in `services/architect.py` and compiles the LangGraph state machine.

4. Error terminal node: **1**
   - `error_handler`

So depending on counting style:
- **4 worker agents** (strict worker-only count)
- **5 primary execution stages** (`preprocessor -> surgeon -> diver -> skeptic -> scorer`)
- **6 compiled graph nodes** (the 5 above + `error_handler`)

## Runtime evidence (source of truth)

### A) Architect graph is real and executed
- `services/architect.py` creates and compiles a `StateGraph`.
- Node registration:
  - `preprocessor`
  - `surgeon`
  - `diver`
  - `skeptic`
  - `scorer`
  - `error_handler`
- `services/runner.py` imports `graph` from `services/architect.py` and streams with `graph.stream(...)`.

### B) Worker separation in code
- Workers are implemented in `services/agents.py` (`surgeon`, `diver`, `skeptic`, `scorer`).
- `preprocessor` is implemented separately in `services/preprocessor.py`.

### C) API path proves orchestrated execution
- `app.py` routes (`/api/verify`, `/api/stream`) call `services/runner.py`.
- `services/runner.py` executes the compiled graph and emits SSE step/complete events.

## Where wording currently clashes

### 1) Planning/docs language
- `implementation_plan.md` says "4 worker agents + 1 Architect orchestrator (5 total nodes)".
- `README.md` says "5-agent LangGraph chain" and also shows a 5-stage sequence that does not include Architect as a stage.

### 2) Frontend representation
- `static/index.html` timeline lists 5 stage names (`preprocessor`, `surgeon`, `diver`, `skeptic`, `scorer`).
- `static/js/truth-graph.js` includes an explicit `architect` node for visualization.

This is not a runtime contradiction; it is a terminology mismatch between:
- "agents" (sometimes used for worker-only),
- "pipeline stages" (includes preprocessor),
- "graph nodes" (includes error terminal),
- and conceptual "Architect" orchestration.

## Recommended canonical phrasing (use this everywhere)
Use this exact wording in docs/UI text:

> "The pipeline has 4 worker agents (Surgeon, Diver, Skeptic, Scorer), plus a Preprocessor stage, all orchestrated by the Architect LangGraph state machine, with an Error Handler terminal node."

Optional short variants:
- "4 worker agents + 1 preprocessing stage; Architect orchestrates the graph."
- "5 primary stages, 6 graph nodes including error handler."

## Quick glossary
- **Worker agents**: `surgeon`, `diver`, `skeptic`, `scorer`
- **Preprocessor stage**: `preprocessor`
- **Architect orchestrator**: graph construction/routing logic in `services/architect.py`
- **Error terminal**: `error_handler`
- **Primary stage flow**: `preprocessor -> surgeon -> diver -> skeptic -> scorer`
