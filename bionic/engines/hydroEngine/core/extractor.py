"""
BIONIC™ Hydrology Engine - Data Extractor

Extraction des données hydrologiques depuis les sources WMS/WFS.
"""

import httpx
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# WMS/WFS Service URLs
GRHQ_SERVICES = {
    "wms": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer",
    "wfs": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WFSServer",
    "layers": {
        "rivers": "0",      # Cours d'eau
        "lakes": "1",       # Lacs
        "wetlands": "2",    # Milieux humides
        "watersheds": "3"   # Bassins versants
    }
}

# Cache directory
CACHE_DIR = Path("/tmp/bionic_hydro_cache")
CACHE_DIR.mkdir(exist_ok=True)


class HydroExtractor:
    """
    Extracteur de données hydrologiques.
    
    Récupère les données de cours d'eau, lacs et milieux humides
    depuis les services WMS/WFS du gouvernement du Québec.
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.wms_url = GRHQ_SERVICES["wms"]
        self.wfs_url = GRHQ_SERVICES["wfs"]
        self.layers = GRHQ_SERVICES["layers"]
    
    def _get_cache_path(self, layer: str, bbox: Dict[str, float]) -> Path:
        """Generate cache file path for a layer and bbox."""
        bbox_str = f"{bbox['min_lat']:.4f}_{bbox['min_lon']:.4f}_{bbox['max_lat']:.4f}_{bbox['max_lon']:.4f}"
        return CACHE_DIR / f"hydro_{layer}_{bbox_str}.json"
    
    async def extract_rivers(
        self,
        bbox: Dict[str, float],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract river data for a bounding box.
        
        Args:
            bbox: Bounding box with min_lat, max_lat, min_lon, max_lon
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary with river features and metadata
        """
        cache_path = self._get_cache_path("rivers", bbox)
        
        # Check cache
        if use_cache and cache_path.exists():
            try:
                with open(cache_path) as f:
                    cached = json.load(f)
                    logger.info(f"Using cached river data for bbox")
                    return cached
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        
        # Build WMS tile URL
        tile_url = self._build_wms_url(
            layer=self.layers["rivers"],
            bbox=bbox,
            width=1024,
            height=1024
        )
        
        result = {
            "layer": "rivers",
            "type": "cours_d_eau",
            "bbox": bbox,
            "tile_url": tile_url,
            "data_source": "GRHQ - Géobase du réseau hydrographique du Québec",
            "license": "CC-BY 4.0",
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "features": [],
            "statistics": {}
        }
        
        # Try to get feature count from WFS
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # GetFeature count
                wfs_params = {
                    "service": "WFS",
                    "version": "2.0.0",
                    "request": "GetFeature",
                    "typeName": "GRHQ:cours_eau",
                    "bbox": f"{bbox['min_lon']},{bbox['min_lat']},{bbox['max_lon']},{bbox['max_lat']},EPSG:4326",
                    "resultType": "hits"
                }
                
                response = await client.get(self.wfs_url, params=wfs_params)
                if response.status_code == 200:
                    # Parse number of features from response
                    text = response.text
                    if "numberMatched" in text:
                        import re
                        match = re.search(r'numberMatched="(\d+)"', text)
                        if match:
                            result["statistics"]["feature_count"] = int(match.group(1))
        except Exception as e:
            logger.warning(f"WFS query error: {e}")
            result["statistics"]["feature_count"] = "unavailable"
        
        # Cache the result
        if use_cache:
            try:
                with open(cache_path, "w") as f:
                    json.dump(result, f)
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
        
        return result
    
    async def extract_lakes(
        self,
        bbox: Dict[str, float],
        min_area_m2: float = 1000,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract lake data for a bounding box.
        
        Args:
            bbox: Bounding box
            min_area_m2: Minimum lake area in square meters
            use_cache: Whether to use cached data
        """
        cache_path = self._get_cache_path("lakes", bbox)
        
        if use_cache and cache_path.exists():
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except Exception:
                pass
        
        tile_url = self._build_wms_url(
            layer=self.layers["lakes"],
            bbox=bbox,
            width=1024,
            height=1024
        )
        
        result = {
            "layer": "lakes",
            "type": "lacs",
            "bbox": bbox,
            "tile_url": tile_url,
            "data_source": "GRHQ",
            "license": "CC-BY 4.0",
            "min_area_filter_m2": min_area_m2,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "features": [],
            "statistics": {}
        }
        
        if use_cache:
            try:
                with open(cache_path, "w") as f:
                    json.dump(result, f)
            except Exception:
                pass
        
        return result
    
    async def extract_wetlands(
        self,
        bbox: Dict[str, float],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract wetland data for a bounding box.
        
        Wetlands include marshes, swamps, peatlands, etc.
        """
        cache_path = self._get_cache_path("wetlands", bbox)
        
        if use_cache and cache_path.exists():
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except Exception:
                pass
        
        tile_url = self._build_wms_url(
            layer=self.layers["wetlands"],
            bbox=bbox,
            width=1024,
            height=1024
        )
        
        result = {
            "layer": "wetlands",
            "type": "milieux_humides",
            "bbox": bbox,
            "tile_url": tile_url,
            "data_source": "GRHQ",
            "license": "CC-BY 4.0",
            "wetland_types": [
                "marais",
                "marecage",
                "tourbiere",
                "eau_peu_profonde"
            ],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "features": [],
            "statistics": {},
            "hunting_relevance": {
                "waterfowl": "excellent",
                "moose": "high",
                "deer": "moderate"
            }
        }
        
        if use_cache:
            try:
                with open(cache_path, "w") as f:
                    json.dump(result, f)
            except Exception:
                pass
        
        return result
    
    async def extract_watersheds(
        self,
        bbox: Dict[str, float],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract watershed boundary data.
        """
        tile_url = self._build_wms_url(
            layer=self.layers["watersheds"],
            bbox=bbox,
            width=1024,
            height=1024
        )
        
        return {
            "layer": "watersheds",
            "type": "bassins_versants",
            "bbox": bbox,
            "tile_url": tile_url,
            "data_source": "GRHQ",
            "license": "CC-BY 4.0",
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "features": [],
            "statistics": {}
        }
    
    async def extract_all(
        self,
        bbox: Dict[str, float],
        include_rivers: bool = True,
        include_lakes: bool = True,
        include_wetlands: bool = True,
        include_watersheds: bool = False,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract all hydrological data for a bounding box.
        """
        result = {
            "request_id": f"hydro_extract_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "bbox": bbox,
            "data_source": "GRHQ (Données Québec)",
            "license": "CC-BY 4.0",
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "layers": {}
        }
        
        # Extract layers in parallel
        tasks = []
        layer_names = []
        
        if include_rivers:
            tasks.append(self.extract_rivers(bbox, use_cache))
            layer_names.append("rivers")
        if include_lakes:
            tasks.append(self.extract_lakes(bbox, use_cache=use_cache))
            layer_names.append("lakes")
        if include_wetlands:
            tasks.append(self.extract_wetlands(bbox, use_cache))
            layer_names.append("wetlands")
        if include_watersheds:
            tasks.append(self.extract_watersheds(bbox, use_cache))
            layer_names.append("watersheds")
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for name, layer_result in zip(layer_names, results):
                if isinstance(layer_result, Exception):
                    result["layers"][name] = {"error": str(layer_result)}
                else:
                    result["layers"][name] = layer_result
        
        return result
    
    def _build_wms_url(
        self,
        layer: str,
        bbox: Dict[str, float],
        width: int = 512,
        height: int = 512
    ) -> str:
        """Build WMS GetMap URL."""
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
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.wms_url}?{query}"
    
    def clear_cache(self, layer: Optional[str] = None) -> Dict[str, int]:
        """Clear extraction cache."""
        count = 0
        pattern = f"hydro_{layer}_*.json" if layer else "hydro_*.json"
        for f in CACHE_DIR.glob(pattern):
            f.unlink()
            count += 1
        return {"cleared": count}


# Singleton instance
hydro_extractor = HydroExtractor()
