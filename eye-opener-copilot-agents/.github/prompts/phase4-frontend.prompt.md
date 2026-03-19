# Phase 4 — Frontend dashboard agent

## When to use this prompt
Use when building the full frontend. Reference with `#phase4-frontend` in Copilot Chat.

---

## Context
The frontend is a single-page dashboard with a workflow timeline, a D3 graph, source/reference panels, and a settings drawer. The user pastes a political claim or YouTube URL, submits it, and watches the workflow animate as stages activate in real time. When the pipeline completes, the Results Panel shows the truth score, per-claim verdicts, retrieval method, and evidence summaries.

---

## File: static/index.html
Generate a complete single-page HTML file with this structure:

**Header bar**: Brand title on the left and a short subtitle on the right.

**Settings drawer**:
- Theme toggles
- LLM provider settings for Ollama, Cerebras, Groq, and GitHub
- Server info section

**Input section**:
- Large textarea (id: `claim-input`) for a claim or YouTube URL
- Submit button
- Loading indicator hidden by default that shows the current active stage

**Workflow section**:
- Full-width container (id: `graph-container`) for the D3 workflow graph
- Linear stage timeline with preprocessor, surgeon, diver, skeptic, scorer, and error handling cues

**Results panel** hidden by default. Contains:
- Large truth score badge
- Retrieval method badge
- Verdict list for per-claim verdict cards
- Sources used panel
- Score explanation panel

**Script imports** at bottom of body:
- D3.js from CDN
- `static/js/truth-graph.js`
- `static/js/main.js`

---

## File: static/css/style.css
Design for a polished light/dark responsive dashboard. Style all components including the header, settings drawer, input section, submit button, loading indicator, workflow timeline, D3 container, results panel, source cards, explanation cards, verdict cards, truth score badge, and mobile breakpoints.

---

## File: static/js/main.js
Handles all UI logic and SSE.

**On submit click**:
1. Read `claim-input` value, validate not empty
2. Disable submit button, show loading indicator
3. Open SSE connection with the submitted input

**On each SSE message**:
- Parse the payload as JSON
- If `event_type === "step"`: update loading text to the active stage, call `window.truthGraph.activateNode(active_agent)`, and update the workflow timeline
- If `event_type === "complete"`: call the result renderer, hide loading, re-enable button, close SSE
- If `event_type === "error"`: show inline error message, hide loading, re-enable button, close SSE

**`renderResults(state)` function**:
- Populate the truth score badge
- Populate the retrieval badge
- Render verdict cards
- Render sources used and score explanation panels
- Show results panel with a fade-in animation

---

## File: static/js/truth-graph.js
D3 workflow graph. Expose as `window.truthGraph`.

**Nodes**:
```js
const nodes = [
  { id: "claim", label: "Claim" },
  { id: "preprocessor", label: "Preprocessor" },
  { id: "surgeon", label: "Surgeon" },
  { id: "diver", label: "Diver" },
  { id: "skeptic", label: "Skeptic" },
  { id: "scorer", label: "Scorer" },
  { id: "architect", label: "Architect" },
  { id: "error", label: "Error" },
]
```

**Links**: connect the architecture node to the stage nodes and highlight the active route.

**Visual rules**:
- Center node: large circle
- Workflow nodes: medium circles with clear stage-specific color cues
- Architect node: distinct orchestrator marker
- Error node: hidden until activated

**`activateNode(nodeId)` method**:
- Remove `active` class from all nodes
- Add `active` class to the node matching `nodeId`
- Highlight the active node with a glow and scale-up effect
- Animate the active link with a moving dash offset

**Init**: auto-size to `#graph-container` dimensions and keep the graph responsive on resize.
