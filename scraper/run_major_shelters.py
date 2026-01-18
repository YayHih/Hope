"""Run just the major shelters scraper."""
from datetime import datetime
import signal
from functools import wraps

from scraper.database import get_db
from scraper.sources.nyc_major_shelters import NYCMajorSheltersScraper
from scraper.processors.geocoding import Geocoder
from scraper.processors.deduplication import Deduplicator


class TimeoutError(Exception):
    """Raised when operation times out."""
    pass


def timeout(seconds):
    """Decorator to add timeout to a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Operation timed out after {seconds} seconds")

            # Set the signal handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                # Restore the old signal handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result
        return wrapper
    return decorator


def run_major_shelters_scraper():
    """Run major shelters scraper only."""
    print("\n" + "=" * 60)
    print("Hope Platform - Major NYC Shelters Scraper")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize
    scraper = NYCMajorSheltersScraper()
    geocoder = Geocoder()

    # Get database session
    with get_db() as db:
        deduplicator = Deduplicator(db)

        try:
            # Scrape data
            print(f"\n📥 Scraping {scraper.source_name}...")
            raw_data = scraper.scrape()
            total_locations = len(raw_data)
            print(f"   Found {total_locations} locations")

            # Process each location
            locations_added = 0
            locations_updated = 0
            locations_skipped = 0
            locations_failed = 0

            for idx, data in enumerate(raw_data, 1):
                percentage = (idx / total_locations) * 100
                print(f"\n[{idx}/{total_locations} - {percentage:.1f}%] Processing: {data.name}")

                try:
                    # Geocode address to get coordinates
                    if not data.street_address:
                        print(f"    ⚠️  No address provided, skipping")
                        locations_skipped += 1
                        continue

                    # Create geocoding function with timeout
                    import asyncio

                    async def geocode_async():
                        return await geocoder.geocode(
                            address=data.street_address,
                            city=data.city,
                            state=data.state
                        )

                    @timeout(30)
                    def geocode_with_timeout():
                        return asyncio.run(geocode_async())

                    try:
                        coords = geocode_with_timeout()
                        if coords:
                            latitude, longitude = coords
                            print(f"    ✓ Geocoded: ({latitude}, {longitude})")
                        else:
                            print(f"    ⚠️  Could not geocode, skipping")
                            locations_skipped += 1
                            continue
                    except TimeoutError:
                        print(f"    ⏱️  Geocoding timed out after 30s, skipping")
                        locations_skipped += 1
                        continue

                    # Check if this is new or existing before creating
                    existing = deduplicator.find_match(data)

                    # Create or update in database
                    location = deduplicator.create_or_update(data, coords)

                    if existing:
                        locations_updated += 1
                        print(f"    ✓ Updated existing location: {location.id}")
                    else:
                        locations_added += 1
                        print(f"    ✓ Added new location: {location.id}")

                    # Add service types and capacity
                    deduplicator.add_services(location, data.service_types, data.service_capacities)
                    print(f"    ✓ Added services: {', '.join(data.service_types)}")

                    # Add operating hours
                    deduplicator.add_operating_hours(location, data.operating_hours)
                    if data.operating_hours:
                        print(f"    ✓ Added {len(data.operating_hours)} operating hours entries")

                except Exception as e:
                    locations_failed += 1
                    print(f"    ❌ Failed to process: {str(e)}")
                    continue

            print(f"\n" + "=" * 60)
            print(f"✅ Scraper completed!")
            print(f"   New locations added: {locations_added}")
            print(f"   Existing locations updated: {locations_updated}")
            print(f"   Locations skipped (no geocode): {locations_skipped}")
            print(f"   Locations failed: {locations_failed}")
            print(f"   Total processed successfully: {locations_added + locations_updated}")
            print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error during scraping: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    run_major_shelters_scraper()
