"""Pytest configuration and shared test fixtures."""

from collections.abc import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture bound to the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Direct database session fixture with cleanup."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
