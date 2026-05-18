from __future__ import annotations



import json
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.auth.models import Farm, User
from app.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    VerifyResponse,
)
from app.config import settings
from app.redis_client import get_redis


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
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
        farm_id=user.farm_id,
        farm_name=user.farm_name,
        created_at=user.created_at,
    )


def register_user(session: Session, body: UserCreate) -> User:
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise DuplicateEmailError("email already registered")
    farm = Farm(name=body.farm_name)
    session.add(farm)
    session.flush()
    user = User(
        email=body.email,
        farm_id=farm.id,
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


def _encode_token(payload: dict) -> str:
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _is_blacklisted(jti: str) -> bool:
    return bool(get_redis().exists(f"access:blacklist:{jti}"))


def create_token_pair(user: User) -> TokenResponse:
    now = datetime.now(timezone.utc)
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    access_exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    refresh_exp = now + timedelta(days=settings.refresh_token_expire_days)

    access_payload = {
        "sub": user.id,
        "email": user.email,
        "farm_id": user.farm_id,
        "jti": access_jti,
        "type": "access",
        "exp": access_exp,
    }
    refresh_payload = {
        "sub": user.id,
        "email": user.email,
        "farm_id": user.farm_id,
        "jti": refresh_jti,
        "type": "refresh",
        "exp": refresh_exp,
    }

    redis_client = get_redis()
    refresh_ttl = settings.refresh_token_expire_days * 86400
    redis_client.setex(
        f"refresh:{refresh_jti}",
        refresh_ttl,
        json.dumps({"user_id": user.id, "farm_id": user.farm_id}),
    )

    return TokenResponse(
        access_token=_encode_token(access_payload),
        refresh_token=_encode_token(refresh_payload),
        expires_in_minutes=settings.access_token_expire_minutes,
    )


def refresh_tokens(session: Session, refresh_token: str) -> TokenResponse:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise InvalidRefreshTokenError("Invalid refresh token") from exc

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError("Invalid token type")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        raise InvalidRefreshTokenError("Invalid refresh token payload")

    redis_client = get_redis()
    if not redis_client.exists(f"refresh:{jti}"):
        raise InvalidRefreshTokenError("Refresh token revoked or expired")

    user = get_user(session, str(user_id))
    if not user:
        raise InvalidRefreshTokenError("User not found")

    redis_client.delete(f"refresh:{jti}")
    return create_token_pair(user)


def logout(access_token: str | None, refresh_token: str | None) -> None:
    redis_client = get_redis()
    for token, prefix in ((access_token, "access"), (refresh_token, "refresh")):
        if not token:
            continue
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            continue
        jti = payload.get("jti")
        if not jti:
            continue
        if prefix == "access":
            exp = payload.get("exp")
            ttl = 3600
            if exp:
                ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
            redis_client.setex(f"access:blacklist:{jti}", ttl, "1")
        else:
            redis_client.delete(f"refresh:{jti}")


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

    if payload.get("type") != "access":
        return VerifyResponse(valid=False)

    jti = payload.get("jti")
    if jti and _is_blacklisted(str(jti)):
        return VerifyResponse(valid=False)

    user_id = payload.get("sub")
    email = payload.get("email")
    farm_id = payload.get("farm_id")
    if not user_id or not get_user(session, str(user_id)):
        return VerifyResponse(valid=False)
    return VerifyResponse(
        valid=True,
        user_id=str(user_id),
        email=email,
        farm_id=str(farm_id) if farm_id else None,
    )


def count_users(session: Session) -> int:
    return len(session.exec(select(User)).all())
