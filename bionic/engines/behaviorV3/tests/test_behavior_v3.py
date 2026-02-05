"""
BIONIC™ P3 - BehaviorEngine v3.0 Tests
=======================================
Tests unitaires et d'intégration pour le module v3.0 auto-calibrant.

Test Coverage:
- SimulatedDataGenerator
- CalibrationHistoryTracker
- MLCalibrator (Gradient Boosting)
- WeightAdjuster
- FeedbackCollector
- RollbackManager
- BehaviorEngineV3 (Integration)
- API Endpoints
"""

import pytest
import sys
import os

# Add paths for imports
sys.path.insert(0, '/app/bionic/engines/behaviorV3')
sys.path.insert(0, '/app/bionic/engines')

from v3_models.v3_schemas import (
    FeedbackInput, FeedbackType, TrainingRequest, CalibrationRequest,
    RollbackRequest, RollbackReason, WeightSet, CalibrationStatus
)


class TestSimulatedDataGenerator:
    """Tests pour le générateur de données simulées."""
    
    def test_generate_dataset(self):
        """Test de génération de dataset."""
        from v3_data.simulated_data_generator import simulated_data_generator
        
        dataset = simulated_data_generator.generate_dataset(n_samples=50)
        
        assert len(dataset) == 50
        assert all(hasattr(d, 'latitude') for d in dataset)
        assert all(hasattr(d, 'global_score') for d in dataset)
        assert all(0 <= d.global_score <= 100 for d in dataset)
    
    def test_species_filter(self):
        """Test du filtre par espèce."""
        from v3_data.simulated_data_generator import simulated_data_generator
        
        dataset = simulated_data_generator.generate_dataset(
            n_samples=30,
            species=["deer"]
        )
        
        assert all(d.species == "deer" for d in dataset)
    
    def test_to_training_format(self):
        """Test de conversion au format ML."""
        from v3_data.simulated_data_generator import simulated_data_generator
        
        dataset = simulated_data_generator.generate_dataset(n_samples=20)
        X, y = simulated_data_generator.to_training_format(dataset)
        
        assert len(X) == 20
        assert len(y) == 20
        assert len(X[0]) == 14  # 14 features


class TestCalibrationHistoryTracker:
    """Tests pour le tracker d'historique."""
    
    def test_add_calibration(self):
        """Test d'ajout de calibration."""
        from v3_data.calibration_history_tracker import CalibrationHistoryTracker
        
        tracker = CalibrationHistoryTracker(storage_path="/tmp/test_history.json")
        tracker.clear_history(keep_active=False)
        
        record = tracker.add_calibration(
            species="deer",
            territory="quebec",
            season="fall",
            weights_before={"activity": 0.20, "seasonal": 0.20, "movement": 0.15, "environmental": 0.20, "temporal": 0.15, "pressure": 0.10},
            weights_after={"activity": 0.22, "seasonal": 0.22, "movement": 0.14, "environmental": 0.18, "temporal": 0.14, "pressure": 0.10},
            improvement_score=5.5,
            confidence=0.75
        )
        
        assert record.id.startswith("cal_")
        assert record.species == "deer"
        assert record.is_active is True
    
    def test_get_current_weights(self):
        """Test de récupération des poids actuels."""
        from v3_data.calibration_history_tracker import CalibrationHistoryTracker
        
        tracker = CalibrationHistoryTracker(storage_path="/tmp/test_history2.json")
        weights = tracker.get_current_weights()
        
        assert isinstance(weights, WeightSet)
        assert 0 < weights.activity < 1
    
    def test_rollback(self):
        """Test de rollback."""
        from v3_data.calibration_history_tracker import CalibrationHistoryTracker
        
        tracker = CalibrationHistoryTracker(storage_path="/tmp/test_history3.json")
        tracker.clear_history(keep_active=False)
        
        # Ajouter deux calibrations
        record1 = tracker.add_calibration(
            species="deer", territory="quebec", season="fall",
            weights_before={"activity": 0.20, "seasonal": 0.20, "movement": 0.15, "environmental": 0.20, "temporal": 0.15, "pressure": 0.10},
            weights_after={"activity": 0.22, "seasonal": 0.22, "movement": 0.14, "environmental": 0.18, "temporal": 0.14, "pressure": 0.10},
            improvement_score=5.0, confidence=0.70
        )
        
        record2 = tracker.add_calibration(
            species="deer", territory="quebec", season="fall",
            weights_before={"activity": 0.22, "seasonal": 0.22, "movement": 0.14, "environmental": 0.18, "temporal": 0.14, "pressure": 0.10},
            weights_after={"activity": 0.25, "seasonal": 0.20, "movement": 0.15, "environmental": 0.18, "temporal": 0.12, "pressure": 0.10},
            improvement_score=3.0, confidence=0.65
        )
        
        # Rollback vers la première
        restored = tracker.rollback_to(record1.id, RollbackReason.USER_REQUEST)
        
        assert restored is not None
        assert tracker._history.active_calibration_id == record1.id


class TestMLCalibrator:
    """Tests pour le calibrateur ML."""
    
    def test_train(self):
        """Test d'entraînement du modèle."""
        from v3_core.ml_calibrator import MLCalibrator
        
        calibrator = MLCalibrator()
        request = TrainingRequest(
            use_simulated_data=True,
            use_feedback_data=False,
            max_iterations=50
        )
        
        response = calibrator.train(request)
        
        assert response.success is True
        assert response.new_model_ready is True
        assert response.metrics is not None
        assert response.metrics.total_samples >= 10
    
    def test_get_suggested_weights(self):
        """Test de suggestion de poids."""
        from v3_core.ml_calibrator import MLCalibrator
        
        calibrator = MLCalibrator()
        calibrator.train(TrainingRequest(max_iterations=30))
        
        suggested = calibrator.get_suggested_weights()
        
        assert suggested is not None
        weights_dict = suggested.to_dict()
        assert abs(sum(weights_dict.values()) - 1.0) < 0.01


class TestWeightAdjuster:
    """Tests pour l'ajusteur de poids."""
    
    def test_calibrate(self):
        """Test de calibration."""
        from v3_core.weight_adjuster import WeightAdjuster
        
        adjuster = WeightAdjuster()
        request = CalibrationRequest(species="deer", territory="quebec")
        
        response = adjuster.calibrate(request)
        
        assert response.success is True
        assert response.status == CalibrationStatus.COMPLETED
        assert 0 < response.confidence <= 1
    
    def test_validate_weights(self):
        """Test de validation des poids."""
        from v3_core.weight_adjuster import WeightAdjuster
        
        adjuster = WeightAdjuster()
        
        valid_weights = WeightSet(
            activity=0.20, seasonal=0.20, movement=0.15,
            environmental=0.20, temporal=0.15, pressure=0.10
        )
        
        result = adjuster.validate_weights(valid_weights)
        assert result["is_valid"] is True


class TestFeedbackCollector:
    """Tests pour le collecteur de feedback."""
    
    def test_submit_feedback(self):
        """Test de soumission de feedback."""
        from v3_core.feedback_collector import FeedbackCollector
        
        collector = FeedbackCollector()
        
        feedback = FeedbackInput(
            latitude=46.8,
            longitude=-71.2,
            species="deer",
            feedback_type=FeedbackType.SUCCESS,
            rating=5,
            notes="Excellent spot!"
        )
        
        response = collector.submit_feedback(feedback)
        
        assert response.success is True
        assert response.feedback_id.startswith("fb_")
    
    def test_get_feedback_summary(self):
        """Test du résumé des feedbacks."""
        from v3_core.feedback_collector import FeedbackCollector
        
        collector = FeedbackCollector()
        summary = collector.get_feedback_summary()
        
        assert "total_feedbacks" in summary
        assert "calibration_ready" in summary


class TestRollbackManager:
    """Tests pour le gestionnaire de rollback."""
    
    def test_can_rollback(self):
        """Test de vérification de rollback."""
        from v3_core.rollback_manager import RollbackManager
        
        manager = RollbackManager()
        result = manager.can_rollback()
        
        assert "can_rollback" in result
        assert "reason" in result
    
    def test_get_rollback_candidates(self):
        """Test de récupération des candidats."""
        from v3_core.rollback_manager import RollbackManager
        
        manager = RollbackManager()
        candidates = manager.get_rollback_candidates(limit=5)
        
        assert isinstance(candidates, list)


class TestBehaviorEngineV3:
    """Tests d'intégration pour le moteur principal."""
    
    def test_get_status(self):
        """Test du statut du moteur."""
        from v3_core.behavior_engine_v3 import BehaviorEngineV3
        
        engine = BehaviorEngineV3()
        status = engine.get_status()
        
        assert status.engine_name == "BehaviorEngine"
        assert status.version == "3.0.0"
        assert status.phase == "P3"
        assert status.status in ["operational", "maintenance"]
    
    def test_train_and_calibrate_workflow(self):
        """Test du workflow complet train + calibrate."""
        from v3_core.behavior_engine_v3 import BehaviorEngineV3
        
        engine = BehaviorEngineV3()
        
        # 1. Train
        train_response = engine.train(TrainingRequest(max_iterations=30))
        assert train_response.success is True
        
        # 2. Calibrate
        cal_response = engine.calibrate(CalibrationRequest(species="moose"))
        assert cal_response.success is True
        
        # 3. Get weights
        weights = engine.get_weights()
        assert weights.species_optimized is True
    
    def test_get_metrics(self):
        """Test des métriques."""
        from v3_core.behavior_engine_v3 import BehaviorEngineV3
        
        engine = BehaviorEngineV3()
        metrics = engine.get_metrics()
        
        assert metrics.avg_calibration_time_ms >= 0
        assert 0 <= metrics.calibration_success_rate <= 100
    
    def test_maintenance_mode(self):
        """Test du mode maintenance."""
        from v3_core.behavior_engine_v3 import BehaviorEngineV3
        
        engine = BehaviorEngineV3()
        
        # Activer
        result = engine.set_maintenance_mode(True)
        assert result["maintenance_mode"] is True
        assert engine.is_maintenance_mode() is True
        
        # Désactiver
        result = engine.set_maintenance_mode(False)
        assert result["maintenance_mode"] is False


class TestAPIEndpoints:
    """Tests pour les endpoints API (mocked)."""
    
    def test_status_endpoint_data(self):
        """Test des données retournées par status."""
        from v3_core.behavior_engine_v3 import behavior_engine_v3
        
        status = behavior_engine_v3.get_status()
        data = status.model_dump()
        
        assert "engine_name" in data
        assert "version" in data
        assert "capabilities" in data
        assert data["capabilities"]["auto_calibration"] is True
    
    def test_weights_endpoint_data(self):
        """Test des données retournées par weights."""
        from v3_core.behavior_engine_v3 import behavior_engine_v3
        
        weights_response = behavior_engine_v3.get_weights()
        
        assert weights_response.current_weights is not None
        weights_dict = weights_response.current_weights.to_dict()
        assert len(weights_dict) == 6  # 6 catégories


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
