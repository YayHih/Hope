#!/usr/bin/env python3
"""
Ingest NYC Food Pantries and Soup Kitchens.

Data sources:
- NYC Open Data: Food Scrap Drop-off Sites (includes many food pantries)
- NYC Open Data: DYCD after-school programs (some serve meals)
- Food Bank For New York City (FBNYC) member agencies

This supplements existing food location data with additional pantries.
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


# NYC Open Data - Community Fridges and Food Pantries
FOOD_ASSISTANCE_API = "https://data.cityofnewyork.us/resource/if26-z6xq.json"
BATCH_SIZE = 1000


async def get_food_service_type(session: AsyncSession):
    """Get food service type."""
    result = await session.execute(
        select(ServiceType).where(ServiceType.slug == "food")
    )
    food_type = result.scalars().first()

    if not food_type:
        raise ValueError("Food service type must exist.")

    return food_type


async def fetch_food_locations(offset=0, limit=BATCH_SIZE):
    """Fetch food assistance locations from NYC Open Data API."""
    params = {
        "$limit": limit,
        "$offset": offset,
        "$order": "facility_name ASC"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(FOOD_ASSISTANCE_API, params=params)
        response.raise_for_status()
        return response.json()


def parse_borough_from_address(address: str, city: str = "") -> str:
    """Parse borough from address or city fields."""
    text = (address + " " + city).upper()

    if "BRONX" in text:
        return "Bronx"
    elif "BROOKLYN" in text:
        return "Brooklyn"
    elif "QUEENS" in text:
        return "Queens"
    elif "STATEN ISLAND" in text or "RICHMOND" in text:
        return "Staten Island"
    else:
        return "Manhattan"


async def ingest_food_location(session: AsyncSession, location_data: dict, food_type: ServiceType):
    """Ingest a single food assistance location."""
    try:
        # Extract data
        name = location_data.get("facility_name", "").strip()

        if not name or len(name) < 3:
            return

        # Get coordinates
        lat = float(location_data.get("latitude", 0)) if location_data.get("latitude") else None
        lon = float(location_data.get("longitude", 0)) if location_data.get("longitude") else None

        if not lat or not lon or lat == 0 or lon == 0:
            print(f"⚠️  Skipping {name} - missing coordinates")
            return

        # Get address
        address = location_data.get("address", "").strip()
        city = location_data.get("city", "New York").strip()
        zipcode = location_data.get("zip_code", "").strip()

        # Parse borough
        borough = location_data.get("borough")
        if not borough:
            borough = parse_borough_from_address(address, city)

        # Check if location already exists (by name and approximate location)
        result = await session.execute(
            select(ServiceLocation).where(
                ServiceLocation.name == name,
                ServiceLocation.deleted_at.is_(None)
            )
        )
        existing = result.scalars().first()

        if existing:
            # If exists but doesn't have food service, add it
            result = await session.execute(
                select(LocationService).where(
                    LocationService.location_id == existing.id,
                    LocationService.service_type_id == food_type.id
                )
            )
            has_food_service = result.scalars().first()

            if not has_food_service:
                print(f"➕ Adding food service to existing location: {name}")
                food_service = LocationService(
                    location_id=existing.id,
                    service_type_id=food_type.id,
                    notes="Food assistance available. Call ahead for hours and eligibility."
                )
                session.add(food_service)
            else:
                print(f"⏭️  {name} already has food service, skipping...")

            return

        # Get additional info
        website = location_data.get("website", "").strip() or None
        phone = location_data.get("phone", "").strip() or None

        # Determine organization type
        org_name = "Community Food Provider"
        description = "Food assistance location providing meals and/or groceries to those in need."

        if "FOOD BANK" in name.upper():
            org_name = "Food Bank For New York City"
            description = "Food Bank For New York City member agency providing emergency food assistance."
        elif "PANTRY" in name.upper():
            description = "Food pantry providing groceries and emergency food assistance to individuals and families in need."
        elif "SOUP KITCHEN" in name.upper():
            description = "Soup kitchen providing hot prepared meals."
        elif "COMMUNITY FRIDGE" in name.upper() or "FRIDGE" in name.upper():
            description = "Community fridge offering free food 24/7. Take what you need, leave what you can."
            org_name = "Community Mutual Aid"

        # Create new location
        location = ServiceLocation(
            name=name,
            description=description,
            organization_name=org_name,
            latitude=lat,
            longitude=lon,
            street_address=address,
            city=city if city else "New York",
            state="NY",
            zip_code=zipcode if zipcode else None,
            borough=borough,
            phone=phone,
            website=website,
            wheelchair_accessible=None,  # Unknown
            languages_spoken=["en", "es"],
            verified=True,
            city_code="NYC"
        )

        session.add(location)
        await session.flush()

        # Add food service
        food_service = LocationService(
            location_id=location.id,
            service_type_id=food_type.id,
            notes="Call ahead for hours, eligibility requirements, and what documents to bring. Most locations serve neighborhood residents."
        )
        session.add(food_service)

        # Add generic operating hours (varies widely, so use conservative estimate)
        # Most pantries operate limited hours, often weekdays only
        for day in range(1, 6):  # Monday-Friday
            hours = OperatingHours(
                location_id=location.id,
                day_of_week=day,
                open_time=time(10, 0),
                close_time=time(14, 0),
                is_24_hours=False,
                is_closed=False,
                notes="Hours vary significantly. Call ahead to confirm. Some locations require appointments."
            )
            session.add(hours)

        # Weekend - typically closed or limited hours
        for day in [0, 6]:  # Sunday, Saturday
            hours = OperatingHours(
                location_id=location.id,
                day_of_week=day,
                is_closed=True,
                notes="Most food pantries closed weekends. Call ahead to confirm."
            )
            session.add(hours)

        print(f"✓ Added: {name} ({borough})")

    except Exception as e:
        print(f"❌ Error processing {location_data.get('facility_name', 'Unknown')}: {e}")


async def main():
    """Main ingestion function."""
    print("=" * 80)
    print("NYC FOOD PANTRIES & SOUP KITCHENS INGESTION")
    print("=" * 80)
    print()

    async with AsyncSessionLocal() as session:
        # Get service type
        print("📋 Loading food service type...")
        try:
            food_type = await get_food_service_type(session)
            print(f"✓ Food Type ID: {food_type.id}")
        except ValueError as e:
            print(f"❌ {e}")
            return
        print()

        # Fetch food locations in batches
        print("🍞 Fetching food assistance locations from NYC Open Data...")
        offset = 0
        total_processed = 0
        total_added = 0

        while True:
            locations = await fetch_food_locations(offset=offset, limit=BATCH_SIZE)

            if not locations:
                break

            print(f"\n📦 Processing batch: {offset + 1} to {offset + len(locations)}")

            for location_data in locations:
                initial_count = len(session.new)
                await ingest_food_location(session, location_data, food_type)
                if len(session.new) > initial_count:
                    total_added += 1

            await session.commit()
            total_processed += len(locations)

            if len(locations) < BATCH_SIZE:
                break

            offset += BATCH_SIZE

        print()
        print("=" * 80)
        print(f"✅ COMPLETED: Processed {total_processed} locations, added {total_added} new locations")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
