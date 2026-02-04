/**
 * BIONIC™ Engines Hook
 * 
 * Hook centralisé pour accéder aux moteurs Sentinel, SIGÉOM et Environment.
 * Gère les appels API, le cache et les états de chargement.
 */

import { useState, useCallback, useRef } from 'react';
import { api } from '@/services/api.client';

// Cache TTL (5 minutes)
const CACHE_TTL = 5 * 60 * 1000;

/**
 * Hook principal pour les moteurs BIONIC™
 */
export const useBionicEngines = () => {
  const [loading, setLoading] = useState({
    sentinel: false,
    sigeom: false,
    environment: false,
    combined: false
  });
  
  const [errors, setErrors] = useState({
    sentinel: null,
    sigeom: null,
    environment: null,
    combined: null
  });
  
  const [data, setData] = useState({
    sentinel: null,
    sigeom: null,
    environment: null,
    combined: null
  });
  
  // Cache ref
  const cacheRef = useRef({});
  
  // Helper to get cache key
  const getCacheKey = (type, params) => {
    return `${type}_${JSON.stringify(params)}`;
  };
  
  // Helper to check cache
  const checkCache = (type, params) => {
    const key = getCacheKey(type, params);
    const cached = cacheRef.current[key];
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.data;
    }
    return null;
  };
  
  // Helper to set cache
  const setCache = (type, params, responseData) => {
    const key = getCacheKey(type, params);
    cacheRef.current[key] = {
      data: responseData,
      timestamp: Date.now()
    };
  };
  
  /**
   * Fetch Sentinel-2 vegetation analysis
   */
  const fetchSentinelAnalysis = useCallback(async (lat, lon, options = {}) => {
    const params = { lat, lon, ...options };
    
    // Check cache
    const cached = checkCache('sentinel', params);
    if (cached) {
      setData(prev => ({ ...prev, sentinel: cached }));
      return cached;
    }
    
    setLoading(prev => ({ ...prev, sentinel: true }));
    setErrors(prev => ({ ...prev, sentinel: null }));
    
    try {
      // Get point analysis
      const response = await api.get('/api/bionic/sentinel/analyze/point', { params });
      
      const result = response.data;
      setCache('sentinel', params, result);
      setData(prev => ({ ...prev, sentinel: result }));
      
      return result;
    } catch (err) {
      console.error('Sentinel analysis error:', err);
      const errorMsg = err.response?.data?.detail || 'Erreur analyse Sentinel';
      setErrors(prev => ({ ...prev, sentinel: errorMsg }));
      return null;
    } finally {
      setLoading(prev => ({ ...prev, sentinel: false }));
    }
  }, []);
  
  /**
   * Fetch Sentinel territory analysis (with bbox)
   */
  const fetchSentinelTerritory = useCallback(async (bbox, targetSpecies = 'deer') => {
    const params = { bbox, targetSpecies };
    
    // Check cache
    const cached = checkCache('sentinel_territory', params);
    if (cached) {
      setData(prev => ({ ...prev, sentinel: cached }));
      return cached;
    }
    
    setLoading(prev => ({ ...prev, sentinel: true }));
    setErrors(prev => ({ ...prev, sentinel: null }));
    
    try {
      const response = await api.post('/api/bionic/sentinel/analyze/territory', {
        bbox,
        target_species: targetSpecies
      });
      
      const result = response.data;
      setCache('sentinel_territory', params, result);
      setData(prev => ({ ...prev, sentinel: result }));
      
      return result;
    } catch (err) {
      console.error('Sentinel territory analysis error:', err);
      const errorMsg = err.response?.data?.detail || 'Erreur analyse territoire Sentinel';
      setErrors(prev => ({ ...prev, sentinel: errorMsg }));
      return null;
    } finally {
      setLoading(prev => ({ ...prev, sentinel: false }));
    }
  }, []);
  
  /**
   * Fetch SIGÉOM geological analysis
   */
  const fetchSigeomAnalysis = useCallback(async (bbox, targetSpecies = 'deer') => {
    const params = { bbox, targetSpecies };
    
    // Check cache
    const cached = checkCache('sigeom', params);
    if (cached) {
      setData(prev => ({ ...prev, sigeom: cached }));
      return cached;
    }
    
    setLoading(prev => ({ ...prev, sigeom: true }));
    setErrors(prev => ({ ...prev, sigeom: null }));
    
    try {
      const response = await api.post('/api/bionic/sigeom/analyze', {
        bbox,
        target_species: targetSpecies
      });
      
      const result = response.data;
      setCache('sigeom', params, result);
      setData(prev => ({ ...prev, sigeom: result }));
      
      return result;
    } catch (err) {
      console.error('SIGÉOM analysis error:', err);
      const errorMsg = err.response?.data?.detail || 'Erreur analyse SIGÉOM';
      setErrors(prev => ({ ...prev, sigeom: errorMsg }));
      return null;
    } finally {
      setLoading(prev => ({ ...prev, sigeom: false }));
    }
  }, []);
  
  /**
   * Fetch SIGÉOM layers data
   */
  const fetchSigeomLayers = useCallback(async (bbox) => {
    setLoading(prev => ({ ...prev, sigeom: true }));
    
    try {
      const response = await api.post('/api/bionic/sigeom/extract', {
        bbox,
        include_bedrock: true,
        include_surficial: true,
        include_faults: true,
        use_cache: true
      });
      
      return response.data;
    } catch (err) {
      console.error('SIGÉOM layers error:', err);
      return null;
    } finally {
      setLoading(prev => ({ ...prev, sigeom: false }));
    }
  }, []);
  
  /**
   * Fetch BIONIC complete analysis (orchestrator)
   */
  const fetchCombinedAnalysis = useCallback(async (lat, lon, options = {}) => {
    const {
      territoryId = `analysis_${Date.now()}`,
      radiusKm = 5,
      species = ['moose', 'deer', 'bear'],
      includePredictions = true,
      includeTemporal = true
    } = options;
    
    setLoading(prev => ({ ...prev, combined: true }));
    setErrors(prev => ({ ...prev, combined: null }));
    
    try {
      const response = await api.post('/api/bionic/analyze', {
        territory_id: territoryId,
        latitude: lat,
        longitude: lon,
        radius_km: radiusKm,
        species,
        include_ai_predictions: includePredictions,
        include_temporal: includeTemporal
      });
      
      const result = response.data.analysis;
      setData(prev => ({ ...prev, combined: result }));
      
      return result;
    } catch (err) {
      console.error('Combined analysis error:', err);
      const errorMsg = err.response?.data?.detail || 'Erreur analyse combinée';
      setErrors(prev => ({ ...prev, combined: errorMsg }));
      return null;
    } finally {
      setLoading(prev => ({ ...prev, combined: false }));
    }
  }, []);
  
  /**
   * Fetch geospatial data (weather, terrain, vegetation)
   */
  const fetchGeospatialData = useCallback(async (lat, lon) => {
    try {
      const response = await api.get('/api/bionic/geospatial/complete', {
        params: { latitude: lat, longitude: lon }
      });
      return response.data;
    } catch (err) {
      console.error('Geospatial data error:', err);
      return null;
    }
  }, []);
  
  /**
   * Get engine status
   */
  const getEngineStatus = useCallback(async (engine) => {
    try {
      const response = await api.get(`/api/bionic/${engine}/status`);
      return response.data;
    } catch (err) {
      return { status: 'error', error: err.message };
    }
  }, []);
  
  /**
   * Clear cache
   */
  const clearCache = useCallback((type = null) => {
    if (type) {
      Object.keys(cacheRef.current).forEach(key => {
        if (key.startsWith(type)) {
          delete cacheRef.current[key];
        }
      });
    } else {
      cacheRef.current = {};
    }
  }, []);
  
  /**
   * Fetch all analyses in parallel
   */
  const fetchAllAnalyses = useCallback(async (lat, lon, bbox, targetSpecies = 'deer') => {
    setLoading({
      sentinel: true,
      sigeom: true,
      environment: true,
      combined: true
    });
    
    const effectiveBbox = bbox || {
      min_lat: lat - 0.05,
      max_lat: lat + 0.05,
      min_lon: lon - 0.05,
      max_lon: lon + 0.05
    };
    
    try {
      const [sentinelResult, sigeomResult, combinedResult] = await Promise.allSettled([
        fetchSentinelAnalysis(lat, lon),
        fetchSigeomAnalysis(effectiveBbox, targetSpecies),
        fetchCombinedAnalysis(lat, lon, { species: [targetSpecies] })
      ]);
      
      return {
        sentinel: sentinelResult.status === 'fulfilled' ? sentinelResult.value : null,
        sigeom: sigeomResult.status === 'fulfilled' ? sigeomResult.value : null,
        combined: combinedResult.status === 'fulfilled' ? combinedResult.value : null
      };
    } finally {
      setLoading({
        sentinel: false,
        sigeom: false,
        environment: false,
        combined: false
      });
    }
  }, [fetchSentinelAnalysis, fetchSigeomAnalysis, fetchCombinedAnalysis]);
  
  return {
    // State
    loading,
    errors,
    data,
    
    // Single engine fetchers
    fetchSentinelAnalysis,
    fetchSentinelTerritory,
    fetchSigeomAnalysis,
    fetchSigeomLayers,
    fetchCombinedAnalysis,
    fetchGeospatialData,
    
    // Combined fetcher
    fetchAllAnalyses,
    
    // Utilities
    getEngineStatus,
    clearCache,
    
    // Computed
    isLoading: Object.values(loading).some(v => v),
    hasErrors: Object.values(errors).some(v => v !== null)
  };
};

export default useBionicEngines;
