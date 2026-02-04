"""
BIONIC™ Pressure Engine - API Endpoints
========================================
Endpoints FastAPI pour l'analyse de pression humaine.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from ..core.analyzer import pressure_analyzer

router = APIRouter(prefix="/api/bionic/pressure", tags=["BIONIC Pressure Engine"])


@router.get("/status")
async def get_status():
    """Get pressure engine status."""
    return {
        "engine": "PressureEngine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Analyse de la pression humaine sur les territoires de chasse",
        "cache_stats": pressure_analyzer.get_cache_stats(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/analyze/point")
async def analyze_point(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(2.0, ge=0.5, le=10, description="Rayon d'analyse en km"),
    use_cache: bool = Query(True, description="Utiliser le cache"),
    use_real_data: bool = Query(True, description="Utiliser les données réelles (OSM)")
):
    """
    Analyze human pressure at a specific point.
    
    Returns road density, building density, remoteness, and hunting impact.
    """
    try:
        result = await pressure_analyzer.analyze_point_async(
            lat, lon,
            radius_km=radius_km,
            use_cache=use_cache,
            use_real_data=use_real_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pressure-impacts")
async def get_pressure_impacts_reference():
    """Get pressure impact reference table."""
    return {
        "pressure_impacts": pressure_analyzer.PRESSURE_IMPACTS,
        "description": "Impact des niveaux de pression sur la chasse"
    }


@router.get("/distance-thresholds")
async def get_distance_thresholds():
    """Get distance thresholds for pressure calculation."""
    return {
        "thresholds": pressure_analyzer.DISTANCE_THRESHOLDS,
        "description": "Seuils de distance pour le calcul de perturbation"
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    return pressure_analyzer.get_cache_stats()
