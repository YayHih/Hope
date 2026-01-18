"""Pydantic schemas for service-related endpoints."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date, time
from uuid import UUID


class ServiceTypeResponse(BaseModel):
    """Response schema for service types."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon_name: Optional[str] = None
    color_hex: Optional[str] = None

    class Config:
        from_attributes = True


class ServiceInfo(BaseModel):
    """Service type information for a location."""
    type: str  # Service type slug
    name: str  # Service type name
    notes: Optional[str] = None
    capacity: Optional[int] = None


class OperatingHoursResponse(BaseModel):
    """Operating hours for a service."""
    day_of_week: int
    day_name: str
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_24_hours: bool = False
    is_closed: bool = False
    notes: Optional[str] = None


class TemporaryClosureResponse(BaseModel):
    """Temporary closure or alert."""
    start_date: date
    end_date: Optional[date] = None
    reason: Optional[str] = None
    description: Optional[str] = None
    alert_type: str
    is_urgent: bool = False


class ServiceLocationResponse(BaseModel):
    """Response schema for service location (list view)."""
    id: UUID
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    distance_km: Optional[float] = None
    street_address: Optional[str] = None
    borough: Optional[str] = None
    phone: Optional[str] = None
    services: List[ServiceInfo]
    operating_hours: List[OperatingHoursResponse] = []
    is_open_now: Optional[bool] = None
    next_open_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceLocationDetail(BaseModel):
    """Detailed response schema for a single service location."""
    id: UUID
    name: str
    description: Optional[str] = None
    organization_name: Optional[str] = None
    latitude: float
    longitude: float
    street_address: Optional[str] = None
    city: str
    state: str
    zip_code: Optional[str] = None
    borough: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    wheelchair_accessible: Optional[bool] = None
    languages_spoken: Optional[List[str]] = None
    services: List[ServiceInfo]
    operating_hours: List[OperatingHoursResponse]
    current_closures: List[TemporaryClosureResponse]
    verified: bool
    last_updated: datetime

    class Config:
        from_attributes = True


class NearbyServicesRequest(BaseModel):
    """Request parameters for nearby services search."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(5.0, ge=0.1, le=50)
    service_types: Optional[List[str]] = None  # List of slugs
    open_now: bool = False
    limit: int = Field(50, ge=1, le=500)
