"""
BIONIC™ Cache Manager
======================
Système de cache multi-niveaux pour optimiser les temps de réponse.

Niveaux de cache:
1. Mémoire (L1) - Cache rapide en RAM avec TTL court
2. Fichier (L2) - Cache persistant sur disque avec TTL long
3. Pre-fetch - Chargement anticipé des données adjacentes

Version: 1.0
"""

import json
import hashlib
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timezone, timedelta
from pathlib import Path
from functools import wraps
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)


# ============================================
# CONFIGURATION
# ============================================

CACHE_CONFIG = {
    # L1 Memory Cache
    "l1_max_size": 1000,        # Max entries
    "l1_ttl_seconds": 300,      # 5 minutes
    
    # L2 File Cache
    "l2_dir": "/tmp/bionic_cache",
    "l2_ttl_seconds": 3600,     # 1 hour
    "l2_max_files": 5000,
    
    # Pre-fetch
    "prefetch_radius_deg": 0.1,  # ~10km
    "prefetch_enabled": True,
    "prefetch_delay_ms": 100,
    
    # Namespaces TTL overrides
    "ttl_overrides": {
        "weather": 600,          # 10 min - weather changes
        "terrain": 86400,        # 24h - terrain doesn't change
        "vegetation": 3600,      # 1h - NDVI updates
        "geology": 86400,        # 24h - geology is static
        "analysis": 1800,        # 30 min - analysis results
    }
}


# ============================================
# L1 MEMORY CACHE
# ============================================

class L1MemoryCache:
    """Fast in-memory LRU cache with TTL."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def _make_key(self, namespace: str, key: str) -> str:
        """Generate cache key."""
        return f"{namespace}:{key}"
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache."""
        full_key = self._make_key(namespace, key)
        
        with self._lock:
            if full_key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            entry = self._cache[full_key]
            
            # Check TTL
            if datetime.now(timezone.utc) > entry["expires_at"]:
                del self._cache[full_key]
                self._stats["misses"] += 1
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(full_key)
            self._stats["hits"] += 1
            
            return entry["value"]
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set value in cache."""
        full_key = self._make_key(namespace, key)
        ttl = ttl or CACHE_CONFIG["ttl_overrides"].get(namespace, self.default_ttl)
        
        with self._lock:
            # Evict if at capacity
            while len(self._cache) >= self.max_size:
                oldest = next(iter(self._cache))
                del self._cache[oldest]
                self._stats["evictions"] += 1
            
            self._cache[full_key] = {
                "value": value,
                "expires_at": datetime.now(timezone.utc) + timedelta(seconds=ttl),
                "created_at": datetime.now(timezone.utc)
            }
    
    def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache."""
        full_key = self._make_key(namespace, key)
        
        with self._lock:
            if full_key in self._cache:
                del self._cache[full_key]
                return True
            return False
    
    def clear(self, namespace: Optional[str] = None) -> int:
        """Clear cache entries."""
        with self._lock:
            if namespace is None:
                count = len(self._cache)
                self._cache.clear()
                return count
            
            keys_to_delete = [
                k for k in self._cache.keys()
                if k.startswith(f"{namespace}:")
            ]
            for k in keys_to_delete:
                del self._cache[k]
            return len(keys_to_delete)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total if total > 0 else 0
            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": round(hit_rate, 3)
            }


# ============================================
# L2 FILE CACHE
# ============================================

class L2FileCache:
    """Persistent file-based cache with TTL."""
    
    def __init__(
        self,
        cache_dir: str = "/tmp/bionic_cache",
        default_ttl: int = 3600,
        max_files: int = 5000
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.max_files = max_files
        self._stats = {"hits": 0, "misses": 0, "writes": 0}
    
    def _make_path(self, namespace: str, key: str) -> Path:
        """Generate file path for cache entry."""
        # Create namespace directory
        ns_dir = self.cache_dir / namespace
        ns_dir.mkdir(exist_ok=True)
        
        # Hash long keys
        key_hash = hashlib.md5(key.encode()).hexdigest()[:16]
        return ns_dir / f"{key_hash}.json"
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from file cache."""
        path = self._make_path(namespace, key)
        
        if not path.exists():
            self._stats["misses"] += 1
            return None
        
        try:
            with open(path, "r") as f:
                entry = json.load(f)
            
            # Check TTL
            expires_at = datetime.fromisoformat(entry["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                path.unlink(missing_ok=True)
                self._stats["misses"] += 1
                return None
            
            self._stats["hits"] += 1
            return entry["value"]
            
        except Exception as e:
            logger.debug(f"L2 cache read error: {e}")
            self._stats["misses"] += 1
            return None
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set value in file cache."""
        ttl = ttl or CACHE_CONFIG["ttl_overrides"].get(namespace, self.default_ttl)
        path = self._make_path(namespace, key)
        
        try:
            entry = {
                "key": key,
                "value": value,
                "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            with open(path, "w") as f:
                json.dump(entry, f)
            
            self._stats["writes"] += 1
            
        except Exception as e:
            logger.warning(f"L2 cache write error: {e}")
    
    def delete(self, namespace: str, key: str) -> bool:
        """Delete value from file cache."""
        path = self._make_path(namespace, key)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def clear(self, namespace: Optional[str] = None) -> int:
        """Clear cache entries."""
        count = 0
        
        if namespace:
            ns_dir = self.cache_dir / namespace
            if ns_dir.exists():
                for f in ns_dir.glob("*.json"):
                    f.unlink()
                    count += 1
        else:
            for ns_dir in self.cache_dir.iterdir():
                if ns_dir.is_dir():
                    for f in ns_dir.glob("*.json"):
                        f.unlink()
                        count += 1
        
        return count
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        count = 0
        now = datetime.now(timezone.utc)
        
        for ns_dir in self.cache_dir.iterdir():
            if not ns_dir.is_dir():
                continue
            
            for path in ns_dir.glob("*.json"):
                try:
                    with open(path, "r") as f:
                        entry = json.load(f)
                    
                    expires_at = datetime.fromisoformat(entry["expires_at"])
                    if now > expires_at:
                        path.unlink()
                        count += 1
                except Exception:
                    # Remove corrupted files
                    path.unlink(missing_ok=True)
                    count += 1
        
        return count
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        file_count = sum(1 for _ in self.cache_dir.rglob("*.json"))
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0
        return {
            **self._stats,
            "file_count": file_count,
            "max_files": self.max_files,
            "hit_rate": round(hit_rate, 3)
        }


# ============================================
# CACHE MANAGER (UNIFIED)
# ============================================

class BionicCacheManager:
    """
    Unified cache manager with multi-level caching and pre-fetch.
    
    Cache hierarchy:
    1. L1 (Memory) - Fast, short TTL
    2. L2 (File) - Persistent, long TTL
    
    Pre-fetch:
    - Adjacent grid cells are pre-loaded
    - Background tasks for anticipatory caching
    """
    
    def __init__(self):
        self.l1 = L1MemoryCache(
            max_size=CACHE_CONFIG["l1_max_size"],
            default_ttl=CACHE_CONFIG["l1_ttl_seconds"]
        )
        self.l2 = L2FileCache(
            cache_dir=CACHE_CONFIG["l2_dir"],
            default_ttl=CACHE_CONFIG["l2_ttl_seconds"],
            max_files=CACHE_CONFIG["l2_max_files"]
        )
        self._prefetch_queue: List[Dict] = []
        self._prefetch_task: Optional[asyncio.Task] = None
    
    def make_geo_key(
        self,
        lat: float,
        lon: float,
        precision: int = 4
    ) -> str:
        """Create geo-based cache key."""
        return f"{round(lat, precision)}_{round(lon, precision)}"
    
    def make_bbox_key(self, bbox: Dict[str, float]) -> str:
        """Create bbox-based cache key."""
        return f"{bbox['min_lat']:.4f}_{bbox['min_lon']:.4f}_{bbox['max_lat']:.4f}_{bbox['max_lon']:.4f}"
    
    def get(
        self,
        namespace: str,
        key: str,
        promote_l2: bool = True
    ) -> Optional[Any]:
        """
        Get value from cache (L1 -> L2).
        
        Args:
            namespace: Cache namespace
            key: Cache key
            promote_l2: If found in L2, promote to L1
        """
        # Try L1 first
        value = self.l1.get(namespace, key)
        if value is not None:
            return value
        
        # Try L2
        value = self.l2.get(namespace, key)
        if value is not None and promote_l2:
            # Promote to L1
            self.l1.set(namespace, key, value)
        
        return value
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        l1_only: bool = False,
        ttl: Optional[int] = None
    ) -> None:
        """
        Set value in cache (L1 + L2).
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            l1_only: Only store in L1 (volatile)
            ttl: Custom TTL override
        """
        self.l1.set(namespace, key, value, ttl)
        
        if not l1_only:
            self.l2.set(namespace, key, value, ttl)
    
    def delete(self, namespace: str, key: str) -> bool:
        """Delete value from all cache levels."""
        l1_deleted = self.l1.delete(namespace, key)
        l2_deleted = self.l2.delete(namespace, key)
        return l1_deleted or l2_deleted
    
    def clear(self, namespace: Optional[str] = None) -> Dict[str, int]:
        """Clear cache entries."""
        return {
            "l1_cleared": self.l1.clear(namespace),
            "l2_cleared": self.l2.clear(namespace)
        }
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "l1": self.l1.stats(),
            "l2": self.l2.stats(),
            "prefetch_queue_size": len(self._prefetch_queue)
        }
    
    # ==========================================
    # PRE-FETCH FUNCTIONALITY
    # ==========================================
    
    def schedule_prefetch(
        self,
        namespace: str,
        lat: float,
        lon: float,
        fetch_func: Callable,
        radius_deg: float = 0.1
    ) -> None:
        """
        Schedule pre-fetch for adjacent grid cells.
        
        Args:
            namespace: Cache namespace
            lat: Center latitude
            lon: Center longitude
            fetch_func: Async function to fetch data
            radius_deg: Radius in degrees for adjacent cells
        """
        if not CACHE_CONFIG["prefetch_enabled"]:
            return
        
        # Generate adjacent cell coordinates
        offsets = [
            (-radius_deg, 0), (radius_deg, 0),
            (0, -radius_deg), (0, radius_deg),
            (-radius_deg, -radius_deg), (radius_deg, radius_deg),
            (-radius_deg, radius_deg), (radius_deg, -radius_deg)
        ]
        
        for dlat, dlon in offsets:
            adj_lat = round(lat + dlat, 4)
            adj_lon = round(lon + dlon, 4)
            key = self.make_geo_key(adj_lat, adj_lon)
            
            # Skip if already cached
            if self.get(namespace, key) is not None:
                continue
            
            # Add to prefetch queue
            self._prefetch_queue.append({
                "namespace": namespace,
                "lat": adj_lat,
                "lon": adj_lon,
                "key": key,
                "fetch_func": fetch_func
            })
    
    async def run_prefetch(self) -> int:
        """
        Execute prefetch queue.
        
        Returns number of items fetched.
        """
        if not self._prefetch_queue:
            return 0
        
        fetched = 0
        
        # Process up to 8 items
        items = self._prefetch_queue[:8]
        self._prefetch_queue = self._prefetch_queue[8:]
        
        for item in items:
            try:
                # Small delay to avoid rate limiting
                await asyncio.sleep(CACHE_CONFIG["prefetch_delay_ms"] / 1000)
                
                result = await item["fetch_func"](item["lat"], item["lon"])
                if result:
                    self.set(item["namespace"], item["key"], result)
                    fetched += 1
                    logger.debug(f"Prefetched {item['namespace']}:{item['key']}")
                    
            except Exception as e:
                logger.debug(f"Prefetch error: {e}")
        
        return fetched
    
    async def start_prefetch_worker(self):
        """Start background prefetch worker."""
        while True:
            try:
                await asyncio.sleep(1)  # Check every second
                if self._prefetch_queue:
                    await self.run_prefetch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Prefetch worker error: {e}")
    
    # ==========================================
    # DECORATORS
    # ==========================================
    
    def cached(
        self,
        namespace: str,
        key_func: Optional[Callable] = None,
        ttl: Optional[int] = None
    ):
        """
        Decorator for caching function results.
        
        Usage:
            @cache_manager.cached("weather", lambda lat, lon: f"{lat}_{lon}")
            async def get_weather(lat, lon):
                ...
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    key = key_func(*args, **kwargs)
                else:
                    key = hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()
                
                # Try cache
                cached = self.get(namespace, key)
                if cached is not None:
                    return cached
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                if result is not None:
                    self.set(namespace, key, result, ttl=ttl)
                
                return result
            return wrapper
        return decorator


# ============================================
# SINGLETON INSTANCE
# ============================================

cache_manager = BionicCacheManager()


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def get_cached(namespace: str, key: str) -> Optional[Any]:
    """Get value from cache."""
    return cache_manager.get(namespace, key)


def set_cached(namespace: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
    """Set value in cache."""
    cache_manager.set(namespace, key, value, ttl=ttl)


def clear_cache(namespace: Optional[str] = None) -> Dict[str, int]:
    """Clear cache."""
    return cache_manager.clear(namespace)


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return cache_manager.stats()


logger.info("BIONIC™ Cache Manager initialized")
