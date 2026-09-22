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

    tickets = client.get("/api/v1/tickets").json()
    assert len(tickets) == 2
    assert {ticket["source"] for ticket in tickets} == {"HUBSPOT"}
    security = next(ticket for ticket in tickets if ticket["title"].startswith("Possible"))
    detail = client.get(f"/api/v1/tickets/{security['id']}").json()
    assert detail["externalId"] == "hs-102"
    assert detail["customerName"] == "HubSpot customer"
    assert detail["routing"]["team"] == "SECURITY"
