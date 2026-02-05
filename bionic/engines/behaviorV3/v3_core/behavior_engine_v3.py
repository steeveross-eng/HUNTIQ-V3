"""
BIONIC™ P3 - BehaviorEngine v3.0 (Auto-Calibrant)
==================================================
Moteur principal d'intelligence adaptative avec ML supervisé.

Version: 3.0.0
Phase: P3
Architecture: Micro-service autonome, 100% isolé

Fonctionnalités:
- Auto-calibration via Gradient Boosting
- CalibrationHistoryTracker intégré
- Feedback utilisateur + données simulées
- Rollback en cas de mauvaise calibration
- Mode Maintenance compatible

IMPORTANT: Ce module est ISOLÉ et n'a aucune dépendance avec:
- Marketplace
- BehaviorFusionEngine (P2)
- Modules Géo-Suite (P1)
- Autres moteurs BIONIC
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Import path config FIRST
import sys
import os
_BASE_PATH = '/app/bionic/engines/behaviorV3'
if _BASE_PATH not in sys.path:
    sys.path.insert(0, _BASE_PATH)

from models.v3_schemas import (
    EngineStatus, EngineMetrics, WeightSet,
    TrainingRequest, TrainingResponse,
    CalibrationRequest, CalibrationResponse,
    FeedbackInput, FeedbackResponse,
    RollbackRequest, RollbackResponse,
    WeightsResponse, CalibrationHistory
)
from data.calibration_history_tracker import calibration_tracker
from data.training_data_manager import training_data_manager
from core.ml_calibrator import ml_calibrator
from core.weight_adjuster import weight_adjuster
from core.feedback_collector import feedback_collector
from core.rollback_manager import rollback_manager

logger = logging.getLogger(__name__)


class BehaviorEngineV3:
    """
    Moteur BehaviorEngine v3.0 Auto-Calibrant.
    
    Point d'entrée unique pour toutes les fonctionnalités P3:
    - Entraînement ML
    - Calibration des pondérations
    - Collecte de feedback
    - Rollback
    - Métriques et monitoring
    """
    
    def __init__(self):
        self.name = "BehaviorEngine"
        self.version = "3.0.0"
        self.phase = "P3"
        self._initialized_at = datetime.now(timezone.utc)
        self._maintenance_mode = False
        
        logger.info(f"BIONIC™ {self.name} v{self.version} ({self.phase}) initialized")
    
    # =========================================================================
    # STATUS & MONITORING
    # =========================================================================
    
    def get_status(self) -> EngineStatus:
        """Retourne le statut complet du moteur."""
        active_calibration = calibration_tracker.get_active_calibration()
        current_weights = calibration_tracker.get_current_weights()
        fb_stats = feedback_collector.get_feedback_summary()
        history = calibration_tracker.get_full_history()
        
        return EngineStatus(
            engine_name=self.name,
            version=self.version,
            phase=self.phase,
            status="operational" if not self._maintenance_mode else "maintenance",
            is_calibrated=active_calibration is not None,
            last_calibration=active_calibration.timestamp if active_calibration else None,
            active_calibration_id=active_calibration.id if active_calibration else None,
            current_weights=current_weights,
            capabilities={
                "auto_calibration": True,
                "gradient_boosting": True,
                "feedback_collection": True,
                "rollback_support": True,
                "history_tracking": True,
                "simulated_data": True,
                "multi_species": True,
                "maintenance_mode": True
            },
            total_feedbacks=fb_stats["total_feedbacks"],
            total_calibrations=history.total_calibrations,
            total_rollbacks=history.total_rollbacks
        )
    
    def get_metrics(self) -> EngineMetrics:
        """Retourne les métriques de performance du moteur."""
        fb_stats = feedback_collector.get_feedback_summary()
        history = calibration_tracker.get_full_history()
        model_status = ml_calibrator.get_model_status()
        training_stats = training_data_manager.get_training_stats()
        
        # Calculer les moyennes
        completed = [r for r in history.records if r.status.value == "completed"]
        avg_improvement = sum(r.improvement_score for r in completed) / len(completed) if completed else 0
        avg_confidence = sum(r.confidence for r in completed) / len(completed) if completed else 0
        
        return EngineMetrics(
            avg_calibration_time_ms=150.0,  # Estimation
            avg_training_time_ms=500.0,  # Estimation
            avg_prediction_time_ms=5.0,  # Estimation
            avg_improvement_score=round(avg_improvement, 2),
            avg_confidence=round(avg_confidence, 3),
            calibration_success_rate=round(history.success_rate, 1),
            total_feedbacks=fb_stats["total_feedbacks"],
            positive_feedbacks=fb_stats.get("by_type", {}).get("success", 0),
            negative_feedbacks=fb_stats.get("by_type", {}).get("failure", 0),
            feedback_rate=round(fb_stats["success_rate"], 1),
            total_training_samples=training_stats.get("feedback_count", 0) + 500,
            simulated_samples_ratio=0.8,  # 80% simulé par défaut
            total_rollbacks=history.total_rollbacks,
            rollback_rate=round(history.total_rollbacks / max(1, history.total_calibrations) * 100, 1)
        )
    
    # =========================================================================
    # TRAINING
    # =========================================================================
    
    def train(self, request: Optional[TrainingRequest] = None) -> TrainingResponse:
        """
        Lance un entraînement du modèle ML.
        
        Args:
            request: Configuration de l'entraînement (optionnel)
        
        Returns:
            TrainingResponse avec les métriques
        """
        if self._maintenance_mode:
            return TrainingResponse(
                success=False,
                training_id="",
                metrics=None,
                message="Moteur en mode maintenance",
                new_model_ready=False
            )
        
        if request is None:
            request = TrainingRequest()
        
        logger.info("BehaviorEngineV3: Starting ML training")
        return ml_calibrator.train(request)
    
    # =========================================================================
    # CALIBRATION
    # =========================================================================
    
    def calibrate(self, request: Optional[CalibrationRequest] = None) -> CalibrationResponse:
        """
        Effectue une calibration des pondérations.
        
        Args:
            request: Configuration de la calibration (optionnel)
        
        Returns:
            CalibrationResponse avec les résultats
        """
        if self._maintenance_mode:
            from models.v3_schemas import CalibrationStatus
            return CalibrationResponse(
                success=False,
                calibration_id="",
                status=CalibrationStatus.FAILED,
                weights_applied=self.get_weights().current_weights,
                improvement_score=0,
                confidence=0,
                message="Moteur en mode maintenance",
                processing_time_ms=0
            )
        
        if request is None:
            request = CalibrationRequest()
        
        logger.info("BehaviorEngineV3: Starting calibration")
        return weight_adjuster.calibrate(request)
    
    # =========================================================================
    # WEIGHTS
    # =========================================================================
    
    def get_weights(self) -> WeightsResponse:
        """Retourne les pondérations actuelles."""
        current = calibration_tracker.get_current_weights()
        active = calibration_tracker.get_active_calibration()
        
        return WeightsResponse(
            current_weights=current,
            calibration_id=active.id if active else None,
            last_updated=active.timestamp if active else None,
            is_default=active is None,
            species_optimized=active is not None
        )
    
    # =========================================================================
    # HISTORY
    # =========================================================================
    
    def get_history(
        self,
        species: Optional[str] = None,
        limit: int = 50,
        include_rolled_back: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retourne l'historique des calibrations.
        
        Args:
            species: Filtrer par espèce
            limit: Nombre max de résultats
            include_rolled_back: Inclure les calibrations rollback
        
        Returns:
            Liste des calibrations
        """
        records = calibration_tracker.get_history(
            species=species,
            limit=limit,
            include_rolled_back=include_rolled_back
        )
        
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "species": r.species,
                "territory": r.territory,
                "season": r.season,
                "status": r.status.value,
                "improvement_score": r.improvement_score,
                "confidence": r.confidence,
                "is_active": r.is_active,
                "weights_before": r.weights_before,
                "weights_after": r.weights_after
            }
            for r in records
        ]
    
    def get_full_history(self) -> CalibrationHistory:
        """Retourne l'historique complet."""
        return calibration_tracker.get_full_history()
    
    def export_history(self, format: str = "json") -> str:
        """Exporte l'historique pour analyse."""
        return calibration_tracker.export_history(format)
    
    # =========================================================================
    # FEEDBACK
    # =========================================================================
    
    def submit_feedback(self, feedback: FeedbackInput) -> FeedbackResponse:
        """
        Soumet un feedback utilisateur.
        
        Args:
            feedback: Données du feedback
        
        Returns:
            FeedbackResponse avec le résultat
        """
        logger.info(f"BehaviorEngineV3: Receiving feedback for {feedback.species}")
        return feedback_collector.submit_feedback(feedback)
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des feedbacks."""
        return feedback_collector.get_feedback_summary()
    
    # =========================================================================
    # ROLLBACK
    # =========================================================================
    
    def rollback(self, request: RollbackRequest) -> RollbackResponse:
        """
        Effectue un rollback vers une calibration précédente.
        
        Args:
            request: Configuration du rollback
        
        Returns:
            RollbackResponse avec le résultat
        """
        logger.info(f"BehaviorEngineV3: Initiating rollback to {request.calibration_id}")
        return rollback_manager.rollback(request)
    
    def get_rollback_candidates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les calibrations disponibles pour rollback."""
        return rollback_manager.get_rollback_candidates(limit)
    
    def can_rollback(self) -> Dict[str, Any]:
        """Vérifie si un rollback est possible."""
        return rollback_manager.can_rollback()
    
    # =========================================================================
    # MAINTENANCE
    # =========================================================================
    
    def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """
        Active ou désactive le mode maintenance.
        
        Args:
            enabled: True pour activer
        
        Returns:
            Status du changement
        """
        self._maintenance_mode = enabled
        status = "activé" if enabled else "désactivé"
        logger.info(f"BehaviorEngineV3: Maintenance mode {status}")
        
        return {
            "maintenance_mode": enabled,
            "message": f"Mode maintenance {status}",
            "engine_status": "maintenance" if enabled else "operational"
        }
    
    def is_maintenance_mode(self) -> bool:
        """Retourne si le mode maintenance est actif."""
        return self._maintenance_mode


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

behavior_engine_v3 = BehaviorEngineV3()

__all__ = ["BehaviorEngineV3", "behavior_engine_v3"]
