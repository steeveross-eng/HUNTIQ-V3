/**
 * BIONIC™ SIGÉOM Module - Mineral Lick Detector
 * Détection des zones à potentiel de licks minéraux
 */

export function detectMineralLickPotential(classifiedZones = []) {
  const potentialLicks = [];

  classifiedZones.forEach(zone => {
    if (!zone.classification) return;

    const mineralScore = zone.classification.mineral_score || 0;
    const permeability = zone.classification.permeability_score || 50;
    const type = zone.classification.id;

    // High mineral + low permeability = mineral accumulation
    const lickScore = (mineralScore * 0.7) + ((100 - permeability) * 0.3);

    if (lickScore >= 60) {
      potentialLicks.push({
        zone_id: zone.id,
        type: zone.classification.label,
        lick_score: Math.round(lickScore),
        likelihood: lickScore >= 80 ? "high" : lickScore >= 70 ? "medium" : "low",
        factors: {
          mineral_content: zone.classification.mineral_content,
          permeability: zone.classification.permeability
        },
        hunting_note: getMineralLickNote(lickScore, type)
      });
    }
  });

  return potentialLicks.sort((a, b) => b.lick_score - a.lick_score);
}

function getMineralLickNote(score, type) {
  if (score >= 80) {
    return `Zone à fort potentiel de lick naturel (${type}). Vérifiez les traces d'activité animale.`;
  }
  if (score >= 70) {
    return `Potentiel modéré de lick minéral. Les cervidés peuvent fréquenter cette zone.`;
  }
  return `Faible potentiel de lick naturel. Zone secondaire.`;
}

export function identifyDrainagePatterns(classifiedZones = []) {
  const drainageZones = [];

  classifiedZones.forEach(zone => {
    if (!zone.classification) return;

    const permeability = zone.classification.permeability;
    
    if (permeability === "very_low" || permeability === "low") {
      drainageZones.push({
        zone_id: zone.id,
        type: zone.classification.label,
        drainage: "poor",
        note: "Zone à drainage faible - Potentiel de mare saisonnière"
      });
    }
  });

  return drainageZones;
}
