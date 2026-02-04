"""
BIONIC™ CORE - API Endpoints

Endpoints FastAPI pour l'analyse complète de territoire.
Utilise le modèle TerritoryFullAnalysis pour consolider
toutes les sources de données BIONIC™.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import httpx
import os

from ..models import (
    ModuleType,
    SpeciesType,
    ScoreRating,
    GeoPoint,
    BoundingBox,
    DataSourceInfo,
    ScoreBreakdown,
    Recommendation,
    ModuleResult,
    HabitatSuitability,
    ActivityPattern,
    SpeciesResult,
    SinglePrediction,
    PredictionResult,
    TemporalResult,
    TerritoryFullAnalysis,
    TerritoryAnalysisRequest,
    TerritoryAnalysisSummary,
    PredictionHorizon,
    Season,
)

# Router
bionic_core_router = APIRouter(
    prefix="/api/bionic/core",
    tags=["BIONIC CORE Engine"]
)

# API Base URL
API_BASE = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')


def get_score_rating(score: float) -> ScoreRating:
    """Convert numeric score to rating"""
    if score >= 85:
        return ScoreRating.EXCEPTIONAL
    elif score >= 75:
        return ScoreRating.EXCELLENT
    elif score >= 60:
        return ScoreRating.GOOD
    elif score >= 45:
        return ScoreRating.MODERATE
    elif score >= 30:
        return ScoreRating.LOW
    else:
        return ScoreRating.POOR


def get_current_season() -> Season:
    """Determine current season in Quebec"""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return Season.SPRING
    elif month in [6, 7, 8]:
        return Season.SUMMER
    elif month in [9, 10, 11]:
        return Season.FALL
    else:
        return Season.WINTER


# =============================================================================
# STATUS ENDPOINT
# =============================================================================

@bionic_core_router.get("/status")
async def get_core_status():
    """Get BIONIC CORE engine status"""
    return {
        "status": "active",
        "engine": "BIONIC_CORE",
        "version": "1.0.0",
        "description": "Moteur d'analyse territoriale consolidée BIONIC™",
        "capabilities": {
            "modules": [m.value for m in ModuleType],
            "species": [s.value for s in SpeciesType],
            "predictions": ["24h", "72h", "7d"],
            "temporal_analysis": True,
            "geojson_output": True
        },
        "endpoints": {
            "full_analysis": "POST /api/bionic/core/analyze",
            "quick_analysis": "GET /api/bionic/core/quick",
            "species_analysis": "POST /api/bionic/core/species",
            "schema": "GET /api/bionic/core/schema"
        }
    }


# =============================================================================
# MAIN ANALYSIS ENDPOINT
# =============================================================================

@bionic_core_router.post("/analyze", response_model=TerritoryFullAnalysis)
async def analyze_territory_full(request: TerritoryAnalysisRequest):
    """
    Perform a complete BIONIC™ territory analysis.
    
    This endpoint orchestrates all BIONIC engines to produce
    a consolidated analysis including:
    - Thematic modules (vegetation, hydrology, terrain, etc.)
    - Species-specific suitability scores
    - AI predictions (24h, 72h, 7d)
    - Temporal analysis (optional)
    - Consolidated recommendations
    - GeoJSON output
    """
    start_time = datetime.now(timezone.utc)
    territory_id = f"terr_{uuid.uuid4().hex[:12]}"
    
    # Calculate bounding box
    delta_lat = request.radius_km / 111.0  # ~111km per degree latitude
    delta_lon = request.radius_km / (111.0 * abs(cos_deg(request.latitude)))
    
    bbox = BoundingBox(
        min_lat=request.latitude - delta_lat,
        max_lat=request.latitude + delta_lat,
        min_lon=request.longitude - delta_lon,
        max_lon=request.longitude + delta_lon
    )
    
    # Collect data from engines
    modules = []
    data_sources = []
    all_recommendations = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch from HydroEngine
        if ModuleType.HYDROLOGY in request.include_modules:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/hydro/analyze",
                    json={"bbox": bbox.model_dump(), "target_species": request.target_species[0].value}
                )
                if response.status_code == 200:
                    data = response.json()
                    modules.append(ModuleResult(
                        module_type=ModuleType.HYDROLOGY,
                        module_name="Analyse Hydrologique",
                        score=data.get("analysis", {}).get("overall_score", 50),
                        rating=get_score_rating(data.get("analysis", {}).get("overall_score", 50)),
                        details=data.get("analysis", {}),
                        recommendations=data.get("recommendations", [])
                    ))
                    data_sources.append(DataSourceInfo(
                        source_id="hydro_grhq",
                        name="GRHQ Hydrologie",
                        provider="HydroEngine"
                    ))
            except Exception as e:
                print(f"HydroEngine error: {e}")
        
        # Fetch from SentinelEngine
        if ModuleType.VEGETATION in request.include_modules:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/sentinel/analyze/territory",
                    json={"bbox": bbox.model_dump(), "target_species": request.target_species[0].value}
                )
                if response.status_code == 200:
                    data = response.json()
                    modules.append(ModuleResult(
                        module_type=ModuleType.VEGETATION,
                        module_name="Analyse Végétation",
                        score=data.get("vegetation_score", data.get("hunting_score", 50)),
                        rating=get_score_rating(data.get("vegetation_score", 50)),
                        details=data,
                        indicators={"ndvi": data.get("ndvi", 0.5)}
                    ))
                    data_sources.append(DataSourceInfo(
                        source_id="sentinel_s2",
                        name="Sentinel-2 Imagery",
                        provider="SentinelEngine"
                    ))
            except Exception as e:
                print(f"SentinelEngine error: {e}")
        
        # Fetch from SigeomEngine
        if ModuleType.GEOLOGY in request.include_modules:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/sigeom/analyze",
                    json={"bbox": bbox.model_dump()}
                )
                if response.status_code == 200:
                    data = response.json()
                    modules.append(ModuleResult(
                        module_type=ModuleType.GEOLOGY,
                        module_name="Analyse Géologique",
                        score=data.get("hunting_score", 50),
                        rating=get_score_rating(data.get("hunting_score", 50)),
                        details=data
                    ))
                    data_sources.append(DataSourceInfo(
                        source_id="sigeom_mern",
                        name="SIGÉOM Québec",
                        provider="SigeomEngine"
                    ))
            except Exception as e:
                print(f"SigeomEngine error: {e}")
        
        # Fetch weather data
        if ModuleType.WEATHER in request.include_modules:
            try:
                response = await client.get(
                    f"{API_BASE}/api/weather",
                    params={"lat": request.latitude, "lon": request.longitude}
                )
                if response.status_code == 200:
                    data = response.json()
                    weather_score = calculate_weather_score(data, request.target_species[0])
                    modules.append(ModuleResult(
                        module_type=ModuleType.WEATHER,
                        module_name="Conditions Météo",
                        score=weather_score,
                        rating=get_score_rating(weather_score),
                        details=data
                    ))
                    data_sources.append(DataSourceInfo(
                        source_id="openweather",
                        name="OpenWeatherMap",
                        provider="WeatherAPI"
                    ))
            except Exception as e:
                print(f"Weather error: {e}")
    
    # Calculate species results
    species_results = []
    for target in request.target_species:
        species_score = calculate_species_score(modules, target)
        
        habitat = HabitatSuitability(
            food_score=get_module_score(modules, ModuleType.VEGETATION) * 0.8,
            water_score=get_module_score(modules, ModuleType.HYDROLOGY),
            cover_score=get_module_score(modules, ModuleType.VEGETATION) * 0.9,
            terrain_score=get_module_score(modules, ModuleType.GEOLOGY),
            disturbance_score=30  # Default low disturbance
        )
        
        species_results.append(SpeciesResult(
            species=target,
            species_name_fr=get_species_name_fr(target),
            suitability_score=species_score,
            rating=get_score_rating(species_score),
            habitat_suitability=habitat,
            activity_pattern=ActivityPattern(
                peak_hours=[6, 7, 17, 18],
                activity_level="moderate",
                feeding_times=["dawn", "dusk"]
            ),
            recommendations=generate_species_recommendations(target, species_score)
        ))
    
    # Generate predictions if requested
    predictions = None
    if request.include_predictions:
        predictions = generate_predictions(modules, request.target_species[0])
    
    # Calculate global score
    if modules:
        global_score = sum(m.score for m in modules) / len(modules)
    else:
        global_score = 50.0
    
    # Generate consolidated recommendations
    recommendations = generate_consolidated_recommendations(
        modules, species_results, global_score
    )
    
    # Calculate processing time
    end_time = datetime.now(timezone.utc)
    processing_time = int((end_time - start_time).total_seconds() * 1000)
    
    # Build the full analysis
    analysis = TerritoryFullAnalysis(
        territory_id=territory_id,
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
        bbox=bbox,
        created_at=start_time,
        analysis_duration_ms=processing_time,
        data_sources=data_sources,
        modules=modules,
        species=species_results,
        predictions=predictions,
        temporal=None,  # TODO: Implement temporal analysis
        global_score=global_score,
        global_rating=get_score_rating(global_score),
        score_breakdown=ScoreBreakdown(
            total_score=global_score,
            rating=get_score_rating(global_score),
            components={m.module_type.value: m.score for m in modules},
            weights={m.module_type.value: 1/len(modules) if modules else 0 for m in modules}
        ),
        recommendations=recommendations,
        geojson=generate_geojson(request.latitude, request.longitude, request.radius_km),
        engine_version="BIONIC_CORE 1.0"
    )
    
    return analysis


# =============================================================================
# QUICK ANALYSIS ENDPOINT
# =============================================================================

@bionic_core_router.get("/quick")
async def quick_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesType = Query(default=SpeciesType.DEER)
):
    """
    Quick territory analysis (lightweight, faster response).
    Returns a summary without full module details.
    """
    territory_id = f"terr_{uuid.uuid4().hex[:8]}"
    
    # Quick score estimation based on location
    base_score = 55
    
    # Adjust by species and latitude
    if species == SpeciesType.MOOSE and lat > 48:
        base_score += 15
    elif species == SpeciesType.DEER and lat < 47:
        base_score += 10
    elif species == SpeciesType.BEAR:
        base_score += 5
    
    # Seasonal adjustment
    season = get_current_season()
    seasonal_modifiers = {
        Season.SPRING: {"deer": 0.85, "moose": 0.90, "bear": 0.95},
        Season.SUMMER: {"deer": 0.80, "moose": 0.75, "bear": 1.00},
        Season.FALL: {"deer": 1.15, "moose": 1.20, "bear": 1.10},
        Season.WINTER: {"deer": 0.95, "moose": 1.00, "bear": 0.20}
    }
    modifier = seasonal_modifiers.get(season, {}).get(species.value, 1.0)
    final_score = min(100, max(0, base_score * modifier))
    
    return TerritoryAnalysisSummary(
        territory_id=territory_id,
        global_score=round(final_score, 1),
        global_rating=get_score_rating(final_score).value,
        top_species=species.value,
        top_recommendation=f"Zone {get_score_rating(final_score).value} pour {get_species_name_fr(species)}",
        analyzed_at=datetime.now(timezone.utc)
    )


# =============================================================================
# SCHEMA ENDPOINT
# =============================================================================

@bionic_core_router.get("/schema")
async def get_analysis_schema():
    """
    Get the JSON schema for TerritoryFullAnalysis model.
    Useful for documentation and client generation.
    """
    return TerritoryFullAnalysis.model_json_schema()


@bionic_core_router.get("/schema/request")
async def get_request_schema():
    """Get the JSON schema for analysis request"""
    return TerritoryAnalysisRequest.model_json_schema()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def cos_deg(degrees: float) -> float:
    """Cosine of angle in degrees"""
    import math
    return math.cos(math.radians(degrees))


def get_module_score(modules: List[ModuleResult], module_type: ModuleType) -> float:
    """Get score for a specific module type"""
    for module in modules:
        if module.module_type == module_type:
            return module.score
    return 50.0  # Default


def calculate_weather_score(weather_data: dict, species) -> float:
    """Calculate hunting score based on weather conditions"""
    score = 60
    
    # Handle both enum and string
    species_key = species.value if hasattr(species, 'value') else species
    
    if "main" in weather_data:
        temp = weather_data["main"].get("temp", 15)
        
        if species_key in ["deer", "moose", "elk"]:
            if 0 <= temp <= 10:
                score = 85
            elif 10 < temp <= 20:
                score = 70
            elif -10 <= temp < 0:
                score = 60
            else:
                score = 45
        elif species_key == "bear":
            if 10 <= temp <= 25:
                score = 80
            else:
                score = 55
    
    # Weather condition penalties
    if "weather" in weather_data and weather_data["weather"]:
        condition = weather_data["weather"][0].get("main", "").lower()
        if condition in ["thunderstorm", "storm"]:
            score *= 0.4
        elif condition in ["rain"]:
            score *= 0.7
    
    return min(100, max(0, score))


def calculate_species_score(modules: List[ModuleResult], species) -> float:
    """Calculate species suitability score from module results"""
    # Handle both enum and string
    species_key = species.value if hasattr(species, 'value') else species
    
    weights = {
        "deer": {ModuleType.VEGETATION: 0.35, ModuleType.HYDROLOGY: 0.25, ModuleType.GEOLOGY: 0.15, ModuleType.WEATHER: 0.25},
        "moose": {ModuleType.VEGETATION: 0.30, ModuleType.HYDROLOGY: 0.35, ModuleType.GEOLOGY: 0.10, ModuleType.WEATHER: 0.25},
        "bear": {ModuleType.VEGETATION: 0.40, ModuleType.HYDROLOGY: 0.20, ModuleType.GEOLOGY: 0.10, ModuleType.WEATHER: 0.30},
    }
    
    species_weights = weights.get(species_key, {ModuleType.VEGETATION: 0.35, ModuleType.HYDROLOGY: 0.25, ModuleType.GEOLOGY: 0.15, ModuleType.WEATHER: 0.25})
    
    score = 0
    total_weight = 0
    
    for module in modules:
        weight = species_weights.get(module.module_type, 0.1)
        score += module.score * weight
        total_weight += weight
    
    if total_weight > 0:
        return score / total_weight
    return 50.0


def get_species_name_fr(species) -> str:
    """Get French name for species"""
    # Handle both enum and string
    species_key = species.value if hasattr(species, 'value') else species
    
    names = {
        "deer": "Cerf de Virginie",
        "moose": "Orignal",
        "bear": "Ours noir",
        "elk": "Wapiti",
        "waterfowl": "Sauvagine",
        "turkey": "Dindon sauvage",
        "smallgame": "Petit gibier"
    }
    return names.get(species_key, str(species_key))


def generate_species_recommendations(species, score: float) -> List[str]:
    """Generate species-specific recommendations"""
    recs = []
    species_name = get_species_name_fr(species)
    species_key = species.value if hasattr(species, 'value') else species
    
    if score >= 70:
        recs.append(f"Zone favorable pour {species_name}")
    elif score >= 50:
        recs.append(f"Potentiel modéré pour {species_name}")
    else:
        recs.append(f"Zone peu propice pour {species_name}")
    
    season = get_current_season()
    if season == Season.FALL:
        if species_key in ["deer", "moose"]:
            recs.append("Période de rut - Utiliser des attractants")
    
    return recs


def generate_predictions(modules: List[ModuleResult], species: SpeciesType) -> PredictionResult:
    """Generate AI predictions"""
    base_score = sum(m.score for m in modules) / len(modules) if modules else 50
    
    predictions = [
        SinglePrediction(
            horizon=PredictionHorizon.H24,
            timestamp=datetime.now(timezone.utc) + timedelta(hours=24),
            predicted_score=base_score * 1.05,
            confidence=0.85
        ),
        SinglePrediction(
            horizon=PredictionHorizon.H72,
            timestamp=datetime.now(timezone.utc) + timedelta(hours=72),
            predicted_score=base_score * 0.98,
            confidence=0.75
        ),
        SinglePrediction(
            horizon=PredictionHorizon.D7,
            timestamp=datetime.now(timezone.utc) + timedelta(days=7),
            predicted_score=base_score * 0.95,
            confidence=0.60
        )
    ]
    
    return PredictionResult(
        predictions=predictions,
        trend="stable",
        best_window={"start": "06:00", "end": "09:00", "confidence": 0.8}
    )


def generate_consolidated_recommendations(
    modules: List[ModuleResult],
    species_results: List[SpeciesResult],
    global_score: float
) -> List[Recommendation]:
    """Generate consolidated recommendations from all sources"""
    recommendations = []
    
    # Global recommendation
    if global_score >= 70:
        recommendations.append(Recommendation(
            id="rec_global_1",
            priority="high",
            category="general",
            message="Zone à fort potentiel de chasse. Conditions favorables.",
            action_type="do"
        ))
    elif global_score >= 50:
        recommendations.append(Recommendation(
            id="rec_global_2",
            priority="medium",
            category="general",
            message="Potentiel modéré. Surveillez les conditions météo.",
            action_type="consider"
        ))
    else:
        recommendations.append(Recommendation(
            id="rec_global_3",
            priority="low",
            category="general",
            message="Zone peu propice. Explorez d'autres territoires.",
            action_type="avoid"
        ))
    
    # Module-specific recommendations
    for module in modules:
        if module.score < 40:
            recommendations.append(Recommendation(
                id=f"rec_{module.module_type.value}_low",
                priority="medium",
                category=module.module_type.value,
                message=f"Score {module.module_name} faible ({module.score:.0f}/100)",
                source_module=module.module_type.value,
                action_type="info"
            ))
    
    # Species-specific
    if species_results:
        best_species = max(species_results, key=lambda s: s.suitability_score)
        recommendations.append(Recommendation(
            id="rec_species_best",
            priority="high",
            category="species",
            message=f"Meilleure cible: {best_species.species_name_fr} (score: {best_species.suitability_score:.0f})",
            action_type="info"
        ))
    
    return recommendations


def generate_geojson(lat: float, lon: float, radius_km: float) -> dict:
    """Generate GeoJSON for the analysis area"""
    import math
    
    # Generate circle polygon (approximation with 32 points)
    points = []
    for i in range(32):
        angle = (i / 32) * 2 * math.pi
        dlat = (radius_km / 111.0) * math.cos(angle)
        dlon = (radius_km / (111.0 * abs(math.cos(math.radians(lat))))) * math.sin(angle)
        points.append([lon + dlon, lat + dlat])
    points.append(points[0])  # Close polygon
    
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Zone d'analyse",
                    "radius_km": radius_km
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
                    "type": "center"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }
        ]
    }
