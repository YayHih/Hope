import React, { useEffect, useRef } from 'react';
import { Marker, useMapEvents, useMap } from 'react-leaflet';

// Map event handler component
export function MapEventHandler({
  onRegionChange,
  isProgrammaticMoveRef
}: {
  onRegionChange: (bounds: any) => void;
  isProgrammaticMoveRef: React.MutableRefObject<boolean>;
}) {
  const lastCenterRef = useRef<{ lat: number; lng: number } | null>(null);

  const map = useMapEvents({
    load: () => {
      const bounds = map.getBounds();
      const zoom = map.getZoom();
      const center = map.getCenter();

      lastCenterRef.current = { lat: center.lat, lng: center.lng };

      onRegionChange({
        minLat: bounds.getSouth(),
        maxLat: bounds.getNorth(),
        minLon: bounds.getWest(),
        maxLon: bounds.getEast(),
        center: center,
        zoom: zoom,
      });
    },
    moveend: () => {
      // FLICKER FIX: Skip fetch if this was a programmatic move
      if (isProgrammaticMoveRef.current) {
        isProgrammaticMoveRef.current = false;
        return;
      }

      const bounds = map.getBounds();
      const zoom = map.getZoom();
      const center = map.getCenter();

      if (lastCenterRef.current) {
        const latDiff = Math.abs(center.lat - lastCenterRef.current.lat);
        const lngDiff = Math.abs(center.lng - lastCenterRef.current.lng);
        const distance = Math.max(latDiff, lngDiff);

        // Guard clause: If movement is very small, skip refetch
        if (distance < 0.005) {
          return;
        }
      }

      lastCenterRef.current = { lat: center.lat, lng: center.lng };

      onRegionChange({
        minLat: bounds.getSouth(),
        maxLat: bounds.getNorth(),
        minLon: bounds.getWest(),
        maxLon: bounds.getEast(),
        center: center,
        zoom: zoom,
      });
    },
  });

  useEffect(() => {
    const bounds = map.getBounds();
    const zoom = map.getZoom();
    onRegionChange({
      minLat: bounds.getSouth(),
      maxLat: bounds.getNorth(),
      minLon: bounds.getWest(),
      maxLon: bounds.getEast(),
      center: map.getCenter(),
      zoom: zoom,
    });
  }, [map, onRegionChange]);

  return null;
}

// Center map on user location component
export function MapCenterController({ center }: { center: [number, number] | null }) {
  const map = useMap();

  useEffect(() => {
    if (center) {
      map.setView(center, 13, { animate: true });
    }
  }, [center, map]);

  return null;
}

// Marker with custom click handler that has map access
export function MarkerWithClick({
  position,
  icon,
  children,
  isProgrammaticMoveRef
}: {
  position: [number, number];
  icon: any;
  children: React.ReactNode;
  isProgrammaticMoveRef: React.MutableRefObject<boolean>;
}) {
  const map = useMap();

  const handleClick = () => {
    // FLICKER FIX: Mark this as a programmatic move to skip API fetch
    isProgrammaticMoveRef.current = true;

    // Pan to marker with offset to show the popup card
    const point = map.project(position, map.getZoom());
    point.y -= 150;
    const newCenter = map.unproject(point, map.getZoom());
    map.panTo(newCenter, { animate: true, duration: 0.5 });
  };

  return (
    <Marker position={position} icon={icon} eventHandlers={{ click: handleClick }}>
      {children}
    </Marker>
  );
}
