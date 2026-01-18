// Theme constants for Hope for NYC
// Color palette: Calm teal/blue (trust), accent green (available), muted orange (warnings), charcoal (text)

export const COLORS = {
  // Primary colors - Calm teal/blue (trust)
  primary: '#2C7A7B',        // Teal - Main brand color
  primaryLight: '#4FD1C5',   // Light teal
  primaryDark: '#234E52',    // Dark teal

  // Accent colors
  accent: '#38A169',         // Green - Available/positive actions
  accentWarning: '#ED8936',  // Muted orange - Warnings/attention
  accentError: '#E53E3E',    // Red - Errors/critical

  // Text colors
  text: '#2D3748',           // Charcoal - Primary text
  textSecondary: '#718096',  // Gray - Secondary text
  textLight: '#A0AEC0',      // Light gray
  textInverse: '#FFFFFF',    // White text on dark backgrounds

  // Background colors
  background: '#FFFFFF',     // White
  backgroundGray: '#F7FAFC', // Light gray background
  backgroundDark: '#2D3748', // Dark background

  // Border colors
  border: '#E2E8F0',
  borderDark: '#CBD5E0',

  // Map marker colors (from backend service types)
  food: '#FF6B6B',
  shelter: '#4ECDC4',
  medical: '#95E1D3',
  social: '#F38181',
  hygiene: '#AA96DA',
  warming: '#FF8C00',
  cooling: '#5DADE2',
} as const;

export const SPACING = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
} as const;

export const TYPOGRAPHY = {
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '32px',
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
} as const;

export const SHADOWS = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
} as const;

export const BORDER_RADIUS = {
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '9999px',
} as const;

export const BREAKPOINTS = {
  mobile: '480px',
  tablet: '768px',
  desktop: '1024px',
  wide: '1280px',
} as const;

export const Z_INDEX = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
} as const;
