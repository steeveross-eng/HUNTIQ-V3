"""
BIONIC™ SIGÉOM Engine - API Endpoints

Endpoints FastAPI pour l'analyse géologique SIGÉOM.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from ..core.extractor import sigeom_extractor
from ..core.analyzer import geology_analyzer

# Create router
sigeom_engine_router = APIRouter(
    prefix="/api/bionic/sigeom",
    tags=["BIONIC SIGÉOM Engine"]
)


class BoundingBox(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class ExtractionRequest(BaseModel):
    bbox: BoundingBox
    include_bedrock: bool = True
    include_surficial: bool = True
    include_faults: bool = True
    use_cache: bool = True


class AnalysisRequest(BaseModel):
    bbox: BoundingBox
    target_species: str = "deer"


# =============================================================================
# STATUS & INFO ENDPOINTS
# =============================================================================

@sigeom_engine_router.get("/status")
async def get_sigeom_engine_status():
    """
    Get status of the SIGÉOM Engine.
    """
    return {
        "status": "active",
        "engine": "SigeomEngine",
        "version": "0.1.0",
        "data_sources": [
            {
                "id": "sigeom",
                "name": "SIGÉOM - Système d'information géominière du Québec",
                "provider": "MERN Québec",
                "type": "WMS/WFS",
                "status": "available",
                "license": "Licence du gouvernement ouvert - Québec"
            }
        ],
        "capabilities": [
            "extract_bedrock_geology",
            "extract_surficial_deposits",
            "extract_faults_structures",
            "analyze_geological_province",
            "calculate_deposit_hunting_score",
            "generate_hunting_recommendations"
        ],
        "layers": list(sigeom_extractor.layers.keys())
    }


@sigeom_engine_router.get("/layers")
async def get_available_layers():
    """
    Get list of available SIGÉOM layers.
    """
    return {
        "layers": sigeom_extractor.layers,
        "wms_url": sigeom_extractor.wms_url,
        "attribution": sigeom_extractor.config["attribution"]
    }


# =============================================================================
# EXTRACTION ENDPOINTS
# =============================================================================

@sigeom_engine_router.post("/extract")
async def extract_geology_data(request: ExtractionRequest):
    """
    Extract geological data for a bounding box.
    
    Returns WMS tile URLs and metadata for bedrock, surficial deposits, and faults.
    """
    bbox = request.bbox.model_dump()
    
    return sigeom_extractor.extract_all(
        bbox=bbox,
        include_bedrock=request.include_bedrock,
        include_surficial=request.include_surficial,
        include_faults=request.include_faults,
        use_cache=request.use_cache
    )


@sigeom_engine_router.get("/extract/bedrock")
async def extract_bedrock(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """
    Extract bedrock geology data.
    """
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return sigeom_extractor.extract_bedrock(bbox)


@sigeom_engine_router.get("/extract/surficial")
async def extract_surficial(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """
    Extract surficial deposits data.
    """
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return sigeom_extractor.extract_surficial(bbox)


@sigeom_engine_router.get("/extract/faults")
async def extract_faults(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """
    Extract fault and structure data.
    """
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return sigeom_extractor.extract_faults(bbox)


# =============================================================================
# ANALYSIS ENDPOINTS
# =============================================================================

@sigeom_engine_router.post("/analyze")
async def analyze_territory(request: AnalysisRequest):
    """
    Perform complete geological analysis of a territory.
    
    Returns:
    - Geological province identification
    - Bedrock and surficial analysis
    - Hunting score based on geology
    - Recommendations
    """
    bbox = request.bbox.model_dump()
    
    # First extract the data
    geology_data = sigeom_extractor.extract_all(bbox)
    
    # Then analyze it
    return geology_analyzer.analyze_territory(
        geology_data=geology_data,
        bbox=bbox,
        target_species=request.target_species
    )


@sigeom_engine_router.get("/analyze/deposit-score")
async def get_deposit_score(
    deposit_type: str = Query(..., description="Type of surficial deposit"),
    species: str = Query("deer", description="Target species")
):
    """
    Calculate hunting score for a surficial deposit type.
    
    Deposit types:
    - till: Glacial till
    - sand_gravel: Sand and gravel (eskers, deltas)
    - marine_clay: Marine clay
    - peat: Peat/peatland
    - alluvium: Recent alluvium
    - bedrock: Exposed bedrock
    """
    return geology_analyzer.calculate_deposit_score(deposit_type, species)


@sigeom_engine_router.get("/analyze/province")
async def get_province_info(
    lat: float = Query(...),
    lon: float = Query(...)
):
    """
    Get geological province information for a location.
    """
    return geology_analyzer.get_province_info(lat, lon)


# =============================================================================
# REFERENCE DATA ENDPOINTS
# =============================================================================

@sigeom_engine_router.get("/reference/provinces")
async def get_geological_provinces():
    """
    Get information about Quebec's geological provinces.
    """
    return {
        "provinces": geology_analyzer.GEOLOGICAL_PROVINCES,
        "note": "Chaque province a des caractéristiques géologiques et de chasse distinctes"
    }


@sigeom_engine_router.get("/reference/deposit-types")
async def get_deposit_types():
    """
    Get surficial deposit types and their hunting scores.
    """
    return {
        "deposit_types": sigeom_extractor._get_surficial_deposit_types(),
        "hunting_scores": geology_analyzer.DEPOSIT_HUNTING_SCORES,
        "note": "Les dépôts de surface influencent l'accessibilité et les habitats"
    }


@sigeom_engine_router.get("/reference/rock-types")
async def get_rock_types():
    """
    Get common rock types in Quebec.
    """
    return {
        "rock_types": sigeom_extractor._get_common_rock_types(),
        "note": "La géologie du socle influence le drainage et la végétation"
    }


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@sigeom_engine_router.post("/cache/clear")
async def clear_cache(layer: Optional[str] = None):
    """
    Clear extraction cache.
    """
    result = sigeom_extractor.clear_cache(layer)
    return {
        "status": "success",
        "message": f"Cleared {result['cleared']} cached files",
        "layer_filter": layer
    }
