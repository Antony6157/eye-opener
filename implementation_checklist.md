# The Eye Opener - Master Implementation Checklist

Date created: March 18, 2026
Last reviewed: March 18, 2026 (post-Phase 4 frontend validation)

Note: status updates below are based on repository code inspection, not full runtime QA.

## Phase 0 - Project Bootstrap and Guardrails

### Scope
- [x] Initialize repository structure.
- [x] Add core config and dependency files.
- [x] Set up minimal Flask server and health route.

### Deliverables
- [x] `.gitignore`
- [x] `.env.example`
- [x] `requirements.txt`
- [x] `config.py`
- [x] `app.py` with `/api/health`
- [x] `services/` directory
- [x] `static/css/` directory
- [x] `static/js/` directory

### Exit criteria
- [x] App boots successfully.
- [x] Health endpoint returns success JSON.
- [ ] Missing critical env vars fail fast with actionable error.

## Phase 1 - State Contract and Input Preprocessing

### Scope
- [x] Define canonical `AgentState` used across all agents.
- [x] Build preprocessing for plain text and YouTube URLs.

### Deliverables
- [x] `services/state.py`
- [x] `services/preprocessor.py`

### Implementation checks
- [x] Preserve `raw_input` for traceability.
- [x] Populate `cleaned_text` after normalization/transcript extraction.
- [x] On transcript/input failure, set `error` in state instead of crashing.

### Exit criteria
- [x] Deterministic preprocessing output for valid text input.
- [x] Graceful failure path for invalid/unavailable YouTube transcripts.

## Phase 2 - LangGraph Core Pipeline and SSE Bridge

### Scope
- [x] Implement the 4 worker agents and orchestrator graph.
- [x] Add execution runner that streams transitions to frontend.

### Deliverables
- [x] `services/agents.py` (Surgeon, Diver stub/live-only, Skeptic, Scorer)
- [x] `services/architect.py` (state graph + error terminal)
- [x] `services/runner.py` (SSE event stream)
- [x] `app.py` SSE endpoint integration

### Implementation checks
- [x] Each node updates `active_agent`.
- [x] SSE payload includes `event_type` and `active_agent`.
- [x] Error state routes to dedicated terminal node.

### Exit criteria
- [x] End-to-end text claim run succeeds.
- [x] SSE emits ordered progression events through pipeline.
- [x] Final payload includes verdicts and `truth_score`.

## Phase 3 - RAG Indexing and Hybrid Retrieval

### Scope
- [x] Build offline indexer for trusted Indian sources.
- [x] Implement hybrid search policy: RAG-first, live fallback.

### Deliverables
- [x] `services/indexer.py`
- [x] `services/retriever.py`
- [x] `services/agents.py` updated so Diver uses hybrid retrieval

### Implementation checks
- [x] Trusted sources covered: PIB, Alt News, Factly, Boom Live, Vishvas News.
- [x] If RAG confidence is below threshold, fallback to live search.
- [x] Persist retrieval path to `retrieval_method` (`rag`, `live_search`, `hybrid`).

### Exit criteria
- [ ] Indexed claims resolve through RAG path.
- [ ] Novel claims trigger fallback successfully.
- [x] Dual-channel failure sets clear `error` and exits safely.

## Phase 4 - Frontend Dashboard and D3 Live Graph

### Scope
- [x] Implement user input UI, SSE client, results rendering, and graph animations.

### Deliverables
- [x] `static/index.html`
- [x] `static/css/style.css`
- [x] `static/js/main.js`
- [x] `static/js/truth-graph.js`

### Implementation checks
- [ ] Include text input + YouTube URL input.
- [x] Render active node glow based on streamed `active_agent`.
- [ ] Display truth score, verdict cards, evidence summary, retrieval badges.
- [x] Show inline error state when backend pipeline fails.

### Exit criteria
- [x] User can submit claim and see real-time graph progression.
- [x] Results panel correctly renders final output.
- [ ] UI works on desktop and mobile breakpoints.

## Phase 5 - Integration Testing and Hardening

### Scope
- [ ] Validate all critical user flows and failure scenarios.
- [ ] Improve logging, resilience, and release readiness.

### Verification matrix
- [x] Env loading and secret handling
- [x] Flask health route and API stability
- [x] Plain text claim pipeline
- [x] YouTube transcript pipeline
- [x] RAG-first retrieval behavior
- [x] Live fallback behavior
- [x] Error-route behavior
- [ ] SSE/CORS behavior from separate origin
- [x] Frontend render consistency

### Exit criteria
- [ ] All critical tests pass.
- [ ] Failure modes are visible and actionable.
- [ ] Repository is clean and ready for team development/release.

## Phase 6 - Post-MVP Optimization (Optional)

### Scope
- [ ] Apply quality and performance improvements after MVP baseline is stable.

### Candidate tasks
- [ ] Tune RAG confidence threshold.
- [ ] Improve prompt quality for claim extraction/scoring.
- [ ] Add regression tests for state schema and retrieval decisions.
- [ ] Optimize frontend rendering for large claim sets.

## Cross-Phase Verification (from implementation plan)

### Backend skeleton
- [x] SSE route streams state transitions.
- [x] CORS allows cross-origin SSE during development.

### LLM routing
- [x] `services/llm.py` used by workers.
- [x] Surgeon/Diver/Skeptic use `get_llm()`.
- [x] Scorer uses `get_llm(prefer_quality=True)`.

### Retrieval behavior
- [x] Deep Diver uses RAG first when available.
- [x] Deep Diver falls back to live search for low-confidence/novel claims.

### Results and UX
- [ ] Results panel shows score, verdicts, evidence summary.
- [ ] Retrieval method badges are displayed correctly.
- [x] Error state is visible and understandable in UI.

## Milestone sequence tracker
- [x] Milestone 1: Bootstrap repo and run health check.
- [x] Milestone 2: Lock `AgentState` and preprocessing behavior.
- [x] Milestone 3: Run first end-to-end pipeline without hybrid retrieval.
- [x] Milestone 4: Add RAG index + hybrid fallback and re-test pipeline.
- [x] Milestone 5: Connect frontend to live SSE updates.
- [ ] Milestone 6: Execute integration test matrix and fix defects.
- [ ] Milestone 7: Start optimization cycle from observed bottlenecks.
