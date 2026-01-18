"""Deduplication processor to match scraped data with existing records."""
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, Tuple
from difflib import SequenceMatcher
import sys
import os

# Add backend path to sys.path to import models
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
sys.path.insert(0, backend_path)

from app.models.service_location import ServiceLocation
from app.models.location_service import LocationService
from app.models.service_type import ServiceType
from app.models.operating_hours import OperatingHours
from scraper.models import RawServiceData


class Deduplicator:
    """Match scraped data to existing database records."""

    def __init__(self, db: Session):
        self.db = db

    def find_match(
        self,
        raw_data: RawServiceData
    ) -> Optional[ServiceLocation]:
        """
        Try to match scraped data to existing record.

        Strategy:
        1. Exact match on external_id + data_source
        2. Fuzzy match on name + address
        3. Geospatial match (within 50 meters) - future enhancement

        Args:
            raw_data: Scraped data to match

        Returns:
            Matching ServiceLocation or None
        """
        # Strategy 1: External ID match
        if raw_data.external_id and raw_data.data_source:
            match = self.db.query(ServiceLocation).filter(
                ServiceLocation.external_id == raw_data.external_id,
                ServiceLocation.data_source == raw_data.data_source
            ).first()

            if match:
                print(f"    ✓ Found exact match by external_id: {match.name}")
                return match

        # Strategy 2: Fuzzy name + address match
        if raw_data.borough:
            # Get all locations in same borough
            candidates = self.db.query(ServiceLocation).filter(
                ServiceLocation.borough == raw_data.borough,
                ServiceLocation.deleted_at.is_(None)
            ).all()

            for candidate in candidates:
                name_similarity = SequenceMatcher(
                    None,
                    raw_data.name.lower(),
                    candidate.name.lower()
                ).ratio()

                # Check address similarity if both have addresses
                address_similarity = 0.0
                if raw_data.street_address and candidate.street_address:
                    address_similarity = SequenceMatcher(
                        None,
                        raw_data.street_address.lower(),
                        candidate.street_address.lower()
                    ).ratio()

                # High confidence match
                if name_similarity > 0.85 and address_similarity > 0.8:
                    print(f"    ✓ Found fuzzy match: {candidate.name} (name: {name_similarity:.2f}, addr: {address_similarity:.2f})")
                    return candidate

        # No match found
        return None

    def create_or_update(
        self,
        raw_data: RawServiceData,
        coords: Optional[Tuple[float, float]]
    ) -> ServiceLocation:
        """
        Create new location or update existing one.

        Args:
            raw_data: Scraped data
            coords: Tuple of (latitude, longitude)

        Returns:
            ServiceLocation object
        """
        if not coords:
            raise ValueError("Coordinates are required to create/update location")

        lat, lon = coords

        # Check for existing match
        existing = self.find_match(raw_data)

        if existing:
            # Update existing record
            print(f"    Updating existing location: {existing.name}")
            existing.name = raw_data.name
            existing.description = raw_data.description or existing.description
            existing.organization_name = raw_data.organization_name or existing.organization_name
            existing.phone = raw_data.phone or existing.phone
            existing.website = raw_data.website or existing.website
            existing.wheelchair_accessible = raw_data.wheelchair_accessible or existing.wheelchair_accessible
            existing.languages_spoken = raw_data.languages_spoken or existing.languages_spoken
            existing.latitude = lat
            existing.longitude = lon

            return existing

        else:
            # Create new record
            print(f"    Creating new location: {raw_data.name}")
            location = ServiceLocation(
                name=raw_data.name,
                description=raw_data.description,
                organization_name=raw_data.organization_name,
                street_address=raw_data.street_address,
                city=raw_data.city,
                state=raw_data.state,
                zip_code=raw_data.zip_code,
                borough=raw_data.borough,
                phone=raw_data.phone,
                website=raw_data.website,
                wheelchair_accessible=raw_data.wheelchair_accessible,
                languages_spoken=raw_data.languages_spoken,
                latitude=lat,
                longitude=lon,
                # No PostGIS needed - just latitude and longitude columns
                data_source=raw_data.data_source,
                external_id=raw_data.external_id,
                verified=False,
            )

            self.db.add(location)
            self.db.flush()  # Get the ID without committing

            return location

    def add_services(
        self,
        location: ServiceLocation,
        service_type_slugs: list[str],
        service_capacities: Optional[list] = None
    ):
        """
        Add service types to a location with optional capacity data.

        Args:
            location: ServiceLocation object
            service_type_slugs: List of service type slugs
            service_capacities: Optional list of ServiceCapacity objects
        """
        # Get service type IDs
        service_types = self.db.query(ServiceType).filter(
            ServiceType.slug.in_(service_type_slugs)
        ).all()

        # Remove existing associations
        self.db.query(LocationService).filter(
            LocationService.location_id == location.id
        ).delete()

        # Create capacity lookup by service type slug
        capacity_map = {}
        if service_capacities:
            for cap in service_capacities:
                capacity_map[cap.service_type] = cap

        # Add new associations
        for service_type in service_types:
            capacity_data = capacity_map.get(service_type.slug)

            location_service = LocationService(
                location_id=location.id,
                service_type_id=service_type.id,
                capacity=capacity_data.capacity if capacity_data else None,
                notes=capacity_data.notes if capacity_data else None
            )
            self.db.add(location_service)

    def add_operating_hours(
        self,
        location: ServiceLocation,
        operating_hours_list: Optional[list]
    ):
        """
        Add operating hours to a location.

        Args:
            location: ServiceLocation object
            operating_hours_list: Optional list of OperatingHours objects from scraper models
        """
        if not operating_hours_list:
            return

        # Flush any pending changes to ensure location_services are in the database
        self.db.flush()

        # Get all service types for this location to map hours
        location_services = self.db.query(LocationService).filter(
            LocationService.location_id == location.id
        ).all()

        # Create a mapping of service_type_id to LocationService
        service_map = {ls.service_type_id: ls for ls in location_services}

        if not service_map:
            print(f"    ⚠️ No service types found for location {location.id}, skipping operating hours")
            return

        # Remove existing operating hours
        self.db.query(OperatingHours).filter(
            OperatingHours.location_id == location.id
        ).delete()

        # Add new operating hours
        for hours_data in operating_hours_list:
            # If the operating hours specify a service type, try to match it
            # For now, we'll add hours for all service types at this location
            for service_type_id in service_map.keys():
                operating_hours = OperatingHours(
                    location_id=location.id,
                    service_type_id=service_type_id,
                    day_of_week=hours_data.day_of_week,
                    open_time=hours_data.open_time,
                    close_time=hours_data.close_time,
                    is_24_hours=hours_data.is_24_hours,
                    is_closed=hours_data.is_closed,
                    notes=hours_data.notes
                )
                self.db.add(operating_hours)
