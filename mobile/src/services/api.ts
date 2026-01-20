/**
 * API Service - Handles all backend communication
 * Implements security best practices and error handling
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { API_CONFIG } from '../constants/config';
import { ServiceLocation, ServiceType, SearchParams } from '../types';
import { authService } from './auth';

// Types for report issue
export interface ReportIssueParams {
  issue_type: 'closed' | 'hours' | 'full' | 'referral' | 'other';
  location_name: string;
  description: string;
  captcha_token?: string;
}

export interface ReportIssueResponse {
  status: string;
  message: string;
}

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
      async (config) => {
        // Add auth token if available
        const token = await authService.getToken();
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
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - clear auth
          await authService.clearAuth();
        }
        return Promise.reject(error);
      }
    );
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

  /**
   * Report an issue with a service location
   * Note: Mobile app sends reports without captcha - backend handles mobile requests differently
   */
  async reportIssue(params: ReportIssueParams): Promise<ReportIssueResponse> {
    const response = await this.client.post<ReportIssueResponse>('/public/issues/report', {
      issue_type: params.issue_type,
      location_name: params.location_name,
      description: params.description,
      // For mobile, we use a placeholder token - backend should detect mobile user agent
      // and apply different rate limiting instead of captcha
      captcha_token: params.captcha_token || 'mobile-app-request',
    });
    return response.data;
  }
}

export const apiService = new ApiService();
