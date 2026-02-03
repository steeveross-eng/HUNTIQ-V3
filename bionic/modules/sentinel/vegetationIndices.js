/**
 * BIONIC™ Sentinel Module - Vegetation Indices
 * Définitions des indices de végétation Sentinel-2
 */

export const vegetationIndices = {
  ndvi: {
    id: "ndvi",
    name: "NDVI",
    fullName: "Normalized Difference Vegetation Index",
    formula: "(B08 - B04) / (B08 + B04)",
    bands: { nir: "B08", red: "B04" },
    range: [-1, 1],
    interpretation: {
      "-1 to 0": "Eau, sol nu, neige",
      "0 to 0.2": "Sol nu, roches, zones urbaines",
      "0.2 to 0.4": "Végétation clairsemée ou stressée",
      "0.4 to 0.6": "Végétation modérée",
      "0.6 to 0.8": "Végétation dense et saine",
      "0.8 to 1": "Forêt dense, végétation très active"
    },
    huntingRelevance: "Indicateur de browse et couvert végétal"
  },
  evi: {
    id: "evi",
    name: "EVI",
    fullName: "Enhanced Vegetation Index",
    formula: "2.5 * ((B08 - B04) / (B08 + 6*B04 - 7.5*B02 + 1))",
    bands: { nir: "B08", red: "B04", blue: "B02" },
    range: [-1, 1],
    interpretation: {
      "< 0.2": "Végétation très faible",
      "0.2 to 0.4": "Végétation modérée",
      "0.4 to 0.6": "Végétation dense",
      "> 0.6": "Végétation très dense"
    },
    huntingRelevance: "Meilleure précision en forêt dense"
  },
  ndwi: {
    id: "ndwi",
    name: "NDWI",
    fullName: "Normalized Difference Water Index",
    formula: "(B03 - B08) / (B03 + B08)",
    bands: { green: "B03", nir: "B08" },
    range: [-1, 1],
    interpretation: {
      "> 0.3": "Eau libre",
      "0 to 0.3": "Zone humide, végétation saturée",
      "< 0": "Végétation terrestre"
    },
    huntingRelevance: "Détection des zones humides et milieux humides"
  },
  nbr: {
    id: "nbr",
    name: "NBR",
    fullName: "Normalized Burn Ratio",
    formula: "(B08 - B12) / (B08 + B12)",
    bands: { nir: "B08", swir: "B12" },
    range: [-1, 1],
    interpretation: {
      "< -0.1": "Zone brûlée récemment",
      "-0.1 to 0.1": "Sol nu ou régénération",
      "> 0.1": "Végétation saine"
    },
    huntingRelevance: "Détection des coupes forestières et perturbations"
  }
};

export function getIndexDefinition(indexKey) {
  return vegetationIndices[indexKey] || null;
}

export function getAllIndices() {
  return Object.values(vegetationIndices);
}
