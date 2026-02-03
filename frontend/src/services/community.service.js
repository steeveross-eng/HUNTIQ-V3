/**
 * HUNTIQ V3 - Community Service
 * API service for community features (posts, leaderboard, etc.)
 * 
 * Note: Backend endpoints to be created. Currently using simulated data.
 */

import { api } from './api.client';

// Simulated community data
const MOCK_POSTS = [
  {
    id: '1',
    user: { name: 'Marc T.', avatar: 'https://i.pravatar.cc/100?img=1', badge: 'Expert' },
    image: 'https://images.unsplash.com/photo-1581971000802-30e846b262ed?w=400&h=400&fit=crop',
    caption: 'Premier orignal de la saison! Zone 17, 850 lbs 🦌',
    likes: 234,
    comments: 45,
    location: 'Laurentides, QC',
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    user: { name: 'Sophie L.', avatar: 'https://i.pravatar.cc/100?img=5', badge: 'Pro' },
    image: 'https://images.unsplash.com/photo-1484406566174-9da000fda645?w=400&h=400&fit=crop',
    caption: 'Magnifique buck 12 pointes. La patience paie!',
    likes: 456,
    comments: 78,
    location: 'Mauricie, QC',
    createdAt: new Date().toISOString(),
  },
  {
    id: '3',
    user: { name: 'Jean-Pierre B.', avatar: 'https://i.pravatar.cc/100?img=3', badge: null },
    image: 'https://images.unsplash.com/photo-1516934024742-b461fba47600?w=400&h=400&fit=crop',
    caption: 'Setup caméra trail parfait. 3 semaines de repérage.',
    likes: 189,
    comments: 32,
    location: 'Abitibi, QC',
    createdAt: new Date().toISOString(),
  },
  {
    id: '4',
    user: { name: 'Marie G.', avatar: 'https://i.pravatar.cc/100?img=9', badge: 'Guide' },
    image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop',
    caption: 'Lever de soleil sur mon territoire préféré ☀️',
    likes: 567,
    comments: 89,
    location: 'Saguenay, QC',
    createdAt: new Date().toISOString(),
  },
];

const MOCK_LEADERBOARD = [
  { rank: 1, name: 'PatrickChasseur', points: 15420, badge: 'crown' },
  { rank: 2, name: 'MarcOrignal', points: 12340, badge: 'medal' },
  { rank: 3, name: 'SophieHunt', points: 11890, badge: 'medal' },
  { rank: 4, name: 'JeanPierrePro', points: 9870, badge: null },
  { rank: 5, name: 'MarieLaurentides', points: 8540, badge: null },
];

export const CommunityService = {
  /**
   * Get community posts/photos
   * @param {Object} params - Pagination params
   * @returns {Promise<Array>} Posts list
   */
  getPosts: async (params = { limit: 10, offset: 0 }) => {
    // TODO: Replace with real API when backend is ready
    // const response = await api.get('/api/community/posts', params);
    // return response.data;
    
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_POSTS);
      }, 300);
    });
  },

  /**
   * Get leaderboard
   * @param {number} limit - Number of entries
   * @returns {Promise<Array>} Leaderboard entries
   */
  getLeaderboard: async (limit = 10) => {
    // TODO: Replace with real API when backend is ready
    // const response = await api.get('/api/community/leaderboard', { limit });
    // return response.data;
    
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_LEADERBOARD.slice(0, limit));
      }, 200);
    });
  },

  /**
   * Like a post
   * @param {string} postId - Post ID
   * @returns {Promise<Object>} Updated post
   */
  likePost: async (postId) => {
    // TODO: Implement when backend is ready
    return { success: true, postId };
  },

  /**
   * Comment on a post
   * @param {string} postId - Post ID
   * @param {string} comment - Comment text
   * @returns {Promise<Object>} Created comment
   */
  commentPost: async (postId, comment) => {
    // TODO: Implement when backend is ready
    return { success: true, postId, comment };
  },

  /**
   * Create a new post
   * @param {Object} post - Post data
   * @returns {Promise<Object>} Created post
   */
  createPost: async (post) => {
    // TODO: Implement when backend is ready
    return { success: true, ...post, id: Date.now().toString() };
  },

  /**
   * Get community stats
   * @returns {Promise<Object>} Community statistics
   */
  getStats: async () => {
    return {
      totalMembers: 12847,
      activeToday: 1247,
      postsThisWeek: 342,
      topRegion: 'Laurentides',
    };
  },
};

export default CommunityService;
