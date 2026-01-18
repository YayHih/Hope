/**
 * Global state management using Zustand
 * Privacy-first: no location tracking, minimal data storage
 */

import { create } from 'zustand';
import { ServiceLocation, ServiceType, AuthState } from '../types';

interface AppState {
  // Services
  nearbyServices: ServiceLocation[];
  serviceTypes: ServiceType[];
  selectedService: ServiceLocation | null;

  // Filters
  selectedServiceTypes: string[];
  searchRadius: number;
  showOpenOnly: boolean;

  // User location (ephemeral - never persisted)
  currentLocation: {
    latitude: number;
    longitude: number;
  } | null;

  // Auth
  auth: AuthState;

  // Actions
  setNearbyServices: (services: ServiceLocation[]) => void;
  setServiceTypes: (types: ServiceType[]) => void;
  setSelectedService: (service: ServiceLocation | null) => void;
  setSelectedServiceTypes: (types: string[]) => void;
  setSearchRadius: (radius: number) => void;
  setShowOpenOnly: (show: boolean) => void;
  setCurrentLocation: (location: { latitude: number; longitude: number } | null) => void;
  setAuth: (auth: AuthState) => void;
  clearAuth: () => void;
}

export const useStore = create<AppState>((set) => ({
  // Initial state
  nearbyServices: [],
  serviceTypes: [],
  selectedService: null,
  selectedServiceTypes: [],
  searchRadius: 5,
  showOpenOnly: false,
  currentLocation: null,
  auth: {
    isAuthenticated: false,
    user: null,
    token: null,
  },

  // Actions
  setNearbyServices: (services) => set({ nearbyServices: services }),
  setServiceTypes: (types) => set({ serviceTypes: types }),
  setSelectedService: (service) => set({ selectedService: service }),
  setSelectedServiceTypes: (types) => set({ selectedServiceTypes: types }),
  setSearchRadius: (radius) => set({ searchRadius: radius }),
  setShowOpenOnly: (show) => set({ showOpenOnly: show }),
  setCurrentLocation: (location) => set({ currentLocation: location }),
  setAuth: (auth) => set({ auth }),
  clearAuth: () =>
    set({
      auth: {
        isAuthenticated: false,
        user: null,
        token: null,
      },
    }),
}));
