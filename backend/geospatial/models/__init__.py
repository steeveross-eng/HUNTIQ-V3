"""
HUNTIQ V3 - BIONIC™ Geospatial Engine
Backend Models - Data structures for geospatial processing

This module defines all data models for the geospatial engine.
NO IMPLEMENTATION - Architecture preparation only.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS - Data Type Classifications
# =============================================================================

class DataSourceType(str, Enum):
    """Available free geospatial data sources"""
    LIDAR_QUEBEC = "lidar_quebec"
    SIGEOM = "sigeom"
    SENTINEL_2 = "sentinel_2"
    LANDSAT_8 = "landsat_8"
    LANDSAT_9 = "landsat_9"
    HYDRO_QUEBEC = "hydro_quebec"
    MNE_QUEBEC = "mne_quebec"
    OSM = "openstreetmap"
    MFFP_FOREST = "mffp_forest"


class LayerType(str, Enum):
    """Geospatial layer types"""
    ELEVATION = "elevation"
    SLOPE = "slope"
    ASPECT = "aspect"
    VEGETATION = "vegetation"
    HYDROLOGY = "hydrology"
    GEOLOGY = "geology"
    FOREST = "forest"
    POTENTIAL = "potential"


class VegetationIndex(str, Enum):
    """Satellite vegetation indices"""
    NDVI = "ndvi"  # Normalized Difference Vegetation Index
    EVI = "evi"    # Enhanced Vegetation Index
    SAVI = "savi"  # Soil Adjusted Vegetation Index
    NDWI = "ndwi"  # Normalized Difference Water Index


class GeologyType(str, Enum):
    """Geological formations"""
    IGNEOUS = "igneous"
    SEDIMENTARY = "sedimentary"
    METAMORPHIC = "metamorphic"
    QUATERNARY_DEPOSITS = "quaternary_deposits"


class ForestType(str, Enum):
    """Forest classifications"""
    CONIFEROUS = "coniferous"
    DECIDUOUS = "deciduous"
    MIXED = "mixed"
    REGENERATION = "regeneration"


class HuntingPotentialLevel(str, Enum):
    """Hunting potential score levels"""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"           # 60-79
    MODERATE = "moderate"   # 40-59
    LOW = "low"             # 20-39
    POOR = "poor"           # 0-19


# =============================================================================
# BASE MODELS - Common structures
# =============================================================================

class GeoCoordinate(BaseModel):
    """Geographic coordinate"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude WGS84")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude WGS84")
    altitude: Optional[float] = Field(None, description="Altitude in meters")


class BoundingBox(BaseModel):
    """Geographic bounding box"""
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)
    
    def to_wkt(self) -> str:
        """Convert to WKT POLYGON format"""
        return f"POLYGON(({self.min_lon} {self.min_lat}, {self.max_lon} {self.min_lat}, {self.max_lon} {self.max_lat}, {self.min_lon} {self.max_lat}, {self.min_lon} {self.min_lat}))"


class GeoPolygon(BaseModel):
    """Geographic polygon (GeoJSON compatible)"""
    type: str = "Polygon"
    coordinates: List[List[List[float]]] = Field(..., description="GeoJSON coordinates")


class DataSourceMetadata(BaseModel):
    """Metadata for a data source"""
    source: DataSourceType
    url: str
    license: str
    last_updated: Optional[datetime] = None
    resolution: Optional[str] = None
    coverage: Optional[str] = None
    notes: Optional[str] = None


# =============================================================================
# LIDAR MODELS - LiDAR Québec (Données ouvertes)
# =============================================================================

class LidarDataRequest(BaseModel):
    """Request for LiDAR data from Données Québec"""
    bbox: BoundingBox
    resolution: float = Field(1.0, description="Resolution in meters")
    include_dsm: bool = Field(True, description="Include Digital Surface Model")
    include_dtm: bool = Field(True, description="Include Digital Terrain Model")
    include_chm: bool = Field(False, description="Include Canopy Height Model")


class LidarDataResponse(BaseModel):
    """Response containing LiDAR-derived data"""
    request_id: str
    status: str
    bbox: BoundingBox
    dtm_url: Optional[str] = None  # Digital Terrain Model
    dsm_url: Optional[str] = None  # Digital Surface Model
    chm_url: Optional[str] = None  # Canopy Height Model
    metadata: Dict[str, Any] = {}


class LidarStats(BaseModel):
    """Statistics derived from LiDAR data"""
    min_elevation: float
    max_elevation: float
    mean_elevation: float
    std_elevation: float
    min_canopy_height: Optional[float] = None
    max_canopy_height: Optional[float] = None
    canopy_cover_percent: Optional[float] = None


# =============================================================================
# SENTINEL-2 MODELS - ESA Copernicus (Free)
# =============================================================================

class SentinelDataRequest(BaseModel):
    """Request for Sentinel-2 imagery"""
    bbox: BoundingBox
    date_start: datetime
    date_end: datetime
    cloud_cover_max: float = Field(20.0, ge=0, le=100)
    indices: List[VegetationIndex] = [VegetationIndex.NDVI]
    bands: List[str] = ["B02", "B03", "B04", "B08"]  # RGB + NIR


class SentinelDataResponse(BaseModel):
    """Response containing Sentinel-2 data"""
    request_id: str
    status: str
    scene_id: Optional[str] = None
    acquisition_date: Optional[datetime] = None
    cloud_cover: Optional[float] = None
    indices: Dict[str, str] = {}  # Index name -> URL
    bands: Dict[str, str] = {}    # Band name -> URL


class VegetationAnalysis(BaseModel):
    """Vegetation analysis from satellite imagery"""
    ndvi_mean: float = Field(..., ge=-1, le=1)
    ndvi_min: float = Field(..., ge=-1, le=1)
    ndvi_max: float = Field(..., ge=-1, le=1)
    evi_mean: Optional[float] = None
    vegetation_health: str
    biomass_estimate: Optional[float] = None


# =============================================================================
# LANDSAT MODELS - USGS (Free)
# =============================================================================

class LandsatDataRequest(BaseModel):
    """Request for Landsat 8/9 imagery"""
    bbox: BoundingBox
    date_start: datetime
    date_end: datetime
    satellite: str = Field("landsat_8", pattern="^landsat_[89]$")
    cloud_cover_max: float = Field(20.0, ge=0, le=100)
    include_thermal: bool = False


class LandsatDataResponse(BaseModel):
    """Response containing Landsat data"""
    request_id: str
    status: str
    scene_id: Optional[str] = None
    satellite: str
    acquisition_date: Optional[datetime] = None
    bands: Dict[str, str] = {}


# =============================================================================
# SIGEOM MODELS - Géologie Québec (Free)
# =============================================================================

class SigeomDataRequest(BaseModel):
    """Request for SIGÉOM geological data"""
    bbox: BoundingBox
    include_bedrock: bool = True
    include_surficial: bool = True
    include_faults: bool = False


class SigeomDataResponse(BaseModel):
    """Response containing SIGÉOM data"""
    request_id: str
    status: str
    bedrock_geology: Optional[Dict[str, Any]] = None
    surficial_geology: Optional[Dict[str, Any]] = None
    faults: Optional[List[Dict[str, Any]]] = None


class GeologyAnalysis(BaseModel):
    """Geological analysis for hunting potential"""
    dominant_rock_type: GeologyType
    soil_permeability: str  # high, medium, low
    drainage_class: str
    mineral_content: Optional[Dict[str, float]] = None
    hunting_relevance: str


# =============================================================================
# HYDROLOGY MODELS - Données ouvertes Québec
# =============================================================================

class HydrologyDataRequest(BaseModel):
    """Request for hydrological data"""
    bbox: BoundingBox
    include_rivers: bool = True
    include_lakes: bool = True
    include_wetlands: bool = True
    include_watersheds: bool = False
    buffer_distance: float = Field(100.0, description="Buffer in meters")


class HydrologyDataResponse(BaseModel):
    """Response containing hydrological data"""
    request_id: str
    status: str
    rivers: Optional[Dict[str, Any]] = None
    lakes: Optional[Dict[str, Any]] = None
    wetlands: Optional[Dict[str, Any]] = None
    watersheds: Optional[Dict[str, Any]] = None


class WaterFeature(BaseModel):
    """Water feature for hunting analysis"""
    feature_type: str  # river, lake, wetland, pond
    name: Optional[str] = None
    area_m2: Optional[float] = None
    length_m: Optional[float] = None
    distance_from_point: float
    hunting_value: str  # high, medium, low


# =============================================================================
# GEOMORPHOLOGY MODELS - Terrain Analysis
# =============================================================================

class GeomorphologyRequest(BaseModel):
    """Request for geomorphological analysis"""
    bbox: BoundingBox
    calculate_slope: bool = True
    calculate_aspect: bool = True
    calculate_curvature: bool = True
    calculate_tpi: bool = True  # Topographic Position Index
    calculate_twi: bool = True  # Topographic Wetness Index


class GeomorphologyResponse(BaseModel):
    """Response containing geomorphological data"""
    request_id: str
    status: str
    slope_url: Optional[str] = None
    aspect_url: Optional[str] = None
    curvature_url: Optional[str] = None
    tpi_url: Optional[str] = None
    twi_url: Optional[str] = None
    statistics: Dict[str, Any] = {}


class TerrainFeature(BaseModel):
    """Terrain feature classification"""
    feature_type: str  # ridge, valley, saddle, peak, flat
    elevation: float
    slope_degrees: float
    aspect_degrees: float
    tpi_value: float
    hunting_significance: str


# =============================================================================
# FOREST MODELS - MFFP Québec (Free)
# =============================================================================

class ForestDataRequest(BaseModel):
    """Request for forest inventory data"""
    bbox: BoundingBox
    include_species: bool = True
    include_age: bool = True
    include_density: bool = True
    include_disturbances: bool = False


class ForestDataResponse(BaseModel):
    """Response containing forest data"""
    request_id: str
    status: str
    forest_stands: Optional[List[Dict[str, Any]]] = None
    species_composition: Optional[Dict[str, float]] = None
    age_class_distribution: Optional[Dict[str, float]] = None


class ForestStand(BaseModel):
    """Forest stand for hunting analysis"""
    stand_id: str
    forest_type: ForestType
    dominant_species: List[str]
    age_class: str
    density_class: str
    height_m: Optional[float] = None
    basal_area: Optional[float] = None
    hunting_value: str


# =============================================================================
# AI PREDICTION MODELS - Hunting corridors & zones
# =============================================================================

class AIPredictionRequest(BaseModel):
    """Request for AI-based hunting zone prediction"""
    bbox: BoundingBox
    target_species: str  # moose, deer, bear, turkey
    season: str  # pre_rut, rut, post_rut, early, late
    layers_to_include: List[LayerType] = []
    weather_conditions: Optional[Dict[str, Any]] = None


class AIPredictionResponse(BaseModel):
    """Response containing AI predictions"""
    request_id: str
    status: str
    corridors: Optional[List[Dict[str, Any]]] = None
    feeding_zones: Optional[List[Dict[str, Any]]] = None
    bedding_zones: Optional[List[Dict[str, Any]]] = None
    water_zones: Optional[List[Dict[str, Any]]] = None
    confidence_score: float = Field(..., ge=0, le=1)


class HuntingCorridor(BaseModel):
    """Predicted animal movement corridor"""
    corridor_id: str
    geometry: GeoPolygon
    corridor_type: str  # travel, escape, feeding
    probability: float = Field(..., ge=0, le=1)
    best_time: str
    species: str


class PredictionZone(BaseModel):
    """Predicted hunting zone"""
    zone_id: str
    geometry: GeoPolygon
    zone_type: str  # feeding, bedding, water, thermal
    probability: float = Field(..., ge=0, le=1)
    best_hours: List[str]
    terrain_features: List[str]


# =============================================================================
# HUNTING POTENTIAL MODELS - Final score calculation
# =============================================================================

class HuntingPotentialRequest(BaseModel):
    """Request for hunting potential score"""
    bbox: BoundingBox
    center_point: GeoCoordinate
    radius_m: float = Field(2000.0, description="Analysis radius in meters")
    target_species: str
    season: str
    include_ai_predictions: bool = True


class HuntingPotentialResponse(BaseModel):
    """Response containing hunting potential analysis"""
    request_id: str
    status: str
    overall_score: float = Field(..., ge=0, le=100)
    level: HuntingPotentialLevel
    component_scores: Dict[str, float] = {}
    recommendations: List[str] = []
    hotspots: List[Dict[str, Any]] = []
    best_stand_locations: List[Dict[str, Any]] = []


class PotentialComponent(BaseModel):
    """Component score for hunting potential"""
    name: str
    score: float = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    description: str
    data_source: DataSourceType


class HuntingHotspot(BaseModel):
    """Identified hunting hotspot"""
    hotspot_id: str
    location: GeoCoordinate
    score: float = Field(..., ge=0, le=100)
    radius_m: float
    primary_feature: str
    secondary_features: List[str]
    best_approach: str
    recommended_time: str
