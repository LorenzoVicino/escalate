from enum import StrEnum


class TicketSource(StrEnum):
    WEB = "WEB"
    EMAIL = "EMAIL"
    API = "API"
    JIRA = "JIRA"
    GITHUB = "GITHUB"
    SLACK = "SLACK"
    OTHER = "OTHER"


class TicketStatus(StrEnum):
    OPEN = "OPEN"
    ROUTED = "ROUTED"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"
    MANUAL_TRIAGE = "MANUAL_TRIAGE"
    RESOLVED = "RESOLVED"


class SupportTier(StrEnum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    ENGINEERING = "ENGINEERING"


class Team(StrEnum):
    SUPPORT = "SUPPORT"
    BACKEND = "BACKEND"
    FRONTEND = "FRONTEND"
    DEVOPS = "DEVOPS"
    DATABASE = "DATABASE"
    SECURITY = "SECURITY"
    MOBILE = "MOBILE"
    PLATFORM = "PLATFORM"
    UNKNOWN = "UNKNOWN"

