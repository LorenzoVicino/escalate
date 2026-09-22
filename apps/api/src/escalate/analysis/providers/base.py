from typing import Protocol

from escalate.analysis.models import TicketAnalysis, TicketAnalysisInput


class DecisionModel(Protocol):
    async def analyze(self, ticket: TicketAnalysisInput) -> TicketAnalysis: ...

