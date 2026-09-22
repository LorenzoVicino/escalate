# ADR-002: Separate probabilistic analysis from deterministic routing

- Status: Accepted
- Date: 2026-09-22

## Context

Model predictions are uncertain and cannot own business policy. Security thresholds and escalation policy must remain testable and auditable.

## Decision

Providers return typed signals only. `RoutingDecisionEngine` combines those signals with centralized `RoutingThresholds` and produces the final tier, team, confidence mode, and deterministic reasons.

## Consequences

Routing thresholds can change without retraining a model. A provider can be replaced without rewriting ticket logic. Rule boundaries can be tested exactly.

