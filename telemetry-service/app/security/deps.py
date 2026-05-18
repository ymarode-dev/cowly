from __future__ import annotations



from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings

security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    user_id: str
    farm_id: str
    email: str | None = None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> CurrentUser:
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user_id = payload.get("sub")
    farm_id = payload.get("farm_id")
    if not user_id or not farm_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    if payload.get("type") not in (None, "access"):
        raise HTTPException(status_code=401, detail="Invalid token type")
    return CurrentUser(
        user_id=str(user_id),
        farm_id=str(farm_id),
        email=payload.get("email"),
    )
