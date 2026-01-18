"""Test the scraper with just a few locations."""
import asyncio
from scrape_food_hours import search_google_for_hours
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

async def test():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        result = await db.execute(text("""
            SELECT sl.id, sl.name, sl.street_address, sl.city
            FROM service_locations sl
            JOIN location_services ls ON sl.id = ls.location_id
            JOIN service_types st ON ls.service_type_id = st.id
            WHERE st.slug = 'food'
            AND sl.deleted_at IS NULL
            AND NOT EXISTS (
                SELECT 1 FROM operating_hours oh
                WHERE oh.location_id = sl.id
            )
            LIMIT 3
        """))

        locations = result.fetchall()

        print("Testing scraper with 3 locations:\n")

        for loc in locations:
            print(f"Location: {loc.name}")
            print(f"Address: {loc.street_address}, {loc.city}")

            result = await search_google_for_hours(loc.name, loc.street_address, loc.city)

            if result:
                print(f"✓ Found hours:")
                for day, hours in result.get('hours', {}).items():
                    print(f"  {day}: {hours}")
            else:
                print("✗ No hours found")

            print()
            await asyncio.sleep(2)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
