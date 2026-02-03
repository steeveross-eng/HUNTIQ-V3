/**
 * BIONIC™ Nutrition Module - Species Profiles
 * Profils nutritionnels des espèces de gibier au Québec
 */

export const speciesProfiles = {
  cerf: {
    id: "cerf",
    label: "Cerf de Virginie",
    energy: 100,
    protein: 18,
    calcium: 0.6,
    phosphorus: 0.3,
    notes: "Besoins variables selon la saison, la condition corporelle et la reproduction."
  },
  orignal: {
    id: "orignal",
    label: "Orignal",
    energy: 160,
    protein: 20,
    calcium: 0.8,
    phosphorus: 0.4,
    notes: "Fortement dépendant des feuillus, régénération et zones humides."
  },
  ours_noir: {
    id: "ours_noir",
    label: "Ours noir",
    energy: 180,
    protein: 16,
    calcium: 0.5,
    phosphorus: 0.3,
    notes: "Régime opportuniste, dépendance aux petits fruits et sources énergétiques."
  }
};

export function getSpeciesProfile(speciesKey) {
  return speciesProfiles[speciesKey] || null;
}
