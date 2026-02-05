/**
 * BIONIC™ P1.5 - UI Interaction Logger
 * ======================================
 * Logger d'interactions pour QA et optimisation UX.
 * Enregistre les actions utilisateur pour analyse.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

// =============================================================================
// INTERACTION TYPES
// =============================================================================

export const INTERACTION_TYPES = {
  // Layer interactions
  LAYER_TOGGLE: 'layer_toggle',
  LAYER_OPACITY_CHANGE: 'layer_opacity_change',
  LAYER_REORDER: 'layer_reorder',
  
  // Species/Territory
  SPECIES_SELECT: 'species_select',
  TERRITORY_SELECT: 'territory_select',
  
  // Analysis
  ANALYSIS_START: 'analysis_start',
  ANALYSIS_COMPLETE: 'analysis_complete',
  ANALYSIS_ERROR: 'analysis_error',
  
  // Map interactions
  MAP_PAN: 'map_pan',
  MAP_ZOOM: 'map_zoom',
  MAP_CLICK: 'map_click',
  LOCATION_CHANGE: 'location_change',
  RADIUS_CHANGE: 'radius_change',
  
  // UI interactions
  PANEL_TOGGLE: 'panel_toggle',
  PRESET_APPLY: 'preset_apply',
  LEGEND_EXPAND: 'legend_expand',
  CONTROLS_EXPAND: 'controls_expand',
  
  // Heatmap interactions
  HEATMAP_RENDER: 'heatmap_render',
  HEATMAP_CLICK: 'heatmap_click',
  
  // Fusion (P2)
  FUSION_SCORE_VIEW: 'fusion_score_view',
  FUSION_WEIGHT_CHANGE: 'fusion_weight_change',
  
  // Performance
  PERFORMANCE_WARNING: 'performance_warning',
  CACHE_HIT: 'cache_hit',
  CACHE_MISS: 'cache_miss'
};

// =============================================================================
// INTERACTION LOG ENTRY
// =============================================================================

class InteractionLogEntry {
  constructor(type, data = {}, metadata = {}) {
    this.id = this._generateId();
    this.type = type;
    this.data = data;
    this.metadata = {
      ...metadata,
      timestamp: Date.now(),
      sessionId: UIInteractionLogger._sessionId,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown'
    };
  }
  
  _generateId() {
    return `int_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
  }
  
  toJSON() {
    return {
      id: this.id,
      type: this.type,
      data: this.data,
      metadata: this.metadata
    };
  }
}

// =============================================================================
// UI INTERACTION LOGGER CLASS
// =============================================================================

class UIInteractionLogger {
  static _sessionId = `ses_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;
  
  constructor() {
    this.logs = [];
    this.maxLogs = 1000;
    this.listeners = new Set();
    this.filters = new Set();
    this.isEnabled = true;
    this.batchSize = 10;
    this.batchQueue = [];
  }
  
  /**
   * Enable/disable logging
   */
  setEnabled(enabled) {
    this.isEnabled = enabled;
  }
  
  /**
   * Add filter for specific interaction types
   */
  addFilter(type) {
    this.filters.add(type);
  }
  
  /**
   * Remove filter
   */
  removeFilter(type) {
    this.filters.delete(type);
  }
  
  /**
   * Log an interaction
   */
  log(type, data = {}, metadata = {}) {
    if (!this.isEnabled) return null;
    if (this.filters.has(type)) return null;
    
    const entry = new InteractionLogEntry(type, data, metadata);
    
    // Add to logs
    this.logs.push(entry);
    
    // Trim if needed
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }
    
    // Notify listeners
    this._notify({ type: 'log_added', entry });
    
    // Add to batch queue
    this.batchQueue.push(entry);
    if (this.batchQueue.length >= this.batchSize) {
      this._flushBatch();
    }
    
    return entry;
  }
  
  /**
   * Convenience methods for common interactions
   */
  logLayerToggle(layerId, isActive, source = 'user') {
    return this.log(INTERACTION_TYPES.LAYER_TOGGLE, { layerId, isActive }, { source });
  }
  
  logLayerOpacityChange(layerId, opacity, source = 'user') {
    return this.log(INTERACTION_TYPES.LAYER_OPACITY_CHANGE, { layerId, opacity }, { source });
  }
  
  logSpeciesSelect(species, previousSpecies) {
    return this.log(INTERACTION_TYPES.SPECIES_SELECT, { species, previousSpecies });
  }
  
  logTerritorySelect(territory, previousTerritory) {
    return this.log(INTERACTION_TYPES.TERRITORY_SELECT, { territory, previousTerritory });
  }
  
  logAnalysisStart(params) {
    return this.log(INTERACTION_TYPES.ANALYSIS_START, params);
  }
  
  logAnalysisComplete(result, durationMs) {
    return this.log(INTERACTION_TYPES.ANALYSIS_COMPLETE, { 
      success: true, 
      durationMs,
      enginesUsed: result.analyses ? Object.keys(result.analyses) : []
    });
  }
  
  logAnalysisError(error, params) {
    return this.log(INTERACTION_TYPES.ANALYSIS_ERROR, { 
      error: error.message, 
      params 
    });
  }
  
  logLocationChange(lat, lon, source = 'user') {
    return this.log(INTERACTION_TYPES.LOCATION_CHANGE, { lat, lon }, { source });
  }
  
  logRadiusChange(radiusKm, previousRadius) {
    return this.log(INTERACTION_TYPES.RADIUS_CHANGE, { radiusKm, previousRadius });
  }
  
  logPresetApply(presetId, layers) {
    return this.log(INTERACTION_TYPES.PRESET_APPLY, { presetId, layers });
  }
  
  logPerformanceWarning(warning) {
    return this.log(INTERACTION_TYPES.PERFORMANCE_WARNING, warning);
  }
  
  logCacheEvent(hit, dataType, params) {
    return this.log(
      hit ? INTERACTION_TYPES.CACHE_HIT : INTERACTION_TYPES.CACHE_MISS,
      { dataType, params }
    );
  }
  
  /**
   * Get logs by type
   */
  getByType(type) {
    return this.logs.filter(log => log.type === type);
  }
  
  /**
   * Get logs within time range
   */
  getByTimeRange(startMs, endMs) {
    return this.logs.filter(log => {
      const ts = log.metadata.timestamp;
      return ts >= startMs && ts <= endMs;
    });
  }
  
  /**
   * Get recent logs
   */
  getRecent(count = 50) {
    return this.logs.slice(-count);
  }
  
  /**
   * Get interaction statistics
   */
  getStats() {
    const stats = {
      total: this.logs.length,
      byType: {},
      lastHour: 0,
      last5Minutes: 0,
      sessionDuration: Date.now() - parseInt(UIInteractionLogger._sessionId.split('_')[1])
    };
    
    const now = Date.now();
    const hourAgo = now - 60 * 60 * 1000;
    const fiveMinAgo = now - 5 * 60 * 1000;
    
    for (const log of this.logs) {
      // Count by type
      stats.byType[log.type] = (stats.byType[log.type] || 0) + 1;
      
      // Count by time
      const ts = log.metadata.timestamp;
      if (ts >= hourAgo) stats.lastHour++;
      if (ts >= fiveMinAgo) stats.last5Minutes++;
    }
    
    return stats;
  }
  
  /**
   * Get analysis patterns (for UX optimization)
   */
  getAnalysisPatterns() {
    const patterns = {
      mostUsedLayers: {},
      averageRadius: 0,
      preferredSpecies: {},
      preferredTerritory: {},
      analysisCount: 0
    };
    
    const layerLogs = this.getByType(INTERACTION_TYPES.LAYER_TOGGLE);
    const speciesLogs = this.getByType(INTERACTION_TYPES.SPECIES_SELECT);
    const territoryLogs = this.getByType(INTERACTION_TYPES.TERRITORY_SELECT);
    const radiusLogs = this.getByType(INTERACTION_TYPES.RADIUS_CHANGE);
    const analysisLogs = this.getByType(INTERACTION_TYPES.ANALYSIS_COMPLETE);
    
    // Layer usage
    for (const log of layerLogs) {
      if (log.data.isActive) {
        const layer = log.data.layerId;
        patterns.mostUsedLayers[layer] = (patterns.mostUsedLayers[layer] || 0) + 1;
      }
    }
    
    // Species preference
    for (const log of speciesLogs) {
      const species = log.data.species;
      patterns.preferredSpecies[species] = (patterns.preferredSpecies[species] || 0) + 1;
    }
    
    // Territory preference
    for (const log of territoryLogs) {
      const territory = log.data.territory;
      patterns.preferredTerritory[territory] = (patterns.preferredTerritory[territory] || 0) + 1;
    }
    
    // Average radius
    if (radiusLogs.length > 0) {
      const sum = radiusLogs.reduce((acc, log) => acc + (log.data.radiusKm || 0), 0);
      patterns.averageRadius = (sum / radiusLogs.length).toFixed(1);
    }
    
    // Analysis count
    patterns.analysisCount = analysisLogs.length;
    
    return patterns;
  }
  
  /**
   * Export logs to JSON
   */
  export() {
    return {
      sessionId: UIInteractionLogger._sessionId,
      exportedAt: new Date().toISOString(),
      stats: this.getStats(),
      patterns: this.getAnalysisPatterns(),
      logs: this.logs.map(log => log.toJSON())
    };
  }
  
  /**
   * Clear all logs
   */
  clear() {
    this.logs = [];
    this._notify({ type: 'logs_cleared' });
  }
  
  /**
   * Flush batch queue (for future remote logging)
   */
  _flushBatch() {
    if (this.batchQueue.length === 0) return;
    
    // In production, this could send to analytics server
    // For now, just clear the queue
    this._notify({ type: 'batch_flushed', count: this.batchQueue.length });
    this.batchQueue = [];
  }
  
  /**
   * Add listener
   */
  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  /**
   * Notify listeners
   */
  _notify(event) {
    this.listeners.forEach(cb => cb(event));
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const interactionLogger = new UIInteractionLogger();

// =============================================================================
// REACT HOOK
// =============================================================================

import { useState, useEffect, useCallback } from 'react';

export function useInteractionLogger() {
  const [stats, setStats] = useState(interactionLogger.getStats());
  
  useEffect(() => {
    const unsubscribe = interactionLogger.addListener((event) => {
      if (event.type === 'log_added' || event.type === 'logs_cleared') {
        setStats(interactionLogger.getStats());
      }
    });
    
    return unsubscribe;
  }, []);
  
  const log = useCallback((type, data, metadata) => {
    return interactionLogger.log(type, data, metadata);
  }, []);
  
  return {
    stats,
    log,
    // Convenience methods
    logLayerToggle: interactionLogger.logLayerToggle.bind(interactionLogger),
    logLayerOpacityChange: interactionLogger.logLayerOpacityChange.bind(interactionLogger),
    logSpeciesSelect: interactionLogger.logSpeciesSelect.bind(interactionLogger),
    logTerritorySelect: interactionLogger.logTerritorySelect.bind(interactionLogger),
    logAnalysisStart: interactionLogger.logAnalysisStart.bind(interactionLogger),
    logAnalysisComplete: interactionLogger.logAnalysisComplete.bind(interactionLogger),
    logAnalysisError: interactionLogger.logAnalysisError.bind(interactionLogger),
    logLocationChange: interactionLogger.logLocationChange.bind(interactionLogger),
    logRadiusChange: interactionLogger.logRadiusChange.bind(interactionLogger),
    logPresetApply: interactionLogger.logPresetApply.bind(interactionLogger),
    // Analysis
    getPatterns: interactionLogger.getAnalysisPatterns.bind(interactionLogger),
    export: interactionLogger.export.bind(interactionLogger),
    clear: interactionLogger.clear.bind(interactionLogger)
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export default UIInteractionLogger;
