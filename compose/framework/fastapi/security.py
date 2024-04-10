import http
import secrets
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials


class HTTPBasicAuth:
    def __init__(self, username: str, password: str, security: HTTPBasic):
        self.username = username
        self.password = password
        self.security = security

    def authenticator(self) -> Callable[[HTTPBasicCredentials], None]:
        security = self.security

        def compare_digest(a: str, b: str) -> bool:
            return secrets.compare_digest(a.encode(), b.encode())

        def authenticate(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> None:
            is_correct_username = compare_digest(credentials.username, self.username)
            is_correct_password = compare_digest(credentials.password, self.password)

            if not (is_correct_username and is_correct_password):
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Basic"},
                )

        return authenticate
