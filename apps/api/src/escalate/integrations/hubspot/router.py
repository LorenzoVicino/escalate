from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from escalate.config import Settings
from escalate.integrations.hubspot.client import HubSpotApiError, HubSpotClient
from escalate.integrations.hubspot.mapper import HubSpotTicketMapper
from escalate.integrations.hubspot.schemas import HubSpotOwner, HubSpotSyncResult
from escalate.integrations.hubspot.service import HubSpotSyncService
from escalate.tickets.router import get_ticket_service
from escalate.tickets.service import TicketService

router = APIRouter(prefix="/api/v1/integrations/hubspot", tags=["integrations"])


def get_hubspot_sync_service(
    request: Request,
    tickets: Annotated[TicketService, Depends(get_ticket_service)],
) -> HubSpotSyncService:
    client: HubSpotClient | None = request.app.state.hubspot_client
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="HubSpot is not configured; set HUBSPOT_ACCESS_TOKEN",
        )
    settings: Settings = request.app.state.settings
    return HubSpotSyncService(
        client=client,
        mapper=HubSpotTicketMapper(settings),
        tickets=tickets,
        page_size=settings.hubspot_sync_page_size,
        pipeline_id=settings.hubspot_pipeline_id,
        settings=settings,
    )


def get_hubspot_client(request: Request) -> HubSpotClient:
    client: HubSpotClient | None = request.app.state.hubspot_client
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="HubSpot is not configured; set HUBSPOT_ACCESS_TOKEN",
        )
    return client


@router.get("/owners", response_model=list[HubSpotOwner])
async def list_hubspot_owners(
    client: Annotated[HubSpotClient, Depends(get_hubspot_client)],
) -> list[HubSpotOwner]:
    return [HubSpotOwner.model_validate(owner) for owner in await client.list_owners()]


@router.post("/sync", response_model=HubSpotSyncResult)
async def sync_hubspot_tickets(
    service: Annotated[HubSpotSyncService, Depends(get_hubspot_sync_service)],
    after: Annotated[str | None, Query()] = None,
    max_pages: Annotated[int, Query(ge=1, le=100)] = 10,
) -> HubSpotSyncResult:
    try:
        return await service.sync(after=after, max_pages=max_pages)
    except HubSpotApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

