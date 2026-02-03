"""
BIONIC™ Sentinel Engine - API Endpoints

Endpoints FastAPI pour l'analyse de végétation Sentinel-2.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List
from pydantic import BaseModel

from ..core.analyzer import sentinel_analyzer
from ..core.indices import vegetation_indices
from ..core.classifier import vegetation_classifier

# Create router
sentinel_engine_router = APIRouter(
    prefix="/api/bionic/sentinel",
    tags=["BIONIC Sentinel Engine"]
)


class BoundingBox(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class BandValues(BaseModel):
    B02: Optional[float] = None  # Blue
    B03: Optional[float] = None  # Green
    B04: Optional[float] = None  # Red
    B08: Optional[float] = None  # NIR
    B11: Optional[float] = None  # SWIR1
    B12: Optional[float] = None  # SWIR2


class PointAnalysisRequest(BaseModel):
    lat: float
    lon: float
    bands: Optional[BandValues] = None


class TerritoryAnalysisRequest(BaseModel):
    bbox: BoundingBox
    target_species: str = "deer"


class NDVIRequest(BaseModel):
    red: float
    nir: float


# =============================================================================
# STATUS & INFO ENDPOINTS
# =============================================================================

@sentinel_engine_router.get("/status")
async def get_sentinel_engine_status():
    """
    Get status of the Sentinel Engine.
    """
    return {
        "status": "active",
        "engine": "SentinelEngine",
        "version": "0.1.0",
        "data_sources": [
            {
                "id": "nasa_gibs",
                "name": "NASA GIBS (MODIS)",
                "status": "available",
                "requires_key": False
            },
            {
                "id": "copernicus",
                "name": "Copernicus Sentinel Hub",
                "status": "requires_api_key",
                "requires_key": True
            }
        ],
        "capabilities": [
            "ndvi_calculation",
            "evi_calculation",
            "savi_calculation",
            "ndwi_water_detection",
            "nbr_burn_detection",
            "vegetation_classification",
            "habitat_analysis",
            "hunting_score_calculation"
        ],
        "supported_indices": ["NDVI", "EVI", "SAVI", "NDWI", "NBR"]
    }


@sentinel_engine_router.get("/bands")
async def get_sentinel_bands():
    """
    Get information about Sentinel-2 spectral bands.
    """
    return {
        "satellite": "Sentinel-2",
        "bands": vegetation_indices.BANDS,
        "usage_note": "Utilisez ces bandes pour calculer les indices de végétation"
    }


# =============================================================================
# VEGETATION INDICES ENDPOINTS
# =============================================================================

@sentinel_engine_router.post("/indices/ndvi")
async def calculate_ndvi(request: NDVIRequest):
    """
    Calculate NDVI (Normalized Difference Vegetation Index).
    
    NDVI = (NIR - Red) / (NIR + Red)
    
    Values:
    - -1 to 0: Water, bare soil
    - 0 to 0.3: Sparse vegetation
    - 0.3 to 0.6: Moderate vegetation
    - 0.6 to 1: Dense vegetation
    """
    return vegetation_indices.calculate_ndvi(request.red, request.nir)


@sentinel_engine_router.get("/indices/ndvi")
async def get_ndvi(
    red: float = Query(..., description="Red band value (B04)"),
    nir: float = Query(..., description="NIR band value (B08)")
):
    """
    Calculate NDVI (GET version).
    """
    return vegetation_indices.calculate_ndvi(red, nir)


@sentinel_engine_router.get("/indices/evi")
async def get_evi(
    red: float = Query(...),
    nir: float = Query(...),
    blue: float = Query(...)
):
    """
    Calculate EVI (Enhanced Vegetation Index).
    """
    return vegetation_indices.calculate_evi(red, nir, blue)


@sentinel_engine_router.get("/indices/savi")
async def get_savi(
    red: float = Query(...),
    nir: float = Query(...),
    l: float = Query(0.5, description="Soil brightness correction factor")
):
    """
    Calculate SAVI (Soil Adjusted Vegetation Index).
    """
    return vegetation_indices.calculate_savi(red, nir, l)


@sentinel_engine_router.get("/indices/ndwi")
async def get_ndwi(
    green: float = Query(..., description="Green band value (B03)"),
    nir: float = Query(..., description="NIR band value (B08)")
):
    """
    Calculate NDWI (Normalized Difference Water Index).
    
    Detects water bodies and moisture content.
    """
    return vegetation_indices.calculate_ndwi(green, nir)


@sentinel_engine_router.get("/indices/nbr")
async def get_nbr(
    nir: float = Query(..., description="NIR band value (B08)"),
    swir: float = Query(..., description="SWIR band value (B12)")
):
    """
    Calculate NBR (Normalized Burn Ratio).
    
    Detects burned areas and fire severity.
    """
    return vegetation_indices.calculate_nbr(nir, swir)


@sentinel_engine_router.post("/indices/all")
async def calculate_all_indices(bands: BandValues):
    """
    Calculate all vegetation indices from band values.
    """
    bands_dict = {k: v for k, v in bands.model_dump().items() if v is not None}
    return vegetation_indices.calculate_all_indices(bands_dict)


# =============================================================================
# ANALYSIS ENDPOINTS
# =============================================================================

@sentinel_engine_router.post("/analyze/point")
async def analyze_point(request: PointAnalysisRequest):
    """
    Analyze vegetation at a specific point.
    
    Returns:
    - Vegetation indices
    - Habitat classification
    - Hunting score
    - Recommendations
    """
    bands_dict = None
    if request.bands:
        bands_dict = {k: v for k, v in request.bands.model_dump().items() if v is not None}
    
    return sentinel_analyzer.analyze_point(
        lat=request.lat,
        lon=request.lon,
        bands=bands_dict
    )


@sentinel_engine_router.get("/analyze/point")
async def analyze_point_get(
    lat: float = Query(...),
    lon: float = Query(...)
):
    """
    Analyze vegetation at a point (GET version with estimated values).
    """
    return sentinel_analyzer.analyze_point(lat, lon)


@sentinel_engine_router.post("/analyze/territory")
async def analyze_territory(request: TerritoryAnalysisRequest):
    """
    Analyze vegetation across a territory.
    
    Returns:
    - Territory-wide vegetation analysis
    - Species suitability assessment
    - Available WMS layers
    - Hunting recommendations
    """
    bbox = request.bbox.model_dump()
    return sentinel_analyzer.analyze_territory(
        bbox=bbox,
        target_species=request.target_species
    )


# =============================================================================
# CLASSIFICATION ENDPOINTS
# =============================================================================

@sentinel_engine_router.get("/classify/forest")
async def classify_forest_type(
    ndvi: float = Query(...),
    evi: Optional[float] = Query(None),
    season: str = Query("summer"),
    lat: float = Query(47.0)
):
    """
    Classify forest type based on vegetation indices.
    
    Returns forest type (coniferous, deciduous, mixed, regenerating)
    with hunting value for each species.
    """
    return vegetation_classifier.classify_forest_type(
        ndvi=ndvi,
        evi=evi,
        season=season,
        lat=lat
    )


@sentinel_engine_router.get("/classify/landcover")
async def classify_land_cover(
    ndvi: float = Query(...),
    ndwi: float = Query(0.0)
):
    """
    Classify land cover type.
    
    Returns cover type (forest, wetland, grassland, water, etc.)
    """
    return vegetation_classifier.classify_land_cover(ndvi, ndwi)


# =============================================================================
# REFERENCE DATA ENDPOINTS
# =============================================================================

@sentinel_engine_router.get("/reference/thresholds")
async def get_ndvi_thresholds():
    """
    Get NDVI classification thresholds.
    """
    return {
        "thresholds": vegetation_indices.NDVI_THRESHOLDS,
        "hunting_values": vegetation_indices.HUNTING_VEGETATION_VALUE,
        "usage": "Utilisez ces seuils pour interpréter les valeurs NDVI"
    }


@sentinel_engine_router.get("/reference/habitats")
async def get_habitat_types():
    """
    Get habitat type classifications.
    """
    return {
        "habitats": sentinel_analyzer.HABITAT_TYPES,
        "note": "Chaque habitat est classifié selon les plages NDVI et NDWI"
    }


@sentinel_engine_router.get("/reference/forest-types")
async def get_forest_types():
    """
    Get Quebec forest type classifications.
    """
    return {
        "forest_types": vegetation_classifier.FOREST_TYPES,
        "note": "Types de forêts typiques du Québec avec valeur de chasse"
    }


@sentinel_engine_router.get("/reference/seasonal")
async def get_seasonal_expectations():
    """
    Get seasonal NDVI expectations for Quebec.
    """
    return {
        "seasonal_ndvi": sentinel_analyzer.SEASONAL_NDVI,
        "note": "Valeurs NDVI attendues par saison au Québec"
    }
