/**
 * BIONIC™ P1.5 - Layer Overlay Panel
 * ====================================
 * Panneau de superposition des couches avec contrôles visuels.
 * Gère l'affichage combiné corridor + densité + landcover.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import React, { useState, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import useGeoSuiteStore, { LAYER_CONFIG } from '../../stores/geoSuiteStore';
import { SUPERPOSITION_PRESETS, useLayerOrchestration } from './LayerOrchestrationEngine';
import { useLayerPriority, LAYER_PRIORITY_ORDER } from './performance/LayerPrioritySystem';
import { useInteractionLogger } from './performance/UIInteractionLogger';

// =============================================================================
// LAYER STACK VISUALIZER
// =============================================================================

function LayerStackVisualizer({ layerStack, onReorder }) {
  return (
    <div className="relative bg-gray-100 rounded-lg p-3" data-testid="layer-stack-visualizer">
      <p className="text-xs text-gray-500 mb-2">Ordre d'affichage (haut = premier plan)</p>
      
      <div className="space-y-1">
        {layerStack.map((layer, index) => {
          const config = LAYER_CONFIG[layer.id];
          
          return (
            <div 
              key={layer.id}
              className="flex items-center gap-2 p-2 bg-white rounded border border-gray-200"
              style={{ 
                opacity: layer.opacity,
                zIndex: layerStack.length - index
              }}
            >
              {/* Drag handle */}
              <span className="text-gray-400 cursor-move">⋮⋮</span>
              
              {/* Layer icon */}
              <span className="text-lg">{config?.icon}</span>
              
              {/* Layer info */}
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-800">{config?.name}</span>
                <div className="flex gap-2 text-xs text-gray-500">
                  <span>z:{layer.zIndex}</span>
                  <span>•</span>
                  <span>{layer.blendMode}</span>
                  <span>•</span>
                  <span>{Math.round(layer.opacity * 100)}%</span>
                </div>
              </div>
              
              {/* Priority badge */}
              <span className={`
                px-2 py-0.5 text-xs rounded-full
                ${layer.category === 'primary' ? 'bg-emerald-100 text-emerald-700' : ''}
                ${layer.category === 'overlay' ? 'bg-orange-100 text-orange-700' : ''}
                ${layer.category === 'heatmap' ? 'bg-purple-100 text-purple-700' : ''}
                ${layer.category === 'base' ? 'bg-blue-100 text-blue-700' : ''}
              `}>
                {layer.category}
              </span>
            </div>
          );
        })}
      </div>
      
      {layerStack.length === 0 && (
        <p className="text-center text-sm text-gray-500 py-4">
          Aucune couche active
        </p>
      )}
    </div>
  );
}

// =============================================================================
// BLEND MODE SELECTOR
// =============================================================================

function BlendModeSelector({ layerId, currentMode, onChange }) {
  const modes = ['normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten'];
  
  return (
    <div className="flex flex-wrap gap-1">
      {modes.map(mode => (
        <button
          key={mode}
          onClick={() => onChange(layerId, mode)}
          className={`
            px-2 py-1 text-xs rounded transition-all
            ${currentMode === mode 
              ? 'bg-purple-500 text-white' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }
          `}
        >
          {mode}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// QUICK PRESETS BAR
// =============================================================================

function QuickPresetsBar({ onApply, activePreset }) {
  const presets = Object.entries(SUPERPOSITION_PRESETS).slice(0, 4);
  
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {presets.map(([id, preset]) => (
        <button
          key={id}
          onClick={() => onApply(id)}
          className={`
            flex-shrink-0 px-3 py-2 rounded-lg border transition-all
            ${activePreset === id 
              ? 'border-purple-500 bg-purple-50 text-purple-700' 
              : 'border-gray-200 bg-white text-gray-700 hover:border-purple-300'
            }
          `}
        >
          <div className="flex items-center gap-2">
            {preset.layers.slice(0, 2).map(layerId => (
              <span key={layerId} className="text-sm">
                {LAYER_CONFIG[layerId]?.icon}
              </span>
            ))}
            <span className="text-xs font-medium">{preset.name}</span>
          </div>
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// CONFLICT ALERT
// =============================================================================

function ConflictAlert({ conflicts }) {
  if (conflicts.length === 0) return null;
  
  return (
    <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <div className="flex items-start gap-2">
        <span className="text-amber-500">⚠️</span>
        <div>
          <p className="text-sm font-medium text-amber-800">Conflits de couches détectés</p>
          <ul className="mt-1 text-xs text-amber-700">
            {conflicts.map((conflict, i) => (
              <li key={i}>
                • {LAYER_CONFIG[conflict.layerId]?.name}: opacité réduite à {Math.round(conflict.suggestedOpacity * 100)}%
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// RECOMMENDATIONS PANEL
// =============================================================================

function RecommendationsPanel({ recommendations, onAddLayer }) {
  if (recommendations.length === 0) return null;
  
  return (
    <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
      <p className="text-sm font-medium text-emerald-800 mb-2">Couches recommandées</p>
      <div className="flex flex-wrap gap-2">
        {recommendations.map(layerId => {
          const config = LAYER_CONFIG[layerId];
          return (
            <button
              key={layerId}
              onClick={() => onAddLayer(layerId)}
              className="flex items-center gap-1 px-3 py-1.5 bg-white border border-emerald-300 rounded-full text-sm text-emerald-700 hover:bg-emerald-100 transition-all"
            >
              <span>{config?.icon}</span>
              <span>{config?.name}</span>
              <span className="text-emerald-500">+</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// =============================================================================
// MAIN LAYER OVERLAY PANEL
// =============================================================================

export function LayerOverlayPanel({ 
  onLayerChange,
  onPresetApply,
  showAdvanced = false,
  showVisualization = true
}) {
  const { 
    activeLayers, 
    layerOpacities, 
    toggleLayer, 
    setLayerOpacity 
  } = useGeoSuiteStore();
  
  const { applyPreset } = useLayerOrchestration();
  const { 
    layerStack, 
    conflicts, 
    recommendations, 
    optimalOpacities 
  } = useLayerPriority(activeLayers, layerOpacities);
  
  const logger = useInteractionLogger();
  
  const [activePreset, setActivePreset] = useState(null);
  const [showBlendOptions, setShowBlendOptions] = useState(false);
  const [blendModes, setBlendModes] = useState({});
  
  // Handle preset application
  const handlePresetApply = useCallback((presetId) => {
    setActivePreset(presetId);
    applyPreset(presetId);
    logger.logPresetApply(presetId, SUPERPOSITION_PRESETS[presetId]?.layers || []);
    onPresetApply?.(presetId);
  }, [applyPreset, logger, onPresetApply]);
  
  // Handle layer toggle
  const handleToggleLayer = useCallback((layerId) => {
    const wasActive = activeLayers.includes(layerId);
    toggleLayer(layerId);
    logger.logLayerToggle(layerId, !wasActive);
    setActivePreset(null);
    onLayerChange?.(layerId, !wasActive);
  }, [activeLayers, toggleLayer, logger, onLayerChange]);
  
  // Handle opacity change
  const handleOpacityChange = useCallback((layerId, opacity) => {
    setLayerOpacity(layerId, opacity);
    logger.logLayerOpacityChange(layerId, opacity);
    setActivePreset(null);
  }, [setLayerOpacity, logger]);
  
  // Handle add recommended layer
  const handleAddRecommended = useCallback((layerId) => {
    if (!activeLayers.includes(layerId)) {
      toggleLayer(layerId);
      logger.logLayerToggle(layerId, true, 'recommendation');
    }
  }, [activeLayers, toggleLayer, logger]);
  
  // Handle blend mode change
  const handleBlendModeChange = useCallback((layerId, mode) => {
    setBlendModes(prev => ({ ...prev, [layerId]: mode }));
  }, []);
  
  // Apply optimal opacities
  const applyOptimalOpacities = useCallback(() => {
    Object.entries(optimalOpacities).forEach(([layerId, opacity]) => {
      setLayerOpacity(layerId, opacity);
    });
  }, [optimalOpacities, setLayerOpacity]);
  
  return (
    <div className="space-y-4" data-testid="layer-overlay-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <span>🎨</span> Superposition de couches
        </h3>
        <span className="text-xs text-gray-500">{activeLayers.length} actives</span>
      </div>
      
      {/* Quick Presets */}
      <QuickPresetsBar onApply={handlePresetApply} activePreset={activePreset} />
      
      {/* Conflict Alert */}
      <ConflictAlert conflicts={conflicts} />
      
      {/* Layer Controls */}
      <div className="space-y-2">
        {Object.entries(LAYER_CONFIG).map(([id, config]) => {
          const isActive = activeLayers.includes(id);
          const opacity = layerOpacities[id] ?? config.defaultOpacity;
          const priority = LAYER_PRIORITY_ORDER[id];
          
          return (
            <div 
              key={id}
              className={`
                p-3 rounded-lg border transition-all
                ${isActive 
                  ? 'border-emerald-300 bg-emerald-50' 
                  : 'border-gray-200 bg-white hover:border-gray-300'
                }
              `}
            >
              {/* Main row */}
              <div className="flex items-center gap-3">
                {/* Toggle */}
                <button
                  onClick={() => handleToggleLayer(id)}
                  className={`
                    w-6 h-6 rounded-md border-2 flex items-center justify-center transition-all
                    ${isActive 
                      ? 'bg-emerald-500 border-emerald-500 text-white' 
                      : 'bg-white border-gray-300 hover:border-emerald-400'
                    }
                  `}
                  data-testid={`layer-toggle-${id}`}
                >
                  {isActive && (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
                
                {/* Icon and label */}
                <div className="flex items-center gap-2 flex-1">
                  <span className="text-xl">{config.icon}</span>
                  <div>
                    <span className="font-medium text-gray-900">{config.name}</span>
                    <p className="text-xs text-gray-500">{priority?.description}</p>
                  </div>
                </div>
                
                {/* Priority indicator */}
                <span className={`
                  px-2 py-0.5 text-xs rounded-full
                  ${priority?.category === 'primary' ? 'bg-emerald-100 text-emerald-700' : ''}
                  ${priority?.category === 'overlay' ? 'bg-orange-100 text-orange-700' : ''}
                  ${priority?.category === 'heatmap' ? 'bg-purple-100 text-purple-700' : ''}
                  ${priority?.category === 'base' ? 'bg-blue-100 text-blue-700' : ''}
                `}>
                  P{priority?.priority || 0}
                </span>
              </div>
              
              {/* Opacity slider (when active) */}
              {isActive && (
                <div className="mt-3 flex items-center gap-3">
                  <span className="text-xs text-gray-500 w-12">Opacité</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={opacity * 100}
                    onChange={(e) => handleOpacityChange(id, e.target.value / 100)}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                  <span className="text-sm font-medium text-gray-700 w-10 text-right">
                    {Math.round(opacity * 100)}%
                  </span>
                </div>
              )}
              
              {/* Blend mode options (advanced) */}
              {isActive && showAdvanced && (
                <div className="mt-3">
                  <button
                    onClick={() => setShowBlendOptions(!showBlendOptions)}
                    className="text-xs text-purple-600 hover:text-purple-800"
                  >
                    {showBlendOptions ? '▼' : '▶'} Mode de fusion
                  </button>
                  
                  {showBlendOptions && (
                    <div className="mt-2">
                      <BlendModeSelector
                        layerId={id}
                        currentMode={blendModes[id] || priority?.blendMode || 'normal'}
                        onChange={handleBlendModeChange}
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Recommendations */}
      <RecommendationsPanel 
        recommendations={recommendations}
        onAddLayer={handleAddRecommended}
      />
      
      {/* Layer Stack Visualization */}
      {showVisualization && layerStack.length > 0 && (
        <LayerStackVisualizer layerStack={layerStack} />
      )}
      
      {/* Actions */}
      <div className="flex gap-2">
        {conflicts.length > 0 && (
          <button
            onClick={applyOptimalOpacities}
            className="flex-1 py-2 bg-amber-100 text-amber-700 rounded-lg text-sm font-medium hover:bg-amber-200 transition-all"
          >
            Optimiser les opacités
          </button>
        )}
        
        <button
          onClick={() => handlePresetApply('minimal')}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-all"
        >
          Réinitialiser
        </button>
      </div>
      
      {/* P2 Fusion info */}
      <div className="text-xs text-center text-purple-600 pt-2 border-t border-gray-200">
        🔮 P2: Les couches seront fusionnées avec BehaviorFusionEngine
      </div>
    </div>
  );
}

LayerOverlayPanel.propTypes = {
  onLayerChange: PropTypes.func,
  onPresetApply: PropTypes.func,
  showAdvanced: PropTypes.bool,
  showVisualization: PropTypes.bool
};

// =============================================================================
// EXPORTS
// =============================================================================

export default LayerOverlayPanel;
