/**
 * BIONIC™ P1.5 - Heatmap Cache Layer
 * ====================================
 * Cache intelligent pour réduire les recalculs de heatmaps.
 * Optimise les performances en mémorisant les données traitées.
 * 
 * @version 1.0.0
 * @architecture Découplé, P2-Ready
 */

// =============================================================================
// CACHE CONFIGURATION
// =============================================================================

const CACHE_CONFIG = {
  maxEntries: 100,
  maxAgeMs: 5 * 60 * 1000, // 5 minutes
  maxSizeBytes: 50 * 1024 * 1024, // 50MB
  cleanupIntervalMs: 60 * 1000, // 1 minute
  compressionThreshold: 10 * 1024 // 10KB
};

// =============================================================================
// CACHE ENTRY CLASS
// =============================================================================

class CacheEntry {
  constructor(key, data, metadata = {}) {
    this.key = key;
    this.data = data;
    this.metadata = metadata;
    this.createdAt = Date.now();
    this.lastAccessedAt = Date.now();
    this.accessCount = 0;
    this.sizeBytes = this._estimateSize(data);
  }
  
  _estimateSize(data) {
    if (data === null || data === undefined) return 0;
    
    if (data instanceof Float32Array || data instanceof Uint8Array) {
      return data.byteLength;
    }
    
    // Rough estimate for objects
    const str = JSON.stringify(data);
    return str ? str.length * 2 : 0;
  }
  
  access() {
    this.lastAccessedAt = Date.now();
    this.accessCount++;
    return this.data;
  }
  
  isExpired() {
    return Date.now() - this.createdAt > CACHE_CONFIG.maxAgeMs;
  }
  
  getAge() {
    return Date.now() - this.createdAt;
  }
}

// =============================================================================
// HEATMAP CACHE LAYER CLASS
// =============================================================================

class HeatmapCacheLayer {
  constructor() {
    this.cache = new Map();
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      totalSizeBytes: 0
    };
    this.listeners = new Set();
    
    // Start cleanup interval
    this._startCleanup();
  }
  
  /**
   * Generate cache key from parameters
   */
  _generateKey(dataType, params) {
    const keyParts = [
      dataType,
      params.lat?.toFixed(4),
      params.lon?.toFixed(4),
      params.radiusKm?.toFixed(1),
      params.resolution,
      params.species
    ].filter(Boolean);
    
    return keyParts.join(':');
  }
  
  /**
   * Get cached data or return null
   */
  get(dataType, params) {
    const key = this._generateKey(dataType, params);
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.stats.misses++;
      this._notify({ type: 'cache_miss', key, dataType });
      return null;
    }
    
    if (entry.isExpired()) {
      this.cache.delete(key);
      this.stats.totalSizeBytes -= entry.sizeBytes;
      this.stats.misses++;
      this._notify({ type: 'cache_expired', key, dataType });
      return null;
    }
    
    this.stats.hits++;
    this._notify({ type: 'cache_hit', key, dataType, age: entry.getAge() });
    return entry.access();
  }
  
  /**
   * Store data in cache
   */
  set(dataType, params, data, metadata = {}) {
    // Check if we need to evict entries
    this._evictIfNeeded();
    
    const key = this._generateKey(dataType, params);
    
    // Remove existing entry if present
    if (this.cache.has(key)) {
      const existing = this.cache.get(key);
      this.stats.totalSizeBytes -= existing.sizeBytes;
    }
    
    const entry = new CacheEntry(key, data, {
      ...metadata,
      dataType,
      params
    });
    
    this.cache.set(key, entry);
    this.stats.totalSizeBytes += entry.sizeBytes;
    
    this._notify({ type: 'cache_set', key, dataType, size: entry.sizeBytes });
    
    return key;
  }
  
  /**
   * Check if data exists in cache
   */
  has(dataType, params) {
    const key = this._generateKey(dataType, params);
    const entry = this.cache.get(key);
    return entry && !entry.isExpired();
  }
  
  /**
   * Invalidate cache entry
   */
  invalidate(dataType, params) {
    const key = this._generateKey(dataType, params);
    
    if (this.cache.has(key)) {
      const entry = this.cache.get(key);
      this.stats.totalSizeBytes -= entry.sizeBytes;
      this.cache.delete(key);
      this._notify({ type: 'cache_invalidated', key, dataType });
      return true;
    }
    
    return false;
  }
  
  /**
   * Invalidate all entries for a data type
   */
  invalidateType(dataType) {
    let count = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.metadata.dataType === dataType) {
        this.stats.totalSizeBytes -= entry.sizeBytes;
        this.cache.delete(key);
        count++;
      }
    }
    
    this._notify({ type: 'cache_type_invalidated', dataType, count });
    return count;
  }
  
  /**
   * Clear entire cache
   */
  clear() {
    const count = this.cache.size;
    this.cache.clear();
    this.stats.totalSizeBytes = 0;
    this._notify({ type: 'cache_cleared', count });
  }
  
  /**
   * Evict entries if cache is full
   */
  _evictIfNeeded() {
    // Evict by count
    while (this.cache.size >= CACHE_CONFIG.maxEntries) {
      this._evictOldest();
    }
    
    // Evict by size
    while (this.stats.totalSizeBytes > CACHE_CONFIG.maxSizeBytes && this.cache.size > 0) {
      this._evictOldest();
    }
  }
  
  /**
   * Evict oldest entry (LRU)
   */
  _evictOldest() {
    let oldest = null;
    let oldestTime = Infinity;
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessedAt < oldestTime) {
        oldestTime = entry.lastAccessedAt;
        oldest = key;
      }
    }
    
    if (oldest) {
      const entry = this.cache.get(oldest);
      this.stats.totalSizeBytes -= entry.sizeBytes;
      this.cache.delete(oldest);
      this.stats.evictions++;
      this._notify({ type: 'cache_evicted', key: oldest });
    }
  }
  
  /**
   * Start cleanup interval
   */
  _startCleanup() {
    this._cleanupInterval = setInterval(() => {
      this._cleanup();
    }, CACHE_CONFIG.cleanupIntervalMs);
  }
  
  /**
   * Cleanup expired entries
   */
  _cleanup() {
    let cleaned = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (entry.isExpired()) {
        this.stats.totalSizeBytes -= entry.sizeBytes;
        this.cache.delete(key);
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      this._notify({ type: 'cache_cleanup', count: cleaned });
    }
  }
  
  /**
   * Stop cleanup interval
   */
  destroy() {
    if (this._cleanupInterval) {
      clearInterval(this._cleanupInterval);
    }
    this.cache.clear();
  }
  
  /**
   * Get cache statistics
   */
  getStats() {
    const hitRate = this.stats.hits + this.stats.misses > 0
      ? (this.stats.hits / (this.stats.hits + this.stats.misses)) * 100
      : 0;
    
    return {
      entries: this.cache.size,
      maxEntries: CACHE_CONFIG.maxEntries,
      sizeBytes: this.stats.totalSizeBytes,
      maxSizeBytes: CACHE_CONFIG.maxSizeBytes,
      hits: this.stats.hits,
      misses: this.stats.misses,
      evictions: this.stats.evictions,
      hitRate: hitRate.toFixed(1) + '%'
    };
  }
  
  /**
   * Get detailed cache info
   */
  getDetailedInfo() {
    const entries = [];
    
    for (const [key, entry] of this.cache.entries()) {
      entries.push({
        key,
        dataType: entry.metadata.dataType,
        sizeBytes: entry.sizeBytes,
        ageMs: entry.getAge(),
        accessCount: entry.accessCount,
        expired: entry.isExpired()
      });
    }
    
    return entries.sort((a, b) => b.accessCount - a.accessCount);
  }
  
  /**
   * Add event listener
   */
  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  /**
   * Notify listeners
   */
  _notify(event) {
    this.listeners.forEach(cb => cb(event));
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const heatmapCache = new HeatmapCacheLayer();

// =============================================================================
// REACT HOOK
// =============================================================================

import { useState, useEffect, useCallback } from 'react';

export function useHeatmapCache() {
  const [stats, setStats] = useState(heatmapCache.getStats());
  
  useEffect(() => {
    const unsubscribe = heatmapCache.addListener((event) => {
      setStats(heatmapCache.getStats());
    });
    
    return unsubscribe;
  }, []);
  
  const get = useCallback((dataType, params) => {
    return heatmapCache.get(dataType, params);
  }, []);
  
  const set = useCallback((dataType, params, data, metadata) => {
    return heatmapCache.set(dataType, params, data, metadata);
  }, []);
  
  const has = useCallback((dataType, params) => {
    return heatmapCache.has(dataType, params);
  }, []);
  
  const invalidate = useCallback((dataType, params) => {
    return heatmapCache.invalidate(dataType, params);
  }, []);
  
  const clear = useCallback(() => {
    heatmapCache.clear();
  }, []);
  
  return {
    stats,
    get,
    set,
    has,
    invalidate,
    clear,
    getDetailedInfo: heatmapCache.getDetailedInfo.bind(heatmapCache)
  };
}

// =============================================================================
// EXPORTS
// =============================================================================

export default HeatmapCacheLayer;
