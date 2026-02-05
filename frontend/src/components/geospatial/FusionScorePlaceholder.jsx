/**
 * BIONIC™ P1.5 - Fusion Score Placeholder
 * =========================================
 * Placeholder UI pour le score global fusionné (P2).
 * Préparation pour BehaviorFusionEngine.
 * 
 * @version 1.0.0
 * @architecture P2-Ready
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import useGeoSuiteStore from '../../stores/geoSuiteStore';
import { CircularGauge } from './GeoSuiteScoreGauge';

// =============================================================================
// FUSION SCORE DISPLAY
// =============================================================================

export function FusionScorePlaceholder({ 
  behaviorScore = null,
  showBehavior = false,
  showProjected = true
}) {
  const { analysisResults, getGlobalScore, getFusionOutput } = useGeoSuiteStore();
  
  // Calculate geospatial score
  const geoScore = useMemo(() => {
    return getGlobalScore();
  }, [getGlobalScore]);
  
  // Get fusion output for P2
  const fusionOutput = useMemo(() => {
    return getFusionOutput();
  }, [getFusionOutput]);
  
  // Project fusion score (placeholder calculation)
  const projectedFusionScore = useMemo(() => {
    if (geoScore === null) return null;
    
    if (behaviorScore !== null) {
      // If we have behavior score, calculate weighted fusion
      return Math.round((geoScore * 0.5) + (behaviorScore * 0.5));
    }
    
    // Otherwise, just return geo score
    return geoScore;
  }, [geoScore, behaviorScore]);
  
  // Individual engine scores
  const engineScores = useMemo(() => {
    const scores = [];
    
    if (analysisResults.corridor?.score !== undefined) {
      scores.push({ name: 'Corridors', icon: '🛤️', score: analysisResults.corridor.score, category: 'geo' });
    }
    if (analysisResults.landcover?.score !== undefined) {
      scores.push({ name: 'Couvert', icon: '🌲', score: analysisResults.landcover.score, category: 'geo' });
    }
    if (analysisResults.nutrition?.score !== undefined) {
      scores.push({ name: 'Nutrition', icon: '🍎', score: analysisResults.nutrition.score, category: 'geo' });
    }
    if (analysisResults.population?.score !== undefined) {
      scores.push({ name: 'Population', icon: '📊', score: analysisResults.population.score, category: 'geo' });
    }
    if (analysisResults.pressure?.score !== undefined) {
      scores.push({ name: 'Pression', icon: '🎯', score: analysisResults.pressure.score, category: 'geo' });
    }
    
    return scores;
  }, [analysisResults]);
  
  // No data
  if (geoScore === null && behaviorScore === null) {
    return (
      <div 
        className="p-6 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 text-center"
        data-testid="fusion-score-placeholder"
      >
        <span className="text-4xl mb-2 block">🔮</span>
        <p className="text-gray-600 font-medium">Score de Fusion</p>
        <p className="text-sm text-gray-500 mt-1">
          Lancez une analyse pour voir le score fusionné
        </p>
        
        {/* P2 info */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <span className="text-xs text-purple-600">
            ⏳ BehaviorFusionEngine (P2) bientôt disponible
          </span>
        </div>
      </div>
    );
  }
  
  return (
    <div 
      className="p-4 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl border border-purple-200"
      data-testid="fusion-score-display"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🔮</span>
          <div>
            <h3 className="font-bold text-gray-900">Score de Fusion</h3>
            <p className="text-xs text-gray-500">
              {showBehavior ? 'Géospatial + Comportement' : 'Géospatial uniquement (P1)'}
            </p>
          </div>
        </div>
        
        {/* P2 badge */}
        {!showBehavior && (
          <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
            P2 Ready
          </span>
        )}
      </div>
      
      {/* Main score */}
      <div className="flex items-center justify-center mb-4">
        <div className="relative">
          <CircularGauge 
            score={projectedFusionScore ?? 0} 
            size={120} 
            strokeWidth={10}
          />
          
          {/* Fusion indicator */}
          <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 bg-white px-2 py-0.5 rounded-full shadow text-xs">
            {showBehavior ? '🔄 Fusionné' : '🗺️ Géo'}
          </div>
        </div>
      </div>
      
      {/* Score breakdown */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        {/* Geospatial score */}
        <div className="p-3 bg-white rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <span>🗺️</span>
            <span className="text-xs text-gray-500">Géospatial</span>
          </div>
          <span className="text-xl font-bold text-emerald-600">
            {geoScore ?? '—'}
          </span>
          <span className="text-xs text-gray-400">/100</span>
        </div>
        
        {/* Behavior score (P2) */}
        <div className={`p-3 rounded-lg ${showBehavior ? 'bg-white' : 'bg-gray-100'}`}>
          <div className="flex items-center gap-2 mb-1">
            <span>🧠</span>
            <span className="text-xs text-gray-500">Comportement</span>
          </div>
          {showBehavior && behaviorScore !== null ? (
            <>
              <span className="text-xl font-bold text-blue-600">
                {behaviorScore}
              </span>
              <span className="text-xs text-gray-400">/100</span>
            </>
          ) : (
            <span className="text-sm text-gray-400">P2</span>
          )}
        </div>
      </div>
      
      {/* Engine scores */}
      <div className="space-y-1">
        {engineScores.map((engine, idx) => (
          <div key={idx} className="flex items-center justify-between py-1">
            <div className="flex items-center gap-2">
              <span>{engine.icon}</span>
              <span className="text-xs text-gray-600">{engine.name}</span>
            </div>
            <span className="text-sm font-medium text-gray-900">{Math.round(engine.score)}</span>
          </div>
        ))}
      </div>
      
      {/* P2 teaser */}
      {!showBehavior && (
        <div className="mt-4 pt-3 border-t border-purple-200">
          <div className="flex items-center gap-2 text-xs text-purple-600">
            <span>⏳</span>
            <span>Phase P2: Fusion avec Behavior Suite pour score combiné</span>
          </div>
        </div>
      )}
      
      {/* Fusion output info (for debugging/P2 prep) */}
      {showProjected && (
        <div className="mt-3 p-2 bg-purple-100/50 rounded text-xs text-purple-700">
          <code>getFusionOutput() ready: {Object.keys(fusionOutput.engines).length} engines</code>
        </div>
      )}
    </div>
  );
}

FusionScorePlaceholder.propTypes = {
  behaviorScore: PropTypes.number,
  showBehavior: PropTypes.bool,
  showProjected: PropTypes.bool
};

// =============================================================================
// MINI FUSION INDICATOR
// =============================================================================

export function MiniFusionIndicator({ geoScore, behaviorScore = null }) {
  const fusionScore = useMemo(() => {
    if (geoScore === null) return null;
    if (behaviorScore !== null) {
      return Math.round((geoScore * 0.5) + (behaviorScore * 0.5));
    }
    return geoScore;
  }, [geoScore, behaviorScore]);
  
  if (fusionScore === null) return null;
  
  const getColor = (score) => {
    if (score >= 70) return '#00C853';
    if (score >= 40) return '#FF9800';
    return '#F44336';
  };
  
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-purple-50 rounded-full">
      <span>🔮</span>
      <span 
        className="font-bold"
        style={{ color: getColor(fusionScore) }}
      >
        {fusionScore}
      </span>
      <span className="text-xs text-gray-500">/100</span>
    </div>
  );
}

MiniFusionIndicator.propTypes = {
  geoScore: PropTypes.number,
  behaviorScore: PropTypes.number
};

// =============================================================================
// EXPORTS
// =============================================================================

export default FusionScorePlaceholder;
