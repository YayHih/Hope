"""
Import LinkNYC kiosk locations into the database.

This script:
1. Creates a LinkNYC service type if it doesn't exist
2. Imports all LinkNYC kiosk locations from CSV
3. Associates each location with the LinkNYC service type
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

async def import_linknyc_data():
    """Import LinkNYC kiosk locations from CSV."""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    csv_file = Path('/home/opc/LinkNYC_Kiosk_Locations.csv')

    if not csv_file.exists():
        print(f"❌ Error: {csv_file} not found!")
        return

    print("=" * 60)
    print("IMPORTING LINKNYC KIOSK LOCATIONS")
    print("=" * 60)

    async with async_session() as db:
        # Step 1: Create or get LinkNYC service type
        print("\nStep 1: Setting up LinkNYC service type...")

        result = await db.execute(text("""
            SELECT id FROM service_types WHERE name = 'Free WiFi (LinkNYC)'
        """))
        service_type = result.fetchone()

        if service_type:
            service_type_id = service_type.id
            print(f"  ✓ Found existing service type: {service_type_id}")
        else:
            # Create new service type
            result = await db.execute(text("""
                INSERT INTO service_types (name, slug, description, icon_name, active, color_hex, sort_order, created_at)
                VALUES (
                    'Free WiFi (LinkNYC)',
                    'free-wifi-linknyc',
                    'Free public WiFi kiosks across NYC providing internet access, phone calls, and device charging',
                    'wifi',
                    true,
                    '#4299E1',
                    100,
                    NOW()
                )
                RETURNING id
            """))
            service_type_id = result.scalar()
            await db.commit()
            print(f"  ✓ Created new service type: {service_type_id}")

        # Step 2: Read CSV and import locations
        print("\nStep 2: Reading CSV data...")

        locations = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Only import live kiosks
                if row['Installation Status'] != 'Live':
                    continue

                locations.append({
                    'site_id': row['Site ID'],
                    'kiosk_type': row['Planned Kiosk Type'],
                    'borough': row['Borough'],
                    'street_address': row['Street Address'],
                    'postcode': row['Postcode'] if row['Postcode'] else None,
                    'latitude': float(row['Latitude']) if row['Latitude'] else None,
                    'longitude': float(row['Longitude']) if row['Longitude'] else None,
                    'neighborhood': row['Neighborhood Tabulation Area (NTA)'] if row['Neighborhood Tabulation Area (NTA)'] else None
                })

        print(f"  ✓ Found {len(locations)} live LinkNYC kiosks")

        # Step 3: Import locations
        print("\nStep 3: Importing locations to database...")

        stats = {
            'imported': 0,
            'skipped': 0,
            'errors': 0
        }

        for loc in locations:
            try:
                # Check if already exists
                result = await db.execute(text("""
                    SELECT id FROM service_locations
                    WHERE name = :name AND street_address = :address
                    AND deleted_at IS NULL
                """), {
                    'name': f"LinkNYC Kiosk - {loc['site_id']}",
                    'address': loc['street_address']
                })

                existing = result.fetchone()

                if existing:
                    stats['skipped'] += 1
                    continue

                # Validate coordinates (must be within NYC)
                if not loc['latitude'] or not loc['longitude']:
                    stats['skipped'] += 1
                    continue

                if loc['latitude'] < 40.4 or loc['latitude'] > 41.0:
                    stats['skipped'] += 1
                    continue

                if loc['longitude'] < -74.3 or loc['longitude'] > -73.7:
                    stats['skipped'] += 1
                    continue

                # Insert location
                result = await db.execute(text("""
                    INSERT INTO service_locations (
                        name,
                        street_address,
                        city,
                        state,
                        zip_code,
                        borough,
                        latitude,
                        longitude,
                        description,
                        data_source,
                        verified,
                        created_at,
                        updated_at
                    ) VALUES (
                        :name,
                        :address,
                        'New York',
                        'NY',
                        :zip_code,
                        :borough,
                        :latitude,
                        :longitude,
                        :description,
                        'LinkNYC Open Data',
                        true,
                        NOW(),
                        NOW()
                    )
                    RETURNING id
                """), {
                    'name': f"LinkNYC Kiosk - {loc['site_id']}",
                    'address': loc['street_address'],
                    'zip_code': loc['postcode'],
                    'borough': loc['borough'],
                    'latitude': loc['latitude'],
                    'longitude': loc['longitude'],
                    'description': f"{loc['kiosk_type']} kiosk providing free WiFi, phone calls, and device charging. Location: {loc['neighborhood'] if loc['neighborhood'] else loc['borough']}"
                })

                location_id = result.scalar()

                # Link to service type
                await db.execute(text("""
                    INSERT INTO location_services (location_id, service_type_id, created_at)
                    VALUES (:location_id, :service_type_id, NOW())
                """), {
                    'location_id': location_id,
                    'service_type_id': service_type_id
                })

                stats['imported'] += 1

                if stats['imported'] % 100 == 0:
                    print(f"  Imported {stats['imported']} locations...")

            except Exception as e:
                stats['errors'] += 1
                print(f"  ⚠ Error importing {loc['site_id']}: {str(e)}")

        # Commit all changes
        await db.commit()

        # Summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"Total locations in CSV:  {len(locations):,}")
        print(f"Successfully imported:   {stats['imported']:,}")
        print(f"Skipped (duplicates):    {stats['skipped']:,}")
        print(f"Errors:                  {stats['errors']:,}")
        print("=" * 60)
        print("\n✓ LinkNYC import complete!")

    await engine.dispose()

if __name__ == "__main__":
    print("\n📡 LinkNYC Kiosk Import Tool")
    print("This will import all live LinkNYC kiosks into the database.\n")

    response = input("Continue with import? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(import_linknyc_data())
    else:
        print("Import cancelled.")
