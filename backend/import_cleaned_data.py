"""
Import cleaned service locations CSV back into the database.

This script:
1. Reads the cleaned CSV file
2. Updates existing database records by ID
3. Handles duplicates that were removed (marks as deleted)
4. Reports what was changed
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

async def import_cleaned_data():
    """Import cleaned CSV data back into database."""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    cleaned_csv = Path('/home/opc/Hope/backend/all_service_locations_CLEANED.csv')

    if not cleaned_csv.exists():
        print(f"❌ Error: {cleaned_csv} not found!")
        return

    print(f"Reading cleaned data from {cleaned_csv.name}...")

    # Read the cleaned CSV
    cleaned_data = {}
    with open(cleaned_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            location_id = row['ID']  # UUID string
            cleaned_data[location_id] = row

    print(f"✓ Loaded {len(cleaned_data)} cleaned locations\n")

    async with async_session() as db:
        # Get all current location IDs
        result = await db.execute(text("""
            SELECT id FROM service_locations WHERE deleted_at IS NULL
        """))
        current_ids = {row.id for row in result.fetchall()}

        print(f"Current database has {len(current_ids)} active locations")

        # Determine which IDs were removed (duplicates or bad coords)
        cleaned_ids = set(cleaned_data.keys())
        removed_ids = current_ids - cleaned_ids

        print(f"Found {len(removed_ids)} locations to mark as deleted (duplicates/bad coords)\n")

        stats = {
            'updated_zip_codes': 0,
            'updated_coordinates': 0,
            'marked_deleted': 0,
            'no_changes': 0
        }

        # Mark removed locations as deleted
        if removed_ids:
            print("Marking removed locations as deleted...")
            for location_id in removed_ids:
                await db.execute(text("""
                    UPDATE service_locations
                    SET deleted_at = NOW()
                    WHERE id = :id AND deleted_at IS NULL
                """), {"id": location_id})
                stats['marked_deleted'] += 1

            print(f"  ✓ Marked {stats['marked_deleted']} locations as deleted\n")

        # Update cleaned locations
        print("Updating cleaned location data...")

        for location_id, row in cleaned_data.items():
            # Get current record
            result = await db.execute(text("""
                SELECT zip_code, latitude, longitude
                FROM service_locations
                WHERE id = :id
            """), {"id": location_id})

            current = result.fetchone()
            if not current:
                continue

            updates = {}
            changed = False

            # Check if zip code was recovered
            new_zip = row['Zip Code'].strip() if row['Zip Code'] else None
            current_zip = current.zip_code

            if new_zip and not current_zip:
                updates['zip_code'] = new_zip
                stats['updated_zip_codes'] += 1
                changed = True

            # Check if coordinates changed (shouldn't, but safety check)
            new_lat = float(row['Latitude']) if row['Latitude'] else None
            new_lon = float(row['Longitude']) if row['Longitude'] else None

            if new_lat and new_lon:
                if abs(new_lat - current.latitude) > 0.00001 or abs(new_lon - current.longitude) > 0.00001:
                    updates['latitude'] = new_lat
                    updates['longitude'] = new_lon
                    stats['updated_coordinates'] += 1
                    changed = True

            # Perform update if anything changed
            if updates:
                update_parts = [f"{k} = :{k}" for k in updates.keys()]
                update_sql = f"""
                    UPDATE service_locations
                    SET {', '.join(update_parts)}, updated_at = NOW()
                    WHERE id = :id
                """
                updates['id'] = location_id
                await db.execute(text(update_sql), updates)
            else:
                stats['no_changes'] += 1

        # Commit all changes
        await db.commit()

        print(f"  ✓ Updated {len(cleaned_data)} location records\n")

        # Summary
        print("=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"Locations marked as deleted:  {stats['marked_deleted']:,}")
        print(f"  (These were duplicates or had bad coordinates)")
        print(f"\nZip codes recovered:          {stats['updated_zip_codes']:,}")
        print(f"Coordinates updated:          {stats['updated_coordinates']:,}")
        print(f"No changes needed:            {stats['no_changes']:,}")
        print(f"\nTotal locations processed:    {len(cleaned_data):,}")
        print("=" * 60)
        print("\n✓ Import complete!")

        # Show what was deleted
        if removed_ids:
            print(f"\nℹ️  {stats['marked_deleted']} locations were soft-deleted (marked with deleted_at)")
            print("   These can be reviewed in the database and restored if needed.")
            print("   They were removed as duplicates or had bad coordinates (lat/lon = 0 or lat > 42)")

    await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("IMPORTING CLEANED DATA INTO DATABASE")
    print("=" * 60)
    print("This script will:")
    print("  1. Update zip codes that were recovered from addresses")
    print("  2. Mark duplicate locations as deleted (soft delete)")
    print("  3. Mark locations with bad coordinates as deleted")
    print("=" * 60)

    response = input("\nContinue with import? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(import_cleaned_data())
    else:
        print("Import cancelled.")
