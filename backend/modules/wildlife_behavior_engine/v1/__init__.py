"""Wildlife Behavior Engine Module v1

Wildlife behavior modeling and prediction.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/wildlife", tags=["Wildlife Behavior Engine"])


class ActivityLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    PEAK = "peak"


SPECIES_BEHAVIORS = {
    "deer": {
        "name": "Cerf de Virginie",
        "scientific_name": "Odocoileus virginianus",
        "activity_pattern": "crepuscular",  # Dawn/dusk
        "peak_hours": ["05:00-08:00", "17:00-20:00"],
        "feeding_times": ["06:00-09:00", "16:00-19:00"],
        "bedding_times": ["10:00-15:00"],
        "home_range_km2": {"male": 2.5, "female": 1.5},
        "seasonal_behavior": {
            "spring": {"activity": "moderate", "focus": "feeding", "movement": "expanding"},
            "summer": {"activity": "low", "focus": "feeding/cooling", "movement": "stable"},
            "fall": {"activity": "peak", "focus": "rut/feeding", "movement": "high"},
            "winter": {"activity": "low", "focus": "survival", "movement": "reduced"}
        },
        "rut_period": {"start": "October 15", "peak": "November 10-20", "end": "December 15"},
        "preferred_habitat": ["forest edge", "agricultural fields", "regeneration zones"],
        "sensitivity": {"hearing": 9, "smell": 10, "vision": 7}
    },
    "moose": {
        "name": "Orignal",
        "scientific_name": "Alces alces",
        "activity_pattern": "crepuscular",
        "peak_hours": ["04:00-09:00", "16:00-21:00"],
        "feeding_times": ["05:00-10:00", "15:00-20:00"],
        "bedding_times": ["11:00-14:00"],
        "home_range_km2": {"male": 25, "female": 15},
        "seasonal_behavior": {
            "spring": {"activity": "high", "focus": "feeding/minerals", "movement": "high"},
            "summer": {"activity": "moderate", "focus": "aquatic feeding", "movement": "moderate"},
            "fall": {"activity": "peak", "focus": "rut", "movement": "very high"},
            "winter": {"activity": "low", "focus": "survival", "movement": "yarding"}
        },
        "rut_period": {"start": "September 15", "peak": "September 25-October 10", "end": "October 25"},
        "preferred_habitat": ["wetlands", "lake shores", "young forests", "willow patches"],
        "sensitivity": {"hearing": 8, "smell": 10, "vision": 6}
    },
    "bear": {
        "name": "Ours noir",
        "scientific_name": "Ursus americanus",
        "activity_pattern": "diurnal/crepuscular",
        "peak_hours": ["06:00-10:00", "16:00-20:00"],
        "feeding_times": ["07:00-11:00", "15:00-19:00"],
        "bedding_times": ["12:00-15:00", "night"],
        "home_range_km2": {"male": 150, "female": 40},
        "seasonal_behavior": {
            "spring": {"activity": "high", "focus": "protein/carrion", "movement": "high"},
            "summer": {"activity": "moderate", "focus": "berries/insects", "movement": "moderate"},
            "fall": {"activity": "very high", "focus": "hyperphagia", "movement": "high"},
            "winter": {"activity": "none", "focus": "hibernation", "movement": "none"}
        },
        "hibernation": {"start": "November", "end": "April"},
        "preferred_habitat": ["mature forests", "berry patches", "salmon streams"],
        "sensitivity": {"hearing": 7, "smell": 10, "vision": 5}
    }
}


def calculate_activity_score(species: str, hour: int, season: str) -> float:
    """Calculate activity score based on species, time and season"""
    if species not in SPECIES_BEHAVIORS:
        return 50.0
    
    behavior = SPECIES_BEHAVIORS[species]
    score = 30.0  # Base
    
    # Time of day factor
    peak_hours = behavior.get("peak_hours", [])
    for period in peak_hours:
        start, end = period.split("-")
        start_h = int(start.split(":")[0])
        end_h = int(end.split(":")[0])
        if start_h <= hour <= end_h:
            score += 40
            break
    
    # Season factor
    seasonal = behavior.get("seasonal_behavior", {}).get(season, {})
    activity_level = seasonal.get("activity", "moderate")
    if activity_level == "peak":
        score += 25
    elif activity_level == "high":
        score += 15
    elif activity_level == "low":
        score -= 15
    elif activity_level == "very_low" or activity_level == "none":
        score -= 30
    
    return min(100, max(0, score))


@router.get("/")
async def wildlife_behavior_info():
    return {
        "module": "wildlife_behavior_engine",
        "version": "1.0.0",
        "description": "Wildlife behavior modeling and prediction",
        "features": ["Species behaviors", "Activity prediction", "Seasonal patterns", "Movement analysis"],
        "supported_species": list(SPECIES_BEHAVIORS.keys())
    }


@router.get("/species/{species}")
async def get_species_behavior(species: str):
    if species not in SPECIES_BEHAVIORS:
        return {"success": False, "error": f"Species '{species}' not found", "available": list(SPECIES_BEHAVIORS.keys())}
    return {"success": True, "species": species, "behavior": SPECIES_BEHAVIORS[species]}


@router.get("/patterns/{species}")
async def get_activity_patterns(species: str):
    if species not in SPECIES_BEHAVIORS:
        return {"success": False, "error": "Species not found"}
    
    behavior = SPECIES_BEHAVIORS[species]
    return {
        "success": True,
        "species": species,
        "activity_pattern": behavior.get("activity_pattern"),
        "peak_hours": behavior.get("peak_hours"),
        "feeding_times": behavior.get("feeding_times"),
        "bedding_times": behavior.get("bedding_times")
    }


@router.get("/predict-activity")
async def predict_activity(species: str, hour: int = Query(..., ge=0, le=23), season: str = Query("fall")):
    if species not in SPECIES_BEHAVIORS:
        return {"success": False, "error": "Species not found"}
    
    score = calculate_activity_score(species, hour, season)
    
    if score >= 80:
        level = ActivityLevel.PEAK
        recommendation = "Moment idéal pour la chasse"
    elif score >= 60:
        level = ActivityLevel.HIGH
        recommendation = "Bon moment, forte activité attendue"
    elif score >= 40:
        level = ActivityLevel.MODERATE
        recommendation = "Activité moyenne, patience requise"
    elif score >= 20:
        level = ActivityLevel.LOW
        recommendation = "Faible activité, considérez un autre moment"
    else:
        level = ActivityLevel.VERY_LOW
        recommendation = "Très faible activité, moment non recommandé"
    
    return {
        "success": True,
        "species": species,
        "hour": hour,
        "season": season,
        "activity_score": round(score, 1),
        "activity_level": level.value,
        "recommendation": recommendation
    }


@router.get("/seasonal/{species}/{season}")
async def get_seasonal_behavior(species: str, season: str):
    if species not in SPECIES_BEHAVIORS:
        return {"success": False, "error": "Species not found"}
    
    behavior = SPECIES_BEHAVIORS[species]
    seasonal = behavior.get("seasonal_behavior", {}).get(season)
    
    if not seasonal:
        return {"success": False, "error": f"Season '{season}' not found"}
    
    return {
        "success": True,
        "species": species,
        "season": season,
        "behavior": seasonal,
        "rut_period": behavior.get("rut_period") if season == "fall" else None
    }


@router.get("/rut-calendar")
async def get_rut_calendar():
    calendar = {}
    for species, data in SPECIES_BEHAVIORS.items():
        if "rut_period" in data:
            calendar[species] = data["rut_period"]
    return {"success": True, "rut_calendar": calendar}


@router.get("/sensitivity/{species}")
async def get_species_sensitivity(species: str):
    if species not in SPECIES_BEHAVIORS:
        return {"success": False, "error": "Species not found"}
    
    sensitivity = SPECIES_BEHAVIORS[species].get("sensitivity", {})
    
    return {
        "success": True,
        "species": species,
        "sensitivity": sensitivity,
        "hunting_tips": {
            "smell": "Chassez vent de face" if sensitivity.get("smell", 0) >= 9 else "Attention au vent",
            "hearing": "Mouvements lents et silencieux" if sensitivity.get("hearing", 0) >= 8 else "Évitez les bruits forts",
            "vision": "Portez du camouflage" if sensitivity.get("vision", 0) >= 7 else "Restez immobile"
        }
    }
