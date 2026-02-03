/**
 * BIONIC™ Sentinel Module - Index
 * Point d'entrée unique pour le module Sentinel-2
 */

export * from "./sentinelEngine.js";
export * from "./vegetationIndices.js";
export * from "./vegetationAnalyzer.js";
export * from "./vegetationScoreCalculator.js";

// Module metadata for orchestrator registration
export const moduleInfo = {
  id: "sentinel",
  name: "Sentinel Engine",
  version: "0.1.0",
  description: "Analyse de la végétation par imagerie satellite Sentinel-2",
  author: "BIONIC™",
  dependencies: [],
  dataSource: "Copernicus Sentinel-2",
  license: "Free and Open Data Policy",
  exports: [
    "runSentinelEngine",
    "getAllIndices",
    "analyzeVegetation",
    "calculateVegetationScore"
  ]
};
