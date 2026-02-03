/**
 * HUNTIQ V3 - Services Index
 * Centralized export of all API services
 */

// Core API
export { default as apiClient, api } from './api.client';
export { API_CONFIG, API_ENDPOINTS } from './api.config';

// Domain Services
export { default as ProductsService } from './products.service';
export { default as CartService } from './cart.service';
export { default as AnalysisService } from './analysis.service';
export { default as TerritoryService } from './territory.service';
export { default as WeatherService } from './weather.service';
export { default as AdminService } from './admin.service';

// Community Services
export { default as CommunityService } from './community.service';
export { default as BlogService } from './blog.service';
export { default as PartnersService } from './partners.service';
export { default as NewsletterService } from './newsletter.service';

// Legacy Service (to be migrated)
export { default as WaterExclusionService } from './WaterExclusionService';
