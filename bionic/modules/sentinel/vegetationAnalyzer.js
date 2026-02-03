/**
 * BIONIC™ Sentinel Module - Vegetation Analyzer
 * Analyse de la végétation à partir des indices spectraux
 */

import { classifyNDVI, round } from "./utils/math.js";

const VEGETATION_HUNTING_VALUE = {
  very_dense: { browse_quality: "low", cover_quality: "excellent", thermal: "excellent" },
  dense: { browse_quality: "medium", cover_quality: "high", thermal: "high" },
  moderate: { browse_quality: "high", cover_quality: "medium", thermal: "medium" },
  sparse: { browse_quality: "high", cover_quality: "low", thermal: "low" },
  bare: { browse_quality: "none", cover_quality: "none", thermal: "none" },
  non_vegetation: { browse_quality: "none", cover_quality: "none", thermal: "none" }
};

export function analyzeVegetation(ndviData = []) {
  return ndviData.map(zone => {
    const classification = classifyNDVI(zone.ndvi);
    const huntingValue = VEGETATION_HUNTING_VALUE[classification.class];

    return {
      ...zone,
      vegetation: {
        ndvi: round(zone.ndvi),
        class: classification.class,
        label: classification.label,
        ...huntingValue
      },
      analysisFlag: "ok"
    };
  });
}

export function calculateVegetationStats(analyzedZones = []) {
  const stats = {
    very_dense: 0,
    dense: 0,
    moderate: 0,
    sparse: 0,
    bare: 0,
    non_vegetation: 0
  };

  analyzedZones.forEach(zone => {
    const vegClass = zone.vegetation?.class;
    if (vegClass && stats[vegClass] !== undefined) {
      stats[vegClass]++;
    }
  });

  const total = analyzedZones.length;
  const percentages = {};
  Object.keys(stats).forEach(key => {
    percentages[key] = total > 0 ? round((stats[key] / total) * 100, 1) : 0;
  });

  return {
    counts: stats,
    percentages,
    total_zones: total,
    dominant_class: Object.entries(stats).sort((a, b) => b[1] - a[1])[0]?.[0] || null
  };
}

export function identifyBrowseZones(analyzedZones = []) {
  // Identify zones optimal for wildlife browse
  return analyzedZones
    .filter(z => z.vegetation?.browse_quality === "high")
    .map(z => ({
      zone_id: z.id,
      ndvi: z.vegetation.ndvi,
      class: z.vegetation.class,
      hunting_note: "Zone de broutage optimal - Végétation accessible"
    }));
}

export function identifyCoverZones(analyzedZones = []) {
  // Identify zones with good thermal/hiding cover
  return analyzedZones
    .filter(z => z.vegetation?.cover_quality === "excellent" || z.vegetation?.cover_quality === "high")
    .map(z => ({
      zone_id: z.id,
      ndvi: z.vegetation.ndvi,
      class: z.vegetation.class,
      hunting_note: "Zone de couvert - Abri thermique pour le gibier"
    }));
}
