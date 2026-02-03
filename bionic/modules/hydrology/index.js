/**
 * BIONIC™ Hydrology Module - Index
 * Point d'entrée unique pour le module hydrologie
 */

export * from "./hydrologyEngine.js";
export * from "./waterSources.js";
export * from "./waterClassifier.js";
export * from "./proximityAnalyzer.js";
export * from "./hydroScoreCalculator.js";

// Module metadata for orchestrator registration
export const moduleInfo = {
  id: "hydrology",
  name: "Hydrology Engine",
  version: "0.1.0",
  description: "Analyse hydrologique des territoires de chasse",
  author: "BIONIC™",
  dependencies: [],
  dataSource: "GRHQ - Données Québec",
  license: "CC-BY 4.0",
  exports: [
    "runHydrologyEngine",
    "getAllWaterSources",
    "classifyWaterFeatures",
    "analyzeWaterProximity",
    "calculateHydroHuntingScore"
  ]
};
