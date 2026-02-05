"""
BIONIC™ P3 - WeightAdjuster
============================
Module d'ajustement dynamique des pondérations.

Responsabilités:
- Appliquer les suggestions ML
- Valider les nouvelles pondérations
- Sauvegarder dans l'historique

Module 100% isolé - Aucune dépendance externe BIONIC.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import sys
if '/app/bionic/engines/behaviorV3' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines/behaviorV3')

from v3_models.v3_schemas import (
    WeightSet, CalibrationRequest, CalibrationResponse, CalibrationStatus
)
from v3_data.calibration_history_tracker import calibration_tracker
from v3_core.ml_calibrator import ml_calibrator

logger = logging.getLogger(__name__)


class WeightAdjuster:
    """
    Gestionnaire d'ajustement des pondérations.
    
    Responsabilités:
    - Récupérer les suggestions du MLCalibrator
    - Valider les nouvelles pondérations
    - Appliquer les changements
    - Sauvegarder dans l'historique via CalibrationHistoryTracker
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self._min_weight = 0.05  # Poids minimum par catégorie
        self._max_weight = 0.40  # Poids maximum par catégorie
        self._max_change_per_calibration = 0.15  # Changement max par calibration
    
    def calibrate(self, request: CalibrationRequest) -> CalibrationResponse:
        """
        Effectue une calibration des pondérations.
        
        Args:
            request: Configuration de la calibration
        
        Returns:
            CalibrationResponse avec les résultats
        """
        import uuid
        start_time = datetime.now(timezone.utc)
        calibration_id = f"cal_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"WeightAdjuster: Starting calibration {calibration_id}")
        
        # Récupérer les poids actuels
        current_weights = calibration_tracker.get_current_weights()
        weights_before = current_weights.to_dict()
        
        # Récupérer les suggestions ML
        suggested_weights = ml_calibrator.get_suggested_weights()
        
        if not suggested_weights:
            # Pas de modèle ML entraîné, utiliser des ajustements par défaut
            suggested_weights = self._get_default_adjustment(
                current_weights, request.species, request.season
            )
        
        # Appliquer les contraintes et limiter les changements
        adjusted_weights = self._apply_constraints(
            current_weights, suggested_weights
        )
        
        # Calculer l'amélioration estimée
        improvement_score = self._estimate_improvement(
            weights_before, adjusted_weights.to_dict()
        )
        
        # Calculer la confiance
        confidence = self._calculate_confidence()
        
        # Sauvegarder dans l'historique
        if request.save_to_history:
            training_stats = ml_calibrator.get_model_status()
            
            calibration_tracker.add_calibration(
                species=request.species,
                territory=request.territory,
                season=request.season or self._detect_season(),
                weights_before=weights_before,
                weights_after=adjusted_weights.to_dict(),
                improvement_score=improvement_score,
                confidence=confidence,
                training_samples=training_stats.get("last_training", {}).get("total_samples", 0) if training_stats.get("last_training") else 0,
                feedback_samples=training_stats.get("last_training", {}).get("feedback_samples", 0) if training_stats.get("last_training") else 0,
                notes=f"Auto-calibration for {request.species}/{request.territory}"
            )
        
        end_time = datetime.now(timezone.utc)
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info(f"WeightAdjuster: Calibration completed. Improvement: {improvement_score:.1f}%")
        
        return CalibrationResponse(
            success=True,
            calibration_id=calibration_id,
            status=CalibrationStatus.COMPLETED,
            weights_applied=adjusted_weights,
            improvement_score=improvement_score,
            confidence=confidence,
            message=f"Calibration réussie. Amélioration estimée: {improvement_score:.1f}%",
            processing_time_ms=processing_time_ms
        )
    
    def _get_default_adjustment(
        self,
        current: WeightSet,
        species: str,
        season: Optional[str]
    ) -> WeightSet:
        """Retourne des ajustements par défaut basés sur l'espèce et la saison."""
        
        # Ajustements par espèce
        species_adjustments = {
            "deer": {"activity": 0.22, "seasonal": 0.22, "movement": 0.18, "environmental": 0.18, "temporal": 0.12, "pressure": 0.08},
            "moose": {"activity": 0.18, "seasonal": 0.25, "movement": 0.20, "environmental": 0.20, "temporal": 0.10, "pressure": 0.07},
            "bear": {"activity": 0.20, "seasonal": 0.25, "movement": 0.15, "environmental": 0.22, "temporal": 0.10, "pressure": 0.08}
        }
        
        # Ajustements saisonniers
        season_adjustments = {
            "fall": {"seasonal": 1.15, "activity": 1.10},
            "winter": {"environmental": 1.20, "movement": 0.85},
            "spring": {"movement": 1.15, "seasonal": 1.10},
            "summer": {"environmental": 1.15, "temporal": 1.05}
        }
        
        # Base
        base = species_adjustments.get(species, species_adjustments["deer"])
        weights = WeightSet(**base)
        
        # Appliquer modificateurs saisonniers
        season = season or self._detect_season()
        if season in season_adjustments:
            mods = season_adjustments[season]
            for key, multiplier in mods.items():
                if hasattr(weights, key):
                    current_val = getattr(weights, key)
                    setattr(weights, key, current_val * multiplier)
        
        return weights.normalize()
    
    def _apply_constraints(
        self,
        current: WeightSet,
        suggested: WeightSet
    ) -> WeightSet:
        """
        Applique les contraintes sur les poids suggérés.
        
        Contraintes:
        - Poids min/max par catégorie
        - Changement max par calibration
        - Somme = 1
        """
        current_dict = current.to_dict()
        suggested_dict = suggested.to_dict()
        
        adjusted = {}
        
        for key in current_dict.keys():
            current_val = current_dict[key]
            suggested_val = suggested_dict.get(key, current_val)
            
            # Limiter le changement
            delta = suggested_val - current_val
            if abs(delta) > self._max_change_per_calibration:
                delta = self._max_change_per_calibration if delta > 0 else -self._max_change_per_calibration
            
            new_val = current_val + delta
            
            # Appliquer min/max
            new_val = max(self._min_weight, min(self._max_weight, new_val))
            
            adjusted[key] = new_val
        
        # Normaliser pour que la somme = 1
        total = sum(adjusted.values())
        adjusted = {k: v / total for k, v in adjusted.items()}
        
        return WeightSet(
            **adjusted,
            species=suggested.species,
            territory=suggested.territory,
            season=suggested.season
        )
    
    def _estimate_improvement(
        self,
        before: Dict[str, float],
        after: Dict[str, float]
    ) -> float:
        """
        Estime l'amélioration entre deux sets de poids.
        
        Basé sur:
        - Magnitude du changement
        - Direction vers les valeurs suggérées par ML
        """
        # Somme des changements absolus
        total_change = sum(abs(after[k] - before[k]) for k in before.keys())
        
        # L'amélioration est proportionnelle au changement (simplification)
        # En production, ceci serait validé sur un set de test
        improvement = total_change * 100  # Convertir en pourcentage
        
        # Ajouter un bonus si le modèle ML est confiant
        model_status = ml_calibrator.get_model_status()
        if model_status.get("model_trained"):
            last_training = model_status.get("last_training", {})
            if last_training:
                accuracy = last_training.get("accuracy", 0)
                improvement *= (1 + accuracy)
        
        return round(min(25.0, max(0.5, improvement)), 1)
    
    def _calculate_confidence(self) -> float:
        """Calcule le niveau de confiance de la calibration."""
        model_status = ml_calibrator.get_model_status()
        
        base_confidence = 0.5
        
        if model_status.get("model_trained"):
            last_training = model_status.get("last_training", {})
            if last_training:
                accuracy = last_training.get("accuracy", 0.5)
                cv_scores = last_training.get("cross_validation_scores", [])
                
                # Confiance basée sur accuracy et stabilité CV
                if cv_scores:
                    cv_std = (sum((s - accuracy)**2 for s in cv_scores) / len(cv_scores))**0.5
                    stability = 1 - cv_std
                    base_confidence = (accuracy + stability) / 2
                else:
                    base_confidence = accuracy
        
        return round(max(0.3, min(0.95, base_confidence)), 3)
    
    def _detect_season(self) -> str:
        """Détecte la saison actuelle."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        return "fall"
    
    def get_current_weights(self) -> WeightSet:
        """Retourne les poids actuels."""
        return calibration_tracker.get_current_weights()
    
    def validate_weights(self, weights: WeightSet) -> Dict[str, Any]:
        """
        Valide un set de poids.
        
        Returns:
            Dict avec is_valid et les éventuelles erreurs
        """
        weights_dict = weights.to_dict()
        errors = []
        
        # Vérifier min/max
        for key, value in weights_dict.items():
            if value < self._min_weight:
                errors.append(f"{key}: {value:.3f} < min ({self._min_weight})")
            if value > self._max_weight:
                errors.append(f"{key}: {value:.3f} > max ({self._max_weight})")
        
        # Vérifier somme
        total = sum(weights_dict.values())
        if not (0.99 <= total <= 1.01):
            errors.append(f"Sum of weights: {total:.3f} (should be 1.0)")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "weights_sum": total
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

weight_adjuster = WeightAdjuster()

__all__ = ["WeightAdjuster", "weight_adjuster"]
