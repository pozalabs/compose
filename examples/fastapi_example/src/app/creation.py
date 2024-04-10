from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic

import compose
from src.dependency import ApplicationContainer, wirer
from src.logging import logger  # noqa: F401
from src.user.entrypoint.router import router as user_router

from . import exceptions

http_basic = HTTPBasic()
http_basic_auth = compose.fastapi.HTTPBasicAuth(
    username="admin",
    password="admin",
    security=http_basic,
).authenticator()


def create_app() -> FastAPI:
    _app = FastAPI()
    inject_dependencies(_app)
    add_middlewares(_app)
    add_exception_handlers(_app)
    add_routers(_app)

    _app.get("/health-check", include_in_schema=False)(compose.fastapi.health_check)

    @_app.get("/auth/basic", dependencies=[Depends(http_basic_auth)], include_in_schema=False)
    def basic_auth():
        return {"message": "Authenticated"}

    return _app


def inject_dependencies(_app: FastAPI) -> None:
    container = ApplicationContainer.wired(wirer=wirer)

    _app.container = container


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
