/**
 * BIONIC™ Current Conditions Panel
 * =================================
 * Panneau indépendant affichant les conditions actuelles pour la chasse.
 * 
 * Features:
 * - Phase lunaire (nom + pourcentage + tendance)
 * - Pression barométrique (valeur + tendance)
 * - Température actuelle
 * - Photopériode (lever/coucher + durée du jour)
 * - Impact direct sur l'activité faunique
 * 
 * Module 100% indépendant - Alimenté par BehaviorWeatherFetcher
 * Compatible futur cache L3 (Redis) et export PDF
 * 
 * @version 1.0.0
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Moon, 
  Thermometer, 
  Wind, 
  Sunrise, 
  Sunset, 
  Gauge, 
  Target,
  RefreshCw,
  Download,
  CloudSun
} from 'lucide-react';

// API Base URL
const API_URL = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Hook personnalisé pour récupérer les conditions actuelles
 */
export const useCurrentConditions = (lat, lon, autoRefresh = false, refreshInterval = 300000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchConditions = useCallback(async () => {
    if (!lat || !lon) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_URL}/api/bionic/conditions/current?lat=${lat}&lon=${lon}&use_cache=true`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
      console.error('Current conditions fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [lat, lon]);

  // Initial fetch
  useEffect(() => {
    fetchConditions();
  }, [fetchConditions]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(fetchConditions, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchConditions]);

  return { data, loading, error, lastUpdated, refresh: fetchConditions };
};

/**
 * Composant Indicateur de Score
 */
const ScoreIndicator = ({ score, level, icon, size = 'lg' }) => {
  const getColorClass = () => {
    if (score >= 75) return 'from-emerald-500 to-green-600';
    if (score >= 55) return 'from-green-500 to-lime-500';
    if (score >= 35) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-rose-600';
  };

  const sizeClasses = {
    sm: 'w-16 h-16 text-lg',
    md: 'w-20 h-20 text-xl',
    lg: 'w-24 h-24 text-2xl'
  };

  return (
    <div className="flex flex-col items-center">
      <div 
        className={`${sizeClasses[size]} rounded-full bg-gradient-to-br ${getColorClass()} 
                    flex items-center justify-center shadow-lg`}
      >
        <span className="text-white font-bold">{Math.round(score)}</span>
      </div>
      <span className="mt-2 text-2xl">{icon}</span>
    </div>
  );
};

/**
 * Composant Condition Card
 */
const ConditionCard = ({ icon: Icon, title, children, className = '' }) => (
  <div className={`bg-slate-800/50 rounded-lg p-3 border border-slate-700/50 ${className}`}>
    <div className="flex items-center gap-2 mb-2">
      <Icon className="w-4 h-4 text-amber-400" />
      <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
    </div>
    <div className="space-y-1">
      {children}
    </div>
  </div>
);

/**
 * Composant Phase Lunaire
 */
const LunarPhase = ({ lunar }) => {
  const getMoonIcon = () => {
    if (lunar.is_new_moon) return '🌑';
    if (lunar.is_full_moon) return '🌕';
    if (lunar.is_waxing) {
      if (lunar.illumination_percent < 25) return '🌒';
      if (lunar.illumination_percent < 50) return '🌓';
      return '🌔';
    } else {
      if (lunar.illumination_percent > 75) return '🌖';
      if (lunar.illumination_percent > 50) return '🌗';
      return '🌘';
    }
  };

  const getImpactColor = () => {
    if (lunar.hunting_impact === 'favorable') return 'text-green-400';
    if (lunar.hunting_impact === 'mixed') return 'text-yellow-400';
    return 'text-slate-400';
  };

  return (
    <ConditionCard icon={Moon} title="Phase Lunaire">
      <div className="flex items-center gap-3">
        <span className="text-3xl">{getMoonIcon()}</span>
        <div>
          <p className="text-white font-semibold">{lunar.phase_name}</p>
          <p className="text-sm text-slate-400">{lunar.illumination_percent.toFixed(0)}% illumination</p>
        </div>
      </div>
      <div className="mt-2 text-xs text-slate-500">
        {lunar.next_event_name} dans {Math.round(lunar.days_to_next_event)} jours
      </div>
      <div className={`mt-1 text-xs ${getImpactColor()}`}>
        {lunar.hunting_description}
      </div>
    </ConditionCard>
  );
};

/**
 * Composant Pression Barométrique
 */
const PressureCard = ({ pressure }) => {
  const getTrendColor = () => {
    if (pressure.trend.includes('rising')) return 'text-green-400';
    if (pressure.trend.includes('falling')) return 'text-red-400';
    return 'text-slate-400';
  };

  const getTrendBg = () => {
    if (pressure.trend === 'rising_fast') return 'bg-green-500/20 text-green-400';
    if (pressure.trend === 'rising') return 'bg-green-500/10 text-green-400';
    if (pressure.trend === 'falling_fast') return 'bg-red-500/20 text-red-400';
    if (pressure.trend === 'falling') return 'bg-red-500/10 text-red-400';
    return 'bg-slate-500/20 text-slate-400';
  };

  return (
    <ConditionCard icon={Gauge} title="Pression">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-white font-semibold text-lg">{pressure.value_hpa.toFixed(1)} hPa</p>
          <Badge className={`${getTrendBg()} text-xs`}>
            {pressure.trend_icon} {pressure.trend.replace('_', ' ')}
          </Badge>
        </div>
        <div className={`text-2xl ${getTrendColor()}`}>
          {pressure.trend_icon}
        </div>
      </div>
      {pressure.change_6h !== 0 && (
        <p className="text-xs text-slate-500 mt-1">
          {pressure.change_6h > 0 ? '+' : ''}{pressure.change_6h.toFixed(1)} hPa / 6h
        </p>
      )}
      <p className="text-xs text-slate-400 mt-1">{pressure.hunting_description}</p>
    </ConditionCard>
  );
};

/**
 * Composant Météo
 */
const WeatherCard = ({ weather }) => {
  const getTempColor = () => {
    if (weather.temperature_c < 0) return 'text-blue-400';
    if (weather.temperature_c < 10) return 'text-cyan-400';
    if (weather.temperature_c < 20) return 'text-green-400';
    if (weather.temperature_c < 30) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <ConditionCard icon={Thermometer} title="Météo">
      <div className="flex items-center gap-3">
        <span className="text-3xl">{weather.weather_icon}</span>
        <div>
          <p className={`text-2xl font-bold ${getTempColor()}`}>
            {weather.temperature_c.toFixed(1)}°C
          </p>
          <p className="text-xs text-slate-400">{weather.weather_description}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mt-2 text-xs text-slate-400">
        <div className="flex items-center gap-1">
          <Wind className="w-3 h-3" />
          <span>{weather.wind_speed_kmh.toFixed(0)} km/h</span>
        </div>
        <div className="flex items-center gap-1">
          <CloudSun className="w-3 h-3" />
          <span>{weather.cloud_cover_percent}%</span>
        </div>
      </div>
    </ConditionCard>
  );
};

/**
 * Composant Photopériode
 */
const PhotoperiodCard = ({ photoperiod }) => (
  <ConditionCard icon={Sunrise} title="Photopériode">
    <div className="grid grid-cols-2 gap-3">
      <div className="flex items-center gap-2">
        <Sunrise className="w-4 h-4 text-amber-400" />
        <div>
          <p className="text-white font-semibold">{photoperiod.sunrise}</p>
          <p className="text-xs text-slate-500">Lever</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Sunset className="w-4 h-4 text-orange-400" />
        <div>
          <p className="text-white font-semibold">{photoperiod.sunset}</p>
          <p className="text-xs text-slate-500">Coucher</p>
        </div>
      </div>
    </div>
    <div className="mt-2 pt-2 border-t border-slate-700">
      <p className="text-sm text-slate-400">
        ☀️ <span className="text-white font-medium">{photoperiod.daylight_hours.toFixed(1)}h</span> de jour
      </p>
      <p className="text-xs text-slate-500 mt-1">
        🌅 Heures dorées: {photoperiod.golden_hour_morning} / {photoperiod.golden_hour_evening}
      </p>
    </div>
  </ConditionCard>
);

/**
 * Composant Principal - CurrentConditionsPanel
 */
const CurrentConditionsPanel = ({ 
  lat, 
  lon, 
  autoRefresh = true,
  refreshInterval = 300000, // 5 minutes
  compact = false,
  onExport = null,
  className = ''
}) => {
  const { data, loading, error, lastUpdated, refresh } = useCurrentConditions(
    lat, lon, autoRefresh, refreshInterval
  );

  const handleExport = async () => {
    if (onExport) {
      onExport(data);
    } else {
      // Default: copy to clipboard
      try {
        await navigator.clipboard.writeText(data?.export_summary || '');
        alert('Résumé copié dans le presse-papier !');
      } catch (err) {
        console.error('Copy failed:', err);
      }
    }
  };

  if (error) {
    return (
      <Card className={`bg-slate-900/90 border-red-500/50 ${className}`}>
        <CardContent className="p-4 text-center">
          <p className="text-red-400">❌ Erreur: {error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            className="mt-2"
            onClick={refresh}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Réessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (loading && !data) {
    return (
      <Card className={`bg-slate-900/90 border-slate-700 ${className}`}>
        <CardContent className="p-6 text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-amber-400 mx-auto mb-2" />
          <p className="text-slate-400">Chargement des conditions...</p>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <Card className={`bg-slate-900/90 border-slate-700 backdrop-blur-sm ${className}`} data-testid="current-conditions-panel">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-amber-400" />
            Conditions Actuelles
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={refresh}
              disabled={loading}
              className="text-slate-400 hover:text-white"
              data-testid="refresh-conditions-btn"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExport}
              className="text-slate-400 hover:text-white"
              data-testid="export-conditions-btn"
            >
              <Download className="w-4 h-4" />
            </Button>
          </div>
        </div>
        {lastUpdated && (
          <p className="text-xs text-slate-500">
            Mis à jour: {lastUpdated.toLocaleTimeString()} • {data.cache_status === 'hit' ? '⚡ Cache' : '🌐 Temps réel'}
          </p>
        )}
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Score Global d'Impact */}
        <div className="flex items-center justify-center py-4 border-b border-slate-700 mb-4">
          <div className="text-center">
            <ScoreIndicator 
              score={data.hunting_impact.score}
              level={data.hunting_impact.level}
              icon={data.hunting_impact.icon}
              size={compact ? 'md' : 'lg'}
            />
            <p className="mt-2 text-sm font-medium text-white">{data.hunting_impact.summary}</p>
            <Badge 
              className={`mt-1 ${
                data.hunting_impact.level === 'excellent' ? 'bg-green-500/20 text-green-400' :
                data.hunting_impact.level === 'good' ? 'bg-lime-500/20 text-lime-400' :
                data.hunting_impact.level === 'moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}
            >
              {data.hunting_impact.level.toUpperCase()}
            </Badge>
          </div>
        </div>

        {/* Grille des Conditions */}
        <div className={`grid ${compact ? 'grid-cols-2' : 'grid-cols-2 lg:grid-cols-4'} gap-3`}>
          <LunarPhase lunar={data.lunar} />
          <PressureCard pressure={data.pressure} />
          <WeatherCard weather={data.weather} />
          <PhotoperiodCard photoperiod={data.photoperiod} />
        </div>

        {/* Source des données */}
        <div className="mt-4 pt-3 border-t border-slate-700 text-center">
          <p className="text-xs text-slate-500">
            📡 {data.data_source}
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default CurrentConditionsPanel;
