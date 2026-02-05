"""
BIONIC™ P3 - BehaviorEngine v3.0 API Endpoints
================================================
Endpoints FastAPI internes pour le module v3.0 auto-calibrant.

Routes:
- GET  /api/bionic/behavior-v3/status          → État du moteur
- POST /api/bionic/behavior-v3/train           → Entraînement ML
- POST /api/bionic/behavior-v3/calibrate       → Calibration des poids
- GET  /api/bionic/behavior-v3/weights         → Pondérations actuelles
- GET  /api/bionic/behavior-v3/history         → Historique des calibrations
- POST /api/bionic/behavior-v3/rollback        → Rollback
- GET  /api/bionic/behavior-v3/metrics         → Métriques de performance
- POST /api/bionic/behavior-v3/feedback        → Soumission feedback chasseur

Module 100% isolé - Aucune dépendance externe BIONIC.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

import sys
if '/app/bionic/engines/behaviorV3' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines/behaviorV3')

from v3_models.v3_schemas import (
    TrainingRequest, CalibrationRequest, FeedbackInput, RollbackRequest,
    FeedbackType, RollbackReason
)
from v3_core.behavior_engine_v3 import behavior_engine_v3

logger = logging.getLogger(__name__)

# Router avec prefix
router = APIRouter(prefix="/api/bionic/behavior-v3", tags=["BehaviorEngine v3.0"])
behavior_v3_router = router  # Alias pour l'import


# =============================================================================
# REQUEST/RESPONSE MODELS FOR API
# =============================================================================

class TrainRequestAPI(BaseModel):
    """Requête d'entraînement via API."""
    use_simulated_data: bool = Field(default=True, description="Utiliser données simulées")
    use_feedback_data: bool = Field(default=True, description="Utiliser feedback utilisateur")
    species_filter: Optional[List[str]] = Field(default=None, description="Filtrer par espèces")
    max_iterations: int = Field(default=100, ge=10, le=500, description="Max itérations")
    learning_rate: float = Field(default=0.1, ge=0.01, le=1.0, description="Taux apprentissage")


class CalibrateRequestAPI(BaseModel):
    """Requête de calibration via API."""
    species: str = Field(default="deer", description="Espèce cible")
    territory: str = Field(default="quebec", description="Territoire")
    season: Optional[str] = Field(default=None, description="Saison (auto-détectée)")


class FeedbackRequestAPI(BaseModel):
    """Requête de feedback via API."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    species: str = Field(default="deer", description="Espèce ciblée")
    feedback_type: str = Field(..., description="Type: success, partial, failure, observation, rating")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Note 1-5")
    notes: Optional[str] = Field(default=None, max_length=500, description="Notes")
    weather_conditions: Optional[str] = Field(default=None, description="Conditions météo")
    time_of_day: Optional[str] = Field(default=None, description="Moment de la journée")
    hunt_duration_hours: Optional[float] = Field(default=None, ge=0, description="Durée chasse")
    animals_observed: Optional[int] = Field(default=None, ge=0, description="Animaux observés")
    harvest_success: Optional[bool] = Field(default=None, description="Récolte réussie")


class RollbackRequestAPI(BaseModel):
    """Requête de rollback via API."""
    calibration_id: str = Field(..., description="ID de la calibration cible")
    reason: str = Field(..., description="Raison: performance_drop, user_request, invalid_weights, system_error, maintenance")
    notes: Optional[str] = Field(default=None, description="Notes additionnelles")


class MaintenanceModeRequest(BaseModel):
    """Requête pour le mode maintenance."""
    enabled: bool = Field(..., description="Activer/désactiver le mode maintenance")


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status")
async def get_status():
    """
    Retourne le statut complet du BehaviorEngine v3.0.
    
    Inclut:
    - Version et phase
    - État de calibration
    - Capacités actives
    - Statistiques globales
    """
    try:
        status = behavior_engine_v3.get_status()
        return status.model_dump()
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics():
    """
    Retourne les métriques de performance du moteur.
    
    Inclut:
    - Temps moyens (calibration, training, prediction)
    - Scores moyens
    - Taux de succès/rollback
    - Statistiques feedback
    """
    try:
        metrics = behavior_engine_v3.get_metrics()
        return metrics.model_dump()
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_model(request: Optional[TrainRequestAPI] = None):
    """
    Lance un entraînement du modèle ML Gradient Boosting.
    
    L'entraînement utilise:
    - Données simulées (calibrées sur le Québec)
    - Feedbacks utilisateurs réels
    
    Retourne les métriques d'entraînement.
    """
    try:
        if request:
            train_request = TrainingRequest(
                use_simulated_data=request.use_simulated_data,
                use_feedback_data=request.use_feedback_data,
                species_filter=request.species_filter,
                max_iterations=request.max_iterations,
                learning_rate=request.learning_rate
            )
        else:
            train_request = None
        
        response = behavior_engine_v3.train(train_request)
        
        result = {
            "success": response.success,
            "training_id": response.training_id,
            "message": response.message,
            "new_model_ready": response.new_model_ready
        }
        
        if response.metrics:
            result["metrics"] = response.metrics.model_dump()
        
        return result
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calibrate")
async def calibrate_weights(request: Optional[CalibrateRequestAPI] = None):
    """
    Effectue une calibration des pondérations.
    
    Utilise le modèle ML entraîné pour suggérer de nouvelles pondérations
    optimisées pour l'espèce et le territoire spécifiés.
    """
    try:
        if request:
            cal_request = CalibrationRequest(
                species=request.species,
                territory=request.territory,
                season=request.season,
                apply_immediately=True,
                save_to_history=True
            )
        else:
            cal_request = None
        
        response = behavior_engine_v3.calibrate(cal_request)
        
        return {
            "success": response.success,
            "calibration_id": response.calibration_id,
            "status": response.status.value,
            "improvement_score": response.improvement_score,
            "confidence": response.confidence,
            "message": response.message,
            "processing_time_ms": response.processing_time_ms,
            "weights_applied": response.weights_applied.model_dump()
        }
    except Exception as e:
        logger.error(f"Error calibrating: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weights")
async def get_weights():
    """
    Retourne les pondérations actuelles.
    
    Inclut:
    - Poids par catégorie (activity, seasonal, movement, etc.)
    - ID de la calibration active
    - Indicateur si ce sont les poids par défaut
    """
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
        logger.error(f"Error getting weights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_calibration_history(
    species: Optional[str] = Query(default=None, description="Filtrer par espèce"),
    limit: int = Query(default=50, ge=1, le=200, description="Nombre max de résultats"),
    include_rolled_back: bool = Query(default=False, description="Inclure les rollbacks")
):
    """
    Retourne l'historique des calibrations.
    
    Permet de filtrer par espèce et de limiter les résultats.
    """
    try:
        history = behavior_engine_v3.get_history(
            species=species,
            limit=limit,
            include_rolled_back=include_rolled_back
        )
        
        full_history = behavior_engine_v3.get_full_history()
        
        return {
            "total_calibrations": full_history.total_calibrations,
            "total_rollbacks": full_history.total_rollbacks,
            "avg_improvement": full_history.avg_improvement,
            "success_rate": full_history.success_rate,
            "active_calibration_id": full_history.active_calibration_id,
            "records": history
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/export")
async def export_history(
    format: str = Query(default="json", description="Format: json ou csv")
):
    """
    Exporte l'historique des calibrations pour analyse externe.
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        data = behavior_engine_v3.export_history(format)
        return {"format": format, "data": data}
    except Exception as e:
        logger.error(f"Error exporting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequestAPI):
    """
    Soumet un feedback chasseur.
    
    Les feedbacks sont utilisés pour améliorer la calibration du modèle.
    Types de feedback:
    - success: Chasse réussie
    - partial: Partiellement utile
    - failure: Échec / non pertinent
    - observation: Observation sans chasse
    - rating: Note 1-5
    """
    try:
        # Convertir le type de feedback
        try:
            fb_type = FeedbackType(request.feedback_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid feedback_type. Valid values: {[t.value for t in FeedbackType]}"
            )
        
        feedback = FeedbackInput(
            latitude=request.latitude,
            longitude=request.longitude,
            species=request.species,
            feedback_type=fb_type,
            rating=request.rating,
            notes=request.notes,
            weather_conditions=request.weather_conditions,
            time_of_day=request.time_of_day,
            hunt_duration_hours=request.hunt_duration_hours,
            animals_observed=request.animals_observed,
            harvest_success=request.harvest_success
        )
        
        response = behavior_engine_v3.submit_feedback(feedback)
        
        return {
            "success": response.success,
            "feedback_id": response.feedback_id,
            "received_at": response.received_at.isoformat(),
            "message": response.message,
            "calibration_impact": response.calibration_impact
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/summary")
async def get_feedback_summary():
    """
    Retourne un résumé des feedbacks collectés.
    """
    try:
        return behavior_engine_v3.get_feedback_summary()
    except Exception as e:
        logger.error(f"Error getting feedback summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback")
async def rollback_calibration(request: RollbackRequestAPI):
    """
    Effectue un rollback vers une calibration précédente.
    
    Raisons valides:
    - performance_drop: Dégradation des performances
    - user_request: Demande utilisateur
    - invalid_weights: Poids invalides
    - system_error: Erreur système
    - maintenance: Maintenance
    """
    try:
        # Convertir la raison
        try:
            reason = RollbackReason(request.reason)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid reason. Valid values: {[r.value for r in RollbackReason]}"
            )
        
        rollback_request = RollbackRequest(
            calibration_id=request.calibration_id,
            reason=reason,
            notes=request.notes
        )
        
        response = behavior_engine_v3.rollback(rollback_request)
        
        return {
            "success": response.success,
            "rolled_back_from": response.rolled_back_from,
            "rolled_back_to": response.rolled_back_to,
            "reason": response.reason.value,
            "message": response.message,
            "weights_restored": response.weights_restored.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during rollback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rollback/candidates")
async def get_rollback_candidates(
    limit: int = Query(default=10, ge=1, le=50, description="Nombre max de candidats")
):
    """
    Retourne les calibrations disponibles pour rollback.
    """
    try:
        candidates = behavior_engine_v3.get_rollback_candidates(limit)
        can_rollback = behavior_engine_v3.can_rollback()
        
        return {
            "can_rollback": can_rollback["can_rollback"],
            "reason": can_rollback["reason"],
            "candidates_count": can_rollback["candidates_count"],
            "candidates": candidates
        }
    except Exception as e:
        logger.error(f"Error getting rollback candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance")
async def set_maintenance_mode(request: MaintenanceModeRequest):
    """
    Active ou désactive le mode maintenance.
    
    En mode maintenance, les opérations de training et calibration sont désactivées.
    """
    try:
        result = behavior_engine_v3.set_maintenance_mode(request.enabled)
        return result
    except Exception as e:
        logger.error(f"Error setting maintenance mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ["router", "behavior_v3_router"]
