/**
 * HUNTIQ V3 - useProducts Hook
 * Hook for products data management
 */

import { useState, useEffect, useCallback } from 'react';
import { ProductsService } from '@/services';

export const useProducts = (options = {}) => {
  const [products, setProducts] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { autoFetch = true, limit = 10 } = options;

  // Fetch all products
  const fetchProducts = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await ProductsService.getAll(params);
      setProducts(data);
      return data;
    } catch (err) {
      setError(err.message || 'Erreur lors du chargement des produits');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch top products (for carousel)
  const fetchTopProducts = useCallback(async (count = limit) => {
    try {
      const data = await ProductsService.getTop(count);
      setTopProducts(data);
      return data;
    } catch (err) {
      console.error('Error fetching top products:', err);
      return [];
    }
  }, [limit]);

  // Search products
  const searchProducts = useCallback(async (query) => {
    setLoading(true);
    try {
      const data = await ProductsService.search({ query });
      setProducts(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Filter products
  const filterProducts = useCallback(async (filters) => {
    setLoading(true);
    try {
      const data = await ProductsService.filter(filters);
      setProducts(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Get product by ID
  const getProduct = useCallback(async (productId) => {
    try {
      return await ProductsService.getById(productId);
    } catch (err) {
      setError(err.message);
      return null;
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    if (autoFetch) {
      fetchProducts();
      fetchTopProducts();
    }
  }, [autoFetch, fetchProducts, fetchTopProducts]);

  return {
    products,
    topProducts,
    loading,
    error,
    fetchProducts,
    fetchTopProducts,
    searchProducts,
    filterProducts,
    getProduct,
    refetch: fetchProducts,
  };
};

export default useProducts;
