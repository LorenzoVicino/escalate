from escalate.analysis.models import TicketAnalysis, TicketAnalysisInput
from escalate.analysis.providers.base import DecisionModel


class AnalysisService:
    def __init__(self, provider: DecisionModel) -> None:
        self._provider = provider

    async def analyze(self, ticket: TicketAnalysisInput) -> TicketAnalysis:
        return await self._provider.analyze(ticket)

