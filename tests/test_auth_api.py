from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from docbrain.db.base import Base, import_all_models
from docbrain.identity.models import UserModel
from docbrain.main import create_app


def test_register_endpoint_creates_user_and_owner_membership() -> None:
    client = _client()

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "sergio@example.com",
            "password": "correct horse battery staple",
            "organization_name": "Acme",
            "display_name": "Sergio",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "owner"


def test_register_endpoint_rejects_duplicate_email() -> None:
    client = _client()
    payload = {
        "email": "sergio@example.com",
        "password": "correct horse battery staple",
        "organization_name": "Acme",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_register_endpoint_persists_normalized_email() -> None:
    session_factory = _session_factory()
    client = _client(session_factory)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Sergio@Example.com",
            "password": "correct horse battery staple",
            "organization_name": "Acme",
        },
    )

    assert response.status_code == 201
    with session_factory() as session:
        assert session.scalar(select(UserModel.email)) == "sergio@example.com"


def _client(
    session_factory: sessionmaker[Session] | None = None,
) -> TestClient:
    app = create_app()
    app.state.session_factory = session_factory or _session_factory()
    return TestClient(app)


def _session_factory() -> sessionmaker[Session]:
    import_all_models()
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
