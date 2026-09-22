from typing import Any


def laya_questions() -> dict[str, dict[str, Any]]:
    return {
        "category": {
            "type": "choice",
            "instructions": "Classify the primary support ticket category.",
            "criteria": {value: value.replace("_", " ").lower() for value in [
                "ACCOUNT", "CONFIGURATION", "HOW_TO", "BUG", "INTEGRATION",
                "PRODUCTION_INCIDENT", "PERFORMANCE", "SECURITY", "DATA_ISSUE",
                "BILLING", "FEATURE_REQUEST", "OTHER",
            ]},
        },
        "sentiment": {
            "type": "choice",
            "instructions": "Classify user sentiment independently of technical severity.",
            "criteria": {value: value.replace("_", " ").lower() for value in [
                "POSITIVE", "NEUTRAL", "NEGATIVE", "VERY_NEGATIVE",
            ]},
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is the issue?",
            "criteria": ["not urgent", "soon", "critical"],
        },
        "customer_impact": {
            "type": "score",
            "instructions": "How broad is customer impact?",
            "criteria": [
                "negligible",
                "one user",
                "part of organization",
                "organization-wide",
            ],
        },
        "technical_complexity": {
            "type": "score",
            "instructions": "How technically complex is resolution?",
            "criteria": [
                "basic support",
                "technical support",
                "specialist investigation",
                "engineering",
            ],
        },
        "requires_developer": {
            "type": "noul",
            "instructions": "Is developer intervention likely required?",
        },
        "security_risk": {
            "type": "noul",
            "instructions": "Does this ticket indicate a security risk?",
        },
        "suggested_team": {
            "type": "choice",
            "instructions": "Which technical team best matches the issue?",
            "criteria": {
                value: value.lower()
                for value in [
                    "SUPPORT",
                    "BACKEND",
                    "FRONTEND",
                    "DEVOPS",
                    "DATABASE",
                    "SECURITY",
                    "MOBILE",
                    "PLATFORM",
                    "UNKNOWN",
                ]
            },
        },
    }
