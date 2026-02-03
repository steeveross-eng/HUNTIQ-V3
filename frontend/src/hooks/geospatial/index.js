/**
 * HUNTIQ V3 - Geospatial Hooks
 * React hooks for geospatial data management
 */

import { useState, useEffect, useCallback } from 'react';
import { GeospatialService } from '../../services/geospatial/geospatial.service';

/**
 * Hook for geospatial engine status
 */
export const useGeospatialStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const data = await GeospatialService.getStatus();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch geospatial status');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  return { status, loading, error };
};

/**
 * Hook for data sources list
 */
export const useDataSources = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        setLoading(true);
        const data = await GeospatialService.getDataSources();
        setSources(data.sources || []);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch data sources');
      } finally {
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  return { sources, loading, error };
};

/**
 * Hook for hunting potential calculation
 */
export const useHuntingPotential = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const calculate = useCallback(async (request) => {
    try {
      setLoading(true);
      setError(null);
      const data = await GeospatialService.potential.calculate(request);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to calculate hunting potential');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getHotspots = useCallback(async (params) => {
    try {
      setLoading(true);
      const data = await GeospatialService.potential.getHotspots(params);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to fetch hotspots');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getStandLocations = useCallback(async (params) => {
    try {
      setLoading(true);
      const data = await GeospatialService.potential.getStandLocations(params);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to fetch stand locations');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    result,
    loading,
    error,
    calculate,
    getHotspots,
    getStandLocations,
  };
};

/**
 * Hook for LiDAR data
 */
export const useLidar = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const query = useCallback(async (request) => {
    try {
      setLoading(true);
      setError(null);
      const result = await GeospatialService.lidar.query(request);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to query LiDAR data');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, query };
};

/**
 * Hook for hydrology data
 */
export const useHydrology = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const query = useCallback(async (request) => {
    try {
      setLoading(true);
      setError(null);
      const result = await GeospatialService.hydro.query(request);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to query hydrology data');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getRivers = useCallback(async (params) => {
    try {
      setLoading(true);
      const result = await GeospatialService.hydro.getRivers(params);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to fetch rivers');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getLakes = useCallback(async (params) => {
    try {
      setLoading(true);
      const result = await GeospatialService.hydro.getLakes(params);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to fetch lakes');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, query, getRivers, getLakes };
};

/**
 * Hook for forest data
 */
export const useForest = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const query = useCallback(async (request) => {
    try {
      setLoading(true);
      setError(null);
      const result = await GeospatialService.forest.query(request);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to query forest data');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, query };
};

/**
 * Hook for geological data
 */
export const useGeology = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const query = useCallback(async (request) => {
    try {
      setLoading(true);
      setError(null);
      const result = await GeospatialService.sigeom.query(request);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to query geological data');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, query };
};

/**
 * Hook for AI predictions
 */
export const useAIPredictions = () => {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const predict = useCallback(async (request) => {
    try {
      setLoading(true);
      setError(null);
      const result = await GeospatialService.ai.predict(request);
      setPredictions(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to generate predictions');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getCorridors = useCallback(async (params) => {
    try {
      setLoading(true);
      const result = await GeospatialService.ai.getCorridors(params);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to fetch corridors');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { predictions, loading, error, predict, getCorridors };
};

// Export all hooks
export default {
  useGeospatialStatus,
  useDataSources,
  useHuntingPotential,
  useLidar,
  useHydrology,
  useForest,
  useGeology,
  useAIPredictions,
};
