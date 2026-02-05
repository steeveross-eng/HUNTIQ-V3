"""
BIONIC™ P3 - CalibrationHistoryTracker
=======================================
Accélérateur stratégique pour le suivi de l'historique des calibrations.

Fonctionnalités:
- Historique complet des calibrations (timestamp, poids avant/après, métriques)
- Rollback vers n'importe quelle calibration précédente
- Export des données pour analyse externe
- Compatibilité future multi-sources (P4+)

Module 100% isolé - Aucune dépendance externe.
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

import sys
if '/app/bionic/engines/behaviorV3' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines/behaviorV3')

from models.v3_schemas import (
    CalibrationRecord, CalibrationHistory, CalibrationStatus,
    WeightSet, RollbackReason
)

logger = logging.getLogger(__name__)


class CalibrationHistoryTracker:
    """
    Gestionnaire de l'historique des calibrations.
    
    Stockage local isolé, compatible avec le mode Maintenance.
    Prêt pour l'intégration multi-sources (P4+).
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.version = "1.0.0"
        self._storage_path = storage_path or "/app/bionic/engines/behaviorV3/data/calibration_history.json"
        self._history: CalibrationHistory = CalibrationHistory()
        self._default_weights = self._get_default_weights()
        self._load_history()
    
    def _get_default_weights(self) -> WeightSet:
        """Retourne les poids par défaut."""
        return WeightSet(
            activity=0.20,
            seasonal=0.20,
            movement=0.15,
            environmental=0.20,
            temporal=0.15,
            pressure=0.10,
            species="deer",
            territory="quebec",
            season="fall"
        )
    
    def _load_history(self) -> None:
        """Charge l'historique depuis le fichier de stockage."""
        try:
            if os.path.exists(self._storage_path):
                with open(self._storage_path, 'r') as f:
                    data = json.load(f)
                    self._history = CalibrationHistory(**data)
                    logger.info(f"CalibrationHistoryTracker: Loaded {len(self._history.records)} records")
            else:
                logger.info("CalibrationHistoryTracker: No existing history, starting fresh")
        except Exception as e:
            logger.warning(f"CalibrationHistoryTracker: Failed to load history: {e}")
            self._history = CalibrationHistory()
    
    def _save_history(self) -> None:
        """Sauvegarde l'historique dans le fichier de stockage."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            
            # Convert to JSON-serializable format
            data = self._history.model_dump()
            
            # Handle datetime serialization
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            def process_dict(d):
                if isinstance(d, dict):
                    return {k: process_dict(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [process_dict(item) for item in d]
                else:
                    return serialize_datetime(d)
            
            data = process_dict(data)
            
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("CalibrationHistoryTracker: History saved")
        except Exception as e:
            logger.error(f"CalibrationHistoryTracker: Failed to save history: {e}")
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def add_calibration(
        self,
        species: str,
        territory: str,
        season: str,
        weights_before: Dict[str, float],
        weights_after: Dict[str, float],
        improvement_score: float,
        confidence: float,
        training_samples: int = 0,
        feedback_samples: int = 0,
        notes: Optional[str] = None
    ) -> CalibrationRecord:
        """
        Ajoute une nouvelle calibration à l'historique.
        
        Args:
            species: Espèce ciblée
            territory: Territoire
            season: Saison
            weights_before: Poids avant calibration
            weights_after: Poids après calibration
            improvement_score: Score d'amélioration (%)
            confidence: Niveau de confiance (0-1)
            training_samples: Nombre d'échantillons d'entraînement
            feedback_samples: Nombre de feedbacks utilisés
            notes: Notes additionnelles
        
        Returns:
            CalibrationRecord créé
        """
        # Désactiver la calibration précédente si elle existe
        if self._history.active_calibration_id:
            for record in self._history.records:
                if record.id == self._history.active_calibration_id:
                    record.is_active = False
                    break
        
        # Créer le nouvel enregistrement
        record = CalibrationRecord(
            species=species,
            territory=territory,
            season=season,
            weights_before=weights_before,
            weights_after=weights_after,
            improvement_score=improvement_score,
            confidence=confidence,
            training_samples=training_samples,
            feedback_samples=feedback_samples,
            status=CalibrationStatus.COMPLETED,
            notes=notes,
            is_active=True
        )
        
        # Ajouter à l'historique
        self._history.records.append(record)
        self._history.total_calibrations += 1
        self._history.active_calibration_id = record.id
        
        # Recalculer les statistiques
        self._update_statistics()
        
        # Sauvegarder
        self._save_history()
        
        logger.info(f"CalibrationHistoryTracker: Added calibration {record.id}")
        return record
    
    def get_calibration(self, calibration_id: str) -> Optional[CalibrationRecord]:
        """Récupère une calibration par son ID."""
        for record in self._history.records:
            if record.id == calibration_id:
                return record
        return None
    
    def get_active_calibration(self) -> Optional[CalibrationRecord]:
        """Récupère la calibration active."""
        if self._history.active_calibration_id:
            return self.get_calibration(self._history.active_calibration_id)
        return None
    
    def get_current_weights(self) -> WeightSet:
        """Récupère les poids actuels (calibration active ou défaut)."""
        active = self.get_active_calibration()
        if active:
            return WeightSet(
                **active.weights_after,
                species=active.species,
                territory=active.territory,
                season=active.season
            )
        return self._default_weights
    
    def get_history(
        self,
        species: Optional[str] = None,
        limit: int = 50,
        include_rolled_back: bool = False
    ) -> List[CalibrationRecord]:
        """
        Récupère l'historique des calibrations.
        
        Args:
            species: Filtrer par espèce
            limit: Nombre max de résultats
            include_rolled_back: Inclure les calibrations rollback
        
        Returns:
            Liste des CalibrationRecord
        """
        records = self._history.records.copy()
        
        # Filtrer par espèce
        if species:
            records = [r for r in records if r.species == species]
        
        # Filtrer les rollbacks
        if not include_rolled_back:
            records = [r for r in records if r.status != CalibrationStatus.ROLLED_BACK]
        
        # Trier par timestamp décroissant
        records.sort(key=lambda r: r.timestamp, reverse=True)
        
        return records[:limit]
    
    def rollback_to(
        self,
        calibration_id: str,
        reason: RollbackReason,
        notes: Optional[str] = None
    ) -> Optional[CalibrationRecord]:
        """
        Rollback vers une calibration précédente.
        
        Args:
            calibration_id: ID de la calibration cible
            reason: Raison du rollback
            notes: Notes additionnelles
        
        Returns:
            CalibrationRecord vers laquelle on a rollback, ou None si échec
        """
        target = self.get_calibration(calibration_id)
        if not target:
            logger.error(f"CalibrationHistoryTracker: Calibration {calibration_id} not found")
            return None
        
        # Marquer la calibration active comme rollback
        current_active = self.get_active_calibration()
        if current_active:
            current_active.is_active = False
            current_active.status = CalibrationStatus.ROLLED_BACK
            current_active.rolled_back_at = datetime.now(timezone.utc)
            current_active.rollback_reason = reason
        
        # Activer la calibration cible
        target.is_active = True
        self._history.active_calibration_id = target.id
        self._history.total_rollbacks += 1
        
        # Recalculer les statistiques
        self._update_statistics()
        
        # Sauvegarder
        self._save_history()
        
        logger.info(f"CalibrationHistoryTracker: Rolled back to {calibration_id}")
        return target
    
    def get_full_history(self) -> CalibrationHistory:
        """Retourne l'historique complet."""
        return self._history
    
    def export_history(self, format: str = "json") -> str:
        """
        Exporte l'historique pour analyse externe.
        
        Args:
            format: Format d'export ("json" ou "csv")
        
        Returns:
            Données exportées
        """
        if format == "json":
            data = self._history.model_dump()
            
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            def process_dict(d):
                if isinstance(d, dict):
                    return {k: process_dict(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [process_dict(item) for item in d]
                else:
                    return serialize_datetime(d)
            
            return json.dumps(process_dict(data), indent=2)
        
        elif format == "csv":
            lines = ["id,timestamp,species,territory,season,improvement_score,confidence,status"]
            for record in self._history.records:
                lines.append(
                    f"{record.id},{record.timestamp.isoformat()},{record.species},"
                    f"{record.territory},{record.season},{record.improvement_score},"
                    f"{record.confidence},{record.status.value}"
                )
            return "\n".join(lines)
        
        return ""
    
    def clear_history(self, keep_active: bool = True) -> None:
        """
        Efface l'historique.
        
        Args:
            keep_active: Garder la calibration active
        """
        if keep_active and self._history.active_calibration_id:
            active = self.get_active_calibration()
            self._history.records = [active] if active else []
        else:
            self._history.records = []
            self._history.active_calibration_id = None
        
        self._history.total_calibrations = len(self._history.records)
        self._history.total_rollbacks = 0
        self._update_statistics()
        self._save_history()
        
        logger.info("CalibrationHistoryTracker: History cleared")
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _update_statistics(self) -> None:
        """Met à jour les statistiques de l'historique."""
        completed = [r for r in self._history.records if r.status == CalibrationStatus.COMPLETED]
        
        if completed:
            self._history.avg_improvement = sum(r.improvement_score for r in completed) / len(completed)
            self._history.success_rate = len(completed) / self._history.total_calibrations * 100 if self._history.total_calibrations > 0 else 0
        else:
            self._history.avg_improvement = 0.0
            self._history.success_rate = 0.0


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

calibration_tracker = CalibrationHistoryTracker()

__all__ = ["CalibrationHistoryTracker", "calibration_tracker"]
