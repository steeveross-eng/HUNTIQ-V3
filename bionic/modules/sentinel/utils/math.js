/**
 * BIONIC™ Sentinel Module - Math Utilities
 */

export function calculateNDVI(nir, red) {
  if (nir + red === 0) return 0;
  return (nir - red) / (nir + red);
}

export function calculateEVI(nir, red, blue) {
  const denominator = nir + 6 * red - 7.5 * blue + 1;
  if (denominator === 0) return 0;
  return 2.5 * ((nir - red) / denominator);
}

export function calculateNDWI(green, nir) {
  if (green + nir === 0) return 0;
  return (green - nir) / (green + nir);
}

export function classifyNDVI(ndviValue) {
  if (ndviValue < 0) return { class: "non_vegetation", label: "Non-végétation" };
  if (ndviValue < 0.2) return { class: "bare", label: "Sol nu" };
  if (ndviValue < 0.4) return { class: "sparse", label: "Végétation clairsemée" };
  if (ndviValue < 0.6) return { class: "moderate", label: "Végétation modérée" };
  if (ndviValue < 0.8) return { class: "dense", label: "Végétation dense" };
  return { class: "very_dense", label: "Végétation très dense" };
}

export function round(value, decimals = 3) {
  if (typeof value !== "number" || isNaN(value)) return null;
  return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
}
