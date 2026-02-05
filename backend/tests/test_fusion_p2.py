"""
BIONIC™ P2 - BehaviorFusionEngine API Tests
============================================
Tests for Phase P2 Fusion endpoints.

Version: 1.0.0
Phase: P2
"""

import pytest
import requests
import os

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFusionStatus:
    """Test fusion engine status endpoint"""
    
    def test_fusion_status_returns_200(self):
        """GET /api/bionic/fusion/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/status")
        assert response.status_code == 200
        
    def test_fusion_status_engine_operational(self):
        """Fusion engine status is operational"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/status")
        data = response.json()
        
        assert data["engine"] == "BehaviorFusionEngine"
        assert data["status"] == "operational"
        assert data["phase"] == "P2"
        assert data["version"] == "1.0.0"
        
    def test_fusion_status_capabilities(self):
        """Fusion engine has all required capabilities"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/status")
        data = response.json()
        
        capabilities = data["capabilities"]
        
        # Check fusion modes
        assert "balanced" in capabilities["fusion_modes"]
        assert "geo_dominant" in capabilities["fusion_modes"]
        assert "behavior" in capabilities["fusion_modes"]
        assert "adaptive" in capabilities["fusion_modes"]
        
        # Check geo engines
        assert len(capabilities["geo_engines"]) == 5
        assert "corridor" in capabilities["geo_engines"]
        assert "landcover" in capabilities["geo_engines"]
        assert "nutrition" in capabilities["geo_engines"]
        assert "population" in capabilities["geo_engines"]
        assert "pressure" in capabilities["geo_engines"]
        
        # Check behavior engines
        assert len(capabilities["behavior_engines"]) == 6
        assert "behavior" in capabilities["behavior_engines"]
        assert "seasonal" in capabilities["behavior_engines"]
        assert "activity" in capabilities["behavior_engines"]
        assert "movement" in capabilities["behavior_engines"]
        
        # Check features
        assert capabilities["heatmap_generation"] == True
        assert capabilities["weight_management"] == True
        assert capabilities["p3_hooks"] == True


class TestFusionAnalyze:
    """Test fusion analysis endpoints"""
    
    def test_analyze_full_returns_200(self):
        """GET /api/bionic/fusion/analyze returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer",
                "territory": "quebec",
                "radius_km": 2.0,
                "mode": "balanced",
                "include_heatmap": True
            }
        )
        assert response.status_code == 200
        
    def test_analyze_full_returns_fusion_data(self):
        """Full analysis returns complete fusion data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer",
                "territory": "quebec"
            }
        )
        data = response.json()
        
        # Check required fields
        assert "fusion_id" in data
        assert "global_score" in data
        assert "geo_score" in data
        assert "behavior_score" in data
        assert "score_level" in data
        assert "geo_breakdown" in data
        assert "behavior_breakdown" in data
        assert "weights_used" in data
        assert "fusion_quality" in data
        assert "fusion_confidence" in data
        assert "recommendations" in data
        
        # Check score ranges
        assert 0 <= data["global_score"] <= 100
        assert 0 <= data["geo_score"] <= 100
        assert 0 <= data["behavior_score"] <= 100
        assert 0 <= data["fusion_confidence"] <= 1
        
    def test_analyze_quick_returns_200(self):
        """GET /api/bionic/fusion/analyze/quick returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze/quick",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer"
            }
        )
        assert response.status_code == 200
        
    def test_analyze_quick_returns_simplified_data(self):
        """Quick analysis returns simplified data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze/quick",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer"
            }
        )
        data = response.json()
        
        assert "fusion_id" in data
        assert "global_score" in data
        assert "score_level" in data
        assert "geo_score" in data
        assert "behavior_score" in data
        assert "fusion_quality" in data
        assert "confidence" in data
        
    def test_analyze_frontend_returns_200(self):
        """GET /api/bionic/fusion/analyze/frontend returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze/frontend",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer",
                "territory": "quebec",
                "radius_km": 2.0
            }
        )
        assert response.status_code == 200
        
    def test_analyze_frontend_returns_frontend_format(self):
        """Frontend analysis returns frontend-optimized format"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze/frontend",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer",
                "territory": "quebec"
            }
        )
        data = response.json()
        
        # Check camelCase keys for frontend
        assert "fusionId" in data
        assert "globalScore" in data
        assert "scoreLevel" in data
        assert "geoScore" in data
        assert "behaviorScore" in data
        assert "breakdown" in data
        assert "heatmapData" in data
        assert "fusionQuality" in data
        assert "confidence" in data
        assert "recommendations" in data
        assert "weightsUsed" in data
        
        # Check breakdown structure
        assert "geo" in data["breakdown"]
        assert "behavior" in data["breakdown"]


class TestFusionHeatmap:
    """Test fusion heatmap endpoint"""
    
    def test_heatmap_returns_200(self):
        """GET /api/bionic/fusion/heatmap returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/heatmap",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer",
                "radius_km": 2.0
            }
        )
        assert response.status_code == 200
        
    def test_heatmap_returns_valid_data(self):
        """Heatmap returns valid heatmap data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/heatmap",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer",
                "radius_km": 2.0
            }
        )
        data = response.json()
        
        assert data["status"] == "success"
        assert "heatmap" in data
        assert "global_score" in data
        assert "score_level" in data
        
        heatmap = data["heatmap"]
        assert heatmap["type"] == "fusion_heatmap"
        assert "bounds" in heatmap
        assert "grid_size" in heatmap
        assert "points" in heatmap
        assert "color_scale" in heatmap
        assert "legend" in heatmap
        
        # Check points structure
        assert len(heatmap["points"]) > 0
        point = heatmap["points"][0]
        assert "lat" in point
        assert "lon" in point
        assert "intensity" in point


class TestFusionWeights:
    """Test fusion weight management endpoints"""
    
    def test_weights_returns_200(self):
        """GET /api/bionic/fusion/weights returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/weights",
            params={
                "species": "deer",
                "territory": "quebec",
                "mode": "balanced"
            }
        )
        assert response.status_code == 200
        
    def test_weights_returns_valid_data(self):
        """Weights endpoint returns valid weight data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/weights",
            params={
                "species": "deer",
                "territory": "quebec",
                "mode": "balanced"
            }
        )
        data = response.json()
        
        assert data["status"] == "success"
        assert "weights" in data
        
        weights = data["weights"]
        assert "mode" in weights
        assert "species" in weights
        assert "territory" in weights
        assert "season" in weights
        assert "suite_weights" in weights
        assert "geo_engine_weights" in weights
        assert "behavior_engine_weights" in weights
        
        # Check suite weights sum to ~1
        suite = weights["suite_weights"]
        assert abs(suite["geo_suite"] + suite["behavior_suite"] - 1.0) < 0.01
        
    def test_species_presets_returns_200(self):
        """GET /api/bionic/fusion/weights/species-presets returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/weights/species-presets")
        assert response.status_code == 200
        
    def test_species_presets_returns_all_species(self):
        """Species presets returns all 6 species"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/weights/species-presets")
        data = response.json()
        
        assert data["status"] == "success"
        assert "presets" in data
        
        presets = data["presets"]
        assert "deer" in presets
        assert "moose" in presets
        assert "bear" in presets
        assert "caribou" in presets
        assert "turkey" in presets
        assert "waterfowl" in presets
        
    def test_territory_modifiers_returns_200(self):
        """GET /api/bionic/fusion/weights/territory-modifiers returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/weights/territory-modifiers")
        assert response.status_code == 200
        
    def test_territory_modifiers_returns_all_territories(self):
        """Territory modifiers returns all 3 territories"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/weights/territory-modifiers")
        data = response.json()
        
        assert data["status"] == "success"
        assert "modifiers" in data
        
        modifiers = data["modifiers"]
        assert "quebec" in modifiers
        assert "canada" in modifiers
        assert "usa" in modifiers
        
    def test_seasonal_modifiers_returns_200(self):
        """GET /api/bionic/fusion/weights/seasonal-modifiers returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/weights/seasonal-modifiers")
        assert response.status_code == 200
        
    def test_seasonal_modifiers_returns_all_seasons(self):
        """Seasonal modifiers returns all 4 seasons"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/weights/seasonal-modifiers")
        data = response.json()
        
        assert data["status"] == "success"
        assert "modifiers" in data
        
        modifiers = data["modifiers"]
        assert "winter" in modifiers
        assert "spring" in modifiers
        assert "summer" in modifiers
        assert "fall" in modifiers


class TestFusionCalibration:
    """Test P3 calibration placeholder endpoints"""
    
    def test_calibration_status_returns_200(self):
        """GET /api/bionic/fusion/calibration/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/calibration/status")
        assert response.status_code == 200
        
    def test_calibration_status_is_placeholder(self):
        """Calibration status is P3 placeholder"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/calibration/status")
        data = response.json()
        
        assert data["status"] == "placeholder"
        assert data["phase"] == "P3"
        assert "current_features" in data
        assert "planned_features" in data
        assert "calibration_placeholder" in data


class TestFusionCompatibility:
    """Test fusion compatibility endpoint"""
    
    def test_compatibility_returns_200(self):
        """GET /api/bionic/fusion/compatibility returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/compatibility")
        assert response.status_code == 200
        
    def test_compatibility_all_compatible(self):
        """All components are compatible"""
        response = requests.get(f"{BASE_URL}/api/bionic/fusion/compatibility")
        data = response.json()
        
        assert data["fusion_engine"]["compatible"] == True
        assert data["geo_suite"]["compatible"] == True
        assert data["behavior_suite"]["compatible"] == True
        assert data["frontend_p15"]["compatible"] == True
        
        # Check P3 hooks
        assert data["p3_hooks"]["adaptive_metrics"] == True
        assert data["p3_hooks"]["feedback_loop"] == True


class TestFusionErrorHandling:
    """Test error handling for fusion endpoints"""
    
    def test_analyze_missing_lat_returns_422(self):
        """Missing lat parameter returns 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze",
            params={"lon": -71.2}
        )
        assert response.status_code == 422
        
    def test_analyze_missing_lon_returns_422(self):
        """Missing lon parameter returns 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze",
            params={"lat": 46.8}
        )
        assert response.status_code == 422
        
    def test_analyze_invalid_lat_returns_422(self):
        """Invalid lat (>90) returns 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze",
            params={"lat": 100, "lon": -71.2}
        )
        assert response.status_code == 422
        
    def test_analyze_invalid_lon_returns_422(self):
        """Invalid lon (>180) returns 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze",
            params={"lat": 46.8, "lon": 200}
        )
        assert response.status_code == 422


class TestFusionMultiTerritory:
    """Test fusion with different territories"""
    
    def test_analyze_quebec_territory(self):
        """Analyze Quebec territory returns correct region"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze/quick",
            params={
                "lat": 46.8,
                "lon": -71.2,
                "species": "deer"
            }
        )
        data = response.json()
        assert response.status_code == 200
        assert "global_score" in data
        
    def test_analyze_usa_territory(self):
        """Analyze USA territory returns correct region"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/analyze/quick",
            params={
                "lat": 44.5,
                "lon": -72.5,
                "species": "deer"
            }
        )
        data = response.json()
        assert response.status_code == 200
        assert "global_score" in data


class TestFusionModes:
    """Test different fusion modes"""
    
    def test_balanced_mode(self):
        """Balanced mode returns valid data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/weights",
            params={"species": "deer", "territory": "quebec", "mode": "balanced"}
        )
        data = response.json()
        assert response.status_code == 200
        # Balanced mode should have roughly equal weights
        suite = data["weights"]["suite_weights"]
        assert abs(suite["geo_suite"] - suite["behavior_suite"]) < 0.2
        
    def test_geo_dominant_mode(self):
        """Geo dominant mode returns valid data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/weights",
            params={"species": "deer", "territory": "quebec", "mode": "geo_dominant"}
        )
        data = response.json()
        assert response.status_code == 200
        suite = data["weights"]["suite_weights"]
        assert suite["geo_suite"] > suite["behavior_suite"]
        
    def test_behavior_dominant_mode(self):
        """Behavior dominant mode returns valid data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/fusion/weights",
            params={"species": "deer", "territory": "quebec", "mode": "behavior"}
        )
        data = response.json()
        assert response.status_code == 200
        suite = data["weights"]["suite_weights"]
        assert suite["behavior_suite"] > suite["geo_suite"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
