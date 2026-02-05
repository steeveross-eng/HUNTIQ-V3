/**
 * BIONIC™ P1.5 - Heatmap Preprocessor
 * =====================================
 * Optimisation et preprocessing des données heatmap.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

// =============================================================================
// HEATMAP CONFIGURATIONS
// =============================================================================

export const HEATMAP_CONFIGS = {
  nutrition: {
    gradient: {
      0.0: '#FF5722',   // Low - red/orange
      0.3: '#FF9800',   // Low-medium
      0.5: '#FFEB3B',   // Medium - yellow
      0.7: '#8BC34A',   // Medium-high
      1.0: '#00E676'    // High - green
    },
    radius: 30,
    blur: 15,
    maxIntensity: 100,
    minOpacity: 0.1
  },
  
  population: {
    gradient: {
      0.0: '#CDDC39',   // Low - lime
      0.3: '#FF9800',   // Medium - orange
      0.6: '#E91E63',   // High - pink
      1.0: '#9C27B0'    // Very high - purple
    },
    radius: 40,
    blur: 20,
    maxIntensity: 50,
    minOpacity: 0.2
  },
  
  pressure: {
    gradient: {
      0.0: '#81C784',   // Minimal - green
      0.25: '#4CAF50',  // Low
      0.5: '#FF9800',   // Moderate - orange
      0.75: '#E53935',  // High - red
      1.0: '#B71C1C'    // Extreme - dark red
    },
    radius: 35,
    blur: 18,
    maxIntensity: 100,
    minOpacity: 0.15
  },
  
  corridors: {
    gradient: {
      0.0: '#64B5F6',   // Low connectivity
      0.3: '#2196F3',
      0.5: '#1976D2',
      0.7: '#0D47A1',
      1.0: '#4CAF50'    // High connectivity - green
    },
    radius: 25,
    blur: 12,
    maxIntensity: 100,
    minOpacity: 0.2
  },
  
  // Combined heatmap for P2 fusion
  fusion: {
    gradient: {
      0.0: '#F44336',   // Poor
      0.2: '#FF9800',   // Low
      0.4: '#FFEB3B',   // Moderate
      0.6: '#8BC34A',   // Good
      0.8: '#4CAF50',   // Very good
      1.0: '#00C853'    // Excellent
    },
    radius: 35,
    blur: 17,
    maxIntensity: 100,
    minOpacity: 0.15
  }
};

// =============================================================================
// HEATMAP PREPROCESSOR CLASS
// =============================================================================

class HeatmapPreprocessor {
  constructor() {
    this.cache = new Map();
    this.workers = [];
    this.maxCacheSize = 50;
  }
  
  // Generate cache key
  _getCacheKey(dataType, bbox, resolution) {
    return `${dataType}:${bbox.join(',')}:${resolution}`;
  }
  
  // Preprocess data for heatmap rendering
  preprocessData(rawData, dataType, options = {}) {
    const {
      bbox = null,
      resolution = 256,
      normalize = true,
      clamp = true,
      smooth = true
    } = options;
    
    // Check cache
    if (bbox) {
      const cacheKey = this._getCacheKey(dataType, bbox, resolution);
      if (this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
      }
    }
    
    // Get configuration
    const config = HEATMAP_CONFIGS[dataType] || HEATMAP_CONFIGS.nutrition;
    
    // Process data
    let processed = this._extractPoints(rawData, dataType);
    
    // Normalize values
    if (normalize) {
      processed = this._normalizeValues(processed, config.maxIntensity);
    }
    
    // Clamp to bounds
    if (clamp && bbox) {
      processed = this._clampToBounds(processed, bbox);
    }
    
    // Apply smoothing
    if (smooth) {
      processed = this._applySmoothing(processed);
    }
    
    // Create result
    const result = {
      points: processed,
      config,
      resolution,
      bounds: bbox,
      metadata: {
        pointCount: processed.length,
        dataType,
        timestamp: Date.now()
      }
    };
    
    // Cache result
    if (bbox) {
      const cacheKey = this._getCacheKey(dataType, bbox, resolution);
      this._addToCache(cacheKey, result);
    }
    
    return result;
  }
  
  // Extract points from raw data
  _extractPoints(rawData, dataType) {
    const points = [];
    
    // Handle different data structures
    if (Array.isArray(rawData)) {
      for (const item of rawData) {
        if (item.lat !== undefined && item.lon !== undefined) {
          points.push({
            lat: item.lat,
            lon: item.lon,
            value: item.score ?? item.value ?? item.intensity ?? 50,
            weight: item.weight ?? 1
          });
        }
      }
    } else if (rawData.data) {
      // Handle engine output format
      const data = rawData.data;
      
      // Extract from species scores or similar nested data
      if (data.species_scores || data.species_habitat_scores || data.species_densities) {
        const scoresObj = data.species_scores || data.species_habitat_scores || data.species_densities;
        const avgScore = Object.values(scoresObj).reduce((a, b) => {
          const val = typeof b === 'object' ? (b.score ?? b.density_per_100km2 ?? 50) : b;
          return a + val;
        }, 0) / Math.max(1, Object.keys(scoresObj).length);
        
        // Create center point with score
        if (rawData.location) {
          points.push({
            lat: rawData.location.lat,
            lon: rawData.location.lon,
            value: avgScore,
            weight: 1
          });
        }
      }
      
      // Handle composition data
      if (data.cover_composition) {
        for (const comp of data.cover_composition) {
          if (rawData.location) {
            points.push({
              lat: rawData.location.lat + (Math.random() - 0.5) * 0.02,
              lon: rawData.location.lon + (Math.random() - 0.5) * 0.02,
              value: comp.habitat_score ?? comp.percent ?? 50,
              weight: comp.percent / 100
            });
          }
        }
      }
    }
    
    return points;
  }
  
  // Normalize values to 0-1 range
  _normalizeValues(points, maxIntensity = 100) {
    if (points.length === 0) return points;
    
    const values = points.map(p => p.value);
    const max = Math.max(...values, maxIntensity);
    const min = Math.min(...values, 0);
    const range = max - min || 1;
    
    return points.map(p => ({
      ...p,
      normalizedValue: (p.value - min) / range
    }));
  }
  
  // Clamp points to bounding box
  _clampToBounds(points, bbox) {
    const [minLon, minLat, maxLon, maxLat] = bbox;
    
    return points.filter(p => 
      p.lat >= minLat && p.lat <= maxLat &&
      p.lon >= minLon && p.lon <= maxLon
    );
  }
  
  // Apply Gaussian smoothing
  _applySmoothing(points, sigma = 0.5) {
    if (points.length < 3) return points;
    
    // Simple moving average smoothing
    return points.map((point, i) => {
      const neighbors = points.filter((p, j) => {
        if (i === j) return false;
        const dist = Math.sqrt(
          Math.pow(p.lat - point.lat, 2) + 
          Math.pow(p.lon - point.lon, 2)
        );
        return dist < sigma;
      });
      
      if (neighbors.length === 0) return point;
      
      const avgValue = neighbors.reduce((sum, n) => sum + n.value, point.value) / (neighbors.length + 1);
      
      return {
        ...point,
        smoothedValue: avgValue
      };
    });
  }
  
  // Generate grid data for efficient rendering
  generateGrid(points, resolution = 64, bbox = null) {
    if (!bbox || points.length === 0) return null;
    
    const [minLon, minLat, maxLon, maxLat] = bbox;
    const cellWidth = (maxLon - minLon) / resolution;
    const cellHeight = (maxLat - minLat) / resolution;
    
    // Initialize grid
    const grid = new Float32Array(resolution * resolution);
    const counts = new Uint16Array(resolution * resolution);
    
    // Populate grid
    for (const point of points) {
      const col = Math.floor((point.lon - minLon) / cellWidth);
      const row = Math.floor((point.lat - minLat) / cellHeight);
      
      if (col >= 0 && col < resolution && row >= 0 && row < resolution) {
        const idx = row * resolution + col;
        grid[idx] += point.normalizedValue ?? point.value / 100;
        counts[idx]++;
      }
    }
    
    // Average values in each cell
    for (let i = 0; i < grid.length; i++) {
      if (counts[i] > 0) {
        grid[i] /= counts[i];
      }
    }
    
    return {
      data: grid,
      width: resolution,
      height: resolution,
      bbox
    };
  }
  
  // Add to cache with size limit
  _addToCache(key, data) {
    if (this.cache.size >= this.maxCacheSize) {
      // Remove oldest entry
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
    this.cache.set(key, data);
  }
  
  // Clear cache
  clearCache() {
    this.cache.clear();
  }
  
  // Get cache stats
  getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize
    };
  }
  
  // Merge multiple heatmap datasets (for P2 fusion)
  mergeHeatmaps(datasets, weights = {}) {
    const merged = [];
    const defaultWeight = 1 / datasets.length;
    
    for (const { dataType, points } of datasets) {
      const weight = weights[dataType] ?? defaultWeight;
      
      for (const point of points) {
        merged.push({
          ...point,
          value: (point.normalizedValue ?? point.value / 100) * weight,
          sourceType: dataType
        });
      }
    }
    
    // Group by location and average
    const grouped = new Map();
    
    for (const point of merged) {
      const key = `${point.lat.toFixed(4)},${point.lon.toFixed(4)}`;
      
      if (!grouped.has(key)) {
        grouped.set(key, { lat: point.lat, lon: point.lon, values: [], weights: [] });
      }
      
      const group = grouped.get(key);
      group.values.push(point.value);
    }
    
    // Calculate weighted average for each location
    return Array.from(grouped.values()).map(group => ({
      lat: group.lat,
      lon: group.lon,
      value: group.values.reduce((a, b) => a + b, 0),
      normalizedValue: group.values.reduce((a, b) => a + b, 0)
    }));
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const heatmapPreprocessor = new HeatmapPreprocessor();

// =============================================================================
// REACT HOOK
// =============================================================================

import { useState, useCallback, useMemo } from 'react';

export function useHeatmapPreprocessor(dataType = 'nutrition') {
  const [processedData, setProcessedData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const config = useMemo(() => HEATMAP_CONFIGS[dataType] || HEATMAP_CONFIGS.nutrition, [dataType]);
  
  const process = useCallback((rawData, options = {}) => {
    setIsProcessing(true);
    
    try {
      const result = heatmapPreprocessor.preprocessData(rawData, dataType, options);
      setProcessedData(result);
      return result;
    } finally {
      setIsProcessing(false);
    }
  }, [dataType]);
  
  const generateGrid = useCallback((points, resolution, bbox) => {
    return heatmapPreprocessor.generateGrid(points, resolution, bbox);
  }, []);
  
  return {
    processedData,
    isProcessing,
    config,
    process,
    generateGrid,
    clearCache: heatmapPreprocessor.clearCache.bind(heatmapPreprocessor)
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export default HeatmapPreprocessor;
