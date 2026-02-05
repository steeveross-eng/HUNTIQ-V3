/**
 * BIONIC™ P2 - Fusion Score Panel
 * =================================
 * Panneau complet affichant le score fusionné Geo+Behavior.
 * Utilise le BehaviorFusionEngine backend.
 * 
 * @version 1.0.0
 * @phase P2
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import useGeoSuiteStore from '../../stores/geoSuiteStore';
import { useFusion, useFusionWeights, FUSION_MODES } from '../../hooks/useFusion';
import { CircularGauge, LinearGauge, MiniGauge } from './GeoSuiteScoreGauge';

// =============================================================================
// SCORE LEVEL COLORS
// =============================================================================

const SCORE_LEVEL_CONFIG = {
  exceptional: { color: '#10B981', bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Exceptionnel' },
  excellent: { color: '#3B82F6', bg: 'bg-blue-100', text: 'text-blue-700', label: 'Excellent' },
  good: { color: '#8B5CF6', bg: 'bg-purple-100', text: 'text-purple-700', label: 'Bon' },
  moderate: { color: '#F59E0B', bg: 'bg-amber-100', text: 'text-amber-700', label: 'Modéré' },
  low: { color: '#EF4444', bg: 'bg-red-100', text: 'text-red-700', label: 'Faible' },
  poor: { color: '#6B7280', bg: 'bg-gray-100', text: 'text-gray-700', label: 'Pauvre' }
};

// =============================================================================
// WEIGHT VISUALIZATION
// =============================================================================

function WeightBar({ label, weight, color = '#8B5CF6' }) {
  const percentage = Math.round(weight * 100);
  
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{percentage}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

// =============================================================================
// BREAKDOWN CHART
// =============================================================================

function BreakdownChart({ geoBreakdown, behaviorBreakdown }) {
  const allScores = useMemo(() => {
    const scores = [];
    
    // Geo scores
    Object.entries(geoBreakdown || {}).forEach(([key, value]) => {
      const name = key.replace('geo_', '');
      scores.push({
        name,
        value,
        type: 'geo',
        icon: getEngineIcon(name, 'geo')
      });
    });
    
    // Behavior scores
    Object.entries(behaviorBreakdown || {}).forEach(([key, value]) => {
      const name = key.replace('behavior_', '');
      scores.push({
        name,
        value,
        type: 'behavior',
        icon: getEngineIcon(name, 'behavior')
      });
    });
    
    return scores.sort((a, b) => b.value - a.value);
  }, [geoBreakdown, behaviorBreakdown]);
  
  return (
    <div className="space-y-2">
      {allScores.slice(0, 6).map((score, idx) => (
        <div key={idx} className="flex items-center gap-2">
          <span className="w-6 text-center">{score.icon}</span>
          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                score.type === 'geo' ? 'bg-emerald-500' : 'bg-blue-500'
              }`}
              style={{ width: `${Math.min(score.value, 100)}%` }}
            />
          </div>
          <span className="w-10 text-right text-sm font-medium">
            {Math.round(score.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

function getEngineIcon(name, type) {
  const icons = {
    // Geo
    corridor: '🛤️',
    landcover: '🌲',
    nutrition: '🍎',
    population: '📊',
    pressure: '🎯',
    // Behavior
    behavior: '🧠',
    seasonal: '🗓️',
    activity: '⏰',
    movement: '🚶',
    rut: '💕',
    species_model: '🦌'
  };
  return icons[name] || (type === 'geo' ? '🗺️' : '🧠');
}

// =============================================================================
// MODE SELECTOR
// =============================================================================

function FusionModeSelector({ mode, onChange }) {
  const modes = [
    { id: FUSION_MODES.BALANCED, label: 'Équilibré', icon: '⚖️' },
    { id: FUSION_MODES.GEO_DOMINANT, label: 'Géo', icon: '🗺️' },
    { id: FUSION_MODES.BEHAVIOR_DOMINANT, label: 'Comportement', icon: '🧠' },
    { id: FUSION_MODES.ADAPTIVE, label: 'Adaptatif', icon: '🔄' }
  ];
  
  return (
    <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
      {modes.map(m => (
        <button
          key={m.id}
          onClick={() => onChange(m.id)}
          className={`
            flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-all
            ${mode === m.id 
              ? 'bg-white text-purple-700 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900'
            }
          `}
        >
          <span>{m.icon}</span>
          <span className="hidden sm:inline">{m.label}</span>
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// RECOMMENDATIONS LIST
// =============================================================================

function RecommendationsList({ recommendations }) {
  if (!recommendations?.length) return null;
  
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
        <span>💡</span> Recommandations
      </h4>
      <div className="space-y-1">
        {recommendations.slice(0, 5).map((rec, idx) => (
          <p key={idx} className="text-sm text-gray-600 pl-6">
            {rec}
          </p>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// MAIN FUSION SCORE PANEL
// =============================================================================

export function FusionScorePanel({
  lat,
  lon,
  species = 'deer',
  territory = 'quebec',
  radiusKm = 2.0,
  autoLoad = false,
  showWeights = true,
  showBreakdown = true,
  showRecommendations = true,
  onAnalyzeComplete
}) {
  const [mode, setMode] = useState(FUSION_MODES.BALANCED);
  
  // Use fusion hook
  const {
    data,
    globalScore,
    scoreLevel,
    geoScore,
    behaviorScore,
    heatmapData,
    recommendations,
    loading,
    error,
    fetchFusion,
    isLoaded
  } = useFusion({
    autoFetch: autoLoad && lat !== null && lon !== null,
    lat,
    lon,
    species,
    territory,
    radiusKm,
    mode
  });
  
  // Use weights hook
  const { weights } = useFusionWeights(species, territory, mode);
  
  // Handle analyze
  const handleAnalyze = useCallback(async () => {
    const result = await fetchFusion({
      lat, lon, species, territory, radiusKm, mode
    });
    
    if (result && onAnalyzeComplete) {
      onAnalyzeComplete(result);
    }
  }, [fetchFusion, lat, lon, species, territory, radiusKm, mode, onAnalyzeComplete]);
  
  // Get level config
  const levelConfig = SCORE_LEVEL_CONFIG[scoreLevel] || SCORE_LEVEL_CONFIG.moderate;
  
  // No location
  if (lat === null || lon === null) {
    return (
      <div 
        className="p-6 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 text-center"
        data-testid="fusion-no-location"
      >
        <span className="text-4xl mb-2 block">📍</span>
        <p className="text-gray-600 font-medium">Sélectionnez une position</p>
        <p className="text-sm text-gray-500 mt-1">
          Cliquez sur la carte pour analyser une zone
        </p>
      </div>
    );
  }
  
  return (
    <div 
      className="bg-white rounded-xl border shadow-sm overflow-hidden"
      data-testid="fusion-score-panel"
    >
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔮</span>
            <div>
              <h3 className="font-bold text-gray-900">Score Fusionné</h3>
              <p className="text-xs text-gray-500">
                Géo-Suite + Behavior Suite
              </p>
            </div>
          </div>
          
          {/* Phase badge */}
          <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full font-medium">
            P2 Active
          </span>
        </div>
        
        {/* Mode selector */}
        <FusionModeSelector mode={mode} onChange={setMode} />
      </div>
      
      {/* Main content */}
      <div className="p-4 space-y-4">
        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center py-8">
            <div className="animate-spin rounded-full h-10 w-10 border-4 border-purple-500 border-t-transparent mb-3" />
            <p className="text-gray-600">Fusion en cours...</p>
          </div>
        )}
        
        {/* Error state */}
        {error && (
          <div className="p-4 bg-red-50 rounded-lg text-red-700 text-sm">
            <p className="font-medium">Erreur de fusion</p>
            <p className="text-xs mt-1">{error}</p>
          </div>
        )}
        
        {/* Results */}
        {isLoaded && !loading && (
          <>
            {/* Main score */}
            <div className="flex justify-center">
              <div className="text-center">
                <CircularGauge 
                  score={globalScore ?? 0} 
                  size={140}
                  strokeWidth={12}
                  showLabel={false}
                />
                <div className="mt-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${levelConfig.bg} ${levelConfig.text}`}>
                    {levelConfig.label}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Suite scores */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-emerald-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span>🗺️</span>
                  <span className="text-sm font-medium text-gray-700">Géo-Suite</span>
                </div>
                <div className="flex items-end gap-1">
                  <span className="text-2xl font-bold text-emerald-600">
                    {Math.round(geoScore ?? 0)}
                  </span>
                  <span className="text-sm text-gray-400 mb-1">/100</span>
                </div>
                {showWeights && weights && (
                  <div className="mt-2 text-xs text-gray-500">
                    Poids: {Math.round((weights.suite_weights?.geo_suite ?? 0.5) * 100)}%
                  </div>
                )}
              </div>
              
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span>🧠</span>
                  <span className="text-sm font-medium text-gray-700">Behavior</span>
                </div>
                <div className="flex items-end gap-1">
                  <span className="text-2xl font-bold text-blue-600">
                    {Math.round(behaviorScore ?? 0)}
                  </span>
                  <span className="text-sm text-gray-400 mb-1">/100</span>
                </div>
                {showWeights && weights && (
                  <div className="mt-2 text-xs text-gray-500">
                    Poids: {Math.round((weights.suite_weights?.behavior_suite ?? 0.5) * 100)}%
                  </div>
                )}
              </div>
            </div>
            
            {/* Breakdown */}
            {showBreakdown && data && (
              <div className="pt-3 border-t">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Détail par moteur</h4>
                <BreakdownChart 
                  geoBreakdown={data.geo_breakdown}
                  behaviorBreakdown={data.behavior_breakdown}
                />
              </div>
            )}
            
            {/* Fusion quality */}
            {data && (
              <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg text-xs">
                <span className="text-gray-500">Qualité de fusion</span>
                <span className={`font-medium ${
                  data.fusion_quality === 'excellent' ? 'text-emerald-600' :
                  data.fusion_quality === 'good' ? 'text-blue-600' :
                  'text-amber-600'
                }`}>
                  {data.fusion_quality} ({Math.round(data.fusion_confidence * 100)}%)
                </span>
              </div>
            )}
            
            {/* Recommendations */}
            {showRecommendations && (
              <RecommendationsList recommendations={recommendations} />
            )}
          </>
        )}
        
        {/* Analyze button */}
        {!isLoaded && !loading && (
          <button
            onClick={handleAnalyze}
            className="w-full py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-indigo-600 transition-all"
          >
            🔮 Analyser la Fusion
          </button>
        )}
        
        {/* Refresh button */}
        {isLoaded && !loading && (
          <button
            onClick={handleAnalyze}
            className="w-full py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-all"
          >
            🔄 Rafraîchir l'analyse
          </button>
        )}
      </div>
      
      {/* Footer */}
      <div className="px-4 py-2 bg-gray-50 border-t text-center">
        <span className="text-xs text-gray-500">
          BIONIC™ P2 • BehaviorFusionEngine v1.0.0
        </span>
      </div>
    </div>
  );
}

FusionScorePanel.propTypes = {
  lat: PropTypes.number,
  lon: PropTypes.number,
  species: PropTypes.string,
  territory: PropTypes.string,
  radiusKm: PropTypes.number,
  autoLoad: PropTypes.bool,
  showWeights: PropTypes.bool,
  showBreakdown: PropTypes.bool,
  showRecommendations: PropTypes.bool,
  onAnalyzeComplete: PropTypes.func
};

// =============================================================================
// EXPORTS
// =============================================================================

export default FusionScorePanel;
