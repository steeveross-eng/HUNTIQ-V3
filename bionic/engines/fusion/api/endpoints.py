"""
BIONIC™ P2 - Fusion API Endpoints
==================================
Endpoints FastAPI pour le BehaviorFusionEngine.

Version: 1.0.0
Phase: P2
"""

import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timezone
import sys

# Add path for imports
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from fusion.behavior_fusion_engine import (
    behavior_fusion_engine,
    fusion_weight_manager,
    FusionMode
)

logger = logging.getLogger(__name__)

# Router principal
fusion_router = APIRouter(
    prefix="/api/bionic/fusion",
    tags=["BIONIC P2 - BehaviorFusionEngine"]
)


# =============================================================================
# STATUS ENDPOINTS
# =============================================================================

@fusion_router.get("/status")
async def get_fusion_status():
    """
    Get status of the BehaviorFusionEngine.
    """
    return {
        "engine": "BehaviorFusionEngine",
        "version": behavior_fusion_engine.version,
        "status": "operational",
        "phase": "P2",
        "capabilities": {
            "fusion_modes": [m.value for m in FusionMode],
            "geo_engines": ["corridor", "landcover", "nutrition", "population", "pressure"],
            "behavior_engines": ["behavior", "seasonal", "activity", "movement", "rut", "species_model"],
            "heatmap_generation": True,
            "weight_management": True,
            "p3_hooks": True
        },
        "weight_manager_version": fusion_weight_manager.version,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# =============================================================================
# FUSION ENDPOINTS
# =============================================================================

@fusion_router.get("/analyze")
async def analyze_fusion(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    species: str = Query(default="deer", description="Espèce cible"),
    territory: str = Query(default="quebec", description="Territoire (quebec, canada, usa)"),
    radius_km: float = Query(default=2.0, ge=0.5, le=50, description="Rayon d'analyse en km"),
    mode: str = Query(default="balanced", description="Mode de fusion"),
    include_heatmap: bool = Query(default=True, description="Inclure les données heatmap")
):
    """
    Run full BehaviorFusion analysis.
    
    Combines Geo-Suite and Behavior Suite data into a unified score.
    
    Returns:
    - Global fused score (0-100)
    - Geo score breakdown
    - Behavior score breakdown
    - Heatmap data (if requested)
    - Fusion-aware recommendations
    """
    try:
        # Parse fusion mode
        try:
            fusion_mode = FusionMode(mode)
        except ValueError:
            fusion_mode = FusionMode.BALANCED
        
        result = await behavior_fusion_engine.fuse(
            lat=lat,
            lon=lon,
            species=species,
            territory=territory,
            radius_km=radius_km,
            mode=fusion_mode,
            include_heatmap=include_heatmap
        )
        
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Fusion analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@fusion_router.get("/analyze/quick")
async def quick_fusion_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: str = Query(default="deer")
):
    """
    Quick fusion analysis without heatmap data.
    
    Returns simplified score data for fast responses.
    """
    try:
        result = await behavior_fusion_engine.fuse(
            lat=lat,
            lon=lon,
            species=species,
            include_heatmap=False
        )
        
        return {
            "fusion_id": result.fusion_id,
            "global_score": result.global_score,
            "score_level": result.score_level,
            "geo_score": result.geo_score,
            "behavior_score": result.behavior_score,
            "fusion_quality": result.fusion_quality,
            "confidence": result.fusion_confidence,
            "top_recommendation": result.recommendations[0] if result.recommendations else None
        }
    
    except Exception as e:
        logger.error(f"Quick fusion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@fusion_router.get("/analyze/frontend")
async def fusion_for_frontend(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: str = Query(default="deer"),
    territory: str = Query(default="quebec"),
    radius_km: float = Query(default=2.0, ge=0.5, le=50)
):
    """
    Fusion analysis optimized for frontend consumption.
    
    Returns data formatted for P1.5 components.
    """
    try:
        result = await behavior_fusion_engine.fuse(
            lat=lat,
            lon=lon,
            species=species,
            territory=territory,
            radius_km=radius_km,
            include_heatmap=True
        )
        
        return result.get_frontend_output()
    
    except Exception as e:
        logger.error(f"Frontend fusion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WEIGHT MANAGEMENT ENDPOINTS
# =============================================================================

@fusion_router.get("/weights")
async def get_fusion_weights(
    species: str = Query(default="deer"),
    territory: str = Query(default="quebec"),
    mode: str = Query(default="balanced")
):
    """
    Get fusion weights for given parameters.
    
    Shows how Geo and Behavior scores will be weighted.
    """
    try:
        fusion_mode = FusionMode(mode)
    except ValueError:
        fusion_mode = FusionMode.BALANCED
    
    weights = fusion_weight_manager.get_weights(
        species=species,
        territory=territory,
        mode=fusion_mode
    )
    
    return {
        "status": "success",
        "weights": weights,
        "description": {
            "suite_weights": "Répartition entre Geo-Suite et Behavior-Suite",
            "geo_engine_weights": "Poids des 5 moteurs géospatiaux",
            "behavior_engine_weights": "Poids des 6 moteurs comportementaux"
        }
    }


@fusion_router.get("/weights/species-presets")
async def get_species_weight_presets():
    """
    Get weight presets for all species.
    """
    return {
        "status": "success",
        "presets": fusion_weight_manager.species_weights,
        "description": "Pondérations optimisées par espèce"
    }


@fusion_router.get("/weights/territory-modifiers")
async def get_territory_modifiers():
    """
    Get territory-based weight modifiers.
    """
    return {
        "status": "success",
        "modifiers": fusion_weight_manager.territory_weights,
        "description": "Modificateurs de poids par territoire"
    }


@fusion_router.get("/weights/seasonal-modifiers")
async def get_seasonal_modifiers():
    """
    Get seasonal weight modifiers.
    """
    return {
        "status": "success",
        "modifiers": fusion_weight_manager.seasonal_modifiers,
        "description": "Modificateurs saisonniers pour les moteurs"
    }


# =============================================================================
# HEATMAP ENDPOINTS
# =============================================================================

@fusion_router.get("/heatmap")
async def get_fusion_heatmap(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: str = Query(default="deer"),
    radius_km: float = Query(default=2.0, ge=0.5, le=10)
):
    """
    Get fusion heatmap data only.
    
    Returns combined Geo+Behavior heatmap for visualization.
    """
    try:
        result = await behavior_fusion_engine.fuse(
            lat=lat,
            lon=lon,
            species=species,
            radius_km=radius_km,
            include_heatmap=True
        )
        
        return {
            "status": "success",
            "heatmap": result.heatmap_data,
            "global_score": result.global_score,
            "score_level": result.score_level
        }
    
    except Exception as e:
        logger.error(f"Heatmap generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# P3 PLACEHOLDER ENDPOINTS
# =============================================================================

@fusion_router.get("/calibration/status")
async def get_calibration_status():
    """
    P3-Ready: Get auto-calibration status.
    
    This endpoint will be enhanced in Phase P3 with ML-based
    automatic weight adjustment.
    """
    return {
        "status": "placeholder",
        "phase": "P3",
        "current_features": {
            "feedback_collection": False,
            "weight_adjustment": False,
            "ml_training": False
        },
        "planned_features": [
            "Collecte automatique des feedbacks chasseurs",
            "Ajustement ML des pondérations",
            "Validation croisée des scores",
            "Amélioration continue des prédictions"
        ],
        "calibration_placeholder": fusion_weight_manager.get_calibration_placeholder()
    }


@fusion_router.post("/calibration/feedback")
async def submit_calibration_feedback(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: str = Query(default="deer"),
    actual_success: bool = Query(..., description="La chasse a-t-elle été réussie?"),
    predicted_score: float = Query(..., ge=0, le=100, description="Score prédit"),
    notes: Optional[str] = Query(None, description="Notes additionnelles")
):
    """
    P3-Ready: Submit calibration feedback.
    
    In Phase P3, this data will be used to improve fusion accuracy.
    Currently stores data for future ML training.
    """
    import uuid
    
    feedback_entry = {
        "feedback_id": f"fb_{uuid.uuid4().hex[:8]}",
        "location": {"lat": lat, "lon": lon},
        "species": species,
        "predicted_score": predicted_score,
        "actual_success": actual_success,
        "notes": notes,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "status": "stored_for_p3"
    }
    
    logger.info(f"Calibration feedback received: {feedback_entry['feedback_id']}")
    
    return {
        "status": "accepted",
        "message": "Feedback stocké pour calibration P3",
        "feedback": feedback_entry
    }


# =============================================================================
# COMPATIBILITY ENDPOINT
# =============================================================================

@fusion_router.get("/compatibility")
async def check_fusion_compatibility():
    """
    Check compatibility with Geo-Suite and Behavior-Suite.
    """
    return {
        "fusion_engine": {
            "name": "BehaviorFusionEngine",
            "version": behavior_fusion_engine.version,
            "compatible": True
        },
        "geo_suite": {
            "engines": ["corridor", "landcover", "nutrition", "population", "pressure"],
            "contract_version": "1.0.0",
            "compatible": True
        },
        "behavior_suite": {
            "engines": ["behavior", "seasonal", "activity", "movement", "rut", "species_model"],
            "contract_version": "1.0.0",
            "compatible": True
        },
        "frontend_p15": {
            "components": [
                "AdvancedVisualizationPanel",
                "FusionScorePlaceholder",
                "HeatmapRenderer",
                "InteractiveLegend"
            ],
            "compatible": True
        },
        "p3_hooks": {
            "adaptive_metrics": True,
            "ml_calibration": "placeholder",
            "feedback_loop": True
        }
    }
