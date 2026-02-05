/**
 * BIONIC™ P1 - GeoSuite Service
 * ==============================
 * Service API pour la Géo-Suite Nord-Américaine.
 * Consomme les Unified Output Contracts.
 * 
 * @version 1.0.0
 * @architecture P2-Ready avec FusionReadyOutput
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// =============================================================================
// CACHE MANAGER
// =============================================================================

class GeoSuiteCacheManager {
  constructor(ttlMs = 300000) { // 5 minutes default
    this.cache = new Map();
    this.ttl = ttlMs;
  }

  _generateKey(endpoint, params) {
    return `${endpoint}:${JSON.stringify(params)}`;
  }

  get(endpoint, params) {
    const key = this._generateKey(endpoint, params);
    const cached = this.cache.get(key);
    
    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.data;
    }
    
    if (cached) {
      this.cache.delete(key);
    }
    
    return null;
  }

  set(endpoint, params, data) {
    const key = this._generateKey(endpoint, params);
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  invalidate(endpoint = null) {
    if (endpoint) {
      for (const key of this.cache.keys()) {
        if (key.startsWith(endpoint)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }

  getStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

const cacheManager = new GeoSuiteCacheManager();

// =============================================================================
// API HELPERS
// =============================================================================

async function fetchWithCache(endpoint, options = {}, useCache = true) {
  const { method = 'GET', body, params } = options;
  
  // Check cache for GET requests
  if (method === 'GET' && useCache) {
    const cached = cacheManager.get(endpoint, params);
    if (cached) {
      return { ...cached, fromCache: true };
    }
  }

  try {
    const url = `${API_BASE}${endpoint}`;
    const fetchOptions = {
      method,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (body) {
      fetchOptions.body = JSON.stringify(body);
    }

    const response = await fetch(url, fetchOptions);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Cache successful GET responses
    if (method === 'GET' && useCache) {
      cacheManager.set(endpoint, params, data);
    }

    return { ...data, fromCache: false };
  } catch (error) {
    console.error(`GeoSuite API Error [${endpoint}]:`, error);
    throw error;
  }
}

// =============================================================================
// GEOSUITE STATUS
// =============================================================================

export async function getGeoSuiteStatus() {
  return fetchWithCache('/api/bionic/geosuite/status');
}

// =============================================================================
// CORRIDOR ENGINE
// =============================================================================

export async function analyzeCorridors(lat, lon, radiusKm = 2.0, targetSpecies = null) {
  return fetchWithCache('/api/bionic/geosuite/corridor/analyze', {
    method: 'POST',
    body: {
      lat,
      lon,
      radius_km: radiusKm,
      target_species: targetSpecies
    }
  }, false);
}

export async function getCorridorSpeciesScore(species, lat, lon, radiusKm = 2.0) {
  return fetchWithCache(
    `/api/bionic/geosuite/corridor/species/${species}?lat=${lat}&lon=${lon}&radius_km=${radiusKm}`,
    { params: { species, lat, lon, radiusKm } }
  );
}

// =============================================================================
// LANDCOVER ENGINE
// =============================================================================

export async function analyzeLandcover(lat, lon, radiusKm = 2.0, targetSpecies = null) {
  return fetchWithCache('/api/bionic/geosuite/landcover/analyze', {
    method: 'POST',
    body: {
      lat,
      lon,
      radius_km: radiusKm,
      target_species: targetSpecies
    }
  }, false);
}

export async function getLandcoverComposition(lat, lon, radiusKm = 2.0) {
  return fetchWithCache(
    `/api/bionic/geosuite/landcover/composition?lat=${lat}&lon=${lon}&radius_km=${radiusKm}`,
    { params: { lat, lon, radiusKm } }
  );
}

export async function getEdgeDensity(lat, lon, radiusKm = 2.0) {
  return fetchWithCache(
    `/api/bionic/geosuite/landcover/edge-density?lat=${lat}&lon=${lon}&radius_km=${radiusKm}`,
    { params: { lat, lon, radiusKm } }
  );
}

// =============================================================================
// NUTRITION ENGINE
// =============================================================================

export async function analyzeNutrition(lat, lon, radiusKm = 2.0, targetSpecies = null) {
  return fetchWithCache('/api/bionic/geosuite/nutrition/analyze', {
    method: 'POST',
    body: {
      lat,
      lon,
      radius_km: radiusKm,
      target_species: targetSpecies
    }
  }, false);
}

export async function getSpeciesNutrition(species, lat, lon, radiusKm = 2.0) {
  return fetchWithCache(
    `/api/bionic/geosuite/nutrition/species/${species}?lat=${lat}&lon=${lon}&radius_km=${radiusKm}`,
    { params: { species, lat, lon, radiusKm } }
  );
}

export async function getMastIndex(lat, lon, radiusKm = 2.0) {
  return fetchWithCache(
    `/api/bionic/geosuite/nutrition/mast-index?lat=${lat}&lon=${lon}&radius_km=${radiusKm}`,
    { params: { lat, lon, radiusKm } }
  );
}

// =============================================================================
// POPULATION DENSITY ENGINE
// =============================================================================

export async function analyzePopulationDensity(lat, lon, radiusKm = 5.0, targetSpecies = null) {
  return fetchWithCache('/api/bionic/geosuite/population/density', {
    method: 'POST',
    body: {
      lat,
      lon,
      radius_km: radiusKm,
      target_species: targetSpecies
    }
  }, false);
}

export async function getPopulationTrend(species, lat, lon) {
  return fetchWithCache(
    `/api/bionic/geosuite/population/trend/${species}?lat=${lat}&lon=${lon}`,
    { params: { species, lat, lon } }
  );
}

export async function getHarvestData(lat, lon) {
  return fetchWithCache(
    `/api/bionic/geosuite/population/harvest?lat=${lat}&lon=${lon}`,
    { params: { lat, lon } }
  );
}

// =============================================================================
// HUNTING PRESSURE MODULE
// =============================================================================

export async function analyzeHuntingPressure(lat, lon, radiusKm = 2.0, targetSpecies = null) {
  return fetchWithCache('/api/bionic/geosuite/hunting-pressure/analyze', {
    method: 'POST',
    body: {
      lat,
      lon,
      radius_km: radiusKm,
      target_species: targetSpecies
    }
  }, false);
}

export async function getBehavioralImpact(lat, lon) {
  return fetchWithCache(
    `/api/bionic/geosuite/hunting-pressure/impact?lat=${lat}&lon=${lon}`,
    { params: { lat, lon } }
  );
}

export async function getOptimalHuntingTiming(lat, lon) {
  return fetchWithCache(
    `/api/bionic/geosuite/hunting-pressure/optimal-timing?lat=${lat}&lon=${lon}`,
    { params: { lat, lon } }
  );
}

// =============================================================================
// FULL SUITE ANALYSIS
// =============================================================================

export async function runFullGeoSuiteAnalysis(params) {
  const {
    lat,
    lon,
    radiusKm = 2.0,
    targetSpecies = null,
    includeCorridors = true,
    includeLandcover = true,
    includeNutrition = true,
    includePopulation = true,
    includePressure = true
  } = params;

  return fetchWithCache('/api/bionic/geosuite/analyze/full', {
    method: 'POST',
    body: {
      lat,
      lon,
      radius_km: radiusKm,
      target_species: targetSpecies,
      include_corridors: includeCorridors,
      include_landcover: includeLandcover,
      include_nutrition: includeNutrition,
      include_population: includePopulation,
      include_pressure: includePressure
    }
  }, false);
}

// =============================================================================
// MAP STYLES & PRESETS
// =============================================================================

export async function getMapStyles() {
  return fetchWithCache('/api/bionic/geosuite/map/styles');
}

export async function getMapStyle(styleId) {
  return fetchWithCache(`/api/bionic/geosuite/map/style/${styleId}`, {
    params: { styleId }
  });
}

export async function getSpeciesPresets() {
  return fetchWithCache('/api/bionic/geosuite/map/species-presets');
}

export async function getSpeciesPreset(species) {
  return fetchWithCache(`/api/bionic/geosuite/map/species-preset/${species}`, {
    params: { species }
  });
}

export async function getDataLayers() {
  return fetchWithCache('/api/bionic/geosuite/map/data-layers');
}

// =============================================================================
// FUSION INTERFACE (P2 READY)
// =============================================================================

export async function getFusionWeights() {
  return fetchWithCache('/api/bionic/geosuite/fusion/weights');
}

export async function checkFusionCompatibility() {
  return fetchWithCache('/api/bionic/geosuite/fusion/compatibility');
}

// =============================================================================
// CACHE MANAGEMENT
// =============================================================================

export function invalidateCache(endpoint = null) {
  cacheManager.invalidate(endpoint);
}

export function getCacheStats() {
  return cacheManager.getStats();
}

// =============================================================================
// EXPORTS
// =============================================================================

const geoSuiteService = {
  // Status
  getStatus: getGeoSuiteStatus,
  
  // Engines
  corridor: {
    analyze: analyzeCorridors,
    getSpeciesScore: getCorridorSpeciesScore
  },
  landcover: {
    analyze: analyzeLandcover,
    getComposition: getLandcoverComposition,
    getEdgeDensity: getEdgeDensity
  },
  nutrition: {
    analyze: analyzeNutrition,
    getSpeciesNutrition: getSpeciesNutrition,
    getMastIndex: getMastIndex
  },
  population: {
    analyze: analyzePopulationDensity,
    getTrend: getPopulationTrend,
    getHarvest: getHarvestData
  },
  pressure: {
    analyze: analyzeHuntingPressure,
    getImpact: getBehavioralImpact,
    getOptimalTiming: getOptimalHuntingTiming
  },
  
  // Full Suite
  analyzeAll: runFullGeoSuiteAnalysis,
  
  // Map
  map: {
    getStyles: getMapStyles,
    getStyle: getMapStyle,
    getSpeciesPresets: getSpeciesPresets,
    getSpeciesPreset: getSpeciesPreset,
    getDataLayers: getDataLayers
  },
  
  // Fusion (P2)
  fusion: {
    getWeights: getFusionWeights,
    checkCompatibility: checkFusionCompatibility
  },
  
  // Cache
  cache: {
    invalidate: invalidateCache,
    getStats: getCacheStats
  }
};

export default geoSuiteService;
