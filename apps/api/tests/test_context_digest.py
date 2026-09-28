from datetime import UTC, datetime

from escalate.integrations.hubspot.enrichment import (
    TicketContext,
    TicketMessage,
    build_context_digest,
    strip_html,
)

DEFAULTS = {"max_messages": 8, "max_chars_per_message": 600, "max_chars": 4000}


def message(body: str, *, channel: str = "NOTE", day: int = 1) -> TicketMessage:
    return TicketMessage(
        external_id=f"m-{day}",
        channel=channel,
        direction=None,
        author=None,
        subject=None,
        body=body,
        occurred_at=datetime(2026, 9, day, tzinfo=UTC),
    )


def test_strip_html_flattens_hubspot_markup() -> None:
    assert strip_html("<p>Hello<br/> <b>world</b></p>") == "Hello world"


def test_digest_is_empty_without_context() -> None:
    assert build_context_digest(None, **DEFAULTS) == ""


def test_digest_includes_owner_contact_and_messages() -> None:
    context = TicketContext(
        owner_name="Anna Rossi",
        contact_email="customer@acme.io",
        messages=[message("Called the customer back", channel="CALL")],
    )
    digest = build_context_digest(context, **DEFAULTS)
    assert "Owner: Anna Rossi" in digest
    assert "Contact: customer@acme.io" in digest
    assert "[CALL|2026-09-01] Called the customer back" in digest


def test_digest_keeps_only_the_most_recent_messages() -> None:
    context = TicketContext(messages=[message(f"body {i}", day=i) for i in range(1, 13)])
    digest = build_context_digest(context, **{**DEFAULTS, "max_messages": 3})
    assert "body 12" in digest
    assert "body 9" not in digest
    assert len(digest.splitlines()) == 3


def test_digest_truncates_long_bodies_and_respects_global_cap() -> None:
    context = TicketContext(messages=[message("word " * 500)])
    digest = build_context_digest(context, **{**DEFAULTS, "max_chars_per_message": 50})
    assert digest.endswith("…")

    many = TicketContext(messages=[message("x" * 300, day=i) for i in range(1, 9)])
    assert len(build_context_digest(many, **{**DEFAULTS, "max_chars": 400})) <= 400
