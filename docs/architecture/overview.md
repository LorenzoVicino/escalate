# Architecture

Escalate starts as a modular monolith. HTTP orchestration, ticket lifecycle, probabilistic analysis, deterministic routing, and persistence have explicit boundaries inside one deployable API. The `DecisionModel` protocol is the seam for a future inference-service extraction if independent GPU scaling or model releases justify it.

```mermaid
flowchart LR
    Web[React + TypeScript] -->|REST| API[FastAPI]
    API --> DB[(PostgreSQL)]
    API --> Analysis[Analysis module]
    Analysis --> Provider{DecisionModel}
    Provider --> Mock[Mock provider]
    Provider --> Laya[Laya Router]
    Analysis --> Rules[Deterministic routing engine]
    Rules --> DB
```

## Decision lifecycle

```mermaid
flowchart TD
    Ticket[Incoming ticket] --> Persist[Persist raw ticket]
    Persist --> Analyze[Laya or mock analysis]
    Analyze --> Signals[Probabilistic signals]
    Signals --> Route[Deterministic routing engine]
    Route --> Gate{Confidence gate}
    Gate -->|>= 0.90| Auto[Automatic route]
    Gate -->|0.70–0.89| Confirm[Operator confirmation]
    Gate -->|< 0.70| Manual[Manual triage]
    Auto --> Feedback[Future feedback dataset]
    Confirm --> Feedback
    Manual --> Feedback
```

## Implemented vertical slice

`POST /api/v1/tickets` owns a single transaction: it persists the ticket, invokes the configured provider, persists queryable analysis fields, evaluates routing rules, persists the decision, applies the confidence gate, and returns the complete result. If any stage fails, the transaction is rolled back.

The mock provider uses deterministic keyword scenarios only inside its adapter. No mock behavior leaks into the routing engine. The Laya adapter owns model initialization, question definitions, response parsing, normalization, and provider metadata.

