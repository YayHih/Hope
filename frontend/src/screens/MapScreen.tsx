import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Popup, Circle } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import axios from 'axios';
import L from 'leaflet';
import { SPACING, TYPOGRAPHY } from '../theme';
import { useTheme } from '../theme/ThemeContext';
import { useLanguage } from '../i18n/LanguageContext';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Import extracted modules
import {
  ServiceLocation,
  ServiceType,
  API_BASE_URL,
  KM_PER_MILE,
  debugLog,
  createColoredIcon,
  getFoodSubCategory,
  getCrisisSubCategory,
  validatePhoneNumber,
  formatOperatingHours,
  isLocationAlwaysOpen,
  getServiceTypeName,
} from './map';
import { getMapStyles } from './map/mapStyles';
import { WeeklyHoursDropdown } from './map/WeeklyHoursDropdown';
import { DHSInfoCard } from './map/DHSInfoCard';
import { MapEventHandler, MapCenterController, MarkerWithClick } from './map/MapControls';

// Set default Leaflet icon
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

const MapScreen: React.FC = () => {
  const { t } = useLanguage();
  const { colors, isDark } = useTheme();
  const [services, setServices] = useState<ServiceLocation[]>([]);
  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [foodSubFilters, setFoodSubFilters] = useState<{hotMeals: boolean, groceries: boolean}>({ hotMeals: true, groceries: true });
  const [crisisSubFilters, setCrisisSubFilters] = useState<{cpep: boolean, other: boolean}>({ cpep: true, other: true });
  const [userLocation, setUserLocation] = useState<[number, number]>([40.7580, -73.9855]);
  const [showDHSInfo, setShowDHSInfo] = useState<boolean>(false);
  const [openNow, setOpenNow] = useState<boolean>(false);
  const [openToday, setOpenToday] = useState<boolean>(false);
  const [mapBounds, setMapBounds] = useState<any>(null);
  const [mapCenter, setMapCenter] = useState<[number, number] | null>(null);
  const [locationRequested, setLocationRequested] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // NETWORK STATUS
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState<boolean>(!navigator.onLine);

  // FLICKER FIX: Track programmatic moves
  const isProgrammaticMoveRef = useRef<boolean>(false);

  // Client-side caching state
  const loadedLocationIds = useRef<Set<string>>(new Set());
  const lastFetchBounds = useRef<{minLat: number, maxLat: number, minLng: number, maxLng: number} | null>(null);
  const lastFetchTime = useRef<number>(0);
  const lastFetchFilters = useRef<{categories: string[], openNow: boolean, openToday: boolean} | null>(null);

  useEffect(() => {
    fetchServiceTypes();
  }, []);

  // NETWORK STATUS: Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      setNetworkError(null);
      if (mapBounds) {
        fetchNearbyServices();
      }
    };

    const handleOffline = () => {
      setIsOffline(true);
      setNetworkError('No Internet Connection');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapBounds]);

  // Handle filter changes
  useEffect(() => {
    if (openNow) {
      loadedLocationIds.current.clear();
      lastFetchBounds.current = null;
      lastFetchFilters.current = null;
      setServices([]);
    }
  }, [selectedCategories, openNow, openToday]);

  // Debounced effect for fetching services
  useEffect(() => {
    if (!showDHSInfo && mapBounds) {
      const timeoutId = setTimeout(() => {
        fetchNearbyServices();
      }, 500);

      return () => {
        clearTimeout(timeoutId);
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategories, openNow, openToday, showDHSInfo, mapBounds]);

  const fetchServiceTypes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/public/service-types`);
      setServiceTypes(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const fetchNearbyServices = async () => {
    if (!mapBounds) return;

    const MIN_ZOOM_LEVEL = 8;
    if (mapBounds.zoom && mapBounds.zoom < MIN_ZOOM_LEVEL) {
      debugLog(`Skipping fetch - zoom level ${mapBounds.zoom} < ${MIN_ZOOM_LEVEL}`);
      setServices([]);
      return;
    }

    const now = Date.now();
    if (now - lastFetchTime.current < 400) {
      debugLog('Skipping fetch - too soon after last request');
      return;
    }

    const latBuffer = (mapBounds.maxLat - mapBounds.minLat) * 0.15;
    const lngBuffer = (mapBounds.maxLon - mapBounds.minLon) * 0.15;

    const bufferedBounds = {
      minLat: mapBounds.minLat - latBuffer,
      maxLat: mapBounds.maxLat + latBuffer,
      minLng: mapBounds.minLon - lngBuffer,
      maxLng: mapBounds.maxLon + lngBuffer,
    };

    const filtersChanged = lastFetchFilters.current === null ||
      lastFetchFilters.current.openNow !== openNow ||
      lastFetchFilters.current.openToday !== openToday ||
      JSON.stringify(lastFetchFilters.current.categories.sort()) !== JSON.stringify(selectedCategories.sort());

    if (lastFetchBounds.current && !filtersChanged) {
      const last = lastFetchBounds.current;
      const lastSize = (last.maxLat - last.minLat) * (last.maxLng - last.minLng);
      const currentSize = (bufferedBounds.maxLat - bufferedBounds.minLat) * (bufferedBounds.maxLng - bufferedBounds.minLng);
      const zoomInRatio = lastSize / currentSize;

      if (zoomInRatio <= 2) {
        const isInsideLast =
          bufferedBounds.minLat >= last.minLat &&
          bufferedBounds.maxLat <= last.maxLat &&
          bufferedBounds.minLng >= last.minLng &&
          bufferedBounds.maxLng <= last.maxLng;

        if (isInsideLast) {
          debugLog('Skipping fetch - viewport inside cached bounds');
          return;
        }
      }
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    setNetworkError(null);
    setIsLoading(true);
    lastFetchTime.current = now;

    try {
      const centerLat = userLocation[0];
      const centerLng = userLocation[1];

      let url = `${API_BASE_URL}/public/services/in-bounds?min_lat=${bufferedBounds.minLat}&max_lat=${bufferedBounds.maxLat}&min_lng=${bufferedBounds.minLng}&max_lng=${bufferedBounds.maxLng}&center_lat=${centerLat}&center_lng=${centerLng}&limit=75`;

      if (selectedCategories.length > 0) {
        selectedCategories.forEach(type => {
          url += `&service_types=${type}`;
        });
      } else {
        url += `&exclude_service_types=free-wifi-linknyc`;
      }

      if (openNow) url += `&open_now=true`;
      if (openToday) url += `&open_today=true`;

      debugLog('Fetching services from bbox:', bufferedBounds);
      const response = await axios.get(url, { signal: abortController.signal });
      debugLog('Received services:', response.data.length);

      const newServices = response.data;
      const newIds = new Set(newServices.map((s: ServiceLocation) => s.id));

      newServices.forEach((s: ServiceLocation) => loadedLocationIds.current.add(s.id));

      if (filtersChanged) {
        debugLog('Filters changed - replacing services');
        setServices(newServices);
      } else {
        debugLog('Viewport changed - merging services');
        setServices(prev => {
          const existingNotInNew = prev.filter(s => !newIds.has(s.id));
          let combined = [...newServices, ...existingNotInNew];

          const MAX_CACHE_SIZE = 3000;
          if (combined.length > MAX_CACHE_SIZE) {
            combined = combined.slice(0, MAX_CACHE_SIZE);
            debugLog(`Cache pruned to ${MAX_CACHE_SIZE}`);
          }

          return combined;
        });
      }

      lastFetchBounds.current = bufferedBounds;
      lastFetchFilters.current = {
        categories: [...selectedCategories],
        openNow: openNow,
        openToday: openToday
      };
    } catch (error) {
      if (axios.isCancel(error)) {
        debugLog('Request cancelled');
      } else {
        console.error('Error fetching services:', error);
        if (axios.isAxiosError(error)) {
          if (!error.response) {
            setNetworkError('Unable to load locations. Check your connection.');
          } else if (error.response.status >= 500) {
            setNetworkError('Server error. Please try again later.');
          } else {
            setNetworkError('Failed to load locations. Please try again.');
          }
        } else {
          setNetworkError('Unable to load locations. Check your connection.');
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegionChange = useCallback((bounds: any) => {
    setMapBounds(bounds);
  }, []);

  const handleRetry = () => {
    setNetworkError(null);
    if (mapBounds) fetchNearbyServices();
  };

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category) ? [] : [category]
    );
  };

  const handleDHSCall = () => {
    window.location.href = 'tel:311';
  };

  const handleCenterMap = () => {
    if (!locationRequested && navigator.geolocation) {
      setLocationRequested(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newLocation: [number, number] = [position.coords.latitude, position.coords.longitude];
          setUserLocation(newLocation);
          setMapCenter(newLocation);
          setTimeout(() => setMapCenter(null), 100);
        },
        (error) => {
          console.error('Error getting location:', error);
          setMapCenter(userLocation);
          setTimeout(() => setMapCenter(null), 100);
        }
      );
    } else {
      setMapCenter(userLocation);
      setTimeout(() => setMapCenter(null), 100);
    }
  };

  // Viewport pruning - only render visible markers
  const visibleServices = useMemo(() => {
    if (!mapBounds) return services;

    const matchesFoodFilter = (service: ServiceLocation): boolean => {
      if (!selectedCategories.includes('food')) return true;
      if (foodSubFilters.hotMeals === foodSubFilters.groceries) return true;

      const foodServices = service.services.filter(s => s.type === 'food');
      for (const foodService of foodServices) {
        const subCategory = getFoodSubCategory(foodService);
        if (subCategory === 'food') return true;
        if (subCategory === 'soup-kitchen' && foodSubFilters.hotMeals) return true;
        if (subCategory === 'pantry' && foodSubFilters.groceries) return true;
      }
      return false;
    };

    const matchesCrisisFilter = (service: ServiceLocation): boolean => {
      if (!selectedCategories.includes('mental-health-crisis')) return true;
      if (crisisSubFilters.cpep === crisisSubFilters.other) return true;

      const crisisServices = service.services.filter(s => s.type === 'mental-health-crisis');
      for (const crisisService of crisisServices) {
        const subCategory = getCrisisSubCategory(crisisService, service.description);
        if (subCategory === 'cpep' && crisisSubFilters.cpep) return true;
        if (subCategory === 'other' && crisisSubFilters.other) return true;
      }
      return false;
    };

    return services.filter(service => {
      const isInBounds =
        service.latitude >= mapBounds.minLat &&
        service.latitude <= mapBounds.maxLat &&
        service.longitude >= mapBounds.minLon &&
        service.longitude <= mapBounds.maxLon;

      return isInBounds && matchesFoodFilter(service) && matchesCrisisFilter(service);
    });
  }, [services, mapBounds, foodSubFilters, crisisSubFilters, selectedCategories]);

  // Memoized markers
  const memoizedMarkers = useMemo(() => {
    return visibleServices.map(service => {
      let iconServiceType = service.services[0]?.type || 'food';
      let iconSymbol: string | undefined = undefined;

      if (selectedCategories.length > 0) {
        const activeFilter = selectedCategories[0];
        const hasActiveService = service.services.some(s => s.type === activeFilter);
        if (hasActiveService) iconServiceType = activeFilter;
      }

      let customColor: string | undefined = undefined;

      if (iconServiceType === 'food') {
        const foodServices = service.services.filter(s => s.type === 'food');
        if (foodServices.length > 0) {
          const subCategory = getFoodSubCategory(foodServices[0]);
          if (subCategory === 'soup-kitchen') {
            iconSymbol = 'food-hot';
            customColor = '#E53935';
          } else if (subCategory === 'pantry') {
            iconSymbol = 'food-grocery';
            customColor = '#43A047';
          }
        }
      } else if (iconServiceType === 'mental-health-crisis') {
        const crisisServices = service.services.filter(s => s.type === 'mental-health-crisis');
        if (crisisServices.length > 0) {
          const subCategory = getCrisisSubCategory(crisisServices[0], service.description);
          if (subCategory === 'cpep') {
            customColor = '#E91E63';
            iconSymbol = 'medical';
          } else {
            customColor = '#7B1FA2';
          }
        }
      } else if (iconServiceType === 'shelter') {
        iconSymbol = 'shelter';
      } else if (iconServiceType === 'intake') {
        iconSymbol = 'intake';
      } else if (iconServiceType === 'drop-in') {
        iconSymbol = 'drop-in';
      } else if (iconServiceType === 'medical') {
        iconSymbol = 'medical';
      }

      const serviceTypeColor = customColor || serviceTypes.find(st => st.slug === iconServiceType)?.color_hex || '#FF6B6B';
      const markerIcon = createColoredIcon(serviceTypeColor, iconSymbol);
      const operatingHoursText = formatOperatingHours(service.operating_hours, t);
      const isAlwaysOpen = isLocationAlwaysOpen(service.operating_hours);

      return (
        <MarkerWithClick
          key={service.id}
          position={[service.latitude, service.longitude]}
          icon={markerIcon}
          isProgrammaticMoveRef={isProgrammaticMoveRef}
        >
          <Popup autoPan={false} keepInView={false} closeOnClick={true} className="map-interactive-popup">
            <h3>{service.name}</h3>
            <p>{service.street_address}</p>
            <p>📍 {(service.distance_km / KM_PER_MILE).toFixed(1)} {t('milesAway')}</p>

            {/* Special messaging for Intake/Drop-In */}
            {iconServiceType === 'intake' && (
              <div style={{ marginTop: '8px', padding: '8px 10px', backgroundColor: '#FFF5F5', border: '2px solid #E53E3E', borderRadius: '6px', fontSize: '0.9em', fontWeight: '600', color: '#C53030', textAlign: 'center' }}>
                🛑 {t('entryPoint')}
              </div>
            )}

            {iconServiceType === 'drop-in' && (
              <div style={{ marginTop: '8px', padding: '8px 10px', backgroundColor: '#EDF2F7', border: '2px solid #4299E1', borderRadius: '6px', fontSize: '0.9em', fontWeight: '600', color: '#2C5282', textAlign: 'center' }}>
                🛋️ {t('dropInCenter')}
              </div>
            )}

            {/* Mental Health Crisis description */}
            {iconServiceType === 'mental-health-crisis' && service.description && (
              <div style={{
                marginTop: '8px', padding: '8px 10px', borderRadius: '6px', fontSize: '0.85em', fontWeight: '600', textAlign: 'center',
                backgroundColor: service.description.includes('EMERGENCY PSYCHIATRIC ER') ? '#FFF5F5' : service.description.includes('CALL') ? '#FFFBEB' : '#F0FFF4',
                border: `2px solid ${service.description.includes('EMERGENCY PSYCHIATRIC ER') ? '#E91E63' : service.description.includes('CALL') ? '#F59E0B' : '#38A169'}`,
                color: service.description.includes('EMERGENCY PSYCHIATRIC ER') ? '#9D174D' : service.description.includes('CALL') ? '#92400E' : '#276749',
              }}>
                {service.description}
              </div>
            )}

            {/* Operating Hours */}
            <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid #e0e0e0' }}>
              {isAlwaysOpen ? (
                <p style={{ fontSize: '0.95em', fontWeight: '600', color: '#38A169' }}>⏰ {t('open24Hours')}</p>
              ) : operatingHoursText ? (
                <div>
                  <p style={{ fontSize: '0.95em', fontWeight: '600', marginBottom: '6px' }}>⏰ {t('operatingHours')}:</p>
                  <p style={{ fontSize: '0.9em', whiteSpace: 'pre-line', color: '#555' }}>{operatingHoursText}</p>
                  {service.operating_hours && service.operating_hours.length > 0 && (
                    <WeeklyHoursDropdown hours={service.operating_hours} t={t} isDark={isDark} />
                  )}
                </div>
              ) : (
                <p style={{ fontSize: '0.9em', color: '#999', fontStyle: 'italic' }}>{t('hoursNotAvailable')}</p>
              )}
            </div>

            {/* Services List */}
            <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid #e0e0e0' }}>
              <p style={{ fontWeight: '600', marginBottom: '6px', fontSize: '0.95em' }}>{t('services')}:</p>
              <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.9em' }}>
                {service.services.map((svc, idx) => {
                  let displayName = getServiceTypeName(svc.name, t);
                  let capacityLabel = null;
                  let showNotes = true;

                  if (svc.type === 'food') {
                    const subCategory = getFoodSubCategory(svc);
                    if (subCategory === 'soup-kitchen') { displayName = `🥣 ${t('hotMeals')}`; showNotes = false; }
                    else if (subCategory === 'pantry') { displayName = `🛍️ ${t('groceries')}`; showNotes = false; }
                    if (svc.capacity && svc.capacity > 0) capacityLabel = ` (${svc.capacity} people)`;
                  }

                  if (svc.type === 'shelter' && svc.capacity && svc.capacity > 0) {
                    capacityLabel = ` (${svc.capacity} ${t('beds')})`;
                  }

                  if (svc.type === 'mental-health-crisis') {
                    const crisisSubCategory = getCrisisSubCategory(svc, service.description);
                    displayName = crisisSubCategory === 'cpep' ? `🚨 ${t('cpepEmergency')}` : `🧠 ${t('otherCrisis')}`;
                    showNotes = false;
                  }

                  return (
                    <li key={idx}>
                      {displayName}
                      {capacityLabel && <span>{capacityLabel}</span>}
                      {showNotes && svc.notes && <span style={{ fontSize: '0.9em', color: '#666' }}> ({svc.notes})</span>}
                    </li>
                  );
                })}
              </ul>
            </div>

            {/* Action Buttons */}
            <div style={{ marginTop: '12px', display: 'flex', gap: '10px' }}>
              {(() => {
                const phoneValidation = validatePhoneNumber(service.phone);
                if (phoneValidation.isValid) {
                  return (
                    <a href={`tel:${phoneValidation.cleaned}`} style={{ flex: 1, display: 'block', padding: '12px', backgroundColor: '#38A169', color: '#fff', textAlign: 'center', textDecoration: 'none', borderRadius: '8px', fontWeight: '600', fontSize: '1em' }}>
                      📞 {t('call')}
                    </a>
                  );
                } else if (service.phone) {
                  const safeDisplay = phoneValidation.original.replace(/[^\d\s\-()+ .x]/gi, '');
                  return (
                    <div style={{ flex: 1, padding: '8px', fontSize: '0.95em', color: '#333', backgroundColor: '#f8f9fa', borderRadius: '4px', textAlign: 'center', border: '1px solid #ddd' }}>
                      📞 {safeDisplay}
                    </div>
                  );
                }
                return null;
              })()}

              <a
                href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(service.street_address)}&travelmode=transit`}
                target="_blank"
                rel="noopener noreferrer"
                style={{ flex: 1, display: 'block', padding: '12px', backgroundColor: '#4299E1', color: '#fff', textAlign: 'center', textDecoration: 'none', borderRadius: '8px', fontWeight: '600', fontSize: '1em' }}
              >
                🚶 {t('directions')}
              </a>
            </div>
          </Popup>
        </MarkerWithClick>
      );
    });
  }, [visibleServices, selectedCategories, serviceTypes, t, isProgrammaticMoveRef, isDark]);

  const styles = getMapStyles(colors, isDark);

  return (
    <div style={styles.container}>
      {/* NETWORK ERROR BANNER */}
      {(networkError || isOffline) && (
        <div style={styles.networkErrorBanner}>
          <div style={styles.networkErrorContent}>
            <span style={styles.networkErrorIcon}>{isOffline ? '⚠️' : '❌'}</span>
            <span style={styles.networkErrorText}>{isOffline ? 'No Internet Connection' : networkError}</span>
            <button onClick={handleRetry} style={styles.retryButton} disabled={isOffline}>Retry</button>
          </div>
        </div>
      )}

      {/* DHS Info Card Overlay */}
      {showDHSInfo && (
        <DHSInfoCard
          t={t}
          colors={colors}
          isDark={isDark}
          onClose={() => setShowDHSInfo(false)}
          onCall311={handleDHSCall}
        />
      )}

      {/* Results count */}
      <div style={styles.resultsCount}>
        {isLoading ? t('loading') : `${visibleServices.length} ${t('locationsFound')}`}
      </div>

      {/* Map */}
      <div style={styles.mapContainer}>
        {/* Loading indicator */}
        {isLoading && (
          <div style={styles.loadingOverlay}>
            <span style={{ animation: 'spin 1s linear infinite' }}>🔄</span>
            {t('loading')}...
          </div>
        )}

        {/* Filters overlay */}
        <div style={styles.filtersOverlay}>
          <div style={styles.filterRow}>
            <button onClick={() => setShowDHSInfo(true)} style={styles.dhsToggleButton}>
              🏛️ {t('dhsOfficial')}
            </button>

            <button onClick={() => setOpenNow(!openNow)} style={{ ...styles.filterButton, ...(openNow ? styles.filterButtonActive : {}) }}>
              {openNow ? '✓ ' : ''}{t('openNow')}
            </button>

            <button onClick={() => setOpenToday(!openToday)} style={{ ...styles.filterButton, ...(openToday ? styles.filterButtonActive : {}) }}>
              {openToday ? '✓ ' : ''}{t('openToday')}
            </button>

            <button onClick={handleCenterMap} style={styles.centerButton} title="Center map on my location" aria-label="Center map on my location">
              🎯
            </button>
          </div>

          <div style={styles.categoryFiltersScroll}>
            {serviceTypes.map(type => {
              if (type.slug === 'dv-hotline') {
                return (
                  <a key={type.slug} href="tel:1-800-621-4673" style={{ padding: `${SPACING.xs} ${SPACING.sm}`, fontSize: TYPOGRAPHY.fontSize.xs, fontWeight: TYPOGRAPHY.fontWeight.bold, color: type.color_hex, backgroundColor: 'transparent', border: `2px dashed ${type.color_hex}`, borderRadius: '6px', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap' }} title={t('dvHotlineDesc')}>
                    📞 {t('dvHotline')}
                  </a>
                );
              }

              const isCrisisButton = type.slug === 'mental-health-crisis';
              const isSelected = selectedCategories.includes(type.slug);

              return (
                <button
                  key={type.slug}
                  onClick={() => handleCategoryToggle(type.slug)}
                  style={{
                    ...styles.categoryButton,
                    ...(isCrisisButton && !isSelected ? { borderWidth: '3px', borderColor: type.color_hex, fontWeight: TYPOGRAPHY.fontWeight.bold } : {}),
                    ...(isSelected ? { backgroundColor: type.color_hex, color: '#fff', borderColor: type.color_hex, ...(isCrisisButton ? { borderWidth: '3px' } : {}) } : {}),
                  }}
                >
                  {isCrisisButton && '🧠 '}
                  {getServiceTypeName(type.name, t)}
                </button>
              );
            })}
          </div>

          {/* Food Sub-Filters */}
          {selectedCategories.includes('food') && (
            <div style={{ display: 'flex', gap: SPACING.xs, marginTop: SPACING.xs, paddingLeft: '4px' }}>
              <button onClick={() => setFoodSubFilters(prev => ({ ...prev, hotMeals: !prev.hotMeals }))} style={{ padding: `${SPACING.xs} ${SPACING.sm}`, fontSize: TYPOGRAPHY.fontSize.xs, fontWeight: TYPOGRAPHY.fontWeight.medium, color: foodSubFilters.hotMeals ? '#fff' : colors.text, backgroundColor: foodSubFilters.hotMeals ? '#38A169' : colors.surface, border: `2px solid ${foodSubFilters.hotMeals ? '#38A169' : colors.border}`, borderRadius: '6px', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                {foodSubFilters.hotMeals ? '✓ ' : ''}🥣 {t('hotMeals')}
              </button>
              <button onClick={() => setFoodSubFilters(prev => ({ ...prev, groceries: !prev.groceries }))} style={{ padding: `${SPACING.xs} ${SPACING.sm}`, fontSize: TYPOGRAPHY.fontSize.xs, fontWeight: TYPOGRAPHY.fontWeight.medium, color: foodSubFilters.groceries ? '#fff' : colors.text, backgroundColor: foodSubFilters.groceries ? '#38A169' : colors.surface, border: `2px solid ${foodSubFilters.groceries ? '#38A169' : colors.border}`, borderRadius: '6px', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                {foodSubFilters.groceries ? '✓ ' : ''}🛍️ {t('groceries')}
              </button>
            </div>
          )}

          {/* Crisis Sub-Filters */}
          {selectedCategories.includes('mental-health-crisis') && (
            <div style={{ display: 'flex', gap: SPACING.xs, marginTop: SPACING.xs, paddingLeft: '4px' }}>
              <button onClick={() => setCrisisSubFilters(prev => ({ ...prev, cpep: !prev.cpep }))} style={{ padding: `${SPACING.xs} ${SPACING.sm}`, fontSize: TYPOGRAPHY.fontSize.xs, fontWeight: TYPOGRAPHY.fontWeight.medium, color: crisisSubFilters.cpep ? '#fff' : colors.text, backgroundColor: crisisSubFilters.cpep ? '#E91E63' : colors.surface, border: `2px solid ${crisisSubFilters.cpep ? '#E91E63' : colors.border}`, borderRadius: '6px', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                {crisisSubFilters.cpep ? '✓ ' : ''}🚨 {t('cpepEmergency')}
              </button>
              <button onClick={() => setCrisisSubFilters(prev => ({ ...prev, other: !prev.other }))} style={{ padding: `${SPACING.xs} ${SPACING.sm}`, fontSize: TYPOGRAPHY.fontSize.xs, fontWeight: TYPOGRAPHY.fontWeight.medium, color: crisisSubFilters.other ? '#fff' : colors.text, backgroundColor: crisisSubFilters.other ? '#9C27B0' : colors.surface, border: `2px solid ${crisisSubFilters.other ? '#9C27B0' : colors.border}`, borderRadius: '6px', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                {crisisSubFilters.other ? '✓ ' : ''}🧠 {t('otherCrisis')}
              </button>
            </div>
          )}
        </div>

        <MapContainer center={userLocation} zoom={13} style={{ height: '100dvh', width: '100%' }} doubleClickZoom={true} scrollWheelZoom={true} touchZoom={true} zoomControl={true}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url={isDark ? "https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png" : "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"}
          />
          <MapEventHandler onRegionChange={handleRegionChange} isProgrammaticMoveRef={isProgrammaticMoveRef} />
          <MapCenterController center={mapCenter} />

          <Circle center={userLocation} radius={100} pathOptions={{ color: '#3388ff', fillColor: '#3388ff', fillOpacity: 0.3, weight: 2 }} />
          <Circle center={userLocation} radius={15} pathOptions={{ color: '#3388ff', fillColor: '#3388ff', fillOpacity: 0.8, weight: 2 }} />

          <MarkerClusterGroup chunkedLoading maxClusterRadius={80} spiderfyOnMaxZoom={true} showCoverageOnHover={false} zoomToBoundsOnClick={true} disableClusteringAtZoom={14} animate={false}>
            {memoizedMarkers}
          </MarkerClusterGroup>
        </MapContainer>
      </div>
    </div>
  );
};

export default MapScreen;
