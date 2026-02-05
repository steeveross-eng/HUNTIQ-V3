"""
BIONIC™ WMS Proxy Controller
Backend proxy for WMS services to bypass CORS restrictions

This module proxies requests to Quebec government and other WMS servers
that block direct browser CORS requests.

AUTHENTICATION SUPPORT:
- Supports API key authentication via headers or query params
- Supports OAuth2 token authentication
- Credentials stored securely in environment variables
"""

import httpx
import asyncio
import hashlib
import os
import json
import base64
from typing import Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("/tmp/bionic_wms_cache")
CACHE_DIR.mkdir(exist_ok=True)

# =============================================================================
# QUEBEC GOVERNMENT WMS CREDENTIALS CONFIGURATION
# Store credentials in environment variables for security
# =============================================================================
QUEBEC_WMS_CREDENTIALS = {
    "mern": {
        # MERN = Ministère de l'Énergie et des Ressources naturelles
        # Services: LiDAR, GRHQ, Territoire
        "env_key": "QUEBEC_MERN_API_KEY",
        "env_token": "QUEBEC_MERN_TOKEN",
        "auth_type": "token",  # "api_key", "token", "basic", "oauth2"
        "auth_header": "Authorization",
        "auth_prefix": "Bearer",
        "token_url": "https://servicescarto.mern.gouv.qc.ca/pes/token"
    },
    "mffp": {
        # MFFP = Ministère des Forêts, de la Faune et des Parcs
        # Services: Inventaire écoforestier
        "env_key": "QUEBEC_MFFP_API_KEY",
        "env_token": "QUEBEC_MFFP_TOKEN",
        "auth_type": "token",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer",
        "token_url": "https://servicescarto.mffp.gouv.qc.ca/token"
    },
    "sigeom": {
        # SIGÉOM = Système d'information géominière
        # Services: Géologie, Dépôts, Failles
        "env_key": "QUEBEC_SIGEOM_API_KEY",
        "env_token": "QUEBEC_SIGEOM_TOKEN",
        "auth_type": "basic",  # GeoServer typically uses basic auth
        "auth_header": "Authorization",
        "auth_prefix": "Basic"
    }
}

def get_quebec_auth_headers(provider: str) -> Dict[str, str]:
    """
    Get authentication headers for Quebec government WMS services.
    
    Args:
        provider: One of "mern", "mffp", "sigeom"
    
    Returns:
        Dict with Authorization header if credentials are available
    """
    config = QUEBEC_WMS_CREDENTIALS.get(provider)
    if not config:
        return {}
    
    headers = {}
    
    if config["auth_type"] == "token":
        token = os.environ.get(config["env_token"])
        if token:
            headers[config["auth_header"]] = f"{config['auth_prefix']} {token}"
    
    elif config["auth_type"] == "basic":
        api_key = os.environ.get(config["env_key"])
        if api_key:
            # For basic auth, api_key should be "username:password"
            encoded = base64.b64encode(api_key.encode()).decode()
            headers[config["auth_header"]] = f"{config['auth_prefix']} {encoded}"
    
    elif config["auth_type"] == "api_key":
        api_key = os.environ.get(config["env_key"])
        if api_key:
            headers["X-API-Key"] = api_key
    
    return headers

def check_quebec_credentials_status() -> Dict[str, Any]:
    """
    Check which Quebec government credentials are configured.
    
    Returns:
        Dict with status for each provider
    """
    status = {}
    for provider, config in QUEBEC_WMS_CREDENTIALS.items():
        has_key = bool(os.environ.get(config.get("env_key", "")))
        has_token = bool(os.environ.get(config.get("env_token", "")))
        status[provider] = {
            "configured": has_key or has_token,
            "auth_type": config["auth_type"],
            "services": []
        }
    
    # Map services to providers
    status["mern"]["services"] = ["lidar", "grhq"]
    status["mffp"]["services"] = ["forest"]
    status["sigeom"]["services"] = ["sigeom"]
    
    return status

# =============================================================================
# WMS SOURCES REGISTRY
# =============================================================================
# status: "available" = working, "unavailable" = requires auth/down, 
#         "auth_required" = needs credentials, "limited" = rate limited
WMS_SOURCES = {
    # SIGÉOM - Géologie Québec (requires authentication)
    "sigeom": {
        "name": "SIGÉOM Géologie",
        "description": "Géologie du socle rocheux, dépôts de surface, failles - Essentiel pour analyse terrain",
        "base_url": "https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms",
        "layers": {
            "bedrock": "SIGEOM_GEOSCIENCES:GEOLOGIE_SOCLE_1M",
            "surficial": "SIGEOM_GEOSCIENCES:DEPOTS_SURFACE_1M",
            "faults": "SIGEOM_GEOSCIENCES:FAILLES_1M",
            "mineral_deposits": "SIGEOM_GEOSCIENCES:GITES_MINERAUX"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.1.1",
        "status": "auth_required",
        "auth_provider": "sigeom",
        "status_reason": "Authentification requise - Credentials API nécessaires",
        "data_source": "Ministère des Ressources naturelles du Québec",
        "use_cases": ["Analyse géologique", "Corridors fauniques", "Qualité du sol"]
    },
    # LiDAR Québec - Élévation (requires authentication)
    "lidar": {
        "name": "LiDAR Québec",
        "description": "Modèles numériques d'élévation haute résolution - Essentiel pour analyse terrain",
        "base_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer",
        "layers": {
            "dtm": "0",  # Digital Terrain Model
            "dsm": "1",  # Digital Surface Model
            "chm": "2",  # Canopy Height Model
            "hillshade": "3",
            "slope": "4"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "auth_required",
        "auth_provider": "mern",
        "status_reason": "Authentification requise - Token MERN nécessaire",
        "data_source": "MERN Québec - Données LiDAR aéroporté",
        "use_cases": ["Modélisation terrain", "Analyse pente", "Couvert forestier"]
    },
    # GRHQ - Hydrographie Québec (requires authentication)
    "grhq": {
        "name": "GRHQ Hydrographie",
        "description": "Réseau hydrographique complet du Québec - Essentiel pour corridors fauniques",
        "base_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer",
        "layers": {
            "rivers": "0",      # Cours d'eau
            "lakes": "1",       # Lacs
            "wetlands": "2",    # Milieux humides
            "watersheds": "3",  # Bassins versants
            "streams": "4"      # Ruisseaux
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "auth_required",
        "auth_provider": "mern",
        "status_reason": "Authentification requise - Token MERN nécessaire",
        "data_source": "MERN Québec - Géobase du réseau hydrographique",
        "use_cases": ["Corridors fauniques", "Habitat aquatique", "Zones humides"]
    },
    # MFFP - Forêt Québec (requires authentication)
    "forest": {
        "name": "Inventaire écoforestier MFFP",
        "description": "Inventaire forestier détaillé - Essentiel pour analyse habitat",
        "base_url": "https://servicescarto.mffp.gouv.qc.ca/Inventaire_Ecoforestier/VerificationInventaire/MapServer/WMSServer",
        "layers": {
            "stands": "0",       # Peuplements forestiers
            "species": "1",      # Composition en espèces
            "age": "2",          # Classe d'âge
            "density": "3",      # Densité du couvert
            "height": "4",       # Hauteur dominante
            "disturbance": "5"   # Perturbations
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "auth_required",
        "auth_provider": "mffp",
        "status_reason": "Authentification requise - Token MFFP nécessaire",
        "data_source": "MFFP Québec - 5e inventaire écoforestier",
        "use_cases": ["Qualité habitat", "Nourriture gibier", "Couvert thermique"]
    },
    # Données Québec ouvertes - Limites administratives
    "quebec_admin": {
        "name": "Limites administratives Québec",
        "description": "MRC, municipalités, régions administratives",
        "base_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
        "layers": {
            "mrc": "0",
            "municipalities": "1",
            "regions": "2"
        },
        "srs": "EPSG:3857",
        "format": "image/png",
        "version": "1.3.0",
        "status": "auth_required",
        "auth_provider": "mern",
        "status_reason": "Authentification requise",
        "data_source": "MERN Québec"
    },
    # OSM WMS - Fully available (fallback/reference)
    "osm": {
        "name": "OpenStreetMap WMS",
        "description": "Carte de référence OpenStreetMap",
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
        "description": "Données vectorielles Canada - Alternative gratuite",
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
        
        # Build headers with authentication if available
        headers = {
            "User-Agent": "BIONIC-GeoEngine/1.0",
            "Accept": "image/png,image/*"
        }
        
        # Add authentication headers for Quebec government services
        auth_provider = source.get("auth_provider")
        if auth_provider:
            auth_headers = get_quebec_auth_headers(auth_provider)
            if auth_headers:
                headers.update(auth_headers)
                logger.info(f"Using {auth_provider} authentication for {source_id}")
            else:
                # No credentials configured, but they are required
                if source.get("status") == "auth_required":
                    return {
                        "error": f"Authentication required for {source['name']}",
                        "auth_provider": auth_provider,
                        "message": f"Configure {QUEBEC_WMS_CREDENTIALS.get(auth_provider, {}).get('env_token', 'credentials')} environment variable"
                    }
        
        # Make request
        async with httpx.AsyncClient(timeout=self.client_timeout) as client:
            try:
                response = await client.get(
                    source["base_url"],
                    params=params,
                    headers=headers
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
