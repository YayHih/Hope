/**
 * API Service - Handles all backend communication
 * Implements security best practices and error handling
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { API_CONFIG } from '../constants/config';
import { ServiceLocation, ServiceType, SearchParams } from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - clear auth
          this.clearAuth();
        }
        return Promise.reject(error);
      }
    );
  }

  private getAuthToken(): string | null {
    // TODO: Implement secure token storage using expo-secure-store
    return null;
  }

  private clearAuth(): void {
    // TODO: Clear stored auth token
  }

  /**
   * Get all service types
   */
  async getServiceTypes(): Promise<ServiceType[]> {
    const response = await this.client.get<ServiceType[]>('/public/service-types');
    return response.data;
  }

  /**
   * Search for nearby services
   */
  async searchNearby(params: SearchParams): Promise<ServiceLocation[]> {
    const response = await this.client.get<ServiceLocation[]>('/public/services/nearby', {
      params: {
        latitude: params.latitude,
        longitude: params.longitude,
        radius_km: params.radius_km || 5,
        service_types: params.service_types?.join(','),
        open_now: params.open_now,
        limit: params.limit || 50,
      },
    });
    return response.data;
  }

  /**
   * Get service location by ID
   */
  async getServiceLocation(id: string): Promise<ServiceLocation> {
    const response = await this.client.get<ServiceLocation>(`/public/services/${id}`);
    return response.data;
  }
}

export const apiService = new ApiService();
