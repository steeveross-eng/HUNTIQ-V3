/**
 * BIONIC™ Nutrition Module - Deficiency Detector
 * Détection des carences nutritionnelles sur un territoire
 */

import { safeAverage, round } from "./utils/math.js";

export function computeSiteAverages(siteResources = []) {
  const energyValues = [];
  const proteinValues = [];
  const calciumValues = [];
  const phosphorusValues = [];

  siteResources.forEach(r => {
    if (!r.nutrition) return;
    const n = r.nutrition;
    if (typeof n.energy === "number") energyValues.push(n.energy);
    if (typeof n.protein === "number") proteinValues.push(n.protein);
    if (typeof n.calcium === "number") calciumValues.push(n.calcium);
    if (typeof n.phosphorus === "number") phosphorusValues.push(n.phosphorus);
  });

  return {
    energy: round(safeAverage(energyValues)),
    protein: round(safeAverage(proteinValues)),
    calcium: round(safeAverage(calciumValues)),
    phosphorus: round(safeAverage(phosphorusValues))
  };
}

export function detectDeficiencies(speciesNeeds, siteResources = []) {
  const siteAvg = computeSiteAverages(siteResources);

  if (!siteAvg.energy && !siteAvg.protein && !siteAvg.calcium && !siteAvg.phosphorus) {
    return {
      status: "no_data",
      message: "Aucune donnée nutritionnelle exploitable pour ce territoire.",
      siteAvg,
      details: {}
    };
  }

  const details = {
    energy: {
      status: siteAvg.energy < speciesNeeds.energy ? "carence" : "ok",
      site: siteAvg.energy,
      need: speciesNeeds.energy
    },
    protein: {
      status: siteAvg.protein < speciesNeeds.protein ? "carence" : "ok",
      site: siteAvg.protein,
      need: speciesNeeds.protein
    },
    calcium: {
      status: siteAvg.calcium < speciesNeeds.calcium ? "carence" : "ok",
      site: siteAvg.calcium,
      need: speciesNeeds.calcium
    },
    phosphorus: {
      status: siteAvg.phosphorus < speciesNeeds.phosphorus ? "carence" : "ok",
      site: siteAvg.phosphorus,
      need: speciesNeeds.phosphorus
    }
  };

  const hasDeficiency = Object.values(details).some(d => d.status === "carence");

  return {
    status: hasDeficiency ? "deficiencies_detected" : "no_deficiency",
    siteAvg,
    details
  };
}
