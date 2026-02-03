"""
BIONIC™ Hydrology Engine - Analyzer

Analyse des données hydrologiques pour le calcul de scores de chasse.
"""

import math
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class HydroAnalyzer:
    """
    Analyseur hydrologique pour les territoires de chasse.
    
    Calcule des scores basés sur:
    - Proximité aux sources d'eau
    - Densité du réseau hydrographique
    - Qualité des habitats humides
    - Connectivité des cours d'eau
    """
    
    # Distance thresholds (meters)
    WATER_PROXIMITY_THRESHOLDS = {
        "optimal": 500,      # < 500m = excellent
        "good": 1000,        # 500-1000m = bon
        "moderate": 2000,    # 1000-2000m = modéré
        "far": 5000          # > 2000m = faible
    }
    
    # Species-specific water preferences
    SPECIES_WATER_NEEDS = {
        "deer": {
            "preferred_distance_m": 800,
            "weight": 0.15,
            "note": "Cervidés visitent l'eau 1-2 fois par jour"
        },
        "moose": {
            "preferred_distance_m": 300,
            "weight": 0.25,
            "note": "Orignaux fortement liés aux milieux aquatiques"
        },
        "bear": {
            "preferred_distance_m": 1000,
            "weight": 0.10,
            "note": "Ours utilisent l'eau pour la thermorégulation"
        },
        "waterfowl": {
            "preferred_distance_m": 100,
            "weight": 0.40,
            "note": "Sauvagine dépend entièrement des plans d'eau"
        }
    }
    
    # Wetland habitat quality scores
    WETLAND_QUALITY = {
        "marais": 0.9,        # Marshes - excellent habitat
        "marecage": 0.8,      # Swamps - very good
        "tourbiere": 0.6,     # Peatlands - moderate
        "eau_peu_profonde": 0.85  # Shallow water - excellent for waterfowl
    }
    
    def __init__(self):
        self.thresholds = self.WATER_PROXIMITY_THRESHOLDS
        self.species_needs = self.SPECIES_WATER_NEEDS
    
    def calculate_proximity_score(
        self,
        distance_m: float,
        species: str = "deer"
    ) -> Dict[str, Any]:
        """
        Calculate water proximity score for a given distance.
        
        Args:
            distance_m: Distance to nearest water in meters
            species: Target species
            
        Returns:
            Score and interpretation
        """
        species_config = self.species_needs.get(species, self.species_needs["deer"])
        preferred = species_config["preferred_distance_m"]
        
        # Score calculation (exponential decay)
        if distance_m <= preferred:
            # Within optimal range
            base_score = 100 - (distance_m / preferred) * 20
        else:
            # Beyond optimal - exponential decay
            factor = (distance_m - preferred) / preferred
            base_score = 80 * math.exp(-factor * 0.5)
        
        # Clamp score
        score = max(0, min(100, base_score))
        
        # Determine level
        if distance_m < self.thresholds["optimal"]:
            level = "excellent"
        elif distance_m < self.thresholds["good"]:
            level = "bon"
        elif distance_m < self.thresholds["moderate"]:
            level = "modéré"
        else:
            level = "faible"
        
        return {
            "score": round(score, 1),
            "level": level,
            "distance_m": distance_m,
            "species": species,
            "preferred_distance_m": preferred,
            "weight": species_config["weight"],
            "interpretation": self._get_interpretation(level, species)
        }
    
    def calculate_network_density_score(
        self,
        total_length_km: float,
        area_km2: float
    ) -> Dict[str, Any]:
        """
        Calculate hydrographic network density score.
        
        Higher density = more water access points = better for wildlife.
        
        Args:
            total_length_km: Total length of waterways in km
            area_km2: Area of the region in km²
        """
        if area_km2 <= 0:
            return {"score": 0, "error": "Invalid area"}
        
        density = total_length_km / area_km2  # km/km²
        
        # Quebec average is ~0.5-1.0 km/km²
        # Score based on density relative to optimal range
        if density >= 1.5:
            score = 100
            level = "excellent"
        elif density >= 1.0:
            score = 80 + (density - 1.0) * 40
            level = "très_bon"
        elif density >= 0.5:
            score = 50 + (density - 0.5) * 60
            level = "bon"
        elif density >= 0.2:
            score = 20 + (density - 0.2) * 100
            level = "modéré"
        else:
            score = density * 100
            level = "faible"
        
        return {
            "score": round(min(100, score), 1),
            "level": level,
            "density_km_per_km2": round(density, 3),
            "total_length_km": round(total_length_km, 2),
            "area_km2": round(area_km2, 2),
            "benchmark": {
                "quebec_average": 0.7,
                "optimal_hunting": 1.0
            }
        }
    
    def calculate_wetland_score(
        self,
        wetland_data: Dict[str, Any],
        area_km2: float
    ) -> Dict[str, Any]:
        """
        Calculate wetland habitat quality score.
        
        Args:
            wetland_data: Extracted wetland data with types
            area_km2: Total area in km²
        """
        # Calculate wetland coverage percentage
        wetland_area = wetland_data.get("total_area_km2", 0)
        coverage_pct = (wetland_area / area_km2 * 100) if area_km2 > 0 else 0
        
        # Optimal wetland coverage for hunting is 5-15%
        if coverage_pct >= 5 and coverage_pct <= 15:
            coverage_score = 100
        elif coverage_pct < 5:
            coverage_score = coverage_pct * 20  # 0-100 for 0-5%
        else:
            # Too much wetland can reduce traversability
            coverage_score = max(50, 100 - (coverage_pct - 15) * 2)
        
        # Calculate type diversity score
        wetland_types = wetland_data.get("types", [])
        type_scores = [self.WETLAND_QUALITY.get(t, 0.5) for t in wetland_types]
        diversity_score = (sum(type_scores) / len(type_scores) * 100) if type_scores else 50
        
        # Combined score
        total_score = coverage_score * 0.6 + diversity_score * 0.4
        
        return {
            "score": round(total_score, 1),
            "coverage_percent": round(coverage_pct, 2),
            "coverage_score": round(coverage_score, 1),
            "diversity_score": round(diversity_score, 1),
            "wetland_types": wetland_types,
            "hunting_value": self._get_wetland_hunting_value(coverage_pct)
        }
    
    def analyze_territory(
        self,
        hydro_data: Dict[str, Any],
        bbox: Dict[str, float],
        target_species: str = "deer"
    ) -> Dict[str, Any]:
        """
        Perform complete hydrological analysis of a territory.
        
        Args:
            hydro_data: Extracted hydrological data
            bbox: Bounding box
            target_species: Target hunting species
            
        Returns:
            Complete analysis with scores and recommendations
        """
        # Calculate area
        lat_diff = bbox["max_lat"] - bbox["min_lat"]
        lon_diff = bbox["max_lon"] - bbox["min_lon"]
        # Approximate area (at ~47° latitude, 1° lat ≈ 111km, 1° lon ≈ 75km)
        area_km2 = lat_diff * 111 * lon_diff * 75
        
        result = {
            "analysis_id": f"hydro_analysis_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "bbox": bbox,
            "area_km2": round(area_km2, 2),
            "target_species": target_species,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "recommendations": []
        }
        
        # Analyze rivers/streams
        if "rivers" in hydro_data.get("layers", {}):
            rivers = hydro_data["layers"]["rivers"]
            result["components"]["rivers"] = {
                "available": True,
                "tile_url": rivers.get("tile_url"),
                "statistics": rivers.get("statistics", {})
            }
        
        # Analyze lakes
        if "lakes" in hydro_data.get("layers", {}):
            lakes = hydro_data["layers"]["lakes"]
            result["components"]["lakes"] = {
                "available": True,
                "tile_url": lakes.get("tile_url"),
                "statistics": lakes.get("statistics", {})
            }
        
        # Analyze wetlands
        if "wetlands" in hydro_data.get("layers", {}):
            wetlands = hydro_data["layers"]["wetlands"]
            wetland_score = self.calculate_wetland_score(
                {"types": wetlands.get("wetland_types", [])},
                area_km2
            )
            result["components"]["wetlands"] = {
                "available": True,
                "tile_url": wetlands.get("tile_url"),
                "score": wetland_score,
                "hunting_relevance": wetlands.get("hunting_relevance", {})
            }
        
        # Calculate overall water score
        component_scores = []
        
        # Estimate proximity score based on data availability
        if result["components"].get("rivers", {}).get("available"):
            component_scores.append(70)  # Base score when rivers present
        if result["components"].get("lakes", {}).get("available"):
            component_scores.append(75)  # Base score when lakes present
        if result["components"].get("wetlands", {}).get("available"):
            wetland_comp = result["components"]["wetlands"]
            if "score" in wetland_comp:
                component_scores.append(wetland_comp["score"]["score"])
        
        # Calculate weighted overall score
        if component_scores:
            overall_score = sum(component_scores) / len(component_scores)
        else:
            overall_score = 40  # Default low score when no data
        
        result["overall_score"] = round(overall_score, 1)
        result["level"] = self._score_to_level(overall_score)
        
        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(
            result, target_species
        )
        
        return result
    
    def _get_interpretation(self, level: str, species: str) -> str:
        """Get interpretation text for a proximity level."""
        interpretations = {
            "excellent": f"Zone idéale pour {species} - Proximité d'eau optimale",
            "bon": f"Bonne zone - Eau accessible pour {species}",
            "modéré": f"Zone acceptable - {species} peut atteindre l'eau",
            "faible": f"Zone éloignée de l'eau - Moins favorable pour {species}"
        }
        return interpretations.get(level, "")
    
    def _get_wetland_hunting_value(self, coverage_pct: float) -> str:
        """Determine hunting value based on wetland coverage."""
        if coverage_pct >= 10:
            return "excellent_pour_sauvagine"
        elif coverage_pct >= 5:
            return "bon_habitat_humide"
        elif coverage_pct >= 2:
            return "quelques_zones_humides"
        else:
            return "terrain_sec"
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to level string."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "bon"
        elif score >= 40:
            return "modéré"
        elif score >= 20:
            return "faible"
        else:
            return "très_faible"
    
    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        species: str
    ) -> List[str]:
        """Generate hunting recommendations based on analysis."""
        recommendations = []
        score = analysis.get("overall_score", 0)
        
        if score >= 70:
            recommendations.append(
                "Excellent accès à l'eau - Positionez-vous entre les zones "
                "de nourriture et les points d'eau pour intercepter le gibier"
            )
        
        if analysis.get("components", {}).get("wetlands", {}).get("available"):
            if species == "moose":
                recommendations.append(
                    "Milieux humides présents - Les orignaux fréquentent "
                    "ces zones pour se nourrir de plantes aquatiques"
                )
            elif species in ["waterfowl", "duck"]:
                recommendations.append(
                    "Milieux humides idéaux pour la sauvagine - "
                    "Installez vos appelants près des marais"
                )
        
        if analysis.get("components", {}).get("rivers", {}).get("available"):
            recommendations.append(
                "Cours d'eau présents - Les cervidés utilisent souvent "
                "les vallées fluviales comme corridors de déplacement"
            )
        
        if analysis.get("components", {}).get("lakes", {}).get("available"):
            recommendations.append(
                "Lacs dans la zone - Surveillez les rives tôt le matin "
                "et en fin de journée (heures d'abreuvement)"
            )
        
        return recommendations


# Singleton instance
hydro_analyzer = HydroAnalyzer()
