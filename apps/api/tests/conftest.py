import os
from collections.abc import Generator

os.environ["DATABASE_URL"] = "sqlite:///./test_escalate.db"
os.environ["AI_PROVIDER"] = "mock"

import pytest
from fastapi.testclient import TestClient

from escalate.db.base import Base
from escalate.db.session import engine
from escalate.main import app


@pytest.fixture(autouse=True)
def clean_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client

