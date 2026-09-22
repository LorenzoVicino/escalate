from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from escalate.analysis.providers.base import DecisionModel
from escalate.analysis.providers.laya import LayaDecisionModel
from escalate.analysis.providers.mock import MockDecisionModel
from escalate.common.logging import RequestContextMiddleware, configure_logging
from escalate.config import Settings, get_settings
from escalate.db.session import engine
from escalate.tickets.router import router as tickets_router


def build_provider(name: str) -> DecisionModel:
    if name == "mock":
        return MockDecisionModel()
    if name == "laya":
        return LayaDecisionModel()
    raise ValueError(f"Unsupported AI_PROVIDER: {name}")


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = app_settings
        app.state.decision_model = build_provider(app_settings.ai_provider)
        yield

    configure_logging()
    app = FastAPI(
        title=app_settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        description="Probabilistic ticket analysis wrapped in deterministic routing rules.",
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(tickets_router)

    @app.get("/health", tags=["operations"])
    def health() -> dict[str, str]:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "provider": app_settings.ai_provider}

    return app


app = create_app()

