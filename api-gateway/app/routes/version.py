import os

from fastapi import APIRouter

router = APIRouter(tags=["meta"])


@router.get("/version")
async def version() -> dict:
    return {
        "service": "api-gateway",
        "version": os.environ.get("COWLY_VERSION", "0.1.0"),
        "build_timestamp": os.environ.get("COWLY_BUILD_TIMESTAMP", "unknown"),
        "vcs_ref": os.environ.get("COWLY_VCS_REF", "unknown"),
    }
