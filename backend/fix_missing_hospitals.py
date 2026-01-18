#!/usr/bin/env python3
"""Fix missing major hospitals that have legacy names in NYS dataset."""

import csv
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

def hospital_exists(name):
    """Check if hospital exists by name (fuzzy)."""
    cur.execute("""
        SELECT sl.id, sl.name FROM service_locations sl
        JOIN location_services ls ON sl.id = ls.location_id
        JOIN service_types st ON ls.service_type_id = st.id
        WHERE st.slug = 'hospitals' AND sl.deleted_at IS NULL
          AND (sl.name ILIKE %s OR sl.name ILIKE %s)
    """, (f'%{name}%', name))
    return cur.fetchone()

def add_hospital(name, address, city, zip_code, borough, lat, lng, phone, org_name='NYC Hospital'):
    """Add a hospital to the database."""
    location_id = str(uuid.uuid4())
    service_type_id = get_service_type_id('hospitals')

    description = 'Major hospital facility providing emergency and medical services. Open 24/7.'

    cur.execute("""
        INSERT INTO service_locations (
            id, name, organization_name, description, street_address, city, state,
            zip_code, borough, latitude, longitude, phone, verified, data_source
        ) VALUES (%s, %s, %s, %s, %s, %s, 'NY', %s, %s, %s, %s, %s, TRUE, 'manual_entry')
    """, (location_id, name, org_name, description, address, city, zip_code, borough, lat, lng, phone))

    cur.execute("""
        INSERT INTO location_services (location_id, service_type_id) VALUES (%s, %s)
    """, (location_id, service_type_id))

    return location_id

# Legacy name mappings: (search_terms, modern_name, address, city, zip, borough, lat, lng, phone)
LEGACY_MAPPINGS = [
    {
        'search_terms': ["St. Luke's-Roosevelt", "St Luke's Roosevelt", "Roosevelt Hospital"],
        'modern_name': "Mount Sinai West",
        'address': "1000 10th Ave",
        'city': "New York",
        'zip': "10019",
        'borough': "Manhattan",
        'lat': 40.7697,
        'lng': -73.9878,
        'phone': "212-523-4000"
    },
    {
        'search_terms': ["St. Luke's Hospital", "St Luke's", "St. Luke's-Roosevelt - St. Luke's"],
        'modern_name': "Mount Sinai Morningside",
        'address': "1111 Amsterdam Ave",
        'city': "New York",
        'zip': "10025",
        'borough': "Manhattan",
        'lat': 40.8049,
        'lng': -73.9622,
        'phone': "212-523-4000"
    },
    {
        'search_terms': ["New York Downtown Hospital", "Beekman Downtown", "NY Downtown"],
        'modern_name': "NewYork-Presbyterian Lower Manhattan Hospital",
        'address': "170 William St",
        'city': "New York",
        'zip': "10038",
        'borough': "Manhattan",
        'lat': 40.7098,
        'lng': -74.0066,
        'phone': "212-312-5000"
    },
    {
        'search_terms': ["Lutheran Medical Center", "Lutheran Medical"],
        'modern_name': "NYU Langone Hospital - Brooklyn",
        'address': "150 55th St",
        'city': "Brooklyn",
        'zip': "11220",
        'borough': "Brooklyn",
        'lat': 40.6420,
        'lng': -74.0098,
        'phone': "718-630-7000"
    },
    {
        'search_terms': ["New York Methodist", "NY Methodist", "Methodist Hospital Brooklyn"],
        'modern_name': "NewYork-Presbyterian Brooklyn Methodist Hospital",
        'address': "506 6th St",
        'city': "Brooklyn",
        'zip': "11215",
        'borough': "Brooklyn",
        'lat': 40.6718,
        'lng': -73.9814,
        'phone': "718-780-3000"
    },
    {
        'search_terms': ["Beth Israel Medical Center", "Beth Israel"],
        'modern_name': "Mount Sinai Beth Israel",
        'address': "281 1st Ave",
        'city': "New York",
        'zip': "10003",
        'borough': "Manhattan",
        'lat': 40.7312,
        'lng': -73.9842,
        'phone': "212-420-2000"
    },
    {
        'search_terms': ["Wyckoff Heights"],
        'modern_name': "Wyckoff Heights Medical Center",
        'address': "374 Stockholm St",
        'city': "Brooklyn",
        'zip': "11237",
        'borough': "Brooklyn",
        'lat': 40.7042,
        'lng': -73.9138,
        'phone': "718-963-7272"
    },
    {
        'search_terms': ["Coney Island Hospital"],
        'modern_name': "NYC Health + Hospitals/Coney Island",
        'address': "2601 Ocean Pkwy",
        'city': "Brooklyn",
        'zip': "11235",
        'borough': "Brooklyn",
        'lat': 40.5783,
        'lng': -73.9632,
        'phone': "718-616-3000"
    },
]

print("=" * 60)
print("FIXING MISSING MAJOR HOSPITALS (Legacy Names)")
print("=" * 60)

# First, scan the NYS CSV for legacy names
print("\n1. Scanning NYS dataset for legacy names...")
found_in_csv = {}

try:
    with open('nys_health_facilities_raw.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Short Description'] != 'HOSP':
                continue
            if row['Facility County'] not in ['Bronx', 'Kings', 'New York', 'Queens', 'Richmond']:
                continue

            name = row['Facility Name']
            for mapping in LEGACY_MAPPINGS:
                for search_term in mapping['search_terms']:
                    if search_term.lower() in name.lower():
                        found_in_csv[mapping['modern_name']] = {
                            'legacy_name': name,
                            'lat': float(row['Facility Latitude']) if row['Facility Latitude'] else mapping['lat'],
                            'lng': float(row['Facility Longitude']) if row['Facility Longitude'] else mapping['lng'],
                            'phone': row['Facility Phone Number'] or mapping['phone'],
                            'address': row['Facility Address 1'] or mapping['address'],
                        }
                        print(f"  Found: '{name}' -> '{mapping['modern_name']}'")
                        break
except FileNotFoundError:
    print("  NYS CSV not found, will use hard-coded values")

# Now check which ones we need to add
print("\n2. Checking which hospitals need to be added...")
added = []
skipped = []

for mapping in LEGACY_MAPPINGS:
    modern_name = mapping['modern_name']

    # Check if already exists
    existing = hospital_exists(modern_name)
    if existing:
        skipped.append((modern_name, existing[1]))
        continue

    # Also check legacy names
    legacy_exists = False
    for search_term in mapping['search_terms']:
        existing = hospital_exists(search_term)
        if existing:
            legacy_exists = True
            skipped.append((modern_name, f"legacy: {existing[1]}"))
            break

    if legacy_exists:
        continue

    # Get data from CSV if found, otherwise use hard-coded
    if modern_name in found_in_csv:
        data = found_in_csv[modern_name]
        lat = data['lat']
        lng = data['lng']
        phone = data['phone']
        address = data['address']
    else:
        lat = mapping['lat']
        lng = mapping['lng']
        phone = mapping['phone']
        address = mapping['address']

    # Format phone
    if phone and len(phone) == 10 and '-' not in phone:
        phone = f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

    # Add the hospital
    print(f"  Adding: {modern_name}")
    add_hospital(
        name=modern_name,
        address=address,
        city=mapping['city'],
        zip_code=mapping['zip'],
        borough=mapping['borough'],
        lat=lat,
        lng=lng,
        phone=phone
    )
    added.append(modern_name)

conn.commit()

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"\nAdded ({len(added)}):")
for name in added:
    print(f"  + {name}")

print(f"\nSkipped - already exists ({len(skipped)}):")
for modern, existing in skipped:
    print(f"  - {modern} (exists as: {existing})")

# Final hospital count
cur.execute("""
    SELECT COUNT(*) FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    JOIN service_types st ON ls.service_type_id = st.id
    WHERE st.slug = 'hospitals' AND sl.deleted_at IS NULL
""")
print(f"\nTotal hospitals in database: {cur.fetchone()[0]}")

# List all Mount Sinai hospitals
print("\n" + "=" * 60)
print("MOUNT SINAI NETWORK:")
cur.execute("""
    SELECT sl.name, sl.street_address, sl.borough FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    JOIN service_types st ON ls.service_type_id = st.id
    WHERE st.slug = 'hospitals' AND sl.deleted_at IS NULL
      AND sl.name ILIKE '%Mount Sinai%'
    ORDER BY sl.name
""")
for row in cur.fetchall():
    print(f"  - {row[0]} ({row[2]})")

# List all NYP hospitals
print("\n" + "=" * 60)
print("NEWYORK-PRESBYTERIAN NETWORK:")
cur.execute("""
    SELECT sl.name, sl.street_address, sl.borough FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    JOIN service_types st ON ls.service_type_id = st.id
    WHERE st.slug = 'hospitals' AND sl.deleted_at IS NULL
      AND (sl.name ILIKE '%Presbyterian%' OR sl.name ILIKE '%NYP%')
    ORDER BY sl.name
""")
for row in cur.fetchall():
    print(f"  - {row[0]} ({row[2]})")

conn.close()
print("\nDone!")
