#!/usr/bin/env python3
"""Fix mislabeled Case Management entries by recategorizing them."""

import os
import psycopg2

# Database connection from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://hope_user:hope_password@localhost:5432/hope_db')
db_url = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
conn = psycopg2.connect(db_url)
cur = conn.cursor()

def get_service_type_id(slug):
    """Get service type ID by slug."""
    cur.execute("SELECT id FROM service_types WHERE slug = %s", (slug,))
    result = cur.fetchone()
    return result[0] if result else None

def move_location_to_service(location_id, from_slug, to_slug):
    """Move a location from one service type to another."""
    from_id = get_service_type_id(from_slug)
    to_id = get_service_type_id(to_slug)

    if not from_id or not to_id:
        print(f"  ERROR: Could not find service types {from_slug} or {to_slug}")
        return False

    # Check if already has the target service
    cur.execute("""
        SELECT 1 FROM location_services
        WHERE location_id = %s AND service_type_id = %s
    """, (location_id, to_id))

    if cur.fetchone():
        # Already has target service, just remove from source
        cur.execute("""
            DELETE FROM location_services
            WHERE location_id = %s AND service_type_id = %s
        """, (location_id, from_id))
    else:
        # Update the service type
        cur.execute("""
            UPDATE location_services
            SET service_type_id = %s
            WHERE location_id = %s AND service_type_id = %s
        """, (to_id, location_id, from_id))

    return True

def recategorize_by_name_pattern(pattern, from_slug, to_slug, description_filter=None):
    """Recategorize locations matching a name pattern."""
    from_id = get_service_type_id(from_slug)

    query = """
        SELECT sl.id, sl.name, sl.description
        FROM service_locations sl
        JOIN location_services ls ON sl.id = ls.location_id
        WHERE ls.service_type_id = %s
          AND sl.deleted_at IS NULL
          AND sl.name ILIKE %s
    """
    cur.execute(query, (from_id, pattern))
    rows = cur.fetchall()

    count = 0
    for row in rows:
        loc_id, name, desc = row

        # Apply description filter if provided
        if description_filter:
            if desc and description_filter.lower() not in desc.lower():
                continue

        print(f"  Moving: {name}")
        if move_location_to_service(loc_id, from_slug, to_slug):
            count += 1

    return count

def recategorize_by_ids(ids, from_slug, to_slug):
    """Recategorize specific locations by ID."""
    count = 0
    for loc_id in ids:
        cur.execute("SELECT name FROM service_locations WHERE id = %s", (loc_id,))
        result = cur.fetchone()
        if result:
            print(f"  Moving: {result[0]}")
            if move_location_to_service(loc_id, from_slug, to_slug):
                count += 1
    return count

def get_locations_by_pattern(pattern, service_slug):
    """Get location IDs matching a pattern."""
    service_id = get_service_type_id(service_slug)
    cur.execute("""
        SELECT sl.id, sl.name
        FROM service_locations sl
        JOIN location_services ls ON sl.id = ls.location_id
        WHERE ls.service_type_id = %s
          AND sl.deleted_at IS NULL
          AND sl.name ILIKE %s
    """, (service_id, pattern))
    return cur.fetchall()

print("=" * 60)
print("FIXING CASE MANAGEMENT MISLABELED ENTRIES")
print("=" * 60)

# 1. Move Food Pantries to 'food'
print("\n1. Moving Food Pantries to 'food'...")
food_patterns = [
    '%Food Pantry%',
    '%Food Bank%',
    '%Kitchen%',
    '%Pantry%',
    '%Hunger%',
]
total_food = 0
for pattern in food_patterns:
    total_food += recategorize_by_name_pattern(pattern, 'social', 'food')
print(f"   Total moved to food: {total_food}")

# 2. Move Drop-In Centers to 'drop-in'
print("\n2. Moving Drop-In Centers to 'drop-in'...")
drop_in_locations = [
    '9a920338-2164-45f9-8f97-0b7f95b69f08',  # Living Room
    'a38919fb-e258-4fcd-a8fc-b31e794acf34',  # Main chance
    '897e857f-dd85-4125-8cee-c460212073eb',  # Olivieri
    'c6a74761-cb38-42c7-a240-362dc5491785',  # The Gathering Place
    'e0eaf0a7-c6a0-400f-8b7d-32c74c1d5e90',  # Project Hospitality (drop-in)
    'fbaa4912-6c32-46df-a309-b3500be6ad4a',  # Breaking Ground - Times Square (drop-in)
]
total_dropin = recategorize_by_ids(drop_in_locations, 'social', 'drop-in')
print(f"   Total moved to drop-in: {total_dropin}")

# 3. Move SNAP Centers and HRA to 'benefits-id'
print("\n3. Moving SNAP Centers and HRA Benefits to 'benefits-id'...")
total_benefits = 0
total_benefits += recategorize_by_name_pattern('%SNAP Center%', 'social', 'benefits-id')
total_benefits += recategorize_by_name_pattern('%HRA Benefits%', 'social', 'benefits-id')
print(f"   Total moved to benefits-id: {total_benefits}")

# 4. Move Homebase offices to appropriate category
# Homebase provides homeless prevention - case management is appropriate, but let's update descriptions
print("\n4. Updating Homebase descriptions (keeping in Case Management)...")
cur.execute("""
    UPDATE service_locations
    SET description = '📋 HOMEBASE - Homeless prevention services. ' || COALESCE(description, '')
    WHERE name ILIKE '%Homebase%'
      OR organization_name ILIKE '%Homebase%'
""")
homebase_count = cur.rowcount
print(f"   Updated {homebase_count} Homebase locations")

# 5. Move Shelters to 'shelter'
print("\n5. Moving Shelters to 'shelter'...")
shelter_patterns = [
    '%Shelter%',
    '%Residence%',
    '%Safe Haven%',
]
# First, check if shelter type exists
shelter_id = get_service_type_id('shelter')
if shelter_id:
    total_shelter = 0
    for pattern in shelter_patterns:
        total_shelter += recategorize_by_name_pattern(pattern, 'social', 'shelter')
    print(f"   Total moved to shelter: {total_shelter}")
else:
    print("   Shelter service type not found, skipping")

# 6. Move youth services
print("\n6. Moving Youth Services...")
youth_locations = [
    'b97dbbd4-0954-4859-b803-f98fc9e1a05d',  # Covenant House New York
]
total_youth = recategorize_by_ids(youth_locations, 'social', 'youth-services')
print(f"   Total moved to youth-services: {total_youth}")

# 7. NYC Relief Mobile Buses - these provide food and services, keep in case management but update description
print("\n7. Updating NYC Relief Mobile Bus descriptions...")
cur.execute("""
    UPDATE service_locations
    SET description = '🚌 MOBILE OUTREACH - ' || COALESCE(description, '')
    WHERE name ILIKE '%NYC Relief Mobile Bus%'
      AND description NOT LIKE '%MOBILE OUTREACH%'
""")
mobile_count = cur.rowcount
print(f"   Updated {mobile_count} mobile bus locations")

# Commit all changes
conn.commit()

# Print summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

# Count remaining in each category
print("\nFinal counts by service type:")
cur.execute("""
    SELECT st.name, st.slug, COUNT(ls.location_id) as count
    FROM service_types st
    LEFT JOIN location_services ls ON st.id = ls.service_type_id
    LEFT JOIN service_locations sl ON ls.location_id = sl.id AND sl.deleted_at IS NULL
    GROUP BY st.id, st.name, st.slug
    ORDER BY count DESC
""")
for row in cur.fetchall():
    print(f"  {row[0]:<25} ({row[1]:<20}): {row[2]}")

conn.close()
print("\nDone!")
