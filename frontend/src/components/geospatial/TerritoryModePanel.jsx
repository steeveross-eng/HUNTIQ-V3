/**
 * BIONIC™ P1.5 - Territory Mode Panel
 * =====================================
 * Panneau de sélection de territoire avec presets automatiques.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import useGeoSuiteStore, { TERRITORY_CONFIG } from '../../stores/geoSuiteStore';

// =============================================================================
// TERRITORY CARD
// =============================================================================

function TerritoryCard({ territory, config, isSelected, onSelect }) {
  return (
    <button
      onClick={() => onSelect(territory)}
      className={`
        flex flex-col p-4 rounded-xl border-2 transition-all duration-200
        ${isSelected 
          ? 'border-blue-500 bg-blue-50 shadow-md' 
          : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-sm'
        }
      `}
      data-testid={`territory-card-${territory}`}
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-3xl">{config.icon}</span>
        <div className="text-left">
          <span className={`font-semibold ${isSelected ? 'text-blue-700' : 'text-gray-900'}`}>
            {config.name}
          </span>
          {isSelected && (
            <span className="block text-xs text-blue-600">
              Centre: {config.center.lat.toFixed(2)}, {config.center.lon.toFixed(2)}
            </span>
          )}
        </div>
      </div>
      
      {/* Data sources */}
      <div className="flex flex-wrap gap-1 mt-2">
        {config.dataSources.slice(0, 4).map(source => (
          <span 
            key={source}
            className={`text-xs px-2 py-0.5 rounded-full ${
              isSelected ? 'bg-blue-200 text-blue-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {source}
          </span>
        ))}
      </div>
    </button>
  );
}

// =============================================================================
// SEASON INFO
// =============================================================================

function SeasonInfo({ territory, species }) {
  const config = TERRITORY_CONFIG[territory];
  const seasonData = config?.seasons?.[species];
  
  if (!seasonData) return null;
  
  return (
    <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
      <div className="flex items-center gap-2 mb-1">
        <span>📅</span>
        <span className="text-sm font-medium text-amber-800">Saison de chasse</span>
      </div>
      <p className="text-sm text-amber-700">
        {seasonData.start} - {seasonData.end}
      </p>
    </div>
  );
}

// =============================================================================
// MAIN TERRITORY MODE PANEL
// =============================================================================

export function TerritoryModePanel({ 
  onTerritoryChange,
  showSeasonInfo = true,
  layout = 'horizontal'
}) {
  const { 
    selectedTerritory, 
    selectedSpecies,
    applyTerritoryPreset,
    analysisLocation
  } = useGeoSuiteStore();
  
  const handleSelect = useCallback((territory) => {
    applyTerritoryPreset(territory);
    onTerritoryChange?.(territory);
  }, [applyTerritoryPreset, onTerritoryChange]);
  
  const layoutClasses = {
    horizontal: 'flex gap-4 overflow-x-auto pb-2',
    vertical: 'flex flex-col gap-3',
    grid: 'grid grid-cols-3 gap-3'
  };
  
  return (
    <div className="space-y-4" data-testid="territory-mode-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <span>🗺️</span> Mode Territoire
        </h3>
        <span className="text-xs text-gray-500">
          {selectedTerritory && TERRITORY_CONFIG[selectedTerritory]?.name}
        </span>
      </div>
      
      {/* Territory selector */}
      <div className={layoutClasses[layout]}>
        {Object.entries(TERRITORY_CONFIG).map(([id, config]) => (
          <TerritoryCard
            key={id}
            territory={id}
            config={config}
            isSelected={selectedTerritory === id}
            onSelect={handleSelect}
          />
        ))}
      </div>
      
      {/* Current location info */}
      <div className="p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>📍</span>
            <span className="text-sm text-gray-700">Position actuelle</span>
          </div>
          <span className="text-sm font-mono text-gray-600">
            {analysisLocation.lat.toFixed(4)}, {analysisLocation.lon.toFixed(4)}
          </span>
        </div>
      </div>
      
      {/* Season info */}
      {showSeasonInfo && (
        <SeasonInfo territory={selectedTerritory} species={selectedSpecies} />
      )}
      
      {/* Quick stats */}
      {selectedTerritory && (
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-white rounded-lg border">
            <span className="text-xs text-gray-500">Sources de données</span>
            <p className="font-semibold text-gray-900">
              {TERRITORY_CONFIG[selectedTerritory]?.dataSources.length || 0}
            </p>
          </div>
          <div className="p-3 bg-white rounded-lg border">
            <span className="text-xs text-gray-500">Zoom par défaut</span>
            <p className="font-semibold text-gray-900">
              {TERRITORY_CONFIG[selectedTerritory]?.defaultZoom || 8}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

TerritoryModePanel.propTypes = {
  onTerritoryChange: PropTypes.func,
  showSeasonInfo: PropTypes.bool,
  layout: PropTypes.oneOf(['horizontal', 'vertical', 'grid'])
};

// =============================================================================
// COMPACT TERRITORY SELECTOR
// =============================================================================

export function CompactTerritorySelector({ onChange }) {
  const { selectedTerritory, applyTerritoryPreset } = useGeoSuiteStore();
  
  const handleChange = (e) => {
    const territory = e.target.value;
    applyTerritoryPreset(territory);
    onChange?.(territory);
  };
  
  return (
    <div className="relative inline-block">
      <select
        value={selectedTerritory}
        onChange={handleChange}
        className="
          appearance-none px-4 py-2 pr-10
          bg-white border border-gray-300 rounded-lg
          text-gray-700 font-medium text-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500
          cursor-pointer
        "
        data-testid="territory-selector-compact"
      >
        {Object.entries(TERRITORY_CONFIG).map(([id, config]) => (
          <option key={id} value={id}>
            {config.icon} {config.name}
          </option>
        ))}
      </select>
      
      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

CompactTerritorySelector.propTypes = {
  onChange: PropTypes.func
};

// =============================================================================
// EXPORTS
// =============================================================================

export default TerritoryModePanel;
