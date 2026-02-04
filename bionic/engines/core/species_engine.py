"""
BIONIC™ Engine - Species Engine
================================
Calcul des scores d'habitat pour les espèces fauniques.

Espèces supportées:
- Orignal (Moose)
- Cerf de Virginie (Deer)
- Ours noir (Bear)
- Caribou forestier (Caribou)
- Loup gris (Wolf)
- Dindon sauvage (Turkey)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import random
import logging

from .configs import (
    ModuleType, SpeciesType, SPECIES_CONFIGS
)
from .helpers import (
    get_current_season,
    get_season_factor,
    get_rating,
    generate_hotspots,
    clamp
)

logger = logging.getLogger(__name__)


class SpeciesEngine:
    """
    Moteur de calcul des scores d'habitat par espèce.
    """
    
    def __init__(self):
        self.configs = SPECIES_CONFIGS
    
    def get_available_species(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des espèces disponibles.
        
        Returns:
            List[Dict]: Liste des espèces avec leurs métadonnées
        """
        species_list = []
        for species_type, config in self.configs.items():
            species_list.append({
                "id": species_type.value,
                "name": config["name"],
                "common_name": config["common_name"],
                "version": config["version"],
                "module_weights": config["module_weights"]
            })
        return species_list
    
    def get_species_info(self, species_id: str) -> Optional[Dict[str, Any]]:
        """
        Retourne les informations détaillées d'une espèce.
        
        Args:
            species_id: Identifiant de l'espèce
            
        Returns:
            Dict ou None si espèce non trouvée
        """
        try:
            species_type = SpeciesType(species_id)
            config = self.configs[species_type]
            return {
                "id": species_id,
                **config
            }
        except ValueError:
            return None
    
    async def calculate_score(
        self,
        species: SpeciesType,
        lat: float,
        lon: float,
        module_scores: Dict[ModuleType, float],
        territory_id: str
    ) -> Dict[str, Any]:
        """
        Calcule le score d'habitat pour une espèce.
        
        Args:
            species: Type d'espèce
            lat: Latitude
            lon: Longitude
            module_scores: Scores des modules thématiques
            territory_id: ID du territoire
            
        Returns:
            Dict: Résultat avec score, métriques, hotspots, recommandations
        """
        config = self.configs[species]
        season = get_current_season()
        season_factor = get_season_factor(species, season)
        
        # Calculer le score pondéré depuis les modules
        weighted_sum = 0
        total_weight = 0
        
        for module_type_str, weight in config["module_weights"].items():
            try:
                module_type = ModuleType(module_type_str)
                if module_type in module_scores:
                    weighted_sum += module_scores[module_type] * weight
                    total_weight += weight
            except ValueError:
                continue
        
        base_score = weighted_sum / total_weight if total_weight > 0 else 50
        final_score = clamp(base_score * season_factor, 0, 100)
        
        # Générer les métriques détaillées
        metrics = self._calculate_metrics(module_scores, config)
        
        # Générer les hotspots
        hotspots = generate_hotspots(lat, lon, count=5)
        
        # Générer les recommandations
        recommendations = self._generate_recommendations(
            species, config, metrics, season
        )
        
        return {
            "species": config["name"],
            "common_name": config["common_name"],
            "score": round(final_score, 1),
            "rating": get_rating(final_score),
            "habitat_suitability": metrics["habitat_suitability"],
            "food_availability": metrics["food_availability"],
            "cover_quality": metrics["cover_quality"],
            "water_access": metrics["water_access"],
            "disturbance_level": metrics["disturbance_level"],
            "season_factor": round(season_factor, 2),
            "hotspots": hotspots,
            "recommendations": recommendations[:3]
        }
    
    async def calculate_all_species(
        self,
        lat: float,
        lon: float,
        module_scores: Dict[ModuleType, float],
        territory_id: str,
        species_list: List[SpeciesType]
    ) -> Dict[SpeciesType, Dict[str, Any]]:
        """
        Calcule les scores pour plusieurs espèces.
        
        Args:
            lat: Latitude
            lon: Longitude
            module_scores: Scores des modules
            territory_id: ID du territoire
            species_list: Liste des espèces à calculer
            
        Returns:
            Dict: Résultats par espèce
        """
        results = {}
        
        for species in species_list:
            try:
                result = await self.calculate_score(
                    species, lat, lon, module_scores, territory_id
                )
                results[species] = result
            except Exception as e:
                logger.error(f"Error calculating species {species.value}: {e}")
                results[species] = self._create_error_result(species, str(e))
        
        return results
    
    def _calculate_metrics(
        self,
        module_scores: Dict[ModuleType, float],
        config: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calcule les métriques détaillées pour une espèce.
        """
        # Score de base pour le calcul
        food_score = module_scores.get(ModuleType.FOOD, 50)
        canopy_score = module_scores.get(ModuleType.CANOPY, 50)
        wetness_score = module_scores.get(ModuleType.WETNESS, 50)
        pressure_score = module_scores.get(ModuleType.PRESSURE, 50)
        
        # Calcul des métriques avec variation
        return {
            "habitat_suitability": clamp(
                sum(module_scores.values()) / len(module_scores) * random.uniform(0.9, 1.1)
                if module_scores else 50, 0, 100
            ),
            "food_availability": clamp(
                food_score * random.uniform(0.9, 1.1), 0, 100
            ),
            "cover_quality": clamp(
                canopy_score * random.uniform(0.9, 1.1), 0, 100
            ),
            "water_access": clamp(
                wetness_score * random.uniform(0.9, 1.1), 0, 100
            ),
            "disturbance_level": clamp(
                100 - pressure_score, 0, 100
            )
        }
    
    def _generate_recommendations(
        self,
        species: SpeciesType,
        config: Dict[str, Any],
        metrics: Dict[str, float],
        season: Any
    ) -> List[str]:
        """
        Génère des recommandations de chasse pour une espèce.
        """
        recommendations = []
        common_name = config["common_name"]
        
        # Recommandations basées sur les métriques
        if metrics["food_availability"] < 50:
            recommendations.append(
                f"Rechercher des zones de nourriture: score actuel {metrics['food_availability']:.0f}/100"
            )
        
        if metrics["cover_quality"] < 50:
            recommendations.append(
                f"Améliorer le couvert forestier: score actuel {metrics['cover_quality']:.0f}/100"
            )
        
        if metrics["disturbance_level"] > 60:
            recommendations.append(
                "Éviter les zones à forte pression humaine"
            )
        
        # Recommandation par défaut si habitat optimal
        if not recommendations:
            recommendations.append(f"Habitat optimal pour {common_name}")
        
        # Recommandations saisonnières
        season_tips = {
            "spring": f"Au printemps, {common_name.lower()} cherche les nouvelles pousses",
            "summer": f"En été, {common_name.lower()} reste près des points d'eau",
            "fall": f"À l'automne, {common_name.lower()} est actif pendant le rut",
            "winter": f"En hiver, {common_name.lower()} se regroupe dans les ravages"
        }
        
        if hasattr(season, 'value'):
            season_value = season.value
        else:
            season_value = str(season)
        
        if season_value in season_tips:
            recommendations.append(season_tips[season_value])
        
        return recommendations
    
    def _create_error_result(
        self,
        species: SpeciesType,
        error_message: str
    ) -> Dict[str, Any]:
        """
        Crée un résultat d'erreur pour une espèce.
        """
        config = self.configs[species]
        return {
            "species": config["name"],
            "common_name": config["common_name"],
            "score": 0,
            "rating": "Erreur",
            "habitat_suitability": 0,
            "food_availability": 0,
            "cover_quality": 0,
            "water_access": 0,
            "disturbance_level": 0,
            "season_factor": 0,
            "hotspots": [],
            "recommendations": [f"Erreur: {error_message}"],
            "error": True,
            "error_message": error_message
        }


# Instance singleton
species_engine = SpeciesEngine()
