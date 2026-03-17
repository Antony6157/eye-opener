# Phase 4 — Frontend dashboard agent

## When to use this prompt
Use when building the full frontend. Reference with `#phase4-frontend` in Copilot Chat.

---

## Context
Single-page dark-themed dashboard. The user pastes a political claim or YouTube URL, submits it, and watches the D3.js force-directed graph animate as agents activate in real time. When the pipeline completes, a Results Panel appears showing the Truth Score, per-claim verdicts, and which retrieval method was used.

---

## File: static/index.html
Generate a complete single-page HTML file with this structure:

**Header bar**: Logo "👁 The Eye Opener" left-aligned. Subtitle "AI-powered fact-checking for Indian political discourse" right-aligned.

**Input section**:
- Large textarea (id: `claim-input`) placeholder: "Paste a political claim or YouTube URL..."
- Submit button (id: `submit-btn`) labelled "Verify Claim"
- Loading indicator (id: `loading`) hidden by default — shows a spinner and the current active agent name

**Graph section**:
- Full-width container (id: `graph-container`) for the D3 force graph
- Minimum height 420px

**Results panel** (id: `results-panel`) hidden by default. Contains:
- Large truth score badge (id: `truth-score`) — coloured: 0-40 red, 41-70 amber, 71-100 green
- Retrieval method badge (id: `retrieval-badge`) — labels: "RAG ✓", "Live Search", "Hybrid"
- List container (id: `verdicts-list`) for per-claim verdict cards
- Each verdict card shows: claim text, verdict label (True/False/Misleading/Unverifiable), confidence %, reasoning

**Script imports** at bottom of body:
- D3.js from CDN: `https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js`
- `static/js/truth-graph.js`
- `static/js/main.js`

---

## File: static/css/style.css
Dark theme. Key design tokens:
```css
--bg-primary: #0d0d0d;
--bg-surface: #1a1a1a;
--bg-card: #242424;
--accent-purple: #7c5cbf;
--accent-teal: #1a9e75;
--text-primary: #e8e8e8;
--text-muted: #888;
--border: #2e2e2e;
--score-red: #e24b4a;
--score-amber: #ef9f27;
--score-green: #639922;
```
Style all components including: header, input section, submit button (purple gradient on hover), loading spinner (CSS keyframe), graph container, results panel, verdict cards (border-left coloured by verdict type), truth score badge (large, bold, coloured).

---

## File: static/js/main.js
Handles all UI logic and SSE.

**On submit click**:
1. Read `claim-input` value, validate not empty
2. Disable submit button, show loading indicator
3. Open SSE connection: `new EventSource('/api/stream?input=' + encodeURIComponent(input))`

**On each SSE message**:
- Parse `data` field as JSON
- If `event_type === "step"`: update loading text to active agent name, call `window.truthGraph.activateNode(active_agent)`
- If `event_type === "complete"`: call `renderResults(state)`, hide loading, re-enable button, close SSE
- If `event_type === "error"`: show inline error message, hide loading, re-enable button, close SSE

**`renderResults(state)` function**:
- Populate truth score badge with `state.truth_score`, apply colour class
- Populate retrieval badge with `state.retrieval_method`
- For each verdict in `state.verdicts`: create a verdict card and append to `verdicts-list`
- Show results panel with a fade-in animation

---

## File: static/js/truth-graph.js
D3.js force-directed graph. Expose as `window.truthGraph`.

**Nodes**:
```js
const nodes = [
  { id: "claim",        label: "Claim",       type: "center"  },
  { id: "preprocessor", label: "Preprocessor", type: "worker"  },
  { id: "surgeon",      label: "Surgeon",      type: "worker"  },
  { id: "diver",        label: "Deep Diver",   type: "worker"  },
  { id: "skeptic",      label: "Skeptic",      type: "worker"  },
  { id: "scorer",       label: "Scorer",       type: "worker"  },
  { id: "architect",    label: "Architect",    type: "orchestrator" },
  { id: "error",        label: "Error",        type: "error"   },
]
```

**Links**: connect each worker to "claim" center node. Connect "architect" to all worker nodes.

**Visual rules**:
- Center node: large circle, purple fill
- Worker nodes: medium circles, dark surface fill, purple border
- Architect node: diamond shape (rotated square), teal fill
- Error node: small circle, red fill, hidden unless activated

**`activateNode(nodeId)` method** (exposed on `window.truthGraph`):
- Remove `active` class from all nodes
- Add `active` class to the node matching `nodeId`
- Active node: bright purple glow effect, scale up to 1.3×
- Animate the link between center and active node: stroke becomes bright, animated dash offset

**Init**: auto-size to `#graph-container` dimensions. Start force simulation with collision, link, and charge forces. Nodes draggable.
