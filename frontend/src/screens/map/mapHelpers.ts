import L from 'leaflet';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Types
export interface Service {
  type: string;
  name: string;
  notes?: string;
  capacity?: number;
}

export interface OperatingHours {
  day_of_week: number;
  day_name: string;
  open_time: string | null;
  close_time: string | null;
  is_24_hours: boolean;
  is_closed: boolean;
  notes?: string;
}

export interface ServiceLocation {
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

export interface ServiceType {
  id: number;
  name: string;
  slug: string;
  color_hex: string;
}

// Constants
export const API_BASE_URL = 'https://hopefornyc.com/api/v1';
export const KM_PER_MILE = 1.60934;

// Conditional logging (SECURITY: VULN-007 - Prevent info disclosure in production)
const isDevelopment = process.env.NODE_ENV === 'development';
export const debugLog = (...args: any[]) => {
  if (isDevelopment) {
    console.log(...args);
  }
};

// Global icon cache to prevent regenerating base64 SVGs on every render
const ICON_CACHE: { [key: string]: L.Icon } = {};

// Helper function to sanitize color hex values (SECURITY: Prevent SVG injection - VULN-001)
export const sanitizeColorHex = (color: string): string => {
  const hexPattern = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
  if (!hexPattern.test(color)) {
    console.warn(`[SECURITY] Invalid color hex: ${color}, defaulting to #2C7A7B`);
    return '#2C7A7B';
  }
  return color;
};

// Function to create color-coded marker icons with embedded symbols and memoization
export const createColoredIcon = (color: string, symbol?: string) => {
  const safeColor = sanitizeColorHex(color);
  const cacheKey = `${safeColor}-${symbol || 'default'}`;

  if (ICON_CACHE[cacheKey]) {
    return ICON_CACHE[cacheKey];
  }

  let symbolSvg = '';
  if (symbol === 'food-hot') {
    symbolSvg = '<ellipse cx="17.5" cy="13" rx="4" ry="3" fill="#333"/><path d="M 13.5 13 Q 17.5 16 21.5 13" stroke="#333" stroke-width="1" fill="none"/>';
  } else if (symbol === 'food-grocery') {
    symbolSvg = '<rect x="14.5" y="11" width="6" height="6" rx="0.5" fill="none" stroke="#333" stroke-width="1.2"/><path d="M 15.5 11 Q 17.5 9 19.5 11" stroke="#333" stroke-width="1.2" fill="none"/>';
  } else if (symbol === 'shelter') {
    symbolSvg = '<rect x="13.5" y="13" width="8" height="3.5" rx="0.5" fill="#333"/><circle cx="15" cy="14.5" r="0.8" fill="#fff"/>';
  } else if (symbol === 'intake') {
    symbolSvg = '<rect x="14" y="11" width="7" height="7" rx="0.5" fill="none" stroke="#333" stroke-width="1.5"/><rect x="16.5" y="14" width="2" height="3" rx="0.5" fill="#333"/><circle cx="16" cy="15.5" r="0.4" fill="#fff"/>';
  } else if (symbol === 'drop-in') {
    symbolSvg = '<rect x="14" y="13" width="7" height="5" rx="0.5" fill="none" stroke="#333" stroke-width="1.2"/><rect x="14" y="11" width="2" height="2" fill="#333"/><rect x="19" y="11" width="2" height="2" fill="#333"/>';
  } else if (symbol === 'medical') {
    symbolSvg = '<rect x="16.5" y="11" width="2" height="6" fill="#333"/><rect x="14" y="13.5" width="7" height="2" fill="#333"/>';
  }

  const svgIcon = `
    <svg width="35" height="50" viewBox="0 0 35 50" xmlns="http://www.w3.org/2000/svg">
      <path fill="${safeColor}" stroke="#fff" stroke-width="2"
        d="M17.5 0C10.596 0 5 5.596 5 12.5c0 8.5 12.5 28.5 12.5 28.5S30 21 30 12.5C30 5.596 24.404 5 17.5 5z"
        transform="scale(1.16667)"/>
      ${symbolSvg || '<circle cx="17.5" cy="14.5" r="5" fill="#fff"/>'}
    </svg>
  `;

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

// Pre-compiled regex patterns (PERFORMANCE: PERF-002 - Avoid recompiling in loops)
const SP_SK_PATTERN = /\b(SP|SK)\b/;
const FP_PATTERN = /\b(FP|FPH|FPK|FPM)\b/;

// Helper function to determine food sub-category using waterfall strategy
export const getFoodSubCategory = (service: Service): 'pantry' | 'soup-kitchen' | 'food' => {
  if (service.notes) {
    const notesUpper = service.notes.toUpperCase().trim();
    if (notesUpper === 'SK' || notesUpper === 'SP' || notesUpper === 'SKM' || notesUpper === 'SKK') {
      return 'soup-kitchen';
    }
    if (notesUpper === 'FP' || notesUpper === 'FPH' || notesUpper === 'FPK' || notesUpper === 'FPM' ||
        notesUpper === 'FPHA' || notesUpper === 'FPV') {
      return 'pantry';
    }
  }

  const searchText = `${service.name} ${service.notes || ''}`.toUpperCase();

  if (searchText.includes('SP') || searchText.includes('SK')) {
    if (SP_SK_PATTERN.test(searchText)) {
      return 'soup-kitchen';
    }
  }

  if (searchText.includes('FP')) {
    if (FP_PATTERN.test(searchText)) {
      return 'pantry';
    }
  }

  const lowerText = searchText.toLowerCase();

  if (lowerText.includes('soup') || lowerText.includes('kitchen') ||
      lowerText.includes('meal') || lowerText.includes('dining') ||
      lowerText.includes('breakfast') || lowerText.includes('lunch') ||
      lowerText.includes('dinner')) {
    return 'soup-kitchen';
  }

  if (lowerText.includes('pantry') || lowerText.includes('basket') ||
      lowerText.includes('grocery') || lowerText.includes('groceries') ||
      lowerText.includes('distribution') || lowerText.includes('food bank')) {
    return 'pantry';
  }

  return 'food';
};

// Helper function to determine mental health crisis sub-category
export const getCrisisSubCategory = (service: Service, description?: string): 'cpep' | 'other' => {
  const searchText = `${service.name} ${service.notes || ''} ${description || ''}`.toUpperCase();

  if (searchText.includes('CPEP') ||
      searchText.includes('EMERGENCY PSYCHIATRIC') ||
      searchText.includes('PSYCHIATRIC ER') ||
      searchText.includes('PSYCHIATRIC EMERGENCY')) {
    return 'cpep';
  }

  return 'other';
};

// Helper function to validate phone numbers
export const validatePhoneNumber = (phoneString: string | undefined): { isValid: boolean; cleaned: string; original: string } => {
  if (!phoneString) {
    return { isValid: false, cleaned: '', original: '' };
  }

  const original = phoneString.trim();
  const cleaned = phoneString.replace(/\D/g, '');
  const isValid = cleaned.length === 10 || cleaned.length === 11;

  return { isValid, cleaned, original };
};

// Format time from 24-hour format to 12-hour format
export const formatTime = (timeStr: string | null): string => {
  if (!timeStr) return '';
  const [hours, minutes] = timeStr.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
};

// Get today's day of week (0 = Sunday in backend)
export const getTodayDayOfWeek = (): number => {
  return new Date().getDay();
};

// Check if location is always open (24/7 with no special notes)
export const isLocationAlwaysOpen = (hours: OperatingHours[] | undefined): boolean => {
  if (!hours || hours.length === 0) return false;
  if (hours.length < 7) return false;

  for (let dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {
    const dayHours = hours.find(h => h.day_of_week === dayOfWeek);
    if (!dayHours || !dayHours.is_24_hours || (dayHours.notes && dayHours.notes.trim() !== '')) {
      return false;
    }
  }

  return true;
};

// Format operating hours for display
export const formatOperatingHours = (hours: OperatingHours[] | undefined, t: (key: any) => string): string => {
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

// Helper function to translate service type names
export const getServiceTypeName = (name: string, t: any): string => {
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
