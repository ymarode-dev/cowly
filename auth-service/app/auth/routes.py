from __future__ import annotations


from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.auth import schemas, service
from app.database import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(
    body: schemas.UserCreate,
    session: Session = Depends(get_session),
) -> schemas.UserResponse:
    try:
        user = service.register_user(session, body)
    except service.DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return service.to_response(user)


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    body: schemas.LoginRequest,
    session: Session = Depends(get_session),
) -> schemas.TokenResponse:
    try:
        user = service.authenticate(session, body)
    except service.InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return service.create_token_pair(user)


@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh(
    body: schemas.RefreshRequest,
    session: Session = Depends(get_session),
) -> schemas.TokenResponse:
    try:
        return service.refresh_tokens(session, body.refresh_token)
    except service.InvalidRefreshTokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/logout", status_code=204)
def logout(
    body: Optional[schemas.RefreshRequest] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> None:
    access = credentials.credentials if credentials else None
    refresh = body.refresh_token if body else None
    service.logout(access, refresh)


@router.get("/verify", response_model=schemas.VerifyResponse)
def verify(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session),
) -> schemas.VerifyResponse:
    token = credentials.credentials if credentials else None
    return service.verify_token(session, token)
