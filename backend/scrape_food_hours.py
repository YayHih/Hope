"""
Scrape operating hours for food locations that are missing hours data.

This script:
1. Finds all food locations without operating hours
2. Searches Google for each location
3. Attempts to extract hours from search results
4. Saves results to CSV for manual review before importing
"""

import asyncio
import os
import csv
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import httpx
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# User agent to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def parse_hours_from_text(text: str) -> dict:
    """
    Extract operating hours from text using pattern matching.

    Returns dict with day -> hours mapping, or empty dict if no hours found.
    """
    hours = {}

    # Common patterns for hours
    # "Monday: 9:00 AM - 5:00 PM"
    # "Mon-Fri: 9AM-5PM"
    # "Weekdays 9-5"

    day_patterns = {
        'monday': ['monday', 'mon'],
        'tuesday': ['tuesday', 'tue', 'tues'],
        'wednesday': ['wednesday', 'wed'],
        'thursday': ['thursday', 'thu', 'thur', 'thurs'],
        'friday': ['friday', 'fri'],
        'saturday': ['saturday', 'sat'],
        'sunday': ['sunday', 'sun']
    }

    # Look for patterns like "Monday: 9:00 AM - 5:00 PM"
    for line in text.split('\n'):
        line = line.strip().lower()

        for day, patterns in day_patterns.items():
            for pattern in patterns:
                if pattern in line and ':' in line:
                    # Extract the part after the day name
                    parts = line.split(pattern, 1)
                    if len(parts) > 1:
                        time_part = parts[1].strip().lstrip(':').strip()
                        if time_part:
                            hours[day] = time_part
                            break

    return hours


async def search_google_for_hours(name: str, address: str, city: str) -> dict:
    """
    Search Google for business hours.

    Returns dict with scraped data or None if not found.
    """
    query = f"{name} {address} {city} hours"
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
            response = await client.get(search_url)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find hours in Google Knowledge Panel
            # Look for common hours patterns
            text = soup.get_text()

            hours = parse_hours_from_text(text)

            if hours:
                return {
                    'source': 'Google Search',
                    'hours': hours,
                    'raw_text': text[:500]  # Save snippet for verification
                }

            return None

    except Exception as e:
        print(f"  Error searching for {name}: {str(e)}")
        return None


async def scrape_missing_hours():
    """Find and scrape operating hours for food locations."""

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    output_file = Path('/home/opc/Hope/backend/food_hours_scraped.csv')

    print("=" * 60)
    print("SCRAPING FOOD LOCATION HOURS")
    print("=" * 60)

    async with async_session() as db:
        # Get all food locations without operating hours
        result = await db.execute(text("""
            SELECT sl.id, sl.name, sl.street_address, sl.city, sl.state, sl.zip_code
            FROM service_locations sl
            JOIN location_services ls ON sl.id = ls.location_id
            JOIN service_types st ON ls.service_type_id = st.id
            WHERE st.slug = 'food'
            AND sl.deleted_at IS NULL
            AND NOT EXISTS (
                SELECT 1 FROM operating_hours oh
                WHERE oh.location_id = sl.id
            )
            ORDER BY sl.name
        """))

        locations = result.fetchall()
        total = len(locations)

        print(f"\nFound {total} food locations without hours")
        print(f"Starting scraping process...\n")

        results = []
        found_count = 0

        for idx, loc in enumerate(locations, 1):
            print(f"[{idx}/{total}] Searching: {loc.name}")

            # Search for hours
            scraped = await search_google_for_hours(
                loc.name,
                loc.street_address,
                loc.city
            )

            if scraped and scraped.get('hours'):
                found_count += 1
                print(f"  ✓ Found hours from {scraped['source']}")

                # Format hours for CSV
                hours_str = '; '.join([f"{day}: {time}" for day, time in scraped['hours'].items()])

                results.append({
                    'id': str(loc.id),
                    'name': loc.name,
                    'address': loc.street_address,
                    'city': loc.city,
                    'hours_found': hours_str,
                    'source': scraped['source'],
                    'status': 'needs_review'
                })
            else:
                print(f"  ✗ No hours found")
                results.append({
                    'id': str(loc.id),
                    'name': loc.name,
                    'address': loc.street_address,
                    'city': loc.city,
                    'hours_found': '',
                    'source': '',
                    'status': 'not_found'
                })

            # Rate limiting - be respectful to Google
            if idx < total:
                await asyncio.sleep(2)  # 2 second delay between requests

            # Progress update every 10 locations
            if idx % 10 == 0:
                print(f"\nProgress: {idx}/{total} ({found_count} found so far)\n")

        # Save results to CSV
        print(f"\nSaving results to {output_file.name}...")
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'name', 'address', 'city', 'hours_found', 'source', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print("\n" + "=" * 60)
        print("SCRAPING SUMMARY")
        print("=" * 60)
        print(f"Total locations processed:  {total}")
        print(f"Hours found:                {found_count}")
        print(f"Not found:                  {total - found_count}")
        print(f"Success rate:               {(found_count / total * 100):.1f}%")
        print("=" * 60)
        print(f"\n✓ Results saved to {output_file.name}")
        print("\nNext steps:")
        print("1. Review the CSV file manually")
        print("2. Verify the hours are correct")
        print("3. Run import_food_hours.py to update the database")

    await engine.dispose()


if __name__ == "__main__":
    print("\n🔍 Food Hours Scraper")
    print("This will search online for operating hours of food locations.")
    print("The process may take a while (2 second delay between requests).\n")

    response = input("Continue with scraping? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(scrape_missing_hours())
    else:
        print("Scraping cancelled.")
