/**
 * HUNTIQ V3 - Hunting Potential Analysis Component
 * Displays hunting potential score and analysis from geospatial data
 */

import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Target, MapPin, Compass, Mountain, Droplets, Trees, 
  Brain, History, ChevronDown, ChevronUp, Loader2,
  AlertCircle, CheckCircle2, Crosshair
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useHuntingPotential } from '@/hooks/geospatial';

// Component icons mapping
const COMPONENT_ICONS = {
  terrain: Mountain,
  water: Droplets,
  forest: Trees,
  geology: Compass,
  vegetation: Trees,
  ai_predictions: Brain,
  historical: History,
};

// Level colors
const LEVEL_COLORS = {
  excellent: { bg: 'bg-green-500', text: 'text-green-400', border: 'border-green-500' },
  good: { bg: 'bg-blue-500', text: 'text-blue-400', border: 'border-blue-500' },
  moderate: { bg: 'bg-yellow-500', text: 'text-yellow-400', border: 'border-yellow-500' },
  low: { bg: 'bg-orange-500', text: 'text-orange-400', border: 'border-orange-500' },
  poor: { bg: 'bg-red-500', text: 'text-red-400', border: 'border-red-500' },
};

// Score component row
const ScoreComponent = ({ name, data, expanded }) => {
  const Icon = COMPONENT_ICONS[name] || Target;
  const score = data?.score || 0;
  const weight = (data?.weight || 0) * 100;
  
  const getScoreColor = (s) => {
    if (s >= 70) return 'text-green-400';
    if (s >= 50) return 'text-yellow-400';
    if (s >= 30) return 'text-orange-400';
    return 'text-red-400';
  };

  const formatName = (n) => {
    const names = {
      terrain: 'Terrain',
      water: 'Hydrologie',
      forest: 'Forêt',
      geology: 'Géologie',
      vegetation: 'Végétation',
      ai_predictions: 'IA Prédictions',
      historical: 'Historique',
    };
    return names[n] || n;
  };

  return (
    <motion.div 
      className="flex items-center gap-3 p-3 bg-black/30 rounded-sm border border-white/5 hover:border-white/10 transition-colors"
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <div className="w-8 h-8 flex items-center justify-center bg-white/5 rounded-sm">
        <Icon className={`h-4 w-4 ${getScoreColor(score)}`} />
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm text-white font-medium">{formatName(name)}</span>
          <span className={`text-sm font-mono font-bold ${getScoreColor(score)}`}>
            {score.toFixed(0)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Progress 
            value={score} 
            className="h-1.5 bg-white/10"
          />
          <span className="text-xs text-gray-500 whitespace-nowrap">
            {weight.toFixed(0)}%
          </span>
        </div>
      </div>
      
      {data?.data_available === false && (
        <Badge className="bg-yellow-500/20 text-yellow-400 text-xs">
          Partiel
        </Badge>
      )}
      
      {expanded && data?.source && (
        <span className="text-xs text-gray-500 hidden md:inline">
          {data.source}
        </span>
      )}
    </motion.div>
  );
};

// Main component
const HuntingPotentialAnalysis = ({ 
  bbox = null,
  targetSpecies = 'deer',
  season = 'rut',
  autoLoad = false,
  compact = false,
}) => {
  const { result, loading, error, calculate } = useHuntingPotential();
  const [expanded, setExpanded] = useState(!compact);
  const [showDetails, setShowDetails] = useState(false);

  // Default bbox for demo (Laurentides region)
  const defaultBbox = {
    min_lat: 46.0,
    max_lat: 46.5,
    min_lon: -74.5,
    max_lon: -74.0,
  };

  const handleCalculate = useCallback(async () => {
    try {
      await calculate({
        bbox: bbox || defaultBbox,
        center_point: {
          latitude: (bbox?.min_lat || defaultBbox.min_lat) + 0.25,
          longitude: (bbox?.min_lon || defaultBbox.min_lon) + 0.25,
        },
        radius_m: 5000,
        target_species: targetSpecies,
        season: season,
        include_ai_predictions: true,
      });
    } catch (err) {
      console.error('Failed to calculate potential:', err);
    }
  }, [bbox, targetSpecies, season, calculate]);

  const levelColors = LEVEL_COLORS[result?.level] || LEVEL_COLORS.moderate;

  return (
    <Card className="bg-[#1a1a1a] border-white/10 rounded-md overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 ${levelColors.bg}/20 rounded-sm flex items-center justify-center`}>
              <Crosshair className={`h-5 w-5 ${levelColors.text}`} />
            </div>
            <div>
              <CardTitle className="text-lg text-white">Potentiel de Chasse</CardTitle>
              <p className="text-xs text-gray-500">Analyse géospatiale BIONIC™</p>
            </div>
          </div>
          
          {!compact && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setExpanded(!expanded)}
              className="text-gray-400 hover:text-white"
            >
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-4">
        {/* Calculate button */}
        {!result && !loading && (
          <div className="text-center py-8">
            <Target className="h-12 w-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-sm mb-4">
              Analysez le potentiel de chasse pour cette zone
            </p>
            <Button
              onClick={handleCalculate}
              className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm"
              disabled={loading}
            >
              <Compass className="h-4 w-4 mr-2" />
              Calculer le potentiel
            </Button>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center py-8">
            <Loader2 className="h-8 w-8 text-[#f5a623] animate-spin mb-3" />
            <p className="text-gray-400 text-sm">Analyse en cours...</p>
            <p className="text-gray-600 text-xs mt-1">
              Interrogation des sources de données Québec
            </p>
          </div>
        )}

        {/* Error state */}
        {error && !loading && (
          <div className="text-center py-6">
            <AlertCircle className="h-8 w-8 text-red-400 mx-auto mb-2" />
            <p className="text-red-400 text-sm">{error}</p>
            <Button
              onClick={handleCalculate}
              variant="outline"
              size="sm"
              className="mt-4 border-white/20 text-white"
            >
              Réessayer
            </Button>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {/* Score display */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  {/* Main score circle */}
                  <div className="relative">
                    <svg className="w-20 h-20 transform -rotate-90">
                      <circle
                        cx="40"
                        cy="40"
                        r="36"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-white/10"
                      />
                      <circle
                        cx="40"
                        cy="40"
                        r="36"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${result.overall_score * 2.26} 226`}
                        strokeLinecap="round"
                        className={levelColors.text}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-bold text-white">
                        {result.overall_score?.toFixed(0)}
                      </span>
                    </div>
                  </div>
                  
                  <div>
                    <Badge className={`${levelColors.bg}/20 ${levelColors.text} border ${levelColors.border}/30 uppercase`}>
                      {result.level}
                    </Badge>
                    <div className="mt-2 text-xs text-gray-500">
                      <span className="text-gray-400">Espèce:</span> {result.target_species}
                      <br />
                      <span className="text-gray-400">Saison:</span> {result.season}
                    </div>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCalculate}
                  className="border-white/20 text-white hover:bg-white/10 rounded-sm"
                  disabled={loading}
                >
                  <Compass className="h-4 w-4 mr-1" />
                  Recalculer
                </Button>
              </div>

              {/* Recommendations */}
              {result.recommendations?.length > 0 && (
                <div className="mb-6 p-4 bg-[#f5a623]/10 rounded-sm border border-[#f5a623]/20">
                  <h4 className="text-[#f5a623] text-sm font-semibold mb-2 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4" />
                    Recommandations
                  </h4>
                  <ul className="space-y-2">
                    {result.recommendations.map((rec, i) => (
                      <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                        <span className="text-[#f5a623] mt-1">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Component scores */}
              {expanded && (
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-white text-sm font-semibold">Composantes du score</h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowDetails(!showDetails)}
                      className="text-gray-400 hover:text-white text-xs"
                    >
                      {showDetails ? 'Masquer détails' : 'Voir détails'}
                    </Button>
                  </div>
                  
                  <div className="space-y-2">
                    {result.component_scores && Object.entries(result.component_scores).map(([name, data], i) => (
                      <ScoreComponent 
                        key={name} 
                        name={name} 
                        data={data}
                        expanded={showDetails}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Data layers info */}
              {showDetails && result.data_layers && (
                <div className="mt-4 p-3 bg-black/40 rounded-sm border border-white/5">
                  <h5 className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                    Couches de données utilisées
                  </h5>
                  <div className="flex flex-wrap gap-2">
                    {Object.keys(result.data_layers).map((layer) => (
                      <Badge key={layer} className="bg-white/5 text-gray-400 text-xs">
                        {layer}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </CardContent>
    </Card>
  );
};

export default HuntingPotentialAnalysis;
