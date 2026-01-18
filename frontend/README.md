# Hope Frontend

React-based frontend for the Hope Platform - NYC homeless services directory.

## Tech Stack

- **React** 18.3.1
- **TypeScript** 4.9.5
- **React Leaflet** 4.2.1 - Interactive map with OpenStreetMap
- **React Leaflet Markercluster** 3.0.0-rc1 - Marker clustering for performance
- **i18next** 23.16.8 - Multi-language support (English, Spanish, Chinese, Arabic, French, Russian, Haitian Creole)
- **Nominatim** - Geocoding and address search

## Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm start
```

Runs on [http://localhost:3000](http://localhost:3000)

### Build for Production
```bash
npm run build
```

Creates optimized production build in `build/` directory.

## Deployment

### Production Deployment Location

**IMPORTANT**: The frontend is served by Nginx from `/var/www/hope-frontend/`, NOT from `/home/admin/Hope/frontend/dist/`.

To deploy the frontend after building:

```bash
# Build the frontend
npm run build

# Deploy to Nginx serving directory (requires sudo)
sudo rsync -av --delete /home/admin/Hope/frontend/build/ /var/www/hope-frontend/
```

### Nginx Configuration

The frontend is configured in `/etc/nginx/conf.d/hope-backend.conf`:

- **Static assets** (JS, CSS, images): Cached for 1 year with `Cache-Control: public, immutable`
- **HTML files**: Cached for 1 hour with `Cache-Control: public, must-revalidate`
- **Service worker**: No cache (`Cache-Control: no-cache, no-store, must-revalidate`)

### Deployment Checklist

1. Make changes to source code
2. Build: `npm run build`
3. Deploy: `sudo rsync -av --delete /home/admin/Hope/frontend/build/ /var/www/hope-frontend/`
4. Users should hard refresh (Ctrl+Shift+R) to bypass browser cache

## Map Features

### Zoom Level Behavior

- **Zoom 0-7**: No markers shown (too zoomed out - state/country level)
- **Zoom 8-11**: Markers shown with clustering (numbered circles group nearby locations)
- **Zoom 12+**: Individual markers shown (no clustering)

This configuration balances performance with usability:
- Prevents loading all locations when viewing entire country/state
- Uses clustering to reduce visual clutter at city/metro level
- Shows individual markers when zoomed in to neighborhood level

### Marker Clustering

Implemented with `react-leaflet-markercluster`:
- `maxClusterRadius={50}` - Markers within 50px are clustered
- `disableClusteringAtZoom={12}` - Individual markers at zoom 12+
- `spiderfyOnMaxZoom={true}` - Spread out overlapping markers when fully zoomed
- `chunkedLoading` - Improves performance with large datasets

### Service Type Filters

Users can filter by service type:
- Food / Comida / 食物
- Shelter / Refugio / 住所
- Hygiene / Higiene / 卫生
- Healthcare / Atención médica / 医疗
- Legal / Legal / 法律
- Employment / Empleo / 就业

Filters update the map in real-time by passing `service_types` parameter to the backend API.

## Performance Optimizations

### Frontend
1. **Marker Clustering**: Reduces DOM nodes from thousands to dozens at metro zoom levels
2. **Debounced Map Updates**: 400ms debounce prevents excessive API calls during pan/zoom
3. **Bounding Box Queries**: Only fetches locations visible in current viewport
4. **Viewport Caching**: Skips API call if viewport is within previously cached bounds

### Backend Integration
The frontend integrates with optimized backend endpoints:
- `/api/v1/public/services/in-bounds` - Bounding box query with eager loading (1 SQL query instead of 226)
- Rate limited to 60 requests/minute per IP
- Redis-backed rate limiting across all uvicorn workers

## Language Support

Full internationalization (i18n) support:
- **English** (en) - Default
- **Spanish** (es) - Español
- **Chinese** (zh) - 中文
- **Arabic** (ar) - العربية (RTL layout)
- **French** (fr) - Français
- **Russian** (ru) - Русский
- **Haitian Creole** (ht) - Kreyòl Ayisyen

Language switcher in header with flag icons. Translations stored in `public/locales/{lang}/translation.json`.

## File Structure

```
frontend/
├── public/
│   ├── locales/           # i18n translation files
│   │   ├── en/
│   │   ├── es/
│   │   ├── zh/
│   │   ├── ar/
│   │   ├── fr/
│   │   ├── ru/
│   │   └── ht/
│   ├── favicon*.png       # App icons
│   └── manifest.json      # PWA manifest
├── src/
│   ├── components/        # Reusable components
│   ├── screens/
│   │   └── MapScreen.tsx  # Main map interface (PRIMARY FILE)
│   ├── services/
│   │   └── api.ts         # Backend API client
│   ├── i18n.ts            # i18next configuration
│   ├── App.tsx            # Root component with routing
│   └── index.tsx          # React entry point
├── build/                 # Production build output (gitignored)
└── package.json
```

## Environment Variables

No environment variables required - all configuration is hardcoded for production deployment to hopefornyc.com.

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Known Issues

### Browser Caching
Due to aggressive browser caching of JavaScript assets (1-year cache), users may need to hard refresh after deployments:
- **Chrome/Edge/Firefox**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- **Safari**: Cmd+Option+R
- **Or**: Open Developer Tools (F12) → Right-click refresh → "Empty Cache and Hard Reload"

The HTML index file has a shorter cache (1 hour) and includes content-based hashes in asset filenames (e.g., `main.9c524db2.js`) which should trigger cache busts on changes, but some browsers may still cache aggressively.

## Security

- Content Security Policy (CSP) configured in Nginx
- HTTPS enforced (HTTP redirects to HTTPS)
- No sensitive data stored in frontend
- All API calls authenticated through CORS headers
- Permissions Policy restricts geolocation to self-origin only

### ⚖️ License & Trademark

The Code: The software source code is licensed under the GNU AGPL v3. You are free to run, study, share, and modify the software. If you run a modified version as a network service, you must share your source code.

The Brand: The name "Hope for NYC", the specific logo, and the domain hopefornyc.com are trademarks of the project maintainers.

✅ You CAN: Fork this repo to create "Hope for Chicago" or "Hope for Philly."

❌ You CANNOT: Host an identical version of this site called "Hope for NYC" that confuses users into thinking it is the official source.

❌ You CANNOT: Use our logo or trademarks in a way that implies endorsement.
