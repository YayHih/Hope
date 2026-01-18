"""
Import operating hours from CSV into the database.

This script reads the food_locations_need_hours.csv file (after manual entry)
and imports the operating hours into the database.
"""

import asyncio
import os
import csv
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# Day of week mapping
DAY_MAP = {
    'monday': 1,
    'tuesday': 2,
    'wednesday': 3,
    'thursday': 4,
    'friday': 5,
    'saturday': 6,
    'sunday': 0
}


def parse_time(time_str: str) -> str:
    """
    Convert time string to 24-hour format HH:MM.

    Handles formats like:
    - 09:00
    - 9:00 AM
    - 2:30 PM
    - 17:30
    """
    if not time_str or not time_str.strip():
        return None

    time_str = time_str.strip().upper()

    # If already in 24-hour format (HH:MM), return as is
    if ':' in time_str and 'AM' not in time_str and 'PM' not in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            try:
                hour = int(parts[0])
                minute = int(parts[1])
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return f"{hour:02d}:{minute:02d}"
            except:
                pass

    # Handle 12-hour format with AM/PM
    if 'AM' in time_str or 'PM' in time_str:
        time_str = time_str.replace('AM', '').replace('PM', '').strip()
        parts = time_str.split(':')
        if len(parts) == 2:
            try:
                hour = int(parts[0])
                minute = int(parts[1])

                if 'PM' in time_str.upper() and hour != 12:
                    hour += 12
                elif 'AM' in time_str.upper() and hour == 12:
                    hour = 0

                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return f"{hour:02d}:{minute:02d}"
            except:
                pass

    return None


async def import_hours_from_csv():
    """Import operating hours from CSV."""

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    csv_file = Path('/home/opc/Hope/backend/food_locations_need_hours.csv')

    if not csv_file.exists():
        print(f"❌ Error: {csv_file} not found!")
        print("Please run export_missing_hours.py first.")
        return

    print("=" * 60)
    print("IMPORTING FOOD LOCATION HOURS")
    print("=" * 60)

    # Read CSV
    hours_data = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hours_data.append(row)

    print(f"\nLoaded {len(hours_data)} locations from CSV\n")

    async with async_session() as db:
        stats = {
            'locations_with_hours': 0,
            'total_hours_added': 0,
            'skipped': 0,
            'errors': 0
        }

        for row in hours_data:
            location_id = row['id']
            location_name = row['name']

            # Check if is_24_7
            is_24_7 = row.get('is_24_7', '').lower() == 'true'

            hours_to_add = []

            # Process each day
            for day_name, day_num in DAY_MAP.items():
                open_key = f'{day_name}_open'
                close_key = f'{day_name}_close'
                notes_key = f'{day_name}_notes'

                open_time = parse_time(row.get(open_key, ''))
                close_time = parse_time(row.get(close_key, ''))
                notes = row.get(notes_key, '').strip()

                # Determine if closed
                is_closed = not is_24_7 and not open_time and not close_time

                hours_to_add.append({
                    'day_of_week': day_num,
                    'day_name': day_name.capitalize(),
                    'open_time': open_time,
                    'close_time': close_time,
                    'is_24_hours': is_24_7,
                    'is_closed': is_closed,
                    'notes': notes if notes else None
                })

            # Check if any hours were provided for this location
            has_hours = is_24_7 or any(h['open_time'] or h['close_time'] for h in hours_to_add)

            if not has_hours:
                stats['skipped'] += 1
                continue

            try:
                # Check if operating hours already exist
                result = await db.execute(text("""
                    SELECT COUNT(*) FROM operating_hours
                    WHERE location_id = :location_id
                """), {'location_id': location_id})

                existing_count = result.scalar()

                if existing_count > 0:
                    print(f"⚠ Skipping {location_name} - already has hours")
                    stats['skipped'] += 1
                    continue

                # Insert operating hours for each day
                for hour in hours_to_add:
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
                        'location_id': location_id,
                        **hour
                    })

                stats['locations_with_hours'] += 1
                stats['total_hours_added'] += len(hours_to_add)

                print(f"✓ Added hours for {location_name}")

            except Exception as e:
                stats['errors'] += 1
                print(f"✗ Error adding hours for {location_name}: {str(e)}")

        # Commit all changes
        await db.commit()

        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"Total locations in CSV:     {len(hours_data)}")
        print(f"Locations with hours added: {stats['locations_with_hours']}")
        print(f"Total hour entries added:   {stats['total_hours_added']}")
        print(f"Skipped (no data/exists):   {stats['skipped']}")
        print(f"Errors:                     {stats['errors']}")
        print("=" * 60)
        print("\n✓ Import complete!")

    await engine.dispose()


if __name__ == "__main__":
    print("\n📅 Food Hours Import Tool")
    print("This will import operating hours from the CSV file.\n")

    response = input("Continue with import? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(import_hours_from_csv())
    else:
        print("Import cancelled.")
