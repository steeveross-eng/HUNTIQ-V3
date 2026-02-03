/**
 * BIONIC™ Nutrition Module - Resource Classifier
 * Classification des ressources nutritionnelles par type de couverture terrestre
 */

const NUTRITION_PROFILES_BY_LANDCOVER = {
  feuillus: { energy: 80, protein: 12, calcium: 0.4, phosphorus: 0.25 },
  coniferes: { energy: 60, protein: 8, calcium: 0.2, phosphorus: 0.18 },
  plantes_herbacees: { energy: 110, protein: 20, calcium: 0.5, phosphorus: 0.3 },
  milieu_humide: { energy: 90, protein: 16, calcium: 0.45, phosphorus: 0.28 }
};

export function classifyResources(landcoverData = []) {
  return landcoverData.map(zone => {
    const profile = NUTRITION_PROFILES_BY_LANDCOVER[zone.type] || null;

    if (!profile) {
      return {
        ...zone,
        nutrition: null,
        nutritionFlag: "unknown_landcover_type"
      };
    }

    return {
      ...zone,
      nutrition: {
        ...profile,
        area: zone.area || null
      },
      nutritionFlag: "ok"
    };
  });
}
