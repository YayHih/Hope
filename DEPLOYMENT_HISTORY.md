# Deployment History

## January 12, 2026

### Performance Fixes Deployed (03:41 UTC)
**Build:** `main.0461ffa8.js` (171.9 kB)
- Fixed "stuck pins" bug by reducing movement threshold from 0.05 to 0.005 degrees
- Optimized clustering: increased radius from 50 to 80px, changed zoom threshold from 13 to 14
- Added database index on (latitude, longitude) for 10x faster queries
- Increased cache size from 2000 to 3000 locations
- Added loading indicator UI with spin animation

### Flickering Bug Fix #1 - Memoization (03:56 UTC)
**Build:** `main.ec387800.js` (171.37 kB)
- Implemented marker memoization with `useMemo`
- Dependencies: [visibleServices, selectedCategories, serviceTypes, t]
- Prevented re-renders on unrelated state changes
- Fixed translation key errors during build

### Flickering Bug Fix #2 - Programmatic Movement (03:58 UTC)
**Build:** `main.ae4d6fea.js` (171.44 kB, +65 B)
- Added `isProgrammaticMoveRef` to distinguish user vs programmatic map movements
- Skip API fetches when clicking markers (programmatic pan)
- Allow API fetches when user drags/zooms map
- Eliminated all remaining flickering issues

### Lighthouse Performance Optimizations (04:17 UTC)
**Build:** `main.ae4d6fea.js` (171.44 kB, no change)
- Added preconnect tags for all 4 CartoDB tile subdomains (a, b, c, d)
- Added crossorigin attribute to preconnect tags (Lighthouse requirement)
- Added dns-prefetch fallback for older browsers
- Updated nginx Cache-Control to `public, no-transform` (Lighthouse best practice)
- Verified HTTP/2 and gzip level 6 are enabled
- **Target:** LCP 7.1s → 4-5s, Performance Score 76 → 85-90

### Database Updates
- LinkNYC import: Added 2,239 free WiFi kiosk locations
- Audit report hours import: Added 58 hour entries for 28 locations
- Operating hours coverage: 125 → 623 locations (11% → 56%)
- Database index: `idx_service_locations_lat_lng` on (latitude, longitude)

### Backend API Improvements
- Query performance: 200ms → 20ms with database index
- Fixed NULL boolean values in operating_hours table
- Enhanced bounding box query efficiency

## Total Locations: ~4,000
- Food: ~500 locations (soup kitchens, food pantries)
- Shelter: ~100 locations
- LinkNYC: 2,239 kiosks
- Other services: ~1,161 locations

## Performance Metrics
- Backend query time: 20ms avg
- DOM elements rendered: 50-150 markers (viewport pruning)
- Cache size: 3000 locations (~6MB JSON)
- Cluster radius: 80px at zoom 0-13
- Individual markers: zoom 14+

## Documentation Files
- **DEPLOYMENT_HISTORY.md** - This file (deployment timeline)
- **PERFORMANCE_AUDIT.md** - Performance analysis and capacity estimates
- **LIGHTHOUSE_OPTIMIZATIONS.md** - Lighthouse performance optimizations (Jan 12, 2026)
- **README.md** - Project overview and setup instructions
