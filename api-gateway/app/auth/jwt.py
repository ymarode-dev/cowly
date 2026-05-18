from __future__ import annotations



from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings
from app.redis_client import is_token_blacklisted


class TokenUser(BaseModel):
    user_id: str
    farm_id: str
    email: str | None = None


def decode_access_token(token: str) -> TokenUser | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return None

    if payload.get("type") not in (None, "access"):
        return None

    jti = payload.get("jti")
    if jti and is_token_blacklisted(str(jti)):
        return None

    user_id = payload.get("sub")
    farm_id = payload.get("farm_id")
    if not user_id or not farm_id:
        return None
    return TokenUser(
        user_id=str(user_id),
        farm_id=str(farm_id),
        email=payload.get("email"),
    )
