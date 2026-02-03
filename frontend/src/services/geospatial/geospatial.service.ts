/**
 * HUNTIQ V3 - BIONIC™ Geospatial Engine
 * Frontend Services - API services for geospatial data
 * 
 * This module provides service stubs for the geospatial engine.
 * NO IMPLEMENTATION - Architecture preparation only.
 */

import { api } from '../api.client';
import type {
  LidarDataRequest,
  LidarDataResponse,
  SentinelDataRequest,
  SentinelDataResponse,
  LandsatDataRequest,
  LandsatDataResponse,
  SigeomDataRequest,
  SigeomDataResponse,
  HydrologyDataRequest,
  HydrologyDataResponse,
  GeomorphologyRequest,
  GeomorphologyResponse,
  ForestDataRequest,
  ForestDataResponse,
  AIPredictionRequest,
  AIPredictionResponse,
  HuntingPotentialRequest,
  HuntingPotentialResponse,
  GeospatialEngineStatus,
  DataSourceInfo,
  BoundingBox,
} from '@/types/geospatial';

// API Base path for geospatial endpoints
const GEOSPATIAL_BASE = '/api/geospatial';

/**
 * Geospatial Engine Service
 * Central service for all geospatial operations
 */
export const GeospatialService = {
  // ===========================================================================
  // STATUS & CONFIGURATION
  // ===========================================================================

  /**
   * Get geospatial engine status
   * @returns Engine status and data source availability
   */
  getStatus: async (): Promise<GeospatialEngineStatus> => {
    const response = await api.get(`${GEOSPATIAL_BASE}/status`);
    return response.data;
  },

  /**
   * List all available free data sources
   * @returns Array of data source information
   */
  getDataSources: async (): Promise<{ sources: DataSourceInfo[] }> => {
    const response = await api.get(`${GEOSPATIAL_BASE}/data-sources`);
    return response.data;
  },

  // ===========================================================================
  // LIDAR MODULE - LiDAR Québec (Données ouvertes)
  // ===========================================================================

  lidar: {
    /**
     * Query LiDAR data for a bounding box
     * @param request - LiDAR data request parameters
     * @returns LiDAR data response with DTM/DSM/CHM URLs
     */
    query: async (request: LidarDataRequest): Promise<LidarDataResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/lidar/query`, request);
      return response.data;
    },

    /**
     * Get LiDAR coverage areas in Québec
     * @returns Available coverage areas
     */
    getCoverage: async () => {
      const response = await api.get(`${GEOSPATIAL_BASE}/lidar/coverage`);
      return response.data;
    },

    /**
     * List available LiDAR tiles
     * @param bbox - Optional bounding box to filter tiles
     * @returns List of available tiles
     */
    listTiles: async (bbox?: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/lidar/tiles`, { bbox });
      return response.data;
    },
  },

  // ===========================================================================
  // SENTINEL MODULE - ESA Copernicus (Free)
  // ===========================================================================

  sentinel: {
    /**
     * Query Sentinel-2 imagery
     * @param request - Sentinel data request parameters
     * @returns Sentinel data response with vegetation indices
     */
    query: async (request: SentinelDataRequest): Promise<SentinelDataResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/sentinel/query`, request);
      return response.data;
    },

    /**
     * List available Sentinel-2 scenes
     * @param bbox - Bounding box (WKT format)
     * @param dateStart - Start date
     * @param dateEnd - End date
     * @param cloudMax - Maximum cloud cover percentage
     * @returns List of available scenes
     */
    listScenes: async (bbox: string, dateStart: string, dateEnd: string, cloudMax = 20) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/sentinel/scenes`, {
        bbox,
        date_start: dateStart,
        date_end: dateEnd,
        cloud_max: cloudMax,
      });
      return response.data;
    },

    /**
     * Get vegetation indices for a scene
     * @param sceneId - Sentinel-2 scene ID
     * @returns Calculated vegetation indices
     */
    getIndices: async (sceneId: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/sentinel/indices/${sceneId}`);
      return response.data;
    },
  },

  // ===========================================================================
  // LANDSAT MODULE - USGS (Free)
  // ===========================================================================

  landsat: {
    /**
     * Query Landsat 8/9 imagery
     * @param request - Landsat data request parameters
     * @returns Landsat data response
     */
    query: async (request: LandsatDataRequest): Promise<LandsatDataResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/landsat/query`, request);
      return response.data;
    },

    /**
     * List available Landsat scenes
     * @param bbox - Bounding box
     * @param dateStart - Start date
     * @param dateEnd - End date
     * @param satellite - Landsat 8 or 9
     * @returns List of available scenes
     */
    listScenes: async (
      bbox: string,
      dateStart: string,
      dateEnd: string,
      satellite = 'landsat_8'
    ) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/landsat/scenes`, {
        bbox,
        date_start: dateStart,
        date_end: dateEnd,
        satellite,
      });
      return response.data;
    },
  },

  // ===========================================================================
  // SIGEOM MODULE - Géologie Québec (Free)
  // ===========================================================================

  sigeom: {
    /**
     * Query geological data from SIGÉOM
     * @param request - SIGÉOM data request parameters
     * @returns Geological data response
     */
    query: async (request: SigeomDataRequest): Promise<SigeomDataResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/sigeom/query`, request);
      return response.data;
    },

    /**
     * Get bedrock geology for a region
     * @param bbox - Bounding box
     * @returns Bedrock geology data
     */
    getBedrock: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/sigeom/bedrock`, { bbox });
      return response.data;
    },

    /**
     * Get surficial geology (Quaternary deposits)
     * @param bbox - Bounding box
     * @returns Surficial geology data
     */
    getSurficial: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/sigeom/surficial`, { bbox });
      return response.data;
    },
  },

  // ===========================================================================
  // HYDROLOGY MODULE - Données ouvertes Québec
  // ===========================================================================

  hydro: {
    /**
     * Query hydrological data
     * @param request - Hydrology data request parameters
     * @returns Hydrological data response
     */
    query: async (request: HydrologyDataRequest): Promise<HydrologyDataResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/hydro/query`, request);
      return response.data;
    },

    /**
     * Get rivers and streams
     * @param bbox - Bounding box
     * @param bufferM - Buffer distance in meters
     * @returns Rivers data
     */
    getRivers: async (bbox: string, bufferM = 100) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/hydro/rivers`, {
        bbox,
        buffer_m: bufferM,
      });
      return response.data;
    },

    /**
     * Get lakes and ponds
     * @param bbox - Bounding box
     * @param minAreaM2 - Minimum area in square meters
     * @returns Lakes data
     */
    getLakes: async (bbox: string, minAreaM2 = 1000) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/hydro/lakes`, {
        bbox,
        min_area_m2: minAreaM2,
      });
      return response.data;
    },

    /**
     * Get wetlands
     * @param bbox - Bounding box
     * @returns Wetlands data
     */
    getWetlands: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/hydro/wetlands`, { bbox });
      return response.data;
    },
  },

  // ===========================================================================
  // GEOMORPHOLOGY MODULE - Terrain Analysis
  // ===========================================================================

  geomorph: {
    /**
     * Perform geomorphological analysis
     * @param request - Geomorphology analysis request
     * @returns Terrain analysis results
     */
    analyze: async (request: GeomorphologyRequest): Promise<GeomorphologyResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/geomorph/analyze`, request);
      return response.data;
    },

    /**
     * Get slope data
     * @param bbox - Bounding box
     * @param units - Degrees or percent
     * @returns Slope data
     */
    getSlope: async (bbox: string, units = 'degrees') => {
      const response = await api.get(`${GEOSPATIAL_BASE}/geomorph/slope`, { bbox, units });
      return response.data;
    },

    /**
     * Get aspect (slope direction) data
     * @param bbox - Bounding box
     * @returns Aspect data
     */
    getAspect: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/geomorph/aspect`, { bbox });
      return response.data;
    },

    /**
     * Identify terrain features (ridges, valleys, etc.)
     * @param bbox - Bounding box
     * @returns Identified terrain features
     */
    getFeatures: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/geomorph/features`, { bbox });
      return response.data;
    },
  },

  // ===========================================================================
  // FOREST MODULE - MFFP Québec (Free)
  // ===========================================================================

  forest: {
    /**
     * Query forest inventory data
     * @param request - Forest data request parameters
     * @returns Forest inventory response
     */
    query: async (request: ForestDataRequest): Promise<ForestDataResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/forest/query`, request);
      return response.data;
    },

    /**
     * Get forest stands
     * @param bbox - Bounding box
     * @returns Forest stands data
     */
    getStands: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/forest/stands`, { bbox });
      return response.data;
    },

    /**
     * Get species composition
     * @param bbox - Bounding box
     * @returns Species composition data
     */
    getSpecies: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/forest/species`, { bbox });
      return response.data;
    },

    /**
     * Get forest age class distribution
     * @param bbox - Bounding box
     * @returns Age class data
     */
    getAge: async (bbox: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/forest/age`, { bbox });
      return response.data;
    },
  },

  // ===========================================================================
  // AI PREDICTION MODULE - Hunting corridors & zones
  // ===========================================================================

  ai: {
    /**
     * Generate AI predictions for hunting zones
     * @param request - AI prediction request
     * @returns Predicted corridors and zones
     */
    predict: async (request: AIPredictionRequest): Promise<AIPredictionResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/ai/predict`, request);
      return response.data;
    },

    /**
     * Get predicted movement corridors
     * @param bbox - Bounding box
     * @param species - Target species
     * @param season - Hunting season
     * @returns Predicted corridors
     */
    getCorridors: async (bbox: string, species: string, season: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/ai/corridors`, {
        bbox,
        species,
        season,
      });
      return response.data;
    },

    /**
     * Get predicted feeding zones
     * @param bbox - Bounding box
     * @param species - Target species
     * @param season - Hunting season
     * @returns Predicted feeding zones
     */
    getFeedingZones: async (bbox: string, species: string, season: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/ai/feeding-zones`, {
        bbox,
        species,
        season,
      });
      return response.data;
    },

    /**
     * Get predicted bedding zones
     * @param bbox - Bounding box
     * @param species - Target species
     * @returns Predicted bedding zones
     */
    getBeddingZones: async (bbox: string, species: string) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/ai/bedding-zones`, {
        bbox,
        species,
      });
      return response.data;
    },
  },

  // ===========================================================================
  // HUNTING POTENTIAL MODULE - Score calculation
  // ===========================================================================

  potential: {
    /**
     * Calculate hunting potential score
     * @param request - Hunting potential request
     * @returns Hunting potential analysis with score
     */
    calculate: async (request: HuntingPotentialRequest): Promise<HuntingPotentialResponse> => {
      const response = await api.post(`${GEOSPATIAL_BASE}/potential/calculate`, request);
      return response.data;
    },

    /**
     * Get hunting hotspots in a region
     * @param bbox - Bounding box
     * @param species - Target species
     * @param season - Hunting season
     * @param limit - Maximum number of hotspots
     * @returns List of hunting hotspots
     */
    getHotspots: async (bbox: string, species: string, season: string, limit = 10) => {
      const response = await api.get(`${GEOSPATIAL_BASE}/potential/hotspots`, {
        bbox,
        species,
        season,
        limit,
      });
      return response.data;
    },

    /**
     * Get recommended stand locations
     * @param lat - Latitude
     * @param lon - Longitude
     * @param radiusM - Search radius in meters
     * @param species - Target species
     * @returns Recommended stand locations
     */
    getStandLocations: async (lat: number, lon: number, radiusM = 1000, species = 'deer') => {
      const response = await api.get(`${GEOSPATIAL_BASE}/potential/stand-locations`, {
        lat,
        lon,
        radius_m: radiusM,
        species,
      });
      return response.data;
    },

    /**
     * Get potential calculation components
     * @returns List of scoring components with weights
     */
    getComponents: async () => {
      const response = await api.get(`${GEOSPATIAL_BASE}/potential/components`);
      return response.data;
    },
  },
};

export default GeospatialService;
