from collections.abc import Sequence

import httpx

from escalate.integrations.hubspot.schemas import HubSpotTicketPage


class HubSpotApiError(RuntimeError):
    pass


class HubSpotClient:
    def __init__(
        self,
        access_token: str,
        *,
        base_url: str,
        tickets_path: str,
        timeout_seconds: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._tickets_path = tickets_path
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout_seconds,
        )

    async def list_tickets(
        self,
        *,
        properties: Sequence[str],
        limit: int,
        after: str | None = None,
    ) -> HubSpotTicketPage:
        params: dict[str, str | int] = {
            "limit": limit,
            "properties": ",".join(dict.fromkeys(properties)),
            "archived": "false",
        }
        if after is not None:
            params["after"] = after
        try:
            response = await self._client.get(
                self._tickets_path,
                params=params,
                headers=self._headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            request_id = exc.response.headers.get("x-hubspot-correlation-id", "unknown")
            raise HubSpotApiError(
                f"HubSpot tickets request failed with status "
                f"{exc.response.status_code}; correlation_id={request_id}"
            ) from exc
        except httpx.HTTPError as exc:
            raise HubSpotApiError("HubSpot tickets request failed") from exc
        return HubSpotTicketPage.model_validate(response.json())

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()
