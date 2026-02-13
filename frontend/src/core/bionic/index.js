/**
 * BIONIC™ Core Module Index
 * Exports centralisés pour le système BIONIC
 */

// Configuration
export { 
  getBionicConfig, 
  updateBionicConfig, 
  resetBionicConfigToDefaults,
  loadBionicConfig,
  DEFAULTS as BIONIC_DEFAULTS 
} from './bionicConfig';

// Scoring
export {
  scoreSlope,
  scoreWaterDistance,
  scoreHydroComplexity,
  scoreHumidity,
  scoreNDVI,
  scoreStandType,
  scoreStandTransition,
  scoreSunExposure,
  scoreThermalComfort,
  scoreVisibility,
  scoreDominantPosition,
  scoreCorridors,
  scoreTrails,
  scoreConnectivity,
  scoreFeedingZone,
  scoreRestingZone,
  calculateHabitatScore,
  calculateRutScore,
  calculateSalinesScore,
  calculateAffutsScore,
  calculateTrajetsScore,
  calculatePeuplementsScore,
  calculateBionicScore,
  getScoresForWaypoint
} from './bionicScoring';

// Modèle hybride
export {
  applyRulesEngine,
  applyAIAdjustment,
  calculateHybridScore,
  generateRecommendations
} from './bionicHybridModel';

// Météo
export {
  fetchWeatherData,
  findNextOptimalWindow,
  getWindDirectionText,
  getWeatherDescription,
  THERMAL_STATES,
  FRONT_TYPES
} from './bionicWeatherEngine';

// Stratégie
export { getStrategyForWaypoint } from './bionicStrategyEngine';

// Data Adapter
export {
  adaptWaypointData,
  adaptTerrainData,
  adaptVegetationData,
  adaptHydroData,
  adaptLayerData
} from './bionicDataAdapter';

// Types et constantes
export const BIONIC_LAYERS = [
  { id: 'habitats', name: 'Habitats optimaux', icon: '🏠', color: '#22c55e' },
  { id: 'rut', name: 'Rut potentiel', icon: '💕', color: '#e91e63' },
  { id: 'salines', name: 'Salines potentielles', icon: '🧂', color: '#00bcd4' },
  { id: 'affuts', name: 'Affûts potentiels', icon: '🎯', color: '#9c27b0' },
  { id: 'trajets', name: 'Trajets de chasse', icon: '🛤️', color: '#ff9800' },
  { id: 'peuplements', name: 'Peuplements forestiers', icon: '🌲', color: '#4caf50' },
  { id: 'ensoleillement', name: 'Ensoleillement', icon: '☀️', color: '#ffeb3b' },
  { id: 'orientation', name: 'Orientation', icon: '🧭', color: '#2196f3' },
  { id: 'hydro', name: 'Hydrographie avancée', icon: '💧', color: '#1976d2' },
  { id: 'alimentation', name: 'Zones d\'alimentation', icon: '🍃', color: '#8bc34a' },
  { id: 'repos', name: 'Zones de repos', icon: '🌙', color: '#795548' },
  { id: 'ndvi', name: 'NDVI / Densité végétale', icon: '🌿', color: '#66bb6a' },
  { id: 'pentes', name: 'Pentes', icon: '⛰️', color: '#ff7043' },
  { id: 'altitude', name: 'Altitude relative', icon: '📊', color: '#78909c' },
  { id: 'corridors', name: 'Corridors fauniques', icon: '🦌', color: '#ff5722' }
];

export const SCORE_CATEGORIES = [
  { id: 'habitat', key: 'score_H', name: 'Habitat', icon: '🏠', weight: 0.25 },
  { id: 'rut', key: 'score_R', name: 'Rut', icon: '💕', weight: 0.20 },
  { id: 'salines', key: 'score_S', name: 'Salines', icon: '🧂', weight: 0.10 },
  { id: 'affuts', key: 'score_A', name: 'Affûts', icon: '🎯', weight: 0.20 },
  { id: 'trajets', key: 'score_T', name: 'Trajets', icon: '🛤️', weight: 0.15 },
  { id: 'peuplements', key: 'score_P', name: 'Peuplements', icon: '🌲', weight: 0.10 }
];
