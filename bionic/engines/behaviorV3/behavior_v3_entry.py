"""
BIONIC™ P3 - BehaviorEngine v3.0 Entry Point
=============================================
Point d'entrée unique pour server.py.
Configure les paths et exporte le router.
"""

import sys
import os

# ========================================
# ÉTAPE 1: Configurer le path AVANT tout import
# ========================================
_BASE_PATH = '/app/bionic/engines/behaviorV3'
if _BASE_PATH not in sys.path:
    sys.path.insert(0, _BASE_PATH)

# ========================================
# ÉTAPE 2: Imports des sous-modules (après config path)
# ========================================
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Import des schémas
from models.v3_schemas import (
    TrainingRequest, CalibrationRequest, FeedbackInput, RollbackRequest,
    FeedbackType, RollbackReason, CalibrationStatus
)

# Import des composants data (ils ajouteront leur propre config path si besoin)
from data.calibration_history_tracker import calibration_tracker
from data.training_data_manager import training_data_manager
from data.simulated_data_generator import simulated_data_generator

# Import des composants core
from core.ml_calibrator import ml_calibrator
from core.weight_adjuster import weight_adjuster
from core.feedback_collector import feedback_collector
from core.rollback_manager import rollback_manager

logger = logging.getLogger(__name__)

# ========================================
# ÉTAPE 3: Créer le BehaviorEngine inline pour éviter import circulaire
# ========================================

class BehaviorEngineV3Inline:
    """
    Moteur BehaviorEngine v3.0 Auto-Calibrant (version inline).
    """
    
    def __init__(self):
        self.name = "BehaviorEngine"
        self.version = "3.0.0"
        self.phase = "P3"
        self._maintenance_mode = False
        logger.info(f"BIONIC™ {self.name} v{self.version} ({self.phase}) initialized")
    
    def get_status(self):
        from models.v3_schemas import EngineStatus, WeightSet
        active = calibration_tracker.get_active_calibration()
        fb_stats = feedback_collector.get_feedback_summary()
        history = calibration_tracker.get_full_history()
        
        return EngineStatus(
            engine_name=self.name,
            version=self.version,
            phase=self.phase,
            status="operational" if not self._maintenance_mode else "maintenance",
            is_calibrated=active is not None,
            last_calibration=active.timestamp if active else None,
            active_calibration_id=active.id if active else None,
            current_weights=calibration_tracker.get_current_weights(),
            total_feedbacks=fb_stats["total_feedbacks"],
            total_calibrations=history.total_calibrations,
            total_rollbacks=history.total_rollbacks
        )
    
    def get_metrics(self):
        from models.v3_schemas import EngineMetrics
        fb_stats = feedback_collector.get_feedback_summary()
        history = calibration_tracker.get_full_history()
        
        completed = [r for r in history.records if r.status.value == "completed"]
        avg_improvement = sum(r.improvement_score for r in completed) / len(completed) if completed else 0
        avg_confidence = sum(r.confidence for r in completed) / len(completed) if completed else 0
        
        return EngineMetrics(
            avg_improvement_score=round(avg_improvement, 2),
            avg_confidence=round(avg_confidence, 3),
            calibration_success_rate=round(history.success_rate, 1),
            total_feedbacks=fb_stats["total_feedbacks"],
            positive_feedbacks=fb_stats.get("by_type", {}).get("success", 0),
            negative_feedbacks=fb_stats.get("by_type", {}).get("failure", 0),
            total_rollbacks=history.total_rollbacks
        )
    
    def train(self, request=None):
        if self._maintenance_mode:
            from models.v3_schemas import TrainingResponse, TrainingMetrics
            return TrainingResponse(
                success=False, training_id="", metrics=TrainingMetrics(),
                message="Moteur en mode maintenance", new_model_ready=False
            )
        if request is None:
            request = TrainingRequest()
        return ml_calibrator.train(request)
    
    def calibrate(self, request=None):
        if self._maintenance_mode:
            from models.v3_schemas import CalibrationResponse
            return CalibrationResponse(
                success=False, calibration_id="", status=CalibrationStatus.FAILED,
                weights_applied=calibration_tracker.get_current_weights(),
                improvement_score=0, confidence=0, message="Moteur en mode maintenance",
                processing_time_ms=0
            )
        if request is None:
            request = CalibrationRequest()
        return weight_adjuster.calibrate(request)
    
    def get_weights(self):
        from models.v3_schemas import WeightsResponse
        current = calibration_tracker.get_current_weights()
        active = calibration_tracker.get_active_calibration()
        return WeightsResponse(
            current_weights=current,
            calibration_id=active.id if active else None,
            last_updated=active.timestamp if active else None,
            is_default=active is None,
            species_optimized=active is not None
        )
    
    def get_history(self, species=None, limit=50, include_rolled_back=False):
        records = calibration_tracker.get_history(species, limit, include_rolled_back)
        return [
            {
                "id": r.id, "timestamp": r.timestamp.isoformat(),
                "species": r.species, "territory": r.territory, "season": r.season,
                "status": r.status.value, "improvement_score": r.improvement_score,
                "confidence": r.confidence, "is_active": r.is_active,
                "weights_before": r.weights_before, "weights_after": r.weights_after
            }
            for r in records
        ]
    
    def get_full_history(self):
        return calibration_tracker.get_full_history()
    
    def export_history(self, format="json"):
        return calibration_tracker.export_history(format)
    
    def submit_feedback(self, feedback):
        return feedback_collector.submit_feedback(feedback)
    
    def get_feedback_summary(self):
        return feedback_collector.get_feedback_summary()
    
    def rollback(self, request):
        return rollback_manager.rollback(request)
    
    def get_rollback_candidates(self, limit=10):
        return rollback_manager.get_rollback_candidates(limit)
    
    def can_rollback(self):
        return rollback_manager.can_rollback()
    
    def set_maintenance_mode(self, enabled):
        self._maintenance_mode = enabled
        return {"maintenance_mode": enabled, "engine_status": "maintenance" if enabled else "operational"}
    
    def is_maintenance_mode(self):
        return self._maintenance_mode


# Instance singleton
behavior_engine_v3 = BehaviorEngineV3Inline()


# ========================================
# ÉTAPE 4: Définir le Router FastAPI
# ========================================

router = APIRouter(prefix="/api/bionic/behavior-v3", tags=["BehaviorEngine v3.0"])


class TrainRequestAPI(BaseModel):
    use_simulated_data: bool = True
    use_feedback_data: bool = True
    species_filter: Optional[List[str]] = None
    max_iterations: int = 100
    learning_rate: float = 0.1


class CalibrateRequestAPI(BaseModel):
    species: str = "deer"
    territory: str = "quebec"
    season: Optional[str] = None


class FeedbackRequestAPI(BaseModel):
    latitude: float
    longitude: float
    species: str = "deer"
    feedback_type: str
    rating: Optional[int] = None
    notes: Optional[str] = None


class RollbackRequestAPI(BaseModel):
    calibration_id: str
    reason: str
    notes: Optional[str] = None


class MaintenanceModeRequest(BaseModel):
    enabled: bool


@router.get("/status")
async def get_status():
    try:
        return behavior_engine_v3.get_status().model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics():
    try:
        return behavior_engine_v3.get_metrics().model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_model(request: Optional[TrainRequestAPI] = None):
    try:
        train_req = TrainingRequest(
            use_simulated_data=request.use_simulated_data if request else True,
            use_feedback_data=request.use_feedback_data if request else True,
            species_filter=request.species_filter if request else None,
            max_iterations=request.max_iterations if request else 100,
            learning_rate=request.learning_rate if request else 0.1
        ) if request else None
        response = behavior_engine_v3.train(train_req)
        return {
            "success": response.success,
            "training_id": response.training_id,
            "message": response.message,
            "new_model_ready": response.new_model_ready,
            "metrics": response.metrics.model_dump() if response.metrics else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calibrate")
async def calibrate_weights(request: Optional[CalibrateRequestAPI] = None):
    try:
        cal_req = CalibrationRequest(
            species=request.species if request else "deer",
            territory=request.territory if request else "quebec",
            season=request.season if request else None
        ) if request else None
        response = behavior_engine_v3.calibrate(cal_req)
        return {
            "success": response.success,
            "calibration_id": response.calibration_id,
            "status": response.status.value,
            "improvement_score": response.improvement_score,
            "confidence": response.confidence,
            "message": response.message,
            "weights_applied": response.weights_applied.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weights")
async def get_weights():
    try:
        response = behavior_engine_v3.get_weights()
        return {
            "current_weights": response.current_weights.model_dump(),
            "calibration_id": response.calibration_id,
            "last_updated": response.last_updated.isoformat() if response.last_updated else None,
            "is_default": response.is_default,
            "species_optimized": response.species_optimized
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    species: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    include_rolled_back: bool = False
):
    try:
        history = behavior_engine_v3.get_history(species, limit, include_rolled_back)
        full = behavior_engine_v3.get_full_history()
        return {
            "total_calibrations": full.total_calibrations,
            "total_rollbacks": full.total_rollbacks,
            "avg_improvement": full.avg_improvement,
            "success_rate": full.success_rate,
            "active_calibration_id": full.active_calibration_id,
            "records": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequestAPI):
    try:
        fb_type = FeedbackType(request.feedback_type)
        feedback = FeedbackInput(
            latitude=request.latitude,
            longitude=request.longitude,
            species=request.species,
            feedback_type=fb_type,
            rating=request.rating,
            notes=request.notes
        )
        response = behavior_engine_v3.submit_feedback(feedback)
        return {
            "success": response.success,
            "feedback_id": response.feedback_id,
            "received_at": response.received_at.isoformat(),
            "message": response.message,
            "calibration_impact": response.calibration_impact
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feedback_type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/summary")
async def get_feedback_summary():
    try:
        return behavior_engine_v3.get_feedback_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback")
async def rollback_calibration(request: RollbackRequestAPI):
    try:
        reason = RollbackReason(request.reason)
        rollback_req = RollbackRequest(
            calibration_id=request.calibration_id,
            reason=reason,
            notes=request.notes
        )
        response = behavior_engine_v3.rollback(rollback_req)
        return {
            "success": response.success,
            "rolled_back_from": response.rolled_back_from,
            "rolled_back_to": response.rolled_back_to,
            "reason": response.reason.value,
            "message": response.message,
            "weights_restored": response.weights_restored.model_dump()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reason")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rollback/candidates")
async def get_rollback_candidates(limit: int = Query(default=10, ge=1, le=50)):
    try:
        candidates = behavior_engine_v3.get_rollback_candidates(limit)
        can = behavior_engine_v3.can_rollback()
        return {
            "can_rollback": can["can_rollback"],
            "reason": can["reason"],
            "candidates": candidates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance")
async def set_maintenance_mode(request: MaintenanceModeRequest):
    try:
        return behavior_engine_v3.set_maintenance_mode(request.enabled)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export
behavior_v3_router = router
__all__ = ["behavior_v3_router", "router", "behavior_engine_v3"]
