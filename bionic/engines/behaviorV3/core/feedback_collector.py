"""
BIONIC™ P3 - FeedbackCollector
================================
Module de collecte et gestion des feedbacks utilisateurs.

Responsabilités:
- Recevoir les feedbacks chasseurs
- Valider et stocker les données
- Déterminer l'impact sur la calibration

Module 100% isolé - Aucune dépendance externe BIONIC.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import sys
if '/app/bionic/engines/behaviorV3' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines/behaviorV3')

from models.v3_schemas import (
    FeedbackInput, FeedbackResponse, FeedbackType
)
from data.training_data_manager import training_data_manager

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """
    Collecteur de feedbacks utilisateurs.
    
    Responsabilités:
    - Recevoir et valider les feedbacks
    - Déterminer l'impact sur la calibration
    - Fournir des statistiques
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self._immediate_calibration_threshold = 50  # Nombre de feedbacks pour déclencher calibration
        self._high_impact_types = [FeedbackType.SUCCESS, FeedbackType.FAILURE]
    
    def submit_feedback(self, feedback: FeedbackInput) -> FeedbackResponse:
        """
        Soumet un nouveau feedback.
        
        Args:
            feedback: Données du feedback
        
        Returns:
            FeedbackResponse avec le résultat
        """
        # Valider le feedback
        validation = self._validate_feedback(feedback)
        if not validation["is_valid"]:
            return FeedbackResponse(
                success=False,
                feedback_id="",
                received_at=datetime.now(timezone.utc),
                message=f"Feedback invalide: {validation['error']}",
                calibration_impact="none"
            )
        
        # Stocker le feedback
        feedback_id = training_data_manager.add_feedback(feedback)
        
        # Déterminer l'impact sur la calibration
        impact = self._determine_calibration_impact(feedback)
        
        logger.info(f"FeedbackCollector: Received feedback {feedback_id} (impact: {impact})")
        
        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            received_at=datetime.now(timezone.utc),
            message="Feedback enregistré avec succès. Merci pour votre contribution!",
            calibration_impact=impact
        )
    
    def _validate_feedback(self, feedback: FeedbackInput) -> Dict[str, Any]:
        """Valide un feedback."""
        errors = []
        
        # Coordonnées
        if not (-90 <= feedback.latitude <= 90):
            errors.append("Latitude invalide")
        if not (-180 <= feedback.longitude <= 180):
            errors.append("Longitude invalide")
        
        # Rating (si fourni)
        if feedback.rating is not None and not (1 <= feedback.rating <= 5):
            errors.append("Rating doit être entre 1 et 5")
        
        # Espèce
        valid_species = ["deer", "moose", "bear", "caribou", "turkey", "waterfowl"]
        if feedback.species not in valid_species:
            errors.append(f"Espèce invalide: {feedback.species}")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None
        }
    
    def _determine_calibration_impact(self, feedback: FeedbackInput) -> str:
        """
        Détermine l'impact du feedback sur la calibration.
        
        Returns:
            "immediate": Déclenche calibration immédiate
            "queued": Ajouté à la queue pour prochaine calibration
            "minimal": Impact minimal
        """
        stats = training_data_manager.get_feedback_stats()
        total_feedbacks = stats["total_feedbacks"]
        
        # Feedbacks de haute importance
        if feedback.feedback_type in self._high_impact_types:
            if total_feedbacks >= self._immediate_calibration_threshold:
                return "immediate"
            return "queued"
        
        # Feedbacks standard
        if total_feedbacks >= self._immediate_calibration_threshold * 2:
            return "queued"
        
        return "minimal"
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des feedbacks collectés."""
        stats = training_data_manager.get_feedback_stats()
        
        # Calculer le taux de succès
        by_type = stats.get("by_type", {})
        successes = by_type.get(FeedbackType.SUCCESS.value, 0)
        failures = by_type.get(FeedbackType.FAILURE.value, 0)
        total_outcomes = successes + failures
        
        success_rate = successes / total_outcomes if total_outcomes > 0 else 0
        
        return {
            "total_feedbacks": stats["total_feedbacks"],
            "processed": stats["processed"],
            "unprocessed": stats["unprocessed"],
            "by_type": stats["by_type"],
            "by_species": stats["by_species"],
            "success_rate": round(success_rate * 100, 1),
            "calibration_ready": stats["total_feedbacks"] >= self._immediate_calibration_threshold,
            "feedbacks_until_calibration": max(0, self._immediate_calibration_threshold - stats["total_feedbacks"])
        }
    
    def get_recent_feedbacks(self, limit: int = 10) -> list:
        """Retourne les feedbacks récents."""
        return [
            {
                "id": fb.feedback_id,
                "species": fb.feedback_input.species,
                "type": fb.feedback_input.feedback_type.value,
                "rating": fb.feedback_input.rating,
                "received_at": fb.received_at.isoformat(),
                "processed": fb.processed
            }
            for fb in training_data_manager.get_feedbacks(limit=limit)
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

feedback_collector = FeedbackCollector()

__all__ = ["FeedbackCollector", "feedback_collector"]
