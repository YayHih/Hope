"""Geospatial service with eager loading and security fixes."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
import math

from app.models.service_location import ServiceLocation
from app.models.service_type import ServiceType
from app.models.location_service import LocationService
from app.models.operating_hours import OperatingHours
from app.models.temporary_closure import TemporaryClosure
from app.schemas.service import (
    ServiceTypeResponse,
    ServiceLocationResponse,
    ServiceLocationDetail,
    ServiceInfo,
    OperatingHoursResponse,
    TemporaryClosureResponse,
)


class GeospatialService:
    """Service for geospatial queries with optimized eager loading."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        Returns distance in meters.
        """
        R = 6371000  # Earth radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _calculate_is_open_now(self, operating_hours_list) -> bool:
        """
        Calculate if location is open now from eager-loaded operating hours.
        This is a synchronous helper that doesn't make database queries.
        """
        if not operating_hours_list:
            return False

        now = datetime.now()
        current_day = now.weekday()  # 0 = Monday, 6 = Sunday
        # Convert to our format (0 = Sunday)
        current_day = (current_day + 1) % 7
        current_time = now.time()

        # Filter hours for today
        today_hours = [h for h in operating_hours_list if h.day_of_week == current_day]

        if not today_hours:
            return False

        # Check if any of the operating hours indicate the location is open
        for hours in today_hours:
            if hours.is_closed:
                continue

            if hours.is_24_hours:
                return True

            if hours.open_time and hours.close_time:
                if hours.open_time <= current_time <= hours.close_time:
                    return True

        return False

    async def get_service_types(self, active_only: bool = True) -> List[ServiceTypeResponse]:
        """Get all service types."""
        query = select(ServiceType)
        if active_only:
            query = query.where(ServiceType.active == True)
        query = query.order_by(ServiceType.sort_order)

        result = await self.db.execute(query)
        service_types = result.scalars().all()

        return [ServiceTypeResponse.model_validate(st) for st in service_types]

    async def find_nearby(
        self,
        lat: float,
        lon: float,
        radius_km: float = 5.0,
        service_types: Optional[List[str]] = None,
        open_now: bool = False,
        limit: int = 50
    ) -> List[ServiceLocationResponse]:
        """
        Find service locations near a point using DATABASE-FILTERED bounding box.

        SECURITY FIX: Uses bounding box approximation in SQL instead of loading
        all locations into memory (RAM bomb vulnerability fix).

        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
            service_types: Filter by service type slugs (optional)
            open_now: Filter by currently open locations (optional)
            limit: Maximum number of results

        Returns:
            List of nearby service locations with distance
        """
        # Security: Hard cap the limit to prevent scraping
        safe_limit = min(limit, 500)

        # Calculate bounding box (approximate, but filters in database)
        # 1 degree latitude ≈ 111 km
        lat_offset = radius_km / 111.0
        # 1 degree longitude ≈ 111km * cos(latitude)
        lon_offset = radius_km / (111.0 * math.cos(math.radians(lat)))

        min_lat = lat - lat_offset
        max_lat = lat + lat_offset
        min_lon = lon - lon_offset
        max_lon = lon + lon_offset

        # Build query with EAGER LOADING (fixes N+1)
        query = (
            select(ServiceLocation)
            .options(
                selectinload(ServiceLocation.location_services).selectinload(LocationService.service_type),
                selectinload(ServiceLocation.operating_hours)
            )
            .where(
                and_(
                    ServiceLocation.deleted_at.is_(None),
                    ServiceLocation.latitude >= min_lat,
                    ServiceLocation.latitude <= max_lat,
                    ServiceLocation.longitude >= min_lon,
                    ServiceLocation.longitude <= max_lon
                )
            )
        )

        # Add service type filter if specified
        if service_types:
            query = (
                query
                .join(LocationService, ServiceLocation.id == LocationService.location_id)
                .join(ServiceType, LocationService.service_type_id == ServiceType.id)
                .where(ServiceType.slug.in_(service_types))
                .distinct()
            )

        # Execute query (ONLY fetches locations in bounding box, not entire table)
        result = await self.db.execute(query)
        locations = result.scalars().unique().all()

        # Calculate exact distances and filter by radius
        locations_with_distance = []
        for location in locations:
            if location.latitude is None or location.longitude is None:
                continue

            distance_meters = self.haversine_distance(
                lat, lon, location.latitude, location.longitude
            )

            if distance_meters <= radius_km * 1000:
                locations_with_distance.append((location, distance_meters))

        # Sort by distance and limit
        locations_with_distance.sort(key=lambda x: x[1])
        locations_with_distance = locations_with_distance[:safe_limit]

        # Build response WITHOUT additional queries (data is already loaded)
        responses = []
        for location, distance_meters in locations_with_distance:
            # Calculate if open now using eager-loaded hours (no query)
            is_open = self._calculate_is_open_now(location.operating_hours)

            # If open_now filter is enabled, skip closed locations
            if open_now and not is_open:
                continue

            # Build services from eager-loaded data (no query)
            services = [
                ServiceInfo(
                    type=ls.service_type.slug,
                    name=ls.service_type.name,
                    notes=ls.notes,
                    capacity=ls.capacity,
                )
                for ls in location.location_services
            ]

            # Build operating hours from eager-loaded data (no query)
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            hours = [
                OperatingHoursResponse(
                    day_of_week=h.day_of_week,
                    day_name=day_names[h.day_of_week],
                    open_time=h.open_time,
                    close_time=h.close_time,
                    is_24_hours=h.is_24_hours,
                    is_closed=h.is_closed,
                    notes=h.notes,
                )
                for h in location.operating_hours
            ]

            responses.append(
                ServiceLocationResponse(
                    id=location.id,
                    name=location.name,
                    description=location.description,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    distance_km=round(distance_meters / 1000, 2),
                    street_address=location.street_address,
                    borough=location.borough,
                    phone=location.phone,
                    services=services,
                    operating_hours=hours,
                    is_open_now=is_open,
                )
            )

        return responses

    async def find_in_bounds(
        self,
        min_lat: float,
        max_lat: float,
        min_lng: float,
        max_lng: float,
        center_lat: Optional[float] = None,
        center_lng: Optional[float] = None,
        service_types: Optional[List[str]] = None,
        exclude_service_types: Optional[List[str]] = None,
        open_now: bool = False,
        limit: int = 75
    ) -> List[ServiceLocationResponse]:
        """
        Find service locations within a bounding box with EAGER LOADING.

        SECURITY FIX: Uses selectinload() to eliminate N+1 query problem.

        Performance: 1 query instead of 1 + (75 locations × 3 queries) = 1 vs 226 queries.

        Args:
            min_lat: Minimum latitude (south)
            max_lat: Maximum latitude (north)
            min_lng: Minimum longitude (west)
            max_lng: Maximum longitude (east)
            center_lat: Center latitude for distance sorting (optional)
            center_lng: Center longitude for distance sorting (optional)
            service_types: Filter by service type slugs (optional)
            exclude_service_types: Exclude specific service type slugs (optional)
            open_now: Filter by currently open locations (optional)
            limit: Maximum number of results (default 75 for performance)

        Returns:
            List of service locations within the bounding box, sorted by distance
        """
        # Security: Hard cap the limit to prevent scraping
        safe_limit = min(limit, 100)

        # Build query with EAGER LOADING (fixes N+1 problem)
        query = (
            select(ServiceLocation)
            .options(
                selectinload(ServiceLocation.location_services).selectinload(LocationService.service_type),
                selectinload(ServiceLocation.operating_hours)
            )
            .where(
                and_(
                    ServiceLocation.deleted_at.is_(None),
                    ServiceLocation.latitude >= min_lat,
                    ServiceLocation.latitude <= max_lat,
                    ServiceLocation.longitude >= min_lng,
                    ServiceLocation.longitude <= max_lng
                )
            )
        )

        # Calculate distance expression BEFORE adding filters (needed for ORDER BY with DISTINCT)
        distance_expr = None
        if center_lat is not None and center_lng is not None:
            # Haversine approximation for sorting (good enough for ORDER BY)
            distance_expr = func.sqrt(
                func.pow(ServiceLocation.latitude - center_lat, 2) +
                func.pow(ServiceLocation.longitude - center_lng, 2)
            )

        # Add service type filter if specified
        if service_types:
            query = (
                query
                .join(LocationService, ServiceLocation.id == LocationService.location_id)
                .join(ServiceType, LocationService.service_type_id == ServiceType.id)
                .where(ServiceType.slug.in_(service_types))
                .distinct(ServiceLocation.id)  # Use DISTINCT ON to allow ORDER BY
            )
            # With DISTINCT ON(id), must order by id first, then distance
            if distance_expr is not None:
                query = query.order_by(ServiceLocation.id, distance_expr)
        elif exclude_service_types:
            # Exclude specific service types (e.g., exclude LinkNYC when not explicitly selected)
            # Use a subquery to find locations that have the excluded service types
            excluded_location_ids = (
                select(LocationService.location_id)
                .join(ServiceType, LocationService.service_type_id == ServiceType.id)
                .where(ServiceType.slug.in_(exclude_service_types))
            )
            query = query.where(ServiceLocation.id.not_in(excluded_location_ids))
            # No service type filter, can order by distance alone
            if distance_expr is not None:
                query = query.order_by(distance_expr)
        else:
            # No service type filter, can order by distance alone
            if distance_expr is not None:
                query = query.order_by(distance_expr)

        # Enforce strict limit for performance
        query = query.limit(safe_limit)

        # Execute query (single optimized query with JOINs)
        result = await self.db.execute(query)
        locations = result.scalars().unique().all()

        # Build response WITHOUT additional queries (data is already loaded)
        responses = []
        for location in locations:
            if location.latitude is None or location.longitude is None:
                continue

            # Calculate if open now using eager-loaded hours (no query)
            is_open = self._calculate_is_open_now(location.operating_hours)

            # If open_now filter is enabled, skip closed locations
            if open_now and not is_open:
                continue

            # Calculate distance if center provided
            distance_km = 0.0
            if center_lat is not None and center_lng is not None:
                distance_m = self.haversine_distance(
                    center_lat, center_lng,
                    location.latitude, location.longitude
                )
                distance_km = distance_m / 1000.0

            # Build services from eager-loaded data (no query)
            services = [
                ServiceInfo(
                    type=ls.service_type.slug,
                    name=ls.service_type.name,
                    notes=ls.notes,
                    capacity=ls.capacity,
                )
                for ls in location.location_services
            ]

            # Build operating hours from eager-loaded data (no query)
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            hours = [
                OperatingHoursResponse(
                    day_of_week=h.day_of_week,
                    day_name=day_names[h.day_of_week],
                    open_time=h.open_time,
                    close_time=h.close_time,
                    is_24_hours=h.is_24_hours,
                    is_closed=h.is_closed,
                    notes=h.notes,
                )
                for h in location.operating_hours
            ]

            responses.append(
                ServiceLocationResponse(
                    id=location.id,
                    name=location.name,
                    description=location.description,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    distance_km=distance_km,
                    street_address=location.street_address,
                    borough=location.borough,
                    phone=location.phone,
                    services=services,
                    operating_hours=hours,
                    is_open_now=is_open,
                )
            )

        return responses

    async def get_location_details(self, location_id: UUID) -> Optional[ServiceLocationDetail]:
        """Get detailed information for a service location with eager loading."""
        query = (
            select(ServiceLocation)
            .options(
                selectinload(ServiceLocation.location_services).selectinload(LocationService.service_type),
                selectinload(ServiceLocation.operating_hours),
                selectinload(ServiceLocation.temporary_closures)
            )
            .where(
                and_(
                    ServiceLocation.id == location_id,
                    ServiceLocation.deleted_at.is_(None)
                )
            )
        )

        result = await self.db.execute(query)
        location = result.scalars().unique().one_or_none()

        if not location:
            return None

        # Build services from eager-loaded data
        services = [
            ServiceInfo(
                type=ls.service_type.slug,
                name=ls.service_type.name,
                notes=ls.notes,
                capacity=ls.capacity,
            )
            for ls in location.location_services
        ]

        # Build operating hours from eager-loaded data
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        hours = [
            OperatingHoursResponse(
                day_of_week=h.day_of_week,
                day_name=day_names[h.day_of_week],
                open_time=h.open_time,
                close_time=h.close_time,
                is_24_hours=h.is_24_hours,
                is_closed=h.is_closed,
                notes=h.notes,
            )
            for h in location.operating_hours
        ]

        # Get current closures from eager-loaded data
        today = date.today()
        closures = [
            TemporaryClosureResponse(
                start_date=c.start_date,
                end_date=c.end_date,
                reason=c.reason,
                description=c.description,
                alert_type=c.alert_type,
                is_urgent=c.is_urgent,
            )
            for c in location.temporary_closures
            if c.is_active and (c.end_date is None or c.end_date >= today)
        ]

        return ServiceLocationDetail(
            id=location.id,
            name=location.name,
            description=location.description,
            organization_name=location.organization_name,
            latitude=location.latitude,
            longitude=location.longitude,
            street_address=location.street_address,
            city=location.city,
            state=location.state,
            zip_code=location.zip_code,
            borough=location.borough,
            phone=location.phone,
            website=location.website,
            email=location.email,
            wheelchair_accessible=location.wheelchair_accessible,
            languages_spoken=location.languages_spoken,
            services=services,
            operating_hours=hours,
            current_closures=closures,
            verified=location.verified,
            last_updated=location.updated_at,
        )
