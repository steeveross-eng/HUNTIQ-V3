/**
 * BIONIC™ P1.5 - Advanced Visualization Panel
 * =============================================
 * Panneau principal de visualisation avancée intégrant:
 * - Heatmaps multi-moteurs
 * - Superposition de couches
 * - Légendes interactives
 * - Modes Espèce/Territoire
 * - Contrôles avancés
 * - Score de Fusion (P2 Ready)
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

import React, { useState, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';

// Store & Hooks
import useGeoSuiteStore from '../../stores/geoSuiteStore';
import { useLayerOrchestration } from './LayerOrchestrationEngine';
import { usePerformanceBudget } from './performance/PerformanceBudget';
import { useHeatmapCache } from './performance/HeatmapCacheLayer';
import { useInteractionLogger } from './performance/UIInteractionLogger';

// Components P1.5
import { HeatmapRenderer, MultiLayerHeatmap } from './HeatmapRenderer';
import { InteractiveLegend } from './InteractiveLegend';
import LayerControlsAdvanced from './LayerControlsAdvanced';
import LayerOverlayPanel from './LayerOverlayPanel';
import SpeciesModePanel from './SpeciesModePanel';
import TerritoryModePanel from './TerritoryModePanel';
import { FusionScorePlaceholder } from './FusionScorePlaceholder';
import { MultiScoreGauge } from './GeoSuiteScoreGauge';

// =============================================================================
// TAB NAVIGATION
// =============================================================================

function TabNavigation({ activeTab, onTabChange, tabs }) {
  return (
    <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all
            ${activeTab === tab.id 
              ? 'bg-white text-emerald-700 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }
          `}
        >
          <span>{tab.icon}</span>
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// PERFORMANCE STATUS BAR
// =============================================================================

function PerformanceStatusBar({ status, cacheStats }) {
  const statusColor = {
    good: 'bg-green-500',
    warning: 'bg-yellow-500',
    critical: 'bg-red-500'
  };
  
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b text-xs">
      <div className="flex items-center gap-4">
        {/* Performance status */}
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${statusColor[status.status] || 'bg-gray-400'}`} />
          <span className="text-gray-600">{status.fps?.toFixed(0) || '—'} FPS</span>
        </div>
        
        {/* Cache status */}
        <div className="flex items-center gap-2">
          <span>💾</span>
          <span className="text-gray-600">
            Cache: {cacheStats.hitRate} ({cacheStats.entries}/{cacheStats.maxEntries})
          </span>
        </div>
      </div>
      
      {/* Profile */}
      <span className="text-gray-500">
        {status.profile}
      </span>
    </div>
  );
}

// =============================================================================
// HEATMAP VIEW
// =============================================================================

function HeatmapView({ analysisResults, activeLayers, layerOpacities }) {
  const heatmapLayers = useMemo(() => {
    const layers = [];
    
    if (activeLayers.includes('nutrition') && analysisResults.nutrition) {
      layers.push({
        dataType: 'nutrition',
        data: analysisResults.nutrition,
        opacity: layerOpacities.nutrition ?? 0.7
      });
    }
    
    if (activeLayers.includes('population') && analysisResults.population) {
      layers.push({
        dataType: 'population',
        data: analysisResults.population,
        opacity: layerOpacities.population ?? 0.6
      });
    }
    
    if (activeLayers.includes('pressure') && analysisResults.pressure) {
      layers.push({
        dataType: 'pressure',
        data: analysisResults.pressure,
        opacity: layerOpacities.pressure ?? 0.5
      });
    }
    
    return layers;
  }, [activeLayers, analysisResults, layerOpacities]);
  
  if (heatmapLayers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-lg border border-dashed border-gray-300">
        <span className="text-4xl mb-2">🗺️</span>
        <p className="text-gray-600">Activez des couches heatmap pour visualiser</p>
        <p className="text-sm text-gray-500 mt-1">
          (Nutrition, Population ou Pression)
        </p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <h4 className="font-medium text-gray-900 flex items-center gap-2">
        <span>🔥</span> Heatmaps actives
      </h4>
      
      {/* Multi-layer heatmap */}
      <MultiLayerHeatmap 
        layers={heatmapLayers}
        width={600}
        height={400}
        showLegends={true}
      />
      
      {/* Individual heatmaps */}
      <div className="grid grid-cols-2 gap-4">
        {heatmapLayers.map(layer => (
          <div key={layer.dataType} className="bg-white rounded-lg border p-3">
            <h5 className="text-sm font-medium text-gray-700 mb-2 capitalize">
              {layer.dataType}
            </h5>
            <HeatmapRenderer
              dataType={layer.dataType}
              rawData={layer.data}
              width={250}
              height={180}
              opacity={layer.opacity}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// MAIN ADVANCED VISUALIZATION PANEL
// =============================================================================

export function AdvancedVisualizationPanel({
  onAnalyze,
  onModeChange,
  showPerformance = true,
  defaultTab = 'layers'
}) {
  const store = useGeoSuiteStore();
  const performanceStatus = usePerformanceBudget();
  const { stats: cacheStats } = useHeatmapCache();
  const logger = useInteractionLogger();
  
  const [activeTab, setActiveTab] = useState(defaultTab);
  
  // Tabs configuration
  const tabs = [
    { id: 'layers', icon: '🎨', label: 'Couches' },
    { id: 'heatmaps', icon: '🔥', label: 'Heatmaps' },
    { id: 'modes', icon: '🎯', label: 'Modes' },
    { id: 'controls', icon: '⚙️', label: 'Contrôles' },
    { id: 'fusion', icon: '🔮', label: 'Fusion' }
  ];
  
  // Handle tab change
  const handleTabChange = useCallback((tabId) => {
    setActiveTab(tabId);
    logger.log('panel_tab_change', { tabId });
  }, [logger]);
  
  // Scores for gauge
  const scores = useMemo(() => ({
    corridor: store.analysisResults.corridor?.score,
    landcover: store.analysisResults.landcover?.score,
    nutrition: store.analysisResults.nutrition?.score,
    population: store.analysisResults.population?.score,
    pressure: store.analysisResults.pressure?.score
  }), [store.analysisResults]);
  
  return (
    <div 
      className="bg-white rounded-xl border shadow-sm overflow-hidden"
      data-testid="advanced-visualization-panel"
    >
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <span>🎨</span> Visualisations Avancées
            </h2>
            <p className="text-sm text-gray-500">
              BIONIC™ P1.5 • Heatmaps • Superpositions • Contrôles
            </p>
          </div>
          
          {/* Score badge */}
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-purple-600">
              {store.getGlobalScore() ?? '—'}
            </span>
            <span className="text-gray-500">/100</span>
          </div>
        </div>
        
        {/* Tab navigation */}
        <TabNavigation 
          activeTab={activeTab}
          onTabChange={handleTabChange}
          tabs={tabs}
        />
      </div>
      
      {/* Performance status bar */}
      {showPerformance && (
        <PerformanceStatusBar 
          status={performanceStatus}
          cacheStats={cacheStats}
        />
      )}
      
      {/* Tab content */}
      <div className="p-4">
        {/* Layers Tab */}
        {activeTab === 'layers' && (
          <LayerOverlayPanel 
            showVisualization={true}
            showAdvanced={false}
          />
        )}
        
        {/* Heatmaps Tab */}
        {activeTab === 'heatmaps' && (
          <HeatmapView 
            analysisResults={store.analysisResults}
            activeLayers={store.activeLayers}
            layerOpacities={store.layerOpacities}
          />
        )}
        
        {/* Modes Tab */}
        {activeTab === 'modes' && (
          <div className="space-y-6">
            <SpeciesModePanel 
              layout="grid"
              showComparison={true}
              showLayerPreview={true}
              onSpeciesChange={(species) => onModeChange?.('species', species)}
            />
            
            <div className="border-t pt-6">
              <TerritoryModePanel 
                layout="horizontal"
                showSeasonInfo={true}
                onTerritoryChange={(territory) => onModeChange?.('territory', territory)}
              />
            </div>
          </div>
        )}
        
        {/* Controls Tab */}
        {activeTab === 'controls' && (
          <LayerControlsAdvanced />
        )}
        
        {/* Fusion Tab (P2 Ready) */}
        {activeTab === 'fusion' && (
          <div className="space-y-4">
            <FusionScorePlaceholder 
              showBehavior={false}
              showProjected={true}
            />
            
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-700 mb-3">Scores par moteur</h4>
              <MultiScoreGauge scores={scores} />
            </div>
          </div>
        )}
      </div>
      
      {/* Legend (floating) */}
      <InteractiveLegend 
        activeLayers={store.activeLayers}
        layerOpacities={store.layerOpacities}
        onOpacityChange={store.setLayerOpacity}
        position="bottom-right"
      />
      
      {/* Footer */}
      <div className="p-3 bg-gray-50 border-t text-center text-xs text-gray-500">
        <span className="text-purple-600">✓</span> Phase P1.5 Complète • 
        <span className="text-emerald-600 ml-1">✓</span> P2 Ready (BehaviorFusionEngine)
      </div>
    </div>
  );
}

AdvancedVisualizationPanel.propTypes = {
  onAnalyze: PropTypes.func,
  onModeChange: PropTypes.func,
  showPerformance: PropTypes.bool,
  defaultTab: PropTypes.oneOf(['layers', 'heatmaps', 'modes', 'controls', 'fusion'])
};

// =============================================================================
// EXPORTS
// =============================================================================

export default AdvancedVisualizationPanel;
