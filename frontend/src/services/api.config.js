/**
 * HUNTIQ V3 - API Configuration
 * Base configuration for all API services
 */

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

export const API_ENDPOINTS = {
  // Products
  PRODUCTS: '/api/products',
  PRODUCTS_TOP: '/api/products/top',
  PRODUCTS_SEARCH: '/api/products/search',
  PRODUCTS_FILTER: '/api/products/filter',
  PRODUCTS_BRANDS: '/api/products/brands',
  PRODUCTS_CATEGORIES: '/api/products/categories',
  PRODUCTS_FILTERS_OPTIONS: '/api/products/filters/options',
  
  // Cart
  CART: '/api/cart',
  CART_SESSION: (sessionId) => `/api/cart/${sessionId}`,
  CART_ITEM: (itemId) => `/api/cart/${itemId}`,
  CART_CLEAR: (sessionId) => `/api/cart/session/${sessionId}`,
  
  // Analysis
  ANALYZE: '/api/analyze',
  ANALYZE_AI: '/api/analyze/ai-advanced',
  ANALYZE_CRITERIA: '/api/analyze/criteria',
  ANALYZE_CATEGORIES: '/api/analyze/categories',
  ANALYZE_REFERENCES: '/api/analyze/references',
  ANALYZE_BIONIC_PRODUCTS: '/api/analyze/bionic-products',
  ANALYZE_COMPETITORS: (category) => `/api/analyze/competitors/${category}`,
  ANALYZE_INGREDIENTS: '/api/analyze/ingredients',
  ANALYZE_REPORTS: '/api/analyze/reports',
  
  // Territory
  TERRITORY_CATEGORIES: '/api/territory/categories',
  TERRITORY_SPECIES_RULES: '/api/territory/species-rules',
  TERRITORY_PROBABILITY: '/api/territory/probability',
  TERRITORY_HEATMAP: '/api/territory/heatmap',
  TERRITORY_ACTION_PLAN: '/api/territory/action-plan',
  TERRITORY_ACTION_PLANS: '/api/territory/action-plans',
  TERRITORY_CAMERAS: '/api/territory/cameras',
  TERRITORY_EVENTS: '/api/territory/events',
  TERRITORY_CLASSIFY_PHOTO: '/api/territory/classify-photo',
  
  // Orders
  ORDERS: '/api/orders',
  ORDER: (orderId) => `/api/orders/${orderId}`,
  ORDER_CANCEL: (orderId) => `/api/orders/${orderId}/cancel`,
  
  // Customers
  CUSTOMERS: '/api/customers',
  CUSTOMER: (customerId) => `/api/customers/${customerId}`,
  
  // Suppliers
  SUPPLIERS: '/api/suppliers',
  SUPPLIER: (supplierId) => `/api/suppliers/${supplierId}`,
  
  // Referral
  REFERRAL_CALCULATE: '/api/referral/calculate-discount',
  REFERRAL_APPLY_PARTNER: '/api/referral/apply-partner',
  REFERRAL_ADMIN_TIERS: '/api/referral/admin/tiers',
  REFERRAL_ADMIN_PROMOTIONS: '/api/referral/admin/promotions',
  REFERRAL_ADMIN_PARTNERS: '/api/referral/admin/partners',
  REFERRAL_ADMIN_DASHBOARD: '/api/referral/admin/dashboard',
  
  // Affiliate
  AFFILIATE_CLICK: '/api/affiliate/click',
  AFFILIATE_CLICKS: '/api/affiliate/clicks',
  AFFILIATE_CONFIRM: (clickId) => `/api/affiliate/confirm/${clickId}`,
  
  // Commissions
  COMMISSIONS: '/api/commissions',
  COMMISSION_PAY: (commissionId) => `/api/commissions/${commissionId}/pay`,
  
  // Admin
  ADMIN_LOGIN: '/api/admin/login',
  ADMIN_STATS: '/api/admin/stats',
  ADMIN_PRODUCTS: '/api/admin/products',
  ADMIN_PRODUCT: (productId) => `/api/admin/products/${productId}`,
  ADMIN_REPORTS_SALES: '/api/admin/reports/sales',
  ADMIN_REPORTS_PRODUCTS: '/api/admin/reports/products',
  ADMIN_REPORTS_SUPPLIERS: '/api/admin/reports/suppliers',
  ADMIN_REPORTS_COMMISSIONS: '/api/admin/reports/commissions',
  ADMIN_ALERTS: '/api/admin/alerts',
  ADMIN_SITE_SETTINGS: '/api/admin/site-settings',
  
  // Site
  SITE_STATUS: '/api/site/status',
  
  // Scheduler
  SCHEDULER_STATUS: '/api/scheduler/status',
  SCHEDULER_SCAN_SCHEDULE: '/api/scheduler/scan/schedule',
  SCHEDULER_SCAN_RUN: '/api/scheduler/scan/run-now',
  SCHEDULER_SCAN_HISTORY: '/api/scheduler/scan/history',
  
  // Email
  EMAIL_STATUS: '/api/email/status',
  
  // Seed
  SEED: '/api/seed',
  
  // Geospatial Engine
  GEOSPATIAL_STATUS: '/api/geospatial/status',
  GEOSPATIAL_DATA_SOURCES: '/api/geospatial/data-sources',
  GEOSPATIAL_LIDAR_QUERY: '/api/geospatial/lidar/query',
  GEOSPATIAL_LIDAR_COVERAGE: '/api/geospatial/lidar/coverage',
  GEOSPATIAL_SENTINEL_QUERY: '/api/geospatial/sentinel/query',
  GEOSPATIAL_SENTINEL_SCENES: '/api/geospatial/sentinel/scenes',
  GEOSPATIAL_SIGEOM_QUERY: '/api/geospatial/sigeom/query',
  GEOSPATIAL_HYDRO_QUERY: '/api/geospatial/hydro/query',
  GEOSPATIAL_HYDRO_RIVERS: '/api/geospatial/hydro/rivers',
  GEOSPATIAL_HYDRO_LAKES: '/api/geospatial/hydro/lakes',
  GEOSPATIAL_HYDRO_WETLANDS: '/api/geospatial/hydro/wetlands',
  GEOSPATIAL_FOREST_QUERY: '/api/geospatial/forest/query',
  GEOSPATIAL_FOREST_SPECIES: '/api/geospatial/forest/species',
  GEOSPATIAL_GEOMORPH_ANALYZE: '/api/geospatial/geomorph/analyze',
  GEOSPATIAL_AI_PREDICT: '/api/geospatial/ai/predict',
  GEOSPATIAL_AI_CORRIDORS: '/api/geospatial/ai/corridors',
  GEOSPATIAL_POTENTIAL_CALCULATE: '/api/geospatial/potential/calculate',
  GEOSPATIAL_POTENTIAL_HOTSPOTS: '/api/geospatial/potential/hotspots',
  GEOSPATIAL_POTENTIAL_STAND_LOCATIONS: '/api/geospatial/potential/stand-locations',
  GEOSPATIAL_POTENTIAL_COMPONENTS: '/api/geospatial/potential/components',
  
  // Weather endpoints
  GEOSPATIAL_WEATHER_CURRENT: '/api/geospatial/weather/current',
  GEOSPATIAL_WEATHER_FORECAST: '/api/geospatial/weather/forecast',
  GEOSPATIAL_WEATHER_HUNTING_SCORE: '/api/geospatial/weather/hunting-score',
  
  // Nutrition endpoints
  GEOSPATIAL_NUTRITION_SPECIES: '/api/geospatial/nutrition/species',
  GEOSPATIAL_NUTRITION_ANALYZE: '/api/geospatial/nutrition/full-analysis',
  GEOSPATIAL_MODULES: '/api/geospatial/modules',
};

export default API_CONFIG;
