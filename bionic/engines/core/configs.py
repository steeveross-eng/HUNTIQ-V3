"""
BIONIC™ Engine - Configurations
================================
Configurations centralisées pour les modules d'analyse et les espèces.

Ce fichier contient:
- MODULE_CONFIGS: Configuration des 8 modules thématiques
- SPECIES_CONFIGS: Configuration des 6 espèces supportées
- Constantes et énumérations
"""

from enum import Enum
from typing import Dict, List, Any


class ModuleType(str, Enum):
    """Types de modules d'analyse BIONIC™"""
    THERMAL = "thermal"
    WETNESS = "wetness"
    FOOD = "food"
    PRESSURE = "pressure"
    ACCESS = "access"
    CORRIDOR = "corridor"
    GEOFORM = "geoform"
    CANOPY = "canopy"


class SpeciesType(str, Enum):
    """Espèces supportées par BIONIC™"""
    MOOSE = "moose"
    DEER = "deer"
    BEAR = "bear"
    CARIBOU = "caribou"
    WOLF = "wolf"
    TURKEY = "turkey"


class SeasonType(str, Enum):
    """Saisons pour l'analyse saisonnière"""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


# ============================================
# MODULE CONFIGURATIONS
# ============================================

MODULE_CONFIGS: Dict[ModuleType, Dict[str, Any]] = {
    ModuleType.THERMAL: {
        "name": "ThermalScore",
        "version": "1.0",
        "description": "Analyse du confort thermique et des refuges",
        "factors": ["temperature", "aspect", "elevation", "canopy_cover", "water_proximity"],
        "weights": {"temperature": 0.3, "aspect": 0.2, "elevation": 0.2, "canopy_cover": 0.2, "water_proximity": 0.1}
    },
    ModuleType.WETNESS: {
        "name": "WetnessScore",
        "version": "1.0",
        "description": "Analyse hydrologique et humidité du terrain",
        "factors": ["twi", "stream_distance", "wetland_area", "precipitation", "ndwi"],
        "weights": {"twi": 0.25, "stream_distance": 0.25, "wetland_area": 0.2, "precipitation": 0.15, "ndwi": 0.15}
    },
    ModuleType.FOOD: {
        "name": "FoodScore",
        "version": "1.0",
        "description": "Analyse de la disponibilité alimentaire",
        "factors": ["ndvi", "forest_type", "edge_density", "mast_production", "browse_availability"],
        "weights": {"ndvi": 0.25, "forest_type": 0.2, "edge_density": 0.2, "mast_production": 0.2, "browse_availability": 0.15}
    },
    ModuleType.PRESSURE: {
        "name": "PressureScore",
        "version": "1.0",
        "description": "Analyse de la pression humaine et perturbations",
        "factors": ["road_density", "building_proximity", "hunting_pressure", "noise_level", "light_pollution"],
        "weights": {"road_density": 0.25, "building_proximity": 0.25, "hunting_pressure": 0.2, "noise_level": 0.15, "light_pollution": 0.15}
    },
    ModuleType.ACCESS: {
        "name": "AccessScore",
        "version": "1.0",
        "description": "Analyse de l'accessibilité pour la chasse",
        "factors": ["trail_distance", "road_distance", "terrain_difficulty", "visibility", "parking_proximity"],
        "weights": {"trail_distance": 0.25, "road_distance": 0.2, "terrain_difficulty": 0.2, "visibility": 0.2, "parking_proximity": 0.15}
    },
    ModuleType.CORRIDOR: {
        "name": "CorridorScore",
        "version": "1.0",
        "description": "Analyse des corridors fauniques",
        "factors": ["connectivity", "bottleneck_index", "crossing_density", "habitat_continuity", "barrier_presence"],
        "weights": {"connectivity": 0.25, "bottleneck_index": 0.2, "crossing_density": 0.2, "habitat_continuity": 0.2, "barrier_presence": 0.15}
    },
    ModuleType.GEOFORM: {
        "name": "GeoFormScore",
        "version": "1.0",
        "description": "Analyse géomorphologique du terrain",
        "factors": ["slope", "aspect", "curvature", "roughness", "landform_type"],
        "weights": {"slope": 0.25, "aspect": 0.2, "curvature": 0.2, "roughness": 0.2, "landform_type": 0.15}
    },
    ModuleType.CANOPY: {
        "name": "CanopyScore",
        "version": "1.0",
        "description": "Analyse de la canopée forestière",
        "factors": ["canopy_height", "canopy_closure", "understory_density", "species_diversity", "age_class"],
        "weights": {"canopy_height": 0.2, "canopy_closure": 0.25, "understory_density": 0.2, "species_diversity": 0.2, "age_class": 0.15}
    }
}


# ============================================
# SPECIES CONFIGURATIONS
# ============================================

SPECIES_CONFIGS: Dict[SpeciesType, Dict[str, Any]] = {
    SpeciesType.MOOSE: {
        "name": "MooseScore",
        "common_name": "Orignal",
        "version": "1.0",
        "module_weights": {
            "thermal": 0.15, "wetness": 0.2, "food": 0.25, "pressure": 0.15,
            "corridor": 0.1, "canopy": 0.1, "geoform": 0.05
        },
        "optimal_habitat": {
            "elevation_range": [100, 800],
            "slope_max": 25,
            "water_distance_max": 500,
            "forest_cover_min": 0.4,
            "road_distance_min": 200
        }
    },
    SpeciesType.DEER: {
        "name": "DeerScore",
        "common_name": "Cerf de Virginie",
        "version": "1.0",
        "module_weights": {
            "thermal": 0.1, "wetness": 0.1, "food": 0.3, "pressure": 0.15,
            "corridor": 0.15, "canopy": 0.1, "geoform": 0.1
        },
        "optimal_habitat": {
            "elevation_range": [0, 600],
            "slope_max": 30,
            "water_distance_max": 1000,
            "forest_cover_min": 0.3,
            "road_distance_min": 100
        }
    },
    SpeciesType.BEAR: {
        "name": "BearScore",
        "common_name": "Ours noir",
        "version": "1.0",
        "module_weights": {
            "thermal": 0.1, "wetness": 0.15, "food": 0.35, "pressure": 0.2,
            "corridor": 0.1, "canopy": 0.05, "geoform": 0.05
        },
        "optimal_habitat": {
            "elevation_range": [0, 1200],
            "slope_max": 40,
            "water_distance_max": 2000,
            "forest_cover_min": 0.5,
            "road_distance_min": 500
        }
    },
    SpeciesType.CARIBOU: {
        "name": "CaribouScore",
        "common_name": "Caribou forestier",
        "version": "1.0",
        "module_weights": {
            "thermal": 0.15, "wetness": 0.15, "food": 0.2, "pressure": 0.25,
            "corridor": 0.15, "canopy": 0.05, "geoform": 0.05
        },
        "optimal_habitat": {
            "elevation_range": [300, 1500],
            "slope_max": 20,
            "water_distance_max": 3000,
            "forest_cover_min": 0.6,
            "road_distance_min": 1000
        }
    },
    SpeciesType.WOLF: {
        "name": "WolfScore",
        "common_name": "Loup gris",
        "version": "1.0",
        "module_weights": {
            "thermal": 0.05, "wetness": 0.1, "food": 0.15, "pressure": 0.3,
            "corridor": 0.25, "canopy": 0.05, "geoform": 0.1
        },
        "optimal_habitat": {
            "elevation_range": [0, 2000],
            "slope_max": 45,
            "water_distance_max": 5000,
            "forest_cover_min": 0.2,
            "road_distance_min": 2000
        }
    },
    SpeciesType.TURKEY: {
        "name": "TurkeyScore",
        "common_name": "Dindon sauvage",
        "version": "1.0",
        "module_weights": {
            "thermal": 0.1, "wetness": 0.05, "food": 0.35, "pressure": 0.1,
            "corridor": 0.1, "canopy": 0.2, "geoform": 0.1
        },
        "optimal_habitat": {
            "elevation_range": [0, 500],
            "slope_max": 20,
            "water_distance_max": 500,
            "forest_cover_min": 0.4,
            "road_distance_min": 50
        }
    }
}


# ============================================
# SEASONAL FACTORS
# ============================================

SEASON_FACTORS: Dict[SpeciesType, Dict[str, float]] = {
    SpeciesType.MOOSE: {"spring": 0.9, "summer": 0.85, "fall": 1.0, "winter": 0.7},
    SpeciesType.DEER: {"spring": 0.85, "summer": 0.8, "fall": 1.0, "winter": 0.75},
    SpeciesType.BEAR: {"spring": 0.95, "summer": 1.0, "fall": 1.0, "winter": 0.1},
    SpeciesType.CARIBOU: {"spring": 0.8, "summer": 0.85, "fall": 0.95, "winter": 1.0},
    SpeciesType.WOLF: {"spring": 0.9, "summer": 0.85, "fall": 0.95, "winter": 1.0},
    SpeciesType.TURKEY: {"spring": 1.0, "summer": 0.9, "fall": 0.95, "winter": 0.7}
}


# ============================================
# TIME OF DAY FACTORS
# ============================================

TIME_OF_DAY_FACTORS: Dict[str, Dict[str, float]] = {
    "dawn": {"moose": 1.2, "deer": 1.3, "bear": 1.1, "turkey": 1.4},
    "morning": {"moose": 1.0, "deer": 1.1, "bear": 1.0, "turkey": 1.2},
    "midday": {"moose": 0.7, "deer": 0.8, "bear": 0.9, "turkey": 0.9},
    "afternoon": {"moose": 0.8, "deer": 0.9, "bear": 1.0, "turkey": 1.0},
    "dusk": {"moose": 1.3, "deer": 1.4, "bear": 1.2, "turkey": 1.1},
    "night": {"moose": 0.6, "deer": 0.5, "bear": 0.8, "turkey": 0.1}
}
