/**
 * HUNTIQ V3 - Geospatial Components
 * Export all geospatial-related components
 * 
 * Updated with BIONIC™ P1 Géo-Suite components
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
