"""NYC HRA Community Food Connection (CFC) Food Pantries Scraper.

Parses the official HRA CFC Active Programs Excel file to extract food pantry
locations with operating hours and days.

Data source: https://www.nyc.gov/assets/hra/downloads/pdf/services/efap/CFC_ACTIVE.pdf
Converted to Excel format for reliable parsing: cfc_active.xlsx
"""

from typing import List
from datetime import time
import re
import pandas as pd

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData, OperatingHours, ServiceCapacity


class NYCCFCFoodPantriesScraper(BaseScraper):
    """Scraper for NYC HRA Community Food Connection food pantries."""

    source_name = "NYC HRA Community Food Connection"
    excel_path = "cfc_active.xlsx"

    # Service type codes - expanded to include all variants
    SERVICE_TYPES = {
        'FP': 'Food Pantry',
        'FPH': 'Food Pantry (Halal)',
        'FPK': 'Food Pantry (Kosher)',
        'FPM': 'Food Pantry (Mobile)',
        'FPHA': 'Food Pantry (Halal)',  # Variant
        'FPV': 'Food Pantry (Vegetarian)',
        'SK': 'Soup Kitchen',
        'SKM': 'Soup Kitchen (Mobile)',
        'SKK': 'Soup Kitchen (Kosher)',
        'SP': 'Soup Kitchen',  # Alternate code
    }

    def scrape(self) -> List[RawServiceData]:
        """Parse CFC Excel file and extract food pantry data."""
        results = []

        try:
            # Read Excel file with pandas
            df = pd.read_excel(self.excel_path)

            # Filter out header rows (where TYPE column == 'TYPE')
            df = df[df['TYPE'] != 'TYPE']

            # Filter out rows with missing essential data
            df = df.dropna(subset=['ID', 'TYPE', 'PROGRAM', 'DISTADD'])

            print(f"  ✓ Loaded {len(df)} valid records from Excel")

            # Iterate through rows
            for idx, row in df.iterrows():
                parsed = self._parse_row(row)
                if parsed:
                    results.append(parsed)

        except Exception as e:
            print(f"  ❌ Error parsing Excel: {e}")
            return []

        print(f"  ✓ Parsed {len(results)} CFC food pantries from Excel")
        return results

    def _parse_row(self, row: pd.Series) -> RawServiceData:
        """Parse a single row from the Excel file."""
        try:
            # Extract fields
            cfc_id = str(int(row['ID'])) if pd.notna(row['ID']) else None
            service_type = str(row['TYPE']).strip().upper() if pd.notna(row['TYPE']) else None
            program = str(row['PROGRAM']).strip() if pd.notna(row['PROGRAM']) else None
            phone = str(row['ORG PHONE']).strip() if pd.notna(row['ORG PHONE']) else None
            address = str(row['DISTADD']).strip() if pd.notna(row['DISTADD']) else None
            borough_code = str(row['TBO']).strip().upper() if pd.notna(row['TBO']) else None
            zipcode = str(int(row['DISTZIP'])) if pd.notna(row['DISTZIP']) else None
            days = str(row['DAYS']).strip() if pd.notna(row['DAYS']) else ''
            hours = str(row['HOURS']).strip() if pd.notna(row['HOURS']) else ''

            # Validate essential fields
            if not all([cfc_id, service_type, program, address]):
                return None

            # Skip invalid service types
            if service_type not in self.SERVICE_TYPES:
                print(f"  ⚠️  Unknown service type '{service_type}' for {program}")
                return None

            # Map borough codes
            # CRITICAL FIX: NYC HRA uses 'NY' for Manhattan, not 'MN'
            borough_map = {
                'BK': 'Brooklyn',
                'BX': 'Bronx',
                'MN': 'Manhattan',  # Legacy code
                'NY': 'Manhattan',  # NYC HRA uses NY for Manhattan in CFC Excel file
                'QN': 'Queens',
                'SI': 'Staten Island'
            }
            borough_name = borough_map.get(borough_code, borough_code)

            # Determine service types
            service_types = ['food']
            food_type_desc = self.SERVICE_TYPES.get(service_type, 'Food Pantry')

            # Parse operating hours
            operating_hours = self._parse_hours(days, hours)

            # Create description based on type
            description = f"{food_type_desc} providing groceries and food assistance. {days} {hours}"

            # CRITICAL: Store the service type code in the notes field
            # This preserves granular classification (FP vs SK vs FPH vs FPK vs FPM)
            # The frontend uses this for accurate filtering between pantries and soup kitchens
            service_capacities = [
                ServiceCapacity(
                    service_type='food',
                    capacity=None,
                    notes=service_type  # Store the raw code: FP, SK, FPH, FPK, FPM, etc.
                )
            ]

            return RawServiceData(
                external_id=f"cfc_{cfc_id}",
                data_source=self.source_name,
                name=program,
                street_address=address,
                city='New York',
                state='NY',
                zip_code=zipcode,
                borough=borough_name,
                phone=phone,
                website='https://www.nyc.gov/site/hra/help/food-assistance.page',
                description=description,
                service_types=service_types,
                service_capacities=service_capacities,  # Include service capacities with notes
                operating_hours=operating_hours if operating_hours else None,
            )

        except Exception as e:
            print(f"  ⚠️  Error parsing row: {e}")
            return None

    def _parse_hours(self, days_str: str, hours_str: str) -> List[OperatingHours]:
        """Parse days and hours into OperatingHours objects."""
        hours_list = []

        # Map day abbreviations to day numbers (0=Sunday, 6=Saturday)
        day_map = {
            'SUN': 0, 'MON': 1, 'TUE': 2, 'WED': 3,
            'THU': 4, 'THUR': 4, 'FRI': 5, 'SAT': 6
        }

        try:
            # Parse which days are active
            days_str_upper = days_str.upper()
            active_days = set()

            # Check for day ranges like MON-FRI
            if '-' in days_str_upper:
                range_match = re.search(r'(MON|TUE|WED|THU|THUR|FRI|SAT|SUN)-(MON|TUE|WED|THU|THUR|FRI|SAT|SUN)', days_str_upper)
                if range_match:
                    start_day = day_map.get(range_match.group(1))
                    end_day = day_map.get(range_match.group(2))
                    if start_day is not None and end_day is not None:
                        # Add all days in range
                        if start_day <= end_day:
                            active_days.update(range(start_day, end_day + 1))
                        else:
                            # Wraps around week (e.g., SAT-MON)
                            active_days.update(range(start_day, 7))
                            active_days.update(range(0, end_day + 1))

            # Check for individual days separated by commas or slashes
            for day_abbr, day_num in day_map.items():
                if day_abbr in days_str_upper:
                    active_days.add(day_num)

            # If no days were found, default to weekdays
            if not active_days:
                active_days = {1, 2, 3, 4, 5}  # Mon-Fri

            # Parse the hours
            open_time = None
            close_time = None
            notes = hours_str

            # Try to extract time ranges like "10AM-12PM" or "10:30AM-12:30PM"
            time_pattern = r'(\d{1,2}):?(\d{2})?\s*(AM|PM)\s*-\s*(\d{1,2}):?(\d{2})?\s*(AM|PM)'
            time_match = re.search(time_pattern, hours_str.upper())

            if time_match:
                open_hour = int(time_match.group(1))
                open_min = int(time_match.group(2)) if time_match.group(2) else 0
                open_period = time_match.group(3)
                close_hour = int(time_match.group(4))
                close_min = int(time_match.group(5)) if time_match.group(5) else 0
                close_period = time_match.group(6)

                # Convert to 24-hour format
                if open_period == 'PM' and open_hour != 12:
                    open_hour += 12
                elif open_period == 'AM' and open_hour == 12:
                    open_hour = 0

                if close_period == 'PM' and close_hour != 12:
                    close_hour += 12
                elif close_period == 'AM' and close_hour == 12:
                    close_hour = 0

                open_time = time(open_hour, open_min)
                close_time = time(close_hour, close_min)

            # Create OperatingHours for each active day
            for day_num in active_days:
                hours_list.append(OperatingHours(
                    day_of_week=day_num,
                    open_time=open_time,
                    close_time=close_time,
                    is_24_hours=False,
                    is_closed=False,
                    notes=notes if not open_time else None  # Only add notes if we couldn't parse times
                ))

            # Add closed days for completeness
            all_days = set(range(7))
            closed_days = all_days - active_days
            for day_num in closed_days:
                hours_list.append(OperatingHours(
                    day_of_week=day_num,
                    is_24_hours=False,
                    is_closed=True,
                ))

        except Exception as e:
            print(f"  ⚠️  Error parsing hours '{days_str} {hours_str}': {e}")
            # Return None to indicate we couldn't parse hours
            return None

        return hours_list
