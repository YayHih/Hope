"""Public API endpoints (no authentication required)."""
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address
import httpx

from app.database import get_db
from app.services.geospatial_service import GeospatialService
from app.services.email_service import email_service
from app.config import settings
from app.schemas.service import (
    ServiceTypeResponse,
    ServiceLocationResponse,
    ServiceLocationDetail,
)
from app.schemas.report import ReportIssueRequest, ReportIssueResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


async def verify_recaptcha(token: str) -> bool:
    """
    Verify reCAPTCHA v2 token with Google.

    Args:
        token: The reCAPTCHA response token from the client

    Returns:
        True if verification succeeds, False otherwise
    """
    if not token:
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)

    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")

    return False


@router.get("/service-types", response_model=List[ServiceTypeResponse])
@limiter.limit("100/minute")
async def get_service_types(
    request: Request,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all service types for filter UI.

    Returns list of service types (Food, Shelter, Hygiene, etc.)
    with icons and colors for the mobile app.

    Rate limit: 100 requests per minute per IP
    """
    geo_service = GeospatialService(db)
    return await geo_service.get_service_types(active_only)


@router.get("/services/nearby", response_model=List[ServiceLocationResponse])
@limiter.limit("60/minute")
async def get_nearby_services(
    request: Request,
    latitude: float = Query(..., ge=-90, le=90, description="User's latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="User's longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=50, description="Search radius in kilometers"),
    service_types: Optional[List[str]] = Query(None, description="Filter by service type slugs"),
    open_now: bool = Query(False, description="Only show currently open locations"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Find services near a location using PostGIS geospatial queries.

    Query parameters:
    - latitude, longitude: User's current position
    - radius_km: Search radius (default 5km, max 50km)
    - service_types: Optional list of service type slugs to filter (e.g., ["food", "shelter"])
    - open_now: Only return locations currently open (default false)
    - limit: Maximum results to return (default 50, max 500)

    Returns:
    - List of service locations sorted by distance
    - Each location includes: id, name, coordinates, distance, services offered, open status

    Rate limit: 60 requests per minute per IP
    """
    geo_service = GeospatialService(db)

    return await geo_service.find_nearby(
        lat=latitude,
        lon=longitude,
        radius_km=radius_km,
        service_types=service_types,
        open_now=open_now,
        limit=limit
    )


@router.get("/services/in-bounds", response_model=List[ServiceLocationResponse])
@limiter.limit("60/minute")
async def get_services_in_bounds(
    request: Request,
    min_lat: float = Query(..., ge=-90, le=90, description="Minimum latitude (south)"),
    max_lat: float = Query(..., ge=-90, le=90, description="Maximum latitude (north)"),
    min_lng: float = Query(..., ge=-180, le=180, description="Minimum longitude (west)"),
    max_lng: float = Query(..., ge=-180, le=180, description="Maximum longitude (east)"),
    center_lat: Optional[float] = Query(None, ge=-90, le=90, description="Center latitude for distance sorting"),
    center_lng: Optional[float] = Query(None, ge=-180, le=180, description="Center longitude for distance sorting"),
    service_types: Optional[List[str]] = Query(None, description="Filter by service type slugs"),
    exclude_service_types: Optional[List[str]] = Query(None, description="Exclude specific service type slugs"),
    open_now: bool = Query(False, description="Only show currently open locations"),
    open_today: bool = Query(False, description="Only show locations open any time today"),
    limit: int = Query(75, ge=1, le=100, description="Maximum number of results (default 75 for performance)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Find services within a bounding box (viewport-based query) with optimized performance.

    PERFORMANCE OPTIMIZATIONS:
    - Uses eager loading with JOINs to eliminate N+1 query problems
    - Enforces strict limit of 75 locations (max 100) for mobile performance
    - Sorts by distance from center when center coordinates provided
    - Single optimized query instead of separate queries per location

    Query parameters:
    - min_lat, max_lat: Latitude bounds (south to north)
    - min_lng, max_lng: Longitude bounds (west to east)
    - center_lat, center_lng: Optional center for distance-based sorting
    - service_types: Optional list of service type slugs to filter
    - open_now: Only return locations currently open
    - open_today: Only return locations open any time today
    - limit: Maximum results (default 75, max 100 for mobile performance)

    Returns:
    - List of service locations within the bounding box, sorted by distance
    - Distance calculated from center if center coordinates provided

    Rate limit: 60 requests per minute per IP
    """
    # Validate bounds
    if min_lat >= max_lat:
        raise HTTPException(status_code=400, detail="min_lat must be less than max_lat")
    if min_lng >= max_lng:
        raise HTTPException(status_code=400, detail="min_lng must be less than max_lng")

    geo_service = GeospatialService(db)

    return await geo_service.find_in_bounds(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        center_lat=center_lat,
        center_lng=center_lng,
        service_types=service_types,
        exclude_service_types=exclude_service_types,
        open_now=open_now,
        open_today=open_today,
        limit=limit
    )


@router.get("/services/{location_id}", response_model=ServiceLocationDetail)
@limiter.limit("100/minute")
async def get_service_details(
    request: Request,
    location_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information for a specific service location.

    Returns:
    - Full location details
    - Operating hours for each day
    - Current closures and alerts
    - Contact information
    - Accessibility information

    Rate limit: 100 requests per minute per IP
    """
    geo_service = GeospatialService(db)
    location = await geo_service.get_location_details(location_id)

    if not location:
        raise HTTPException(status_code=404, detail="Service location not found")

    return location


@router.post("/issues/report", response_model=ReportIssueResponse)
@limiter.limit("10/hour")
async def report_issue(
    request: Request,
    report: ReportIssueRequest
):
    """
    Submit an issue report about a service location.

    This endpoint allows users to report problems such as:
    - Location permanently closed
    - Incorrect hours
    - Facility full or unavailable
    - Referral required
    - Other issues

    The report will be sent via email to the support team for review.

    Rate limit: 10 requests per hour per IP (to prevent spam)
    Protected by: Google reCAPTCHA v2
    """
    try:
        # Verify reCAPTCHA token
        is_valid = await verify_recaptcha(report.captcha_token)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="reCAPTCHA verification failed. Please try again."
            )

        # Get user's IP address for logging
        user_ip = get_remote_address(request)

        # Map issue types to human-readable labels
        issue_type_labels = {
            'closed': 'Location Permanently Closed',
            'hours': 'Hours Incorrect',
            'full': 'Facility Full/Unavailable',
            'referral': 'Referral Required',
            'other': 'Other Issue'
        }

        issue_label = issue_type_labels.get(report.issue_type, report.issue_type)

        # Send email notification
        email_sent = await email_service.send_report_email(
            issue_type=issue_label,
            location_name=report.location_name,
            description=report.description,
            user_ip=user_ip
        )

        if not email_sent:
            # Log the error but don't fail the request
            # The report is still recorded even if email fails
            raise HTTPException(
                status_code=500,
                detail="Failed to send report notification. Please try again later."
            )

        return ReportIssueResponse(
            status="success",
            message="Thank you for your report. We will review it shortly."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while submitting your report: {str(e)}"
        )
