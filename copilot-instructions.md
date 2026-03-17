# The Eye Opener — Master Copilot Instructions

## Project overview
You are assisting in building "The Eye Opener", an AI-powered fact-checking platform for Indian political discourse. Always keep this context in mind for every suggestion, completion, and review.

## Tech stack
- **Backend**: Python, Flask, flask-cors
- **AI / Orchestration**: LangGraph, LangChain, langchain-openai, langchain-groq
- **LLM Routing**: `services/llm.py` with 3-tier free model architecture
    - Primary: Cerebras `llama-3.3-70b` (OpenAI-compatible API)
    - Fallback 1: Groq `llama-3.3-70b-versatile` (ChatGroq)
    - Fallback 2 (quality mode): GitHub Models `gpt-4.1-mini` (OpenAI-compatible API)
- **RAG**: ChromaDB, Google Generative AI embeddings
- **Retrieval**: duckduckgo-search, BeautifulSoup4, requests
- **Input handling**: youtube-transcript-api
- **Frontend**: Vanilla JS, D3.js (force-directed graph), SSE (Server-Sent Events)
- **Config**: python-dotenv

## Project folder structure
```
eye-opener/
├── .env                        # secrets, never committed
├── .env.example                # template with key names only
├── .gitignore
├── requirements.txt
├── config.py                   # loads .env via python-dotenv
├── app.py                      # Flask server, SSE route, CORS
├── services/
│   ├── state.py                # AgentState TypedDict
│   ├── preprocessor.py         # YouTube transcript + input cleaning
│   ├── llm.py                  # centralized LLM provider selector
│   ├── agents.py               # 4 worker agents
│   ├── architect.py            # LangGraph StateGraph definition
│   ├── runner.py               # executes graph, yields SSE events
│   └── indexer.py              # ChromaDB indexer for trusted sources
└── static/
    ├── index.html
    ├── css/style.css
    └── js/
        ├── main.js             # SSE listener, UI interactions
        └── truth-graph.js      # D3.js force-directed graph
```

## AgentState shape (always import from services/state.py)
```python
class AgentState(TypedDict):
    raw_input: str
    cleaned_text: str
    claims: list[str]
    research_logs: list[dict]
    critiques: list[str]
    verdicts: list[dict]
    truth_score: int              # 1–100
    active_agent: str             # name of currently running node
    retrieval_method: str         # "rag", "live_search", or "hybrid"
    error: Optional[str]          # None if pipeline succeeded
```

## The 5 pipeline nodes (in order)
1. `preprocessor` — cleans input, extracts YouTube transcripts
2. `surgeon` — extracts testable claims from cleaned_text
3. `diver` — retrieves evidence (RAG first, live search fallback)
4. `skeptic` — devil's advocate critique of evidence
5. `scorer` — calculates 1–100 truth score and per-claim verdicts

The Architect wires these into a LangGraph StateGraph. Any node can route to an `error` terminal node by setting `state["error"]`.

## Trusted Indian sources (Deep Diver targets)
- https://pib.gov.in
- https://altnews.in
- https://factly.in
- https://boomlive.in
- https://vishvasnews.com

## Coding rules — always follow these
- Never hardcode API keys. All secrets come from `config.py`.
- All agents must import `get_llm` from `services/llm.py` instead of constructing LLM clients directly.
- Always type-hint function signatures.
- Every agent function signature: `def agent_name(state: AgentState) -> AgentState`
- SSE events must always include `active_agent` and `event_type` fields.
- All Flask routes must handle exceptions and return JSON error responses.
- Use `Optional[str]` not `str | None` for Python 3.9 compatibility.
- Frontend JS uses vanilla JS only — no React, no jQuery.

## Git branch convention
- `main` — stable, protected
- `develop` — integration branch
- `feat/ai-pipeline` — Dev A (you)
- `feat/rag-retrieval` — Dev B
- `feat/frontend` — Dev C
- Commit format: `feat:`, `fix:`, `chore:`, `docs:`

## What to avoid
- Do not suggest adding new dependencies without updating requirements.txt.
- Do not suggest putting logic in app.py that belongs in services/.
- Do not suggest localStorage or sessionStorage for the frontend.
- Do not hallucinate library APIs — if unsure, say so.
