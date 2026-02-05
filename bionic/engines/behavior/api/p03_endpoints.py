"""
BIONIC™ P0-3 - Integration Testing & Calibration API
======================================================
Endpoints pour les tests d'intégration et la calibration ML.

Version: 1.0.0
"""

import logging
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime, timezone
import sys
import json

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import SpeciesCode
from behavior.core.integration_calibration import (
    integration_tester,
    calibration_adjuster,
    report_generator,
    QuebecCalibrationData
)

logger = logging.getLogger(__name__)

# Router
p03_router = APIRouter(
    prefix="/api/bionic/p03",
    tags=["BIONIC P0-3 Integration"]
)

# Store for async results
_async_results = {}


@p03_router.get("/status")
async def get_p03_status():
    """
    Get status of P0-3 Integration & Calibration module.
    """
    return {
        "module": "BIONIC™ P0-3 Integration & Calibration",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Integration testing between 6 behavior engines",
            "Coherence matrix validation",
            "ML calibration with Quebec data",
            "Report generation"
        ],
        "test_locations": [loc["name"] for loc in integration_tester.TEST_LOCATIONS],
        "test_species": [s.value for s in integration_tester.TEST_SPECIES],
        "calibration_regions": list(QuebecCalibrationData.REGIONS.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@p03_router.get("/test/single")
async def run_single_integration_test(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    species: SpeciesCode = Query(default=SpeciesCode.DEER, description="Espèce")
):
    """
    Run a single integration test at specified location.
    
    Tests all 6 engines and evaluates coherence.
    """
    try:
        result = await integration_tester.run_full_integration_test(lat, lon, species)
        return {
            "status": "completed",
            "test_result": result
        }
    except Exception as e:
        logger.error(f"Single integration test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@p03_router.post("/test/full")
async def run_full_integration_tests(
    background_tasks: BackgroundTasks,
    include_report: bool = Query(True, description="Générer rapport complet")
):
    """
    Run full integration test suite (all locations & species).
    
    This runs in the background due to long execution time.
    Returns a task_id to check results later.
    """
    import uuid
    task_id = f"p03_{uuid.uuid4().hex[:12]}"
    
    async def run_tests():
        try:
            # Run all integration tests
            results = await integration_tester.run_all_tests()
            
            # Generate calibration report
            calibration_report = calibration_adjuster.generate_calibration_report(
                results.get("results", [])
            )
            
            # Generate full report if requested
            if include_report:
                full_report = report_generator.generate_full_report(
                    results,
                    calibration_report
                )
                _async_results[task_id] = {
                    "status": "completed",
                    "report": full_report,
                    "raw_results": results,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                _async_results[task_id] = {
                    "status": "completed",
                    "results": results,
                    "calibration": calibration_report,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            _async_results[task_id] = {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now(timezone.utc).isoformat()
            }
    
    # Mark as running
    _async_results[task_id] = {
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Schedule background task
    background_tasks.add_task(run_tests)
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Full integration test suite started. Check /api/bionic/p03/test/result/{task_id} for results.",
        "estimated_duration": "2-5 minutes"
    }


@p03_router.get("/test/result/{task_id}")
async def get_test_result(task_id: str):
    """
    Get result of an async integration test.
    """
    if task_id not in _async_results:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return _async_results[task_id]


@p03_router.get("/calibration/quebec")
async def get_quebec_calibration_data():
    """
    Get Quebec-specific calibration data and coefficients.
    """
    return {
        "regions": QuebecCalibrationData.REGIONS,
        "monthly_temperatures": QuebecCalibrationData.MONTHLY_TEMPS,
        "rut_peaks_doy": QuebecCalibrationData.RUT_PEAKS_DOY,
        "thermal_coefficients": QuebecCalibrationData.THERMAL_COEFFICIENTS,
        "pressure_coefficients": QuebecCalibrationData.PRESSURE_COEFFICIENTS,
        "lunar_coefficients": QuebecCalibrationData.LUNAR_COEFFICIENTS,
        "harvest_density": QuebecCalibrationData.HARVEST_DENSITY,
        "data_source": "MFFP + Environnement Canada + Télémétrie GPS",
        "last_updated": "2024-12"
    }


@p03_router.get("/calibration/region")
async def get_region_calibration(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER)
):
    """
    Get calibration data for a specific region and species.
    """
    region = QuebecCalibrationData.get_region_for_coords(lat, lon)
    
    if not region:
        return {
            "location": {"lat": lat, "lon": lon},
            "region": None,
            "message": "Location is outside calibrated Quebec regions",
            "using_defaults": True
        }
    
    region_data = QuebecCalibrationData.REGIONS.get(region, {})
    harvest = QuebecCalibrationData.HARVEST_DENSITY.get(region, {})
    thermal = QuebecCalibrationData.THERMAL_COEFFICIENTS.get(species.value, {})
    
    # Current conditions
    month = datetime.now().month
    hour = datetime.now().hour
    expected_level, expected_prob = QuebecCalibrationData.get_expected_activity_level(
        species.value, month, hour
    )
    
    return {
        "location": {"lat": lat, "lon": lon},
        "region": region,
        "region_data": region_data,
        "species": species.value,
        "harvest_density": harvest.get(species.value, 1.0),
        "thermal_coefficients": thermal,
        "expected_activity": {
            "level": expected_level,
            "probability": expected_prob,
            "month": month,
            "hour": hour
        },
        "primary_species": region_data.get("primary_species", [])
    }


@p03_router.get("/coherence/matrix")
async def get_coherence_matrix(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    species: SpeciesCode = Query(default=SpeciesCode.DEER)
):
    """
    Run coherence matrix analysis for a location.
    
    Tests the logical consistency between all 6 engines.
    """
    try:
        result = await integration_tester.run_full_integration_test(lat, lon, species)
        
        return {
            "location": {"lat": lat, "lon": lon},
            "species": species.value,
            "coherence": result.get("coherence", {}),
            "calibration": result.get("calibration", {}),
            "raw_scores": result.get("raw_scores", {}),
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Coherence matrix error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@p03_router.get("/report/summary")
async def get_integration_summary():
    """
    Get summary of all integration tests run in this session.
    """
    if not integration_tester.test_results:
        return {
            "message": "No tests have been run yet",
            "run_tests_at": "/api/bionic/p03/test/full"
        }
    
    results = integration_tester.test_results
    
    # Summary stats
    total = len(results)
    coherence_scores = [r.get("coherence", {}).get("overall_score", 0) for r in results]
    avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
    
    regions = list(set(r.get("region") for r in results if r.get("region")))
    species = list(set(r.get("species") for r in results))
    
    return {
        "summary": {
            "total_tests": total,
            "average_coherence_score": round(avg_coherence, 3),
            "regions_tested": regions,
            "species_tested": species,
            "behavior_suite_status": "VALIDATED" if avg_coherence >= 0.7 else "NEEDS_REVIEW"
        },
        "latest_tests": results[-5:] if results else [],
        "recommendation": "Run /api/bionic/p03/test/full for comprehensive analysis"
    }


logger.info("BIONIC™ P0-3 API Router loaded")
