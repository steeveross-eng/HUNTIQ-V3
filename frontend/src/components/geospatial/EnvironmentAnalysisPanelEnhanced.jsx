/**
 * HUNTIQ V3 - BIONIC™ Environment Analysis Panel (Enhanced)
 * 
 * Panneau d'affichage intégrant les moteurs:
 * - EnvironmentEngine: Score global combiné
 * - SentinelEngine: Analyse végétation Sentinel-2
 * - SigeomEngine: Analyse géologique SIGÉOM
 * 
 * Version: 2.0 (Phase 2 Integration)
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
  Target, Loader2, RefreshCw, AlertCircle, ChevronDown, ChevronUp,
  Droplets, Leaf, Mountain, Cloud, TrendingUp, Info, Satellite,
  CheckCircle, AlertTriangle, Sparkles, Layers, Map, Thermometer,
  Wind, Activity, Trees
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import useBionicEngines from '@/hooks/useBionicEngines';

// Species options (updated with configs.py values)
const SPECIES_OPTIONS = [
  { value: 'deer', label: 'Cerf de Virginie', icon: '🦌' },
  { value: 'moose', label: 'Orignal', icon: '🫎' },
  { value: 'bear', label: 'Ours noir', icon: '🐻' },
  { value: 'caribou', label: 'Caribou forestier', icon: '🦌' },
  { value: 'wolf', label: 'Loup gris', icon: '🐺' },
  { value: 'turkey', label: 'Dindon sauvage', icon: '🦃' }
];

// Score classification colors
const CLASSIFICATION_COLORS = {
  exceptional: { bg: 'bg-emerald-500', text: 'text-emerald-400', border: 'border-emerald-500' },
  excellent: { bg: 'bg-green-500', text: 'text-green-400', border: 'border-green-500' },
  good: { bg: 'bg-lime-500', text: 'text-lime-400', border: 'border-lime-500' },
  moderate: { bg: 'bg-yellow-500', text: 'text-yellow-400', border: 'border-yellow-500' },
  low: { bg: 'bg-orange-500', text: 'text-orange-400', border: 'border-orange-500' },
  poor: { bg: 'bg-red-500', text: 'text-red-400', border: 'border-red-500' }
};

// Get rating category from score
const getRatingCategory = (score) => {
  if (score >= 85) return 'exceptional';
  if (score >= 70) return 'excellent';
  if (score >= 55) return 'good';
  if (score >= 40) return 'moderate';
  if (score >= 25) return 'low';
  return 'poor';
};

// Get rating label from score
const getRatingLabel = (score) => {
  if (score >= 85) return 'Exceptionnel';
  if (score >= 70) return 'Excellent';
  if (score >= 55) return 'Bon';
  if (score >= 40) return 'Modéré';
  if (score >= 25) return 'Faible';
  return 'Très faible';
};

/**
 * Score Gauge Component
 */
const ScoreGauge = ({ score, size = 'md' }) => {
  const category = getRatingCategory(score);
  const colors = CLASSIFICATION_COLORS[category];
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;
  
  const sizeClasses = {
    sm: 'w-20 h-20',
    md: 'w-32 h-32',
    lg: 'w-40 h-40'
  };

  return (
    <div className={`relative mx-auto ${sizeClasses[size]}`}>
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke="currentColor"
          strokeWidth="8"
          fill="transparent"
          className="text-white/10"
        />
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke="currentColor"
          strokeWidth="8"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={colors.text}
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-bold text-white ${size === 'sm' ? 'text-xl' : 'text-3xl'}`}>
          {Math.round(score)}
        </span>
        <span className="text-xs text-gray-400">/100</span>
      </div>
    </div>
  );
};

/**
 * Mini Score Bar
 */
const MiniScoreBar = ({ label, score, icon: Icon, color }) => (
  <div className="space-y-1">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        {Icon && <Icon className={`h-3 w-3 ${color}`} />}
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <span className="text-xs font-medium text-white">{Math.round(score)}</span>
    </div>
    <Progress value={score} className="h-1" />
  </div>
);

/**
 * Sentinel Analysis Tab
 */
const SentinelTab = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 text-green-400 animate-spin" />
        <span className="ml-2 text-sm text-gray-400">Analyse Sentinel-2...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-sm">
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }
  
  if (!data) {
    return (
      <div className="text-center py-6 text-gray-500">
        <Satellite className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Cliquez sur la carte pour analyser la végétation</p>
      </div>
    );
  }
  
  const { indices, habitat, hunting_score, classification, recommendations } = data;
  
  // Support both new standardized format (overall_score) and legacy (hunting_score)
  const scoreData = data.overall_score || hunting_score;
  
  // Extract score value - handle both direct value and nested object
  const scoreValue = typeof scoreData === 'object' 
    ? scoreData?.score || 0 
    : scoreData || 0;
  const category = getRatingCategory(scoreValue);
  const colors = CLASSIFICATION_COLORS[category];
  
  // Extract NDVI value
  const ndviValue = typeof indices?.ndvi === 'object' ? indices.ndvi.value : indices?.ndvi;
  const ndviDesc = typeof indices?.ndvi === 'object' ? indices.ndvi.description : '';
  
  // Extract NDWI value
  const ndwiValue = typeof indices?.ndwi === 'object' ? indices.ndwi.value : indices?.ndwi;
  const ndwiDesc = typeof indices?.ndwi === 'object' ? indices.ndwi.description : '';
  
  // Extract EVI value
  const eviValue = typeof indices?.evi === 'object' ? indices.evi.value : indices?.evi;
  
  // Extract SAVI value
  const saviValue = typeof indices?.savi === 'object' ? indices.savi.value : indices?.savi;
  
  return (
    <div className="space-y-4">
      {/* Score */}
      <div className={`p-3 rounded-sm border ${colors.border}/30`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Leaf className="h-5 w-5 text-green-400" />
            <span className="text-sm font-medium text-white">Score Végétation</span>
          </div>
          <Badge className={`${colors.bg}/20 ${colors.text}`}>
            {Math.round(scoreValue)}/100
          </Badge>
        </div>
        {scoreData?.interpretation && (
          <p className="text-xs text-gray-400 mt-1">{scoreData.interpretation}</p>
        )}
      </div>
      
      {/* Indices */}
      {indices && (
        <div className="space-y-2">
          <span className="text-xs text-gray-500 uppercase tracking-wider">Indices</span>
          <div className="grid grid-cols-2 gap-2">
            {ndviValue !== undefined && (
              <div className="p-2 bg-black/20 rounded-sm">
                <span className="text-xs text-gray-400">NDVI</span>
                <p className="text-lg font-bold text-green-400">
                  {typeof ndviValue === 'number' ? ndviValue.toFixed(2) : 'N/A'}
                </p>
                <p className="text-xs text-gray-500 truncate">{ndviDesc || ''}</p>
              </div>
            )}
            {ndwiValue !== undefined && (
              <div className="p-2 bg-black/20 rounded-sm">
                <span className="text-xs text-gray-400">NDWI</span>
                <p className="text-lg font-bold text-blue-400">
                  {typeof ndwiValue === 'number' ? ndwiValue.toFixed(2) : 'N/A'}
                </p>
                <p className="text-xs text-gray-500 truncate">{ndwiDesc || ''}</p>
              </div>
            )}
            {eviValue !== undefined && (
              <div className="p-2 bg-black/20 rounded-sm">
                <span className="text-xs text-gray-400">EVI</span>
                <p className="text-lg font-bold text-lime-400">
                  {typeof eviValue === 'number' ? eviValue.toFixed(2) : 'N/A'}
                </p>
              </div>
            )}
            {saviValue !== undefined && (
              <div className="p-2 bg-black/20 rounded-sm">
                <span className="text-xs text-gray-400">SAVI</span>
                <p className="text-lg font-bold text-yellow-400">
                  {typeof saviValue === 'number' ? saviValue.toFixed(2) : 'N/A'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Habitat */}
      {habitat && (
        <div className="p-2 bg-black/20 rounded-sm">
          <span className="text-xs text-gray-400">Type d'habitat</span>
          <p className="text-sm font-medium text-white">{habitat.type || habitat.name || 'N/A'}</p>
          <p className="text-xs text-gray-500 mt-1">{habitat.description || ''}</p>
        </div>
      )}
      
      {/* Classification */}
      {classification && (
        <div className="p-2 bg-black/20 rounded-sm">
          <span className="text-xs text-gray-400">Classification forestière</span>
          <p className="text-sm font-medium text-white">
            {classification.forest_type || classification.type || 'N/A'}
          </p>
          <p className="text-xs text-gray-500 mt-1">{classification.cover_type || classification.description || ''}</p>
        </div>
      )}
      
      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="space-y-1">
          <span className="text-xs text-gray-500">Recommandations</span>
          {recommendations.slice(0, 3).map((rec, i) => (
            <p key={i} className="text-xs text-gray-300 pl-2 border-l border-green-500/30">
              {typeof rec === 'string' ? rec : (rec?.message || rec?.text || JSON.stringify(rec))}
            </p>
          ))}
        </div>
      )}
      
      <p className="text-xs text-gray-600 text-center">
        Source: Sentinel-2 / NASA GIBS
      </p>
    </div>
  );
};

/**
 * SIGÉOM Analysis Tab
 */
const SigeomTab = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 text-purple-400 animate-spin" />
        <span className="ml-2 text-sm text-gray-400">Analyse SIGÉOM...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-sm">
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }
  
  if (!data) {
    return (
      <div className="text-center py-6 text-gray-500">
        <Mountain className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Cliquez sur la carte pour analyser la géologie</p>
      </div>
    );
  }
  
  // Extract data from response
  const province = data.geological_province;
  const bedrock = data.bedrock_analysis;
  const surficial = data.surficial_analysis;
  const huntingScore = data.hunting_score;
  const recommendations = data.recommendations;
  
  // Get score value
  const scoreValue = typeof huntingScore === 'object' 
    ? huntingScore?.score || 0 
    : huntingScore || 70; // Default if not provided
  const category = getRatingCategory(scoreValue);
  const colors = CLASSIFICATION_COLORS[category];
  
  return (
    <div className="space-y-4">
      {/* Score */}
      <div className={`p-3 rounded-sm border ${colors.border}/30`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Mountain className="h-5 w-5 text-purple-400" />
            <span className="text-sm font-medium text-white">Score Géologique</span>
          </div>
          <Badge className={`${colors.bg}/20 ${colors.text}`}>
            {Math.round(scoreValue)}/100
          </Badge>
        </div>
        {huntingScore?.interpretation && (
          <p className="text-xs text-gray-400 mt-1">{huntingScore.interpretation}</p>
        )}
      </div>
      
      {/* Geological Province */}
      {province && (
        <div className="p-2 bg-black/20 rounded-sm">
          <span className="text-xs text-gray-400">Province géologique</span>
          <p className="text-sm font-medium text-white capitalize">
            {province.replace(/_/g, ' ') || 'N/A'}
          </p>
          {data.area_km2 && (
            <Badge className="mt-1 bg-purple-500/20 text-purple-300 text-xs">
              {data.area_km2?.toFixed(0)} km²
            </Badge>
          )}
        </div>
      )}
      
      {/* Bedrock Analysis */}
      {bedrock && (
        <div className="p-2 bg-black/20 rounded-sm">
          <span className="text-xs text-gray-400">Socle rocheux</span>
          {bedrock.rock_types && bedrock.rock_types.length > 0 ? (
            <div className="space-y-1 mt-1">
              {bedrock.rock_types.slice(0, 3).map((rock, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm text-white">{rock.name || rock.type}</span>
                  <span className="text-xs text-gray-500">{rock.province}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm font-medium text-white">
              {bedrock.dominant_type || bedrock.type || 'Données disponibles'}
            </p>
          )}
        </div>
      )}
      
      {/* Surficial Deposits */}
      {surficial && (
        <div className="p-2 bg-black/20 rounded-sm">
          <span className="text-xs text-gray-400">Dépôts de surface</span>
          {surficial.deposit_types && surficial.deposit_types.length > 0 ? (
            <div className="space-y-1 mt-1">
              {surficial.deposit_types.slice(0, 3).map((deposit, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm text-white">{deposit.name || deposit.type}</span>
                  {deposit.drainage && (
                    <div className="flex items-center gap-1">
                      <Droplets className="h-3 w-3 text-blue-400" />
                      <span className="text-xs text-gray-400">{deposit.drainage}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : surficial.dominant_type ? (
            <p className="text-sm font-medium text-white">{surficial.dominant_type}</p>
          ) : (
            <p className="text-sm text-gray-400">Données en cours de chargement...</p>
          )}
        </div>
      )}
      
      {/* Species Impact */}
      {data.species_impact && (
        <div className="p-2 bg-black/20 rounded-sm">
          <span className="text-xs text-gray-400">Impact pour {data.target_species}</span>
          <p className="text-sm text-white mt-1">{data.species_impact.summary || data.species_impact}</p>
        </div>
      )}
      
      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="space-y-1">
          <span className="text-xs text-gray-500">Recommandations</span>
          {recommendations.slice(0, 3).map((rec, i) => (
            <p key={i} className="text-xs text-gray-300 pl-2 border-l border-purple-500/30">
              {typeof rec === 'string' ? rec : (rec?.message || rec?.text || JSON.stringify(rec))}
            </p>
          ))}
        </div>
      )}
      
      <p className="text-xs text-gray-600 text-center">
        Source: SIGÉOM - MERN Québec
      </p>
    </div>
  );
};

/**
 * Combined Analysis Tab (Main Tab)
 */
const CombinedTab = ({ data, loading, error, targetSpecies }) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-8">
        <Loader2 className="h-8 w-8 text-emerald-400 animate-spin mb-2" />
        <p className="text-sm text-gray-400">Analyse BIONIC™ en cours...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-sm">
        <AlertCircle className="h-4 w-4 text-red-400 mb-1" />
        <p className="text-sm text-red-400">{error}</p>
      </div>
    );
  }
  
  if (!data) {
    return (
      <div className="text-center py-8">
        <Target className="h-10 w-10 text-gray-600 mx-auto mb-2" />
        <p className="text-sm text-gray-400">
          Sélectionnez une zone sur la carte pour obtenir une analyse complète
        </p>
      </div>
    );
  }
  
  const score = data.overall_score || 0;
  const category = getRatingCategory(score);
  const colors = CLASSIFICATION_COLORS[category];
  const modules = data.modules || {};
  const species = data.species || {};
  const predictions = data.predictions || {};
  const realConditions = data.real_conditions || {};
  
  // Get target species data
  const speciesData = species[targetSpecies] || Object.values(species)[0] || {};
  
  return (
    <div className="space-y-4">
      {/* Main Score */}
      <div className={`p-4 rounded-sm border ${colors.border}/30 bg-gradient-to-b from-${colors.bg.replace('bg-', '')}/10 to-transparent`}>
        <ScoreGauge score={score} size="md" />
        
        <div className="text-center mt-3">
          <Badge className={`${colors.bg}/20 ${colors.text} border ${colors.border}/50`}>
            <Sparkles className="h-3 w-3 mr-1" />
            {getRatingLabel(score)}
          </Badge>
          <p className="text-xs text-gray-400 mt-2">
            Score de potentiel de chasse BIONIC™
          </p>
        </div>
        
        {/* Season */}
        {data.season && (
          <div className="flex items-center justify-center gap-2 mt-2 text-xs text-gray-500">
            <span>Saison: {data.season}</span>
          </div>
        )}
      </div>
      
      {/* Real Weather Conditions */}
      {realConditions.weather && (
        <div className="p-2 bg-black/20 rounded-sm">
          <div className="flex items-center gap-2 mb-2">
            <Cloud className="h-4 w-4 text-cyan-400" />
            <span className="text-xs text-gray-400">Conditions actuelles</span>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <Thermometer className="h-3 w-3 mx-auto text-orange-400" />
              <p className="text-sm font-medium text-white">
                {realConditions.weather.temperature?.toFixed(1) || '--'}°C
              </p>
            </div>
            <div>
              <Droplets className="h-3 w-3 mx-auto text-blue-400" />
              <p className="text-sm font-medium text-white">
                {realConditions.weather.humidity || '--'}%
              </p>
            </div>
            <div>
              <Wind className="h-3 w-3 mx-auto text-gray-400" />
              <p className="text-sm font-medium text-white">
                {realConditions.weather.wind_speed?.toFixed(0) || '--'} km/h
              </p>
            </div>
          </div>
          {realConditions.weather.description && (
            <p className="text-xs text-gray-500 text-center mt-1">
              {realConditions.weather.description}
            </p>
          )}
        </div>
      )}
      
      {/* Species Score */}
      {speciesData.score !== undefined && (
        <div className="p-2 bg-black/20 rounded-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Score {speciesData.common_name || targetSpecies}</span>
            <Badge className="bg-emerald-500/20 text-emerald-300 text-xs">
              {Math.round(speciesData.score)}/100
            </Badge>
          </div>
          <Progress value={speciesData.score} className="h-1.5" />
          {speciesData.recommendations && speciesData.recommendations.length > 0 && (
            <p className="text-xs text-gray-500 mt-1">
              {speciesData.recommendations[0]}
            </p>
          )}
        </div>
      )}
      
      {/* Module Scores */}
      {Object.keys(modules).length > 0 && (
        <div className="space-y-2">
          <span className="text-xs text-gray-500 uppercase tracking-wider">Modules</span>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(modules).slice(0, 6).map(([key, mod]) => {
              const modScore = mod.score || 0;
              const modCategory = getRatingCategory(modScore);
              const modColors = CLASSIFICATION_COLORS[modCategory];
              
              return (
                <div key={key} className="p-2 bg-black/20 rounded-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400 truncate">{mod.module || key}</span>
                    <span className={`text-xs font-medium ${modColors.text}`}>
                      {Math.round(modScore)}
                    </span>
                  </div>
                  <Progress value={modScore} className="h-1 mt-1" />
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Predictions */}
      {predictions.forecast_24h && (
        <div className="p-2 bg-black/20 rounded-sm">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-4 w-4 text-yellow-400" />
            <span className="text-xs text-gray-400">Prédictions 24h</span>
          </div>
          <div className="flex gap-2">
            {Object.entries(predictions.forecast_24h).slice(0, 3).map(([sp, val]) => (
              <div key={sp} className="flex-1 text-center">
                <p className="text-xs text-gray-500 capitalize">{sp}</p>
                <p className="text-sm font-medium text-white">{Math.round(val)}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Data Sources */}
      {data.data_sources && data.data_sources.length > 0 && (
        <div className="text-xs text-gray-600 text-center">
          Sources: {data.data_sources.join(', ')}
        </div>
      )}
      
      <p className="text-xs text-gray-500 text-center">
        BIONIC™ Engine {data.engine_version || '2.0'}
      </p>
    </div>
  );
};

/**
 * Main Enhanced Environment Analysis Panel
 */
const EnvironmentAnalysisPanelEnhanced = ({
  bbox,
  location,
  onAnalysisComplete,
  position = 'inline',
  defaultTab = 'combined'
}) => {
  const [expanded, setExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [targetSpecies, setTargetSpecies] = useState('deer');
  
  const {
    loading,
    errors,
    data,
    fetchSentinelAnalysis,
    fetchSigeomAnalysis,
    fetchCombinedAnalysis,
    fetchAllAnalyses,
    isLoading
  } = useBionicEngines();

  const isInline = position === 'inline';

  // Fetch all analyses when location changes
  const handleAnalyze = useCallback(async () => {
    if (!location && !bbox) return;
    
    const lat = location?.lat || (bbox?.min_lat + bbox?.max_lat) / 2;
    const lon = location?.lng || (bbox?.min_lon + bbox?.max_lon) / 2;
    
    const effectiveBbox = bbox || {
      min_lat: lat - 0.05,
      max_lat: lat + 0.05,
      min_lon: lon - 0.05,
      max_lon: lon + 0.05
    };
    
    // Fetch all analyses in parallel
    const results = await fetchAllAnalyses(lat, lon, effectiveBbox, targetSpecies);
    
    if (onAnalysisComplete) {
      onAnalysisComplete(results);
    }
  }, [location, bbox, targetSpecies, fetchAllAnalyses, onAnalysisComplete]);

  // Auto-analyze on mount and when location changes
  useEffect(() => {
    if (location || bbox) {
      handleAnalyze();
    }
  }, [location?.lat, location?.lng, bbox?.min_lat, handleAnalyze]);

  // Re-analyze when species changes
  useEffect(() => {
    if (data.combined && (location || bbox)) {
      handleAnalyze();
    }
  }, [targetSpecies]);

  const content = (
    <div className="space-y-4">
      {/* Species Selector */}
      <div className="flex items-center gap-2">
        <Select value={targetSpecies} onValueChange={setTargetSpecies}>
          <SelectTrigger className="bg-black/40 border-white/10 text-white h-8 flex-1">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-[#1a1a1a] border-white/10">
            {SPECIES_OPTIONS.map(species => (
              <SelectItem key={species.value} value={species.value} className="text-white">
                <div className="flex items-center gap-2">
                  <span>{species.icon}</span>
                  <span className="text-sm">{species.label}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="outline"
                onClick={handleAnalyze}
                disabled={isLoading}
                className="h-8 w-8 border-white/20"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Actualiser l'analyse</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-black/40">
          <TabsTrigger 
            value="combined" 
            className="data-[state=active]:bg-emerald-500/20 data-[state=active]:text-emerald-400"
          >
            <Target className="h-3 w-3 mr-1" />
            <span className="hidden sm:inline">Global</span>
          </TabsTrigger>
          <TabsTrigger 
            value="sentinel"
            className="data-[state=active]:bg-green-500/20 data-[state=active]:text-green-400"
          >
            <Leaf className="h-3 w-3 mr-1" />
            <span className="hidden sm:inline">Végétation</span>
          </TabsTrigger>
          <TabsTrigger 
            value="sigeom"
            className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-400"
          >
            <Mountain className="h-3 w-3 mr-1" />
            <span className="hidden sm:inline">Géologie</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="combined" className="mt-3">
          <CombinedTab 
            data={data.combined}
            loading={loading.combined}
            error={errors.combined}
            targetSpecies={targetSpecies}
          />
        </TabsContent>

        <TabsContent value="sentinel" className="mt-3">
          <SentinelTab 
            data={data.sentinel}
            loading={loading.sentinel}
            error={errors.sentinel}
          />
        </TabsContent>

        <TabsContent value="sigeom" className="mt-3">
          <SigeomTab 
            data={data.sigeom}
            loading={loading.sigeom}
            error={errors.sigeom}
          />
        </TabsContent>
      </Tabs>

      {/* No location message */}
      {!bbox && !location && !isLoading && (
        <div className="text-center py-4">
          <Map className="h-8 w-8 text-gray-600 mx-auto mb-2" />
          <p className="text-sm text-gray-400">
            Cliquez sur la carte pour analyser un point
          </p>
        </div>
      )}
    </div>
  );

  // Inline mode
  if (isInline) {
    return <div className="p-4">{content}</div>;
  }

  // Card mode
  return (
    <Card className="absolute right-4 top-4 z-10 w-80 bg-black/95 border-white/10 backdrop-blur-md shadow-xl">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-emerald-400" />
            <CardTitle className="text-sm text-white">Analyse BIONIC™</CardTitle>
          </div>
          <Button
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 text-gray-400 hover:text-white"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
      </CardHeader>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            <CardContent className="overflow-y-auto max-h-[600px]">
              {content}
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export default EnvironmentAnalysisPanelEnhanced;
