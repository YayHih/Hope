"""Bowery Mission scraper - manual data entry for known locations."""
import httpx
from typing import List
from datetime import datetime, time

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData, OperatingHours, ServiceCapacity


class BoweryMissionScraper(BaseScraper):
    """
    Scrape Bowery Mission locations.

    Note: Bowery Mission has a small number of locations.
    Using manual data entry based on their public information.
    """

    # Known Bowery Mission locations from their website
    LOCATIONS = [
        {
            "name": "Bowery Mission - Women's Center",
            "address": "191 Chrystie Street, New York, NY 10002",
            "phone": "212-253-0122",
            "website": "https://www.bowery.org/location/womens-center/",
            "description": "Women's shelter and services including meals, showers, clothing, and case management for women experiencing homelessness.",
            "services": ["shelter", "food", "hygiene", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 65, "notes": "Women's emergency shelter beds"},
            ],
            "hours": [
                # Monday-Sunday: 24/7 shelter
                {"day": 0, "is_24_hours": True},
                {"day": 1, "is_24_hours": True},
                {"day": 2, "is_24_hours": True},
                {"day": 3, "is_24_hours": True},
                {"day": 4, "is_24_hours": True},
                {"day": 5, "is_24_hours": True},
                {"day": 6, "is_24_hours": True},
            ]
        },
        {
            "name": "Bowery Mission",
            "address": "227 Bowery, New York, NY 10002",
            "phone": "1-800-269-3791",
            "website": "https://www.bowery.org/location/bowery-mission/",
            "description": "Men's shelter and services including hot meals, chapel services, clothing, showers, and addiction recovery programs.",
            "services": ["shelter", "food", "hygiene", "medical", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 180, "notes": "Men's emergency shelter beds"},
            ],
            "hours": [
                # Meals served 7:30am, 12pm, 5pm daily
                # Shelter intake: 4pm-6pm daily
                # Chapel services: 7pm daily
                # 24/7 shelter for residents
                {"day": 0, "is_24_hours": True, "notes": "Meals at 7:30am, 12pm, 5pm. Intake 4-6pm"},
                {"day": 1, "is_24_hours": True, "notes": "Meals at 7:30am, 12pm, 5pm. Intake 4-6pm"},
                {"day": 2, "is_24_hours": True, "notes": "Meals at 7:30am, 12pm, 5pm. Intake 4-6pm"},
                {"day": 3, "is_24_hours": True, "notes": "Meals at 7:30am, 12pm, 5pm. Intake 4-6pm"},
                {"day": 4, "is_24_hours": True, "notes": "Meals at 7:30am, 12pm, 5pm. Intake 4-6pm"},
                {"day": 5, "is_24_hours": True, "notes": "Meals at 7:30am, 12pm, 5pm. Intake 4-6pm"},
                {"day": 6, "is_24_hours": True, "notes": "Meals at 7:30am, 12pm, 5pm. Intake 4-6pm"},
            ]
        },
        {
            "name": "Bowery Mission Transitional Center",
            "address": "90 Lafayette Street, New York, NY 10013",
            "phone": "1-800-269-3791",
            "website": "https://www.bowery.org/programs/",
            "description": "Transitional housing and career training programs for men recovering from addiction and homelessness.",
            "services": ["shelter", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 35, "notes": "Transitional housing program beds"},
            ],
            "hours": [
                # Program-based housing, 24/7 access for residents
                {"day": 0, "is_24_hours": True, "notes": "Residential program"},
                {"day": 1, "is_24_hours": True, "notes": "Residential program"},
                {"day": 2, "is_24_hours": True, "notes": "Residential program"},
                {"day": 3, "is_24_hours": True, "notes": "Residential program"},
                {"day": 4, "is_24_hours": True, "notes": "Residential program"},
                {"day": 5, "is_24_hours": True, "notes": "Residential program"},
                {"day": 6, "is_24_hours": True, "notes": "Residential program"},
            ]
        },
    ]

    async def scrape(self) -> List[RawServiceData]:
        """Return manually curated Bowery Mission locations."""
        print(f"  Using {len(self.LOCATIONS)} manually curated Bowery Mission locations")

        results = []
        for location in self.LOCATIONS:
            try:
                # Parse address
                address_parts = location["address"].split(",")
                street = address_parts[0].strip()
                city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else "New York"
                zip_code = address_parts[2].strip().split()[-1] if len(address_parts) > 2 else None

                # Convert capacities to ServiceCapacity objects
                service_capacities = None
                if "capacities" in location:
                    service_capacities = [
                        ServiceCapacity(
                            service_type=cap["service_type"],
                            capacity=cap["capacity"],
                            notes=cap.get("notes")
                        )
                        for cap in location["capacities"]
                    ]

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
                    organization_name="The Bowery Mission",
                    description=location["description"],
                    street_address=street,
                    city="New York",
                    state="NY",
                    zip_code=zip_code,
                    borough="Manhattan",  # All Bowery Mission locations are in Manhattan
                    phone=location["phone"],
                    website=location.get("website", "https://www.bowery.org"),
                    service_types=location["services"],
                    service_capacities=service_capacities,
                    operating_hours=operating_hours,
                    external_id=str(hash(location["name"])),
                    data_source="Bowery Mission",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error processing Bowery Mission location: {e}")
                continue

        return results
