"""
Export all service locations to CSV for verification.
Includes all location details, services, and operating hours.
"""

import asyncio
import csv
from sqlalchemy import text
from app.database import AsyncSessionLocal


async def export_locations_to_csv():
    """Export all locations to CSV file."""

    async with AsyncSessionLocal() as db:
        try:
            print("=== Exporting All Service Locations to CSV ===\n")

            # Get all locations with their services and operating hours
            result = await db.execute(text("""
                SELECT
                    sl.id,
                    sl.name,
                    sl.street_address,
                    sl.city,
                    sl.state,
                    sl.zip_code,
                    sl.borough,
                    sl.latitude,
                    sl.longitude,
                    sl.phone,
                    sl.website,
                    sl.email,
                    sl.description,
                    sl.organization_name,
                    sl.wheelchair_accessible,
                    sl.languages_spoken,
                    sl.data_source,
                    sl.verified,
                    sl.verification_date,
                    sl.created_at,
                    sl.updated_at,
                    STRING_AGG(DISTINCT st.name || ' (' || st.slug || ')', ', ') as service_types,
                    STRING_AGG(DISTINCT st.color_hex, ', ') as service_colors,
                    BOOL_OR(oh.is_24_hours) as is_24_hours,
                    COUNT(DISTINCT oh.id) as hours_count
                FROM service_locations sl
                LEFT JOIN location_services ls ON sl.id = ls.location_id
                LEFT JOIN service_types st ON ls.service_type_id = st.id
                LEFT JOIN operating_hours oh ON sl.id = oh.location_id
                WHERE sl.deleted_at IS NULL
                GROUP BY sl.id
                ORDER BY sl.name
            """))

            locations = result.fetchall()

            print(f"Found {len(locations)} active locations\n")

            # Define CSV columns
            csv_file = '/home/opc/all_service_locations.csv'

            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    'ID',
                    'Name',
                    'Street Address',
                    'City',
                    'State',
                    'Zip Code',
                    'Borough',
                    'Latitude',
                    'Longitude',
                    'Phone',
                    'Website',
                    'Email',
                    'Description',
                    'Organization Name',
                    'Wheelchair Accessible',
                    'Languages Spoken',
                    'Data Source',
                    'Verified',
                    'Verification Date',
                    'Service Types',
                    'Service Colors',
                    '24/7 Operation',
                    'Operating Hours Count',
                    'Created At',
                    'Updated At'
                ])

                # Write data rows
                for loc in locations:
                    writer.writerow([
                        str(loc[0]),  # ID
                        loc[1],  # Name
                        loc[2],  # Street Address
                        loc[3],  # City
                        loc[4],  # State
                        loc[5],  # Zip Code
                        loc[6],  # Borough
                        loc[7],  # Latitude
                        loc[8],  # Longitude
                        loc[9],  # Phone
                        loc[10],  # Website
                        loc[11],  # Email
                        loc[12],  # Description
                        loc[13],  # Organization Name
                        'Yes' if loc[14] else 'No' if loc[14] is False else 'Unknown',  # Wheelchair
                        ', '.join(loc[15]) if loc[15] else '',  # Languages
                        loc[16],  # Data Source
                        'Yes' if loc[17] else 'No',  # Verified
                        str(loc[18]) if loc[18] else '',  # Verification Date
                        loc[21],  # Service Types
                        loc[22],  # Service Colors
                        'Yes' if loc[23] else 'No',  # 24/7
                        loc[24],  # Hours Count
                        str(loc[19]),  # Created At
                        str(loc[20])   # Updated At
                    ])

            print(f"✅ CSV exported to: {csv_file}\n")

            # Print summary statistics
            print("=== Summary Statistics ===")

            # Count by service type
            result = await db.execute(text("""
                SELECT
                    st.name,
                    st.slug,
                    COUNT(DISTINCT sl.id) as location_count
                FROM service_types st
                LEFT JOIN location_services ls ON st.id = ls.service_type_id
                LEFT JOIN service_locations sl ON ls.location_id = sl.id AND sl.deleted_at IS NULL
                WHERE st.active = TRUE
                GROUP BY st.name, st.slug
                ORDER BY location_count DESC
            """))

            service_counts = result.fetchall()

            print("\nLocations by Service Type:")
            for svc in service_counts:
                print(f"  {svc[0]}: {svc[2]} locations")

            # Count by borough
            result = await db.execute(text("""
                SELECT
                    COALESCE(borough, 'Unknown') as borough,
                    COUNT(*) as count
                FROM service_locations
                WHERE deleted_at IS NULL
                GROUP BY borough
                ORDER BY count DESC
            """))

            borough_counts = result.fetchall()

            print("\nLocations by Borough:")
            for borough in borough_counts:
                print(f"  {borough[0]}: {borough[1]} locations")

            # Count verified vs unverified
            result = await db.execute(text("""
                SELECT
                    verified,
                    COUNT(*) as count
                FROM service_locations
                WHERE deleted_at IS NULL
                GROUP BY verified
            """))

            verified_counts = result.fetchall()

            print("\nVerification Status:")
            for v in verified_counts:
                status = "Verified" if v[0] else "Unverified"
                print(f"  {status}: {v[1]} locations")

            # Count 24/7 locations
            result = await db.execute(text("""
                SELECT COUNT(DISTINCT sl.id)
                FROM service_locations sl
                JOIN operating_hours oh ON sl.id = oh.location_id
                WHERE sl.deleted_at IS NULL
                AND oh.is_24_hours = TRUE
            """))

            always_open_count = result.scalar()

            print(f"\n24/7 Locations: {always_open_count}")

            print("\n=== SUCCESS ===")
            print(f"Exported {len(locations)} locations to {csv_file}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            raise


if __name__ == "__main__":
    print("Hope for NYC - Location Database Export")
    print("=" * 60)
    print()
    asyncio.run(export_locations_to_csv())
