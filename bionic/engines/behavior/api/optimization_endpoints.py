"""
BIONIC™ Coherence Optimization API
====================================
Endpoints pour l'optimisation de la cohérence inter-moteurs.

Version: 1.0.0
"""

import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timezone
import sys

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import SpeciesCode
from behavior.core.coherence_optimizer import (
    coherence_optimizer,
    QuebecEnhancedData,
    SpeciesCalibrationManager,
    GeospatialFusionHooks
)
from behavior.core.behavior_engine import behavior_engine
from behavior.core.seasonal_attractiveness_engine import seasonal_attractiveness_engine
from behavior.core.activity_probability_engine import activity_probability_engine
from behavior.core.rut_prediction_engine import rut_prediction_engine
from behavior.core.movement_engine import movement_engine
from behavior.core.species_model_engine import species_model_engine

from behavior.models.schemas import (
    BehaviorAnalysisInput, SeasonalAttractivenessInput, ActivityProbabilityInput,
    RutPredictionInput, MovementAnalysisInput, SpeciesModelInput
)

logger = logging.getLogger(__name__)

# Router
optimization_router = APIRouter(
    prefix="/api/bionic/optimization",
    tags=["BIONIC Coherence Optimization"]
)


@optimization_router.get("/status")
async def get_optimization_status():
    """
    Get status of the coherence optimization module.
    """
    return {
        "module": "BIONIC™ Coherence Optimization",
        "version": "1.0.0",
        "status": "operational",
        "current_coherence": "88.1%",
        "target_coherence": "100%",
        "optimization_axes": [
            "Inter-engine weighting refinement",
            "Quebec enhanced data (UGAF, ZEC, reserves)",
            "Species-specific calibration profiles",
            "Geospatial pre-fusion hooks (P1)"
        ],
        "species_profiles": list(SpeciesCalibrationManager.PROFILES.keys()),
        "quebec_zones": list(QuebecEnhancedData.UGAF_ZONES.keys())[:5] + ["..."],
        "p1_hooks_ready": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@optimization_router.get("/evaluate")
async def evaluate_optimized_coherence(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER)
):
    """
    Evaluate coherence with all optimizations applied.
    
    Returns optimized coherence score and detailed analysis.
    """
    try:
        # Run all 6 engines
        results = {}
        
        behavior_input = BehaviorAnalysisInput(latitude=lat, longitude=lon, species=species)
        behavior_output = await behavior_engine.analyze(behavior_input)
        results["behavior"] = behavior_output.model_dump() if hasattr(behavior_output, 'model_dump') else behavior_output
        
        seasonal_input = SeasonalAttractivenessInput(latitude=lat, longitude=lon, species=species)
        seasonal_output = await seasonal_attractiveness_engine.analyze(seasonal_input)
        results["seasonal"] = seasonal_output.model_dump() if hasattr(seasonal_output, 'model_dump') else seasonal_output
        
        activity_input = ActivityProbabilityInput(latitude=lat, longitude=lon, species=species)
        activity_output = await activity_probability_engine.analyze(activity_input)
        results["activity"] = activity_output.model_dump() if hasattr(activity_output, 'model_dump') else activity_output
        
        rut_output = None
        if species in [SpeciesCode.DEER, SpeciesCode.MOOSE]:
            rut_input = RutPredictionInput(latitude=lat, longitude=lon, species=species)
            rut_output = await rut_prediction_engine.analyze(rut_input)
            results["rut"] = rut_output.model_dump() if hasattr(rut_output, 'model_dump') else rut_output
        
        movement_input = MovementAnalysisInput(latitude=lat, longitude=lon, species=species)
        movement_output = await movement_engine.analyze(movement_input)
        results["movement"] = movement_output.model_dump() if hasattr(movement_output, 'model_dump') else movement_output
        
        species_input = SpeciesModelInput(latitude=lat, longitude=lon, species=species)
        species_output = await species_model_engine.analyze(species_input)
        results["species_model"] = species_output.model_dump() if hasattr(species_output, 'model_dump') else species_output
        
        # Run optimized coherence evaluation
        optimized_result = coherence_optimizer.optimize_coherence_evaluation(
            species=species.value,
            lat=lat,
            lon=lon,
            behavior_result=results["behavior"],
            seasonal_result=results["seasonal"],
            activity_result=results["activity"],
            rut_result=results.get("rut"),
            movement_result=results["movement"],
            species_result=results["species_model"]
        )
        
        return {
            "location": {"lat": lat, "lon": lon},
            "species": species.value,
            "optimized_coherence": optimized_result,
            "raw_scores": {
                "behavior_activity": results["behavior"].get("overall_activity_score"),
                "seasonal_attractiveness": results["seasonal"].get("overall_attractiveness"),
                "activity_probability": results["activity"].get("activity_probability"),
                "movement_km": results["movement"].get("daily_movement_km"),
                "habitat_suitability": results["species_model"].get("habitat_suitability")
            },
            "improvement_vs_baseline": {
                "baseline": 0.881,  # 88.1%
                "optimized": optimized_result["overall_score"],
                "improvement": round(optimized_result["overall_score"] - 0.881, 3)
            }
        }
        
    except Exception as e:
        logger.error(f"Optimized coherence evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@optimization_router.get("/species-profile/{species}")
async def get_species_calibration_profile(species: str):
    """
    Get the calibration profile for a specific species.
    """
    if species not in SpeciesCalibrationManager.PROFILES:
        raise HTTPException(status_code=404, detail=f"Profile not found for species: {species}")
    
    profile = SpeciesCalibrationManager.get_profile(species)
    
    return {
        "species": species,
        "profile": {
            "activity_threshold_low": profile.activity_threshold_low,
            "activity_threshold_high": profile.activity_threshold_high,
            "movement_threshold_low": profile.movement_threshold_low,
            "movement_threshold_high": profile.movement_threshold_high,
            "activity_movement_correlation": profile.activity_movement_correlation,
            "rut_activity_boost": profile.rut_activity_boost,
            "habitat_tolerance": profile.habitat_tolerance,
            "winter_movement_pattern": profile.winter_movement_pattern,
            "summer_movement_pattern": profile.summer_movement_pattern,
            "rut_movement_pattern": profile.rut_movement_pattern
        }
    }


@optimization_router.get("/quebec/enhanced-data")
async def get_quebec_enhanced_data():
    """
    Get enhanced Quebec data for calibration.
    """
    return {
        "ugaf_zones": list(QuebecEnhancedData.UGAF_ZONES.keys()),
        "hunting_pressure_by_region": QuebecEnhancedData.HUNTING_PRESSURE,
        "protected_areas": list(QuebecEnhancedData.PROTECTED_AREAS.keys()),
        "harvest_history_regions": list(QuebecEnhancedData.HARVEST_HISTORY["deer"].keys()),
        "seasonal_corrections": QuebecEnhancedData.SEASONAL_CORRECTIONS,
        "data_sources": [
            "UGAF - Unités de gestion des animaux à fourrure",
            "ZEC - Zones d'exploitation contrôlée",
            "Réserves fauniques du Québec",
            "MFFP - Données de récolte 2015-2024"
        ]
    }


@optimization_router.get("/quebec/location-factors")
async def get_location_factors(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: str = Query(default="deer")
):
    """
    Get all factors affecting a specific location.
    """
    # Protected area factor
    protected_factor = QuebecEnhancedData.get_protected_area_factor(lat, lon, species)
    
    # Find which protected area (if any)
    protected_area = None
    for area_name, area_data in QuebecEnhancedData.PROTECTED_AREAS.items():
        lat_min, lat_max = area_data["lat_range"]
        lon_min, lon_max = area_data["lon_range"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            protected_area = area_name
            break
    
    # Region and hunting pressure
    from behavior.core.integration_calibration import QuebecCalibrationData
    region = QuebecCalibrationData.get_region_for_coords(lat, lon)
    hunting_pressure_mod = QuebecEnhancedData.get_hunting_pressure_modifier(region, species) if region else 1.0
    
    # Seasonal correction
    month = datetime.now().month
    day_of_year = datetime.now().timetuple().tm_yday
    seasonal_phase, seasonal_correction = QuebecEnhancedData.get_seasonal_correction(species, month, day_of_year)
    
    return {
        "location": {"lat": lat, "lon": lon},
        "species": species,
        "factors": {
            "region": region,
            "protected_area": protected_area,
            "protected_factor": protected_factor,
            "hunting_pressure_modifier": hunting_pressure_mod,
            "seasonal_phase": seasonal_phase,
            "seasonal_correction": seasonal_correction
        },
        "combined_modifier": round(protected_factor * hunting_pressure_mod * seasonal_correction, 3)
    }


@optimization_router.get("/p1-hooks")
async def get_p1_fusion_hooks():
    """
    Get the pre-fusion hooks ready for P1 geospatial engines.
    """
    return {
        "hooks_version": "1.0.0",
        "ready_for_p1": True,
        "expected_engines": GeospatialFusionHooks.EXPECTED_P1_ENGINES,
        "fusion_interface": {
            "input_format": "prepare_fusion_input()",
            "prefusion_coherence": "calculate_prefusion_coherence()",
            "output": "Dict with behavior_data, seasonal_data, activity_data, movement_data, species_data"
        },
        "integration_notes": [
            "corridorEngine will boost movement coherence",
            "landcoverEngine will improve habitat-species match",
            "nutritionEngine will enhance seasonal attractiveness accuracy"
        ]
    }


@optimization_router.get("/compare")
async def compare_baseline_vs_optimized(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER)
):
    """
    Compare baseline coherence vs optimized coherence.
    """
    try:
        # Get optimized result
        optimized_response = await evaluate_optimized_coherence(lat, lon, species)
        
        # Get baseline from P0-3 integration tester
        from behavior.core.integration_calibration import integration_tester
        baseline_result = await integration_tester.run_full_integration_test(lat, lon, species)
        
        baseline_score = baseline_result.get("coherence", {}).get("overall_score", 0.881)
        optimized_score = optimized_response["optimized_coherence"]["overall_score"]
        
        return {
            "location": {"lat": lat, "lon": lon},
            "species": species.value,
            "comparison": {
                "baseline_coherence": round(baseline_score, 3),
                "optimized_coherence": round(optimized_score, 3),
                "improvement": round(optimized_score - baseline_score, 3),
                "improvement_percent": f"{((optimized_score - baseline_score) / baseline_score) * 100:.1f}%"
            },
            "optimizations_applied": optimized_response["optimized_coherence"]["optimizations_applied"],
            "target": 1.0,
            "remaining_gap": round(1.0 - optimized_score, 3)
        }
        
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


logger.info("BIONIC™ Coherence Optimization API loaded")
