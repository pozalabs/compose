from dishka.integrations.fastapi import setup_dishka
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import compose
from src import constants
from src.dependency import create_container
from src.logging import logger  # noqa: F401
from src.user.entrypoint.router import router as user_router

from . import exceptions

http_basic = compose.fastapi.HTTPBasic.static(username="admin", password="admin")


def create_app() -> FastAPI:
    _app = FastAPI(
        openapi_tags=compose.fastapi.openapi_tags(constants.OpenApiTag),
    )
    inject_dependencies(_app)
    add_middlewares(_app)
    add_exception_handlers(_app)
    add_routers(_app)

    _app.get("/health-check", include_in_schema=False)(compose.fastapi.health_check)

    @_app.get("/auth/basic", dependencies=[Depends(http_basic)], include_in_schema=False)
    def basic_auth():
        return {"message": "Authenticated"}

    return _app


def inject_dependencies(_app: FastAPI) -> None:
    container = create_container()
    setup_dishka(container, _app)


def add_middlewares(_app: FastAPI) -> None:
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )


def add_exception_handlers(_app: FastAPI) -> None:
    for info in exceptions.EXCEPTION_HANDLER_INFOS:
        _app.add_exception_handler(
            exc_class_or_status_code=info.exc_class_or_status_code,
            handler=info.handler,
        )


def add_routers(_app: FastAPI) -> None:
    _app.include_router(user_router)
