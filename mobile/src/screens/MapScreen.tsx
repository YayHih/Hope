/**
 * Map Screen - Primary interface for finding nearby services
 * Features: Region-based auto-update, DHS toggle, filters, accessible UI
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
  ScrollView,
  Switch,
  Linking,
  Animated,
} from 'react-native';
import MapView, { Marker, Region } from 'react-native-maps';
import * as Location from 'expo-location';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useStore } from '../store/useStore';
import { apiService } from '../services/api';
import { MAP_CONFIG } from '../constants/config';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS, BORDER_RADIUS } from '../constants/theme';

// Conditional logging (SECURITY: Prevent info disclosure in production)
const isDevelopment = __DEV__;
const debugLog = (...args: any[]) => {
  if (isDevelopment) {
    console.log(...args);
  }
};

// Helper function to sanitize color hex values (SECURITY: Prevent injection)
const sanitizeColorHex = (color: string): string => {
  // Only allow valid hex colors (#RGB or #RRGGBB)
  const hexPattern = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
  if (!hexPattern.test(color)) {
    console.warn(`[SECURITY] Invalid color hex: ${color}, defaulting to #2C7A7B`);
    return '#2C7A7B'; // Safe default color
  }
  return color;
};

// Service type categories
const SERVICE_CATEGORIES = [
  { id: 'food', name: 'Food', icon: '🍽️', color: COLORS.food },
  { id: 'shelter', name: 'Shelter', icon: '🏠', color: COLORS.shelter },
  { id: 'medical', name: 'Medical', icon: '🏥', color: COLORS.medical },
  { id: 'social', name: 'Social', icon: '🤝', color: COLORS.social },
  { id: 'hygiene', name: 'Hygiene', icon: '🧼', color: COLORS.hygiene },
];

// Helper function to calculate coordinate movement distance
const getCoordinateDelta = (region1: Region, region2: Region): number => {
  const latDiff = Math.abs(region1.latitude - region2.latitude);
  const lonDiff = Math.abs(region1.longitude - region2.longitude);
  return Math.max(latDiff, lonDiff);
};

export function MapScreen() {
  const insets = useSafeAreaInsets();
  const [loading, setLoading] = useState(true);
  const [region, setRegion] = useState<Region>(MAP_CONFIG.INITIAL_REGION);
  const [showFilters, setShowFilters] = useState(false);
  const [showDHSInfo, setShowDHSInfo] = useState(false);
  const [openNow, setOpenNow] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const lastRegionRef = useRef<Region>(MAP_CONFIG.INITIAL_REGION);
  const cardAnimation = useRef(new Animated.Value(0)).current;
  const abortControllerRef = useRef<AbortController | null>(null);

  const {
    nearbyServices,
    setNearbyServices,
    setCurrentLocation,
    selectedService,
    setSelectedService,
  } = useStore();

  useEffect(() => {
    requestLocationPermission();
  }, []);

  useEffect(() => {
    // Auto-update when filters or toggle change
    if (!showDHSInfo && region) {
      searchNearbyServices();
    }

    // SECURITY FIX: Cleanup to prevent race conditions
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, [selectedCategories, openNow, showDHSInfo]);

  const requestLocationPermission = async () => {
    try {
      const { status} = await Location.requestForegroundPermissionsAsync();

      if (status === 'granted') {
        const location = await Location.getCurrentPositionAsync({});
        const coords = {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
        };

        setCurrentLocation(coords);

        const newRegion = {
          ...coords,
          latitudeDelta: MAP_CONFIG.DEFAULT_DELTA,
          longitudeDelta: MAP_CONFIG.DEFAULT_DELTA * 0.5,
        };
        setRegion(newRegion);

        await searchNearbyServices(newRegion);
      } else {
        // Use default NYC location
        await searchNearbyServices();
      }
    } catch (error) {
      console.error('Error getting location:', error);
      await searchNearbyServices();
    } finally {
      setLoading(false);
    }
  };

  const calculateBoundingBox = (reg: Region) => {
    // Add 10-20% buffer to visible region
    const buffer = 0.15; // 15% buffer
    const latBuffer = reg.latitudeDelta * buffer;
    const lonBuffer = reg.longitudeDelta * buffer;

    return {
      minLat: reg.latitude - reg.latitudeDelta / 2 - latBuffer,
      maxLat: reg.latitude + reg.latitudeDelta / 2 + latBuffer,
      minLon: reg.longitude - reg.longitudeDelta / 2 - lonBuffer,
      maxLon: reg.longitude + reg.longitudeDelta / 2 + lonBuffer,
    };
  };

  const searchNearbyServices = async (searchRegion?: Region) => {
    if (showDHSInfo) return; // Don't fetch when showing DHS info

    const targetRegion = searchRegion || region;

    // SECURITY FIX: Create new abort controller for this request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    try {
      const bbox = calculateBoundingBox(targetRegion);

      // Calculate radius from bounding box (rough approximation)
      const latDiff = bbox.maxLat - bbox.minLat;
      const lonDiff = bbox.maxLon - bbox.minLon;
      const radius_km = Math.max(latDiff, lonDiff) * 111; // 1 degree ≈ 111 km

      const services = await apiService.searchNearby({
        latitude: targetRegion.latitude,
        longitude: targetRegion.longitude,
        radius_km: Math.min(radius_km, 50), // Cap at 50km
        service_types: selectedCategories.length > 0 ? selectedCategories : undefined,
        open_now: openNow,
        limit: 500,
      });

      setNearbyServices(services);
    } catch (error: any) {
      // Don't show error for aborted requests
      if (error?.name === 'AbortError' || error?.name === 'CanceledError') {
        debugLog('[searchNearbyServices] Request aborted');
        return;
      }
      console.error('Error searching services:', error);
      Alert.alert('Error', 'Could not load nearby services. Please try again.');
    }
  };

  const handleRegionChangeComplete = useCallback(
    (newRegion: Region) => {
      setRegion(newRegion);

      // Smart threshold check to prevent pan flicker
      const movementDelta = getCoordinateDelta(lastRegionRef.current, newRegion);

      // Use different thresholds based on card state
      // Small threshold when no card is open, large threshold when card is active
      const threshold = selectedService ? 0.02 : 0.005;

      // Only fetch if movement exceeds threshold
      if (movementDelta > threshold) {
        lastRegionRef.current = newRegion;
        searchNearbyServices(newRegion);
      }
    },
    [selectedCategories, openNow, showDHSInfo, selectedService]
  );

  const toggleCategory = (categoryId: string) => {
    setSelectedCategories((prev) => {
      if (prev.includes(categoryId)) {
        return prev.filter((id) => id !== categoryId);
      } else {
        return [...prev, categoryId];
      }
    });
  };

  // Handle marker press with stable data copy
  const handleMarkerPress = useCallback((service: any) => {
    // Create a stable copy to prevent card disappearing on list updates
    const serviceCopy = { ...service };
    setSelectedService(serviceCopy);

    // Animate card in
    Animated.spring(cardAnimation, {
      toValue: 1,
      useNativeDriver: true,
      tension: 50,
      friction: 7,
    }).start();
  }, []);

  // Handle card close
  const handleCloseCard = useCallback(() => {
    // Animate card out
    Animated.timing(cardAnimation, {
      toValue: 0,
      duration: 200,
      useNativeDriver: true,
    }).start(() => {
      setSelectedService(null);
    });
  }, []);

  const handleDHSCall = () => {
    Linking.openURL('tel:311');
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer} accessibilityRole="progressbar" accessibilityLabel="Loading nearby services">
        <ActivityIndicator size="large" color={COLORS.primary} accessibilityLabel="Loading" />
        <Text style={styles.loadingText}>Finding nearby services...</Text>
      </View>
    );
  }

  // Show DHS Safe Options Card when toggle is ON
  if (showDHSInfo) {
    return (
      <View style={styles.dhsContainer}>
        <View style={styles.dhsCard}>
          <Text style={styles.dhsIcon}>🏛️</Text>
          <Text style={styles.dhsTitle}>Safe Options</Text>
          <Text style={styles.dhsSubtitle}>Official DHS Resources</Text>

          <View style={styles.dhsContent}>
            <Text style={styles.dhsText}>
              For safety, confidential shelters are not listed on public maps.
            </Text>
            <Text style={styles.dhsText}>
              Please contact the Department of Homeless Services (DHS) or call 311 for placement.
            </Text>

            <TouchableOpacity
              style={styles.dhsCallButton}
              onPress={handleDHSCall}
              accessibilityRole="button"
              accessibilityLabel="Call 311 for shelter placement"
              accessibilityHint="Opens phone app to call 311"
            >
              <Text style={styles.dhsCallButtonText}>📞 Call 311</Text>
            </TouchableOpacity>

            <View style={styles.dhsInfoBox}>
              <Text style={styles.dhsInfoTitle}>What 311 Can Help With:</Text>
              <Text style={styles.dhsInfoText}>
                • Emergency shelter placement{'\n'}
                • Family shelter intake{'\n'}
                • Single adult intake{'\n'}
                • Veterans services{'\n'}
                • DHS facility information
              </Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.dhsBackButton}
            onPress={() => setShowDHSInfo(false)}
            accessibilityRole="button"
            accessibilityLabel="Back to map"
          >
            <Text style={styles.dhsBackButtonText}>← Back to Map</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        region={region}
        onRegionChangeComplete={handleRegionChangeComplete}
        showsUserLocation
        showsMyLocationButton
      >
        {nearbyServices.map((service) => {
          // SECURITY FIX: Sanitize color values to prevent injection
          const rawColor = service.services[0]
            ? COLORS[service.services[0].type as keyof typeof COLORS] || COLORS.primary
            : COLORS.primary;
          const safeColor = sanitizeColorHex(rawColor);

          return (
            <Marker
              key={service.id}
              coordinate={{
                latitude: service.latitude,
                longitude: service.longitude,
              }}
              title={service.name}
              description={`${service.distance_km} km away`}
              pinColor={safeColor}
              onPress={() => handleMarkerPress(service)}
            />
          );
        })}
      </MapView>

      {/* DHS Toggle */}
      <View style={styles.dhsToggle} accessibilityRole="none">
        <View style={styles.dhsToggleContent}>
          <Text style={styles.dhsToggleLabel} nativeID="dhs-toggle-label">Show DHS / Official Resources</Text>
          <Switch
            value={showDHSInfo}
            onValueChange={setShowDHSInfo}
            trackColor={{ false: COLORS.border, true: COLORS.primaryLight }}
            thumbColor={showDHSInfo ? COLORS.primary : COLORS.textLight}
            accessibilityLabel="Show DHS official resources"
            accessibilityHint="Toggle to show Department of Homeless Services contact information"
            accessibilityRole="switch"
          />
        </View>
      </View>

      {/* Filters Button */}
      <TouchableOpacity
        style={styles.filtersButton}
        onPress={() => setShowFilters(!showFilters)}
        accessibilityRole="button"
        accessibilityLabel={showFilters ? 'Close filters' : 'Open filters'}
        accessibilityState={{ expanded: showFilters }}
      >
        <Text style={styles.filtersButtonText}>
          {showFilters ? '✕ Close Filters' : '🔍 Filters'}
        </Text>
      </TouchableOpacity>

      {/* Filters Panel */}
      {showFilters && (
        <View style={styles.filtersPanel}>
          <ScrollView showsVerticalScrollIndicator={false}>
            {/* Open Now Filter */}
            <View style={styles.filterSection}>
              <Text style={styles.filterSectionTitle}>Time</Text>
              <TouchableOpacity
                style={[styles.filterChip, openNow && styles.filterChipActive]}
                onPress={() => setOpenNow(!openNow)}
                accessibilityRole="checkbox"
                accessibilityState={{ checked: openNow }}
                accessibilityLabel="Filter by open now"
                accessibilityHint="Only show locations that are currently open"
              >
                <Text
                  style={[
                    styles.filterChipText,
                    openNow && styles.filterChipTextActive,
                  ]}
                >
                  ⏰ Open Now
                </Text>
              </TouchableOpacity>
            </View>

            {/* Category Filters */}
            <View style={styles.filterSection}>
              <Text style={styles.filterSectionTitle}>Categories</Text>
              <View style={styles.filterChipsContainer}>
                {SERVICE_CATEGORIES.map((category) => (
                  <TouchableOpacity
                    key={category.id}
                    style={[
                      styles.filterChip,
                      selectedCategories.includes(category.id) &&
                        styles.filterChipActive,
                    ]}
                    onPress={() => toggleCategory(category.id)}
                    accessibilityRole="checkbox"
                    accessibilityState={{ checked: selectedCategories.includes(category.id) }}
                    accessibilityLabel={`Filter by ${category.name}`}
                    accessibilityHint={`Toggle ${category.name} services filter`}
                  >
                    <Text style={styles.filterChipIcon} accessibilityLabel="">{category.icon}</Text>
                    <Text
                      style={[
                        styles.filterChipText,
                        selectedCategories.includes(category.id) &&
                          styles.filterChipTextActive,
                      ]}
                    >
                      {category.name}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Clear All */}
            {(selectedCategories.length > 0 || openNow) && (
              <TouchableOpacity
                style={styles.clearButton}
                onPress={() => {
                  setSelectedCategories([]);
                  setOpenNow(false);
                }}
                accessibilityRole="button"
                accessibilityLabel="Clear all filters"
                accessibilityHint="Remove all active filters"
              >
                <Text style={styles.clearButtonText}>Clear All Filters</Text>
              </TouchableOpacity>
            )}
          </ScrollView>
        </View>
      )}

      {/* Results Counter */}
      <View style={styles.resultsCounter} accessibilityRole="text" accessibilityLiveRegion="polite">
        <Text style={styles.resultsText}>
          {nearbyServices.length} location{nearbyServices.length !== 1 ? 's' : ''} found
        </Text>
      </View>

      {/* Service Card with Safe Area positioning */}
      {selectedService && (
        <Animated.View
          style={[
            styles.serviceCard,
            {
              bottom: insets.bottom + 10,
              transform: [
                {
                  translateY: cardAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: [400, 0],
                  }),
                },
              ],
              opacity: cardAnimation,
            },
          ]}
        >
          <View style={styles.serviceCardHeader}>
            <Text style={styles.serviceCardTitle} numberOfLines={2}>
              {selectedService.name}
            </Text>
            <TouchableOpacity
              onPress={handleCloseCard}
              style={styles.closeButton}
              accessibilityRole="button"
              accessibilityLabel="Close service details"
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          {selectedService.address && (
            <Text style={styles.serviceCardAddress} numberOfLines={2}>
              📍 {selectedService.address}
            </Text>
          )}

          {selectedService.distance_km !== undefined && (
            <Text style={styles.serviceCardDistance}>
              📏 {selectedService.distance_km.toFixed(2)} km away
            </Text>
          )}

          {selectedService.services && selectedService.services.length > 0 && (
            <View style={styles.serviceTypesContainer}>
              {selectedService.services.slice(0, 3).map((service: any, index: number) => {
                // SECURITY FIX: Sanitize badge color values
                const rawBadgeColor = COLORS[service.type as keyof typeof COLORS] || COLORS.primary;
                const safeBadgeColor = sanitizeColorHex(rawBadgeColor);

                return (
                  <View
                    key={index}
                    style={[
                      styles.serviceTypeBadge,
                      { backgroundColor: safeBadgeColor },
                    ]}
                  >
                    <Text style={styles.serviceTypeBadgeText}>{service.type}</Text>
                  </View>
                );
              })}
            </View>
          )}

          <TouchableOpacity
            style={styles.viewDetailsButton}
            onPress={() => {
              // Navigate to details screen when implemented
              Alert.alert('Details', `View full details for ${selectedService.name}`);
            }}
            accessibilityRole="button"
            accessibilityLabel={`View details for ${selectedService.name}`}
          >
            <Text style={styles.viewDetailsButtonText}>View Details →</Text>
          </TouchableOpacity>
        </Animated.View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: SPACING.md,
    ...TYPOGRAPHY.body,
    color: COLORS.text,
  },
  dhsContainer: {
    flex: 1,
    backgroundColor: COLORS.backgroundSecondary,
    justifyContent: 'center',
    padding: SPACING.lg,
  },
  dhsCard: {
    backgroundColor: COLORS.background,
    padding: SPACING.xl,
    borderRadius: BORDER_RADIUS.xl,
    alignItems: 'center',
    ...SHADOWS.large,
  },
  dhsIcon: {
    fontSize: 64,
    marginBottom: SPACING.md,
  },
  dhsTitle: {
    ...TYPOGRAPHY.h1,
    color: COLORS.primary,
    marginBottom: SPACING.xs,
    textAlign: 'center',
  },
  dhsSubtitle: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xl,
    textAlign: 'center',
  },
  dhsContent: {
    width: '100%',
    marginBottom: SPACING.xl,
  },
  dhsText: {
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.md,
    lineHeight: 24,
    textAlign: 'center',
  },
  dhsCallButton: {
    backgroundColor: COLORS.accent,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    marginVertical: SPACING.lg,
    ...SHADOWS.medium,
  },
  dhsCallButtonText: {
    ...TYPOGRAPHY.button,
    color: COLORS.textInverse,
    fontSize: 18,
  },
  dhsInfoBox: {
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.primary,
  },
  dhsInfoTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 16,
    color: COLORS.text,
    marginBottom: SPACING.sm,
  },
  dhsInfoText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textSecondary,
    lineHeight: 22,
  },
  dhsBackButton: {
    padding: SPACING.md,
  },
  dhsBackButtonText: {
    ...TYPOGRAPHY.body,
    color: COLORS.primary,
    fontWeight: '600',
  },
  dhsToggle: {
    position: 'absolute',
    top: SPACING.md,
    left: SPACING.md,
    right: SPACING.md,
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.sm,
    ...SHADOWS.medium,
  },
  dhsToggleContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dhsToggleLabel: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.text,
    fontWeight: '600',
    flex: 1,
  },
  filtersButton: {
    position: 'absolute',
    top: 70,
    alignSelf: 'center',
    backgroundColor: COLORS.primary,
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.round,
    ...SHADOWS.medium,
  },
  filtersButtonText: {
    ...TYPOGRAPHY.button,
    color: COLORS.textInverse,
    fontSize: 14,
  },
  filtersPanel: {
    position: 'absolute',
    top: 110,
    left: SPACING.md,
    right: SPACING.md,
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
    maxHeight: '60%',
    ...SHADOWS.large,
  },
  filterSection: {
    marginBottom: SPACING.lg,
  },
  filterSectionTitle: {
    ...TYPOGRAPHY.h3,
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: SPACING.sm,
    textTransform: 'uppercase',
  },
  filterChipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  filterChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.round,
    borderWidth: 2,
    borderColor: COLORS.border,
  },
  filterChipActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  filterChipIcon: {
    fontSize: 16,
    marginRight: SPACING.xs,
  },
  filterChipText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.text,
    fontWeight: '600',
  },
  filterChipTextActive: {
    color: COLORS.textInverse,
  },
  clearButton: {
    backgroundColor: COLORS.surface,
    padding: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    marginTop: SPACING.sm,
  },
  clearButtonText: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.textSecondary,
    fontWeight: '600',
  },
  resultsCounter: {
    position: 'absolute',
    bottom: SPACING.md,
    alignSelf: 'center',
    backgroundColor: COLORS.surface,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.round,
    ...SHADOWS.small,
  },
  resultsText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.text,
    fontWeight: '600',
  },
  serviceCard: {
    position: 'absolute',
    left: SPACING.md,
    right: SPACING.md,
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.lg,
    ...SHADOWS.large,
  },
  serviceCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  serviceCardTitle: {
    ...TYPOGRAPHY.h2,
    fontSize: 18,
    color: COLORS.text,
    flex: 1,
    marginRight: SPACING.sm,
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: BORDER_RADIUS.round,
    backgroundColor: COLORS.surface,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 18,
    color: COLORS.textSecondary,
    fontWeight: '600',
  },
  serviceCardAddress: {
    ...TYPOGRAPHY.body,
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xs,
  },
  serviceCardDistance: {
    ...TYPOGRAPHY.bodySmall,
    color: COLORS.primary,
    fontWeight: '600',
    marginBottom: SPACING.md,
  },
  serviceTypesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.xs,
    marginBottom: SPACING.md,
  },
  serviceTypeBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: BORDER_RADIUS.sm,
  },
  serviceTypeBadgeText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textInverse,
    fontWeight: '600',
    fontSize: 11,
    textTransform: 'capitalize',
  },
  viewDetailsButton: {
    backgroundColor: COLORS.primary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    marginTop: SPACING.sm,
  },
  viewDetailsButtonText: {
    ...TYPOGRAPHY.button,
    color: COLORS.textInverse,
    fontWeight: '600',
  },
});
