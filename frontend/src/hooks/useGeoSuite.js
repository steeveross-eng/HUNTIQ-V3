/**
 * BIONIC™ P1 - useGeoSuite Hook
 * ==============================
 * Hook React pour consommer la Géo-Suite.
 * Cache intelligent, mock mode, P2-ready.
 * 
 * @version 1.0.0
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import geoSuiteService from '../services/geosuite.service';
import useGeoSuiteStore, { MOCK_DATA } from '../stores/geoSuiteStore';

// =============================================================================
// MAIN HOOK
// =============================================================================

export function useGeoSuite() {
  const store = useGeoSuiteStore();
  
  // Analyze with single engine
  const analyzeEngine = useCallback(async (engine) => {
    const { lat, lon, radiusKm } = store.analysisLocation;
    const species = [store.selectedSpecies];
    
    // Check mock mode
    if (store.mockMode) {
      const mockData = MOCK_DATA[engine];
      if (mockData) {
        store.setAnalysisResult(engine, mockData);
        return mockData;
      }
    }
    
    store.setLoading(engine, true);
    store.setError(engine, null);
    
    try {
      let result;
      
      switch (engine) {
        case 'corridor':
          result = await geoSuiteService.corridor.analyze(lat, lon, radiusKm, species);
          break;
        case 'landcover':
          result = await geoSuiteService.landcover.analyze(lat, lon, radiusKm, species);
          break;
        case 'nutrition':
          result = await geoSuiteService.nutrition.analyze(lat, lon, radiusKm, species);
          break;
        case 'population':
          result = await geoSuiteService.population.analyze(lat, lon, radiusKm, species);
          break;
        case 'pressure':
          result = await geoSuiteService.pressure.analyze(lat, lon, radiusKm, species);
          break;
        default:
          throw new Error(`Unknown engine: ${engine}`);
      }
      
      store.setAnalysisResult(engine, result);
      return result;
    } catch (error) {
      store.setError(engine, error.message);
      throw error;
    } finally {
      store.setLoading(engine, false);
    }
  }, [store]);
  
  // Analyze all active engines
  const analyzeAll = useCallback(async () => {
    const { lat, lon, radiusKm } = store.analysisLocation;
    const species = [store.selectedSpecies];
    
    // Check mock mode
    if (store.mockMode) {
      const results = {};
      for (const engine of ['corridor', 'landcover', 'nutrition', 'population', 'pressure']) {
        const mockData = MOCK_DATA[engine];
        if (mockData) {
          store.setAnalysisResult(engine, mockData);
          results[engine] = mockData;
        }
      }
      return results;
    }
    
    store.setLoading('full', true);
    
    try {
      const result = await geoSuiteService.analyzeAll({
        lat,
        lon,
        radiusKm,
        targetSpecies: species,
        includeCorridors: store.activeLayers.includes('corridors'),
        includeLandcover: store.activeLayers.includes('landcover'),
        includeNutrition: store.activeLayers.includes('nutrition'),
        includePopulation: store.activeLayers.includes('population'),
        includePressure: store.activeLayers.includes('pressure')
      });
      
      // Store individual results
      if (result.analyses) {
        for (const [engine, data] of Object.entries(result.analyses)) {
          store.setAnalysisResult(engine, data);
        }
      }
      
      store.setAnalysisResult('full', result);
      return result;
    } catch (error) {
      store.setError('full', error.message);
      throw error;
    } finally {
      store.setLoading('full', false);
    }
  }, [store]);
  
  // Get fusion output for P2
  const getFusionOutput = useCallback(() => {
    return store.getFusionOutput();
  }, [store]);
  
  return {
    // State
    ...store,
    
    // Actions
    analyzeEngine,
    analyzeAll,
    getFusionOutput,
    
    // Convenience
    isLoading: store.isAnyLoading(),
    globalScore: store.getGlobalScore(),
    speciesConfig: store.getSpeciesConfig(),
    territoryConfig: store.getTerritoryConfig()
  };
}

// =============================================================================
// INDIVIDUAL ENGINE HOOKS
// =============================================================================

export function useCorridorAnalysis() {
  const { analysisLocation, selectedSpecies, mockMode, analysisResults, loading, errors } = useGeoSuiteStore();
  const [data, setData] = useState(null);
  
  const analyze = useCallback(async () => {
    if (mockMode) {
      setData(MOCK_DATA.corridor);
      return MOCK_DATA.corridor;
    }
    
    const { lat, lon, radiusKm } = analysisLocation;
    const result = await geoSuiteService.corridor.analyze(lat, lon, radiusKm, [selectedSpecies]);
    setData(result);
    return result;
  }, [analysisLocation, selectedSpecies, mockMode]);
  
  const getFusionOutput = useCallback(() => {
    if (!data) return null;
    return {
      score_normalized: data.score / 100,
      confidence: data.confidence || 0.7,
      engine: 'corridor',
      weight_suggestion: 0.2
    };
  }, [data]);
  
  return {
    data: data || analysisResults.corridor,
    loading: loading.corridor,
    error: errors.corridor,
    analyze,
    getFusionOutput
  };
}

export function useLandcoverAnalysis() {
  const { analysisLocation, selectedSpecies, mockMode, analysisResults, loading, errors } = useGeoSuiteStore();
  const [data, setData] = useState(null);
  
  const analyze = useCallback(async () => {
    if (mockMode) {
      setData(MOCK_DATA.landcover);
      return MOCK_DATA.landcover;
    }
    
    const { lat, lon, radiusKm } = analysisLocation;
    const result = await geoSuiteService.landcover.analyze(lat, lon, radiusKm, [selectedSpecies]);
    setData(result);
    return result;
  }, [analysisLocation, selectedSpecies, mockMode]);
  
  const getFusionOutput = useCallback(() => {
    if (!data) return null;
    return {
      score_normalized: data.score / 100,
      confidence: data.confidence || 0.7,
      engine: 'landcover',
      weight_suggestion: 0.2
    };
  }, [data]);
  
  return {
    data: data || analysisResults.landcover,
    loading: loading.landcover,
    error: errors.landcover,
    analyze,
    getFusionOutput
  };
}

export function useNutritionAnalysis() {
  const { analysisLocation, selectedSpecies, mockMode, analysisResults, loading, errors } = useGeoSuiteStore();
  const [data, setData] = useState(null);
  
  const analyze = useCallback(async () => {
    if (mockMode) {
      setData(MOCK_DATA.nutrition);
      return MOCK_DATA.nutrition;
    }
    
    const { lat, lon, radiusKm } = analysisLocation;
    const result = await geoSuiteService.nutrition.analyze(lat, lon, radiusKm, [selectedSpecies]);
    setData(result);
    return result;
  }, [analysisLocation, selectedSpecies, mockMode]);
  
  const getFusionOutput = useCallback(() => {
    if (!data) return null;
    return {
      score_normalized: data.score / 100,
      confidence: data.confidence || 0.7,
      engine: 'nutrition',
      weight_suggestion: 0.2
    };
  }, [data]);
  
  return {
    data: data || analysisResults.nutrition,
    loading: loading.nutrition,
    error: errors.nutrition,
    analyze,
    getFusionOutput
  };
}

export function usePopulationAnalysis() {
  const { analysisLocation, selectedSpecies, mockMode, analysisResults, loading, errors } = useGeoSuiteStore();
  const [data, setData] = useState(null);
  
  const analyze = useCallback(async () => {
    if (mockMode) {
      setData(MOCK_DATA.population);
      return MOCK_DATA.population;
    }
    
    const { lat, lon, radiusKm } = analysisLocation;
    const result = await geoSuiteService.population.analyze(lat, lon, radiusKm, [selectedSpecies]);
    setData(result);
    return result;
  }, [analysisLocation, selectedSpecies, mockMode]);
  
  const getFusionOutput = useCallback(() => {
    if (!data) return null;
    return {
      score_normalized: data.score / 100,
      confidence: data.confidence || 0.7,
      engine: 'population',
      weight_suggestion: 0.2
    };
  }, [data]);
  
  return {
    data: data || analysisResults.population,
    loading: loading.population,
    error: errors.population,
    analyze,
    getFusionOutput
  };
}

export function usePressureAnalysis() {
  const { analysisLocation, selectedSpecies, mockMode, analysisResults, loading, errors } = useGeoSuiteStore();
  const [data, setData] = useState(null);
  
  const analyze = useCallback(async () => {
    if (mockMode) {
      setData(MOCK_DATA.pressure);
      return MOCK_DATA.pressure;
    }
    
    const { lat, lon, radiusKm } = analysisLocation;
    const result = await geoSuiteService.pressure.analyze(lat, lon, radiusKm, [selectedSpecies]);
    setData(result);
    return result;
  }, [analysisLocation, selectedSpecies, mockMode]);
  
  const getFusionOutput = useCallback(() => {
    if (!data) return null;
    return {
      score_normalized: data.score / 100,
      confidence: data.confidence || 0.7,
      engine: 'pressure',
      weight_suggestion: 0.2
    };
  }, [data]);
  
  return {
    data: data || analysisResults.pressure,
    loading: loading.pressure,
    error: errors.pressure,
    analyze,
    getFusionOutput
  };
}

// =============================================================================
// MAP HOOKS
// =============================================================================

export function useGeoSuiteMap() {
  const [styles, setStyles] = useState([]);
  const [presets, setPresets] = useState({});
  const [layers, setLayers] = useState({});
  
  useEffect(() => {
    const loadMapData = async () => {
      try {
        const [stylesData, presetsData, layersData] = await Promise.all([
          geoSuiteService.map.getStyles(),
          geoSuiteService.map.getSpeciesPresets(),
          geoSuiteService.map.getDataLayers()
        ]);
        
        setStyles(stylesData.styles || []);
        setPresets(presetsData || {});
        setLayers(layersData || {});
      } catch (error) {
        console.error('Failed to load map data:', error);
      }
    };
    
    loadMapData();
  }, []);
  
  return { styles, presets, layers };
}

// =============================================================================
// STATUS HOOK
// =============================================================================

export function useGeoSuiteStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await geoSuiteService.getStatus();
        setStatus(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStatus();
  }, []);
  
  return { status, loading, error };
}

// =============================================================================
// EXPORTS
// =============================================================================

export default useGeoSuite;
