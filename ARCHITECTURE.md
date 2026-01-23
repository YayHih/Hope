# Hope Platform - Component Tree & Schema

## Frontend (Web) - React 18 + TypeScript

### Provider Tree
```
<ThemeProvider>              ← Dark/light mode (localStorage)
  <LanguageProvider>         ← EN/ES (localStorage)
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  </LanguageProvider>
</ThemeProvider>
```

### Component Tree
```
AppContent
├── Header                          [src/components/Header.tsx]
│   ├── HamburgerMenu (☰)          → About, How It Works, Report, Providers
│   ├── App Title ("Hope")
│   ├── Theme Toggle (☀️/🌙)        → useTheme().toggleTheme
│   └── Language Toggle (EN/ES)     → useLanguage().setLanguage
│
├── <Routes>                        [src/App.tsx]
│   ├── "/" ──────────────→ MapScreen          [src/screens/MapScreen.tsx]
│   ├── "/about" ─────────→ AboutScreen        [src/screens/AboutScreen.tsx]
│   ├── "/how-it-works" ──→ HowItWorksScreen   [src/screens/HowItWorksScreen.tsx]
│   ├── "/privacy" ───────→ PrivacyPolicyScreen [src/screens/PrivacyPolicyScreen.tsx]
│   ├── "/terms" ─────────→ TermsOfUseScreen   [src/screens/TermsOfUseScreen.tsx]
│   ├── "/report" ────────→ ReportIssueScreen  [src/screens/ReportIssueScreen.tsx]
│   └── "/providers" ─────→ ProviderPortalScreen [src/screens/ProviderPortalScreen.tsx]
│
└── BottomNav                       [src/components/BottomNav.tsx]
    ├── Map (🗺️)
    ├── Privacy (🔒)
    ├── Terms (📄)
    ├── Report (📝)
    └── Providers (🏛️)
```

### MapScreen Component Tree
```
MapScreen                            [src/screens/MapScreen.tsx]
├── NetworkErrorBanner               (conditional - API errors)
├── LoadingOverlay                   (conditional - fetching)
├── FilterBar
│   ├── TopRow
│   │   ├── DHS Toggle (yellow)     → shows DHSInfoCard
│   │   ├── Center Button (🎯)      → MapCenterController
│   │   ├── Open Now filter
│   │   └── Open Today filter
│   └── CategoryRow (scrollable)
│       ├── Food (Hot Meals | Groceries)
│       ├── Intake Center
│       ├── Drop-In Center
│       ├── Mental Health Crisis (CPEP | Other)
│       ├── Youth Services
│       ├── Free WiFi & Charging
│       ├── Benefits & ID Help
│       ├── Case Management
│       ├── Hygiene
│       ├── Medical
│       ├── Hospitals
│       ├── Public Restrooms
│       ├── Warming Center
│       ├── Cooling Center
│       └── DV Hotline (direct call)
│
├── MapContainer (react-leaflet)
│   ├── TileLayer                    (Carto Voyager / Dark Matter)
│   ├── MapEventHandler              [src/screens/map/MapControls.tsx]
│   ├── MapCenterController          [src/screens/map/MapControls.tsx]
│   └── MarkerClusterGroup
│       └── MarkerWithClick[]        [src/screens/map/MapControls.tsx]
│           └── Popup
│               ├── Service Name + Type Badge
│               ├── Address + Phone
│               ├── Open/Closed Status
│               └── WeeklyHoursDropdown [src/screens/map/WeeklyHoursDropdown.tsx]
│
└── DHSInfoCard (overlay)            [src/screens/map/DHSInfoCard.tsx]
    ├── DHS Intake Locations
    ├── Call 311 Button
    └── Safe Horizon Hotline
```

### Map Module Exports
```
src/screens/map/
├── index.ts                 ← barrel exports
├── mapHelpers.ts            ← Types, constants, utilities
│   ├── Types: Service, OperatingHours, ServiceLocation, ServiceType
│   ├── Constants: API_BASE_URL, KM_PER_MILE
│   └── Functions: createColoredIcon, formatTime, validatePhoneNumber, etc.
├── mapStyles.ts             ← getMapStyles(colors, isDark)
├── MapControls.tsx          ← MapEventHandler, MapCenterController, MarkerWithClick
├── DHSInfoCard.tsx          ← DHS overlay component
└── WeeklyHoursDropdown.tsx  ← Collapsible hours display
```

### Theme System
```
src/theme/
├── index.ts                 ← Static design tokens
│   ├── COLORS (17 colors)
│   ├── SPACING (xs:4 sm:8 md:16 lg:24 xl:32 xxl:48)
│   ├── TYPOGRAPHY (fontFamily, fontSize, fontWeight, lineHeight)
│   ├── SHADOWS (sm, md, lg, xl)
│   ├── BORDER_RADIUS (sm:4 md:8 lg:12 xl:16 full:999)
│   ├── BREAKPOINTS (mobile:480 tablet:768 desktop:1024 wide:1280)
│   └── Z_INDEX (base:0 → modal:1300)
│
└── ThemeContext.tsx          ← Dynamic theme provider
    ├── ThemeProvider          (context + localStorage)
    └── useTheme()             → { mode, colors, isDark, toggleTheme }
```

### i18n System (Web)
```
src/i18n/
├── LanguageContext.tsx       ← Provider + useLanguage() hook
└── translations.ts           ← { en: {...}, es: {...} }
    └── 50+ translation keys
```

---

## Mobile App - React Native + Expo SDK 54

### Provider Tree
```
<ErrorBoundary>              ← Crash recovery UI
  <LanguageProvider>         ← EN/ES/ZH (AsyncStorage)
    <SafeAreaProvider>
      <NetworkProvider>      ← Offline detection banner
        <AppNavigator />
        <StatusBar />
      </NetworkProvider>
    </SafeAreaProvider>
  </LanguageProvider>
</ErrorBoundary>
```

### Navigation Structure
```
Stack.Navigator (headerShown: false)
├── "Main" ──→ Tab.Navigator (bottom tabs)
│   ├── "MapTab" ─────→ MapScreen          [src/screens/MapScreen.tsx]
│   ├── "Privacy" ────→ PrivacyPolicyScreen [src/screens/PrivacyPolicyScreen.tsx]
│   ├── "Terms" ──────→ TermsOfUseScreen   [src/screens/TermsOfUseScreen.tsx]
│   ├── "Report" ─────→ ReportIssueScreen  [src/screens/ReportIssueScreen.tsx]
│   └── "Providers" ──→ ProviderPortalScreen [src/screens/ProviderPortalScreen.tsx]
│
├── "About" ──────────→ AboutScreen         [src/screens/AboutScreen.tsx]
└── "HowItWorks" ─────→ HowItWorksScreen   [src/screens/HowItWorksScreen.tsx]
```

### Header Component Tree
```
CustomHeader                         [src/navigation/AppNavigator.tsx]
├── HamburgerMenu (☰)
│   └── Modal (slide)
│       ├── Menu Items
│       │   ├── About (ℹ️)
│       │   ├── How It Works (❓)
│       │   ├── Report an Issue (🚩)
│       │   └── Provider Portal (🏢)
│       └── LanguageSelector
│
├── App Title ("Hope")
└── LanguageSelector
    └── Single cycling button: EN → ES → 中文 → EN
```

### MapScreen Component Tree (Mobile)
```
MapScreen                            [src/screens/MapScreen.tsx]
├── MapView (react-native-maps)
│   └── Marker[] (service locations)
│
├── FilterPanel (conditional)
│   ├── Open Now toggle
│   ├── Category filters
│   │   ├── Food
│   │   ├── Shelter
│   │   ├── Medical
│   │   ├── Social
│   │   └── Hygiene
│   └── Clear All button
│
├── DHS Toggle button
│   └── DHS Safe Options overlay
│       ├── Intake locations
│       ├── Call 311
│       └── Back to Map
│
└── Service Detail Card (Animated)
    ├── Service name + type
    ├── Address
    ├── Distance
    ├── Open/Closed status
    └── View Details button
```

### State Management (Zustand)
```
useStore                             [src/store/useStore.ts]
├── Services
│   ├── nearbyServices: ServiceLocation[]
│   ├── serviceTypes: ServiceType[]
│   └── selectedService: ServiceLocation | null
│
├── Filters
│   ├── selectedServiceTypes: string[]
│   ├── searchRadius: number (default: 5km)
│   └── showOpenOnly: boolean
│
├── Location (ephemeral - never persisted)
│   └── currentLocation: { latitude, longitude } | null
│
└── Auth
    ├── isAuthenticated: boolean
    ├── user: User | null
    └── token: string | null
```

### Services Layer
```
src/services/
├── api.ts                   ← ApiService class (axios)
│   ├── getServiceTypes()     → GET /public/service-types
│   ├── searchNearby(params)  → GET /public/services/nearby
│   ├── getServiceLocation(id)→ GET /public/services/:id
│   └── reportIssue(params)   → POST /public/issues/report
│
├── auth.ts                  ← AuthService class (expo-secure-store)
│   ├── setToken() / getToken()
│   ├── setUser() / getUser()
│   ├── clearAuth()
│   └── isAuthenticated()
│
└── sentry.ts                ← Error tracking (production only)
    ├── initSentry()
    ├── captureException()
    ├── captureMessage()
    ├── setUser()
    └── addBreadcrumb()
```

### i18n System (Mobile)
```
src/i18n/
├── index.ts                 ← barrel exports
├── LanguageContext.tsx       ← Provider + useLanguage() hook (AsyncStorage)
└── translations.ts          ← { EN: {...}, ES: {...}, ZH: {...} }
    └── 130+ translation keys
```

### Theme Constants (Mobile)
```
src/constants/
├── theme.ts
│   ├── COLORS
│   │   ├── primary: '#2C7A7B' (teal)
│   │   ├── accent: '#38A169' (green)
│   │   ├── Service markers: food, shelter, medical, social, hygiene, warming, cooling
│   │   └── UI: text, background, border, shadow, status colors
│   ├── SPACING (xs:4 sm:8 md:16 lg:24 xl:32 xxl:48)
│   ├── TYPOGRAPHY (h1-h3, body, bodySmall, caption, button)
│   ├── SHADOWS (small, medium, large)
│   └── BORDER_RADIUS (sm:4 md:8 lg:12 xl:16 round:999)
│
└── config.ts
    ├── API_CONFIG { BASE_URL, TIMEOUT }
    ├── GOOGLE_AUTH_CONFIG { CLIENT_ID }
    └── MAP_CONFIG { DEFAULT coords NYC, INITIAL_REGION }
```

---

## Data Schema

### ServiceLocation
```typescript
{
  id: string
  name: string
  description: string | null
  organization_name: string | null
  street_address: string | null
  city: string
  state: string
  zip_code: string | null
  borough: string | null
  latitude: number
  longitude: number
  phone: string | null
  website: string | null
  email: string | null
  wheelchair_accessible: boolean | null
  languages_spoken: string[] | null
  data_source: string
  verified: boolean
  services: ServiceType[]
  operating_hours?: OperatingHours[]
  is_open_now?: boolean
  distance_km?: number
}
```

### ServiceType
```typescript
{
  id: number
  name: string
  slug: string
  icon: string | null
  color_hex: string | null
  description: string | null
}
```

### OperatingHours
```typescript
{
  day_of_week: number       // 0=Sunday, 6=Saturday
  day_name: string
  open_time: string         // "HH:MM"
  close_time: string        // "HH:MM"
  is_24_hours: boolean
  is_closed: boolean
  notes: string | null
}
```

### ReportIssue
```typescript
{
  issue_type: 'closed' | 'hours' | 'full' | 'referral' | 'other'
  location_name: string
  description: string
  captcha_token?: string    // web only (reCAPTCHA)
}
```

---

## API Endpoints Used

| Method | Endpoint | Used By |
|--------|----------|---------|
| GET | `/public/service-types` | MapScreen (both) |
| GET | `/public/services/nearby` | Mobile MapScreen |
| GET | `/public/services/in-bounds` | Web MapScreen |
| GET | `/public/services/:id` | Service detail |
| POST | `/public/issues/report` | ReportIssueScreen (both) |

---

## Key Differences: Web vs Mobile

| Feature | Web (Frontend) | Mobile |
|---------|---------------|--------|
| Map Library | React Leaflet + Carto tiles | react-native-maps (native) |
| State | React useState/Context only | Zustand store + Context |
| Languages | EN, ES | EN, ES, ZH (中文) |
| Theme | Light/Dark toggle (context) | No dark mode yet |
| Auth Storage | N/A (no auth) | expo-secure-store |
| Offline | No handling | NetworkContext + banner |
| Error Recovery | None | ErrorBoundary component |
| Crash Reporting | None | Sentry integration |
| Map Clustering | react-leaflet-markercluster | Native clustering |
| CAPTCHA | reCAPTCHA v2 | None (rate limiting only) |
| Persistence | localStorage | AsyncStorage + SecureStore |
