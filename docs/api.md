# API Reference

Base URL:
- http://localhost:5000

## GET /

Purpose:
- Serves the frontend page.

Success:
- 200 with HTML from [static/index.html](../static/index.html)

Failure:
- 500 with JSON error payload when static file serving fails

## GET /api/health

Purpose:
- Returns runtime and configuration health state.

Response payload fields:
- status
- config_ok
- config_errors
- config_warnings

Typical response:
- status: ok
- config_ok: true
- config_errors: empty list
- config_warnings: list may be empty or contain setup warnings

Notes:
- `config_errors` is currently wired but normally empty unless explicit blocking validation is introduced.

## GET /api/ollama-models

Purpose:
- Proxies Ollama's tags endpoint so the frontend can list locally available models.

Success:
- 200 with `status: ok` and a sorted list of model names

Failure:
- 502 when Ollama is unreachable
- 500 for unexpected proxy errors

## GET /api/settings

Purpose:
- Returns the current configurable runtime settings loaded from `config.py`.

## POST /api/settings

Purpose:
- Saves allowed settings back into `.env` and reloads the config module.

Accepted keys:
- USE_LOCAL_LLM
- OLLAMA_BASE_URL
- OLLAMA_MODEL
- CEREBRAS_API_KEY
- CEREBRAS_MODEL
- GROQ_API_KEY
- GROQ_MODEL
- GITHUB_TOKEN
- GITHUB_QUALITY_MODEL

## POST /api/verify

Purpose:
- Executes the full pipeline once and returns the final state in one response.

Request body:
- input: claim text or YouTube URL

Success:
- 200
- body contains `status: ok` and the final state object

Validation failure:
- 400
- body contains `status: error` and state.error details

Configuration failure:
- 503 when `config_errors` is non-empty

Route failure:
- 500 for unexpected exceptions

## GET /api/stream

Purpose:
- Runs the pipeline and streams step-level updates via SSE.

Query parameter:
- input

Content type:
- text/event-stream

Stream payload shape:
- active_agent
- event_type
- state_snapshot on step events
- state on terminal events

Observed event behavior:
- step events for each graph stage
- terminal event currently emitted as `complete`
- handled failures are represented by `state.error` even when the terminal event type is `complete`
- unhandled exceptions are emitted as `event_type: error`

Important edge-case note:
- empty input currently produces a terminal `complete` event with `error_handler` state and populated `state.error`.

## SSE event semantics

Step event example fields:
- active_agent: preprocessor, surgeon, diver, skeptic, scorer, or error_handler
- event_type: step
- state_snapshot: current state snapshot

Terminal event example fields:
- active_agent: final stage or error_handler
- event_type: complete (current behavior)
- state: final state snapshot

Client handling guidance:
- treat `state.error` as the authoritative error signal even when the terminal event type is `complete`

## CORS

Current configuration:
- Flask-CORS is enabled at app level
- cross-origin client requests are allowed in development

## API contract risks to track

1. Terminal event-type normalization for failures:
- currently mixed semantics (`complete` with error state)

2. Stability under upstream provider limits:
- retry logic is present for LLM acquisition, but end-to-end behavior should be integration-tested under load
