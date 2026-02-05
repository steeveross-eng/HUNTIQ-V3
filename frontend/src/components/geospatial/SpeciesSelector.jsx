/**
 * BIONIC™ P1 - SpeciesSelector
 * =============================
 * Sélecteur d'espèces avec presets automatiques.
 * Applique les configurations de couches par espèce.
 * 
 * @version 1.0.0
 * @architecture P2-Ready
 */

import React from 'react';
import PropTypes from 'prop-types';
import useGeoSuiteStore, { SPECIES_CONFIG } from '../../stores/geoSuiteStore';

// =============================================================================
// SPECIES CARD
// =============================================================================

function SpeciesCard({ species, config, isSelected, onSelect }) {
  return (
    <button
      onClick={() => onSelect(species)}
      className={`
        flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-200
        ${isSelected 
          ? 'border-emerald-500 bg-emerald-50 shadow-md' 
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
        }
      `}
      data-testid={`species-card-${species}`}
    >
      <span className="text-3xl mb-2">{config.icon}</span>
      <span className={`font-medium text-sm ${isSelected ? 'text-emerald-700' : 'text-gray-700'}`}>
        {config.name}
      </span>
      {isSelected && (
        <span className="text-xs text-emerald-600 mt-1">
          {config.defaultLayers.length} couches actives
        </span>
      )}
    </button>
  );
}

SpeciesCard.propTypes = {
  species: PropTypes.string.isRequired,
  config: PropTypes.object.isRequired,
  isSelected: PropTypes.bool.isRequired,
  onSelect: PropTypes.func.isRequired
};

// =============================================================================
// COMPACT SELECTOR (Dropdown style)
// =============================================================================

export function CompactSpeciesSelector({ onChange }) {
  const { selectedSpecies, setSpecies } = useGeoSuiteStore();
  
  const handleChange = (e) => {
    const species = e.target.value;
    setSpecies(species);
    onChange?.(species);
  };
  
  return (
    <div className="relative">
      <select
        value={selectedSpecies}
        onChange={handleChange}
        className="
          appearance-none w-full px-4 py-2.5 pr-10
          bg-white border border-gray-300 rounded-lg
          text-gray-700 font-medium
          focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent
          cursor-pointer
        "
        data-testid="species-selector-compact"
      >
        {Object.entries(SPECIES_CONFIG).map(([id, config]) => (
          <option key={id} value={id}>
            {config.icon} {config.name}
          </option>
        ))}
      </select>
      
      {/* Custom arrow */}
      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}

CompactSpeciesSelector.propTypes = {
  onChange: PropTypes.func
};

// =============================================================================
// GRID SELECTOR
// =============================================================================

export function GridSpeciesSelector({ columns = 3, showDescription = false, onChange }) {
  const { selectedSpecies, setSpecies, applySpeciesPreset } = useGeoSuiteStore();
  
  const handleSelect = (species) => {
    applySpeciesPreset(species);
    onChange?.(species);
  };
  
  const gridCols = {
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
    6: 'grid-cols-6'
  };
  
  return (
    <div className={`grid ${gridCols[columns] || 'grid-cols-3'} gap-3`} data-testid="species-selector-grid">
      {Object.entries(SPECIES_CONFIG).map(([id, config]) => (
        <SpeciesCard
          key={id}
          species={id}
          config={config}
          isSelected={selectedSpecies === id}
          onSelect={handleSelect}
        />
      ))}
    </div>
  );
}

GridSpeciesSelector.propTypes = {
  columns: PropTypes.number,
  showDescription: PropTypes.bool,
  onChange: PropTypes.func
};

// =============================================================================
// HORIZONTAL SELECTOR (Pills style)
// =============================================================================

export function HorizontalSpeciesSelector({ onChange }) {
  const { selectedSpecies, applySpeciesPreset } = useGeoSuiteStore();
  
  const handleSelect = (species) => {
    applySpeciesPreset(species);
    onChange?.(species);
  };
  
  return (
    <div className="flex flex-wrap gap-2" data-testid="species-selector-horizontal">
      {Object.entries(SPECIES_CONFIG).map(([id, config]) => (
        <button
          key={id}
          onClick={() => handleSelect(id)}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-full border transition-all
            ${selectedSpecies === id
              ? 'bg-emerald-500 text-white border-emerald-500'
              : 'bg-white text-gray-700 border-gray-300 hover:border-emerald-400'
            }
          `}
        >
          <span>{config.icon}</span>
          <span className="font-medium text-sm">{config.name}</span>
        </button>
      ))}
    </div>
  );
}

HorizontalSpeciesSelector.propTypes = {
  onChange: PropTypes.func
};

// =============================================================================
// MAIN SELECTOR (with preset info)
// =============================================================================

export function SpeciesSelector({ variant = 'grid', showPresetInfo = true, onChange }) {
  const { selectedSpecies, activeLayers } = useGeoSuiteStore();
  const config = SPECIES_CONFIG[selectedSpecies];
  
  return (
    <div className="space-y-4" data-testid="species-selector">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Espèce cible</h3>
        {showPresetInfo && config && (
          <span className="text-xs text-gray-500">
            Preset: {config.defaultLayers.length} couches
          </span>
        )}
      </div>
      
      {/* Selector based on variant */}
      {variant === 'grid' && <GridSpeciesSelector columns={3} onChange={onChange} />}
      {variant === 'horizontal' && <HorizontalSpeciesSelector onChange={onChange} />}
      {variant === 'compact' && <CompactSpeciesSelector onChange={onChange} />}
      
      {/* Active preset info */}
      {showPresetInfo && config && (
        <div className="p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">{config.icon}</span>
            <span className="font-medium text-gray-900">{config.name}</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {activeLayers.map(layer => (
              <span 
                key={layer}
                className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs rounded-full"
              >
                {layer}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

SpeciesSelector.propTypes = {
  variant: PropTypes.oneOf(['grid', 'horizontal', 'compact']),
  showPresetInfo: PropTypes.bool,
  onChange: PropTypes.func
};

// =============================================================================
// EXPORTS
// =============================================================================

export default SpeciesSelector;
