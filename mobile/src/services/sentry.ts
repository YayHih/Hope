/**
 * Sentry Integration - Crash reporting and error monitoring
 * Provides production-grade error tracking for the mobile app
 */

import * as Sentry from '@sentry/react-native';

// Initialize Sentry
export function initSentry() {
  // Only initialize in production or if DSN is configured
  const dsn = process.env.EXPO_PUBLIC_SENTRY_DSN;

  if (!dsn) {
    if (__DEV__) {
      console.log('[Sentry] Not initialized - no DSN configured');
    }
    return;
  }

  Sentry.init({
    dsn,
    // Performance monitoring
    tracesSampleRate: __DEV__ ? 1.0 : 0.2,
    // Only enable in production
    enabled: !__DEV__,
    // Environment
    environment: __DEV__ ? 'development' : 'production',
    // Add app version info
    release: `hope-platform@${process.env.EXPO_PUBLIC_APP_VERSION || '1.0.0'}`,
    // Breadcrumbs for better error context
    enableAutoSessionTracking: true,
    sessionTrackingIntervalMillis: 30000,
    // Capture unhandled promise rejections
    enableNative: true,
    // Prevent sending PII
    beforeSend(event) {
      // Scrub potentially sensitive data
      if (event.user) {
        delete event.user.ip_address;
        delete event.user.email;
      }
      return event;
    },
  });
}

/**
 * Capture an exception with optional context
 */
export function captureException(
  error: Error,
  context?: Record<string, any>
) {
  if (__DEV__) {
    console.error('[Sentry] Would capture:', error, context);
    return;
  }

  Sentry.captureException(error, {
    extra: context,
  });
}

/**
 * Capture a message for logging
 */
export function captureMessage(
  message: string,
  level: Sentry.SeverityLevel = 'info'
) {
  if (__DEV__) {
    console.log(`[Sentry] [${level}] ${message}`);
    return;
  }

  Sentry.captureMessage(message, level);
}

/**
 * Set user context for error tracking
 * Note: Only set non-PII identifiers
 */
export function setUser(userId: string | null) {
  if (userId) {
    Sentry.setUser({ id: userId });
  } else {
    Sentry.setUser(null);
  }
}

/**
 * Add breadcrumb for debugging
 */
export function addBreadcrumb(
  category: string,
  message: string,
  data?: Record<string, any>
) {
  Sentry.addBreadcrumb({
    category,
    message,
    data,
    level: 'info',
  });
}

export { Sentry };
