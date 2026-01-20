/**
 * Auth Service - Secure token storage and authentication management
 * Uses expo-secure-store for encrypted token storage on device
 */

import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'hope_auth_token';
const USER_KEY = 'hope_user_data';

export interface StoredUser {
  id: string;
  email: string | null;
  phone: string | null;
}

class AuthService {
  private cachedToken: string | null = null;
  private cachedUser: StoredUser | null = null;

  /**
   * Store authentication token securely
   */
  async setToken(token: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(TOKEN_KEY, token);
      this.cachedToken = token;
    } catch (error) {
      console.error('[AuthService] Failed to store token:', error);
      throw new Error('Failed to store authentication token');
    }
  }

  /**
   * Retrieve authentication token
   */
  async getToken(): Promise<string | null> {
    // Return cached token if available
    if (this.cachedToken) {
      return this.cachedToken;
    }

    try {
      const token = await SecureStore.getItemAsync(TOKEN_KEY);
      this.cachedToken = token;
      return token;
    } catch (error) {
      console.error('[AuthService] Failed to retrieve token:', error);
      return null;
    }
  }

  /**
   * Store user data securely
   */
  async setUser(user: StoredUser): Promise<void> {
    try {
      await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
      this.cachedUser = user;
    } catch (error) {
      console.error('[AuthService] Failed to store user:', error);
      throw new Error('Failed to store user data');
    }
  }

  /**
   * Retrieve user data
   */
  async getUser(): Promise<StoredUser | null> {
    if (this.cachedUser) {
      return this.cachedUser;
    }

    try {
      const userData = await SecureStore.getItemAsync(USER_KEY);
      if (userData) {
        this.cachedUser = JSON.parse(userData);
        return this.cachedUser;
      }
      return null;
    } catch (error) {
      console.error('[AuthService] Failed to retrieve user:', error);
      return null;
    }
  }

  /**
   * Clear all authentication data
   */
  async clearAuth(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
      await SecureStore.deleteItemAsync(USER_KEY);
      this.cachedToken = null;
      this.cachedUser = null;
    } catch (error) {
      console.error('[AuthService] Failed to clear auth:', error);
    }
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    const token = await this.getToken();
    return token !== null;
  }
}

export const authService = new AuthService();
