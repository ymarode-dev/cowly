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
    return service.create_token(user)


@router.get("/verify", response_model=schemas.VerifyResponse)
def verify(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: Session = Depends(get_session),
) -> schemas.VerifyResponse:
    token = credentials.credentials if credentials else None
    return service.verify_token(session, token)
