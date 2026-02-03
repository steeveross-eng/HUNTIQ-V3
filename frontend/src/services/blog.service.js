/**
 * HUNTIQ V3 - Blog Service
 * API service for blog articles and SEO content
 * 
 * Note: Backend endpoints to be created. Currently using simulated data.
 */

import { api } from './api.client';

// Simulated blog articles
const MOCK_ARTICLES = [
  {
    id: '1',
    title: 'Guide complet: Préparer votre territoire pour la saison du rut',
    excerpt: 'Découvrez les meilleures stratégies pour maximiser vos chances pendant la période de reproduction du cerf de Virginie.',
    content: '',
    image: 'https://images.unsplash.com/photo-1484406566174-9da000fda645?w=800&h=400&fit=crop',
    author: { name: 'Jean-Pierre Tremblay', avatar: 'https://i.pravatar.cc/50?img=1' },
    date: '2025-11-28',
    readTime: '8 min',
    category: 'Stratégie',
    tags: ['rut', 'cerf', 'préparation', 'territoire'],
    views: 3421,
    comments: 45,
    featured: true,
    slug: 'guide-preparation-territoire-rut',
  },
  {
    id: '2',
    title: 'Les 10 erreurs à éviter avec les attractants',
    excerpt: 'Une analyse scientifique des erreurs les plus courantes et comment les éviter pour maximiser l\'efficacité.',
    content: '',
    image: 'https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=400&h=200&fit=crop',
    author: { name: 'Marie Gagnon', avatar: 'https://i.pravatar.cc/50?img=5' },
    date: '2025-11-25',
    readTime: '5 min',
    category: 'Analyse',
    tags: ['attractants', 'erreurs', 'conseils'],
    views: 2156,
    comments: 28,
    featured: false,
    slug: 'erreurs-attractants',
  },
  {
    id: '3',
    title: 'Météo et comportement: Comprendre le lien',
    excerpt: 'Comment la pression atmosphérique et les fronts météo influencent les déplacements du gibier.',
    content: '',
    image: 'https://images.unsplash.com/photo-1627891858448-0b99239685fa?w=400&h=200&fit=crop',
    author: { name: 'Marc Bouchard', avatar: 'https://i.pravatar.cc/50?img=3' },
    date: '2025-11-22',
    readTime: '6 min',
    category: 'Science',
    tags: ['météo', 'comportement', 'gibier', 'science'],
    views: 1834,
    comments: 19,
    featured: false,
    slug: 'meteo-comportement-gibier',
  },
  {
    id: '4',
    title: 'Nouveaux règlements 2026: Ce qui change',
    excerpt: 'Résumé des modifications réglementaires pour la prochaine saison de chasse au Québec.',
    content: '',
    image: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=200&fit=crop',
    author: { name: 'Sophie Lavoie', avatar: 'https://i.pravatar.cc/50?img=9' },
    date: '2025-11-20',
    readTime: '4 min',
    category: 'Réglementation',
    tags: ['règlements', '2026', 'québec'],
    views: 4521,
    comments: 67,
    featured: false,
    slug: 'reglements-2026-quebec',
  },
];

const CATEGORIES = ['Tous', 'Stratégie', 'Analyse', 'Science', 'Réglementation', 'Équipement', 'Territoire'];

export const BlogService = {
  /**
   * Get all articles
   * @param {Object} params - Filter/pagination params
   * @returns {Promise<Array>} Articles list
   */
  getArticles: async (params = {}) => {
    // TODO: Replace with real API when backend is ready
    // const response = await api.get('/api/blog/articles', params);
    // return response.data;
    
    return new Promise((resolve) => {
      setTimeout(() => {
        let articles = [...MOCK_ARTICLES];
        
        if (params.category && params.category !== 'Tous') {
          articles = articles.filter(a => a.category === params.category);
        }
        
        if (params.featured) {
          articles = articles.filter(a => a.featured);
        }
        
        if (params.limit) {
          articles = articles.slice(0, params.limit);
        }
        
        resolve(articles);
      }, 300);
    });
  },

  /**
   * Get featured article
   * @returns {Promise<Object>} Featured article
   */
  getFeaturedArticle: async () => {
    const articles = await BlogService.getArticles({ featured: true, limit: 1 });
    return articles[0] || null;
  },

  /**
   * Get article by slug
   * @param {string} slug - Article slug
   * @returns {Promise<Object>} Article data
   */
  getBySlug: async (slug) => {
    // TODO: Replace with real API
    return new Promise((resolve) => {
      setTimeout(() => {
        const article = MOCK_ARTICLES.find(a => a.slug === slug);
        resolve(article || null);
      }, 200);
    });
  },

  /**
   * Get article by ID
   * @param {string} id - Article ID
   * @returns {Promise<Object>} Article data
   */
  getById: async (id) => {
    // TODO: Replace with real API
    return new Promise((resolve) => {
      setTimeout(() => {
        const article = MOCK_ARTICLES.find(a => a.id === id);
        resolve(article || null);
      }, 200);
    });
  },

  /**
   * Get blog categories
   * @returns {Promise<Array>} Categories list
   */
  getCategories: async () => {
    return CATEGORIES;
  },

  /**
   * Get related articles
   * @param {string} articleId - Current article ID
   * @param {number} limit - Number of related articles
   * @returns {Promise<Array>} Related articles
   */
  getRelated: async (articleId, limit = 3) => {
    const current = MOCK_ARTICLES.find(a => a.id === articleId);
    if (!current) return [];
    
    return MOCK_ARTICLES
      .filter(a => a.id !== articleId && a.category === current.category)
      .slice(0, limit);
  },

  /**
   * Search articles
   * @param {string} query - Search query
   * @returns {Promise<Array>} Search results
   */
  search: async (query) => {
    const q = query.toLowerCase();
    return MOCK_ARTICLES.filter(a => 
      a.title.toLowerCase().includes(q) ||
      a.excerpt.toLowerCase().includes(q) ||
      a.tags.some(tag => tag.toLowerCase().includes(q))
    );
  },

  /**
   * Get popular articles
   * @param {number} limit - Number of articles
   * @returns {Promise<Array>} Popular articles
   */
  getPopular: async (limit = 5) => {
    return [...MOCK_ARTICLES]
      .sort((a, b) => b.views - a.views)
      .slice(0, limit);
  },
};

export default BlogService;
