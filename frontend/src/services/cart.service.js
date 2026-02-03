/**
 * HUNTIQ V3 - Cart Service
 * API service for shopping cart operations
 */

import { api } from './api.client';
import { API_ENDPOINTS } from './api.config';

// Generate or get session ID
const getSessionId = () => {
  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('session_id', sessionId);
  }
  return sessionId;
};

export const CartService = {
  /**
   * Get session ID
   * @returns {string} Session ID
   */
  getSessionId,

  /**
   * Get cart items for current session
   * @returns {Promise<Array>} Cart items
   */
  getItems: async () => {
    const sessionId = getSessionId();
    const response = await api.get(API_ENDPOINTS.CART_SESSION(sessionId));
    return response.data;
  },

  /**
   * Add item to cart
   * @param {Object} item - Item data { product_id, quantity }
   * @returns {Promise<Object>} Created cart item
   */
  addItem: async (item) => {
    const sessionId = getSessionId();
    const response = await api.post(API_ENDPOINTS.CART, {
      ...item,
      session_id: sessionId,
    });
    return response.data;
  },

  /**
   * Update item quantity
   * @param {string} itemId - Cart item ID
   * @param {number} quantity - New quantity
   * @returns {Promise<Object>} Updated cart item
   */
  updateQuantity: async (itemId, quantity) => {
    const response = await api.put(API_ENDPOINTS.CART_ITEM(itemId), { quantity });
    return response.data;
  },

  /**
   * Remove item from cart
   * @param {string} itemId - Cart item ID
   * @returns {Promise<void>}
   */
  removeItem: async (itemId) => {
    await api.delete(API_ENDPOINTS.CART_ITEM(itemId));
  },

  /**
   * Clear entire cart
   * @returns {Promise<void>}
   */
  clearCart: async () => {
    const sessionId = getSessionId();
    await api.delete(API_ENDPOINTS.CART_CLEAR(sessionId));
  },

  /**
   * Get cart count
   * @returns {Promise<number>} Total items count
   */
  getCount: async () => {
    const items = await CartService.getItems();
    return items.reduce((total, item) => total + (item.quantity || 1), 0);
  },

  /**
   * Get cart total price
   * @returns {Promise<number>} Total price
   */
  getTotal: async () => {
    const items = await CartService.getItems();
    return items.reduce((total, item) => total + (item.price * (item.quantity || 1)), 0);
  },
};

export default CartService;
