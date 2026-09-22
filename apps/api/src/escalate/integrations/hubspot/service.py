import structlog

from escalate.integrations.hubspot.client import HubSpotClient
from escalate.integrations.hubspot.mapper import HubSpotTicketMapper
from escalate.integrations.hubspot.schemas import HubSpotSyncResult
from escalate.tickets.service import TicketService

logger = structlog.get_logger()


class HubSpotSyncService:
    def __init__(
        self,
        client: HubSpotClient,
        mapper: HubSpotTicketMapper,
        tickets: TicketService,
        page_size: int,
    ) -> None:
        self._client = client
        self._mapper = mapper
        self._tickets = tickets
        self._page_size = page_size

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
            )
            pages += 1
            for external_ticket in page.results:
                _, created = await self._tickets.create_if_missing(
                    self._mapper.to_ticket_create(external_ticket)
                )
                imported += int(created)
                skipped += int(not created)
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
