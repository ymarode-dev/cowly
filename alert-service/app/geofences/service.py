from __future__ import annotations

import math

from sqlmodel import Session, select

from app.geofences.models import Geofence
from app.geofences.schemas import GeofenceCreate, GeofenceResponse, GeofenceUpdate


class GeofenceNotFoundError(Exception):
    pass


def to_response(geofence: Geofence) -> GeofenceResponse:
    return GeofenceResponse(
        id=geofence.id,
        farm_id=geofence.farm_id,
        name=geofence.name,
        center_latitude=geofence.center_latitude,
        center_longitude=geofence.center_longitude,
        radius_meters=geofence.radius_meters,
        active=geofence.active,
        created_at=geofence.created_at,
    )


def list_geofences(session: Session, farm_id: str) -> list[GeofenceResponse]:
    rows = session.exec(
        select(Geofence).where(Geofence.farm_id == farm_id).order_by(Geofence.created_at)
    ).all()
    return [to_response(g) for g in rows]


def create_geofence(
    session: Session,
    farm_id: str,
    body: GeofenceCreate,
) -> GeofenceResponse:
    geofence = Geofence(farm_id=farm_id, **body.model_dump())
    session.add(geofence)
    session.commit()
    session.refresh(geofence)
    return to_response(geofence)


def get_geofence(session: Session, farm_id: str, geofence_id: str) -> GeofenceResponse:
    geofence = session.get(Geofence, geofence_id)
    if not geofence or geofence.farm_id != farm_id:
        raise GeofenceNotFoundError("Geofence not found")
    return to_response(geofence)


def update_geofence(
    session: Session,
    farm_id: str,
    geofence_id: str,
    body: GeofenceUpdate,
) -> GeofenceResponse:
    geofence = session.get(Geofence, geofence_id)
    if not geofence or geofence.farm_id != farm_id:
        raise GeofenceNotFoundError("Geofence not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(geofence, key, value)
    session.add(geofence)
    session.commit()
    session.refresh(geofence)
    return to_response(geofence)


def delete_geofence(session: Session, farm_id: str, geofence_id: str) -> None:
    geofence = session.get(Geofence, geofence_id)
    if not geofence or geofence.farm_id != farm_id:
        raise GeofenceNotFoundError("Geofence not found")
    session.delete(geofence)
    session.commit()


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_earth = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * radius_earth * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_inside_geofence(
    latitude: float,
    longitude: float,
    geofence: Geofence,
) -> bool:
    distance = haversine_meters(
        latitude,
        longitude,
        geofence.center_latitude,
        geofence.center_longitude,
    )
    return distance <= geofence.radius_meters
