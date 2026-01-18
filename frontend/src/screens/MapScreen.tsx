import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMapEvents, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import axios from 'axios';
import L from 'leaflet';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme';
import { useLanguage } from '../i18n/LanguageContext';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Set default Leaflet icon
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Global icon cache to prevent regenerating base64 SVGs on every render
const ICON_CACHE: { [key: string]: L.Icon } = {};

// Helper function to sanitize color hex values (SECURITY: Prevent SVG injection - VULN-001)
const sanitizeColorHex = (color: string): string => {
  // Only allow valid hex colors (#RGB or #RRGGBB)
  const hexPattern = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
  if (!hexPattern.test(color)) {
    console.warn(`[SECURITY] Invalid color hex: ${color}, defaulting to #2C7A7B`);
    return '#2C7A7B'; // Safe default color
  }
  return color;
};

// Function to create color-coded marker icons with embedded symbols and memoization
const createColoredIcon = (color: string, symbol?: string) => {
  const safeColor = sanitizeColorHex(color); // SECURITY FIX
  const cacheKey = `${safeColor}-${symbol || 'default'}`;

  // Return cached icon if it exists
  if (ICON_CACHE[cacheKey]) {
    return ICON_CACHE[cacheKey];
  }

  // Define symbol SVG paths for different service types (using simple shapes instead of emoji)
  let symbolSvg = '';
  if (symbol === 'food-hot') {
    // Bowl shape for hot meals
    symbolSvg = '<ellipse cx="17.5" cy="13" rx="4" ry="3" fill="#333"/><path d="M 13.5 13 Q 17.5 16 21.5 13" stroke="#333" stroke-width="1" fill="none"/>';
  } else if (symbol === 'food-grocery') {
    // Shopping bag shape for groceries
    symbolSvg = '<rect x="14.5" y="11" width="6" height="6" rx="0.5" fill="none" stroke="#333" stroke-width="1.2"/><path d="M 15.5 11 Q 17.5 9 19.5 11" stroke="#333" stroke-width="1.2" fill="none"/>';
  } else if (symbol === 'shelter') {
    // Bed/house shape for shelter
    symbolSvg = '<rect x="13.5" y="13" width="8" height="3.5" rx="0.5" fill="#333"/><circle cx="15" cy="14.5" r="0.8" fill="#fff"/>';
  } else if (symbol === 'intake') {
    // Door shape for intake centers (front door)
    symbolSvg = '<rect x="14" y="11" width="7" height="7" rx="0.5" fill="none" stroke="#333" stroke-width="1.5"/><rect x="16.5" y="14" width="2" height="3" rx="0.5" fill="#333"/><circle cx="16" cy="15.5" r="0.4" fill="#fff"/>';
  } else if (symbol === 'drop-in') {
    // Chair shape for drop-in centers
    symbolSvg = '<rect x="14" y="13" width="7" height="5" rx="0.5" fill="none" stroke="#333" stroke-width="1.2"/><rect x="14" y="11" width="2" height="2" fill="#333"/><rect x="19" y="11" width="2" height="2" fill="#333"/>';
  } else if (symbol === 'medical') {
    // Cross symbol for medical
    symbolSvg = '<rect x="16.5" y="11" width="2" height="6" fill="#333"/><rect x="14" y="13.5" width="7" height="2" fill="#333"/>';
  }

  // Generate new icon and cache it
  const svgIcon = `
    <svg width="35" height="50" viewBox="0 0 35 50" xmlns="http://www.w3.org/2000/svg">
      <path fill="${safeColor}" stroke="#fff" stroke-width="2"
        d="M17.5 0C10.596 0 5 5.596 5 12.5c0 8.5 12.5 28.5 12.5 28.5S30 21 30 12.5C30 5.596 24.404 5 17.5 5z"
        transform="scale(1.16667)"/>
      ${symbolSvg || '<circle cx="17.5" cy="14.5" r="5" fill="#fff"/>'}
    </svg>
  `;

  // Use URI encoding instead of btoa to handle all characters safely
  const icon = L.icon({
    iconUrl: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgIcon),
    shadowUrl: iconShadow,
    iconSize: [35, 50],
    iconAnchor: [17, 50],
    popupAnchor: [1, -40],
  });

  ICON_CACHE[cacheKey] = icon;
  return icon;
};

interface Service {
  type: string;
  name: string;
  notes?: string;
  capacity?: number;
}

interface OperatingHours {
  day_of_week: number;
  day_name: string;
  open_time: string | null;
  close_time: string | null;
  is_24_hours: boolean;
  is_closed: boolean;
  notes?: string;
}

interface ServiceLocation {
  id: string;
  name: string;
  description?: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  street_address: string;
  borough: string;
  phone: string;
  services: Service[];
  operating_hours?: OperatingHours[];
  is_open_now?: boolean;
}

interface ServiceType {
  id: number;
  name: string;
  slug: string;
  color_hex: string;
}

const API_BASE_URL = 'https://hopefornyc.com/api/v1';
const KM_PER_MILE = 1.60934;

// Conditional logging (SECURITY: VULN-007 - Prevent info disclosure in production)
const isDevelopment = process.env.NODE_ENV === 'development';
const debugLog = (...args: any[]) => {
  if (isDevelopment) {
    console.log(...args);
  }
};

// Pre-compiled regex patterns (PERFORMANCE: PERF-002 - Avoid recompiling in loops)
const SP_SK_PATTERN = /\b(SP|SK)\b/;
const FP_PATTERN = /\b(FP|FPH|FPK|FPM)\b/;

// Helper function to determine food sub-category using waterfall strategy
const getFoodSubCategory = (service: Service): 'pantry' | 'soup-kitchen' | 'food' => {
  // PRIORITY 1: Check service.notes field for NYC HRA CFC codes (highest confidence)
  // After scraper update, the notes field contains the raw code from Excel file
  if (service.notes) {
    const notesUpper = service.notes.toUpperCase().trim();

    // Exact match on service type codes (most reliable)
    // Soup Kitchen codes: SK, SP, SKM (Mobile), SKK (Kosher)
    if (notesUpper === 'SK' || notesUpper === 'SP' || notesUpper === 'SKM' || notesUpper === 'SKK') {
      return 'soup-kitchen';
    }
    // Food Pantry codes: FP, FPH (Halal), FPK (Kosher), FPM (Mobile), FPHA (Halal variant), FPV (Vegetarian)
    if (notesUpper === 'FP' || notesUpper === 'FPH' || notesUpper === 'FPK' || notesUpper === 'FPM' ||
        notesUpper === 'FPHA' || notesUpper === 'FPV') {
      return 'pantry';
    }
  }

  // PRIORITY 2: Check for explicit codes in name/notes text (high confidence)
  // These codes come from NYC HRA Community Food Connection system
  const searchText = `${service.name} ${service.notes || ''}`.toUpperCase();

  // Soup Kitchen codes
  if (searchText.includes('SP') || searchText.includes('SK')) {
    // Check if it's actually a code and not part of a word like "hospital"
    if (SP_SK_PATTERN.test(searchText)) {
      return 'soup-kitchen';
    }
  }

  // Food Pantry codes
  if (searchText.includes('FP')) {
    // Check for specific pantry types with word boundaries
    if (FP_PATTERN.test(searchText)) {
      return 'pantry';
    }
  }

  // PRIORITY 3: Fallback to keyword matching (medium confidence)
  // Only run if no explicit code was found
  const lowerText = searchText.toLowerCase();

  // Soup kitchen keywords
  if (lowerText.includes('soup') || lowerText.includes('kitchen') ||
      lowerText.includes('meal') || lowerText.includes('dining') ||
      lowerText.includes('breakfast') || lowerText.includes('lunch') ||
      lowerText.includes('dinner')) {
    return 'soup-kitchen';
  }

  // Pantry keywords
  if (lowerText.includes('pantry') || lowerText.includes('basket') ||
      lowerText.includes('grocery') || lowerText.includes('groceries') ||
      lowerText.includes('distribution') || lowerText.includes('food bank')) {
    return 'pantry';
  }

  // PRIORITY 4: Default to generic (safety net)
  // Better to show it than hide it - user can read the details
  return 'food';
};

// Helper function to get descriptive food label
const getFoodLabel = (service: Service): string => {
  const searchText = `${service.name} ${service.notes || ''}`.toLowerCase();

  // Check for specific pantry types
  if (searchText.includes('halal')) {
    return 'Halal Food Pantry';
  }
  if (searchText.includes('kosher')) {
    return 'Kosher Food Pantry';
  }
  if (searchText.includes('mobile')) {
    return 'Mobile Food Pantry';
  }

  // Check category
  const subCategory = getFoodSubCategory(service);
  if (subCategory === 'soup-kitchen') {
    return 'Soup Kitchen (Hot Meals)';
  }
  if (subCategory === 'pantry') {
    return 'Food Pantry (Groceries)';
  }

  return service.name || 'Food';
};

// Helper function to determine mental health crisis sub-category
const getCrisisSubCategory = (service: Service, description?: string): 'cpep' | 'other' => {
  const searchText = `${service.name} ${service.notes || ''} ${description || ''}`.toUpperCase();

  // CPEP = Comprehensive Psychiatric Emergency Program (ER-level care)
  if (searchText.includes('CPEP') ||
      searchText.includes('EMERGENCY PSYCHIATRIC') ||
      searchText.includes('PSYCHIATRIC ER') ||
      searchText.includes('PSYCHIATRIC EMERGENCY')) {
    return 'cpep';
  }

  return 'other';
};

// Helper function to validate phone numbers
const validatePhoneNumber = (phoneString: string | undefined): { isValid: boolean; cleaned: string; original: string } => {
  if (!phoneString) {
    return { isValid: false, cleaned: '', original: '' };
  }

  const original = phoneString.trim();

  // Strip all non-numeric characters
  const cleaned = phoneString.replace(/\D/g, '');

  // Check if length is valid (10 or 11 digits for US numbers)
  const isValid = cleaned.length === 10 || cleaned.length === 11;

  return { isValid, cleaned, original };
};

// Format time from 24-hour format to 12-hour format
const formatTime = (timeStr: string | null): string => {
  if (!timeStr) return '';
  const [hours, minutes] = timeStr.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
};

// Get today's day of week (0 = Sunday in backend)
const getTodayDayOfWeek = (): number => {
  return new Date().getDay();
};

// Check if location is always open (24/7 with no special notes)
const isLocationAlwaysOpen = (hours: OperatingHours[] | undefined): boolean => {
  if (!hours || hours.length === 0) return false;

  // Must have exactly 7 days of hours (all days of the week)
  if (hours.length < 7) return false;

  // Check if all 7 days are 24 hours AND have no notes
  for (let dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {
    const dayHours = hours.find(h => h.day_of_week === dayOfWeek);
    if (!dayHours || !dayHours.is_24_hours || (dayHours.notes && dayHours.notes.trim() !== '')) {
      return false;
    }
  }

  return true;
};

// Format operating hours for display
const formatOperatingHours = (hours: OperatingHours[] | undefined, t: (key: any) => string): string => {
  if (!hours || hours.length === 0) return '';

  const today = getTodayDayOfWeek();
  const todayHours = hours.find(h => h.day_of_week === today);

  if (!todayHours) return '';

  if (todayHours.is_closed) {
    return t('closedToday');
  }

  if (todayHours.is_24_hours) {
    return t('access247') + (todayHours.notes ? ` - ${todayHours.notes}` : '');
  }

  if (todayHours.open_time && todayHours.close_time) {
    const openTime = formatTime(todayHours.open_time);
    const closeTime = formatTime(todayHours.close_time);
    const timeStr = `${t('today')}: ${openTime} - ${closeTime}`;
    return todayHours.notes ? `${timeStr} (${todayHours.notes})` : timeStr;
  }

  return todayHours.notes || '';
};

// Weekly hours dropdown component
const WeeklyHoursDropdown: React.FC<{ hours: OperatingHours[]; t: (key: any) => string }> = ({ hours, t }) => {
  const [isOpen, setIsOpen] = useState(false);

  const dayKeys = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'] as const;

  const hoursGroupedByDay = dayKeys.map((dayKey, dayIndex) => {
    const dayHours = hours.filter(h => h.day_of_week === dayIndex);
    const primaryHours = dayHours[0];

    if (!primaryHours) {
      return { day: t(dayKey), text: t('hoursNotAvailable') };
    }

    let hoursText = '';
    if (primaryHours.is_closed) {
      hoursText = t('closed');
    } else if (primaryHours.is_24_hours) {
      hoursText = t('hours24');
      if (primaryHours.notes) hoursText += ` (${primaryHours.notes})`;
    } else if (primaryHours.open_time && primaryHours.close_time) {
      const openTime = formatTime(primaryHours.open_time);
      const closeTime = formatTime(primaryHours.close_time);
      hoursText = `${openTime} - ${closeTime}`;
      if (primaryHours.notes) hoursText += ` (${primaryHours.notes})`;
    } else if (primaryHours.notes) {
      hoursText = primaryHours.notes;
    } else {
      hoursText = t('hoursNotAvailable');
    }

    return { day: t(dayKey), text: hoursText };
  });

  const today = getTodayDayOfWeek();

  return (
    <div style={{ marginTop: '8px' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          padding: '4px 8px',
          fontSize: '0.8em',
          cursor: 'pointer',
          width: '100%',
          textAlign: 'left',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <span>📅 {t('viewAllHours')}</span>
        <span>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div style={{
          marginTop: '4px',
          padding: '6px',
          backgroundColor: '#f8f9fa',
          borderRadius: '4px',
          fontSize: '0.8em'
        }}>
          {hoursGroupedByDay.map((item, idx) => (
            <div
              key={idx}
              style={{
                padding: '4px 0',
                borderBottom: idx < hoursGroupedByDay.length - 1 ? '1px solid #dee2e6' : 'none',
                fontWeight: idx === today ? 'bold' : 'normal',
                backgroundColor: idx === today ? '#fff3cd' : 'transparent',
                paddingLeft: idx === today ? '4px' : '0',
                borderRadius: '2px'
              }}
            >
              <strong>{item.day}:</strong> {item.text}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


// Map event handler component
function MapEventHandler({
  onRegionChange,
  isProgrammaticMoveRef
}: {
  onRegionChange: (bounds: any) => void;
  isProgrammaticMoveRef: React.MutableRefObject<boolean>;
}) {
  const lastCenterRef = useRef<{ lat: number; lng: number } | null>(null);

  const map = useMapEvents({
    load: () => {
      // Set initial bounds when map first loads
      const bounds = map.getBounds();
      const zoom = map.getZoom();
      const center = map.getCenter();

      // Store initial center
      lastCenterRef.current = { lat: center.lat, lng: center.lng };

      onRegionChange({
        minLat: bounds.getSouth(),
        maxLat: bounds.getNorth(),
        minLon: bounds.getWest(),
        maxLon: bounds.getEast(),
        center: center,
        zoom: zoom,
      });
    },
    moveend: () => {
      // FLICKER FIX: Skip fetch if this was a programmatic move (e.g., clicking a location card)
      if (isProgrammaticMoveRef.current) {
        isProgrammaticMoveRef.current = false; // Reset flag
        return;
      }

      const bounds = map.getBounds();
      const zoom = map.getZoom();
      const center = map.getCenter();

      // Calculate distance moved from last center
      if (lastCenterRef.current) {
        const latDiff = Math.abs(center.lat - lastCenterRef.current.lat);
        const lngDiff = Math.abs(center.lng - lastCenterRef.current.lng);
        const distance = Math.max(latDiff, lngDiff);

        // Guard clause: If movement is very small (e.g., auto-pan for popup), skip refetch
        // 0.005 degrees ≈ 0.3 miles (500 meters) - prevents unnecessary fetches for popup pans
        if (distance < 0.005) {
          return;
        }
      }

      // Update last center
      lastCenterRef.current = { lat: center.lat, lng: center.lng };

      onRegionChange({
        minLat: bounds.getSouth(),
        maxLat: bounds.getNorth(),
        minLon: bounds.getWest(),
        maxLon: bounds.getEast(),
        center: center,
        zoom: zoom,
      });
    },
  });

  // Also set bounds on component mount as fallback
  useEffect(() => {
    const bounds = map.getBounds();
    const zoom = map.getZoom();
    onRegionChange({
      minLat: bounds.getSouth(),
      maxLat: bounds.getNorth(),
      minLon: bounds.getWest(),
      maxLon: bounds.getEast(),
      center: map.getCenter(),
      zoom: zoom,
    });
  }, [map, onRegionChange]);

  return null;
}

// Center map on user location component
function MapCenterController({ center }: { center: [number, number] | null }) {
  const map = useMap();

  useEffect(() => {
    if (center) {
      map.setView(center, 13, { animate: true });
    }
  }, [center, map]);

  return null;
}

// Marker with custom click handler that has map access
function MarkerWithClick({
  position,
  icon,
  children,
  isProgrammaticMoveRef
}: {
  position: [number, number];
  icon: any;
  children: React.ReactNode;
  isProgrammaticMoveRef: React.MutableRefObject<boolean>;
}) {
  const map = useMap();

  const handleClick = () => {
    // FLICKER FIX: Mark this as a programmatic move to skip API fetch
    isProgrammaticMoveRef.current = true;

    // Pan to marker with offset to show the popup card
    // Offset upward by 150 pixels so the card is visible
    const point = map.project(position, map.getZoom());
    point.y -= 150; // Move view up by 150px to show popup below
    const newCenter = map.unproject(point, map.getZoom());
    map.panTo(newCenter, { animate: true, duration: 0.5 });
  };

  return (
    <Marker position={position} icon={icon} eventHandlers={{ click: handleClick }}>
      {children}
    </Marker>
  );
}

// Helper function to translate service type names
const getServiceTypeName = (name: string, t: any): string => {
  const nameMap: { [key: string]: string } = {
    'Food': t('food'),
    'Intake Center': t('intakeCenter'),
    'Drop-In Center': t('dropInCenter'),
    'Hygiene': t('hygiene'),
    'Medical': t('medical'),
    'Social Services': t('social'),
    'Case Management': t('caseManagement'),
    'Warming Center': t('warmingCenter'),
    'Cooling Center': t('coolingCenter'),
    'Hospitals': t('hospitals'),
    'Shelter': t('shelter'),
    'Free WiFi (LinkNYC)': t('freeWifiLinkNYC'),
    'Free WiFi & Charging': t('freeWifiLinkNYC'),
    'Public Restrooms': t('publicRestrooms'),
    'Mental Health Crisis': t('mentalHealthCrisis'),
    'Youth Services': t('youthServices'),
    'Benefits & ID Help': t('benefitsId'),
    'DV Hotline': t('dvHotline'),
  };
  return nameMap[name] || name;
};

// Center button component

const MapScreen: React.FC = () => {
  const { t } = useLanguage();
  const [services, setServices] = useState<ServiceLocation[]>([]);
  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [foodSubFilters, setFoodSubFilters] = useState<{hotMeals: boolean, groceries: boolean}>({ hotMeals: true, groceries: true });
  const [crisisSubFilters, setCrisisSubFilters] = useState<{cpep: boolean, other: boolean}>({ cpep: true, other: true });
  const [userLocation, setUserLocation] = useState<[number, number]>([40.7580, -73.9855]);
  const [showDHSInfo, setShowDHSInfo] = useState<boolean>(false);
  const [openNow, setOpenNow] = useState<boolean>(false);
  const [mapBounds, setMapBounds] = useState<any>(null);
  const [mapCenter, setMapCenter] = useState<[number, number] | null>(null);
  const [locationRequested, setLocationRequested] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const abortControllerRef = React.useRef<AbortController | null>(null);

  // NETWORK STATUS: Track connection errors and offline state
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState<boolean>(!navigator.onLine);

  // FLICKER FIX: Track programmatic moves (clicking cards) to prevent unnecessary API fetches
  const isProgrammaticMoveRef = React.useRef<boolean>(false);

  // Client-side caching state
  const loadedLocationIds = React.useRef<Set<string>>(new Set());
  const lastFetchBounds = React.useRef<{minLat: number, maxLat: number, minLng: number, maxLng: number} | null>(null);
  const lastFetchTime = React.useRef<number>(0);
  const lastFetchFilters = React.useRef<{categories: string[], openNow: boolean} | null>(null);

  useEffect(() => {
    fetchServiceTypes();
    // Don't request geolocation on page load - wait for user interaction
  }, []);

  // NETWORK STATUS: Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      setNetworkError(null);
      // Auto-retry fetching services when connection is restored
      if (mapBounds) {
        fetchNearbyServices();
      }
    };

    const handleOffline = () => {
      setIsOffline(true);
      setNetworkError('No Internet Connection');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapBounds]);

  // Handle filter changes - only clear cache when necessary
  useEffect(() => {
    // When openNow changes, we need fresh data (time-dependent)
    if (openNow) {
      loadedLocationIds.current.clear();
      lastFetchBounds.current = null;
      lastFetchFilters.current = null;
      setServices([]);
    }
    // When categories change, don't clear anything - just let the fetch happen
    // The fetch function will check if filters changed and handle accordingly
  }, [selectedCategories, openNow]);

  // Debounced effect for fetching services
  // SECURITY FIX (VULN-005): Added abort controller cleanup to prevent race conditions
  useEffect(() => {
    if (!showDHSInfo && mapBounds) {
      // Debounce the fetch by 500ms
      const timeoutId = setTimeout(() => {
        fetchNearbyServices();
      }, 500);

      return () => {
        clearTimeout(timeoutId);
        // Abort any in-flight request from this effect cycle
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategories, openNow, showDHSInfo, mapBounds]);

  const fetchServiceTypes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/public/service-types`);
      setServiceTypes(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const fetchNearbyServices = async () => {
    if (!mapBounds) return;

    // ZOOM LEVEL CHECK: Block API calls only when zoomed WAY out (state/country level)
    // Clustering handles visual organization at metro/city level (zoom 10-12)
    const MIN_ZOOM_LEVEL = 8; // Very zoomed out = state/country level
    if (mapBounds.zoom && mapBounds.zoom < MIN_ZOOM_LEVEL) {
      debugLog(`Skipping fetch - zoom level ${mapBounds.zoom} < ${MIN_ZOOM_LEVEL} (too zoomed out)`);
      setServices([]); // Clear markers when zoomed out to state/country level
      return;
    }

    // Rate limiting: Don't fetch more than once every 400ms
    const now = Date.now();
    if (now - lastFetchTime.current < 400) {
      debugLog('Skipping fetch - too soon after last request');
      return;
    }

    // Calculate buffered bounds (expand by 15% to reduce edge fetches)
    const latBuffer = (mapBounds.maxLat - mapBounds.minLat) * 0.15;
    const lngBuffer = (mapBounds.maxLon - mapBounds.minLon) * 0.15;

    const bufferedBounds = {
      minLat: mapBounds.minLat - latBuffer,
      maxLat: mapBounds.maxLat + latBuffer,
      minLng: mapBounds.minLon - lngBuffer,
      maxLng: mapBounds.maxLon + lngBuffer,
    };

    // Check if filters have changed
    const filtersChanged = lastFetchFilters.current === null ||
      lastFetchFilters.current.openNow !== openNow ||
      JSON.stringify(lastFetchFilters.current.categories.sort()) !== JSON.stringify(selectedCategories.sort());

    // Check if viewport has significantly changed to avoid redundant fetches
    // BUT always fetch if: (1) filters changed, (2) zoomed in significantly, or (3) panned far away
    if (lastFetchBounds.current && !filtersChanged) {
      const last = lastFetchBounds.current;

      // Calculate viewport size change (zoom change indicator)
      const lastSize = (last.maxLat - last.minLat) * (last.maxLng - last.minLng);
      const currentSize = (bufferedBounds.maxLat - bufferedBounds.minLat) * (bufferedBounds.maxLng - bufferedBounds.minLng);
      const zoomInRatio = lastSize / currentSize;

      // If zoomed in significantly (>2x), always fetch for better accuracy
      if (zoomInRatio > 2) {
        debugLog('Fetching - zoomed in significantly, need more accurate data');
      } else {
        // Only skip fetch if viewport is mostly inside cached bounds AND not zoomed in much
        const isInsideLast =
          bufferedBounds.minLat >= last.minLat &&
          bufferedBounds.maxLat <= last.maxLat &&
          bufferedBounds.minLng >= last.minLng &&
          bufferedBounds.maxLng <= last.maxLng;

        if (isInsideLast) {
          debugLog('Skipping fetch - viewport inside cached bounds and filters unchanged');
          return;
        }
      }
    }

    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller for this request
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    // Clear any previous errors
    setNetworkError(null);
    setIsLoading(true);
    lastFetchTime.current = now;

    try {
      // Use user's actual location for distance calculation (not viewport center)
      // This ensures distances remain consistent as the map moves
      const centerLat = userLocation[0];
      const centerLng = userLocation[1];

      // Use optimized bounding box API with distance sorting and strict limit (75 locations)
      let url = `${API_BASE_URL}/public/services/in-bounds?min_lat=${bufferedBounds.minLat}&max_lat=${bufferedBounds.maxLat}&min_lng=${bufferedBounds.minLng}&max_lng=${bufferedBounds.maxLng}&center_lat=${centerLat}&center_lng=${centerLng}&limit=75`;

      if (selectedCategories.length > 0) {
        selectedCategories.forEach(type => {
          url += `&service_types=${type}`;
        });
      } else {
        // When no category is selected, exclude LinkNYC to prevent loading 2,239 kiosks by default
        // LinkNYC will only show when explicitly selected
        url += `&exclude_service_types=free-wifi-linknyc`;
      }

      // Add open_now parameter if enabled
      if (openNow) {
        url += `&open_now=true`;
      }

      debugLog('Fetching services from bbox:', bufferedBounds);
      const response = await axios.get(url, { signal: abortController.signal });
      debugLog('Received services:', response.data.length);

      // Merge with existing services (deduplication)
      const newServices = response.data;
      const newIds = new Set(newServices.map((s: ServiceLocation) => s.id));

      // Add new IDs to loaded set
      newServices.forEach((s: ServiceLocation) => loadedLocationIds.current.add(s.id));

      // When filters change, REPLACE services (don't merge with old filtered results)
      // When just panning/zooming, MERGE with existing services
      if (filtersChanged) {
        // Filter changed: replace all services with new results
        debugLog('Filters changed - replacing services');
        setServices(newServices);
      } else {
        // Just viewport change: merge with existing services using LRU (Recency) strategy
        debugLog('Viewport changed - merging services with LRU pruning');
        setServices(prev => {
          const existingNotInNew = prev.filter(s => !newIds.has(s.id));

          // FIX 3: LRU Cache Strategy - Put new services at FRONT, old data falls off the END
          // This ensures newly fetched data (at viewport edge) is always preserved
          // PERFORMANCE FIX (PERF-001): Prevent unbounded growth with 3000 item cap (~6MB JSON)
          let combined = [...newServices, ...existingNotInNew];

          // Hard cap the cache at 3000 locations to prevent memory leaks
          // Increased from 2000 to 3000 to reduce re-fetches with 4k+ total locations
          const MAX_CACHE_SIZE = 3000;
          if (combined.length > MAX_CACHE_SIZE) {
            // Simply slice to keep the first 3000 (most recent)
            // New data is at the front (index 0), old data naturally falls off the end
            combined = combined.slice(0, MAX_CACHE_SIZE);
            debugLog(`Cache size exceeded ${MAX_CACHE_SIZE}, pruned using LRU (kept most recent)`);
          }

          return combined;
        });
      }

      // Update last fetched bounds and filters
      lastFetchBounds.current = bufferedBounds;
      lastFetchFilters.current = {
        categories: [...selectedCategories],
        openNow: openNow
      };
    } catch (error) {
      if (axios.isCancel(error)) {
        debugLog('Request cancelled:', error.message);
      } else {
        console.error('Error fetching services:', error);
        // NETWORK ERROR: Show user-friendly error message
        if (axios.isAxiosError(error)) {
          if (!error.response) {
            // Network error (no response from server)
            setNetworkError('Unable to load locations. Check your connection.');
          } else if (error.response.status >= 500) {
            // Server error
            setNetworkError('Server error. Please try again later.');
          } else {
            // Other error
            setNetworkError('Failed to load locations. Please try again.');
          }
        } else {
          setNetworkError('Unable to load locations. Check your connection.');
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegionChange = useCallback((bounds: any) => {
    setMapBounds(bounds);
  }, []);

  const handleRetry = () => {
    setNetworkError(null);
    if (mapBounds) {
      fetchNearbyServices();
    }
  };

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? [] // Deselect if already selected
        : [category] // Replace with new selection (single selection)
    );
  };

  const handleDHSCall = () => {
    window.location.href = 'tel:311';
  };

  const handleCenterMap = () => {
    // Request geolocation only when user clicks center button
    if (!locationRequested && navigator.geolocation) {
      setLocationRequested(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newLocation: [number, number] = [position.coords.latitude, position.coords.longitude];
          setUserLocation(newLocation);
          setMapCenter(newLocation);
          setTimeout(() => setMapCenter(null), 100);
        },
        (error) => {
          console.error('Error getting location:', error);
          // Fall back to default NYC location
          setMapCenter(userLocation);
          setTimeout(() => setMapCenter(null), 100);
        }
      );
    } else {
      // Already have location, just center
      setMapCenter(userLocation);
      setTimeout(() => setMapCenter(null), 100);
    }
  };

  // FIX 1: Viewport Pruning - Only render markers that are visible on screen
  // Keep all services in memory (JavaScript is fast), but only render what's visible (DOM is slow)
  // SECURITY FIX (VULN-002): Move filter logic inside useMemo to avoid stale closure
  const visibleServices = useMemo(() => {
    if (!mapBounds) return services;

    // Define filter logic inline to prevent stale closure issues
    const matchesFoodFilter = (service: ServiceLocation): boolean => {
      // If food filter is not active, return true (no filtering needed)
      if (!selectedCategories.includes('food')) {
        return true;
      }

      // If both sub-filters are on or both are off, show everything
      if (foodSubFilters.hotMeals === foodSubFilters.groceries) {
        return true;
      }

      // Check each food service using the classification helper
      const foodServices = service.services.filter(s => s.type === 'food');

      for (const foodService of foodServices) {
        const subCategory = getFoodSubCategory(foodService);

        // PERMISSIVE FILTER LOGIC:
        // Generic 'food' items are shown in BOTH filters (better to show than hide)
        if (subCategory === 'food') {
          return true;
        }

        // Show soup kitchens if hot meals filter is on
        if (subCategory === 'soup-kitchen' && foodSubFilters.hotMeals) {
          return true;
        }

        // Show pantries if groceries filter is on
        if (subCategory === 'pantry' && foodSubFilters.groceries) {
          return true;
        }
      }

      return false;
    };

    // Mental Health Crisis sub-filter logic
    const matchesCrisisFilter = (service: ServiceLocation): boolean => {
      // If mental health crisis filter is not active, return true
      if (!selectedCategories.includes('mental-health-crisis')) {
        return true;
      }

      // If both sub-filters are on or both are off, show everything
      if (crisisSubFilters.cpep === crisisSubFilters.other) {
        return true;
      }

      // Check mental health crisis services
      const crisisServices = service.services.filter(s => s.type === 'mental-health-crisis');

      for (const crisisService of crisisServices) {
        const subCategory = getCrisisSubCategory(crisisService, service.description);

        // Show CPEP locations if cpep filter is on
        if (subCategory === 'cpep' && crisisSubFilters.cpep) {
          return true;
        }

        // Show other crisis services if other filter is on
        if (subCategory === 'other' && crisisSubFilters.other) {
          return true;
        }
      }

      return false;
    };

    // Filter services to only those within current viewport bounds and matching sub-filters
    return services.filter(service => {
      const isInBounds =
        service.latitude >= mapBounds.minLat &&
        service.latitude <= mapBounds.maxLat &&
        service.longitude >= mapBounds.minLon &&
        service.longitude <= mapBounds.maxLon;

      return isInBounds && matchesFoodFilter(service) && matchesCrisisFilter(service);
    });
  }, [services, mapBounds, foodSubFilters, crisisSubFilters, selectedCategories]);

  // Log viewport pruning stats
  useEffect(() => {
    if (services.length !== visibleServices.length) {
      debugLog(`Viewport pruning: ${services.length} in cache, ${visibleServices.length} visible`);
    }
  }, [services.length, visibleServices.length]);

  // PERFORMANCE FIX: Memoize markers to prevent flickering on state changes
  // Only re-render markers when visibleServices, selectedCategories, serviceTypes, or language changes
  const memoizedMarkers = useMemo(() => {
    return visibleServices.map(service => {
      // Context-Aware Icon Logic: Icon adapts to active filter
      let iconServiceType = service.services[0]?.type || 'food';
      let iconSymbol: string | undefined = undefined;

      // If a specific category filter is active, use that service type for the icon (if the location has it)
      if (selectedCategories.length > 0) {
        const activeFilter = selectedCategories[0];
        const hasActiveService = service.services.some(s => s.type === activeFilter);
        if (hasActiveService) {
          iconServiceType = activeFilter;
        }
      }

      // Determine icon symbol and color based on service type and sub-category
      let customColor: string | undefined = undefined;

      if (iconServiceType === 'food') {
        // Get the first food service to determine icon and color
        const foodServices = service.services.filter(s => s.type === 'food');
        if (foodServices.length > 0) {
          const subCategory = getFoodSubCategory(foodServices[0]);
          if (subCategory === 'soup-kitchen') {
            iconSymbol = 'food-hot';
            customColor = '#E53935'; // Red for hot meals/soup kitchens
          } else if (subCategory === 'pantry') {
            iconSymbol = 'food-grocery';
            customColor = '#43A047'; // Green for food pantries/groceries
          }
        }
      } else if (iconServiceType === 'mental-health-crisis') {
        // Different colors for CPEP vs other crisis services
        const crisisServices = service.services.filter(s => s.type === 'mental-health-crisis');
        if (crisisServices.length > 0) {
          const subCategory = getCrisisSubCategory(crisisServices[0], service.description);
          if (subCategory === 'cpep') {
            customColor = '#E91E63'; // Pink/Magenta for CPEP (ER)
            iconSymbol = 'medical';
          } else {
            customColor = '#7B1FA2'; // Dark purple for clinics/hotlines
          }
        }
      } else if (iconServiceType === 'shelter') {
        iconSymbol = 'shelter';
      } else if (iconServiceType === 'intake') {
        iconSymbol = 'intake';
      } else if (iconServiceType === 'drop-in') {
        iconSymbol = 'drop-in';
      } else if (iconServiceType === 'medical') {
        iconSymbol = 'medical';
      }

      const serviceTypeColor = customColor || serviceTypes.find(st => st.slug === iconServiceType)?.color_hex || '#FF6B6B';
      const markerIcon = createColoredIcon(serviceTypeColor, iconSymbol);
      const operatingHoursText = formatOperatingHours(service.operating_hours, t);
      const isAlwaysOpen = isLocationAlwaysOpen(service.operating_hours);

      return (
        <MarkerWithClick
          key={service.id}
          position={[service.latitude, service.longitude]}
          icon={markerIcon}
          isProgrammaticMoveRef={isProgrammaticMoveRef}
        >
        <Popup
          autoPan={false}
          keepInView={false}
          closeOnClick={true}
          className="map-interactive-popup"
        >
          <h3>{service.name}</h3>
          <p>{service.street_address}</p>
          <p>📍 {(service.distance_km / KM_PER_MILE).toFixed(1)} {t('milesAway')}</p>

          {/* Special messaging for Intake and Drop-In Centers */}
          {iconServiceType === 'intake' && (
            <div style={{
              marginTop: '8px',
              padding: '8px 10px',
              backgroundColor: '#FFF5F5',
              border: '2px solid #E53E3E',
              borderRadius: '6px',
              fontSize: '0.9em',
              fontWeight: '600',
              color: '#C53030',
              textAlign: 'center'
            }}>
              🛑 {t('entryPoint')}
            </div>
          )}

          {iconServiceType === 'drop-in' && (
            <div style={{
              marginTop: '8px',
              padding: '8px 10px',
              backgroundColor: '#EDF2F7',
              border: '2px solid #4299E1',
              borderRadius: '6px',
              fontSize: '0.9em',
              fontWeight: '600',
              color: '#2C5282',
              textAlign: 'center'
            }}>
              🛋️ {t('dropInCenter')}
            </div>
          )}

          {/* Mental Health Crisis - Show description with actionable info */}
          {iconServiceType === 'mental-health-crisis' && service.description && (
            <div style={{
              marginTop: '8px',
              padding: '8px 10px',
              backgroundColor: service.description.includes('EMERGENCY PSYCHIATRIC ER') ? '#FFF5F5' :
                             service.description.includes('CALL FOR SERVICE') ? '#FFFBEB' :
                             service.description.includes('CALL FIRST') ? '#FFFBEB' :
                             service.description.includes('REFERRAL REQUIRED') ? '#FEF3C7' : '#F0FFF4',
              border: `2px solid ${service.description.includes('EMERGENCY PSYCHIATRIC ER') ? '#E91E63' :
                                   service.description.includes('CALL') ? '#F59E0B' :
                                   service.description.includes('REFERRAL') ? '#D97706' : '#38A169'}`,
              borderRadius: '6px',
              fontSize: '0.85em',
              fontWeight: '600',
              color: service.description.includes('EMERGENCY PSYCHIATRIC ER') ? '#9D174D' :
                     service.description.includes('CALL') ? '#92400E' :
                     service.description.includes('REFERRAL') ? '#92400E' : '#276749',
              textAlign: 'center'
            }}>
              {service.description}
            </div>
          )}

          {/* Operating Hours Section - Always Show */}
          <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid #e0e0e0' }}>
            {isAlwaysOpen ? (
              <p style={{ fontSize: '0.95em', fontWeight: '600', color: '#38A169' }}>
                ⏰ {t('open24Hours')}
              </p>
            ) : operatingHoursText ? (
              <div>
                <p style={{ fontSize: '0.95em', fontWeight: '600', marginBottom: '6px' }}>⏰ {t('operatingHours')}:</p>
                <p style={{ fontSize: '0.9em', whiteSpace: 'pre-line', color: '#555' }}>
                  {operatingHoursText}
                </p>
                {/* Weekly Hours Dropdown - Show full week schedule */}
                {service.operating_hours && service.operating_hours.length > 0 && (
                  <WeeklyHoursDropdown hours={service.operating_hours} t={t} />
                )}
              </div>
            ) : (
              <p style={{ fontSize: '0.9em', color: '#999', fontStyle: 'italic' }}>
                {t('hoursNotAvailable')}
              </p>
            )}
          </div>

          {/* Services List */}
          <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid #e0e0e0' }}>
            <p style={{ fontWeight: '600', marginBottom: '6px', fontSize: '0.95em' }}>{t('services')}:</p>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.9em' }}>
              {service.services.map((svc, idx) => {
                let displayName = getServiceTypeName(svc.name, t);
                let capacityLabel = null;
                let showNotes = true;

                // For food services, show Soup Kitchen or Food Pantry instead of generic "Food"
                if (svc.type === 'food') {
                  const subCategory = getFoodSubCategory(svc);
                  if (subCategory === 'soup-kitchen') {
                    displayName = `🥣 ${t('hotMeals')}`; // Soup Kitchen
                    showNotes = false; // Don't show "SK" code
                  } else if (subCategory === 'pantry') {
                    displayName = `🛍️ ${t('groceries')}`; // Food Pantry
                    showNotes = false; // Don't show "FP" code
                  }
                  if (svc.capacity && svc.capacity > 0) {
                    capacityLabel = ` (${svc.capacity} people)`;
                  }
                }

                // Capacity display logic for shelter
                if (svc.type === 'shelter') {
                  if (svc.capacity && svc.capacity > 0) {
                    capacityLabel = ` (${svc.capacity} ${t('beds')})`;
                  }
                }

                // For mental health crisis, show CPEP or Clinic label
                if (svc.type === 'mental-health-crisis') {
                  const crisisSubCategory = getCrisisSubCategory(svc, service.description);
                  if (crisisSubCategory === 'cpep') {
                    displayName = `🚨 ${t('cpepEmergency')}`;
                  } else {
                    displayName = `🧠 ${t('otherCrisis')}`;
                  }
                  showNotes = false;
                }

                return (
                  <li key={idx}>
                    {displayName}
                    {capacityLabel && <span>{capacityLabel}</span>}
                    {showNotes && svc.notes && <span style={{ fontSize: '0.9em', color: '#666' }}> ({svc.notes})</span>}
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Action Buttons - Row layout for space saving */}
          <div style={{ marginTop: '12px', display: 'flex', gap: '10px' }}>
            {/* Phone Button with Validation */}
            {(() => {
              const phoneValidation = validatePhoneNumber(service.phone);
              if (phoneValidation.isValid) {
                return (
                  <a
                    href={`tel:${phoneValidation.cleaned}`}
                    style={{
                      flex: 1,
                      display: 'block',
                      padding: '12px',
                      backgroundColor: '#38A169',
                      color: '#fff',
                      textAlign: 'center',
                      textDecoration: 'none',
                      borderRadius: '8px',
                      fontWeight: '600',
                      fontSize: '1em',
                    }}
                  >
                    📞 {t('call')}
                  </a>
                );
              } else if (service.phone) {
                // SECURITY FIX (VULN-003): Sanitize phone display - only show printable ASCII and common phone chars
                const safeDisplay = phoneValidation.original.replace(/[^\d\s\-()+ .x]/gi, '');
                return (
                  <div style={{
                    flex: 1,
                    padding: '8px',
                    fontSize: '0.95em',
                    color: '#333',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    textAlign: 'center',
                    border: '1px solid #ddd'
                  }}>
                    📞 {safeDisplay}
                  </div>
                );
              }
              return null;
            })()}

            {/* Directions Button */}
            <a
              href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(service.street_address)}&travelmode=transit`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                flex: 1,
                display: 'block',
                padding: '12px',
                backgroundColor: '#4299E1',
                color: '#fff',
                textAlign: 'center',
                textDecoration: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '1em',
              }}
            >
              🚶 {t('directions')}
            </a>
          </div>
        </Popup>
      </MarkerWithClick>
      );
    });
  }, [visibleServices, selectedCategories, serviceTypes, t, isProgrammaticMoveRef]);

  return (
    <div style={styles.container}>
      {/* NETWORK ERROR BANNER - Shows connection issues */}
      {(networkError || isOffline) && (
        <div style={styles.networkErrorBanner}>
          <div style={styles.networkErrorContent}>
            <span style={styles.networkErrorIcon}>
              {isOffline ? '⚠️' : '❌'}
            </span>
            <span style={styles.networkErrorText}>
              {isOffline ? 'No Internet Connection' : networkError}
            </span>
            <button
              onClick={handleRetry}
              style={styles.retryButton}
              disabled={isOffline}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* DHS Safe Options Card Overlay - renders on top of map without unmounting it */}
      {showDHSInfo && (
        <div style={styles.dhsContainer}>
          <div style={styles.dhsCard}>
            <div style={styles.dhsIcon}>🏛️</div>
            <h2 style={styles.dhsTitle}>Safe Options & Intake</h2>
            <h3 style={styles.dhsSubtitle}>{t('officialDHSEntryPoints')}</h3>

            {/* Warning Block */}
            <div style={styles.dhsWarningBlock}>
              <p style={styles.dhsWarningText}>
                ℹ️ {t('dhsWarning')}
              </p>
            </div>

            {/* Action Buttons Row */}
            <div style={styles.dhsActionRow}>
              <button onClick={handleDHSCall} style={styles.dhsActionButton}>
                📞 {t('call311')}<br />
                <span style={styles.dhsActionSubtext}>{t('cityServices')}</span>
              </button>
              <a
                href="tel:988"
                style={styles.dhsActionButton}
                onClick={(e) => {
                  e.preventDefault();
                  window.location.href = 'tel:988';
                }}
              >
                🧠 {t('call988')}<br />
                <span style={styles.dhsActionSubtext}>{t('mentalHealth')}</span>
              </a>
            </div>

            {/* Intake Centers Section */}
            <div style={styles.dhsSection}>
              <h4 style={styles.dhsSectionTitle}>🛑 {t('intakeCentersTitle')}</h4>
              <p style={styles.dhsSectionSubtext}>{t('intakeCentersSubtext')}</p>

              <div style={styles.dhsLocationList}>
                <div style={styles.dhsLocationItem}>
                  <strong>{t('familiesWithKids')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=151+East+151st+St+Bronx+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    151 East 151st St, Bronx (PATH)
                  </a>
                </div>

                <div style={styles.dhsLocationItem}>
                  <strong>{t('singleMen')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=400+East+30th+St+Manhattan+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    400-430 East 30th St, Manhattan
                  </a>
                </div>

                <div style={styles.dhsLocationItem}>
                  <strong>{t('singleWomen')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=116+Williams+Ave+Brooklyn+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    116 Williams Ave, Brooklyn (HELP Center)
                  </a>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=1122+Franklin+Ave+Bronx+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    1122 Franklin Ave, Bronx (Franklin Shelter)
                  </a>
                </div>

                <div style={styles.dhsLocationItem}>
                  <strong>{t('adultFamilies')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=400+East+30th+St+Manhattan+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    400-430 East 30th St, Manhattan (AFIC)
                  </a>
                </div>
              </div>
            </div>

            {/* Drop-In Centers Section */}
            <div style={styles.dhsSection}>
              <h4 style={styles.dhsSectionTitle}>🛋️ {t('dropInCentersTitle')}</h4>
              <p style={styles.dhsSectionSubtext}>{t('dropInCentersSubtext')}</p>

              <div style={styles.dhsLocationList}>
                <div style={styles.dhsLocationItem}>
                  <strong>{t('manhattan')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=120+E+32nd+St+Manhattan+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    Mainchance (120 E 32nd St)
                  </a>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=257+W+30th+St+Manhattan+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    Olivieri Center (257 W 30th St)
                  </a>
                </div>

                <div style={styles.dhsLocationItem}>
                  <strong>{t('bronx')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=800+Barretto+St+Bronx+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    The Living Room (800 Barretto St)
                  </a>
                </div>

                <div style={styles.dhsLocationItem}>
                  <strong>{t('brooklyn')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=2402+Atlantic+Ave+Brooklyn+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    The Gathering Place (2402 Atlantic Ave)
                  </a>
                </div>

                <div style={styles.dhsLocationItem}>
                  <strong>{t('statenIsland')}</strong>
                  <a
                    href="https://www.google.com/maps/dir/?api=1&destination=25+Central+Ave+Staten+Island+NY&travelmode=transit"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.dhsAddressLink}
                  >
                    Project Hospitality (25 Central Ave)
                  </a>
                </div>
              </div>
            </div>

            <button onClick={() => setShowDHSInfo(false)} style={styles.dhsBackButton}>
              ← Back to Map
            </button>
          </div>
        </div>
      )}

      {/* Results count at top - removed cached count as it adds no value */}
      <div style={styles.resultsCount}>
        {isLoading ? t('loading') : `${visibleServices.length} ${t('locationsFound')}`}
      </div>

      {/* Map */}
      <div style={styles.mapContainer}>
        {/* Loading indicator overlay */}
        {isLoading && (
          <div style={{
            position: 'absolute',
            top: '80px',
            right: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            padding: '10px 16px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            zIndex: 1000,
            fontSize: '14px',
            fontWeight: 500,
            color: COLORS.text,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <span style={{ animation: 'spin 1s linear infinite' }}>🔄</span>
            {t('loading')}...
          </div>
        )}

        {/* Filters overlay at bottom of map */}
        <div style={styles.filtersOverlay}>
          <div style={styles.filterRow}>
            <button
              onClick={() => setShowDHSInfo(true)}
              style={styles.dhsToggleButton}
            >
              🏛️ {t('dhsOfficial')}
            </button>

            <button
              onClick={() => setOpenNow(!openNow)}
              style={{
                ...styles.filterButton,
                ...(openNow ? styles.filterButtonActive : {}),
              }}
            >
              {openNow ? '✓ ' : ''}{t('openNow')}
            </button>

            <button
              onClick={handleCenterMap}
              style={styles.centerButton}
              title="Center map on my location"
              aria-label="Center map on my location"
            >
              🎯
            </button>
          </div>

          <div style={styles.categoryFiltersScroll}>
            {serviceTypes.map(type => {
              // Special handling for DV Hotline - opens phone call, styled as text link
              if (type.slug === 'dv-hotline') {
                return (
                  <a
                    key={type.slug}
                    href="tel:1-800-621-4673"
                    style={{
                      padding: `${SPACING.xs} ${SPACING.sm}`,
                      fontSize: TYPOGRAPHY.fontSize.xs,
                      fontWeight: TYPOGRAPHY.fontWeight.bold,
                      color: type.color_hex,
                      backgroundColor: 'transparent',
                      border: `2px dashed ${type.color_hex}`,
                      borderRadius: '6px',
                      textDecoration: 'none',
                      display: 'inline-flex',
                      alignItems: 'center',
                      whiteSpace: 'nowrap',
                    }}
                    title={t('dvHotlineDesc')}
                  >
                    📞 {t('dvHotline')}
                  </a>
                );
              }

              // Mental Health Crisis - distinct styling for police/EMS visibility
              const isCrisisButton = type.slug === 'mental-health-crisis';
              const isSelected = selectedCategories.includes(type.slug);

              return (
                <button
                  key={type.slug}
                  onClick={() => handleCategoryToggle(type.slug)}
                  style={{
                    ...styles.categoryButton,
                    // Crisis button: bold border and slightly larger when not selected
                    ...(isCrisisButton && !isSelected ? {
                      borderWidth: '3px',
                      borderColor: type.color_hex,
                      fontWeight: TYPOGRAPHY.fontWeight.bold,
                    } : {}),
                    ...(isSelected ? {
                      backgroundColor: type.color_hex,
                      color: '#fff',
                      borderColor: type.color_hex,
                      ...(isCrisisButton ? { borderWidth: '3px' } : {}),
                    } : {}),
                  }}
                >
                  {/* Add brain emoji for Crisis button to make it stand out */}
                  {isCrisisButton && '🧠 '}
                  {getServiceTypeName(type.name, t)}
                </button>
              );
            })}
          </div>

          {/* Food Sub-Filters - Show when Food filter is active */}
          {selectedCategories.includes('food') && (
            <div style={{ display: 'flex', gap: SPACING.xs, marginTop: SPACING.xs, paddingLeft: '4px' }}>
              <button
                onClick={() => setFoodSubFilters(prev => ({ ...prev, hotMeals: !prev.hotMeals }))}
                style={{
                  padding: `${SPACING.xs} ${SPACING.sm}`,
                  fontSize: TYPOGRAPHY.fontSize.xs,
                  fontWeight: TYPOGRAPHY.fontWeight.medium,
                  color: foodSubFilters.hotMeals ? '#fff' : COLORS.text,
                  backgroundColor: foodSubFilters.hotMeals ? '#38A169' : COLORS.background,
                  border: `2px solid ${foodSubFilters.hotMeals ? '#38A169' : COLORS.border}`,
                  borderRadius: '6px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                {foodSubFilters.hotMeals ? '✓ ' : ''}🥣 {t('hotMeals')}
              </button>
              <button
                onClick={() => setFoodSubFilters(prev => ({ ...prev, groceries: !prev.groceries }))}
                style={{
                  padding: `${SPACING.xs} ${SPACING.sm}`,
                  fontSize: TYPOGRAPHY.fontSize.xs,
                  fontWeight: TYPOGRAPHY.fontWeight.medium,
                  color: foodSubFilters.groceries ? '#fff' : COLORS.text,
                  backgroundColor: foodSubFilters.groceries ? '#38A169' : COLORS.background,
                  border: `2px solid ${foodSubFilters.groceries ? '#38A169' : COLORS.border}`,
                  borderRadius: '6px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                {foodSubFilters.groceries ? '✓ ' : ''}🛍️ {t('groceries')}
              </button>
            </div>
          )}

          {/* Mental Health Crisis Sub-Filters - Show when Crisis filter is active */}
          {selectedCategories.includes('mental-health-crisis') && (
            <div style={{ display: 'flex', gap: SPACING.xs, marginTop: SPACING.xs, paddingLeft: '4px' }}>
              <button
                onClick={() => setCrisisSubFilters(prev => ({ ...prev, cpep: !prev.cpep }))}
                style={{
                  padding: `${SPACING.xs} ${SPACING.sm}`,
                  fontSize: TYPOGRAPHY.fontSize.xs,
                  fontWeight: TYPOGRAPHY.fontWeight.medium,
                  color: crisisSubFilters.cpep ? '#fff' : COLORS.text,
                  backgroundColor: crisisSubFilters.cpep ? '#E91E63' : COLORS.background,
                  border: `2px solid ${crisisSubFilters.cpep ? '#E91E63' : COLORS.border}`,
                  borderRadius: '6px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                {crisisSubFilters.cpep ? '✓ ' : ''}🚨 {t('cpepEmergency')}
              </button>
              <button
                onClick={() => setCrisisSubFilters(prev => ({ ...prev, other: !prev.other }))}
                style={{
                  padding: `${SPACING.xs} ${SPACING.sm}`,
                  fontSize: TYPOGRAPHY.fontSize.xs,
                  fontWeight: TYPOGRAPHY.fontWeight.medium,
                  color: crisisSubFilters.other ? '#fff' : COLORS.text,
                  backgroundColor: crisisSubFilters.other ? '#9C27B0' : COLORS.background,
                  border: `2px solid ${crisisSubFilters.other ? '#9C27B0' : COLORS.border}`,
                  borderRadius: '6px',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                {crisisSubFilters.other ? '✓ ' : ''}🧠 {t('otherCrisis')}
              </button>
            </div>
          )}
        </div>
        <MapContainer
          center={userLocation}
          zoom={13}
          style={{ height: '100dvh', width: '100%' }}
          doubleClickZoom={true}
          scrollWheelZoom={true}
          touchZoom={true}
          zoomControl={true}
        >
          <TileLayer
  // This attribution is legally required by Carto
  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
  // This is the "Voyager" style (Streets + Navigation)
  url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
/>
          <MapEventHandler onRegionChange={handleRegionChange} isProgrammaticMoveRef={isProgrammaticMoveRef} />
          <MapCenterController center={mapCenter} />

          {/* User location indicator */}
          <Circle
            center={userLocation}
            radius={100}
            pathOptions={{
              color: '#3388ff',
              fillColor: '#3388ff',
              fillOpacity: 0.3,
              weight: 2
            }}
          />
          <Circle
            center={userLocation}
            radius={15}
            pathOptions={{
              color: '#3388ff',
              fillColor: '#3388ff',
              fillOpacity: 0.8,
              weight: 2
            }}
          />

          {/* FIX 2: Marker Clustering - Groups nearby markers at zoom 0-13, individual markers at zoom 14+ */}
          {/* PERFORMANCE FIX: Use memoized markers to prevent flickering */}
          <MarkerClusterGroup
            chunkedLoading
            maxClusterRadius={80}  // Increased from 50 to 80 for better clustering with 4k+ locations
            spiderfyOnMaxZoom={true}
            showCoverageOnHover={false}
            zoomToBoundsOnClick={true}
            disableClusteringAtZoom={14}  // Show individual markers at zoom 14+ (street level), clusters at zoom 0-13
            animate={false}  // Disable animation to prevent flickering on marker click
          >
            {memoizedMarkers}
          </MarkerClusterGroup>
        </MapContainer>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    height: '100%',
    width: '100%',
    overflow: 'hidden',
    touchAction: 'none',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 1,
  },
  filtersOverlay: {
    position: 'fixed',
    bottom: '10%',
    left: 16,
    right: 16,
    maxWidth: '800px',
    margin: '0 auto',
    zIndex: 1000,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    borderRadius: '12px',
    padding: SPACING.xs,
    boxShadow: '0 8px 32px rgba(0,0,0,0.25)',
},
  filterRow: {
    display: 'flex',
    gap: SPACING.xs,
    marginBottom: SPACING.xs,
  },
  dhsToggleButton: {
    padding: `${SPACING.sm} ${SPACING.md}`,
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.textInverse,
    backgroundColor: COLORS.accentWarning,
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  },
  filterButton: {
    padding: `${SPACING.sm} ${SPACING.md}`,
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.text,
    backgroundColor: COLORS.background,
    border: `2px solid ${COLORS.border}`,
    borderRadius: '8px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  },
  filterButtonActive: {
    backgroundColor: COLORS.accent,
    color: COLORS.textInverse,
    borderColor: COLORS.accent,
  },
  categoryFiltersScroll: {
    display: 'flex',
    gap: SPACING.xs,
    overflowX: 'auto',
    overflowY: 'hidden',
    paddingBottom: SPACING.xs,
    scrollbarWidth: 'thin',
    WebkitOverflowScrolling: 'touch',
  },
  categoryButton: {
    padding: `${SPACING.sm} ${SPACING.md}`,
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.text,
    backgroundColor: COLORS.background,
    border: `2px solid ${COLORS.border}`,
    borderRadius: '8px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  },
  centerButton: {
    padding: `${SPACING.sm} ${SPACING.md}`,
    fontSize: '20px',
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.text,
    backgroundColor: COLORS.background,
    border: `2px solid ${COLORS.border}`,
    borderRadius: '8px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    flexShrink: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  mapContainer: {
    flex: 1,
    position: 'relative',
  },
  resultsCount: {
    position: 'absolute',
    top: SPACING.sm,
    right: SPACING.sm,
    padding: `${SPACING.xs} ${SPACING.sm}`,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    borderRadius: '8px',
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.text,
    boxShadow: '0 4px 8px rgba(0,0,0,0.15)', 
    zIndex: 1000,
},
  dhsContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: SPACING.xl,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    backdropFilter: 'blur(4px)',
    zIndex: 2000,
  },
  dhsCard: {
    maxWidth: '700px',
    maxHeight: '75vh',
    overflowY: 'auto',
    padding: SPACING.xl,
    backgroundColor: COLORS.background,
    borderRadius: '16px',
    boxShadow: '0 12px 40px rgba(0,0,0,0.2)',
    textAlign: 'left',
},
  dhsIcon: {
    fontSize: '48px',
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  dhsTitle: {
    fontSize: TYPOGRAPHY.fontSize['2xl'],
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.primary,
    marginBottom: SPACING.xs,
    textAlign: 'center',
  },
  dhsSubtitle: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.textSecondary,
    marginBottom: SPACING.lg,
    textAlign: 'center',
  },
  dhsText: {
    fontSize: TYPOGRAPHY.fontSize.base,
    lineHeight: TYPOGRAPHY.lineHeight.relaxed,
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  dhsWarningBlock: {
    backgroundColor: '#FFF4E6',
    border: '2px solid #FFB84D',
    borderRadius: '8px',
    padding: SPACING.md,
    marginBottom: SPACING.lg,
  },
  dhsWarningText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    lineHeight: TYPOGRAPHY.lineHeight.relaxed,
    color: '#744210',
    margin: 0,
  },
  dhsActionRow: {
    display: 'flex',
    gap: SPACING.sm,
    marginBottom: SPACING.xl,
  },
  dhsActionButton: {
    flex: 1,
    padding: SPACING.md,
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.textInverse,
    backgroundColor: COLORS.accent,
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    textAlign: 'center',
    textDecoration: 'none',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dhsActionSubtext: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    fontWeight: TYPOGRAPHY.fontWeight.normal,
    marginTop: '4px',
    opacity: 0.9,
  },
  dhsSection: {
    marginBottom: SPACING.xl,
    paddingBottom: SPACING.lg,
    borderBottom: `1px solid ${COLORS.border}`,
  },
  dhsSectionTitle: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.text,
    marginBottom: SPACING.xs,
    marginTop: 0,
  },
  dhsSectionSubtext: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textSecondary,
    marginBottom: SPACING.md,
    fontStyle: 'italic',
  },
  dhsLocationList: {
    display: 'flex',
    flexDirection: 'column',
    gap: SPACING.md,
  },
  dhsLocationItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: SPACING.xs,
  },
  dhsAddressLink: {
    color: COLORS.primary,
    textDecoration: 'none',
    fontSize: TYPOGRAPHY.fontSize.sm,
    paddingLeft: SPACING.md,
    display: 'block',
    transition: 'color 0.2s',
  },
  dhsBackButton: {
    padding: `${SPACING.sm} ${SPACING.lg}`,
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.primary,
    backgroundColor: 'transparent',
    border: `2px solid ${COLORS.primary}`,
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: SPACING.md,
    width: '100%',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 2000,
    backdropFilter: 'blur(2px)',
  },
  loadingSpinner: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: SPACING.md,
  },
  spinner: {
    width: '50px',
    height: '50px',
    border: `4px solid ${COLORS.backgroundGray}`,
    borderTop: `4px solid ${COLORS.primary}`,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.text,
  },
  // NETWORK ERROR BANNER STYLES
  networkErrorBanner: {
    position: 'fixed',
    top: '10px',
    left: '50%',
    transform: 'translateX(-50%)',
    zIndex: 2001,
    maxWidth: '600px',
    width: 'calc(100% - 32px)',
    animation: 'slideDown 0.3s ease-out',
  },
  networkErrorContent: {
    backgroundColor: '#DC2626',
    color: '#FFFFFF',
    padding: '12px 16px',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
  },
  networkErrorIcon: {
    fontSize: '20px',
    flexShrink: 0,
  },
  networkErrorText: {
    flex: 1,
    fontSize: '14px',
    fontWeight: '600',
    lineHeight: '1.4',
  },
  retryButton: {
    backgroundColor: '#FFFFFF',
    color: '#DC2626',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s',
    flexShrink: 0,
  },
};

export default MapScreen;
