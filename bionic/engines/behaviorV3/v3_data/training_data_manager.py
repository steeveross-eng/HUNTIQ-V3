"""
BIONIC™ P3 - TrainingDataManager
=================================
Gestionnaire des données d'entraînement pour le ML.

Combine:
- Données simulées (SimulatedDataGenerator)
- Feedback utilisateur réel

Module 100% isolé - Aucune dépendance externe.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path

import sys
if '/app/bionic/engines/behaviorV3' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines/behaviorV3')

from v3_models.v3_schemas import FeedbackInput, FeedbackType
from v3_data.simulated_data_generator import simulated_data_generator, SimulatedDataPoint

logger = logging.getLogger(__name__)


class FeedbackRecord:
    """Enregistrement d'un feedback utilisateur."""
    
    def __init__(
        self,
        feedback_id: str,
        feedback_input: FeedbackInput,
        received_at: datetime,
        processed: bool = False
    ):
        self.feedback_id = feedback_id
        self.feedback_input = feedback_input
        self.received_at = received_at
        self.processed = processed
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "feedback_input": self.feedback_input.model_dump(),
            "received_at": self.received_at.isoformat(),
            "processed": self.processed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackRecord":
        return cls(
            feedback_id=data["feedback_id"],
            feedback_input=FeedbackInput(**data["feedback_input"]),
            received_at=datetime.fromisoformat(data["received_at"]),
            processed=data.get("processed", False)
        )


class TrainingDataManager:
    """
    Gestionnaire centralisé des données d'entraînement.
    
    Responsabilités:
    - Stocker les feedbacks utilisateurs
    - Générer des données simulées à la demande
    - Combiner les deux sources pour l'entraînement
    - Préparer les datasets au format ML
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.version = "1.0.0"
        self._storage_path = storage_path or "/app/bionic/engines/behaviorV3/data/feedback_store.json"
        self._feedbacks: List[FeedbackRecord] = []
        self._load_feedbacks()
    
    def _load_feedbacks(self) -> None:
        """Charge les feedbacks depuis le stockage."""
        try:
            if os.path.exists(self._storage_path):
                with open(self._storage_path, 'r') as f:
                    data = json.load(f)
                    self._feedbacks = [FeedbackRecord.from_dict(fb) for fb in data]
                    logger.info(f"TrainingDataManager: Loaded {len(self._feedbacks)} feedbacks")
            else:
                logger.info("TrainingDataManager: No existing feedbacks, starting fresh")
        except Exception as e:
            logger.warning(f"TrainingDataManager: Failed to load feedbacks: {e}")
            self._feedbacks = []
    
    def _save_feedbacks(self) -> None:
        """Sauvegarde les feedbacks dans le stockage."""
        try:
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            data = [fb.to_dict() for fb in self._feedbacks]
            with open(self._storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug("TrainingDataManager: Feedbacks saved")
        except Exception as e:
            logger.error(f"TrainingDataManager: Failed to save feedbacks: {e}")
    
    # =========================================================================
    # FEEDBACK MANAGEMENT
    # =========================================================================
    
    def add_feedback(self, feedback: FeedbackInput) -> str:
        """
        Ajoute un nouveau feedback utilisateur.
        
        Args:
            feedback: Données du feedback
        
        Returns:
            ID du feedback créé
        """
        import uuid
        feedback_id = f"fb_{uuid.uuid4().hex[:12]}"
        
        record = FeedbackRecord(
            feedback_id=feedback_id,
            feedback_input=feedback,
            received_at=datetime.now(timezone.utc)
        )
        
        self._feedbacks.append(record)
        self._save_feedbacks()
        
        logger.info(f"TrainingDataManager: Added feedback {feedback_id}")
        return feedback_id
    
    def get_feedbacks(
        self,
        species: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        processed: Optional[bool] = None,
        limit: int = 100
    ) -> List[FeedbackRecord]:
        """
        Récupère les feedbacks avec filtres optionnels.
        
        Args:
            species: Filtrer par espèce
            feedback_type: Filtrer par type
            processed: Filtrer par statut de traitement
            limit: Nombre max de résultats
        
        Returns:
            Liste de FeedbackRecord
        """
        results = self._feedbacks.copy()
        
        if species:
            results = [fb for fb in results if fb.feedback_input.species == species]
        
        if feedback_type:
            results = [fb for fb in results if fb.feedback_input.feedback_type == feedback_type]
        
        if processed is not None:
            results = [fb for fb in results if fb.processed == processed]
        
        # Trier par date décroissante
        results.sort(key=lambda fb: fb.received_at, reverse=True)
        
        return results[:limit]
    
    def mark_feedback_processed(self, feedback_id: str) -> bool:
        """Marque un feedback comme traité."""
        for fb in self._feedbacks:
            if fb.feedback_id == feedback_id:
                fb.processed = True
                self._save_feedbacks()
                return True
        return False
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des feedbacks."""
        total = len(self._feedbacks)
        processed = sum(1 for fb in self._feedbacks if fb.processed)
        
        by_type = {}
        for fb in self._feedbacks:
            t = fb.feedback_input.feedback_type.value
            by_type[t] = by_type.get(t, 0) + 1
        
        by_species = {}
        for fb in self._feedbacks:
            s = fb.feedback_input.species
            by_species[s] = by_species.get(s, 0) + 1
        
        return {
            "total_feedbacks": total,
            "processed": processed,
            "unprocessed": total - processed,
            "by_type": by_type,
            "by_species": by_species
        }
    
    # =========================================================================
    # TRAINING DATA PREPARATION
    # =========================================================================
    
    def prepare_training_data(
        self,
        n_simulated: int = 500,
        species: Optional[List[str]] = None,
        include_feedbacks: bool = True,
        min_feedback_count: int = 5
    ) -> Tuple[List[List[float]], List[float]]:
        """
        Prépare un dataset combiné pour l'entraînement ML.
        
        Args:
            n_simulated: Nombre de données simulées à générer
            species: Liste des espèces à inclure
            include_feedbacks: Inclure les feedbacks utilisateurs
            min_feedback_count: Minimum de feedbacks pour les inclure
        
        Returns:
            (X, y) - Features et targets pour l'entraînement
        """
        X = []
        y = []
        
        # 1. Données simulées
        if n_simulated > 0:
            simulated = simulated_data_generator.generate_dataset(
                n_samples=n_simulated,
                species=species
            )
            sim_X, sim_y = simulated_data_generator.to_training_format(simulated)
            X.extend(sim_X)
            y.extend(sim_y)
            logger.info(f"TrainingDataManager: Added {len(sim_X)} simulated samples")
        
        # 2. Feedbacks utilisateurs
        if include_feedbacks:
            feedbacks = self._feedbacks
            
            if species:
                feedbacks = [fb for fb in feedbacks if fb.feedback_input.species in species]
            
            if len(feedbacks) >= min_feedback_count:
                fb_X, fb_y = self._feedbacks_to_training_format(feedbacks)
                X.extend(fb_X)
                y.extend(fb_y)
                logger.info(f"TrainingDataManager: Added {len(fb_X)} feedback samples")
        
        logger.info(f"TrainingDataManager: Total training samples: {len(X)}")
        return X, y
    
    def _feedbacks_to_training_format(
        self,
        feedbacks: List[FeedbackRecord]
    ) -> Tuple[List[List[float]], List[float]]:
        """Convertit les feedbacks en format ML."""
        X = []
        y = []
        
        for fb in feedbacks:
            inp = fb.feedback_input
            
            # Features basiques
            features = [
                inp.latitude,
                inp.longitude,
                inp.observation_date.month if inp.observation_date else 10,
                inp.observation_date.timetuple().tm_yday if inp.observation_date else 280,
                12,  # Heure par défaut (midi)
                10.0,  # Température par défaut
                60.0,  # Humidité par défaut
                1013.0,  # Pression par défaut
                10.0,  # Vent par défaut
                50.0,  # Nuages par défaut
                0.5,  # Phase lunaire par défaut
                # One-hot species
                1 if inp.species == "deer" else 0,
                1 if inp.species == "moose" else 0,
                1 if inp.species == "bear" else 0
            ]
            
            # Target basé sur le type de feedback
            target_map = {
                FeedbackType.SUCCESS: 85.0,
                FeedbackType.PARTIAL: 60.0,
                FeedbackType.FAILURE: 30.0,
                FeedbackType.OBSERVATION: 55.0,
                FeedbackType.RATING: (inp.rating or 3) * 20.0
            }
            target = target_map.get(inp.feedback_type, 50.0)
            
            X.append(features)
            y.append(target)
        
        return X, y
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des données d'entraînement disponibles."""
        fb_stats = self.get_feedback_stats()
        
        return {
            "feedback_count": fb_stats["total_feedbacks"],
            "feedback_by_type": fb_stats["by_type"],
            "feedback_by_species": fb_stats["by_species"],
            "simulated_available": True,
            "recommended_simulated_samples": max(500, 1000 - fb_stats["total_feedbacks"]),
            "data_balance": {
                "has_enough_data": fb_stats["total_feedbacks"] >= 10 or True,  # Toujours True avec simulé
                "recommended_action": "train" if fb_stats["total_feedbacks"] >= 10 else "collect_more_feedback"
            }
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

training_data_manager = TrainingDataManager()

__all__ = ["TrainingDataManager", "training_data_manager", "FeedbackRecord"]
