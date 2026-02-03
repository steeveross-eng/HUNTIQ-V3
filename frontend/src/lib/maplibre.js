/**
 * HUNTIQ V3 - BIONIC™ GeoEngine
 * MapLibre GL Component - Open-source map engine
 * 
 * 100% gratuit et open-source
 * Compatible avec l'API Mapbox GL
 * Utilise des tuiles OpenStreetMap et styles libres
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

// Free tile providers
const TILE_PROVIDERS = {
  osm: {
    name: 'OpenStreetMap',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors'
  },
  carto_dark: {
    name: 'Carto Dark',
    url: 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '© CARTO'
  },
  carto_light: {
    name: 'Carto Positron',
    url: 'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attribution: '© CARTO'
  },
  stamen_terrain: {
    name: 'Stadia Terrain',
    url: 'https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png',
    attribution: '© Stadia Maps, © OpenMapTiles'
  }
};

// Default style for BIONIC™ dark theme
const BIONIC_DARK_STYLE = {
  version: 8,
  name: 'BIONIC Dark',
  sources: {
    'osm-tiles': {
      type: 'raster',
      tiles: [TILE_PROVIDERS.carto_dark.url],
      tileSize: 256,
      attribution: TILE_PROVIDERS.carto_dark.attribution
    }
  },
  layers: [
    {
      id: 'osm-layer',
      type: 'raster',
      source: 'osm-tiles',
      minzoom: 0,
      maxzoom: 19
    }
  ]
};

// Quebec center coordinates
const QUEBEC_CENTER = {
  lng: -71.2082,
  lat: 46.8139
};

/**
 * Custom hook for MapLibre GL map management
 */
export const useMapLibre = (containerRef, options = {}) => {
  const mapRef = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState(null);

  const {
    center = [QUEBEC_CENTER.lng, QUEBEC_CENTER.lat],
    zoom = 6,
    style = BIONIC_DARK_STYLE,
    minZoom = 3,
    maxZoom = 18
  } = options;

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      mapRef.current = new maplibregl.Map({
        container: containerRef.current,
        style: style,
        center: center,
        zoom: zoom,
        minZoom: minZoom,
        maxZoom: maxZoom,
        attributionControl: true
      });

      const map = mapRef.current;

      // Add navigation controls
      map.addControl(new maplibregl.NavigationControl(), 'top-right');
      map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
      map.addControl(new maplibregl.GeolocateControl({
        positionOptions: { enableHighAccuracy: true },
        trackUserLocation: true
      }), 'top-right');

      map.on('load', () => {
        setMapLoaded(true);
        setMapError(null);
      });

      map.on('error', (e) => {
        console.error('Map error:', e);
        setMapError(e.error?.message || 'Map error');
      });

      return () => {
        map.remove();
      };
    } catch (error) {
      setMapError(error.message);
    }
  }, []);

  return { map: mapRef.current, mapLoaded, mapError };
};

/**
 * Add WMS layer from Quebec government sources
 */
export const addWMSLayer = (map, layerId, wmsUrl, layerName, options = {}) => {
  if (!map || !map.getStyle()) return;

  const {
    opacity = 0.7,
    beforeLayer = null
  } = options;

  // Build WMS URL with parameters
  const wmsSource = {
    type: 'raster',
    tiles: [
      `${wmsUrl}?bbox={bbox-epsg-3857}&format=image/png&service=WMS&version=1.1.1&request=GetMap&srs=EPSG:3857&transparent=true&width=256&height=256&layers=${layerName}`
    ],
    tileSize: 256
  };

  // Remove existing source/layer if present
  if (map.getLayer(layerId)) {
    map.removeLayer(layerId);
  }
  if (map.getSource(layerId)) {
    map.removeSource(layerId);
  }

  // Add source
  map.addSource(layerId, wmsSource);

  // Add layer
  const layerConfig = {
    id: layerId,
    type: 'raster',
    source: layerId,
    paint: {
      'raster-opacity': opacity
    }
  };

  if (beforeLayer && map.getLayer(beforeLayer)) {
    map.addLayer(layerConfig, beforeLayer);
  } else {
    map.addLayer(layerConfig);
  }
};

/**
 * Add GeoJSON layer for markers, polygons, etc.
 */
export const addGeoJSONLayer = (map, layerId, geojson, type = 'circle', paint = {}) => {
  if (!map || !map.getStyle()) return;

  // Remove existing
  if (map.getLayer(layerId)) {
    map.removeLayer(layerId);
  }
  if (map.getSource(layerId)) {
    map.removeSource(layerId);
  }

  // Add source
  map.addSource(layerId, {
    type: 'geojson',
    data: geojson
  });

  // Default paint options
  const defaultPaints = {
    circle: {
      'circle-radius': 8,
      'circle-color': '#f5a623',
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff'
    },
    fill: {
      'fill-color': '#f5a623',
      'fill-opacity': 0.3,
      'fill-outline-color': '#f5a623'
    },
    line: {
      'line-color': '#f5a623',
      'line-width': 2
    }
  };

  // Add layer
  map.addLayer({
    id: layerId,
    type: type,
    source: layerId,
    paint: { ...defaultPaints[type], ...paint }
  });
};

/**
 * Toggle layer visibility
 */
export const toggleLayerVisibility = (map, layerId) => {
  if (!map || !map.getLayer(layerId)) return;

  const visibility = map.getLayoutProperty(layerId, 'visibility');
  map.setLayoutProperty(
    layerId,
    'visibility',
    visibility === 'visible' ? 'none' : 'visible'
  );
};

/**
 * Add marker to map
 */
export const addMarker = (map, coordinates, options = {}) => {
  if (!map) return null;

  const {
    color = '#f5a623',
    popup = null,
    draggable = false
  } = options;

  const marker = new maplibregl.Marker({ color, draggable })
    .setLngLat(coordinates)
    .addTo(map);

  if (popup) {
    marker.setPopup(
      new maplibregl.Popup({ offset: 25 })
        .setHTML(popup)
    );
  }

  return marker;
};

/**
 * Quebec government WMS layers configuration
 */
export const QUEBEC_WMS_LAYERS = {
  lidar: {
    id: 'lidar-elevation',
    name: 'LiDAR - Élévation',
    url: 'https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer',
    layer: '0',
    license: 'CC-BY 4.0'
  },
  hydro_rivers: {
    id: 'hydro-rivers',
    name: 'Cours d\'eau',
    url: 'https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer',
    layer: '0',
    license: 'CC-BY 4.0'
  },
  hydro_lakes: {
    id: 'hydro-lakes',
    name: 'Lacs',
    url: 'https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer',
    layer: '1',
    license: 'CC-BY 4.0'
  },
  hydro_wetlands: {
    id: 'hydro-wetlands',
    name: 'Milieux humides',
    url: 'https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer',
    layer: '2',
    license: 'CC-BY 4.0'
  },
  forest: {
    id: 'forest-stands',
    name: 'Peuplements forestiers',
    url: 'https://servicescarto.mffp.gouv.qc.ca/Inventaire_Ecoforestier/VerificationInventaire/MapServer/WMSServer',
    layer: '0',
    license: 'CC-BY 4.0'
  },
  geology_bedrock: {
    id: 'geology-bedrock',
    name: 'Géologie du socle',
    url: 'https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms',
    layer: 'SIGEOM_GEOSCIENCES:GEOLOGIE_SOCLE_1M',
    license: 'Données ouvertes Québec'
  }
};

export { TILE_PROVIDERS, BIONIC_DARK_STYLE, QUEBEC_CENTER };
export default useMapLibre;
