#!/usr/bin/env python3
"""
Enhanced Food Pantry Ingestion with Multiple Data Sources

This script attempts to gather food pantry data with operating hours from:
1. NYC HRA Community Food Connection (CFC) - Official list
2. City Harvest Food Map
3. Plentiful App data (if accessible)
4. Web scraping as fallback

Approach:
- Use httpx to fetch pages
- Parse HTML/JSON for pantry info
- Extract hours when available
- Update existing pantries with hours data
"""
import asyncio
import sys
import re
from pathlib import Path
from datetime import time as dt_time
from typing import Optional, List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.service_location import ServiceLocation
from app.models.service_type import ServiceType
from app.models.location_service import LocationService
from app.models.operating_hours import OperatingHours


def parse_time_string(time_str: str) -> Optional[dt_time]:
    """Parse time strings like '9:00 AM', '2:30 PM', '14:00' to time objects."""
    if not time_str:
        return None

    time_str = time_str.strip().upper()

    # Try 12-hour format with AM/PM
    match = re.match(r'(\d{1,2}):?(\d{2})?\s*(AM|PM)', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)

        if period == 'PM' and hour != 12:
            hour += 12
        elif period == 'AM' and hour == 12:
            hour = 0

        return dt_time(hour, minute)

    # Try 24-hour format
    match = re.match(r'(\d{1,2}):(\d{2})', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return dt_time(hour, minute)

    return None


def parse_day_name(day: str) -> Optional[int]:
    """Convert day name to database day number (0=Sunday, 1=Monday, etc.)"""
    day_map = {
        'SUNDAY': 0, 'SUN': 0,
        'MONDAY': 1, 'MON': 1,
        'TUESDAY': 2, 'TUE': 2, 'TUES': 2,
        'WEDNESDAY': 3, 'WED': 3,
        'THURSDAY': 4, 'THU': 4, 'THUR': 4, 'THURS': 4,
        'FRIDAY': 5, 'FRI': 5,
        'SATURDAY': 6, 'SAT': 6
    }
    return day_map.get(day.upper().strip())


async def scrape_city_harvest_foodmap(session: AsyncSession, food_type: ServiceType):
    """
    Scrape City Harvest Food Map for locations with hours.

    City Harvest has a public food map that shows pantries, soup kitchens,
    community fridges, and mobile markets with hours.

    Note: This is a placeholder - actual implementation requires analyzing
    their map's data source (likely a JSON API endpoint).
    """
    print("\n🥕 City Harvest Food Map...")

    # City Harvest likely loads data via JavaScript/API
    # Would need to inspect network tab to find actual endpoint
    # Example: https://www.cityharvest.org/api/food-locations

    # Placeholder for demonstration
    print("⚠️  City Harvest requires API endpoint identification")
    print("   Recommended: Use browser dev tools to find data endpoint")
    return 0


async def scrape_foodhelp_nyc():
    """
    Extract data from NYC's Food Help Finder.

    The Food Help NYC site (finder.nyc.gov/foodhelp) is a React app that
    likely loads data from an API. We need to:
    1. Inspect network requests
    2. Find the API endpoint
    3. Parse the response

    Returns list of locations with hours.
    """
    print("\n🗽 NYC Food Help Finder...")

    # This is a single-page app, so we'd need to:
    # 1. Find the API endpoint it calls
    # 2. Make requests to that endpoint
    # 3. Parse JSON response

    # Common patterns:
    # - /api/locations
    # - /data/food-pantries.json
    # - GraphQL endpoint

    # Placeholder
    print("⚠️  Food Help NYC requires API endpoint identification")
    print("   URL: https://finder.nyc.gov/foodhelp")
    print("   Action: Open in browser, check Network tab for API calls")

    return []


async def update_location_hours(
    session: AsyncSession,
    location_name: str,
    hours_data: List[Dict]
):
    """
    Update operating hours for an existing location.

    hours_data format:
    [
        {"day": "Monday", "open": "9:00 AM", "close": "5:00 PM"},
        {"day": "Tuesday", "open": "9:00 AM", "close": "5:00 PM"},
        ...
    ]
    """
    # Find location
    result = await session.execute(
        select(ServiceLocation).where(
            ServiceLocation.name.ilike(f"%{location_name}%"),
            ServiceLocation.deleted_at.is_(None)
        )
    )
    location = result.scalars().first()

    if not location:
        print(f"⏭️  {location_name} not found")
        return False

    # Delete existing hours
    result = await session.execute(
        select(OperatingHours).where(
            OperatingHours.location_id == location.id
        )
    )
    existing_hours = result.scalars().all()
    for h in existing_hours:
        await session.delete(h)

    # Add new hours
    for day_hours in hours_data:
        day_num = parse_day_name(day_hours['day'])
        if day_num is None:
            continue

        open_time = parse_time_string(day_hours.get('open'))
        close_time = parse_time_string(day_hours.get('close'))

        if day_hours.get('closed'):
            hours = OperatingHours(
                location_id=location.id,
                day_of_week=day_num,
                is_closed=True,
                notes=day_hours.get('notes', 'Closed')
            )
        elif open_time and close_time:
            hours = OperatingHours(
                location_id=location.id,
                day_of_week=day_num,
                open_time=open_time,
                close_time=close_time,
                notes=day_hours.get('notes')
            )
        else:
            continue

        session.add(hours)

    await session.flush()
    print(f"✓ Updated hours: {location_name}")
    return True


async def manual_enhancement_example(session: AsyncSession):
    """
    Example of manually curated food pantry data with hours.

    This demonstrates the data structure needed. You can populate this
    from official sources like:
    - Food Bank For New York City published lists
    - NYC HRA Community Food Connection directory
    - Individual pantry websites
    """
    print("\n📋 Manual Data Enhancement Example...")

    # Example: West Side Campaign Against Hunger
    # (One of NYC's largest food pantries)
    example_updates = [
        {
            "name": "West Side Campaign Against Hunger",
            "hours": [
                {"day": "Monday", "open": "9:00 AM", "close": "5:00 PM"},
                {"day": "Tuesday", "open": "9:00 AM", "close": "7:00 PM"},
                {"day": "Wednesday", "open": "9:00 AM", "close": "5:00 PM"},
                {"day": "Thursday", "open": "9:00 AM", "close": "7:00 PM"},
                {"day": "Friday", "open": "9:00 AM", "close": "5:00 PM"},
                {"day": "Saturday", "closed": True},
                {"day": "Sunday", "closed": True}
            ]
        },
        # Add more manually curated entries here
    ]

    updated_count = 0
    for entry in example_updates:
        success = await update_location_hours(
            session,
            entry['name'],
            entry['hours']
        )
        if success:
            updated_count += 1

    return updated_count


async def main():
    """Main enhancement function."""
    print("=" * 80)
    print("ENHANCED FOOD PANTRY HOURS INGESTION")
    print("=" * 80)
    print()
    print("This script demonstrates multiple approaches to gather food pantry hours:")
    print("1. Web scraping official directories")
    print("2. API integration (when endpoints are identified)")
    print("3. Manual curation from published sources")
    print()

    async with AsyncSessionLocal() as session:
        # Get food service type
        result = await session.execute(
            select(ServiceType).where(ServiceType.slug == "food")
        )
        food_type = result.scalars().first()

        if not food_type:
            print("❌ Food service type not found")
            return

        print(f"✓ Food Type ID: {food_type.id}")

        # Run different data sources
        # Note: Most require API endpoint identification first

        # 1. Manual enhancement example
        manual_count = await manual_enhancement_example(session)

        # 2. City Harvest (needs API endpoint)
        city_harvest_count = await scrape_city_harvest_foodmap(session, food_type)

        # 3. NYC Food Help (needs API endpoint)
        # foodhelp_data = await scrape_foodhelp_nyc()

        await session.commit()

        print()
        print("=" * 80)
        print(f"✅ COMPLETED")
        print(f"   Manual updates: {manual_count}")
        print(f"   City Harvest: {city_harvest_count}")
        print()
        print("NEXT STEPS:")
        print("1. Identify API endpoints using browser dev tools")
        print("2. Contact Food Bank NYC for data partnership")
        print("3. Expand manual curation with official sources")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
