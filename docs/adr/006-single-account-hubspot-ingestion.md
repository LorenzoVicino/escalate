# ADR-006: Use a Private App for single-account HubSpot ingestion

- Status: Accepted
- Date: 2026-09-22

## Context

Escalate needs to retrieve support tickets from one company-owned HubSpot account. Multi-tenant installation and delegated customer authorization are not requirements.

## Decision

Authenticate with a HubSpot Private App token supplied only through environment configuration. Keep HubSpot behind an inbound adapter that owns pagination and property mapping. Import records read-only, identify them by `(HUBSPOT, HubSpot record ID)`, and send normalized tickets through the existing analysis and routing workflow.

## Consequences

OAuth token exchange and tenant credential tables are unnecessary. Repeated syncs are idempotent, and HubSpot response changes remain isolated. The sync endpoint must be operator-protected before internet exposure. Real-time webhooks require a later durable inbox plus signature validation; write-back requires a separate policy decision and additional scopes.

