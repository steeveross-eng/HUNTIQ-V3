"""
BIONIC™ Territory Analysis Engine - API Router
===============================================
Router FastAPI léger qui délègue à l'orchestrateur BIONIC™.

Ce fichier contient UNIQUEMENT:
- Définitions des endpoints FastAPI
- Validation des requêtes
- Conversion des réponses
- Stockage MongoDB

La logique métier est déléguée aux moteurs dans /app/bionic/engines/core/

Endpoints:
- /api/bionic/modules - Liste des modules
- /api/bionic/species - Liste des espèces
- /api/bionic/analyze - Analyse complète
- /api/bionic/stats - Statistiques globales
- /api/bionic/geospatial/* - Données géospatiales

Version: 2.0 (Refactorisé)
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone, timedelta
import os
import logging
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add bionic engines to path
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

# Import orchestrator and engines from core
from core import (
    bionic_orchestrator,
    module_runner,
    species_engine,
    prediction_engine,
    temporal_engine,
    ModuleType,
    SpeciesType,
    SeasonType,
    get_current_season,
    get_rating,
)

# Import geospatial data service
from geospatial_data import (
    get_geospatial_service,
    weather_to_bionic_factors,
    terrain_to_bionic_factors,
    vegetation_to_bionic_factors,
    interpret_vegetation,
    interpret_ndvi,
    interpret_ndwi,
    GeospatialBundle,
)

router = APIRouter(prefix="/api/bionic", tags=["BIONIC™ Territory Engine"])

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")

client = None
db = None


async def get_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    return db


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class TerritoryAnalysisRequest(BaseModel):
    territory_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, ge=0.1, le=50)
    modules: List[ModuleType] = Field(default_factory=lambda: list(ModuleType))
    species: List[SpeciesType] = Field(default_factory=lambda: [SpeciesType.MOOSE, SpeciesType.DEER, SpeciesType.BEAR])
    include_ai_predictions: bool = True
    include_temporal: bool = True


class BionicGlobalStats(BaseModel):
    """Statistiques globales BIONIC_CORE pour les compteurs animés"""
    total_analyses: int = 0
    total_species_models: int = 0
    total_zones_generated: int = 0
    total_waypoints: int = 0
    total_favorites: int = 0
    average_global_score: float = 0.0
    top_species_frequency: Dict[str, int] = {}
    modules_usage: Dict[str, int] = {}
    rating_distribution: Dict[str, int] = {}
    engine_version: str = "BIONIC_CORE 2.0"
    last_update: Optional[datetime] = None


# ============================================
# GEOSPATIAL DATA CACHE
# ============================================

_geospatial_cache: Dict[str, GeospatialBundle] = {}


async def get_real_geospatial_data(lat: float, lon: float) -> GeospatialBundle:
    """Fetch real geospatial data from external APIs with caching"""
    cache_key = f"{round(lat, 4)}_{round(lon, 4)}"
    
    if cache_key in _geospatial_cache:
        cached = _geospatial_cache[cache_key]
        cache_time = datetime.fromisoformat(cached.fetch_timestamp.replace('Z', '+00:00'))
        if datetime.now(timezone.utc) - cache_time < timedelta(minutes=5):
            return cached
    
    try:
        service = await get_geospatial_service()
        data = await service.get_complete_data(lat, lon)
        _geospatial_cache[cache_key] = data
        return data
    except Exception as e:
        logger.error(f"Error fetching geospatial data: {e}")
        return GeospatialBundle(
            latitude=lat,
            longitude=lon,
            fetch_timestamp=datetime.now(timezone.utc).isoformat(),
            data_quality="failed",
            errors=[str(e)]
        )


# ============================================
# MODULE ENDPOINTS
# ============================================

@router.get("/modules")
async def list_modules():
    """List all available analysis modules"""
    modules = module_runner.get_available_modules()
    return {"success": True, "modules": modules, "total": len(modules)}


@router.get("/modules/{module_id}")
async def get_module_info(module_id: str):
    """Get detailed information about a specific module"""
    module_info = module_runner.get_module_info(module_id)
    if module_info is None:
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
    return {"success": True, "module": module_info}


@router.post("/modules/{module_id}/run")
async def run_module(
    module_id: str,
    territory_id: str,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    """Run a specific module analysis"""
    try:
        module_type = ModuleType(module_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
    
    geospatial_data = await get_real_geospatial_data(latitude, longitude)
    result = await module_runner.calculate_score(
        module_type, latitude, longitude, territory_id, geospatial_data
    )
    
    # Store result in database
    database = await get_db()
    await database.module_results.insert_one({
        "territory_id": territory_id,
        "module": module_id,
        "latitude": latitude,
        "longitude": longitude,
        "result": result,
        "created_at": datetime.now(timezone.utc)
    })
    
    return {"success": True, "result": result}


# ============================================
# SPECIES ENDPOINTS
# ============================================

@router.get("/species")
async def list_species():
    """List all available wildlife models"""
    species_list = species_engine.get_available_species()
    return {"success": True, "species": species_list, "total": len(species_list)}


@router.get("/species/{species_id}")
async def get_species_info(species_id: str):
    """Get detailed information about a species model"""
    species_info = species_engine.get_species_info(species_id)
    if species_info is None:
        raise HTTPException(status_code=404, detail=f"Species '{species_id}' not found")
    return {"success": True, "species": species_info}


@router.post("/species/{species_id}/score")
async def calculate_species_habitat_score(
    species_id: str,
    territory_id: str,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    """Calculate habitat score for a specific species"""
    try:
        species_type = SpeciesType(species_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Species '{species_id}' not found")
    
    # Calculate all module scores first
    geospatial_data = await get_real_geospatial_data(latitude, longitude)
    module_results = await module_runner.calculate_all_modules(
        latitude, longitude, territory_id, list(ModuleType), geospatial_data
    )
    module_scores = {m: r.get("score", 50) for m, r in module_results.items()}
    
    # Calculate species score
    species_result = await species_engine.calculate_score(
        species_type, latitude, longitude, module_scores, territory_id
    )
    
    # Store result
    database = await get_db()
    await database.species_scores.insert_one({
        "territory_id": territory_id,
        "species": species_id,
        "latitude": latitude,
        "longitude": longitude,
        "result": species_result,
        "created_at": datetime.now(timezone.utc)
    })
    
    return {"success": True, "result": species_result}


# ============================================
# MAIN ANALYSIS ENDPOINT
# ============================================

@router.post("/analyze")
async def full_territory_analysis(request: TerritoryAnalysisRequest):
    """
    Run complete territory analysis using the BIONIC™ Orchestrator.
    
    This endpoint delegates to the modular engine architecture.
    """
    # Fetch real geospatial data
    geospatial_data = await get_real_geospatial_data(request.latitude, request.longitude)
    
    # Use orchestrator for analysis
    results = await bionic_orchestrator.analyze_territory(
        territory_id=request.territory_id,
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
        modules=request.modules,
        species=request.species,
        include_predictions=request.include_ai_predictions,
        include_temporal=request.include_temporal,
        geospatial_data=geospatial_data
    )
    
    # Store complete analysis
    database = await get_db()
    await database.territory_analyses.insert_one({
        **results,
        "created_at": datetime.now(timezone.utc)
    })
    
    return {"success": True, "analysis": results}


# ============================================
# AI PREDICTION ENDPOINTS
# ============================================

@router.post("/ai/predict")
async def ai_predict(
    territory_id: str,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    species: List[SpeciesType] = Query(default=[SpeciesType.MOOSE, SpeciesType.DEER, SpeciesType.BEAR])
):
    """Generate AI predictions for wildlife activity"""
    geospatial_data = await get_real_geospatial_data(latitude, longitude)
    
    # Calculate module and species scores
    module_results = await module_runner.calculate_all_modules(
        latitude, longitude, territory_id, list(ModuleType), geospatial_data
    )
    module_scores = {m: r.get("score", 50) for m, r in module_results.items()}
    
    species_scores = {}
    for s in species:
        result = await species_engine.calculate_score(
            s, latitude, longitude, module_scores, territory_id
        )
        species_scores[s] = result.get("score", 50)
    
    predictions = await prediction_engine.generate_predictions(
        latitude, longitude, species_scores, territory_id, geospatial_data
    )
    
    return {"success": True, "predictions": predictions}


@router.post("/ai/dynamic-score")
async def dynamic_score(
    territory_id: str,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    weather_temp: float = Query(default=15, description="Current temperature in Celsius"),
    weather_precip: float = Query(default=0, ge=0, le=100, description="Precipitation probability %"),
    time_of_day: Literal["dawn", "morning", "midday", "afternoon", "dusk", "night"] = "morning"
):
    """Calculate dynamic scores adjusted for current conditions"""
    geospatial_data = await get_real_geospatial_data(latitude, longitude)
    
    # Calculate base scores
    module_results = await module_runner.calculate_all_modules(
        latitude, longitude, territory_id, list(ModuleType), geospatial_data
    )
    module_scores = {m: r.get("score", 50) for m, r in module_results.items()}
    
    base_scores = {}
    for species_type in [SpeciesType.MOOSE, SpeciesType.DEER, SpeciesType.BEAR, SpeciesType.TURKEY]:
        result = await species_engine.calculate_score(
            species_type, latitude, longitude, module_scores, territory_id
        )
        base_scores[species_type] = result.get("score", 50)
    
    # Get dynamic scores
    dynamic_results = await prediction_engine.calculate_dynamic_score(
        latitude, longitude, base_scores, weather_temp, weather_precip, time_of_day
    )
    
    return {"success": True, **dynamic_results}


@router.post("/ai/time-series")
async def time_series_analysis(
    territory_id: str,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    """Generate temporal analysis data"""
    temporal = await temporal_engine.generate_analysis(latitude, longitude, territory_id)
    return {"success": True, "temporal_analysis": temporal}


# ============================================
# RESULTS ENDPOINT
# ============================================

@router.get("/results/{territory_id}")
async def get_territory_results(
    territory_id: str,
    limit: int = Query(default=10, le=100)
):
    """Get historical analysis results for a territory"""
    database = await get_db()
    
    results = await database.territory_analyses.find(
        {"territory_id": territory_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {
        "success": True,
        "territory_id": territory_id,
        "results": results,
        "total": len(results)
    }


# ============================================
# STATS ENDPOINT
# ============================================

@router.get("/stats", response_model=BionicGlobalStats)
async def get_bionic_stats():
    """
    Provides animated counters for BIONIC_CORE.
    Aggregates data from multiple MongoDB collections.
    """
    database = await get_db()
    if database is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    stats = BionicGlobalStats()
    
    # a. total_analyses
    try:
        stats.total_analyses = await database.territory_analyses.count_documents({})
    except Exception as e:
        logger.warning(f"Failed to count analyses: {e}")
        stats.total_analyses = 0
    
    # b. total_species_models
    try:
        pipeline_species = [
            {
                "$project": {
                    "species_count": {
                        "$cond": {
                            "if": {"$isArray": "$species"},
                            "then": {"$size": "$species"},
                            "else": {
                                "$cond": {
                                    "if": {"$eq": [{"$type": "$species"}, "object"]},
                                    "then": {"$size": {"$objectToArray": "$species"}},
                                    "else": 0
                                }
                            }
                        }
                    }
                }
            },
            {"$group": {"_id": None, "total": {"$sum": "$species_count"}}}
        ]
        result = await database.territory_analyses.aggregate(pipeline_species).to_list(length=1)
        stats.total_species_models = result[0]["total"] if result else 0
    except Exception:
        stats.total_species_models = 0
    
    # c. total_zones_generated
    try:
        pipeline_zones = [{"$group": {"_id": None, "total": {"$sum": "$zones_generated"}}}]
        result = await database.territory_stats.aggregate(pipeline_zones).to_list(length=1)
        stats.total_zones_generated = result[0]["total"] if result else 0
    except Exception:
        stats.total_zones_generated = 0
    
    # d. total_waypoints
    try:
        stats.total_waypoints = await database.user_waypoints.count_documents({})
        if stats.total_waypoints == 0:
            stats.total_waypoints = await database.waypoints.count_documents({})
    except Exception:
        stats.total_waypoints = 0
    
    # e. total_favorites
    try:
        stats.total_favorites = await database.zone_favorites.count_documents({})
    except Exception:
        stats.total_favorites = 0
    
    # f. average_global_score
    try:
        pipeline_avg = [
            {"$group": {"_id": None, "avg_score": {"$avg": {"$ifNull": ["$overall_score", "$global_score"]}}}}
        ]
        result = await database.territory_analyses.aggregate(pipeline_avg).to_list(length=1)
        stats.average_global_score = round(result[0]["avg_score"], 2) if result and result[0]["avg_score"] else 0.0
    except Exception:
        stats.average_global_score = 0.0
    
    # g. top_species_frequency
    try:
        pipeline_freq = [
            {"$project": {"species_keys": {"$cond": {"if": {"$eq": [{"$type": "$species"}, "object"]}, "then": {"$objectToArray": "$species"}, "else": []}}}},
            {"$unwind": {"path": "$species_keys", "preserveNullAndEmptyArrays": False}},
            {"$group": {"_id": "$species_keys.k", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = await database.territory_analyses.aggregate(pipeline_freq).to_list(length=10)
        stats.top_species_frequency = {item["_id"]: item["count"] for item in results if item["_id"]}
    except Exception:
        stats.top_species_frequency = {}
    
    # h. modules_usage
    try:
        pipeline_modules = [
            {"$project": {"module_keys": {"$cond": {"if": {"$eq": [{"$type": "$modules"}, "object"]}, "then": {"$objectToArray": "$modules"}, "else": []}}}},
            {"$unwind": {"path": "$module_keys", "preserveNullAndEmptyArrays": False}},
            {"$group": {"_id": "$module_keys.k", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        results = await database.territory_analyses.aggregate(pipeline_modules).to_list(length=20)
        stats.modules_usage = {item["_id"]: item["count"] for item in results if item["_id"]}
    except Exception:
        stats.modules_usage = {}
    
    # i. rating_distribution
    try:
        pipeline_rating = [
            {"$group": {"_id": {"$ifNull": ["$overall_rating", "$global_rating"]}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        results = await database.territory_analyses.aggregate(pipeline_rating).to_list(length=10)
        stats.rating_distribution = {str(item["_id"]): item["count"] for item in results if item["_id"]}
    except Exception:
        stats.rating_distribution = {}
    
    # j. last_update
    try:
        latest = await database.territory_analyses.find_one({}, {"timestamp": 1, "created_at": 1}, sort=[("timestamp", -1)])
        if latest:
            ts = latest.get("timestamp") or latest.get("created_at")
            if isinstance(ts, str):
                stats.last_update = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            elif isinstance(ts, datetime):
                stats.last_update = ts
            else:
                stats.last_update = datetime.now(timezone.utc)
        else:
            stats.last_update = datetime.now(timezone.utc)
    except Exception:
        stats.last_update = datetime.now(timezone.utc)
    
    return stats


# ============================================
# GEOSPATIAL ENDPOINTS
# ============================================

@router.get("/geospatial/weather")
async def get_real_weather(
    latitude: float = Query(..., ge=-90, le=90, description="WGS84 Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="WGS84 Longitude")
):
    """Get real-time weather data from Open-Meteo"""
    try:
        service = await get_geospatial_service()
        weather = await service.get_weather_only(latitude, longitude)
        
        if not weather:
            raise HTTPException(status_code=503, detail="Weather service unavailable")
        
        return {
            "success": True,
            "source": "Open-Meteo",
            "location": {"latitude": latitude, "longitude": longitude},
            "current": {
                "temperature": weather.temperature,
                "feels_like": weather.apparent_temperature,
                "humidity": weather.humidity,
                "precipitation": weather.precipitation,
                "precipitation_probability": weather.precipitation_probability,
                "wind_speed": weather.wind_speed,
                "wind_direction": weather.wind_direction,
                "cloud_cover": weather.cloud_cover,
                "pressure": weather.pressure,
                "uv_index": weather.uv_index,
                "is_day": weather.is_day,
                "description": weather.weather_description
            },
            "forecast_24h": weather.forecast_24h,
            "forecast_72h": weather.forecast_72h,
            "forecast_7d": weather.forecast_7d,
            "timestamp": weather.timestamp
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geospatial/terrain")
async def get_terrain_data(
    latitude: float = Query(..., ge=-90, le=90, description="WGS84 Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="WGS84 Longitude")
):
    """Get terrain elevation data from Open-Elevation"""
    try:
        service = await get_geospatial_service()
        terrain = await service.get_terrain_only(latitude, longitude)
        
        if not terrain:
            raise HTTPException(status_code=503, detail="Terrain service unavailable")
        
        from core.helpers import aspect_to_direction
        
        return {
            "success": True,
            "source": "Open-Elevation",
            "location": {"latitude": latitude, "longitude": longitude},
            "terrain": {
                "elevation_m": terrain.elevation,
                "slope_deg": terrain.slope,
                "aspect_deg": terrain.aspect,
                "aspect_direction": aspect_to_direction(terrain.aspect) if terrain.aspect else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching terrain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geospatial/vegetation")
async def get_vegetation_data(
    latitude: float = Query(..., ge=-90, le=90, description="WGS84 Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="WGS84 Longitude")
):
    """Get vegetation indices (NDVI, NDWI) with interpretation"""
    try:
        service = await get_geospatial_service()
        vegetation = await service.get_vegetation_only(latitude, longitude)
        
        if not vegetation:
            raise HTTPException(status_code=503, detail="Vegetation service unavailable")
        
        interpretation = interpret_vegetation(vegetation.ndvi, vegetation.ndwi or 0)
        
        return {
            "success": True,
            "source": vegetation.source,
            "location": {"latitude": latitude, "longitude": longitude},
            "vegetation": {
                "ndvi": vegetation.ndvi,
                "ndwi": vegetation.ndwi,
                "evi": vegetation.evi,
                "lai": vegetation.lai,
                "data_date": vegetation.data_date,
                "quality_flag": vegetation.quality_flag
            },
            "interpretation": {
                "ndvi": {
                    "label": interpretation["ndvi"]["label"],
                    "description": interpretation["ndvi"]["description"],
                    "icon": interpretation["ndvi"]["icon"]
                },
                "ndwi": {
                    "label": interpretation["ndwi"]["label"],
                    "description": interpretation["ndwi"]["description"],
                    "icon": interpretation["ndwi"]["icon"]
                },
                "conclusion": interpretation["conclusion"],
                "summary": interpretation["summary"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vegetation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geospatial/complete")
async def get_complete_geospatial_data(
    latitude: float = Query(..., ge=-90, le=90, description="WGS84 Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="WGS84 Longitude")
):
    """Get all geospatial data in one call"""
    try:
        data = await get_real_geospatial_data(latitude, longitude)
        
        result = {
            "success": True,
            "location": {"latitude": latitude, "longitude": longitude},
            "data_quality": data.data_quality,
            "fetch_timestamp": data.fetch_timestamp,
            "errors": data.errors
        }
        
        if data.weather:
            result["weather"] = {
                "temperature": data.weather.temperature,
                "feels_like": data.weather.apparent_temperature,
                "humidity": data.weather.humidity,
                "wind_speed": data.weather.wind_speed,
                "precipitation_probability": data.weather.precipitation_probability,
                "description": data.weather.weather_description,
                "source": "Open-Meteo"
            }
        
        if data.terrain:
            result["terrain"] = {
                "elevation_m": data.terrain.elevation,
                "slope_deg": data.terrain.slope,
                "aspect_deg": data.terrain.aspect,
                "source": "Open-Elevation"
            }
        
        if data.vegetation:
            result["vegetation"] = {
                "ndvi": data.vegetation.ndvi,
                "ndwi": data.vegetation.ndwi,
                "evi": data.vegetation.evi,
                "source": data.vegetation.source
            }
        
        return result
    except Exception as e:
        logger.error(f"Error fetching complete geospatial data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geospatial/interpret")
async def interpret_vegetation_indices(
    ndvi: float = Query(..., ge=-1, le=1, description="NDVI value (-1 to 1)"),
    ndwi: float = Query(..., ge=-1, le=1, description="NDWI value (-1 to 1)")
):
    """Simple interpretation of NDVI and NDWI values"""
    interpretation = interpret_vegetation(ndvi, ndwi)
    
    return {
        "success": True,
        "ndvi": {
            "value": ndvi,
            "level": interpretation["ndvi"]["level"],
            "label": interpretation["ndvi"]["label"],
            "description": interpretation["ndvi"]["description"],
            "icon": interpretation["ndvi"]["icon"]
        },
        "ndwi": {
            "value": ndwi,
            "level": interpretation["ndwi"]["level"],
            "label": interpretation["ndwi"]["label"],
            "description": interpretation["ndwi"]["description"],
            "icon": interpretation["ndwi"]["icon"]
        },
        "conclusion": interpretation["conclusion"],
        "summary": interpretation["summary"]
    }


logger.info("BIONIC™ Engine Router initialized (v2.0 - Refactored)")
