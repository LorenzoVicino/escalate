# ADR-001: Use Laya for decision inference

- Status: Accepted
- Date: 2026-09-22

## Context

Escalate needs typed probabilistic signals rather than generated support replies. The model must be swappable and practical to preload in an API process.

## Decision

Use Laya 0.3.5 through its external Python package and `Router(preload=True)`. Keep all Laya imports, questions, normalization, and response parsing inside `LayaDecisionModel`. Use `MockDecisionModel` by default for lightweight local development and tests.

## Consequences

The application does not vendor model source or load a checkpoint per request. The real provider has substantial ML dependencies and model-download costs, so it is an explicit installation/build option.

