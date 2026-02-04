"""
BIONIC™ Engine - Main Analysis Endpoint
bionic_engine.py

Endpoint principal pour l'analyse complète de territoire BIONIC™.
Orchestre tous les modules, modèles fauniques, prédictions IA et analyse temporelle.

Version: BIONIC_CORE 1.0
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import math
import os
import httpx

# Import des modèles BIONIC
from bionic_core_models import (
    TerritoryFullAnalysis,
    ModuleResult,
    SpeciesResult,
    PredictionResult,
    TemporalResult,
    SinglePrediction,
    HabitatSuitability,
    NDVITimeSeries,
    SnowAnalysis,
    PhenologyData,
    ModuleType,
    SpeciesType,
    PredictionHorizon,
)

# MongoDB
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Router
bionic_engine_router = APIRouter(
    prefix="/api/bionic",
    tags=["BIONIC Engine"]
)

# =============================================================================
# CONFIGURATION
# =============================================================================

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'huntiq')
API_BASE = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')

# Configuration des modules BIONIC
MODULE_CONFIGS = {
    ModuleType.VEGETATION: {
        "name": "Analyse Végétation",
        "weight": 0.25,
        "factors": ["ndvi", "forest_cover", "canopy_density", "understory"],
        "thresholds": {"excellent": 80, "good": 65, "moderate": 50, "low": 35}
    },
    ModuleType.HYDROLOGY: {
        "name": "Analyse Hydrologique",
        "weight": 0.20,
        "factors": ["water_proximity", "wetland_coverage", "stream_density", "water_quality"],
        "thresholds": {"excellent": 75, "good": 60, "moderate": 45, "low": 30}
    },
    ModuleType.TERRAIN: {
        "name": "Analyse Terrain",
        "weight": 0.15,
        "factors": ["elevation", "slope", "aspect", "ruggedness"],
        "thresholds": {"excellent": 70, "good": 55, "moderate": 40, "low": 25}
    },
    ModuleType.FOOD: {
        "name": "Sources Alimentaires",
        "weight": 0.20,
        "factors": ["mast_availability", "browse_quality", "agriculture_proximity", "seasonal_food"],
        "thresholds": {"excellent": 80, "good": 65, "moderate": 50, "low": 35}
    },
    ModuleType.COVER: {
        "name": "Couvert & Abris",
        "weight": 0.10,
        "factors": ["thermal_cover", "escape_cover", "bedding_areas", "edge_habitat"],
        "thresholds": {"excellent": 75, "good": 60, "moderate": 45, "low": 30}
    },
    ModuleType.WEATHER: {
        "name": "Conditions Météo",
        "weight": 0.10,
        "factors": ["temperature", "precipitation", "wind", "pressure"],
        "thresholds": {"excellent": 85, "good": 70, "moderate": 55, "low": 40}
    },
}

# Configuration des espèces
SPECIES_CONFIGS = {
    SpeciesType.DEER: {
        "name_fr": "Cerf de Virginie",
        "weights": {"vegetation": 0.30, "food": 0.25, "cover": 0.20, "water": 0.15, "terrain": 0.10},
        "optimal_temp_range": (5, 20),
        "activity_peaks": [6, 7, 17, 18, 19],
        "seasonal_factors": {"spring": 0.85, "summer": 0.75, "fall": 1.15, "winter": 0.90}
    },
    SpeciesType.MOOSE: {
        "name_fr": "Orignal",
        "weights": {"water": 0.35, "vegetation": 0.25, "food": 0.20, "cover": 0.15, "terrain": 0.05},
        "optimal_temp_range": (-5, 15),
        "activity_peaks": [5, 6, 18, 19, 20],
        "seasonal_factors": {"spring": 0.90, "summer": 0.70, "fall": 1.20, "winter": 0.95}
    },
    SpeciesType.BEAR: {
        "name_fr": "Ours noir",
        "weights": {"food": 0.40, "cover": 0.25, "vegetation": 0.20, "water": 0.10, "terrain": 0.05},
        "optimal_temp_range": (10, 25),
        "activity_peaks": [6, 7, 8, 17, 18, 19],
        "seasonal_factors": {"spring": 0.95, "summer": 1.00, "fall": 1.15, "winter": 0.10}
    },
    SpeciesType.ELK: {
        "name_fr": "Wapiti",
        "weights": {"vegetation": 0.35, "food": 0.25, "terrain": 0.20, "water": 0.15, "cover": 0.05},
        "optimal_temp_range": (0, 18),
        "activity_peaks": [5, 6, 7, 17, 18],
        "seasonal_factors": {"spring": 0.85, "summer": 0.80, "fall": 1.15, "winter": 0.95}
    },
    SpeciesType.WATERFOWL: {
        "name_fr": "Sauvagine",
        "weights": {"water": 0.50, "vegetation": 0.20, "food": 0.20, "cover": 0.05, "terrain": 0.05},
        "optimal_temp_range": (5, 20),
        "activity_peaks": [6, 7, 8, 16, 17, 18],
        "seasonal_factors": {"spring": 1.10, "summer": 0.70, "fall": 1.15, "winter": 0.50}
    },
}


# =============================================================================
# REQUEST MODEL
# =============================================================================

class TerritoryAnalysisRequest(BaseModel):
    """Requête d'analyse de territoire BIONIC"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude du centre")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude du centre")
    radius_km: float = Field(default=5.0, gt=0, le=50, description="Rayon d'analyse en km")
    
    modules: List[str] = Field(
        default=["vegetation", "hydrology", "terrain", "food", "cover", "weather"],
        description="Modules à exécuter"
    )
    species: List[str] = Field(
        default=["deer"],
        description="Espèces à analyser"
    )
    
    include_ai_predictions: bool = Field(default=True, description="Inclure les prédictions IA")
    include_temporal: bool = Field(default=False, description="Inclure l'analyse temporelle")


# =============================================================================
# GEOSPATIAL SERVICE
# =============================================================================

class GeospatialBundle(BaseModel):
    """Bundle de données géospatiales"""
    weather: Dict[str, Any] = {}
    terrain: Dict[str, Any] = {}
    vegetation: Dict[str, Any] = {}
    hydrology: Dict[str, Any] = {}
    ndvi: Optional[float] = None
    ndwi: Optional[float] = None
    elevation: Optional[float] = None
    slope: Optional[float] = None
    land_cover: Optional[str] = None
    data_sources: List[str] = []


async def get_geospatial_service(lat: float, lon: float, radius_km: float) -> GeospatialBundle:
    """
    Récupère un bundle complet de données géospatiales.
    Appelle les différents services BIONIC pour collecter les données.
    """
    bundle = GeospatialBundle()
    
    # Calculer le bounding box
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * abs(math.cos(math.radians(lat))))
    bbox = {
        "min_lat": lat - delta_lat,
        "max_lat": lat + delta_lat,
        "min_lon": lon - delta_lon,
        "max_lon": lon + delta_lon
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Météo
        try:
            response = await client.get(f"{API_BASE}/api/weather", params={"lat": lat, "lon": lon})
            if response.status_code == 200:
                bundle.weather = response.json()
                bundle.data_sources.append("OpenWeatherMap")
        except Exception as e:
            print(f"Weather fetch error: {e}")
        
        # Hydrologie (HydroEngine)
        try:
            response = await client.post(
                f"{API_BASE}/api/bionic/hydro/analyze",
                json={"bbox": bbox, "target_species": "deer"}
            )
            if response.status_code == 200:
                bundle.hydrology = response.json()
                bundle.data_sources.append("HydroEngine-GRHQ")
        except Exception as e:
            print(f"Hydrology fetch error: {e}")
        
        # Végétation (SentinelEngine)
        try:
            response = await client.post(
                f"{API_BASE}/api/bionic/sentinel/analyze/territory",
                json={"bbox": bbox, "target_species": "deer"}
            )
            if response.status_code == 200:
                data = response.json()
                bundle.vegetation = data
                bundle.ndvi = data.get("ndvi", 0.5)
                bundle.data_sources.append("SentinelEngine-S2")
        except Exception as e:
            print(f"Vegetation fetch error: {e}")
        
        # Géologie (SigeomEngine)
        try:
            response = await client.post(
                f"{API_BASE}/api/bionic/sigeom/analyze",
                json={"bbox": bbox}
            )
            if response.status_code == 200:
                bundle.terrain = response.json()
                bundle.data_sources.append("SigeomEngine-MERN")
        except Exception as e:
            print(f"Terrain fetch error: {e}")
    
    # Valeurs par défaut si non récupérées
    if bundle.ndvi is None:
        bundle.ndvi = 0.55  # Valeur moyenne
    if bundle.ndwi is None:
        bundle.ndwi = 0.20
    if bundle.elevation is None:
        bundle.elevation = 200  # Altitude moyenne Québec sud
    if bundle.slope is None:
        bundle.slope = 5  # Pente légère
    if bundle.land_cover is None:
        bundle.land_cover = "mixed_forest"
    
    return bundle


# =============================================================================
# MODULE EXECUTION
# =============================================================================

def get_score_rating(score: float) -> str:
    """Convertit un score en rating A/B/C/D/E"""
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    else:
        return "E"


def execute_vegetation_module(bundle: GeospatialBundle) -> ModuleResult:
    """Exécute le module d'analyse de végétation"""
    config = MODULE_CONFIGS[ModuleType.VEGETATION]
    
    # Calculer les facteurs
    ndvi_score = min(100, max(0, (bundle.ndvi + 1) * 50)) if bundle.ndvi else 50
    forest_cover = bundle.vegetation.get("forest_coverage", 60)
    canopy_density = bundle.vegetation.get("canopy_density", 50)
    understory = bundle.vegetation.get("understory_quality", 50)
    
    # Score pondéré
    factors = {
        "ndvi": ndvi_score,
        "forest_cover": forest_cover,
        "canopy_density": canopy_density,
        "understory": understory
    }
    score = sum(factors.values()) / len(factors)
    
    # Recommandations
    recommendations = []
    if ndvi_score >= 70:
        recommendations.append("Végétation dense - Excellent couvert pour le gibier")
    elif ndvi_score < 40:
        recommendations.append("Végétation clairsemée - Chercher des zones plus denses")
    
    return ModuleResult(
        module_type=ModuleType.VEGETATION,
        module_name=config["name"],
        score=round(score, 2),
        rating=get_score_rating(score),
        details=bundle.vegetation,
        indicators=factors,
        recommendations=recommendations
    )


def execute_hydrology_module(bundle: GeospatialBundle) -> ModuleResult:
    """Exécute le module d'analyse hydrologique"""
    config = MODULE_CONFIGS[ModuleType.HYDROLOGY]
    
    hydro_data = bundle.hydrology.get("analysis", {})
    
    # Calculer les facteurs
    water_proximity = hydro_data.get("water_proximity_score", 50)
    wetland_coverage = hydro_data.get("wetland_coverage", 30)
    stream_density = hydro_data.get("stream_density_score", 50)
    water_quality = hydro_data.get("water_quality", 70)
    
    factors = {
        "water_proximity": water_proximity,
        "wetland_coverage": wetland_coverage,
        "stream_density": stream_density,
        "water_quality": water_quality
    }
    score = sum(factors.values()) / len(factors)
    
    # Recommandations
    recommendations = []
    if water_proximity >= 70:
        recommendations.append("Bonne proximité aux sources d'eau")
    if wetland_coverage >= 40:
        recommendations.append("Zones humides présentes - Idéal pour orignal et sauvagine")
    if score < 40:
        recommendations.append("Faible présence d'eau - Les animaux peuvent être moins présents")
    
    return ModuleResult(
        module_type=ModuleType.HYDROLOGY,
        module_name=config["name"],
        score=round(score, 2),
        rating=get_score_rating(score),
        details=bundle.hydrology,
        indicators=factors,
        recommendations=recommendations
    )


def execute_terrain_module(bundle: GeospatialBundle) -> ModuleResult:
    """Exécute le module d'analyse du terrain"""
    config = MODULE_CONFIGS[ModuleType.TERRAIN]
    
    terrain_data = bundle.terrain
    
    # Calculer les facteurs basés sur l'élévation et la pente
    elevation = bundle.elevation or 200
    slope = bundle.slope or 5
    
    # Score d'élévation (optimal: 100-400m pour le cerf)
    if 100 <= elevation <= 400:
        elevation_score = 80
    elif 50 <= elevation < 100 or 400 < elevation <= 600:
        elevation_score = 65
    else:
        elevation_score = 50
    
    # Score de pente (optimal: 5-15 degrés)
    if 5 <= slope <= 15:
        slope_score = 85
    elif slope < 5:
        slope_score = 70  # Plat
    elif slope <= 25:
        slope_score = 60
    else:
        slope_score = 40  # Trop abrupt
    
    factors = {
        "elevation": elevation_score,
        "slope": slope_score,
        "aspect": 65,  # Default
        "ruggedness": terrain_data.get("ruggedness_score", 60)
    }
    score = sum(factors.values()) / len(factors)
    
    recommendations = []
    if slope_score >= 70:
        recommendations.append("Terrain favorable aux déplacements du gibier")
    if elevation_score >= 70:
        recommendations.append("Altitude optimale pour la chasse")
    
    return ModuleResult(
        module_type=ModuleType.TERRAIN,
        module_name=config["name"],
        score=round(score, 2),
        rating=get_score_rating(score),
        details=terrain_data,
        indicators=factors,
        recommendations=recommendations
    )


def execute_food_module(bundle: GeospatialBundle) -> ModuleResult:
    """Exécute le module d'analyse des sources alimentaires"""
    config = MODULE_CONFIGS[ModuleType.FOOD]
    
    # Estimer la disponibilité de nourriture
    ndvi = bundle.ndvi or 0.5
    season = get_current_season()
    
    # Score basé sur NDVI et saison
    base_food_score = min(100, max(0, (ndvi + 0.5) * 60))
    
    seasonal_multipliers = {
        "spring": 0.85,  # Peu de nourriture après l'hiver
        "summer": 1.10,  # Abondance
        "fall": 1.20,    # Glands, fruits
        "winter": 0.60   # Rare
    }
    
    mast_score = base_food_score * seasonal_multipliers.get(season, 1.0)
    browse_score = min(100, bundle.vegetation.get("browse_quality", 60))
    
    factors = {
        "mast_availability": min(100, mast_score),
        "browse_quality": browse_score,
        "agriculture_proximity": 50,  # Default
        "seasonal_food": min(100, base_food_score * seasonal_multipliers.get(season, 1.0))
    }
    score = sum(factors.values()) / len(factors)
    
    recommendations = []
    if season == "fall":
        recommendations.append("Saison des glands et fruits - Période d'alimentation intense")
    if score >= 70:
        recommendations.append("Bonne disponibilité de sources alimentaires")
    elif score < 40:
        recommendations.append("Nourriture limitée - Le gibier peut être dispersé")
    
    return ModuleResult(
        module_type=ModuleType.FOOD,
        module_name=config["name"],
        score=round(score, 2),
        rating=get_score_rating(score),
        details={"season": season, "ndvi": ndvi},
        indicators=factors,
        recommendations=recommendations
    )


def execute_cover_module(bundle: GeospatialBundle) -> ModuleResult:
    """Exécute le module d'analyse du couvert"""
    config = MODULE_CONFIGS[ModuleType.COVER]
    
    # Estimer la qualité du couvert
    forest_cover = bundle.vegetation.get("forest_coverage", 60)
    canopy = bundle.vegetation.get("canopy_density", 50)
    
    thermal_cover = min(100, forest_cover * 1.1)
    escape_cover = min(100, canopy * 0.9)
    bedding_score = min(100, (forest_cover + canopy) / 2 * 1.05)
    edge_habitat = min(100, 100 - abs(forest_cover - 50))  # Optimal near 50% forest
    
    factors = {
        "thermal_cover": thermal_cover,
        "escape_cover": escape_cover,
        "bedding_areas": bedding_score,
        "edge_habitat": edge_habitat
    }
    score = sum(factors.values()) / len(factors)
    
    recommendations = []
    if thermal_cover >= 70:
        recommendations.append("Bon couvert thermique pour les périodes froides")
    if edge_habitat >= 65:
        recommendations.append("Habitat de lisière favorable - Transition forêt/ouverture")
    
    return ModuleResult(
        module_type=ModuleType.COVER,
        module_name=config["name"],
        score=round(score, 2),
        rating=get_score_rating(score),
        details=bundle.vegetation,
        indicators=factors,
        recommendations=recommendations
    )


def execute_weather_module(bundle: GeospatialBundle) -> ModuleResult:
    """Exécute le module d'analyse météo"""
    config = MODULE_CONFIGS[ModuleType.WEATHER]
    
    weather = bundle.weather
    
    # Extraire les données météo
    temp = weather.get("main", {}).get("temp", 15)
    humidity = weather.get("main", {}).get("humidity", 60)
    wind = weather.get("wind", {}).get("speed", 5)
    pressure = weather.get("main", {}).get("pressure", 1013)
    
    # Score de température (optimal: 5-15°C pour la chasse)
    if 5 <= temp <= 15:
        temp_score = 90
    elif 0 <= temp < 5 or 15 < temp <= 20:
        temp_score = 75
    elif -10 <= temp < 0 or 20 < temp <= 25:
        temp_score = 55
    else:
        temp_score = 35
    
    # Score de vent (optimal: faible)
    if wind < 10:
        wind_score = 90
    elif wind < 20:
        wind_score = 70
    elif wind < 30:
        wind_score = 50
    else:
        wind_score = 30
    
    # Score de pression (haute pression = meilleur)
    if pressure >= 1020:
        pressure_score = 85
    elif pressure >= 1010:
        pressure_score = 70
    else:
        pressure_score = 55
    
    # Score d'humidité
    if 40 <= humidity <= 70:
        humidity_score = 80
    else:
        humidity_score = 60
    
    factors = {
        "temperature": temp_score,
        "wind": wind_score,
        "pressure": pressure_score,
        "humidity": humidity_score
    }
    score = sum(factors.values()) / len(factors)
    
    # Pénalité pour conditions extrêmes
    conditions = weather.get("weather", [{}])
    if conditions:
        main_condition = conditions[0].get("main", "").lower()
        if main_condition in ["thunderstorm", "storm"]:
            score *= 0.4
        elif main_condition in ["rain", "drizzle"]:
            score *= 0.75
        elif main_condition in ["snow"]:
            score *= 0.85
    
    recommendations = []
    if score >= 70:
        recommendations.append("Conditions météo favorables pour la chasse")
    if wind_score >= 80:
        recommendations.append("Vent faible - Idéal pour l'approche")
    if temp_score >= 80:
        recommendations.append("Température optimale - Le gibier sera actif")
    if score < 50:
        recommendations.append("Conditions météo défavorables - Considérer de reporter")
    
    return ModuleResult(
        module_type=ModuleType.WEATHER,
        module_name=config["name"],
        score=round(min(100, score), 2),
        rating=get_score_rating(score),
        details=weather,
        indicators=factors,
        recommendations=recommendations
    )


def execute_module(module_type: ModuleType, bundle: GeospatialBundle) -> ModuleResult:
    """Exécute un module spécifique"""
    executors = {
        ModuleType.VEGETATION: execute_vegetation_module,
        ModuleType.HYDROLOGY: execute_hydrology_module,
        ModuleType.TERRAIN: execute_terrain_module,
        ModuleType.FOOD: execute_food_module,
        ModuleType.COVER: execute_cover_module,
        ModuleType.WEATHER: execute_weather_module,
    }
    
    executor = executors.get(module_type)
    if executor:
        return executor(bundle)
    
    # Module par défaut
    return ModuleResult(
        module_type=module_type,
        module_name=MODULE_CONFIGS.get(module_type, {}).get("name", str(module_type)),
        score=50.0,
        rating="C",
        details={},
        indicators={},
        recommendations=[]
    )


# =============================================================================
# SPECIES ANALYSIS
# =============================================================================

def analyze_species(species: SpeciesType, modules: List[ModuleResult], bundle: GeospatialBundle) -> SpeciesResult:
    """Analyse un territoire pour une espèce spécifique"""
    config = SPECIES_CONFIGS.get(species, SPECIES_CONFIGS[SpeciesType.DEER])
    weights = config["weights"]
    
    # Calculer les scores d'habitat
    def get_module_score(module_type: ModuleType) -> float:
        for m in modules:
            if m.module_type == module_type:
                return m.score
        return 50.0
    
    veg_score = get_module_score(ModuleType.VEGETATION)
    food_score = get_module_score(ModuleType.FOOD)
    cover_score = get_module_score(ModuleType.COVER)
    water_score = get_module_score(ModuleType.HYDROLOGY)
    terrain_score = get_module_score(ModuleType.TERRAIN)
    
    # Habitat suitability
    habitat = HabitatSuitability(
        food_score=food_score,
        water_score=water_score,
        cover_score=cover_score,
        terrain_score=terrain_score,
        disturbance_score=30  # Assume low disturbance
    )
    
    # Score pondéré selon l'espèce
    weighted_score = (
        veg_score * weights.get("vegetation", 0.25) +
        food_score * weights.get("food", 0.25) +
        cover_score * weights.get("cover", 0.20) +
        water_score * weights.get("water", 0.15) +
        terrain_score * weights.get("terrain", 0.15)
    )
    
    # Ajustement saisonnier
    season = get_current_season()
    seasonal_factor = config["seasonal_factors"].get(season, 1.0)
    final_score = min(100, weighted_score * seasonal_factor)
    
    # Déterminer la densité estimée
    if final_score >= 75:
        density = "high"
    elif final_score >= 55:
        density = "medium"
    else:
        density = "low"
    
    # Recommandations spécifiques
    recommendations = []
    if final_score >= 70:
        recommendations.append(f"Zone favorable pour {config['name_fr']}")
    elif final_score >= 50:
        recommendations.append(f"Potentiel modéré pour {config['name_fr']}")
    else:
        recommendations.append(f"Zone peu propice pour {config['name_fr']}")
    
    if season == "fall" and species in [SpeciesType.DEER, SpeciesType.MOOSE, SpeciesType.ELK]:
        recommendations.append("Période de rut - Utiliser des attractants olfactifs ou appels")
    
    if species == SpeciesType.BEAR and season == "fall":
        recommendations.append("Période d'hyperphagie - Chercher près des sources de nourriture")
    
    # Meilleure période de chasse
    if species in [SpeciesType.DEER, SpeciesType.MOOSE]:
        best_period = "Automne (rut: octobre-novembre)"
    elif species == SpeciesType.BEAR:
        best_period = "Printemps et automne"
    else:
        best_period = "Selon la réglementation"
    
    return SpeciesResult(
        species=species,
        species_name_fr=config["name_fr"],
        suitability_score=round(final_score, 2),
        rating=get_score_rating(final_score),
        habitat_suitability=habitat,
        estimated_density=density,
        recommendations=recommendations,
        best_hunting_period=best_period
    )


# =============================================================================
# AI PREDICTIONS
# =============================================================================

def generate_ai_predictions(modules: List[ModuleResult], species: List[SpeciesResult], bundle: GeospatialBundle) -> PredictionResult:
    """Génère les prédictions IA pour 24h, 72h et 7 jours"""
    
    # Score de base
    if modules:
        base_score = sum(m.score for m in modules) / len(modules)
    else:
        base_score = 50.0
    
    # Ajuster selon la météo prévue (simulation)
    weather = bundle.weather
    temp = weather.get("main", {}).get("temp", 15)
    
    # Facteurs d'ajustement temporel
    now = datetime.now(timezone.utc)
    
    # Prédiction 24h
    pred_24h = base_score * 1.02  # Légère amélioration attendue
    if 5 <= temp <= 15:
        pred_24h *= 1.05
    
    # Prédiction 72h
    pred_72h = base_score * 0.98  # Légère dégradation
    
    # Prédiction 7j
    pred_7d = base_score * 0.95  # Incertitude croissante
    
    predictions = [
        SinglePrediction(
            horizon=PredictionHorizon.H24,
            timestamp=now + timedelta(hours=24),
            predicted_score=round(min(100, max(0, pred_24h)), 2),
            confidence=0.85,
            key_factors={"weather": 0.35, "activity_cycle": 0.40, "seasonal": 0.25}
        ),
        SinglePrediction(
            horizon=PredictionHorizon.H72,
            timestamp=now + timedelta(hours=72),
            predicted_score=round(min(100, max(0, pred_72h)), 2),
            confidence=0.70,
            key_factors={"weather": 0.45, "activity_cycle": 0.30, "seasonal": 0.25}
        ),
        SinglePrediction(
            horizon=PredictionHorizon.D7,
            timestamp=now + timedelta(days=7),
            predicted_score=round(min(100, max(0, pred_7d)), 2),
            confidence=0.55,
            key_factors={"weather": 0.50, "activity_cycle": 0.20, "seasonal": 0.30}
        ),
    ]
    
    # Déterminer la tendance
    if pred_24h > base_score * 1.05:
        trend = "improving"
    elif pred_24h < base_score * 0.95:
        trend = "declining"
    else:
        trend = "stable"
    
    # Meilleure fenêtre de chasse
    best_window = {
        "start": "06:00",
        "end": "09:00",
        "secondary_start": "16:30",
        "secondary_end": "19:00",
        "confidence": 0.80,
        "factors": ["dawn_activity", "temperature_optimal", "low_disturbance"]
    }
    
    # Alertes
    alerts = []
    if temp > 25:
        alerts.append("Température élevée prévue - Activité réduite en journée")
    if weather.get("weather", [{}])[0].get("main", "").lower() in ["rain", "thunderstorm"]:
        alerts.append("Précipitations prévues - Ajuster les horaires")
    
    return PredictionResult(
        model_name="BIONIC_PREDICTOR",
        model_version="1.0",
        predictions=predictions,
        trend=trend,
        best_window=best_window,
        alerts=alerts,
        generated_at=now
    )


# =============================================================================
# TEMPORAL ANALYSIS
# =============================================================================

def generate_temporal_analysis(bundle: GeospatialBundle) -> TemporalResult:
    """Génère l'analyse temporelle (NDVI, NDWI, neige, phénologie)"""
    now = datetime.now(timezone.utc)
    season = get_current_season()
    
    # Générer une série NDVI simulée (30 jours)
    ndvi_dates = [now - timedelta(days=30-i) for i in range(31)]
    base_ndvi = bundle.ndvi or 0.5
    ndvi_values = [
        round(base_ndvi + 0.1 * math.sin(i * 0.2) + 0.02 * (i - 15), 3)
        for i in range(31)
    ]
    
    ndvi_series = NDVITimeSeries(
        dates=ndvi_dates,
        values=ndvi_values,
        trend="stable" if season in ["summer", "fall"] else "declining",
        anomalies=[]
    )
    
    # Série NDWI simulée
    base_ndwi = bundle.ndwi or 0.2
    ndwi_values = [
        round(base_ndwi + 0.05 * math.cos(i * 0.15), 3)
        for i in range(31)
    ]
    
    ndwi_series = NDVITimeSeries(
        dates=ndvi_dates,
        values=ndwi_values,
        trend="stable",
        anomalies=[]
    )
    
    # Analyse neige (seulement en hiver/début printemps)
    snow_analysis = None
    if season == "winter":
        snow_analysis = SnowAnalysis(
            snow_coverage_percent=65.0,
            snow_depth_cm=25.0,
            days_since_last_snow=3,
            melting_status="stable"
        )
    elif season == "spring":
        snow_analysis = SnowAnalysis(
            snow_coverage_percent=20.0,
            snow_depth_cm=5.0,
            days_since_last_snow=10,
            melting_status="melting"
        )
    
    # Phénologie
    phenology_phases = {
        "spring": "green_up",
        "summer": "maturity",
        "fall": "senescence",
        "winter": "dormancy"
    }
    
    phenology = PhenologyData(
        current_phase=phenology_phases.get(season, "maturity"),
        days_to_next_phase=30,
        green_up_date=datetime(now.year, 4, 15, tzinfo=timezone.utc),
        peak_green_date=datetime(now.year, 7, 15, tzinfo=timezone.utc),
        senescence_date=datetime(now.year, 10, 1, tzinfo=timezone.utc)
    )
    
    return TemporalResult(
        analysis_period_start=now - timedelta(days=30),
        analysis_period_end=now,
        current_season=season,
        ndvi_series=ndvi_series,
        ndwi_series=ndwi_series,
        snow_analysis=snow_analysis,
        phenology=phenology,
        compared_to_average="normal",
        year_over_year_change=2.5,
        detected_events=[]
    )


# =============================================================================
# HELPERS
# =============================================================================

def get_current_season() -> str:
    """Détermine la saison actuelle au Québec"""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def generate_geojson(lat: float, lon: float, radius_km: float) -> Dict[str, Any]:
    """Génère le GeoJSON pour la zone d'analyse"""
    # Générer un cercle approximé (32 points)
    points = []
    for i in range(32):
        angle = (i / 32) * 2 * math.pi
        dlat = (radius_km / 111.0) * math.cos(angle)
        dlon = (radius_km / (111.0 * abs(math.cos(math.radians(lat))))) * math.sin(angle)
        points.append([lon + dlon, lat + dlat])
    points.append(points[0])  # Fermer le polygone
    
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Zone d'analyse BIONIC",
                    "radius_km": radius_km,
                    "type": "analysis_area"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [points]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Centre",
                    "type": "center_point"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }
        ]
    }


def consolidate_recommendations(
    modules: List[ModuleResult],
    species: List[SpeciesResult],
    predictions: Optional[PredictionResult],
    temporal: Optional[TemporalResult]
) -> List[str]:
    """Consolide et déduplique toutes les recommandations"""
    all_recs = []
    
    # Recommandations des modules
    for module in modules:
        all_recs.extend(module.recommendations)
    
    # Recommandations des espèces
    for sp in species:
        all_recs.extend(sp.recommendations)
    
    # Alertes des prédictions
    if predictions:
        all_recs.extend(predictions.alerts)
    
    # Dédupliquer
    unique_recs = list(dict.fromkeys(all_recs))
    
    # Trier par importance (mots-clés)
    priority_keywords = ["favorable", "idéal", "optimal", "excellent", "bon"]
    warning_keywords = ["défavorable", "faible", "limité", "reporter", "éviter"]
    
    def sort_key(rec: str) -> int:
        rec_lower = rec.lower()
        for kw in priority_keywords:
            if kw in rec_lower:
                return 0
        for kw in warning_keywords:
            if kw in rec_lower:
                return 2
        return 1
    
    return sorted(unique_recs, key=sort_key)


def get_db():
    """Obtient la connexion MongoDB"""
    try:
        client = MongoClient(MONGO_URL)
        return client[DB_NAME]
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None


# =============================================================================
# MAIN ENDPOINT
# =============================================================================

@bionic_engine_router.post("/analyze", response_model=TerritoryFullAnalysis)
async def analyze_territory(request: TerritoryAnalysisRequest):
    """
    Analyse complète d'un territoire BIONIC™.
    
    Orchestre tous les modules, modèles fauniques, prédictions IA
    et analyse temporelle pour produire une analyse consolidée.
    """
    start_time = datetime.now(timezone.utc)
    territory_id = f"bionic_{uuid.uuid4().hex[:12]}"
    
    # a. Récupérer le bundle géospatial
    bundle = await get_geospatial_service(
        request.latitude,
        request.longitude,
        request.radius_km
    )
    
    # b. Exécuter les modules demandés
    modules: List[ModuleResult] = []
    for module_name in request.modules:
        try:
            module_type = ModuleType(module_name.lower())
            result = execute_module(module_type, bundle)
            modules.append(result)
        except ValueError:
            print(f"Module inconnu: {module_name}")
    
    # c. Analyser les espèces demandées
    species_results: List[SpeciesResult] = []
    for species_name in request.species:
        try:
            species_type = SpeciesType(species_name.lower())
            result = analyze_species(species_type, modules, bundle)
            species_results.append(result)
        except ValueError:
            print(f"Espèce inconnue: {species_name}")
    
    # d. Générer les prédictions IA
    predictions = None
    if request.include_ai_predictions:
        predictions = generate_ai_predictions(modules, species_results, bundle)
    
    # e. Générer l'analyse temporelle
    temporal = None
    if request.include_temporal:
        temporal = generate_temporal_analysis(bundle)
    
    # f. Calculer le score global
    if modules:
        # Moyenne pondérée des modules
        weighted_sum = 0
        weight_total = 0
        for module in modules:
            config = MODULE_CONFIGS.get(module.module_type, {"weight": 0.1})
            weight = config.get("weight", 0.1)
            weighted_sum += module.score * weight
            weight_total += weight
        
        global_score = weighted_sum / weight_total if weight_total > 0 else 50.0
        
        # Ajuster selon les espèces (bonus si bon score espèce principale)
        if species_results:
            best_species_score = max(s.suitability_score for s in species_results)
            global_score = (global_score * 0.7) + (best_species_score * 0.3)
    else:
        global_score = 50.0
    
    global_score = round(global_score, 2)
    global_rating = get_score_rating(global_score)
    
    # g. Consolider les recommandations
    recommendations = consolidate_recommendations(modules, species_results, predictions, temporal)
    
    # h. Construire le GeoJSON
    geojson = generate_geojson(request.latitude, request.longitude, request.radius_km)
    
    # i. Construire l'analyse complète
    analysis = TerritoryFullAnalysis(
        territory_id=territory_id,
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
        created_at=start_time,
        updated_at=datetime.now(timezone.utc),
        data_sources=bundle.data_sources,
        modules=modules,
        species=species_results,
        predictions=predictions,
        temporal=temporal,
        global_score=global_score,
        global_rating=global_rating,
        recommendations=recommendations,
        geojson=geojson,
        engine_version="BIONIC_CORE 1.0"
    )
    
    # j. Sauvegarder dans MongoDB
    db = get_db()
    if db is not None:
        try:
            collection = db["territory_analyses"]
            # Créer l'index unique si nécessaire
            collection.create_index("territory_id", unique=True)
            
            # Convertir en dict pour MongoDB
            doc = analysis.model_dump(mode="json")
            collection.insert_one(doc)
            print(f"Analysis saved: {territory_id}")
        except DuplicateKeyError:
            print(f"Analysis already exists: {territory_id}")
        except Exception as e:
            print(f"MongoDB save error: {e}")
    
    # k. Retourner l'analyse
    return analysis


# =============================================================================
# ADDITIONAL ENDPOINTS
# =============================================================================

@bionic_engine_router.get("/status")
async def get_engine_status():
    """Statut du moteur BIONIC"""
    return {
        "status": "active",
        "engine": "BIONIC_ENGINE",
        "version": "1.0",
        "modules": list(MODULE_CONFIGS.keys()),
        "species": list(SPECIES_CONFIGS.keys()),
        "capabilities": {
            "ai_predictions": True,
            "temporal_analysis": True,
            "geojson_output": True,
            "mongodb_persistence": True
        }
    }


@bionic_engine_router.get("/analyses/{territory_id}")
async def get_analysis(territory_id: str):
    """Récupère une analyse sauvegardée"""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    doc = db["territory_analyses"].find_one(
        {"territory_id": territory_id},
        {"_id": 0}
    )
    
    if not doc:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return doc


@bionic_engine_router.get("/analyses")
async def list_analyses(limit: int = 10, skip: int = 0):
    """Liste les analyses récentes"""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    cursor = db["territory_analyses"].find(
        {},
        {"_id": 0, "territory_id": 1, "latitude": 1, "longitude": 1, 
         "global_score": 1, "global_rating": 1, "created_at": 1}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    return {"analyses": list(cursor), "limit": limit, "skip": skip}
