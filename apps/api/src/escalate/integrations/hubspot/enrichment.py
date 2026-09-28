import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from escalate.integrations.hubspot.client import HubSpotClient


@dataclass(frozen=True)
class TicketMessage:
    external_id: str
    channel: str
    direction: str | None
    author: str | None
    subject: str | None
    body: str
    occurred_at: datetime


@dataclass(frozen=True)
class TicketContext:
    owner_id: str | None = None
    owner_name: str | None = None
    owner_email: str | None = None
    contact_email: str | None = None
    messages: list[TicketMessage] = field(default_factory=list)


@dataclass(frozen=True)
class EngagementSpec:
    """One HubSpot engagement object type and how to read it into a TicketMessage."""

    object_type: str
    channel: str
    properties: Sequence[str]
    body_keys: Sequence[str]
    subject_key: str | None = None
    direction_key: str | None = None
    author_key: str | None = None


_ENGAGEMENTS: tuple[EngagementSpec, ...] = (
    EngagementSpec(
        object_type="notes",
        channel="NOTE",
        properties=("hs_note_body", "hs_timestamp"),
        body_keys=("hs_note_body",),
    ),
    EngagementSpec(
        object_type="emails",
        channel="EMAIL",
        properties=(
            "hs_email_subject",
            "hs_email_text",
            "hs_email_html",
            "hs_email_direction",
            "hs_email_from_email",
            "hs_timestamp",
        ),
        body_keys=("hs_email_text", "hs_email_html"),
        subject_key="hs_email_subject",
        direction_key="hs_email_direction",
        author_key="hs_email_from_email",
    ),
    EngagementSpec(
        object_type="calls",
        channel="CALL",
        properties=(
            "hs_call_title",
            "hs_call_body",
            "hs_call_direction",
            "hs_call_duration",
            "hs_timestamp",
        ),
        body_keys=("hs_call_body", "hs_call_title"),
        subject_key="hs_call_title",
        direction_key="hs_call_direction",
    ),
    EngagementSpec(
        object_type="meetings",
        channel="MEETING",
        properties=(
            "hs_meeting_title",
            "hs_meeting_body",
            "hs_meeting_outcome",
            "hs_timestamp",
        ),
        body_keys=("hs_meeting_body", "hs_meeting_title"),
        subject_key="hs_meeting_title",
    ),
    EngagementSpec(
        object_type="tasks",
        channel="TASK",
        properties=("hs_task_subject", "hs_task_body", "hs_task_status", "hs_timestamp"),
        body_keys=("hs_task_body", "hs_task_subject"),
        subject_key="hs_task_subject",
    ),
)

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_DIRECTION_MAX = 16


def strip_html(value: str) -> str:
    """HubSpot note and email bodies arrive as HTML; the model wants flat text."""
    return _WHITESPACE_RE.sub(" ", _TAG_RE.sub(" ", value)).strip()


def _parse_timestamp(raw: str | None) -> datetime:
    if not raw:
        return datetime.now(UTC)
    try:
        return datetime.fromtimestamp(int(raw) / 1000, tz=UTC)
    except (TypeError, ValueError):
        return datetime.now(UTC)


def _first_value(properties: dict[str, Any], keys: Sequence[str]) -> str | None:
    for key in keys:
        value = properties.get(key)
        if value:
            return str(value)
    return None


async def _fetch_engagements(
    client: HubSpotClient, ticket_id: str, spec: EngagementSpec
) -> list[TicketMessage]:
    ids = await client.get_associations("tickets", ticket_id, spec.object_type)
    if not ids:
        return []
    messages = []
    for record in await client.batch_read(spec.object_type, ids, spec.properties):
        properties = record.get("properties") or {}
        body = _first_value(properties, spec.body_keys)
        if not body:
            continue
        direction = properties.get(spec.direction_key) if spec.direction_key else None
        messages.append(
            TicketMessage(
                external_id=str(record["id"]),
                channel=spec.channel,
                direction=str(direction)[:_DIRECTION_MAX] if direction else None,
                author=properties.get(spec.author_key) if spec.author_key else None,
                subject=properties.get(spec.subject_key) if spec.subject_key else None,
                body=strip_html(body),
                occurred_at=_parse_timestamp(properties.get("hs_timestamp")),
            )
        )
    return messages


async def fetch_ticket_context(
    client: HubSpotClient,
    ticket_id: str,
    owner_id: str | None,
    owner: dict[str, Any] | None = None,
) -> TicketContext:
    """Best-effort enrichment: any missing scope or API failure yields empty fields.

    `owner` may be supplied from a pre-loaded directory; HubSpot's single-owner
    endpoint 404s for deactivated users, so the directory is the reliable source.
    """
    owner_name = owner_email = contact_email = None

    if owner_id:
        owner = owner or await client.get_owner(owner_id)
        if owner:
            owner_email = owner.get("email")
            first, last = owner.get("firstName") or "", owner.get("lastName") or ""
            owner_name = f"{first} {last}".strip() or owner_email

    contact_ids = await client.get_associations("tickets", ticket_id, "contacts")
    if contact_ids:
        contacts = await client.batch_read("contacts", contact_ids[:1], ["email"])
        if contacts:
            contact_email = (contacts[0].get("properties") or {}).get("email")

    messages: list[TicketMessage] = []
    for spec in _ENGAGEMENTS:
        messages.extend(await _fetch_engagements(client, ticket_id, spec))

    messages.sort(key=lambda message: message.occurred_at)
    return TicketContext(
        owner_id=owner_id,
        owner_name=owner_name,
        owner_email=owner_email,
        contact_email=contact_email,
        messages=messages,
    )


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    clipped = value[:limit].rsplit(" ", 1)[0] or value[:limit]
    return f"{clipped}…"


def build_context_digest(
    context: TicketContext | None,
    *,
    max_messages: int,
    max_chars_per_message: int,
    max_chars: int,
) -> str:
    """Flatten a ticket's HubSpot context into bounded plain text for the decision model."""
    if context is None:
        return ""

    header = []
    if context.owner_name:
        header.append(f"Owner: {context.owner_name}")
    if context.contact_email:
        header.append(f"Contact: {context.contact_email}")

    lines = []
    for message in context.messages[-max_messages:]:
        stamp = message.occurred_at.date().isoformat()
        meta = "|".join(
            part for part in (message.channel, message.direction, message.author, stamp) if part
        )
        subject = f"{message.subject}: " if message.subject else ""
        body = _truncate(message.body, max_chars_per_message)
        lines.append(f"[{meta}] {subject}{body}")

    digest = "\n".join(header + lines).strip()
    while len(digest) > max_chars and lines:
        lines.pop(0)
        digest = "\n".join(header + lines).strip()
    return digest[:max_chars]
