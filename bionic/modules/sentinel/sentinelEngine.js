/**
 * BIONIC™ Sentinel Module - Main Engine
 * Orchestrateur principal du module Sentinel-2
 */

import { analyzeVegetation, calculateVegetationStats, identifyBrowseZones, identifyCoverZones } from "./vegetationAnalyzer.js";
import { calculateVegetationScore, generateVegetationRecommendations } from "./vegetationScoreCalculator.js";
import { getAllIndices } from "./vegetationIndices.js";

export async function runSentinelEngine(ndviData = [], options = {}) {
  const { includeIndicesInfo = true } = options;

  // Step 1: Analyze vegetation from NDVI data
  const analyzedZones = analyzeVegetation(ndviData);

  // Step 2: Calculate vegetation statistics
  const vegetationStats = calculateVegetationStats(analyzedZones);

  // Step 3: Identify browse zones (food sources)
  const browseZones = identifyBrowseZones(analyzedZones);

  // Step 4: Identify cover zones (shelter)
  const coverZones = identifyCoverZones(analyzedZones);

  // Step 5: Calculate vegetation hunting score
  const vegScore = calculateVegetationScore(vegetationStats, browseZones, coverZones);

  // Step 6: Generate recommendations
  const recommendations = generateVegetationRecommendations(vegScore, browseZones, coverZones);

  return {
    analyzed_zones: analyzedZones,
    vegetation_stats: vegetationStats,
    browse_zones: browseZones,
    cover_zones: coverZones,
    vegetation_score: vegScore,
    recommendations,
    indices_info: includeIndicesInfo ? getAllIndices() : null,
    meta: {
      module: "SentinelEngine",
      version: "0.1.0",
      timestamp: new Date().toISOString(),
      data_source: "Copernicus Sentinel-2",
      license: "Free and Open Data Policy"
    }
  };
}

export { getAllIndices };
