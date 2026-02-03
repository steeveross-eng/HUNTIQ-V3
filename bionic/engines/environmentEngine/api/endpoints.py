"""
BIONIC™ Environment Engine - API Endpoints

Endpoints FastAPI pour l'analyse environnementale combinée.
Fusionne les données de tous les moteurs BIONIC™.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import httpx
import os

from ..core.combiner import environment_combiner
from ..core.scorer import environment_scorer

# Create router
environment_engine_router = APIRouter(
    prefix="/api/bionic/environment",
    tags=["BIONIC Environment Engine"]
)

# Base URL for internal API calls
API_BASE = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')


class BoundingBox(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class PointLocation(BaseModel):
    lat: float
    lon: float


class CombinedAnalysisRequest(BaseModel):
    bbox: BoundingBox
    target_species: str = "deer"
    include_hydro: bool = True
    include_sentinel: bool = True
    include_sigeom: bool = True
    include_weather: bool = True
    include_nutrition: bool = False
    apply_seasonal: bool = True


class PointAnalysisRequest(BaseModel):
    location: PointLocation
    target_species: str = "deer"
    include_weather: bool = True


class ZoneComparisonRequest(BaseModel):
    zones: List[BoundingBox]
    target_species: str = "deer"


class CustomWeightsRequest(BaseModel):
    bbox: BoundingBox
    target_species: str = "deer"
    weights: Dict[str, float]  # ex: {"vegetation": 0.4, "hydrology": 0.3, ...}


# =============================================================================
# STATUS & INFO ENDPOINTS
# =============================================================================

@environment_engine_router.get("/status")
async def get_environment_engine_status():
    """
    Get status of the Environment Engine.
    """
    return {
        "status": "active",
        "engine": "EnvironmentEngine",
        "version": "0.1.0",
        "description": "Moteur d'analyse environnementale combinée BIONIC™",
        "data_sources": [
            {
                "id": "hydro",
                "name": "HydroEngine",
                "description": "Analyse hydrologique (GRHQ)",
                "weight_default": 0.25
            },
            {
                "id": "sentinel",
                "name": "SentinelEngine", 
                "description": "Analyse végétation (Sentinel-2/MODIS)",
                "weight_default": 0.35
            },
            {
                "id": "sigeom",
                "name": "SigeomEngine",
                "description": "Analyse géologique (SIGÉOM)",
                "weight_default": 0.15
            },
            {
                "id": "weather",
                "name": "OpenWeatherMap",
                "description": "Conditions météo temps réel",
                "weight_default": 0.15
            },
            {
                "id": "nutrition",
                "name": "NutritionEngine",
                "description": "Analyse nutritionnelle",
                "weight_default": 0.10
            }
        ],
        "capabilities": [
            "combined_territory_analysis",
            "point_analysis",
            "multi_zone_comparison",
            "custom_weight_analysis",
            "seasonal_adjustments",
            "species_specific_scoring"
        ],
        "supported_species": ["deer", "moose", "bear", "elk", "waterfowl"]
    }


@environment_engine_router.get("/weights")
async def get_default_weights(species: str = Query("deer")):
    """
    Get default analysis weights for a species.
    """
    weights = environment_combiner.get_weights_for_species(species)
    return {
        "species": species,
        "weights": weights,
        "description": "Pondération utilisée pour calculer le score global",
        "total": sum(weights.values())
    }


@environment_engine_router.get("/weights/all")
async def get_all_species_weights():
    """
    Get weights for all supported species.
    """
    return {
        "species_weights": environment_combiner.species_weight_adjustments,
        "default_weights": environment_combiner.default_weights
    }


# =============================================================================
# MAIN ANALYSIS ENDPOINTS
# =============================================================================

@environment_engine_router.post("/analyze/territory")
async def analyze_territory_combined(request: CombinedAnalysisRequest):
    """
    Perform combined environmental analysis of a territory.
    
    This endpoint fetches data from all enabled BIONIC™ engines and
    calculates a global hunting potential score.
    
    Returns:
    - Global hunting score (0-100)
    - Individual component scores
    - Detailed recommendations
    - Classification (exceptional/excellent/good/moderate/low/poor)
    """
    bbox = request.bbox.model_dump()
    
    # Collect data from engines
    hydro_data = None
    sentinel_data = None
    sigeom_data = None
    weather_data = None
    nutrition_data = None
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch hydrology data
        if request.include_hydro:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/hydro/analyze",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    hydro_data = response.json()
            except Exception as e:
                hydro_data = {"error": str(e), "status": "unavailable"}
        
        # Fetch vegetation data
        if request.include_sentinel:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/sentinel/analyze/territory",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    sentinel_data = response.json()
            except Exception as e:
                sentinel_data = {"error": str(e), "status": "unavailable"}
        
        # Fetch geology data
        if request.include_sigeom:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/sigeom/analyze",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    sigeom_data = response.json()
            except Exception as e:
                sigeom_data = {"error": str(e), "status": "unavailable"}
        
        # Fetch weather data
        if request.include_weather:
            try:
                center_lat = (bbox["min_lat"] + bbox["max_lat"]) / 2
                center_lon = (bbox["min_lon"] + bbox["max_lon"]) / 2
                response = await client.get(
                    f"{API_BASE}/api/weather",
                    params={"lat": center_lat, "lon": center_lon}
                )
                if response.status_code == 200:
                    weather_data = response.json()
            except Exception as e:
                weather_data = {"error": str(e), "status": "unavailable"}
    
    # Combine all data
    combined_data = environment_combiner.combine_analysis_data(
        hydro_data=hydro_data,
        sentinel_data=sentinel_data,
        sigeom_data=sigeom_data,
        weather_data=weather_data,
        nutrition_data=nutrition_data,
        target_species=request.target_species
    )
    
    # Calculate global score
    result = environment_scorer.calculate_global_score(
        combined_data=combined_data,
        apply_seasonal=request.apply_seasonal
    )
    
    # Add raw component data for transparency
    result["component_data"] = combined_data.get("components", {})
    result["metadata"] = combined_data.get("metadata", {})
    
    return result


@environment_engine_router.post("/analyze/point")
async def analyze_point(request: PointAnalysisRequest):
    """
    Analyze environmental conditions at a specific point.
    
    Lighter analysis focused on a single location.
    """
    lat = request.location.lat
    lon = request.location.lon
    
    # Create small bbox around point (roughly 500m radius)
    delta = 0.005  # ~500m at Quebec latitudes
    bbox = {
        "min_lat": lat - delta,
        "max_lat": lat + delta,
        "min_lon": lon - delta,
        "max_lon": lon + delta
    }
    
    hydro_data = None
    sentinel_data = None
    weather_data = None
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Quick hydrology check
        try:
            response = await client.get(
                f"{API_BASE}/api/bionic/hydro/score/proximity",
                params={"distance_m": 200, "species": request.target_species}
            )
            if response.status_code == 200:
                hydro_data = response.json()
        except:
            pass
        
        # Vegetation at point
        try:
            response = await client.get(
                f"{API_BASE}/api/bionic/sentinel/analyze/point",
                params={"lat": lat, "lon": lon}
            )
            if response.status_code == 200:
                sentinel_data = response.json()
        except:
            pass
        
        # Weather at point
        if request.include_weather:
            try:
                response = await client.get(
                    f"{API_BASE}/api/weather",
                    params={"lat": lat, "lon": lon}
                )
                if response.status_code == 200:
                    weather_data = response.json()
            except:
                pass
    
    # Combine and score
    combined = environment_combiner.combine_analysis_data(
        hydro_data=hydro_data,
        sentinel_data=sentinel_data,
        weather_data=weather_data,
        target_species=request.target_species
    )
    
    result = environment_scorer.calculate_global_score(combined)
    result["location"] = {"lat": lat, "lon": lon}
    
    return result


@environment_engine_router.post("/compare/zones")
async def compare_zones(request: ZoneComparisonRequest):
    """
    Compare multiple zones and rank them by hunting potential.
    
    Useful for deciding which area to hunt.
    """
    zone_results = []
    
    for i, zone_bbox in enumerate(request.zones):
        bbox = zone_bbox.model_dump()
        
        # Simplified analysis for each zone
        async with httpx.AsyncClient(timeout=20.0) as client:
            hydro_data = None
            sentinel_data = None
            
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/hydro/analyze",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    hydro_data = response.json()
            except:
                pass
            
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/sentinel/analyze/territory",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    sentinel_data = response.json()
            except:
                pass
        
        combined = environment_combiner.combine_analysis_data(
            hydro_data=hydro_data,
            sentinel_data=sentinel_data,
            target_species=request.target_species
        )
        
        result = environment_scorer.calculate_global_score(combined)
        result["zone_index"] = i
        result["bbox"] = bbox
        zone_results.append(result)
    
    # Compare and rank zones
    comparison = environment_scorer.compare_zones(zone_results)
    
    return {
        "target_species": request.target_species,
        "zones_analyzed": len(request.zones),
        "comparison": comparison
    }


# =============================================================================
# CUSTOM ANALYSIS ENDPOINTS
# =============================================================================

@environment_engine_router.post("/analyze/custom-weights")
async def analyze_with_custom_weights(request: CustomWeightsRequest):
    """
    Analyze territory with custom weight distribution.
    
    Allows users to prioritize different factors.
    """
    # Validate weights sum to ~1.0
    weight_sum = sum(request.weights.values())
    if abs(weight_sum - 1.0) > 0.1:
        raise HTTPException(
            status_code=400,
            detail=f"Weights should sum to 1.0 (currently: {weight_sum})"
        )
    
    bbox = request.bbox.model_dump()
    
    # Fetch data from enabled engines (based on weights)
    async with httpx.AsyncClient(timeout=30.0) as client:
        hydro_data = None
        sentinel_data = None
        sigeom_data = None
        weather_data = None
        
        if request.weights.get("hydrology", 0) > 0:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/hydro/analyze",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    hydro_data = response.json()
            except:
                pass
        
        if request.weights.get("vegetation", 0) > 0:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/sentinel/analyze/territory",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    sentinel_data = response.json()
            except:
                pass
        
        if request.weights.get("geology", 0) > 0:
            try:
                response = await client.post(
                    f"{API_BASE}/api/bionic/sigeom/analyze",
                    json={"bbox": bbox, "target_species": request.target_species}
                )
                if response.status_code == 200:
                    sigeom_data = response.json()
            except:
                pass
        
        if request.weights.get("weather", 0) > 0:
            center_lat = (bbox["min_lat"] + bbox["max_lat"]) / 2
            center_lon = (bbox["min_lon"] + bbox["max_lon"]) / 2
            try:
                response = await client.get(
                    f"{API_BASE}/api/weather",
                    params={"lat": center_lat, "lon": center_lon}
                )
                if response.status_code == 200:
                    weather_data = response.json()
            except:
                pass
    
    # Override combiner weights
    original_weights = environment_combiner.default_weights.copy()
    environment_combiner.default_weights = request.weights
    
    combined = environment_combiner.combine_analysis_data(
        hydro_data=hydro_data,
        sentinel_data=sentinel_data,
        sigeom_data=sigeom_data,
        weather_data=weather_data,
        target_species=request.target_species
    )
    
    # Restore original weights
    environment_combiner.default_weights = original_weights
    
    result = environment_scorer.calculate_global_score(combined)
    result["custom_weights_used"] = request.weights
    
    return result


# =============================================================================
# REFERENCE ENDPOINTS
# =============================================================================

@environment_engine_router.get("/reference/score-thresholds")
async def get_score_thresholds():
    """
    Get score classification thresholds.
    """
    return {
        "thresholds": environment_scorer.score_thresholds,
        "descriptions": environment_scorer.score_descriptions
    }


@environment_engine_router.get("/reference/seasonal-modifiers")
async def get_seasonal_modifiers():
    """
    Get seasonal adjustment factors for each species.
    """
    return {
        "seasonal_modifiers": environment_scorer.seasonal_modifiers,
        "current_season": environment_scorer._get_current_season(),
        "note": "Multiplicateurs appliqués au score selon la saison"
    }


@environment_engine_router.get("/quick-score")
async def get_quick_score(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    species: str = Query("deer", description="Target species")
):
    """
    Get a quick estimated score for a location.
    
    Uses simplified calculations without full engine queries.
    """
    # Simple heuristics based on location in Quebec
    # This is a fallback when engines are slow or unavailable
    
    base_score = 60
    
    # Quebec hunting zones tend to be better in certain regions
    # Northern regions (higher lat) often have more moose
    # Southern regions better for deer
    
    if species == "moose":
        if lat > 48:
            base_score += 15
        elif lat > 46:
            base_score += 5
    elif species == "deer":
        if lat < 47:
            base_score += 10
        elif lat < 48:
            base_score += 5
    elif species == "bear":
        base_score += 5  # Bears are widespread
    
    # Apply seasonal modifier
    season = environment_scorer._get_current_season()
    modifier = environment_scorer.seasonal_modifiers.get(season, {}).get(species, 1.0)
    
    final_score = min(100, max(0, base_score * modifier))
    
    return {
        "quick_score": round(final_score, 1),
        "location": {"lat": lat, "lon": lon},
        "species": species,
        "season": season,
        "seasonal_modifier": modifier,
        "note": "Score estimé rapidement. Utilisez /analyze/territory pour une analyse complète."
    }
