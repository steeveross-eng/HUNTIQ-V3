/**
 * BIONIC™ SIGÉOM Module - Geological Classifier
 * Classification des zones géologiques
 */

import { getGeologicalProfile } from "./geologicalProfiles.js";
import { categorizePermeability, categorizeMineralContent } from "./utils/math.js";

export function classifyGeology(geoData = []) {
  return geoData.map(zone => {
    const profile = getGeologicalProfile(zone.type);

    if (!profile) {
      return {
        ...zone,
        classification: null,
        classificationFlag: "unknown_geology_type"
      };
    }

    return {
      ...zone,
      classification: {
        ...profile,
        permeability_score: categorizePermeability(profile.permeability),
        mineral_score: categorizeMineralContent(profile.mineral_content),
        area: zone.area || null
      },
      classificationFlag: "ok"
    };
  });
}

export function calculateGeologicalCoverage(classifiedZones = []) {
  const coverage = {
    sedimentaire: 0,
    ignee: 0,
    metamorphique: 0,
    quaternaire: 0
  };

  let totalArea = 0;

  classifiedZones.forEach(zone => {
    if (!zone.classification) return;
    const area = zone.classification.area || 1;
    const category = zone.classification.category;
    
    if (coverage[category] !== undefined) {
      coverage[category] += area;
    }
    totalArea += area;
  });

  // Convert to percentages
  const percentages = {};
  Object.keys(coverage).forEach(key => {
    percentages[key] = totalArea > 0 ? (coverage[key] / totalArea) * 100 : 0;
  });

  return {
    areas: coverage,
    percentages,
    total_area: totalArea,
    dominant_category: Object.entries(percentages)
      .sort((a, b) => b[1] - a[1])[0]?.[0] || null
  };
}
