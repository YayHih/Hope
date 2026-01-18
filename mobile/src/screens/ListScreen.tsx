/**
 * List Screen - Accessible list view of nearby services
 * Optimized for readability and easy navigation
 */

import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Linking,
} from 'react-native';
import { useStore } from '../store/useStore';
import { apiService } from '../services/api';
import { COLORS } from '../constants/config';
import { ServiceLocation } from '../types';

export function ListScreen() {
  const { nearbyServices, setNearbyServices, currentLocation } = useStore();
  const [refreshing, setRefreshing] = React.useState(false);

  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    if (!currentLocation) return;

    try {
      const services = await apiService.searchNearby({
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        radius_km: 5,
      });
      setNearbyServices(services);
    } catch (error) {
      console.error('Error loading services:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadServices();
    setRefreshing(false);
  };

  const handleCall = (phone: string) => {
    Linking.openURL(`tel:${phone}`);
  };

  const renderServiceItem = ({ item }: { item: ServiceLocation }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.serviceName}>{item.name}</Text>
        {item.verified && (
          <View style={styles.verifiedBadge}>
            <Text style={styles.verifiedText}>✓</Text>
          </View>
        )}
      </View>

      {item.organization_name && (
        <Text style={styles.organizationName}>{item.organization_name}</Text>
      )}

      {item.street_address && (
        <Text style={styles.address}>
          {item.street_address}
          {item.borough && `, ${item.borough}`}
        </Text>
      )}

      <View style={styles.servicesContainer}>
        {item.services.map((service) => (
          <View key={service.id} style={styles.serviceTag}>
            <Text style={styles.serviceTagText}>{service.name}</Text>
          </View>
        ))}
      </View>

      {item.phone && (
        <TouchableOpacity
          style={styles.callButton}
          onPress={() => handleCall(item.phone!)}
        >
          <Text style={styles.callButtonText}>📞 Call</Text>
        </TouchableOpacity>
      )}

      {item.wheelchair_accessible && (
        <Text style={styles.accessibilityText}>♿ Wheelchair Accessible</Text>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Nearby Services</Text>
        <Text style={styles.headerSubtitle}>
          {nearbyServices.length} locations
        </Text>
      </View>

      <FlatList
        data={nearbyServices}
        renderItem={renderServiceItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No services found nearby</Text>
            <Text style={styles.emptySubtext}>
              Try expanding your search radius or changing filters
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.surface,
  },
  header: {
    backgroundColor: COLORS.primary,
    padding: 20,
    paddingTop: 60,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.background,
  },
  headerSubtitle: {
    fontSize: 16,
    color: COLORS.background,
    opacity: 0.9,
    marginTop: 4,
  },
  listContainer: {
    padding: 16,
  },
  card: {
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  serviceName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.text,
    flex: 1,
  },
  verifiedBadge: {
    backgroundColor: COLORS.success,
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  verifiedText: {
    color: COLORS.background,
    fontSize: 16,
    fontWeight: 'bold',
  },
  organizationName: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: 8,
  },
  address: {
    fontSize: 14,
    color: COLORS.text,
    marginBottom: 12,
  },
  servicesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  serviceTag: {
    backgroundColor: COLORS.secondary,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  serviceTagText: {
    color: COLORS.background,
    fontSize: 12,
    fontWeight: '600',
  },
  callButton: {
    backgroundColor: COLORS.success,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
  },
  callButtonText: {
    color: COLORS.background,
    fontSize: 16,
    fontWeight: '600',
  },
  accessibilityText: {
    fontSize: 14,
    color: COLORS.success,
    marginTop: 8,
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
});
