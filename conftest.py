"""Shared pytest fixtures.

Lives at the repo root (rather than under tests/) so pytest adds this
directory to sys.path when it loads it, letting `import main` succeed
whether the suite is invoked as `pytest` or `python -m pytest`.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


@pytest.fixture(name="session")
def session_fixture():
    """A fresh, isolated in-memory database for a single test.

    Never touches the real cv.db: each test gets its own engine and
    schema, torn down when the test ends.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """A TestClient wired to the app with the DB session dependency
    overridden to use the isolated `session` fixture instead of the
    real cv.db.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    # Not used as a context manager on purpose: entering it would run
    # the app's startup event, which creates tables against the real
    # cv.db engine defined in main.py.
    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
