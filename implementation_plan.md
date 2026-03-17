# 'The Eye Opener' Implementation Plan

**Goal Description**: 
Develop 'The Eye Opener', an AI-powered fact-checking platform for Indian political discourse. The system uses a LangGraph-based state machine orchestrated by 'The Architect' and incorporates 4 specialized 'Worker' agents (Surgeon, Diver, Skeptic, Scorer) to verify claims against trusted Indian sources. The Deep Diver utilizes a hybrid retrieval architecture (ChromaDB RAG primary, DuckDuckGo Live Search fallback). Results and data flow are visualized in real-time using a D3.js Force-Directed Graph.

## User Review Required
> [!IMPORTANT]
> The updated architecture incorporates LangGraph for the state machine and the 4 worker agents + 1 Architect orchestrator (5 total nodes). 
> **NEW:** A hybrid retrieval system is now planned. `indexer.py` will handle offline scraping/indexing into a local ChromaDB instance. The Deep Diver agent will utilize this RAG layer first, and only fall back to live DuckDuckGo searching if the semantic search yields low-confidence results.
> A dedicated `services/runner.py` bridges graph execution to SSE streaming. Visualizations use a D3.js force-directed graph with glowing data flow links, and the Results Panel will display badges indicating the retrieval method used per claim. We are ready to proceed to EXECUTION.

## Proposed Changes

### Backend Skeleton (Flask)
- Create the core web server (`app.py`) to serve the frontend and handle API requests.
- Add a Server-Sent Events (SSE) route to stream LangGraph state transitions back to the frontend in real time.
- Configure `flask-cors` in `app.py` to allow cross-origin SSE requests during development and external client access.

#### [NEW] `requirements.txt`
Dependencies: `flask`, `flask-cors`, `langchain`, `langgraph`, `langchain-openai`, `langchain-groq`, `youtube-transcript-api`, `beautifulsoup4`, `ddgs`, `python-dotenv`, `requests`, `chromadb`, `langchain-community` etc.

#### [NEW] `.env`
Stores secrets: `CEREBRAS_API_KEY`, `GROQ_API_KEY`, `GITHUB_TOKEN`, and any other API tokens. Never committed to version control. Listed in `.gitignore`.

#### [NEW] `config.py`
Loads and exposes environment variables from `.env` via `python-dotenv`. All agents and app modules import keys from here — no hardcoded secrets anywhere.

#### [NEW] `app.py`
Main Flask server: route definitions, SSE endpoint, CORS setup, and frontend serving. Delegates graph execution to `services/runner.py`.

### Core AI Logic & Agents (LangGraph)

#### [NEW] `services/state.py`
Defines the `AgentState` TypedDict containing:
- `raw_input` — original text or YouTube URL
- `cleaned_text` — preprocessed plain text after transcript extraction (if applicable)
- `claims` — list of extracted testable claims
- `research_logs` — evidence gathered per claim
- `retrieval_method` — string indicating retrieval path: `"rag"`, `"live_search"`, or `"hybrid"`
- `critiques` — skeptic analysis notes
- `verdicts` — final per-claim truth assessments
- `truth_score` — integer 1–100 overall score
- `active_agent` — current node name for SSE/D3 updates
- `error` — Optional[str] capturing failure reason; None if pipeline succeeded

#### [NEW] `services/indexer.py`
**RAG Pipeline**: Scrapes and indexes content from trusted Indian sources (PIB, Alt News, Factly, Boom Live, Vishvas News) into a local ChromaDB instance using local vector indexing. Can be run as a standalone script to prepopulate the vector store.

#### [NEW] `services/preprocessor.py`
Input Handler (Preprocessing): Runs before the agent pipeline. Detects if input is a YouTube URL and uses `youtube-transcript-api` to extract the transcript. Passes cleaned plain text into `AgentState.cleaned_text` for The Surgeon to process. Handles fetch failures gracefully by writing to `AgentState.error`.

#### [NEW] `services/agents.py`
- **LLM Routing (Shared)**: All workers import `get_llm(prefer_quality=False)` from `services/llm.py` instead of instantiating clients inline. The chain is:
  - **Primary**: Cerebras `llama-3.3-70b` via OpenAI-compatible endpoint (`https://api.cerebras.ai/v1`)
  - **Fallback 1**: Groq `llama-3.3-70b-versatile` via `ChatGroq`
  - **Fallback 2 (quality mode only)**: GitHub Models `gpt-4.1-mini` via OpenAI-compatible endpoint (`https://models.inference.ai.azure.com`)
- **The Claims Surgeon** (Extraction): Scans `cleaned_text` and precision-extracts specific, testable factual claims into `AgentState.claims`.
- **The Deep Diver** (Hybrid Research): 
  - **Primary**: Queries the local ChromaDB vector store using semantic similarity search.
  - **Fallback**: If ChromaDB returns results below a confidence threshold, it falls back to site-restricted DuckDuckGo searches targeting trusted portals. Populates `AgentState.research_logs` and sets `AgentState.retrieval_method`.
- **The Skeptic** (Verification): Acts as devil's advocate — checks for missing context, selective quoting, and framing shifts in the research logs. Writes analysis to `AgentState.critiques`.
- **The Integrity Scorer** (Synthesis): Uses `get_llm(prefer_quality=True)` to prioritize GitHub Models quality inference, then weighs claims, evidence, and critiques to calculate a 1–100 Truth Score. Populates `AgentState.verdicts` and `AgentState.truth_score`.

#### [NEW] `services/architect.py`
**The Architect**: Defines and compiles the LangGraph `StateGraph`. Wires nodes in order: preprocessor → surgeon → diver → skeptic → scorer. Includes a dedicated error terminal node that any step can route to if `AgentState.error` is set. Manages all state transitions.

#### [NEW] `services/runner.py`
**Execution Bridge**: The critical link between `architect.py` and `app.py`. Invokes the compiled LangGraph graph, intercepts each state transition event, and yields SSE-formatted messages containing the `active_agent` name and relevant state snapshot. Called directly by the SSE route in `app.py` to stream live updates to the frontend.

### Frontend Dashboard
#### [NEW] `static/index.html`
Single-page dashboard with a modern dark theme. Contains:
- Text input area and YouTube URL input field
- Submit button
- D3.js graph container
- Results Panel — displays the final Truth Score (1–100), per-claim verdicts, a small badge indicating whether each claim was verified via RAG, live search, or both (`retrieval_method`), and an evidence summary once the pipeline completes. Hidden until the Scorer node finishes.

#### [NEW] `static/css/style.css`
Full dark-theme stylesheet. Covers layout, typography, input components, the results panel (score badge, verdict cards, retrieval method badges, evidence list), and D3 graph container styling.

#### [NEW] `static/js/main.js`
Handles UI interactions, API calls, and SSE listener. On receiving each SSE event:
- Updates the active agent in the D3 graph (triggers glow animation)
- On pipeline completion, populates and reveals the Results Panel with score, verdicts, and retrieval methodology badges based on the state's `retrieval_method`.
- On error state, displays an inline error message to the user.

#### [NEW] `static/js/truth-graph.js`
D3.js Force-Directed Graph logic:
- Central node representing the claim / overall process.
- Satellite nodes for: Surgeon, Diver, Skeptic, Scorer, and Architect.
- Glowing animated links illuminate between nodes based on the `active_agent` value streamed via SSE from `runner.py`.
- Error node lights up in red if the pipeline enters the error state.

## Verification Plan
### Manual Verification
- Test `services/indexer.py` to ensure it successfully scrapes and embeds documents into the ChromaDB vector store.
- Confirm `.env` loads correctly and no API keys are hardcoded.
- Run Flask app locally with a plain-text political claim and verify all 4 worker nodes fire sequentially.
- **Confirm RAG-first retrieval**: Check logs to verify that ChromaDB is queried first and succeeds for known ingested claims.
- **Confirm Live Search fallback**: Query a completely novel claim not present in ChromaDB and verify that the Deep Diver gracefully falls back to the duckduckgo-search mechanism.
- Run with a YouTube URL input and verify the preprocessor extracts the transcript before passing to The Surgeon.
- Simulate a Deep Diver search failure (both RAG and fallback) and confirm the pipeline routes to the error node cleanly.
- Verify the D3.js force graph renders with correct glowing links corresponding to each backend step via SSE.
- Confirm the Results Panel populates with the Truth Score, verdicts, evidence summary, and the correct retrieval method badges on completion.
- Test SSE from a separate origin to confirm CORS is correctly configured.
