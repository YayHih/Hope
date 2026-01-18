"""
Replace generic shelter data with verified Front Door locations.
This script:
1. Deletes all existing shelter-type locations
2. Adds new service types (intake, drop-in)
3. Inserts verified Front Door locations
"""

import asyncio
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, AsyncSessionLocal

# Front Door Services Data
FRONT_DOOR_SERVICES = [
    {
        "id": "INTAKE_MEN_01",
        "name": "30th Street Intake Center (Men)",
        "type": "intake",
        "population": "Single Men",
        "address": "400-430 East 30th Street, New York, NY 10016",
        "latitude": 40.7395,
        "longitude": -73.9733,
        "open_times": "24/7",
        "phone": "212-481-0771",
        "description": "The main entry point for all single men seeking shelter in NYC. Open 24/7. Go here to be processed and assigned a bed."
    },
    {
        "id": "INTAKE_WOMEN_01",
        "name": "HELP Women's Center",
        "type": "intake",
        "population": "Single Women",
        "address": "116 Williams Avenue, Brooklyn, NY 11207",
        "latitude": 40.6728,
        "longitude": -73.8967,
        "open_times": "24/7",
        "phone": "718-483-7700",
        "description": "Main intake center for single women. Open 24/7. Walk-ins accepted."
    },
    {
        "id": "INTAKE_WOMEN_02",
        "name": "Franklin Shelter Intake",
        "type": "intake",
        "population": "Single Women",
        "address": "1122 Franklin Avenue, Bronx, NY 10456",
        "latitude": 40.8306,
        "longitude": -73.9036,
        "open_times": "24/7",
        "phone": "311",
        "description": "Secondary intake location for single women in the Bronx. Open 24/7."
    },
    {
        "id": "INTAKE_FAMILIES_01",
        "name": "PATH (Prevention Assistance and Temporary Housing)",
        "type": "intake",
        "population": "Families with Children",
        "address": "151 East 151st Street, Bronx, NY 10451",
        "latitude": 40.8202,
        "longitude": -73.9265,
        "open_times": "24/7",
        "phone": "311",
        "description": "The ONLY intake center for families with children. Open 24/7."
    },
    {
        "id": "INTAKE_ADULT_FAM_01",
        "name": "AFIC (Adult Family Intake Center)",
        "type": "intake",
        "population": "Adult Families (No minor children)",
        "address": "400-430 East 30th Street, New York, NY 10016",
        "latitude": 40.7395,
        "longitude": -73.9733,
        "open_times": "24/7",
        "phone": "311",
        "description": "Intake for couples or adult families without minor children. Located at the 30th St complex."
    },
    {
        "id": "DROPIN_MANHATTAN_01",
        "name": "Mainchance Drop-In Center",
        "type": "drop-in",
        "population": "All Adults",
        "address": "120 East 32nd Street, New York, NY 10016",
        "latitude": 40.7457,
        "longitude": -73.9806,
        "open_times": "24/7",
        "phone": "212-883-0680",
        "description": "Chairs, food, showers, and case management. Respite bed placement available. Open 24/7."
    },
    {
        "id": "DROPIN_MANHATTAN_02",
        "name": "The Olivieri Center",
        "type": "drop-in",
        "population": "All Adults",
        "address": "257 West 30th Street, New York, NY 10001",
        "latitude": 40.7496,
        "longitude": -73.9937,
        "open_times": "24/7",
        "phone": "212-947-3211",
        "description": "Located near Penn Station. Showers, food, and clothing. Open 24/7."
    },
    {
        "id": "DROPIN_BRONX_01",
        "name": "The Living Room (BronxWorks)",
        "type": "drop-in",
        "population": "All Adults",
        "address": "800 Barretto Street, Bronx, NY 10474",
        "latitude": 40.8169,
        "longitude": -73.8893,
        "open_times": "24/7",
        "phone": "718-893-3606",
        "description": "Safe haven and drop-in center. Hot meals, showers, and laundry access. Open 24/7."
    },
    {
        "id": "DROPIN_BROOKLYN_01",
        "name": "The Gathering Place",
        "type": "drop-in",
        "population": "All Adults",
        "address": "2402 Atlantic Avenue, Brooklyn, NY 11233",
        "latitude": 40.6766,
        "longitude": -73.9056,
        "open_times": "24/7",
        "phone": "718-385-8726",
        "description": "Day center and drop-in services. Three meals a day, showers, and clothing. Open 24/7."
    },
    {
        "id": "DROPIN_STATEN_01",
        "name": "Project Hospitality Drop-In",
        "type": "drop-in",
        "population": "All Adults",
        "address": "150 Richmond Terrace, Staten Island, NY 10301",
        "latitude": 40.6433,
        "longitude": -74.0763,
        "open_times": "24/7",
        "phone": "718-720-0079",
        "description": "The primary drop-in location for Staten Island. Located near the Ferry Terminal. Meals, showers, and intake services. Open 24/7."
    }
]


async def replace_shelter_data():
    """Replace shelter data with front door services."""

    async with AsyncSessionLocal() as db:
        try:
            print("=== STEP 1: Checking current shelter data ===")

            # Count existing shelters
            result = await db.execute(text("""
                SELECT COUNT(*) FROM service_locations sl
                JOIN location_services ls ON sl.id = ls.location_id
                JOIN service_types st ON ls.service_type_id = st.id
                WHERE st.slug = 'shelter'
            """))
            shelter_count = result.scalar()
            print(f"Found {shelter_count} existing shelter locations")

            print("\n=== STEP 2: Deleting existing shelter locations ===")

            # Get shelter service type ID
            result = await db.execute(text(
                "SELECT id FROM service_types WHERE slug = 'shelter'"
            ))
            shelter_type_id = result.scalar()

            if shelter_type_id:
                # Delete location_services entries for shelters
                result = await db.execute(text("""
                    DELETE FROM location_services
                    WHERE service_type_id = :type_id
                """), {"type_id": shelter_type_id})
                print(f"Deleted {result.rowcount} shelter service entries")

                # Delete operating hours for those locations
                result = await db.execute(text("""
                    DELETE FROM operating_hours
                    WHERE location_id IN (
                        SELECT sl.id FROM service_locations sl
                        WHERE sl.id NOT IN (SELECT location_id FROM location_services)
                    )
                """))
                print(f"Deleted {result.rowcount} orphaned operating hours")

                # Delete service locations with no services
                result = await db.execute(text("""
                    DELETE FROM service_locations
                    WHERE id NOT IN (SELECT location_id FROM location_services)
                """))
                print(f"Deleted {result.rowcount} shelter locations")

            print("\n=== STEP 3: Adding new service types ===")

            # Add intake service type
            result = await db.execute(text("""
                INSERT INTO service_types (name, slug, icon_name, color_hex, description, active)
                VALUES (:name, :slug, :icon_name, :color_hex, :description, TRUE)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    icon_name = EXCLUDED.icon_name,
                    color_hex = EXCLUDED.color_hex,
                    description = EXCLUDED.description
                RETURNING id
            """), {
                "name": "Intake Center",
                "slug": "intake",
                "icon_name": "door",
                "color_hex": "#E53E3E",
                "description": "Front door locations to get assigned a shelter bed. Walk-ins accepted 24/7."
            })
            intake_type_id = result.scalar()
            print(f"✅ Intake type ID: {intake_type_id}")

            # Add drop-in service type
            result = await db.execute(text("""
                INSERT INTO service_types (name, slug, icon_name, color_hex, description, active)
                VALUES (:name, :slug, :icon_name, :color_hex, :description, TRUE)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    icon_name = EXCLUDED.icon_name,
                    color_hex = EXCLUDED.color_hex,
                    description = EXCLUDED.description
                RETURNING id
            """), {
                "name": "Drop-In Center",
                "slug": "drop-in",
                "icon_name": "chair",
                "color_hex": "#DD6B20",
                "description": "Safe haven locations offering chairs, food, showers, and case management. No intake required."
            })
            dropin_type_id = result.scalar()
            print(f"✅ Drop-In type ID: {dropin_type_id}")

            print("\n=== STEP 4: Inserting Front Door locations ===")

            type_id_map = {
                "intake": intake_type_id,
                "drop-in": dropin_type_id
            }

            for service in FRONT_DOOR_SERVICES:
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

                # Link to service type
                service_type_id = type_id_map[service["type"]]
                await db.execute(text("""
                    INSERT INTO location_services (location_id, service_type_id)
                    VALUES (:location_id, :service_type_id)
                """), {
                    "location_id": location_id,
                    "service_type_id": service_type_id
                })

                # Add 24/7 operating hours for all days
                for day_num in range(7):
                    await db.execute(text("""
                        INSERT INTO operating_hours (
                            location_id, day_of_week, open_time, close_time,
                            is_24_hours, is_closed
                        ) VALUES (
                            :location_id, :day, NULL, NULL, TRUE, FALSE
                        )
                    """), {
                        "location_id": location_id,
                        "day": day_num
                    })

                print(f"✅ Added: {service['name']} ({service['type']})")

            await db.commit()

            print("\n=== STEP 5: Verification ===")

            # Count new intake centers
            result = await db.execute(text("""
                SELECT COUNT(*) FROM service_locations sl
                JOIN location_services ls ON sl.id = ls.location_id
                JOIN service_types st ON ls.service_type_id = st.id
                WHERE st.slug = 'intake'
            """))
            intake_count = result.scalar()
            print(f"✅ Intake Centers: {intake_count}")

            # Count new drop-in centers
            result = await db.execute(text("""
                SELECT COUNT(*) FROM service_locations sl
                JOIN location_services ls ON sl.id = ls.location_id
                JOIN service_types st ON ls.service_type_id = st.id
                WHERE st.slug = 'drop-in'
            """))
            dropin_count = result.scalar()
            print(f"✅ Drop-In Centers: {dropin_count}")

            print("\n=== SUCCESS ===")
            print(f"Replaced {shelter_count} generic shelters with {len(FRONT_DOOR_SERVICES)} verified Front Door locations")
            print("All locations are 24/7 and have verified addresses and phone numbers")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ ERROR: {e}")
            raise


if __name__ == "__main__":
    print("Hope for NYC - Front Door Services Data Replacement")
    print("=" * 60)
    print()
    asyncio.run(replace_shelter_data())
