/**
 * BIONIC™ Stats Engine - Hook
 * 
 * Gère:
 * - Récupération API avec fallback
 * - Seuils de valeurs minimales
 * - Animation progressive (count-up)
 * - Valeurs formatées pour affichage
 */

import { useEffect, useState, useCallback, useRef } from "react";
import { api } from "@/services/api.client";

/**
 * Hook principal du Stats Engine
 * @param {Object} config - Configuration du hook
 * @param {string} config.apiUrl - URL de l'API stats
 * @param {number} config.subscriberThreshold - Seuil minimum pour afficher le vrai nombre d'abonnés
 * @param {number} config.zonesThreshold - Seuil minimum pour afficher le vrai nombre de zones
 * @param {number} config.animationDuration - Durée de l'animation en ms
 * @param {number} config.refreshInterval - Intervalle de rafraîchissement en ms (0 = pas de refresh)
 */
export function useStatsEngine({
  apiUrl = "/api/stats",
  subscriberThreshold = 20017,
  zonesThreshold = 2901,
  animationDuration = 1200,
  refreshInterval = 60000, // Refresh toutes les minutes
} = {}) {
  // Stats brutes depuis l'API
  const [stats, setStats] = useState({
    subscribers: 0,
    territories: 2547,
    attractants: 850,
    zones: 0,
    satisfaction: 98,
    activeUsers: 0,
    totalProducts: 0,
  });

  // Valeurs animées
  const [animated, setAnimated] = useState({
    subscribers: 0,
    zones: 0,
    territories: 0,
    activeUsers: 0,
  });

  // États
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const animationRef = useRef(null);

  // Animation progressive (count-up)
  const animateValue = useCallback((start, target, key, duration = animationDuration) => {
    const startTime = performance.now();

    function step(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-out-cubic)
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.floor(start + (target - start) * eased);
      
      setAnimated(prev => ({ ...prev, [key]: value }));
      
      if (progress < 1) {
        animationRef.current = requestAnimationFrame(step);
      }
    }

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    
    requestAnimationFrame(step);
  }, [animationDuration]);

  // Fetch des stats depuis l'API
  const fetchStats = useCallback(async () => {
    try {
      const response = await api.get(apiUrl);
      const data = response.data;
      
      setStats(prev => ({ ...prev, ...data }));
      setError(null);
      
      // Lancer les animations pour les nouvelles valeurs
      if (data.subscribers !== undefined) {
        animateValue(0, data.subscribers, 'subscribers');
      }
      if (data.zones !== undefined) {
        animateValue(0, data.zones, 'zones');
      }
      if (data.territories !== undefined) {
        animateValue(0, data.territories, 'territories');
      }
      if (data.activeUsers !== undefined) {
        animateValue(0, data.activeUsers, 'activeUsers');
      }
      
    } catch (err) {
      console.warn("Stats API unreachable, using fallback values.", err);
      setError("API indisponible");
      
      // Utiliser les valeurs par défaut et animer
      animateValue(0, 20017, 'subscribers');
      animateValue(0, 2901, 'zones');
      animateValue(0, 2547, 'territories');
      animateValue(0, 1247, 'activeUsers');
    } finally {
      setLoading(false);
    }
  }, [apiUrl, animateValue]);

  // Fetch initial et refresh périodique
  useEffect(() => {
    fetchStats();

    if (refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchStats, refreshInterval]);

  // Cleanup des animations
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Valeurs affichées avec logique de seuil
  const displayedSubscribers = stats.subscribers < subscriberThreshold
    ? "20K+"
    : animated.subscribers.toLocaleString("fr-CA");

  const displayedZones = stats.zones < zonesThreshold
    ? "2,901+"
    : animated.zones.toLocaleString("fr-CA");

  const displayedTerritories = animated.territories > 0
    ? animated.territories.toLocaleString("fr-CA") + "+"
    : "2,547+";

  const displayedActiveUsers = animated.activeUsers > 0
    ? animated.activeUsers.toLocaleString("fr-CA")
    : "1,247";

  return {
    // Valeurs affichées (formatées avec seuils)
    displayedSubscribers,
    displayedZones,
    displayedTerritories,
    displayedActiveUsers,
    
    // Valeurs brutes
    rawStats: stats,
    territories: stats.territories,
    attractants: stats.attractants,
    satisfaction: stats.satisfaction,
    
    // États
    loading,
    error,
    
    // Actions
    refresh: fetchStats,
  };
}

export default useStatsEngine;
