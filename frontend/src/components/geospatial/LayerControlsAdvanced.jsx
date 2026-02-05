/**
 * BIONIC™ P1.5 - Advanced Layer Controls
 * ========================================
 * Contrôles avancés: transparence, rayon, profondeur temporelle.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import useGeoSuiteStore, { LAYER_CONFIG } from '../../stores/geoSuiteStore';
import { SUPERPOSITION_PRESETS, useLayerOrchestration } from './LayerOrchestrationEngine';

// =============================================================================
// OPACITY SLIDER
// =============================================================================

function OpacitySlider({ layerId, value, onChange }) {
  const config = LAYER_CONFIG[layerId];
  
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm">{config?.icon}</span>
      <span className="text-sm text-gray-700 w-20 truncate">{config?.name}</span>
      <input
        type="range"
        min="0"
        max="100"
        value={value * 100}
        onChange={(e) => onChange(layerId, e.target.value / 100)}
        className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
      />
      <span className="text-xs text-gray-600 w-10 text-right">
        {Math.round(value * 100)}%
      </span>
    </div>
  );
}

// =============================================================================
// RADIUS CONTROL
// =============================================================================

function RadiusControl({ value, onChange, min = 0.5, max = 50, step = 0.5 }) {
  const radiusPresets = [1, 2, 5, 10, 20];
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Rayon d&apos;analyse</span>
        <span className="text-sm font-bold text-emerald-600">{value} km</span>
      </div>
      
      {/* Slider */}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
      />
      
      {/* Presets */}
      <div className="flex gap-2">
        {radiusPresets.map(preset => (
          <button
            key={preset}
            onClick={() => onChange(preset)}
            className={`
              px-3 py-1 text-xs rounded-full transition-all
              ${value === preset 
                ? 'bg-emerald-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }
            `}
          >
            {preset} km
          </button>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// TEMPORAL DEPTH CONTROL
// =============================================================================

function TemporalDepthControl({ value, onChange }) {
  const periods = [
    { id: '1m', label: '1 mois', value: 1 },
    { id: '3m', label: '3 mois', value: 3 },
    { id: '6m', label: '6 mois', value: 6 },
    { id: '1y', label: '1 an', value: 12 },
    { id: '5y', label: '5 ans', value: 60 },
    { id: '10y', label: '10 ans', value: 120 }
  ];
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Profondeur temporelle</span>
        <span className="text-xs text-gray-500">Historique densité/pression</span>
      </div>
      
      <div className="grid grid-cols-3 gap-2">
        {periods.map(period => (
          <button
            key={period.id}
            onClick={() => onChange(period.value)}
            className={`
              px-2 py-2 text-xs rounded-lg transition-all
              ${value === period.value 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }
            `}
          >
            {period.label}
          </button>
        ))}
      </div>
      
      <p className="text-xs text-gray-500 italic">
        📊 Les données de densité et pression utilisent un historique de {
          periods.find(p => p.value === value)?.label || '1 an'
        }
      </p>
    </div>
  );
}

// =============================================================================
// SUPERPOSITION PRESET SELECTOR
// =============================================================================

function SuperpositionPresets({ onApply }) {
  const [activePreset, setActivePreset] = useState(null);
  
  const handleApply = (presetId) => {
    setActivePreset(presetId);
    onApply?.(presetId);
  };
  
  return (
    <div className="space-y-2">
      <span className="text-sm font-medium text-gray-700">Presets de superposition</span>
      
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(SUPERPOSITION_PRESETS).map(([id, preset]) => (
          <button
            key={id}
            onClick={() => handleApply(id)}
            className={`
              p-3 text-left rounded-lg border transition-all
              ${activePreset === id 
                ? 'border-purple-500 bg-purple-50' 
                : 'border-gray-200 bg-white hover:border-purple-300'
              }
            `}
          >
            <span className={`text-sm font-medium ${activePreset === id ? 'text-purple-700' : 'text-gray-900'}`}>
              {preset.name}
            </span>
            <p className="text-xs text-gray-500 mt-1">{preset.description}</p>
            <div className="flex gap-1 mt-2">
              {preset.layers.slice(0, 3).map(layerId => (
                <span key={layerId} className="text-sm">
                  {LAYER_CONFIG[layerId]?.icon}
                </span>
              ))}
              {preset.layers.length > 3 && (
                <span className="text-xs text-gray-400">+{preset.layers.length - 3}</span>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// MAIN ADVANCED CONTROLS
// =============================================================================

export function LayerControlsAdvanced({ 
  onRadiusChange,
  onTemporalDepthChange,
  onPresetApply
}) {
  const { 
    activeLayers, 
    layerOpacities, 
    setLayerOpacity,
    analysisLocation,
    setRadius
  } = useGeoSuiteStore();
  
  const { applyPreset } = useLayerOrchestration();
  
  const [temporalDepth, setTemporalDepth] = useState(12); // 1 year default
  const [expanded, setExpanded] = useState({
    opacity: true,
    radius: true,
    temporal: false,
    presets: false
  });
  
  const toggleSection = (section) => {
    setExpanded(prev => ({ ...prev, [section]: !prev[section] }));
  };
  
  const handleRadiusChange = useCallback((value) => {
    setRadius(value);
    onRadiusChange?.(value);
  }, [setRadius, onRadiusChange]);
  
  const handleTemporalChange = useCallback((value) => {
    setTemporalDepth(value);
    onTemporalDepthChange?.(value);
  }, [onTemporalDepthChange]);
  
  const handlePresetApply = useCallback((presetId) => {
    applyPreset(presetId);
    onPresetApply?.(presetId);
  }, [applyPreset, onPresetApply]);
  
  return (
    <div className="space-y-4" data-testid="layer-controls-advanced">
      {/* Header */}
      <div className="flex items-center gap-2">
        <span>⚙️</span>
        <h3 className="font-semibold text-gray-900">Contrôles avancés</h3>
      </div>
      
      {/* Opacity section */}
      <div className="border rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection('opacity')}
          className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100"
        >
          <span className="text-sm font-medium text-gray-700">Transparence des couches</span>
          <svg 
            className={`w-4 h-4 text-gray-500 transition-transform ${expanded.opacity ? 'rotate-180' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        {expanded.opacity && (
          <div className="p-3 space-y-3">
            {activeLayers.map(layerId => (
              <OpacitySlider
                key={layerId}
                layerId={layerId}
                value={layerOpacities[layerId] ?? LAYER_CONFIG[layerId]?.defaultOpacity ?? 0.7}
                onChange={setLayerOpacity}
              />
            ))}
            
            {activeLayers.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-2">
                Aucune couche active
              </p>
            )}
          </div>
        )}
      </div>
      
      {/* Radius section */}
      <div className="border rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection('radius')}
          className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100"
        >
          <span className="text-sm font-medium text-gray-700">Rayon d&apos;analyse</span>
          <span className="text-sm text-emerald-600 font-bold">{analysisLocation.radiusKm} km</span>
        </button>
        
        {expanded.radius && (
          <div className="p-3">
            <RadiusControl
              value={analysisLocation.radiusKm}
              onChange={handleRadiusChange}
            />
          </div>
        )}
      </div>
      
      {/* Temporal depth section */}
      <div className="border rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection('temporal')}
          className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100"
        >
          <span className="text-sm font-medium text-gray-700">Profondeur temporelle</span>
          <span className="text-sm text-blue-600">
            {temporalDepth >= 12 ? `${temporalDepth / 12} an${temporalDepth > 12 ? 's' : ''}` : `${temporalDepth} mois`}
          </span>
        </button>
        
        {expanded.temporal && (
          <div className="p-3">
            <TemporalDepthControl
              value={temporalDepth}
              onChange={handleTemporalChange}
            />
          </div>
        )}
      </div>
      
      {/* Presets section */}
      <div className="border rounded-lg overflow-hidden">
        <button
          onClick={() => toggleSection('presets')}
          className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100"
        >
          <span className="text-sm font-medium text-gray-700">Presets de superposition</span>
          <svg 
            className={`w-4 h-4 text-gray-500 transition-transform ${expanded.presets ? 'rotate-180' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        {expanded.presets && (
          <div className="p-3">
            <SuperpositionPresets onApply={handlePresetApply} />
          </div>
        )}
      </div>
    </div>
  );
}

LayerControlsAdvanced.propTypes = {
  onRadiusChange: PropTypes.func,
  onTemporalDepthChange: PropTypes.func,
  onPresetApply: PropTypes.func
};

// =============================================================================
// EXPORTS
// =============================================================================

export default LayerControlsAdvanced;
