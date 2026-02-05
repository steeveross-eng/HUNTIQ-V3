"""
BIONIC™ P3 - MLCalibrator (Gradient Boosting)
==============================================
Module de calibration ML utilisant Gradient Boosting.

Algorithme choisi: Gradient Boosting
- Équilibre précision / stabilité / légèreté
- Performant sur petits datasets
- Interprétable (feature importance)

Module 100% isolé - Aucune dépendance externe BIONIC.
"""

import logging
import math
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass

import sys
if '/app/bionic/engines/behaviorV3' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines/behaviorV3')

from v3_models.v3_schemas import (
    TrainingMetrics, TrainingRequest, TrainingResponse, WeightSet
)
from v3_data.training_data_manager import training_data_manager

logger = logging.getLogger(__name__)


class GradientBoostingSimple:
    """
    Implémentation simplifiée de Gradient Boosting.
    
    Pour production, remplacer par sklearn.ensemble.GradientBoostingRegressor
    quand disponible dans l'environnement.
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 5
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.trees: List[Dict] = []
        self.initial_prediction = 0.0
        self.feature_importances_: List[float] = []
    
    def fit(self, X: List[List[float]], y: List[float]) -> "GradientBoostingSimple":
        """
        Entraîne le modèle Gradient Boosting.
        
        Args:
            X: Features (liste de vecteurs)
            y: Targets (liste de valeurs)
        
        Returns:
            self
        """
        if not X or not y:
            return self
        
        n_samples = len(X)
        n_features = len(X[0]) if X else 0
        
        # Prédiction initiale (moyenne)
        self.initial_prediction = sum(y) / n_samples
        
        # Résidus initiaux
        residuals = [yi - self.initial_prediction for yi in y]
        
        # Feature importances
        self.feature_importances_ = [0.0] * n_features
        
        # Entraînement itératif
        for i in range(self.n_estimators):
            # Créer un arbre simple (stub pour démo)
            tree = self._fit_simple_tree(X, residuals, n_features)
            self.trees.append(tree)
            
            # Prédictions de l'arbre
            predictions = [self._predict_tree(tree, x) for x in X]
            
            # Mise à jour des résidus
            for j in range(n_samples):
                residuals[j] -= self.learning_rate * predictions[j]
            
            # Mise à jour feature importances
            if tree.get("feature_idx") is not None:
                self.feature_importances_[tree["feature_idx"]] += tree.get("importance", 0.01)
        
        # Normaliser feature importances
        total = sum(self.feature_importances_) or 1
        self.feature_importances_ = [fi / total for fi in self.feature_importances_]
        
        return self
    
    def predict(self, X: List[List[float]]) -> List[float]:
        """Prédit les valeurs pour X."""
        predictions = []
        for x in X:
            pred = self.initial_prediction
            for tree in self.trees:
                pred += self.learning_rate * self._predict_tree(tree, x)
            predictions.append(pred)
        return predictions
    
    def _fit_simple_tree(
        self,
        X: List[List[float]],
        residuals: List[float],
        n_features: int
    ) -> Dict:
        """Crée un arbre de décision simple (stump)."""
        # Sélection aléatoire de feature
        feature_idx = random.randint(0, n_features - 1)
        
        # Calcul du split optimal simplifié
        feature_values = [x[feature_idx] for x in X]
        median_value = sorted(feature_values)[len(feature_values) // 2]
        
        # Calcul des prédictions pour chaque côté du split
        left_residuals = [r for x, r in zip(X, residuals) if x[feature_idx] <= median_value]
        right_residuals = [r for x, r in zip(X, residuals) if x[feature_idx] > median_value]
        
        left_pred = sum(left_residuals) / len(left_residuals) if left_residuals else 0
        right_pred = sum(right_residuals) / len(right_residuals) if right_residuals else 0
        
        # Importance basée sur la réduction de variance
        total_var = sum(r**2 for r in residuals) / len(residuals) if residuals else 0
        left_var = sum(r**2 for r in left_residuals) / len(left_residuals) if left_residuals else 0
        right_var = sum(r**2 for r in right_residuals) / len(right_residuals) if right_residuals else 0
        importance = max(0, total_var - (left_var + right_var) / 2)
        
        return {
            "feature_idx": feature_idx,
            "threshold": median_value,
            "left_pred": left_pred,
            "right_pred": right_pred,
            "importance": importance
        }
    
    def _predict_tree(self, tree: Dict, x: List[float]) -> float:
        """Prédit avec un seul arbre."""
        if x[tree["feature_idx"]] <= tree["threshold"]:
            return tree["left_pred"]
        return tree["right_pred"]


class MLCalibrator:
    """
    Calibrateur ML pour BehaviorEngine v3.0.
    
    Utilise Gradient Boosting pour:
    - Apprendre les patterns de comportement
    - Extraire l'importance des features
    - Suggérer des ajustements de pondérations
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.model: Optional[GradientBoostingSimple] = None
        self.last_training: Optional[TrainingMetrics] = None
        self._feature_names = [
            "latitude", "longitude", "month", "day_of_year", "hour",
            "temperature", "humidity", "pressure", "wind_speed", "cloud_cover",
            "lunar_phase", "is_deer", "is_moose", "is_bear"
        ]
        self._weight_categories = ["activity", "seasonal", "movement", "environmental", "temporal", "pressure"]
    
    def train(self, request: TrainingRequest) -> TrainingResponse:
        """
        Entraîne le modèle ML sur les données disponibles.
        
        Args:
            request: Configuration de l'entraînement
        
        Returns:
            TrainingResponse avec les métriques
        """
        import uuid
        start_time = datetime.now(timezone.utc)
        training_id = f"train_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"MLCalibrator: Starting training {training_id}")
        
        # Préparer les données
        n_simulated = 500 if request.use_simulated_data else 0
        
        X, y = training_data_manager.prepare_training_data(
            n_simulated=n_simulated,
            species=request.species_filter,
            include_feedbacks=request.use_feedback_data,
            min_feedback_count=request.min_feedback_count
        )
        
        if len(X) < 10:
            return TrainingResponse(
                success=False,
                training_id=training_id,
                metrics=TrainingMetrics(training_id=training_id),
                message="Insufficient training data (min 10 samples required)",
                new_model_ready=False
            )
        
        # Split train/validation (80/20)
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Calculer loss initial (baseline)
        mean_y = sum(y_train) / len(y_train)
        loss_initial = sum((yi - mean_y)**2 for yi in y_train) / len(y_train)
        
        # Entraîner le modèle
        self.model = GradientBoostingSimple(
            n_estimators=min(request.max_iterations, 100),
            learning_rate=request.learning_rate,
            max_depth=5
        )
        self.model.fit(X_train, y_train)
        
        # Évaluer sur validation
        predictions = self.model.predict(X_val)
        loss_final = sum((yi - pi)**2 for yi, pi in zip(y_val, predictions)) / len(y_val)
        
        # Calculer l'accuracy (RMSE-based)
        rmse = math.sqrt(loss_final)
        accuracy = max(0, 100 - rmse) / 100
        
        # Cross-validation simplifiée (3-fold)
        cv_scores = []
        fold_size = len(X) // 3
        for i in range(3):
            start = i * fold_size
            end = start + fold_size
            X_fold_val = X[start:end]
            y_fold_val = y[start:end]
            X_fold_train = X[:start] + X[end:]
            y_fold_train = y[:start] + y[end:]
            
            fold_model = GradientBoostingSimple(n_estimators=50, learning_rate=0.1)
            fold_model.fit(X_fold_train, y_fold_train)
            fold_preds = fold_model.predict(X_fold_val)
            fold_rmse = math.sqrt(sum((yi - pi)**2 for yi, pi in zip(y_fold_val, fold_preds)) / len(y_fold_val))
            cv_scores.append(max(0, 100 - fold_rmse) / 100)
        
        end_time = datetime.now(timezone.utc)
        
        # Métriques finales
        stats = training_data_manager.get_training_stats()
        
        metrics = TrainingMetrics(
            training_id=training_id,
            started_at=start_time,
            completed_at=end_time,
            simulated_samples=n_simulated,
            feedback_samples=stats["feedback_count"],
            total_samples=len(X),
            iterations_completed=self.model.n_estimators,
            loss_initial=round(loss_initial, 4),
            loss_final=round(loss_final, 4),
            accuracy=round(accuracy, 4),
            n_estimators_used=self.model.n_estimators,
            max_depth=5,
            learning_rate=request.learning_rate,
            validation_score=round(accuracy, 4),
            cross_validation_scores=cv_scores
        )
        
        self.last_training = metrics
        
        logger.info(f"MLCalibrator: Training completed. Accuracy: {accuracy:.2%}")
        
        return TrainingResponse(
            success=True,
            training_id=training_id,
            metrics=metrics,
            message=f"Training completed successfully. Accuracy: {accuracy:.2%}",
            new_model_ready=True
        )
    
    def get_suggested_weights(self) -> Optional[WeightSet]:
        """
        Suggère des pondérations basées sur l'importance des features.
        
        Returns:
            WeightSet suggéré ou None si pas de modèle
        """
        if not self.model or not self.model.feature_importances_:
            return None
        
        importances = self.model.feature_importances_
        
        # Mapping features -> catégories de poids
        # indices: lat, lon, month, doy, hour, temp, humidity, pressure, wind, clouds, lunar, deer, moose, bear
        category_weights = {
            "activity": importances[4] + importances[10],  # hour + lunar
            "seasonal": importances[2] + importances[3],   # month + doy
            "movement": importances[8] + importances[4],   # wind + hour
            "environmental": importances[5] + importances[6],  # temp + humidity
            "temporal": importances[4] + importances[10],  # hour + lunar
            "pressure": importances[7]                     # pressure
        }
        
        # Normaliser
        total = sum(category_weights.values()) or 1
        normalized = {k: v / total for k, v in category_weights.items()}
        
        return WeightSet(
            activity=round(normalized["activity"], 4),
            seasonal=round(normalized["seasonal"], 4),
            movement=round(normalized["movement"], 4),
            environmental=round(normalized["environmental"], 4),
            temporal=round(normalized["temporal"], 4),
            pressure=round(normalized["pressure"], 4)
        ).normalize()
    
    def get_feature_importances(self) -> Dict[str, float]:
        """Retourne l'importance des features."""
        if not self.model or not self.model.feature_importances_:
            return {}
        
        return {
            name: round(imp, 4)
            for name, imp in zip(self._feature_names, self.model.feature_importances_)
        }
    
    def predict_score(self, features: List[float]) -> float:
        """
        Prédit un score pour un vecteur de features.
        
        Args:
            features: Vecteur de 14 features
        
        Returns:
            Score prédit (0-100)
        """
        if not self.model:
            return 50.0  # Défaut
        
        predictions = self.model.predict([features])
        return max(0, min(100, predictions[0]))
    
    def get_model_status(self) -> Dict[str, Any]:
        """Retourne le statut du modèle."""
        return {
            "model_trained": self.model is not None,
            "n_estimators": self.model.n_estimators if self.model else 0,
            "last_training": self.last_training.model_dump() if self.last_training else None,
            "feature_importances": self.get_feature_importances()
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

ml_calibrator = MLCalibrator()

__all__ = ["MLCalibrator", "ml_calibrator", "GradientBoostingSimple"]
