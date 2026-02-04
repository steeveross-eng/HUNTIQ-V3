"""
BIONIC™ Terrain Engine - API Endpoints
=======================================
Endpoints FastAPI pour l'analyse de terrain.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from ..core.analyzer import terrain_analyzer

router = APIRouter(prefix="/api/bionic/terrain", tags=["BIONIC Terrain Engine"])


@router.get("/status")
async def get_status():
    """Get terrain engine status."""
    return {
        "engine": "TerrainEngine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Analyse du terrain (MNT, pente, exposition) pour les territoires de chasse",
        "cache_stats": terrain_analyzer.get_cache_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/analyze/point")
async def analyze_point(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    use_cache: bool = Query(True, description="Utiliser le cache"),
    use_real_data: bool = Query(True, description="Utiliser les données réelles")
):
    """
    Analyze terrain at a specific point.
    
    Returns elevation, slope, aspect, TPI, and hunting assessment.
    """
    try:
        result = await terrain_analyzer.analyze_point_async(
            lat, lon,
            use_cache=use_cache,
            use_real_data=use_real_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slope-difficulty")
async def get_slope_difficulty_reference():
    """Get slope difficulty reference table."""
    return {
        "slope_difficulty": terrain_analyzer.SLOPE_DIFFICULTY,
        "description": "Classification de difficulté du terrain selon la pente"
    }


@router.get("/aspect-values")
async def get_aspect_values_reference():
    """Get aspect hunting values reference."""
    return {
        "aspect_values": terrain_analyzer.ASPECT_VALUE,
        "description": "Valeur de chasse selon l'exposition du versant"
    }


@router.get("/tpi-classes")
async def get_tpi_classes_reference():
    """Get TPI classification reference."""
    return {
        "tpi_classes": terrain_analyzer.TPI_CLASSES,
        "description": "Classification des positions topographiques"
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    return terrain_analyzer.get_cache_stats()
