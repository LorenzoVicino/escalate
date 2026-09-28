from typing import Any

import structlog

from escalate.config import Settings
from escalate.integrations.hubspot.client import HubSpotClient
from escalate.integrations.hubspot.enrichment import (
    TicketContext,
    build_context_digest,
    fetch_ticket_context,
)
from escalate.integrations.hubspot.mapper import HubSpotTicketMapper
from escalate.integrations.hubspot.schemas import HubSpotSyncResult, HubSpotTicket
from escalate.tickets.schemas import TicketContextUpdate, TicketMessageCreate
from escalate.tickets.service import TicketService

logger = structlog.get_logger()


class HubSpotSyncService:
    def __init__(
        self,
        client: HubSpotClient,
        mapper: HubSpotTicketMapper,
        tickets: TicketService,
        page_size: int,
        pipeline_id: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._client = client
        self._mapper = mapper
        self._tickets = tickets
        self._page_size = page_size
        self._pipeline_id = pipeline_id
        self._settings = settings or Settings()
        self._owners: dict[str, dict[str, Any]] | None = None

    async def _owner_directory(self) -> dict[str, dict[str, Any]]:
        """Owners are resolved from one cached listing: HubSpot's per-id endpoint
        404s for deactivated users, who still own plenty of tickets."""
        if self._owners is None:
            active = await self._client.list_owners()
            archived = await self._client.list_owners(archived=True)
            self._owners = {str(owner["id"]): owner for owner in [*active, *archived]}
        return self._owners

    async def sync(self, *, after: str | None, max_pages: int) -> HubSpotSyncResult:
        imported = 0
        skipped = 0
        pages = 0
        cursor = after

        while pages < max_pages:
            page = await self._client.list_tickets(
                properties=self._mapper.requested_properties,
                limit=self._page_size,
                after=cursor,
                pipeline_id=self._pipeline_id,
            )
            pages += 1
            for external_ticket in page.results:
                data = self._mapper.to_ticket_create(external_ticket)
                # Skip known tickets before spending any HubSpot or model work on them.
                if data.external_id is not None and self._tickets.exists_external(
                    data.source.value, data.external_id
                ):
                    skipped += 1
                    continue

                context = await self._fetch_context(external_ticket)
                data = data.model_copy(
                    update={
                        "analysis_context": build_context_digest(
                            context,
                            max_messages=self._settings.analysis_context_max_messages,
                            max_chars_per_message=(
                                self._settings.analysis_context_max_chars_per_message
                            ),
                            max_chars=self._settings.analysis_context_max_chars,
                        )
                    }
                )
                result, created = await self._tickets.create_if_missing(data)
                imported += int(created)
                skipped += int(not created)
                if created and context is not None:
                    self._persist_context(result.id, context)
            cursor = page.next_cursor
            if cursor is None:
                break

        logger.info(
            "hubspot_sync_completed",
            imported=imported,
            skipped=skipped,
            pages=pages,
            next_cursor=cursor,
        )
        return HubSpotSyncResult(
            imported=imported,
            skipped=skipped,
            pages=pages,
            next_cursor=cursor,
        )

    async def _fetch_context(self, external_ticket: HubSpotTicket) -> TicketContext | None:
        owner_id = self._mapper.owner_id(external_ticket)
        try:
            owner = (await self._owner_directory()).get(owner_id) if owner_id else None
            return await fetch_ticket_context(
                self._client, external_ticket.id, owner_id, owner
            )
        except Exception:
            logger.warning(
                "hubspot_ticket_enrichment_failed",
                external_id=external_ticket.id,
                exc_info=True,
            )
            return None

    def _persist_context(self, ticket_id: str, context: TicketContext) -> None:
        self._tickets.set_context(
            ticket_id,
            TicketContextUpdate(
                owner_id=context.owner_id,
                owner_name=context.owner_name,
                owner_email=context.owner_email,
                contact_email=context.contact_email,
                messages=[
                    TicketMessageCreate(
                        external_id=message.external_id,
                        channel=message.channel,
                        direction=message.direction,
                        author=message.author,
                        subject=message.subject,
                        body=message.body,
                        occurred_at=message.occurred_at,
                    )
                    for message in context.messages
                ],
            ),
        )
