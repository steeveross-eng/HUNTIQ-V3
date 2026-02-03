"""
BIONIC™ Hydrology Engine - API Endpoints

Endpoints FastAPI pour l'analyse hydrologique.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from ..core.extractor import hydro_extractor
from ..core.analyzer import hydro_analyzer
from ..core.network import stream_network_analyzer

# Create router
hydro_engine_router = APIRouter(
    prefix="/api/bionic/hydro",
    tags=["BIONIC Hydrology Engine"]
)


class BoundingBox(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class HydroExtractionRequest(BaseModel):
    bbox: BoundingBox
    include_rivers: bool = True
    include_lakes: bool = True
    include_wetlands: bool = True
    include_watersheds: bool = False
    use_cache: bool = True


class HydroAnalysisRequest(BaseModel):
    bbox: BoundingBox
    target_species: str = "deer"
    include_rivers: bool = True
    include_lakes: bool = True
    include_wetlands: bool = True


class ProximityScoreRequest(BaseModel):
    distance_m: float
    species: str = "deer"


# =============================================================================
# EXTRACTION ENDPOINTS
# =============================================================================

@hydro_engine_router.get("/status")
async def get_hydro_engine_status():
    """
    Get status of the Hydrology Engine.
    """
    return {
        "status": "active",
        "engine": "HydroEngine",
        "version": "0.1.0",
        "data_sources": [
            {
                "id": "grhq",
                "name": "GRHQ - Géobase du réseau hydrographique du Québec",
                "type": "WMS/WFS",
                "status": "available",
                "license": "CC-BY 4.0"
            }
        ],
        "capabilities": [
            "extract_rivers",
            "extract_lakes",
            "extract_wetlands",
            "analyze_territory",
            "calculate_proximity_score",
            "identify_corridors"
        ]
    }


@hydro_engine_router.post("/extract")
async def extract_hydro_data(request: HydroExtractionRequest):
    """
    Extract hydrological data for a bounding box.
    
    Returns WMS tile URLs and metadata for rivers, lakes, and wetlands.
    """
    bbox = request.bbox.model_dump()
    
    result = await hydro_extractor.extract_all(
        bbox=bbox,
        include_rivers=request.include_rivers,
        include_lakes=request.include_lakes,
        include_wetlands=request.include_wetlands,
        include_watersheds=request.include_watersheds,
        use_cache=request.use_cache
    )
    
    return result


@hydro_engine_router.get("/extract/rivers")
async def extract_rivers(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """
    Extract river data for a region.
    """
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await hydro_extractor.extract_rivers(bbox)


@hydro_engine_router.get("/extract/lakes")
async def extract_lakes(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    min_area_m2: float = Query(1000)
):
    """
    Extract lake data for a region.
    """
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await hydro_extractor.extract_lakes(bbox, min_area_m2)


@hydro_engine_router.get("/extract/wetlands")
async def extract_wetlands(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """
    Extract wetland data for a region.
    """
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await hydro_extractor.extract_wetlands(bbox)


# =============================================================================
# ANALYSIS ENDPOINTS
# =============================================================================

@hydro_engine_router.post("/analyze")
async def analyze_territory(request: HydroAnalysisRequest):
    """
    Perform complete hydrological analysis of a territory.
    
    Returns:
    - Overall hydrology score
    - Component scores (rivers, lakes, wetlands)
    - Hunting recommendations
    """
    bbox = request.bbox.model_dump()
    
    # First extract the data
    hydro_data = await hydro_extractor.extract_all(
        bbox=bbox,
        include_rivers=request.include_rivers,
        include_lakes=request.include_lakes,
        include_wetlands=request.include_wetlands
    )
    
    # Then analyze it
    analysis = hydro_analyzer.analyze_territory(
        hydro_data=hydro_data,
        bbox=bbox,
        target_species=request.target_species
    )
    
    return analysis


@hydro_engine_router.post("/score/proximity")
async def calculate_proximity_score(request: ProximityScoreRequest):
    """
    Calculate water proximity score for a given distance.
    
    Args:
        distance_m: Distance to nearest water source in meters
        species: Target hunting species
    """
    return hydro_analyzer.calculate_proximity_score(
        distance_m=request.distance_m,
        species=request.species
    )


@hydro_engine_router.get("/score/proximity")
async def get_proximity_score(
    distance_m: float = Query(..., description="Distance to water in meters"),
    species: str = Query("deer", description="Target species")
):
    """
    Calculate water proximity score (GET version).
    """
    return hydro_analyzer.calculate_proximity_score(
        distance_m=distance_m,
        species=species
    )


@hydro_engine_router.get("/score/network-density")
async def get_network_density_score(
    total_length_km: float = Query(..., description="Total waterway length in km"),
    area_km2: float = Query(..., description="Area in km²")
):
    """
    Calculate hydrographic network density score.
    """
    return hydro_analyzer.calculate_network_density_score(
        total_length_km=total_length_km,
        area_km2=area_km2
    )


# =============================================================================
# NETWORK ANALYSIS ENDPOINTS
# =============================================================================

@hydro_engine_router.get("/network/corridors")
async def get_corridor_info(
    stream_order: int = Query(2, description="Stream order (1-5)"),
    length_km: float = Query(5.0, description="Stream length in km"),
    species: str = Query("deer", description="Target species")
):
    """
    Get corridor score and recommendations for a stream segment.
    """
    stream_data = {
        "order": stream_order,
        "length_km": length_km
    }
    return stream_network_analyzer.calculate_corridor_score(
        stream_data=stream_data,
        target_species=species
    )


@hydro_engine_router.get("/network/funnel-types")
async def get_funnel_types():
    """
    Get list of natural funnel point types for wildlife.
    """
    return {
        "funnel_types": stream_network_analyzer.identify_funnel_points([], None),
        "usage": "Identifiez ces points sur votre territoire pour maximiser vos chances"
    }


@hydro_engine_router.post("/network/confluence")
async def analyze_confluence(
    lat: float = Query(...),
    lon: float = Query(...),
    stream_orders: List[int] = Query(default=[2, 2])
):
    """
    Analyze hunting potential at a stream confluence.
    """
    return stream_network_analyzer.analyze_confluence_potential(
        confluence_point={"lat": lat, "lon": lon},
        stream_orders=stream_orders
    )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@hydro_engine_router.get("/species-preferences")
async def get_species_water_preferences():
    """
    Get water proximity preferences for different species.
    """
    return {
        "species_preferences": hydro_analyzer.SPECIES_WATER_NEEDS,
        "note": "Distance préférée et importance de l'eau pour chaque espèce"
    }


@hydro_engine_router.get("/wetland-types")
async def get_wetland_types():
    """
    Get wetland type classifications and hunting values.
    """
    return {
        "wetland_types": hydro_analyzer.WETLAND_QUALITY,
        "descriptions": {
            "marais": "Marsh - Excellent for waterfowl",
            "marecage": "Swamp - Good wildlife habitat",
            "tourbiere": "Peatland/Bog - Moderate value",
            "eau_peu_profonde": "Shallow water - Excellent for wading birds"
        }
    }


@hydro_engine_router.post("/cache/clear")
async def clear_hydro_cache(layer: Optional[str] = None):
    """
    Clear extraction cache.
    """
    result = hydro_extractor.clear_cache(layer)
    return {
        "status": "success",
        "message": f"Cleared {result['cleared']} cached files",
        "layer_filter": layer
    }
