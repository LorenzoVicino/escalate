from typing import Any

from fastapi.testclient import TestClient

from escalate.integrations.hubspot.schemas import HubSpotTicketPage


class FakeHubSpotClient:
    async def list_tickets(self, **_: Any) -> HubSpotTicketPage:
        return HubSpotTicketPage.model_validate(
            {
                "results": [
                    {
                        "id": "hs-101",
                        "properties": {
                            "subject": "API authentication failing",
                            "content": "Our integration returns 401 after changing credentials.",
                            "company_name": "Acme Mobility",
                        },
                        "createdAt": "2026-09-22T08:00:00Z",
                        "updatedAt": "2026-09-22T08:01:00Z",
                    },
                    {
                        "id": "hs-102",
                        "properties": {
                            "subject": "Possible unauthorized access",
                            "content": "Users report unknown IP sessions and account changes.",
                            "company_name": "Northstar Logistics",
                        },
                        "createdAt": "2026-09-22T09:00:00Z",
                        "updatedAt": "2026-09-22T09:01:00Z",
                    },
                ]
            }
        )

    async def list_owners(self, **_: Any) -> list:
        return []

    async def get_owner(self, owner_id: str) -> None:
        return None

    async def get_associations(self, object_type: str, object_id: str, to_object_type: str) -> list:
        return []

    async def batch_read(self, object_type: str, ids: list, properties: list) -> list:
        return []

    async def close(self) -> None:
        pass


def test_sync_requires_configuration(client: TestClient) -> None:
    response = client.post("/api/v1/integrations/hubspot/sync")
    assert response.status_code == 503


def test_sync_imports_routes_and_deduplicates_hubspot_tickets(client: TestClient) -> None:
    client.app.state.hubspot_client = FakeHubSpotClient()

    first = client.post("/api/v1/integrations/hubspot/sync")
    assert first.status_code == 200
    assert first.json() == {
        "imported": 2,
        "skipped": 0,
        "pages": 1,
        "nextCursor": None,
    }

    second = client.post("/api/v1/integrations/hubspot/sync")
    assert second.status_code == 200
    assert second.json()["imported"] == 0
    assert second.json()["skipped"] == 2

    tickets = client.get("/api/v1/tickets").json()["items"]
    assert len(tickets) == 2
    assert {ticket["source"] for ticket in tickets} == {"HUBSPOT"}
    security = next(ticket for ticket in tickets if ticket["title"].startswith("Possible"))
    detail = client.get(f"/api/v1/tickets/{security['id']}").json()
    assert detail["externalId"] == "hs-102"
    assert detail["customerName"] == "HubSpot customer"
    assert detail["routing"]["team"] == "SECURITY"
    assert detail["ownerName"] is None
    assert detail["messages"] == []


_ASSOCIATED = {"contacts", "notes", "emails", "calls", "meetings", "tasks"}

_BATCH_READ: dict[str, list[dict]] = {
    "contacts": [{"id": "contacts-1", "properties": {"email": "customer@acme.io"}}],
    "notes": [
        {
            "id": "notes-1",
            "properties": {
                "hs_note_body": "<p>Called the customer back.</p>",
                "hs_timestamp": "1758528000000",
            },
        }
    ],
    "emails": [
        {
            "id": "emails-1",
            "properties": {
                "hs_email_subject": "Re: API authentication failing",
                "hs_email_text": "Please try rotating the credential.",
                "hs_email_direction": "INCOMING_EMAIL",
                "hs_email_from_email": "agent@example.com",
                "hs_timestamp": "1758531600000",
            },
        }
    ],
    "calls": [
        {
            "id": "calls-1",
            "properties": {
                "hs_call_title": "Follow-up call",
                "hs_call_body": "Walked through the credential rotation.",
                "hs_call_direction": "OUTBOUND",
                "hs_timestamp": "1758535200000",
            },
        }
    ],
    "meetings": [
        {
            "id": "meetings-1",
            "properties": {
                "hs_meeting_title": "Incident review",
                "hs_meeting_body": "Agreed on a permanent fix.",
                "hs_timestamp": "1758538800000",
            },
        }
    ],
    "tasks": [
        {
            "id": "tasks-1",
            "properties": {
                "hs_task_subject": "Rotate production credential",
                "hs_task_body": "Due before the next release.",
                "hs_timestamp": "1758542400000",
            },
        }
    ],
}


class EnrichedFakeHubSpotClient(FakeHubSpotClient):
    async def list_tickets(self, **kwargs: Any) -> HubSpotTicketPage:
        page = await super().list_tickets(**kwargs)
        for ticket in page.results:
            ticket.properties["hubspot_owner_id"] = "owner-1"
        return page

    async def get_owner(self, owner_id: str) -> dict | None:
        return {"email": "agent@example.com", "firstName": "Anna", "lastName": "Rossi"}

    async def get_associations(self, object_type: str, object_id: str, to_object_type: str) -> list:
        return [f"{to_object_type}-1"] if to_object_type in _ASSOCIATED else []

    async def batch_read(self, object_type: str, ids: list, properties: list) -> list:
        return _BATCH_READ.get(object_type, [])


def test_sync_enriches_tickets_with_owner_contact_and_conversation(client: TestClient) -> None:
    client.app.state.hubspot_client = EnrichedFakeHubSpotClient()

    client.post("/api/v1/integrations/hubspot/sync")

    tickets = client.get("/api/v1/tickets").json()["items"]
    ticket = next(t for t in tickets if t["title"].startswith("API authentication"))
    detail = client.get(f"/api/v1/tickets/{ticket['id']}").json()

    assert detail["ownerName"] == "Anna Rossi"
    assert detail["ownerEmail"] == "agent@example.com"
    assert detail["contactEmail"] == "customer@acme.io"
    assert [m["channel"] for m in detail["messages"]] == [
        "NOTE",
        "EMAIL",
        "CALL",
        "MEETING",
        "TASK",
    ]
    assert detail["messages"][1]["subject"] == "Re: API authentication failing"
    assert detail["messages"][2]["direction"] == "OUTBOUND"
    # HTML from HubSpot is flattened before it reaches the model or the UI.
    assert detail["messages"][0]["body"] == "Called the customer back."


def test_queue_is_ordered_by_when_the_ticket_was_raised(client: TestClient) -> None:
    """Import order says nothing about ticket age, so the queue sorts on the HubSpot date."""
    client.app.state.hubspot_client = FakeHubSpotClient()
    client.post("/api/v1/integrations/hubspot/sync")

    items = client.get("/api/v1/tickets").json()["items"]
    # hs-102 was created an hour after hs-101 in HubSpot, though both imported together.
    assert [item["title"] for item in items] == [
        "Possible unauthorized access",
        "API authentication failing",
    ]
    assert items[0]["raisedAt"].startswith("2026-09-22T09:00")


def test_owner_name_resolves_for_deactivated_users(client: TestClient) -> None:
    """HubSpot 404s on GET /owners/{id} for deactivated users, so the sync must
    resolve names from the owners listing (which includes archived ones)."""

    class ArchivedOwnerClient(FakeHubSpotClient):
        async def list_tickets(self, **kwargs: Any) -> HubSpotTicketPage:
            page = await super().list_tickets(**kwargs)
            for ticket in page.results:
                ticket.properties["hubspot_owner_id"] = "gone-1"
            return page

        async def list_owners(self, **kwargs: Any) -> list:
            if not kwargs.get("archived"):
                return []
            return [
                {
                    "id": "gone-1",
                    "email": "ex@example.com",
                    "firstName": "Ex",
                    "lastName": "Employee",
                }
            ]

        async def get_owner(self, owner_id: str) -> None:
            return None  # mirrors the real 404

    client.app.state.hubspot_client = ArchivedOwnerClient()
    client.post("/api/v1/integrations/hubspot/sync")

    ticket = client.get("/api/v1/tickets").json()["items"][0]
    detail = client.get(f"/api/v1/tickets/{ticket['id']}").json()
    assert detail["ownerName"] == "Ex Employee"
    assert client.get("/api/v1/tickets?ownerId=gone-1").json()["total"] == 2


def test_owners_endpoint_lists_hubspot_users(client: TestClient) -> None:
    class OwnersClient(FakeHubSpotClient):
        async def list_owners(self, **_: Any) -> list:
            return [
                {"id": "1", "email": "a@example.com", "firstName": "Anna", "lastName": "Rossi"}
            ]

    client.app.state.hubspot_client = OwnersClient()
    response = client.get("/api/v1/integrations/hubspot/owners")
    assert response.status_code == 200
    assert response.json() == [
        {"id": "1", "email": "a@example.com", "firstName": "Anna", "lastName": "Rossi"}
    ]


def test_owners_endpoint_requires_configuration(client: TestClient) -> None:
    assert client.get("/api/v1/integrations/hubspot/owners").status_code == 503


def test_conversation_context_reaches_the_decision_model(client: TestClient) -> None:
    """The mock provider keys off 'unauthorized', which appears ONLY in the note body."""

    class SecurityContextClient(FakeHubSpotClient):
        async def list_tickets(self, **kwargs: Any) -> HubSpotTicketPage:
            return HubSpotTicketPage.model_validate(
                {
                    "results": [
                        {
                            "id": "hs-900",
                            "properties": {
                                "subject": "Question about the portal",
                                "content": "A customer asked how to export a report.",
                            },
                            "createdAt": "2026-09-22T08:00:00Z",
                            "updatedAt": "2026-09-22T08:01:00Z",
                        }
                    ]
                }
            )

        async def get_associations(self, object_type: str, object_id: str, to: str) -> list:
            return ["notes-1"] if to == "notes" else []

        async def batch_read(self, object_type: str, ids: list, properties: list) -> list:
            if object_type != "notes":
                return []
            return [
                {
                    "id": "notes-1",
                    "properties": {
                        "hs_note_body": "Caller reported unauthorized access to the account.",
                        "hs_timestamp": "1758528000000",
                    },
                }
            ]

    client.app.state.hubspot_client = SecurityContextClient()
    client.post("/api/v1/integrations/hubspot/sync")

    ticket = client.get("/api/v1/tickets").json()["items"][0]
    detail = client.get(f"/api/v1/tickets/{ticket['id']}").json()
    # Title/description alone would never route here — only the note body can.
    assert detail["routing"]["team"] == "SECURITY"
