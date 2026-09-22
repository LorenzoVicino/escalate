from escalate.analysis.providers.laya import LayaDecisionModel


def test_laya_response_parsing_is_confined_to_adapter() -> None:
    raw = {
        "answers": {
            "category": {"choice": "bug", "confidence": 0.88},
            "sentiment": {"choice": "negative", "confidence": 0.81},
            "urgency": {"score": 1.8, "confidence": 0.84},
            "customer_impact": {"score": 2.7, "confidence": 0.89},
            "technical_complexity": {"score": 2.1, "confidence": 0.78},
            "requires_developer": {"noul": 0.82},
            "security_risk": {"noul": 0.12},
            "suggested_team": {"choice": "backend", "confidence": 0.8},
        },
        "routing": {"repo": "convaiinnovations/laya"},
    }
    parsed = LayaDecisionModel._parse(raw, 42)
    assert parsed.category.value.value == "BUG"
    assert parsed.urgency.value == 0.9
    assert parsed.customer_impact.value == 0.9
    assert parsed.requires_developer.value == 0.82
    assert parsed.model == "convaiinnovations/laya"
    assert parsed.processing_time_ms == 42

