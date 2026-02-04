"""
BIONIC™ Refactored API Tests - Phase 1 Validation
==================================================
Tests for the refactored bionic_engine.py (747 lines) with modular architecture.

Validates:
- GET /api/bionic/modules - 8 modules
- GET /api/bionic/species - 6 species
- POST /api/bionic/analyze - Complete analysis
- GET /api/bionic/stats - Global stats with BIONIC_CORE 2.0
- GET /api/bionic/geospatial/complete - Weather, terrain, vegetation
- GET /api/bionic/geospatial/weather - Real-time weather
- POST /api/bionic/modules/{module_id}/run - Individual module execution
- POST /api/bionic/species/{species_id}/score - Species habitat score
- GET /api/stats - Frontend stats (Stats Engine)
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fauna-analysis.preview.emergentagent.com').rstrip('/')

# Test coordinates (Quebec City area)
TEST_LAT = 46.8
TEST_LON = -71.2
TEST_TERRITORY_ID = "test_refactored_001"


class TestBionicModulesEndpoint:
    """Tests for GET /api/bionic/modules - Should return 8 modules"""
    
    def test_modules_returns_200(self):
        """Verify modules endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_modules_returns_8_modules(self):
        """Verify exactly 8 modules are returned"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        data = response.json()
        
        assert data["success"] is True
        assert data["total"] == 8, f"Expected 8 modules, got {data['total']}"
        assert len(data["modules"]) == 8
    
    def test_modules_have_correct_ids(self):
        """Verify all 8 module IDs are present"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        data = response.json()
        
        expected_ids = ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"]
        actual_ids = [m["id"] for m in data["modules"]]
        
        for expected_id in expected_ids:
            assert expected_id in actual_ids, f"Missing module: {expected_id}"
    
    def test_modules_have_required_fields(self):
        """Verify each module has required fields"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        data = response.json()
        
        required_fields = ["id", "name", "version", "description", "factors"]
        
        for module in data["modules"]:
            for field in required_fields:
                assert field in module, f"Module {module.get('id', 'unknown')} missing field: {field}"


class TestBionicSpeciesEndpoint:
    """Tests for GET /api/bionic/species - Should return 6 species"""
    
    def test_species_returns_200(self):
        """Verify species endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        assert response.status_code == 200
    
    def test_species_returns_6_species(self):
        """Verify exactly 6 species are returned"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        data = response.json()
        
        assert data["success"] is True
        assert data["total"] == 6, f"Expected 6 species, got {data['total']}"
        assert len(data["species"]) == 6
    
    def test_species_have_correct_ids(self):
        """Verify all 6 species IDs are present"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        data = response.json()
        
        expected_ids = ["moose", "deer", "bear", "caribou", "wolf", "turkey"]
        actual_ids = [s["id"] for s in data["species"]]
        
        for expected_id in expected_ids:
            assert expected_id in actual_ids, f"Missing species: {expected_id}"
    
    def test_species_have_module_weights(self):
        """Verify each species has module_weights"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        data = response.json()
        
        for species in data["species"]:
            assert "module_weights" in species, f"Species {species['id']} missing module_weights"
            assert isinstance(species["module_weights"], dict)
            assert len(species["module_weights"]) > 0


class TestBionicAnalyzeEndpoint:
    """Tests for POST /api/bionic/analyze - Complete territory analysis"""
    
    def test_analyze_returns_200(self):
        """Verify analyze endpoint returns 200"""
        payload = {
            "territory_id": TEST_TERRITORY_ID,
            "latitude": TEST_LAT,
            "longitude": TEST_LON,
            "radius_km": 5.0,
            "modules": ["thermal", "wetness", "food"],
            "species": ["moose", "deer"],
            "include_ai_predictions": True,
            "include_temporal": True
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_analyze_returns_all_modules(self):
        """Verify analysis includes all requested modules"""
        payload = {
            "territory_id": TEST_TERRITORY_ID,
            "latitude": TEST_LAT,
            "longitude": TEST_LON,
            "modules": ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"],
            "species": ["moose", "deer", "bear"]
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        assert data["success"] is True
        analysis = data["analysis"]
        
        # Verify all 8 modules are in response
        assert len(analysis["modules"]) == 8, f"Expected 8 modules, got {len(analysis['modules'])}"
        
        for module_id in ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"]:
            assert module_id in analysis["modules"], f"Missing module: {module_id}"
    
    def test_analyze_returns_species_scores(self):
        """Verify analysis includes species scores"""
        payload = {
            "territory_id": TEST_TERRITORY_ID,
            "latitude": TEST_LAT,
            "longitude": TEST_LON,
            "species": ["moose", "deer", "bear"]
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data["analysis"]
        assert "species" in analysis
        assert len(analysis["species"]) == 3
        
        for species_id in ["moose", "deer", "bear"]:
            assert species_id in analysis["species"], f"Missing species: {species_id}"
            species_data = analysis["species"][species_id]
            assert "score" in species_data
            assert "rating" in species_data
            assert "hotspots" in species_data
    
    def test_analyze_returns_predictions(self):
        """Verify analysis includes AI predictions"""
        payload = {
            "territory_id": TEST_TERRITORY_ID,
            "latitude": TEST_LAT,
            "longitude": TEST_LON,
            "include_ai_predictions": True
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data["analysis"]
        assert "predictions" in analysis
        assert analysis["predictions"] is not None
        assert "forecast_24h" in analysis["predictions"]
        assert "weather_impact" in analysis["predictions"]
    
    def test_analyze_returns_temporal(self):
        """Verify analysis includes temporal data"""
        payload = {
            "territory_id": TEST_TERRITORY_ID,
            "latitude": TEST_LAT,
            "longitude": TEST_LON,
            "include_temporal": True
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data["analysis"]
        assert "temporal" in analysis
        assert analysis["temporal"] is not None
        assert "ndvi_trend" in analysis["temporal"]
    
    def test_analyze_returns_engine_version_2(self):
        """Verify engine version is BIONIC_CORE 2.0"""
        payload = {
            "territory_id": TEST_TERRITORY_ID,
            "latitude": TEST_LAT,
            "longitude": TEST_LON
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data["analysis"]
        assert "engine_version" in analysis
        assert analysis["engine_version"] == "BIONIC_CORE 2.0", f"Expected BIONIC_CORE 2.0, got {analysis['engine_version']}"


class TestBionicStatsEndpoint:
    """Tests for GET /api/bionic/stats - Global statistics"""
    
    def test_stats_returns_200(self):
        """Verify stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        assert response.status_code == 200
    
    def test_stats_has_required_fields(self):
        """Verify stats has all required fields"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        required_fields = [
            "total_analyses", "total_species_models", "total_zones_generated",
            "total_waypoints", "total_favorites", "average_global_score",
            "top_species_frequency", "modules_usage", "rating_distribution",
            "engine_version", "last_update"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_stats_engine_version_is_2(self):
        """Verify engine version is BIONIC_CORE 2.0"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        assert data["engine_version"] == "BIONIC_CORE 2.0", f"Expected BIONIC_CORE 2.0, got {data['engine_version']}"
    
    def test_stats_values_are_valid(self):
        """Verify stats values are reasonable"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        assert data["total_analyses"] >= 0
        assert data["total_species_models"] >= 0
        assert 0 <= data["average_global_score"] <= 100


class TestBionicGeospatialEndpoints:
    """Tests for geospatial data endpoints"""
    
    def test_geospatial_complete_returns_200(self):
        """Verify complete geospatial endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        assert response.status_code == 200
    
    def test_geospatial_complete_has_weather(self):
        """Verify complete geospatial includes weather data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        assert data["success"] is True
        assert "weather" in data
        assert "temperature" in data["weather"]
        assert "humidity" in data["weather"]
    
    def test_geospatial_complete_has_terrain(self):
        """Verify complete geospatial includes terrain data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        assert "terrain" in data
        assert "elevation_m" in data["terrain"]
    
    def test_geospatial_complete_has_vegetation(self):
        """Verify complete geospatial includes vegetation data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/complete",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        assert "vegetation" in data
        assert "ndvi" in data["vegetation"]
    
    def test_geospatial_weather_returns_200(self):
        """Verify weather endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/weather",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        assert response.status_code == 200
    
    def test_geospatial_weather_has_forecast(self):
        """Verify weather includes forecasts"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/geospatial/weather",
            params={"latitude": TEST_LAT, "longitude": TEST_LON}
        )
        data = response.json()
        
        assert data["success"] is True
        assert "current" in data
        assert "forecast_24h" in data
        assert "forecast_72h" in data
        assert "forecast_7d" in data


class TestBionicModuleRunEndpoint:
    """Tests for POST /api/bionic/modules/{module_id}/run"""
    
    def test_module_run_thermal_returns_200(self):
        """Verify running thermal module returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/modules/thermal/run",
            params={
                "territory_id": TEST_TERRITORY_ID,
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            }
        )
        assert response.status_code == 200
    
    def test_module_run_returns_score(self):
        """Verify module run returns score and rating"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/modules/food/run",
            params={
                "territory_id": TEST_TERRITORY_ID,
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            }
        )
        data = response.json()
        
        assert data["success"] is True
        result = data["result"]
        assert "score" in result
        assert "rating" in result
        assert "factors" in result
        assert "recommendations" in result
        assert 0 <= result["score"] <= 100
    
    def test_module_run_invalid_module_returns_404(self):
        """Verify invalid module returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/modules/invalid_module/run",
            params={
                "territory_id": TEST_TERRITORY_ID,
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            }
        )
        assert response.status_code == 404


class TestBionicSpeciesScoreEndpoint:
    """Tests for POST /api/bionic/species/{species_id}/score"""
    
    def test_species_score_moose_returns_200(self):
        """Verify moose score endpoint returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/species/moose/score",
            params={
                "territory_id": TEST_TERRITORY_ID,
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            }
        )
        assert response.status_code == 200
    
    def test_species_score_returns_habitat_metrics(self):
        """Verify species score returns habitat metrics"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/species/deer/score",
            params={
                "territory_id": TEST_TERRITORY_ID,
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            }
        )
        data = response.json()
        
        assert data["success"] is True
        result = data["result"]
        
        required_fields = [
            "species", "common_name", "score", "rating",
            "habitat_suitability", "food_availability", "cover_quality",
            "water_access", "disturbance_level", "season_factor", "hotspots"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_species_score_invalid_species_returns_404(self):
        """Verify invalid species returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/species/invalid_species/score",
            params={
                "territory_id": TEST_TERRITORY_ID,
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            }
        )
        assert response.status_code == 404


class TestFrontendStatsEndpoint:
    """Tests for GET /api/stats - Frontend Stats Engine"""
    
    def test_stats_returns_200(self):
        """Verify frontend stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
    
    def test_stats_has_required_fields(self):
        """Verify frontend stats has all required fields"""
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        
        required_fields = [
            "subscribers", "zones", "territories", "activeUsers",
            "attractants", "satisfaction", "lastUpdated"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_stats_values_are_thresholds(self):
        """Verify stats values meet minimum thresholds"""
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        
        # These are the minimum threshold values
        assert data["subscribers"] >= 20017
        assert data["zones"] >= 2901
        assert data["territories"] >= 2547
        assert data["activeUsers"] >= 1247
        assert data["attractants"] >= 850
        assert data["satisfaction"] >= 98


class TestAPICompatibility:
    """Tests to verify 100% API compatibility after refactoring"""
    
    def test_all_endpoints_accessible(self):
        """Verify all main endpoints are accessible"""
        endpoints = [
            ("GET", "/api/bionic/modules"),
            ("GET", "/api/bionic/species"),
            ("GET", "/api/bionic/stats"),
            ("GET", "/api/stats"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Endpoint {endpoint} failed with {response.status_code}"
    
    def test_analyze_backward_compatible(self):
        """Verify analyze endpoint maintains backward compatibility"""
        # Minimal payload (should use defaults)
        payload = {
            "territory_id": "compat_test",
            "latitude": TEST_LAT,
            "longitude": TEST_LON
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure is maintained
        assert "success" in data
        assert "analysis" in data
        analysis = data["analysis"]
        
        # Core fields that must exist
        assert "territory_id" in analysis
        assert "location" in analysis
        assert "modules" in analysis
        assert "species" in analysis
        assert "overall_score" in analysis
        assert "overall_rating" in analysis


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
