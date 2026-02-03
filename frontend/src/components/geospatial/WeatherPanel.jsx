/**
 * HUNTIQ V3 - BIONIC™ Weather Panel
 * Real-time weather data with hunting score
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Cloud, Sun, CloudRain, CloudSnow, Wind, Droplets, 
  Thermometer, Gauge, Target, Clock, RefreshCw, Loader2,
  AlertCircle, ChevronDown, ChevronUp, Sunrise, Sunset
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api.client';
import { API_ENDPOINTS } from '@/services/api.config';

// Weather condition icons
const WEATHER_ICONS = {
  Clear: Sun,
  Clouds: Cloud,
  Rain: CloudRain,
  Drizzle: CloudRain,
  Snow: CloudSnow,
  Thunderstorm: CloudRain,
  Mist: Cloud,
  Fog: Cloud,
  default: Cloud
};

// Score level colors
const SCORE_COLORS = {
  excellent: { bg: 'bg-green-500', text: 'text-green-400', border: 'border-green-500' },
  bon: { bg: 'bg-blue-500', text: 'text-blue-400', border: 'border-blue-500' },
  moyen: { bg: 'bg-yellow-500', text: 'text-yellow-400', border: 'border-yellow-500' },
  faible: { bg: 'bg-orange-500', text: 'text-orange-400', border: 'border-orange-500' },
  mauvais: { bg: 'bg-red-500', text: 'text-red-400', border: 'border-red-500' }
};

// Factor status indicator
const FactorIndicator = ({ factor }) => {
  const getStatusColor = (status) => {
    if (status.includes('optimal') || status.includes('calme') || status.includes('favorable')) {
      return 'text-green-400';
    }
    if (status.includes('acceptable') || status.includes('modéré') || status.includes('normale')) {
      return 'text-yellow-400';
    }
    return 'text-red-400';
  };

  const getImpactColor = (impact) => {
    if (impact > 0) return 'text-green-400';
    if (impact === 0) return 'text-gray-400';
    return 'text-red-400';
  };

  return (
    <div className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
      <span className="text-sm text-gray-300">{factor.factor}</span>
      <div className="flex items-center gap-2">
        <span className={`text-xs ${getStatusColor(factor.status)}`}>
          {factor.status}
        </span>
        <span className={`text-xs font-mono ${getImpactColor(factor.impact)}`}>
          {factor.impact > 0 ? '+' : ''}{factor.impact}
        </span>
      </div>
    </div>
  );
};

// Main Weather Panel Component
const WeatherPanel = ({ 
  latitude, 
  longitude, 
  compact = false,
  autoRefresh = true,
  refreshInterval = 300000 // 5 minutes
}) => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(!compact);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch weather data
  const fetchWeather = useCallback(async () => {
    if (!latitude || !longitude) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.get('/api/geospatial/weather/current', {
        lat: latitude,
        lon: longitude,
        units: 'metric'
      });

      if (response.data.status === 'success') {
        setWeather(response.data);
        setLastUpdate(new Date());
      } else {
        setError(response.data.message || 'Erreur de chargement');
      }
    } catch (err) {
      setError(err.message || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  }, [latitude, longitude]);

  // Initial fetch and auto-refresh
  useEffect(() => {
    fetchWeather();

    if (autoRefresh) {
      const interval = setInterval(fetchWeather, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchWeather, autoRefresh, refreshInterval]);

  // Get weather icon
  const WeatherIcon = weather?.weather?.condition 
    ? WEATHER_ICONS[weather.weather.condition] || WEATHER_ICONS.default
    : WEATHER_ICONS.default;

  // Get score colors
  const scoreColors = weather?.hunting_score?.level 
    ? SCORE_COLORS[weather.hunting_score.level] || SCORE_COLORS.moyen
    : SCORE_COLORS.moyen;

  return (
    <Card className="bg-[#1a1a1a] border-white/10 rounded-md overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#f5a623]/10 rounded-sm flex items-center justify-center">
              <WeatherIcon className="h-5 w-5 text-[#f5a623]" />
            </div>
            <div>
              <CardTitle className="text-lg text-white">Météo & Score</CardTitle>
              {weather?.location?.name && (
                <p className="text-xs text-gray-500">{weather.location.name}</p>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={fetchWeather}
              disabled={loading}
              className="h-8 w-8 p-0 text-gray-400 hover:text-white"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
            {!compact && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setExpanded(!expanded)}
                className="h-8 w-8 p-0 text-gray-400 hover:text-white"
              >
                {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-4">
        {/* Loading state */}
        {loading && !weather && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 text-[#f5a623] animate-spin" />
          </div>
        )}

        {/* Error state */}
        {error && !weather && (
          <div className="text-center py-6">
            <AlertCircle className="h-8 w-8 text-red-400 mx-auto mb-2" />
            <p className="text-red-400 text-sm">{error}</p>
            <Button
              onClick={fetchWeather}
              variant="outline"
              size="sm"
              className="mt-4 border-white/20 text-white"
            >
              Réessayer
            </Button>
          </div>
        )}

        {/* Weather data */}
        {weather && (
          <div className="space-y-4">
            {/* Main weather display */}
            <div className="flex items-center justify-between">
              {/* Temperature */}
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-white">
                    {weather.current?.temperature?.toFixed(0)}
                    <span className="text-xl text-gray-400">{weather.current?.temp_unit}</span>
                  </div>
                  <p className="text-sm text-gray-400 capitalize">
                    {weather.weather?.description}
                  </p>
                </div>
              </div>

              {/* Hunting score */}
              <div className="text-center">
                <div className="relative w-20 h-20">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="40"
                      cy="40"
                      r="36"
                      stroke="currentColor"
                      strokeWidth="6"
                      fill="none"
                      className="text-white/10"
                    />
                    <circle
                      cx="40"
                      cy="40"
                      r="36"
                      stroke="currentColor"
                      strokeWidth="6"
                      fill="none"
                      strokeDasharray={`${(weather.hunting_score?.score || 0) * 2.26} 226`}
                      strokeLinecap="round"
                      className={scoreColors.text}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <Target className={`h-4 w-4 ${scoreColors.text} mb-1`} />
                    <span className="text-xl font-bold text-white">
                      {weather.hunting_score?.score}
                    </span>
                  </div>
                </div>
                <Badge className={`mt-2 ${scoreColors.bg}/20 ${scoreColors.text} border ${scoreColors.border}/30`}>
                  {weather.hunting_score?.level}
                </Badge>
              </div>
            </div>

            {/* Quick stats */}
            <div className="grid grid-cols-4 gap-2">
              <div className="bg-black/40 rounded-sm p-2 text-center">
                <Thermometer className="h-4 w-4 text-orange-400 mx-auto mb-1" />
                <p className="text-xs text-gray-400">Ressenti</p>
                <p className="text-sm text-white font-medium">
                  {weather.current?.feels_like?.toFixed(0)}°
                </p>
              </div>
              <div className="bg-black/40 rounded-sm p-2 text-center">
                <Wind className="h-4 w-4 text-blue-400 mx-auto mb-1" />
                <p className="text-xs text-gray-400">Vent</p>
                <p className="text-sm text-white font-medium">
                  {weather.wind?.speed?.toFixed(0)} {weather.wind?.unit}
                </p>
              </div>
              <div className="bg-black/40 rounded-sm p-2 text-center">
                <Droplets className="h-4 w-4 text-cyan-400 mx-auto mb-1" />
                <p className="text-xs text-gray-400">Humidité</p>
                <p className="text-sm text-white font-medium">
                  {weather.current?.humidity}%
                </p>
              </div>
              <div className="bg-black/40 rounded-sm p-2 text-center">
                <Gauge className="h-4 w-4 text-purple-400 mx-auto mb-1" />
                <p className="text-xs text-gray-400">Pression</p>
                <p className="text-sm text-white font-medium">
                  {weather.current?.pressure} hPa
                </p>
              </div>
            </div>

            {/* Expanded content */}
            <AnimatePresence>
              {expanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="space-y-4"
                >
                  {/* Recommendation */}
                  <div className="p-3 bg-[#f5a623]/10 rounded-sm border border-[#f5a623]/20">
                    <p className="text-sm text-[#f5a623]">
                      {weather.hunting_score?.recommendation}
                    </p>
                  </div>

                  {/* Score factors */}
                  <div>
                    <h4 className="text-sm text-white font-semibold mb-2">Facteurs du score</h4>
                    <div className="bg-black/40 rounded-sm p-3">
                      {weather.hunting_score?.factors?.map((factor, i) => (
                        <FactorIndicator key={i} factor={factor} />
                      ))}
                    </div>
                  </div>

                  {/* Optimal hours */}
                  {weather.hunting_score?.optimal_hours?.length > 0 && (
                    <div>
                      <h4 className="text-sm text-white font-semibold mb-2 flex items-center gap-2">
                        <Clock className="h-4 w-4 text-[#f5a623]" />
                        Heures optimales
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {weather.hunting_score.optimal_hours.map((hour, i) => (
                          <Badge key={i} className="bg-white/5 text-gray-300 text-xs">
                            {hour}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sun times */}
                  {weather.sun?.sunrise && (
                    <div className="flex items-center justify-between text-xs text-gray-400">
                      <div className="flex items-center gap-2">
                        <Sunrise className="h-4 w-4 text-orange-400" />
                        <span>
                          {new Date(weather.sun.sunrise).toLocaleTimeString('fr-CA', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Sunset className="h-4 w-4 text-orange-600" />
                        <span>
                          {new Date(weather.sun.sunset).toLocaleTimeString('fr-CA', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </span>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Last update */}
            {lastUpdate && (
              <p className="text-xs text-gray-600 text-center">
                Mis à jour: {lastUpdate.toLocaleTimeString('fr-CA')}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WeatherPanel;
