#!/usr/bin/env python3
"""Import NYS hospitals from Health Data NY, filtering for NYC hospitals only."""

import csv
import os
import psycopg2
import uuid
from difflib import SequenceMatcher

# Database connection from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://hope_user:hope_password@localhost:5432/hope_db')
db_url = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
conn = psycopg2.connect(db_url)
cur = conn.cursor()

def get_service_type_id(slug):
    cur.execute("SELECT id FROM service_types WHERE slug = %s", (slug,))
    result = cur.fetchone()
    return result[0] if result else None

def similar(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_name(name):
    """Normalize hospital name for comparison."""
    # Remove common suffixes/prefixes
    name = name.lower()
    for term in ['hospital', 'center', 'medical', 'inc', 'llc', 'corp', 'the', '-', '&', 'and']:
        name = name.replace(term, ' ')
    return ' '.join(name.split())  # Normalize whitespace

def check_duplicate(name, address, zip_code):
    """Check if a similar hospital already exists."""
    # Check exact name match
    cur.execute("""
        SELECT sl.id, sl.name, sl.street_address FROM service_locations sl
        JOIN location_services ls ON sl.id = ls.location_id
        JOIN service_types st ON ls.service_type_id = st.id
        WHERE st.slug = 'hospitals' AND sl.deleted_at IS NULL
    """)
    existing = cur.fetchall()

    normalized_new = normalize_name(name)

    for loc_id, existing_name, existing_address in existing:
        normalized_existing = normalize_name(existing_name)

        # Exact name match
        if normalized_new == normalized_existing:
            return True, existing_name

        # High similarity (>80%)
        if similar(normalized_new, normalized_existing) > 0.80:
            return True, existing_name

        # Same zip code and partial name match
        if existing_address and zip_code:
            if zip_code in (existing_address or '') and similar(normalized_new, normalized_existing) > 0.5:
                return True, existing_name

    return False, None

# Read the raw CSV
print("=" * 60)
print("IMPORTING NYS HOSPITALS FOR NYC")
print("=" * 60)

hospitals_to_add = []
skipped_duplicates = []
skipped_non_hospital = []
skipped_non_nyc = []

# NYC counties in NYS data
NYC_COUNTIES = ['Bronx', 'Kings', 'New York', 'Queens', 'Richmond']
COUNTY_TO_BOROUGH = {
    'Bronx': 'Bronx',
    'Kings': 'Brooklyn',
    'New York': 'Manhattan',
    'Queens': 'Queens',
    'Richmond': 'Staten Island'
}

with open('nys_health_facilities_raw.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for row in reader:
        # Filter: Only Hospitals (not DTCs, nursing homes, etc.)
        if row['Short Description'] != 'HOSP':
            skipped_non_hospital.append(row['Facility Name'])
            continue

        # Filter: Only NYC counties
        county = row['Facility County']
        if county not in NYC_COUNTIES:
            skipped_non_nyc.append(row['Facility Name'])
            continue

        # Check for duplicates
        is_dup, existing_name = check_duplicate(
            row['Facility Name'],
            row['Facility Address 1'],
            row['Facility Zip Code']
        )

        if is_dup:
            skipped_duplicates.append((row['Facility Name'], existing_name))
            continue

        # Add to list
        hospitals_to_add.append({
            'name': row['Facility Name'],
            'address': row['Facility Address 1'],
            'city': row['Facility City'],
            'state': row['Facility State'],
            'zip': row['Facility Zip Code'],
            'borough': COUNTY_TO_BOROUGH[county],
            'phone': row['Facility Phone Number'],
            'website': row['Facility Website'] if row['Facility Website'] else None,
            'lat': float(row['Facility Latitude']) if row['Facility Latitude'] else None,
            'lng': float(row['Facility Longitude']) if row['Facility Longitude'] else None,
            'operator': row['Operator Name'],
        })

print(f"\nFiltering Results:")
print(f"  - Skipped (not hospitals): {len(skipped_non_hospital)}")
print(f"  - Skipped (not NYC): {len(skipped_non_nyc)}")
print(f"  - Skipped (duplicates): {len(skipped_duplicates)}")
print(f"  - New hospitals to add: {len(hospitals_to_add)}")

# Show duplicates that were skipped
if skipped_duplicates:
    print("\nSkipped Duplicates:")
    for new_name, existing_name in skipped_duplicates[:15]:
        print(f"  '{new_name}' matches '{existing_name}'")
    if len(skipped_duplicates) > 15:
        print(f"  ... and {len(skipped_duplicates) - 15} more")

# Show hospitals to add
print("\n" + "=" * 60)
print("HOSPITALS TO ADD:")
print("=" * 60)
for h in hospitals_to_add:
    print(f"  - {h['name']} ({h['borough']})")
    print(f"    {h['address']}, {h['city']} {h['zip']}")

# Confirm and add
if hospitals_to_add:
    print("\n" + "=" * 60)
    print("ADDING NEW HOSPITALS...")
    print("=" * 60)

    service_type_id = get_service_type_id('hospitals')
    added = 0

    for h in hospitals_to_add:
        # Skip if no coordinates
        if not h['lat'] or not h['lng']:
            print(f"  Skipping {h['name']} - no coordinates")
            continue

        location_id = str(uuid.uuid4())

        # Determine if it's an HHC hospital
        is_hhc = 'NYC Health' in h['name'] or 'H+H' in h['name']
        org_name = 'NYC Health + Hospitals (Public)' if is_hhc else 'NYC Hospital'
        description = '🏥 PUBLIC SAFETY-NET HOSPITAL - Serves all patients regardless of ability to pay. Social workers on-site. Walk-in emergency care.' if is_hhc else 'Major hospital facility providing emergency and medical services. Open 24/7.'

        # Format phone
        phone = h['phone']
        if phone and len(phone) == 10:
            phone = f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

        try:
            # State must be 2 chars
            state = 'NY'

            cur.execute("""
                INSERT INTO service_locations (
                    id, name, organization_name, description, street_address, city, state,
                    zip_code, borough, latitude, longitude, phone, website, verified, data_source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                location_id, h['name'], org_name, description, h['address'], h['city'], state,
                h['zip'], h['borough'], h['lat'], h['lng'], phone, h['website'], True, 'nys_health_data'
            ))

            cur.execute("""
                INSERT INTO location_services (location_id, service_type_id)
                VALUES (%s, %s)
            """, (location_id, service_type_id))

            print(f"  Added: {h['name']}")
            added += 1

        except Exception as e:
            print(f"  Error adding {h['name']}: {e}")
            conn.rollback()

    conn.commit()
    print(f"\nTotal added: {added}")

# Final count
print("\n" + "=" * 60)
print("FINAL HOSPITAL COUNT:")
cur.execute("""
    SELECT COUNT(*) FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    JOIN service_types st ON ls.service_type_id = st.id
    WHERE st.slug = 'hospitals' AND sl.deleted_at IS NULL
""")
print(f"  Total hospitals in database: {cur.fetchone()[0]}")

conn.close()
print("\nDone!")
