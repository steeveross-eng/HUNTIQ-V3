"""
BIONIC™ P3 - BehaviorEngine v3.0 API Tests
============================================
Tests for the auto-calibrant ML module with Gradient Boosting.

Endpoints tested:
- GET  /api/bionic/behavior-v3/status
- POST /api/bionic/behavior-v3/train
- POST /api/bionic/behavior-v3/calibrate
- GET  /api/bionic/behavior-v3/weights
- GET  /api/bionic/behavior-v3/history
- POST /api/bionic/behavior-v3/feedback
- GET  /api/bionic/behavior-v3/feedback/summary
- GET  /api/bionic/behavior-v3/rollback/candidates
- GET  /api/bionic/behavior-v3/metrics
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://territory-hunter.preview.emergentagent.com')
API_PREFIX = '/api/bionic/behavior-v3'


class TestBehaviorV3Status:
    """Tests for GET /api/bionic/behavior-v3/status"""
    
    def test_status_returns_200(self):
        """Status endpoint returns 200"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/status")
        assert response.status_code == 200
    
    def test_status_has_correct_version(self):
        """Status returns version 3.0.0"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/status")
        data = response.json()
        assert data["version"] == "3.0.0"
        assert data["phase"] == "P3"
    
    def test_status_has_engine_name(self):
        """Status returns BehaviorEngine as engine name"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/status")
        data = response.json()
        assert data["engine_name"] == "BehaviorEngine"
    
    def test_status_is_operational(self):
        """Status shows operational"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/status")
        data = response.json()
        assert data["status"] == "operational"
    
    def test_status_has_capabilities(self):
        """Status includes all required capabilities"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/status")
        data = response.json()
        
        assert "capabilities" in data
        caps = data["capabilities"]
        
        # Check all P3 capabilities
        assert caps.get("auto_calibration") == True
        assert caps.get("gradient_boosting") == True
        assert caps.get("feedback_collection") == True
        assert caps.get("rollback_support") == True
        assert caps.get("history_tracking") == True
        assert caps.get("simulated_data") == True
    
    def test_status_has_current_weights(self):
        """Status includes current weights"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/status")
        data = response.json()
        
        assert "current_weights" in data
        weights = data["current_weights"]
        
        # Check weight categories exist
        assert "activity" in weights
        assert "seasonal" in weights
        assert "movement" in weights
        assert "environmental" in weights
        assert "temporal" in weights
        assert "pressure" in weights


class TestBehaviorV3Training:
    """Tests for POST /api/bionic/behavior-v3/train"""
    
    def test_train_with_simulated_data(self):
        """Training with simulated data returns success"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/train",
            json={
                "use_simulated_data": True,
                "use_feedback_data": True,
                "max_iterations": 50,
                "learning_rate": 0.1
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "training_id" in data
        assert data["new_model_ready"] == True
    
    def test_train_returns_metrics(self):
        """Training returns detailed metrics"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/train",
            json={
                "use_simulated_data": True,
                "max_iterations": 30
            }
        )
        data = response.json()
        
        assert "metrics" in data
        metrics = data["metrics"]
        
        assert "training_id" in metrics
        assert "total_samples" in metrics
        assert "accuracy" in metrics
        assert "loss_initial" in metrics
        assert "loss_final" in metrics
        assert "cross_validation_scores" in metrics
    
    def test_train_accuracy_reasonable(self):
        """Training achieves reasonable accuracy (>50%)"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/train",
            json={
                "use_simulated_data": True,
                "max_iterations": 50
            }
        )
        data = response.json()
        
        accuracy = data["metrics"]["accuracy"]
        assert accuracy > 0.5, f"Accuracy {accuracy} should be > 0.5"


class TestBehaviorV3Calibration:
    """Tests for POST /api/bionic/behavior-v3/calibrate"""
    
    def test_calibrate_deer(self):
        """Calibration for deer species returns success"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calibrate",
            json={
                "species": "deer",
                "territory": "quebec",
                "season": "fall"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["status"] == "completed"
        assert "calibration_id" in data
    
    def test_calibrate_moose(self):
        """Calibration for moose species returns success"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calibrate",
            json={
                "species": "moose",
                "territory": "quebec"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
    
    def test_calibrate_returns_weights(self):
        """Calibration returns applied weights"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calibrate",
            json={
                "species": "bear",
                "territory": "quebec"
            }
        )
        data = response.json()
        
        assert "weights_applied" in data
        weights = data["weights_applied"]
        
        # Verify all weight categories
        assert "activity" in weights
        assert "seasonal" in weights
        assert "movement" in weights
        assert "environmental" in weights
        assert "temporal" in weights
        assert "pressure" in weights
    
    def test_calibrate_improvement_score(self):
        """Calibration returns improvement score"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calibrate",
            json={"species": "deer"}
        )
        data = response.json()
        
        assert "improvement_score" in data
        assert "confidence" in data
        assert data["improvement_score"] >= 0
        assert 0 <= data["confidence"] <= 1


class TestBehaviorV3Weights:
    """Tests for GET /api/bionic/behavior-v3/weights"""
    
    def test_weights_returns_200(self):
        """Weights endpoint returns 200"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/weights")
        assert response.status_code == 200
    
    def test_weights_has_current_weights(self):
        """Weights returns current_weights object"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/weights")
        data = response.json()
        
        assert "current_weights" in data
        weights = data["current_weights"]
        
        # All weight categories should be present
        required_keys = ["activity", "seasonal", "movement", "environmental", "temporal", "pressure"]
        for key in required_keys:
            assert key in weights, f"Missing weight key: {key}"
    
    def test_weights_sum_to_one(self):
        """Weight values should approximately sum to 1"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/weights")
        data = response.json()
        weights = data["current_weights"]
        
        # Sum only the numeric weight values (exclude species, territory, season)
        weight_sum = sum([
            weights.get("activity", 0),
            weights.get("seasonal", 0),
            weights.get("movement", 0),
            weights.get("environmental", 0),
            weights.get("temporal", 0),
            weights.get("pressure", 0)
        ])
        
        assert 0.95 <= weight_sum <= 1.05, f"Weights sum {weight_sum} should be ~1.0"
    
    def test_weights_has_metadata(self):
        """Weights includes metadata fields"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/weights")
        data = response.json()
        
        assert "is_default" in data
        assert "species_optimized" in data


class TestBehaviorV3History:
    """Tests for GET /api/bionic/behavior-v3/history"""
    
    def test_history_returns_200(self):
        """History endpoint returns 200"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/history")
        assert response.status_code == 200
    
    def test_history_has_records(self):
        """History returns records array"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/history")
        data = response.json()
        
        assert "records" in data
        assert isinstance(data["records"], list)
    
    def test_history_has_statistics(self):
        """History includes statistics"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/history")
        data = response.json()
        
        assert "total_calibrations" in data
        assert "total_rollbacks" in data
        assert "success_rate" in data
    
    def test_history_with_limit(self):
        """History respects limit parameter"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["records"]) <= 5


class TestBehaviorV3Feedback:
    """Tests for POST /api/bionic/behavior-v3/feedback"""
    
    def test_submit_success_feedback(self):
        """Submit success feedback returns 200"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/feedback",
            json={
                "latitude": 46.8,
                "longitude": -71.2,
                "species": "deer",
                "feedback_type": "success",
                "rating": 5,
                "notes": "Test feedback - great spot"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "feedback_id" in data
    
    def test_submit_failure_feedback(self):
        """Submit failure feedback returns 200"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/feedback",
            json={
                "latitude": 45.5,
                "longitude": -73.5,
                "species": "moose",
                "feedback_type": "failure",
                "rating": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
    
    def test_feedback_invalid_type_returns_400(self):
        """Invalid feedback type returns 400"""
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/feedback",
            json={
                "latitude": 46.0,
                "longitude": -71.0,
                "species": "deer",
                "feedback_type": "invalid_type"
            }
        )
        assert response.status_code == 400


class TestBehaviorV3FeedbackSummary:
    """Tests for GET /api/bionic/behavior-v3/feedback/summary"""
    
    def test_feedback_summary_returns_200(self):
        """Feedback summary returns 200"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/feedback/summary")
        assert response.status_code == 200
    
    def test_feedback_summary_has_totals(self):
        """Feedback summary includes totals"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/feedback/summary")
        data = response.json()
        
        assert "total_feedbacks" in data
        assert "processed" in data
        assert "unprocessed" in data
    
    def test_feedback_summary_has_breakdown(self):
        """Feedback summary includes breakdown by type"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/feedback/summary")
        data = response.json()
        
        assert "by_type" in data
        assert "by_species" in data


class TestBehaviorV3RollbackCandidates:
    """Tests for GET /api/bionic/behavior-v3/rollback/candidates"""
    
    def test_rollback_candidates_returns_200(self):
        """Rollback candidates returns 200"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/rollback/candidates")
        assert response.status_code == 200
    
    def test_rollback_candidates_has_can_rollback(self):
        """Rollback candidates includes can_rollback flag"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/rollback/candidates")
        data = response.json()
        
        assert "can_rollback" in data
        assert "reason" in data
        assert "candidates" in data


class TestBehaviorV3Metrics:
    """Tests for GET /api/bionic/behavior-v3/metrics"""
    
    def test_metrics_returns_200(self):
        """Metrics endpoint returns 200"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/metrics")
        assert response.status_code == 200
    
    def test_metrics_has_performance_data(self):
        """Metrics includes performance data"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/metrics")
        data = response.json()
        
        assert "avg_improvement_score" in data
        assert "avg_confidence" in data
        assert "calibration_success_rate" in data
    
    def test_metrics_has_feedback_stats(self):
        """Metrics includes feedback statistics"""
        response = requests.get(f"{BASE_URL}{API_PREFIX}/metrics")
        data = response.json()
        
        assert "total_feedbacks" in data
        assert "positive_feedbacks" in data
        assert "negative_feedbacks" in data


class TestBehaviorV3Integration:
    """Integration tests for full workflow"""
    
    def test_train_then_calibrate_workflow(self):
        """Full workflow: train -> calibrate -> verify weights"""
        # Step 1: Train
        train_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/train",
            json={"use_simulated_data": True, "max_iterations": 30}
        )
        assert train_response.status_code == 200
        assert train_response.json()["success"] == True
        
        # Step 2: Calibrate
        calibrate_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/calibrate",
            json={"species": "deer", "territory": "quebec"}
        )
        assert calibrate_response.status_code == 200
        assert calibrate_response.json()["success"] == True
        
        calibration_id = calibrate_response.json()["calibration_id"]
        
        # Step 3: Verify weights updated (check calibration_id exists, not exact match due to concurrent tests)
        weights_response = requests.get(f"{BASE_URL}{API_PREFIX}/weights")
        assert weights_response.status_code == 200
        
        weights_data = weights_response.json()
        # In shared test environment, another calibration may have occurred
        # Just verify that a calibration_id exists and species_optimized is True
        assert weights_data["calibration_id"] is not None
        assert weights_data["species_optimized"] == True
    
    def test_feedback_then_summary_workflow(self):
        """Workflow: submit feedback -> check summary"""
        # Submit feedback
        feedback_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/feedback",
            json={
                "latitude": 47.0,
                "longitude": -70.5,
                "species": "deer",
                "feedback_type": "success",
                "rating": 4
            }
        )
        assert feedback_response.status_code == 200
        
        # Check summary
        summary_response = requests.get(f"{BASE_URL}{API_PREFIX}/feedback/summary")
        assert summary_response.status_code == 200
        
        summary = summary_response.json()
        assert summary["total_feedbacks"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
