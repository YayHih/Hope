"""
Automated hours scraper using OpenStreetMap Overpass API.

This script automatically finds and imports operating hours for food locations
by querying OpenStreetMap data, which includes business hours for many locations.
"""

import asyncio
import os
import re
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import httpx

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# Day of week mapping for OSM hours
DAY_MAP = {
    'Mo': 1,  # Monday
    'Tu': 2,  # Tuesday
    'We': 3,  # Wednesday
    'Th': 4,  # Thursday
    'Fr': 5,  # Friday
    'Sa': 6,  # Saturday
    'Su': 0   # Sunday
}

DAY_NAMES = {
    0: 'Sunday',
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday'
}


def parse_osm_opening_hours(opening_hours: str) -> list:
    """
    Parse OpenStreetMap opening_hours format.

    Examples:
    - "Mo-Fr 10:00-17:00"
    - "Mo-Fr 09:00-17:00; Sa 10:00-14:00"
    - "24/7"
    - "Mo,We,Fr 10:00-17:00"

    Returns list of dicts with day_of_week, open_time, close_time
    """
    if not opening_hours:
        return []

    hours_list = []

    # Handle 24/7
    if opening_hours.strip() == '24/7':
        for day_num in range(7):
            hours_list.append({
                'day_of_week': day_num,
                'day_name': DAY_NAMES[day_num],
                'open_time': None,
                'close_time': None,
                'is_24_hours': True,
                'is_closed': False,
                'notes': None
            })
        return hours_list

    # Split by semicolon for multiple time ranges
    segments = opening_hours.split(';')

    for segment in segments:
        segment = segment.strip()

        # Pattern: "Mo-Fr 10:00-17:00" or "Mo,We,Fr 10:00-17:00"
        match = re.match(r'([A-Za-z,\-]+)\s+(\d{2}:\d{2})-(\d{2}:\d{2})', segment)

        if match:
            days_part = match.group(1)
            open_time = match.group(2)
            close_time = match.group(3)

            # Parse days
            days = []

            # Handle ranges (Mo-Fr)
            if '-' in days_part and ',' not in days_part:
                parts = days_part.split('-')
                if len(parts) == 2:
                    start_day = DAY_MAP.get(parts[0])
                    end_day = DAY_MAP.get(parts[1])
                    if start_day is not None and end_day is not None:
                        if start_day <= end_day:
                            days = list(range(start_day, end_day + 1))
                        else:
                            # Wraps around week (e.g., Sa-Mo)
                            days = list(range(start_day, 7)) + list(range(0, end_day + 1))

            # Handle comma-separated (Mo,We,Fr)
            elif ',' in days_part:
                for day_abbr in days_part.split(','):
                    day_num = DAY_MAP.get(day_abbr.strip())
                    if day_num is not None:
                        days.append(day_num)

            # Single day
            else:
                day_num = DAY_MAP.get(days_part)
                if day_num is not None:
                    days.append(day_num)

            # Add hours for each day
            for day_num in days:
                hours_list.append({
                    'day_of_week': day_num,
                    'day_name': DAY_NAMES[day_num],
                    'open_time': open_time,
                    'close_time': close_time,
                    'is_24_hours': False,
                    'is_closed': False,
                    'notes': None
                })

    return hours_list


async def search_osm_for_location(name: str, lat: float, lon: float, radius: int = 100) -> dict:
    """
    Search OpenStreetMap for a location near the given coordinates.

    Returns dict with opening_hours if found, None otherwise.
    """
    # Overpass API query
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"](around:{radius},{lat},{lon});
      way["amenity"](around:{radius},{lat},{lon});
    );
    out tags;
    """

    overpass_url = "https://overpass-api.de/api/interpreter"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(overpass_url, data={'data': query})

            if response.status_code != 200:
                return None

            data = response.json()

            # Look through results for matching location
            for element in data.get('elements', []):
                tags = element.get('tags', {})

                # Check if name matches (case-insensitive, partial match)
                osm_name = tags.get('name', '').lower()
                search_name = name.lower()

                # Remove common suffixes for better matching
                for suffix in [' food pantry', ' soup kitchen', ' church', ' inc', ' corp', ':']:
                    osm_name = osm_name.replace(suffix, '')
                    search_name = search_name.replace(suffix, '')

                if search_name in osm_name or osm_name in search_name:
                    opening_hours = tags.get('opening_hours')
                    if opening_hours:
                        return {
                            'opening_hours': opening_hours,
                            'osm_id': element.get('id'),
                            'osm_type': element.get('type'),
                            'osm_name': tags.get('name')
                        }

            return None

    except Exception as e:
        print(f"  Error querying OSM: {str(e)}")
        return None


async def auto_scrape_hours():
    """Automatically scrape and import operating hours."""

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print("=" * 60)
    print("AUTOMATED HOURS SCRAPING (OpenStreetMap)")
    print("=" * 60)

    async with async_session() as db:
        # Get food locations without hours
        result = await db.execute(text("""
            SELECT sl.id, sl.name, sl.street_address, sl.city,
                   sl.latitude, sl.longitude
            FROM service_locations sl
            JOIN location_services ls ON sl.id = ls.location_id
            JOIN service_types st ON ls.service_type_id = st.id
            WHERE st.slug = 'food'
            AND sl.deleted_at IS NULL
            AND sl.latitude IS NOT NULL
            AND sl.longitude IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM operating_hours oh
                WHERE oh.location_id = sl.id
            )
            ORDER BY sl.name
            LIMIT 50
        """))

        locations = result.fetchall()
        total = len(locations)

        print(f"\nProcessing first {total} food locations without hours")
        print(f"(Limited to 50 to avoid API rate limits)\n")

        stats = {
            'found': 0,
            'not_found': 0,
            'imported': 0,
            'errors': 0
        }

        for idx, loc in enumerate(locations, 1):
            print(f"[{idx}/{total}] {loc.name}")

            # Search OSM
            osm_data = await search_osm_for_location(
                loc.name,
                loc.latitude,
                loc.longitude,
                radius=100  # 100 meters
            )

            if osm_data and osm_data.get('opening_hours'):
                print(f"  ✓ Found in OSM: {osm_data['osm_name']}")
                print(f"    Hours: {osm_data['opening_hours']}")

                # Parse hours
                hours_list = parse_osm_opening_hours(osm_data['opening_hours'])

                if hours_list:
                    stats['found'] += 1

                    try:
                        # Import hours into database
                        for hour in hours_list:
                            await db.execute(text("""
                                INSERT INTO operating_hours (
                                    location_id, day_of_week, day_name,
                                    open_time, close_time,
                                    is_24_hours, is_closed, notes,
                                    created_at
                                ) VALUES (
                                    :location_id, :day_of_week, :day_name,
                                    :open_time, :close_time,
                                    :is_24_hours, :is_closed, :notes,
                                    NOW()
                                )
                            """), {
                                'location_id': loc.id,
                                **hour
                            })

                        stats['imported'] += 1
                        print(f"    ✓ Imported {len(hours_list)} day entries")

                    except Exception as e:
                        stats['errors'] += 1
                        print(f"    ✗ Error importing: {str(e)}")
                else:
                    print(f"    ⚠ Could not parse hours format")
                    stats['not_found'] += 1
            else:
                stats['not_found'] += 1
                print(f"  ✗ Not found in OSM")

            # Rate limiting - be respectful to Overpass API
            if idx < total:
                await asyncio.sleep(1)  # 1 second between requests

            # Progress update every 10
            if idx % 10 == 0:
                await db.commit()  # Commit in batches
                print(f"\n--- Progress: {idx}/{total} ({stats['imported']} imported) ---\n")

        # Final commit
        await db.commit()

        print("\n" + "=" * 60)
        print("SCRAPING SUMMARY")
        print("=" * 60)
        print(f"Locations processed:  {total}")
        print(f"Hours found in OSM:   {stats['found']}")
        print(f"Successfully imported: {stats['imported']}")
        print(f"Not found:            {stats['not_found']}")
        print(f"Errors:               {stats['errors']}")
        print("=" * 60)
        print("\n✓ Automated scraping complete!")
        print("\nNote: This processed the first 50 locations.")
        print("Run again to process the next batch.")

    await engine.dispose()


if __name__ == "__main__":
    print("\n🤖 Automated Food Hours Scraper")
    print("Using OpenStreetMap Overpass API (free, no key required)")
    print("Processing first 50 locations with 1-second delays.\n")

    response = input("Continue with automated scraping? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(auto_scrape_hours())
    else:
        print("Scraping cancelled.")
