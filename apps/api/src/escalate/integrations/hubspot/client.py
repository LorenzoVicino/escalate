from collections.abc import Sequence
from typing import Any

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
        pipeline_id: str | None = None,
    ) -> HubSpotTicketPage:
        if pipeline_id is not None:
            return await self._search_tickets(
                properties=properties,
                limit=limit,
                after=after,
                pipeline_id=pipeline_id,
            )
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

    async def _search_tickets(
        self,
        *,
        properties: Sequence[str],
        limit: int,
        after: str | None,
        pipeline_id: str,
    ) -> HubSpotTicketPage:
        body: dict[str, object] = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "hs_pipeline",
                            "operator": "EQ",
                            "value": pipeline_id,
                        }
                    ]
                }
            ],
            # Without an explicit sort HubSpot returns the OLDEST tickets first, which
            # in a large pipeline means a triage queue full of years-old tickets.
            "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
            "properties": list(dict.fromkeys(properties)),
            "limit": limit,
        }
        if after is not None:
            body["after"] = after
        try:
            response = await self._client.post(
                f"{self._tickets_path}/search",
                json=body,
                headers=self._headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            request_id = exc.response.headers.get("x-hubspot-correlation-id", "unknown")
            raise HubSpotApiError(
                f"HubSpot tickets search failed with status "
                f"{exc.response.status_code}; correlation_id={request_id}"
            ) from exc
        except httpx.HTTPError as exc:
            raise HubSpotApiError("HubSpot tickets search failed") from exc
        return HubSpotTicketPage.model_validate(response.json())

    async def list_owners(
        self, *, limit: int = 100, archived: bool = False
    ) -> list[dict[str, Any]]:
        owners: list[dict[str, Any]] = []
        after: str | None = None
        while True:
            params: dict[str, str | int] = {"limit": limit}
            if archived:
                params["archived"] = "true"
            if after is not None:
                params["after"] = after
            try:
                response = await self._client.get(
                    "/crm/v3/owners", params=params, headers=self._headers
                )
                response.raise_for_status()
            except httpx.HTTPError:
                return owners
            payload = response.json()
            owners.extend(payload.get("results", []))
            after = (payload.get("paging") or {}).get("next", {}).get("after")
            if after is None:
                return owners

    async def get_owner(self, owner_id: str) -> dict[str, Any] | None:
        try:
            response = await self._client.get(
                f"/crm/v3/owners/{owner_id}", headers=self._headers
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
        except httpx.HTTPError:
            return None
        payload: dict[str, Any] = response.json()
        return payload

    async def get_associations(
        self, object_type: str, object_id: str, to_object_type: str
    ) -> list[str]:
        try:
            response = await self._client.get(
                f"/crm/v4/objects/{object_type}/{object_id}/associations/{to_object_type}",
                headers=self._headers,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        return [str(result["toObjectId"]) for result in response.json().get("results", [])]

    async def batch_read(
        self, object_type: str, ids: Sequence[str], properties: Sequence[str]
    ) -> list[dict[str, Any]]:
        if not ids:
            return []
        try:
            response = await self._client.post(
                f"/crm/v3/objects/{object_type}/batch/read",
                json={
                    "inputs": [{"id": object_id} for object_id in ids],
                    "properties": list(properties),
                },
                headers=self._headers,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        results: list[dict[str, Any]] = response.json().get("results", [])
        return results

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()
