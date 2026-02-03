/**
 * BIONIC™ Nutrition Module - Index
 * Point d'entrée unique pour le module de nutrition
 * 
 * Ce module est 100% modulaire, remplaçable, testable et extensible.
 * Il peut être appelé depuis l'orchestrateur géospatial BIONIC™.
 */

export * from "./nutritionEngine.js";
export * from "./speciesProfiles.js";
export * from "./resourceClassifier.js";
export * from "./deficiencyDetector.js";
export * from "./recommendationEngine.js";

// Module metadata for orchestrator registration
export const moduleInfo = {
  id: "nutrition",
  name: "Nutrition Engine",
  version: "0.1.0",
  description: "Analyse nutritionnelle des territoires de chasse",
  author: "BIONIC™",
  dependencies: [],
  exports: [
    "runNutritionEngine",
    "getSpeciesProfile",
    "classifyResources",
    "detectDeficiencies",
    "generateRecommendations"
  ]
};
