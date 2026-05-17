from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


class TokenUser(BaseModel):
    user_id: str
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
    user_id = payload.get("sub")
    if not user_id:
        return None
    return TokenUser(user_id=str(user_id), email=payload.get("email"))
