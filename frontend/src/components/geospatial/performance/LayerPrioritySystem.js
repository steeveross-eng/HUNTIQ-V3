/**
 * BIONIC™ P1.5 - Layer Priority System
 * ======================================
 * Gestion avancée de l'ordre d'affichage des couches.
 * Ordre: corridor > densité > landcover (top to bottom)
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

// =============================================================================
// PRIORITY DEFINITIONS
// =============================================================================

export const LAYER_PRIORITY_ORDER = {
  // Top priority (foreground)
  corridors: {
    priority: 100,
    category: 'primary',
    zIndex: 50,
    blendMode: 'normal',
    description: 'Corridors fauniques - toujours au premier plan'
  },
  
  // High priority (analysis overlays)
  pressure: {
    priority: 90,
    category: 'overlay',
    zIndex: 45,
    blendMode: 'multiply',
    description: 'Pression de chasse - overlay analytique'
  },
  
  // Medium priority (heatmaps)
  nutrition: {
    priority: 70,
    category: 'heatmap',
    zIndex: 35,
    blendMode: 'screen',
    description: 'Nutrition - heatmap de densité alimentaire'
  },
  
  population: {
    priority: 60,
    category: 'heatmap',
    zIndex: 30,
    blendMode: 'multiply',
    description: 'Population - densité animale'
  },
  
  // Base layers (background)
  landcover: {
    priority: 10,
    category: 'base',
    zIndex: 10,
    blendMode: 'normal',
    description: 'Couvert végétal - couche de base'
  },
  
  // Fusion layers (P2)
  fusion: {
    priority: 80,
    category: 'fusion',
    zIndex: 40,
    blendMode: 'overlay',
    description: 'Score fusionné Geo+Behavior'
  }
};

// =============================================================================
// CONFLICT MATRIX
// =============================================================================

export const LAYER_CONFLICTS = {
  // Recommendations when adding these layers (with conflict info)
  corridors: {
    simpleConflicts: [],
    recommended: ['landcover'],
    conflictsWith: [],
    enhances: ['nutrition', 'population']
  },
  landcover: {
    simpleConflicts: [],
    recommended: ['corridors'],
    conflictsWith: [],
    enhances: []
  },
  nutrition: {
    simpleConflicts: ['pressure'], // Both are heatmaps, conflict visually
    recommended: ['landcover', 'corridors'],
    conflictsWith: ['pressure'],
    enhances: ['corridors']
  },
  population: {
    simpleConflicts: [],
    recommended: ['landcover'],
    conflictsWith: [],
    enhances: ['nutrition']
  },
  pressure: {
    simpleConflicts: ['nutrition'], // Both are heatmaps, conflict visually
    recommended: ['landcover', 'corridors'],
    conflictsWith: ['nutrition'],
    enhances: ['corridors']
  }
};

// =============================================================================
// LAYER PRIORITY SYSTEM CLASS
// =============================================================================

class LayerPrioritySystem {
  constructor() {
    this.activeLayers = new Map();
    this.listeners = new Set();
    this.conflictResolutions = new Map();
  }
  
  /**
   * Sort layers by priority (highest first)
   */
  sortByPriority(layerIds) {
    return [...layerIds].sort((a, b) => {
      const priorityA = LAYER_PRIORITY_ORDER[a]?.priority ?? 0;
      const priorityB = LAYER_PRIORITY_ORDER[b]?.priority ?? 0;
      return priorityB - priorityA;
    });
  }
  
  /**
   * Get z-index for a layer
   */
  getZIndex(layerId) {
    return LAYER_PRIORITY_ORDER[layerId]?.zIndex ?? 20;
  }
  
  /**
   * Get blend mode for a layer
   */
  getBlendMode(layerId) {
    return LAYER_PRIORITY_ORDER[layerId]?.blendMode ?? 'normal';
  }
  
  /**
   * Check if adding a layer would cause conflicts
   */
  checkConflicts(layerId, currentLayers) {
    const conflicts = LAYER_CONFLICTS[layerId] || [];
    const activeConflicts = [];
    
    if (Array.isArray(conflicts)) {
      for (const conflictId of conflicts) {
        if (currentLayers.includes(conflictId)) {
          activeConflicts.push({
            layerId: conflictId,
            resolution: 'reduce_opacity',
            suggestedOpacity: 0.3
          });
        }
      }
    } else if (conflicts.conflictsWith) {
      for (const conflictId of conflicts.conflictsWith) {
        if (currentLayers.includes(conflictId)) {
          activeConflicts.push({
            layerId: conflictId,
            resolution: 'reduce_opacity',
            suggestedOpacity: 0.3
          });
        }
      }
    }
    
    return activeConflicts;
  }
  
  /**
   * Get recommended layers to add
   */
  getRecommendations(currentLayers) {
    const recommendations = new Set();
    
    for (const layerId of currentLayers) {
      const config = LAYER_CONFLICTS[layerId];
      if (config?.recommended) {
        for (const rec of config.recommended) {
          if (!currentLayers.includes(rec)) {
            recommendations.add(rec);
          }
        }
      }
    }
    
    return Array.from(recommendations);
  }
  
  /**
   * Get layers that are enhanced by current selection
   */
  getEnhancedLayers(currentLayers) {
    const enhanced = new Set();
    
    for (const layerId of currentLayers) {
      const config = LAYER_CONFLICTS[layerId];
      if (config?.enhances) {
        for (const enhId of config.enhances) {
          if (!currentLayers.includes(enhId)) {
            enhanced.add(enhId);
          }
        }
      }
    }
    
    return Array.from(enhanced);
  }
  
  /**
   * Calculate optimal opacity for each layer to minimize conflicts
   */
  calculateOptimalOpacities(layerIds, baseOpacities = {}) {
    const result = {};
    const conflicts = [];
    
    // First pass: identify conflicts
    for (const layerId of layerIds) {
      const layerConflicts = this.checkConflicts(layerId, layerIds.filter(l => l !== layerId));
      conflicts.push(...layerConflicts);
    }
    
    // Second pass: calculate opacities
    for (const layerId of layerIds) {
      const baseOpacity = baseOpacities[layerId] ?? 0.7;
      const conflict = conflicts.find(c => c.layerId === layerId);
      
      if (conflict) {
        result[layerId] = Math.min(baseOpacity, conflict.suggestedOpacity);
      } else {
        result[layerId] = baseOpacity;
      }
    }
    
    return result;
  }
  
  /**
   * Generate layer stack for rendering
   */
  generateLayerStack(layerIds, opacities = {}) {
    const sorted = this.sortByPriority(layerIds);
    
    return sorted.map((layerId, index) => ({
      id: layerId,
      zIndex: this.getZIndex(layerId),
      blendMode: this.getBlendMode(layerId),
      opacity: opacities[layerId] ?? 0.7,
      priority: LAYER_PRIORITY_ORDER[layerId]?.priority ?? 0,
      category: LAYER_PRIORITY_ORDER[layerId]?.category ?? 'unknown',
      renderOrder: index
    }));
  }
  
  /**
   * Add listener for priority changes
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

export const layerPrioritySystem = new LayerPrioritySystem();

// =============================================================================
// REACT HOOK
// =============================================================================

import { useState, useCallback, useMemo } from 'react';

export function useLayerPriority(layerIds = [], baseOpacities = {}) {
  const sortedLayers = useMemo(() => {
    return layerPrioritySystem.sortByPriority(layerIds);
  }, [layerIds]);
  
  const layerStack = useMemo(() => {
    return layerPrioritySystem.generateLayerStack(layerIds, baseOpacities);
  }, [layerIds, baseOpacities]);
  
  const optimalOpacities = useMemo(() => {
    return layerPrioritySystem.calculateOptimalOpacities(layerIds, baseOpacities);
  }, [layerIds, baseOpacities]);
  
  const conflicts = useMemo(() => {
    const allConflicts = [];
    for (const layerId of layerIds) {
      const others = layerIds.filter(l => l !== layerId);
      allConflicts.push(...layerPrioritySystem.checkConflicts(layerId, others));
    }
    return allConflicts;
  }, [layerIds]);
  
  const recommendations = useMemo(() => {
    return layerPrioritySystem.getRecommendations(layerIds);
  }, [layerIds]);
  
  const getZIndex = useCallback((layerId) => {
    return layerPrioritySystem.getZIndex(layerId);
  }, []);
  
  const getBlendMode = useCallback((layerId) => {
    return layerPrioritySystem.getBlendMode(layerId);
  }, []);
  
  return {
    sortedLayers,
    layerStack,
    optimalOpacities,
    conflicts,
    recommendations,
    getZIndex,
    getBlendMode
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export default LayerPrioritySystem;
