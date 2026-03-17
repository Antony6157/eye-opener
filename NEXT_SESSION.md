# NEXT_SESSION

## Section 1 — Current project status

### Fully working
- Backend app boots and `/api/health` returns OK.
- SSE pipeline runs end-to-end for non-empty claims through: `preprocessor -> surgeon -> diver -> skeptic -> scorer`.
- `retrieval_method` is being populated in final output (`hybrid` observed in multiple runs).
- Frontend wiring is now in place:
  - `static/index.html` includes D3 CDN + `truth-graph.js` + `main.js` in correct order.
  - Claim submit triggers SSE stream and updates active agent text/status.
  - Results panel populates on completion.
- D3 graph now renders in `#graph-container` with all 8 nodes visible at load.
- Graph node highlighting works visually during SSE (confirmed for surgeon/diver/skeptic/scorer in live runs).

### Partially working
- Full visual sequence from graph node classes is mostly confirmed, but `preprocessor` highlight is hard to reliably capture in automated sampling because the transition is very fast.
- Verdict quality is inconsistent across runs for complex factual claims; same pipeline may return strong verdicts in one run and weak/Unverifiable outputs in another.
- Source retrieval works, but evidence relevance/quality is inconsistent, especially on claims requiring authoritative government stats.

### Broken
- Some runs collapse to low-quality final scoring (`Unverifiable (0%)` across split claims) even when claim is likely verifiable.
- Rate-limit behavior is not hardened: 429 paths degrade output quality and can route to error handling instead of robust retry/fallback.
- Some source adapters/selectors are stale or blocked (PIB/BoomLive/VishvasNews issues below).
- Empty-input validation at runner level is still not fully verified for correct SSE error event semantics.

## Section 2 — Known bugs to fix

### Bug 1: `truth_score` becomes 0 when Groq hits 429 during skeptic/scorer
- Symptom:
  - Final score drops to `0` or run degrades after upstream 429s.
  - Pipeline can route to `error_handler` instead of recovering.
- Root cause (known/likely):
  - No resilient retry/backoff path around LLM calls in late pipeline stages.
  - Error bubbling marks state as fatal too early.
- File to fix:
  - `services/llm.py`
  - `services/agents.py` (error propagation handling in skeptic/scorer)
  - `services/architect.py` (only if graph routing logic needs non-fatal retry path)
- Exact fix to apply:
  1. Add retry wrapper in `services/llm.py` for 429 with exponential backoff.
  2. Try Cerebras first where configured; on retryable failure, fall back to Groq.
  3. Between retries, sleep 5s (then 10s, then 20s).
  4. Return structured retryable error metadata; in skeptic/scorer treat retryable failures as recoverable before setting terminal `error`.
  5. Only route to `error_handler` after max retries exhausted.

### Bug 2: Scorer returns `Unverifiable (0%)` for all claims in some runs
- Symptom:
  - Final verdict list contains mostly/only `Unverifiable (0%)`, including claims that should be checkable.
- Root cause (known/likely):
  - Upstream rate limiting causing low-context/empty context for scoring.
  - Evidence quality threshold too strict/poor retrieval match for certain claims.
  - Scoring prompt not robustly handling sparse but non-empty evidence.
- File to fix:
  - `services/agents.py` (scorer prompt/template and evidence packaging)
  - `services/retriever.py` (confidence threshold and evidence selection)
- Exact fix to apply:
  1. Update scorer prompt: default to `Unverifiable` only when evidence is truly insufficient, not as a blanket fallback.
  2. Ensure scorer receives top evidence snippets + source metadata consistently.
  3. Lower RAG threshold (see Section 3) to improve evidence intake.
  4. Add guardrail: if evidence count is zero due to retriever/LLM failure, surface explicit retrieval-quality warning in state.

### Bug 3: PIB source returns HTTP 403 in indexer
- Symptom:
  - Indexing or fetching PIB pages fails with 403.
- Root cause (known):
  - Requests do not look like a browser; missing realistic headers.
- File to fix:
  - `services/indexer.py`
- Exact fix to apply:
  1. Add browser-like headers: `User-Agent`, `Accept`, `Accept-Language`, `Referer`, and reasonable `Connection` settings.
  2. Reuse a `requests.Session()` with those headers.
  3. Add polite delay between requests and retry on transient failures.
  4. Log blocked URLs separately for re-run.

### Bug 4: BoomLive and VishvasNews selectors no longer match
- Symptom:
  - Extracted content is empty/partial or parser misses article body.
- Root cause (known):
  - Site DOM changed; static selectors are stale.
- File to fix:
  - `services/indexer.py`
- Exact fix to apply:
  1. Use Playwright to inspect current DOM for each site.
  2. Update selector map with primary + fallback selectors.
  3. Add selector health check: if extraction length below threshold, try fallback selector set.
  4. Add per-site extraction tests with stored sample URLs.

### Bug 5: Empty input emits `event_type: complete` instead of `event_type: error`
- Symptom:
  - Empty claim can terminate as `complete` rather than explicit validation error.
- Root cause (known/likely):
  - Runner/validation path marks run as done without standardized error event.
- File to fix:
  - `services/runner.py`
  - possibly `services/preprocessor.py` (if validation is there)
- Exact fix to apply:
  1. Add explicit early validation in runner entrypoint.
  2. For empty/whitespace input, emit SSE payload with `event_type: error`, set `state.error`, and stop stream.
  3. Keep this path distinct from normal `complete` finalization.
  4. Add a direct endpoint test to verify this behavior (not yet verified currently).

## Section 3 — Quality improvements to implement

1. Lower RAG confidence threshold from `0.75` to `0.60` in `services/retriever.py`.
2. Scorer prompt update in `services/agents.py`: default to `Unverifiable` when evidence is insufficient, not `False`.
3. Add exponential-backoff retry in `services/llm.py` for 429 errors:
   - Provider order: Cerebras first, then Groq fallback.
   - Wait 5s between retries (then scale up exponentially).
4. Add `time.sleep(...)` between DuckDuckGo site-restricted queries in live search to reduce rate limiting.

## Section 4 — Git tasks remaining

1. Create GitHub repository and push current code.
2. Set branch protection rules on `main` and `develop`.
3. Invite teammates Dev B and Dev C.
4. Teammate onboarding steps (each teammate):
   - Clone repository.
   - Create `.env` from `.env.example` with their own keys.
   - Run `python -m services.indexer` to build local vector data.

## Section 5 — How to resume next session

Paste this exact prompt into Copilot Chat at session start:

```text
Read and follow project context from these files first:
1) copilot-instructions.md
2) NEXT_SESSION.md
3) implementation_checklist.md

Then continue from Phase 5 hardening and bug-fix work only.
Priority order:
- Fix 429 retry/fallback behavior in services/llm.py and prevent premature error_handler routing.
- Fix scorer quality degradation (Unverifiable 0% overuse) by improving scorer prompt and evidence packaging.
- Fix indexer source reliability: PIB 403 headers, BoomLive/VishvasNews selector refresh via Playwright.
- Verify and fix empty-input SSE contract in services/runner.py so empty input emits event_type:error, not complete.

Constraints:
- Make minimal, targeted edits.
- After each fix, run a quick validation and report exact observed output.
- Do not start new features outside Phase 5 until these are stable.
```
