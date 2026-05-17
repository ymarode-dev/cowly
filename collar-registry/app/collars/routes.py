from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.collars import schemas, service
from app.database import get_session
from app.security.deps import get_current_user

router = APIRouter(
    prefix="/api/v1/collars",
    tags=["collars"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[schemas.CollarResponse])
def list_collars(session: Session = Depends(get_session)) -> list[schemas.CollarResponse]:
    return service.list_collars(session)


@router.post("", response_model=schemas.CollarResponse, status_code=201)
def register_collar(
    body: schemas.CollarRegister,
    session: Session = Depends(get_session),
) -> schemas.CollarResponse:
    try:
        return service.register_collar(session, body)
    except service.DuplicateMacError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{collar_id}", response_model=schemas.CollarResponse)
def get_collar(
    collar_id: str,
    session: Session = Depends(get_session),
) -> schemas.CollarResponse:
    try:
        return service.get_collar(session, collar_id)
    except service.CollarNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{collar_id}/assign/{cow_id}", response_model=schemas.CollarResponse)
def assign_collar(
    collar_id: str,
    cow_id: str,
    session: Session = Depends(get_session),
) -> schemas.CollarResponse:
    try:
        return service.assign_collar(session, collar_id, cow_id)
    except service.CollarNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
