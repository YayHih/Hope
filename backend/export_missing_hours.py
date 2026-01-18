"""
Export food locations without operating hours to CSV for manual entry.

This script creates a CSV file that you can fill in with hours data,
then import back into the database.
"""

import asyncio
import os
import csv
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


async def export_missing_hours():
    """Export food locations without hours to CSV."""

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    output_file = Path('/home/opc/Hope/backend/food_locations_need_hours.csv')

    print("=" * 60)
    print("EXPORTING FOOD LOCATIONS WITHOUT HOURS")
    print("=" * 60)

    async with async_session() as db:
        # Get all food locations without operating hours
        result = await db.execute(text("""
            SELECT
                sl.id,
                sl.name,
                sl.street_address,
                sl.city,
                sl.state,
                sl.zip_code,
                sl.phone,
                sl.website
            FROM service_locations sl
            JOIN location_services ls ON sl.id = ls.location_id
            JOIN service_types st ON ls.service_type_id = st.id
            WHERE st.slug = 'food'
            AND sl.deleted_at IS NULL
            AND NOT EXISTS (
                SELECT 1 FROM operating_hours oh
                WHERE oh.location_id = sl.id
            )
            ORDER BY sl.borough, sl.name
        """))

        locations = result.fetchall()
        total = len(locations)

        print(f"\nFound {total} food locations without hours\n")

        # Write to CSV with columns for entering hours
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'name', 'street_address', 'city', 'state', 'zip_code',
                'phone', 'website',
                'monday_open', 'monday_close', 'monday_notes',
                'tuesday_open', 'tuesday_close', 'tuesday_notes',
                'wednesday_open', 'wednesday_close', 'wednesday_notes',
                'thursday_open', 'thursday_close', 'thursday_notes',
                'friday_open', 'friday_close', 'friday_notes',
                'saturday_open', 'saturday_close', 'saturday_notes',
                'sunday_open', 'sunday_close', 'sunday_notes',
                'is_24_7', 'hours_notes'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for loc in locations:
                writer.writerow({
                    'id': str(loc.id),
                    'name': loc.name,
                    'street_address': loc.street_address,
                    'city': loc.city,
                    'state': loc.state,
                    'zip_code': loc.zip_code,
                    'phone': loc.phone or '',
                    'website': loc.website or '',
                    # Leave hours columns empty for manual entry
                })

        print(f"✓ Exported {total} locations to {output_file.name}\n")
        print("=" * 60)
        print("INSTRUCTIONS FOR MANUAL ENTRY")
        print("=" * 60)
        print("1. Open food_locations_need_hours.csv in a spreadsheet")
        print("2. For each location, fill in the hours columns:")
        print("   - Use 24-hour format (e.g., 09:00, 17:30)")
        print("   - Leave blank if closed that day")
        print("   - Set is_24_7 to 'true' if open 24/7")
        print("   - Add notes like 'Appointment only' if needed")
        print("3. Save the CSV file")
        print("4. Run import_food_hours.py to import the data")
        print("=" * 60)

        # Also create a quick reference guide
        guide_file = Path('/home/opc/Hope/backend/hours_entry_guide.txt')
        with open(guide_file, 'w') as f:
            f.write("FOOD LOCATION HOURS ENTRY GUIDE\n")
            f.write("=" * 60 + "\n\n")
            f.write("HOW TO FIND HOURS:\n")
            f.write("1. Search Google for: [location name] + [address] + hours\n")
            f.write("2. Check the location's website (if listed)\n")
            f.write("3. Call the phone number (if listed)\n\n")
            f.write("TIME FORMAT:\n")
            f.write("- Use 24-hour format: 09:00, 14:30, 17:00\n")
            f.write("- Or 12-hour with AM/PM: 9:00 AM, 2:30 PM, 5:00 PM\n\n")
            f.write("EXAMPLES:\n")
            f.write("monday_open: 09:00\n")
            f.write("monday_close: 17:00\n")
            f.write("monday_notes: By appointment only\n\n")
            f.write("SPECIAL CASES:\n")
            f.write("- If closed all day: leave open/close blank\n")
            f.write("- If 24/7: set is_24_7 to 'true'\n")
            f.write("- If same hours every day: copy the values\n")
            f.write("- If hours vary: add note in hours_notes column\n\n")
            f.write("=" * 60 + "\n")

        print(f"\n✓ Created entry guide: {guide_file.name}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(export_missing_hours())
