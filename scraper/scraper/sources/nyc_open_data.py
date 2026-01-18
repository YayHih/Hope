"""NYC Open Data scraper - primary data source."""
import httpx
from typing import List
from datetime import datetime

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData
from scraper.config import settings


class NYCOpenDataScraper(BaseScraper):
    """Scrape NYC Open Data API for homeless services."""

    # NYC Open Data endpoints
    API_BASE = "https://data.cityofnewyork.us/resource"

    # Datasets
    DATASETS = {
        "drop_in_centers": "bmxf-3rd4.json",     # Directory of Homeless Drop-In Centers
        "homebase": "ntcm-2w4k.json",            # Homebase Locations (homeless prevention)
        "snap_centers": "tc6u-8rnp.json",        # SNAP Centers (food assistance offices)
    }

    def __init__(self):
        super().__init__()
        self.app_token = settings.NYC_OPEN_DATA_APP_TOKEN

    async def scrape(self) -> List[RawServiceData]:
        """Scrape all NYC Open Data datasets."""
        all_data = []

        # Scrape drop-in centers
        drop_in_data = await self._scrape_drop_in_centers()
        all_data.extend(drop_in_data)

        # Scrape homebase locations
        homebase_data = await self._scrape_homebase()
        all_data.extend(homebase_data)

        # Scrape SNAP centers
        snap_data = await self._scrape_snap_centers()
        all_data.extend(snap_data)

        return all_data

    async def _scrape_drop_in_centers(self) -> List[RawServiceData]:
        """Scrape Directory of Homeless Drop-In Centers dataset."""
        url = f"{self.API_BASE}/{self.DATASETS['drop_in_centers']}"

        headers = {
            "X-App-Token": self.app_token if self.app_token else "",
        }

        params = {
            "$limit": 10000,  # Max records
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        print(f"  Fetched {len(data)} records from Drop-In Centers dataset")

        results = []
        for record in data:
            try:
                # Map service types
                service_types = self._map_service_types(record)
                if not service_types:
                    continue

                # Extract borough from address if available
                borough = self._extract_borough(record)

                results.append(RawServiceData(
                    name=record.get("center_name", "Unknown"),
                    organization_name=None,  # Not provided in this dataset
                    description=record.get("comments"),
                    street_address=record.get("address"),
                    city="New York",
                    zip_code=record.get("postcode"),
                    borough=borough,
                    phone=self._format_phone(record.get("phone")),
                    service_types=service_types,
                    external_id=str(hash(record.get("center_name") + record.get("address", ""))),
                    data_source="NYC Open Data - Drop-In Centers",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error parsing record: {e}")
                continue

        return results

    def _map_service_types(self, record: dict) -> List[str]:
        """
        Map NYC Open Data facility types to our service type slugs.

        Args:
            record: NYC Open Data record

        Returns:
            List of service type slugs
        """
        # For Drop-In Centers dataset, all locations provide food and hygiene
        # This is a safe default for the "Directory of Homeless Drop-In Centers" dataset
        service_types = ["food", "hygiene"]

        # Check center name and comments for additional services
        center_name = record.get("center_name", "").lower()
        comments = record.get("comments", "").lower()

        if "shelter" in center_name or "shelter" in comments:
            service_types.append("shelter")

        if "medical" in center_name or "health" in center_name or "clinic" in center_name:
            service_types.append("medical")

        if "social" in center_name or "case management" in comments:
            service_types.append("social")

        # Remove duplicates
        return list(set(service_types))

    def _extract_borough(self, record: dict) -> str:
        """
        Extract borough from record.

        Args:
            record: NYC Open Data record

        Returns:
            Borough name or None
        """
        # Check for explicit borough field
        borough = record.get("borough")
        if borough:
            return self._normalize_borough(borough)

        # Extract from city field
        city = record.get("city", "")
        if city:
            return self._normalize_borough(city)

        return None

    def _normalize_borough(self, borough: str) -> str:
        """
        Normalize borough names.

        Args:
            borough: Raw borough string

        Returns:
            Normalized borough name
        """
        borough_lower = borough.lower()

        if "manhattan" in borough_lower or "new york" in borough_lower:
            return "Manhattan"
        elif "brooklyn" in borough_lower:
            return "Brooklyn"
        elif "queens" in borough_lower:
            return "Queens"
        elif "bronx" in borough_lower:
            return "Bronx"
        elif "staten" in borough_lower or "richmond" in borough_lower:
            return "Staten Island"

        return None

    def _format_phone(self, phone: str) -> str:
        """
        Format phone number.

        Args:
            phone: Raw phone string

        Returns:
            Formatted phone number or None
        """
        if not phone:
            return None

        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))

        # Format as (XXX) XXX-XXXX if 10 digits
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

        # Return as-is if not 10 digits
        return phone

    async def _scrape_homebase(self) -> List[RawServiceData]:
        """Scrape Homebase locations (homeless prevention services)."""
        url = f"{self.API_BASE}/{self.DATASETS['homebase']}"

        headers = {
            "X-App-Token": self.app_token if self.app_token else "",
        }

        params = {
            "$limit": 10000,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        print(f"  Fetched {len(data)} records from Homebase dataset")

        results = []
        for record in data:
            try:
                # Homebase provides homeless prevention services (social services)
                service_types = ["social"]

                borough = self._normalize_borough(record.get("borough", ""))

                results.append(RawServiceData(
                    name=record.get("homebase_office", "Unknown Homebase"),
                    organization_name="NYC Homebase",
                    description=f"Homebase office serving ZIP codes: {record.get('service_area_zip_code', 'NYC')}. Provides homeless prevention services.",
                    street_address=record.get("address"),
                    city="New York",
                    zip_code=record.get("postcode"),
                    borough=borough,
                    phone=self._format_phone(record.get("phone_number")),
                    service_types=service_types,
                    external_id=str(hash(record.get("homebase_office") + record.get("address", ""))),
                    data_source="NYC Open Data - Homebase",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error parsing Homebase record: {e}")
                continue

        return results

    async def _scrape_snap_centers(self) -> List[RawServiceData]:
        """Scrape SNAP Centers (food assistance/SNAP enrollment)."""
        url = f"{self.API_BASE}/{self.DATASETS['snap_centers']}"

        headers = {
            "X-App-Token": self.app_token if self.app_token else "",
        }

        params = {
            "$limit": 10000,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        print(f"  Fetched {len(data)} records from SNAP Centers dataset")

        results = []
        for record in data:
            try:
                # SNAP Centers help people enroll in food assistance programs
                service_types = ["food", "social"]

                borough = self._normalize_borough(record.get("borough", ""))

                # Parse operating hours from comments
                description = record.get("comments", "SNAP enrollment and food assistance center")

                results.append(RawServiceData(
                    name=record.get("facility_name", "Unknown SNAP Center"),
                    organization_name="NYC Human Resources Administration",
                    description=description,
                    street_address=record.get("street_address"),
                    city=record.get("city", "New York"),
                    zip_code=record.get("zip_code"),
                    borough=borough,
                    phone=self._format_phone(record.get("phone_number_s_")),
                    service_types=service_types,
                    external_id=str(hash(record.get("facility_name") + record.get("street_address", ""))),
                    data_source="NYC Open Data - SNAP Centers",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error parsing SNAP Center record: {e}")
                continue

        return results
