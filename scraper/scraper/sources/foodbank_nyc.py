"""Food Bank For NYC scraper using Playwright to access their map data."""
import httpx
from typing import List
from datetime import datetime, time
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import re

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData, OperatingHours, ServiceCapacity
from scraper.config import settings


class FoodBankNYCScraper(BaseScraper):
    """
    Scrape Food Bank For NYC pantry locations.

    Food Bank NYC uses an embedded Azure-hosted map iframe at:
    https://fbnycmap.z13.web.core.windows.net/

    The map loads data from a CSV file that we can intercept using Playwright.
    """

    MAP_URL = "https://fbnycmap.z13.web.core.windows.net/"

    async def scrape(self) -> List[RawServiceData]:
        """
        Scrape Food Bank NYC pantry data using Playwright.

        We access their map iframe and intercept the CSV data it loads.
        """
        print(f"  🌐 Launching Playwright to scrape Food Bank NYC pantry network...")

        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                page = await browser.new_page()

                # Track network requests to intercept CSV data
                csv_data = None

                async def handle_response(response):
                    nonlocal csv_data
                    if '.csv' in response.url and response.status == 200:
                        print(f"  ✓ Intercepted CSV data from: {response.url}")
                        try:
                            csv_data = await response.text()
                        except Exception as e:
                            print(f"  ⚠️  Error reading CSV: {e}")

                page.on("response", handle_response)

                # Navigate to map iframe
                print(f"  → Loading map from {self.MAP_URL}")
                await page.goto(self.MAP_URL, wait_until='networkidle', timeout=60000)

                # Wait a bit for CSV to load
                await asyncio.sleep(3)

                await browser.close()

                if csv_data:
                    print(f"  ✓ Successfully intercepted CSV data!")
                    return self._parse_csv_data(csv_data)
                else:
                    print(f"  ⚠️  Could not intercept CSV data - falling back to manual locations")
                    return self._get_manual_locations()

        except PlaywrightTimeout:
            print(f"  ⚠️  Timeout loading Food Bank map - falling back to manual locations")
            return self._get_manual_locations()
        except Exception as e:
            print(f"  ❌ Error with Playwright: {e}")
            print(f"  ℹ️  Falling back to manual Food Bank community kitchens")
            return self._get_manual_locations()

    def _parse_csv_data(self, csv_text: str) -> List[RawServiceData]:
        """Parse CSV data from Food Bank NYC."""
        results = []

        # Parse CSV
        lines = csv_text.strip().split('\n')
        if len(lines) < 2:
            print(f"  ⚠️  CSV has no data rows")
            return self._get_manual_locations()

        # Get header
        header = lines[0].split(',')
        print(f"  ℹ️  CSV columns: {', '.join(header)}")

        # Parse each row
        for i, line in enumerate(lines[1:], 1):
            try:
                # Simple CSV parsing (may need adjustment for quoted fields)
                values = line.split(',')
                row = dict(zip(header, values))

                # Extract location data (actual column names from Food Bank CSV)
                # CSV has: Agency, Address 1, Address 2, Address 3, Address 4, Phone, etc.
                name = row.get('Agency') or 'Unknown'

                # Build full address from multiple address fields
                address_parts = []
                for i in range(1, 5):
                    addr_part = row.get(f'Address {i}', '').strip()
                    if addr_part:
                        address_parts.append(addr_part)

                if len(address_parts) == 0:
                    # Skip entries without addresses
                    continue

                # Parse address components
                street = address_parts[0] if len(address_parts) > 0 else ''
                city = address_parts[1] if len(address_parts) > 1 else 'New York'
                state_zip = address_parts[2] if len(address_parts) > 2 else 'NY'

                # Extract state and ZIP from "NY 10001" format
                state = 'NY'
                zip_code = ''
                if state_zip:
                    parts = state_zip.split()
                    if len(parts) >= 2:
                        state = parts[0]
                        zip_code = parts[1]
                    elif len(parts) == 1:
                        if parts[0].isdigit():
                            zip_code = parts[0]
                        else:
                            state = parts[0]

                borough = self._guess_borough(street + ' ' + city, zip_code)
                phone = row.get('Phone', '').strip()

                # Pantries provide food services
                service_types = ["food"]

                results.append(RawServiceData(
                    name=name.strip('"').strip(),
                    organization_name="Food Bank For New York City",
                    description=f"Food pantry or soup kitchen in the Food Bank For NYC network.",
                    street_address=street.strip('"').strip(),
                    city=city.strip('"').strip(),
                    state=state.strip('"').strip(),
                    zip_code=zip_code.strip('"').strip(),
                    borough=borough.strip('"').strip() if borough else None,
                    phone=phone.strip('"').strip() if phone else None,
                    website="https://www.foodbanknyc.org",
                    service_types=service_types,
                    external_id=f"fbnyc-{str(hash(name + street))}",
                    data_source="Food Bank For NYC",
                    scraped_at=datetime.now(),
                ))

            except Exception as e:
                print(f"  ⚠️  Error parsing CSV row {i}: {e}")
                continue

        print(f"  ✓ Parsed {len(results)} pantries from CSV")
        return results

    def _guess_borough(self, address: str, zip_code: str) -> str:
        """Guess borough from address or ZIP code."""
        address_lower = address.lower()

        if 'bronx' in address_lower:
            return 'Bronx'
        elif 'brooklyn' in address_lower:
            return 'Brooklyn'
        elif 'queens' in address_lower:
            return 'Queens'
        elif 'staten island' in address_lower:
            return 'Staten Island'
        else:
            return 'Manhattan'  # Default

    def _get_manual_locations(self) -> List[RawServiceData]:
        """Return manually curated Food Bank locations as fallback."""
        manual_locations = [
            {
                "name": "Food Bank For NYC - Community Kitchen Harlem",
                "address": "2132 Frederick Douglass Boulevard, New York, NY 10026",
                "phone": "646-975-4292",
                "website": "https://www.foodbanknyc.org/community-kitchen/harlem/",
                "description": "Community kitchen providing hot meals, groceries, health screenings, SNAP enrollment assistance, and social services.",
                "services": ["food", "hygiene", "medical", "social"],
                "hours": [
                    # Monday-Friday: Breakfast 8am-9:30am, Lunch 12pm-1:30pm
                    {"day": 0, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 1, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 2, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 3, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 4, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    # Closed weekends
                    {"day": 5, "is_closed": True},
                    {"day": 6, "is_closed": True},
                ],
            },
            {
                "name": "Food Bank For NYC - Community Kitchen South Bronx",
                "address": "355 Food Center Drive, Bronx, NY 10474",
                "phone": "718-991-4300",
                "website": "https://www.foodbanknyc.org/community-kitchen/south-bronx/",
                "description": "Community kitchen providing hot meals, groceries, health screenings, SNAP enrollment assistance, and social services.",
                "services": ["food", "hygiene", "medical", "social"],
                "hours": [
                    # Monday-Friday: Breakfast 8am-9:30am, Lunch 12pm-1:30pm
                    {"day": 0, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 1, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 2, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 3, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    {"day": 4, "open_time": time(8, 0), "close_time": time(13, 30), "notes": "Breakfast 8-9:30am, Lunch 12-1:30pm"},
                    # Closed weekends
                    {"day": 5, "is_closed": True},
                    {"day": 6, "is_closed": True},
                ],
            },
        ]

        results = []
        for location in manual_locations:
            address_parts = location["address"].split(",")
            street = address_parts[0].strip()
            borough = "Bronx" if "Bronx" in location["address"] else "Manhattan"
            zip_code = address_parts[-1].strip().split()[-1] if len(address_parts) > 2 else None

            # Convert operating hours to OperatingHours objects
            operating_hours = None
            if "hours" in location:
                operating_hours = [
                    OperatingHours(
                        day_of_week=hours["day"],
                        open_time=hours.get("open_time"),
                        close_time=hours.get("close_time"),
                        is_24_hours=hours.get("is_24_hours", False),
                        is_closed=hours.get("is_closed", False),
                        notes=hours.get("notes")
                    )
                    for hours in location["hours"]
                ]

            results.append(RawServiceData(
                name=location["name"],
                organization_name="Food Bank For New York City",
                description=location["description"],
                street_address=street,
                city="New York",
                state="NY",
                zip_code=zip_code,
                borough=borough,
                phone=location["phone"],
                website=location.get("website", "https://www.foodbanknyc.org"),
                service_types=location["services"],
                operating_hours=operating_hours,
                external_id=str(hash(location["name"])),
                data_source="Food Bank For NYC",
                scraped_at=datetime.now(),
            ))

        return results
