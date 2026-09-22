import asyncio
from time import perf_counter
from typing import Any

from escalate.analysis.models import (
    Category,
    ChoiceSignal,
    NumericSignal,
    Sentiment,
    TicketAnalysis,
    TicketAnalysisInput,
)
from escalate.analysis.prompts import laya_questions
from escalate.tickets.domain import Team


class LayaDecisionModel:
    """Adapter that contains every dependency on Laya's response shape."""

    def __init__(self) -> None:
        try:
            from laya import Router
        except ImportError as exc:
            raise RuntimeError(
                "AI_PROVIDER=laya requires installation with `pip install '.[laya]'`"
            ) from exc
        self._router = Router(preload=True)

    async def analyze(self, ticket: TicketAnalysisInput) -> TicketAnalysis:
        state = {
            "subject": ticket.title,
            "body": ticket.description,
            "customer": ticket.customer_name,
        }
        started = perf_counter()
        raw = await asyncio.to_thread(self._router.predict, state, laya_questions())
        elapsed_ms = round((perf_counter() - started) * 1000)
        return self._parse(raw, elapsed_ms)

    @classmethod
    def _parse(cls, raw: dict[str, Any], elapsed_ms: int) -> TicketAnalysis:
        answers = raw["answers"]
        routing = raw.get("routing", {})
        return TicketAnalysis(
            category=cls._choice(answers["category"], Category),
            sentiment=cls._choice(answers["sentiment"], Sentiment),
            urgency=cls._score(answers["urgency"], 2),
            customer_impact=cls._score(answers["customer_impact"], 3),
            technical_complexity=cls._score(answers["technical_complexity"], 3),
            requires_developer=cls._noul(answers["requires_developer"]),
            security_risk=cls._noul(answers["security_risk"]),
            suggested_team=cls._choice(answers["suggested_team"], Team),
            provider="laya",
            model=str(routing.get("repo", routing.get("model", "laya-router"))),
            processing_time_ms=elapsed_ms,
        )

    @staticmethod
    def _choice(answer: dict[str, Any], enum_type: Any) -> ChoiceSignal[Any]:
        return ChoiceSignal(
            value=enum_type(str(answer["choice"]).upper()),
            confidence=float(answer["confidence"]),
        )

    @staticmethod
    def _score(answer: dict[str, Any], maximum: int) -> NumericSignal:
        return NumericSignal(
            value=max(0.0, min(1.0, float(answer["score"]) / maximum)),
            confidence=float(answer["confidence"]),
        )

    @staticmethod
    def _noul(answer: dict[str, Any]) -> NumericSignal:
        probability = float(answer["noul"])
        return NumericSignal(
            value=probability,
            confidence=float(answer.get("confidence", max(probability, 1 - probability))),
        )
