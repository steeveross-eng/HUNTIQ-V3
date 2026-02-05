"""
BIONIC™ Coherence Optimization API Tests
=========================================
Tests for the coherence optimization module endpoints.

Endpoints tested:
- GET /api/bionic/optimization/status
- GET /api/bionic/optimization/evaluate
- GET /api/bionic/optimization/species-profile/{species}
- GET /api/bionic/optimization/quebec/enhanced-data
- GET /api/bionic/optimization/quebec/location-factors
- GET /api/bionic/optimization/p1-hooks
- GET /api/bionic/optimization/compare
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates for Quebec regions
TEST_LOCATIONS = {
    "laurentides": {"lat": 46.5, "lon": -74.5},
    "saguenay": {"lat": 48.5, "lon": -71.0},
    "outaouais": {"lat": 46.0, "lon": -76.5},
    "abitibi": {"lat": 48.5, "lon": -78.0},
    "gaspesie": {"lat": 48.8, "lon": -66.0}
}

# Species to test
TEST_SPECIES = ["deer", "moose", "bear"]


class TestOptimizationStatus:
    """Tests for /api/bionic/optimization/status endpoint"""
    
    def test_status_returns_200(self):
        """Status endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/status")
        assert response.status_code == 200
        
    def test_status_contains_required_fields(self):
        """Status response contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/status")
        data = response.json()
        
        assert "module" in data
        assert "version" in data
        assert "status" in data
        assert "current_coherence" in data
        assert "target_coherence" in data
        assert "optimization_axes" in data
        assert "species_profiles" in data
        assert "quebec_zones" in data
        assert "p1_hooks_ready" in data
        assert "timestamp" in data
        
    def test_status_module_operational(self):
        """Module status is operational"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/status")
        data = response.json()
        
        assert data["status"] == "operational"
        assert data["module"] == "BIONIC™ Coherence Optimization"
        assert data["version"] == "1.0.0"
        
    def test_status_has_3_species_profiles(self):
        """Status shows 3 species profiles (deer, moose, bear)"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/status")
        data = response.json()
        
        assert len(data["species_profiles"]) == 3
        assert "deer" in data["species_profiles"]
        assert "moose" in data["species_profiles"]
        assert "bear" in data["species_profiles"]
        
    def test_status_has_4_optimization_axes(self):
        """Status shows 4 optimization axes"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/status")
        data = response.json()
        
        assert len(data["optimization_axes"]) == 4
        assert "Inter-engine weighting refinement" in data["optimization_axes"]
        assert "Quebec enhanced data (UGAF, ZEC, reserves)" in data["optimization_axes"]
        assert "Species-specific calibration profiles" in data["optimization_axes"]
        assert "Geospatial pre-fusion hooks (P1)" in data["optimization_axes"]


class TestSpeciesProfiles:
    """Tests for /api/bionic/optimization/species-profile/{species} endpoint"""
    
    @pytest.mark.parametrize("species", TEST_SPECIES)
    def test_species_profile_returns_200(self, species):
        """Species profile endpoint returns 200 for valid species"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/species-profile/{species}")
        assert response.status_code == 200
        
    @pytest.mark.parametrize("species", TEST_SPECIES)
    def test_species_profile_contains_required_fields(self, species):
        """Species profile contains all calibration parameters"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/species-profile/{species}")
        data = response.json()
        
        assert data["species"] == species
        assert "profile" in data
        
        profile = data["profile"]
        assert "activity_threshold_low" in profile
        assert "activity_threshold_high" in profile
        assert "movement_threshold_low" in profile
        assert "movement_threshold_high" in profile
        assert "activity_movement_correlation" in profile
        assert "rut_activity_boost" in profile
        assert "habitat_tolerance" in profile
        assert "winter_movement_pattern" in profile
        assert "summer_movement_pattern" in profile
        assert "rut_movement_pattern" in profile
        
    def test_deer_profile_values(self):
        """Deer profile has correct calibration values"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/species-profile/deer")
        data = response.json()
        profile = data["profile"]
        
        assert profile["activity_threshold_low"] == 0.2
        assert profile["activity_threshold_high"] == 0.7
        assert profile["movement_threshold_low"] == 0.3
        assert profile["movement_threshold_high"] == 2.5
        assert profile["rut_activity_boost"] == 1.45
        assert profile["winter_movement_pattern"] == "local"
        
    def test_moose_profile_values(self):
        """Moose profile has correct calibration values"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/species-profile/moose")
        data = response.json()
        profile = data["profile"]
        
        assert profile["activity_threshold_low"] == 0.15
        assert profile["activity_threshold_high"] == 0.65
        assert profile["movement_threshold_high"] == 5.0
        assert profile["rut_activity_boost"] == 1.65  # More intense than deer
        assert profile["winter_movement_pattern"] == "sedentary"
        
    def test_bear_profile_values(self):
        """Bear profile has correct calibration values (no rut)"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/species-profile/bear")
        data = response.json()
        profile = data["profile"]
        
        assert profile["activity_threshold_low"] == 0.1  # Hibernation
        assert profile["activity_threshold_high"] == 0.8  # Hyperphagia
        assert profile["movement_threshold_low"] == 0.0  # Hibernation
        assert profile["movement_threshold_high"] == 15.0  # Large territory
        assert profile["rut_activity_boost"] == 1.0  # No rut
        assert profile["winter_movement_pattern"] == "sedentary"  # Hibernation
        
    def test_invalid_species_returns_404(self):
        """Invalid species returns 404"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/species-profile/invalid_species")
        assert response.status_code == 404


class TestQuebecEnhancedData:
    """Tests for /api/bionic/optimization/quebec/enhanced-data endpoint"""
    
    def test_enhanced_data_returns_200(self):
        """Enhanced data endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/quebec/enhanced-data")
        assert response.status_code == 200
        
    def test_enhanced_data_contains_ugaf_zones(self):
        """Enhanced data contains UGAF zones"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/quebec/enhanced-data")
        data = response.json()
        
        assert "ugaf_zones" in data
        assert len(data["ugaf_zones"]) == 10  # 10 UGAF zones defined
        assert "UGAF_06" in data["ugaf_zones"]  # Laurentides
        assert "UGAF_28" in data["ugaf_zones"]  # Saguenay
        
    def test_enhanced_data_contains_hunting_pressure(self):
        """Enhanced data contains hunting pressure by region"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/quebec/enhanced-data")
        data = response.json()
        
        assert "hunting_pressure_by_region" in data
        pressure = data["hunting_pressure_by_region"]
        
        # Check all 5 regions
        assert "laurentides" in pressure
        assert "saguenay" in pressure
        assert "outaouais" in pressure
        assert "abitibi" in pressure
        assert "gaspesie" in pressure
        
        # Check species in each region
        for region in pressure:
            assert "deer" in pressure[region]
            assert "moose" in pressure[region]
            assert "bear" in pressure[region]
            
    def test_enhanced_data_contains_protected_areas(self):
        """Enhanced data contains protected areas (reserves, ZEC)"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/quebec/enhanced-data")
        data = response.json()
        
        assert "protected_areas" in data
        areas = data["protected_areas"]
        
        assert "reserve_rouge_matawin" in areas
        assert "reserve_laurentides" in areas
        assert "zec_batiscan_neilson" in areas
        assert "zec_chapais" in areas
        
    def test_enhanced_data_contains_seasonal_corrections(self):
        """Enhanced data contains seasonal corrections for all species"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/quebec/enhanced-data")
        data = response.json()
        
        assert "seasonal_corrections" in data
        corrections = data["seasonal_corrections"]
        
        # Check all 3 species
        assert "deer" in corrections
        assert "moose" in corrections
        assert "bear" in corrections
        
        # Check deer seasonal phases
        deer = corrections["deer"]
        assert "winter" in deer
        assert "spring" in deer
        assert "summer" in deer
        assert "pre_rut" in deer
        assert "rut" in deer
        assert "post_rut" in deer
        
        # Check bear seasonal phases (different from deer/moose)
        bear = corrections["bear"]
        assert "winter" in bear
        assert "hyperphagia" in bear
        assert "pre_denning" in bear
        
    def test_enhanced_data_contains_data_sources(self):
        """Enhanced data lists data sources"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/quebec/enhanced-data")
        data = response.json()
        
        assert "data_sources" in data
        sources = data["data_sources"]
        
        assert len(sources) == 4
        assert any("UGAF" in s for s in sources)
        assert any("ZEC" in s for s in sources)
        assert any("Réserves" in s for s in sources)
        assert any("MFFP" in s for s in sources)


class TestLocationFactors:
    """Tests for /api/bionic/optimization/quebec/location-factors endpoint"""
    
    @pytest.mark.parametrize("region,coords", TEST_LOCATIONS.items())
    def test_location_factors_returns_200(self, region, coords):
        """Location factors endpoint returns 200 for all Quebec regions"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/quebec/location-factors",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        assert response.status_code == 200
        
    def test_location_factors_laurentides_deer(self):
        """Location factors for Laurentides deer are correct"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/quebec/location-factors",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        assert data["location"]["lat"] == coords["lat"]
        assert data["location"]["lon"] == coords["lon"]
        assert data["species"] == "deer"
        
        factors = data["factors"]
        assert factors["region"] == "laurentides"
        assert factors["protected_area"] == "reserve_rouge_matawin"  # In protected area
        assert factors["protected_factor"] == 1.15  # +15% density
        assert factors["seasonal_phase"] == "winter"  # February
        assert factors["seasonal_correction"] == 0.4  # Winter correction for deer
        
    def test_location_factors_saguenay_moose(self):
        """Location factors for Saguenay moose are correct"""
        coords = TEST_LOCATIONS["saguenay"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/quebec/location-factors",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "moose"}
        )
        data = response.json()
        
        factors = data["factors"]
        assert factors["region"] == "saguenay"
        assert factors["protected_area"] is None  # Not in protected area
        assert factors["protected_factor"] == 1.0
        assert factors["seasonal_phase"] == "winter"
        assert factors["seasonal_correction"] == 0.35  # Winter correction for moose
        
    def test_location_factors_combined_modifier(self):
        """Combined modifier is calculated correctly"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/quebec/location-factors",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        factors = data["factors"]
        expected_combined = round(
            factors["protected_factor"] * 
            factors["hunting_pressure_modifier"] * 
            factors["seasonal_correction"], 
            3
        )
        assert data["combined_modifier"] == expected_combined
        
    def test_location_factors_invalid_coords(self):
        """Invalid coordinates return 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/quebec/location-factors",
            params={"lat": 999, "lon": -74.5, "species": "deer"}
        )
        assert response.status_code == 422


class TestP1Hooks:
    """Tests for /api/bionic/optimization/p1-hooks endpoint"""
    
    def test_p1_hooks_returns_200(self):
        """P1 hooks endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/p1-hooks")
        assert response.status_code == 200
        
    def test_p1_hooks_contains_required_fields(self):
        """P1 hooks response contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/p1-hooks")
        data = response.json()
        
        assert data["hooks_version"] == "1.0.0"
        assert data["ready_for_p1"] == True
        assert "expected_engines" in data
        assert "fusion_interface" in data
        assert "integration_notes" in data
        
    def test_p1_hooks_expected_engines(self):
        """P1 hooks defines 3 expected geospatial engines"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/p1-hooks")
        data = response.json()
        
        engines = data["expected_engines"]
        assert "corridorEngine" in engines
        assert "landcoverEngine" in engines
        assert "nutritionEngine" in engines
        
    def test_p1_hooks_corridor_engine_format(self):
        """corridorEngine has correct output format and fusion weights"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/p1-hooks")
        data = response.json()
        
        corridor = data["expected_engines"]["corridorEngine"]
        
        # Output format
        assert corridor["output_format"]["corridor_score"] == "float"
        assert corridor["output_format"]["connectivity_index"] == "float"
        assert corridor["output_format"]["movement_facilitation"] == "str"
        assert corridor["output_format"]["bottlenecks"] == "list"
        
        # Fusion weights
        assert corridor["fusion_weights"]["movement"] == 0.35
        assert corridor["fusion_weights"]["behavior"] == 0.25
        
    def test_p1_hooks_landcover_engine_format(self):
        """landcoverEngine has correct output format"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/p1-hooks")
        data = response.json()
        
        landcover = data["expected_engines"]["landcoverEngine"]
        
        assert landcover["output_format"]["cover_type"] == "str"
        assert landcover["output_format"]["cover_quality"] == "float"
        assert landcover["output_format"]["thermal_cover_percent"] == "float"
        
    def test_p1_hooks_nutrition_engine_format(self):
        """nutritionEngine has correct output format"""
        response = requests.get(f"{BASE_URL}/api/bionic/optimization/p1-hooks")
        data = response.json()
        
        nutrition = data["expected_engines"]["nutritionEngine"]
        
        assert nutrition["output_format"]["nutrition_score"] == "float"
        assert nutrition["output_format"]["food_availability"] == "str"
        assert nutrition["output_format"]["mast_index"] == "float"  # For bear


class TestEvaluateCoherence:
    """Tests for /api/bionic/optimization/evaluate endpoint"""
    
    @pytest.mark.parametrize("species", TEST_SPECIES)
    def test_evaluate_returns_200(self, species):
        """Evaluate endpoint returns 200 for all species"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": species}
        )
        assert response.status_code == 200
        
    def test_evaluate_contains_required_fields(self):
        """Evaluate response contains all required fields"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        assert "location" in data
        assert "species" in data
        assert "optimized_coherence" in data
        assert "raw_scores" in data
        assert "improvement_vs_baseline" in data
        
    def test_evaluate_optimized_coherence_structure(self):
        """Optimized coherence has correct structure"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        coherence = data["optimized_coherence"]
        assert "overall_score" in coherence
        assert "tests" in coherence
        assert "optimizations_applied" in coherence
        assert "p1_prefusion" in coherence
        assert "target_coherence" in coherence
        assert "gap_to_target" in coherence
        
        # Score should be between 0 and 1
        assert 0 <= coherence["overall_score"] <= 1
        assert coherence["target_coherence"] == 1.0
        
    def test_evaluate_has_5_coherence_tests(self):
        """Evaluate runs 5 coherence tests"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        tests = data["optimized_coherence"]["tests"]
        assert len(tests) == 5
        
        test_names = [t["test_name"] for t in tests]
        assert "activity_movement_correlation" in test_names
        assert "rut_activity_boost" in test_names
        assert "seasonal_behavior_alignment" in test_names
        assert "species_habitat_match" in test_names
        assert "movement_seasonal_pattern" in test_names
        
    def test_evaluate_test_structure(self):
        """Each coherence test has correct structure"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        for test in data["optimized_coherence"]["tests"]:
            assert "test_name" in test
            assert "is_coherent" in test
            assert "score" in test
            assert "explanation" in test
            assert "importance" in test
            
            # Score should be between 0 and 1
            assert 0 <= test["score"] <= 1
            
    def test_evaluate_optimizations_applied(self):
        """Optimizations applied contains all factors"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        opts = data["optimized_coherence"]["optimizations_applied"]
        assert "species_profile" in opts
        assert "seasonal_correction" in opts
        assert "seasonal_phase" in opts
        assert "protected_area_factor" in opts
        assert "hunting_pressure_modifier" in opts
        assert "region" in opts
        
    def test_evaluate_raw_scores(self):
        """Raw scores from all engines are present"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        raw = data["raw_scores"]
        assert "behavior_activity" in raw
        assert "seasonal_attractiveness" in raw
        assert "activity_probability" in raw
        assert "movement_km" in raw
        assert "habitat_suitability" in raw
        
    def test_evaluate_p1_prefusion_scores(self):
        """P1 prefusion scores are calculated"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        prefusion = data["optimized_coherence"]["p1_prefusion"]
        assert "behavior_activity" in prefusion
        assert "seasonal_species" in prefusion
        assert "activity_movement" in prefusion
        assert "overall_prefusion" in prefusion
        
    def test_evaluate_invalid_coords(self):
        """Invalid coordinates return 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": 999, "lon": -74.5, "species": "deer"}
        )
        assert response.status_code == 422


class TestCompareCoherence:
    """Tests for /api/bionic/optimization/compare endpoint"""
    
    @pytest.mark.parametrize("species", TEST_SPECIES)
    def test_compare_returns_200(self, species):
        """Compare endpoint returns 200 for all species"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/compare",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": species}
        )
        assert response.status_code == 200
        
    def test_compare_contains_required_fields(self):
        """Compare response contains all required fields"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/compare",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        assert "location" in data
        assert "species" in data
        assert "comparison" in data
        assert "optimizations_applied" in data
        assert "target" in data
        assert "remaining_gap" in data
        
    def test_compare_comparison_structure(self):
        """Comparison has baseline vs optimized scores"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/compare",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        comparison = data["comparison"]
        assert "baseline_coherence" in comparison
        assert "optimized_coherence" in comparison
        assert "improvement" in comparison
        assert "improvement_percent" in comparison
        
        # Scores should be between 0 and 1
        assert 0 <= comparison["baseline_coherence"] <= 1
        assert 0 <= comparison["optimized_coherence"] <= 1
        
    def test_compare_target_is_100_percent(self):
        """Target coherence is 1.0 (100%)"""
        coords = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/compare",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        data = response.json()
        
        assert data["target"] == 1.0
        
    def test_compare_invalid_coords(self):
        """Invalid coordinates return 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/compare",
            params={"lat": 999, "lon": -74.5, "species": "deer"}
        )
        assert response.status_code == 422


class TestAllRegionsAllSpecies:
    """Cross-validation tests for all regions and species"""
    
    @pytest.mark.parametrize("region,coords", TEST_LOCATIONS.items())
    @pytest.mark.parametrize("species", TEST_SPECIES)
    def test_evaluate_all_regions_all_species(self, region, coords, species):
        """Evaluate works for all region/species combinations"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/evaluate",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": species}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["species"] == species
        assert 0 <= data["optimized_coherence"]["overall_score"] <= 1
        
    @pytest.mark.parametrize("region,coords", TEST_LOCATIONS.items())
    def test_location_factors_all_regions(self, region, coords):
        """Location factors work for all Quebec regions"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/optimization/quebec/location-factors",
            params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Region should be detected (may be None for some coords)
        assert "factors" in data
        assert "combined_modifier" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
