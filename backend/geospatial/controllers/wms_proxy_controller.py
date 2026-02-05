"""
BIONIC™ WMS Proxy Controller
Backend proxy for WMS services to bypass CORS restrictions

This module proxies requests to Quebec government and other WMS servers
that block direct browser CORS requests.
"""

import httpx
import asyncio
import hashlib
import os
import json
from typing import Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("/tmp/bionic_wms_cache")
CACHE_DIR.mkdir(exist_ok=True)

# WMS Sources Registry
# status: "available" = working, "unavailable" = requires auth/down, "limited" = rate limited
WMS_SOURCES = {
    # SIGÉOM - Géologie Québec (requires authentication since 2024)
    "sigeom": {
        "name": "SIGÉOM",
        "base_url": "https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms",
        "layers": {
            "bedrock": "SIGEOM_GEOSCIENCES:GEOLOGIE_SOCLE_1M",
            "surficial": "SIGEOM_GEOSCIENCES:DEPOTS_SURFACE_1M",
            "faults": "SIGEOM_GEOSCIENCES:FAILLES_1M"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.1.1",
        "status": "unavailable",
        "status_reason": "Authentification requise"
    },
    # LiDAR Québec - Élévation (requires authentication since 2024)
    "lidar": {
        "name": "LiDAR Québec",
        "base_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer",
        "layers": {
            "dtm": "0",
            "dsm": "1",
            "chm": "2"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "unavailable",
        "status_reason": "Authentification requise"
    },
    # GRHQ - Hydrographie Québec (requires authentication since 2024)
    "grhq": {
        "name": "GRHQ Hydrographie",
        "base_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer",
        "layers": {
            "rivers": "0",
            "lakes": "1",
            "wetlands": "2",
            "watersheds": "3"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "unavailable",
        "status_reason": "Authentification requise"
    },
    # MFFP - Forêt Québec (requires authentication since 2024)
    "forest": {
        "name": "Inventaire forestier MFFP",
        "base_url": "https://servicescarto.mffp.gouv.qc.ca/Inventaire_Ecoforestier/VerificationInventaire/MapServer/WMSServer",
        "layers": {
            "stands": "0",
            "species": "1",
            "age": "2"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "unavailable",
        "status_reason": "Authentification requise"
    },
    # HydroSHEDS - requires authentication
    "hydrosheds": {
        "name": "HydroSHEDS",
        "base_url": "https://hydrosheds.org/arcgis/services/HydroSHEDS/HydroSHEDS/MapServer/WMSServer",
        "layers": {
            "rivers": "0",
            "basins": "1"
        },
        "srs": "EPSG:4326",
        "format": "image/png",
        "version": "1.1.1",
        "status": "unavailable",
        "status_reason": "Service non disponible"
    },
    # OSM WMS - Fully available
    "osm": {
        "name": "OpenStreetMap WMS",
        "base_url": "https://ows.terrestris.de/osm/service",
        "layers": {
            "osm": "OSM-WMS"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.1.1",
        "status": "available"
    },
    # CanVec - Natural Resources Canada - Fully available
    "canvec": {
        "name": "CanVec NRCan",
        "base_url": "https://maps.geogratis.gc.ca/wms/canvec_en",
        "layers": {
            "hydro": "hydro",
            "transport": "transport",
            "admin": "admin_boundaries"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "available"
    },
    # USGS National Map - Fully available
    "usgs": {
        "name": "USGS National Map",
        "base_url": "https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/WMSServer",
        "layers": {
            "topo": "0"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.1.1",
        "status": "available"
    },
    # NOAA Weather - requires authentication
    "noaa": {
        "name": "NOAA NowCOAST",
        "base_url": "https://nowcoast.noaa.gov/arcgis/services/nowcoast/radar_meteo_imagery_nexrad_time/MapServer/WMSServer",
        "layers": {
            "radar": "1"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "unavailable",
        "status_reason": "Accès refusé (403)"
    },
    # Sentinel Hub (requires API key for full access)
    "sentinel_hub": {
        "name": "Sentinel Hub",
        "base_url": "https://services.sentinel-hub.com/ogc/wms",
        "layers": {
            "true_color": "TRUE-COLOR-S2L2A",
            "ndvi": "NDVI"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "requires_key": True
    },
    # NASA GIBS
    "nasa_gibs": {
        "name": "NASA GIBS",
        "base_url": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi",
        "layers": {
            "modis_terra": "MODIS_Terra_CorrectedReflectance_TrueColor",
            "viirs": "VIIRS_SNPP_CorrectedReflectance_TrueColor"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.1.1"
    }
}


class WMSProxyController:
    """
    WMS Proxy Controller
    Handles proxying and caching of WMS tile requests
    """
    
    def __init__(self):
        self.sources = WMS_SOURCES
        self.cache_ttl = timedelta(hours=24)  # Cache tiles for 24 hours
        self.client_timeout = 30
    
    def get_source(self, source_id: str) -> Optional[Dict]:
        """Get WMS source configuration"""
        return self.sources.get(source_id)
    
    def list_sources(self, include_unavailable: bool = False) -> list:
        """List WMS sources
        
        Args:
            include_unavailable: If True, include sources that are not currently accessible
        
        Returns:
            List of source info dicts
        """
        sources = []
        for source_id, config in self.sources.items():
            status = config.get("status", "available")
            
            # Skip unavailable sources unless explicitly requested
            if not include_unavailable and status == "unavailable":
                continue
                
            sources.append({
                "id": source_id,
                "name": config["name"],
                "layers": list(config["layers"].keys()),
                "requires_key": config.get("requires_key", False),
                "status": status,
                "status_reason": config.get("status_reason", None)
            })
        
        return sources
    
    def get_cache_key(self, source_id: str, layer: str, bbox: str, width: int, height: int) -> str:
        """Generate cache key for a tile request"""
        key_str = f"{source_id}:{layer}:{bbox}:{width}:{height}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_cached_tile(self, cache_key: str) -> Optional[bytes]:
        """Get tile from cache if not expired"""
        cache_file = CACHE_DIR / f"{cache_key}.png"
        meta_file = CACHE_DIR / f"{cache_key}.meta"
        
        if cache_file.exists() and meta_file.exists():
            try:
                with open(meta_file) as f:
                    meta = json.load(f)
                
                cached_time = datetime.fromisoformat(meta["timestamp"])
                if datetime.now(timezone.utc) - cached_time < self.cache_ttl:
                    with open(cache_file, "rb") as f:
                        return f.read()
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        
        return None
    
    def save_to_cache(self, cache_key: str, data: bytes):
        """Save tile to cache"""
        try:
            cache_file = CACHE_DIR / f"{cache_key}.png"
            meta_file = CACHE_DIR / f"{cache_key}.meta"
            
            with open(cache_file, "wb") as f:
                f.write(data)
            
            with open(meta_file, "w") as f:
                json.dump({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "size": len(data)
                }, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    async def get_tile(
        self,
        source_id: str,
        layer: str,
        bbox: str,
        width: int = 256,
        height: int = 256,
        transparent: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get WMS tile through proxy
        
        Args:
            source_id: WMS source identifier
            layer: Layer name within the source
            bbox: Bounding box (minx,miny,maxx,maxy)
            width: Tile width
            height: Tile height
            transparent: Request transparent tiles
            use_cache: Whether to use caching
        
        Returns:
            Dict with tile data or error
        """
        source = self.get_source(source_id)
        if not source:
            return {"error": f"Unknown WMS source: {source_id}"}
        
        layer_name = source["layers"].get(layer)
        if not layer_name:
            return {"error": f"Unknown layer '{layer}' for source '{source_id}'"}
        
        # Check cache
        cache_key = self.get_cache_key(source_id, layer, bbox, width, height)
        if use_cache:
            cached = self.get_cached_tile(cache_key)
            if cached:
                return {
                    "data": cached,
                    "content_type": "image/png",
                    "cached": True,
                    "source": source["name"]
                }
        
        # Build WMS request
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": source["version"],
            "layers": layer_name,
            "styles": "",
            "format": source["format"],
            "transparent": "true" if transparent else "false",
            "width": str(width),
            "height": str(height),
        }
        
        # Handle SRS/CRS based on version
        if source["version"] == "1.3.0":
            params["crs"] = source["srs"]
        else:
            params["srs"] = source["srs"]
        
        params["bbox"] = bbox
        
        # Make request
        async with httpx.AsyncClient(timeout=self.client_timeout) as client:
            try:
                response = await client.get(
                    source["base_url"],
                    params=params,
                    headers={
                        "User-Agent": "BIONIC-GeoEngine/1.0",
                        "Accept": "image/png,image/*"
                    }
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    
                    # Check if it's actually an image
                    if "image" in content_type or len(response.content) > 100:
                        # Cache the tile
                        if use_cache:
                            self.save_to_cache(cache_key, response.content)
                        
                        return {
                            "data": response.content,
                            "content_type": "image/png",
                            "cached": False,
                            "source": source["name"]
                        }
                    else:
                        # Probably an error response
                        return {
                            "error": f"WMS returned non-image: {response.text[:200]}",
                            "status": response.status_code
                        }
                else:
                    return {
                        "error": f"WMS request failed",
                        "status": response.status_code,
                        "details": response.text[:500]
                    }
                    
            except httpx.TimeoutException:
                return {"error": "WMS request timeout"}
            except Exception as e:
                logger.error(f"WMS proxy error: {e}")
                return {"error": str(e)}
    
    def build_tile_url(
        self,
        source_id: str,
        layer: str
    ) -> Optional[str]:
        """
        Build tile URL template for MapLibre GL
        Returns URL with {bbox-epsg-3857} placeholder
        """
        source = self.get_source(source_id)
        if not source:
            return None
        
        layer_name = source["layers"].get(layer)
        if not layer_name:
            return None
        
        # Build proxy URL
        return f"/api/wms/tile/{source_id}/{layer}?bbox={{bbox-epsg-3857}}"
    
    def clear_cache(self, source_id: Optional[str] = None) -> Dict[str, int]:
        """Clear WMS cache"""
        count = 0
        for f in CACHE_DIR.glob("*.png"):
            if source_id is None or source_id in f.stem:
                f.unlink()
                meta = f.with_suffix(".meta")
                if meta.exists():
                    meta.unlink()
                count += 1
        
        return {"cleared": count}


# Singleton instance
wms_proxy = WMSProxyController()
