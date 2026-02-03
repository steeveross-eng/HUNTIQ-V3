/**
 * HUNTIQ V3 - API Client
 * Centralized HTTP client with error handling
 */

import axios from 'axios';
import { API_CONFIG } from './api.config';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: API_CONFIG.headers,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add session ID for cart operations
    const sessionId = localStorage.getItem('session_id');
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Handle unauthorized
          localStorage.removeItem('auth_token');
          break;
        case 503:
          // Handle maintenance mode
          console.warn('Service en maintenance');
          break;
        default:
          break;
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Generic API methods
 */
export const api = {
  get: (url, params = {}) => apiClient.get(url, { params }),
  post: (url, data = {}) => apiClient.post(url, data),
  put: (url, data = {}) => apiClient.put(url, data),
  patch: (url, data = {}) => apiClient.patch(url, data),
  delete: (url) => apiClient.delete(url),
};

export default apiClient;
