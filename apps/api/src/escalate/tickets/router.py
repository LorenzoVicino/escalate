from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from escalate.analysis.providers.base import DecisionModel
from escalate.analysis.service import AnalysisService
from escalate.config import Settings
from escalate.db.session import get_db
from escalate.routing.engine import RoutingDecisionEngine
from escalate.routing.rules import RoutingThresholds
from escalate.tickets.repository import TicketRepository
from escalate.tickets.schemas import TicketCreate, TicketResult, TicketSummary
from escalate.tickets.service import TicketNotFoundError, TicketService

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])


def get_ticket_service(
    request: Request, session: Annotated[Session, Depends(get_db)]
) -> TicketService:
    provider: DecisionModel = request.app.state.decision_model
    settings: Settings = request.app.state.settings
    return TicketService(
        TicketRepository(session),
        AnalysisService(provider),
        RoutingDecisionEngine(RoutingThresholds.from_settings(settings)),
    )


@router.post("", response_model=TicketResult, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: TicketCreate, service: Annotated[TicketService, Depends(get_ticket_service)]
) -> TicketResult:
    return await service.create(data)


@router.get("", response_model=list[TicketSummary])
def list_tickets(
    service: Annotated[TicketService, Depends(get_ticket_service)],
) -> list[TicketSummary]:
    return service.list()


@router.get("/{ticket_id}", response_model=TicketResult)
def get_ticket(
    ticket_id: str, service: Annotated[TicketService, Depends(get_ticket_service)]
) -> TicketResult:
    try:
        return service.get(ticket_id)
    except TicketNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Ticket not found") from exc

