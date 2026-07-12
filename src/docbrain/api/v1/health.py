from typing import TypedDict

from fastapi import APIRouter, Request

from docbrain.core.config import Settings

router = APIRouter()


class LiveResponse(TypedDict):
    status: str


class ReadyResponse(TypedDict):
    status: str
    environment: str
    checks: dict[str, str]


@router.get("/health/live")
def live() -> LiveResponse:
    return {"status": "ok"}


@router.get("/health/ready")
def ready(request: Request) -> ReadyResponse:
    settings = _get_settings(request)
    return {
        "status": "ok",
        "environment": settings.environment,
        "checks": {"application": "ok"},
    }


def _get_settings(request: Request) -> Settings:
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        raise RuntimeError("Application settings are not configured")
    return settings

