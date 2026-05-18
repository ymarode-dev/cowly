from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.geofences import schemas, service
from app.security.deps import CurrentUser, get_current_user

router = APIRouter(
    prefix="/api/v1/geofences",
    tags=["geofences"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=List[schemas.GeofenceResponse])
def list_geofences(
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[schemas.GeofenceResponse]:
    return service.list_geofences(session, user.farm_id)


@router.post("", response_model=schemas.GeofenceResponse, status_code=201)
def create_geofence(
    body: schemas.GeofenceCreate,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.GeofenceResponse:
    return service.create_geofence(session, user.farm_id, body)


@router.get("/{geofence_id}", response_model=schemas.GeofenceResponse)
def get_geofence(
    geofence_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.GeofenceResponse:
    try:
        return service.get_geofence(session, user.farm_id, geofence_id)
    except service.GeofenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{geofence_id}", response_model=schemas.GeofenceResponse)
def update_geofence(
    geofence_id: str,
    body: schemas.GeofenceUpdate,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.GeofenceResponse:
    try:
        return service.update_geofence(session, user.farm_id, geofence_id, body)
    except service.GeofenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{geofence_id}", status_code=204)
def delete_geofence(
    geofence_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    try:
        service.delete_geofence(session, user.farm_id, geofence_id)
    except service.GeofenceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
