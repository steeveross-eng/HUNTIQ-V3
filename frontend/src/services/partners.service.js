/**
 * HUNTIQ V3 - Partners Service
 * API service for partners and pourvoiries
 * 
 * Note: Backend endpoints to be created. Currently using simulated data.
 */

import { api } from './api.client';

// Simulated partners data
const MOCK_PARTNERS = [
  { id: '1', name: 'FédéCP', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=FédéCP', type: 'Institution', url: 'https://fedecp.com' },
  { id: '2', name: 'SÉPAQ', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=SÉPAQ', type: 'Institution', url: 'https://sepaq.com' },
  { id: '3', name: 'Buck Bomb', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=BuckBomb', type: 'Marque', url: '#' },
  { id: '4', name: 'Tink\'s', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=Tinks', type: 'Marque', url: '#' },
  { id: '5', name: 'Code Blue', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=CodeBlue', type: 'Marque', url: '#' },
  { id: '6', name: 'Wildlife Research', logo: 'https://via.placeholder.com/120x60/1a1a1a/f5a623?text=WRC', type: 'Marque', url: '#' },
];

const MOCK_POURVOIRIES = [
  {
    id: '1',
    name: 'Pourvoirie du Lac Blanc',
    location: 'Zone 10 - Mauricie',
    region: 'Mauricie',
    zone: '10',
    rating: 4.9,
    reviews: 156,
    image: 'https://images.unsplash.com/photo-1510797215324-95aa89f43c33?w=400&h=200&fit=crop',
    verified: true,
    features: ['Orignal', 'Ours', 'Hébergement'],
    description: 'Pourvoirie familiale avec 50 ans d\'expérience.',
    contact: { phone: '819-555-0100', email: 'info@lacblanc.com' },
    coordinates: { lat: 46.8, lon: -73.2 },
  },
  {
    id: '2',
    name: 'Domaine Chasseur',
    location: 'Zone 14 - Laurentides',
    region: 'Laurentides',
    zone: '14',
    rating: 4.8,
    reviews: 98,
    image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=200&fit=crop',
    verified: true,
    features: ['Cerf', 'Dindon', 'Guidage'],
    description: 'Spécialisée dans la chasse au cerf de Virginie.',
    contact: { phone: '450-555-0200', email: 'info@domainechasseur.com' },
    coordinates: { lat: 46.2, lon: -74.5 },
  },
  {
    id: '3',
    name: 'Pourvoirie Nature Sauvage',
    location: 'Zone 17 - Abitibi',
    region: 'Abitibi',
    zone: '17',
    rating: 4.7,
    reviews: 72,
    image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=200&fit=crop',
    verified: true,
    features: ['Orignal', 'Petit gibier', 'Tout inclus'],
    description: 'Territoire sauvage de 500 km² en Abitibi.',
    contact: { phone: '819-555-0300', email: 'info@naturesauvage.com' },
    coordinates: { lat: 48.5, lon: -78.0 },
  },
];

export const PartnersService = {
  /**
   * Get all partners
   * @param {Object} params - Filter params
   * @returns {Promise<Array>} Partners list
   */
  getPartners: async (params = {}) => {
    // TODO: Replace with real API when backend is ready
    return new Promise((resolve) => {
      setTimeout(() => {
        let partners = [...MOCK_PARTNERS];
        
        if (params.type) {
          partners = partners.filter(p => p.type === params.type);
        }
        
        resolve(partners);
      }, 200);
    });
  },

  /**
   * Get all pourvoiries
   * @param {Object} params - Filter params (region, zone, features)
   * @returns {Promise<Array>} Pourvoiries list
   */
  getPourvoiries: async (params = {}) => {
    // TODO: Replace with real API when backend is ready
    return new Promise((resolve) => {
      setTimeout(() => {
        let pourvoiries = [...MOCK_POURVOIRIES];
        
        if (params.region) {
          pourvoiries = pourvoiries.filter(p => p.region === params.region);
        }
        
        if (params.zone) {
          pourvoiries = pourvoiries.filter(p => p.zone === params.zone);
        }
        
        if (params.verified) {
          pourvoiries = pourvoiries.filter(p => p.verified);
        }
        
        if (params.limit) {
          pourvoiries = pourvoiries.slice(0, params.limit);
        }
        
        resolve(pourvoiries);
      }, 300);
    });
  },

  /**
   * Get pourvoirie by ID
   * @param {string} id - Pourvoirie ID
   * @returns {Promise<Object>} Pourvoirie data
   */
  getPourvoirieById: async (id) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const pourvoirie = MOCK_POURVOIRIES.find(p => p.id === id);
        resolve(pourvoirie || null);
      }, 200);
    });
  },

  /**
   * Get featured pourvoiries
   * @param {number} limit - Number of pourvoiries
   * @returns {Promise<Array>} Featured pourvoiries
   */
  getFeaturedPourvoiries: async (limit = 3) => {
    const pourvoiries = await PartnersService.getPourvoiries({ verified: true, limit });
    return pourvoiries.sort((a, b) => b.rating - a.rating);
  },

  /**
   * Get partners statistics
   * @returns {Promise<Object>} Statistics
   */
  getStats: async () => {
    return {
      totalPourvoiries: 156,
      totalZones: 29,
      satisfiedHunters: 12000,
      satisfactionRate: 98,
    };
  },

  /**
   * Get partner types
   * @returns {Promise<Array>} Partner types
   */
  getPartnerTypes: async () => {
    return ['Institution', 'Marque', 'Pourvoirie', 'Guide'];
  },

  /**
   * Get regions with pourvoiries
   * @returns {Promise<Array>} Regions list
   */
  getRegions: async () => {
    return ['Laurentides', 'Mauricie', 'Abitibi', 'Saguenay', 'Outaouais', 'Estrie', 'Lanaudière'];
  },
};

export default PartnersService;
