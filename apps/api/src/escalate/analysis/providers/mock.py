from time import perf_counter

from escalate.analysis.models import (
    Category,
    ChoiceSignal,
    NumericSignal,
    Sentiment,
    TicketAnalysis,
    TicketAnalysisInput,
)
from escalate.tickets.domain import Team


class MockDecisionModel:
    """Deterministic keyword model for local development and ordinary tests."""

    async def analyze(self, ticket: TicketAnalysisInput) -> TicketAnalysis:
        started = perf_counter()
        text = f"{ticket.title} {ticket.description}".lower()

        category, team, complexity, developer = self._technical_signals(text)
        urgency, impact = self._severity_signals(text)
        security = 0.94 if self._contains(text, "unauthorized", "unknown ip", "breach") else 0.05
        if security >= 0.8:
            category, team, developer, urgency, impact = (
                Category.SECURITY,
                Team.SECURITY,
                0.91,
                max(urgency, 0.88),
                max(impact, 0.72),
            )

        sentiment = Sentiment.NEUTRAL
        if self._contains(text, "fucking", "furious", "unacceptable"):
            sentiment = Sentiment.VERY_NEGATIVE
        elif self._contains(text, "angry", "frustrated", "doesn't work", "not working"):
            sentiment = Sentiment.NEGATIVE

        return TicketAnalysis(
            category=ChoiceSignal(value=category, confidence=0.93),
            sentiment=ChoiceSignal(value=sentiment, confidence=0.91),
            urgency=NumericSignal(value=urgency, confidence=0.92),
            customer_impact=NumericSignal(value=impact, confidence=0.92),
            technical_complexity=NumericSignal(value=complexity, confidence=0.90),
            requires_developer=NumericSignal(value=developer, confidence=0.91),
            security_risk=NumericSignal(value=security, confidence=0.96),
            suggested_team=ChoiceSignal(value=team, confidence=0.90),
            provider="mock",
            model="deterministic-demo-v1",
            processing_time_ms=max(1, round((perf_counter() - started) * 1000)),
        )

    @staticmethod
    def _contains(text: str, *needles: str) -> bool:
        return any(needle in text for needle in needles)

    def _technical_signals(self, text: str) -> tuple[Category, Team, float, float]:
        if self._contains(text, "password", "reset", "login"):
            return Category.ACCOUNT, Team.SUPPORT, 0.12, 0.05
        if self._contains(text, "401", "api", "integration", "credential"):
            return Category.INTEGRATION, Team.SUPPORT, 0.48, 0.28
        if self._contains(text, "duplicate", "data inconsistency", "transactions"):
            return Category.DATA_ISSUE, Team.DATABASE, 0.78, 0.84
        if self._contains(text, "dashboard", "not updating", "stopped updating"):
            return Category.BUG, Team.BACKEND, 0.74, 0.69
        if self._contains(text, "offline", "outage", "production"):
            return Category.PRODUCTION_INCIDENT, Team.PLATFORM, 0.86, 0.91
        if self._contains(text, "slow", "latency", "performance"):
            return Category.PERFORMANCE, Team.BACKEND, 0.72, 0.75
        return Category.OTHER, Team.SUPPORT, 0.22, 0.12

    def _severity_signals(self, text: str) -> tuple[float, float]:
        if self._contains(text, "all 250", "all customer", "fleet", "system-wide", "outage"):
            return 0.96, 0.98
        if self._contains(text, "transactions", "duplicated", "production"):
            return 0.89, 0.91
        if self._contains(text, "several users", "organization"):
            return 0.77, 0.72
        return 0.28, 0.24
