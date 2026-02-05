/**
 * BIONIC™ P3 - BehaviorEngine v3.0 Service
 * =========================================
 * Service API pour le module auto-calibrant v3.
 * 
 * Endpoints:
 * - GET  /api/bionic/behavior-v3/status
 * - POST /api/bionic/behavior-v3/train
 * - POST /api/bionic/behavior-v3/calibrate
 * - GET  /api/bionic/behavior-v3/weights
 * - GET  /api/bionic/behavior-v3/history
 * - POST /api/bionic/behavior-v3/rollback
 * - GET  /api/bionic/behavior-v3/metrics
 * - POST /api/bionic/behavior-v3/feedback
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;
const BASE_PATH = '/api/bionic/behavior-v3';

/**
 * Helper pour les requêtes API
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_URL}${BASE_PATH}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const response = await fetch(url, { ...defaultOptions, ...options });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

/**
 * Récupère le statut du BehaviorEngine v3.0
 */
export async function getEngineStatus() {
  return apiRequest('/status');
}

/**
 * Récupère les métriques de performance
 */
export async function getEngineMetrics() {
  return apiRequest('/metrics');
}

/**
 * Lance un entraînement ML
 * @param {Object} options - Options d'entraînement
 * @param {boolean} options.useSimulatedData - Utiliser données simulées
 * @param {boolean} options.useFeedbackData - Utiliser feedback utilisateur
 * @param {string[]} options.speciesFilter - Filtrer par espèces
 * @param {number} options.maxIterations - Max itérations
 * @param {number} options.learningRate - Taux d'apprentissage
 */
export async function trainModel(options = {}) {
  const body = {
    use_simulated_data: options.useSimulatedData ?? true,
    use_feedback_data: options.useFeedbackData ?? true,
    species_filter: options.speciesFilter || null,
    max_iterations: options.maxIterations || 100,
    learning_rate: options.learningRate || 0.1,
  };
  
  return apiRequest('/train', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Effectue une calibration des pondérations
 * @param {Object} options - Options de calibration
 * @param {string} options.species - Espèce cible
 * @param {string} options.territory - Territoire
 * @param {string} options.season - Saison (optionnel)
 */
export async function calibrateWeights(options = {}) {
  const body = {
    species: options.species || 'deer',
    territory: options.territory || 'quebec',
    season: options.season || null,
  };
  
  return apiRequest('/calibrate', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Récupère les pondérations actuelles
 */
export async function getCurrentWeights() {
  return apiRequest('/weights');
}

/**
 * Récupère l'historique des calibrations
 * @param {Object} options - Options de filtrage
 * @param {string} options.species - Filtrer par espèce
 * @param {number} options.limit - Nombre max de résultats
 * @param {boolean} options.includeRolledBack - Inclure les rollbacks
 */
export async function getCalibrationHistory(options = {}) {
  const params = new URLSearchParams();
  if (options.species) params.append('species', options.species);
  if (options.limit) params.append('limit', options.limit);
  if (options.includeRolledBack) params.append('include_rolled_back', 'true');
  
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiRequest(`/history${query}`);
}

/**
 * Exporte l'historique des calibrations
 * @param {string} format - Format d'export ('json' ou 'csv')
 */
export async function exportHistory(format = 'json') {
  return apiRequest(`/history/export?format=${format}`);
}

/**
 * Soumet un feedback chasseur
 * @param {Object} feedback - Données du feedback
 */
export async function submitFeedback(feedback) {
  const body = {
    latitude: feedback.latitude,
    longitude: feedback.longitude,
    species: feedback.species || 'deer',
    feedback_type: feedback.feedbackType,
    rating: feedback.rating || null,
    notes: feedback.notes || null,
    weather_conditions: feedback.weatherConditions || null,
    time_of_day: feedback.timeOfDay || null,
    hunt_duration_hours: feedback.huntDurationHours || null,
    animals_observed: feedback.animalsObserved || null,
    harvest_success: feedback.harvestSuccess || null,
  };
  
  return apiRequest('/feedback', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Récupère le résumé des feedbacks
 */
export async function getFeedbackSummary() {
  return apiRequest('/feedback/summary');
}

/**
 * Effectue un rollback vers une calibration précédente
 * @param {string} calibrationId - ID de la calibration cible
 * @param {string} reason - Raison du rollback
 * @param {string} notes - Notes additionnelles
 */
export async function rollbackCalibration(calibrationId, reason, notes = null) {
  const body = {
    calibration_id: calibrationId,
    reason: reason,
    notes: notes,
  };
  
  return apiRequest('/rollback', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Récupère les candidats pour rollback
 * @param {number} limit - Nombre max de candidats
 */
export async function getRollbackCandidates(limit = 10) {
  return apiRequest(`/rollback/candidates?limit=${limit}`);
}

/**
 * Active/désactive le mode maintenance
 * @param {boolean} enabled - Activer le mode maintenance
 */
export async function setMaintenanceMode(enabled) {
  return apiRequest('/maintenance', {
    method: 'POST',
    body: JSON.stringify({ enabled }),
  });
}

// Export par défaut
const behaviorV3Service = {
  getEngineStatus,
  getEngineMetrics,
  trainModel,
  calibrateWeights,
  getCurrentWeights,
  getCalibrationHistory,
  exportHistory,
  submitFeedback,
  getFeedbackSummary,
  rollbackCalibration,
  getRollbackCandidates,
  setMaintenanceMode,
};

export default behaviorV3Service;
