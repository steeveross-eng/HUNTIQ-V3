/**
 * BIONIC™ P2 - Fusion Service
 * ============================
 * Service API pour le BehaviorFusionEngine.
 * Consomme les scores fusionnés Geo+Behavior.
 * 
 * @version 1.0.0
 * @phase P2
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

// =============================================================================
// FUSION MODES
// =============================================================================

export const FUSION_MODES = {
  BALANCED: 'balanced',
  GEO_DOMINANT: 'geo_dominant',
  BEHAVIOR_DOMINANT: 'behavior',
  ADAPTIVE: 'adaptive',
  CUSTOM: 'custom'
};

// =============================================================================
// API METHODS
// =============================================================================

/**
 * Get fusion engine status
 */
export async function getFusionStatus() {
  const response = await fetch(`${API_URL}/api/bionic/fusion/status`);
  if (!response.ok) throw new Error('Failed to get fusion status');
  return response.json();
}

/**
 * Run full fusion analysis
 */
export async function analyzeFusion(params) {
  const {
    lat,
    lon,
    species = 'deer',
    territory = 'quebec',
    radiusKm = 2.0,
    mode = FUSION_MODES.BALANCED,
    includeHeatmap = true
  } = params;
  
  const queryParams = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    species,
    territory,
    radius_km: radiusKm.toString(),
    mode,
    include_heatmap: includeHeatmap.toString()
  });
  
  const response = await fetch(`${API_URL}/api/bionic/fusion/analyze?${queryParams}`);
  if (!response.ok) throw new Error('Fusion analysis failed');
  return response.json();
}

/**
 * Quick fusion analysis (no heatmap)
 */
export async function quickFusionAnalysis(lat, lon, species = 'deer') {
  const queryParams = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    species
  });
  
  const response = await fetch(`${API_URL}/api/bionic/fusion/analyze/quick?${queryParams}`);
  if (!response.ok) throw new Error('Quick fusion failed');
  return response.json();
}

/**
 * Get fusion data optimized for frontend
 */
export async function getFusionForFrontend(params) {
  const {
    lat,
    lon,
    species = 'deer',
    territory = 'quebec',
    radiusKm = 2.0
  } = params;
  
  const queryParams = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    species,
    territory,
    radius_km: radiusKm.toString()
  });
  
  const response = await fetch(`${API_URL}/api/bionic/fusion/analyze/frontend?${queryParams}`);
  if (!response.ok) throw new Error('Frontend fusion failed');
  return response.json();
}

/**
 * Get fusion heatmap data
 */
export async function getFusionHeatmap(lat, lon, species = 'deer', radiusKm = 2.0) {
  const queryParams = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    species,
    radius_km: radiusKm.toString()
  });
  
  const response = await fetch(`${API_URL}/api/bionic/fusion/heatmap?${queryParams}`);
  if (!response.ok) throw new Error('Heatmap fetch failed');
  return response.json();
}

// =============================================================================
// WEIGHT MANAGEMENT
// =============================================================================

/**
 * Get fusion weights for parameters
 */
export async function getFusionWeights(species = 'deer', territory = 'quebec', mode = 'balanced') {
  const queryParams = new URLSearchParams({ species, territory, mode });
  
  const response = await fetch(`${API_URL}/api/bionic/fusion/weights?${queryParams}`);
  if (!response.ok) throw new Error('Failed to get weights');
  return response.json();
}

/**
 * Get species weight presets
 */
export async function getSpeciesWeightPresets() {
  const response = await fetch(`${API_URL}/api/bionic/fusion/weights/species-presets`);
  if (!response.ok) throw new Error('Failed to get species presets');
  return response.json();
}

/**
 * Get territory modifiers
 */
export async function getTerritoryModifiers() {
  const response = await fetch(`${API_URL}/api/bionic/fusion/weights/territory-modifiers`);
  if (!response.ok) throw new Error('Failed to get territory modifiers');
  return response.json();
}

/**
 * Get seasonal modifiers
 */
export async function getSeasonalModifiers() {
  const response = await fetch(`${API_URL}/api/bionic/fusion/weights/seasonal-modifiers`);
  if (!response.ok) throw new Error('Failed to get seasonal modifiers');
  return response.json();
}

// =============================================================================
// P3 CALIBRATION (PLACEHOLDER)
// =============================================================================

/**
 * Get calibration status (P3)
 */
export async function getCalibrationStatus() {
  const response = await fetch(`${API_URL}/api/bionic/fusion/calibration/status`);
  if (!response.ok) throw new Error('Failed to get calibration status');
  return response.json();
}

/**
 * Submit calibration feedback (P3)
 */
export async function submitCalibrationFeedback(params) {
  const {
    lat,
    lon,
    species = 'deer',
    actualSuccess,
    predictedScore,
    notes = ''
  } = params;
  
  const queryParams = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    species,
    actual_success: actualSuccess.toString(),
    predicted_score: predictedScore.toString(),
    notes
  });
  
  const response = await fetch(`${API_URL}/api/bionic/fusion/calibration/feedback?${queryParams}`, {
    method: 'POST'
  });
  if (!response.ok) throw new Error('Failed to submit feedback');
  return response.json();
}

/**
 * Check fusion compatibility
 */
export async function checkFusionCompatibility() {
  const response = await fetch(`${API_URL}/api/bionic/fusion/compatibility`);
  if (!response.ok) throw new Error('Failed to check compatibility');
  return response.json();
}

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  FUSION_MODES,
  getFusionStatus,
  analyzeFusion,
  quickFusionAnalysis,
  getFusionForFrontend,
  getFusionHeatmap,
  getFusionWeights,
  getSpeciesWeightPresets,
  getTerritoryModifiers,
  getSeasonalModifiers,
  getCalibrationStatus,
  submitCalibrationFeedback,
  checkFusionCompatibility
};
