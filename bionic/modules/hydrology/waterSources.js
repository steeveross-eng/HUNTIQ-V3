/**
 * BIONIC™ Hydrology Module - Water Sources Profiles
 * Profils des sources d'eau pour l'analyse hydrologique
 */

export const waterSourceTypes = {
  riviere: {
    id: "riviere",
    label: "Rivière",
    importance_score: 95,
    wildlife_value: "critical",
    seasonal_variation: "high",
    notes: "Source d'eau principale, corridor de déplacement naturel pour la faune."
  },
  ruisseau: {
    id: "ruisseau",
    label: "Ruisseau",
    importance_score: 80,
    wildlife_value: "high",
    seasonal_variation: "medium",
    notes: "Point d'abreuvement régulier, souvent associé à des ravages."
  },
  lac: {
    id: "lac",
    label: "Lac",
    importance_score: 90,
    wildlife_value: "critical",
    seasonal_variation: "low",
    notes: "Source d'eau stable, zone d'alimentation pour l'orignal."
  },
  etang: {
    id: "etang",
    label: "Étang / Mare",
    importance_score: 70,
    wildlife_value: "high",
    seasonal_variation: "high",
    notes: "Point d'eau saisonnier, attractif en période sèche."
  },
  marecage: {
    id: "marecage",
    label: "Marécage",
    importance_score: 85,
    wildlife_value: "critical",
    seasonal_variation: "medium",
    notes: "Habitat critique pour l'orignal, zone de nutrition riche."
  },
  tourbiere: {
    id: "tourbiere",
    label: "Tourbière",
    importance_score: 60,
    wildlife_value: "medium",
    seasonal_variation: "low",
    notes: "Zone humide acide, moins attractive pour les cervidés."
  },
  source: {
    id: "source",
    label: "Source / Résurgence",
    importance_score: 75,
    wildlife_value: "high",
    seasonal_variation: "low",
    notes: "Eau fraîche constante, point d'attraction en toute saison."
  }
};

export function getWaterSourceProfile(sourceKey) {
  return waterSourceTypes[sourceKey] || null;
}

export function getAllWaterSources() {
  return Object.values(waterSourceTypes);
}
