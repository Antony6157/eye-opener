# Architecture Notes: Current State vs Documentation

## What is actually implemented right now
- Architect orchestrator is real and in use.
- Graph is built and compiled in [services/architect.py](services/architect.py).
- Runner imports and executes that compiled graph in [services/runner.py](services/runner.py).
- Worker count is 4.
- The worker functions are surgeon, diver, skeptic, and scorer in [services/agents.py](services/agents.py).
- Preprocessor is separate in [services/preprocessor.py](services/preprocessor.py).
- Architect is orchestration logic, not a streamed worker step.
- Streamed steps come from graph node events in [services/runner.py](services/runner.py).
- The final SSE payload uses the last node state, with `event_type: complete` on normal or handled-failure completion.

## Why the wording drifted
- Some docs count only worker agents.
- Some docs count the preprocessing stage too.
- The graph includes `error_handler`, but the UI timeline and the SSE step stream only surface the processing stages that actually run in order.

## Canonical truth to use going forward
- 4 worker agents: surgeon, diver, skeptic, scorer.
- 1 preprocessing node before workers.
- Architect orchestrator exists and is used to wire and execute the graph.
- Error handler node exists for terminal failures.

## Counting guide
- Worker agents = 4
- Main pipeline stages = 5
- Graph nodes including error handler = 6
