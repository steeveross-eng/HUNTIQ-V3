/**
 * HUNTIQ V3 - BIONIC™ Hydro Analysis Panel
 * 
 * Panneau d'affichage des scores de proximité à l'eau
 * et recommandations hydrologiques pour la chasse.
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Droplets, Target, MapPin, Compass, AlertCircle,
  Loader2, RefreshCw, Info, ChevronDown, ChevronUp,
  TreePine, Mountain, Waves
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api.client';

// Species options
const SPECIES_OPTIONS = [
  { value: 'deer', label: 'Cerf de Virginie', icon: '🦌' },
  { value: 'moose', label: 'Orignal', icon: '🫎' },
  { value: 'bear', label: 'Ours noir', icon: '🐻' },
  { value: 'waterfowl', label: 'Sauvagine', icon: '🦆' },
  { value: 'turkey', label: 'Dindon sauvage', icon: '🦃' }
];

// Score level colors
const SCORE_COLORS = {
  excellent: 'bg-green-500',
  bon: 'bg-blue-500',
  modéré: 'bg-yellow-500',
  faible: 'bg-orange-500',
  très_faible: 'bg-red-500'
};

/**
 * Score Display Component
 */
const ScoreDisplay = ({ score, level, label }) => {
  const color = SCORE_COLORS[level] || 'bg-gray-500';
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-400">{label}</span>
        <span className="text-lg font-bold text-white">{score}/100</span>
      </div>
      <Progress value={score} className="h-2" indicatorClassName={color} />
      <Badge className={`${color} text-white text-xs`}>
        {level?.replace('_', ' ')}
      </Badge>
    </div>
  );
};

/**
 * Recommendation Card
 */
const RecommendationCard = ({ text, icon: Icon = Info }) => (
  <div className="flex items-start gap-3 p-3 bg-black/30 rounded-sm border border-white/5">
    <Icon className="h-4 w-4 text-[#f5a623] mt-0.5 flex-shrink-0" />
    <p className="text-sm text-gray-300">{text}</p>
  </div>
);

/**
 * Main Hydro Analysis Panel
 */
const HydroAnalysisPanel = ({
  bbox,
  onAnalysisComplete,
  position = 'right'
}) => {
  const [expanded, setExpanded] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [targetSpecies, setTargetSpecies] = useState('deer');
  const [proximityScore, setProximityScore] = useState(null);
  
  // Check if inline mode (embedded in parent card)
  const isInline = position === 'inline';
  
  // Fetch hydrology analysis
  const fetchAnalysis = useCallback(async () => {
    if (!bbox) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/bionic/hydro/analyze', {
        bbox: bbox,
        target_species: targetSpecies,
        include_rivers: true,
        include_lakes: true,
        include_wetlands: true
      });
      
      setAnalysis(response.data);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(response.data);
      }
    } catch (err) {
      console.error('Hydro analysis error:', err);
      setError('Erreur lors de l\'analyse hydrologique');
    } finally {
      setLoading(false);
    }
  }, [bbox, targetSpecies, onAnalysisComplete]);
  
  // Fetch proximity score for a sample distance
  const fetchProximityScore = useCallback(async () => {
    try {
      // Use a sample distance (500m is typical)
      const response = await api.get(`/api/bionic/hydro/score/proximity`, {
        params: {
          distance_m: 500,
          species: targetSpecies
        }
      });
      setProximityScore(response.data);
    } catch (err) {
      console.error('Proximity score error:', err);
    }
  }, [targetSpecies]);
  
  // Fetch data when bbox or species changes
  useEffect(() => {
    if (bbox) {
      fetchAnalysis();
      fetchProximityScore();
    }
  }, [bbox, fetchAnalysis, fetchProximityScore]);
  
  // Position styles (for absolute positioning)
  const positionStyles = position === 'right'
    ? 'right-4 top-4'
    : position === 'left'
    ? 'left-4 top-4'
    : '';
  
  // If inline mode, render without Card wrapper
  if (isInline) {
    return (
      <div className="p-4 space-y-4">
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
          <div className="flex items-center justify-center py-6">
            <Loader2 className="h-6 w-6 text-blue-400 animate-spin" />
          </div>
        )}
        
        {/* Error state */}
        {error && !loading && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-sm">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
        
        {/* Analysis Results */}
        {analysis && !loading && (
          <>
            {/* Overall Score */}
            <div className="p-4 bg-gradient-to-r from-blue-500/10 to-transparent rounded-sm border border-blue-500/20">
              <ScoreDisplay
                score={analysis.overall_score || 0}
                level={analysis.level || 'modéré'}
                label="Score Hydrologique"
              />
            </div>
            
            {/* Proximity Score */}
            {proximityScore && (
              <div className="p-3 bg-black/30 rounded-sm border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="h-4 w-4 text-[#f5a623]" />
                  <span className="text-sm font-medium text-white">Proximité Eau</span>
                </div>
                <p className="text-xs text-gray-400">
                  {proximityScore.interpretation}
                </p>
              </div>
            )}
            
            {/* Recommendations */}
            {analysis.recommendations && analysis.recommendations.length > 0 && (
              <div className="space-y-2">
                <span className="text-xs text-gray-400">Recommandations</span>
                <div className="space-y-2">
                  {analysis.recommendations.slice(0, 2).map((rec, i) => (
                    <RecommendationCard key={i} text={rec} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
        
        {/* Refresh button */}
        {bbox && (
          <Button
            size="sm"
            variant="outline"
            onClick={fetchAnalysis}
            disabled={loading}
            className="w-full border-white/20 text-gray-300 hover:text-white"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
        )}
        
        {/* Data source */}
        <p className="text-xs text-gray-500 text-center">
          BIONIC™ HydroEngine | Données GRHQ
        </p>
      </div>
    );
  }
  
  return (
    <Card className={`absolute ${positionStyles} z-10 w-80 bg-black/95 border-white/10 backdrop-blur-md shadow-xl max-h-[600px] overflow-hidden`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="h-5 w-5 text-blue-400" />
            <CardTitle className="text-sm text-white">Analyse Hydrologique</CardTitle>
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
            <CardContent className="space-y-4 overflow-y-auto max-h-[500px]">
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
                <div className="flex items-center justify-center py-6">
                  <Loader2 className="h-6 w-6 text-blue-400 animate-spin" />
                </div>
              )}
              
              {/* Error state */}
              {error && !loading && (
                <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-sm">
                  <AlertCircle className="h-4 w-4 text-red-400" />
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}
              
              {/* Analysis Results */}
              {analysis && !loading && (
                <>
                  {/* Overall Score */}
                  <div className="p-4 bg-gradient-to-r from-blue-500/10 to-transparent rounded-sm border border-blue-500/20">
                    <ScoreDisplay
                      score={analysis.overall_score || 0}
                      level={analysis.level || 'modéré'}
                      label="Score Hydrologique"
                    />
                  </div>
                  
                  {/* Proximity Score */}
                  {proximityScore && (
                    <div className="p-3 bg-black/30 rounded-sm border border-white/5">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="h-4 w-4 text-[#f5a623]" />
                        <span className="text-sm font-medium text-white">Proximité Eau (500m)</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-400">Score:</span>
                          <span className="ml-2 text-white font-medium">{proximityScore.score}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Niveau:</span>
                          <Badge className={`ml-2 ${SCORE_COLORS[proximityScore.level] || 'bg-gray-500'} text-white text-xs`}>
                            {proximityScore.level}
                          </Badge>
                        </div>
                      </div>
                      <p className="mt-2 text-xs text-gray-400">
                        {proximityScore.interpretation}
                      </p>
                    </div>
                  )}
                  
                  {/* Components */}
                  <div className="space-y-2">
                    <span className="text-xs text-gray-400">Composantes hydrologiques</span>
                    
                    <div className="grid grid-cols-3 gap-2">
                      {analysis.components?.rivers?.available && (
                        <div className="p-2 bg-black/30 rounded-sm text-center">
                          <Waves className="h-4 w-4 text-blue-400 mx-auto mb-1" />
                          <span className="text-xs text-gray-300">Rivières</span>
                        </div>
                      )}
                      {analysis.components?.lakes?.available && (
                        <div className="p-2 bg-black/30 rounded-sm text-center">
                          <Droplets className="h-4 w-4 text-cyan-400 mx-auto mb-1" />
                          <span className="text-xs text-gray-300">Lacs</span>
                        </div>
                      )}
                      {analysis.components?.wetlands?.available && (
                        <div className="p-2 bg-black/30 rounded-sm text-center">
                          <TreePine className="h-4 w-4 text-green-400 mx-auto mb-1" />
                          <span className="text-xs text-gray-300">Wetlands</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Recommendations */}
                  {analysis.recommendations && analysis.recommendations.length > 0 && (
                    <div className="space-y-2">
                      <span className="text-xs text-gray-400">Recommandations</span>
                      <div className="space-y-2">
                        {analysis.recommendations.map((rec, i) => (
                          <RecommendationCard key={i} text={rec} />
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
              
              {/* Refresh button */}
              {bbox && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={fetchAnalysis}
                  disabled={loading}
                  className="w-full border-white/20 text-gray-300 hover:text-white"
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Actualiser l'analyse
                </Button>
              )}
              
              {/* No bbox message */}
              {!bbox && (
                <div className="text-center py-6">
                  <MapPin className="h-8 w-8 text-gray-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">
                    Sélectionnez une zone sur la carte pour l'analyse
                  </p>
                </div>
              )}
              
              {/* Data source */}
              <div className="pt-2 border-t border-white/5">
                <p className="text-xs text-gray-500 text-center">
                  Source: GRHQ - Données Québec | BIONIC™ HydroEngine
                </p>
              </div>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export default HydroAnalysisPanel;
