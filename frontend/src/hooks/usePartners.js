/**
 * HUNTIQ V3 - usePartners Hook
 * Hook for partners and pourvoiries
 */

import { useState, useEffect, useCallback } from 'react';
import { PartnersService } from '@/services';

export const usePartners = () => {
  const [partners, setPartners] = useState([]);
  const [pourvoiries, setPourvoiries] = useState([]);
  const [featuredPourvoiries, setFeaturedPourvoiries] = useState([]);
  const [stats, setStats] = useState(null);
  const [regions, setRegions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch partners
  const fetchPartners = useCallback(async (params = {}) => {
    try {
      const data = await PartnersService.getPartners(params);
      setPartners(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  }, []);

  // Fetch pourvoiries
  const fetchPourvoiries = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const data = await PartnersService.getPourvoiries(params);
      setPourvoiries(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch featured pourvoiries
  const fetchFeatured = useCallback(async (limit = 3) => {
    try {
      const data = await PartnersService.getFeaturedPourvoiries(limit);
      setFeaturedPourvoiries(data);
      return data;
    } catch (err) {
      console.error('Featured pourvoiries error:', err);
      return [];
    }
  }, []);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const data = await PartnersService.getStats();
      setStats(data);
      return data;
    } catch (err) {
      console.error('Stats error:', err);
      return null;
    }
  }, []);

  // Fetch regions
  const fetchRegions = useCallback(async () => {
    try {
      const data = await PartnersService.getRegions();
      setRegions(data);
      return data;
    } catch (err) {
      return [];
    }
  }, []);

  // Filter by region
  const filterByRegion = useCallback(async (region) => {
    await fetchPourvoiries({ region });
  }, [fetchPourvoiries]);

  // Get pourvoirie by ID
  const getPourvoirie = useCallback(async (id) => {
    try {
      return await PartnersService.getPourvoirieById(id);
    } catch (err) {
      setError(err.message);
      return null;
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchPartners();
    fetchPourvoiries();
    fetchFeatured();
    fetchStats();
    fetchRegions();
  }, [fetchPartners, fetchPourvoiries, fetchFeatured, fetchStats, fetchRegions]);

  return {
    partners,
    pourvoiries,
    featuredPourvoiries,
    stats,
    regions,
    loading,
    error,
    fetchPartners,
    fetchPourvoiries,
    fetchFeatured,
    filterByRegion,
    getPourvoirie,
    refetch: () => {
      fetchPartners();
      fetchPourvoiries();
      fetchFeatured();
    },
  };
};

export default usePartners;
