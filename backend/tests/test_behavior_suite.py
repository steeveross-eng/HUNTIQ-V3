"""
BIONIC™ Behavior Suite - Backend API Tests
============================================
Tests for P0-1 Behavior Suite implementation:
- 6 engines: BehaviorEngine, SeasonalAttractivenessEngine, ActivityProbabilityEngine,
             RutPredictionEngine, MovementEngine, SpeciesModelEngine
- 8 API endpoints
- Support for 8 Quebec species

All engines use heuristic/stub logic (no real ML) - testing structure and endpoints.
"""

import pytest
import requests
import os
from datetime import datetime

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Supported species codes
SPECIES_CODES = ["moose", "deer", "bear", "caribou", "wolf", "turkey", "waterfowl", "smallgame"]

# Test coordinates (Quebec region)
TEST_LAT = 46.8
TEST_LON = -71.2
TEST_LAT_NORTH = 47.0  # For rut prediction at 47°N


class TestBehaviorSuiteStatus:
    """Test /api/bionic/behavior/status endpoint"""
    
    def test_status_returns_operational(self):
        """GET /api/bionic/behavior/status - Returns operational status with 6 engines"""
        response = requests.get(f"{BASE_URL}/api/bionic/behavior/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify suite info
        assert data["suite"] == "BIONIC Behavior Suite"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
        assert data["phase"] == "P0-1 (Fondations)"
        
        # Verify all 6 engines are active
        engines = data["engines"]
        assert len(engines) == 6
        
        expected_engines = ["behavior", "seasonal", "activity", "rut", "movement", "species_model"]
        for engine_name in expected_engines:
            assert engine_name in engines
            assert engines[engine_name]["status"] == "active"
            assert engines[engine_name]["version"] == "1.0.0"
        
        # Verify 8 supported species
        assert len(data["supported_species"]) == 8
        for species in SPECIES_CODES:
            assert species in data["supported_species"]
        
        # Verify timestamp
        assert "timestamp" in data


class TestBehaviorEngine:
    """Test /api/bionic/behavior/analyze endpoint - Behavior analysis for deer"""
    
    def test_analyze_deer_behavior(self):
        """GET /api/bionic/behavior/analyze - Analyze deer behavior"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("beh_")
        assert data["species"] == "deer"
        assert data["species_name_fr"] == "Cerf de Virginie"
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        
        # Verify scores
        assert 0 <= data["overall_activity_score"] <= 100
        assert 0 <= data["hunting_opportunity_score"] <= 100
        assert 0 <= data["confidence"] <= 1
        
        # Verify activity windows
        assert len(data["peak_activity_windows"]) >= 1
        for window in data["peak_activity_windows"]:
            assert 0 <= window["start_hour"] <= 23
            assert 0 <= window["end_hour"] <= 23
            assert 0 <= window["probability"] <= 1
            assert window["activity_level"] in ["very_low", "low", "moderate", "high", "very_high", "peak"]
        
        # Verify current activity level
        assert data["current_activity_level"] in ["very_low", "low", "moderate", "high", "very_high", "peak"]
        
        # Verify behavioral factors
        assert "behavioral_factors" in data
        factors = data["behavioral_factors"]
        assert "temperature" in factors
        assert "precipitation" in factors
        assert "wind" in factors
        assert "lunar" in factors
        assert "pressure" in factors
        
        # Verify predictions
        assert "predictions_24h" in data
        if data["predictions_24h"]:
            assert "hourly_scores" in data["predictions_24h"]
            assert "best_hours" in data["predictions_24h"]
        
        # Verify recommendations
        assert len(data["recommendations"]) >= 1
    
    def test_analyze_with_weather_params(self):
        """GET /api/bionic/behavior/analyze - With weather parameters"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={
                "lat": TEST_LAT, 
                "lon": TEST_LON, 
                "species": "deer",
                "temperature_c": 10.0,
                "precipitation_mm": 0.0,
                "wind_speed_kmh": 15.0,
                "moon_phase": 0.5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "deer"
        assert 0 <= data["overall_activity_score"] <= 100


class TestSeasonalAttractivenessEngine:
    """Test /api/bionic/behavior/seasonal endpoint - Seasonal attractiveness for moose"""
    
    def test_seasonal_moose_analysis(self):
        """GET /api/bionic/behavior/seasonal - Analyze moose seasonal attractiveness"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/seasonal",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "moose"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("seas_")
        assert data["species"] == "moose"
        
        # Verify seasonal phase
        assert data["current_phase"] in [
            "winter_survival", "spring_dispersal", "summer_foraging",
            "pre_rut_preparation", "rut_active", "post_rut_recovery", "fall_preparation"
        ]
        assert "phase_name_fr" in data
        assert data["days_into_phase"] >= 0
        assert data["days_remaining"] >= 0
        
        # Verify attractiveness scores
        assert 0 <= data["overall_attractiveness"] <= 100
        assert 0 <= data["food_attractiveness"] <= 100
        assert 0 <= data["cover_attractiveness"] <= 100
        assert 0 <= data["water_attractiveness"] <= 100
        assert 0 <= data["thermal_attractiveness"] <= 100
        
        # Verify hotspots
        assert len(data["hotspots"]) >= 1
        for hotspot in data["hotspots"]:
            assert "latitude" in hotspot
            assert "longitude" in hotspot
            assert 0 <= hotspot["score"] <= 100
            assert 0 <= hotspot["confidence"] <= 1
            assert "reason" in hotspot
        
        # Verify trend
        assert data["trend"] in ["increasing", "stable", "decreasing"]
        assert "trend_description" in data
        
        # Verify best hunting days
        assert len(data["best_hunting_days"]) >= 1
        
        # Verify recommendations
        assert len(data["recommendations"]) >= 1


class TestActivityProbabilityEngine:
    """Test /api/bionic/behavior/activity endpoint - Activity probability"""
    
    def test_activity_probability(self):
        """GET /api/bionic/behavior/activity - Calculate activity probability"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/activity",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("act_")
        assert data["species"] == "deer"
        
        # Verify probability
        assert 0 <= data["activity_probability"] <= 1
        assert data["activity_level"] in ["very_low", "low", "moderate", "high", "very_high", "peak"]
        
        # Verify hourly probabilities
        assert len(data["hourly_probabilities"]) == 24
        for hour, prob in data["hourly_probabilities"].items():
            assert 0 <= prob <= 1
        
        # Verify factors
        assert "factors" in data
        factors = data["factors"]
        assert "weather" in factors
        assert "lunar" in factors
        assert "seasonal" in factors
        
        # Verify optimal window
        assert "optimal_window" in data
        window = data["optimal_window"]
        assert 0 <= window["start_hour"] <= 23
        assert 0 <= window["end_hour"] <= 23
        assert 0 <= window["probability"] <= 1
        
        # Verify confidence and recommendations
        assert 0 <= data["confidence"] <= 1
        assert len(data["recommendations"]) >= 1


class TestRutPredictionEngine:
    """Test /api/bionic/behavior/rut endpoint - Rut prediction for deer at 47°N"""
    
    def test_rut_prediction_deer_47n(self):
        """GET /api/bionic/behavior/rut - Predict rut for deer at 47°N latitude"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/rut",
            params={"lat": TEST_LAT_NORTH, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("rut_")
        assert data["species"] == "deer"
        assert data["location"]["lat"] == TEST_LAT_NORTH
        
        # Verify year
        assert data["year"] == datetime.now().year
        
        # Verify current phase
        assert data["current_phase"] in ["pre_rut", "seeking", "chasing", "breeding", "post_rut", "recovery"]
        assert "phase_name_fr" in data
        assert 0 <= data["phase_intensity"] <= 1
        
        # Verify timeline dates
        assert "pre_rut_start" in data
        assert "seeking_start" in data
        assert "peak_breeding" in data
        assert "post_rut_start" in data
        
        # Verify days to peak
        assert "days_to_peak" in data
        assert len(data["peak_dates"]) >= 1
        
        # Verify expected behaviors
        assert len(data["expected_behaviors"]) >= 1
        
        # Verify activity levels
        assert data["buck_activity_level"] in ["very_low", "low", "moderate", "high", "very_high", "peak"]
        assert data["doe_activity_level"] in ["very_low", "low", "moderate", "high", "very_high", "peak"]
        
        # Verify tactics and calling times
        assert len(data["recommended_tactics"]) >= 1
        assert len(data["best_calling_times"]) >= 1
        
        # Verify confidence
        assert 0 <= data["confidence"] <= 1
    
    def test_rut_prediction_moose(self):
        """GET /api/bionic/behavior/rut - Predict rut for moose"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/rut",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "moose"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "moose"
        assert "current_phase" in data


class TestMovementEngine:
    """Test /api/bionic/behavior/movement endpoint - Movement and corridors analysis"""
    
    def test_movement_analysis(self):
        """GET /api/bionic/behavior/movement - Analyze movement patterns and corridors"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/movement",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("mov_")
        assert data["species"] == "deer"
        
        # Verify movement pattern
        assert data["current_pattern"] in ["sedentary", "local", "regional", "migratory", "dispersal"]
        assert "pattern_name_fr" in data
        
        # Verify home range
        assert data["home_range_km2"] > 0
        assert data["core_area_km2"] > 0
        assert data["core_area_km2"] < data["home_range_km2"]
        
        # Verify corridors
        assert len(data["corridors"]) >= 1
        for corridor in data["corridors"]:
            assert "start_lat" in corridor
            assert "start_lon" in corridor
            assert "end_lat" in corridor
            assert "end_lon" in corridor
            assert corridor["width_m"] > 0
            assert 0 <= corridor["usage_probability"] <= 1
            assert "terrain_type" in corridor
        
        # Verify primary corridor score
        assert 0 <= data["primary_corridor_score"] <= 1
        
        # Verify distances
        assert data["daily_movement_km"] > 0
        assert data["seasonal_range_km"] > 0
        
        # Verify areas
        assert len(data["bedding_areas"]) >= 1
        assert len(data["feeding_areas"]) >= 1
        assert len(data["travel_routes"]) >= 1
        
        # Verify likely positions
        assert len(data["likely_positions"]) >= 1
        for pos in data["likely_positions"]:
            assert "latitude" in pos
            assert "longitude" in pos
            assert 0 <= pos["score"] <= 100
            assert 0 <= pos["confidence"] <= 1
        
        # Verify confidence
        assert 0 <= data["confidence"] <= 1


class TestSpeciesModelEngine:
    """Test /api/bionic/behavior/species-model endpoint - Species model for bear"""
    
    def test_species_model_bear(self):
        """GET /api/bionic/behavior/species-model - Get bear species model"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/species-model",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "bear"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("spe_")
        assert data["species"] == "bear"
        assert data["species_name_fr"] == "Ours noir"
        assert data["species_name_en"] == "Black Bear"
        
        # Verify species profile
        profile = data["species_profile"]
        assert profile["scientific_name"] == "Ursus americanus"
        assert profile["family"] == "Ursidés"
        assert "weight_range_kg" in profile
        assert "habitat_preference" in profile
        assert "diet" in profile
        assert "activity_pattern" in profile
        assert "hunting_season_qc" in profile
        assert "population_qc" in profile
        
        # Verify habitat suitability
        assert 0 <= data["habitat_suitability"] <= 100
        assert "habitat_factors" in data
        factors = data["habitat_factors"]
        assert "vegetation" in factors
        assert "water" in factors
        assert "cover" in factors
        assert "elevation" in factors
        
        # Verify behavior summary
        assert "behavior_summary" in data
        assert "current_behavior_phase" in data
        
        # Verify seasonal factors
        assert "seasonal_factors" in data
        seasonal = data["seasonal_factors"]
        assert "month" in seasonal
        assert "opportunity_factor" in seasonal
        assert "is_peak_season" in seasonal
        assert "season_quality" in seasonal
        
        # Verify scores
        assert 0 <= data["overall_score"] <= 100
        assert 0 <= data["hunting_index"] <= 100
        
        # Verify tips and recommendations
        assert len(data["species_specific_tips"]) >= 1
        assert len(data["optimal_tactics"]) >= 1
        assert len(data["gear_recommendations"]) >= 1
        
        # Verify confidence
        assert 0 <= data["confidence"] <= 1


class TestFullBehaviorAnalysis:
    """Test /api/bionic/behavior/full endpoint - Full analysis with 6 engines in parallel"""
    
    def test_full_analysis_all_engines(self):
        """GET /api/bionic/behavior/full - Run all 6 engines in parallel"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/full",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify suite metadata
        assert data["suite_version"] == "1.0.0"
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("full_")
        assert data["species"] == "deer"
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        
        # Verify processing time
        assert "processing_time_ms" in data
        
        # Verify all 6 engines executed
        assert len(data["engines_executed"]) == 6
        expected_engines = ["behavior", "seasonal", "activity", "rut", "movement", "species_model"]
        for engine in expected_engines:
            assert engine in data["engines_executed"]
        
        # Verify each engine result is present
        assert data["behavior"] is not None
        assert data["behavior"]["analysis_id"].startswith("beh_")
        
        assert data["seasonal"] is not None
        assert data["seasonal"]["analysis_id"].startswith("seas_")
        
        assert data["activity"] is not None
        assert data["activity"]["analysis_id"].startswith("act_")
        
        assert data["rut"] is not None
        assert data["rut"]["analysis_id"].startswith("rut_")
        
        assert data["movement"] is not None
        assert data["movement"]["analysis_id"].startswith("mov_")
        
        assert data["species_model"] is not None
        assert data["species_model"]["analysis_id"].startswith("spe_")
        
        # Verify global scores
        assert 0 <= data["global_opportunity_score"] <= 100
        assert 0 <= data["confidence"] <= 1
        
        # Verify aggregated recommendations
        assert len(data["top_recommendations"]) >= 1
        
        # Verify aggregated hotspots
        assert len(data["hotspots"]) >= 1
    
    def test_full_analysis_selective_engines(self):
        """GET /api/bionic/behavior/full - Run with selective engines"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/full",
            params={
                "lat": TEST_LAT, 
                "lon": TEST_LON, 
                "species": "deer",
                "include_behavior": True,
                "include_seasonal": True,
                "include_activity": False,
                "include_rut": False,
                "include_movement": False,
                "include_species_model": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify only selected engines executed
        assert "behavior" in data["engines_executed"]
        assert "seasonal" in data["engines_executed"]
        assert len(data["engines_executed"]) == 2
        
        # Verify results
        assert data["behavior"] is not None
        assert data["seasonal"] is not None
        assert data["activity"] is None
        assert data["rut"] is None
        assert data["movement"] is None
        assert data["species_model"] is None


class TestAllSpeciesSupport:
    """Test that all 8 Quebec species are supported"""
    
    @pytest.mark.parametrize("species", SPECIES_CODES)
    def test_status_endpoint_species(self, species):
        """Verify species is in supported list"""
        response = requests.get(f"{BASE_URL}/api/bionic/behavior/status")
        assert response.status_code == 200
        data = response.json()
        assert species in data["supported_species"]
    
    @pytest.mark.parametrize("species", ["deer", "moose", "bear", "turkey"])
    def test_behavior_analyze_species(self, species):
        """Test behavior analysis for different species"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": species}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == species


class TestInputValidation:
    """Test input validation for endpoints"""
    
    def test_invalid_latitude(self):
        """Test with invalid latitude (>90)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": 100, "lon": TEST_LON, "species": "deer"}
        )
        assert response.status_code == 422
    
    def test_invalid_longitude(self):
        """Test with invalid longitude (>180)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": 200, "species": "deer"}
        )
        assert response.status_code == 422
    
    def test_missing_required_params(self):
        """Test with missing required parameters"""
        response = requests.get(f"{BASE_URL}/api/bionic/behavior/analyze")
        assert response.status_code == 422
    
    def test_invalid_species(self):
        """Test with invalid species code"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "invalid_species"}
        )
        assert response.status_code == 422


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_extreme_north_quebec(self):
        """Test with extreme northern Quebec coordinates"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": 55.0, "lon": -77.0, "species": "caribou"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "caribou"
    
    def test_extreme_south_quebec(self):
        """Test with southern Quebec coordinates"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": 45.0, "lon": -73.5, "species": "deer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "deer"
    
    def test_moon_phase_boundaries(self):
        """Test moon phase at boundaries (0 and 1)"""
        # New moon
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/activity",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer", "moon_phase": 0}
        )
        assert response.status_code == 200
        
        # Full moon
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/activity",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer", "moon_phase": 1}
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
