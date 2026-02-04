/**
 * HUNTIQ V3 - BIONIC™ Environment Analysis Panel
 * 
 * Panneau d'affichage du score global combiné de potentiel de chasse.
 * Fusionne les analyses de HydroEngine, SentinelEngine, SigeomEngine et météo.
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Target, Loader2, RefreshCw, AlertCircle, ChevronDown, ChevronUp,
  Droplets, Leaf, Mountain, Cloud, Utensils, TrendingUp, Info,
  CheckCircle, AlertTriangle, Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api.client';

// Species options
const SPECIES_OPTIONS = [
  { value: 'deer', label: 'Cerf de Virginie', icon: '🦌' },
  { value: 'moose', label: 'Orignal', icon: '🫎' },
  { value: 'bear', label: 'Ours noir', icon: '🐻' },
  { value: 'elk', label: 'Wapiti', icon: '🦌' },
  { value: 'waterfowl', label: 'Sauvagine', icon: '🦆' }
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

// Component icons
const COMPONENT_ICONS = {
  vegetation: { icon: Leaf, color: 'text-green-400', label: 'Végétation' },
  hydrology: { icon: Droplets, color: 'text-blue-400', label: 'Hydrologie' },
  geology: { icon: Mountain, color: 'text-purple-400', label: 'Géologie' },
  weather: { icon: Cloud, color: 'text-cyan-400', label: 'Météo' },
  nutrition: { icon: Utensils, color: 'text-orange-400', label: 'Nutrition' }
};

/**
 * Score Gauge Component - Visual circular gauge
 */
const ScoreGauge = ({ score, classification }) => {
  const colors = CLASSIFICATION_COLORS[classification?.category] || CLASSIFICATION_COLORS.moderate;
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative w-32 h-32 mx-auto">
      <svg className="w-full h-full transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="64"
          cy="64"
          r="45"
          stroke="currentColor"
          strokeWidth="8"
          fill="transparent"
          className="text-white/10"
        />
        {/* Progress circle */}
        <circle
          cx="64"
          cy="64"
          r="45"
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
        <span className="text-3xl font-bold text-white">{Math.round(score)}</span>
        <span className="text-xs text-gray-400">/100</span>
      </div>
    </div>
  );
};

/**
 * Component Score Bar
 */
const ComponentScoreBar = ({ component, data }) => {
  const config = COMPONENT_ICONS[component];
  if (!config || !data) return null;

  const Icon = config.icon;
  const score = data.raw_score || 0;
  const contribution = data.contribution || 0;
  const weight = data.weight || 0;

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className={`h-4 w-4 ${config.color}`} />
          <span className="text-xs text-gray-300">{config.label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">{(weight * 100).toFixed(0)}%</span>
          <span className="text-sm font-medium text-white">{Math.round(score)}</span>
        </div>
      </div>
      <Progress 
        value={score} 
        className="h-1.5" 
        indicatorClassName={config.color.replace('text-', 'bg-')} 
      />
    </div>
  );
};

/**
 * Recommendation Item
 */
const RecommendationItem = ({ rec }) => {
  const icons = {
    positive: CheckCircle,
    warning: AlertTriangle,
    info: Info
  };
  const colors = {
    positive: 'text-green-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400'
  };

  const Icon = icons[rec.type] || Info;
  const color = colors[rec.type] || 'text-gray-400';

  return (
    <div className="flex items-start gap-2 p-2 bg-black/20 rounded-sm">
      <Icon className={`h-4 w-4 ${color} mt-0.5 flex-shrink-0`} />
      <p className="text-xs text-gray-300">{rec.message}</p>
    </div>
  );
};

/**
 * Main Environment Analysis Panel
 */
const EnvironmentAnalysisPanel = ({
  bbox,
  location,
  onAnalysisComplete,
  position = 'inline',
  showDetailedBreakdown = true
}) => {
  const [expanded, setExpanded] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [targetSpecies, setTargetSpecies] = useState('deer');
  const [showDetails, setShowDetails] = useState(false);

  const isInline = position === 'inline';

  // Fetch combined environment analysis
  const fetchAnalysis = useCallback(async () => {
    if (!bbox && !location) return;

    setLoading(true);
    setError(null);

    try {
      let requestBbox = bbox;
      
      // If only location provided, create small bbox
      if (!bbox && location) {
        const delta = 0.05; // ~5km
        requestBbox = {
          min_lat: location.lat - delta,
          max_lat: location.lat + delta,
          min_lon: location.lng - delta,
          max_lon: location.lng + delta
        };
      }

      const response = await api.post('/api/bionic/environment/analyze/territory', {
        bbox: requestBbox,
        target_species: targetSpecies,
        include_hydro: true,
        include_sentinel: true,
        include_sigeom: true,
        include_weather: true,
        apply_seasonal: true
      });

      setAnalysis(response.data);

      if (onAnalysisComplete) {
        onAnalysisComplete(response.data);
      }
    } catch (err) {
      console.error('Environment analysis error:', err);
      setError('Erreur lors de l\'analyse environnementale');
      
      // Try quick score as fallback
      if (location) {
        try {
          const quickResponse = await api.get('/api/bionic/environment/quick-score', {
            params: {
              lat: location.lat,
              lon: location.lng,
              species: targetSpecies
            }
          });
          
          // Convert quick score to analysis format
          setAnalysis({
            global_score: quickResponse.data.quick_score,
            classification: {
              category: quickResponse.data.quick_score >= 70 ? 'good' : 
                        quickResponse.data.quick_score >= 50 ? 'moderate' : 'low',
              label: quickResponse.data.quick_score >= 70 ? 'Bon' : 
                     quickResponse.data.quick_score >= 50 ? 'Modéré' : 'Faible'
            },
            seasonal_modifier: quickResponse.data.seasonal_modifier,
            season: quickResponse.data.season,
            recommendations: [],
            component_contributions: {},
            isQuickScore: true
          });
          setError(null);
        } catch (quickErr) {
          console.error('Quick score also failed:', quickErr);
        }
      }
    } finally {
      setLoading(false);
    }
  }, [bbox, location, targetSpecies, onAnalysisComplete]);

  // Fetch on mount and when dependencies change
  useEffect(() => {
    if (bbox || location) {
      fetchAnalysis();
    }
  }, [bbox, location, fetchAnalysis]);

  // Re-fetch when species changes
  useEffect(() => {
    if (analysis && (bbox || location)) {
      fetchAnalysis();
    }
  }, [targetSpecies]);

  const classification = analysis?.classification || {};
  const colors = CLASSIFICATION_COLORS[classification.category] || CLASSIFICATION_COLORS.moderate;

  const content = (
    <div className="space-y-4">
      {/* Species Selector */}
      <div className="space-y-2">
        <label className="text-xs text-gray-400">Espèce cible</label>
        <Select value={targetSpecies} onValueChange={setTargetSpecies}>
          <SelectTrigger className="bg-black/40 border-white/10 text-white h-9">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-[#1a1a1a] border-white/10">
            {SPECIES_OPTIONS.map(species => (
              <SelectItem key={species.value} value={species.value} className="text-white">
                <div className="flex items-center gap-2">
                  <span>{species.icon}</span>
                  <span>{species.label}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-8">
          <Loader2 className="h-8 w-8 text-emerald-400 animate-spin mb-2" />
          <p className="text-xs text-gray-400">Analyse en cours...</p>
        </div>
      )}

      {/* Error state */}
      {error && !loading && !analysis && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-sm">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !loading && (
        <>
          {/* Main Score Gauge */}
          <div className={`p-4 rounded-sm border ${colors.border}/30 bg-gradient-to-b from-${colors.bg.replace('bg-', '')}/10 to-transparent`}>
            <ScoreGauge 
              score={analysis.global_score || 0} 
              classification={classification}
            />
            
            <div className="text-center mt-3">
              <Badge className={`${colors.bg}/20 ${colors.text} border ${colors.border}/50`}>
                <Sparkles className="h-3 w-3 mr-1" />
                {classification.label || 'Analyse'}
              </Badge>
              <p className="text-xs text-gray-400 mt-2">
                {classification.description || 'Score de potentiel de chasse'}
              </p>
            </div>

            {/* Season indicator */}
            {analysis.season && (
              <div className="flex items-center justify-center gap-2 mt-3 text-xs text-gray-500">
                <span>Saison: {analysis.season}</span>
                {analysis.seasonal_modifier !== 1 && (
                  <Badge className="bg-white/5 text-gray-400 text-xs">
                    ×{analysis.seasonal_modifier?.toFixed(2)}
                  </Badge>
                )}
              </div>
            )}

            {/* Quick score notice */}
            {analysis.isQuickScore && (
              <p className="text-xs text-yellow-400/70 text-center mt-2">
                Score estimé (analyse rapide)
              </p>
            )}
          </div>

          {/* Component Breakdown */}
          {showDetailedBreakdown && analysis.component_contributions && 
           Object.keys(analysis.component_contributions).length > 0 && (
            <div className="space-y-3">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-between text-gray-400 hover:text-white"
                onClick={() => setShowDetails(!showDetails)}
              >
                <span className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Détail par composante
                </span>
                {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>

              <AnimatePresence>
                {showDetails && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="space-y-3 overflow-hidden"
                  >
                    {Object.entries(analysis.component_contributions).map(([key, data]) => (
                      <ComponentScoreBar key={key} component={key} data={data} />
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Recommendations */}
          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs text-gray-400 font-medium">Recommandations</span>
              <ScrollArea className="max-h-32">
                <div className="space-y-2">
                  {analysis.recommendations.slice(0, 4).map((rec, i) => (
                    <RecommendationItem key={i} rec={rec} />
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}

          {/* Main recommendation */}
          {classification.recommendation && (
            <div className="p-3 bg-[#f5a623]/10 border border-[#f5a623]/20 rounded-sm">
              <p className="text-sm text-[#f5a623]">{classification.recommendation}</p>
            </div>
          )}
        </>
      )}

      {/* No data message */}
      {!bbox && !location && !loading && (
        <div className="text-center py-6">
          <Target className="h-8 w-8 text-gray-600 mx-auto mb-2" />
          <p className="text-sm text-gray-400">
            Sélectionnez une zone sur la carte
          </p>
        </div>
      )}

      {/* Refresh button */}
      {(bbox || location) && (
        <Button
          size="sm"
          variant="outline"
          onClick={fetchAnalysis}
          disabled={loading}
          className="w-full border-white/20 text-gray-300 hover:text-white"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          {analysis ? 'Actualiser' : 'Analyser'}
        </Button>
      )}

      {/* Data source */}
      <p className="text-xs text-gray-500 text-center">
        BIONIC™ EnvironmentEngine | Analyse combinée
      </p>
    </div>
  );

  // Inline mode
  if (isInline) {
    return <div className="p-4">{content}</div>;
  }

  // Card mode (for absolute positioning)
  return (
    <Card className="absolute right-4 top-4 z-10 w-80 bg-black/95 border-white/10 backdrop-blur-md shadow-xl">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-emerald-400" />
            <CardTitle className="text-sm text-white">Score Global BIONIC™</CardTitle>
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
            <CardContent className="overflow-y-auto max-h-[500px]">
              {content}
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export default EnvironmentAnalysisPanel;
