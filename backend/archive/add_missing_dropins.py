"""
Add the 4 missing drop-in centers to the database.
"""

import asyncio
import uuid
from sqlalchemy import text
from app.database import AsyncSessionLocal


# The 4 missing drop-in centers
MISSING_DROPINS = [
    {
        "name": "Paul's Place",
        "address": "114 West 14th Street, New York, NY 10011",
        "latitude": 40.7379,
        "longitude": -73.9984,
        "phone": "212-229-0703",
        "description": "Safe Haven and Drop-In Center run by CUCS. Open 24/7. Located between 6th and 7th Ave."
    },
    {
        "name": "Breaking Ground 9th Ave",
        "address": "771 9th Avenue, New York, NY 10019",
        "latitude": 40.7642,
        "longitude": -73.9886,
        "phone": "311",
        "description": "Located near 52nd St. Showers, meals, and placement services. Open 24/7."
    },
    {
        "name": "QDIC (Queens Drop-In Center)",
        "address": "100-32 Atlantic Avenue, Jamaica, NY 11416",
        "latitude": 40.6923,
        "longitude": -73.8415,
        "phone": "311",
        "description": "The primary drop-in for Queens. Services include food, showers, and case management. Open 24/7."
    },
    {
        "name": "Union Hall Drop-In",
        "address": "92-32 Union Hall Street, Jamaica, NY 11433",
        "latitude": 40.7027,
        "longitude": -73.8016,
        "phone": "311",
        "description": "Additional drop-in location in Jamaica. Near York College. Open 24/7."
    }
]


async def add_missing_dropins():
    """Add the 4 missing drop-in centers."""

    async with AsyncSessionLocal() as db:
        try:
            print("=== Adding Missing Drop-In Centers ===\n")

            # Get the drop-in service type ID
            result = await db.execute(text("""
                SELECT id FROM service_types WHERE slug = 'drop-in'
            """))
            dropin_type_id = result.scalar()

            if not dropin_type_id:
                print("❌ ERROR: drop-in service type not found!")
                return

            print(f"✅ Found drop-in service type ID: {dropin_type_id}\n")

            added_count = 0

            for service in MISSING_DROPINS:
                # Check if location already exists by name
                result = await db.execute(text("""
                    SELECT id FROM service_locations
                    WHERE name = :name AND deleted_at IS NULL
                """), {"name": service["name"]})

                existing = result.scalar()

                if existing:
                    print(f"⚠️  SKIP: '{service['name']}' already exists")
                    continue

                # Insert service location
                location_id = uuid.uuid4()
                await db.execute(text("""
                    INSERT INTO service_locations (
                        id, name, street_address, latitude, longitude, phone,
                        description, city, state, verified, created_at, updated_at
                    ) VALUES (
                        :id, :name, :street_address, :latitude, :longitude, :phone,
                        :description, 'New York', 'NY', TRUE, NOW(), NOW()
                    )
                """), {
                    "id": location_id,
                    "name": service["name"],
                    "street_address": service["address"],
                    "latitude": service["latitude"],
                    "longitude": service["longitude"],
                    "phone": service["phone"],
                    "description": service["description"]
                })

                # Link to drop-in service type
                await db.execute(text("""
                    INSERT INTO location_services (location_id, service_type_id)
                    VALUES (:location_id, :service_type_id)
                """), {
                    "location_id": location_id,
                    "service_type_id": dropin_type_id
                })

                # Add 24/7 operating hours (7 days: 0=Sunday, 1=Monday, ... 6=Saturday)
                for day_num in range(7):
                    await db.execute(text("""
                        INSERT INTO operating_hours (
                            location_id, day_of_week, is_24_hours, is_closed, created_at, updated_at
                        ) VALUES (
                            :location_id, :day_of_week, TRUE, FALSE, NOW(), NOW()
                        )
                    """), {
                        "location_id": location_id,
                        "day_of_week": day_num
                    })

                print(f"✅ Added: {service['name']}")
                added_count += 1

            await db.commit()

            print(f"\n=== Verification ===")

            # Count total drop-in centers
            result = await db.execute(text("""
                SELECT COUNT(DISTINCT sl.id)
                FROM service_locations sl
                JOIN location_services ls ON sl.id = ls.location_id
                JOIN service_types st ON ls.service_type_id = st.id
                WHERE st.slug = 'drop-in' AND sl.deleted_at IS NULL
            """))
            total_dropins = result.scalar()

            print(f"Total Drop-In Centers in database: {total_dropins}")
            print(f"New locations added: {added_count}")

            print("\n=== SUCCESS ===")
            print(f"Added {added_count} missing drop-in centers")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ ERROR: {e}")
            raise


if __name__ == "__main__":
    print("Hope for NYC - Add Missing Drop-In Centers")
    print("=" * 60)
    print()
    asyncio.run(add_missing_dropins())
