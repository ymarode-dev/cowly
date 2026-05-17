from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.cows import schemas, service
from app.database import get_session
from app.security.deps import get_current_user

router = APIRouter(
    prefix="/api/v1/cows",
    tags=["cows"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[schemas.CowResponse])
def list_cows(session: Session = Depends(get_session)) -> list[schemas.CowResponse]:
    return service.list_cows(session)


@router.post("", response_model=schemas.CowResponse, status_code=201)
def create_cow(
    body: schemas.CowCreate,
    session: Session = Depends(get_session),
) -> schemas.CowResponse:
    try:
        return service.create_cow(session, body)
    except service.DuplicateEarTagError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{cow_id}", response_model=schemas.CowResponse)
def get_cow(
    cow_id: str,
    session: Session = Depends(get_session),
) -> schemas.CowResponse:
    try:
        return service.get_cow(session, cow_id)
    except service.CowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{cow_id}", response_model=schemas.CowResponse)
def update_cow(
    cow_id: str,
    body: schemas.CowUpdate,
    session: Session = Depends(get_session),
) -> schemas.CowResponse:
    try:
        return service.update_cow(session, cow_id, body)
    except service.CowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{cow_id}", status_code=204)
def delete_cow(cow_id: str, session: Session = Depends(get_session)) -> None:
    try:
        service.delete_cow(session, cow_id)
    except service.CowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
