import asyncio

import structlog

from escalate.analysis.providers.base import DecisionModel
from escalate.analysis.service import AnalysisService
from escalate.config import Settings
from escalate.db.session import SessionLocal
from escalate.integrations.hubspot.client import HubSpotClient
from escalate.integrations.hubspot.mapper import HubSpotTicketMapper
from escalate.integrations.hubspot.service import HubSpotSyncService
from escalate.routing.engine import RoutingDecisionEngine
from escalate.routing.rules import RoutingThresholds
from escalate.tickets.repository import TicketRepository
from escalate.tickets.service import TicketService

logger = structlog.get_logger()


async def poll_hubspot_forever(
    client: HubSpotClient,
    provider: DecisionModel,
    settings: Settings,
) -> None:
    """Repeatedly syncs the configured pipeline; runs once immediately, then every interval."""
    while True:
        started = asyncio.get_running_loop().time()
        try:
            with SessionLocal() as session:
                service = HubSpotSyncService(
                    client=client,
                    mapper=HubSpotTicketMapper(settings),
                    tickets=TicketService(
                        TicketRepository(session),
                        AnalysisService(provider),
                        RoutingDecisionEngine(RoutingThresholds.from_settings(settings)),
                    ),
                    page_size=settings.hubspot_sync_page_size,
                    pipeline_id=settings.hubspot_pipeline_id,
                    settings=settings,
                )
                result = await service.sync(after=None, max_pages=settings.hubspot_poll_max_pages)
                logger.info(
                    "hubspot_poll_completed",
                    imported=result.imported,
                    skipped=result.skipped,
                    pages=result.pages,
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("hubspot_poll_failed", exc_info=True)

        # Laya inference can outrun the interval; subtract elapsed so cycles never stack.
        elapsed = asyncio.get_running_loop().time() - started
        await asyncio.sleep(max(0.0, settings.hubspot_poll_interval_seconds - elapsed))
