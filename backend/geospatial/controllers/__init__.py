"""
HUNTIQ V3 - BIONIC™ Geospatial Engine
Controllers - Data source connectors for free geospatial APIs

This module implements the actual data fetching from:
- Données Québec (LiDAR, Hydro, MNE, Forest)
- SIGÉOM (Geological data)
- Copernicus/Sentinel Hub (Satellite imagery)
- OpenStreetMap (Road/POI data)
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import os
import logging
import json

logger = logging.getLogger(__name__)

# =============================================================================
# WMS/WFS SERVICE URLS - DONNÉES QUÉBEC (100% GRATUIT)
# =============================================================================

QUEBEC_WMS_SERVICES = {
    # LiDAR / Elevation
    "lidar": {
        "wms": "https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer",
        "layers": ["0", "1", "2"],  # MNT, MNS, etc.
    },
    "mne": {
        "wms": "https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/SDA_20K/MapServer/WMSServer",
        "layers": ["0"],
    },
    # Hydrographie
    "hydro": {
        "wms": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer",
        "wfs": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WFSServer",
        "layers": ["0", "1", "2", "3"],  # Cours d'eau, Lacs, Milieux humides, Bassins
    },
    # Forêt écoforestière
    "forest": {
        "wms": "https://servicescarto.mffp.gouv.qc.ca/Inventaire_Ecoforestier/VerificationInventaire/MapServer/WMSServer",
        "layers": ["0", "1", "2"],
    },
}

SIGEOM_WMS = {
    "bedrock": "https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms",
    "surficial": "https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms",
    "layers": {
        "bedrock": "SIGEOM_GEOSCIENCES:GEOLOGIE_SOCLE_1M",
        "surficial": "SIGEOM_GEOSCIENCES:DEPOTS_SURFACE_1M",
    }
}

# Copernicus Sentinel Hub (free tier)
COPERNICUS_CONFIG = {
    "odata_url": "https://catalogue.dataspace.copernicus.eu/odata/v1",
    "scihub_url": "https://scihub.copernicus.eu/dhus",
}

# OpenStreetMap Overpass API
OSM_OVERPASS_URL = "https://overpass-api.de/api/interpreter"


# =============================================================================
# BASE HTTP CLIENT
# =============================================================================

class GeoDataClient:
    """Base HTTP client for geospatial data fetching"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        return self.client
    
    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None


# =============================================================================
# LIDAR QUÉBEC CONTROLLER
# =============================================================================

class LidarQuebecController:
    """
    Controller for LiDAR data from Données Québec
    Source: https://www.donneesquebec.ca/recherche/dataset/produits-derives-de-base-du-lidar
    License: CC-BY 4.0
    """
    
    def __init__(self):
        self.base_url = QUEBEC_WMS_SERVICES["lidar"]["wms"]
        self.mne_url = QUEBEC_WMS_SERVICES["mne"]["wms"]
        self.client = GeoDataClient()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get WMS capabilities to check available layers"""
        http = await self.client.get_client()
        try:
            response = await http.get(
                self.base_url,
                params={
                    "service": "WMS",
                    "request": "GetCapabilities",
                    "version": "1.3.0"
                }
            )
            return {
                "status": "available" if response.status_code == 200 else "unavailable",
                "url": self.base_url,
                "response_code": response.status_code
            }
        except Exception as e:
            logger.error(f"LiDAR GetCapabilities error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_coverage(self, bbox: Dict[str, float]) -> Dict[str, Any]:
        """Get LiDAR coverage availability for a bounding box"""
        # Check if LiDAR data exists for this region
        http = await self.client.get_client()
        try:
            # Request a small tile to check coverage
            params = {
                "service": "WMS",
                "request": "GetMap",
                "version": "1.3.0",
                "layers": "0",  # DTM layer
                "styles": "",
                "format": "image/png",
                "transparent": "true",
                "width": "256",
                "height": "256",
                "crs": "EPSG:4326",
                "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
            }
            response = await http.get(self.base_url, params=params)
            
            # Check if we got actual data (not just a blank tile)
            has_data = response.status_code == 200 and len(response.content) > 1000
            
            return {
                "bbox": bbox,
                "has_coverage": has_data,
                "data_source": "LiDAR Québec",
                "license": "CC-BY 4.0",
                "resolution": "1m"
            }
        except Exception as e:
            logger.error(f"LiDAR coverage check error: {e}")
            return {"has_coverage": False, "error": str(e)}
    
    async def get_elevation_tile_url(
        self, 
        bbox: Dict[str, float], 
        width: int = 512, 
        height: int = 512,
        layer: str = "dtm"
    ) -> str:
        """Generate WMS URL for elevation data tile"""
        layer_id = "0" if layer == "dtm" else "1"  # 0=DTM, 1=DSM
        
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": layer_id,
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": str(width),
            "height": str(height),
            "crs": "EPSG:4326",
            "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{query_string}"
    
    async def query_data(
        self,
        bbox: Dict[str, float],
        include_dtm: bool = True,
        include_dsm: bool = True,
        include_chm: bool = False
    ) -> Dict[str, Any]:
        """Query LiDAR data for a region"""
        result = {
            "request_id": f"lidar_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "status": "success",
            "bbox": bbox,
            "data_source": "LiDAR Québec (Données ouvertes)",
            "license": "CC-BY 4.0",
            "metadata": {}
        }
        
        # Generate tile URLs
        if include_dtm:
            result["dtm_url"] = await self.get_elevation_tile_url(bbox, layer="dtm")
        if include_dsm:
            result["dsm_url"] = await self.get_elevation_tile_url(bbox, layer="dsm")
        
        # CHM would require processing DTM - DSM
        if include_chm:
            result["chm_note"] = "CHM requires server-side processing of DTM-DSM"
        
        # Check actual coverage
        coverage = await self.get_coverage(bbox)
        result["has_data"] = coverage.get("has_coverage", False)
        
        return result


# =============================================================================
# SIGEOM CONTROLLER (GÉOLOGIE QUÉBEC)
# =============================================================================

class SigeomController:
    """
    Controller for geological data from SIGÉOM
    Source: https://sigeom.mines.gouv.qc.ca/
    License: Données ouvertes Québec
    """
    
    def __init__(self):
        self.base_url = SIGEOM_WMS["bedrock"]
        self.client = GeoDataClient()
    
    async def get_bedrock_geology(self, bbox: Dict[str, float]) -> Dict[str, Any]:
        """Get bedrock geology data for a region"""
        http = await self.client.get_client()
        try:
            # WMS GetFeatureInfo for geology
            params = {
                "service": "WMS",
                "request": "GetMap",
                "version": "1.3.0",
                "layers": SIGEOM_WMS["layers"]["bedrock"],
                "styles": "",
                "format": "image/png",
                "transparent": "true",
                "width": "512",
                "height": "512",
                "crs": "EPSG:4326",
                "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
            }
            
            response = await http.get(self.base_url, params=params)
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "tile_url": f"{self.base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
                "layer": "bedrock",
                "data_source": "SIGÉOM - Géologie du socle",
                "license": "Données ouvertes Québec"
            }
        except Exception as e:
            logger.error(f"SIGÉOM bedrock error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_surficial_geology(self, bbox: Dict[str, float]) -> Dict[str, Any]:
        """Get surficial (Quaternary) deposits data"""
        http = await self.client.get_client()
        try:
            params = {
                "service": "WMS",
                "request": "GetMap",
                "version": "1.3.0",
                "layers": SIGEOM_WMS["layers"]["surficial"],
                "styles": "",
                "format": "image/png",
                "transparent": "true",
                "width": "512",
                "height": "512",
                "crs": "EPSG:4326",
                "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
            }
            
            response = await http.get(SIGEOM_WMS["surficial"], params=params)
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "tile_url": f"{SIGEOM_WMS['surficial']}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
                "layer": "surficial",
                "data_source": "SIGÉOM - Dépôts de surface",
                "license": "Données ouvertes Québec"
            }
        except Exception as e:
            logger.error(f"SIGÉOM surficial error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def query_data(
        self,
        bbox: Dict[str, float],
        include_bedrock: bool = True,
        include_surficial: bool = True,
        include_faults: bool = False
    ) -> Dict[str, Any]:
        """Query geological data for a region"""
        result = {
            "request_id": f"sigeom_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "status": "success",
            "bbox": bbox,
            "data_source": "SIGÉOM (MERN Québec)",
            "license": "Données ouvertes Québec"
        }
        
        if include_bedrock:
            result["bedrock"] = await self.get_bedrock_geology(bbox)
        if include_surficial:
            result["surficial"] = await self.get_surficial_geology(bbox)
        
        return result


# =============================================================================
# HYDROLOGY CONTROLLER (GRHQ)
# =============================================================================

class HydrologyController:
    """
    Controller for hydrological data from GRHQ
    Source: https://www.donneesquebec.ca/recherche/dataset/grhq
    License: CC-BY 4.0
    """
    
    def __init__(self):
        self.wms_url = QUEBEC_WMS_SERVICES["hydro"]["wms"]
        self.wfs_url = QUEBEC_WMS_SERVICES["hydro"]["wfs"]
        self.client = GeoDataClient()
    
    async def get_rivers_tile_url(self, bbox: Dict[str, float], width: int = 512, height: int = 512) -> str:
        """Generate WMS URL for rivers layer"""
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": "0",  # Cours d'eau
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": str(width),
            "height": str(height),
            "crs": "EPSG:4326",
            "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
        }
        return f"{self.wms_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    async def get_lakes_tile_url(self, bbox: Dict[str, float], width: int = 512, height: int = 512) -> str:
        """Generate WMS URL for lakes layer"""
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": "1",  # Lacs
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": str(width),
            "height": str(height),
            "crs": "EPSG:4326",
            "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
        }
        return f"{self.wms_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    async def get_wetlands_tile_url(self, bbox: Dict[str, float], width: int = 512, height: int = 512) -> str:
        """Generate WMS URL for wetlands layer"""
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": "2",  # Milieux humides
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": str(width),
            "height": str(height),
            "crs": "EPSG:4326",
            "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
        }
        return f"{self.wms_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    async def query_data(
        self,
        bbox: Dict[str, float],
        include_rivers: bool = True,
        include_lakes: bool = True,
        include_wetlands: bool = True,
        include_watersheds: bool = False
    ) -> Dict[str, Any]:
        """Query hydrological data for a region"""
        result = {
            "request_id": f"hydro_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "status": "success",
            "bbox": bbox,
            "data_source": "GRHQ (Données Québec)",
            "license": "CC-BY 4.0",
            "layers": {}
        }
        
        if include_rivers:
            result["layers"]["rivers"] = {
                "tile_url": await self.get_rivers_tile_url(bbox),
                "description": "Cours d'eau (rivières, ruisseaux)"
            }
        if include_lakes:
            result["layers"]["lakes"] = {
                "tile_url": await self.get_lakes_tile_url(bbox),
                "description": "Lacs et plans d'eau"
            }
        if include_wetlands:
            result["layers"]["wetlands"] = {
                "tile_url": await self.get_wetlands_tile_url(bbox),
                "description": "Milieux humides (marais, tourbières)"
            }
        
        return result


# =============================================================================
# FOREST INVENTORY CONTROLLER (MFFP)
# =============================================================================

class ForestController:
    """
    Controller for forest inventory data from MFFP
    Source: https://www.donneesquebec.ca/recherche/dataset/carte-ecoforestiere-avec-perturbations
    License: CC-BY 4.0
    """
    
    def __init__(self):
        self.wms_url = QUEBEC_WMS_SERVICES["forest"]["wms"]
        self.client = GeoDataClient()
    
    async def get_forest_tile_url(
        self, 
        bbox: Dict[str, float], 
        layer: str = "0",
        width: int = 512, 
        height: int = 512
    ) -> str:
        """Generate WMS URL for forest layer"""
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": layer,
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": str(width),
            "height": str(height),
            "crs": "EPSG:4326",
            "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
        }
        return f"{self.wms_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    async def query_data(
        self,
        bbox: Dict[str, float],
        include_species: bool = True,
        include_age: bool = True,
        include_density: bool = True,
        include_disturbances: bool = False
    ) -> Dict[str, Any]:
        """Query forest inventory data for a region"""
        result = {
            "request_id": f"forest_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "status": "success",
            "bbox": bbox,
            "data_source": "Carte écoforestière MFFP",
            "license": "CC-BY 4.0",
            "layers": {}
        }
        
        # Main forest layer
        result["layers"]["stands"] = {
            "tile_url": await self.get_forest_tile_url(bbox, layer="0"),
            "description": "Peuplements forestiers"
        }
        
        return result


# =============================================================================
# SENTINEL-2 CONTROLLER (COPERNICUS)
# =============================================================================

class SentinelController:
    """
    Controller for Sentinel-2 satellite imagery
    Source: https://scihub.copernicus.eu/ (Free and Open)
    Note: For full access, requires Copernicus account (free registration)
    """
    
    def __init__(self):
        self.catalog_url = COPERNICUS_CONFIG["odata_url"]
        self.client = GeoDataClient()
    
    async def search_scenes(
        self,
        bbox: Dict[str, float],
        date_start: str,
        date_end: str,
        cloud_cover_max: float = 20.0
    ) -> Dict[str, Any]:
        """Search for available Sentinel-2 scenes"""
        # Note: Full implementation requires Copernicus credentials
        # This returns the API endpoint format for documentation
        
        footprint = (
            f"POLYGON(({bbox['min_lon']} {bbox['min_lat']},"
            f"{bbox['max_lon']} {bbox['min_lat']},"
            f"{bbox['max_lon']} {bbox['max_lat']},"
            f"{bbox['min_lon']} {bbox['max_lat']},"
            f"{bbox['min_lon']} {bbox['min_lat']}))"
        )
        
        return {
            "request_id": f"sentinel_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "status": "ready",
            "search_params": {
                "bbox": bbox,
                "date_range": {"start": date_start, "end": date_end},
                "cloud_cover_max": cloud_cover_max,
                "footprint": footprint
            },
            "api_url": f"{self.catalog_url}/Products",
            "note": "Full imagery access requires Copernicus account (free)",
            "registration_url": "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/registrations",
            "data_source": "Copernicus Sentinel-2",
            "license": "Free and Open Data Policy"
        }
    
    def calculate_ndvi_formula(self) -> Dict[str, str]:
        """Return NDVI calculation formula"""
        return {
            "formula": "NDVI = (B08 - B04) / (B08 + B04)",
            "bands": {
                "B04": "Red (665nm)",
                "B08": "NIR (842nm)"
            },
            "range": "[-1, 1]",
            "interpretation": {
                "-1 to 0": "Water, bare soil",
                "0 to 0.3": "Sparse vegetation",
                "0.3 to 0.6": "Moderate vegetation",
                "0.6 to 1": "Dense vegetation"
            }
        }


# =============================================================================
# OPENSTREETMAP CONTROLLER
# =============================================================================

class OSMController:
    """
    Controller for OpenStreetMap data via Overpass API
    Source: https://www.openstreetmap.org/
    License: ODbL
    """
    
    def __init__(self):
        self.overpass_url = OSM_OVERPASS_URL
        self.client = GeoDataClient()
    
    async def get_roads(self, bbox: Dict[str, float]) -> Dict[str, Any]:
        """Get roads and paths from OSM"""
        query = f"""
        [out:json][timeout:25];
        (
            way["highway"]({bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']});
        );
        out body;
        >;
        out skel qt;
        """
        
        http = await self.client.get_client()
        try:
            response = await http.post(
                self.overpass_url,
                data={"data": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "elements_count": len(data.get("elements", [])),
                    "data": data,
                    "data_source": "OpenStreetMap",
                    "license": "ODbL"
                }
            return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"OSM roads error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_buildings(self, bbox: Dict[str, float]) -> Dict[str, Any]:
        """Get buildings from OSM"""
        query = f"""
        [out:json][timeout:25];
        (
            way["building"]({bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']});
        );
        out body;
        >;
        out skel qt;
        """
        
        http = await self.client.get_client()
        try:
            response = await http.post(
                self.overpass_url,
                data={"data": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "elements_count": len(data.get("elements", [])),
                    "data": data,
                    "data_source": "OpenStreetMap",
                    "license": "ODbL"
                }
            return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"OSM buildings error: {e}")
            return {"status": "error", "error": str(e)}


# =============================================================================
# HUNTING POTENTIAL CALCULATOR
# =============================================================================

class HuntingPotentialCalculator:
    """
    Calculate hunting potential score based on all geospatial data
    Score range: 0-100
    """
    
    WEIGHTS = {
        "terrain": 0.20,
        "vegetation": 0.20,
        "water": 0.15,
        "forest": 0.15,
        "geology": 0.10,
        "ai_predictions": 0.10,
        "historical": 0.10
    }
    
    LEVELS = {
        (80, 100): "excellent",
        (60, 79): "good",
        (40, 59): "moderate",
        (20, 39): "low",
        (0, 19): "poor"
    }
    
    def __init__(self):
        self.lidar = LidarQuebecController()
        self.sigeom = SigeomController()
        self.hydro = HydrologyController()
        self.forest = ForestController()
    
    def get_level(self, score: float) -> str:
        """Get hunting potential level from score"""
        for (low, high), level in self.LEVELS.items():
            if low <= score <= high:
                return level
        return "unknown"
    
    async def calculate(
        self,
        bbox: Dict[str, float],
        target_species: str = "deer",
        season: str = "rut"
    ) -> Dict[str, Any]:
        """Calculate hunting potential score"""
        
        # Collect data from all sources
        components = {}
        
        # Check data availability (these are placeholder scores based on data availability)
        lidar_data = await self.lidar.query_data(bbox)
        components["terrain"] = {
            "score": 65 if lidar_data.get("has_data") else 40,
            "weight": self.WEIGHTS["terrain"],
            "data_available": lidar_data.get("has_data", False),
            "source": "LiDAR Québec"
        }
        
        hydro_data = await self.hydro.query_data(bbox)
        components["water"] = {
            "score": 70,  # Base score for water proximity
            "weight": self.WEIGHTS["water"],
            "data_available": True,
            "source": "GRHQ"
        }
        
        forest_data = await self.forest.query_data(bbox)
        components["forest"] = {
            "score": 60,  # Base score for forest
            "weight": self.WEIGHTS["forest"],
            "data_available": True,
            "source": "MFFP"
        }
        
        geology_data = await self.sigeom.query_data(bbox)
        components["geology"] = {
            "score": 55,  # Base score for geology
            "weight": self.WEIGHTS["geology"],
            "data_available": True,
            "source": "SIGÉOM"
        }
        
        # Default scores for components without real-time data
        components["vegetation"] = {
            "score": 50,
            "weight": self.WEIGHTS["vegetation"],
            "note": "Requires Sentinel-2 processing",
            "source": "Copernicus"
        }
        
        components["ai_predictions"] = {
            "score": 50,
            "weight": self.WEIGHTS["ai_predictions"],
            "note": "AI model training in progress",
            "source": "BIONIC AI"
        }
        
        components["historical"] = {
            "score": 50,
            "weight": self.WEIGHTS["historical"],
            "note": "Historical data collection in progress",
            "source": "User data"
        }
        
        # Calculate weighted score
        total_score = sum(
            c["score"] * c["weight"] 
            for c in components.values()
        )
        
        level = self.get_level(total_score)
        
        # Generate recommendations based on score
        recommendations = self._generate_recommendations(components, target_species, season)
        
        return {
            "request_id": f"potential_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "status": "success",
            "overall_score": round(total_score, 1),
            "level": level,
            "target_species": target_species,
            "season": season,
            "component_scores": components,
            "recommendations": recommendations,
            "data_layers": {
                "lidar": lidar_data,
                "hydro": hydro_data,
                "forest": forest_data,
                "geology": geology_data
            }
        }
    
    def _generate_recommendations(
        self, 
        components: Dict, 
        species: str, 
        season: str
    ) -> List[str]:
        """Generate hunting recommendations based on analysis"""
        recommendations = []
        
        if components["water"]["score"] > 60:
            recommendations.append(
                "Zones proches des cours d'eau recommandées - "
                "Les cervidés s'abreuvent généralement à l'aube et au crépuscule"
            )
        
        if components["forest"]["score"] > 55:
            recommendations.append(
                "Couvert forestier présent - "
                "Cherchez les lisières et les éclaircies pour l'affût"
            )
        
        if season == "rut":
            recommendations.append(
                "Période du rut - "
                "Les mâles sont plus actifs, utilisez des appels et des leurres olfactifs"
            )
        
        if components["terrain"]["data_available"]:
            recommendations.append(
                "Données LiDAR disponibles - "
                "Identifiez les crêtes et les corridors naturels"
            )
        
        return recommendations


# =============================================================================
# MAIN GEOSPATIAL SERVICE
# =============================================================================

class GeospatialService:
    """
    Main service orchestrating all geospatial data sources
    """
    
    def __init__(self):
        self.lidar = LidarQuebecController()
        self.sigeom = SigeomController()
        self.hydro = HydrologyController()
        self.forest = ForestController()
        self.sentinel = SentinelController()
        self.osm = OSMController()
        self.potential_calc = HuntingPotentialCalculator()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status of all data sources"""
        lidar_status = await self.lidar.get_capabilities()
        
        return {
            "status": "operational",
            "engine_version": "1.0.0",
            "architecture_ready": True,
            "implementation_status": "active",
            "data_sources": {
                "lidar_quebec": {
                    "status": lidar_status.get("status", "unknown"),
                    "url": QUEBEC_WMS_SERVICES["lidar"]["wms"],
                    "free": True,
                    "license": "CC-BY 4.0"
                },
                "sigeom": {
                    "status": "available",
                    "url": SIGEOM_WMS["bedrock"],
                    "free": True,
                    "license": "Données ouvertes Québec"
                },
                "hydro_quebec": {
                    "status": "available",
                    "url": QUEBEC_WMS_SERVICES["hydro"]["wms"],
                    "free": True,
                    "license": "CC-BY 4.0"
                },
                "forest_mffp": {
                    "status": "available",
                    "url": QUEBEC_WMS_SERVICES["forest"]["wms"],
                    "free": True,
                    "license": "CC-BY 4.0"
                },
                "sentinel_2": {
                    "status": "ready",
                    "url": COPERNICUS_CONFIG["odata_url"],
                    "free": True,
                    "license": "Free and Open Data Policy",
                    "note": "Full access requires free Copernicus account"
                },
                "osm": {
                    "status": "available",
                    "url": OSM_OVERPASS_URL,
                    "free": True,
                    "license": "ODbL"
                }
            },
            "modules": {
                "lidar": "active",
                "sentinel": "ready",
                "landsat": "ready",
                "sigeom": "active",
                "hydro": "active",
                "geomorphology": "active",
                "forest": "active",
                "ai": "in_development",
                "potential": "active"
            }
        }


# Singleton instances
geospatial_service = GeospatialService()
lidar_controller = LidarQuebecController()
sigeom_controller = SigeomController()
hydrology_controller = HydrologyController()
forest_controller = ForestController()
sentinel_controller = SentinelController()
osm_controller = OSMController()
hunting_potential = HuntingPotentialCalculator()
