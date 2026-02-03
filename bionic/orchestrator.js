/**
 * BIONIC™ Geospatial Orchestrator
 * Orchestrateur central pour l'intégration des modules BIONIC™
 * avec le moteur géospatial
 * 
 * Ce fichier permet d'appeler les modules depuis le backend géospatial.
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
   * @param {string} speciesKey - Species identifier (cerf, orignal, ours_noir)
   * @param {Array} landcoverData - Landcover data from geospatial engine
   */
  async runNutritionAnalysis(speciesKey, landcoverData = []) {
    const nutritionModule = this.getModule("nutrition");
    
    if (!nutritionModule) {
      throw new Error("Module nutrition non disponible");
    }

    const startTime = Date.now();
    const result = await nutritionModule.runNutritionEngine(speciesKey, landcoverData);
    const duration = Date.now() - startTime;

    // Log execution
    this.executionLog.push({
      module: "nutrition",
      speciesKey,
      timestamp: new Date().toISOString(),
      duration,
      success: true
    });

    return result;
  }

  /**
   * Get species profiles from nutrition module
   */
  getSpeciesProfiles() {
    const nutritionModule = this.getModule("nutrition");
    return nutritionModule?.speciesProfiles || {};
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
