/**
 * BIONIC™ P1.5 - Layer Orchestration Engine
 * ===========================================
 * Gestion des priorités visuelles, interactions et superposition des couches.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

// =============================================================================
// LAYER PRIORITIES (Z-INDEX ORDER)
// =============================================================================

export const LAYER_PRIORITIES = {
  // Base layers (bottom)
  landcover: { zIndex: 10, category: 'base', blendMode: 'normal' },
  
  // Data layers (middle)
  nutrition: { zIndex: 20, category: 'heatmap', blendMode: 'multiply' },
  population: { zIndex: 30, category: 'points', blendMode: 'normal' },
  
  // Overlay layers (top)
  corridors: { zIndex: 40, category: 'lines', blendMode: 'normal' },
  pressure: { zIndex: 50, category: 'overlay', blendMode: 'color-burn' },
  
  // UI layers (topmost)
  highlights: { zIndex: 100, category: 'ui', blendMode: 'normal' },
  markers: { zIndex: 110, category: 'ui', blendMode: 'normal' }
};

// =============================================================================
// LAYER INTERACTION RULES
// =============================================================================

export const LAYER_INTERACTIONS = {
  // When corridor is active, enhance visibility
  corridors: {
    enhances: ['landcover'],
    conflicts: [],
    recommended: ['nutrition', 'population']
  },
  
  // Landcover works well with most layers
  landcover: {
    enhances: [],
    conflicts: [],
    recommended: ['corridors', 'nutrition']
  },
  
  // Nutrition heatmap can overlay landcover
  nutrition: {
    enhances: ['landcover'],
    conflicts: ['pressure'], // Too much visual noise
    recommended: ['corridors']
  },
  
  // Population points work on any base
  population: {
    enhances: [],
    conflicts: [],
    recommended: ['landcover', 'corridors']
  },
  
  // Pressure zones can conflict with heatmaps
  pressure: {
    enhances: [],
    conflicts: ['nutrition'],
    recommended: ['landcover', 'corridors']
  }
};

// =============================================================================
// SUPERPOSITION PRESETS
// =============================================================================

export const SUPERPOSITION_PRESETS = {
  // Habitat analysis
  habitat: {
    name: 'Analyse habitat',
    layers: ['landcover', 'corridors', 'nutrition'],
    opacities: { landcover: 0.7, corridors: 0.9, nutrition: 0.5 },
    description: 'Couvert végétal + corridors + nutrition'
  },
  
  // Population focus
  population_focus: {
    name: 'Focus population',
    layers: ['landcover', 'population', 'corridors'],
    opacities: { landcover: 0.5, population: 0.8, corridors: 0.6 },
    description: 'Densité animale avec corridors'
  },
  
  // Hunting strategy
  hunting: {
    name: 'Stratégie chasse',
    layers: ['landcover', 'corridors', 'pressure'],
    opacities: { landcover: 0.6, corridors: 0.8, pressure: 0.5 },
    description: 'Pression de chasse et corridors'
  },
  
  // Full analysis
  full: {
    name: 'Analyse complète',
    layers: ['landcover', 'corridors', 'nutrition', 'population', 'pressure'],
    opacities: { landcover: 0.5, corridors: 0.7, nutrition: 0.4, population: 0.6, pressure: 0.3 },
    description: 'Toutes les couches combinées'
  },
  
  // Minimal (clean view)
  minimal: {
    name: 'Vue minimale',
    layers: ['landcover', 'corridors'],
    opacities: { landcover: 0.8, corridors: 0.9 },
    description: 'Couvert et corridors seulement'
  }
};

// =============================================================================
// LAYER ORCHESTRATION ENGINE
// =============================================================================

class LayerOrchestrationEngine {
  constructor() {
    this.activeLayers = new Set();
    this.layerStates = new Map();
    this.listeners = new Set();
    this.performanceBudget = null;
  }
  
  // Initialize with performance budget
  init(performanceBudget = null) {
    this.performanceBudget = performanceBudget;
    return this;
  }
  
  // Add listener for state changes
  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  // Notify listeners
  _notify(event) {
    this.listeners.forEach(cb => cb(event));
  }
  
  // Activate a layer
  activateLayer(layerId, options = {}) {
    const priority = LAYER_PRIORITIES[layerId];
    if (!priority) {
      console.warn(`Unknown layer: ${layerId}`);
      return false;
    }
    
    // Check performance budget
    if (this.performanceBudget) {
      const canAdd = this.performanceBudget.canAddLayer(layerId, this.activeLayers.size);
      if (!canAdd) {
        console.warn(`Performance budget exceeded for layer: ${layerId}`);
        return false;
      }
    }
    
    // Check for conflicts
    const interactions = LAYER_INTERACTIONS[layerId];
    if (interactions?.conflicts) {
      for (const conflictId of interactions.conflicts) {
        if (this.activeLayers.has(conflictId)) {
          console.warn(`Layer conflict: ${layerId} conflicts with ${conflictId}`);
          // Auto-reduce opacity of conflicting layer
          this._reduceConflictingLayer(conflictId);
        }
      }
    }
    
    this.activeLayers.add(layerId);
    this.layerStates.set(layerId, {
      visible: true,
      opacity: options.opacity ?? priority.defaultOpacity ?? 0.7,
      zIndex: priority.zIndex,
      blendMode: options.blendMode ?? priority.blendMode,
      ...options
    });
    
    this._notify({ type: 'layer_activated', layerId, state: this.layerStates.get(layerId) });
    return true;
  }
  
  // Deactivate a layer
  deactivateLayer(layerId) {
    if (!this.activeLayers.has(layerId)) return false;
    
    this.activeLayers.delete(layerId);
    this.layerStates.delete(layerId);
    
    this._notify({ type: 'layer_deactivated', layerId });
    return true;
  }
  
  // Toggle layer
  toggleLayer(layerId, options = {}) {
    if (this.activeLayers.has(layerId)) {
      return this.deactivateLayer(layerId);
    }
    return this.activateLayer(layerId, options);
  }
  
  // Set layer opacity
  setLayerOpacity(layerId, opacity) {
    if (!this.layerStates.has(layerId)) return false;
    
    const state = this.layerStates.get(layerId);
    state.opacity = Math.max(0, Math.min(1, opacity));
    
    this._notify({ type: 'layer_opacity_changed', layerId, opacity: state.opacity });
    return true;
  }
  
  // Set layer visibility
  setLayerVisibility(layerId, visible) {
    if (!this.layerStates.has(layerId)) return false;
    
    const state = this.layerStates.get(layerId);
    state.visible = visible;
    
    this._notify({ type: 'layer_visibility_changed', layerId, visible });
    return true;
  }
  
  // Apply superposition preset
  applyPreset(presetId) {
    const preset = SUPERPOSITION_PRESETS[presetId];
    if (!preset) {
      console.warn(`Unknown preset: ${presetId}`);
      return false;
    }
    
    // Deactivate all current layers
    for (const layerId of this.activeLayers) {
      this.deactivateLayer(layerId);
    }
    
    // Activate preset layers with specified opacities
    for (const layerId of preset.layers) {
      this.activateLayer(layerId, {
        opacity: preset.opacities[layerId] ?? 0.7
      });
    }
    
    this._notify({ type: 'preset_applied', presetId, preset });
    return true;
  }
  
  // Get sorted layers by z-index
  getSortedLayers() {
    const layers = Array.from(this.activeLayers).map(id => ({
      id,
      ...this.layerStates.get(id),
      priority: LAYER_PRIORITIES[id]
    }));
    
    return layers.sort((a, b) => a.zIndex - b.zIndex);
  }
  
  // Get recommended layers based on active layers
  getRecommendedLayers() {
    const recommended = new Set();
    
    for (const layerId of this.activeLayers) {
      const interactions = LAYER_INTERACTIONS[layerId];
      if (interactions?.recommended) {
        interactions.recommended.forEach(r => {
          if (!this.activeLayers.has(r)) {
            recommended.add(r);
          }
        });
      }
    }
    
    return Array.from(recommended);
  }
  
  // Check if adding a layer would cause conflicts
  checkConflicts(layerId) {
    const interactions = LAYER_INTERACTIONS[layerId];
    if (!interactions?.conflicts) return [];
    
    return interactions.conflicts.filter(c => this.activeLayers.has(c));
  }
  
  // Reduce opacity of conflicting layer
  _reduceConflictingLayer(layerId) {
    const state = this.layerStates.get(layerId);
    if (state) {
      state.opacity = Math.min(state.opacity, 0.3);
      this._notify({ type: 'layer_opacity_changed', layerId, opacity: state.opacity, reason: 'conflict' });
    }
  }
  
  // Get current state snapshot
  getSnapshot() {
    return {
      activeLayers: Array.from(this.activeLayers),
      layerStates: Object.fromEntries(this.layerStates),
      sortedLayers: this.getSortedLayers(),
      recommendedLayers: this.getRecommendedLayers()
    };
  }
  
  // Restore from snapshot
  restoreFromSnapshot(snapshot) {
    this.activeLayers.clear();
    this.layerStates.clear();
    
    for (const layerId of snapshot.activeLayers) {
      const state = snapshot.layerStates[layerId];
      this.activeLayers.add(layerId);
      this.layerStates.set(layerId, { ...state });
    }
    
    this._notify({ type: 'snapshot_restored', snapshot });
  }
  
  // Clear all layers
  clear() {
    this.activeLayers.clear();
    this.layerStates.clear();
    this._notify({ type: 'cleared' });
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const layerOrchestrator = new LayerOrchestrationEngine();

// =============================================================================
// REACT HOOK
// =============================================================================

import { useState, useEffect, useCallback } from 'react';

export function useLayerOrchestration() {
  const [state, setState] = useState(layerOrchestrator.getSnapshot());
  
  useEffect(() => {
    const unsubscribe = layerOrchestrator.addListener((event) => {
      setState(layerOrchestrator.getSnapshot());
    });
    
    return unsubscribe;
  }, []);
  
  const activateLayer = useCallback((layerId, options) => {
    return layerOrchestrator.activateLayer(layerId, options);
  }, []);
  
  const deactivateLayer = useCallback((layerId) => {
    return layerOrchestrator.deactivateLayer(layerId);
  }, []);
  
  const toggleLayer = useCallback((layerId, options) => {
    return layerOrchestrator.toggleLayer(layerId, options);
  }, []);
  
  const setLayerOpacity = useCallback((layerId, opacity) => {
    return layerOrchestrator.setLayerOpacity(layerId, opacity);
  }, []);
  
  const applyPreset = useCallback((presetId) => {
    return layerOrchestrator.applyPreset(presetId);
  }, []);
  
  return {
    ...state,
    activateLayer,
    deactivateLayer,
    toggleLayer,
    setLayerOpacity,
    applyPreset,
    checkConflicts: layerOrchestrator.checkConflicts.bind(layerOrchestrator),
    clear: layerOrchestrator.clear.bind(layerOrchestrator)
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export default LayerOrchestrationEngine;
