/**
 * BIONIC™ Hydrology Module - Water Classifier
 * Classification des zones hydrographiques
 */

import { getWaterSourceProfile } from "./waterSources.js";

const HYDRO_VALUE_BY_TYPE = {
  riviere: { flow_rate: "permanent", wildlife_corridor: true, fish_presence: true },
  ruisseau: { flow_rate: "seasonal", wildlife_corridor: true, fish_presence: false },
  lac: { flow_rate: "static", wildlife_corridor: false, fish_presence: true },
  etang: { flow_rate: "static", wildlife_corridor: false, fish_presence: false },
  marecage: { flow_rate: "slow", wildlife_corridor: false, fish_presence: false },
  tourbiere: { flow_rate: "slow", wildlife_corridor: false, fish_presence: false },
  source: { flow_rate: "permanent", wildlife_corridor: false, fish_presence: false }
};

export function classifyWaterFeatures(hydroData = []) {
  return hydroData.map(feature => {
    const profile = getWaterSourceProfile(feature.type);
    const hydroValue = HYDRO_VALUE_BY_TYPE[feature.type] || null;

    if (!profile) {
      return {
        ...feature,
        classification: null,
        classificationFlag: "unknown_water_type"
      };
    }

    return {
      ...feature,
      classification: {
        ...profile,
        ...hydroValue,
        area: feature.area || null,
        length: feature.length || null
      },
      classificationFlag: "ok"
    };
  });
}

export function calculateWaterCoverage(classifiedFeatures = [], totalArea) {
  const waterArea = classifiedFeatures
    .filter(f => f.classification && f.classification.area)
    .reduce((sum, f) => sum + f.classification.area, 0);

  return {
    water_area_m2: waterArea,
    total_area_m2: totalArea,
    water_percentage: totalArea > 0 ? (waterArea / totalArea) * 100 : 0
  };
}
