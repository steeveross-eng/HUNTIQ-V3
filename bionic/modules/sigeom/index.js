/**
 * BIONIC™ SIGÉOM Module - Index
 * Point d'entrée unique pour le module SIGÉOM
 */

export * from "./sigeomEngine.js";
export * from "./geologicalProfiles.js";
export * from "./geologicalClassifier.js";
export * from "./mineralLickDetector.js";
export * from "./geologicalScoreCalculator.js";

// Module metadata for orchestrator registration
export const moduleInfo = {
  id: "sigeom",
  name: "SIGÉOM Engine",
  version: "0.1.0",
  description: "Analyse géologique des territoires de chasse",
  author: "BIONIC™",
  dependencies: [],
  dataSource: "SIGÉOM - MERN Québec",
  license: "Données ouvertes Québec",
  exports: [
    "runSigeomEngine",
    "getAllGeologicalTypes",
    "classifyGeology",
    "detectMineralLickPotential",
    "calculateGeologicalScore"
  ]
};
