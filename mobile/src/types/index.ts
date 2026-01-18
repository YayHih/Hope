/**
 * Type definitions for the Hope Platform
 */

export interface ServiceLocation {
  id: string;
  name: string;
  description: string | null;
  organization_name: string | null;
  street_address: string | null;
  city: string;
  state: string;
  zip_code: string | null;
  borough: string | null;
  latitude: number;
  longitude: number;
  phone: string | null;
  website: string | null;
  email: string | null;
  wheelchair_accessible: boolean | null;
  languages_spoken: string[] | null;
  data_source: string;
  verified: boolean;
  services: ServiceType[];
}

export interface ServiceType {
  id: number;
  name: string;
  slug: string;
  icon: string | null;
  color: string | null;
  description: string | null;
}

export interface SearchParams {
  latitude: number;
  longitude: number;
  radius_km?: number;
  service_types?: string[];
  open_now?: boolean;
  limit?: number;
}

export interface User {
  id: string;
  email: string | null;
  phone: string | null;
  created_at: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}
