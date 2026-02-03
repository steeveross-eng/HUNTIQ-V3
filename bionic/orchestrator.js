/**
 * BIONIC™ Geospatial Orchestrator
 * Orchestrateur central pour l'intégration des modules BIONIC™
 * avec le moteur géospatial
 * 
 * Permet l'exécution individuelle ou combinée des modules:
 * - Nutrition: Analyse nutritionnelle par espèce
 * - Hydrology: Analyse hydrologique et proximité eau
 * - Sentinel: Analyse végétation (NDVI)
 * - SIGÉOM: Analyse géologique et licks minéraux
 */

import { modules, getModule, listModules } from "./modules/index.js";

/**
 * BIONIC Orchestrator Class
 * Gère l'exécution des modules et leur intégration avec les données géospatiales
 */
export class BionicOrchestrator {
  constructor() {
    this.modules = modules;
    this.executionLog = [];
    this.version = "1.0.0";
  }

  /**
   * List all available modules
   */
  listModules() {
    return listModules();
  }

  /**
   * Get a specific module
   */
  getModule(moduleId) {
    return getModule(moduleId);
  }

  /**
   * Execute the nutrition module
   */
  async runNutritionAnalysis(speciesKey, landcoverData = []) {
    const nutritionModule = this.getModule("nutrition");
    if (!nutritionModule) throw new Error("Module nutrition non disponible");

    const startTime = Date.now();
    const result = await nutritionModule.runNutritionEngine(speciesKey, landcoverData);
    this._logExecution("nutrition", { speciesKey }, Date.now() - startTime);

    return result;
  }

  /**
   * Execute the hydrology module
   */
  async runHydrologyAnalysis(targetPoint, hydroData = [], options = {}) {
    const hydrologyModule = this.getModule("hydrology");
    if (!hydrologyModule) throw new Error("Module hydrology non disponible");

    const startTime = Date.now();
    const result = await hydrologyModule.runHydrologyEngine(targetPoint, hydroData, options);
    this._logExecution("hydrology", { targetPoint }, Date.now() - startTime);

    return result;
  }

  /**
   * Execute the Sentinel module
   */
  async runSentinelAnalysis(ndviData = [], options = {}) {
    const sentinelModule = this.getModule("sentinel");
    if (!sentinelModule) throw new Error("Module sentinel non disponible");

    const startTime = Date.now();
    const result = await sentinelModule.runSentinelEngine(ndviData, options);
    this._logExecution("sentinel", {}, Date.now() - startTime);

    return result;
  }

  /**
   * Execute the SIGÉOM module
   */
  async runSigeomAnalysis(geoData = [], options = {}) {
    const sigeomModule = this.getModule("sigeom");
    if (!sigeomModule) throw new Error("Module sigeom non disponible");

    const startTime = Date.now();
    const result = await sigeomModule.runSigeomEngine(geoData, options);
    this._logExecution("sigeom", {}, Date.now() - startTime);

    return result;
  }

  /**
   * Execute combined analysis pipeline
   * Nutrition + Hydrology + Vegetation + Geology
   */
  async runCombinedAnalysis(params) {
    const {
      targetPoint,
      speciesKey = "cerf",
      landcoverData = [],
      hydroData = [],
      ndviData = [],
      geoData = [],
      options = {}
    } = params;

    const startTime = Date.now();
    const results = {};
    const errors = [];

    // Run all modules in parallel
    const promises = [
      this.runNutritionAnalysis(speciesKey, landcoverData)
        .then(r => results.nutrition = r)
        .catch(e => errors.push({ module: "nutrition", error: e.message })),
      
      this.runHydrologyAnalysis(targetPoint, hydroData, options)
        .then(r => results.hydrology = r)
        .catch(e => errors.push({ module: "hydrology", error: e.message })),
      
      this.runSentinelAnalysis(ndviData, options)
        .then(r => results.sentinel = r)
        .catch(e => errors.push({ module: "sentinel", error: e.message })),
      
      this.runSigeomAnalysis(geoData, options)
        .then(r => results.sigeom = r)
        .catch(e => errors.push({ module: "sigeom", error: e.message }))
    ];

    await Promise.all(promises);

    // Calculate combined score
    const combinedScore = this._calculateCombinedScore(results);
    const combinedRecommendations = this._combineRecommendations(results);

    this._logExecution("combined", { speciesKey, targetPoint }, Date.now() - startTime);

    return {
      target_point: targetPoint,
      species: speciesKey,
      modules: results,
      combined_score: combinedScore,
      combined_recommendations: combinedRecommendations,
      errors: errors.length > 0 ? errors : null,
      meta: {
        orchestrator: "BIONIC™ Orchestrator",
        version: this.version,
        timestamp: new Date().toISOString(),
        modules_executed: Object.keys(results).length,
        total_duration_ms: Date.now() - startTime
      }
    };
  }

  /**
   * Calculate combined hunting score from all modules
   */
  _calculateCombinedScore(results) {
    const weights = {
      nutrition: 0.25,
      hydrology: 0.25,
      sentinel: 0.25,
      sigeom: 0.25
    };

    let totalWeight = 0;
    let weightedSum = 0;
    const components = [];

    if (results.nutrition?.deficiency_report?.status === "no_deficiency") {
      const score = 80; // Good nutrition = high score
      weightedSum += score * weights.nutrition;
      totalWeight += weights.nutrition;
      components.push({ module: "nutrition", score, weight: weights.nutrition });
    } else if (results.nutrition) {
      const score = 50;
      weightedSum += score * weights.nutrition;
      totalWeight += weights.nutrition;
      components.push({ module: "nutrition", score, weight: weights.nutrition });
    }

    if (results.hydrology?.hydro_score?.score) {
      const score = results.hydrology.hydro_score.score;
      weightedSum += score * weights.hydrology;
      totalWeight += weights.hydrology;
      components.push({ module: "hydrology", score, weight: weights.hydrology });
    }

    if (results.sentinel?.vegetation_score?.score) {
      const score = results.sentinel.vegetation_score.score;
      weightedSum += score * weights.sentinel;
      totalWeight += weights.sentinel;
      components.push({ module: "sentinel", score, weight: weights.sentinel });
    }

    if (results.sigeom?.geological_score?.score) {
      const score = results.sigeom.geological_score.score;
      weightedSum += score * weights.sigeom;
      totalWeight += weights.sigeom;
      components.push({ module: "sigeom", score, weight: weights.sigeom });
    }

    const finalScore = totalWeight > 0 ? Math.round(weightedSum / totalWeight) : 0;

    let level;
    if (finalScore >= 80) level = "excellent";
    else if (finalScore >= 60) level = "bon";
    else if (finalScore >= 40) level = "moyen";
    else level = "faible";

    return {
      score: finalScore,
      level,
      components,
      weights_used: weights
    };
  }

  /**
   * Combine recommendations from all modules
   */
  _combineRecommendations(results) {
    const allRecs = [];

    if (results.nutrition?.recommendations) {
      allRecs.push(...results.nutrition.recommendations.map(r => ({
        module: "nutrition",
        recommendation: r
      })));
    }

    if (results.hydrology?.recommendations) {
      allRecs.push(...results.hydrology.recommendations.map(r => ({
        module: "hydrology",
        recommendation: r
      })));
    }

    if (results.sentinel?.recommendations) {
      allRecs.push(...results.sentinel.recommendations.map(r => ({
        module: "sentinel",
        recommendation: r
      })));
    }

    if (results.sigeom?.recommendations) {
      allRecs.push(...results.sigeom.recommendations.map(r => ({
        module: "sigeom",
        recommendation: r
      })));
    }

    return allRecs;
  }

  /**
   * Log execution for debugging
   */
  _logExecution(module, params, duration) {
    this.executionLog.push({
      module,
      params,
      timestamp: new Date().toISOString(),
      duration_ms: duration,
      success: true
    });

    // Keep only last 100 entries
    if (this.executionLog.length > 100) {
      this.executionLog = this.executionLog.slice(-100);
    }
  }

  /**
   * Get species profiles from nutrition module
   */
  getSpeciesProfiles() {
    const nutritionModule = this.getModule("nutrition");
    return nutritionModule?.speciesProfiles || {};
  }

  /**
   * Get water source types from hydrology module
   */
  getWaterSourceTypes() {
    const hydrologyModule = this.getModule("hydrology");
    return hydrologyModule?.getAllWaterSources?.() || [];
  }

  /**
   * Get vegetation indices from sentinel module
   */
  getVegetationIndices() {
    const sentinelModule = this.getModule("sentinel");
    return sentinelModule?.getAllIndices?.() || [];
  }

  /**
   * Get geological types from sigeom module
   */
  getGeologicalTypes() {
    const sigeomModule = this.getModule("sigeom");
    return sigeomModule?.getAllGeologicalTypes?.() || [];
  }

  /**
   * Get execution history
   */
  getExecutionLog() {
    return this.executionLog;
  }

  /**
   * Clear execution log
   */
  clearExecutionLog() {
    this.executionLog = [];
  }
}

// Singleton instance
export const orchestrator = new BionicOrchestrator();

// Re-export modules for direct access
export { modules, getModule, listModules };
