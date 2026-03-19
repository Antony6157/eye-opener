# Phase 5 — Integration testing agent

## When to use this prompt
Use when running the full end-to-end test and hardening pass. Reference with `#phase5-testing` in Copilot Chat.

---

## Your role
Act as a senior QA engineer. Review the code and verify that every item in this checklist passes. For each failure, suggest the exact fix.

---

## Test checklist

### 1. Environment and config
- [ ] `.env` exists and is in `.gitignore`
- [ ] `config.py` exposes a non-fatal warning when all LLM keys are missing (`CEREBRAS_API_KEY`, `GROQ_API_KEY`, `GITHUB_TOKEN`)
- [ ] `python -c "import config"` runs without error

### 2. Backend health
- [ ] `GET /api/health` returns `{"status": "ok"}` with HTTP 200
- [ ] CORS headers present on API responses
- [ ] Submitting a request from a different port succeeds

### 3. Plain text claim pipeline
- [ ] POST `/api/verify` or SSE to `/api/stream` with a real Indian political claim completes without error
- [ ] SSE events arrive in order: preprocessor → surgeon → diver → skeptic → scorer
- [ ] Final state contains `truth_score` between 1 and 100
- [ ] `verdicts` list is non-empty and each item has `claim`, `verdict`, `confidence`, `reasoning`

### 4. YouTube URL input
- [ ] Input a real YouTube URL of a political speech or press conference
- [ ] `preprocessor` correctly extracts transcript into `cleaned_text`
- [ ] Pipeline completes normally from transcript

### 5. RAG and retrieval
- [ ] `chroma_db/` folder exists and is non-empty after running the indexer
- [ ] `retrieval_method` field in final state is one of: `"rag"`, `"live_search"`, `"hybrid"`
- [ ] Querying a well-known fact can use the `"rag"` path when the local index covers it
- [ ] If ChromaDB returns low-confidence results, fallback to live search is triggered

### 6. Error state
- [ ] Pass an empty string as input - pipeline sets `error` and returns a clean error event or handled failure state
- [ ] Pass an invalid YouTube URL - preprocessor sets `error`, pipeline routes to error node
- [ ] Revoke all three keys (`CEREBRAS_API_KEY`, `GROQ_API_KEY`, `GITHUB_TOKEN`) and run pipeline - warning is visible and failure is returned as a controlled error response, not a 500 crash

### 7. Frontend
- [ ] Workflow graph renders on page load with all stages visible
- [ ] Each SSE step event highlights the correct node in the graph
- [ ] Results panel is hidden on load and appears only after pipeline completes
- [ ] Truth score badge color: red for ≤40, amber for 41–70, green for ≥71
- [ ] Retrieval badge correctly shows `"RAG ✓"`, `"Live Search"`, or `"Hybrid"`
- [ ] Page is usable on mobile screen widths (≥ 360px)

### 8. Git hygiene
- [ ] No `.env` file committed
- [ ] No `chroma_db/` folder committed
- [ ] All feature branches merged into `develop` via PR
- [ ] `develop` merged into `main` via PR with at least 1 approval

---

## How to use this prompt
Paste this prompt into Copilot Chat and then add:
> "Review my [filename] and tell me which of these checks it fails and why."

Or:
> "Write a pytest test for check #3 (plain text claim pipeline) using mock LLM responses."
