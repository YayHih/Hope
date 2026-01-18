"""
Update service type ordering and deactivate old shelter type.
Puts Intake Center and Drop-In Center right after Food.
"""

import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal


async def update_service_type_order():
    """Update service type sort order and deactivate shelter."""

    async with AsyncSessionLocal() as db:
        try:
            print("=== Updating Service Type Order ===\n")

            # Define new sort order
            # Food (1), Intake (2), Drop-In (3), then others
            sort_order_map = {
                'food': 1,
                'intake': 2,
                'drop-in': 3,
                'hygiene': 4,
                'medical': 5,
                'social': 6,
                'warming': 7,
                'cooling': 8,
                'hospitals': 9,
                'shelter': 999  # Push to end (will be deactivated)
            }

            for slug, order in sort_order_map.items():
                await db.execute(text("""
                    UPDATE service_types
                    SET sort_order = :order
                    WHERE slug = :slug
                """), {"slug": slug, "order": order})
                print(f"✅ {slug}: sort_order = {order}")

            # Deactivate old shelter type
            await db.execute(text("""
                UPDATE service_types
                SET active = FALSE
                WHERE slug = 'shelter'
            """))
            print(f"\n❌ Deactivated 'shelter' service type")

            await db.commit()

            print("\n=== Verification ===")
            result = await db.execute(text("""
                SELECT name, slug, sort_order, active
                FROM service_types
                WHERE active = TRUE
                ORDER BY sort_order
            """))
            types = result.fetchall()

            print("\nActive Service Types (in display order):")
            for i, t in enumerate(types, 1):
                print(f"{i}. {t[0]} ({t[1]}) - sort_order: {t[2]}")

            print("\n=== SUCCESS ===")
            print("Service type order updated successfully!")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ ERROR: {e}")
            raise


if __name__ == "__main__":
    print("Hope for NYC - Service Type Order Update")
    print("=" * 60)
    print()
    asyncio.run(update_service_type_order())
