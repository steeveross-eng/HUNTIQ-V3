/**
 * BIONIC™ Sentinel Module - Vegetation Score Calculator
 * Calcul du score de chasse basé sur la végétation
 */

export function calculateVegetationScore(vegetationStats, browseZones, coverZones) {
  let score = 50; // Base score
  const factors = [];

  // Factor 1: Vegetation diversity (max +20)
  const diversityCount = Object.values(vegetationStats?.counts || {})
    .filter(v => v > 0).length;
  const diversityImpact = Math.min(diversityCount * 4, 20);
  score += diversityImpact;
  factors.push({
    factor: "Diversité végétale",
    value: diversityCount,
    impact: diversityImpact,
    status: diversityCount >= 4 ? "excellent" : diversityCount >= 2 ? "bon" : "limité"
  });

  // Factor 2: Browse availability (max +20)
  const browseCount = browseZones?.length || 0;
  const browseImpact = Math.min(browseCount * 4, 20);
  score += browseImpact;
  factors.push({
    factor: "Zones de broutage",
    value: browseCount,
    impact: browseImpact,
    status: browseCount >= 3 ? "abondant" : browseCount >= 1 ? "présent" : "rare"
  });

  // Factor 3: Cover availability (max +15)
  const coverCount = coverZones?.length || 0;
  const coverImpact = Math.min(coverCount * 3, 15);
  score += coverImpact;
  factors.push({
    factor: "Zones de couvert",
    value: coverCount,
    impact: coverImpact,
    status: coverCount >= 3 ? "abondant" : coverCount >= 1 ? "présent" : "rare"
  });

  // Factor 4: Edge habitat (transition zones) (max +10)
  // Edges between dense and sparse vegetation are optimal
  const densePercent = vegetationStats?.percentages?.dense || 0;
  const moderatePercent = vegetationStats?.percentages?.moderate || 0;
  const hasGoodEdges = densePercent > 20 && moderatePercent > 20;
  const edgeImpact = hasGoodEdges ? 10 : 0;
  score += edgeImpact;
  factors.push({
    factor: "Lisières",
    value: hasGoodEdges ? "présentes" : "limitées",
    impact: edgeImpact,
    status: hasGoodEdges ? "optimal" : "limité"
  });

  // Ensure bounds
  score = Math.max(0, Math.min(100, score));

  // Determine level
  let level, recommendation;
  if (score >= 80) {
    level = "excellent";
    recommendation = "Végétation idéale pour la chasse. Mélange optimal de broutage et de couvert.";
  } else if (score >= 60) {
    level = "bon";
    recommendation = "Bonne diversité végétale. Concentrez-vous sur les lisières forêt-clairière.";
  } else if (score >= 40) {
    level = "moyen";
    recommendation = "Végétation homogène. Cherchez les poches de diversité.";
  } else {
    level = "faible";
    recommendation = "Végétation peu favorable. Le gibier sera dispersé.";
  }

  return {
    score,
    level,
    recommendation,
    factors,
    optimal_for: score >= 60 ? ["cerf", "orignal"] : ["petit_gibier"]
  };
}

export function generateVegetationRecommendations(vegScore, browseZones, coverZones) {
  const recs = [];

  if (browseZones?.length > 0) {
    recs.push(`${browseZones.length} zone(s) de broutage identifiée(s) - Activité alimentaire probable à l'aube et au crépuscule.`);
  }

  if (coverZones?.length > 0) {
    recs.push(`${coverZones.length} zone(s) de couvert dense - Zones de repos diurne pour les cervidés.`);
  }

  if (vegScore?.factors?.some(f => f.factor === "Lisières" && f.impact > 0)) {
    recs.push("Lisières forêt-clairière présentes - Position d'affût idéale en bordure.");
  }

  if (vegScore?.score < 40) {
    recs.push("Végétation peu diversifiée - Recherchez les sources d'eau comme points de concentration.");
  }

  return recs;
}
