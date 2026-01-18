"""
Clean service locations CSV dataset.

This script performs the following operations:
1. Remove duplicate entries (same name and address)
2. Extract missing zip codes from addresses
3. Identify and separate locations with bad coordinates
4. Fill missing operating hours with default text
5. Generate cleaned dataset and a file for manual review
"""

import pandas as pd
import re
from pathlib import Path

def extract_zip_from_address(address):
    """
    Extract 5-digit zip code from the end of an address string.

    Args:
        address: Address string

    Returns:
        Zip code string if found, None otherwise
    """
    if pd.isna(address):
        return None

    # Look for 5 digits at the end of the string
    match = re.search(r'\b(\d{5})$', str(address).strip())
    if match:
        return match.group(1)
    return None

def main():
    # File paths
    input_file = Path('/home/opc/Hope/backend/all_service_locations.csv')
    output_cleaned = Path('/home/opc/Hope/backend/all_service_locations_CLEANED.csv')
    output_to_fix = Path('/home/opc/Hope/backend/locations_to_fix_manually.csv')

    # Load the dataset
    print(f"Loading dataset from {input_file}...")
    df = pd.read_csv(input_file)

    initial_count = len(df)
    print(f"Initial dataset: {initial_count} rows\n")

    # Statistics tracking
    stats = {
        'duplicates_removed': 0,
        'zip_codes_recovered': 0,
        'bad_locations_moved': 0,
        'hours_filled': 0
    }

    # ============================================
    # 1. Remove Duplicates
    # ============================================
    print("Step 1: Removing duplicates...")

    # Identify columns for duplicate detection
    # Use exact column names from export
    name_col = 'Name'
    address_col = 'Street Address'

    if name_col and address_col:
        before_dup = len(df)
        df = df.drop_duplicates(subset=[name_col, address_col], keep='first')
        stats['duplicates_removed'] = before_dup - len(df)
        print(f"  ✓ Removed {stats['duplicates_removed']} duplicate locations")
    else:
        print(f"  ⚠ Could not find Name and Address columns. Available columns: {list(df.columns)}")

    # ============================================
    # 2. Fix Missing Zip Codes
    # ============================================
    print("\nStep 2: Recovering missing zip codes from addresses...")

    # Use exact column name from export
    zip_col = 'Zip Code'

    if zip_col and address_col:
        # Find rows with missing zip codes
        missing_zip_mask = df[zip_col].isna()
        missing_zip_count = missing_zip_mask.sum()

        print(f"  Found {missing_zip_count} rows with missing zip codes")

        # Try to extract zip codes from addresses
        for idx in df[missing_zip_mask].index:
            address = df.loc[idx, address_col]
            extracted_zip = extract_zip_from_address(address)
            if extracted_zip:
                df.loc[idx, zip_col] = extracted_zip
                stats['zip_codes_recovered'] += 1

        print(f"  ✓ Recovered {stats['zip_codes_recovered']} zip codes from addresses")
    else:
        print(f"  ⚠ Could not find Zip Code or Address column")

    # ============================================
    # 3. Handle Incorrect Coordinates
    # ============================================
    print("\nStep 3: Identifying locations with bad coordinates...")

    # Use exact column names from export
    lat_col = 'Latitude'
    lon_col = 'Longitude'

    if lat_col and lon_col:
        # Identify bad coordinates
        bad_coords_mask = (
            (df[lat_col] == 0.0) |
            (df[lon_col] == 0.0) |
            (df[lat_col] > 42.0) |
            (df[lat_col].isna()) |
            (df[lon_col].isna())
        )

        bad_locations = df[bad_coords_mask].copy()
        stats['bad_locations_moved'] = len(bad_locations)

        # Remove bad locations from main dataset
        df = df[~bad_coords_mask]

        # Save bad locations to separate file
        if len(bad_locations) > 0:
            bad_locations.to_csv(output_to_fix, index=False)
            print(f"  ✓ Moved {stats['bad_locations_moved']} locations with bad coordinates to {output_to_fix.name}")
            print(f"    Reasons: lat/lon = 0, lat > 42 (upstate NY), or missing coordinates")
        else:
            print(f"  ✓ No bad coordinates found")
    else:
        print(f"  ⚠ Could not find Latitude/Longitude columns. Available: {list(df.columns)}")

    # ============================================
    # 4. Fill Missing Operating Hours
    # ============================================
    print("\nStep 4: Filling missing operating hours...")

    # Note: Operating hours are stored in separate table, not in this export
    # We only have 'Is 24 Hours' boolean, so skip this step
    hours_col = None

    if hours_col:
        missing_hours_mask = df[hours_col].isna()
        stats['hours_filled'] = missing_hours_mask.sum()

        df.loc[missing_hours_mask, hours_col] = "Please call to verify hours"
        print(f"  ✓ Filled {stats['hours_filled']} missing operating hours entries")
    else:
        print(f"  ⚠ Could not find Operating Hours column")

    # ============================================
    # 5. Save Cleaned Dataset
    # ============================================
    print(f"\nStep 5: Saving cleaned dataset...")
    df.to_csv(output_cleaned, index=False)

    final_count = len(df)
    print(f"  ✓ Saved cleaned dataset to {output_cleaned.name}")
    print(f"  Final dataset: {final_count} rows\n")

    # ============================================
    # Summary
    # ============================================
    print("=" * 60)
    print("CLEANING SUMMARY")
    print("=" * 60)
    print(f"Initial rows:              {initial_count:,}")
    print(f"Duplicates removed:        {stats['duplicates_removed']:,}")
    print(f"Zip codes recovered:       {stats['zip_codes_recovered']:,}")
    print(f"Bad locations moved:       {stats['bad_locations_moved']:,}")
    print(f"Operating hours filled:    {stats['hours_filled']:,}")
    print(f"Final cleaned rows:        {final_count:,}")
    print("=" * 60)

    if stats['bad_locations_moved'] > 0:
        print(f"\n⚠ MANUAL REVIEW NEEDED:")
        print(f"  {stats['bad_locations_moved']} locations saved to '{output_to_fix.name}'")
        print(f"  These need geocoding fixes before adding to the database.\n")

    print("✓ Dataset cleaning complete!")

if __name__ == "__main__":
    main()
