/**
 * HUNTIQ V3 - BIONIC™ Geospatial Engine
 * Hooks - React hooks for geospatial data management
 * 
 * This module provides hooks for the geospatial engine.
 * NO IMPLEMENTATION - Architecture preparation only.
 */

import { useState, useEffect, useCallback } from 'react';
import { GeospatialService } from '@/services/geospatial';
import type {
  GeospatialEngineStatus,
  DataSourceInfo,
  BoundingBox,
  HuntingPotentialResponse,
  AIPredictionResponse,
} from '@/types/geospatial';

/**
 * Hook for geospatial engine status
 * @returns Engine status and data source availability
 */
export const useGeospatialStatus = () => {
  const [status, setStatus] = useState<GeospatialEngineStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const data = await GeospatialService.getStatus();
      setStatus(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Error fetching geospatial status');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return { status, loading, error, refetch: fetchStatus };
};

/**
 * Hook for available data sources
 * @returns List of free geospatial data sources
 */
export const useDataSources = () => {
  const [sources, setSources] = useState<DataSourceInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSources = useCallback(async () => {
    setLoading(true);
    try {
      const data = await GeospatialService.getDataSources();
      setSources(data.sources);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Error fetching data sources');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  return { sources, loading, error, refetch: fetchSources };
};

/**
 * Hook for LiDAR data
 * @param bbox - Bounding box for query
 * @returns LiDAR data and loading state
 */
export const useLidar = (bbox?: BoundingBox) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (queryBbox: BoundingBox) => {
    setLoading(true);
    try {
      const response = await GeospatialService.lidar.query({
        bbox: queryBbox,
        includeDtm: true,
        includeDsm: true,
      });
      setData(response);
      setError(null);
      return response;
    } catch (err: any) {
      setError(err.message || 'Error fetching LiDAR data');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, fetchData };
};

/**
 * Hook for Sentinel-2 vegetation indices
 * @returns Vegetation analysis functions
 */
export const useSentinel = () => {
  const [data, setData] = useState<any>(null);
  const [scenes, setScenes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchScenes = useCallback(async (
    bbox: string,
    dateStart: string,
    dateEnd: string,
    cloudMax = 20
  ) => {
    setLoading(true);
    try {
      const response = await GeospatialService.sentinel.listScenes(
        bbox, dateStart, dateEnd, cloudMax
      );
      setScenes(response.scenes || []);
      return response;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getIndices = useCallback(async (sceneId: string) => {
    setLoading(true);
    try {
      const response = await GeospatialService.sentinel.getIndices(sceneId);
      setData(response);
      return response;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, scenes, loading, error, fetchScenes, getIndices };
};

/**
 * Hook for hydrology data
 * @returns Water features and analysis
 */
export const useHydrology = () => {
  const [rivers, setRivers] = useState<any[]>([]);
  const [lakes, setLakes] = useState<any[]>([]);
  const [wetlands, setWetlands] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async (bbox: string) => {
    setLoading(true);
    try {
      const [riversRes, lakesRes, wetlandsRes] = await Promise.all([
        GeospatialService.hydro.getRivers(bbox),
        GeospatialService.hydro.getLakes(bbox),
        GeospatialService.hydro.getWetlands(bbox),
      ]);
      setRivers(riversRes.rivers || []);
      setLakes(lakesRes.lakes || []);
      setWetlands(wetlandsRes.wetlands || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { rivers, lakes, wetlands, loading, error, fetchAll };
};

/**
 * Hook for terrain/geomorphology analysis
 * @returns Terrain features and analysis
 */
export const useGeomorphology = () => {
  const [slope, setSlope] = useState<any>(null);
  const [aspect, setAspect] = useState<any>(null);
  const [features, setFeatures] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (bbox: string) => {
    setLoading(true);
    try {
      const [slopeRes, aspectRes, featuresRes] = await Promise.all([
        GeospatialService.geomorph.getSlope(bbox),
        GeospatialService.geomorph.getAspect(bbox),
        GeospatialService.geomorph.getFeatures(bbox),
      ]);
      setSlope(slopeRes);
      setAspect(aspectRes);
      setFeatures(featuresRes.features || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { slope, aspect, features, loading, error, analyze };
};

/**
 * Hook for forest inventory data
 * @returns Forest stands and composition
 */
export const useForest = () => {
  const [stands, setStands] = useState<any[]>([]);
  const [species, setSpecies] = useState<Record<string, number>>({});
  const [ageClasses, setAgeClasses] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (bbox: string) => {
    setLoading(true);
    try {
      const [standsRes, speciesRes, ageRes] = await Promise.all([
        GeospatialService.forest.getStands(bbox),
        GeospatialService.forest.getSpecies(bbox),
        GeospatialService.forest.getAge(bbox),
      ]);
      setStands(standsRes.stands || []);
      setSpecies(speciesRes.species || {});
      setAgeClasses(ageRes.age_classes || {});
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { stands, species, ageClasses, loading, error, fetchData };
};

/**
 * Hook for AI predictions
 * @returns Corridors, feeding zones, bedding zones
 */
export const useAIPredictions = () => {
  const [predictions, setPredictions] = useState<AIPredictionResponse | null>(null);
  const [corridors, setCorridors] = useState<any[]>([]);
  const [feedingZones, setFeedingZones] = useState<any[]>([]);
  const [beddingZones, setBeddingZones] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predict = useCallback(async (
    bbox: string,
    species: string,
    season: string
  ) => {
    setLoading(true);
    try {
      const [corridorsRes, feedingRes, beddingRes] = await Promise.all([
        GeospatialService.ai.getCorridors(bbox, species, season),
        GeospatialService.ai.getFeedingZones(bbox, species, season),
        GeospatialService.ai.getBeddingZones(bbox, species),
      ]);
      setCorridors(corridorsRes.corridors || []);
      setFeedingZones(feedingRes.zones || []);
      setBeddingZones(beddingRes.zones || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    predictions,
    corridors,
    feedingZones,
    beddingZones,
    loading,
    error,
    predict,
  };
};

/**
 * Hook for hunting potential calculation
 * @returns Hunting score and hotspots
 */
export const useHuntingPotential = () => {
  const [potential, setPotential] = useState<HuntingPotentialResponse | null>(null);
  const [hotspots, setHotspots] = useState<any[]>([]);
  const [standLocations, setStandLocations] = useState<any[]>([]);
  const [components, setComponents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculate = useCallback(async (
    bbox: string,
    lat: number,
    lon: number,
    species: string,
    season: string
  ) => {
    setLoading(true);
    try {
      const [hotspotsRes, locationsRes] = await Promise.all([
        GeospatialService.potential.getHotspots(bbox, species, season),
        GeospatialService.potential.getStandLocations(lat, lon, 1000, species),
      ]);
      setHotspots(hotspotsRes.hotspots || []);
      setStandLocations(locationsRes.locations || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchComponents = useCallback(async () => {
    try {
      const res = await GeospatialService.potential.getComponents();
      setComponents(res.components || []);
    } catch (err: any) {
      console.error('Error fetching components:', err);
    }
  }, []);

  useEffect(() => {
    fetchComponents();
  }, [fetchComponents]);

  return {
    potential,
    hotspots,
    standLocations,
    components,
    loading,
    error,
    calculate,
  };
};

// Export all hooks
export default {
  useGeospatialStatus,
  useDataSources,
  useLidar,
  useSentinel,
  useHydrology,
  useGeomorphology,
  useForest,
  useAIPredictions,
  useHuntingPotential,
};
