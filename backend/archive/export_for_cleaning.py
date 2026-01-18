"""
Export all service locations from database to CSV for cleaning.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import csv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

async def export_locations_to_csv():
    """Export all service locations to CSV."""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    output_file = Path('/home/opc/Hope/backend/all_service_locations.csv')

    async with async_session() as db:
        # Query to get all location data
        query = text("""
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
                STRING_AGG(DISTINCT st.name, ', ') as service_types,
                BOOL_OR(oh.is_24_hours) as is_24_hours
            FROM service_locations sl
            LEFT JOIN location_services ls ON sl.id = ls.location_id
            LEFT JOIN service_types st ON ls.service_type_id = st.id
            LEFT JOIN operating_hours oh ON sl.id = oh.location_id
            WHERE sl.deleted_at IS NULL
            GROUP BY sl.id
            ORDER BY sl.name
        """)

        result = await db.execute(query)
        rows = result.fetchall()

        print(f"Found {len(rows)} service locations")

        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                'ID', 'Name', 'Street Address', 'City', 'State', 'Zip Code',
                'Borough', 'Latitude', 'Longitude', 'Phone', 'Website', 'Email',
                'Description', 'Organization Name', 'Wheelchair Accessible',
                'Languages Spoken', 'Data Source', 'Verified', 'Verification Date',
                'Created At', 'Updated At', 'Service Types', 'Is 24 Hours'
            ])

            # Write data rows
            for row in rows:
                writer.writerow([
                    row.id,
                    row.name,
                    row.street_address,
                    row.city,
                    row.state,
                    row.zip_code,
                    row.borough,
                    row.latitude,
                    row.longitude,
                    row.phone,
                    row.website,
                    row.email,
                    row.description,
                    row.organization_name,
                    row.wheelchair_accessible,
                    row.languages_spoken,
                    row.data_source,
                    row.verified,
                    row.verification_date,
                    row.created_at,
                    row.updated_at,
                    row.service_types,
                    row.is_24_hours
                ])

        print(f"✓ Exported to {output_file}")
        print(f"\nColumn names for reference:")
        print("  - Name: 'Name'")
        print("  - Address: 'Street Address'")
        print("  - Zip Code: 'Zip Code'")
        print("  - Latitude: 'Latitude'")
        print("  - Longitude: 'Longitude'")
        print("  - Hours: (not exported, only 'Is 24 Hours' boolean)")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_locations_to_csv())
