/**
 * BIONIC™ P1.5 - Species Mode Panel
 * ===================================
 * Panneau de mode espèce avec presets automatiques avancés.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import React, { useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import useGeoSuiteStore, { SPECIES_CONFIG, LAYER_CONFIG } from '../../stores/geoSuiteStore';

// =============================================================================
// SPECIES DETAIL CARD
// =============================================================================

function SpeciesDetailCard({ species, config, isSelected, onSelect, analysisResults }) {
  // Get score for this species from analysis results
  const speciesScore = useMemo(() => {
    if (!analysisResults) return null;
    
    const scores = [];
    
    // Get from corridor
    if (analysisResults.corridor?.data?.species_scores?.[species]) {
      scores.push(analysisResults.corridor.data.species_scores[species]);
    }
    
    // Get from landcover
    if (analysisResults.landcover?.data?.species_habitat_scores?.[species]) {
      scores.push(analysisResults.landcover.data.species_habitat_scores[species]);
    }
    
    // Get from nutrition
    if (analysisResults.nutrition?.data?.species_nutrition?.[species]?.score) {
      scores.push(analysisResults.nutrition.data.species_nutrition[species].score);
    }
    
    if (scores.length === 0) return null;
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  }, [analysisResults, species]);
  
  return (
    <button
      onClick={() => onSelect(species)}
      className={`
        relative flex flex-col p-4 rounded-xl border-2 transition-all duration-200 text-left
        ${isSelected 
          ? 'border-emerald-500 bg-emerald-50 shadow-md' 
          : 'border-gray-200 bg-white hover:border-emerald-300 hover:shadow-sm'
        }
      `}
      data-testid={`species-detail-card-${species}`}
    >
      {/* Score badge */}
      {speciesScore !== null && (
        <div 
          className={`
            absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold
            ${speciesScore >= 70 ? 'bg-green-500' : speciesScore >= 40 ? 'bg-yellow-500' : 'bg-red-500'}
          `}
        >
          {speciesScore}
        </div>
      )}
      
      {/* Icon and name */}
      <div className="flex items-center gap-3 mb-2">
        <span className="text-4xl">{config.icon}</span>
        <div>
          <span className={`font-semibold block ${isSelected ? 'text-emerald-700' : 'text-gray-900'}`}>
            {config.name}
          </span>
          <span className="text-xs text-gray-500">
            {config.defaultLayers.length} couches actives
          </span>
        </div>
      </div>
      
      {/* Active layers preview */}
      <div className="flex flex-wrap gap-1 mt-2">
        {config.defaultLayers.map(layerId => {
          const layerConfig = LAYER_CONFIG[layerId];
          return (
            <span 
              key={layerId}
              className={`text-xs px-2 py-0.5 rounded-full ${
                isSelected ? 'bg-emerald-200 text-emerald-700' : 'bg-gray-100 text-gray-600'
              }`}
            >
              {layerConfig?.icon} {layerConfig?.name || layerId}
            </span>
          );
        })}
      </div>
      
      {/* Water requirement indicator */}
      {config.water_requirement && (
        <div className="mt-2 text-xs text-gray-500">
          💧 Besoin en eau: {config.water_requirement}
        </div>
      )}
    </button>
  );
}

// =============================================================================
// SPECIES COMPARISON
// =============================================================================

function SpeciesComparison({ analysisResults }) {
  const speciesScores = useMemo(() => {
    if (!analysisResults) return {};
    
    const scores = {};
    
    Object.keys(SPECIES_CONFIG).forEach(species => {
      const speciesScoresArr = [];
      
      // Collect scores from all engines
      if (analysisResults.corridor?.data?.species_scores?.[species]) {
        speciesScoresArr.push(analysisResults.corridor.data.species_scores[species]);
      }
      if (analysisResults.landcover?.data?.species_habitat_scores?.[species]) {
        speciesScoresArr.push(analysisResults.landcover.data.species_habitat_scores[species]);
      }
      if (analysisResults.nutrition?.data?.species_nutrition?.[species]?.score) {
        speciesScoresArr.push(analysisResults.nutrition.data.species_nutrition[species].score);
      }
      
      if (speciesScoresArr.length > 0) {
        scores[species] = Math.round(speciesScoresArr.reduce((a, b) => a + b, 0) / speciesScoresArr.length);
      }
    });
    
    return scores;
  }, [analysisResults]);
  
  const sortedSpecies = useMemo(() => {
    return Object.entries(speciesScores)
      .sort((a, b) => b[1] - a[1]);
  }, [speciesScores]);
  
  if (sortedSpecies.length === 0) return null;
  
  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">Classement habitat</h4>
      <div className="space-y-2">
        {sortedSpecies.slice(0, 4).map(([species, score], index) => {
          const config = SPECIES_CONFIG[species];
          const getBarColor = (s) => {
            if (s >= 70) return 'bg-green-500';
            if (s >= 40) return 'bg-yellow-500';
            return 'bg-red-500';
          };
          
          return (
            <div key={species} className="flex items-center gap-2">
              <span className="text-sm w-4 text-gray-500">#{index + 1}</span>
              <span className="text-lg">{config?.icon}</span>
              <div className="flex-1">
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${getBarColor(score)}`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
              <span className="text-sm font-semibold text-gray-700 w-8 text-right">{score}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// =============================================================================
// MAIN SPECIES MODE PANEL
// =============================================================================

export function SpeciesModePanel({ 
  onSpeciesChange,
  showComparison = true,
  showLayerPreview = true,
  layout = 'grid'
}) {
  const { 
    selectedSpecies, 
    applySpeciesPreset,
    activeLayers,
    analysisResults
  } = useGeoSuiteStore();
  
  const handleSelect = useCallback((species) => {
    applySpeciesPreset(species);
    onSpeciesChange?.(species);
  }, [applySpeciesPreset, onSpeciesChange]);
  
  const currentConfig = SPECIES_CONFIG[selectedSpecies];
  
  const layoutClasses = {
    grid: 'grid grid-cols-2 md:grid-cols-3 gap-3',
    list: 'flex flex-col gap-2',
    horizontal: 'flex gap-3 overflow-x-auto pb-2'
  };
  
  return (
    <div className="space-y-4" data-testid="species-mode-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <span>🎯</span> Mode Espèce
        </h3>
        {currentConfig && (
          <span className="flex items-center gap-2 text-sm text-emerald-600">
            <span>{currentConfig.icon}</span>
            <span>{currentConfig.name}</span>
          </span>
        )}
      </div>
      
      {/* Species selector */}
      <div className={layoutClasses[layout]}>
        {Object.entries(SPECIES_CONFIG).map(([id, config]) => (
          <SpeciesDetailCard
            key={id}
            species={id}
            config={config}
            isSelected={selectedSpecies === id}
            onSelect={handleSelect}
            analysisResults={analysisResults}
          />
        ))}
      </div>
      
      {/* Layer preview */}
      {showLayerPreview && currentConfig && (
        <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
          <h4 className="text-sm font-semibold text-emerald-800 mb-2">
            Couches actives pour {currentConfig.name}
          </h4>
          <div className="flex flex-wrap gap-2">
            {activeLayers.map(layerId => {
              const layerConfig = LAYER_CONFIG[layerId];
              const opacity = currentConfig.layerOpacities?.[layerId] ?? 0.7;
              
              return (
                <div 
                  key={layerId}
                  className="flex items-center gap-2 px-3 py-1.5 bg-white rounded-full border border-emerald-200"
                >
                  <span>{layerConfig?.icon}</span>
                  <span className="text-sm text-gray-700">{layerConfig?.name}</span>
                  <span className="text-xs text-gray-500">{Math.round(opacity * 100)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Species comparison */}
      {showComparison && <SpeciesComparison analysisResults={analysisResults} />}
      
      {/* Tips */}
      <div className="text-xs text-gray-500 italic">
        💡 Sélectionner une espèce active automatiquement les couches optimales
      </div>
    </div>
  );
}

SpeciesModePanel.propTypes = {
  onSpeciesChange: PropTypes.func,
  showComparison: PropTypes.bool,
  showLayerPreview: PropTypes.bool,
  layout: PropTypes.oneOf(['grid', 'list', 'horizontal'])
};

// =============================================================================
// EXPORTS
// =============================================================================

export default SpeciesModePanel;
