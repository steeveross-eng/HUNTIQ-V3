/**
 * HUNTIQ V3 - Admin Service
 * API service for administration operations
 */

import { api } from './api.client';
import { API_ENDPOINTS } from './api.config';

export const AdminService = {
  /**
   * Authenticate admin user
   * @param {string} password - Admin password
   * @returns {Promise<Object>} Auth result
   */
  login: async (password) => {
    const response = await api.post(API_ENDPOINTS.ADMIN_LOGIN, { password });
    return response.data;
  },

  /**
   * Get admin dashboard stats
   * @returns {Promise<Object>} Dashboard statistics
   */
  getStats: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_STATS);
    return response.data;
  },

  /**
   * Get all products (admin view)
   * @returns {Promise<Array>} Products list
   */
  getProducts: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_PRODUCTS);
    return response.data;
  },

  /**
   * Create product
   * @param {Object} product - Product data
   * @returns {Promise<Object>} Created product
   */
  createProduct: async (product) => {
    const response = await api.post(API_ENDPOINTS.ADMIN_PRODUCTS, product);
    return response.data;
  },

  /**
   * Update product
   * @param {string} productId - Product ID
   * @param {Object} product - Product data
   * @returns {Promise<Object>} Updated product
   */
  updateProduct: async (productId, product) => {
    const response = await api.put(API_ENDPOINTS.ADMIN_PRODUCT(productId), product);
    return response.data;
  },

  /**
   * Delete product
   * @param {string} productId - Product ID
   * @returns {Promise<void>}
   */
  deleteProduct: async (productId) => {
    await api.delete(API_ENDPOINTS.ADMIN_PRODUCT(productId));
  },

  /**
   * Get sales reports
   * @returns {Promise<Object>} Sales data
   */
  getSalesReports: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_REPORTS_SALES);
    return response.data;
  },

  /**
   * Get products reports
   * @returns {Promise<Object>} Products data
   */
  getProductsReports: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_REPORTS_PRODUCTS);
    return response.data;
  },

  /**
   * Get suppliers reports
   * @returns {Promise<Object>} Suppliers data
   */
  getSuppliersReports: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_REPORTS_SUPPLIERS);
    return response.data;
  },

  /**
   * Get commissions reports
   * @returns {Promise<Object>} Commissions data
   */
  getCommissionsReports: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_REPORTS_COMMISSIONS);
    return response.data;
  },

  /**
   * Get admin alerts
   * @returns {Promise<Array>} Alerts list
   */
  getAlerts: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_ALERTS);
    return response.data;
  },

  /**
   * Generate new alerts
   * @returns {Promise<Array>} Generated alerts
   */
  generateAlerts: async () => {
    const response = await api.post(`${API_ENDPOINTS.ADMIN_ALERTS}/generate`);
    return response.data;
  },

  /**
   * Mark alert as read
   * @param {string} alertId - Alert ID
   * @returns {Promise<Object>} Updated alert
   */
  markAlertRead: async (alertId) => {
    const response = await api.put(`${API_ENDPOINTS.ADMIN_ALERTS}/${alertId}/read`);
    return response.data;
  },

  /**
   * Get site settings
   * @returns {Promise<Object>} Settings data
   */
  getSiteSettings: async () => {
    const response = await api.get(API_ENDPOINTS.ADMIN_SITE_SETTINGS);
    return response.data;
  },

  /**
   * Update maintenance mode
   * @param {boolean} enabled - Enable/disable maintenance
   * @returns {Promise<Object>} Updated settings
   */
  setMaintenanceMode: async (enabled) => {
    const response = await api.put(`${API_ENDPOINTS.ADMIN_SITE_SETTINGS}/maintenance`, {
      enabled,
    });
    return response.data;
  },
};

export default AdminService;
