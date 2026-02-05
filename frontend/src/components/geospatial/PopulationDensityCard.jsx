/**
 * BIONIC™ P1 - PopulationDensityCard
 * ====================================
 * Visualisation des résultats du populationDensityEngine.
 * 
 * @version 1.0.0
 * @architecture P2-Ready avec getFusionOutput()
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { CircularGauge, LinearGauge } from './GeoSuiteScoreGauge';

// Density category configurations
const DENSITY_CATEGORIES = {
  high: { label: 'Élevée', color: '#4CAF50', bgColor: '#E8F5E9' },
  medium: { label: 'Moyenne', color: '#FF9800', bgColor: '#FFF3E0' },
  low: { label: 'Faible', color: '#F44336', bgColor: '#FFEBEE' },
  very_low: { label: 'Très faible', color: '#9E9E9E', bgColor: '#F5F5F5' }
};

// Trend configurations
const TRENDS = {
  increasing: { label: 'En hausse', icon: '📈', color: '#4CAF50' },
  stable: { label: 'Stable', icon: '➡️', color: '#2196F3' },
  decreasing: { label: 'En baisse', icon: '📉', color: '#F44336' },
  unknown: { label: 'Inconnu', icon: '❓', color: '#9E9E9E' }
};

// =============================================================================
// SPECIES DENSITY ITEM
// =============================================================================

function SpeciesDensityItem({ species, data }) {
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
  
  const density = data.density_per_100km2 ?? 0;
  const trend = data.trend ?? 'unknown';
  const category = data.density_category ?? 'low';
  const confidence = data.confidence ?? 0.5;
  
  const trendConfig = TRENDS[trend] || TRENDS.unknown;
  const categoryConfig = DENSITY_CATEGORIES[category] || DENSITY_CATEGORIES.low;
  
  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{speciesIcons[species] || '🎯'}</span>
          <span className="font-medium text-gray-900 capitalize">{species}</span>
        </div>
        <span 
          className="text-xs px-2 py-0.5 rounded-full flex items-center gap-1"
          style={{ backgroundColor: trendConfig.color + '20', color: trendConfig.color }}
        >
          {trendConfig.icon} {trendConfig.label}
        </span>
      </div>
      
      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-2xl font-bold" style={{ color: categoryConfig.color }}>
          {density.toFixed(1)}
        </span>
        <span className="text-sm text-gray-500">/100 km²</span>
      </div>
      
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">Confiance:</span>
        <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 rounded-full"
            style={{ width: `${confidence * 100}%` }}
          />
        </div>
        <span className="text-xs text-gray-500">{Math.round(confidence * 100)}%</span>
      </div>
    </div>
  );
}

// =============================================================================
// HARVEST DATA DISPLAY
// =============================================================================

function HarvestDataDisplay({ harvestData }) {
  if (!harvestData || Object.keys(harvestData).length === 0) return null;
  
  const speciesIcons = {
    deer: '🦌',
    moose: '🫎',
    bear: '🐻',
    turkey: '🦃'
  };
  
  return (
    <div className="grid grid-cols-2 gap-3">
      {Object.entries(harvestData).slice(0, 4).map(([species, data]) => {
        const avgAnnual = data.avg_annual ?? 0;
        const successRate = data.success_rate ?? 0;
        
        return (
          <div key={species} className="p-2 bg-indigo-50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <span>{speciesIcons[species] || '🎯'}</span>
              <span className="text-sm font-medium text-gray-700 capitalize">{species}</span>
            </div>
            <p className="text-xs text-gray-500">
              Moy. annuelle: <span className="font-semibold text-indigo-600">{avgAnnual.toLocaleString()}</span>
            </p>
            <p className="text-xs text-gray-500">
              Taux succès: <span className="font-semibold text-indigo-600">{(successRate * 100).toFixed(0)}%</span>
            </p>
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// MAIN CARD
// =============================================================================

export function PopulationDensityCard({ data, loading = false, compact = false }) {
  // Extract data safely
  const score = data?.score ?? 0;
  const level = data?.level ?? 'unknown';
  const densityCategory = data?.data?.density_category ?? 'low';
  const speciesDensities = data?.data?.species_densities ?? {};
  const overallTrend = data?.data?.overall_trend ?? 'unknown';
  const harvestPressure = data?.data?.harvest_pressure ?? 0;
  const harvestData = data?.data?.harvest_data ?? {};
  const subRegion = data?.data?.sub_region ?? 'unknown';
  const dataYearRange = data?.data?.data_year_range ?? '2015-2024';
  const recommendations = data?.recommendations ?? [];
  
  const categoryConfig = DENSITY_CATEGORIES[densityCategory] || DENSITY_CATEGORIES.low;
  const trendConfig = TRENDS[overallTrend] || TRENDS.unknown;
  
  // Fusion output for P2
  const getFusionOutput = useMemo(() => ({
    score_normalized: score / 100,
    confidence: data?.confidence ?? 0.7,
    engine: 'population',
    weight_suggestion: 0.2,
    harvest_pressure: harvestPressure
  }), [score, data?.confidence, harvestPressure]);
  
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
        <span className="text-2xl mb-2 block">📊</span>
        <p className="text-sm">Analyse de densité non disponible</p>
      </div>
    );
  }
  
  // Compact version
  if (compact) {
    return (
      <div className="bg-white rounded-xl border p-4" data-testid="population-card-compact">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📊</span>
            <div>
              <h4 className="font-semibold text-gray-900">Densité</h4>
              <p className="text-xs flex items-center gap-1" style={{ color: trendConfig.color }}>
                {trendConfig.icon} {trendConfig.label}
              </p>
            </div>
          </div>
          <CircularGauge score={score} size={60} strokeWidth={6} />
        </div>
      </div>
    );
  }
  
  // Full version
  return (
    <div className="bg-white rounded-xl border overflow-hidden" data-testid="population-card">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📊</span>
            <div>
              <h3 className="font-bold text-gray-900">Densité de Population</h3>
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span 
                  className="px-2 py-0.5 rounded-full text-xs"
                  style={{ backgroundColor: categoryConfig.bgColor, color: categoryConfig.color }}
                >
                  {categoryConfig.label}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1" style={{ color: trendConfig.color }}>
                  {trendConfig.icon} {trendConfig.label}
                </span>
              </p>
            </div>
          </div>
          <CircularGauge score={score} size={80} strokeWidth={8} />
        </div>
      </div>
      
      {/* Sub-region & Data range */}
      <div className="px-4 py-2 bg-gray-50 border-b flex justify-between text-xs text-gray-500">
        <span>📍 Sous-région: {subRegion}</span>
        <span>📅 Données: {dataYearRange}</span>
      </div>
      
      {/* Species Densities */}
      {Object.keys(speciesDensities).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Densités par espèce</h4>
          <div className="space-y-2">
            {Object.entries(speciesDensities).slice(0, 4).map(([species, speciesData]) => (
              <SpeciesDensityItem key={species} species={species} data={speciesData} />
            ))}
          </div>
        </div>
      )}
      
      {/* Harvest Pressure */}
      <div className="p-4 border-b">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Pression de récolte</h4>
        <LinearGauge 
          score={harvestPressure * 100} 
          height={8}
          showValue={true}
          showLevel={true}
        />
      </div>
      
      {/* Harvest Data */}
      {Object.keys(harvestData).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Statistiques de récolte</h4>
          <HarvestDataDisplay harvestData={harvestData} />
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

PopulationDensityCard.propTypes = {
  data: PropTypes.shape({
    score: PropTypes.number,
    level: PropTypes.string,
    confidence: PropTypes.number,
    data: PropTypes.shape({
      density_category: PropTypes.string,
      species_densities: PropTypes.object,
      overall_trend: PropTypes.string,
      harvest_pressure: PropTypes.number,
      harvest_data: PropTypes.object,
      sub_region: PropTypes.string,
      data_year_range: PropTypes.string
    }),
    recommendations: PropTypes.array
  }),
  loading: PropTypes.bool,
  compact: PropTypes.bool
};

// P2 Interface
PopulationDensityCard.getFusionOutput = (data) => ({
  score_normalized: (data?.score ?? 0) / 100,
  confidence: data?.confidence ?? 0.7,
  engine: 'population',
  weight_suggestion: 0.2
});

export default PopulationDensityCard;
