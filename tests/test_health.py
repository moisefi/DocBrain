from fastapi.testclient import TestClient

from docbrain.main import create_app


def test_live_healthcheck_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_healthcheck_returns_application_check() -> None:
    client = TestClient(create_app())

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "environment": "local",
        "checks": {"application": "ok"},
    }

