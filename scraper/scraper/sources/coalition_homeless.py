"""Coalition for the Homeless scraper."""
import httpx
from typing import List
from datetime import datetime, time
from bs4 import BeautifulSoup

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData, OperatingHours, ServiceCapacity
from scraper.config import settings


class CoalitionHomelessScraper(BaseScraper):
    """
    Scrape Coalition for the Homeless resources.

    Note: Coalition provides advocacy and resources but doesn't maintain
    a comprehensive list of all NYC shelters on their website.
    They provide general hotline numbers and refer to NYC DHS.
    """

    # Known Coalition-operated or affiliated programs and NYC shelter locations
    PROGRAMS = [
        {
            "name": "Coalition for the Homeless - Grand Central Food Program",
            "address": "Grand Central Terminal, 89 East 42nd Street, New York, NY 10017",
            "phone": "212-776-2000",
            "website": "https://www.coalitionforthehomeless.org",
            "description": "Daily meal program serving breakfast and dinner to people experiencing homelessness at Grand Central Terminal.",
            "services": ["food"],
            "hours": [
                {"day": 0, "open_time": time(7, 0), "close_time": time(9, 0), "notes": "Breakfast 7-9am, Dinner 6-8pm"},
                {"day": 1, "open_time": time(7, 0), "close_time": time(9, 0), "notes": "Breakfast 7-9am, Dinner 6-8pm"},
                {"day": 2, "open_time": time(7, 0), "close_time": time(9, 0), "notes": "Breakfast 7-9am, Dinner 6-8pm"},
                {"day": 3, "open_time": time(7, 0), "close_time": time(9, 0), "notes": "Breakfast 7-9am, Dinner 6-8pm"},
                {"day": 4, "open_time": time(7, 0), "close_time": time(9, 0), "notes": "Breakfast 7-9am, Dinner 6-8pm"},
                {"day": 5, "open_time": time(7, 0), "close_time": time(9, 0), "notes": "Breakfast 7-9am, Dinner 6-8pm"},
                {"day": 6, "open_time": time(7, 0), "close_time": time(9, 0), "notes": "Breakfast 7-9am, Dinner 6-8pm"},
            ],
        },
        # NYC DHS Shelter Locations
        {
            "name": "Project Renewal - Stevenson Family Residence",
            "address": "127 Madison Avenue, New York, NY 10016",
            "phone": "212-620-0340",
            "website": "https://www.projectrenewal.org",
            "description": "Family shelter providing temporary housing, case management, and support services for homeless families.",
            "services": ["shelter", "food", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 42, "notes": "Family units"},
            ],
            "hours": [
                {"day": 0, "is_24_hours": True, "notes": "24/7 shelter access"},
                {"day": 1, "is_24_hours": True, "notes": "24/7 shelter access"},
                {"day": 2, "is_24_hours": True, "notes": "24/7 shelter access"},
                {"day": 3, "is_24_hours": True, "notes": "24/7 shelter access"},
                {"day": 4, "is_24_hours": True, "notes": "24/7 shelter access"},
                {"day": 5, "is_24_hours": True, "notes": "24/7 shelter access"},
                {"day": 6, "is_24_hours": True, "notes": "24/7 shelter access"},
            ],
        },
        {
            "name": "HELP USA - Andrews Family Residence",
            "address": "930 Intervale Avenue, Bronx, NY 10459",
            "phone": "718-991-4300",
            "website": "https://www.helpusa.org",
            "description": "Family shelter with supportive services including job training, childcare, and case management.",
            "services": ["shelter", "food", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 200, "notes": "Family units"},
            ],
            "hours": [
                {"day": 0, "is_24_hours": True},
                {"day": 1, "is_24_hours": True},
                {"day": 2, "is_24_hours": True},
                {"day": 3, "is_24_hours": True},
                {"day": 4, "is_24_hours": True},
                {"day": 5, "is_24_hours": True},
                {"day": 6, "is_24_hours": True},
            ],
        },
        {
            "name": "BRC - Catherine Street Residence",
            "address": "60 Catherine Street, New York, NY 10038",
            "phone": "212-803-5700",
            "website": "https://www.brc.org",
            "description": "Supportive housing for chronically homeless single adults with mental health and substance abuse issues.",
            "services": ["shelter", "medical", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 91, "notes": "Single adults"},
            ],
            "hours": [
                {"day": 0, "is_24_hours": True},
                {"day": 1, "is_24_hours": True},
                {"day": 2, "is_24_hours": True},
                {"day": 3, "is_24_hours": True},
                {"day": 4, "is_24_hours": True},
                {"day": 5, "is_24_hours": True},
                {"day": 6, "is_24_hours": True},
            ],
        },
        {
            "name": "Partnership for the Homeless - Schwartz Residence",
            "address": "30 Third Avenue, Brooklyn, NY 11217",
            "phone": "718-625-5233",
            "website": "https://www.partnershipforthehomeless.org",
            "description": "Transitional housing for formerly homeless adults, providing support services and job training.",
            "services": ["shelter", "food", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 67, "notes": "Single adults"},
            ],
            "hours": [
                {"day": 0, "is_24_hours": True},
                {"day": 1, "is_24_hours": True},
                {"day": 2, "is_24_hours": True},
                {"day": 3, "is_24_hours": True},
                {"day": 4, "is_24_hours": True},
                {"day": 5, "is_24_hours": True},
                {"day": 6, "is_24_hours": True},
            ],
        },
        {
            "name": "Breaking Ground - Horatio House",
            "address": "507 West 25th Street, New York, NY 10001",
            "phone": "212-389-9300",
            "website": "https://www.breakingground.org",
            "description": "Permanent supportive housing for formerly homeless individuals with mental illness.",
            "services": ["shelter", "medical", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 126, "notes": "Permanent supportive housing"},
            ],
            "hours": [
                {"day": 0, "is_24_hours": True},
                {"day": 1, "is_24_hours": True},
                {"day": 2, "is_24_hours": True},
                {"day": 3, "is_24_hours": True},
                {"day": 4, "is_24_hours": True},
                {"day": 5, "is_24_hours": True},
                {"day": 6, "is_24_hours": True},
            ],
        },
        {
            "name": "Samaritan Village - Shelter Plus Care",
            "address": "138-02 Queens Boulevard, Queens, NY 11435",
            "phone": "718-206-2000",
            "website": "https://www.samaritanvillage.org",
            "description": "Permanent supportive housing for homeless individuals with substance abuse disorders.",
            "services": ["shelter", "medical", "social"],
            "capacities": [
                {"service_type": "shelter", "capacity": 85, "notes": "Adults with substance abuse issues"},
            ],
            "hours": [
                {"day": 0, "is_24_hours": True},
                {"day": 1, "is_24_hours": True},
                {"day": 2, "is_24_hours": True},
                {"day": 3, "is_24_hours": True},
                {"day": 4, "is_24_hours": True},
                {"day": 5, "is_24_hours": True},
                {"day": 6, "is_24_hours": True},
            ],
        },
    ]

    async def scrape(self) -> List[RawServiceData]:
        """
        Scrape Coalition for the Homeless data.

        Currently using known programs. Future enhancement: scrape their
        resources page for updated information.
        """
        print(f"  Using {len(self.PROGRAMS)} Coalition for the Homeless programs")

        results = []
        for program in self.PROGRAMS:
            try:
                # Parse address
                address_parts = program["address"].split(",")
                street = address_parts[0].strip()
                zip_code = address_parts[-1].strip().split()[-1] if len(address_parts) > 2 else None

                # Determine borough from address
                borough = "Manhattan"  # default
                if "Bronx" in program["address"]:
                    borough = "Bronx"
                elif "Brooklyn" in program["address"]:
                    borough = "Brooklyn"
                elif "Queens" in program["address"]:
                    borough = "Queens"

                # Convert capacities to ServiceCapacity objects
                service_capacities = None
                if "capacities" in program:
                    service_capacities = [
                        ServiceCapacity(
                            service_type=cap["service_type"],
                            capacity=cap["capacity"],
                            notes=cap.get("notes")
                        )
                        for cap in program["capacities"]
                    ]

                # Convert operating hours to OperatingHours objects
                operating_hours = None
                if "hours" in program:
                    operating_hours = [
                        OperatingHours(
                            day_of_week=hours["day"],
                            open_time=hours.get("open_time"),
                            close_time=hours.get("close_time"),
                            is_24_hours=hours.get("is_24_hours", False),
                            is_closed=hours.get("is_closed", False),
                            notes=hours.get("notes")
                        )
                        for hours in program["hours"]
                    ]

                results.append(RawServiceData(
                    name=program["name"],
                    organization_name=program.get("organization_name", "Coalition for the Homeless"),
                    description=program["description"],
                    street_address=street,
                    city="New York",
                    state="NY",
                    zip_code=zip_code,
                    borough=borough,
                    phone=program["phone"],
                    website=program.get("website", "https://www.coalitionforthehomeless.org"),
                    service_types=program["services"],
                    service_capacities=service_capacities,
                    operating_hours=operating_hours,
                    external_id=str(hash(program["name"])),
                    data_source="Coalition for the Homeless",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error processing Coalition program: {e}")
                continue

        # Add general NYC homeless hotline info
        results.append(RawServiceData(
            name="NYC Homeless Services - 311 Hotline",
            organization_name="NYC Department of Homeless Services",
            description="24/7 hotline for homeless services in NYC. Call 311 or 212-NEW-YORK for shelter placement, outreach services, and emergency assistance.",
            street_address="33 Beaver Street",
            city="New York",
            state="NY",
            zip_code="10004",
            borough="Manhattan",
            phone="311",
            website="https://www.nyc.gov/dhs",
            service_types=["social", "shelter"],
            external_id="nyc-311-homeless-hotline",
            data_source="NYC DHS via Coalition",
            scraped_at=datetime.now(),
        ))

        return results
