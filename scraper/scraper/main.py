"""Main scraper execution script."""
import asyncio
from datetime import datetime

from scraper.database import get_db
from scraper.sources.nyc_open_data import NYCOpenDataScraper
from scraper.sources.nyc_hospitals import NYCHospitalsScraper
from scraper.sources.nyc_cooling_warming import NYCCoolingWarmingScraper
from scraper.sources.bowery_mission import BoweryMissionScraper
from scraper.sources.coalition_homeless import CoalitionHomelessScraper
from scraper.sources.nyc_relief import NYCReliefScraper
from scraper.sources.foodbank_nyc import FoodBankNYCScraper
from scraper.sources.nyc_shelters_comprehensive import NYCSheltersComprehensiveScraper
from scraper.sources.nyc_major_shelters import NYCMajorSheltersScraper
from scraper.processors.geocoding import Geocoder
from scraper.processors.deduplication import Deduplicator


async def run_all_scrapers():
    """Run all configured scrapers."""
    print("\n" + "=" * 60)
    print("Hope Platform - Data Scraper")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize scrapers
    scrapers = [
        NYCOpenDataScraper(),
        NYCHospitalsScraper(),
        NYCCoolingWarmingScraper(),
        BoweryMissionScraper(),
        CoalitionHomelessScraper(),
        NYCReliefScraper(),
        FoodBankNYCScraper(),
        NYCSheltersComprehensiveScraper(),
        NYCMajorSheltersScraper(),
    ]

    # Initialize processors
    geocoder = Geocoder()

    stats = {
        "total_scraped": 0,
        "total_valid": 0,
        "total_geocoded": 0,
        "total_created": 0,
        "total_updated": 0,
        "total_failed": 0,
    }

    with get_db() as db:
        deduplicator = Deduplicator(db)

        for scraper in scrapers:
            print(f"\n{'='*60}")
            print(f"Running: {scraper.source_name}")
            print(f"{'='*60}")

            # Scrape data
            raw_data = await scraper.run()
            stats["total_scraped"] += len(raw_data)
            stats["total_valid"] += len(raw_data)

            # Process each record
            for i, data in enumerate(raw_data, 1):
                print(f"\n  [{i}/{len(raw_data)}] Processing: {data.name}")

                try:
                    # Geocode address
                    coords = await geocoder.geocode_with_fallback(
                        address=data.street_address,
                        city=data.city,
                        state=data.state,
                        zip_code=data.zip_code,
                        borough=data.borough
                    )

                    if not coords:
                        print(f"    ❌ Failed to geocode: {data.street_address}")
                        stats["total_failed"] += 1
                        continue

                    stats["total_geocoded"] += 1
                    lat, lon = coords
                    print(f"    ✓ Geocoded: ({lat:.4f}, {lon:.4f})")

                    # Create or update location
                    existing = deduplicator.find_match(data)
                    location = deduplicator.create_or_update(data, coords)

                    if existing:
                        stats["total_updated"] += 1
                    else:
                        stats["total_created"] += 1

                    # Add service types and capacity
                    deduplicator.add_services(location, data.service_types, data.service_capacities)
                    print(f"    ✓ Added services: {', '.join(data.service_types)}")

                    # Add operating hours
                    deduplicator.add_operating_hours(location, data.operating_hours)
                    if data.operating_hours:
                        print(f"    ✓ Added {len(data.operating_hours)} operating hours entries")

                    # Commit after each location
                    db.commit()

                except Exception as e:
                    print(f"    ❌ Error processing {data.name}: {e}")
                    stats["total_failed"] += 1
                    db.rollback()
                    continue

    # Print final statistics
    print("\n" + "=" * 60)
    print("Scraping Complete")
    print("=" * 60)
    print(f"Total scraped:  {stats['total_scraped']}")
    print(f"Total valid:    {stats['total_valid']}")
    print(f"Total geocoded: {stats['total_geocoded']}")
    print(f"Total created:  {stats['total_created']}")
    print(f"Total updated:  {stats['total_updated']}")
    print(f"Total failed:   {stats['total_failed']}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")


def main():
    """CLI entry point."""
    asyncio.run(run_all_scrapers())


if __name__ == "__main__":
    main()
