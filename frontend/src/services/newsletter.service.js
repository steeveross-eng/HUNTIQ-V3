/**
 * HUNTIQ V3 - Newsletter Service
 * API service for newsletter subscriptions
 * 
 * Note: Backend endpoint to be created. Currently uses simulated response.
 */

import { api } from './api.client';

export const NewsletterService = {
  /**
   * Subscribe to newsletter
   * @param {string} email - Email address
   * @param {Object} preferences - Subscription preferences
   * @returns {Promise<Object>} Subscription result
   */
  subscribe: async (email, preferences = {}) => {
    // TODO: Replace with real API when backend is ready
    // const response = await api.post('/api/newsletter/subscribe', { email, ...preferences });
    // return response.data;
    
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
          reject({ error: 'Format d\'email invalide' });
          return;
        }
        
        // Simulate successful subscription
        resolve({
          success: true,
          message: 'Inscription réussie! Vérifiez votre boîte mail.',
          email,
          subscribedAt: new Date().toISOString(),
        });
      }, 800);
    });
  },

  /**
   * Unsubscribe from newsletter
   * @param {string} email - Email address
   * @param {string} token - Unsubscribe token
   * @returns {Promise<Object>} Unsubscribe result
   */
  unsubscribe: async (email, token) => {
    // TODO: Implement when backend is ready
    return { success: true, message: 'Désinscription effectuée.' };
  },

  /**
   * Update subscription preferences
   * @param {string} email - Email address
   * @param {Object} preferences - New preferences
   * @returns {Promise<Object>} Update result
   */
  updatePreferences: async (email, preferences) => {
    // TODO: Implement when backend is ready
    return { success: true, preferences };
  },

  /**
   * Get newsletter categories
   * @returns {Promise<Array>} Categories list
   */
  getCategories: async () => {
    return [
      { id: 'weather', label: 'Alertes météo', description: 'Conditions optimales de chasse' },
      { id: 'products', label: 'Nouveaux produits', description: 'Attractants et équipements testés' },
      { id: 'offers', label: 'Offres exclusives', description: 'Promotions et réductions' },
      { id: 'tips', label: 'Conseils pro', description: 'Stratégies et techniques' },
      { id: 'regulations', label: 'Règlements', description: 'Mises à jour réglementaires' },
    ];
  },

  /**
   * Verify email subscription
   * @param {string} token - Verification token
   * @returns {Promise<Object>} Verification result
   */
  verifyEmail: async (token) => {
    // TODO: Implement when backend is ready
    return { success: true, verified: true };
  },
};

export default NewsletterService;
