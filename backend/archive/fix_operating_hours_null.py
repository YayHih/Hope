"""
Fix NULL is_closed values in operating_hours table.
Set is_closed = FALSE for all records where it's NULL.
"""

import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal


async def fix_null_is_closed():
    """Fix NULL is_closed values."""

    async with AsyncSessionLocal() as db:
        try:
            print("=== Fixing NULL is_closed Values ===\n")

            # Count rows with NULL is_closed
            result = await db.execute(text("""
                SELECT COUNT(*) FROM operating_hours WHERE is_closed IS NULL
            """))
            null_count = result.scalar()
            print(f"Found {null_count} rows with NULL is_closed\n")

            # Update NULL is_closed to FALSE
            result = await db.execute(text("""
                UPDATE operating_hours
                SET is_closed = FALSE
                WHERE is_closed IS NULL
            """))

            print(f"✅ Updated {result.rowcount} rows\n")

            await db.commit()

            # Verify
            result = await db.execute(text("""
                SELECT COUNT(*) FROM operating_hours WHERE is_closed IS NULL
            """))
            remaining_null = result.scalar()

            print(f"=== Verification ===")
            print(f"Remaining NULL values: {remaining_null}")
            print("\n=== SUCCESS ===")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ ERROR: {e}")
            raise


if __name__ == "__main__":
    print("Hope for NYC - Fix Operating Hours NULL Values")
    print("=" * 60)
    print()
    asyncio.run(fix_null_is_closed())
