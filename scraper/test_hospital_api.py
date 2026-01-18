"""Test script to explore NYC hospital data."""
import asyncio
import httpx
from collections import Counter


async def test_hospital_data():
    """Test what data is available in the NYC Health Facilities dataset."""
    url = "https://data.cityofnewyork.us/resource/833y-fsy8.json"

    params = {
        "$limit": 100,  # Just get a sample
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    print(f"Fetched {len(data)} sample records\n")

    # Check facility types
    facility_types = Counter()
    sample_records = []

    for record in data:
        ft = record.get("facility_type", "unknown")
        facility_types[ft] += 1

        # Save first record of each type for inspection
        if len([r for r in sample_records if r.get("facility_type") == ft]) == 0:
            sample_records.append(record)

    print("=" * 60)
    print("Facility Types Found:")
    print("=" * 60)
    for ft, count in facility_types.most_common():
        print(f"  {ft}: {count}")

    print("\n" + "=" * 60)
    print("Sample Record Fields:")
    print("=" * 60)
    if sample_records:
        for key in sorted(sample_records[0].keys()):
            print(f"  - {key}")

    print("\n" + "=" * 60)
    print("Sample Hospital Record:")
    print("=" * 60)
    for record in sample_records[:3]:
        print(f"\nFacility: {record.get('facility_name')}")
        print(f"Type: {record.get('facility_type')}")
        print(f"Address: {record.get('address_1')}")
        print(f"City: {record.get('city')}")
        print(f"Borough: {record.get('borough')}")


if __name__ == "__main__":
    asyncio.run(test_hospital_data())
