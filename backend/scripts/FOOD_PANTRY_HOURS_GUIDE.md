# Getting Food Pantry Hours Data - Comprehensive Guide

**Current Status**: 53% of food pantries (499 of 941) are missing operating hours

## Multiple Approaches to Get Hours Data

### ✅ Approach 1: Official Data Partnerships (RECOMMENDED)

**1. Food Bank For New York City**
- **URL**: https://www.foodbanknyc.org/get-help/
- **Coverage**: 800+ NYC pantries, soup kitchens, mobile pantries
- **Action**: Email data@foodbanknyc.org or partnerships team
- **Ask for**: Bulk data export with hours, eligibility, services
- **Format**: CSV/JSON preferred
- **Pros**: Official, comprehensive, includes hours
- **Cons**: Requires partnership agreement

**2. Plentiful App**
- **URL**: https://plentifulapp.com/providers
- **Coverage**: 360+ NYC food pantries with reservation system
- **Contact**: info@plentifulapp.com
- **Action**: Request data partnership or API access
- **Data includes**: Real-time availability, hours, reservation info
- **Pros**: Real-time, reservation-integrated
- **Cons**: Not all pantries use Plentiful

**3. City Harvest**
- **URL**: https://www.cityharvest.org/food-map/
- **Coverage**: Pantries, soup kitchens, community fridges, mobile markets
- **Action**: Contact data team for bulk export
- **Pros**: Includes mobile markets, community fridges
- **Cons**: Subset of total NYC pantries

### ✅ Approach 2: API Endpoint Discovery (TECHNICAL)

**Step 1: Identify Hidden APIs**

Many NYC food finders are React/Vue apps that load data from hidden APIs:

```bash
# Example: NYC Food Help Finder
# 1. Open https://finder.nyc.gov/foodhelp/ in browser
# 2. Open Developer Tools (F12) → Network tab
# 3. Filter: XHR/Fetch
# 4. Interact with map/search
# 5. Look for API calls like:
#    - /api/locations
#    - /data/food-pantries.json
#    - GraphQL endpoint
#    - Geospatial API (e.g., ArcGIS)
```

**Common API Patterns to Check:**

```bash
# City Harvest Food Map
curl "https://www.cityharvest.org/api/food-locations" | jq

# NYC Open Data filtered
curl "https://data.cityofnewyork.us/resource/DATASET_ID.json?\$limit=1000"

# ArcGIS REST API (common for NYC maps)
curl "https://services.arcgis.com/.../FeatureServer/0/query?where=1=1&outFields=*&f=json"
```

**Once API found:**
1. Document endpoint URL
2. Check rate limits
3. Parse response structure
4. Update script with actual endpoint

### ✅ Approach 3: Web Scraping (FALLBACK)

**Tools Needed:**
- `httpx` - HTTP client
- `beautifulsoup4` - HTML parsing
- `playwright` or `selenium` - JavaScript rendering (if needed)

**Example: Scrape individual pantry websites**

```python
import httpx
from bs4 import BeautifulSoup

async def scrape_pantry_hours(url):
    """
    Scrape hours from a food pantry website.
    Common HTML patterns:
    - <div class="hours">...</div>
    - <table class="operating-hours">
    - <span class="day">Monday</span> <span class="time">9AM-5PM</span>
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for hours patterns
        hours_div = soup.find('div', class_='hours')
        if hours_div:
            # Parse hours from HTML
            # Return structured data
            pass

    return hours_data
```

**Respectful Scraping Rules:**
- Add User-Agent header
- Rate limit requests (1-2 seconds between)
- Cache results
- Respect robots.txt
- Don't overwhelm small nonprofit sites

### ✅ Approach 4: Manual Curation (ACCURATE)

**Sources for Manual Curation:**

1. **NYC HRA Community Food Connection (CFC)**
   - URL: https://www.nyc.gov/site/hra/help/food-assistance.page
   - Download PDF directory
   - Extract hours manually or with PDF parsing

2. **NYC 311 Database**
   - Call 311 or use portal
   - Request bulk list with hours
   - May require FOIL request

3. **Borough-specific directories**
   - Bronx Borough President: https://bronxboropres.nyc.gov/health-human-services/food-assistance/
   - Brooklyn Community Boards
   - Queens community organizations
   - Manhattan neighborhood associations

4. **Direct pantry contact**
   - Call each pantry (499 without hours)
   - Automated script to dial and record hours
   - Volunteer crowdsourcing effort

**Manual Entry Template:**

```python
CURATED_PANTRY_HOURS = [
    {
        "name": "West Side Campaign Against Hunger",
        "address": "263 W 86th St, New York, NY 10024",
        "phone": "(212) 362-8001",
        "hours": [
            {"day": "Monday", "open": "9:00 AM", "close": "5:00 PM"},
            {"day": "Tuesday", "open": "9:00 AM", "close": "7:00 PM"},
            # ... etc
        ],
        "notes": "Appointments preferred. Serves Upper West Side residents.",
        "source": "Called 1/10/2026",
        "verified_date": "2026-01-10"
    },
    # Add more entries...
]
```

### ✅ Approach 5: Crowdsourcing

**Community Data Collection:**

1. **Google Forms Survey**
   - Share with social workers, volunteers
   - Fields: Pantry name, address, hours, notes
   - Review and import submissions

2. **Volunteer Phone Banking**
   - Script to call 499 pantries
   - Record hours in spreadsheet
   - Import via CSV

3. **Partnership with Social Service Agencies**
   - DYCD after-school programs
   - Community boards
   - Faith-based organizations

## Implementation Priority

### Phase 1: Quick Wins (1-2 weeks)
1. ✅ Contact Food Bank NYC for data partnership
2. ✅ Identify API endpoints for major finders
3. ✅ Manual curation of top 50 largest pantries

### Phase 2: Bulk Import (2-4 weeks)
1. Implement API integrations (if available)
2. Build web scrapers for official directories
3. CSV import from manual curation

### Phase 3: Maintenance (Ongoing)
1. Quarterly data refresh
2. User-submitted corrections
3. Automated verification checks

## Technical Implementation

### Script Usage:

```bash
cd /home/opc/Hope/backend
source venv/bin/activate

# Run enhanced ingestion (with API endpoints identified)
python3 scripts/ingest_food_pantries_enhanced.py

# Manual update with CSV
python3 scripts/import_pantry_hours_csv.py pantry_hours.csv
```

### Database Schema:

Operating hours already support:
- Day of week (0-6)
- Open/close times
- 24-hour flag
- Closed flag
- Notes field

No schema changes needed!

### Validation:

```python
# Check coverage after import
python3 -c "
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import select, func
from app.models import ServiceLocation, LocationService, OperatingHours, ServiceType

async def check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ServiceType.id).where(ServiceType.slug == 'food')
        )
        food_id = result.scalar()

        # With hours
        result = await session.execute(
            select(func.count(ServiceLocation.id.distinct()))
            .select_from(ServiceLocation)
            .join(LocationService).join(OperatingHours)
            .where(LocationService.service_type_id == food_id)
        )
        with_hours = result.scalar()

        # Total
        result = await session.execute(
            select(func.count(ServiceLocation.id.distinct()))
            .select_from(ServiceLocation)
            .join(LocationService)
            .where(LocationService.service_type_id == food_id)
        )
        total = result.scalar()

        percent = (with_hours / total * 100) if total > 0 else 0
        print(f'{with_hours}/{total} ({percent:.1f}%) have hours')

asyncio.run(check())
"
```

## Legal & Ethical Considerations

### Data Usage:
- ✅ Public directories (NYC HRA, Community Boards)
- ✅ Official nonprofit websites
- ✅ Data partnerships with written agreement
- ⚠️ Web scraping (check terms of service)
- ❌ Selling or commercializing nonprofit data

### Attribution:
Always credit data sources:
```python
location.notes = "Hours verified 1/10/2026 via Food Bank NYC directory"
location.data_source = "Food Bank For New York City"
location.verified_at = datetime.now()
```

### Privacy:
- Don't collect personal information
- Phone numbers for pantries only (not individuals)
- No client/recipient data

## Success Metrics

**Target**: Reduce missing hours from 53% to <10%

**Milestones:**
- Week 1: Identify 3 working API endpoints → 25% coverage
- Week 2: Manual curation of top 100 pantries → 40% coverage
- Week 4: Complete data partnerships → 90% coverage

## Resources

### Data Sources:
- [Food Bank For New York City](https://www.foodbanknyc.org/get-help/)
- [Plentiful App](https://plentifulapp.com)
- [City Harvest Food Map](https://www.cityharvest.org/food-map/)
- [NYC Food Help Finder](https://finder.nyc.gov/foodhelp/)
- [NYC HRA Food Assistance](https://www.nyc.gov/site/hra/help/food-assistance.page)

### Contact:
- Food Bank NYC: partnerships@foodbanknyc.org
- Plentiful: info@plentifulapp.com
- City Harvest: data@cityharvest.org
- NYC 311: Data requests via portal

---

**Last Updated**: January 10, 2026
**Status**: 53% missing hours (499 of 941 pantries)
**Next Action**: Contact Food Bank NYC for data partnership
