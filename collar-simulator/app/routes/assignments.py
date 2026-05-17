from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.mappers import cow_to_response
from app.models import (
    AssignByCowIdRequest,
    AssignWithCowDataRequest,
    AssignmentResponse,
)
from app.services.assignment import AssignmentError, assign_collar_to_cow, assign_collar_with_cow_data

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/link-cow", response_model=AssignmentResponse)
async def link_existing_cow(body: AssignByCowIdRequest) -> AssignmentResponse:
    """Link an existing cow record to a verified collar."""
    try:
        cow, assigned_at_str = await assign_collar_to_cow(
            body.collar_id,
            body.cow_id,
            require_identify=body.require_identify,
        )
    except AssignmentError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return AssignmentResponse(
        collar_id=body.collar_id,
        cow=cow_to_response(cow),
        assigned_at=datetime.fromisoformat(assigned_at_str),
        message=f"Collar {body.collar_id} assigned to cow {cow.id}",
    )


@router.post("/link-cow-data", response_model=AssignmentResponse)
async def link_with_cow_data(body: AssignWithCowDataRequest) -> AssignmentResponse:
    """Create cow from provided data and assign to a verified collar."""
    try:
        cow, assigned_at_str = await assign_collar_with_cow_data(
            body.collar_id,
            body.cow,
            require_identify=body.require_identify,
        )
    except AssignmentError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return AssignmentResponse(
        collar_id=body.collar_id,
        cow=cow_to_response(cow),
        assigned_at=datetime.fromisoformat(assigned_at_str),
        message=f"Collar {body.collar_id} assigned to new cow {cow.id}",
    )
