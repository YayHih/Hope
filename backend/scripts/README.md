# Hope Platform - Data Ingestion Scripts

Comprehensive data ingestion scripts for NYC homeless services, with focus on permanent cooling/warming centers and food assistance.

## Summary of Current Data

### Database Stats (After Library Ingestion)
- **Total Service Locations**: 1,247
- **Food Pantries**: 941 (53% missing operating hours)
- **Cooling/Warming Centers**: 185 (all libraries)
- **Service Types**: 8 (Food, Shelter, Hygiene, Medical, Cooling, Social, Hospitals, Warming)

## Completed Ingestions

### ✅ Libraries - Permanent Cooling/Warming Centers

**Script**: [`ingest_all_libraries_comprehensive.py`](ingest_all_libraries_comprehensive.py)

**Why Libraries?**
- Year-round operation (not ephemeral seasonal datasets)
- Climate-controlled (AC in summer, heat in winter)
- Free public access - no membership required
- Multiple services: books, computers, WiFi, restrooms, water
- ADA accessible, multilingual staff

**Data Sources:**
- Queens Library: [NYC Open Data kh3d-xhq7](https://data.cityofnewyork.us/widgets/kh3d-xhq7) ✓ Working
- NYPL & Brooklyn: Curated from official library websites

**Results:**
- 174 libraries added
- 65 Queens Library branches
- 11 NYPL branches (Manhattan, Bronx)
- 8 Brooklyn Public Library branches

**Usage:**
```bash
cd /home/opc/Hope/backend
source venv/bin/activate
python3 scripts/ingest_all_libraries_comprehensive.py
```

**Re-runnable**: Yes - skips existing locations

## Scripts Ready (Not Yet Run)

### NYC Parks Recreation Centers

**Script**: [`ingest_recreation_centers.py`](ingest_recreation_centers.py)

**Purpose**: Secondary tier cooling/warming centers with:
- Indoor facilities
- Air conditioning / heating
- Programs and activities
- Gym facilities, pools

**Data Source**: NYC Parks Structures dataset
**Status**: Ready to run (API endpoint needs verification)

**Usage:**
```bash
python3 scripts/ingest_recreation_centers.py
```

### Food Pantries Enhancement

**Script**: [`ingest_food_pantries.py`](ingest_food_pantries.py)

**Purpose**: Add additional food pantries and soup kitchens

**Current Gap**: 53% of existing food pantries (499 of 941) lack operating hours

**Recommended Approach**:
Given NYC Open Data API inconsistencies, the most reliable approach is:

1. **Food Bank For New York City (FBNYC)**: https://www.foodbanknyc.org/get-help/
   - Has comprehensive member agency list
   - Includes hours, eligibility, services

2. **NYC Human Resources Admin**: https://www1.nyc.gov/site/hra/help/food-assistance.page
   - Official city food assistance directory

3. **Feeding America**: Partner agency data
   - National database with NYC locations

**Manual Enhancement Needed**: Operating hours data requires either:
- Web scraping official directories
- API integration with Food Bank systems
- Manual curation from published lists

## Script Architecture

### Common Pattern

All scripts follow this structure:

```python
import asyncio
from datetime import time
from app.database import AsyncSessionLocal
from app.models import ServiceLocation, ServiceType, LocationService, OperatingHours

async def main():
    async with AsyncSessionLocal() as session:
        # 1. Get/create service types
        # 2. Fetch data from API or curated list
        # 3. For each location:
        #    - Check if exists (skip duplicates)
        #    - Create ServiceLocation
        #    - Add LocationService links
        #    - Add OperatingHours
        # 4. Commit session
```

### Database Integrity

- **Duplicate Prevention**: Checks by name before inserting
- **Soft Deletes**: Respects `deleted_at IS NULL` filter
- **Relationships**: Properly links locations to service types
- **Time Objects**: Uses `datetime.time(hour, minute)` for PostgreSQL TIME fields

### Error Handling

- **Transaction Rollback**: Automatic on errors
- **Skip on Failure**: Individual location failures don't break batch
- **Verbose Logging**: ✓/⏭️/⚠️/❌ status indicators

## Data Quality Issues

### NYC Open Data API Problems

Many NYC Open Data datasets have issues:

1. **Empty Responses**: Dataset IDs exist but return empty objects
   - Libraries dataset: `p4pf-fyc4` (broken)
   - Recreation Centers: `cqys-iuv3` (404 Not Found)

2. **Field Name Changes**: Undocumented schema changes

3. **Sorting Restrictions**: Some fields can't be used in `$order`

**Workaround**: Use curated data from official sources + working APIs (like Queens Library)

## Future Enhancements

### Recommended Next Steps:

1. **Add More NYPL/Brooklyn Branches**: Current scripts have ~20 branches, expand to full ~216 branches
2. **Recreation Centers**: Find working API endpoint or curate from NYC Parks website
3. **Food Pantry Hours**: Partner with FBNYC for official hours data
4. **Verification**: Add `verified_at` timestamp for data freshness tracking
5. **Geocoding**: Add Nominatim/Geoclient fallback for locations missing coordinates

### Data Refresh Strategy:

**Libraries**: Quarterly
- Hours change seasonally
- New branches open occasionally

**Food Pantries**: Monthly
- High churn rate (locations open/close)
- Hours change frequently

**Recreation Centers**: Quarterly
- Seasonal program changes
- Renovation closures

## Technical Notes

### Time Zone Handling

All operating hours stored in **local NYC time** (ET/EDT).
- No timezone conversion needed
- Database uses TIME WITHOUT TIME ZONE
- Python datetime.time objects: `time(10, 0)` = 10:00 AM

### Borough Mapping

```python
BOROUGH_CODES = {
    "1": "Manhattan",
    "2": "Bronx",
    "3": "Brooklyn",
    "4": "Queens",
    "5": "Staten Island",
    "M": "Manhattan",
    "X": "Bronx",
    "B": "Brooklyn",
    "Q": "Queens",
    "R": "Staten Island"
}
```

### Day of Week Encoding

```python
# Database uses: 0 = Sunday, 1 = Monday, ..., 6 = Saturday
# Python datetime.weekday(): 0 = Monday, ..., 6 = Sunday
# Conversion needed: (python_day + 1) % 7 = db_day
```

## Troubleshooting

### Common Errors:

**"'str' object has no attribute 'hour'"**
- **Cause**: Passing string "10:00" instead of time(10, 0)
- **Fix**: Import `from datetime import time` and use time objects

**"404 Not Found" from API**
- **Cause**: Dataset ID changed or deprecated
- **Fix**: Search NYC Open Data for current dataset ID

**"PendingRollbackError"**
- **Cause**: Previous exception in transaction
- **Fix**: Call `session.rollback()` before retrying

**Duplicate locations**
- **Expected**: Scripts skip existing locations by name
- **Check**: `⏭️ {name} already exists` in output

## Support

For NYC Open Data issues:
- Portal: https://opendata.cityofnewyork.us
- Support: opendata@cityhall.nyc.gov

For Hope Platform ingestion questions:
- Review this README
- Check script comments
- Test APIs manually with curl

---

**Last Updated**: January 10, 2026
**Maintainer**: Hope Platform Team
