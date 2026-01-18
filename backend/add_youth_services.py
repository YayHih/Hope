#!/usr/bin/env python3
"""Add major Youth Services locations to the database."""

import os
import psycopg2
import uuid

# Database connection from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://hope_user:hope_password@localhost:5432/hope_db')
db_url = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
conn = psycopg2.connect(db_url)
cur = conn.cursor()

def get_service_type_id(slug):
    cur.execute("SELECT id FROM service_types WHERE slug = %s", (slug,))
    result = cur.fetchone()
    return result[0] if result else None

def add_location(name, org_name, description, address, city, state, zip_code, borough, lat, lng, phone, website, service_type_slug):
    """Add a location and link it to a service type."""
    location_id = str(uuid.uuid4())
    service_type_id = get_service_type_id(service_type_slug)

    if not service_type_id:
        print(f"  ERROR: Service type {service_type_slug} not found")
        return None

    # Check if location already exists (by name and address)
    cur.execute("""
        SELECT id FROM service_locations
        WHERE name = %s AND street_address = %s AND deleted_at IS NULL
    """, (name, address))
    existing = cur.fetchone()

    if existing:
        print(f"  Already exists: {name}")
        return existing[0]

    # Insert location
    cur.execute("""
        INSERT INTO service_locations (
            id, name, organization_name, description, street_address, city, state,
            zip_code, borough, latitude, longitude, phone, website, verified, data_source
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        location_id, name, org_name, description, address, city, state,
        zip_code, borough, lat, lng, phone, website, True, 'manual_entry'
    ))

    # Link to service type
    cur.execute("""
        INSERT INTO location_services (location_id, service_type_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (location_id, service_type_id))

    print(f"  Added: {name}")
    return location_id

print("=" * 60)
print("ADDING YOUTH SERVICES LOCATIONS")
print("=" * 60)

# 1. Ali Forney Center - Main Drop-In (Harlem)
print("\n1. Ali Forney Center (LGBTQ+ Youth)...")
add_location(
    name="Ali Forney Center - Harlem Drop-In",
    org_name="Ali Forney Center",
    description="🏳️‍🌈 LGBTQ+ YOUTH DROP-IN - Ages 16-24. Safe space, meals, showers, case management, housing assistance. Walk-in welcome.",
    address="324 W 125th St",
    city="New York",
    state="NY",
    zip_code="10027",
    borough="Manhattan",
    lat=40.8105,
    lng=-73.9521,
    phone="212-222-3427",
    website="https://aliforneycenter.org",
    service_type_slug="youth-services"
)

# 2. The Door - SoHo (Major youth hub)
print("\n2. The Door (Youth Hub)...")
add_location(
    name="The Door",
    org_name="The Door",
    description="🧑‍🤝‍🧑 YOUTH HUB - Ages 12-24. Health clinic, legal services, education, career training, food, counseling. No appointment needed for drop-in services.",
    address="555 Broome St",
    city="New York",
    state="NY",
    zip_code="10013",
    borough="Manhattan",
    lat=40.7245,
    lng=-74.0037,
    phone="212-941-9090",
    website="https://door.org",
    service_type_slug="youth-services"
)

# 3. Safe Horizon Streetwork Project - Harlem
print("\n3. Safe Horizon Streetwork - Harlem...")
add_location(
    name="Safe Horizon Streetwork Project - Harlem Drop-In",
    org_name="Safe Horizon",
    description="🧑‍🤝‍🧑 YOUTH DROP-IN - Ages 14-21. Safe space, meals, showers, clothing, case management. Walk-in welcome.",
    address="209 W 125th St",
    city="New York",
    state="NY",
    zip_code="10027",
    borough="Manhattan",
    lat=40.8093,
    lng=-73.9474,
    phone="212-695-2220",
    website="https://safehorizon.org",
    service_type_slug="youth-services"
)

# 4. Safe Horizon Streetwork Project - Lower East Side
print("\n4. Safe Horizon Streetwork - LES...")
add_location(
    name="Safe Horizon Streetwork Project - Lower East Side Drop-In",
    org_name="Safe Horizon",
    description="🧑‍🤝‍🧑 YOUTH DROP-IN - Ages 14-21. Safe space, meals, showers, clothing, case management. Walk-in welcome.",
    address="33 Essex St",
    city="New York",
    state="NY",
    zip_code="10002",
    borough="Manhattan",
    lat=40.7158,
    lng=-73.9877,
    phone="212-695-2220",
    website="https://safehorizon.org",
    service_type_slug="youth-services"
)

# 5. SCO Family of Services - Brooklyn Youth Programs
print("\n5. SCO Family of Services - Brooklyn...")
add_location(
    name="SCO Family of Services - Brooklyn Youth Center",
    org_name="SCO Family of Services",
    description="🧑‍🤝‍🧑 YOUTH SERVICES - Ages 16-24. Transitional living, education support, job training, case management for homeless youth.",
    address="1170 Bedford Ave",
    city="Brooklyn",
    state="NY",
    zip_code="11216",
    borough="Brooklyn",
    lat=40.6879,
    lng=-73.9573,
    phone="718-636-3614",
    website="https://sco.org",
    service_type_slug="youth-services"
)

# 6. Covenant House - already exists, but let's ensure it's properly tagged
print("\n6. Checking Covenant House...")
cur.execute("""
    SELECT sl.id, sl.name FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    JOIN service_types st ON ls.service_type_id = st.id
    WHERE sl.name ILIKE '%Covenant House%' AND st.slug = 'youth-services'
""")
covenant = cur.fetchone()
if covenant:
    print(f"  Covenant House already in youth-services: {covenant[1]}")
else:
    print("  Covenant House not found in youth-services, adding...")
    add_location(
        name="Covenant House New York",
        org_name="Covenant House New York",
        description="🧑‍🤝‍🧑 YOUTH SHELTER - Ages 16-24. Walk-in welcome 24/7. Safe housing, meals, counseling, education, job training for runaway and homeless youth.",
        address="460 W 41st St",
        city="New York",
        state="NY",
        zip_code="10036",
        borough="Manhattan",
        lat=40.7578,
        lng=-73.9927,
        phone="212-613-0300",
        website="https://covenanthouse.org",
        service_type_slug="youth-services"
    )

conn.commit()

# Print final count
print("\n" + "=" * 60)
print("YOUTH SERVICES LOCATIONS:")
cur.execute("""
    SELECT sl.name, sl.street_address, sl.borough
    FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    JOIN service_types st ON ls.service_type_id = st.id
    WHERE st.slug = 'youth-services' AND sl.deleted_at IS NULL
    ORDER BY sl.name
""")
for row in cur.fetchall():
    print(f"  - {row[0]} ({row[2]})")

conn.close()
print("\nDone!")
