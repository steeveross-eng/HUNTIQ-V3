/**
 * BIONIC™ P1 - GeoSuite State Manager
 * =====================================
 * Gestionnaire d'état centralisé pour la Géo-Suite.
 * Gère: espèce, territoire, couches actives, transparence, presets.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// =============================================================================
// SPECIES CONFIGURATIONS
// =============================================================================

export const SPECIES_CONFIG = {
  deer: {
    id: 'deer',
    name: 'Cerf de Virginie',
    icon: '🦌',
    color: '#8B4513',
    layers: ['corridors', 'landcover', 'nutrition', 'population', 'pressure'],
    defaultLayers: ['corridors', 'landcover', 'nutrition'],
    layerOpacities: {
      corridors: 0.8,
      landcover: 0.6,
      nutrition: 0.7,
      population: 0.5,
      pressure: 0.5
    }
  },
  moose: {
    id: 'moose',
    name: 'Orignal',
    icon: '🫎',
    color: '#4A4A4A',
    layers: ['corridors', 'landcover', 'nutrition', 'population', 'pressure'],
    defaultLayers: ['landcover', 'nutrition', 'population'],
    layerOpacities: {
      corridors: 0.7,
      landcover: 0.8,
      nutrition: 0.8,
      population: 0.6,
      pressure: 0.4
    }
  },
  bear: {
    id: 'bear',
    name: 'Ours noir',
    icon: '🐻',
    color: '#2C1810',
    layers: ['corridors', 'landcover', 'nutrition', 'population', 'pressure'],
    defaultLayers: ['nutrition', 'landcover', 'corridors'],
    layerOpacities: {
      corridors: 0.6,
      landcover: 0.7,
      nutrition: 0.9,
      population: 0.5,
      pressure: 0.4
    }
  },
  turkey: {
    id: 'turkey',
    name: 'Dindon sauvage',
    icon: '🦃',
    color: '#8B0000',
    layers: ['corridors', 'landcover', 'nutrition', 'population', 'pressure'],
    defaultLayers: ['landcover', 'nutrition'],
    layerOpacities: {
      corridors: 0.5,
      landcover: 0.8,
      nutrition: 0.8,
      population: 0.4,
      pressure: 0.5
    }
  },
  waterfowl: {
    id: 'waterfowl',
    name: 'Sauvagine',
    icon: '🦆',
    color: '#006400',
    layers: ['corridors', 'landcover', 'population', 'pressure'],
    defaultLayers: ['landcover', 'population'],
    layerOpacities: {
      corridors: 0.4,
      landcover: 0.9,
      nutrition: 0.3,
      population: 0.7,
      pressure: 0.5
    }
  },
  smallgame: {
    id: 'smallgame',
    name: 'Petit gibier',
    icon: '🐰',
    color: '#A0522D',
    layers: ['corridors', 'landcover', 'nutrition', 'pressure'],
    defaultLayers: ['landcover', 'nutrition'],
    layerOpacities: {
      corridors: 0.5,
      landcover: 0.7,
      nutrition: 0.6,
      population: 0.4,
      pressure: 0.5
    }
  }
};

// =============================================================================
// TERRITORY CONFIGURATIONS
// =============================================================================

export const TERRITORY_CONFIG = {
  quebec: {
    id: 'quebec',
    name: 'Québec',
    icon: '⚜️',
    center: { lat: 46.8, lon: -71.2 },
    defaultZoom: 8,
    dataSources: ['sigeom', 'mffp', 'ugaf', 'zec'],
    seasons: {
      deer: { start: 'September', end: 'November' },
      moose: { start: 'September', end: 'October' },
      bear: { start: 'May', end: 'June' }
    }
  },
  canada: {
    id: 'canada',
    name: 'Canada (hors QC)',
    icon: '🍁',
    center: { lat: 50.0, lon: -95.0 },
    defaultZoom: 5,
    dataSources: ['canvec', 'nrcan'],
    seasons: {
      deer: { start: 'October', end: 'December' },
      moose: { start: 'September', end: 'November' }
    }
  },
  usa: {
    id: 'usa',
    name: 'États-Unis',
    icon: '🇺🇸',
    center: { lat: 40.0, lon: -95.0 },
    defaultZoom: 5,
    dataSources: ['nlcd', 'usgs', 'usda', 'usfws'],
    seasons: {
      deer: { start: 'September', end: 'January' },
      turkey: { start: 'April', end: 'May' }
    }
  }
};

// =============================================================================
// LAYER CONFIGURATIONS
// =============================================================================

export const LAYER_CONFIG = {
  corridors: {
    id: 'corridors',
    name: 'Corridors fauniques',
    icon: '🛤️',
    engine: 'corridorEngine',
    type: 'line',
    defaultOpacity: 0.8,
    colors: {
      riparian: '#2196F3',
      ridgeline: '#4CAF50',
      forest_edge: '#8BC34A',
      valley: '#009688',
      agricultural_edge: '#FFC107'
    }
  },
  landcover: {
    id: 'landcover',
    name: 'Couvert végétal',
    icon: '🌲',
    engine: 'landcoverEngine',
    type: 'fill',
    defaultOpacity: 0.6,
    colors: {
      deciduous_forest: '#228B22',
      coniferous_forest: '#006400',
      mixed_forest: '#2E8B57',
      shrubland: '#9ACD32',
      wetland: '#4682B4'
    }
  },
  nutrition: {
    id: 'nutrition',
    name: 'Indice nutritionnel',
    icon: '🍎',
    engine: 'nutritionEngine',
    type: 'heatmap',
    defaultOpacity: 0.7,
    colors: {
      high: '#00E676',
      medium: '#FFEB3B',
      low: '#FF5722'
    }
  },
  population: {
    id: 'population',
    name: 'Densité population',
    icon: '📊',
    engine: 'populationDensityEngine',
    type: 'circle',
    defaultOpacity: 0.7,
    colors: {
      high: '#E91E63',
      medium: '#FF9800',
      low: '#CDDC39'
    }
  },
  pressure: {
    id: 'pressure',
    name: 'Pression de chasse',
    icon: '🎯',
    engine: 'huntingPressureModule',
    type: 'fill',
    defaultOpacity: 0.5,
    colors: {
      extreme: '#B71C1C',
      high: '#E53935',
      moderate: '#FF9800',
      low: '#4CAF50',
      minimal: '#81C784'
    }
  }
};

// =============================================================================
// MOCK DATA (Development Mode)
// =============================================================================

export const MOCK_DATA = {
  corridor: {
    engine_name: 'CorridorEngine',
    engine_version: '1.0.0',
    score: 65,
    level: 'good',
    region: 'quebec',
    data: {
      corridors_count: 5,
      connectivity_index: 0.72,
      corridors: [
        { type: 'riparian', score: 80, length_km: 2.3 },
        { type: 'forest_edge', score: 65, length_km: 1.8 }
      ],
      species_scores: { deer: 75, moose: 60 }
    },
    recommendations: ['✅ Excellente connectivité', '🛤️ Corridor riparian dominant']
  },
  landcover: {
    engine_name: 'LandcoverEngine',
    engine_version: '1.0.0',
    score: 78,
    level: 'good',
    region: 'quebec',
    data: {
      dominant_cover: 'mixed_forest',
      thermal_cover_percent: 65,
      structural_diversity: 0.72,
      species_habitat_scores: { deer: 82, moose: 75, bear: 70 }
    },
    recommendations: ['🌲 Couvert mixte dominant', '✅ Bon couvert thermique']
  },
  nutrition: {
    engine_name: 'NutritionEngine',
    engine_version: '1.0.0',
    score: 55,
    level: 'moderate',
    region: 'quebec',
    data: {
      food_availability: 'moderate',
      mast_index: { score: 45, year_trend: 'average' },
      browse_quality: 60,
      current_season: 'winter'
    },
    recommendations: ['⚠️ Glandée modérée', '❄️ Hiver: zones de brout']
  },
  population: {
    engine_name: 'PopulationDensityEngine',
    engine_version: '1.0.0',
    score: 70,
    level: 'good',
    region: 'quebec',
    data: {
      density_category: 'medium',
      overall_trend: 'stable',
      species_densities: {
        deer: { density_per_100km2: 12.5, trend: 'stable' },
        moose: { density_per_100km2: 4.2, trend: 'stable' }
      }
    },
    recommendations: ['📊 Densité modérée', '📈 Population stable']
  },
  pressure: {
    engine_name: 'HuntingPressureModule',
    engine_version: '1.0.0',
    score: 72,
    level: 'good',
    region: 'quebec',
    data: {
      pressure_level: 'low',
      behavioral_impact: { overall: -0.15 },
      weekly_pattern: { wednesday: 0.3, saturday: 0.85 }
    },
    recommendations: ['🟢 Pression faible', '⏰ Mercredi optimal']
  }
};

// =============================================================================
// ZUSTAND STORE
// =============================================================================

const useGeoSuiteStore = create(
  persist(
    (set, get) => ({
      // === STATE ===
      
      // Current species
      selectedSpecies: 'deer',
      
      // Current territory
      selectedTerritory: 'quebec',
      
      // Analysis location
      analysisLocation: {
        lat: 46.8,
        lon: -71.2,
        radiusKm: 2.0
      },
      
      // Active layers
      activeLayers: ['corridors', 'landcover', 'nutrition'],
      
      // Layer opacities
      layerOpacities: {
        corridors: 0.8,
        landcover: 0.6,
        nutrition: 0.7,
        population: 0.5,
        pressure: 0.5
      },
      
      // Map style
      mapStyle: 'light',
      
      // Analysis results (cache)
      analysisResults: {
        corridor: null,
        landcover: null,
        nutrition: null,
        population: null,
        pressure: null,
        full: null
      },
      
      // Loading states
      loading: {
        corridor: false,
        landcover: false,
        nutrition: false,
        population: false,
        pressure: false,
        full: false
      },
      
      // Errors
      errors: {},
      
      // Mock mode for development
      mockMode: false,
      
      // Panel visibility
      panelOpen: true,
      
      // === ACTIONS ===
      
      // Set species and apply preset
      setSpecies: (species) => {
        const config = SPECIES_CONFIG[species];
        if (config) {
          set({
            selectedSpecies: species,
            activeLayers: config.defaultLayers,
            layerOpacities: config.layerOpacities
          });
        }
      },
      
      // Set territory and update location
      setTerritory: (territory) => {
        const config = TERRITORY_CONFIG[territory];
        if (config) {
          set({
            selectedTerritory: territory,
            analysisLocation: {
              ...get().analysisLocation,
              lat: config.center.lat,
              lon: config.center.lon
            }
          });
        }
      },
      
      // Set analysis location
      setLocation: (lat, lon, radiusKm = null) => {
        set({
          analysisLocation: {
            lat,
            lon,
            radiusKm: radiusKm ?? get().analysisLocation.radiusKm
          }
        });
      },
      
      // Set radius
      setRadius: (radiusKm) => {
        set({
          analysisLocation: {
            ...get().analysisLocation,
            radiusKm
          }
        });
      },
      
      // Toggle layer
      toggleLayer: (layerId) => {
        const current = get().activeLayers;
        if (current.includes(layerId)) {
          set({ activeLayers: current.filter(l => l !== layerId) });
        } else {
          set({ activeLayers: [...current, layerId] });
        }
      },
      
      // Set layer opacity
      setLayerOpacity: (layerId, opacity) => {
        set({
          layerOpacities: {
            ...get().layerOpacities,
            [layerId]: opacity
          }
        });
      },
      
      // Set map style
      setMapStyle: (style) => set({ mapStyle: style }),
      
      // Store analysis result
      setAnalysisResult: (engine, result) => {
        set({
          analysisResults: {
            ...get().analysisResults,
            [engine]: result
          }
        });
      },
      
      // Set loading state
      setLoading: (engine, isLoading) => {
        set({
          loading: {
            ...get().loading,
            [engine]: isLoading
          }
        });
      },
      
      // Set error
      setError: (engine, error) => {
        set({
          errors: {
            ...get().errors,
            [engine]: error
          }
        });
      },
      
      // Clear errors
      clearErrors: () => set({ errors: {} }),
      
      // Toggle mock mode
      setMockMode: (enabled) => set({ mockMode: enabled }),
      
      // Toggle panel
      togglePanel: () => set({ panelOpen: !get().panelOpen }),
      
      // Apply species preset
      applySpeciesPreset: (species) => {
        const config = SPECIES_CONFIG[species];
        if (config) {
          set({
            selectedSpecies: species,
            activeLayers: config.defaultLayers,
            layerOpacities: config.layerOpacities
          });
        }
      },
      
      // Apply territory preset
      applyTerritoryPreset: (territory) => {
        const config = TERRITORY_CONFIG[territory];
        if (config) {
          set({
            selectedTerritory: territory,
            analysisLocation: {
              lat: config.center.lat,
              lon: config.center.lon,
              radiusKm: get().analysisLocation.radiusKm
            }
          });
        }
      },
      
      // Reset to defaults
      reset: () => {
        set({
          selectedSpecies: 'deer',
          selectedTerritory: 'quebec',
          analysisLocation: { lat: 46.8, lon: -71.2, radiusKm: 2.0 },
          activeLayers: ['corridors', 'landcover', 'nutrition'],
          layerOpacities: {
            corridors: 0.8,
            landcover: 0.6,
            nutrition: 0.7,
            population: 0.5,
            pressure: 0.5
          },
          mapStyle: 'light',
          analysisResults: {
            corridor: null,
            landcover: null,
            nutrition: null,
            population: null,
            pressure: null,
            full: null
          },
          loading: {
            corridor: false,
            landcover: false,
            nutrition: false,
            population: false,
            pressure: false,
            full: false
          },
          errors: {},
          mockMode: false
        });
      },
      
      // Get mock data (for development)
      getMockData: (engine) => {
        if (get().mockMode) {
          return MOCK_DATA[engine] || null;
        }
        return null;
      },
      
      // === COMPUTED / GETTERS ===
      
      // Get current species config
      getSpeciesConfig: () => SPECIES_CONFIG[get().selectedSpecies],
      
      // Get current territory config
      getTerritoryConfig: () => TERRITORY_CONFIG[get().selectedTerritory],
      
      // Get active layer configs
      getActiveLayerConfigs: () => {
        return get().activeLayers.map(id => LAYER_CONFIG[id]).filter(Boolean);
      },
      
      // Get global score (average of all engines)
      getGlobalScore: () => {
        const results = get().analysisResults;
        const scores = Object.values(results)
          .filter(r => r && r.score !== undefined)
          .map(r => r.score);
        
        if (scores.length === 0) return null;
        return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
      },
      
      // Check if any analysis is loading
      isAnyLoading: () => {
        return Object.values(get().loading).some(v => v);
      },
      
      // Get fusion output for P2
      getFusionOutput: () => {
        const results = get().analysisResults;
        const outputs = {};
        
        for (const [engine, result] of Object.entries(results)) {
          if (result && result.score !== undefined) {
            outputs[engine] = {
              score_normalized: result.score / 100,
              confidence: result.confidence || 0.7,
              engine_name: result.engine_name,
              level: result.level
            };
          }
        }
        
        return {
          engines: outputs,
          global_score: get().getGlobalScore(),
          species: get().selectedSpecies,
          territory: get().selectedTerritory,
          location: get().analysisLocation,
          fusion_ready: true
        };
      }
    }),
    {
      name: 'bionic-geosuite-state',
      partialize: (state) => ({
        selectedSpecies: state.selectedSpecies,
        selectedTerritory: state.selectedTerritory,
        activeLayers: state.activeLayers,
        layerOpacities: state.layerOpacities,
        mapStyle: state.mapStyle,
        mockMode: state.mockMode
      })
    }
  )
);

export default useGeoSuiteStore;
