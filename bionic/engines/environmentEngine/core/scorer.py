"""
BIONIC™ Environment Engine - Global Scorer

Calcule le score global de potentiel de chasse basé sur
les données combinées de tous les moteurs.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import math


class EnvironmentScorer:
    """
    Calcule les scores de potentiel de chasse.
    """
    
    def __init__(self):
        # Seuils de classification du score global
        self.score_thresholds = {
            "exceptional": 85,   # Zone exceptionnelle
            "excellent": 75,     # Excellent potentiel
            "good": 60,          # Bon potentiel
            "moderate": 45,      # Potentiel modéré
            "low": 30,           # Faible potentiel
            "poor": 0            # Potentiel très faible
        }
        
        # Descriptions des niveaux
        self.score_descriptions = {
            "exceptional": {
                "label": "Exceptionnel",
                "color": "#10b981",  # Emerald
                "description": "Zone à très haut potentiel de chasse. Conditions optimales.",
                "recommendation": "Priorisez cette zone. Planifiez une session prolongée."
            },
            "excellent": {
                "label": "Excellent",
                "color": "#22c55e",  # Green
                "description": "Excellent potentiel. Plusieurs facteurs favorables.",
                "recommendation": "Zone recommandée pour la chasse active."
            },
            "good": {
                "label": "Bon",
                "color": "#84cc16",  # Lime
                "description": "Bon potentiel de chasse. Conditions favorables.",
                "recommendation": "Zone viable, surveillez les conditions météo."
            },
            "moderate": {
                "label": "Modéré",
                "color": "#eab308",  # Yellow
                "description": "Potentiel modéré. Certains facteurs limitants.",
                "recommendation": "Considérez d'autres zones ou attendez de meilleures conditions."
            },
            "low": {
                "label": "Faible",
                "color": "#f97316",  # Orange
                "description": "Faible potentiel. Plusieurs facteurs défavorables.",
                "recommendation": "Non recommandé sauf pour le repérage."
            },
            "poor": {
                "label": "Très faible",
                "color": "#ef4444",  # Red
                "description": "Potentiel très faible. Conditions défavorables.",
                "recommendation": "Évitez cette zone pour la chasse."
            }
        }
        
        # Facteurs de bonus/malus saisonniers
        self.seasonal_modifiers = {
            "spring": {
                "deer": 0.85,   # Faons, moins actifs
                "moose": 0.90,
                "bear": 0.95,   # Sortie d'hibernation
                "elk": 0.85,
                "waterfowl": 1.10  # Migration
            },
            "summer": {
                "deer": 0.80,   # Chaleur, moins actifs
                "moose": 0.75,
                "bear": 1.00,
                "elk": 0.80,
                "waterfowl": 0.70
            },
            "fall": {
                "deer": 1.15,   # Rut
                "moose": 1.20,  # Rut
                "bear": 1.10,   # Hyperphagie
                "elk": 1.15,    # Rut
                "waterfowl": 1.15  # Migration
            },
            "winter": {
                "deer": 0.95,
                "moose": 1.00,
                "bear": 0.20,   # Hibernation
                "elk": 0.95,
                "waterfowl": 0.50
            }
        }
    
    def calculate_global_score(
        self,
        combined_data: Dict[str, Any],
        apply_seasonal: bool = True,
        current_season: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calcule le score global de potentiel de chasse.
        
        Args:
            combined_data: Données combinées du combiner
            apply_seasonal: Appliquer les modificateurs saisonniers
            current_season: Saison actuelle (auto-détectée si None)
            
        Returns:
            Dict avec le score global et les détails
        """
        weights = combined_data.get("metadata", {}).get("weights_used", {})
        scores = combined_data.get("scores", {})
        target_species = combined_data.get("metadata", {}).get("target_species", "deer")
        
        # Calculer le score pondéré
        weighted_score = 0
        weight_sum = 0
        component_contributions = {}
        
        for component, weight in weights.items():
            if component in scores:
                score = scores[component]
                contribution = score * weight
                weighted_score += contribution
                weight_sum += weight
                component_contributions[component] = {
                    "raw_score": score,
                    "weight": weight,
                    "contribution": contribution,
                    "percentage": round(contribution / 100 * 100 / weight * weight, 1)
                }
        
        # Normaliser si tous les poids ne sont pas présents
        if weight_sum > 0 and weight_sum < 1:
            weighted_score = weighted_score / weight_sum
        
        # Appliquer modificateur saisonnier
        seasonal_modifier = 1.0
        if apply_seasonal:
            if current_season is None:
                current_season = self._get_current_season()
            
            if current_season in self.seasonal_modifiers:
                seasonal_modifier = self.seasonal_modifiers[current_season].get(
                    target_species, 1.0
                )
        
        final_score = min(100, max(0, weighted_score * seasonal_modifier))
        
        # Classifier le score
        classification = self._classify_score(final_score)
        
        # Générer les recommandations
        recommendations = self._generate_recommendations(
            final_score=final_score,
            component_contributions=component_contributions,
            target_species=target_species,
            season=current_season
        )
        
        return {
            "global_score": round(final_score, 1),
            "raw_weighted_score": round(weighted_score, 1),
            "seasonal_modifier": seasonal_modifier,
            "season": current_season,
            "classification": classification,
            "component_contributions": component_contributions,
            "recommendations": recommendations,
            "target_species": target_species,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _classify_score(self, score: float) -> Dict[str, Any]:
        """Classifie un score dans une catégorie."""
        for category, threshold in sorted(
            self.score_thresholds.items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            if score >= threshold:
                return {
                    "category": category,
                    **self.score_descriptions[category]
                }
        
        return {
            "category": "poor",
            **self.score_descriptions["poor"]
        }
    
    def _get_current_season(self) -> str:
        """Détermine la saison actuelle au Québec."""
        month = datetime.now().month
        
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"
    
    def _generate_recommendations(
        self,
        final_score: float,
        component_contributions: Dict,
        target_species: str,
        season: str
    ) -> List[Dict[str, str]]:
        """Génère des recommandations basées sur l'analyse."""
        recommendations = []
        
        # Recommandations basées sur le score global
        if final_score >= 75:
            recommendations.append({
                "type": "positive",
                "priority": "high",
                "message": f"Zone idéale pour la chasse au {self._species_name(target_species)}. Conditions optimales détectées."
            })
        elif final_score >= 60:
            recommendations.append({
                "type": "positive",
                "priority": "medium",
                "message": f"Bonnes conditions pour la chasse. Le territoire offre un potentiel intéressant."
            })
        elif final_score < 45:
            recommendations.append({
                "type": "warning",
                "priority": "high",
                "message": "Conditions sous-optimales. Considérez d'explorer d'autres zones."
            })
        
        # Recommandations par composant faible
        for component, data in component_contributions.items():
            if data["raw_score"] < 40:
                rec = self._get_component_recommendation(component, data["raw_score"], target_species)
                if rec:
                    recommendations.append(rec)
        
        # Recommandations par composant fort
        best_component = max(
            component_contributions.items(),
            key=lambda x: x[1]["raw_score"],
            default=(None, {"raw_score": 0})
        )
        if best_component[0] and best_component[1]["raw_score"] > 75:
            recommendations.append({
                "type": "info",
                "priority": "medium",
                "message": f"Point fort: {self._component_name(best_component[0])} (score: {best_component[1]['raw_score']:.0f})"
            })
        
        # Recommandations saisonnières
        seasonal_rec = self._get_seasonal_recommendation(target_species, season)
        if seasonal_rec:
            recommendations.append(seasonal_rec)
        
        return recommendations
    
    def _get_component_recommendation(
        self, 
        component: str, 
        score: float,
        species: str
    ) -> Optional[Dict]:
        """Génère une recommandation pour un composant spécifique."""
        messages = {
            "hydrology": {
                "low": f"Faible présence d'eau. Les {self._species_name(species)}s peuvent être moins présents.",
                "action": "Recherchez des zones avec plus de cours d'eau ou points d'eau."
            },
            "vegetation": {
                "low": "Végétation clairsemée ou inadaptée.",
                "action": "Privilégiez les zones forestières plus denses."
            },
            "geology": {
                "low": "Terrain peu favorable (rocheux ou marécageux).",
                "action": "Le terrain peut limiter les déplacements du gibier."
            },
            "weather": {
                "low": "Conditions météo défavorables.",
                "action": "Attendez une amélioration des conditions."
            },
            "nutrition": {
                "low": "Faible disponibilité de sources de nourriture.",
                "action": "Identifiez les zones de gagnage à proximité."
            }
        }
        
        if component in messages:
            return {
                "type": "warning",
                "priority": "medium",
                "message": f"{messages[component]['low']} {messages[component]['action']}"
            }
        return None
    
    def _get_seasonal_recommendation(self, species: str, season: str) -> Optional[Dict]:
        """Génère une recommandation saisonnière."""
        recommendations = {
            ("deer", "fall"): {
                "type": "info",
                "priority": "high",
                "message": "Période de rut du cerf. Utilisez des attractants à base de phéromones."
            },
            ("moose", "fall"): {
                "type": "info",
                "priority": "high",
                "message": "Période de rut de l'orignal. Les appels (calls) sont très efficaces."
            },
            ("bear", "fall"): {
                "type": "info",
                "priority": "medium",
                "message": "Période d'hyperphagie de l'ours. Cherchez près des sources de nourriture."
            },
            ("bear", "winter"): {
                "type": "warning",
                "priority": "high",
                "message": "L'ours est en hibernation. Chasse non recommandée."
            }
        }
        
        return recommendations.get((species, season))
    
    def _species_name(self, species: str) -> str:
        """Retourne le nom français de l'espèce."""
        names = {
            "deer": "cerf",
            "moose": "orignal",
            "bear": "ours",
            "elk": "wapiti",
            "waterfowl": "sauvagine"
        }
        return names.get(species, species)
    
    def _component_name(self, component: str) -> str:
        """Retourne le nom français du composant."""
        names = {
            "hydrology": "Hydrologie",
            "vegetation": "Végétation",
            "geology": "Géologie",
            "weather": "Météo",
            "nutrition": "Nutrition"
        }
        return names.get(component, component)
    
    def compare_zones(
        self, 
        zone_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare plusieurs zones et classe-les par potentiel.
        
        Args:
            zone_results: Liste de résultats d'analyse par zone
            
        Returns:
            Classement des zones avec comparaison
        """
        if not zone_results:
            return {"zones": [], "best_zone": None}
        
        # Trier par score décroissant
        sorted_zones = sorted(
            zone_results,
            key=lambda x: x.get("global_score", 0),
            reverse=True
        )
        
        best = sorted_zones[0]
        
        return {
            "zones": [
                {
                    "rank": i + 1,
                    "score": z.get("global_score", 0),
                    "classification": z.get("classification", {}).get("label", "Unknown"),
                    "data": z
                }
                for i, z in enumerate(sorted_zones)
            ],
            "best_zone": {
                "score": best.get("global_score", 0),
                "classification": best.get("classification", {}),
                "recommendations": best.get("recommendations", [])
            },
            "score_spread": sorted_zones[0].get("global_score", 0) - sorted_zones[-1].get("global_score", 0) if len(sorted_zones) > 1 else 0
        }


# Instance singleton
environment_scorer = EnvironmentScorer()
