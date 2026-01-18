"""
Import NYC Public Restrooms dataset into the Hope database.

This script:
1. Reads the Public_Restrooms CSV file
2. Creates a new service type 'Public Restrooms' if not exists
3. Imports operational restrooms with valid coordinates
4. Maps operating hours from the CSV format to our database format
5. Links each restroom to the 'Public Restrooms' service type
"""

import asyncio
import os
import csv
import re
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def day_name_to_int(day_name):
    """Convert day name to integer (0=Sunday, 6=Saturday)"""
    day_map = {
        'sunday': 0,
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6
    }
    return day_map.get(day_name.lower())

def parse_hours(hours_text):
    """
    Parse hours text from CSV into structured operating hours.

    Examples:
    - "6am-11pm" -> [{"day": "Monday", "open_time": "06:00", "close_time": "23:00", ...}]
    - "8am-4pm, Open later seasonally" -> [{"day": "Monday", "open_time": "08:00", "close_time": "16:00", ...}]
    - Multi-line library hours with day-specific times
    """
    if not hours_text or hours_text.strip() == '':
        return []

    hours_text = hours_text.strip()

    # Check if it's library-style hours (contains day names and times)
    if any(day in hours_text for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
        return parse_library_hours(hours_text)

    # Simple hours like "6am-11pm" or "8am-4pm"
    time_pattern = r'(\d{1,2})\s*([ap]m)\s*-\s*(\d{1,2})\s*([ap]m)'
    match = re.search(time_pattern, hours_text, re.IGNORECASE)

    if match:
        start_hour = int(match.group(1))
        start_period = match.group(2).lower()
        end_hour = int(match.group(3))
        end_period = match.group(4).lower()

        # Convert to 24-hour format
        if start_period == 'pm' and start_hour != 12:
            start_hour += 12
        elif start_period == 'am' and start_hour == 12:
            start_hour = 0

        if end_period == 'pm' and end_hour != 12:
            end_hour += 12
        elif end_period == 'am' and end_hour == 12:
            end_hour = 0

        # Clamp hours to valid range (0-23)
        start_hour = max(0, min(23, start_hour))
        end_hour = max(0, min(23, end_hour))

        open_time = time(start_hour, 0)
        close_time = time(end_hour, 0)

        # Apply to all 7 days
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return [
            {
                'day_of_week': day_name_to_int(day),
                'open_time': open_time,
                'close_time': close_time,
                'is_closed': False
            }
            for day in days
        ]

    return []

def parse_library_hours(hours_text):
    """
    Parse library-style hours with day-specific times.

    Example:
    Monday	10 am - 6 pm
    Tuesday	1 pm - 8 pm
    Wednesday	10 am - 6 pm
    """
    hours = []
    lines = hours_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to match "Day Time - Time" or "Day CLOSED"
        day_match = re.match(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(.+)', line, re.IGNORECASE)
        if not day_match:
            continue

        day = day_match.group(1).capitalize()
        time_info = day_match.group(2).strip()

        if 'CLOSED' in time_info.upper():
            hours.append({
                'day_of_week': day_name_to_int(day),
                'open_time': None,
                'close_time': None,
                'is_closed': True
            })
            continue

        # Parse time range
        time_pattern = r'(\d{1,2})\s*:?\s*(\d{2})?\s*([ap]m)\s*-\s*(\d{1,2})\s*:?\s*(\d{2})?\s*([ap]m)'
        time_match = re.search(time_pattern, time_info, re.IGNORECASE)

        if time_match:
            start_hour = int(time_match.group(1))
            start_min = int(time_match.group(2)) if time_match.group(2) else 0
            start_period = time_match.group(3).lower()
            end_hour = int(time_match.group(4))
            end_min = int(time_match.group(5)) if time_match.group(5) else 0
            end_period = time_match.group(6).lower()

            # Convert to 24-hour format
            if start_period == 'pm' and start_hour != 12:
                start_hour += 12
            elif start_period == 'am' and start_hour == 12:
                start_hour = 0

            if end_period == 'pm' and end_hour != 12:
                end_hour += 12
            elif end_period == 'am' and end_hour == 12:
                end_hour = 0

            # Clamp hours to valid range (0-23)
            start_hour = max(0, min(23, start_hour))
            end_hour = max(0, min(23, end_hour))

            hours.append({
                'day_of_week': day_name_to_int(day),
                'open_time': time(start_hour, start_min),
                'close_time': time(end_hour, end_min),
                'is_closed': False
            })

    return hours

async def import_public_restrooms():
    """Import public restrooms data into database."""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    csv_file = Path('/home/opc/Public_Restrooms_20260112.csv')

    if not csv_file.exists():
        print(f"❌ Error: {csv_file} not found!")
        return

    print(f"Reading restroom data from {csv_file.name}...")

    # Read the CSV
    restrooms = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            restrooms.append(row)

    print(f"✓ Loaded {len(restrooms)} restroom records\n")

    async with async_session() as db:
        # Step 1: Create or get the 'Public Restrooms' service type
        print("Step 1: Setting up service type...")

        result = await db.execute(text("""
            SELECT id FROM service_types WHERE slug = 'public-restrooms'
        """))
        service_type_row = result.fetchone()

        if service_type_row:
            service_type_id = service_type_row.id
            print(f"  ✓ Found existing service type (ID: {service_type_id})")
        else:
            # Create the service type
            result = await db.execute(text("""
                INSERT INTO service_types (name, slug, description, icon_name, color_hex, sort_order, active)
                VALUES ('Public Restrooms', 'public-restrooms',
                        'Public restrooms in parks, libraries, and other facilities',
                        'restroom', '#8B5CF6', 10, true)
                RETURNING id
            """))
            service_type_id = result.fetchone().id
            await db.commit()
            print(f"  ✓ Created new service type (ID: {service_type_id})")

        # Step 2: Import restroom locations
        print("\nStep 2: Importing restroom locations...")

        stats = {
            'imported': 0,
            'skipped_no_coords': 0,
            'skipped_not_operational': 0,
            'with_hours': 0,
            'duplicates': 0
        }

        for row in restrooms:
            # Parse coordinates
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
            except (ValueError, TypeError):
                stats['skipped_no_coords'] += 1
                continue

            # Skip non-operational restrooms
            status = row.get('Status', '').strip()
            if status not in ['Operational', '']:
                stats['skipped_not_operational'] += 1
                continue

            # Skip invalid coordinates
            if lat == 0 or lon == 0 or abs(lat) > 90 or abs(lon) > 180:
                stats['skipped_no_coords'] += 1
                continue

            # Prepare location data
            facility_name = row['Facility Name'].strip()
            location_type = row.get('Location Type', '').strip()
            operator = row.get('Operator', '').strip()
            website = row.get('Website', '').strip()
            hours_text = row.get('Hours of Operation', '').strip()
            accessibility = row.get('Accessibility', '').strip()
            restroom_type = row.get('Restroom Type', '').strip()
            changing_stations = row.get('Changing Stations', '').strip()
            additional_notes = row.get('Additional Notes', '').strip()

            # Build description
            description_parts = []
            if location_type:
                description_parts.append(f"Type: {location_type}")
            if operator:
                description_parts.append(f"Operated by {operator}")
            if restroom_type:
                description_parts.append(f"Facilities: {restroom_type}")
            if accessibility:
                description_parts.append(f"Accessibility: {accessibility}")
            if changing_stations and changing_stations.lower() == 'yes':
                description_parts.append("Changing stations available")
            if additional_notes:
                description_parts.append(f"Note: {additional_notes}")

            description = ' • '.join(description_parts)

            # Check for duplicates (same name and very close coordinates)
            dup_check = await db.execute(text("""
                SELECT id FROM service_locations
                WHERE name = :name
                  AND ABS(latitude - :lat) < 0.0001
                  AND ABS(longitude - :lon) < 0.0001
                  AND deleted_at IS NULL
            """), {'name': facility_name, 'lat': lat, 'lon': lon})

            if dup_check.fetchone():
                stats['duplicates'] += 1
                continue

            # Insert location
            result = await db.execute(text("""
                INSERT INTO service_locations
                (name, description, organization_name, latitude, longitude,
                 website, wheelchair_accessible, data_source, verified)
                VALUES (:name, :description, :org_name, :lat, :lon,
                        :website, :wheelchair_accessible, 'NYC OpenData - Public Restrooms', false)
                RETURNING id
            """), {
                'name': facility_name,
                'description': description,
                'org_name': operator if operator else None,
                'lat': lat,
                'lon': lon,
                'website': website if website else None,
                'wheelchair_accessible': accessibility == 'Fully Accessible'
            })

            location_id = result.fetchone().id

            # Link to service type
            await db.execute(text("""
                INSERT INTO location_services (location_id, service_type_id)
                VALUES (:location_id, :service_type_id)
            """), {'location_id': location_id, 'service_type_id': service_type_id})

            # Parse and insert operating hours if available
            if hours_text:
                operating_hours = parse_hours(hours_text)
                if operating_hours:
                    for hour_entry in operating_hours:
                        await db.execute(text("""
                            INSERT INTO operating_hours
                            (location_id, day_of_week, open_time, close_time, is_24_hours, is_closed)
                            VALUES (:location_id, :day_of_week, :open_time, :close_time, :is_24_hours, :is_closed)
                        """), {
                            'location_id': location_id,
                            'day_of_week': hour_entry['day_of_week'],
                            'open_time': hour_entry['open_time'],
                            'close_time': hour_entry['close_time'],
                            'is_24_hours': False,
                            'is_closed': hour_entry['is_closed']
                        })
                    stats['with_hours'] += 1

            stats['imported'] += 1

            # Commit every 50 records
            if stats['imported'] % 50 == 0:
                await db.commit()
                print(f"  Progress: {stats['imported']} restrooms imported...")

        # Final commit
        await db.commit()

        print(f"\n  ✓ Imported {stats['imported']} restroom locations")

        # Summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"Total records in CSV:           {len(restrooms):,}")
        print(f"Successfully imported:          {stats['imported']:,}")
        print(f"  - With operating hours:       {stats['with_hours']:,}")
        print(f"Skipped (no coordinates):       {stats['skipped_no_coords']:,}")
        print(f"Skipped (not operational):      {stats['skipped_not_operational']:,}")
        print(f"Skipped (duplicates):           {stats['duplicates']:,}")
        print("=" * 60)
        print("\n✓ Import complete!")

    await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("IMPORTING NYC PUBLIC RESTROOMS")
    print("=" * 60)
    print("This script will:")
    print("  1. Create 'Public Restrooms' service type")
    print("  2. Import operational restrooms with valid coordinates")
    print("  3. Parse and store operating hours")
    print("  4. Link restrooms to the service type")
    print("=" * 60)

    response = input("\nContinue with import? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(import_public_restrooms())
    else:
        print("Import cancelled.")
