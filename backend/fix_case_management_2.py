#!/usr/bin/env python3
"""Fix remaining mislabeled Case Management entries."""

import os
import psycopg2

# Database connection from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://hope_user:hope_password@localhost:5432/hope_db')
db_url = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
conn = psycopg2.connect(db_url)
cur = conn.cursor()

def get_service_type_id(slug):
    cur.execute("SELECT id FROM service_types WHERE slug = %s", (slug,))
    result = cur.fetchone()
    return result[0] if result else None

def move_location_to_service(location_id, from_slug, to_slug):
    from_id = get_service_type_id(from_slug)
    to_id = get_service_type_id(to_slug)
    if not from_id or not to_id:
        return False
    cur.execute("""
        SELECT 1 FROM location_services
        WHERE location_id = %s AND service_type_id = %s
    """, (location_id, to_id))
    if cur.fetchone():
        cur.execute("""
            DELETE FROM location_services
            WHERE location_id = %s AND service_type_id = %s
        """, (location_id, from_id))
    else:
        cur.execute("""
            UPDATE location_services
            SET service_type_id = %s
            WHERE location_id = %s AND service_type_id = %s
        """, (to_id, location_id, from_id))
    return True

# Additional food locations that were missed
print("Moving additional food locations...")
food_locations = [
    '7b2b410f-5f33-4fbe-8a8b-1fb0e2bbe458',  # Part of the Solution (POTS) - Bronx
    '31800615-1ffe-4e61-83ca-d9abc84a1f9f',  # Project Hospitality - Staten Island
    'dc17d40e-cc0c-4823-92ba-d988fa8802b9',  # Queens Community House - Forest Hills
    '452c66e5-5779-427c-963b-fec6541e0bf1',  # Salvation Army - Flushing Corps
    'e7ebd422-2718-4256-b774-de0f6c73833e',  # Salvation Army - Jamaica Corps (has food)
]
for loc_id in food_locations:
    cur.execute("SELECT name FROM service_locations WHERE id = %s", (loc_id,))
    result = cur.fetchone()
    if result:
        print(f"  Moving: {result[0]}")
        move_location_to_service(loc_id, 'social', 'food')

# Additional shelter locations (supportive housing, residences, etc.)
print("\nMoving additional shelter locations...")
shelter_locations = [
    '72489ef2-fa81-45e3-9f78-bdfd5e3b06e4',  # Bowery Mission (Men's shelter)
    '497f46dc-e700-436f-bef1-5f7793aef3ee',  # Bowery Mission Transitional Center
    'b45885d7-088c-48d2-bfac-6ef7405cb32f',  # Bowery Mission - Women's Center
    'cbdca7ec-593a-4b39-8d2f-bc5230648e59',  # BRC - Andrews House
    'df224dfa-d980-47bb-821c-70696845b15a',  # BRC - Ready, Willing & Able
    '54e342d9-8c4f-46b8-a439-1ae066f39d52',  # Breaking Ground - Horatio House
    '1d2cdc81-e4d5-46d8-a033-c33f1c66cff6',  # Breaking Ground - Prince George
    '7cbe9656-73d9-44fd-81bb-ba6a3bd7c1da',  # Breaking Ground - Times Square
    'ecef0259-161b-41e5-a171-d2e52eda1bfa',  # Brooklyn Community Services - Ella's Place
    '7cbaaaf3-4f7d-4454-ba81-f85e16e9b9d5',  # Catholic Charities - St. Rita's Haven
    'c140a699-e4df-470e-8ef5-98bd1ac6eef9',  # Goddard Riverside (supportive housing)
    '57b57cb8-aac9-4f70-b065-dd990c8c3cdf',  # HELP USA - Williams Women's Center
    '681adaa4-b29f-4455-beac-a1bab1297c46',  # Henry Street Settlement - Urban Family Center
    '43ab42fc-0d25-4c77-ae84-a64f565cf3aa',  # Interfaith Assembly (shelters)
    '16bf7481-1d7e-46e2-a034-39de8c5cc251',  # New York City Rescue Mission - Lafayette
    '7d70ca9f-edf4-4d05-bb24-f152bc1227a3',  # Partnership for the Homeless - Bedford Atlantic
    '6a1e0861-0abf-496e-812f-84788a236ea5',  # Partnership for the Homeless - Prospect Plaza
    '33eae018-4867-4f8b-a599-bfdc82a6c129',  # Project Renewal - Goddard Riverside
    '116a65ea-2850-4ccb-8757-f0ebc43b0216',  # Salvation Army - Bowery Corps (has shelter)
    'c222d2ec-c1f6-4d7e-b79f-1bd4b77d00fb',  # Salvation Army - Bronx Corps
    '6e674ae4-22bf-4f7a-9a81-7c119ba6e2ed',  # Salvation Army - Harlem Temple Corps
    '92db8f26-8a68-4afc-9b09-d2136f131543',  # Urban Pathways - West Side Federation
]
for loc_id in shelter_locations:
    cur.execute("SELECT name FROM service_locations WHERE id = %s", (loc_id,))
    result = cur.fetchone()
    if result:
        print(f"  Moving: {result[0]}")
        move_location_to_service(loc_id, 'social', 'shelter')

conn.commit()

# Final count
print("\n" + "=" * 60)
print("Final counts by service type:")
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
