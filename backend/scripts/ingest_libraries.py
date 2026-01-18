#!/usr/bin/env python3
"""
Ingest NYC Public Libraries as Cooling/Warming Centers.

Data sources:
- NYC Open Data: Libraries (all branches - NYPL, Brooklyn, Queens)
- Dataset: https://data.cityofnewyork.us/Education/Libraries/p4pf-fyc4
"""
import asyncio
import sys
import os
from pathlib import Path

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


LIBRARIES_API = "https://data.cityofnewyork.us/resource/p4pf-fyc4.json"
BATCH_SIZE = 1000  # NYC Open Data limit


async def get_or_create_service_types(session: AsyncSession):
    """Get or create cooling and warming service types."""
    # Get cooling service type
    result = await session.execute(
        select(ServiceType).where(ServiceType.slug == "cooling")
    )
    cooling_type = result.scalars().first()

    if not cooling_type:
        print("Creating 'cooling' service type...")
        cooling_type = ServiceType(
            name="Cooling Center",
            slug="cooling",
            description="Air-conditioned spaces during hot weather",
            icon_name="ac_unit",
            color_hex="#4A90E2",
            sort_order=5,
            active=True
        )
        session.add(cooling_type)
        await session.flush()

    # Get warming service type
    result = await session.execute(
        select(ServiceType).where(ServiceType.slug == "warming")
    )
    warming_type = result.scalars().first()

    if not warming_type:
        print("Creating 'warming' service type...")
        warming_type = ServiceType(
            name="Warming Center",
            slug="warming",
            description="Heated spaces during cold weather",
            icon_name="local_fire_department",
            color_hex="#E67E22",
            sort_order=6,
            active=True
        )
        session.add(warming_type)
        await session.flush()

    await session.commit()
    return cooling_type, warming_type


async def fetch_libraries(offset=0, limit=BATCH_SIZE):
    """Fetch libraries from NYC Open Data API."""
    params = {
        "$limit": limit,
        "$offset": offset
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(LIBRARIES_API, params=params)
        response.raise_for_status()
        return response.json()


def parse_borough(city: str) -> str:
    """Parse borough from city field."""
    city_upper = city.upper() if city else ""

    if "BRONX" in city_upper:
        return "Bronx"
    elif "BROOKLYN" in city_upper:
        return "Brooklyn"
    elif "QUEENS" in city_upper:
        return "Queens"
    elif "STATEN" in city_upper or "RICHMOND" in city_upper:
        return "Staten Island"
    else:
        return "Manhattan"


async def ingest_library(session: AsyncSession, lib_data: dict, cooling_type: ServiceType, warming_type: ServiceType):
    """Ingest a single library location."""
    try:
        # Extract data
        name = lib_data.get("name", "Unknown Library")
        housenum = lib_data.get("housenum", "")
        streetname = lib_data.get("streetname", "")
        address = f"{housenum} {streetname}".strip() if housenum or streetname else None
        city = lib_data.get("city", "")
        zipcode = lib_data.get("zip")
        phone = None  # Not in dataset
        website = lib_data.get("url")

        # Get coordinates from the_geom point field
        the_geom = lib_data.get("the_geom")
        if the_geom and "coordinates" in the_geom:
            coords = the_geom["coordinates"]
            lon = float(coords[0]) if len(coords) > 0 else None
            lat = float(coords[1]) if len(coords) > 1 else None
        else:
            lat = None
            lon = None

        if not lat or not lon:
            print(f"⚠️  Skipping {name} - missing coordinates")
            return

        # Determine borough from borocode or city
        borocode = lib_data.get("borocode", "")
        if borocode == "1":
            borough = "Manhattan"
        elif borocode == "2":
            borough = "Bronx"
        elif borocode == "3":
            borough = "Brooklyn"
        elif borocode == "4":
            borough = "Queens"
        elif borocode == "5":
            borough = "Staten Island"
        else:
            borough = parse_borough(city)

        # Check if location already exists (by name and approximate location)
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

        # Determine organization from system field
        library_system = lib_data.get("system", "").upper()
        if library_system == "NYPL":
            org_name = "New York Public Library (NYPL)"
        elif library_system == "BPL":
            org_name = "Brooklyn Public Library"
        elif library_system == "QPL":
            org_name = "Queens Public Library"
        else:
            org_name = "NYC Public Library"

        # Create new location
        location = ServiceLocation(
            name=name,
            description=f"Public library providing free access to books, computers, WiFi, and climate-controlled space. Serves as a cooling center in summer and warming center in winter.",
            organization_name=org_name,
            latitude=lat,
            longitude=lon,
            street_address=address,
            city=city if city else "New York",
            state="NY",
            zip_code=zipcode,
            borough=borough,
            phone=phone,
            website=website,
            wheelchair_accessible=True,  # Most NYC libraries are ADA compliant
            languages_spoken=["en", "es"],  # Most have multilingual staff
            verified=True,
            city_code="NYC"
        )

        session.add(location)
        await session.flush()

        # Add cooling center service
        cooling_service = LocationService(
            location_id=location.id,
            service_type_id=cooling_type.id,
            notes="Air-conditioned space available during library hours. Peak season: June-September."
        )
        session.add(cooling_service)

        # Add warming center service
        warming_service = LocationService(
            location_id=location.id,
            service_type_id=warming_type.id,
            notes="Heated space available during library hours. Peak season: November-March."
        )
        session.add(warming_service)

        # Add typical library operating hours (Mon-Sat 10am-6pm, closed Sunday)
        # Note: Individual libraries may vary, this is a reasonable default
        for day in range(1, 7):  # Monday-Saturday
            hours = OperatingHours(
                location_id=location.id,
                day_of_week=day,
                open_time="10:00",
                close_time="18:00",
                is_24_hours=False,
                is_closed=False,
                notes="Hours may vary by branch. Call ahead to confirm."
            )
            session.add(hours)

        # Sunday - typically closed
        sunday_hours = OperatingHours(
            location_id=location.id,
            day_of_week=0,
            is_closed=True,
            notes="Most branches closed Sundays. Check with specific branch."
        )
        session.add(sunday_hours)

        print(f"✓ Added: {name} ({borough})")

    except Exception as e:
        print(f"❌ Error processing {lib_data.get('name', 'Unknown')}: {e}")


async def main():
    """Main ingestion function."""
    print("=" * 80)
    print("NYC LIBRARIES INGESTION - Cooling & Warming Centers")
    print("=" * 80)
    print()

    async with AsyncSessionLocal() as session:
        # Get or create service types
        print("📋 Setting up service types...")
        cooling_type, warming_type = await get_or_create_service_types(session)
        print(f"✓ Cooling Type ID: {cooling_type.id}")
        print(f"✓ Warming Type ID: {warming_type.id}")
        print()

        # Fetch libraries in batches
        print("📚 Fetching libraries from NYC Open Data...")
        offset = 0
        total_added = 0

        while True:
            libraries = await fetch_libraries(offset=offset, limit=BATCH_SIZE)

            if not libraries:
                break

            print(f"\n📦 Processing batch: {offset + 1} to {offset + len(libraries)}")

            for lib_data in libraries:
                await ingest_library(session, lib_data, cooling_type, warming_type)

            await session.commit()
            total_added += len(libraries)

            if len(libraries) < BATCH_SIZE:
                break

            offset += BATCH_SIZE

        print()
        print("=" * 80)
        print(f"✅ COMPLETED: Processed {total_added} libraries")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
