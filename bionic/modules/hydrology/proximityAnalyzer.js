/**
 * BIONIC™ Hydrology Module - Proximity Analyzer
 * Analyse de la proximité aux sources d'eau
 */

import { calculateDistance, calculateWaterProximityScore, round } from "./utils/math.js";

export function analyzeWaterProximity(targetPoint, waterFeatures = []) {
  const distances = [];

  waterFeatures.forEach(feature => {
    if (!feature.coordinates) return;

    // Handle different geometry types
    if (feature.coordinates.lat && feature.coordinates.lon) {
      // Point geometry
      const dist = calculateDistance(targetPoint, feature.coordinates);
      distances.push({
        feature_id: feature.id,
        feature_type: feature.type,
        distance_m: round(dist),
        importance: feature.classification?.importance_score || 50
      });
    } else if (Array.isArray(feature.coordinates)) {
      // Line/Polygon - find nearest point
      let minDist = Infinity;
      feature.coordinates.forEach(coord => {
        const dist = calculateDistance(targetPoint, coord);
        if (dist < minDist) minDist = dist;
      });
      distances.push({
        feature_id: feature.id,
        feature_type: feature.type,
        distance_m: round(minDist),
        importance: feature.classification?.importance_score || 50
      });
    }
  });

  // Sort by distance
  distances.sort((a, b) => a.distance_m - b.distance_m);

  // Calculate scores
  const nearestWater = distances[0] || null;
  const proximityScore = calculateWaterProximityScore(
    distances.map(d => d.distance_m)
  );

  // Count features within ranges
  const within100m = distances.filter(d => d.distance_m <= 100).length;
  const within500m = distances.filter(d => d.distance_m <= 500).length;
  const within1000m = distances.filter(d => d.distance_m <= 1000).length;

  return {
    target_point: targetPoint,
    nearest_water: nearestWater,
    proximity_score: proximityScore,
    water_access: {
      within_100m: within100m,
      within_500m: within500m,
      within_1000m: within1000m
    },
    all_distances: distances.slice(0, 10) // Top 10 nearest
  };
}

export function identifyWaterCorridors(waterFeatures = []) {
  // Identify connected water features that form wildlife corridors
  const corridors = [];
  const rivers = waterFeatures.filter(f => 
    f.type === "riviere" || f.type === "ruisseau"
  );

  rivers.forEach(river => {
    corridors.push({
      type: "water_corridor",
      name: river.name || `Corridor ${river.id}`,
      feature_id: river.id,
      wildlife_value: river.classification?.wildlife_value || "high",
      notes: "Corridor naturel de déplacement pour la faune"
    });
  });

  return corridors;
}
