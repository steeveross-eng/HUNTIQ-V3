/**
 * HUNTIQ V3 - useBlog Hook
 * Hook for blog articles
 */

import { useState, useEffect, useCallback } from 'react';
import { BlogService } from '@/services';

export const useBlog = () => {
  const [articles, setArticles] = useState([]);
  const [featuredArticle, setFeaturedArticle] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('Tous');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch articles
  const fetchArticles = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const data = await BlogService.getArticles(params);
      setArticles(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch featured article
  const fetchFeatured = useCallback(async () => {
    try {
      const data = await BlogService.getFeaturedArticle();
      setFeaturedArticle(data);
      return data;
    } catch (err) {
      console.error('Featured article error:', err);
      return null;
    }
  }, []);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const data = await BlogService.getCategories();
      setCategories(data);
      return data;
    } catch (err) {
      console.error('Categories error:', err);
      return [];
    }
  }, []);

  // Filter by category
  const filterByCategory = useCallback(async (category) => {
    setSelectedCategory(category);
    await fetchArticles({ category });
  }, [fetchArticles]);

  // Search articles
  const searchArticles = useCallback(async (query) => {
    setLoading(true);
    try {
      const data = await BlogService.search(query);
      setArticles(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Get article by slug
  const getArticle = useCallback(async (slug) => {
    try {
      return await BlogService.getBySlug(slug);
    } catch (err) {
      setError(err.message);
      return null;
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchArticles();
    fetchFeatured();
    fetchCategories();
  }, [fetchArticles, fetchFeatured, fetchCategories]);

  return {
    articles,
    featuredArticle,
    categories,
    selectedCategory,
    loading,
    error,
    fetchArticles,
    fetchFeatured,
    filterByCategory,
    searchArticles,
    getArticle,
    refetch: () => {
      fetchArticles();
      fetchFeatured();
    },
  };
};

export default useBlog;
