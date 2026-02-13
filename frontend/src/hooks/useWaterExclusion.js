/**
 * useWaterExclusion.js
 * 
 * Hook personnalisé pour l'exclusion des zones aquatiques dans BIONIC™
 * 
 * Fonctionnalités:
 * - Détection des surfaces d'eau via l'API hydrographique
 * - Filtrage automatique des zones situées dans l'eau
 * - Tolérance de distance configurable (défaut: 5m du rivage)
 * - Cache des données pour performances optimales
 * 
 * Zones exclues:
 * - Fleuves, océans, mers
 * - Rivières, ruisseaux, canaux
 * - Lacs, étangs, réservoirs
 * - Marais, zones humides
 */

import { useState, useCallback, useEffect, useRef } from 'react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

// Configuration par défaut
const DEFAULT_SHORE_TOLERANCE = 5; // mètres
const CACHE_DURATION = 60000; // 1 minute
const DEBOUNCE_DELAY = 500; // ms

/**
 * Hook pour l'exclusion des zones aquatiques
 */
export const useWaterExclusion = (options = {}) => {
  const {
    enabled = true,
    shoreTolerance = DEFAULT_SHORE_TOLERANCE,
    autoFilter = true
  } = options;
  
  const [isLoading, setIsLoading] = useState(false);
  const [waterFeatures, setWaterFeatures] = useState([]);
  const [excludedCount, setExcludedCount] = useState(0);
  const [lastFilterStats, setLastFilterStats] = useState(null);
  const [error, setError] = useState(null);
  
  const cacheRef = useRef({});
  const debounceRef = useRef(null);
  
  /**
   * Génère une clé de cache basée sur les limites
   */
  const getCacheKey = useCallback((bounds) => {
    if (!bounds) return null;
    const { north, south, east, west } = bounds;
    return `${north.toFixed(3)}_${south.toFixed(3)}_${east.toFixed(3)}_${west.toFixed(3)}`;
  }, []);
  
  /**
   * Vérifie si le cache est valide
   */
  const isCacheValid = useCallback((key) => {
    const cached = cacheRef.current[key];
    if (!cached) return false;
    return Date.now() - cached.timestamp < CACHE_DURATION;
  }, []);
  
  /**
   * Récupère les surfaces d'eau pour une zone
   */
  const fetchWaterFeatures = useCallback(async (lat, lng, radius = 5000) => {
    if (!enabled) return [];
    
    try {
      const response = await fetch(
        `${API_BASE}/api/hydro/water-features?lat=${lat}&lng=${lng}&radius=${radius}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      return data.features || [];
    } catch (err) {
      console.error('Error fetching water features:', err);
      setError(err.message);
      return [];
    }
  }, [enabled]);
  
  /**
   * Filtre les zones pour exclure celles dans l'eau
   */
  const filterZones = useCallback(async (zones, bounds) => {
    if (!enabled || !zones || zones.length === 0) {
      return { filteredZones: zones, stats: null };
    }
    
    // Vérifier le cache
    const cacheKey = getCacheKey(bounds);
    if (cacheKey && isCacheValid(cacheKey)) {
      const cached = cacheRef.current[cacheKey];
      // Appliquer le filtre depuis le cache
      const waterPolygons = cached.waterFeatures || [];
      const filtered = filterZonesLocally(zones, waterPolygons, shoreTolerance);
      return { filteredZones: filtered.zones, stats: filtered.stats };
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Préparer la requête
      const requestBody = {
        zones: zones.map(z => ({
          id: z.id,
          center: z.center,
          radiusMeters: z.radiusMeters,
          moduleId: z.moduleId,
          percentage: z.percentage
        })),
        bounds: {
          north: bounds.north || bounds._northEast?.lat,
          south: bounds.south || bounds._southWest?.lat,
          east: bounds.east || bounds._northEast?.lng,
          west: bounds.west || bounds._southWest?.lng
        },
        tolerance_meters: shoreTolerance
      };
      
      const response = await fetch(`${API_BASE}/api/hydro/filter-zones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Mettre à jour les stats
      setLastFilterStats(data.stats);
      setExcludedCount(data.stats?.excluded || 0);
      
      // Mettre en cache
      if (cacheKey) {
        cacheRef.current[cacheKey] = {
          timestamp: Date.now(),
          waterFeatures: data.stats?.water_features || [],
          stats: data.stats
        };
      }
      
      return {
        filteredZones: data.filtered_zones || zones,
        stats: data.stats
      };
      
    } catch (err) {
      console.error('Error filtering zones:', err);
      setError(err.message);
      // En cas d'erreur, retourner les zones non filtrées
      return { filteredZones: zones, stats: null };
    } finally {
      setIsLoading(false);
    }
  }, [enabled, shoreTolerance, getCacheKey, isCacheValid]);
  
  /**
   * Vérifie si un point spécifique est dans l'eau
   */
  const checkPoint = useCallback(async (lat, lng, bounds = null) => {
    if (!enabled) return { isInWater: false };
    
    try {
      const requestBody = {
        lat,
        lng,
        tolerance_meters: shoreTolerance,
        bounds: bounds ? {
          north: bounds.north || bounds._northEast?.lat,
          south: bounds.south || bounds._southWest?.lat,
          east: bounds.east || bounds._northEast?.lng,
          west: bounds.west || bounds._southWest?.lng
        } : null
      };
      
      const response = await fetch(`${API_BASE}/api/hydro/check-point`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      return {
        isInWater: data.is_in_water,
        waterType: data.water_type,
        waterName: data.water_name
      };
      
    } catch (err) {
      console.error('Error checking point:', err);
      return { isInWater: false, error: err.message };
    }
  }, [enabled, shoreTolerance]);
  
  /**
   * Filtre les zones localement (sans appel API)
   * Utilisé quand les données d'eau sont déjà en cache
   */
  const filterZonesLocally = useCallback((zones, waterPolygons, tolerance) => {
    if (!waterPolygons || waterPolygons.length === 0) {
      return { zones, stats: { excluded: 0, total: zones.length } };
    }
    
    const filtered = [];
    let excludedCount = 0;
    
    zones.forEach(zone => {
      const [lat, lng] = zone.center;
      let isExcluded = false;
      
      // Vérifier contre chaque polygone d'eau
      for (const water of waterPolygons) {
        if (isPointInOrNearPolygon(lat, lng, water.polygon, tolerance)) {
          isExcluded = true;
          break;
        }
      }
      
      if (!isExcluded) {
        filtered.push(zone);
      } else {
        excludedCount++;
      }
    });
    
    return {
      zones: filtered,
      stats: {
        total: zones.length,
        filtered: filtered.length,
        excluded: excludedCount
      }
    };
  }, []);
  
  /**
   * Vide le cache
   */
  const clearCache = useCallback(() => {
    cacheRef.current = {};
  }, []);
  
  return {
    // État
    isLoading,
    waterFeatures,
    excludedCount,
    lastFilterStats,
    error,
    
    // Actions
    filterZones,
    checkPoint,
    fetchWaterFeatures,
    clearCache,
    
    // Config
    shoreTolerance,
    enabled
  };
};

/**
 * Vérifie si un point est dans ou près d'un polygone
 * (Implémentation simplifiée côté client)
 */
function isPointInOrNearPolygon(lat, lng, polygon, toleranceMeters) {
  if (!polygon || polygon.length < 3) return false;
  
  // Algorithme ray-casting pour point-in-polygon
  let inside = false;
  const x = lat, y = lng;
  
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  
  if (inside) return true;
  
  // Vérifier la distance au bord si tolérance > 0
  if (toleranceMeters > 0) {
    // Approximation simple: vérifier la distance aux sommets
    for (const [plat, plng] of polygon) {
      const dist = haversineDistance(lat, lng, plat, plng);
      if (dist <= toleranceMeters) return true;
    }
  }
  
  return false;
}

/**
 * Calcule la distance en mètres entre deux points GPS
 */
function haversineDistance(lat1, lng1, lat2, lng2) {
  const R = 6371000; // Rayon de la Terre en mètres
  const phi1 = lat1 * Math.PI / 180;
  const phi2 = lat2 * Math.PI / 180;
  const deltaPhi = (lat2 - lat1) * Math.PI / 180;
  const deltaLambda = (lng2 - lng1) * Math.PI / 180;
  
  const a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
            Math.cos(phi1) * Math.cos(phi2) *
            Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
}

export default useWaterExclusion;
