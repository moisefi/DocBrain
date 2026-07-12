from fastapi import FastAPI

from docbrain.api.router import api_router
from docbrain.core.config import Settings, get_settings
from docbrain.db.session import create_database_engine, create_session_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        docs_url="/docs" if resolved_settings.enable_docs else None,
        redoc_url="/redoc" if resolved_settings.enable_docs else None,
        openapi_url="/openapi.json" if resolved_settings.enable_docs else None,
    )
    app.state.settings = resolved_settings
    app.state.engine = create_database_engine(resolved_settings)
    app.state.session_factory = create_session_factory(app.state.engine)
    app.include_router(api_router)
    return app


app = create_app()
