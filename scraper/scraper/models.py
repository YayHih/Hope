"""Shared data models for scraper."""
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, time


class OperatingHours(BaseModel):
    """Operating hours for a specific day and service type."""
    day_of_week: int  # 0=Monday, 6=Sunday
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_24_hours: bool = False
    is_closed: bool = False
    notes: Optional[str] = None


class ServiceCapacity(BaseModel):
    """Capacity and notes for a specific service type."""
    service_type: str  # slug like "shelter", "food"
    capacity: Optional[int] = None
    notes: Optional[str] = None


class RawServiceData(BaseModel):
    """Standardized format for all scrapers."""

    # Basic info
    name: str
    organization_name: Optional[str] = None
    description: Optional[str] = None

    # Address
    street_address: Optional[str] = None
    city: str = "New York"
    state: str = "NY"
    zip_code: Optional[str] = None
    borough: Optional[str] = None

    # Contact
    phone: Optional[str] = None
    website: Optional[str] = None

    # Service types (slugs)
    service_types: List[str]  # ["food", "shelter"]

    # Service-specific details
    service_capacities: Optional[List[ServiceCapacity]] = None
    operating_hours: Optional[List[OperatingHours]] = None

    # Accessibility
    wheelchair_accessible: Optional[bool] = None
    languages_spoken: Optional[List[str]] = None

    # Metadata for deduplication
    external_id: str  # From source system
    data_source: str  # "NYC Open Data", "211 NYC", etc.
    scraped_at: datetime = datetime.now()

    class Config:
        arbitrary_types_allowed = True
