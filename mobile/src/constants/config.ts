/**
 * Application configuration
 */

export const API_CONFIG = {
  BASE_URL: 'https://hopefornyc.com/api/v1',
  TIMEOUT: 10000,
} as const;

export const GOOGLE_AUTH_CONFIG = {
  CLIENT_ID: process.env.GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID',
  CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || 'YOUR_GOOGLE_CLIENT_SECRET',
} as const;

export const MAP_CONFIG = {
  DEFAULT_LATITUDE: 40.7580,
  DEFAULT_LONGITUDE: -73.9855,
  DEFAULT_DELTA: 0.0922,
  INITIAL_REGION: {
    latitude: 40.7580,
    longitude: -73.9855,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  },
} as const;

// Export all constants from a single location
export * from './theme';
