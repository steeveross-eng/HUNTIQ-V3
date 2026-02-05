"""
BIONIC™ P1 - GeoCore Module
=============================
Module commun pour tous les moteurs géospatiaux P1.

Centralise:
- Normalisation géospatiale (CRS, formats)
- Tuilage des données
- Indexation spatiale
- Loaders pour chaque source de données

Version: 1.0.0
"""

import logging
import hashlib
import json
import math
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import os

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Standard CRS for all operations
STANDARD_CRS = "EPSG:4326"

# Earth radius in km
EARTH_RADIUS_KM = 6371.0

# Cache directory
CACHE_DIR = Path("/app/bionic/engines/geospatial/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ENUMS
# =============================================================================

class NormalizationFormat(Enum):
    """Formats de données supportés."""
    GEOJSON = "geojson"
    WKT = "wkt"
    BBOX = "bbox"
    POINT = "point"


class TileSize(Enum):
    """Tailles de tuiles supportées."""
    SMALL = 256
    MEDIUM = 512
    LARGE = 1024


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class BoundingBox:
    """Représentation d'une bounding box."""
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    
    @classmethod
    def from_point(cls, lat: float, lon: float, radius_km: float) -> "BoundingBox":
        """Crée une bbox à partir d'un point et d'un rayon."""
        # 1 degré ≈ 111 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        return cls(
            min_lat=lat - lat_delta,
            max_lat=lat + lat_delta,
            min_lon=lon - lon_delta,
            max_lon=lon + lon_delta
        )
    
    def to_wms_bbox(self) -> str:
        """Retourne la bbox au format WMS."""
        return f"{self.min_lon},{self.min_lat},{self.max_lon},{self.max_lat}"
    
    def to_overpass_bbox(self) -> str:
        """Retourne la bbox au format Overpass API."""
        return f"{self.min_lat},{self.min_lon},{self.max_lat},{self.max_lon}"
    
    @property
    def area_km2(self) -> float:
        """Calcule l'aire approximative en km²."""
        lat_diff = (self.max_lat - self.min_lat) * 111.0
        lon_diff = (self.max_lon - self.min_lon) * 111.0 * math.cos(math.radians((self.max_lat + self.min_lat) / 2))
        return abs(lat_diff * lon_diff)


@dataclass
class NormalizedData:
    """Données géospatiales normalisées."""
    data_type: str
    crs: str
    bbox: BoundingBox
    features: List[Dict[str, Any]]
    source: str
    timestamp: str
    raw_data: Optional[Dict] = None


@dataclass
class Tile:
    """Représentation d'une tuile."""
    tile_id: str
    x: int
    y: int
    z: int
    bbox: BoundingBox
    data: Optional[bytes] = None


# =============================================================================
# NORMALIZER
# =============================================================================

class GeoNormalizer:
    """
    Normalise les données géospatiales vers un format standardisé.
    """
    
    def __init__(self, target_crs: str = STANDARD_CRS):
        self.target_crs = target_crs
    
    def normalize_point(self, lat: float, lon: float) -> Dict[str, float]:
        """Normalise un point."""
        return {
            "type": "Point",
            "coordinates": [lon, lat],
            "crs": self.target_crs
        }
    
    def normalize_bbox(self, bbox: Union[BoundingBox, Dict, str]) -> BoundingBox:
        """Normalise une bounding box."""
        if isinstance(bbox, BoundingBox):
            return bbox
        
        if isinstance(bbox, str):
            parts = [float(x) for x in bbox.split(",")]
            return BoundingBox(
                min_lat=parts[1],
                max_lat=parts[3],
                min_lon=parts[0],
                max_lon=parts[2]
            )
        
        if isinstance(bbox, dict):
            return BoundingBox(
                min_lat=bbox.get("min_lat", bbox.get("south", 0)),
                max_lat=bbox.get("max_lat", bbox.get("north", 0)),
                min_lon=bbox.get("min_lon", bbox.get("west", 0)),
                max_lon=bbox.get("max_lon", bbox.get("east", 0))
            )
        
        raise ValueError(f"Cannot normalize bbox: {type(bbox)}")
    
    def normalize_geojson(self, geojson: Dict) -> NormalizedData:
        """Normalise des données GeoJSON."""
        features = geojson.get("features", [])
        
        # Extraire la bbox des features
        if features:
            all_coords = []
            for f in features:
                geom = f.get("geometry", {})
                coords = geom.get("coordinates", [])
                all_coords.extend(self._extract_coords(coords))
            
            if all_coords:
                lats = [c[1] for c in all_coords]
                lons = [c[0] for c in all_coords]
                bbox = BoundingBox(
                    min_lat=min(lats),
                    max_lat=max(lats),
                    min_lon=min(lons),
                    max_lon=max(lons)
                )
            else:
                bbox = BoundingBox(0, 0, 0, 0)
        else:
            bbox = BoundingBox(0, 0, 0, 0)
        
        return NormalizedData(
            data_type="geojson",
            crs=self.target_crs,
            bbox=bbox,
            features=features,
            source="geojson",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _extract_coords(self, coords: Any) -> List[Tuple[float, float]]:
        """Extrait les coordonnées d'une géométrie."""
        result = []
        if isinstance(coords, (list, tuple)):
            if len(coords) >= 2 and isinstance(coords[0], (int, float)):
                result.append((coords[0], coords[1]))
            else:
                for c in coords:
                    result.extend(self._extract_coords(c))
        return result
    
    def transform_coordinates(
        self,
        lat: float,
        lon: float,
        from_crs: str,
        to_crs: str = STANDARD_CRS
    ) -> Tuple[float, float]:
        """
        Transforme des coordonnées entre CRS.
        Note: Simplifié - supporte seulement EPSG:4326 pour l'instant.
        """
        if from_crs == to_crs:
            return lat, lon
        
        # TODO: Implémenter transformations CRS complètes avec pyproj si nécessaire
        logger.warning(f"CRS transformation {from_crs} -> {to_crs} not implemented, returning original")
        return lat, lon


# =============================================================================
# TILER
# =============================================================================

class GeoTiler:
    """
    Gère le tuilage des données géospatiales.
    """
    
    def __init__(self, tile_size: TileSize = TileSize.MEDIUM):
        self.tile_size = tile_size.value
    
    def create_tile_id(self, x: int, y: int, z: int) -> str:
        """Crée un identifiant unique pour une tuile."""
        return f"tile_{z}_{x}_{y}"
    
    def lat_lon_to_tile(self, lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """Convertit lat/lon en coordonnées de tuile."""
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x, y
    
    def tile_to_bbox(self, x: int, y: int, z: int) -> BoundingBox:
        """Convertit une tuile en bounding box."""
        n = 2.0 ** z
        
        lon_min = x / n * 360.0 - 180.0
        lon_max = (x + 1) / n * 360.0 - 180.0
        
        lat_max = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        lat_min = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
        
        return BoundingBox(
            min_lat=lat_min,
            max_lat=lat_max,
            min_lon=lon_min,
            max_lon=lon_max
        )
    
    def get_tiles_for_bbox(self, bbox: BoundingBox, zoom: int) -> List[Tile]:
        """Retourne toutes les tuiles couvrant une bbox."""
        min_x, max_y = self.lat_lon_to_tile(bbox.min_lat, bbox.min_lon, zoom)
        max_x, min_y = self.lat_lon_to_tile(bbox.max_lat, bbox.max_lon, zoom)
        
        tiles = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                tile_bbox = self.tile_to_bbox(x, y, zoom)
                tiles.append(Tile(
                    tile_id=self.create_tile_id(x, y, zoom),
                    x=x,
                    y=y,
                    z=zoom,
                    bbox=tile_bbox
                ))
        
        return tiles
    
    def get_optimal_zoom(self, bbox: BoundingBox) -> int:
        """Détermine le zoom optimal pour une bbox."""
        area = bbox.area_km2
        
        if area < 1:
            return 16
        elif area < 10:
            return 14
        elif area < 100:
            return 12
        elif area < 1000:
            return 10
        else:
            return 8


# =============================================================================
# SPATIAL INDEXER
# =============================================================================

class SpatialIndexer:
    """
    Index spatial simple pour les requêtes géospatiales.
    Utilise un système de grille pour l'indexation.
    """
    
    def __init__(self, grid_size: float = 0.01):  # ~1km
        self.grid_size = grid_size
        self._index: Dict[str, List[Dict]] = {}
    
    def _get_grid_key(self, lat: float, lon: float) -> str:
        """Génère une clé de grille pour une coordonnée."""
        grid_lat = int(lat / self.grid_size)
        grid_lon = int(lon / self.grid_size)
        return f"{grid_lat}_{grid_lon}"
    
    def add(self, item: Dict, lat: float, lon: float) -> None:
        """Ajoute un élément à l'index."""
        key = self._get_grid_key(lat, lon)
        if key not in self._index:
            self._index[key] = []
        self._index[key].append({**item, "_lat": lat, "_lon": lon})
    
    def query_point(self, lat: float, lon: float) -> List[Dict]:
        """Requête les éléments à une position."""
        key = self._get_grid_key(lat, lon)
        return self._index.get(key, [])
    
    def query_radius(self, lat: float, lon: float, radius_km: float) -> List[Dict]:
        """Requête les éléments dans un rayon."""
        results = []
        
        # Calculer les cellules de grille à vérifier
        grid_radius = int(radius_km / (self.grid_size * 111)) + 1
        center_lat_grid = int(lat / self.grid_size)
        center_lon_grid = int(lon / self.grid_size)
        
        for dlat in range(-grid_radius, grid_radius + 1):
            for dlon in range(-grid_radius, grid_radius + 1):
                key = f"{center_lat_grid + dlat}_{center_lon_grid + dlon}"
                for item in self._index.get(key, []):
                    dist = self._haversine(lat, lon, item["_lat"], item["_lon"])
                    if dist <= radius_km:
                        results.append(item)
        
        return results
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance entre deux points en km."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return EARTH_RADIUS_KM * c
    
    def clear(self) -> None:
        """Vide l'index."""
        self._index.clear()
    
    @property
    def size(self) -> int:
        """Retourne le nombre total d'éléments indexés."""
        return sum(len(items) for items in self._index.values())


# =============================================================================
# CACHE MANAGER
# =============================================================================

class GeoCacheManager:
    """
    Gestionnaire de cache pour les données géospatiales.
    """
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._memory_ttl_seconds = 300  # 5 minutes
    
    def _generate_cache_key(self, source: str, params: Dict) -> str:
        """Génère une clé de cache unique."""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(f"{source}:{param_str}".encode()).hexdigest()
    
    def get(self, source: str, params: Dict) -> Optional[Any]:
        """Récupère des données du cache."""
        key = self._generate_cache_key(source, params)
        
        # Check memory cache first
        if key in self._memory_cache:
            data, timestamp = self._memory_cache[key]
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()
            if age < self._memory_ttl_seconds:
                logger.debug(f"Cache hit (memory): {source}")
                return data
            else:
                del self._memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                
                # Check TTL
                cached_at = datetime.fromisoformat(cached["cached_at"])
                ttl = cached.get("ttl_seconds", 3600)
                age = (datetime.now(timezone.utc) - cached_at).total_seconds()
                
                if age < ttl:
                    logger.debug(f"Cache hit (disk): {source}")
                    # Promote to memory cache
                    self._memory_cache[key] = (cached["data"], datetime.now(timezone.utc))
                    return cached["data"]
                else:
                    cache_file.unlink()  # Remove expired cache
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        
        return None
    
    def set(
        self,
        source: str,
        params: Dict,
        data: Any,
        ttl_seconds: int = 3600
    ) -> None:
        """Stocke des données dans le cache."""
        key = self._generate_cache_key(source, params)
        
        # Memory cache
        self._memory_cache[key] = (data, datetime.now(timezone.utc))
        
        # Disk cache
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    "source": source,
                    "params": params,
                    "data": data,
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                    "ttl_seconds": ttl_seconds
                }, f)
            logger.debug(f"Cache set: {source}")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def clear(self, source: Optional[str] = None) -> int:
        """Vide le cache (tout ou par source)."""
        cleared = 0
        
        if source:
            # Clear specific source
            keys_to_remove = []
            for key, (data, _) in self._memory_cache.items():
                if source in str(key):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._memory_cache[key]
                cleared += 1
        else:
            # Clear all
            cleared = len(self._memory_cache)
            self._memory_cache.clear()
            
            # Clear disk cache
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                cleared += 1
        
        return cleared


# =============================================================================
# GEOCORE MAIN CLASS
# =============================================================================

class GeoCore:
    """
    Module central pour tous les moteurs géospatiaux P1.
    
    Usage:
        core = GeoCore()
        data = await core.load_landcover(lat, lon, radius_km)
        normalized = core.normalize(data)
    """
    
    def __init__(self):
        self.normalizer = GeoNormalizer()
        self.tiler = GeoTiler()
        self.indexer = SpatialIndexer()
        self.cache = GeoCacheManager()
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.info("BIONIC™ GeoCore initialized (v1.0.0)")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtient ou crée une session HTTP."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session
    
    async def close(self) -> None:
        """Ferme les ressources."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def get_bbox(self, lat: float, lon: float, radius_km: float) -> BoundingBox:
        """Crée une bounding box autour d'un point."""
        return BoundingBox.from_point(lat, lon, radius_km)
    
    def normalize_geojson(self, geojson: Dict) -> NormalizedData:
        """Normalise des données GeoJSON."""
        return self.normalizer.normalize_geojson(geojson)
    
    def get_tiles(self, bbox: BoundingBox, zoom: Optional[int] = None) -> List[Tile]:
        """Obtient les tuiles pour une bbox."""
        if zoom is None:
            zoom = self.tiler.get_optimal_zoom(bbox)
        return self.tiler.get_tiles_for_bbox(bbox, zoom)
    
    def index_features(self, features: List[Dict]) -> int:
        """Indexe des features géospatiales."""
        count = 0
        for feature in features:
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [])
            
            if geom.get("type") == "Point" and len(coords) >= 2:
                self.indexer.add(feature, coords[1], coords[0])
                count += 1
            elif geom.get("type") in ["LineString", "Polygon"]:
                # Index au centroïde
                all_coords = self.normalizer._extract_coords(coords)
                if all_coords:
                    avg_lon = sum(c[0] for c in all_coords) / len(all_coords)
                    avg_lat = sum(c[1] for c in all_coords) / len(all_coords)
                    self.indexer.add(feature, avg_lat, avg_lon)
                    count += 1
        
        return count
    
    def query_indexed(self, lat: float, lon: float, radius_km: float = 1.0) -> List[Dict]:
        """Requête l'index spatial."""
        return self.indexer.query_radius(lat, lon, radius_km)
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance entre deux points en km."""
        return self.indexer._haversine(lat1, lon1, lat2, lon2)


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

geo_core = GeoCore()


logger.info("BIONIC™ GeoCore module loaded")
