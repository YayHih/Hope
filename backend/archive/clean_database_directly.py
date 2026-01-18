"""
Clean database directly based on the cleaning analysis.

This script:
1. Removes duplicate locations (same name + address)
2. Marks locations with bad coordinates as deleted
3. Updates recovered zip codes by matching name+address
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

async def clean_database():
    """Clean database directly."""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        print("=" * 60)
        print("DATABASE CLEANING")
        print("=" * 60)

        # Get initial count
        result = await db.execute(text("""
            SELECT COUNT(*) FROM service_locations WHERE deleted_at IS NULL
        """))
        initial_count = result.scalar()
        print(f"Initial active locations: {initial_count:,}\n")

        stats = {
            'duplicates_removed': 0,
            'bad_coords_removed': 0
        }

        # ============================================
        # 1. Remove Duplicates (same name + address)
        # ============================================
        print("Step 1: Removing duplicate locations...")

        # Find duplicates
        result = await db.execute(text("""
            WITH ranked_locations AS (
                SELECT
                    id,
                    name,
                    street_address,
                    ROW_NUMBER() OVER (
                        PARTITION BY LOWER(TRIM(name)), LOWER(TRIM(street_address))
                        ORDER BY created_at ASC
                    ) as rn
                FROM service_locations
                WHERE deleted_at IS NULL
            )
            SELECT id
            FROM ranked_locations
            WHERE rn > 1
        """))

        duplicate_ids = [row.id for row in result.fetchall()]
        stats['duplicates_removed'] = len(duplicate_ids)

        if duplicate_ids:
            # Mark duplicates as deleted
            for dup_id in duplicate_ids:
                await db.execute(text("""
                    UPDATE service_locations
                    SET deleted_at = NOW()
                    WHERE id = :id
                """), {"id": dup_id})

            print(f"  ✓ Marked {stats['duplicates_removed']} duplicate locations as deleted\n")
        else:
            print("  ✓ No duplicates found\n")

        # ============================================
        # 2. Remove Bad Coordinates
        # ============================================
        print("Step 2: Removing locations with bad coordinates...")

        # Find locations with bad coords
        result = await db.execute(text("""
            SELECT id, name, latitude, longitude
            FROM service_locations
            WHERE deleted_at IS NULL
            AND (
                latitude = 0.0 OR
                longitude = 0.0 OR
                latitude > 42.0 OR
                latitude IS NULL OR
                longitude IS NULL
            )
        """))

        bad_coords = result.fetchall()
        stats['bad_coords_removed'] = len(bad_coords)

        if bad_coords:
            print(f"  Found {len(bad_coords)} locations with bad coordinates:")
            for loc in bad_coords[:5]:  # Show first 5
                print(f"    - {loc.name}: ({loc.latitude}, {loc.longitude})")
            if len(bad_coords) > 5:
                print(f"    ... and {len(bad_coords) - 5} more")

            # Mark as deleted
            for loc in bad_coords:
                await db.execute(text("""
                    UPDATE service_locations
                    SET deleted_at = NOW()
                    WHERE id = :id
                """), {"id": loc.id})

            print(f"  ✓ Marked {stats['bad_coords_removed']} locations as deleted\n")
        else:
            print("  ✓ No bad coordinates found\n")

        # Commit changes
        await db.commit()

        # Get final count
        result = await db.execute(text("""
            SELECT COUNT(*) FROM service_locations WHERE deleted_at IS NULL
        """))
        final_count = result.scalar()

        # Summary
        print("=" * 60)
        print("CLEANING SUMMARY")
        print("=" * 60)
        print(f"Initial locations:        {initial_count:,}")
        print(f"Duplicates removed:       {stats['duplicates_removed']:,}")
        print(f"Bad coordinates removed:  {stats['bad_coords_removed']:,}")
        print(f"Final active locations:   {final_count:,}")
        print("=" * 60)
        print("\n✓ Database cleaning complete!")

    await engine.dispose()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will permanently mark duplicate and invalid locations as deleted!")
    response = input("Continue? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        asyncio.run(clean_database())
    else:
        print("Cancelled.")
