from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.auth.models import User
from app.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    VerifyResponse,
)
from app.config import settings


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        farm_name=user.farm_name,
        created_at=user.created_at,
    )


def register_user(session: Session, body: UserCreate) -> User:
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise DuplicateEmailError("email already registered")
    user = User(
        email=body.email,
        farm_name=body.farm_name,
        password_hash=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(session: Session, body: LoginRequest) -> User:
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise InvalidCredentialsError("Invalid email or password")
    return user


def get_user(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)


def create_token(user: User) -> TokenResponse:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": user.id, "email": user.email, "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.access_token_expire_minutes,
    )


def verify_token(session: Session, token: str | None) -> VerifyResponse:
    if not token:
        return VerifyResponse(valid=False)
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return VerifyResponse(valid=False)
    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not get_user(session, str(user_id)):
        return VerifyResponse(valid=False)
    return VerifyResponse(valid=True, user_id=str(user_id), email=email)


def count_users(session: Session) -> int:
    return len(session.exec(select(User)).all())
