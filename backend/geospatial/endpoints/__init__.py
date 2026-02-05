"""
HUNTIQ V3 - BIONIC™ Geospatial Engine
Backend Endpoints - API routes for geospatial data

This module defines all API endpoints for the geospatial engine.
Connected to real data sources from Données Québec, SIGÉOM, Copernicus.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from ..models import (
    # Request models
    LidarDataRequest, SentinelDataRequest, LandsatDataRequest,
    SigeomDataRequest, HydrologyDataRequest, GeomorphologyRequest,
    ForestDataRequest, AIPredictionRequest, HuntingPotentialRequest,
    BoundingBox, GeoCoordinate,
    # Response models
    LidarDataResponse, SentinelDataResponse, LandsatDataResponse,
    SigeomDataResponse, HydrologyDataResponse, GeomorphologyResponse,
    ForestDataResponse, AIPredictionResponse, HuntingPotentialResponse,
)

from ..controllers import (
    geospatial_service,
    lidar_controller,
    sigeom_controller,
    hydrology_controller,
    forest_controller,
    sentinel_controller,
    osm_controller,
    hunting_potential,
)
from ..controllers.weather_controller import weather_controller

# Create router for geospatial endpoints
geospatial_router = APIRouter(prefix="/api/geospatial", tags=["Geospatial Engine"])


# =============================================================================
# HEALTH & STATUS ENDPOINTS
# =============================================================================

@geospatial_router.get("/status")
async def get_geospatial_status():
    """
    Get status of geospatial engine and data sources.
    
    Returns availability status of each data source.
    """
    return await geospatial_service.get_status()


@geospatial_router.get("/data-sources")
async def list_data_sources():
    """
    List all available free geospatial data sources.
    
    Provides URLs, licenses, and coverage information.
    """
    return {
        "sources": [
            {
                "id": "lidar_quebec",
                "name": "LiDAR Québec",
                "provider": "Gouvernement du Québec",
                "url": "https://www.donneesquebec.ca/recherche/dataset/produits-derives-de-base-du-lidar",
                "license": "Creative Commons CC-BY 4.0",
                "coverage": "Zones urbaines et périurbaines du Québec",
                "resolution": "1m",
                "formats": ["LAZ", "GeoTIFF"],
                "free": True,
                "api_type": "WMS/WCS"
            },
            {
                "id": "sigeom",
                "name": "SIGÉOM - Système d'information géominière",
                "provider": "MERN Québec",
                "url": "https://sigeom.mines.gouv.qc.ca/",
                "license": "Données ouvertes Québec",
                "coverage": "Tout le Québec",
                "resolution": "Variable",
                "formats": ["Shapefile", "GeoJSON", "WMS"],
                "free": True,
                "api_type": "WMS/WFS"
            },
            {
                "id": "sentinel_2",
                "name": "Sentinel-2 MSI",
                "provider": "ESA Copernicus",
                "url": "https://scihub.copernicus.eu/dhus/",
                "license": "Free and Open Data Policy",
                "coverage": "Global",
                "resolution": "10m-60m",
                "formats": ["SAFE", "GeoTIFF"],
                "free": True,
                "api_type": "OData/REST",
                "note": "Full access requires free Copernicus account"
            },
            {
                "id": "landsat_8_9",
                "name": "Landsat 8/9",
                "provider": "USGS",
                "url": "https://earthexplorer.usgs.gov/",
                "license": "Public Domain",
                "coverage": "Global",
                "resolution": "30m",
                "formats": ["GeoTIFF"],
                "free": True,
                "api_type": "REST/STAC"
            },
            {
                "id": "hydro_quebec",
                "name": "Hydrographie Québec (GRHQ)",
                "provider": "Gouvernement du Québec",
                "url": "https://www.donneesquebec.ca/recherche/dataset/grhq",
                "license": "Creative Commons CC-BY 4.0",
                "coverage": "Tout le Québec",
                "resolution": "1:20000",
                "formats": ["Shapefile", "GeoJSON"],
                "free": True,
                "api_type": "WMS/WFS"
            },
            {
                "id": "mne_quebec",
                "name": "Modèle numérique d'élévation",
                "provider": "Gouvernement du Québec",
                "url": "https://www.donneesquebec.ca/recherche/dataset/modeles-numeriques-d-elevation",
                "license": "Creative Commons CC-BY 4.0",
                "coverage": "Tout le Québec",
                "resolution": "1m-10m",
                "formats": ["GeoTIFF"],
                "free": True,
                "api_type": "WMS/WCS"
            },
            {
                "id": "osm",
                "name": "OpenStreetMap",
                "provider": "OSM Community",
                "url": "https://www.openstreetmap.org/",
                "license": "ODbL",
                "coverage": "Global",
                "resolution": "Variable",
                "formats": ["PBF", "XML", "GeoJSON"],
                "free": True,
                "api_type": "Overpass API"
            },
            {
                "id": "mffp_forest",
                "name": "Inventaire forestier MFFP",
                "provider": "MFFP Québec",
                "url": "https://www.donneesquebec.ca/recherche/dataset/carte-ecoforestiere-avec-perturbations",
                "license": "Creative Commons CC-BY 4.0",
                "coverage": "Forêts publiques du Québec",
                "resolution": "1:20000",
                "formats": ["Shapefile", "GDB"],
                "free": True,
                "api_type": "WMS"
            }
        ]
    }


# =============================================================================
# LIDAR ENDPOINTS - LiDAR Québec
# =============================================================================

@geospatial_router.post("/lidar/query")
async def query_lidar_data(request: LidarDataRequest):
    """
    Query LiDAR data from Données Québec.
    
    Returns DTM, DSM, and CHM tile URLs for the specified bounding box.
    
    **Data Source:** https://www.donneesquebec.ca/
    **License:** CC-BY 4.0
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    result = await lidar_controller.query_data(
        bbox=bbox_dict,
        include_dtm=request.include_dtm,
        include_dsm=request.include_dsm,
        include_chm=request.include_chm
    )
    
    return result


@geospatial_router.get("/lidar/coverage")
async def get_lidar_coverage(
    min_lat: float = Query(..., description="Minimum latitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    min_lon: float = Query(..., description="Minimum longitude"),
    max_lon: float = Query(..., description="Maximum longitude")
):
    """Get LiDAR coverage availability for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await lidar_controller.get_coverage(bbox)


@geospatial_router.get("/lidar/tiles")
async def list_lidar_tiles(
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None
):
    """List available LiDAR tiles for a region."""
    if all([min_lat, max_lat, min_lon, max_lon]):
        bbox = {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon
        }
        url = await lidar_controller.get_elevation_tile_url(bbox)
        return {
            "status": "available",
            "tile_url": url,
            "note": "Direct WMS tile URL for elevation data"
        }
    return {
        "status": "ready",
        "note": "Provide bounding box parameters to get tile URL"
    }


# =============================================================================
# SENTINEL-2 ENDPOINTS - ESA Copernicus
# =============================================================================

@geospatial_router.post("/sentinel/query")
async def query_sentinel_data(request: SentinelDataRequest):
    """
    Query Sentinel-2 imagery from Copernicus.
    
    Returns search parameters and API info for vegetation indices.
    
    **Data Source:** https://scihub.copernicus.eu/
    **License:** Free and Open Data Policy
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    result = await sentinel_controller.search_scenes(
        bbox=bbox_dict,
        date_start=request.date_start.isoformat(),
        date_end=request.date_end.isoformat(),
        cloud_cover_max=request.cloud_cover_max
    )
    
    # Add NDVI formula info
    result["ndvi_info"] = sentinel_controller.calculate_ndvi_formula()
    
    return result


@geospatial_router.get("/sentinel/scenes")
async def list_sentinel_scenes(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    date_start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    date_end: str = Query(..., description="End date (YYYY-MM-DD)"),
    cloud_max: float = Query(20.0, description="Maximum cloud cover %")
):
    """List available Sentinel-2 scenes for a region and date range."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    
    return await sentinel_controller.search_scenes(
        bbox=bbox,
        date_start=date_start,
        date_end=date_end,
        cloud_cover_max=cloud_max
    )


@geospatial_router.get("/sentinel/indices/{scene_id}")
async def get_vegetation_indices(scene_id: str):
    """Calculate vegetation indices info for a Sentinel-2 scene."""
    return {
        "scene_id": scene_id,
        "indices": sentinel_controller.calculate_ndvi_formula(),
        "note": "Full index calculation requires downloaded scene data"
    }


# =============================================================================
# LANDSAT ENDPOINTS - USGS
# =============================================================================

@geospatial_router.post("/landsat/query")
async def query_landsat_data(request: LandsatDataRequest):
    """
    Query Landsat 8/9 imagery from USGS.
    
    **Data Source:** https://earthexplorer.usgs.gov/
    **License:** Public Domain
    """
    return {
        "request_id": f"landsat_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "ready",
        "satellite": request.satellite,
        "search_params": {
            "bbox": {
                "min_lat": request.bbox.min_lat,
                "max_lat": request.bbox.max_lat,
                "min_lon": request.bbox.min_lon,
                "max_lon": request.bbox.max_lon
            },
            "date_range": {
                "start": request.date_start.isoformat(),
                "end": request.date_end.isoformat()
            },
            "cloud_cover_max": request.cloud_cover_max
        },
        "api_url": "https://earthexplorer.usgs.gov/",
        "stac_url": "https://landsatlook.usgs.gov/stac-server",
        "note": "Full access requires USGS EarthExplorer account (free)",
        "data_source": "USGS Landsat",
        "license": "Public Domain"
    }


@geospatial_router.get("/landsat/scenes")
async def list_landsat_scenes(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    date_start: str = Query(...),
    date_end: str = Query(...),
    satellite: str = Query("landsat_8")
):
    """List available Landsat scenes for a region."""
    return {
        "status": "ready",
        "satellite": satellite,
        "stac_search_url": "https://landsatlook.usgs.gov/stac-server/search",
        "note": "Use STAC API for scene discovery"
    }


# =============================================================================
# SIGEOM ENDPOINTS - Géologie Québec
# =============================================================================

@geospatial_router.post("/sigeom/query")
async def query_sigeom_data(request: SigeomDataRequest):
    """
    Query geological data from SIGÉOM.
    
    Returns bedrock geology, surficial deposits, and fault lines.
    
    **Data Source:** https://sigeom.mines.gouv.qc.ca/
    **License:** Données ouvertes Québec
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    return await sigeom_controller.query_data(
        bbox=bbox_dict,
        include_bedrock=request.include_bedrock,
        include_surficial=request.include_surficial,
        include_faults=request.include_faults
    )


@geospatial_router.get("/sigeom/bedrock")
async def get_bedrock_geology(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get bedrock geology for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await sigeom_controller.get_bedrock_geology(bbox)


@geospatial_router.get("/sigeom/surficial")
async def get_surficial_geology(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get surficial geology (Quaternary deposits) for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await sigeom_controller.get_surficial_geology(bbox)


# =============================================================================
# HYDROLOGY ENDPOINTS - Données ouvertes Québec
# =============================================================================

@geospatial_router.post("/hydro/query")
async def query_hydrology_data(request: HydrologyDataRequest):
    """
    Query hydrological data from Données Québec.
    
    Returns rivers, lakes, wetlands, and watersheds.
    
    **Data Source:** https://www.donneesquebec.ca/
    **License:** CC-BY 4.0
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    return await hydrology_controller.query_data(
        bbox=bbox_dict,
        include_rivers=request.include_rivers,
        include_lakes=request.include_lakes,
        include_wetlands=request.include_wetlands,
        include_watersheds=request.include_watersheds
    )


@geospatial_router.get("/hydro/rivers")
async def get_rivers(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    buffer_m: float = Query(100, description="Buffer distance in meters")
):
    """Get rivers and streams for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    tile_url = await hydrology_controller.get_rivers_tile_url(bbox)
    return {
        "status": "available",
        "tile_url": tile_url,
        "data_source": "GRHQ - Cours d'eau",
        "license": "CC-BY 4.0"
    }


@geospatial_router.get("/hydro/lakes")
async def get_lakes(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    min_area_m2: float = Query(1000, description="Minimum lake area in m²")
):
    """Get lakes and ponds for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    tile_url = await hydrology_controller.get_lakes_tile_url(bbox)
    return {
        "status": "available",
        "tile_url": tile_url,
        "data_source": "GRHQ - Lacs",
        "license": "CC-BY 4.0"
    }


@geospatial_router.get("/hydro/wetlands")
async def get_wetlands(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get wetlands for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    tile_url = await hydrology_controller.get_wetlands_tile_url(bbox)
    return {
        "status": "available",
        "tile_url": tile_url,
        "data_source": "GRHQ - Milieux humides",
        "license": "CC-BY 4.0"
    }


# =============================================================================
# GEOMORPHOLOGY ENDPOINTS - Terrain Analysis
# =============================================================================

@geospatial_router.post("/geomorph/analyze")
async def analyze_geomorphology(request: GeomorphologyRequest):
    """
    Perform geomorphological analysis.
    
    Calculates slope, aspect, curvature, TPI, and TWI from DEM data.
    
    **Derived from:** MNE Québec, LiDAR
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    # Get elevation data as base
    lidar_data = await lidar_controller.query_data(bbox_dict)
    
    return {
        "request_id": f"geomorph_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "success",
        "elevation_source": lidar_data,
        "analysis": {
            "slope": {
                "note": "Calculated from DEM gradient",
                "optimal_hunting": "5-15 degrees"
            },
            "aspect": {
                "note": "Slope direction (N/S/E/W)",
                "favorable": "South-facing slopes (thermal advantage)"
            },
            "tpi": {
                "note": "Topographic Position Index",
                "valleys": "Negative TPI (wildlife corridors)",
                "ridges": "Positive TPI (vantage points)"
            },
            "twi": {
                "note": "Topographic Wetness Index",
                "high_values": "Water accumulation areas"
            }
        }
    }


@geospatial_router.get("/geomorph/slope")
async def get_slope(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    units: str = Query("degrees", description="degrees or percent")
):
    """Calculate slope for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    elevation_url = await lidar_controller.get_elevation_tile_url(bbox)
    return {
        "status": "available",
        "elevation_url": elevation_url,
        "units": units,
        "note": "Slope calculation requires client-side processing of elevation data"
    }


@geospatial_router.get("/geomorph/aspect")
async def get_aspect(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Calculate aspect (slope direction) for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    elevation_url = await lidar_controller.get_elevation_tile_url(bbox)
    return {
        "status": "available",
        "elevation_url": elevation_url,
        "note": "Aspect calculation requires client-side processing of elevation data"
    }


@geospatial_router.get("/geomorph/features")
async def identify_terrain_features(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Identify terrain features (ridges, valleys, saddles)."""
    return {
        "status": "available",
        "features": [
            {"type": "ridge", "hunting_use": "Vantage point for observation"},
            {"type": "valley", "hunting_use": "Wildlife movement corridor"},
            {"type": "saddle", "hunting_use": "Natural crossing point"},
            {"type": "bench", "hunting_use": "Bedding area for deer"}
        ],
        "note": "Feature identification requires elevation data analysis"
    }


# =============================================================================
# FOREST ENDPOINTS - MFFP Québec
# =============================================================================

@geospatial_router.post("/forest/query")
async def query_forest_data(request: ForestDataRequest):
    """
    Query forest inventory data from MFFP.
    
    Returns forest stands, species composition, and age classes.
    
    **Data Source:** https://www.donneesquebec.ca/
    **License:** CC-BY 4.0
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    return await forest_controller.query_data(
        bbox=bbox_dict,
        include_species=request.include_species,
        include_age=request.include_age,
        include_density=request.include_density,
        include_disturbances=request.include_disturbances
    )


@geospatial_router.get("/forest/stands")
async def get_forest_stands(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get forest stands for a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    result = await forest_controller.query_data(bbox)
    return result


@geospatial_router.get("/forest/species")
async def get_species_composition(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get tree species composition for a region."""
    return {
        "status": "available",
        "common_species": {
            "EPN": {"name": "Épinette noire", "hunting_value": "Cover for moose"},
            "SAB": {"name": "Sapin baumier", "hunting_value": "Thermal cover"},
            "BOP": {"name": "Bouleau à papier", "hunting_value": "Browse for deer"},
            "PET": {"name": "Peuplier faux-tremble", "hunting_value": "Food source"},
            "ERS": {"name": "Érable à sucre", "hunting_value": "Mast production"},
            "THO": {"name": "Thuya occidental", "hunting_value": "Winter cover"}
        },
        "data_source": "Carte écoforestière MFFP",
        "license": "CC-BY 4.0"
    }


@geospatial_router.get("/forest/age")
async def get_forest_age(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get forest age class distribution for a region."""
    return {
        "status": "available",
        "age_classes": {
            "10": "Régénération (0-20 ans) - Jeune repousse",
            "30": "Jeune (20-40 ans) - Perchis",
            "50": "Intermédiaire (40-60 ans) - Jeune futaie",
            "70": "Mature (60-80 ans) - Futaie",
            "90": "Vieux (80+ ans) - Vieille futaie"
        },
        "hunting_relevance": {
            "best_for_deer": "Edges between young and mature stands",
            "best_for_moose": "Regenerating areas with browse",
            "best_for_bear": "Mature forests with mast"
        },
        "data_source": "Carte écoforestière MFFP",
        "license": "CC-BY 4.0"
    }


# =============================================================================
# AI PREDICTION ENDPOINTS - Hunting corridors & zones
# =============================================================================

@geospatial_router.post("/ai/predict")
async def predict_hunting_zones(request: AIPredictionRequest):
    """
    AI-based prediction of hunting zones and corridors.
    
    Uses geospatial data to predict animal movement patterns,
    feeding zones, and bedding areas.
    
    **Note:** Full AI model training in progress
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    return {
        "request_id": f"ai_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "status": "active",
        "target_species": request.target_species,
        "season": request.season,
        "predictions": {
            "corridors": {
                "status": "model_training",
                "description": "Predicted animal movement corridors",
                "factors": ["Terrain", "Water proximity", "Forest edges"]
            },
            "feeding_zones": {
                "status": "model_training",
                "description": "Predicted feeding areas",
                "factors": ["NDVI", "Forest type", "Mast production"]
            },
            "bedding_zones": {
                "status": "model_training",
                "description": "Predicted bedding areas",
                "factors": ["Slope", "Cover density", "South exposure"]
            }
        },
        "confidence_score": 0.0,
        "note": "AI models are being trained on Quebec hunting data"
    }


@geospatial_router.get("/ai/corridors")
async def get_movement_corridors(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    species: str = Query(..., description="Target species"),
    season: str = Query(..., description="Hunting season")
):
    """Predict animal movement corridors."""
    return {
        "status": "active",
        "species": species,
        "season": season,
        "corridor_factors": [
            "Valleys and drainage patterns",
            "Forest edges and openings",
            "Water sources connection",
            "Saddles between ridges"
        ],
        "note": "Full corridor prediction requires trained AI model"
    }


@geospatial_router.get("/ai/feeding-zones")
async def get_feeding_zones(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    species: str = Query(...),
    season: str = Query(...)
):
    """Predict feeding zones."""
    return {
        "status": "active",
        "species": species,
        "season": season,
        "feeding_indicators": [
            "High NDVI areas (vegetation health)",
            "Deciduous stands (browse)",
            "Oak/beech presence (mast)",
            "Recent cuts (regeneration)"
        ],
        "note": "Full feeding zone prediction requires Sentinel-2 analysis"
    }


@geospatial_router.get("/ai/bedding-zones")
async def get_bedding_zones(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    species: str = Query(...)
):
    """Predict bedding areas."""
    return {
        "status": "active",
        "species": species,
        "bedding_characteristics": {
            "deer": {
                "slope": "5-15 degrees",
                "aspect": "South/Southeast",
                "cover": "Dense evergreen or thickets",
                "elevation": "Mid-slope benches"
            },
            "moose": {
                "slope": "0-10 degrees",
                "cover": "Young conifer regeneration",
                "proximity": "Near water and browse"
            },
            "bear": {
                "terrain": "Secluded areas",
                "cover": "Dense understory",
                "proximity": "Near food sources"
            }
        },
        "note": "Bedding zone prediction uses terrain and forest analysis"
    }


# =============================================================================
# HUNTING POTENTIAL ENDPOINTS - Score calculation
# =============================================================================

@geospatial_router.post("/potential/calculate")
async def calculate_hunting_potential(request: HuntingPotentialRequest):
    """
    Calculate hunting potential score (0-100).
    
    Combines all geospatial data sources to generate a comprehensive
    hunting potential analysis with recommendations.
    
    **Components:**
    - Terrain analysis (slope, aspect, elevation)
    - Vegetation health (NDVI, forest type)
    - Water proximity
    - Geological factors
    - AI predictions
    """
    bbox_dict = {
        "min_lat": request.bbox.min_lat,
        "max_lat": request.bbox.max_lat,
        "min_lon": request.bbox.min_lon,
        "max_lon": request.bbox.max_lon
    }
    
    return await hunting_potential.calculate(
        bbox=bbox_dict,
        target_species=request.target_species,
        season=request.season
    )


@geospatial_router.get("/potential/hotspots")
async def get_hunting_hotspots(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    species: str = Query(...),
    season: str = Query(...),
    limit: int = Query(10, description="Maximum number of hotspots")
):
    """Get top hunting hotspots in a region."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    
    # Calculate potential and extract hotspots
    result = await hunting_potential.calculate(
        bbox=bbox,
        target_species=species,
        season=season
    )
    
    return {
        "status": "success",
        "species": species,
        "season": season,
        "overall_score": result["overall_score"],
        "level": result["level"],
        "hotspot_criteria": [
            "Intersection of corridors",
            "Proximity to water (< 500m)",
            "Forest edge zones",
            "South-facing slopes"
        ],
        "recommendations": result["recommendations"]
    }


@geospatial_router.get("/potential/stand-locations")
async def get_stand_locations(
    lat: float = Query(..., description="Center latitude"),
    lon: float = Query(..., description="Center longitude"),
    radius_m: float = Query(1000, description="Search radius in meters"),
    species: str = Query("deer", description="Target species")
):
    """Get recommended stand locations."""
    # Create bbox from center point and radius
    # Approximate conversion: 1 degree lat ≈ 111km, 1 degree lon varies with lat
    radius_deg = radius_m / 111000
    
    bbox = {
        "min_lat": lat - radius_deg,
        "max_lat": lat + radius_deg,
        "min_lon": lon - radius_deg * 1.3,  # Adjust for latitude
        "max_lon": lon + radius_deg * 1.3
    }
    
    result = await hunting_potential.calculate(
        bbox=bbox,
        target_species=species,
        season="rut"
    )
    
    return {
        "status": "success",
        "center": {"lat": lat, "lon": lon},
        "radius_m": radius_m,
        "species": species,
        "score": result["overall_score"],
        "stand_recommendations": [
            {
                "type": "Tree stand",
                "criteria": "Ridge overlooking corridor",
                "height": "15-20 feet",
                "shot_distance": "20-40 yards"
            },
            {
                "type": "Ground blind",
                "criteria": "Field edge near water",
                "concealment": "Natural vegetation"
            },
            {
                "type": "Saddle position",
                "criteria": "Low point between ridges",
                "advantage": "Funnels deer movement"
            }
        ],
        "data_layers": result.get("data_layers", {})
    }


@geospatial_router.get("/potential/components")
async def get_potential_components():
    """List all components used in hunting potential calculation."""
    return {
        "components": [
            {
                "name": "terrain_suitability",
                "weight": 0.20,
                "description": "Slope, aspect, and elevation analysis",
                "data_sources": ["lidar_quebec", "mne_quebec"],
                "optimal_values": {
                    "slope": "5-15 degrees",
                    "aspect": "South/Southwest",
                    "elevation": "Mid-slope"
                }
            },
            {
                "name": "vegetation_quality",
                "weight": 0.20,
                "description": "Vegetation health and food availability",
                "data_sources": ["sentinel_2", "mffp_forest"],
                "indicators": ["NDVI > 0.4", "Browse availability", "Mast presence"]
            },
            {
                "name": "water_proximity",
                "weight": 0.15,
                "description": "Distance to water sources",
                "data_sources": ["hydro_quebec"],
                "optimal_distance": "< 500m"
            },
            {
                "name": "forest_structure",
                "weight": 0.15,
                "description": "Forest type, age, and density",
                "data_sources": ["mffp_forest", "sentinel_2"],
                "favorable": "Mixed forest, mature with openings"
            },
            {
                "name": "geological_factors",
                "weight": 0.10,
                "description": "Soil type, drainage, mineral content",
                "data_sources": ["sigeom"],
                "relevance": "Natural mineral licks, travel ease"
            },
            {
                "name": "corridor_probability",
                "weight": 0.10,
                "description": "AI-predicted movement corridors",
                "data_sources": ["ai_model"],
                "factors": ["Terrain funnels", "Cover connectivity"]
            },
            {
                "name": "historical_data",
                "weight": 0.10,
                "description": "Historical sightings and harvest data",
                "data_sources": ["user_data"],
                "note": "Improves with user contributions"
            }
        ],
        "score_formula": "Score = Σ(component_score × weight) × 100",
        "levels": {
            "excellent": "80-100",
            "good": "60-79",
            "moderate": "40-59",
            "low": "20-39",
            "poor": "0-19"
        }
    }


# =============================================================================
# OSM DATA ENDPOINTS - Roads & Infrastructure
# =============================================================================

@geospatial_router.get("/osm/roads")
async def get_osm_roads(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get roads and paths from OpenStreetMap."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await osm_controller.get_roads(bbox)


@geospatial_router.get("/osm/buildings")
async def get_osm_buildings(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...)
):
    """Get buildings from OpenStreetMap."""
    bbox = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }
    return await osm_controller.get_buildings(bbox)


# =============================================================================
# NUTRITION MODULE ENDPOINTS - BIONIC™ Nutrition Engine
# =============================================================================

from ..controllers.nutrition_controller import nutrition_engine

@geospatial_router.get("/nutrition/species")
async def list_nutrition_species():
    """
    List all supported species for nutrition analysis.
    
    Returns species profiles with nutritional needs.
    """
    return {
        "status": "success",
        "species": nutrition_engine.list_species(),
        "module": "NutritionEngine",
        "version": nutrition_engine.VERSION
    }


@geospatial_router.get("/nutrition/species/{species_key}")
async def get_species_nutrition_profile(species_key: str):
    """
    Get nutritional needs profile for a specific species.
    
    Supported species: cerf, orignal, ours_noir (or English: deer, moose, bear)
    """
    profile = nutrition_engine.get_species_profile(species_key)
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Espèce non supportée: {species_key}. Espèces valides: cerf, orignal, ours_noir"
        )
    
    return {
        "status": "success",
        "species_key": species_key,
        "profile": profile
    }


@geospatial_router.get("/nutrition/landcover-types")
async def list_landcover_types():
    """
    List supported landcover types for nutrition classification.
    
    Each landcover type has associated nutritional values.
    """
    return {
        "status": "success",
        "landcover_types": nutrition_engine.list_landcover_types(),
        "note": "Chaque type de couverture terrestre possède un profil nutritionnel associé"
    }


@geospatial_router.post("/nutrition/analyze")
async def analyze_territory_nutrition(
    species_key: str = Query(..., description="Species key (cerf, orignal, ours_noir, deer, moose, bear)"),
    landcover_data: list = []
):
    """
    Analyze territory nutrition potential for a species.
    
    Performs deficiency detection and generates recommendations.
    
    **Example landcover_data:**
    ```json
    [
        {"type": "feuillus", "area": 5000},
        {"type": "coniferes", "area": 3000},
        {"type": "milieu_humide", "area": 1000}
    ]
    ```
    """
    try:
        result = await nutrition_engine.run(species_key, landcover_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


from pydantic import BaseModel
from typing import List, Optional

class LandcoverZone(BaseModel):
    type: str
    area: Optional[float] = None
    name: Optional[str] = None

class NutritionAnalysisRequest(BaseModel):
    species_key: str
    landcover_data: List[LandcoverZone]

@geospatial_router.post("/nutrition/full-analysis")
async def full_nutrition_analysis(request: NutritionAnalysisRequest):
    """
    Run complete nutrition analysis for a territory.
    
    **Request body:**
    - species_key: Species identifier (cerf, orignal, ours_noir)
    - landcover_data: Array of zones with type and area
    
    **Returns:**
    - Species profile
    - Classified resources with nutrition values
    - Deficiency report
    - Recommendations
    """
    try:
        landcover_dicts = [zone.dict() for zone in request.landcover_data]
        result = await nutrition_engine.run(request.species_key, landcover_dicts)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@geospatial_router.get("/modules")
async def list_bionic_modules():
    """
    List all available BIONIC™ modules.
    
    Returns module information and status.
    """
    return {
        "status": "success",
        "modules": [
            {
                "id": "nutrition",
                "name": "Nutrition Engine",
                "version": "0.1.0",
                "status": "active",
                "description": "Analyse nutritionnelle des territoires de chasse",
                "endpoints": [
                    "/api/geospatial/nutrition/species",
                    "/api/geospatial/nutrition/analyze",
                    "/api/geospatial/nutrition/full-analysis"
                ]
            },
            {
                "id": "lidar",
                "name": "LiDAR Module",
                "version": "1.0.0",
                "status": "active",
                "description": "Données d'élévation LiDAR Québec"
            },
            {
                "id": "hydro",
                "name": "Hydrology Module",
                "version": "1.0.0",
                "status": "active",
                "description": "Hydrographie GRHQ"
            },
            {
                "id": "forest",
                "name": "Forest Module",
                "version": "1.0.0",
                "status": "active",
                "description": "Inventaire forestier MFFP"
            },
            {
                "id": "sigeom",
                "name": "Geology Module",
                "version": "1.0.0",
                "status": "active",
                "description": "Données géologiques SIGÉOM"
            },
            {
                "id": "potential",
                "name": "Hunting Potential",
                "version": "1.0.0",
                "status": "active",
                "description": "Calcul du potentiel de chasse"
            }
        ],
        "upcoming": [
            {"id": "hydrologie_avancee", "name": "Hydrologie Avancée", "status": "planned"},
            {"id": "sigeom_v2", "name": "SIGÉOM V2", "status": "planned"},
            {"id": "prediction_ia", "name": "Prédiction IA", "status": "in_development"}
        ]
    }


# =============================================================================
# WEATHER ENDPOINTS - OpenWeatherMap API (Real-time)
# =============================================================================

@geospatial_router.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    units: str = Query("metric", description="Units: metric (°C) or imperial (°F)")
):
    """
    Get current weather conditions for a location.
    
    Includes hunting score calculation based on temperature, wind, pressure, etc.
    
    **Data Source:** OpenWeatherMap API
    """
    return await weather_controller.get_current_weather(lat, lon, units)


@geospatial_router.get("/weather/forecast")
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    units: str = Query("metric", description="Units: metric (°C) or imperial (°F)")
):
    """
    Get 5-day weather forecast for a location.
    
    Includes daily hunting scores and optimal hunting hours.
    
    **Data Source:** OpenWeatherMap API
    """
    return await weather_controller.get_forecast(lat, lon, units)


@geospatial_router.get("/weather/hunting-score")
async def get_hunting_weather_score(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Get hunting score based on current weather conditions.
    
    Score factors:
    - Temperature (optimal: 5-15°C)
    - Wind speed (optimal: < 10 km/h)
    - Barometric pressure
    - Cloud cover
    - Precipitation
    
    Returns score 0-100 with level and recommendations.
    """
    weather = await weather_controller.get_current_weather(lat, lon, "metric")
    
    if weather.get("status") != "success":
        return weather
    
    return {
        "status": "success",
        "location": weather.get("location"),
        "hunting_score": weather.get("hunting_score"),
        "current_conditions": {
            "temperature": weather.get("current", {}).get("temperature"),
            "humidity": weather.get("current", {}).get("humidity"),
            "wind": weather.get("wind"),
            "condition": weather.get("weather", {}).get("condition")
        },
        "timestamp": weather.get("timestamp")
    }



# =============================================================================
# WMS PROXY ENDPOINTS - BIONIC™ WMS Proxy
# =============================================================================

from fastapi.responses import Response
from ..controllers.wms_proxy_controller import wms_proxy

@geospatial_router.get("/wms/sources")
async def list_wms_sources(
    include_unavailable: bool = Query(False, description="Include sources that are down or not accessible"),
    include_auth_required: bool = Query(False, description="Include sources that require authentication credentials")
):
    """
    List WMS sources.
    
    Returns WMS services with their layers.
    - Default: Only fully available sources
    - include_auth_required=true: Also include Quebec government sources pending credentials
    - include_unavailable=true: Include sources that are completely unavailable
    """
    return {
        "status": "success",
        "sources": wms_proxy.list_sources(
            include_unavailable=include_unavailable,
            include_auth_required=include_auth_required
        ),
        "note": "Use /wms/tile/{source}/{layer} to fetch tiles. Use /wms/quebec-urls for credential requirements."
    }



@geospatial_router.get("/wms/source/{source_id}")
async def get_wms_source_info(source_id: str):
    """
    Get detailed information about a WMS source.
    """
    source = wms_proxy.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail=f"WMS source not found: {source_id}")
    
    return {
        "status": "success",
        "source_id": source_id,
        "name": source["name"],
        "base_url": source["base_url"],
        "layers": source["layers"],
        "srs": source["srs"],
        "format": source["format"],
        "version": source["version"],
        "requires_key": source.get("requires_key", False)
    }


@geospatial_router.get("/wms/tile/{source_id}/{layer}")
async def get_wms_tile(
    source_id: str,
    layer: str,
    bbox: str = Query(..., description="Bounding box: minx,miny,maxx,maxy"),
    width: int = Query(256, description="Tile width"),
    height: int = Query(256, description="Tile height"),
    transparent: bool = Query(True, description="Transparent background"),
    use_cache: bool = Query(True, description="Use tile cache")
):
    """
    Fetch a WMS tile through the proxy.
    
    This endpoint bypasses CORS restrictions by proxying WMS requests.
    Tiles are cached for 24 hours to improve performance.
    
    **Example:**
    ```
    /api/geospatial/wms/tile/sigeom/bedrock?bbox=-8000000,5800000,-7900000,5900000
    ```
    """
    result = await wms_proxy.get_tile(
        source_id=source_id,
        layer=layer,
        bbox=bbox,
        width=width,
        height=height,
        transparent=transparent,
        use_cache=use_cache
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=400 if "Unknown" in result.get("error", "") else 502,
            detail=result["error"]
        )
    
    # Return the actual image data
    return Response(
        content=result["data"],
        media_type=result.get("content_type", "image/png"),
        headers={
            "X-WMS-Source": result.get("source", "unknown"),
            "X-Cache-Hit": "true" if result.get("cached") else "false",
            "Cache-Control": "public, max-age=86400"  # 24 hours
        }
    )


@geospatial_router.get("/wms/tile-url/{source_id}/{layer}")
async def get_wms_tile_url_template(source_id: str, layer: str):
    """
    Get the tile URL template for MapLibre GL.
    
    Returns a URL with {bbox-epsg-3857} placeholder for use in MapLibre.
    """
    url = wms_proxy.build_tile_url(source_id, layer)
    if not url:
        raise HTTPException(status_code=404, detail=f"Could not build URL for {source_id}/{layer}")
    
    # Get the external URL for the proxy
    return {
        "status": "success",
        "source_id": source_id,
        "layer": layer,
        "tile_url_template": url,
        "usage_note": "Use this URL in MapLibre GL raster source with tiles array"
    }


@geospatial_router.post("/wms/cache/clear")
async def clear_wms_cache(source_id: Optional[str] = None):
    """
    Clear WMS tile cache.
    
    If source_id is provided, only clears cache for that source.
    Otherwise, clears all cached tiles.
    """
    result = wms_proxy.clear_cache(source_id)
    return {
        "status": "success",
        "message": f"Cleared {result['cleared']} cached tiles",
        "source_filter": source_id
    }


@geospatial_router.get("/wms/maplibre-config")
async def get_maplibre_wms_config():
    """
    Get ready-to-use MapLibre GL configuration for all WMS sources.
    
    Returns sources and layers configuration that can be directly
    merged into a MapLibre style document.
    """
    sources = {}
    layers = []
    
    for source_info in wms_proxy.list_sources():
        source_id = source_info["id"]
        source = wms_proxy.get_source(source_id)
        
        if source.get("requires_key"):
            continue  # Skip sources requiring API keys
        
        for layer_key in source_info["layers"]:
            layer_id = f"wms-{source_id}-{layer_key}"
            source_key = f"wms-{source_id}-{layer_key}"
            
            # Build proxy URL
            base_url = "/api/geospatial/wms/tile"
            tile_url = f"{base_url}/{source_id}/{layer_key}?bbox={{bbox-epsg-3857}}&width=256&height=256"
            
            sources[source_key] = {
                "type": "raster",
                "tiles": [tile_url],
                "tileSize": 256,
                "attribution": f"© {source['name']}"
            }
            
            layers.append({
                "id": layer_id,
                "type": "raster",
                "source": source_key,
                "paint": {
                    "raster-opacity": 0.7
                },
                "layout": {
                    "visibility": "none"  # Hidden by default
                },
                "metadata": {
                    "wms_source": source_id,
                    "wms_layer": layer_key,
                    "display_name": f"{source['name']} - {layer_key}"
                }
            })
    
    return {
        "status": "success",
        "sources": sources,
        "layers": layers,
        "usage_note": "Merge sources and layers into your MapLibre style"
    }


@geospatial_router.get("/wms/quebec-credentials-status")
async def get_quebec_credentials_status():
    """
    Check status of Quebec government WMS credentials.
    
    Returns which credentials are configured and which services they enable.
    """
    from ..controllers.wms_proxy_controller import check_quebec_credentials_status, QUEBEC_WMS_CREDENTIALS
    
    status = check_quebec_credentials_status()
    
    return {
        "status": "success",
        "credentials": status,
        "configuration_guide": {
            "mern": {
                "description": "MERN (Ministère de l'Énergie et des Ressources naturelles)",
                "services_enabled": ["LiDAR Québec", "GRHQ Hydrographie", "Limites administratives"],
                "env_variables": {
                    "QUEBEC_MERN_TOKEN": "Bearer token from MERN portal"
                },
                "portal_url": "https://www.donneesquebec.ca/",
                "auth_type": "OAuth2 Bearer Token"
            },
            "mffp": {
                "description": "MFFP (Ministère des Forêts, de la Faune et des Parcs)",
                "services_enabled": ["Inventaire écoforestier"],
                "env_variables": {
                    "QUEBEC_MFFP_TOKEN": "Bearer token from MFFP portal"
                },
                "portal_url": "https://www.donneesquebec.ca/",
                "auth_type": "OAuth2 Bearer Token"
            },
            "sigeom": {
                "description": "SIGÉOM (Système d'information géominière)",
                "services_enabled": ["Géologie du socle", "Dépôts de surface", "Failles"],
                "env_variables": {
                    "QUEBEC_SIGEOM_API_KEY": "username:password for Basic Auth"
                },
                "portal_url": "https://sigeom.mines.gouv.qc.ca/",
                "auth_type": "HTTP Basic Authentication"
            }
        }
    }


@geospatial_router.get("/wms/quebec-urls")
async def get_quebec_wms_urls():
    """
    Get complete list of Quebec government WMS/WMTS URLs needed for BIONIC™.
    
    Returns URLs organized by ministry/provider with layer details.
    """
    return {
        "status": "success",
        "title": "URLs WMS/WMTS du Gouvernement du Québec pour BIONIC™",
        "providers": {
            "mern": {
                "name": "MERN - Ministère de l'Énergie et des Ressources naturelles",
                "portal": "https://www.donneesquebec.ca/",
                "services": {
                    "lidar": {
                        "name": "LiDAR Québec - Élévation",
                        "type": "WMS",
                        "url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer",
                        "capabilities_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer?service=WMS&request=GetCapabilities",
                        "layers": {
                            "0": "DTM - Digital Terrain Model (Modèle numérique de terrain)",
                            "1": "DSM - Digital Surface Model (Modèle numérique de surface)",
                            "2": "CHM - Canopy Height Model (Modèle de hauteur du couvert)",
                            "3": "Hillshade (Ombrage)",
                            "4": "Slope (Pente)"
                        },
                        "srs": "EPSG:3857",
                        "use_cases": ["Modélisation terrain", "Analyse pente", "Couvert forestier"]
                    },
                    "grhq": {
                        "name": "GRHQ - Géobase du réseau hydrographique du Québec",
                        "type": "WMS",
                        "url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer",
                        "capabilities_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer?service=WMS&request=GetCapabilities",
                        "layers": {
                            "0": "Cours d'eau (Rivières)",
                            "1": "Plans d'eau (Lacs)",
                            "2": "Milieux humides",
                            "3": "Bassins versants",
                            "4": "Ruisseaux"
                        },
                        "srs": "EPSG:3857",
                        "use_cases": ["Corridors fauniques", "Habitat aquatique", "Zones humides"]
                    },
                    "admin": {
                        "name": "SDA - Système de découpage administratif",
                        "type": "WMS",
                        "url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
                        "layers": {
                            "0": "MRC",
                            "1": "Municipalités",
                            "2": "Régions administratives"
                        },
                        "srs": "EPSG:3857"
                    }
                },
                "auth_requirements": {
                    "type": "OAuth2 Bearer Token",
                    "token_endpoint": "https://servicescarto.mern.gouv.qc.ca/pes/token",
                    "header": "Authorization: Bearer {token}"
                }
            },
            "mffp": {
                "name": "MFFP - Ministère des Forêts, de la Faune et des Parcs",
                "portal": "https://www.donneesquebec.ca/",
                "services": {
                    "ecoforest": {
                        "name": "Inventaire écoforestier du Québec",
                        "type": "WMS",
                        "url": "https://servicescarto.mffp.gouv.qc.ca/Inventaire_Ecoforestier/VerificationInventaire/MapServer/WMSServer",
                        "capabilities_url": "https://servicescarto.mffp.gouv.qc.ca/Inventaire_Ecoforestier/VerificationInventaire/MapServer/WMSServer?service=WMS&request=GetCapabilities",
                        "layers": {
                            "0": "Peuplements forestiers",
                            "1": "Composition en espèces",
                            "2": "Classe d'âge",
                            "3": "Densité du couvert",
                            "4": "Hauteur dominante",
                            "5": "Perturbations (feux, coupes, etc.)"
                        },
                        "srs": "EPSG:3857",
                        "use_cases": ["Qualité habitat", "Nourriture gibier", "Couvert thermique"]
                    }
                },
                "auth_requirements": {
                    "type": "OAuth2 Bearer Token",
                    "token_endpoint": "https://servicescarto.mffp.gouv.qc.ca/token",
                    "header": "Authorization: Bearer {token}"
                }
            },
            "sigeom": {
                "name": "SIGÉOM - Système d'information géominière du Québec",
                "portal": "https://sigeom.mines.gouv.qc.ca/",
                "services": {
                    "geology": {
                        "name": "Cartes géologiques",
                        "type": "WMS (GeoServer)",
                        "url": "https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms",
                        "capabilities_url": "https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms?service=WMS&request=GetCapabilities",
                        "layers": {
                            "SIGEOM_GEOSCIENCES:GEOLOGIE_SOCLE_1M": "Géologie du socle rocheux (1:1M)",
                            "SIGEOM_GEOSCIENCES:DEPOTS_SURFACE_1M": "Dépôts de surface (1:1M)",
                            "SIGEOM_GEOSCIENCES:FAILLES_1M": "Failles géologiques",
                            "SIGEOM_GEOSCIENCES:GITES_MINERAUX": "Gîtes minéraux"
                        },
                        "srs": "EPSG:3857",
                        "use_cases": ["Analyse géologique", "Corridors fauniques", "Qualité du sol"]
                    }
                },
                "auth_requirements": {
                    "type": "HTTP Basic Authentication",
                    "header": "Authorization: Basic {base64(username:password)}"
                }
            }
        },
        "integration_checklist": [
            "1. Obtenir les credentials API de chaque ministère via donneesquebec.ca",
            "2. Configurer les variables d'environnement dans le backend",
            "3. Tester les endpoints GetCapabilities pour valider l'accès",
            "4. Activer les couches dans le WMSLayerSelector frontend"
        ],
        "env_variables_needed": {
            "QUEBEC_MERN_TOKEN": "Token OAuth2 pour MERN (LiDAR, GRHQ)",
            "QUEBEC_MFFP_TOKEN": "Token OAuth2 pour MFFP (Inventaire forestier)",
            "QUEBEC_SIGEOM_API_KEY": "Credentials Basic Auth pour SIGÉOM (username:password)"
        }
    }


@geospatial_router.get("/wms/sources-all")
async def list_all_wms_sources():
    """
    List ALL WMS sources including those requiring authentication.
    
    Useful for admin interface to see what sources are available
    and their authentication status.
    """
    available = wms_proxy.list_sources(include_unavailable=False, include_auth_required=False)
    auth_required = wms_proxy.list_sources(include_unavailable=False, include_auth_required=True)
    
    # Filter to get only auth_required
    auth_only = [s for s in auth_required if s["status"] == "auth_required"]
    
    return {
        "status": "success",
        "available_sources": available,
        "auth_required_sources": auth_only,
        "summary": {
            "total_available": len(available),
            "total_auth_required": len(auth_only),
            "quebec_sources_pending": [s["id"] for s in auth_only if s.get("auth_provider")]
        }
    }
