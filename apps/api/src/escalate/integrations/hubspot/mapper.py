from escalate.config import Settings
from escalate.integrations.hubspot.schemas import HubSpotTicket
from escalate.tickets.domain import TicketSource
from escalate.tickets.schemas import TicketCreate


class HubSpotTicketMapper:
    def __init__(self, settings: Settings) -> None:
        self._title = settings.hubspot_title_property
        self._description = settings.hubspot_description_property
        self._customer = settings.hubspot_customer_name_property

    @property
    def requested_properties(self) -> list[str]:
        return [
            property_name
            for property_name in (self._title, self._description, self._customer)
            if property_name
        ]

    def to_ticket_create(self, ticket: HubSpotTicket) -> TicketCreate:
        properties = ticket.properties
        return TicketCreate(
            external_id=ticket.id,
            title=properties.get(self._title) or f"HubSpot ticket {ticket.id}",
            description=(
                properties.get(self._description)
                or "No description was provided in the HubSpot ticket."
            ),
            customer_name=(
                properties.get(self._customer) if self._customer else None
            )
            or "HubSpot customer",
            source=TicketSource.HUBSPOT,
        )
