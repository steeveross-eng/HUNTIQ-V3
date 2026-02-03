/**
 * BIONIC™ Nutrition Module - Recommendation Engine
 * Génération de recommandations basées sur les carences détectées
 */

export function generateRecommendations(deficiencyReport, speciesProfile) {
  if (!deficiencyReport || deficiencyReport.status === "no_data") {
    return [
      "Impossible de générer des recommandations : données nutritionnelles insuffisantes."
    ];
  }

  const recs = [];
  const d = deficiencyReport.details || {};

  if (d.energy?.status === "carence") {
    recs.push("Énergie : Ajouter des sources énergétiques (grains, blocs énergétiques, coupes favorisant les rejets).");
  }

  if (d.protein?.status === "carence") {
    recs.push("Protéines : Favoriser les légumineuses, herbacées, ou installer des suppléments protéinés.");
  }

  if (d.calcium?.status === "carence") {
    recs.push("Calcium : Installer des blocs minéraux riches en calcium.");
  }

  if (d.phosphorus?.status === "carence") {
    recs.push("Phosphore : Utiliser des minéraux complets avec ratio Ca/P équilibré.");
  }

  if (recs.length === 0) {
    recs.push(
      `Aucune carence majeure détectée pour ${speciesProfile?.label}. Optimiser la tranquillité et la répartition spatiale.`
    );
  }

  return recs;
}
