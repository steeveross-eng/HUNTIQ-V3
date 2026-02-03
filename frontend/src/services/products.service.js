/**
 * HUNTIQ V3 - Products Service
 * API service for products operations
 */

import { api } from './api.client';
import { API_ENDPOINTS } from './api.config';

export const ProductsService = {
  /**
   * Get all products
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} Products list
   */
  getAll: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.PRODUCTS, params);
    return response.data;
  },

  /**
   * Get top products for carousel
   * @param {number} limit - Number of products
   * @returns {Promise<Array>} Top products
   */
  getTop: async (limit = 10) => {
    const response = await api.get(API_ENDPOINTS.PRODUCTS_TOP, { limit });
    return response.data;
  },

  /**
   * Get single product by ID
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Product data
   */
  getById: async (productId) => {
    const response = await api.get(`${API_ENDPOINTS.PRODUCTS}/${productId}`);
    return response.data;
  },

  /**
   * Search products
   * @param {Object} searchParams - Search criteria
   * @returns {Promise<Array>} Search results
   */
  search: async (searchParams) => {
    const response = await api.post(API_ENDPOINTS.PRODUCTS_SEARCH, searchParams);
    return response.data;
  },

  /**
   * Filter products
   * @param {Object} filters - Filter criteria
   * @returns {Promise<Array>} Filtered products
   */
  filter: async (filters) => {
    const response = await api.post(API_ENDPOINTS.PRODUCTS_FILTER, filters);
    return response.data;
  },

  /**
   * Get filter options (brands, categories, etc.)
   * @returns {Promise<Object>} Filter options
   */
  getFilterOptions: async () => {
    const response = await api.get(API_ENDPOINTS.PRODUCTS_FILTERS_OPTIONS);
    return response.data;
  },

  /**
   * Get all brands
   * @returns {Promise<Array>} Brands list
   */
  getBrands: async () => {
    const response = await api.get(API_ENDPOINTS.PRODUCTS_BRANDS);
    return response.data;
  },

  /**
   * Get all categories
   * @returns {Promise<Array>} Categories list
   */
  getCategories: async () => {
    const response = await api.get(API_ENDPOINTS.PRODUCTS_CATEGORIES);
    return response.data;
  },

  /**
   * Analyze a product
   * @param {string} productId - Product ID
   * @returns {Promise<Object>} Analysis result
   */
  analyze: async (productId) => {
    const response = await api.post(`${API_ENDPOINTS.PRODUCTS}/${productId}/analyze`);
    return response.data;
  },

  /**
   * Compare products
   * @param {string} productId - Base product ID
   * @param {Array} compareIds - IDs to compare with
   * @returns {Promise<Object>} Comparison result
   */
  compare: async (productId, compareIds) => {
    const response = await api.post(`${API_ENDPOINTS.PRODUCTS}/${productId}/compare`, {
      compare_with: compareIds,
    });
    return response.data;
  },
};

export default ProductsService;
