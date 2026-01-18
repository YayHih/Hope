"""NYC DHS Shelter scraper using official Open Data sources."""
import httpx
from typing import List
from datetime import datetime

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData, ServiceCapacity


class NYCDHSShelterScraper(BaseScraper):
    """
    Scraper for NYC Department of Homeless Services shelter facilities.

    Data sources:
    - Shelter Repair Scorecard (dvaj-b7yx): Official DHS building list with capacity
    - Directory of Homeless Drop-In Centers (bmxf-3rd4): Geocoded drop-in centers

    Note: The Scorecard dataset has shelter names, boroughs, types, and capacity
    but lacks street addresses. We use building names to match when possible.
    """

    SCORECARD_API = "https://data.cityofnewyork.us/resource/dvaj-b7yx.json"
    DROPIN_API = "https://data.cityofnewyork.us/resource/bmxf-3rd4.json"

    async def scrape(self) -> List[RawServiceData]:
        """Scrape DHS shelter data from NYC Open Data."""
        results = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get drop-in centers (these have addresses and coordinates)
            print(f"  Fetching drop-in centers with addresses...")
            dropin_response = await client.get(
                self.DROPIN_API,
                params={"$limit": 500}
            )
            dropin_response.raise_for_status()
            dropin_centers = dropin_response.json()

            print(f"  Found {len(dropin_centers)} drop-in centers")

            # Process drop-in centers
            for center in dropin_centers:
                try:
                    # Parse address
                    address_full = center.get("address", "")
                    address_parts = address_full.split(";")
                    street_address = address_parts[0].strip() if address_parts else None

                    # Determine if 24 hours from comments
                    comments = center.get("comments", "")
                    is_24_hours = "24 hours" in comments.lower() or "open 24" in comments.lower()

                    # Operating hours based on comments
                    operating_hours = None
                    if is_24_hours:
                        from scraper.models import OperatingHours
                        operating_hours = [
                            OperatingHours(
                                day_of_week=day,
                                is_24_hours=True,
                                notes=comments if comments else "24 hour access"
                            )
                            for day in range(7)
                        ]
                    elif "7:30 a.m.-8:30 p.m." in comments:
                        from scraper.models import OperatingHours
                        from datetime import time
                        operating_hours = [
                            OperatingHours(
                                day_of_week=day,
                                open_time=time(7, 30),
                                close_time=time(20, 30),
                                notes=comments
                            )
                            for day in range(7)
                        ]

                    results.append(RawServiceData(
                        name=center.get("center_name", "Unknown"),
                        organization_name="NYC DHS",
                        description=f"Drop-in center. {comments}",
                        street_address=street_address,
                        city="New York",
                        state="NY",
                        zip_code=center.get("postcode"),
                        borough=center.get("borough"),
                        service_types=["social", "hygiene"],  # Drop-in centers provide day services
                        operating_hours=operating_hours,
                        external_id=f"dhs-dropin-{center.get('center_name', '').replace(' ', '-').lower()}",
                        data_source="NYC DHS Drop-In Centers",
                        scraped_at=datetime.now(),
                    ))
                except Exception as e:
                    print(f"  Error processing drop-in center: {e}")
                    continue

            # Get unique shelters from Scorecard (using December 2022 data)
            print(f"  Fetching DHS shelter buildings...")

            # Get all shelters from one month to avoid duplicates
            scorecard_response = await client.get(
                self.SCORECARD_API,
                params={
                    "month": "2022-12-01T00:00:00.000",
                    "$limit": 5000
                }
            )
            scorecard_response.raise_for_status()
            shelters = scorecard_response.json()

            print(f"  Found {len(shelters)} unique DHS shelter buildings")

            # Process shelters (without addresses - will need geocoding)
            for shelter in shelters:
                try:
                    shelter_name_full = shelter.get("shelter_name_all", "")

                    # Extract shelter name and operator from combined field
                    # Format: "Bld ID: 92456 -- SHELTER NAME, OPERATOR, Type -- Borough"
                    parts = shelter_name_full.split("--")
                    shelter_name = parts[1].strip() if len(parts) > 1 else shelter_name_full

                    # Further parse: "NAME, OPERATOR, Type"
                    name_parts = shelter_name.split(",")
                    actual_name = name_parts[0].strip() if name_parts else shelter_name
                    operator = name_parts[1].strip() if len(name_parts) > 1 else "NYC DHS"

                    capacity_value = None
                    try:
                        capacity_value = int(shelter.get("capacity", 0))
                    except (ValueError, TypeError):
                        pass

                    service_capacities = None
                    if capacity_value and capacity_value > 0:
                        service_capacities = [
                            ServiceCapacity(
                                service_type="shelter",
                                capacity=capacity_value,
                                notes=shelter.get("facility_type")
                            )
                        ]

                    # Operating hours: Assume 24/7 for shelters
                    from scraper.models import OperatingHours
                    operating_hours = [
                        OperatingHours(
                            day_of_week=day,
                            is_24_hours=True,
                            notes="Call for intake procedures"
                        )
                        for day in range(7)
                    ]

                    results.append(RawServiceData(
                        name=actual_name,
                        organization_name=operator,
                        description=f"{shelter.get('facility_type', 'Shelter')} operated by {operator}",
                        # NO STREET ADDRESS - will need geocoding based on name/borough
                        street_address=None,
                        city="New York",
                        state="NY",
                        borough=shelter.get("borough"),
                        service_types=["shelter"],
                        service_capacities=service_capacities,
                        operating_hours=operating_hours,
                        external_id=f"dhs-shelter-{shelter.get('dhs_bld_id')}",
                        data_source="NYC DHS Shelter Scorecard",
                        scraped_at=datetime.now(),
                    ))
                except Exception as e:
                    print(f"  Error processing shelter: {e}")
                    continue

        return results
