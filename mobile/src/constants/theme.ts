/**
 * Theme Configuration - Mobile-first design
 * Color palette focused on trust, calm, and accessibility
 */

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
  backgroundSecondary: '#F7FAFC', // Very light gray
  surface: '#EDF2F7',        // Light gray surface
  surfaceDark: '#E2E8F0',    // Slightly darker surface

  // UI element colors
  border: '#CBD5E0',         // Gray border
  divider: '#E2E8F0',        // Light divider
  shadow: '#000000',         // Shadow color

  // Status colors
  success: '#38A169',        // Green
  warning: '#ED8936',        // Orange
  error: '#E53E3E',          // Red
  info: '#3182CE',           // Blue

  // Map marker colors (from backend service types)
  food: '#FF6B6B',           // Red
  shelter: '#4ECDC4',        // Teal
  medical: '#95E1D3',        // Light teal
  social: '#F38181',         // Pink
  hygiene: '#AA96DA',        // Purple
  warming: '#FF8C00',        // Dark orange
  cooling: '#5DADE2',        // Blue
} as const;

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const TYPOGRAPHY = {
  h1: {
    fontSize: 32,
    fontWeight: 'bold' as const,
    lineHeight: 40,
    color: COLORS.text,
  },
  h2: {
    fontSize: 24,
    fontWeight: 'bold' as const,
    lineHeight: 32,
    color: COLORS.text,
  },
  h3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
    color: COLORS.text,
  },
  body: {
    fontSize: 16,
    fontWeight: 'normal' as const,
    lineHeight: 24,
    color: COLORS.text,
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: 'normal' as const,
    lineHeight: 20,
    color: COLORS.textSecondary,
  },
  caption: {
    fontSize: 12,
    fontWeight: 'normal' as const,
    lineHeight: 16,
    color: COLORS.textLight,
  },
  button: {
    fontSize: 16,
    fontWeight: '600' as const,
    lineHeight: 24,
  },
} as const;

export const SHADOWS = {
  small: {
    shadowColor: COLORS.shadow,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  medium: {
    shadowColor: COLORS.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 4,
  },
  large: {
    shadowColor: COLORS.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.30,
    shadowRadius: 4.65,
    elevation: 8,
  },
} as const;

export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  round: 999,
} as const;
