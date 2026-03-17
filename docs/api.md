# API Reference

Base URL: `http://localhost:5000`

## GET /

Serves frontend page from `static/index.html`.

Response:
- `200` HTML on success.
- `500` JSON error if static page load fails.

## GET /api/health

Returns server and configuration status.

Example response:

```json
{
  "status": "ok",
  "config_ok": true,
  "config_errors": [],
  "config_warnings": []
}
```

Notes:
- `config_warnings` includes missing-credential warnings.
- `config_errors` is currently present for future hard-stop validation but is not populated by default config logic.

## POST /api/verify

Runs the full pipeline once and returns final state.

Request body:

```json
{
  "input": "Claim text or YouTube URL"
}
```

Success response:
- `200` with:

```json
{
  "status": "ok",
  "state": {
    "raw_input": "...",
    "cleaned_text": "...",
    "claims": [],
    "research_logs": [],
    "critiques": [],
    "verdicts": [],
    "truth_score": 0,
    "active_agent": "scorer",
    "retrieval_method": "live_search",
    "error": null
  }
}
```

Failure responses:
- `400` if pipeline state contains `error`.
- `503` if server configuration has blocking errors.
- `500` for unexpected route-level exceptions.

## GET /api/stream?input=...

Runs the pipeline and streams JSON payloads over SSE.

SSE event format:

```text
data: {"active_agent":"preprocessor","event_type":"step","state":{...}}

```

Event types:
- `step`: emitted for each graph node transition.
- `complete`: emitted once with final state.

Headers/content type:
- `Content-Type: text/event-stream`

## CORS

CORS is enabled app-wide using `flask-cors`, allowing cross-origin client access during development.
