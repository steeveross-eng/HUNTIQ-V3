/**
 * BIONIC™ Hydrology Module - Main Engine
 * Orchestrateur principal du module hydrologie
 */

import { classifyWaterFeatures, calculateWaterCoverage } from "./waterClassifier.js";
import { analyzeWaterProximity, identifyWaterCorridors } from "./proximityAnalyzer.js";
import { calculateHydroHuntingScore, generateHydroRecommendations } from "./hydroScoreCalculator.js";
import { getAllWaterSources } from "./waterSources.js";

export async function runHydrologyEngine(targetPoint, hydroData = [], options = {}) {
  const { totalArea = null, includeCorridors = true } = options;

  // Step 1: Classify water features
  const classifiedFeatures = classifyWaterFeatures(hydroData);

  // Step 2: Calculate water coverage
  const waterCoverage = totalArea 
    ? calculateWaterCoverage(classifiedFeatures, totalArea)
    : null;

  // Step 3: Analyze proximity to target point
  const proximityAnalysis = analyzeWaterProximity(targetPoint, classifiedFeatures);

  // Step 4: Identify wildlife corridors
  const corridors = includeCorridors 
    ? identifyWaterCorridors(classifiedFeatures)
    : [];

  // Step 5: Calculate hunting score
  const hydroScore = calculateHydroHuntingScore(proximityAnalysis, classifiedFeatures);

  // Step 6: Generate recommendations
  const recommendations = generateHydroRecommendations(hydroScore, proximityAnalysis);

  return {
    target_point: targetPoint,
    water_features: classifiedFeatures,
    water_coverage: waterCoverage,
    proximity_analysis: proximityAnalysis,
    corridors,
    hydro_score: hydroScore,
    recommendations,
    meta: {
      module: "HydrologyEngine",
      version: "0.1.0",
      timestamp: new Date().toISOString(),
      data_source: "GRHQ - Données Québec"
    }
  };
}

export { getAllWaterSources };
