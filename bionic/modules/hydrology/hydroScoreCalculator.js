/**
 * BIONIC™ Hydrology Module - Hunting Score Calculator
 * Calcul du score de chasse basé sur l'hydrologie
 */

export function calculateHydroHuntingScore(proximityAnalysis, waterClassification) {
  let score = 50; // Base score
  const factors = [];

  // Factor 1: Proximity to water (max +30)
  const proximityScore = proximityAnalysis?.proximity_score || 0;
  const proximityImpact = Math.round(proximityScore * 0.3);
  score += proximityImpact;
  factors.push({
    factor: "Proximité eau",
    value: proximityScore,
    impact: proximityImpact,
    status: proximityScore > 70 ? "excellent" : proximityScore > 40 ? "bon" : "faible"
  });

  // Factor 2: Water diversity (max +15)
  const waterTypes = new Set(
    waterClassification
      ?.filter(f => f.classificationFlag === "ok")
      .map(f => f.type)
  );
  const diversityScore = Math.min(waterTypes.size * 3, 15);
  score += diversityScore;
  factors.push({
    factor: "Diversité hydro",
    value: waterTypes.size,
    impact: diversityScore,
    status: waterTypes.size >= 3 ? "excellent" : waterTypes.size >= 2 ? "bon" : "limité"
  });

  // Factor 3: Corridor presence (max +10)
  const hasCorridors = waterClassification?.some(
    f => f.classification?.wildlife_corridor === true
  );
  const corridorImpact = hasCorridors ? 10 : 0;
  score += corridorImpact;
  factors.push({
    factor: "Corridors",
    value: hasCorridors ? "présents" : "absents",
    impact: corridorImpact,
    status: hasCorridors ? "optimal" : "absent"
  });

  // Factor 4: Critical habitats (wetlands/swamps for moose) (max +10)
  const criticalHabitats = waterClassification?.filter(
    f => f.type === "marecage" || f.type === "tourbiere"
  ).length || 0;
  const habitatImpact = Math.min(criticalHabitats * 5, 10);
  score += habitatImpact;
  factors.push({
    factor: "Habitats critiques",
    value: criticalHabitats,
    impact: habitatImpact,
    status: criticalHabitats >= 2 ? "excellent" : criticalHabitats >= 1 ? "présent" : "absent"
  });

  // Ensure score bounds
  score = Math.max(0, Math.min(100, score));

  // Determine level
  let level, recommendation;
  if (score >= 80) {
    level = "excellent";
    recommendation = "Zone hydrologiquement idéale pour la chasse. Concentration probable de gibier près des points d'eau.";
  } else if (score >= 60) {
    level = "bon";
    recommendation = "Bonne présence d'eau. Surveillez les corridors aquatiques à l'aube et au crépuscule.";
  } else if (score >= 40) {
    level = "moyen";
    recommendation = "Présence d'eau modérée. Les animaux peuvent parcourir de plus grandes distances.";
  } else {
    level = "faible";
    recommendation = "Zone sèche. Le gibier se concentrera aux rares points d'eau disponibles.";
  }

  return {
    score,
    level,
    recommendation,
    factors,
    optimal_for: score >= 70 ? ["orignal", "cerf", "ours_noir"] : ["cerf"]
  };
}

export function generateHydroRecommendations(hydroScore, proximityAnalysis) {
  const recs = [];

  if (proximityAnalysis?.nearest_water) {
    const nearest = proximityAnalysis.nearest_water;
    if (nearest.distance_m <= 200) {
      recs.push(`Point d'eau à ${nearest.distance_m}m (${nearest.feature_type}) - Position d'affût recommandée à 50-100m.`);
    } else if (nearest.distance_m <= 500) {
      recs.push(`Point d'eau le plus proche à ${nearest.distance_m}m. Installez-vous sur un corridor vers cette source.`);
    }
  }

  if (proximityAnalysis?.water_access?.within_100m > 0) {
    recs.push("Plusieurs sources d'eau à proximité immédiate - Zone d'activité intense probable.");
  }

  if (hydroScore?.factors?.some(f => f.factor === "Corridors" && f.impact > 0)) {
    recs.push("Corridors aquatiques identifiés - Privilégiez les intersections avec les sentiers.");
  }

  if (hydroScore?.score < 40) {
    recs.push("Zone à faible densité hydrique - Concentrez vos efforts aux rares points d'eau.");
  }

  return recs;
}
