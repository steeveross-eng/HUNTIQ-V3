/**
 * BIONIC™ Hydrology Module - Math Utilities
 */

export function calculateDistance(point1, point2) {
  // Haversine formula for distance calculation
  const R = 6371000; // Earth's radius in meters
  const lat1 = point1.lat * Math.PI / 180;
  const lat2 = point2.lat * Math.PI / 180;
  const deltaLat = (point2.lat - point1.lat) * Math.PI / 180;
  const deltaLon = (point2.lon - point1.lon) * Math.PI / 180;

  const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
            Math.cos(lat1) * Math.cos(lat2) *
            Math.sin(deltaLon/2) * Math.sin(deltaLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

  return R * c; // Distance in meters
}

export function calculateWaterProximityScore(distances, maxDistance = 500) {
  if (!distances || distances.length === 0) return 0;
  
  const minDistance = Math.min(...distances);
  if (minDistance >= maxDistance) return 0;
  
  // Linear score: 100 at 0m, 0 at maxDistance
  return Math.round((1 - minDistance / maxDistance) * 100);
}

export function safeAverage(values = []) {
  const valid = values.filter(v => typeof v === "number" && !isNaN(v));
  if (valid.length === 0) return null;
  return valid.reduce((acc, v) => acc + v, 0) / valid.length;
}

export function round(value, decimals = 2) {
  if (typeof value !== "number" || isNaN(value)) return null;
  return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
}
