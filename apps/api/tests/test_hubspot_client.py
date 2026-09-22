import httpx
import pytest

from escalate.integrations.hubspot.client import HubSpotApiError, HubSpotClient


@pytest.mark.anyio
async def test_client_requests_configured_properties_and_cursor() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer private-token"
        assert request.url.params["properties"] == "subject,content,company_name"
        assert request.url.params["after"] == "cursor-1"
        assert request.url.params["limit"] == "100"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": "123",
                        "properties": {"subject": "API unavailable"},
                        "createdAt": "2026-09-22T08:00:00Z",
                        "updatedAt": "2026-09-22T08:01:00Z",
                        "archived": False,
                    }
                ],
                "paging": {"next": {"after": "cursor-2"}},
            },
        )

    http_client = httpx.AsyncClient(
        base_url="https://api.hubapi.com",
        transport=httpx.MockTransport(handler),
    )
    client = HubSpotClient(
        "private-token",
        base_url="https://api.hubapi.com",
        tickets_path="/crm/v3/objects/tickets",
        timeout_seconds=10,
        client=http_client,
    )
    page = await client.list_tickets(
        properties=["subject", "content", "company_name"],
        limit=100,
        after="cursor-1",
    )
    await http_client.aclose()

    assert page.results[0].id == "123"
    assert page.next_cursor == "cursor-2"


@pytest.mark.anyio
async def test_client_does_not_expose_token_in_api_errors() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            headers={"x-hubspot-correlation-id": "corr-123"},
            request=request,
        )

    http_client = httpx.AsyncClient(
        base_url="https://api.hubapi.com",
        transport=httpx.MockTransport(handler),
    )
    client = HubSpotClient(
        "super-secret-token",
        base_url="https://api.hubapi.com",
        tickets_path="/crm/v3/objects/tickets",
        timeout_seconds=10,
        client=http_client,
    )
    with pytest.raises(HubSpotApiError) as error:
        await client.list_tickets(properties=["subject"], limit=100)
    await http_client.aclose()

    assert "corr-123" in str(error.value)
    assert "super-secret-token" not in str(error.value)

