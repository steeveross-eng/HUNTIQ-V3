/**
 * HUNTIQ V3 - useWeather Hook
 * Hook for weather and hunting conditions
 */

import { useState, useEffect, useCallback } from 'react';
import { WeatherService } from '@/services';

export const useWeather = (initialRegion = 'laurentides') => {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [region, setRegion] = useState(initialRegion);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch weather for region
  const fetchWeather = useCallback(async (regionKey = region) => {
    setLoading(true);
    setError(null);
    try {
      const data = await WeatherService.getRegionWeather(regionKey);
      setWeather(data);
      return data;
    } catch (err) {
      setError(err.message || 'Erreur lors du chargement météo');
      // Use simulated data as fallback
      const fallback = WeatherService.getSimulatedWeather();
      setWeather(fallback);
      return fallback;
    } finally {
      setLoading(false);
    }
  }, [region]);

  // Fetch 5-day forecast
  const fetchForecast = useCallback(async (regionKey = region) => {
    try {
      const data = await WeatherService.getForecast(regionKey);
      setForecast(data);
      return data;
    } catch (err) {
      console.error('Forecast error:', err);
      return [];
    }
  }, [region]);

  // Change region
  const changeRegion = useCallback(async (newRegion) => {
    setRegion(newRegion);
    await fetchWeather(newRegion);
    await fetchForecast(newRegion);
  }, [fetchWeather, fetchForecast]);

  // Get all available regions
  const getRegions = useCallback(() => {
    return WeatherService.getRegions();
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchWeather();
    fetchForecast();
  }, []);

  return {
    weather,
    forecast,
    region,
    regions: getRegions(),
    loading,
    error,
    fetchWeather,
    fetchForecast,
    changeRegion,
    huntingScore: weather?.hunting?.score || 0,
    huntingStatus: weather?.hunting?.status || 'N/A',
    huntingAdvice: weather?.hunting?.advice || '',
  };
};

export default useWeather;
