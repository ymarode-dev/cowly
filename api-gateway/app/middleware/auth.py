from __future__ import annotations


from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.jwt import decode_access_token

PUBLIC_METHOD_PATHS = {
    ("POST", "/api/v1/auth/register"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/refresh"),
}

PUBLIC_PATH_PREFIXES = (
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
)


def is_public_route(method: str, path: str) -> bool:
    if path == "/":
        return True
    if any(path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES):
        return True
    normalized = path.rstrip("/") or "/"
    return (method.upper(), normalized) in PUBLIC_METHOD_PATHS


def extract_bearer_token(request: Request) -> str | None:
    auth = request.headers.get("authorization")
    if not auth:
        return None
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        if not request.url.path.startswith("/api/v1"):
            return await call_next(request)

        if is_public_route(request.method, request.url.path):
            return await call_next(request)

        token = extract_bearer_token(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = decode_access_token(token)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user_id = user.user_id
        request.state.user_email = user.email
        request.state.farm_id = user.farm_id
        return await call_next(request)
