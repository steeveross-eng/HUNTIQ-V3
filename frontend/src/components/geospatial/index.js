/**
 * HUNTIQ V3 - Geospatial Components
 * Export all geospatial-related components
 * 
 * Updated with BIONIC™ P1 + P1.5 Géo-Suite components
 */

// Legacy components
export { default as HuntingPotentialAnalysis } from './HuntingPotentialAnalysis';
export { default as DataSourcesPanel } from './DataSourcesPanel';
export { default as TerritoryMap } from './TerritoryMap';
export { default as WeatherPanel } from './WeatherPanel';
export { default as WMSLayerSelector } from './WMSLayerSelector';
export { default as HydroAnalysisPanel } from './HydroAnalysisPanel';
export { default as EnvironmentAnalysisPanel } from './EnvironmentAnalysisPanel';
export { default as CurrentConditionsPanel } from './CurrentConditionsPanel';

// =============================================================================
// BIONIC™ P1 Géo-Suite Components
// =============================================================================

// Main Panel (orchestrator)
export { default as GeoSuitePanel } from './GeoSuitePanel';

// Analysis Cards (5 engines)
export { default as CorridorAnalysisCard } from './CorridorAnalysisCard';
export { default as LandcoverAnalysisCard } from './LandcoverAnalysisCard';
export { default as NutritionAnalysisCard } from './NutritionAnalysisCard';
export { default as PopulationDensityCard } from './PopulationDensityCard';
export { default as HuntingPressureCard } from './HuntingPressureCard';

// Species Selector
export { default as SpeciesSelector } from './SpeciesSelector';
export { 
  CompactSpeciesSelector, 
  GridSpeciesSelector, 
  HorizontalSpeciesSelector 
} from './SpeciesSelector';

// Score Gauges
export {
  CircularGauge,
  LinearGauge,
  MiniGauge,
  MultiScoreGauge
} from './GeoSuiteScoreGauge';

// =============================================================================
// BIONIC™ P1.5 Advanced Visualization Components
// =============================================================================

// Heatmap Rendering
export { default as HeatmapRenderer, MultiLayerHeatmap } from './HeatmapRenderer';

// Interactive Legend
export { default as InteractiveLegend, MiniLegend } from './InteractiveLegend';

// Advanced Layer Controls
export { default as LayerControlsAdvanced } from './LayerControlsAdvanced';

// Layer Overlay Panel
export { default as LayerOverlayPanel } from './LayerOverlayPanel';

// Mode Panels (Species & Territory)
export { default as SpeciesModePanel } from './SpeciesModePanel';
export { default as TerritoryModePanel, CompactTerritorySelector } from './TerritoryModePanel';

// Fusion Score Placeholder (P2 Ready)
export { default as FusionScorePlaceholder, MiniFusionIndicator } from './FusionScorePlaceholder';

// Layer Orchestration Engine
export { 
  default as LayerOrchestrationEngine,
  layerOrchestrator,
  useLayerOrchestration,
  LAYER_PRIORITIES,
  LAYER_INTERACTIONS,
  SUPERPOSITION_PRESETS
} from './LayerOrchestrationEngine';

// =============================================================================
// BIONIC™ P1.5 Performance Modules
// =============================================================================

// Performance Budget
export { 
  default as PerformanceBudget,
  performanceBudget,
  usePerformanceBudget,
  PERFORMANCE_THRESHOLDS,
  DEVICE_PROFILES
} from './performance/PerformanceBudget';

// Heatmap Preprocessor
export { 
  default as HeatmapPreprocessor,
  heatmapPreprocessor,
  useHeatmapPreprocessor,
  HEATMAP_CONFIGS
} from './performance/HeatmapPreprocessor';

// Layer Priority System
export {
  default as LayerPrioritySystem,
  layerPrioritySystem,
  useLayerPriority,
  LAYER_PRIORITY_ORDER,
  LAYER_CONFLICTS
} from './performance/LayerPrioritySystem';

// Heatmap Cache Layer
export {
  default as HeatmapCacheLayer,
  heatmapCache,
  useHeatmapCache
} from './performance/HeatmapCacheLayer';

// UI Interaction Logger
export {
  default as UIInteractionLogger,
  interactionLogger,
  useInteractionLogger,
  INTERACTION_TYPES
} from './performance/UIInteractionLogger';

// =============================================================================
// BIONIC™ P1.5 Main Orchestrator
// =============================================================================

// Advanced Visualization Panel (Main P1.5 Component)
export { default as AdvancedVisualizationPanel } from './AdvancedVisualizationPanel';

// =============================================================================
// BIONIC™ P2 BehaviorFusionEngine Components
// =============================================================================

// Fusion Score Panel (Main P2 Component)
export { default as FusionScorePanel } from './FusionScorePanel';

// =============================================================================
// PHASE P3: BEHAVIORENGINE V3.0 AUTO-CALIBRANT
// =============================================================================

// BehaviorV3 Panel (Main P3 Component - ML Auto-Calibration)
export { default as BehaviorV3Panel } from './BehaviorV3Panel';
