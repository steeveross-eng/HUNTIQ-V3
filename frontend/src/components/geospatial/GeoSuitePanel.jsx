/**
 * BIONIC™ P1 - GeoSuitePanel
 * ===========================
 * Panneau orchestrateur principal de la Géo-Suite.
 * Intègre les 5 moteurs et le système de presets.
 * 
 * @version 1.0.0
 * @architecture P2-Ready avec getFusionOutput()
 */

import React, { useState, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';

// Components
import { SpeciesSelector, CompactSpeciesSelector } from './SpeciesSelector';
import { MultiScoreGauge, CircularGauge } from './GeoSuiteScoreGauge';
import CorridorAnalysisCard from './CorridorAnalysisCard';
import LandcoverAnalysisCard from './LandcoverAnalysisCard';
import NutritionAnalysisCard from './NutritionAnalysisCard';
import PopulationDensityCard from './PopulationDensityCard';
import HuntingPressureCard from './HuntingPressureCard';

// Hooks & Store
import useGeoSuiteStore, { SPECIES_CONFIG, TERRITORY_CONFIG, LAYER_CONFIG } from '../../stores/geoSuiteStore';
import geoSuiteService from '../../services/geosuite.service';

// =============================================================================
// TERRITORY SELECTOR
// =============================================================================

function TerritorySelector({ onChange }) {
  const { selectedTerritory, applyTerritoryPreset } = useGeoSuiteStore();
  
  const handleSelect = (territory) => {
    applyTerritoryPreset(territory);
    onChange?.(territory);
  };
  
  return (
    <div className="flex gap-2" data-testid="territory-selector">
      {Object.entries(TERRITORY_CONFIG).map(([id, config]) => (
        <button
          key={id}
          onClick={() => handleSelect(id)}
          className={`
            flex items-center gap-2 px-3 py-2 rounded-lg border transition-all
            ${selectedTerritory === id
              ? 'bg-blue-50 border-blue-500 text-blue-700'
              : 'bg-white border-gray-200 text-gray-600 hover:border-blue-300'
            }
          `}
        >
          <span>{config.icon}</span>
          <span className="text-sm font-medium">{config.name}</span>
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// LAYER CONTROLS
// =============================================================================

function LayerControls({ onChange }) {
  const { activeLayers, toggleLayer, layerOpacities, setLayerOpacity } = useGeoSuiteStore();
  
  return (
    <div className="space-y-2" data-testid="layer-controls">
      {Object.entries(LAYER_CONFIG).map(([id, config]) => {
        const isActive = activeLayers.includes(id);
        const opacity = layerOpacities[id] ?? config.defaultOpacity;
        
        return (
          <div key={id} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
            {/* Toggle */}
            <button
              onClick={() => { toggleLayer(id); onChange?.(id); }}
              className={`
                w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                ${isActive 
                  ? 'bg-emerald-500 border-emerald-500 text-white' 
                  : 'bg-white border-gray-300'
                }
              `}
            >
              {isActive && (
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
            
            {/* Label */}
            <div className="flex items-center gap-2 flex-1">
              <span>{config.icon}</span>
              <span className="text-sm text-gray-700">{config.name}</span>
            </div>
            
            {/* Opacity slider */}
            {isActive && (
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={opacity * 100}
                  onChange={(e) => setLayerOpacity(id, e.target.value / 100)}
                  className="w-20 h-1 bg-gray-300 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-xs text-gray-500 w-8">{Math.round(opacity * 100)}%</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// RADIUS CONTROL
// =============================================================================

function RadiusControl() {
  const { analysisLocation, setRadius } = useGeoSuiteStore();
  
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600">Rayon:</span>
      <input
        type="range"
        min="0.5"
        max="20"
        step="0.5"
        value={analysisLocation.radiusKm}
        onChange={(e) => setRadius(parseFloat(e.target.value))}
        className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
      />
      <span className="text-sm font-medium text-gray-900 w-12">
        {analysisLocation.radiusKm} km
      </span>
    </div>
  );
}

// =============================================================================
// MOCK MODE TOGGLE (Dev)
// =============================================================================

function MockModeToggle() {
  const { mockMode, setMockMode } = useGeoSuiteStore();
  
  if (process.env.NODE_ENV !== 'development') return null;
  
  return (
    <div className="flex items-center gap-2 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
      <span className="text-yellow-600">🧪</span>
      <span className="text-xs text-yellow-700">Mode Mock</span>
      <button
        onClick={() => setMockMode(!mockMode)}
        className={`
          w-10 h-5 rounded-full transition-all relative
          ${mockMode ? 'bg-yellow-500' : 'bg-gray-300'}
        `}
      >
        <span 
          className={`
            absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all
            ${mockMode ? 'left-5' : 'left-0.5'}
          `}
        />
      </button>
    </div>
  );
}

// =============================================================================
// MAIN PANEL
// =============================================================================

export function GeoSuitePanel({ 
  onAnalyze,
  onLocationChange,
  compact = false,
  showControls = true,
  autoAnalyze = false
}) {
  const store = useGeoSuiteStore();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  
  // Run full analysis
  const runAnalysis = useCallback(async () => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const { lat, lon, radiusKm } = store.analysisLocation;
      const species = [store.selectedSpecies];
      
      // Check mock mode
      if (store.mockMode) {
        // Use mock data
        const { MOCK_DATA } = await import('../../stores/geoSuiteStore');
        store.setAnalysisResult('corridor', MOCK_DATA.corridor);
        store.setAnalysisResult('landcover', MOCK_DATA.landcover);
        store.setAnalysisResult('nutrition', MOCK_DATA.nutrition);
        store.setAnalysisResult('population', MOCK_DATA.population);
        store.setAnalysisResult('pressure', MOCK_DATA.pressure);
        onAnalyze?.({ mock: true });
        return;
      }
      
      // Run full suite
      const result = await geoSuiteService.analyzeAll({
        lat,
        lon,
        radiusKm,
        targetSpecies: species,
        includeCorridors: store.activeLayers.includes('corridors'),
        includeLandcover: store.activeLayers.includes('landcover'),
        includeNutrition: store.activeLayers.includes('nutrition'),
        includePopulation: store.activeLayers.includes('population'),
        includePressure: store.activeLayers.includes('pressure')
      });
      
      // Store results
      if (result.analyses) {
        Object.entries(result.analyses).forEach(([engine, data]) => {
          store.setAnalysisResult(engine, data);
        });
      }
      store.setAnalysisResult('full', result);
      
      onAnalyze?.(result);
    } catch (err) {
      setError(err.message);
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  }, [store, onAnalyze]);
  
  // Auto-analyze on location change
  useEffect(() => {
    if (autoAnalyze && store.analysisLocation.lat && store.analysisLocation.lon) {
      runAnalysis();
    }
  }, [autoAnalyze, store.analysisLocation.lat, store.analysisLocation.lon]);
  
  // Get scores for gauge
  const scores = {
    corridor: store.analysisResults.corridor?.score,
    landcover: store.analysisResults.landcover?.score,
    nutrition: store.analysisResults.nutrition?.score,
    population: store.analysisResults.population?.score,
    pressure: store.analysisResults.pressure?.score
  };
  
  // Compact view
  if (compact) {
    return (
      <div className="bg-white rounded-xl border shadow-sm p-4" data-testid="geosuite-panel-compact">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-gray-900 flex items-center gap-2">
            <span>🗺️</span> Géo-Suite BIONIC™
          </h3>
          <CompactSpeciesSelector />
        </div>
        
        <MultiScoreGauge scores={scores} compact={true} />
        
        <button
          onClick={runAnalysis}
          disabled={isAnalyzing}
          className="mt-4 w-full py-2 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-600 disabled:opacity-50 transition-all"
        >
          {isAnalyzing ? 'Analyse...' : 'Analyser'}
        </button>
      </div>
    );
  }
  
  // Full view
  return (
    <div className="bg-white rounded-xl border shadow-sm overflow-hidden" data-testid="geosuite-panel">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-emerald-50 to-blue-50 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <span>🗺️</span> Géo-Suite BIONIC™
            </h2>
            <p className="text-sm text-gray-500">5 moteurs géospatiaux • North America Ready</p>
          </div>
          <MockModeToggle />
        </div>
      </div>
      
      {/* Controls */}
      {showControls && (
        <div className="p-4 border-b space-y-4">
          {/* Species */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Espèce cible</h4>
            <SpeciesSelector variant="horizontal" showPresetInfo={false} />
          </div>
          
          {/* Territory */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Territoire</h4>
            <TerritorySelector />
          </div>
          
          {/* Radius */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Zone d'analyse</h4>
            <RadiusControl />
          </div>
          
          {/* Layers */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Couches actives</h4>
            <LayerControls />
          </div>
          
          {/* Location display */}
          <div className="p-2 bg-gray-50 rounded-lg text-sm text-gray-600">
            📍 Position: {store.analysisLocation.lat.toFixed(4)}, {store.analysisLocation.lon.toFixed(4)}
          </div>
        </div>
      )}
      
      {/* Analyze button */}
      <div className="p-4 border-b">
        <button
          onClick={runAnalysis}
          disabled={isAnalyzing}
          className="w-full py-3 bg-emerald-500 text-white rounded-lg font-semibold hover:bg-emerald-600 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
          data-testid="analyze-button"
        >
          {isAnalyzing ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Analyse en cours...
            </>
          ) : (
            <>🔍 Lancer l'analyse complète</>
          )}
        </button>
        
        {error && (
          <p className="mt-2 text-sm text-red-600 text-center">❌ {error}</p>
        )}
      </div>
      
      {/* Global Score */}
      <div className="p-4 border-b">
        <MultiScoreGauge scores={scores} />
      </div>
      
      {/* Analysis Cards */}
      <div className="p-4 space-y-4">
        {store.activeLayers.includes('corridors') && (
          <CorridorAnalysisCard 
            data={store.analysisResults.corridor}
            loading={isAnalyzing && !store.analysisResults.corridor}
          />
        )}
        
        {store.activeLayers.includes('landcover') && (
          <LandcoverAnalysisCard 
            data={store.analysisResults.landcover}
            loading={isAnalyzing && !store.analysisResults.landcover}
          />
        )}
        
        {store.activeLayers.includes('nutrition') && (
          <NutritionAnalysisCard 
            data={store.analysisResults.nutrition}
            loading={isAnalyzing && !store.analysisResults.nutrition}
          />
        )}
        
        {store.activeLayers.includes('population') && (
          <PopulationDensityCard 
            data={store.analysisResults.population}
            loading={isAnalyzing && !store.analysisResults.population}
          />
        )}
        
        {store.activeLayers.includes('pressure') && (
          <HuntingPressureCard 
            data={store.analysisResults.pressure}
            loading={isAnalyzing && !store.analysisResults.pressure}
          />
        )}
      </div>
      
      {/* Footer - P2 info */}
      <div className="p-3 bg-gray-50 border-t text-center text-xs text-gray-500">
        <span className="text-emerald-600">✓</span> Compatible BehaviorFusionEngine (P2)
      </div>
    </div>
  );
}

GeoSuitePanel.propTypes = {
  onAnalyze: PropTypes.func,
  onLocationChange: PropTypes.func,
  compact: PropTypes.bool,
  showControls: PropTypes.bool,
  autoAnalyze: PropTypes.bool
};

// P2 Interface
GeoSuitePanel.getFusionOutput = () => {
  const store = useGeoSuiteStore.getState();
  return store.getFusionOutput();
};

export default GeoSuitePanel;
