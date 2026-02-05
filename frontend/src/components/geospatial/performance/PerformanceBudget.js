/**
 * BIONIC™ P1.5 - Performance Budget
 * ==================================
 * Gestion des limites de performance pour les visualisations.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

// =============================================================================
// PERFORMANCE THRESHOLDS
// =============================================================================

export const PERFORMANCE_THRESHOLDS = {
  // Frame rate targets
  FPS_TARGET: 30,
  FPS_MINIMUM: 15,
  FPS_WARNING: 20,
  
  // Tile limits
  MAX_TILES_PER_LAYER: 256,
  MAX_TOTAL_TILES: 1024,
  TILE_SIZE_BYTES: 256 * 256 * 4, // RGBA
  
  // Layer limits
  MAX_VISIBLE_LAYERS: 5,
  MAX_HEATMAP_LAYERS: 2,
  MAX_POINTS_PER_LAYER: 10000,
  MAX_TOTAL_POINTS: 30000,
  
  // Memory limits
  MAX_MEMORY_MB: 256,
  MEMORY_WARNING_MB: 200,
  
  // Render time limits (ms)
  MAX_RENDER_TIME: 100,
  MAX_DATA_PROCESS_TIME: 500,
  
  // Resolution limits
  HEATMAP_MAX_RESOLUTION: 512,
  HEATMAP_MIN_RESOLUTION: 64
};

// =============================================================================
// DEVICE PROFILES
// =============================================================================

export const DEVICE_PROFILES = {
  high: {
    name: 'High Performance',
    maxLayers: 5,
    maxHeatmaps: 2,
    heatmapResolution: 512,
    maxPoints: 30000,
    enableBlending: true,
    enableAnimations: true
  },
  medium: {
    name: 'Medium Performance',
    maxLayers: 4,
    maxHeatmaps: 1,
    heatmapResolution: 256,
    maxPoints: 15000,
    enableBlending: true,
    enableAnimations: true
  },
  low: {
    name: 'Low Performance',
    maxLayers: 3,
    maxHeatmaps: 1,
    heatmapResolution: 128,
    maxPoints: 5000,
    enableBlending: false,
    enableAnimations: false
  },
  mobile: {
    name: 'Mobile',
    maxLayers: 3,
    maxHeatmaps: 1,
    heatmapResolution: 128,
    maxPoints: 3000,
    enableBlending: false,
    enableAnimations: false
  }
};

// =============================================================================
// PERFORMANCE BUDGET CLASS
// =============================================================================

class PerformanceBudget {
  constructor() {
    this.profile = this._detectProfile();
    this.metrics = {
      fps: [],
      renderTimes: [],
      memoryUsage: 0,
      activePointCount: 0,
      activeTileCount: 0
    };
    this.warnings = [];
    this.listeners = new Set();
  }
  
  // Detect device profile
  _detectProfile() {
    // Check for mobile
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (isMobile) {
      return DEVICE_PROFILES.mobile;
    }
    
    // Check memory (if available)
    if (navigator.deviceMemory) {
      if (navigator.deviceMemory >= 8) return DEVICE_PROFILES.high;
      if (navigator.deviceMemory >= 4) return DEVICE_PROFILES.medium;
      return DEVICE_PROFILES.low;
    }
    
    // Check hardware concurrency
    if (navigator.hardwareConcurrency) {
      if (navigator.hardwareConcurrency >= 8) return DEVICE_PROFILES.high;
      if (navigator.hardwareConcurrency >= 4) return DEVICE_PROFILES.medium;
      return DEVICE_PROFILES.low;
    }
    
    // Default to medium
    return DEVICE_PROFILES.medium;
  }
  
  // Set profile manually
  setProfile(profileId) {
    this.profile = DEVICE_PROFILES[profileId] || this.profile;
    this._notify({ type: 'profile_changed', profile: this.profile });
  }
  
  // Add listener
  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  // Notify listeners
  _notify(event) {
    this.listeners.forEach(cb => cb(event));
  }
  
  // Record FPS sample
  recordFPS(fps) {
    this.metrics.fps.push(fps);
    if (this.metrics.fps.length > 60) {
      this.metrics.fps.shift();
    }
    
    // Check thresholds
    if (fps < PERFORMANCE_THRESHOLDS.FPS_MINIMUM) {
      this._addWarning('critical_fps', `FPS critique: ${fps.toFixed(1)}`);
    } else if (fps < PERFORMANCE_THRESHOLDS.FPS_WARNING) {
      this._addWarning('low_fps', `FPS faible: ${fps.toFixed(1)}`);
    }
    
    return fps >= PERFORMANCE_THRESHOLDS.FPS_MINIMUM;
  }
  
  // Record render time
  recordRenderTime(ms) {
    this.metrics.renderTimes.push(ms);
    if (this.metrics.renderTimes.length > 30) {
      this.metrics.renderTimes.shift();
    }
    
    if (ms > PERFORMANCE_THRESHOLDS.MAX_RENDER_TIME) {
      this._addWarning('slow_render', `Rendu lent: ${ms.toFixed(0)}ms`);
    }
    
    return ms <= PERFORMANCE_THRESHOLDS.MAX_RENDER_TIME;
  }
  
  // Check if can add layer
  canAddLayer(layerId, currentLayerCount) {
    if (currentLayerCount >= this.profile.maxLayers) {
      this._addWarning('max_layers', `Limite de couches atteinte: ${this.profile.maxLayers}`);
      return false;
    }
    return true;
  }
  
  // Check if can add heatmap
  canAddHeatmap(currentHeatmapCount) {
    if (currentHeatmapCount >= this.profile.maxHeatmaps) {
      this._addWarning('max_heatmaps', `Limite de heatmaps atteinte: ${this.profile.maxHeatmaps}`);
      return false;
    }
    return true;
  }
  
  // Check if can add points
  canAddPoints(pointCount) {
    const newTotal = this.metrics.activePointCount + pointCount;
    if (newTotal > this.profile.maxPoints) {
      this._addWarning('max_points', `Limite de points atteinte: ${this.profile.maxPoints}`);
      return false;
    }
    return true;
  }
  
  // Update point count
  updatePointCount(count) {
    this.metrics.activePointCount = count;
    
    if (count > this.profile.maxPoints * 0.8) {
      this._addWarning('high_point_count', `Nombre de points élevé: ${count}`);
    }
  }
  
  // Get optimal heatmap resolution
  getHeatmapResolution(dataSize) {
    let resolution = this.profile.heatmapResolution;
    
    // Reduce resolution for large datasets
    if (dataSize > 1000) {
      resolution = Math.min(resolution, 256);
    }
    if (dataSize > 5000) {
      resolution = Math.min(resolution, 128);
    }
    
    return Math.max(PERFORMANCE_THRESHOLDS.HEATMAP_MIN_RESOLUTION, resolution);
  }
  
  // Check if blending is enabled
  isBlendingEnabled() {
    return this.profile.enableBlending;
  }
  
  // Check if animations are enabled
  isAnimationsEnabled() {
    return this.profile.enableAnimations;
  }
  
  // Add warning
  _addWarning(type, message) {
    const warning = { type, message, timestamp: Date.now() };
    this.warnings.push(warning);
    
    // Keep last 20 warnings
    if (this.warnings.length > 20) {
      this.warnings.shift();
    }
    
    this._notify({ type: 'warning', warning });
  }
  
  // Clear warnings
  clearWarnings() {
    this.warnings = [];
  }
  
  // Get average FPS
  getAverageFPS() {
    if (this.metrics.fps.length === 0) return 60;
    return this.metrics.fps.reduce((a, b) => a + b, 0) / this.metrics.fps.length;
  }
  
  // Get average render time
  getAverageRenderTime() {
    if (this.metrics.renderTimes.length === 0) return 0;
    return this.metrics.renderTimes.reduce((a, b) => a + b, 0) / this.metrics.renderTimes.length;
  }
  
  // Get performance status
  getStatus() {
    const avgFPS = this.getAverageFPS();
    const avgRender = this.getAverageRenderTime();
    
    let status = 'good';
    if (avgFPS < PERFORMANCE_THRESHOLDS.FPS_WARNING) status = 'warning';
    if (avgFPS < PERFORMANCE_THRESHOLDS.FPS_MINIMUM) status = 'critical';
    
    return {
      status,
      fps: avgFPS,
      renderTime: avgRender,
      profile: this.profile.name,
      warnings: this.warnings.slice(-5),
      limits: {
        maxLayers: this.profile.maxLayers,
        maxPoints: this.profile.maxPoints,
        heatmapResolution: this.profile.heatmapResolution
      }
    };
  }
  
  // Get recommendations
  getRecommendations() {
    const recommendations = [];
    const avgFPS = this.getAverageFPS();
    
    if (avgFPS < PERFORMANCE_THRESHOLDS.FPS_WARNING) {
      recommendations.push('Réduisez le nombre de couches actives');
      recommendations.push('Désactivez les heatmaps haute résolution');
    }
    
    if (this.metrics.activePointCount > this.profile.maxPoints * 0.7) {
      recommendations.push('Réduisez le rayon d\'analyse');
    }
    
    return recommendations;
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const performanceBudget = new PerformanceBudget();

// =============================================================================
// REACT HOOK
// =============================================================================

import { useState, useEffect, useCallback } from 'react';

export function usePerformanceBudget() {
  const [status, setStatus] = useState(performanceBudget.getStatus());
  
  useEffect(() => {
    const unsubscribe = performanceBudget.addListener((event) => {
      setStatus(performanceBudget.getStatus());
    });
    
    // FPS monitoring
    let lastTime = performance.now();
    let frameCount = 0;
    let animationId;
    
    const measureFPS = () => {
      frameCount++;
      const now = performance.now();
      
      if (now - lastTime >= 1000) {
        const fps = frameCount * 1000 / (now - lastTime);
        performanceBudget.recordFPS(fps);
        frameCount = 0;
        lastTime = now;
      }
      
      animationId = requestAnimationFrame(measureFPS);
    };
    
    animationId = requestAnimationFrame(measureFPS);
    
    return () => {
      unsubscribe();
      cancelAnimationFrame(animationId);
    };
  }, []);
  
  return {
    ...status,
    canAddLayer: performanceBudget.canAddLayer.bind(performanceBudget),
    canAddHeatmap: performanceBudget.canAddHeatmap.bind(performanceBudget),
    canAddPoints: performanceBudget.canAddPoints.bind(performanceBudget),
    getHeatmapResolution: performanceBudget.getHeatmapResolution.bind(performanceBudget),
    getRecommendations: performanceBudget.getRecommendations.bind(performanceBudget),
    setProfile: performanceBudget.setProfile.bind(performanceBudget)
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export default PerformanceBudget;
