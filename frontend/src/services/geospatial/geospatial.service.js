/**
 * HUNTIQ V3 - BIONIC™ Geospatial Engine Service
 * Frontend service for geospatial data operations
 * 
 * Connects to real Quebec government data sources (100% free)
 */

import { api } from '../api.client';
import { API_ENDPOINTS } from '../api.config';

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
   * @returns {Promise<Object>} Engine status and data source availability
   */
  getStatus: async () => {
    const response = await api.get(API_ENDPOINTS.GEOSPATIAL_STATUS);
    return response.data;
  },

  /**
   * List all available free data sources
   * @returns {Promise<Object>} Array of data source information
   */
  getDataSources: async () => {
    const response = await api.get(API_ENDPOINTS.GEOSPATIAL_DATA_SOURCES);
    return response.data;
  },

  // ===========================================================================
  // LIDAR MODULE - LiDAR Québec (Données ouvertes)
  // ===========================================================================

  lidar: {
    /**
     * Query LiDAR data for a bounding box
     * @param {Object} request - LiDAR data request parameters
     * @returns {Promise<Object>} LiDAR data response with DTM/DSM/CHM URLs
     */
    query: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_LIDAR_QUERY, request);
      return response.data;
    },

    /**
     * Get LiDAR coverage areas in Québec
     * @param {Object} bbox - Bounding box
     * @returns {Promise<Object>} Available coverage areas
     */
    getCoverage: async (bbox) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_LIDAR_COVERAGE, bbox);
      return response.data;
    },
  },

  // ===========================================================================
  // SENTINEL MODULE - ESA Copernicus (Free)
  // ===========================================================================

  sentinel: {
    /**
     * Query Sentinel-2 imagery
     * @param {Object} request - Sentinel data request parameters
     * @returns {Promise<Object>} Sentinel data response with vegetation indices
     */
    query: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_SENTINEL_QUERY, request);
      return response.data;
    },

    /**
     * List available Sentinel-2 scenes
     * @param {Object} params - Search parameters
     * @returns {Promise<Object>} List of available scenes
     */
    listScenes: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_SENTINEL_SCENES, params);
      return response.data;
    },
  },

  // ===========================================================================
  // SIGEOM MODULE - Géologie Québec (Free)
  // ===========================================================================

  sigeom: {
    /**
     * Query geological data from SIGÉOM
     * @param {Object} request - SIGÉOM data request parameters
     * @returns {Promise<Object>} Geological data response
     */
    query: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_SIGEOM_QUERY, request);
      return response.data;
    },
  },

  // ===========================================================================
  // HYDROLOGY MODULE - Données ouvertes Québec
  // ===========================================================================

  hydro: {
    /**
     * Query hydrological data
     * @param {Object} request - Hydrology data request parameters
     * @returns {Promise<Object>} Hydrological data response
     */
    query: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_HYDRO_QUERY, request);
      return response.data;
    },

    /**
     * Get rivers and streams
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} Rivers data
     */
    getRivers: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_HYDRO_RIVERS, params);
      return response.data;
    },

    /**
     * Get lakes and ponds
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} Lakes data
     */
    getLakes: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_HYDRO_LAKES, params);
      return response.data;
    },

    /**
     * Get wetlands
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} Wetlands data
     */
    getWetlands: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_HYDRO_WETLANDS, params);
      return response.data;
    },
  },

  // ===========================================================================
  // FOREST MODULE - MFFP Québec (Free)
  // ===========================================================================

  forest: {
    /**
     * Query forest inventory data
     * @param {Object} request - Forest data request parameters
     * @returns {Promise<Object>} Forest inventory response
     */
    query: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_FOREST_QUERY, request);
      return response.data;
    },

    /**
     * Get species composition
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} Species composition data
     */
    getSpecies: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_FOREST_SPECIES, params);
      return response.data;
    },
  },

  // ===========================================================================
  // GEOMORPHOLOGY MODULE - Terrain Analysis
  // ===========================================================================

  geomorph: {
    /**
     * Perform geomorphological analysis
     * @param {Object} request - Geomorphology analysis request
     * @returns {Promise<Object>} Terrain analysis results
     */
    analyze: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_GEOMORPH_ANALYZE, request);
      return response.data;
    },
  },

  // ===========================================================================
  // AI PREDICTION MODULE - Hunting corridors & zones
  // ===========================================================================

  ai: {
    /**
     * Generate AI predictions for hunting zones
     * @param {Object} request - AI prediction request
     * @returns {Promise<Object>} Predicted corridors and zones
     */
    predict: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_AI_PREDICT, request);
      return response.data;
    },

    /**
     * Get predicted movement corridors
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} Predicted corridors
     */
    getCorridors: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_AI_CORRIDORS, params);
      return response.data;
    },
  },

  // ===========================================================================
  // HUNTING POTENTIAL MODULE - Score calculation
  // ===========================================================================

  potential: {
    /**
     * Calculate hunting potential score
     * @param {Object} request - Hunting potential request
     * @returns {Promise<Object>} Hunting potential analysis with score
     */
    calculate: async (request) => {
      const response = await api.post(API_ENDPOINTS.GEOSPATIAL_POTENTIAL_CALCULATE, request);
      return response.data;
    },

    /**
     * Get hunting hotspots in a region
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} List of hunting hotspots
     */
    getHotspots: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_POTENTIAL_HOTSPOTS, params);
      return response.data;
    },

    /**
     * Get recommended stand locations
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} Recommended stand locations
     */
    getStandLocations: async (params) => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_POTENTIAL_STAND_LOCATIONS, params);
      return response.data;
    },

    /**
     * Get potential calculation components
     * @returns {Promise<Object>} List of scoring components with weights
     */
    getComponents: async () => {
      const response = await api.get(API_ENDPOINTS.GEOSPATIAL_POTENTIAL_COMPONENTS);
      return response.data;
    },
  },
};

export default GeospatialService;
