"""Weather Fauna Simulation Engine Module v1

Simulation of weather impact on wildlife activity.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import random

router = APIRouter(prefix="/api/v1/simulation", tags=["Weather Fauna Simulation Engine"])


WEATHER_IMPACT_MATRIX = {
    "deer": {
        "temperature": {"optimal_min": -5, "optimal_max": 15, "activity_boost": 1.3},
        "pressure_change": {"threshold": 5, "activity_boost": 1.5},
        "wind": {"optimal_max": 15, "penalty_factor": 0.8},
        "precipitation": {"light": 0.9, "heavy": 0.5, "snow": 1.2},
        "moon_full": {"day_penalty": 0.7, "night_boost": 1.3}
    },
    "moose": {
        "temperature": {"optimal_min": -10, "optimal_max": 10, "activity_boost": 1.2},
        "pressure_change": {"threshold": 8, "activity_boost": 1.4},
        "wind": {"optimal_max": 20, "penalty_factor": 0.85},
        "precipitation": {"light": 1.0, "heavy": 0.7, "snow": 1.1},
        "moon_full": {"day_penalty": 0.8, "night_boost": 1.2}
    },
    "bear": {
        "temperature": {"optimal_min": 5, "optimal_max": 25, "activity_boost": 1.1},
        "pressure_change": {"threshold": 10, "activity_boost": 1.2},
        "wind": {"optimal_max": 25, "penalty_factor": 0.9},
        "precipitation": {"light": 0.8, "heavy": 0.4, "snow": 0},
        "moon_full": {"day_penalty": 1.0, "night_boost": 1.0}
    }
}


def simulate_activity(species: str, temperature: float, pressure_change: float, 
                      wind_speed: float, precipitation: str, moon_phase: str) -> Dict:
    """Simulate wildlife activity based on weather conditions"""
    if species not in WEATHER_IMPACT_MATRIX:
        return {"error": "Species not supported"}
    
    matrix = WEATHER_IMPACT_MATRIX[species]
    base_activity = 50.0
    factors = []
    
    # Temperature impact
    temp_config = matrix["temperature"]
    if temp_config["optimal_min"] <= temperature <= temp_config["optimal_max"]:
        base_activity *= temp_config["activity_boost"]
        factors.append(f"Température optimale (+{int((temp_config['activity_boost']-1)*100)}%)")
    elif temperature < temp_config["optimal_min"] - 10 or temperature > temp_config["optimal_max"] + 10:
        base_activity *= 0.6
        factors.append("Température extrême (-40%)")
    
    # Pressure change impact
    if abs(pressure_change) >= matrix["pressure_change"]["threshold"]:
        base_activity *= matrix["pressure_change"]["activity_boost"]
        factors.append(f"Changement de pression (+{int((matrix['pressure_change']['activity_boost']-1)*100)}%)")
    
    # Wind impact
    if wind_speed > matrix["wind"]["optimal_max"]:
        base_activity *= matrix["wind"]["penalty_factor"]
        factors.append(f"Vent fort ({int((1-matrix['wind']['penalty_factor'])*100)}%)")
    
    # Precipitation impact
    precip_factor = matrix["precipitation"].get(precipitation, 1.0)
    if precip_factor != 1.0:
        base_activity *= precip_factor
        if precip_factor > 1:
            factors.append(f"Neige (+{int((precip_factor-1)*100)}%)")
        else:
            factors.append(f"Précipitations ({int((1-precip_factor)*100)}%)")
    
    # Moon phase impact
    if moon_phase == "full":
        base_activity *= matrix["moon_full"]["day_penalty"]
        factors.append("Pleine lune - activité diurne réduite")
    
    # Normalize
    activity_score = min(100, max(0, base_activity))
    
    return {
        "activity_score": round(activity_score, 1),
        "factors": factors,
        "prediction": "Excellente" if activity_score >= 75 else "Bonne" if activity_score >= 50 else "Faible"
    }


@router.get("/")
async def simulation_engine_info():
    return {
        "module": "weather_fauna_simulation_engine",
        "version": "1.0.0",
        "description": "Simulation of weather impact on wildlife",
        "features": ["Activity simulation", "Optimal conditions", "Multi-factor analysis", "Predictive alerts"],
        "supported_species": list(WEATHER_IMPACT_MATRIX.keys())
    }


@router.post("/weather-impact")
async def simulate_weather_impact(
    species: str,
    temperature: float = Query(...),
    pressure_change: float = Query(0, description="hPa change in last 24h"),
    wind_speed: float = Query(10, ge=0),
    precipitation: str = Query("none", description="none, light, heavy, snow"),
    moon_phase: str = Query("other", description="full, new, other")
):
    result = simulate_activity(species, temperature, pressure_change, wind_speed, precipitation, moon_phase)
    
    if "error" in result:
        return {"success": False, **result, "available_species": list(WEATHER_IMPACT_MATRIX.keys())}
    
    return {
        "success": True,
        "species": species,
        "conditions": {
            "temperature": temperature,
            "pressure_change": pressure_change,
            "wind_speed": wind_speed,
            "precipitation": precipitation,
            "moon_phase": moon_phase
        },
        "simulation": result
    }


@router.get("/predict/{species}")
async def predict_best_conditions(species: str):
    if species not in WEATHER_IMPACT_MATRIX:
        return {"success": False, "error": "Species not supported"}
    
    matrix = WEATHER_IMPACT_MATRIX[species]
    
    return {
        "success": True,
        "species": species,
        "optimal_conditions": {
            "temperature": {
                "min": matrix["temperature"]["optimal_min"],
                "max": matrix["temperature"]["optimal_max"],
                "unit": "°C"
            },
            "pressure": f"Variation > {matrix['pressure_change']['threshold']} hPa",
            "wind": f"< {matrix['wind']['optimal_max']} km/h",
            "precipitation": "Légère neige idéale" if matrix["precipitation"].get("snow", 0) > 1 else "Temps sec préféré",
            "moon": "Nouvelle lune ou croissant"
        },
        "tip": "Les changements de pression barométrique sont le meilleur indicateur d'activité"
    }


@router.get("/optimal-conditions")
async def get_optimal_conditions(species: str = "deer"):
    if species not in WEATHER_IMPACT_MATRIX:
        return {"success": False, "error": "Species not supported"}
    
    matrix = WEATHER_IMPACT_MATRIX[species]
    
    # Simulate finding optimal windows
    optimal_windows = [
        {"day": "Lundi", "time": "06:00-09:00", "score": 85, "reason": "Pression en hausse"},
        {"day": "Mercredi", "time": "16:00-19:00", "score": 78, "reason": "Température idéale après front froid"},
        {"day": "Samedi", "time": "05:30-08:30", "score": 92, "reason": "Conditions parfaites prévues"}
    ]
    
    return {
        "success": True,
        "species": species,
        "optimal_windows": optimal_windows,
        "current_recommendation": "Samedi matin offre les meilleures conditions"
    }


@router.get("/alerts")
async def get_activity_alerts(species: str = "deer"):
    if species not in WEATHER_IMPACT_MATRIX:
        return {"success": False, "error": "Species not supported"}
    
    # Simulated alerts
    alerts = [
        {"type": "optimal", "message": f"Conditions optimales prévues samedi", "priority": "high"},
        {"type": "pressure", "message": "Front froid prévu jeudi - forte activité attendue", "priority": "medium"},
        {"type": "rut", "message": "Pic du rut dans 5 jours", "priority": "high"}
    ]
    
    return {"success": True, "species": species, "alerts": alerts}
