from fastapi.testclient import TestClient
from sqlalchemy import func, select

from escalate.db.models import RoutingDecisionRecord, TicketAnalysisRecord, TicketRecord
from escalate.db.session import SessionLocal


def create(client: TestClient, title: str, description: str) -> dict[str, object]:
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": title,
            "description": description,
            "customerName": "Acme Mobility",
            "source": "WEB",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_complete_ticket_lifecycle_is_persisted_and_returned(client: TestClient) -> None:
    result = create(
        client,
        "All customer vehicles offline",
        "Since 08:30 all 250 vehicles from our production fleet appear offline.",
    )

    assert result["analysis"]["category"]["value"] == "PRODUCTION_INCIDENT"
    assert result["routing"]["supportTier"] == "ENGINEERING"
    assert result["routing"]["team"] == "PLATFORM"
    assert result["routing"]["routingMode"] == "AUTOMATIC"
    assert result["status"] == "ROUTED"

    with SessionLocal() as session:
        assert session.scalar(select(func.count()).select_from(TicketRecord)) == 1
        assert session.scalar(select(func.count()).select_from(TicketAnalysisRecord)) == 1
        assert session.scalar(select(func.count()).select_from(RoutingDecisionRecord)) == 1

    fetched = client.get(f"/api/v1/tickets/{result['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == result
    listing = client.get("/api/v1/tickets")
    assert listing.status_code == 200
    assert listing.json()[0]["title"] == "All customer vehicles offline"


def test_angry_trivial_ticket_does_not_inflate_severity(client: TestClient) -> None:
    result = create(
        client,
        "THIS FUCKING PASSWORD RESET DOESN'T WORK",
        "I am furious. Reset my password now.",
    )
    assert result["analysis"]["sentiment"]["value"] == "VERY_NEGATIVE"
    assert result["analysis"]["technicalComplexity"]["value"] == 0.12
    assert result["routing"]["supportTier"] == "L1"


def test_security_ticket_bypasses_support_tiers(client: TestClient) -> None:
    result = create(
        client,
        "Possible unauthorized access",
        "Several users report sessions from unknown IP addresses and account changes.",
    )
    assert result["analysis"]["securityRisk"]["value"] == 0.94
    assert result["routing"]["supportTier"] == "ENGINEERING"
    assert result["routing"]["team"] == "SECURITY"


def test_validation_and_missing_ticket(client: TestClient) -> None:
    invalid = client.post(
        "/api/v1/tickets",
        json={"title": "x", "description": "no", "customerName": "", "source": "EMAIL"},
    )
    assert invalid.status_code == 422
    assert client.get("/api/v1/tickets/not-found").status_code == 404


def test_health_checks_database_and_provider(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "provider": "mock"}
    assert response.headers["x-request-id"]

