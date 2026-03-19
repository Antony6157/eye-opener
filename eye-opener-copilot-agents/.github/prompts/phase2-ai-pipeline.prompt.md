# Phase 2 — AI pipeline agent

## When to use this prompt
Use when building the core LangGraph pipeline. Reference with `#phase2-ai-pipeline` in Copilot Chat.

---

## Context
The pipeline is a LangGraph StateGraph with 5 processing stages: preprocessor → surgeon → diver → skeptic → scorer, plus an error terminal node. All nodes share a single `AgentState` TypedDict defined in `services/state.py`.

---

## File: services/state.py
Generate the complete `AgentState` TypedDict with these exact fields:
```python
raw_input: str
cleaned_text: str
claims: list[str]
research_logs: list[dict]   # each: {claim, sources, evidence}
critiques: list[str]
verdicts: list[dict]        # each: {claim, verdict, confidence}
truth_score: int
active_agent: str
retrieval_method: str       # "rag" | "live_search" | "hybrid"
error: Optional[str]
```
Include an `initial_state(raw_input: str) -> AgentState` factory function.

---

## File: services/preprocessor.py
Function: `preprocess(state: AgentState) -> AgentState`
- Set `state["active_agent"] = "preprocessor"`
- Detect if `raw_input` is a YouTube URL (regex match on youtube.com/watch or youtu.be)
- If YouTube: use `youtube_transcript_api.YouTubeTranscriptApi` to fetch transcript, join to plain text, store in `cleaned_text`
- If plain text: strip whitespace, store directly in `cleaned_text`
- On any failure: set `state["error"]` with a descriptive message, return early
- Log each step with Python's `logging` module

---

## File: services/agents.py
Generate all 4 agent functions using the centralized helper from `services/llm.py`. Do not instantiate provider clients directly in `agents.py`.

Use this selection behavior:
- Surgeon, Diver, Skeptic: speed-first path with local Ollama when available, then cloud fallback routing
- Scorer: quality-first path with `prefer_quality=True`

**surgeon(state) → AgentState**
Prompt: extract all specific, verifiable factual claims from `cleaned_text`. Return as a numbered list. Parse response into `state["claims"]` as a Python list of strings. Set `active_agent = "surgeon"`.

**diver(state) → AgentState**
Use hybrid retrieval for each claim. Call `hybrid_search(claim)` and store the returned evidence in `state["research_logs"]`. Set `active_agent = "diver"`. Set `state["retrieval_method"]` based on the search result.

**skeptic(state) → AgentState**
Prompt: given the claims and research logs, act as a devil's advocate. Identify missing context, potential misquotations, selective framing, or unsupported assertions. Store critique strings in `state["critiques"]`. Set `active_agent = "skeptic"`.

**scorer(state) → AgentState**
Prompt: synthesize claims, evidence, and critiques. For each claim produce a verdict dict: `{claim, verdict: "True"|"False"|"Misleading"|"Unverifiable", confidence: 0-100, reasoning}`. Calculate overall `truth_score` from the per-claim scores. Set `active_agent = "scorer"`.

Each function must check for `state["error"]` at entry and return immediately if set.

---

## File: services/llm.py
Create a centralized provider selector with one public function:
`get_llm(prefer_quality: bool = False)`

Routing rules:
- Primary: local Ollama when `USE_LOCAL_LLM` is true and the service is reachable
- Fallback 1: Cerebras (`llama-3.3-70b`) via OpenAI-compatible `ChatOpenAI` client at `https://api.cerebras.ai/v1`
- Fallback 2: Groq (`llama-3.3-70b-versatile`) via `ChatGroq`
- GitHub Models (`gpt-4.1-mini`) via OpenAI-compatible `ChatOpenAI` client at `https://models.inference.ai.azure.com` only when `prefer_quality=True` and no other provider is available
- Choose providers based on keys loaded in `config.py`

---

## File: services/architect.py
Build the LangGraph `StateGraph`:
- Import all 4 agents plus the preprocessor from their modules
- Add nodes: preprocessor, surgeon, diver, skeptic, scorer, error_handler
- Set entry point: preprocessor
- Add edges: preprocessor → surgeon → diver → skeptic → scorer
- Add conditional edges from every node: if `state["error"]` is set, route to `error_handler`
- `error_handler` node: logs the error, sets `truth_score = 0`, returns state
- Compile and export as `graph = builder.compile()`

---

## File: services/runner.py
Function: `run_pipeline(raw_input: str) -> Generator`
- Build initial state using `initial_state(raw_input)`
- Use `graph.stream(state)` to iterate over state transitions
- After each transition yield a `text/event-stream` formatted string:
  ```
  data: {"active_agent": "...", "event_type": "step", "state_snapshot": {...}}
  ```
- On pipeline completion yield a final event with `event_type: "complete"` and full state
- On exception yield `event_type: "error"` with a message

The Flask SSE route in `app.py` calls this generator via `Response(run_pipeline(input), mimetype="text/event-stream")`.
