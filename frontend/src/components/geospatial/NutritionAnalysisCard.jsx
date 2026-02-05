/**
 * BIONIC™ P1 - NutritionAnalysisCard
 * ====================================
 * Visualisation des résultats du nutritionEngine.
 * 
 * @version 1.0.0
 * @architecture P2-Ready avec getFusionOutput()
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { CircularGauge, LinearGauge } from './GeoSuiteScoreGauge';

// Season configurations
const SEASONS = {
  spring: { label: 'Printemps', icon: '🌱', color: '#8BC34A' },
  summer: { label: 'Été', icon: '☀️', color: '#FFC107' },
  fall: { label: 'Automne', icon: '🍂', color: '#FF9800' },
  winter: { label: 'Hiver', icon: '❄️', color: '#03A9F4' }
};

// Food availability levels
const AVAILABILITY_LEVELS = {
  abundant: { label: 'Abondante', color: '#00C853', bgColor: '#E8F5E9' },
  moderate: { label: 'Modérée', color: '#FF9800', bgColor: '#FFF3E0' },
  scarce: { label: 'Rare', color: '#F44336', bgColor: '#FFEBEE' }
};

// =============================================================================
// MAST INDEX DISPLAY
// =============================================================================

function MastIndexDisplay({ mastIndex }) {
  if (!mastIndex) return null;
  
  const score = mastIndex.score ?? 0;
  const trend = mastIndex.year_trend ?? 'average';
  
  const trendConfig = {
    good: { label: 'Bonne année', icon: '📈', color: '#4CAF50' },
    average: { label: 'Année moyenne', icon: '➡️', color: '#FF9800' },
    poor: { label: 'Faible année', icon: '📉', color: '#F44336' }
  };
  
  const config = trendConfig[trend] || trendConfig.average;
  
  return (
    <div className="p-3 bg-amber-50 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">Indice de glandée</span>
        <span 
          className="text-xs px-2 py-0.5 rounded-full"
          style={{ backgroundColor: config.color + '20', color: config.color }}
        >
          {config.icon} {config.label}
        </span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-2xl">🌰</span>
        <div className="flex-1">
          <LinearGauge 
            score={score} 
            height={8}
            showValue={false}
            showLevel={false}
          />
        </div>
        <span className="font-bold text-amber-700">{Math.round(score)}</span>
      </div>
    </div>
  );
}

// =============================================================================
// SPECIES NUTRITION LIST
// =============================================================================

function SpeciesNutritionList({ speciesNutrition }) {
  if (!speciesNutrition || Object.keys(speciesNutrition).length === 0) return null;
  
  const speciesIcons = {
    deer: '🦌',
    moose: '🫎',
    bear: '🐻',
    turkey: '🦃',
    waterfowl: '🦆',
    smallgame: '🐰'
  };
  
  return (
    <div className="space-y-3">
      {Object.entries(speciesNutrition).slice(0, 4).map(([species, data]) => {
        const score = data.score ?? 0;
        const availability = data.food_availability ?? 'moderate';
        const foods = data.primary_foods_available ?? [];
        const deficiencies = data.deficiencies ?? [];
        
        const availConfig = AVAILABILITY_LEVELS[availability] || AVAILABILITY_LEVELS.moderate;
        
        return (
          <div key={species} className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xl">{speciesIcons[species] || '🎯'}</span>
                <span className="font-medium text-gray-900 capitalize">{species}</span>
              </div>
              <span 
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ backgroundColor: availConfig.bgColor, color: availConfig.color }}
              >
                {availConfig.label}
              </span>
            </div>
            
            <LinearGauge 
              score={score} 
              height={6}
              showValue={true}
              showLevel={false}
            />
            
            {foods.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {foods.slice(0, 3).map((food, idx) => (
                  <span key={idx} className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
                    {food}
                  </span>
                ))}
              </div>
            )}
            
            {deficiencies.length > 0 && (
              <div className="mt-2">
                <span className="text-xs text-red-600">⚠️ {deficiencies[0]}</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// MAIN CARD
// =============================================================================

export function NutritionAnalysisCard({ data, loading = false, compact = false }) {
  // Extract data safely
  const score = data?.score ?? 0;
  const level = data?.level ?? 'unknown';
  const foodAvailability = data?.data?.food_availability ?? 'moderate';
  const speciesNutrition = data?.data?.species_nutrition ?? {};
  const mastIndex = data?.data?.mast_index ?? null;
  const browseQuality = data?.data?.browse_quality ?? 0;
  const currentSeason = data?.data?.current_season ?? 'unknown';
  const seasonalVariation = data?.data?.seasonal_variation ?? {};
  const recommendations = data?.recommendations ?? [];
  
  const seasonConfig = SEASONS[currentSeason] || { label: currentSeason, icon: '📅', color: '#9E9E9E' };
  const availConfig = AVAILABILITY_LEVELS[foodAvailability] || AVAILABILITY_LEVELS.moderate;
  
  // Fusion output for P2
  const getFusionOutput = useMemo(() => ({
    score_normalized: score / 100,
    confidence: data?.confidence ?? 0.7,
    engine: 'nutrition',
    weight_suggestion: 0.2,
    seasonal_factor: seasonalVariation[currentSeason] ? seasonalVariation[currentSeason] / 100 : 1
  }), [score, data?.confidence, currentSeason, seasonalVariation]);
  
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
        <span className="text-2xl mb-2 block">🍎</span>
        <p className="text-sm">Analyse nutritionnelle non disponible</p>
      </div>
    );
  }
  
  // Compact version
  if (compact) {
    return (
      <div className="bg-white rounded-xl border p-4" data-testid="nutrition-card-compact">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🍎</span>
            <div>
              <h4 className="font-semibold text-gray-900">Nutrition</h4>
              <p className="text-xs" style={{ color: availConfig.color }}>{availConfig.label}</p>
            </div>
          </div>
          <CircularGauge score={score} size={60} strokeWidth={6} />
        </div>
      </div>
    );
  }
  
  // Full version
  return (
    <div className="bg-white rounded-xl border overflow-hidden" data-testid="nutrition-card">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🍎</span>
            <div>
              <h3 className="font-bold text-gray-900">Indice Nutritionnel</h3>
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span>{seasonConfig.icon} {seasonConfig.label}</span>
                <span>•</span>
                <span style={{ color: availConfig.color }}>{availConfig.label}</span>
              </p>
            </div>
          </div>
          <CircularGauge score={score} size={80} strokeWidth={8} />
        </div>
      </div>
      
      {/* Mast Index */}
      {mastIndex && (
        <div className="p-4 border-b">
          <MastIndexDisplay mastIndex={mastIndex} />
        </div>
      )}
      
      {/* Browse Quality */}
      <div className="p-4 border-b">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Qualité du brout</h4>
        <LinearGauge 
          score={browseQuality} 
          height={8}
          showValue={true}
          showLevel={true}
        />
      </div>
      
      {/* Species Nutrition */}
      {Object.keys(speciesNutrition).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Nutrition par espèce</h4>
          <SpeciesNutritionList speciesNutrition={speciesNutrition} />
        </div>
      )}
      
      {/* Seasonal Variation */}
      {Object.keys(seasonalVariation).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Variation saisonnière</h4>
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(SEASONS).map(([season, config]) => {
              const value = seasonalVariation[season] ?? 50;
              const isCurrent = season === currentSeason;
              
              return (
                <div 
                  key={season}
                  className={`text-center p-2 rounded-lg ${isCurrent ? 'bg-amber-100 ring-2 ring-amber-400' : 'bg-gray-50'}`}
                >
                  <span className="text-lg">{config.icon}</span>
                  <p className="text-xs text-gray-500 mt-1">{config.label}</p>
                  <p className="font-bold" style={{ color: config.color }}>{Math.round(value)}</p>
                </div>
              );
            })}
          </div>
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

NutritionAnalysisCard.propTypes = {
  data: PropTypes.shape({
    score: PropTypes.number,
    level: PropTypes.string,
    confidence: PropTypes.number,
    data: PropTypes.shape({
      food_availability: PropTypes.string,
      species_nutrition: PropTypes.object,
      mast_index: PropTypes.object,
      browse_quality: PropTypes.number,
      current_season: PropTypes.string,
      seasonal_variation: PropTypes.object
    }),
    recommendations: PropTypes.array
  }),
  loading: PropTypes.bool,
  compact: PropTypes.bool
};

// P2 Interface
NutritionAnalysisCard.getFusionOutput = (data) => ({
  score_normalized: (data?.score ?? 0) / 100,
  confidence: data?.confidence ?? 0.7,
  engine: 'nutrition',
  weight_suggestion: 0.2
});

export default NutritionAnalysisCard;
