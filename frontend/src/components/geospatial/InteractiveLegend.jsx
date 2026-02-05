/**
 * BIONIC™ P1.5 - Interactive Legend
 * ==================================
 * Légendes interactives pour les couches géospatiales.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import { LAYER_CONFIG } from '../../stores/geoSuiteStore';
import { HEATMAP_CONFIGS } from './performance/HeatmapPreprocessor';

// =============================================================================
// GRADIENT BAR
// =============================================================================

let gradientCounter = 0;

function GradientBar({ gradient, width = 150, height = 12 }) {
  const gradientId = useMemo(() => `gradient-${++gradientCounter}`, []);
  
  const stops = Object.entries(gradient).sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]));
  
  return (
    <svg width={width} height={height}>
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
          {stops.map(([offset, color]) => (
            <stop key={offset} offset={`${parseFloat(offset) * 100}%`} stopColor={color} />
          ))}
        </linearGradient>
      </defs>
      <rect 
        x="0" 
        y="0" 
        width={width} 
        height={height} 
        fill={`url(#${gradientId})`}
        rx="2"
        ry="2"
      />
    </svg>
  );
}

// =============================================================================
// COLOR SWATCH
// =============================================================================

function ColorSwatch({ color, label, value, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 py-1 px-2 rounded hover:bg-gray-100 transition-colors w-full text-left"
    >
      <span 
        className="w-4 h-4 rounded-sm border border-gray-300"
        style={{ backgroundColor: color }}
      />
      <span className="text-xs text-gray-700 flex-1">{label}</span>
      {value !== undefined && (
        <span className="text-xs text-gray-500">{value}</span>
      )}
    </button>
  );
}

// =============================================================================
// LAYER LEGEND ITEM
// =============================================================================

function LayerLegendItem({ layerId, config, expanded, onToggle, onOpacityChange, opacity }) {
  const heatmapConfig = HEATMAP_CONFIGS[layerId];
  
  const legendItems = useMemo(() => {
    if (config.colors) {
      return Object.entries(config.colors).map(([key, color]) => ({
        key,
        color,
        label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
      }));
    }
    return [];
  }, [config.colors]);
  
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span>{config.icon}</span>
          <span className="font-medium text-sm text-gray-900">{config.name}</span>
        </div>
        <svg 
          className={`w-4 h-4 text-gray-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {/* Expanded content */}
      {expanded && (
        <div className="p-3 space-y-3">
          {/* Opacity slider */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 w-16">Opacité</span>
            <input
              type="range"
              min="0"
              max="100"
              value={(opacity ?? config.defaultOpacity ?? 0.7) * 100}
              onChange={(e) => onOpacityChange?.(e.target.value / 100)}
              className="flex-1 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-xs text-gray-600 w-8 text-right">
              {Math.round((opacity ?? config.defaultOpacity ?? 0.7) * 100)}%
            </span>
          </div>
          
          {/* Gradient for heatmaps */}
          {heatmapConfig?.gradient && (
            <div className="space-y-1">
              <GradientBar gradient={heatmapConfig.gradient} width={180} height={10} />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Faible</span>
                <span>Élevé</span>
              </div>
            </div>
          )}
          
          {/* Color swatches */}
          {legendItems.length > 0 && (
            <div className="space-y-1">
              {legendItems.slice(0, 6).map(({ key, color, label }) => (
                <ColorSwatch key={key} color={color} label={label} />
              ))}
            </div>
          )}
          
          {/* Layer type info */}
          <div className="text-xs text-gray-500 italic">
            Type: {config.type}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// MAIN INTERACTIVE LEGEND
// =============================================================================

export function InteractiveLegend({ 
  activeLayers = [], 
  layerOpacities = {}, 
  onOpacityChange,
  onLayerToggle,
  compact = false,
  position = 'bottom-right'
}) {
  const [expandedLayers, setExpandedLayers] = useState(new Set());
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  const toggleExpanded = (layerId) => {
    setExpandedLayers(prev => {
      const next = new Set(prev);
      if (next.has(layerId)) {
        next.delete(layerId);
      } else {
        next.add(layerId);
      }
      return next;
    });
  };
  
  // Position classes
  const positionClasses = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4'
  };
  
  // Compact mode
  if (compact) {
    return (
      <div className={`absolute ${positionClasses[position]} z-10`}>
        <div className="bg-white rounded-lg shadow-lg border p-2">
          <div className="flex flex-wrap gap-2">
            {activeLayers.map(layerId => {
              const config = LAYER_CONFIG[layerId];
              if (!config) return null;
              
              return (
                <div 
                  key={layerId}
                  className="flex items-center gap-1 px-2 py-1 bg-gray-50 rounded text-xs"
                >
                  <span>{config.icon}</span>
                  <span>{config.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }
  
  // Full legend
  return (
    <div 
      className={`absolute ${positionClasses[position]} z-10`}
      data-testid="interactive-legend"
    >
      <div className="bg-white rounded-lg shadow-lg border overflow-hidden w-64">
        {/* Header */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full flex items-center justify-between p-3 bg-emerald-50 hover:bg-emerald-100 transition-colors"
        >
          <div className="flex items-center gap-2">
            <span>🗺️</span>
            <span className="font-semibold text-sm text-emerald-900">Légende</span>
            <span className="text-xs text-emerald-600">({activeLayers.length} couches)</span>
          </div>
          <svg 
            className={`w-4 h-4 text-emerald-600 transition-transform ${isCollapsed ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </button>
        
        {/* Content */}
        {!isCollapsed && (
          <div className="p-3 space-y-2 max-h-96 overflow-y-auto">
            {activeLayers.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                Aucune couche active
              </p>
            ) : (
              activeLayers.map(layerId => {
                const config = LAYER_CONFIG[layerId];
                if (!config) return null;
                
                return (
                  <LayerLegendItem
                    key={layerId}
                    layerId={layerId}
                    config={config}
                    expanded={expandedLayers.has(layerId)}
                    onToggle={() => toggleExpanded(layerId)}
                    opacity={layerOpacities[layerId]}
                    onOpacityChange={(opacity) => onOpacityChange?.(layerId, opacity)}
                  />
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}

InteractiveLegend.propTypes = {
  activeLayers: PropTypes.arrayOf(PropTypes.string),
  layerOpacities: PropTypes.object,
  onOpacityChange: PropTypes.func,
  onLayerToggle: PropTypes.func,
  compact: PropTypes.bool,
  position: PropTypes.oneOf(['bottom-right', 'bottom-left', 'top-right', 'top-left'])
};

// =============================================================================
// MINI LEGEND (for embedding)
// =============================================================================

export function MiniLegend({ layerId, showGradient = true }) {
  const config = LAYER_CONFIG[layerId];
  const heatmapConfig = HEATMAP_CONFIGS[layerId];
  
  if (!config) return null;
  
  return (
    <div className="inline-flex items-center gap-2 px-2 py-1 bg-white rounded border text-xs">
      <span>{config.icon}</span>
      <span className="text-gray-700">{config.name}</span>
      {showGradient && heatmapConfig?.gradient && (
        <GradientBar gradient={heatmapConfig.gradient} width={60} height={8} />
      )}
    </div>
  );
}

MiniLegend.propTypes = {
  layerId: PropTypes.string.isRequired,
  showGradient: PropTypes.bool
};

// =============================================================================
// EXPORTS
// =============================================================================

export default InteractiveLegend;
