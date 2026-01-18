"""Run the NYC CFC food pantries scraper."""
from datetime import datetime
import signal
from functools import wraps
import time

from scraper.database import get_db
from scraper.sources.nyc_cfc_food_pantries import NYCCFCFoodPantriesScraper
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


def run_cfc_scraper():
    """Run CFC food pantries scraper."""
    print("\n" + "=" * 60)
    print("Hope Platform - NYC CFC Food Pantries Scraper")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize
    scraper = NYCCFCFoodPantriesScraper()
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

            if total_locations == 0:
                print("   ⚠️  No data found. Make sure cfc_active.pdf is in the scraper directory.")
                return

            # Process each location
            locations_added = 0
            locations_updated = 0
            locations_skipped = 0
            locations_failed = 0

            for idx, data in enumerate(raw_data, 1):
                percentage = (idx / total_locations) * 100
                print(f"\n[{idx}/{total_locations} - {percentage:.1f}%] Processing: {data.name}")

                try:
                    # RESUMABLE SCRAPER: Check if this location already has valid coordinates
                    existing = deduplicator.find_match(data)
                    if existing and existing.latitude and existing.longitude and existing.latitude != 0 and existing.longitude != 0:
                        print(f"    ⏭️  [Skipping] {data.name} - Already geocoded")
                        # Still update the record with new data (services, hours, etc.)
                        location = deduplicator.create_or_update(data, (existing.latitude, existing.longitude))
                        locations_updated += 1

                        # Update services and hours
                        deduplicator.add_services(location, data.service_types, data.service_capacities)
                        deduplicator.add_operating_hours(location, data.operating_hours)
                        db.commit()
                        continue

                    # Geocode address to get coordinates
                    if not data.street_address:
                        print(f"    ⚠️  No address provided, skipping")
                        locations_skipped += 1
                        continue

                    # Create geocoding function with timeout
                    import asyncio

                    async def geocode_async():
                        # FIX: Use borough name for Manhattan to improve geocoding accuracy
                        # Nominatim works better with "Manhattan, NY" than "New York, NY"
                        city_for_geocoding = data.city
                        if data.borough and data.borough in ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island']:
                            city_for_geocoding = data.borough

                        return await geocoder.geocode_with_fallback(
                            address=data.street_address,
                            city=city_for_geocoding,
                            state=data.state,
                            zip_code=data.zip_code,
                            borough=data.borough
                        )

                    @timeout(30)
                    def geocode_with_timeout():
                        return asyncio.run(geocode_async())

                    try:
                        coords = geocode_with_timeout()
                        if coords:
                            latitude, longitude = coords
                            print(f"    ✓ Geocoded: ({latitude}, {longitude})")

                            # RATE LIMITING: Sleep 1.2s to respect Nominatim's 1 req/sec limit
                            time.sleep(1.2)
                        else:
                            print(f"    ⚠️  Could not geocode, skipping")
                            locations_skipped += 1
                            continue
                    except TimeoutError:
                        print(f"    ⏱️  Geocoding timed out after 30s, skipping")
                        locations_skipped += 1
                        continue

                    # Check if this is new or existing before creating (already checked above for skip logic)
                    if not existing:
                        existing = deduplicator.find_match(data)

                    # Create or update in database
                    location = deduplicator.create_or_update(data, coords)

                    if existing:
                        locations_updated += 1
                        print(f"    ✓ Updated existing location: {location.id}")
                    else:
                        locations_added += 1
                        print(f"    ✓ Added new location: {location.id}")

                    # Add service types
                    deduplicator.add_services(location, data.service_types, data.service_capacities)
                    print(f"    ✓ Added services: {', '.join(data.service_types)}")

                    # Add operating hours
                    deduplicator.add_operating_hours(location, data.operating_hours)
                    if data.operating_hours:
                        print(f"    ✓ Added {len(data.operating_hours)} operating hours entries")

                    # Commit after each successful location
                    db.commit()

                except Exception as e:
                    locations_failed += 1
                    print(f"    ❌ Failed to process: {str(e)}")
                    # Rollback the transaction on error
                    db.rollback()
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
    run_cfc_scraper()
