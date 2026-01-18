#!/usr/bin/env python3
"""
Import operating hours from audit_report.txt into the database
"""
import asyncio
import re
from datetime import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def parse_time(time_str):
    """Convert time string to time object"""
    time_str = time_str.strip().upper()

    # Handle 24-hour format
    if ':' in time_str and ('AM' not in time_str and 'PM' not in time_str):
        parts = time_str.split(':')
        hour = int(parts[0])
        minute = int(parts[1])
        return time(hour, minute)

    # Handle 12-hour format
    is_pm = 'PM' in time_str
    time_str = time_str.replace('AM', '').replace('PM', '').strip()

    parts = time_str.split(':')
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0

    if is_pm and hour != 12:
        hour += 12
    elif not is_pm and hour == 12:
        hour = 0

    return time(hour, minute)

def day_name_to_int(day_name):
    """Convert day name to integer (0=Sunday, 6=Saturday)"""
    day_map = {
        'sunday': 0,
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6
    }
    return day_map.get(day_name.lower())

def parse_hours_line(line):
    """Parse a line containing 'Verified Hours:' and return structured data"""
    hours_data = []

    # Remove the "Verified Hours:" prefix
    line = re.sub(r'^Verified Hours:\s*', '', line, flags=re.IGNORECASE)

    # Pattern 1a: "Monday through Friday, 9:30 AM to 5:30 PM"
    match = re.search(r'Monday through Friday,?\s*(\d{1,2}:\d{2}\s*[AP]M)\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
    if match:
        open_time = parse_time(match.group(1))
        close_time = parse_time(match.group(2))
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            hours_data.append({
                'day_of_week': day_name_to_int(day),
                'open_time': open_time,
                'close_time': close_time
            })
        return hours_data

    # Pattern 1b: "Monday through Thursday" or "Wednesday through Saturday"
    match = re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*through\s*(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s*(\d{1,2}:\d{2}\s*[AP]M)\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
    if match:
        start_day = match.group(1).lower()
        end_day = match.group(2).lower()
        open_time = parse_time(match.group(3))
        close_time = parse_time(match.group(4))

        all_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        start_idx = all_days.index(start_day)
        end_idx = all_days.index(end_day)

        # Handle wrap-around (e.g., Friday through Monday)
        if end_idx >= start_idx:
            days_range = all_days[start_idx:end_idx+1]
        else:
            days_range = all_days[start_idx:] + all_days[:end_idx+1]

        for day in days_range:
            hours_data.append({
                'day_of_week': day_name_to_int(day),
                'open_time': open_time,
                'close_time': close_time
            })
        return hours_data

    # Pattern 2: "Mon/Wed/Fri/Sat 10:00 AM - 3:00 PM"
    match = re.search(r'((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)(?:/(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun))*)\s*(\d{1,2}:\d{2}\s*[AP]M)\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
    if match:
        days_str = match.group(1)
        open_time = parse_time(match.group(2))
        close_time = parse_time(match.group(3))

        day_map = {
            'Mon': 'monday', 'Tue': 'tuesday', 'Wed': 'wednesday',
            'Thu': 'thursday', 'Fri': 'friday', 'Sat': 'saturday', 'Sun': 'sunday'
        }

        for day_abbr in days_str.split('/'):
            if day_abbr in day_map:
                hours_data.append({
                    'day_of_week': day_name_to_int(day_map[day_abbr]),
                    'open_time': open_time,
                    'close_time': close_time
                })
        return hours_data

    # Pattern 3: "Wednesdays from 11:00 AM to 2:00 PM"
    match = re.search(r'(Mondays?|Tuesdays?|Wednesdays?|Thursdays?|Fridays?|Saturdays?|Sundays?)\s*(?:from)?\s*(\d{1,2}:\d{2}\s*[AP]M)\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
    if match:
        day = match.group(1).lower().rstrip('s')  # Remove trailing 's'
        open_time = parse_time(match.group(2))
        close_time = parse_time(match.group(3))
        hours_data.append({
            'day_of_week': day_name_to_int(day),
            'open_time': open_time,
            'close_time': close_time
        })

    # Pattern 4: Multiple separate schedules in one line
    # "Tuesdays 6:00 PM - 7:15 PM and Thursdays 11:00 AM - 2:15 PM"
    matches = re.finditer(r'(Mondays?|Tuesdays?|Wednesdays?|Thursdays?|Fridays?|Saturdays?|Sundays?)\s*(\d{1,2}:\d{2}\s*[AP]M)\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
    for match in matches:
        day = match.group(1).lower().rstrip('s')
        open_time = parse_time(match.group(2))
        close_time = parse_time(match.group(3))
        hours_data.append({
            'day_of_week': day_name_to_int(day),
            'open_time': open_time,
            'close_time': close_time
        })

    # Pattern 5: "2nd & 4th Thursdays of the month"
    if 'nd' in line or 'rd' in line or 'th' in line:
        match = re.search(r'(\d+)(?:st|nd|rd|th)\s*(?:&|and)\s*(\d+)(?:st|nd|rd|th)\s*(Mondays?|Tuesdays?|Wednesdays?|Thursdays?|Fridays?|Saturdays?|Sundays?)[^,]*,?\s*(\d{1,2}:\d{2}\s*[AP]M)\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
        if match:
            day = match.group(3).lower().rstrip('s')
            open_time = parse_time(match.group(4))
            close_time = parse_time(match.group(5))
            hours_data.append({
                'day_of_week': day_name_to_int(day),
                'open_time': open_time,
                'close_time': close_time,
                'notes': f"Only {match.group(1)} and {match.group(2)} {match.group(3)} of the month"
            })

    # Pattern 6: Daily schedule "Breakfast: 6:00-7:30 AM; Lunch: 12:00-1:30 PM"
    if 'daily' in line.lower() or ('breakfast' in line.lower() and 'dinner' in line.lower()):
        # Extract time ranges
        time_matches = re.finditer(r'(\d{1,2}:\d{2})(?:\s*[AP]M)?\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
        for match in time_matches:
            try:
                open_time = parse_time(match.group(1))
                close_time = parse_time(match.group(2))
                # Add for all days
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    hours_data.append({
                        'day_of_week': day_name_to_int(day),
                        'open_time': open_time,
                        'close_time': close_time
                    })
            except:
                pass

    return hours_data

async def find_location_by_address(db: AsyncSession, address: str):
    """Find location in database by address"""
    # Clean the address
    address = address.strip()

    # Try exact match first
    result = await db.execute(text("""
        SELECT id, name, street_address FROM service_locations
        WHERE LOWER(street_address) = LOWER(:address)
    """), {'address': address})

    location = result.fetchone()
    if location:
        return location

    # Try matching just the street number and street name
    match = re.match(r'(\d+(?:-\d+)?)\s+(.+?),', address)
    if match:
        street_num = match.group(1)
        street_name = match.group(2)

        result = await db.execute(text("""
            SELECT id, name, street_address FROM service_locations
            WHERE street_address ILIKE :pattern
        """), {'pattern': f'{street_num} {street_name}%'})

        location = result.fetchone()
        if location:
            return location

    return None

async def import_hours():
    """Parse audit report and import hours"""
    async with AsyncSessionLocal() as db:
        with open('audit_report.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        stats = {
            'found': 0,
            'not_found': 0,
            'hours_added': 0,
            'errors': 0
        }

        # Split into sections by location
        # Pattern: Location name on its own line, then "Location: address"
        sections = re.split(r'\n([A-Z][^\n]+?(?:Church|Center|House|Mission|Pantry|Kitchen|Ministry|Services|Committee|Council|Campaign|Organization|Corp\.|Inc\.))\s*\n', content)

        current_location_name = None

        for i in range(len(sections)):
            section = sections[i]

            # Check if this is a location name
            if re.match(r'^[A-Z]', section.strip()) and len(section.strip()) < 100:
                current_location_name = section.strip()
                continue

            # Look for address and hours in this section
            if current_location_name and 'Location:' in section and 'Verified Hours:' in section:
                # Extract address
                addr_match = re.search(r'Location:\s*([^\n]+)', section)
                if not addr_match:
                    continue

                address = addr_match.group(1).strip()

                # Extract hours
                hours_match = re.search(r'Verified Hours:\s*([^\n]+(?:\n(?!Location:|Service|Verified|Requirements:)[^\n]+)*)', section, re.MULTILINE)
                if not hours_match:
                    continue

                hours_text = hours_match.group(1).strip()

                # Parse the hours
                hours_data = parse_hours_line(hours_text)

                if not hours_data:
                    print(f"⚠️  Could not parse hours for {current_location_name}: {hours_text}")
                    continue

                # Find location in database
                location = await find_location_by_address(db, address)

                if location:
                    print(f"✓ Found: {current_location_name}")
                    print(f"  Address: {address}")
                    print(f"  Hours: {hours_text}")
                    stats['found'] += 1

                    # Delete existing hours for this location
                    await db.execute(text("""
                        DELETE FROM operating_hours WHERE location_id = :location_id
                    """), {'location_id': location.id})

                    # Insert new hours
                    for hours in hours_data:
                        try:
                            await db.execute(text("""
                                INSERT INTO operating_hours (location_id, day_of_week, open_time, close_time, is_24_hours, is_closed, notes)
                                VALUES (:location_id, :day_of_week, :open_time, :close_time, :is_24_hours, :is_closed, :notes)
                            """), {
                                'location_id': location.id,
                                'day_of_week': hours['day_of_week'],
                                'open_time': hours['open_time'],
                                'close_time': hours['close_time'],
                                'is_24_hours': hours.get('is_24_hours', False),
                                'is_closed': hours.get('is_closed', False),
                                'notes': hours.get('notes')
                            })
                            stats['hours_added'] += 1
                        except Exception as e:
                            print(f"  ✗ Error adding hours: {e}")
                            stats['errors'] += 1

                    await db.commit()
                    print(f"  ✓ Added {len(hours_data)} hour entries\n")
                else:
                    print(f"✗ Not found: {current_location_name}")
                    print(f"  Address: {address}\n")
                    stats['not_found'] += 1

        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Locations found in database: {stats['found']}")
        print(f"Locations not found: {stats['not_found']}")
        print(f"Total hour entries added: {stats['hours_added']}")
        print(f"Errors: {stats['errors']}")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(import_hours())
