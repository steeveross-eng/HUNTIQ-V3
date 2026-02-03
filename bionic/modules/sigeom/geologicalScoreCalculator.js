/**
 * BIONIC™ SIGÉOM Module - Geological Score Calculator
 * Calcul du score de chasse basé sur la géologie
 */

export function calculateGeologicalScore(coverage, mineralLicks) {
  let score = 50; // Base score
  const factors = [];

  // Factor 1: Mineral lick potential (max +25)
  const highLicks = mineralLicks?.filter(l => l.likelihood === "high").length || 0;
  const mediumLicks = mineralLicks?.filter(l => l.likelihood === "medium").length || 0;
  const lickImpact = Math.min((highLicks * 10) + (mediumLicks * 5), 25);
  score += lickImpact;
  factors.push({
    factor: "Licks minéraux",
    value: highLicks + mediumLicks,
    impact: lickImpact,
    status: highLicks > 0 ? "excellent" : mediumLicks > 0 ? "présent" : "absent"
  });

  // Factor 2: Geological diversity (max +15)
  const categories = Object.values(coverage?.percentages || {})
    .filter(p => p > 5).length;
  const diversityImpact = Math.min(categories * 4, 15);
  score += diversityImpact;
  factors.push({
    factor: "Diversité géologique",
    value: categories,
    impact: diversityImpact,
    status: categories >= 3 ? "excellent" : categories >= 2 ? "bon" : "limité"
  });

  // Factor 3: Quaternary deposits (better for wildlife) (max +10)
  const quaternaryPercent = coverage?.percentages?.quaternaire || 0;
  const quaternaryImpact = Math.min(Math.round(quaternaryPercent / 10), 10);
  score += quaternaryImpact;
  factors.push({
    factor: "Dépôts quaternaires",
    value: `${Math.round(quaternaryPercent)}%`,
    impact: quaternaryImpact,
    status: quaternaryPercent > 50 ? "dominant" : quaternaryPercent > 20 ? "présent" : "limité"
  });

  // Ensure bounds
  score = Math.max(0, Math.min(100, score));

  // Determine level
  let level, recommendation;
  if (score >= 80) {
    level = "excellent";
    recommendation = "Géologie favorable à la faune. Présence probable de licks naturels.";
  } else if (score >= 60) {
    level = "bon";
    recommendation = "Bonne diversité géologique. Recherchez les zones d'accumulation minérale.";
  } else if (score >= 40) {
    level = "moyen";
    recommendation = "Géologie standard. Facteur secondaire pour la chasse.";
  } else {
    level = "faible";
    recommendation = "Géologie peu favorable. Concentrez-vous sur d'autres facteurs.";
  }

  return {
    score,
    level,
    recommendation,
    factors
  };
}

export function generateGeologicalRecommendations(geoScore, mineralLicks) {
  const recs = [];

  if (mineralLicks?.length > 0) {
    const highPotential = mineralLicks.filter(l => l.likelihood === "high");
    if (highPotential.length > 0) {
      recs.push(`${highPotential.length} zone(s) à fort potentiel de lick minéral identifiée(s). Installation de caméra recommandée.`);
    }
  }

  if (geoScore?.factors?.some(f => f.factor === "Dépôts quaternaires" && f.impact >= 5)) {
    recs.push("Dépôts quaternaires présents - Sols propices à la végétation diversifiée.");
  }

  if (geoScore?.score < 40) {
    recs.push("Géologie peu favorable - Priorisez les analyses hydrologiques et végétales.");
  }

  return recs;
}
