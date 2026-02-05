"""
BIONIC™ P1 - Geospatial Engines Suite
=======================================
North America Ready - Québec, Canada, USA

Moteurs géospatiaux:
1. corridorEngine - Détection de corridors fauniques
2. landcoverEngine - Classification du couvert végétal
3. nutritionEngine - Indice nutritionnel par espèce
4. populationDensityEngine - Densité de population faunique
5. huntingPressureModule - Module de pression de chasse

Sources de données (100% gratuites et publiques):
- SIGÉOM (Québec)
- CanVec (Canada) 
- NLCD (USA)
- USGS (Amérique du Nord)
- USDA (USA)
- MFFP (Québec)
- USFWS (USA)
- OSM (Global)
- NOAA (Amérique du Nord)
- NASA EarthData (Global)

Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import math

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class Region(Enum):
    """Régions nord-américaines supportées."""
    QUEBEC = "quebec"
    CANADA_OTHER = "canada_other"
    USA = "usa"
    UNKNOWN = "unknown"


class DataSource(Enum):
    """Sources de données disponibles."""
    # Québec
    SIGEOM = "sigeom"
    MFFP = "mffp"
    # Canada
    CANVEC = "canvec"
    NRCAN = "nrcan"
    # USA
    NLCD = "nlcd"
    USGS = "usgs"
    USDA = "usda"
    USFWS = "usfws"
    # Global
    OSM = "osm"
    NOAA = "noaa"
    NASA = "nasa"


class LandCoverType(Enum):
    """Types de couvert végétal."""
    DECIDUOUS_FOREST = "deciduous_forest"
    CONIFEROUS_FOREST = "coniferous_forest"
    MIXED_FOREST = "mixed_forest"
    SHRUBLAND = "shrubland"
    GRASSLAND = "grassland"
    WETLAND = "wetland"
    WATER = "water"
    AGRICULTURAL = "agricultural"
    URBAN = "urban"
    BARREN = "barren"


class CorridorType(Enum):
    """Types de corridors fauniques."""
    RIPARIAN = "riparian"  # Cours d'eau
    RIDGELINE = "ridgeline"  # Crêtes
    FOREST_EDGE = "forest_edge"  # Lisières
    VALLEY = "valley"  # Vallées
    UTILITY = "utility"  # Lignes électriques
    AGRICULTURAL_EDGE = "agricultural_edge"  # Bordures agricoles


# =============================================================================
# DATA SOURCE CONFIGURATIONS
# =============================================================================

class NorthAmericaDataSources:
    """
    Configuration des sources de données nord-américaines.
    Toutes les sources sont 100% gratuites et publiques.
    """
    
    # Québec - SIGÉOM WMS Services
    SIGEOM_WMS = {
        "base_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
        "layers": {
            "geology": "0",
            "surficial_deposits": "1",
            "bedrock": "2",
            "mining_rights": "3"
        },
        "crs": "EPSG:4326",
        "format": "image/png",
        "transparent": True
    }
    
    # Québec - MFFP Faune
    MFFP_DATA = {
        "ugaf_zones_url": "https://www.donneesquebec.ca/recherche/dataset/ugaf",
        "zec_url": "https://www.donneesquebec.ca/recherche/dataset/zec",
        "reserves_url": "https://www.donneesquebec.ca/recherche/dataset/reserves-fauniques",
        "harvest_data_url": "https://mffp.gouv.qc.ca/statistiques-chasse",
        "format": "geojson"
    }
    
    # Canada - CanVec
    CANVEC = {
        "base_url": "https://maps.geogratis.gc.ca/wms/canvec_en",
        "layers": {
            "hydrology": "waterbody,watercourse",
            "vegetation": "wooded_area",
            "transport": "road,trail",
            "landform": "contour"
        },
        "crs": "EPSG:4326",
        "format": "image/png"
    }
    
    # Canada - Natural Resources Canada
    NRCAN = {
        "dem_url": "https://maps.geogratis.gc.ca/wms/cdem_en",
        "landcover_url": "https://www.nrcan.gc.ca/maps-tools-publications/satellite-imagery-air-photos/land-cover-canada"
    }
    
    # USA - NLCD (National Land Cover Database)
    NLCD = {
        "wms_url": "https://www.mrlc.gov/geoserver/mrlc_display/wms",
        "layers": {
            "landcover_2021": "NLCD_2021_Land_Cover_L48",
            "tree_canopy": "NLCD_2021_Tree_Canopy_L48",
            "impervious": "NLCD_2021_Impervious_L48"
        },
        "classification": {
            11: "water",
            21: "developed_open",
            22: "developed_low",
            23: "developed_medium",
            24: "developed_high",
            31: "barren",
            41: "deciduous_forest",
            42: "evergreen_forest",
            43: "mixed_forest",
            52: "shrubland",
            71: "grassland",
            81: "pasture",
            82: "crops",
            90: "wetland_woody",
            95: "wetland_herbaceous"
        }
    }
    
    # USA - USGS
    USGS = {
        "elevation_api": "https://epqs.nationalmap.gov/v1/json",
        "hydro_api": "https://hydro.nationalmap.gov/arcgis/rest/services",
        "topo_wms": "https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/WMSServer"
    }
    
    # USA - USDA
    USDA = {
        "plants_api": "https://plantsdb.xyz/api",
        "soils_api": "https://SDMDataAccess.sc.egov.usda.gov/Tabular/SDMTabularService.asmx",
        "forest_inventory": "https://apps.fs.usda.gov/fia/datamart"
    }
    
    # USA - USFWS (Fish and Wildlife Service)
    USFWS = {
        "harvest_data": "https://www.fws.gov/harvestsurvey/",
        "species_data": "https://ecos.fws.gov/ecp/species",
        "refuges_api": "https://www.fws.gov/refuges/data"
    }
    
    # Global - OpenStreetMap
    OSM = {
        "overpass_api": "https://overpass-api.de/api/interpreter",
        "nominatim": "https://nominatim.openstreetmap.org",
        "tags": {
            "water": "natural=water",
            "forest": "landuse=forest",
            "farmland": "landuse=farmland",
            "road": "highway=*",
            "building": "building=*"
        }
    }
    
    # NOAA (Weather & Climate)
    NOAA = {
        "weather_api": "https://api.weather.gov",
        "climate_data": "https://www.ncdc.noaa.gov/cdo-web/api/v2"
    }
    
    # NASA EarthData
    NASA = {
        "modis_ndvi": "https://modis.gsfc.nasa.gov/data/dataprod/mod13.php",
        "landsat_api": "https://earthexplorer.usgs.gov/",
        "earthdata_api": "https://cmr.earthdata.nasa.gov/search"
    }
    
    @classmethod
    def get_sources_for_region(cls, lat: float, lon: float) -> Dict[str, List[str]]:
        """
        Retourne les sources de données disponibles pour une localisation.
        """
        region = cls.determine_region(lat, lon)
        
        sources = {
            "primary": [],
            "secondary": [],
            "global": ["osm", "noaa", "nasa"]
        }
        
        if region == Region.QUEBEC:
            sources["primary"] = ["sigeom", "mffp"]
            sources["secondary"] = ["canvec", "nrcan"]
        elif region == Region.CANADA_OTHER:
            sources["primary"] = ["canvec", "nrcan"]
            sources["secondary"] = []
        elif region == Region.USA:
            sources["primary"] = ["nlcd", "usgs", "usda", "usfws"]
            sources["secondary"] = []
        
        return sources
    
    @classmethod
    def determine_region(cls, lat: float, lon: float) -> Region:
        """
        Détermine la région nord-américaine pour des coordonnées.
        """
        # Québec bounds (approximatif)
        if 45.0 <= lat <= 62.0 and -79.5 <= lon <= -57.0:
            return Region.QUEBEC
        
        # Reste du Canada
        if 42.0 <= lat <= 83.0 and -141.0 <= lon <= -52.0:
            return Region.CANADA_OTHER
        
        # USA (continental + Alaska + Hawaii)
        if (24.0 <= lat <= 49.5 and -125.0 <= lon <= -66.0) or \
           (51.0 <= lat <= 71.5 and -180.0 <= lon <= -129.0) or \
           (18.5 <= lat <= 22.5 and -160.5 <= lon <= -154.5):
            return Region.USA
        
        return Region.UNKNOWN


# =============================================================================
# BASE GEOSPATIAL ENGINE
# =============================================================================

@dataclass
class GeospatialEngineOutput:
    """Format de sortie standardisé pour les moteurs géospatiaux."""
    engine_name: str
    engine_version: str
    analysis_id: str
    location: Dict[str, float]
    region: str
    data_sources_used: List[str]
    score: float
    level: str
    data: Dict[str, Any]
    recommendations: List[str]
    confidence: float
    from_cache: bool
    analyzed_at: str


class BaseGeospatialEngine:
    """
    Classe de base pour tous les moteurs géospatiaux P1.
    """
    
    ENGINE_NAME = "BaseGeospatialEngine"
    ENGINE_VERSION = "1.0.0"
    
    def __init__(self):
        self.data_sources = NorthAmericaDataSources()
        self._cache_namespace = "geospatial"
        logger.info(f"BIONIC™ {self.ENGINE_NAME} initialized (v{self.ENGINE_VERSION})")
    
    def _determine_region(self, lat: float, lon: float) -> Region:
        """Détermine la région pour une localisation."""
        return NorthAmericaDataSources.determine_region(lat, lon)
    
    def _get_data_sources(self, lat: float, lon: float) -> Dict[str, List[str]]:
        """Retourne les sources de données pour une localisation."""
        return NorthAmericaDataSources.get_sources_for_region(lat, lon)
    
    def _score_to_level(self, score: float) -> str:
        """Convertit un score en niveau."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "moderate"
        elif score >= 20:
            return "low"
        return "poor"
    
    async def analyze(self, lat: float, lon: float, **kwargs) -> GeospatialEngineOutput:
        """Méthode d'analyse à implémenter par les sous-classes."""
        raise NotImplementedError


# =============================================================================
# ENGINE SPECIFICATIONS (KPIs & ENDPOINTS)
# =============================================================================

ENGINE_SPECIFICATIONS = {
    "corridorEngine": {
        "description": "Détection de corridors fauniques multi-espèces",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/bionic/corridor/analyze/point",
            "GET /api/bionic/corridor/analyze/area",
            "GET /api/bionic/corridor/connectivity/{species}",
            "GET /api/bionic/corridor/bottlenecks"
        ],
        "kpis": {
            "corridor_detection_accuracy": ">85%",
            "multi_species_coverage": "8 species",
            "response_time_p95": "<500ms",
            "data_freshness": "<24h"
        },
        "output_format": {
            "corridor_score": "float (0-100)",
            "corridors_detected": "list[Corridor]",
            "connectivity_index": "float (0-1)",
            "bottlenecks": "list[Bottleneck]",
            "seasonal_variation": "dict[season, float]"
        },
        "fusion_weights": {
            "movement_engine": 0.35,
            "behavior_engine": 0.25,
            "seasonal_engine": 0.20,
            "activity_engine": 0.20
        }
    },
    "landcoverEngine": {
        "description": "Classification du couvert végétal et structure forestière",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/bionic/landcover/analyze/point",
            "GET /api/bionic/landcover/analyze/area",
            "GET /api/bionic/landcover/classification",
            "GET /api/bionic/landcover/edge-density"
        ],
        "kpis": {
            "classification_accuracy": ">90%",
            "cover_types_supported": "10 types",
            "response_time_p95": "<400ms",
            "resolution": "30m (NLCD) / 10m (SIGÉOM)"
        },
        "output_format": {
            "cover_score": "float (0-100)",
            "dominant_cover": "LandCoverType",
            "cover_composition": "dict[type, percent]",
            "edge_density_m_ha": "float",
            "thermal_cover_percent": "float",
            "structural_diversity": "float (0-1)"
        },
        "fusion_weights": {
            "species_model_engine": 0.30,
            "seasonal_engine": 0.30,
            "behavior_engine": 0.25,
            "activity_engine": 0.15
        }
    },
    "nutritionEngine": {
        "description": "Indice nutritionnel par espèce et par saison",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/bionic/nutrition/analyze/point",
            "GET /api/bionic/nutrition/food-availability/{species}",
            "GET /api/bionic/nutrition/mast-index",
            "GET /api/bionic/nutrition/browse-quality"
        ],
        "kpis": {
            "species_coverage": "8 species",
            "seasonal_accuracy": ">80%",
            "response_time_p95": "<450ms",
            "ndvi_integration": "real-time"
        },
        "output_format": {
            "nutrition_score": "float (0-100)",
            "food_availability": "str (abundant/moderate/scarce)",
            "species_nutrition": "dict[species, score]",
            "mast_index": "float (0-100)",
            "browse_quality": "float (0-100)",
            "seasonal_variation": "dict[season, score]"
        },
        "fusion_weights": {
            "seasonal_engine": 0.35,
            "species_model_engine": 0.30,
            "behavior_engine": 0.20,
            "movement_engine": 0.15
        }
    },
    "populationDensityEngine": {
        "description": "Densité de population faunique multi-annuelle",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/bionic/population/density/point",
            "GET /api/bionic/population/density/area",
            "GET /api/bionic/population/trend/{species}",
            "GET /api/bionic/population/harvest-data"
        ],
        "kpis": {
            "species_coverage": "8 species",
            "data_years": "10 years (2015-2024)",
            "response_time_p95": "<350ms",
            "regional_coverage": "Quebec, Canada, USA"
        },
        "output_format": {
            "density_score": "float (0-100)",
            "density_category": "str (high/medium/low/very_low)",
            "species_densities": "dict[species, density_per_km2]",
            "trend": "str (increasing/stable/decreasing)",
            "confidence_level": "float (0-1)",
            "harvest_pressure": "float (0-1)"
        },
        "data_sources": {
            "quebec": ["MFFP", "UGAF", "ZEC", "Reserves"],
            "canada": ["Provincial harvest data"],
            "usa": ["USFWS", "State wildlife agencies"]
        }
    },
    "huntingPressureModule": {
        "description": "Module de pression de chasse pondéré",
        "version": "1.0.0",
        "endpoints": [
            "GET /api/bionic/pressure/analyze/point",
            "GET /api/bionic/pressure/annual-trend",
            "GET /api/bionic/pressure/behavioral-impact",
            "GET /api/bionic/pressure/optimal-zones"
        ],
        "kpis": {
            "accuracy": ">85%",
            "temporal_resolution": "weekly",
            "response_time_p95": "<300ms"
        },
        "output_format": {
            "pressure_score": "float (0-100)",
            "pressure_level": "str (extreme/high/moderate/low/minimal)",
            "behavioral_impact": "float (-1 to 1)",
            "optimal_timing": "list[TimeWindow]",
            "avoidance_zones": "list[Zone]"
        }
    }
}


# Log initialization
logger.info("BIONIC™ P1 Geospatial Suite specifications loaded - North America Ready")
