"""
BIONIC™ P3 - RollbackManager
==============================
Module de gestion des rollbacks de calibration.

Responsabilités:
- Rollback vers une calibration précédente
- Validation avant rollback
- Logging des rollbacks

Module 100% isolé - Aucune dépendance externe BIONIC.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import sys
if '/app/bionic/engines/behaviorV3' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines/behaviorV3')

from models.v3_schemas import (
    RollbackRequest, RollbackResponse, RollbackReason, WeightSet, CalibrationRecord
)
from data.calibration_history_tracker import calibration_tracker

logger = logging.getLogger(__name__)


class RollbackManager:
    """
    Gestionnaire des rollbacks de calibration.
    
    Permet de revenir à une calibration précédente en cas de:
    - Dégradation des performances
    - Demande utilisateur
    - Erreur système
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self._rollback_log: list = []
    
    def rollback(self, request: RollbackRequest) -> RollbackResponse:
        """
        Effectue un rollback vers une calibration précédente.
        
        Args:
            request: Configuration du rollback
        
        Returns:
            RollbackResponse avec le résultat
        """
        logger.info(f"RollbackManager: Initiating rollback to {request.calibration_id}")
        
        # Vérifier que la calibration cible existe
        target = calibration_tracker.get_calibration(request.calibration_id)
        if not target:
            return RollbackResponse(
                success=False,
                rolled_back_from="",
                rolled_back_to=request.calibration_id,
                weights_restored=calibration_tracker.get_current_weights(),
                reason=request.reason,
                message=f"Calibration {request.calibration_id} non trouvée"
            )
        
        # Récupérer la calibration active actuelle
        current = calibration_tracker.get_active_calibration()
        current_id = current.id if current else "default"
        
        # Effectuer le rollback
        restored = calibration_tracker.rollback_to(
            calibration_id=request.calibration_id,
            reason=request.reason,
            notes=request.notes
        )
        
        if not restored:
            return RollbackResponse(
                success=False,
                rolled_back_from=current_id,
                rolled_back_to=request.calibration_id,
                weights_restored=calibration_tracker.get_current_weights(),
                reason=request.reason,
                message="Échec du rollback"
            )
        
        # Logger le rollback
        self._log_rollback(
            from_id=current_id,
            to_id=request.calibration_id,
            reason=request.reason,
            notes=request.notes
        )
        
        # Récupérer les poids restaurés
        weights_restored = WeightSet(
            **restored.weights_after,
            species=restored.species,
            territory=restored.territory,
            season=restored.season
        )
        
        logger.info(f"RollbackManager: Successfully rolled back from {current_id} to {request.calibration_id}")
        
        return RollbackResponse(
            success=True,
            rolled_back_from=current_id,
            rolled_back_to=request.calibration_id,
            weights_restored=weights_restored,
            reason=request.reason,
            message=f"Rollback réussi vers la calibration {request.calibration_id}"
        )
    
    def _log_rollback(
        self,
        from_id: str,
        to_id: str,
        reason: RollbackReason,
        notes: Optional[str]
    ) -> None:
        """Enregistre un rollback dans le log."""
        self._rollback_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from_calibration": from_id,
            "to_calibration": to_id,
            "reason": reason.value,
            "notes": notes
        })
    
    def get_rollback_candidates(self, limit: int = 10) -> list:
        """
        Retourne les calibrations disponibles pour rollback.
        
        Args:
            limit: Nombre max de candidats
        
        Returns:
            Liste des calibrations candidates
        """
        history = calibration_tracker.get_history(
            include_rolled_back=False,
            limit=limit + 1  # +1 pour exclure l'active
        )
        
        # Exclure la calibration active
        active_id = calibration_tracker._history.active_calibration_id
        candidates = [
            {
                "calibration_id": record.id,
                "timestamp": record.timestamp.isoformat(),
                "species": record.species,
                "territory": record.territory,
                "season": record.season,
                "improvement_score": record.improvement_score,
                "confidence": record.confidence,
                "is_active": record.id == active_id
            }
            for record in history
            if record.id != active_id
        ]
        
        return candidates[:limit]
    
    def get_rollback_history(self, limit: int = 20) -> list:
        """Retourne l'historique des rollbacks."""
        return self._rollback_log[-limit:]
    
    def can_rollback(self) -> Dict[str, Any]:
        """
        Vérifie si un rollback est possible.
        
        Returns:
            Dict avec can_rollback et la raison
        """
        history = calibration_tracker.get_history(include_rolled_back=False, limit=10)
        active_id = calibration_tracker._history.active_calibration_id
        
        # Filtrer l'active
        candidates = [r for r in history if r.id != active_id]
        
        if not candidates:
            return {
                "can_rollback": False,
                "reason": "Aucune calibration précédente disponible",
                "candidates_count": 0
            }
        
        return {
            "can_rollback": True,
            "reason": f"{len(candidates)} calibration(s) disponible(s) pour rollback",
            "candidates_count": len(candidates),
            "oldest_candidate": candidates[-1].timestamp.isoformat() if candidates else None
        }
    
    def suggest_rollback(self) -> Optional[Dict[str, Any]]:
        """
        Suggère un rollback si les performances se dégradent.
        
        Pour l'instant, retourne None (feature future).
        En production, analyserait les métriques récentes.
        """
        # Placeholder pour la détection automatique de dégradation
        # Sera implémenté avec plus de données de feedback
        return None


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

rollback_manager = RollbackManager()

__all__ = ["RollbackManager", "rollback_manager"]
