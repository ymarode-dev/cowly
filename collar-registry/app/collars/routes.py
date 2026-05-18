from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.collars import schemas, service
from app.database import get_session
from app.security.deps import CurrentUser, get_current_user

router = APIRouter(
    prefix="/api/v1/collars",
    tags=["collars"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=List[schemas.CollarResponse])
def list_collars(
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[schemas.CollarResponse]:
    return service.list_collars(session, user.farm_id)


@router.post("", response_model=schemas.CollarResponse, status_code=201)
def register_collar(
    body: schemas.CollarRegister,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.CollarResponse:
    try:
        return service.register_collar(session, user.farm_id, body)
    except service.DuplicateMacError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{collar_id}", response_model=schemas.CollarResponse)
def get_collar(
    collar_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.CollarResponse:
    try:
        return service.get_collar(session, user.farm_id, collar_id)
    except service.CollarNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{collar_id}/assign/{cow_id}", response_model=schemas.CollarResponse)
def assign_collar(
    collar_id: str,
    cow_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.CollarResponse:
    try:
        return service.assign_collar(session, user.farm_id, collar_id, cow_id)
    except service.CollarNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
