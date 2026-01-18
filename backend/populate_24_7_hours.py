#!/usr/bin/env python3
"""
Populate operating hours for locations that are always open (24/7).
Carefully targets specific categories to avoid mislabeling.
"""

import os
import psycopg2

# Database connection from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://hope_user:hope_password@localhost:5432/hope_db')

# Parse DATABASE_URL for psycopg2 (it expects individual params, not a URL with +asyncpg)
# Handle both formats: postgresql+asyncpg://... and postgresql://...
db_url = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
conn = psycopg2.connect(db_url)
cur = conn.cursor()

def get_service_type_id(slug):
    """Get service type ID by slug."""
    cur.execute("SELECT id FROM service_types WHERE slug = %s", (slug,))
    result = cur.fetchone()
    return result[0] if result else None

def location_has_hours(location_id):
    """Check if a location already has operating hours."""
    cur.execute("""
        SELECT COUNT(*) FROM operating_hours WHERE location_id = %s
    """, (location_id,))
    return cur.fetchone()[0] > 0

def add_24_7_hours(location_id, service_type_id, notes="Open 24/7"):
    """Add 24/7 hours for all 7 days of the week."""
    for day in range(7):  # 0=Sunday through 6=Saturday
        cur.execute("""
            INSERT INTO operating_hours (location_id, service_type_id, day_of_week, is_24_hours, is_closed, notes)
            VALUES (%s, %s, %s, TRUE, FALSE, %s)
        """, (location_id, service_type_id, day, notes))

print("=" * 60)
print("POPULATING 24/7 OPERATING HOURS")
print("=" * 60)

# Track statistics
stats = {
    'hospitals': {'checked': 0, 'updated': 0, 'skipped': 0},
    'linknyc': {'checked': 0, 'updated': 0, 'skipped': 0, 'library_skipped': 0},
    'cpep': {'checked': 0, 'updated': 0, 'skipped': 0},
}

# =============================================================================
# 1. HOSPITALS - All hospitals have 24/7 ER
# =============================================================================
print("\n1. Processing HOSPITALS...")

hospitals_type_id = get_service_type_id('hospitals')
cur.execute("""
    SELECT sl.id, sl.name
    FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    WHERE ls.service_type_id = %s AND sl.deleted_at IS NULL
    ORDER BY sl.name
""", (hospitals_type_id,))

hospitals = cur.fetchall()
for loc_id, name in hospitals:
    stats['hospitals']['checked'] += 1

    if location_has_hours(loc_id):
        stats['hospitals']['skipped'] += 1
        continue

    add_24_7_hours(loc_id, hospitals_type_id, "Emergency Room open 24/7")
    stats['hospitals']['updated'] += 1
    print(f"  + {name}")

print(f"  Checked: {stats['hospitals']['checked']}, Updated: {stats['hospitals']['updated']}, Already had hours: {stats['hospitals']['skipped']}")

# =============================================================================
# 2. LINKNYC KIOSKS - 24/7 WiFi (but NOT libraries)
# =============================================================================
print("\n2. Processing LINKNYC KIOSKS...")

wifi_type_id = get_service_type_id('free-wifi-linknyc')
cur.execute("""
    SELECT sl.id, sl.name
    FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    WHERE ls.service_type_id = %s
      AND sl.deleted_at IS NULL
      AND sl.name ILIKE '%%LinkNYC%%'
    ORDER BY sl.name
""", (wifi_type_id,))

linknyc_locations = cur.fetchall()
for loc_id, name in linknyc_locations:
    stats['linknyc']['checked'] += 1

    # SAFETY CHECK: Skip libraries
    if 'library' in name.lower():
        stats['linknyc']['library_skipped'] += 1
        print(f"  SKIPPED (Library): {name}")
        continue

    if location_has_hours(loc_id):
        stats['linknyc']['skipped'] += 1
        continue

    add_24_7_hours(loc_id, wifi_type_id, "LinkNYC kiosk - 24/7 WiFi & charging")
    stats['linknyc']['updated'] += 1

print(f"  Checked: {stats['linknyc']['checked']}, Updated: {stats['linknyc']['updated']}, Already had hours: {stats['linknyc']['skipped']}, Libraries skipped: {stats['linknyc']['library_skipped']}")

# =============================================================================
# 3. CPEP (Comprehensive Psychiatric Emergency Program) - 24/7 ER
# =============================================================================
print("\n3. Processing CPEP LOCATIONS...")

crisis_type_id = get_service_type_id('mental-health-crisis')
cur.execute("""
    SELECT sl.id, sl.name
    FROM service_locations sl
    JOIN location_services ls ON sl.id = ls.location_id
    WHERE ls.service_type_id = %s
      AND sl.deleted_at IS NULL
      AND (sl.name ILIKE '%%CPEP%%' OR sl.description ILIKE '%%CPEP%%')
    ORDER BY sl.name
""", (crisis_type_id,))

cpep_locations = cur.fetchall()
for loc_id, name in cpep_locations:
    stats['cpep']['checked'] += 1

    if location_has_hours(loc_id):
        stats['cpep']['skipped'] += 1
        continue

    add_24_7_hours(loc_id, crisis_type_id, "CPEP - Psychiatric Emergency open 24/7")
    stats['cpep']['updated'] += 1
    print(f"  + {name}")

print(f"  Checked: {stats['cpep']['checked']}, Updated: {stats['cpep']['updated']}, Already had hours: {stats['cpep']['skipped']}")

# Commit all changes
conn.commit()

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"""
Hospitals:
  - Checked: {stats['hospitals']['checked']}
  - Updated with 24/7 hours: {stats['hospitals']['updated']}
  - Already had hours: {stats['hospitals']['skipped']}

LinkNYC Kiosks:
  - Checked: {stats['linknyc']['checked']}
  - Updated with 24/7 hours: {stats['linknyc']['updated']}
  - Already had hours: {stats['linknyc']['skipped']}
  - Libraries skipped (safety): {stats['linknyc']['library_skipped']}

CPEP (Psychiatric ER):
  - Checked: {stats['cpep']['checked']}
  - Updated with 24/7 hours: {stats['cpep']['updated']}
  - Already had hours: {stats['cpep']['skipped']}

TOTAL LOCATIONS UPDATED: {stats['hospitals']['updated'] + stats['linknyc']['updated'] + stats['cpep']['updated']}
""")

# Verify final hours coverage
print("=" * 60)
print("UPDATED HOURS COVERAGE:")
cur.execute("""
    SELECT
        st.name as "Service Type",
        COUNT(DISTINCT sl.id) as "Total",
        COUNT(DISTINCT oh.location_id) as "With Hours",
        ROUND(100.0 * COUNT(DISTINCT oh.location_id) / NULLIF(COUNT(DISTINCT sl.id), 0), 1) as "Coverage %"
    FROM service_types st
    LEFT JOIN location_services ls ON st.id = ls.service_type_id
    LEFT JOIN service_locations sl ON ls.location_id = sl.id AND sl.deleted_at IS NULL
    LEFT JOIN operating_hours oh ON sl.id = oh.location_id
    WHERE st.slug IN ('hospitals', 'free-wifi-linknyc', 'mental-health-crisis')
    GROUP BY st.id, st.name
    ORDER BY st.name
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[2]}/{row[1]} ({row[3]}%)")

conn.close()
print("\nDone!")
