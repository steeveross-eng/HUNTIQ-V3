/**
 * BIONIC™ P1.5 - HeatmapRenderer
 * ================================
 * Rendu de heatmaps dynamiques multi-moteurs.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import React, { useRef, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import { HEATMAP_CONFIGS, useHeatmapPreprocessor } from './performance/HeatmapPreprocessor';
import { usePerformanceBudget } from './performance/PerformanceBudget';

// =============================================================================
// CANVAS HEATMAP
// =============================================================================

function CanvasHeatmap({ data, config, width, height, opacity = 0.7 }) {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    if (!canvasRef.current || !data?.points?.length) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw gradient background if needed
    const gradient = ctx.createRadialGradient(
      width / 2, height / 2, 0,
      width / 2, height / 2, Math.max(width, height) / 2
    );
    
    // Add gradient stops from config
    if (config?.gradient) {
      Object.entries(config.gradient).forEach(([offset, color]) => {
        gradient.addColorStop(parseFloat(offset), color);
      });
    }
    
    // Draw each point
    const radius = config?.radius ?? 30;
    const blur = config?.blur ?? 15;
    
    ctx.globalAlpha = opacity;
    
    for (const point of data.points) {
      const x = ((point.lon - data.bounds[0]) / (data.bounds[2] - data.bounds[0])) * width;
      const y = height - ((point.lat - data.bounds[1]) / (data.bounds[3] - data.bounds[1])) * height;
      
      const value = point.normalizedValue ?? point.value / 100;
      const pointRadius = radius * (0.5 + value * 0.5);
      
      // Create radial gradient for this point
      const pointGradient = ctx.createRadialGradient(x, y, 0, x, y, pointRadius);
      
      // Get color from gradient based on value
      const colorIndex = Math.min(1, Math.max(0, value));
      const stops = Object.entries(config?.gradient ?? {}).sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]));
      
      let color = '#4CAF50';
      for (let i = 0; i < stops.length - 1; i++) {
        const [offset1, color1] = stops[i];
        const [offset2, color2] = stops[i + 1];
        if (colorIndex >= parseFloat(offset1) && colorIndex <= parseFloat(offset2)) {
          color = color1;
          break;
        }
      }
      if (colorIndex >= parseFloat(stops[stops.length - 1]?.[0] ?? 1)) {
        color = stops[stops.length - 1]?.[1] ?? '#4CAF50';
      }
      
      pointGradient.addColorStop(0, color);
      pointGradient.addColorStop(1, 'transparent');
      
      ctx.fillStyle = pointGradient;
      ctx.beginPath();
      ctx.arc(x, y, pointRadius, 0, Math.PI * 2);
      ctx.fill();
    }
    
  }, [data, config, width, height, opacity]);
  
  return (
    <canvas 
      ref={canvasRef} 
      width={width} 
      height={height}
      className="absolute inset-0 pointer-events-none"
      style={{ opacity }}
    />
  );
}

// =============================================================================
// SVG HEATMAP (for smaller datasets)
// =============================================================================

function SVGHeatmap({ data, config, width, height, opacity = 0.7 }) {
  const radius = config?.radius ?? 30;
  const bounds = data?.bounds || [-180, -90, 180, 90];
  
  const getColor = useCallback((value) => {
    const stops = Object.entries(config?.gradient ?? {}).sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]));
    
    for (let i = 0; i < stops.length - 1; i++) {
      const [offset1, color1] = stops[i];
      const [offset2] = stops[i + 1];
      if (value >= parseFloat(offset1) && value <= parseFloat(offset2)) {
        return color1;
      }
    }
    return stops[stops.length - 1]?.[1] ?? '#4CAF50';
  }, [config?.gradient]);
  
  if (!data?.points?.length) return null;
  
  return (
    <svg 
      width={width} 
      height={height} 
      className="absolute inset-0 pointer-events-none"
      style={{ opacity }}
    >
      <defs>
        {data.points.map((point, i) => {
          const value = point.normalizedValue ?? point.value / 100;
          const color = getColor(value);
          
          return (
            <radialGradient key={i} id={`heatmap-gradient-${i}`}>
              <stop offset="0%" stopColor={color} stopOpacity="0.8" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </radialGradient>
          );
        })}
      </defs>
      
      {data.points.map((point, i) => {
        const x = ((point.lon - bounds[0]) / (bounds[2] - bounds[0])) * width;
        const y = height - ((point.lat - bounds[1]) / (bounds[3] - bounds[1])) * height;
        const value = point.normalizedValue ?? point.value / 100;
        const pointRadius = radius * (0.5 + value * 0.5);
        
        return (
          <circle
            key={i}
            cx={x}
            cy={y}
            r={pointRadius}
            fill={`url(#heatmap-gradient-${i})`}
          />
        );
      })}
    </svg>
  );
}

// =============================================================================
// MAIN HEATMAP RENDERER
// =============================================================================

export function HeatmapRenderer({
  dataType = 'nutrition',
  rawData,
  bbox,
  width = 400,
  height = 300,
  opacity = 0.7,
  renderer = 'auto',
  showLegend = true,
  onPointClick
}) {
  const { processedData, isProcessing, config, process } = useHeatmapPreprocessor(dataType);
  const performanceBudget = usePerformanceBudget();
  
  // Process data when inputs change
  useEffect(() => {
    if (rawData) {
      const resolution = performanceBudget.getHeatmapResolution(
        Array.isArray(rawData) ? rawData.length : 100
      );
      
      process(rawData, { bbox, resolution });
    }
  }, [rawData, bbox, process, performanceBudget]);
  
  // Determine renderer based on data size and performance
  const rendererType = useMemo(() => {
    if (renderer !== 'auto') return renderer;
    
    const pointCount = processedData?.points?.length ?? 0;
    
    if (pointCount > 500 || !performanceBudget.isAnimationsEnabled()) {
      return 'canvas';
    }
    return 'svg';
  }, [renderer, processedData, performanceBudget]);
  
  if (isProcessing) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-100 rounded"
        style={{ width, height }}
      >
        <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
      </div>
    );
  }
  
  if (!processedData?.points?.length) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-50 rounded border border-dashed border-gray-300"
        style={{ width, height }}
      >
        <p className="text-sm text-gray-500">Aucune donnée pour la heatmap</p>
      </div>
    );
  }
  
  return (
    <div 
      className="relative bg-gray-100 rounded overflow-hidden"
      style={{ width, height }}
      data-testid={`heatmap-${dataType}`}
    >
      {/* Heatmap */}
      {rendererType === 'canvas' ? (
        <CanvasHeatmap 
          data={processedData}
          config={config}
          width={width}
          height={height}
          opacity={opacity}
        />
      ) : (
        <SVGHeatmap 
          data={processedData}
          config={config}
          width={width}
          height={height}
          opacity={opacity}
        />
      )}
      
      {/* Legend */}
      {showLegend && (
        <div className="absolute bottom-2 left-2 bg-white/90 rounded px-2 py-1">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">{config?.name || dataType}</span>
            <div className="flex gap-0.5">
              {Object.values(config?.gradient ?? {}).slice(0, 5).map((color, i) => (
                <span 
                  key={i}
                  className="w-3 h-2 rounded-sm"
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Point count */}
      <div className="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-0.5 rounded">
        {processedData.points.length} points
      </div>
    </div>
  );
}

HeatmapRenderer.propTypes = {
  dataType: PropTypes.oneOf(['nutrition', 'population', 'pressure', 'corridors', 'fusion']),
  rawData: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  bbox: PropTypes.arrayOf(PropTypes.number),
  width: PropTypes.number,
  height: PropTypes.number,
  opacity: PropTypes.number,
  renderer: PropTypes.oneOf(['auto', 'canvas', 'svg']),
  showLegend: PropTypes.bool,
  onPointClick: PropTypes.func
};

// =============================================================================
// MULTI-LAYER HEATMAP (for combined views)
// =============================================================================

export function MultiLayerHeatmap({
  layers = [],
  width = 400,
  height = 300,
  showLegends = true
}) {
  return (
    <div 
      className="relative bg-gray-100 rounded overflow-hidden"
      style={{ width, height }}
      data-testid="multi-layer-heatmap"
    >
      {layers.map((layer, index) => (
        <div 
          key={layer.dataType}
          className="absolute inset-0"
          style={{ zIndex: index }}
        >
          <HeatmapRenderer
            dataType={layer.dataType}
            rawData={layer.data}
            bbox={layer.bbox}
            width={width}
            height={height}
            opacity={layer.opacity ?? 0.5}
            showLegend={false}
          />
        </div>
      ))}
      
      {/* Combined legend */}
      {showLegends && (
        <div className="absolute bottom-2 left-2 bg-white/90 rounded p-2 space-y-1">
          {layers.map(layer => (
            <div key={layer.dataType} className="flex items-center gap-2 text-xs">
              <span className="w-2 h-2 rounded-full" style={{ 
                backgroundColor: Object.values(HEATMAP_CONFIGS[layer.dataType]?.gradient ?? {})[3] ?? '#4CAF50'
              }} />
              <span className="text-gray-600">{layer.dataType}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

MultiLayerHeatmap.propTypes = {
  layers: PropTypes.arrayOf(PropTypes.shape({
    dataType: PropTypes.string.isRequired,
    data: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
    bbox: PropTypes.arrayOf(PropTypes.number),
    opacity: PropTypes.number
  })),
  width: PropTypes.number,
  height: PropTypes.number,
  showLegends: PropTypes.bool
};

// =============================================================================
// EXPORTS
// =============================================================================

export default HeatmapRenderer;
