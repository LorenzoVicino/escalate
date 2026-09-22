# ADR-005: Persist ticket, analysis, and routing separately

- Status: Accepted
- Date: 2026-09-22

## Context

Raw customer input, model predictions, and business decisions have different meanings and lifecycles. A single JSON document would obscure queries and evaluation history.

## Decision

Store them in `tickets`, `ticket_analyses`, and `routing_decisions`. Important signal values and confidences are typed columns; provider-only metadata may use JSON. Human feedback will receive its own relation in the next vertical slice.

## Consequences

Predictions can be re-evaluated without rewriting raw tickets, decisions remain auditable, and later feedback can compare prediction, recommendation, and final operator action.

