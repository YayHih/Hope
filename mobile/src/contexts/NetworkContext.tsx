/**
 * Network Context - Monitors network connectivity and provides offline handling
 * Displays user-friendly messages when offline
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import { COLORS, SPACING, TYPOGRAPHY } from '../constants/theme';

interface NetworkContextValue {
  isConnected: boolean;
  isInternetReachable: boolean | null;
  connectionType: string | null;
}

const NetworkContext = createContext<NetworkContextValue>({
  isConnected: true,
  isInternetReachable: true,
  connectionType: null,
});

export const useNetwork = () => useContext(NetworkContext);

interface NetworkProviderProps {
  children: ReactNode;
}

export function NetworkProvider({ children }: NetworkProviderProps) {
  const [networkState, setNetworkState] = useState<NetworkContextValue>({
    isConnected: true,
    isInternetReachable: true,
    connectionType: null,
  });
  const [showBanner, setShowBanner] = useState(false);
  const bannerAnimation = useState(new Animated.Value(0))[0];

  useEffect(() => {
    // Subscribe to network state changes
    const unsubscribe = NetInfo.addEventListener((state: NetInfoState) => {
      const isConnected = state.isConnected ?? false;
      const isInternetReachable = state.isInternetReachable;

      setNetworkState({
        isConnected,
        isInternetReachable,
        connectionType: state.type,
      });

      // Show/hide offline banner
      if (!isConnected || isInternetReachable === false) {
        setShowBanner(true);
        Animated.spring(bannerAnimation, {
          toValue: 1,
          useNativeDriver: true,
          tension: 50,
          friction: 7,
        }).start();
      } else if (showBanner) {
        // Show "back online" message briefly
        Animated.timing(bannerAnimation, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }).start(() => {
          setShowBanner(false);
        });
      }
    });

    // Get initial state
    NetInfo.fetch().then((state) => {
      setNetworkState({
        isConnected: state.isConnected ?? true,
        isInternetReachable: state.isInternetReachable,
        connectionType: state.type,
      });
    });

    return () => unsubscribe();
  }, []);

  return (
    <NetworkContext.Provider value={networkState}>
      {children}
      {showBanner && (
        <Animated.View
          style={[
            styles.banner,
            {
              opacity: bannerAnimation,
              transform: [
                {
                  translateY: bannerAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: [-50, 0],
                  }),
                },
              ],
            },
          ]}
          accessibilityRole="alert"
          accessibilityLiveRegion="polite"
        >
          <View style={styles.bannerContent}>
            <Text style={styles.bannerIcon}>📡</Text>
            <View style={styles.bannerTextContainer}>
              <Text style={styles.bannerTitle}>No Internet Connection</Text>
              <Text style={styles.bannerMessage}>
                Some features may be unavailable
              </Text>
            </View>
          </View>
        </Animated.View>
      )}
    </NetworkContext.Provider>
  );
}

/**
 * Offline Fallback Component - Display when content requires network
 */
interface OfflineFallbackProps {
  message?: string;
  onRetry?: () => void;
}

export function OfflineFallback({
  message = 'This feature requires an internet connection',
  onRetry
}: OfflineFallbackProps) {
  const { isConnected } = useNetwork();

  if (isConnected) {
    return null;
  }

  return (
    <View style={styles.fallbackContainer}>
      <Text style={styles.fallbackIcon}>📵</Text>
      <Text style={styles.fallbackTitle}>You're Offline</Text>
      <Text style={styles.fallbackMessage}>{message}</Text>
      {onRetry && (
        <Text
          style={styles.retryButton}
          onPress={onRetry}
          accessibilityRole="button"
        >
          Tap to Retry
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: COLORS.accentWarning,
    paddingTop: 50, // Account for status bar
    paddingBottom: SPACING.sm,
    paddingHorizontal: SPACING.md,
    zIndex: 9999,
    elevation: 10,
  },
  bannerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  bannerIcon: {
    fontSize: 24,
    marginRight: SPACING.sm,
  },
  bannerTextContainer: {
    flex: 1,
  },
  bannerTitle: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.text,
    fontWeight: '700',
  },
  bannerMessage: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textSecondary,
  },
  fallbackContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: SPACING.xl,
    backgroundColor: COLORS.background,
  },
  fallbackIcon: {
    fontSize: 64,
    marginBottom: SPACING.md,
  },
  fallbackTitle: {
    ...TYPOGRAPHY.h2,
    color: COLORS.text,
    marginBottom: SPACING.sm,
  },
  fallbackMessage: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginBottom: SPACING.lg,
  },
  retryButton: {
    ...TYPOGRAPHY.button,
    color: COLORS.primary,
    padding: SPACING.md,
  },
});
