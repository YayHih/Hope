"""NYC Cooling and Warming Centers scraper."""
from typing import List
from datetime import datetime

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData


class NYCCoolingWarmingScraper(BaseScraper):
    """Scrape NYC cooling and warming centers."""

    # NYC Cooling Centers (Summer)
    COOLING_CENTERS = [
        {
            "name": "Harlem YMCA",
            "address": "180 West 135th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10030",
            "phone": "(212) 912-2100"
        },
        {
            "name": "Riverbank State Park",
            "address": "679 Riverside Drive",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10031",
            "phone": "(212) 694-3600"
        },
        {
            "name": "East Side Settlement House",
            "address": "337 Alexander Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10454",
            "phone": "(718) 665-5250"
        },
        {
            "name": "Woodside Community Center",
            "address": "50-43 Skillman Avenue",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11377",
            "phone": "(718) 651-5455"
        },
        {
            "name": "Brooklyn Public Library - Central",
            "address": "10 Grand Army Plaza",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11238",
            "phone": "(718) 230-2100"
        },
        {
            "name": "West Brighton Community Center",
            "address": "207 Pavilion Avenue",
            "city": "Staten Island",
            "borough": "Staten Island",
            "zip": "10310",
            "phone": "(718) 816-5900"
        },
    ]

    # NYC Warming Centers (Winter)
    WARMING_CENTERS = [
        {
            "name": "Bowery Mission - Emergency Warming Center",
            "address": "227 Bowery",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10002",
            "phone": "(212) 674-3456"
        },
        {
            "name": "Partnership with Children - Warming Center",
            "address": "1002 Dean Street",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11238",
            "phone": "(718) 398-2050"
        },
        {
            "name": "Bronx YMCA - Warming Center",
            "address": "2 Castle Hill Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10473",
            "phone": "(718) 792-9736"
        },
        {
            "name": "Queens Community House",
            "address": "108-25 62nd Drive",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11375",
            "phone": "(718) 592-5757"
        },
        {
            "name": "Project Hospitality - Warming Center",
            "address": "100 Park Avenue",
            "city": "Staten Island",
            "borough": "Staten Island",
            "zip": "10302",
            "phone": "(718) 448-1544"
        },
    ]

    async def scrape(self) -> List[RawServiceData]:
        """Return hardcoded list of NYC cooling and warming centers."""
        results = []

        print(f"  Loading {len(self.COOLING_CENTERS)} cooling centers")

        # Add cooling centers
        for center in self.COOLING_CENTERS:
            try:
                results.append(RawServiceData(
                    name=center["name"],
                    organization_name="NYC Cooling Center",
                    description="NYC cooling center providing air-conditioned relief during extreme heat events.",
                    street_address=center["address"],
                    city=center["city"],
                    zip_code=center["zip"],
                    borough=center["borough"],
                    phone=center["phone"],
                    service_types=["cooling"],
                    external_id=f"nyc-cooling-{center['name'].lower().replace(' ', '-')}",
                    data_source="NYC Cooling Centers",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error adding cooling center {center['name']}: {e}")
                continue

        print(f"  Loading {len(self.WARMING_CENTERS)} warming centers")

        # Add warming centers
        for center in self.WARMING_CENTERS:
            try:
                results.append(RawServiceData(
                    name=center["name"],
                    organization_name="NYC Warming Center",
                    description="NYC warming center providing heated shelter during extreme cold weather events.",
                    street_address=center["address"],
                    city=center["city"],
                    zip_code=center["zip"],
                    borough=center["borough"],
                    phone=center["phone"],
                    service_types=["warming"],
                    external_id=f"nyc-warming-{center['name'].lower().replace(' ', '-')}",
                    data_source="NYC Warming Centers",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error adding warming center {center['name']}: {e}")
                continue

        return results
