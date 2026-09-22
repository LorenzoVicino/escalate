# ADR-004: Start as a modular monolith

- Status: Accepted
- Date: 2026-09-22

## Context

The first valuable capability is one transactional workflow. Separate services would add networking, deployment, and consistency costs before scaling requirements exist.

## Decision

Deploy one FastAPI process with explicit ticket, analysis, routing, and persistence modules. Retain a provider protocol so inference can be extracted later for GPU isolation, independent scaling, or a separate release lifecycle.

## Consequences

Local operation and transactional behavior remain simple. Module boundaries prevent the monolith from becoming one undifferentiated service.

