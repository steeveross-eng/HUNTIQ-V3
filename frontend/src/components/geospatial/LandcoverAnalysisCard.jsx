/**
 * BIONIC™ P1 - LandcoverAnalysisCard
 * ====================================
 * Visualisation des résultats du landcoverEngine.
 * 
 * @version 1.0.0
 * @architecture P2-Ready avec getFusionOutput()
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { CircularGauge, LinearGauge } from './GeoSuiteScoreGauge';

// Cover type configurations
const COVER_TYPES = {
  deciduous_forest: { label: 'Feuillus', icon: '🌳', color: '#228B22' },
  coniferous_forest: { label: 'Conifères', icon: '🌲', color: '#006400' },
  mixed_forest: { label: 'Mixte', icon: '🌿', color: '#2E8B57' },
  shrubland: { label: 'Arbustes', icon: '🌾', color: '#9ACD32' },
  grassland: { label: 'Prairie', icon: '🌱', color: '#90EE90' },
  wetland: { label: 'Milieu humide', icon: '💧', color: '#4682B4' },
  water: { label: 'Eau', icon: '🌊', color: '#1E90FF' },
  agricultural: { label: 'Agricole', icon: '🚜', color: '#F4A460' },
  urban: { label: 'Urbain', icon: '🏘️', color: '#808080' },
  barren: { label: 'Nu', icon: '🏜️', color: '#D2B48C' }
};

// =============================================================================
// COMPOSITION BAR
// =============================================================================

function CompositionBar({ composition }) {
  if (!composition || composition.length === 0) return null;
  
  // Sort by percent descending
  const sorted = [...composition].sort((a, b) => b.percent - a.percent);
  
  return (
    <div className="space-y-2">
      {sorted.slice(0, 5).map((item, idx) => {
        const config = COVER_TYPES[item.cover_type] || { label: item.cover_type, icon: '📍', color: '#9E9E9E' };
        
        return (
          <div key={idx} className="flex items-center gap-3">
            <div className="flex items-center gap-2 w-28">
              <span>{config.icon}</span>
              <span className="text-sm text-gray-600 truncate">{config.label}</span>
            </div>
            <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full transition-all duration-500"
                style={{ 
                  width: `${item.percent}%`,
                  backgroundColor: config.color
                }}
              />
            </div>
            <span className="text-sm font-medium text-gray-700 w-12 text-right">
              {item.percent.toFixed(0)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// HABITAT SCORE GRID
// =============================================================================

function HabitatScoreGrid({ scores }) {
  if (!scores || Object.keys(scores).length === 0) return null;
  
  const speciesIcons = {
    deer: '🦌',
    moose: '🫎',
    bear: '🐻',
    turkey: '🦃',
    waterfowl: '🦆',
    smallgame: '🐰',
    caribou: '🦌',
    wolf: '🐺'
  };
  
  const entries = Object.entries(scores).slice(0, 6);
  
  return (
    <div className="grid grid-cols-3 gap-2">
      {entries.map(([species, score]) => {
        const getColor = (s) => {
          if (s >= 80) return '#00C853';
          if (s >= 60) return '#4CAF50';
          if (s >= 40) return '#FF9800';
          return '#F44336';
        };
        
        return (
          <div 
            key={species}
            className="flex flex-col items-center p-2 bg-gray-50 rounded-lg"
          >
            <span className="text-xl mb-1">{speciesIcons[species] || '🎯'}</span>
            <span className="text-xs text-gray-500 capitalize">{species}</span>
            <span 
              className="font-bold text-sm"
              style={{ color: getColor(score) }}
            >
              {Math.round(score)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// MAIN CARD
// =============================================================================

export function LandcoverAnalysisCard({ data, loading = false, compact = false }) {
  // Extract data safely
  const score = data?.score ?? 0;
  const level = data?.level ?? 'unknown';
  const dominantCover = data?.data?.dominant_cover ?? 'unknown';
  const composition = data?.data?.cover_composition ?? [];
  const edgeDensity = data?.data?.edge_density_m_ha ?? 0;
  const thermalCover = data?.data?.thermal_cover_percent ?? 0;
  const structuralDiversity = data?.data?.structural_diversity ?? 0;
  const speciesHabitat = data?.data?.species_habitat_scores ?? {};
  const recommendations = data?.recommendations ?? [];
  
  const dominantConfig = COVER_TYPES[dominantCover] || { label: dominantCover, icon: '🌿', color: '#2E8B57' };
  
  // Fusion output for P2
  const getFusionOutput = useMemo(() => ({
    score_normalized: score / 100,
    confidence: data?.confidence ?? 0.7,
    engine: 'landcover',
    weight_suggestion: 0.2,
    thermal_factor: thermalCover / 100,
    diversity_factor: structuralDiversity
  }), [score, data?.confidence, thermalCover, structuralDiversity]);
  
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
        <span className="text-2xl mb-2 block">🌲</span>
        <p className="text-sm">Analyse du couvert non disponible</p>
      </div>
    );
  }
  
  // Compact version
  if (compact) {
    return (
      <div className="bg-white rounded-xl border p-4" data-testid="landcover-card-compact">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{dominantConfig.icon}</span>
            <div>
              <h4 className="font-semibold text-gray-900">Couvert végétal</h4>
              <p className="text-xs text-gray-500">{dominantConfig.label}</p>
            </div>
          </div>
          <CircularGauge score={score} size={60} strokeWidth={6} />
        </div>
      </div>
    );
  }
  
  // Full version
  return (
    <div className="bg-white rounded-xl border overflow-hidden" data-testid="landcover-card">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{dominantConfig.icon}</span>
            <div>
              <h3 className="font-bold text-gray-900">Couvert Végétal</h3>
              <p className="text-sm text-gray-500">
                Dominant: {dominantConfig.label} • Diversité {Math.round(structuralDiversity * 100)}%
              </p>
            </div>
          </div>
          <CircularGauge score={score} size={80} strokeWidth={8} />
        </div>
      </div>
      
      {/* Composition */}
      {composition.length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Composition du couvert</h4>
          <CompositionBar composition={composition} />
        </div>
      )}
      
      {/* Thermal Cover & Edge Density */}
      <div className="p-4 border-b grid grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Couvert thermique</h4>
          <LinearGauge 
            score={thermalCover} 
            height={8}
            showValue={true}
            showLevel={false}
          />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Densité lisières</h4>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-emerald-600">{Math.round(edgeDensity)}</span>
            <span className="text-sm text-gray-500">m/ha</span>
          </div>
        </div>
      </div>
      
      {/* Species Habitat Scores */}
      {Object.keys(speciesHabitat).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Scores d'habitat par espèce</h4>
          <HabitatScoreGrid scores={speciesHabitat} />
        </div>
      )}
      
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

LandcoverAnalysisCard.propTypes = {
  data: PropTypes.shape({
    score: PropTypes.number,
    level: PropTypes.string,
    confidence: PropTypes.number,
    data: PropTypes.shape({
      dominant_cover: PropTypes.string,
      cover_composition: PropTypes.array,
      edge_density_m_ha: PropTypes.number,
      thermal_cover_percent: PropTypes.number,
      structural_diversity: PropTypes.number,
      species_habitat_scores: PropTypes.object
    }),
    recommendations: PropTypes.array
  }),
  loading: PropTypes.bool,
  compact: PropTypes.bool
};

// P2 Interface
LandcoverAnalysisCard.getFusionOutput = (data) => ({
  score_normalized: (data?.score ?? 0) / 100,
  confidence: data?.confidence ?? 0.7,
  engine: 'landcover',
  weight_suggestion: 0.2
});

export default LandcoverAnalysisCard;
