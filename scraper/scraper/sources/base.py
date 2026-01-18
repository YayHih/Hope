"""Base scraper class."""
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

from scraper.models import RawServiceData


class BaseScraper(ABC):
    """Base class for all data source scrapers."""

    def __init__(self):
        self.source_name = self.__class__.__name__
        self.results: List[RawServiceData] = []

    @abstractmethod
    async def scrape(self) -> List[RawServiceData]:
        """
        Implement scraping logic in subclass.

        Returns:
            List of RawServiceData objects
        """
        pass

    def validate_result(self, data: RawServiceData) -> bool:
        """
        Basic validation of scraped data.

        Args:
            data: RawServiceData to validate

        Returns:
            True if data is valid, False otherwise
        """
        if not data.name:
            print(f"  ❌ Missing name")
            return False

        if not data.street_address:
            print(f"  ❌ Missing address for {data.name}")
            return False

        if not data.service_types:
            print(f"  ❌ No service types for {data.name}")
            return False

        return True

    async def run(self) -> List[RawServiceData]:
        """
        Main execution method.

        Returns:
            List of valid RawServiceData objects
        """
        print(f"\n{'='*60}")
        print(f"Starting scraper: {self.source_name}")
        print(f"{'='*60}")

        try:
            raw_data = await self.scrape()
            print(f"  Scraped {len(raw_data)} records")

            # Filter out invalid results
            valid_data = [d for d in raw_data if self.validate_result(d)]
            print(f"  ✓ {len(valid_data)} valid records")

            return valid_data

        except Exception as e:
            print(f"  ❌ Scraper failed: {e}")
            return []
