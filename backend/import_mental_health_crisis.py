"""
Import Mental Health Crisis Resources into the Hope database.

This script imports from multiple sources:
1. NYS OMH Program Directory - Crisis/Emergency programs for NYC
2. NYC DHS Drop-in Centers - 24/7 safe haven locations

Priority is given to:
- CPEP (Comprehensive Psychiatric Emergency Programs) - 24/7 walk-in psychiatric ERs
- Mobile Crisis Teams - Teams that go to the client
- Drop-in Centers - Immediate walk-in access for rest/food
- Crisis Respite Beds - Short-term crisis housing
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
from datetime import time

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def parse_coordinates(geo_point):
    """
    Parse coordinates from POINT format.
    Example: "POINT (-73.97639 40.73984)" -> (40.73984, -73.97639)
    """
    if not geo_point or geo_point.strip() == '':
        return None, None

    match = re.search(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)', geo_point)
    if match:
        lon = float(match.group(1))
        lat = float(match.group(2))
        return lat, lon
    return None, None

def get_service_priority(subcategory, program_type):
    """
    Assign priority to help with sorting/display.
    Lower number = higher priority for first responders.
    """
    subcategory_lower = (subcategory or '').lower()
    program_type_lower = (program_type or '').lower()

    if 'cpep' in subcategory_lower or 'cpep' in program_type_lower:
        return 1  # Highest priority - 24/7 psychiatric ER
    if 'mobile crisis' in subcategory_lower or 'mobile crisis' in program_type_lower:
        return 2  # Mobile teams can come to client
    if 'home based crisis' in program_type_lower:
        return 3  # Home-based intervention
    if 'crisis' in subcategory_lower and 'respite' in program_type_lower:
        return 4  # Crisis respite beds
    if 'crisis' in subcategory_lower:
        return 5  # Other crisis services
    return 10  # Other services

def classify_service_type(subcategory, program_type):
    """
    Classify the mental health service for the description.
    """
    subcategory_lower = (subcategory or '').lower()
    program_type_lower = (program_type or '').lower()

    if 'cpep' in subcategory_lower or 'cpep' in program_type_lower:
        return "Crisis (ER)", "24/7 Psychiatric Emergency - Walk-ins accepted"
    if 'mobile crisis' in subcategory_lower or 'mobile crisis' in program_type_lower:
        return "Mobile Crisis", "Team can respond to location"
    if 'home based crisis' in program_type_lower:
        return "Home-Based Crisis", "Crisis intervention at home"
    if 'crisis' in subcategory_lower and 'respite' in program_type_lower:
        return "Crisis Respite", "Short-term crisis housing"
    if 'crisis' in subcategory_lower:
        return "Crisis Intervention", "Crisis services available"
    return "Mental Health", "Mental health services"

async def import_mental_health_resources():
    """Import mental health crisis resources into database."""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # File paths
    omh_csv = Path('/home/opc/nys_mental_health_programs.csv')
    dhs_csv = Path('/home/opc/nyc_dhs_facilities.csv')

    if not omh_csv.exists():
        print(f"❌ Error: {omh_csv} not found!")
        return

    print(f"Reading NYS OMH data from {omh_csv.name}...")

    # Read NYS OMH CSV - filter for NYC Crisis/Emergency programs
    omh_programs = []
    with open(omh_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Strip whitespace from keys (CSV has leading spaces in headers)
            row = {k.strip(): v for k, v in row.items()}

            # Filter for NYC region
            if row.get('Program Region', '') != 'New York City':
                continue

            # Filter for Emergency/Crisis category or Crisis in subcategory
            category = row.get('Program Category Description', '')
            subcategory = row.get('Program Subcategory Description', '')
            program_type = row.get('Program Type Description', '')

            is_crisis = (
                'Emergency/Crisis' in category or
                'Crisis' in subcategory or
                'CPEP' in program_type or
                'Mobile Crisis' in program_type or
                'Home Based Crisis' in program_type
            )

            if is_crisis:
                omh_programs.append(row)

    print(f"✓ Found {len(omh_programs)} NYC crisis/emergency programs\n")

    # Read DHS Drop-in Centers
    dhs_centers = []
    if dhs_csv.exists():
        with open(dhs_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dhs_centers.append(row)
        print(f"✓ Found {len(dhs_centers)} NYC Drop-in Centers\n")
    else:
        print("⚠️ DHS Drop-in CSV not found, skipping...\n")

    async with async_session() as db:
        # Step 1: Create or get the 'Mental Health Crisis' service type
        print("Step 1: Setting up service type...")

        result = await db.execute(text("""
            SELECT id FROM service_types WHERE slug = 'mental-health-crisis'
        """))
        service_type_row = result.fetchone()

        if service_type_row:
            service_type_id = service_type_row.id
            print(f"  ✓ Found existing service type (ID: {service_type_id})")
        else:
            # Create the service type
            result = await db.execute(text("""
                INSERT INTO service_types (name, slug, description, icon_name, color_hex, sort_order, active)
                VALUES ('Mental Health Crisis', 'mental-health-crisis',
                        'Psychiatric emergency rooms, mobile crisis teams, crisis respite beds, and drop-in centers',
                        'brain', '#E91E63', 5, true)
                RETURNING id
            """))
            service_type_id = result.fetchone().id
            await db.commit()
            print(f"  ✓ Created new service type (ID: {service_type_id})")

        # Step 2: Import NYS OMH Crisis Programs
        print("\nStep 2: Importing NYS OMH crisis programs...")

        stats = {
            'omh_imported': 0,
            'omh_skipped_no_coords': 0,
            'omh_skipped_no_address': 0,
            'omh_duplicates': 0,
            'dhs_imported': 0,
            'dhs_duplicates': 0,
            'cpep_count': 0,
            'mobile_crisis_count': 0,
        }

        for row in omh_programs:
            # Parse coordinates
            geo_point = row.get('Georeference', '')
            lat, lon = parse_coordinates(geo_point)

            # Skip if no valid coordinates (many NYS records have placeholder coords)
            if not lat or not lon or abs(lat - 42.65155) < 0.001:  # Albany placeholder
                # Try to use address for geocoding later
                address = row.get('Program Address 1', '').strip()
                city = row.get('Program City', '').strip()

                if not address or not city:
                    stats['omh_skipped_no_address'] += 1
                    continue

                # For now, skip records without valid NYC coordinates
                stats['omh_skipped_no_coords'] += 1
                continue

            # Skip coordinates outside NYC bounds
            if lat < 40.4 or lat > 41.0 or lon < -74.3 or lon > -73.6:
                stats['omh_skipped_no_coords'] += 1
                continue

            # Get program details
            program_name = row.get('Program Name', '').strip()
            facility_name = row.get('Facility Name', '').strip()
            agency_name = row.get('Agency Name', '').strip()

            # Use program name, or facility name if program name is generic
            name = program_name
            if not name or name == facility_name:
                name = facility_name

            if not name:
                continue

            # Build address
            address1 = row.get('Program Address 1', '').strip()
            address2 = row.get('Program Address 2', '').strip()
            city = row.get('Program City', '').strip()
            state = row.get('Program State', '').strip()
            zip_code = row.get('Program Zip', '').strip()

            street_address = address1
            if address2:
                street_address = f"{address1}, {address2}"

            # Get phone numbers
            agency_phone = row.get('Agency Phone', '').strip()
            program_phone = row.get('Program Phone', '').strip()
            phone = program_phone if program_phone and program_phone != 'Not Available' else agency_phone
            if phone == 'Not Available':
                phone = None

            # Classify service type
            subcategory = row.get('Program Subcategory Description', '')
            program_type = row.get('Program Type Description', '')
            service_label, service_desc = classify_service_type(subcategory, program_type)

            # Track CPEP and Mobile Crisis counts
            if 'CPEP' in program_type or 'CPEP' in subcategory:
                stats['cpep_count'] += 1
            if 'Mobile Crisis' in program_type:
                stats['mobile_crisis_count'] += 1

            # Build description
            populations = row.get('Populations Served', '').strip()
            description_parts = [service_desc]
            if populations:
                description_parts.append(f"Serves: {populations}")
            if agency_name and agency_name != facility_name:
                description_parts.append(f"Operated by: {agency_name}")

            description = ' • '.join(description_parts)

            # Check for duplicates
            dup_check = await db.execute(text("""
                SELECT id FROM service_locations
                WHERE name = :name
                  AND ABS(latitude - :lat) < 0.0005
                  AND ABS(longitude - :lon) < 0.0005
                  AND deleted_at IS NULL
            """), {'name': name, 'lat': lat, 'lon': lon})

            if dup_check.fetchone():
                stats['omh_duplicates'] += 1
                continue

            # Insert location
            result = await db.execute(text("""
                INSERT INTO service_locations
                (name, description, organization_name, street_address, city, state, zip_code,
                 latitude, longitude, phone, data_source, verified, borough)
                VALUES (:name, :description, :org_name, :street_address, :city, :state, :zip_code,
                        :lat, :lon, :phone, 'NYS OMH Program Directory', false,
                        CASE
                            WHEN :county = 'New York' THEN 'Manhattan'
                            WHEN :county = 'Kings' THEN 'Brooklyn'
                            WHEN :county = 'Richmond' THEN 'Staten Island'
                            ELSE :county
                        END)
                RETURNING id
            """), {
                'name': name,
                'description': description,
                'org_name': agency_name if agency_name else None,
                'street_address': street_address if street_address else None,
                'city': city if city else None,
                'state': state if state else 'NY',
                'zip_code': zip_code if zip_code else None,
                'lat': lat,
                'lon': lon,
                'phone': phone,
                'county': row.get('Program County', '')
            })

            location_id = result.fetchone().id

            # Link to service type
            await db.execute(text("""
                INSERT INTO location_services (location_id, service_type_id)
                VALUES (:location_id, :service_type_id)
            """), {'location_id': location_id, 'service_type_id': service_type_id})

            # Add 24/7 hours for CPEP programs
            if 'CPEP' in program_type or 'CPEP' in subcategory:
                for day in range(7):  # 0=Sunday through 6=Saturday
                    await db.execute(text("""
                        INSERT INTO operating_hours
                        (location_id, day_of_week, is_24_hours, is_closed)
                        VALUES (:location_id, :day, true, false)
                    """), {'location_id': location_id, 'day': day})

            stats['omh_imported'] += 1

            if stats['omh_imported'] % 10 == 0:
                await db.commit()
                print(f"  Progress: {stats['omh_imported']} OMH programs imported...")

        await db.commit()
        print(f"  ✓ Imported {stats['omh_imported']} OMH crisis programs")

        # Step 3: Import DHS Drop-in Centers
        print("\nStep 3: Importing DHS Drop-in Centers...")

        for row in dhs_centers:
            name = row.get('Center Name', '').strip()
            if not name:
                continue

            try:
                lat = float(row.get('Latitude', 0))
                lon = float(row.get('Longitude', 0))
            except (ValueError, TypeError):
                continue

            if lat == 0 or lon == 0:
                continue

            # Parse address
            full_address = row.get('Address', '').strip()
            # Extract street address (before semicolon)
            street_address = full_address.split(';')[0].strip() if full_address else None

            borough = row.get('Borough', '').strip()
            zip_code = row.get('Postcode', '').strip()
            comments = row.get('Comments', '').strip()

            # Build description
            description = "Drop-in Center - Safe haven for rest, food, and services"
            if comments:
                description = f"{description} • {comments}"

            # Check for duplicates
            dup_check = await db.execute(text("""
                SELECT id FROM service_locations
                WHERE name = :name
                  AND ABS(latitude - :lat) < 0.0005
                  AND ABS(longitude - :lon) < 0.0005
                  AND deleted_at IS NULL
            """), {'name': name, 'lat': lat, 'lon': lon})

            if dup_check.fetchone():
                stats['dhs_duplicates'] += 1
                continue

            # Insert location
            result = await db.execute(text("""
                INSERT INTO service_locations
                (name, description, street_address, borough, zip_code,
                 latitude, longitude, data_source, verified)
                VALUES (:name, :description, :street_address, :borough, :zip_code,
                        :lat, :lon, 'NYC DHS Drop-in Centers', false)
                RETURNING id
            """), {
                'name': name,
                'description': description,
                'street_address': street_address,
                'borough': borough,
                'zip_code': zip_code,
                'lat': lat,
                'lon': lon
            })

            location_id = result.fetchone().id

            # Link to service type
            await db.execute(text("""
                INSERT INTO location_services (location_id, service_type_id)
                VALUES (:location_id, :service_type_id)
            """), {'location_id': location_id, 'service_type_id': service_type_id})

            # Add 24/7 hours if mentioned in comments
            if '24 hours' in comments.lower() or '24/7' in comments.lower():
                for day in range(7):
                    await db.execute(text("""
                        INSERT INTO operating_hours
                        (location_id, day_of_week, is_24_hours, is_closed)
                        VALUES (:location_id, :day, true, false)
                    """), {'location_id': location_id, 'day': day})

            stats['dhs_imported'] += 1

        await db.commit()
        print(f"  ✓ Imported {stats['dhs_imported']} DHS Drop-in Centers")

        # Summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"\nNYS OMH Crisis Programs:")
        print(f"  Successfully imported:        {stats['omh_imported']:,}")
        print(f"    - CPEP (Psych ER):          {stats['cpep_count']:,}")
        print(f"    - Mobile Crisis Teams:      {stats['mobile_crisis_count']:,}")
        print(f"  Skipped (no coordinates):     {stats['omh_skipped_no_coords']:,}")
        print(f"  Skipped (no address):         {stats['omh_skipped_no_address']:,}")
        print(f"  Skipped (duplicates):         {stats['omh_duplicates']:,}")
        print(f"\nNYC DHS Drop-in Centers:")
        print(f"  Successfully imported:        {stats['dhs_imported']:,}")
        print(f"  Skipped (duplicates):         {stats['dhs_duplicates']:,}")
        print(f"\nTOTAL LOCATIONS:               {stats['omh_imported'] + stats['dhs_imported']:,}")
        print("=" * 60)
        print("\n✓ Import complete!")

    await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("IMPORTING MENTAL HEALTH CRISIS RESOURCES")
    print("=" * 60)
    print("This script will import:")
    print("  1. NYS OMH Crisis/Emergency Programs (NYC)")
    print("     - CPEP (Comprehensive Psychiatric Emergency Programs)")
    print("     - Mobile Crisis Teams")
    print("     - Crisis Respite Beds")
    print("  2. NYC DHS Drop-in Centers")
    print("=" * 60)

    response = input("\nContinue with import? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(import_mental_health_resources())
    else:
        print("Import cancelled.")
