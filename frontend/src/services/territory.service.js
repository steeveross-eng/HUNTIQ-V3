/**
 * HUNTIQ V3 - Territory Service
 * API service for territory and hunting zone operations
 */

import { api } from './api.client';
import { API_ENDPOINTS } from './api.config';

export const TerritoryService = {
  /**
   * Get territory categories (zones de chasse)
   * @returns {Promise<Array>} Categories list
   */
  getCategories: async () => {
    const response = await api.get(API_ENDPOINTS.TERRITORY_CATEGORIES);
    return response.data;
  },

  /**
   * Get species rules and regulations
   * @returns {Promise<Array>} Species rules
   */
  getSpeciesRules: async () => {
    const response = await api.get(API_ENDPOINTS.TERRITORY_SPECIES_RULES);
    return response.data;
  },

  /**
   * Calculate hunting probability
   * @param {Object} params - Location, species, conditions
   * @returns {Promise<Object>} Probability data
   */
  calculateProbability: async (params) => {
    const response = await api.post(API_ENDPOINTS.TERRITORY_PROBABILITY, params);
    return response.data;
  },

  /**
   * Generate territory heatmap
   * @param {Object} params - Heatmap parameters
   * @returns {Promise<Object>} Heatmap data
   */
  generateHeatmap: async (params) => {
    const response = await api.post(API_ENDPOINTS.TERRITORY_HEATMAP, params);
    return response.data;
  },

  /**
   * Create action plan for territory
   * @param {Object} plan - Action plan data
   * @returns {Promise<Object>} Created plan
   */
  createActionPlan: async (plan) => {
    const response = await api.post(API_ENDPOINTS.TERRITORY_ACTION_PLAN, plan);
    return response.data;
  },

  /**
   * Get all action plans
   * @returns {Promise<Array>} Action plans list
   */
  getActionPlans: async () => {
    const response = await api.get(API_ENDPOINTS.TERRITORY_ACTION_PLANS);
    return response.data;
  },

  /**
   * Get trail cameras
   * @returns {Promise<Array>} Cameras list
   */
  getCameras: async () => {
    const response = await api.get(API_ENDPOINTS.TERRITORY_CAMERAS);
    return response.data;
  },

  /**
   * Add trail camera
   * @param {Object} camera - Camera data
   * @returns {Promise<Object>} Created camera
   */
  addCamera: async (camera) => {
    const response = await api.post(API_ENDPOINTS.TERRITORY_CAMERAS, camera);
    return response.data;
  },

  /**
   * Test camera connection
   * @param {string} cameraId - Camera ID
   * @returns {Promise<Object>} Test result
   */
  testCamera: async (cameraId) => {
    const response = await api.post(`${API_ENDPOINTS.TERRITORY_CAMERAS}/${cameraId}/test`);
    return response.data;
  },

  /**
   * Get territory events (sightings, activity)
   * @returns {Promise<Array>} Events list
   */
  getEvents: async () => {
    const response = await api.get(API_ENDPOINTS.TERRITORY_EVENTS);
    return response.data;
  },

  /**
   * Add territory event
   * @param {Object} event - Event data
   * @returns {Promise<Object>} Created event
   */
  addEvent: async (event) => {
    const response = await api.post(API_ENDPOINTS.TERRITORY_EVENTS, event);
    return response.data;
  },

  /**
   * Classify photo using AI
   * @param {Object} photoData - Photo data for classification
   * @returns {Promise<Object>} Classification result
   */
  classifyPhoto: async (photoData) => {
    const response = await api.post(API_ENDPOINTS.TERRITORY_CLASSIFY_PHOTO, photoData);
    return response.data;
  },
};

export default TerritoryService;
