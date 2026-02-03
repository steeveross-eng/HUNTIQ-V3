/**
 * BIONIC™ SIGÉOM Module - Main Engine
 * Orchestrateur principal du module SIGÉOM
 */

import { classifyGeology, calculateGeologicalCoverage } from "./geologicalClassifier.js";
import { detectMineralLickPotential, identifyDrainagePatterns } from "./mineralLickDetector.js";
import { calculateGeologicalScore, generateGeologicalRecommendations } from "./geologicalScoreCalculator.js";
import { getAllGeologicalTypes } from "./geologicalProfiles.js";

export async function runSigeomEngine(geoData = [], options = {}) {
  const { includeDrainage = true } = options;

  // Step 1: Classify geological zones
  const classifiedZones = classifyGeology(geoData);

  // Step 2: Calculate geological coverage
  const coverage = calculateGeologicalCoverage(classifiedZones);

  // Step 3: Detect mineral lick potential
  const mineralLicks = detectMineralLickPotential(classifiedZones);

  // Step 4: Identify drainage patterns
  const drainagePatterns = includeDrainage 
    ? identifyDrainagePatterns(classifiedZones)
    : [];

  // Step 5: Calculate geological hunting score
  const geoScore = calculateGeologicalScore(coverage, mineralLicks);

  // Step 6: Generate recommendations
  const recommendations = generateGeologicalRecommendations(geoScore, mineralLicks);

  return {
    classified_zones: classifiedZones,
    coverage,
    mineral_licks: mineralLicks,
    drainage_patterns: drainagePatterns,
    geological_score: geoScore,
    recommendations,
    meta: {
      module: "SigeomEngine",
      version: "0.1.0",
      timestamp: new Date().toISOString(),
      data_source: "SIGÉOM - MERN Québec",
      license: "Données ouvertes Québec"
    }
  };
}

export { getAllGeologicalTypes };
