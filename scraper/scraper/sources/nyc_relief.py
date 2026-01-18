"""NYC Relief scraper - mobile relief bus schedules."""
import httpx
from typing import List
from datetime import datetime

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData


class NYCReliefScraper(BaseScraper):
    """
    Scrape NYC Relief mobile bus locations.

    Note: NYC Relief operates mobile relief buses that move to different
    locations on a schedule. These are not fixed locations but recurring stops.
    """

    # Known NYC Relief mobile bus stops (based on their public schedule)
    # These represent regular stops, not fixed facilities
    BUS_STOPS = [
        {
            "name": "NYC Relief Mobile Bus - Times Square",
            "address": "West 42nd Street and 8th Avenue, New York, NY 10036",
            "description": "Mobile relief bus serving Times Square area. Provides hot meals, clothing, hygiene kits, and social services. Schedule varies - check nycrelief.org for current times.",
            "services": ["food", "hygiene", "social"],
        },
        {
            "name": "NYC Relief Mobile Bus - Penn Station",
            "address": "7th Avenue and West 33rd Street, New York, NY 10001",
            "description": "Mobile relief bus serving Penn Station area. Provides hot meals, clothing, hygiene kits, and social services. Schedule varies - check nycrelief.org for current times.",
            "services": ["food", "hygiene", "social"],
        },
        {
            "name": "NYC Relief Mobile Bus - Port Authority",
            "address": "8th Avenue and West 42nd Street, New York, NY 10018",
            "description": "Mobile relief bus serving Port Authority area. Provides hot meals, clothing, hygiene kits, and social services. Schedule varies - check nycrelief.org for current times.",
            "services": ["food", "hygiene", "social"],
        },
        {
            "name": "NYC Relief Mobile Bus - Brooklyn",
            "address": "Atlantic Avenue and Flatbush Avenue, Brooklyn, NY 11217",
            "description": "Mobile relief bus serving Brooklyn. Provides hot meals, clothing, hygiene kits, and social services. Schedule varies - check nycrelief.org for current times.",
            "services": ["food", "hygiene", "social"],
        },
    ]

    async def scrape(self) -> List[RawServiceData]:
        """
        Return NYC Relief mobile bus locations.

        Note: These are mobile services with varying schedules.
        Future enhancement: scrape nycrelief.org for current schedule.
        """
        print(f"  Using {len(self.BUS_STOPS)} NYC Relief mobile bus stops")
        print(f"  ⚠️  Note: NYC Relief buses are mobile - schedules vary")

        results = []
        for stop in self.BUS_STOPS:
            try:
                # Parse address
                address_parts = stop["address"].split(",")
                street = address_parts[0].strip()
                borough = "Brooklyn" if "Brooklyn" in stop["address"] else "Manhattan"
                zip_code = address_parts[-1].strip().split()[-1] if len(address_parts) > 2 else None

                results.append(RawServiceData(
                    name=stop["name"],
                    organization_name="NYC Relief",
                    description=stop["description"],
                    street_address=street,
                    city="New York",
                    state="NY",
                    zip_code=zip_code,
                    borough=borough,
                    phone="646-315-7740",
                    website="https://nycrelief.org",
                    service_types=stop["services"],
                    external_id=str(hash(stop["name"])),
                    data_source="NYC Relief",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error processing NYC Relief stop: {e}")
                continue

        return results
