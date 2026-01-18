"""Geocoding processor using Nominatim (OpenStreetMap)."""
import httpx
from typing import Optional, Tuple
import asyncio

from scraper.config import settings


class Geocoder:
    """Geocode addresses using Nominatim (free, no API key required)."""

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self):
        self.user_agent = settings.USER_AGENT

    async def geocode(
        self,
        address: str,
        city: str = "New York",
        state: str = "NY"
    ) -> Optional[Tuple[float, float]]:
        """
        Geocode an address to latitude/longitude.

        Args:
            address: Street address
            city: City name
            state: State code

        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        if not address:
            return None

        full_address = f"{address}, {city}, {state}"

        headers = {
            "User-Agent": self.user_agent  # Required by Nominatim
        }

        params = {
            "q": full_address,
            "format": "json",
            "limit": 1,
            "countrycodes": "us",  # Limit to US
        }

        try:
            # Add small delay to respect Nominatim rate limits
            await asyncio.sleep(1)

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    headers=headers,
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        result = data[0]
                        lat = float(result["lat"])
                        lon = float(result["lon"])
                        return (lat, lon)

        except Exception as e:
            print(f"  ⚠️  Geocoding failed for {address}: {e}")

        return None

    async def geocode_with_fallback(
        self,
        address: str,
        city: str = "New York",
        state: str = "NY",
        zip_code: Optional[str] = None,
        borough: Optional[str] = None
    ) -> Optional[Tuple[float, float]]:
        """
        Geocode with fallback strategies.

        Tries:
        1. Full address
        2. ZIP code + city
        3. Borough center (approximate)

        Args:
            address: Street address
            city: City name
            state: State code
            zip_code: ZIP code (optional)
            borough: Borough name (optional)

        Returns:
            Tuple of (latitude, longitude) or None
        """
        # Try full address first
        coords = await self.geocode(address, city, state)
        if coords:
            return coords

        # Try ZIP code if available
        if zip_code:
            coords = await self.geocode(zip_code, city, state)
            if coords:
                print(f"  ℹ️  Used ZIP code for geocoding: {zip_code}")
                return coords

        # Fallback to borough center (very approximate)
        if borough:
            coords = self._borough_center(borough)
            if coords:
                print(f"  ℹ️  Used borough center for geocoding: {borough}")
                return coords

        return None

    def _borough_center(self, borough: str) -> Optional[Tuple[float, float]]:
        """
        Get approximate center coordinates for NYC boroughs.

        Args:
            borough: Borough name

        Returns:
            Tuple of (latitude, longitude) or None
        """
        borough_centers = {
            "Manhattan": (40.7831, -73.9712),
            "Brooklyn": (40.6782, -73.9442),
            "Queens": (40.7282, -73.7949),
            "Bronx": (40.8448, -73.8648),
            "Staten Island": (40.5795, -74.1502),
        }

        return borough_centers.get(borough)
