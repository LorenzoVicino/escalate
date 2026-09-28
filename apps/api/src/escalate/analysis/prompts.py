from typing import Any


def laya_questions() -> dict[str, dict[str, Any]]:
    return {
        "category": {
            "type": "choice",
            "instructions": "Classify the primary support ticket category.",
            "criteria": {
                "DEVICE_CONNECTIVITY": (
                    "telematic device (centralina/periferica) not communicating, "
                    "offline, or not transmitting data"
                ),
                "PROVISIONING": (
                    "device preparation, installation, collaudo, or contract activation"
                ),
                "ACCOUNT_CONTRACT": (
                    "customer account, contract, tenant, or option/privilege access"
                ),
                "CONFIGURATION": "configuration",
                "HOW_TO": "how to",
                "BUG": "bug",
                "INTEGRATION": "cross-system integration (HubSpot, TeamSystem, GTSAT, Middleware)",
                "PRODUCTION_INCIDENT": "production incident",
                "PERFORMANCE": "performance",
                "SECURITY": "security",
                "DATA_QUALITY": (
                    "incorrect or inconsistent telemetry/report data "
                    "(GPS, AVL, fuel consumption, routes)"
                ),
                "BILLING": "billing",
                "FEATURE_REQUEST": "feature request",
                "OTHER": "other",
            },
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
                "SUPPORT": "support",
                "BACKEND": "backend",
                "FRONTEND": "frontend",
                "DEVOPS": "devops",
                "DATABASE": "database",
                "SECURITY": "security",
                "MOBILE": "mobile",
                "PLATFORM": "platform",
                "MIDDLEWARE": "middleware (cross-system identity, orders, catalog orchestration)",
                "GTSAT": "GTSAT (telematic device catalog, provisioning, and webservice)",
                "INGESTION": "telemetry ingestion (GPS/AVL data pipeline)",
                "UNKNOWN": "unknown",
            },
        },
    }
