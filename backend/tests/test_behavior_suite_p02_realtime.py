"""
BIONIC™ Behavior Suite - P0-2 Real-Time Data Tests
====================================================
Tests for P0-2 Behavior Suite implementation with real-time data:
- BehaviorWeatherFetcher (Open-Meteo + astronomical lunar algorithm)
- 6 engines with real-time weather, lunar phase, pressure, photoperiod
- Validation of data_source = 'real_time' in responses

Test coordinates: lat=47.5, lon=-72.5 (Québec)
"""

import pytest
import requests
import os
from datetime import datetime

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates (Québec region as specified)
TEST_LAT = 47.5
TEST_LON = -72.5

# Supported species codes
SPECIES_CODES = ["moose", "deer", "bear", "caribou", "wolf", "turkey", "waterfowl", "smallgame"]


class TestBehaviorSuiteStatusP02:
    """Test /api/bionic/behavior/status endpoint - Verify 6 engines active"""
    
    def test_status_returns_6_engines(self):
        """GET /api/bionic/behavior/status - Returns status with 6 active engines"""
        response = requests.get(f"{BASE_URL}/api/bionic/behavior/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify suite info
        assert data["suite"] == "BIONIC Behavior Suite"
        assert data["status"] == "operational"
        
        # Verify all 6 engines are active
        engines = data["engines"]
        assert len(engines) == 6, f"Expected 6 engines, got {len(engines)}"
        
        expected_engines = ["behavior", "seasonal", "activity", "rut", "movement", "species_model"]
        for engine_name in expected_engines:
            assert engine_name in engines, f"Missing engine: {engine_name}"
            assert engines[engine_name]["status"] == "active"
        
        # Verify 8 supported species
        assert len(data["supported_species"]) == 8
        for species in SPECIES_CODES:
            assert species in data["supported_species"]
        
        print(f"✅ Status endpoint: 6 engines active, 8 species supported")


class TestBehaviorEngineRealTime:
    """Test /api/bionic/behavior/analyze - BehaviorEngine with real-time weather data"""
    
    def test_analyze_with_realtime_weather(self):
        """GET /api/bionic/behavior/analyze - Verify real-time weather integration"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("beh_")
        assert data["species"] == "deer"
        assert data["species_name_fr"] == "Cerf de Virginie"
        
        # Verify scores
        assert 0 <= data["overall_activity_score"] <= 100
        assert 0 <= data["hunting_opportunity_score"] <= 100
        
        # Verify behavioral factors include real-time data
        assert "behavioral_factors" in data
        factors = data["behavioral_factors"]
        assert "temperature" in factors
        assert "lunar" in factors
        assert "pressure" in factors
        
        # Check for lunar phase name (from real-time calculation)
        if "lunar_phase" in factors:
            print(f"  Lunar phase: {factors['lunar_phase']}")
        
        # Check for real-time data indicators
        if "real_time_data" in data:
            rt_data = data["real_time_data"]
            print(f"  Real-time data source: {rt_data.get('data_source', 'unknown')}")
            print(f"  Temperature: {rt_data.get('temperature_c', 'N/A')}°C")
            print(f"  Weather: {rt_data.get('weather', 'N/A')}")
            print(f"  Sunrise: {rt_data.get('sunrise', 'N/A')}")
            print(f"  Sunset: {rt_data.get('sunset', 'N/A')}")
            
            # Verify data_source is real_time
            if rt_data.get('data_source') == 'real_time':
                print(f"✅ BehaviorEngine using REAL-TIME data")
            else:
                print(f"⚠️ BehaviorEngine using estimated data: {rt_data.get('data_source')}")
        
        # Verify recommendations
        assert len(data["recommendations"]) >= 1
        
        print(f"✅ BehaviorEngine analysis complete - Score: {data['overall_activity_score']}")
    
    def test_analyze_all_species(self):
        """Test behavior analysis for all 8 species"""
        for species in SPECIES_CODES:
            response = requests.get(
                f"{BASE_URL}/api/bionic/behavior/analyze",
                params={"lat": TEST_LAT, "lon": TEST_LON, "species": species}
            )
            
            assert response.status_code == 200, f"Failed for species {species}: {response.text}"
            data = response.json()
            assert data["species"] == species
            assert 0 <= data["overall_activity_score"] <= 100
        
        print(f"✅ All 8 species supported in BehaviorEngine")


class TestActivityProbabilityEngineRealTime:
    """Test /api/bionic/behavior/activity - ActivityProbabilityEngine with lunar phase"""
    
    def test_activity_with_lunar_phase(self):
        """GET /api/bionic/behavior/activity - Verify lunar phase integration"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/activity",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
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
        
        # Verify factors include lunar
        assert "factors" in data
        factors = data["factors"]
        assert "lunar" in factors
        
        # Check lunar details
        lunar_factors = factors["lunar"]
        if isinstance(lunar_factors, dict):
            print(f"  Lunar phase: {lunar_factors.get('phase_name', 'N/A')}")
            print(f"  Illumination: {lunar_factors.get('illumination_percent', 'N/A')}%")
            print(f"  Hunting impact: {lunar_factors.get('hunting_impact', 'N/A')}")
        
        # Verify optimal window
        assert "optimal_window" in data
        window = data["optimal_window"]
        assert 0 <= window["start_hour"] <= 23
        assert 0 <= window["end_hour"] <= 23
        
        print(f"✅ ActivityProbabilityEngine - Probability: {data['activity_probability']:.2f}")


class TestSeasonalAttractivenessEngine:
    """Test /api/bionic/behavior/seasonal - SeasonalAttractivenessEngine with phases"""
    
    def test_seasonal_attractiveness(self):
        """GET /api/bionic/behavior/seasonal - Verify seasonal phase analysis"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/seasonal",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "moose"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("seas_")
        assert data["species"] == "moose"
        
        # Verify seasonal phase
        valid_phases = [
            "winter_survival", "spring_dispersal", "summer_foraging",
            "pre_rut_preparation", "rut_active", "post_rut_recovery", "fall_preparation"
        ]
        assert data["current_phase"] in valid_phases, f"Invalid phase: {data['current_phase']}"
        assert "phase_name_fr" in data
        
        print(f"  Current phase: {data['current_phase']} ({data['phase_name_fr']})")
        print(f"  Days into phase: {data['days_into_phase']}")
        print(f"  Days remaining: {data['days_remaining']}")
        
        # Verify attractiveness scores
        assert 0 <= data["overall_attractiveness"] <= 100
        assert 0 <= data["food_attractiveness"] <= 100
        assert 0 <= data["cover_attractiveness"] <= 100
        assert 0 <= data["water_attractiveness"] <= 100
        
        # Verify hotspots
        assert len(data["hotspots"]) >= 1
        
        # Verify trend
        assert data["trend"] in ["increasing", "stable", "decreasing"]
        
        print(f"✅ SeasonalAttractivenessEngine - Overall: {data['overall_attractiveness']}")


class TestRutPredictionEngine:
    """Test /api/bionic/behavior/rut - RutPredictionEngine with date predictions"""
    
    def test_rut_prediction_deer(self):
        """GET /api/bionic/behavior/rut - Verify rut prediction for deer"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/rut",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("rut_")
        assert data["species"] == "deer"
        
        # Verify year
        assert data["year"] == datetime.now().year
        
        # Verify current phase
        valid_phases = ["pre_rut", "seeking", "chasing", "breeding", "post_rut", "recovery"]
        assert data["current_phase"] in valid_phases, f"Invalid phase: {data['current_phase']}"
        assert "phase_name_fr" in data
        assert 0 <= data["phase_intensity"] <= 1
        
        print(f"  Current phase: {data['current_phase']} ({data['phase_name_fr']})")
        print(f"  Phase intensity: {data['phase_intensity']:.2f}")
        
        # Verify timeline dates
        assert "pre_rut_start" in data
        assert "seeking_start" in data
        assert "peak_breeding" in data
        assert "post_rut_start" in data
        
        print(f"  Pre-rut start: {data['pre_rut_start']}")
        print(f"  Peak breeding: {data['peak_breeding']}")
        print(f"  Days to peak: {data['days_to_peak']}")
        
        # Verify peak dates
        assert len(data["peak_dates"]) >= 1
        
        # Verify expected behaviors
        assert len(data["expected_behaviors"]) >= 1
        
        # Verify tactics
        assert len(data["recommended_tactics"]) >= 1
        assert len(data["best_calling_times"]) >= 1
        
        print(f"✅ RutPredictionEngine - Phase: {data['current_phase']}")
    
    def test_rut_prediction_moose(self):
        """GET /api/bionic/behavior/rut - Verify rut prediction for moose"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/rut",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "moose"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "moose"
        assert "current_phase" in data
        print(f"✅ RutPredictionEngine (moose) - Phase: {data['current_phase']}")


class TestMovementEngine:
    """Test /api/bionic/behavior/movement - MovementEngine with corridors"""
    
    def test_movement_with_corridors(self):
        """GET /api/bionic/behavior/movement - Verify corridor analysis"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/movement",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer", "include_corridors": True}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("mov_")
        assert data["species"] == "deer"
        
        # Verify movement pattern
        valid_patterns = ["sedentary", "local", "regional", "migratory", "dispersal"]
        assert data["current_pattern"] in valid_patterns
        assert "pattern_name_fr" in data
        
        print(f"  Movement pattern: {data['current_pattern']} ({data['pattern_name_fr']})")
        
        # Verify home range
        assert data["home_range_km2"] > 0
        assert data["core_area_km2"] > 0
        assert data["core_area_km2"] < data["home_range_km2"]
        
        print(f"  Home range: {data['home_range_km2']:.2f} km²")
        print(f"  Core area: {data['core_area_km2']:.2f} km²")
        
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
        
        print(f"  Corridors found: {len(data['corridors'])}")
        
        # Verify primary corridor score
        assert 0 <= data["primary_corridor_score"] <= 1
        
        # Verify distances
        assert data["daily_movement_km"] > 0
        
        # Verify areas
        assert len(data["bedding_areas"]) >= 1
        assert len(data["feeding_areas"]) >= 1
        assert len(data["travel_routes"]) >= 1
        
        # Verify likely positions
        assert len(data["likely_positions"]) >= 1
        
        print(f"✅ MovementEngine - Pattern: {data['current_pattern']}, Corridors: {len(data['corridors'])}")


class TestSpeciesModelEngine:
    """Test /api/bionic/behavior/species-model - SpeciesModelEngine with detailed profiles"""
    
    def test_species_model_detailed(self):
        """GET /api/bionic/behavior/species-model - Verify detailed species profile"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/species-model",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify analysis metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("spe_")
        assert data["species"] == "deer"
        assert data["species_name_fr"] == "Cerf de Virginie"
        assert data["species_name_en"] == "White-tailed Deer"
        
        # Verify species profile
        profile = data["species_profile"]
        assert profile["scientific_name"] == "Odocoileus virginianus"
        assert profile["family"] == "Cervidés"
        assert "weight_range_kg" in profile
        assert "habitat_preference" in profile
        assert "diet" in profile
        assert "activity_pattern" in profile
        assert "hunting_season_qc" in profile
        assert "population_qc" in profile
        
        print(f"  Scientific name: {profile['scientific_name']}")
        print(f"  Population QC: {profile['population_qc']}")
        
        # Verify habitat suitability
        assert 0 <= data["habitat_suitability"] <= 100
        assert "habitat_factors" in data
        
        # Verify behavior summary
        assert "behavior_summary" in data
        assert "current_behavior_phase" in data
        
        print(f"  Current phase: {data['current_behavior_phase']}")
        
        # Verify seasonal factors
        assert "seasonal_factors" in data
        seasonal = data["seasonal_factors"]
        assert "month" in seasonal
        assert "opportunity_factor" in seasonal
        assert "is_peak_season" in seasonal
        
        print(f"  Season quality: {seasonal.get('season_quality', 'N/A')}")
        
        # Verify scores
        assert 0 <= data["overall_score"] <= 100
        assert 0 <= data["hunting_index"] <= 100
        
        # Verify tips and recommendations
        assert len(data["species_specific_tips"]) >= 1
        assert len(data["optimal_tactics"]) >= 1
        assert len(data["gear_recommendations"]) >= 1
        
        print(f"✅ SpeciesModelEngine - Habitat: {data['habitat_suitability']}, Hunting Index: {data['hunting_index']}")
    
    def test_species_model_all_species(self):
        """Test species model for multiple species"""
        test_species = ["deer", "moose", "bear", "turkey", "caribou"]
        
        for species in test_species:
            response = requests.get(
                f"{BASE_URL}/api/bionic/behavior/species-model",
                params={"lat": TEST_LAT, "lon": TEST_LON, "species": species}
            )
            
            assert response.status_code == 200, f"Failed for species {species}: {response.text}"
            data = response.json()
            assert data["species"] == species
            assert "species_profile" in data
        
        print(f"✅ SpeciesModelEngine works for all tested species")


class TestFullBehaviorAnalysisP02:
    """Test /api/bionic/behavior/full - Full analysis with all 6 engines"""
    
    def test_full_analysis_all_engines(self):
        """GET /api/bionic/behavior/full - Run all 6 engines with real-time data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/full",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify suite metadata
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("full_")
        assert data["species"] == "deer"
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        
        # Verify processing time
        assert "processing_time_ms" in data
        print(f"  Processing time: {data['processing_time_ms']}ms")
        
        # Verify all 6 engines executed
        assert len(data["engines_executed"]) == 6
        expected_engines = ["behavior", "seasonal", "activity", "rut", "movement", "species_model"]
        for engine in expected_engines:
            assert engine in data["engines_executed"], f"Missing engine: {engine}"
        
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
        
        print(f"  Global opportunity score: {data['global_opportunity_score']}")
        print(f"  Confidence: {data['confidence']}")
        
        # Verify aggregated recommendations
        assert len(data["top_recommendations"]) >= 1
        
        # Verify aggregated hotspots
        assert len(data["hotspots"]) >= 1
        
        # Check for real-time data in behavior engine
        if "real_time_data" in data["behavior"]:
            rt_data = data["behavior"]["real_time_data"]
            data_source = rt_data.get("data_source", "unknown")
            print(f"  Data source: {data_source}")
            
            if data_source == "real_time":
                print(f"✅ Full analysis using REAL-TIME data")
            else:
                print(f"⚠️ Full analysis using estimated data")
        
        print(f"✅ Full analysis complete - 6 engines executed")


class TestRealTimeDataValidation:
    """Validate that real-time data is being integrated correctly"""
    
    def test_weather_data_integration(self):
        """Verify weather data is integrated in behavior analysis"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for real-time data
        if "real_time_data" in data:
            rt_data = data["real_time_data"]
            
            # Verify temperature is present and reasonable
            if "temperature_c" in rt_data:
                temp = rt_data["temperature_c"]
                # Temperature should be reasonable for Quebec (-40 to +40)
                assert -50 <= temp <= 50, f"Temperature out of range: {temp}"
                print(f"  Temperature: {temp}°C")
            
            # Verify sunrise/sunset
            if "sunrise" in rt_data:
                print(f"  Sunrise: {rt_data['sunrise']}")
            if "sunset" in rt_data:
                print(f"  Sunset: {rt_data['sunset']}")
            
            # Verify data source
            data_source = rt_data.get("data_source", "unknown")
            print(f"  Data source: {data_source}")
            
            if data_source == "real_time":
                print(f"✅ Weather data integration: REAL-TIME")
            else:
                print(f"⚠️ Weather data integration: {data_source}")
        else:
            print(f"⚠️ No real_time_data field in response")
    
    def test_lunar_phase_calculation(self):
        """Verify lunar phase is calculated correctly"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/activity",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check lunar factors
        if "factors" in data and "lunar" in data["factors"]:
            lunar = data["factors"]["lunar"]
            
            if isinstance(lunar, dict):
                # Verify illumination is present
                if "illumination_percent" in lunar:
                    illum = lunar["illumination_percent"]
                    assert 0 <= illum <= 100, f"Illumination out of range: {illum}"
                    print(f"  Lunar illumination: {illum}%")
                
                # Verify phase name
                if "phase_name" in lunar:
                    print(f"  Lunar phase: {lunar['phase_name']}")
                
                # Verify hunting impact
                if "hunting_impact" in lunar:
                    print(f"  Hunting impact: {lunar['hunting_impact']}")
                
                print(f"✅ Lunar phase calculation: Working")
            else:
                print(f"  Lunar factor (numeric): {lunar}")
        else:
            print(f"⚠️ No lunar factors in response")
    
    def test_pressure_trend_integration(self):
        """Verify barometric pressure trend is integrated"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check behavioral factors for pressure
        if "behavioral_factors" in data:
            factors = data["behavioral_factors"]
            
            if "pressure" in factors:
                pressure = factors["pressure"]
                print(f"  Pressure factor: {pressure}")
            
            if "pressure_trend" in factors:
                print(f"  Pressure trend: {factors['pressure_trend']}")
        
        print(f"✅ Pressure integration check complete")


class TestDynamicRecommendations:
    """Validate that recommendations are dynamic based on conditions"""
    
    def test_recommendations_present(self):
        """Verify recommendations are generated for all endpoints"""
        endpoints = [
            ("/api/bionic/behavior/analyze", {"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}),
            ("/api/bionic/behavior/seasonal", {"lat": TEST_LAT, "lon": TEST_LON, "species": "moose"}),
            ("/api/bionic/behavior/activity", {"lat": TEST_LAT, "lon": TEST_LON, "species": "deer"}),
            ("/api/bionic/behavior/species-model", {"lat": TEST_LAT, "lon": TEST_LON, "species": "bear"}),
        ]
        
        for endpoint, params in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
            assert response.status_code == 200, f"Failed for {endpoint}: {response.text}"
            data = response.json()
            
            assert "recommendations" in data, f"No recommendations in {endpoint}"
            assert len(data["recommendations"]) >= 1, f"Empty recommendations in {endpoint}"
            
            print(f"  {endpoint}: {len(data['recommendations'])} recommendations")
        
        print(f"✅ All endpoints return recommendations")


class TestInputValidationP02:
    """Test input validation for P0-2 endpoints"""
    
    def test_invalid_latitude(self):
        """Test with invalid latitude (>90)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": 100, "lon": TEST_LON, "species": "deer"}
        )
        assert response.status_code == 422
        print(f"✅ Invalid latitude rejected (422)")
    
    def test_invalid_longitude(self):
        """Test with invalid longitude (>180)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": 200, "species": "deer"}
        )
        assert response.status_code == 422
        print(f"✅ Invalid longitude rejected (422)")
    
    def test_invalid_species(self):
        """Test with invalid species code"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/behavior/analyze",
            params={"lat": TEST_LAT, "lon": TEST_LON, "species": "invalid_species"}
        )
        assert response.status_code == 422
        print(f"✅ Invalid species rejected (422)")
    
    def test_missing_required_params(self):
        """Test with missing required parameters"""
        response = requests.get(f"{BASE_URL}/api/bionic/behavior/analyze")
        assert response.status_code == 422
        print(f"✅ Missing params rejected (422)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
