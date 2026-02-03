/**
 * BIONIC™ Nutrition Module - Math Utilities
 * Fonctions mathématiques utilitaires
 */

export function safeAverage(values = []) {
  const valid = values.filter(v => typeof v === "number" && !isNaN(v));
  if (valid.length === 0) return null;
  const sum = valid.reduce((acc, v) => acc + v, 0);
  return sum / valid.length;
}

export function round(value, decimals = 2) {
  if (typeof value !== "number" || isNaN(value)) return null;
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
}
