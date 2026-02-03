"""
BIONIC™ Sentinel Engine - Vegetation Classifier

Classification avancée de la végétation pour l'analyse de territoires.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class VegetationClassifier:
    """
    Classificateur de végétation pour l'identification des habitats de chasse.
    
    Classes supportées:
    - Forêt de conifères
    - Forêt de feuillus
    - Forêt mixte
    - Milieux humides
    - Prairies/champs
    - Zones brûlées/perturbées
    """
    
    # Quebec forest types and their characteristics
    FOREST_TYPES = {
        "coniferous": {
            "name": "Forêt de conifères",
            "typical_ndvi": (0.5, 0.8),
            "seasonal_variation": "low",
            "species": ["épinette", "sapin", "pin"],
            "hunting_value": {
                "moose": "excellent",
                "deer": "good",
                "bear": "good",
                "smallgame": "excellent"
            }
        },
        "deciduous": {
            "name": "Forêt de feuillus",
            "typical_ndvi": (0.6, 0.9),
            "seasonal_variation": "high",
            "species": ["érable", "bouleau", "chêne", "hêtre"],
            "hunting_value": {
                "moose": "good",
                "deer": "excellent",
                "bear": "excellent",
                "turkey": "excellent"
            }
        },
        "mixed": {
            "name": "Forêt mixte",
            "typical_ndvi": (0.5, 0.85),
            "seasonal_variation": "moderate",
            "species": ["mélange conifères/feuillus"],
            "hunting_value": {
                "moose": "excellent",
                "deer": "excellent",
                "bear": "excellent",
                "turkey": "good"
            }
        },
        "regenerating": {
            "name": "Forêt en régénération",
            "typical_ndvi": (0.3, 0.5),
            "seasonal_variation": "moderate",
            "species": ["jeunes pousses", "arbustes"],
            "hunting_value": {
                "moose": "excellent",
                "deer": "excellent",
                "smallgame": "good"
            }
        }
    }
    
    # Land cover classes
    LAND_COVER = {
        "forest": {"ndvi_range": (0.4, 1.0), "color": "#228B22"},
        "shrubland": {"ndvi_range": (0.25, 0.4), "color": "#90EE90"},
        "grassland": {"ndvi_range": (0.15, 0.3), "color": "#ADFF2F"},
        "cropland": {"ndvi_range": (0.2, 0.5), "color": "#FFD700"},
        "wetland": {"ndvi_range": (0.1, 0.4), "color": "#4682B4"},
        "bare_soil": {"ndvi_range": (-0.1, 0.15), "color": "#D2691E"},
        "water": {"ndvi_range": (-1.0, 0.0), "color": "#1E90FF"},
        "urban": {"ndvi_range": (-0.2, 0.1), "color": "#808080"},
        "snow_ice": {"ndvi_range": (-0.5, 0.1), "color": "#FFFFFF"}
    }
    
    def __init__(self):
        self.forest_types = self.FOREST_TYPES
        self.land_cover = self.LAND_COVER
    
    def classify_forest_type(
        self,
        ndvi: float,
        evi: Optional[float] = None,
        season: str = "summer",
        lat: float = 47.0
    ) -> Dict[str, Any]:
        """
        Classify forest type based on vegetation indices.
        """
        # Adjust for season
        seasonal_factor = self._get_seasonal_factor(season)
        adjusted_ndvi = ndvi / seasonal_factor if seasonal_factor > 0 else ndvi
        
        # Classify based on NDVI and location
        if adjusted_ndvi < 0.3:
            forest_type = "regenerating"
            confidence = 70
        elif adjusted_ndvi < 0.5:
            forest_type = "mixed"
            confidence = 65
        elif adjusted_ndvi < 0.7:
            # Use EVI to distinguish coniferous vs deciduous
            if evi and evi > 0.4:
                forest_type = "deciduous"
                confidence = 75
            else:
                forest_type = "coniferous"
                confidence = 70
        else:
            # High NDVI - likely deciduous in summer
            if season == "summer":
                forest_type = "deciduous"
                confidence = 80
            else:
                forest_type = "coniferous"
                confidence = 75
        
        # Adjust confidence based on latitude (boreal vs temperate)
        if lat > 49:
            # Boreal zone - more likely coniferous
            if forest_type == "coniferous":
                confidence += 10
        elif lat < 46:
            # Temperate zone - more likely deciduous/mixed
            if forest_type in ["deciduous", "mixed"]:
                confidence += 10
        
        forest_info = self.forest_types.get(forest_type, {})
        
        return {
            "type": forest_type,
            "name": forest_info.get("name", "Non classifié"),
            "confidence": min(100, confidence),
            "typical_species": forest_info.get("species", []),
            "hunting_value": forest_info.get("hunting_value", {}),
            "seasonal_variation": forest_info.get("seasonal_variation", "moderate"),
            "adjusted_ndvi": round(adjusted_ndvi, 3)
        }
    
    def classify_land_cover(
        self,
        ndvi: float,
        ndwi: float = 0
    ) -> Dict[str, Any]:
        """
        Classify land cover type.
        """
        # Check for water first
        if ndwi > 0.3 or ndvi < -0.1:
            cover_type = "water"
            confidence = 90 if ndwi > 0.5 else 75
        elif ndvi < 0.1:
            cover_type = "bare_soil"
            confidence = 70
        elif ndvi < 0.2:
            cover_type = "grassland"
            confidence = 65
        elif ndvi < 0.35:
            # Could be shrubland or cropland
            cover_type = "shrubland"
            confidence = 60
        elif ndvi < 0.5:
            # Wetland or sparse forest
            if ndwi > 0:
                cover_type = "wetland"
                confidence = 70
            else:
                cover_type = "shrubland"
                confidence = 65
        else:
            cover_type = "forest"
            confidence = 80
        
        cover_info = self.land_cover.get(cover_type, {})
        
        return {
            "type": cover_type,
            "display_name": self._get_cover_display_name(cover_type),
            "confidence": confidence,
            "color": cover_info.get("color", "#888888"),
            "ndvi_range": cover_info.get("ndvi_range", (0, 1))
        }
    
    def get_hunting_zones(
        self,
        classifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify optimal hunting zones based on land cover classification.
        """
        zones = {
            "high_potential": [],
            "moderate_potential": [],
            "low_potential": [],
            "water_points": []
        }
        
        for i, classification in enumerate(classifications):
            cover_type = classification.get("type", "")
            
            if cover_type in ["forest", "shrubland"]:
                if classification.get("confidence", 0) > 70:
                    zones["high_potential"].append(i)
                else:
                    zones["moderate_potential"].append(i)
            elif cover_type == "wetland":
                zones["high_potential"].append(i)
            elif cover_type == "water":
                zones["water_points"].append(i)
            elif cover_type in ["grassland", "cropland"]:
                zones["moderate_potential"].append(i)
            else:
                zones["low_potential"].append(i)
        
        return {
            "zones": zones,
            "summary": {
                "high_potential_count": len(zones["high_potential"]),
                "moderate_potential_count": len(zones["moderate_potential"]),
                "water_points_count": len(zones["water_points"]),
                "total_classified": len(classifications)
            }
        }
    
    def _get_seasonal_factor(self, season: str) -> float:
        """Get NDVI adjustment factor for season."""
        factors = {
            "spring": 0.7,
            "summer": 1.0,
            "fall": 0.8,
            "winter": 0.4
        }
        return factors.get(season, 1.0)
    
    def _get_cover_display_name(self, cover_type: str) -> str:
        """Get French display name for cover type."""
        names = {
            "forest": "Forêt",
            "shrubland": "Arbustes/broussailles",
            "grassland": "Prairie",
            "cropland": "Terres agricoles",
            "wetland": "Milieu humide",
            "bare_soil": "Sol nu",
            "water": "Eau",
            "urban": "Zone urbaine",
            "snow_ice": "Neige/glace"
        }
        return names.get(cover_type, cover_type)


# Singleton instance
vegetation_classifier = VegetationClassifier()
