/**
 * BIONIC™ SIGÉOM Module - Math Utilities
 */

export function calculateAreaWeightedAverage(zones = [], valueKey) {
  let totalArea = 0;
  let weightedSum = 0;

  zones.forEach(zone => {
    const area = zone.area || 1;
    const value = zone[valueKey];
    if (typeof value === "number") {
      totalArea += area;
      weightedSum += value * area;
    }
  });

  return totalArea > 0 ? weightedSum / totalArea : null;
}

export function round(value, decimals = 2) {
  if (typeof value !== "number" || isNaN(value)) return null;
  return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

export function categorizePermeability(level) {
  const scores = {
    very_high: 90,
    high: 70,
    medium: 50,
    low: 30,
    very_low: 10
  };
  return scores[level] || 50;
}

export function categorizeMineralContent(level) {
  const scores = {
    high: 80,
    medium: 50,
    low: 20
  };
  return scores[level] || 50;
}
