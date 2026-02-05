/**
 * BIONIC™ P1 - CorridorAnalysisCard
 * ==================================
 * Visualisation des résultats du corridorEngine.
 * 
 * @version 1.0.0
 * @architecture P2-Ready avec getFusionOutput()
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { CircularGauge, LinearGauge } from './GeoSuiteScoreGauge';

// Corridor type configurations
const CORRIDOR_TYPES = {
  riparian: { label: 'Riparian', icon: '🌊', color: '#2196F3' },
  ridgeline: { label: 'Crête', icon: '⛰️', color: '#4CAF50' },
  forest_edge: { label: 'Lisière', icon: '🌲', color: '#8BC34A' },
  valley: { label: 'Vallée', icon: '🏞️', color: '#009688' },
  agricultural_edge: { label: 'Agricole', icon: '🌾', color: '#FFC107' }
};

// =============================================================================
// CORRIDOR ITEM
// =============================================================================

function CorridorItem({ corridor }) {
  const config = CORRIDOR_TYPES[corridor.type] || { label: corridor.type, icon: '📍', color: '#9E9E9E' };
  
  return (
    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2">
        <span>{config.icon}</span>
        <span className="text-sm font-medium text-gray-700">{config.label}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs text-gray-500">{corridor.length_km?.toFixed(1)} km</span>
        <div 
          className="w-16 h-2 rounded-full overflow-hidden bg-gray-200"
        >
          <div 
            className="h-full rounded-full transition-all"
            style={{ 
              width: `${corridor.score || 50}%`,
              backgroundColor: config.color
            }}
          />
        </div>
        <span className="text-sm font-semibold" style={{ color: config.color }}>
          {corridor.score || 50}
        </span>
      </div>
    </div>
  );
}

// =============================================================================
// SPECIES SCORE ITEM
// =============================================================================

function SpeciesScoreItem({ species, score }) {
  const speciesIcons = {
    deer: '🦌',
    moose: '🫎',
    bear: '🐻',
    turkey: '🦃',
    waterfowl: '🦆',
    smallgame: '🐰'
  };
  
  return (
    <div className="flex items-center justify-between py-1">
      <div className="flex items-center gap-2">
        <span>{speciesIcons[species] || '🎯'}</span>
        <span className="text-sm text-gray-700 capitalize">{species}</span>
      </div>
      <span className="font-semibold text-gray-900">{Math.round(score)}</span>
    </div>
  );
}

// =============================================================================
// MAIN CARD
// =============================================================================

export function CorridorAnalysisCard({ data, loading = false, compact = false }) {
  // Extract data safely
  const score = data?.score ?? 0;
  const level = data?.level ?? 'unknown';
  const corridors = data?.data?.corridors ?? [];
  const corridorsCount = data?.data?.corridors_count ?? corridors.length;
  const connectivityIndex = data?.data?.connectivity_index ?? 0;
  const speciesScores = data?.data?.species_scores ?? {};
  const seasonalScores = data?.data?.seasonal_scores ?? {};
  const recommendations = data?.recommendations ?? [];
  
  // Fusion output for P2
  const getFusionOutput = useMemo(() => ({
    score_normalized: score / 100,
    confidence: data?.confidence ?? 0.7,
    engine: 'corridor',
    weight_suggestion: 0.2,
    connectivity_factor: connectivityIndex
  }), [score, data?.confidence, connectivityIndex]);
  
  if (loading) {
    return (
      <div className="bg-white rounded-xl border p-4 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-20 bg-gray-200 rounded mb-4" />
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </div>
      </div>
    );
  }
  
  if (!data) {
    return (
      <div className="bg-white rounded-xl border p-4 text-center text-gray-500">
        <span className="text-2xl mb-2 block">🛤️</span>
        <p className="text-sm">Analyse des corridors non disponible</p>
      </div>
    );
  }
  
  // Compact version
  if (compact) {
    return (
      <div className="bg-white rounded-xl border p-4" data-testid="corridor-card-compact">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🛤️</span>
            <div>
              <h4 className="font-semibold text-gray-900">Corridors</h4>
              <p className="text-xs text-gray-500">{corridorsCount} détectés</p>
            </div>
          </div>
          <CircularGauge score={score} size={60} strokeWidth={6} />
        </div>
      </div>
    );
  }
  
  // Full version
  return (
    <div className="bg-white rounded-xl border overflow-hidden" data-testid="corridor-card">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-emerald-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🛤️</span>
            <div>
              <h3 className="font-bold text-gray-900">Corridors Fauniques</h3>
              <p className="text-sm text-gray-500">
                {corridorsCount} corridor{corridorsCount > 1 ? 's' : ''} • Connectivité {Math.round(connectivityIndex * 100)}%
              </p>
            </div>
          </div>
          <CircularGauge score={score} size={80} strokeWidth={8} />
        </div>
      </div>
      
      {/* Corridors List */}
      {corridors.length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Corridors détectés</h4>
          <div className="space-y-2">
            {corridors.slice(0, 5).map((corridor, idx) => (
              <CorridorItem key={idx} corridor={corridor} />
            ))}
          </div>
        </div>
      )}
      
      {/* Species Scores */}
      {Object.keys(speciesScores).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Scores par espèce</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(speciesScores).slice(0, 4).map(([species, speciesScore]) => (
              <SpeciesScoreItem key={species} species={species} score={speciesScore} />
            ))}
          </div>
        </div>
      )}
      
      {/* Connectivity Index */}
      <div className="p-4 border-b">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Indice de connectivité</h4>
        <LinearGauge 
          score={connectivityIndex * 100} 
          height={8}
          showValue={true}
          showLevel={false}
        />
      </div>
      
      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="p-4 bg-gray-50">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Recommandations</h4>
          <ul className="space-y-1">
            {recommendations.slice(0, 3).map((rec, idx) => (
              <li key={idx} className="text-sm text-gray-600">{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

CorridorAnalysisCard.propTypes = {
  data: PropTypes.shape({
    score: PropTypes.number,
    level: PropTypes.string,
    confidence: PropTypes.number,
    data: PropTypes.shape({
      corridors: PropTypes.array,
      corridors_count: PropTypes.number,
      connectivity_index: PropTypes.number,
      species_scores: PropTypes.object,
      seasonal_scores: PropTypes.object
    }),
    recommendations: PropTypes.array
  }),
  loading: PropTypes.bool,
  compact: PropTypes.bool
};

// P2 Interface
CorridorAnalysisCard.getFusionOutput = (data) => ({
  score_normalized: (data?.score ?? 0) / 100,
  confidence: data?.confidence ?? 0.7,
  engine: 'corridor',
  weight_suggestion: 0.2
});

export default CorridorAnalysisCard;
