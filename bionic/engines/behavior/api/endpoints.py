"""
BIONIC™ Behavior Suite - API Endpoints
=======================================
Endpoints FastAPI pour les moteurs comportementaux.

Version: 1.0 - P0 Étape 1 (Fondations)
"""

import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timezone, date
import sys

# Add path for imports
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import (
    SpeciesCode,
    BehaviorAnalysisInput,
    SeasonalAttractivenessInput,
    ActivityProbabilityInput,
    RutPredictionInput,
    MovementAnalysisInput,
    SpeciesModelInput,
    BehaviorSuiteOutput
)

from behavior.core.behavior_engine import behavior_engine
from behavior.core.seasonal_attractiveness_engine import seasonal_attractiveness_engine
from behavior.core.activity_probability_engine import activity_probability_engine
from behavior.core.rut_prediction_engine import rut_prediction_engine
from behavior.core.movement_engine import movement_engine
from behavior.core.species_model_engine import species_model_engine

logger = logging.getLogger(__name__)

# Router principal
behavior_router = APIRouter(
    prefix="/api/bionic/behavior",
    tags=["BIONIC Behavior Suite"]
)


# =============================================================================
# STATUS ENDPOINTS
# =============================================================================

@behavior_router.get("/status")
async def get_behavior_suite_status():
    """
    Get status of all Behavior Suite engines.
    """
    return {
        "suite": "BIONIC Behavior Suite",
        "version": "1.0.0",
        "status": "operational",
        "phase": "P0-1 (Fondations)",
        "engines": {
            "behavior": {"status": "active", "version": behavior_engine.version},
            "seasonal": {"status": "active", "version": seasonal_attractiveness_engine.version},
            "activity": {"status": "active", "version": activity_probability_engine.version},
            "rut": {"status": "active", "version": rut_prediction_engine.version},
            "movement": {"status": "active", "version": movement_engine.version},
            "species_model": {"status": "active", "version": species_model_engine.version}
        },
        "supported_species": [s.value for s in SpeciesCode],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# =============================================================================
# BEHAVIOR ENGINE
# =============================================================================

@behavior_router.get("/analyze")
async def analyze_behavior(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    species: SpeciesCode = Query(default=SpeciesCode.DEER, description="Espèce cible"),
    include_predictions: bool = Query(True, description="Inclure prédictions 24h"),
    temperature_c: Optional[float] = Query(None, description="Température en °C"),
    precipitation_mm: Optional[float] = Query(None, description="Précipitations en mm"),
    wind_speed_kmh: Optional[float] = Query(None, description="Vitesse du vent en km/h"),
    moon_phase: Optional[float] = Query(None, ge=0, le=1, description="Phase lunaire (0-1)")
):
    """
    Analyze animal behavior at a specific location.
    
    Returns activity scores, optimal time windows, and hunting recommendations.
    """
    try:
        input_data = BehaviorAnalysisInput(
            latitude=lat,
            longitude=lon,
            species=species,
            include_predictions=include_predictions,
            temperature_c=temperature_c,
            precipitation_mm=precipitation_mm,
            wind_speed_kmh=wind_speed_kmh,
            moon_phase=moon_phase
        )
        
        result = await behavior_engine.analyze(input_data)
        return result
    except Exception as e:
        logger.error(f"Behavior analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SEASONAL ATTRACTIVENESS ENGINE
# =============================================================================

@behavior_router.get("/seasonal")
async def analyze_seasonal_attractiveness(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER),
    radius_km: float = Query(default=5.0, ge=0.5, le=50),
    ndvi: Optional[float] = Query(None, description="NDVI de la zone")
):
    """
    Analyze seasonal attractiveness of habitat.
    
    Returns attractiveness scores, current phase, hotspots, and trends.
    """
    try:
        input_data = SeasonalAttractivenessInput(
            latitude=lat,
            longitude=lon,
            species=species,
            radius_km=radius_km,
            ndvi=ndvi
        )
        
        result = await seasonal_attractiveness_engine.analyze(input_data)
        return result
    except Exception as e:
        logger.error(f"Seasonal analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ACTIVITY PROBABILITY ENGINE
# =============================================================================

@behavior_router.get("/activity")
async def analyze_activity_probability(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER),
    temperature_c: Optional[float] = Query(None),
    cloud_cover_percent: Optional[float] = Query(None, ge=0, le=100),
    precipitation_mm: Optional[float] = Query(None),
    wind_speed_kmh: Optional[float] = Query(None),
    moon_phase: Optional[float] = Query(None, ge=0, le=1)
):
    """
    Calculate animal activity probability.
    
    Returns hourly probabilities, optimal window, and influencing factors.
    """
    try:
        input_data = ActivityProbabilityInput(
            latitude=lat,
            longitude=lon,
            species=species,
            temperature_c=temperature_c,
            cloud_cover_percent=cloud_cover_percent,
            precipitation_mm=precipitation_mm,
            wind_speed_kmh=wind_speed_kmh,
            moon_phase=moon_phase
        )
        
        result = await activity_probability_engine.analyze(input_data)
        return result
    except Exception as e:
        logger.error(f"Activity probability error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# RUT PREDICTION ENGINE
# =============================================================================

@behavior_router.get("/rut")
async def predict_rut(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER),
    year: Optional[int] = Query(None, description="Année de prédiction")
):
    """
    Predict rut phases and timing.
    
    Returns current phase, peak dates, expected behaviors, and tactics.
    """
    try:
        input_data = RutPredictionInput(
            latitude=lat,
            longitude=lon,
            species=species,
            year=year
        )
        
        result = await rut_prediction_engine.analyze(input_data)
        return result
    except Exception as e:
        logger.error(f"Rut prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MOVEMENT ENGINE
# =============================================================================

@behavior_router.get("/movement")
async def analyze_movement(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER),
    include_corridors: bool = Query(True, description="Inclure analyse des corridors")
):
    """
    Analyze animal movement patterns and corridors.
    
    Returns home range, corridors, likely positions, and travel routes.
    """
    try:
        input_data = MovementAnalysisInput(
            latitude=lat,
            longitude=lon,
            species=species,
            include_corridors=include_corridors
        )
        
        result = await movement_engine.analyze(input_data)
        return result
    except Exception as e:
        logger.error(f"Movement analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SPECIES MODEL ENGINE
# =============================================================================

@behavior_router.get("/species-model")
async def analyze_species_model(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER),
    analysis_type: str = Query(default="full", description="Type d'analyse (full, habitat, behavior, seasonal)")
):
    """
    Get species-specific analysis and recommendations.
    
    Returns species profile, habitat suitability, tactics, and gear recommendations.
    """
    try:
        input_data = SpeciesModelInput(
            latitude=lat,
            longitude=lon,
            species=species,
            analysis_type=analysis_type
        )
        
        result = await species_model_engine.analyze(input_data)
        return result
    except Exception as e:
        logger.error(f"Species model error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# COMBINED ANALYSIS
# =============================================================================

@behavior_router.get("/full")
async def full_behavior_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER),
    include_behavior: bool = Query(True),
    include_seasonal: bool = Query(True),
    include_activity: bool = Query(True),
    include_rut: bool = Query(True),
    include_movement: bool = Query(True),
    include_species_model: bool = Query(True)
):
    """
    Run full Behavior Suite analysis.
    
    Combines all engines into a consolidated result.
    """
    import asyncio
    import uuid
    
    start_time = datetime.now(timezone.utc)
    analysis_id = f"full_{uuid.uuid4().hex[:12]}"
    
    # Run selected engines in parallel
    tasks = {}
    
    if include_behavior:
        tasks["behavior"] = behavior_engine.analyze(BehaviorAnalysisInput(
            latitude=lat, longitude=lon, species=species
        ))
    
    if include_seasonal:
        tasks["seasonal"] = seasonal_attractiveness_engine.analyze(SeasonalAttractivenessInput(
            latitude=lat, longitude=lon, species=species
        ))
    
    if include_activity:
        tasks["activity"] = activity_probability_engine.analyze(ActivityProbabilityInput(
            latitude=lat, longitude=lon, species=species
        ))
    
    if include_rut and species in [SpeciesCode.DEER, SpeciesCode.MOOSE]:
        tasks["rut"] = rut_prediction_engine.analyze(RutPredictionInput(
            latitude=lat, longitude=lon, species=species
        ))
    
    if include_movement:
        tasks["movement"] = movement_engine.analyze(MovementAnalysisInput(
            latitude=lat, longitude=lon, species=species
        ))
    
    if include_species_model:
        tasks["species_model"] = species_model_engine.analyze(SpeciesModelInput(
            latitude=lat, longitude=lon, species=species
        ))
    
    # Execute all tasks
    results = {}
    if tasks:
        task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for key, result in zip(tasks.keys(), task_results):
            if isinstance(result, Exception):
                results[key] = {"error": str(result)}
            else:
                results[key] = result
    
    # Calculate global opportunity score
    scores = []
    if "behavior" in results and hasattr(results["behavior"], "hunting_opportunity_score"):
        scores.append(results["behavior"].hunting_opportunity_score)
    if "seasonal" in results and hasattr(results["seasonal"], "overall_attractiveness"):
        scores.append(results["seasonal"].overall_attractiveness)
    if "activity" in results and hasattr(results["activity"], "activity_probability"):
        scores.append(results["activity"].activity_probability * 100)
    
    global_score = sum(scores) / len(scores) if scores else 50
    
    # Aggregate recommendations
    top_recommendations = []
    for key, result in results.items():
        if hasattr(result, "recommendations"):
            for rec in result.recommendations[:2]:
                top_recommendations.append(f"[{key.upper()}] {rec}")
    
    # Aggregate hotspots
    hotspots = []
    if "seasonal" in results and hasattr(results["seasonal"], "hotspots"):
        hotspots.extend(results["seasonal"].hotspots[:3])
    if "movement" in results and hasattr(results["movement"], "likely_positions"):
        hotspots.extend(results["movement"].likely_positions[:3])
    
    end_time = datetime.now(timezone.utc)
    
    return BehaviorSuiteOutput(
        suite_version="1.0.0",
        analysis_id=analysis_id,
        location={"lat": lat, "lon": lon},
        species=species,
        analyzed_at=start_time,
        processing_time_ms=int((end_time - start_time).total_seconds() * 1000),
        behavior=results.get("behavior"),
        seasonal=results.get("seasonal"),
        activity=results.get("activity"),
        rut=results.get("rut"),
        movement=results.get("movement"),
        species_model=results.get("species_model"),
        global_opportunity_score=round(global_score, 1),
        confidence=0.75,
        top_recommendations=top_recommendations[:8],
        hotspots=hotspots[:5],
        engines_executed=list(tasks.keys()),
        from_cache=False
    )
