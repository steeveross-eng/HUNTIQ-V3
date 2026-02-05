/**
 * BIONIC™ P2 - useFusion Hook
 * ============================
 * Hook React pour consommer les scores fusionnés.
 * 
 * @version 1.0.0
 * @phase P2
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import {
  analyzeFusion,
  quickFusionAnalysis,
  getFusionForFrontend,
  getFusionHeatmap,
  getFusionWeights,
  getFusionStatus,
  FUSION_MODES
} from '../services/fusion.service';

// =============================================================================
// MAIN FUSION HOOK
// =============================================================================

/**
 * Hook principal pour la fusion Geo+Behavior
 */
export function useFusion(options = {}) {
  const {
    autoFetch = false,
    lat = null,
    lon = null,
    species = 'deer',
    territory = 'quebec',
    radiusKm = 2.0,
    mode = FUSION_MODES.BALANCED
  } = options;
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastFetch, setLastFetch] = useState(null);
  
  // Fetch fusion data
  const fetchFusion = useCallback(async (overrides = {}) => {
    const params = {
      lat: overrides.lat ?? lat,
      lon: overrides.lon ?? lon,
      species: overrides.species ?? species,
      territory: overrides.territory ?? territory,
      radiusKm: overrides.radiusKm ?? radiusKm,
      mode: overrides.mode ?? mode,
      includeHeatmap: overrides.includeHeatmap ?? true
    };
    
    if (params.lat === null || params.lon === null) {
      setError('Location required');
      return null;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await analyzeFusion(params);
      setData(result);
      setLastFetch(new Date());
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [lat, lon, species, territory, radiusKm, mode]);
  
  // Auto-fetch if enabled and location is set
  useEffect(() => {
    if (autoFetch && lat !== null && lon !== null) {
      fetchFusion();
    }
  }, [autoFetch, lat, lon, fetchFusion]);
  
  // Clear data
  const clear = useCallback(() => {
    setData(null);
    setError(null);
    setLastFetch(null);
  }, []);
  
  // Derived state
  const globalScore = useMemo(() => data?.global_score ?? null, [data]);
  const scoreLevel = useMemo(() => data?.score_level ?? null, [data]);
  const geoScore = useMemo(() => data?.geo_score ?? null, [data]);
  const behaviorScore = useMemo(() => data?.behavior_score ?? null, [data]);
  const heatmapData = useMemo(() => data?.heatmap_data ?? null, [data]);
  const recommendations = useMemo(() => data?.recommendations ?? [], [data]);
  
  return {
    // Data
    data,
    globalScore,
    scoreLevel,
    geoScore,
    behaviorScore,
    heatmapData,
    recommendations,
    
    // State
    loading,
    error,
    lastFetch,
    
    // Actions
    fetchFusion,
    clear,
    
    // Helpers
    isLoaded: data !== null,
    hasHeatmap: heatmapData !== null
  };
}

// =============================================================================
// QUICK FUSION HOOK
// =============================================================================

/**
 * Hook pour analyse rapide (sans heatmap)
 */
export function useQuickFusion() {
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchQuick = useCallback(async (lat, lon, species = 'deer') => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await quickFusionAnalysis(lat, lon, species);
      setScore(result);
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return {
    score,
    globalScore: score?.global_score ?? null,
    scoreLevel: score?.score_level ?? null,
    loading,
    error,
    fetchQuick
  };
}

// =============================================================================
// FRONTEND OPTIMIZED HOOK
// =============================================================================

/**
 * Hook pour données optimisées frontend
 */
export function useFusionFrontend() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchForFrontend = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getFusionForFrontend(params);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return {
    data,
    loading,
    error,
    fetchForFrontend,
    
    // Shorthand accessors
    globalScore: data?.globalScore ?? null,
    geoScore: data?.geoScore ?? null,
    behaviorScore: data?.behaviorScore ?? null,
    breakdown: data?.breakdown ?? { geo: {}, behavior: {} },
    heatmapData: data?.heatmapData ?? null,
    recommendations: data?.recommendations ?? []
  };
}

// =============================================================================
// HEATMAP HOOK
// =============================================================================

/**
 * Hook pour heatmap fusionnée
 */
export function useFusionHeatmap() {
  const [heatmap, setHeatmap] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchHeatmap = useCallback(async (lat, lon, species = 'deer', radiusKm = 2.0) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getFusionHeatmap(lat, lon, species, radiusKm);
      setHeatmap(result.heatmap);
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return {
    heatmap,
    loading,
    error,
    fetchHeatmap,
    
    // Derived
    points: heatmap?.points ?? [],
    bounds: heatmap?.bounds ?? null,
    colorScale: heatmap?.color_scale ?? {}
  };
}

// =============================================================================
// WEIGHTS HOOK
// =============================================================================

/**
 * Hook pour les poids de fusion
 */
export function useFusionWeights(species = 'deer', territory = 'quebec', mode = 'balanced') {
  const [weights, setWeights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchWeights = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getFusionWeights(species, territory, mode);
      setWeights(result.weights);
      return result.weights;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [species, territory, mode]);
  
  // Auto-fetch when params change
  useEffect(() => {
    fetchWeights();
  }, [fetchWeights]);
  
  return {
    weights,
    loading,
    error,
    refetch: fetchWeights,
    
    // Derived
    suiteWeights: weights?.suite_weights ?? {},
    geoWeights: weights?.geo_engine_weights ?? {},
    behaviorWeights: weights?.behavior_engine_weights ?? {}
  };
}

// =============================================================================
// STATUS HOOK
// =============================================================================

/**
 * Hook pour le status du moteur de fusion
 */
export function useFusionStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const result = await getFusionStatus();
        setStatus(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStatus();
  }, []);
  
  return {
    status,
    loading,
    error,
    isOperational: status?.status === 'operational',
    version: status?.version ?? 'unknown'
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export { FUSION_MODES };

export default useFusion;
