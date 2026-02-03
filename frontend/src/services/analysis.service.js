/**
 * HUNTIQ V3 - Analysis Service
 * API service for BIONIC™ product analysis
 */

import { api } from './api.client';
import { API_ENDPOINTS } from './api.config';

export const AnalysisService = {
  /**
   * Perform standard product analysis
   * @param {Object} params - Analysis parameters
   * @returns {Promise<Object>} Analysis result
   */
  analyze: async (params) => {
    const response = await api.post(API_ENDPOINTS.ANALYZE, params);
    return response.data;
  },

  /**
   * Perform AI-powered advanced analysis (GPT-5.2)
   * @param {Object} params - Analysis parameters with AI options
   * @returns {Promise<Object>} AI analysis result
   */
  analyzeAI: async (params) => {
    const response = await api.post(API_ENDPOINTS.ANALYZE_AI, params);
    return response.data;
  },

  /**
   * Get analysis criteria (13 BIONIC criteria)
   * @returns {Promise<Array>} Criteria list with weights
   */
  getCriteria: async () => {
    const response = await api.get(API_ENDPOINTS.ANALYZE_CRITERIA);
    return response.data;
  },

  /**
   * Get analysis categories
   * @returns {Promise<Array>} Categories list
   */
  getCategories: async () => {
    const response = await api.get(API_ENDPOINTS.ANALYZE_CATEGORIES);
    return response.data;
  },

  /**
   * Get scientific references
   * @returns {Promise<Array>} References list
   */
  getReferences: async () => {
    const response = await api.get(API_ENDPOINTS.ANALYZE_REFERENCES);
    return response.data;
  },

  /**
   * Get BIONIC products for analysis
   * @returns {Promise<Array>} BIONIC products
   */
  getBionicProducts: async () => {
    const response = await api.get(API_ENDPOINTS.ANALYZE_BIONIC_PRODUCTS);
    return response.data;
  },

  /**
   * Get competitors by category
   * @param {string} category - Category slug
   * @returns {Promise<Array>} Competitor products
   */
  getCompetitors: async (category) => {
    const response = await api.get(API_ENDPOINTS.ANALYZE_COMPETITORS(category));
    return response.data;
  },

  /**
   * Get ingredients database
   * @returns {Promise<Array>} Ingredients list
   */
  getIngredients: async () => {
    const response = await api.get(API_ENDPOINTS.ANALYZE_INGREDIENTS);
    return response.data;
  },

  /**
   * Get analysis reports history
   * @returns {Promise<Array>} Reports list
   */
  getReports: async () => {
    const response = await api.get(API_ENDPOINTS.ANALYZE_REPORTS);
    return response.data;
  },

  /**
   * Get specific report by ID
   * @param {string} reportId - Report ID
   * @returns {Promise<Object>} Report data
   */
  getReport: async (reportId) => {
    const response = await api.get(`${API_ENDPOINTS.ANALYZE_REPORTS}/${reportId}`);
    return response.data;
  },
};

export default AnalysisService;
