/**
 * BIONIC™ SIGÉOM Module - Geological Profiles
 * Profils géologiques pour l'analyse du terrain
 */

export const geologicalTypes = {
  // Roches sédimentaires
  calcaire: {
    id: "calcaire",
    category: "sedimentaire",
    label: "Calcaire",
    permeability: "high",
    mineral_content: "high",
    wildlife_value: "high",
    notes: "Riche en minéraux, favorise les licks naturels"
  },
  gres: {
    id: "gres",
    category: "sedimentaire",
    label: "Grès",
    permeability: "medium",
    mineral_content: "medium",
    wildlife_value: "medium",
    notes: "Bon drainage, sols généralement fertiles"
  },
  schiste: {
    id: "schiste",
    category: "sedimentaire",
    label: "Schiste",
    permeability: "low",
    mineral_content: "low",
    wildlife_value: "low",
    notes: "Sols acides, végétation plus pauvre"
  },
  
  // Roches ignées
  granite: {
    id: "granite",
    category: "ignee",
    label: "Granite",
    permeability: "low",
    mineral_content: "low",
    wildlife_value: "medium",
    notes: "Terrain accidenté, bon couvert"
  },
  basalte: {
    id: "basalte",
    category: "ignee",
    label: "Basalte",
    permeability: "low",
    mineral_content: "medium",
    wildlife_value: "medium",
    notes: "Sols fertiles en décomposition"
  },
  
  // Roches métamorphiques
  gneiss: {
    id: "gneiss",
    category: "metamorphique",
    label: "Gneiss",
    permeability: "low",
    mineral_content: "low",
    wildlife_value: "medium",
    notes: "Terrain varié, microhabitats"
  },
  marbre: {
    id: "marbre",
    category: "metamorphique",
    label: "Marbre",
    permeability: "high",
    mineral_content: "high",
    wildlife_value: "high",
    notes: "Source de calcium naturelle"
  },
  
  // Dépôts de surface
  till: {
    id: "till",
    category: "quaternaire",
    label: "Till glaciaire",
    permeability: "medium",
    mineral_content: "medium",
    wildlife_value: "medium",
    notes: "Dépôts variés, sols mixtes"
  },
  argile: {
    id: "argile",
    category: "quaternaire",
    label: "Argile",
    permeability: "very_low",
    mineral_content: "high",
    wildlife_value: "high",
    notes: "Retient l'eau, licks de minéraux"
  },
  sable: {
    id: "sable",
    category: "quaternaire",
    label: "Sable",
    permeability: "very_high",
    mineral_content: "low",
    wildlife_value: "low",
    notes: "Drainage excessif, végétation limitée"
  },
  tourbe: {
    id: "tourbe",
    category: "quaternaire",
    label: "Tourbe",
    permeability: "low",
    mineral_content: "low",
    wildlife_value: "medium",
    notes: "Zones humides, habitat orignal"
  }
};

export function getGeologicalProfile(geoKey) {
  return geologicalTypes[geoKey] || null;
}

export function getAllGeologicalTypes() {
  return Object.values(geologicalTypes);
}

export function getTypesByCategory(category) {
  return Object.values(geologicalTypes).filter(t => t.category === category);
}
