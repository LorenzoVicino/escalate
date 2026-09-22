# ADR-003: Gate automation by confidence

- Status: Accepted
- Date: 2026-09-22

## Context

Automatically routing every prediction treats uncertainty as certainty and hides operational risk.

## Decision

Route automatically at confidence `>= 0.90`, require confirmation from `0.70` through `< 0.90`, and use manual triage below `0.70`. Thresholds are typed configuration. Non-automatic decisions include a human-review reason.

## Consequences

Uncertain predictions remain visible and actionable. The policy can later be calibrated from persisted feedback instead of anecdote.

