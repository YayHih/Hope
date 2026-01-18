#!/usr/bin/env python3
"""
Ingest NYC Parks Recreation Centers as Cooling/Warming Centers.

Data source:
- NYC Open Data: Recreation Centers
- Dataset: https://data.cityofnewyork.us/Recreation/NYC-Parks-Recreation-Centers/cqys-iuv3
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import time

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.service_location import ServiceLocation
from app.models.service_type import ServiceType
from app.models.location_service import LocationService
from app.models.operating_hours import OperatingHours


REC_CENTERS_API = "https://data.cityofnewyork.us/resource/cqys-iuv3.json"
BATCH_SIZE = 1000


async def get_service_types(session: AsyncSession):
    """Get cooling and warming service types."""
    result = await session.execute(
        select(ServiceType).where(ServiceType.slug.in_(["cooling", "warming"]))
    )
    types = {st.slug: st for st in result.scalars().all()}

    if "cooling" not in types or "warming" not in types:
        raise ValueError("Cooling and Warming service types must exist. Run ingest_libraries.py first.")

    return types["cooling"], types["warming"]


async def fetch_rec_centers(offset=0, limit=BATCH_SIZE):
    """Fetch recreation centers from NYC Open Data API."""
    params = {
        "$limit": limit,
        "$offset": offset,
        "$order": "name ASC"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(REC_CENTERS_API, params=params)
        response.raise_for_status()
        return response.json()


def parse_borough_code(borough: str) -> str:
    """Parse borough code to full name."""
    borough_map = {
        "M": "Manhattan",
        "X": "Bronx",
        "B": "Brooklyn",
        "Q": "Queens",
        "R": "Staten Island"
    }
    return borough_map.get(borough, "Manhattan")


async def ingest_rec_center(session: AsyncSession, center_data: dict, cooling_type: ServiceType, warming_type: ServiceType):
    """Ingest a single recreation center location."""
    try:
        # Extract data
        name = center_data.get("name", "Unknown Recreation Center")

        # Skip if not a recreation center
        if not name or "Recreation Center" not in name:
            return

        # Get coordinates from location field
        location_data = center_data.get("location")
        if not location_data:
            print(f"⚠️  Skipping {name} - missing location data")
            return

        lat = float(location_data.get("latitude", 0)) if location_data.get("latitude") else None
        lon = float(location_data.get("longitude", 0)) if location_data.get("longitude") else None

        if not lat or not lon or lat == 0 or lon == 0:
            print(f"⚠️  Skipping {name} - invalid coordinates")
            return

        # Get address
        address = center_data.get("address")
        zipcode = center_data.get("zipcode")
        borough_code = center_data.get("borough", "M")
        borough = parse_borough_code(borough_code)

        # Get contact info
        phone = center_data.get("phone")

        # Check if location already exists
        result = await session.execute(
            select(ServiceLocation).where(
                ServiceLocation.name == name,
                ServiceLocation.deleted_at.is_(None)
            )
        )
        existing = result.scalars().first()

        if existing:
            print(f"⏭️  {name} already exists, skipping...")
            return

        # Create new location
        location = ServiceLocation(
            name=name,
            description=f"NYC Parks recreation center with indoor facilities, programs, and climate-controlled space. Serves as a cooling center in summer and warming center in winter.",
            organization_name="NYC Parks & Recreation",
            latitude=lat,
            longitude=lon,
            street_address=address,
            city="New York",
            state="NY",
            zip_code=zipcode,
            borough=borough,
            phone=phone,
            wheelchair_accessible=True,  # Most rec centers are ADA compliant
            languages_spoken=["en", "es"],
            verified=True,
            city_code="NYC"
        )

        session.add(location)
        await session.flush()

        # Add cooling center service
        cooling_service = LocationService(
            location_id=location.id,
            service_type_id=cooling_type.id,
            notes="Air-conditioned indoor recreation center. Peak season: June-September."
        )
        session.add(cooling_service)

        # Add warming center service
        warming_service = LocationService(
            location_id=location.id,
            service_type_id=warming_type.id,
            notes="Heated indoor recreation center. Peak season: November-March."
        )
        session.add(warming_service)

        # Add typical rec center operating hours (Mon-Fri 8am-9pm, Sat-Sun 9am-5pm)
        # Weekdays
        for day in range(1, 6):  # Monday-Friday
            hours = OperatingHours(
                location_id=location.id,
                day_of_week=day,
                open_time=time(8, 0),
                close_time=time(21, 0),
                is_24_hours=False,
                is_closed=False,
                notes="Hours may vary by season and programs. Call ahead to confirm."
            )
            session.add(hours)

        # Saturday
        saturday_hours = OperatingHours(
            location_id=location.id,
            day_of_week=6,
            open_time=time(9, 0),
            close_time=time(17, 0),
            is_24_hours=False,
            is_closed=False,
            notes="Weekend hours may vary. Call ahead to confirm."
        )
        session.add(saturday_hours)

        # Sunday
        sunday_hours = OperatingHours(
            location_id=location.id,
            day_of_week=0,
            open_time=time(9, 0),
            close_time=time(17, 0),
            is_24_hours=False,
            is_closed=False,
            notes="Weekend hours may vary. Call ahead to confirm."
        )
        session.add(sunday_hours)

        print(f"✓ Added: {name} ({borough})")

    except Exception as e:
        print(f"❌ Error processing {center_data.get('name', 'Unknown')}: {e}")


async def main():
    """Main ingestion function."""
    print("=" * 80)
    print("NYC PARKS RECREATION CENTERS INGESTION - Cooling & Warming Centers")
    print("=" * 80)
    print()

    async with AsyncSessionLocal() as session:
        # Get service types
        print("📋 Loading service types...")
        try:
            cooling_type, warming_type = await get_service_types(session)
            print(f"✓ Cooling Type ID: {cooling_type.id}")
            print(f"✓ Warming Type ID: {warming_type.id}")
        except ValueError as e:
            print(f"❌ {e}")
            return
        print()

        # Fetch rec centers in batches
        print("🏃 Fetching recreation centers from NYC Open Data...")
        offset = 0
        total_added = 0

        while True:
            centers = await fetch_rec_centers(offset=offset, limit=BATCH_SIZE)

            if not centers:
                break

            print(f"\n📦 Processing batch: {offset + 1} to {offset + len(centers)}")

            for center_data in centers:
                await ingest_rec_center(session, center_data, cooling_type, warming_type)

            await session.commit()
            total_added += len(centers)

            if len(centers) < BATCH_SIZE:
                break

            offset += BATCH_SIZE

        print()
        print("=" * 80)
        print(f"✅ COMPLETED: Processed {total_added} recreation centers")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
