/**
 * HUNTIQ V3 - useCommunity Hook
 * Hook for community features
 */

import { useState, useEffect, useCallback } from 'react';
import { CommunityService } from '@/services';

export const useCommunity = () => {
  const [posts, setPosts] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch posts
  const fetchPosts = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const data = await CommunityService.getPosts(params);
      setPosts(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch leaderboard
  const fetchLeaderboard = useCallback(async (limit = 10) => {
    try {
      const data = await CommunityService.getLeaderboard(limit);
      setLeaderboard(data);
      return data;
    } catch (err) {
      console.error('Leaderboard error:', err);
      return [];
    }
  }, []);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const data = await CommunityService.getStats();
      setStats(data);
      return data;
    } catch (err) {
      console.error('Stats error:', err);
      return null;
    }
  }, []);

  // Like post
  const likePost = useCallback(async (postId) => {
    try {
      await CommunityService.likePost(postId);
      // Update local state
      setPosts(prev => prev.map(p => 
        p.id === postId ? { ...p, likes: p.likes + 1 } : p
      ));
      return true;
    } catch (err) {
      return false;
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchPosts();
    fetchLeaderboard();
    fetchStats();
  }, [fetchPosts, fetchLeaderboard, fetchStats]);

  return {
    posts,
    leaderboard,
    stats,
    loading,
    error,
    fetchPosts,
    fetchLeaderboard,
    fetchStats,
    likePost,
    refetch: () => {
      fetchPosts();
      fetchLeaderboard();
      fetchStats();
    },
  };
};

export default useCommunity;
