"""Ecoforestry Engine Module v1

Ecoforestry data and habitat analysis.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

router = APIRouter(prefix="/api/v1/ecoforestry", tags=["Ecoforestry Engine"])


class ForestType(str, Enum):
    CONIFEROUS = "coniferous"  # Résineux
    DECIDUOUS = "deciduous"    # Feuillus
    MIXED = "mixed"            # Mixte
    REGENERATION = "regeneration"  # Régénération


class ForestStand(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ForestType
    species_dominant: str  # Ex: "Érable", "Épinette noire"
    age_class: str         # "10-30", "30-50", "50-70", "70-90", "90+"
    density: float = Field(ge=0, le=100)  # % coverage
    height_avg: float      # meters
    area_ha: float
    coordinates: Dict[str, float] = {}


HABITAT_SUITABILITY = {
    "deer": {
        "preferred_forest": ["mixed", "deciduous"],
        "preferred_age": ["30-50", "50-70"],
        "min_density": 40,
        "max_density": 80,
        "notes": "Préfère les lisières et zones de régénération"
    },
    "moose": {
        "preferred_forest": ["mixed", "coniferous"],
        "preferred_age": ["10-30", "30-50"],
        "min_density": 30,
        "max_density": 70,
        "notes": "Recherche les zones humides et jeunes forêts"
    },
    "bear": {
        "preferred_forest": ["mixed", "deciduous"],
        "preferred_age": ["50-70", "70-90"],
        "min_density": 50,
        "max_density": 90,
        "notes": "Préfère les forêts matures avec fruits"
    }
}

SAMPLE_STANDS = [
    {"id": "stand-001", "type": "mixed", "species_dominant": "Érable à sucre", "age_class": "50-70", "density": 65, "height_avg": 18, "area_ha": 45.2},
    {"id": "stand-002", "type": "coniferous", "species_dominant": "Épinette noire", "age_class": "30-50", "density": 75, "height_avg": 12, "area_ha": 120.5},
    {"id": "stand-003", "type": "regeneration", "species_dominant": "Tremble", "age_class": "10-30", "density": 40, "height_avg": 6, "area_ha": 28.0},
    {"id": "stand-004", "type": "deciduous", "species_dominant": "Bouleau jaune", "age_class": "70-90", "density": 55, "height_avg": 22, "area_ha": 67.8},
]


def calculate_habitat_score(stand: Dict, species: str) -> float:
    """Calculate habitat suitability score for a species"""
    if species not in HABITAT_SUITABILITY:
        return 50.0
    
    prefs = HABITAT_SUITABILITY[species]
    score = 50.0
    
    if stand.get("type") in prefs["preferred_forest"]:
        score += 20
    if stand.get("age_class") in prefs["preferred_age"]:
        score += 15
    
    density = stand.get("density", 50)
    if prefs["min_density"] <= density <= prefs["max_density"]:
        score += 15
    
    return min(100, score)


@router.get("/")
async def ecoforestry_engine_info():
    return {
        "module": "ecoforestry_engine",
        "version": "1.0.0",
        "description": "Ecoforestry data and habitat analysis",
        "features": ["Forest stand data", "Habitat suitability", "Species preferences", "Cut analysis"],
        "forest_types": [f.value for f in ForestType],
        "supported_species": list(HABITAT_SUITABILITY.keys())
    }


@router.get("/stands")
async def list_forest_stands(forest_type: Optional[str] = None, min_density: float = Query(0, ge=0, le=100)):
    stands = SAMPLE_STANDS.copy()
    if forest_type:
        stands = [s for s in stands if s["type"] == forest_type]
    stands = [s for s in stands if s["density"] >= min_density]
    return {"success": True, "stands": stands}


@router.get("/habitats/{species}")
async def get_habitat_preferences(species: str):
    if species not in HABITAT_SUITABILITY:
        return {"success": False, "error": f"Species '{species}' not found", "available": list(HABITAT_SUITABILITY.keys())}
    return {"success": True, "species": species, "preferences": HABITAT_SUITABILITY[species]}


@router.post("/analyze")
async def analyze_habitat(latitude: float, longitude: float, species: str = "deer"):
    # Simulated analysis based on coordinates
    sample_stand = SAMPLE_STANDS[0].copy()
    score = calculate_habitat_score(sample_stand, species)
    
    return {
        "success": True,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "species": species,
        "habitat_score": round(score, 1),
        "stand_info": sample_stand,
        "recommendation": "Zone favorable" if score >= 70 else "Zone moyenne" if score >= 50 else "Zone peu favorable"
    }


@router.get("/cuts")
async def get_recent_cuts(years_back: int = Query(5, ge=1, le=20)):
    cuts = [
        {"id": "cut-001", "year": 2023, "type": "CPRS", "area_ha": 35.2, "species_affected": ["deer", "moose"]},
        {"id": "cut-002", "year": 2022, "type": "Coupe partielle", "area_ha": 18.5, "species_affected": ["deer"]},
        {"id": "cut-003", "year": 2021, "type": "Éclaircie", "area_ha": 45.0, "species_affected": ["moose"]},
    ]
    return {"success": True, "years_back": years_back, "cuts": cuts}


@router.get("/species-distribution")
async def get_species_distribution():
    return {
        "success": True,
        "distribution": {
            "deer": {"density": "high", "best_areas": ["mixed forests", "edges", "regeneration zones"]},
            "moose": {"density": "medium", "best_areas": ["wetlands", "young forests", "lake shores"]},
            "bear": {"density": "low-medium", "best_areas": ["mature forests", "berry areas", "salmon streams"]}
        }
    }
