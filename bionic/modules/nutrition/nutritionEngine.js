/**
 * BIONIC™ Nutrition Module - Main Engine
 * Orchestrateur principal du module de nutrition
 */

import { getSpeciesProfile } from "./speciesProfiles.js";
import { classifyResources } from "./resourceClassifier.js";
import { detectDeficiencies } from "./deficiencyDetector.js";
import { generateRecommendations } from "./recommendationEngine.js";

export async function runNutritionEngine(speciesKey, landcoverData = []) {
  const speciesProfile = getSpeciesProfile(speciesKey);

  if (!speciesProfile) {
    throw new Error(`Espèce inconnue ou non supportée : ${speciesKey}`);
  }

  const resources = classifyResources(landcoverData);
  const deficiencyReport = detectDeficiencies(speciesProfile, resources);
  const recommendations = generateRecommendations(deficiencyReport, speciesProfile);

  return {
    species: {
      key: speciesKey,
      profile: speciesProfile
    },
    resources,
    deficiencyReport,
    recommendations,
    meta: {
      module: "NutritionEngine",
      version: "0.1.0",
      timestamp: new Date().toISOString()
    }
  };
}
