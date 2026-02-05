"""
BIONIC™ P0-3 Integration Testing & ML Calibration - Backend Tests
==================================================================
Tests for P0-3 module: Integration testing between 6 behavior engines,
coherence matrix validation, and ML calibration with Quebec data.

Test Coverage:
- GET /api/bionic/p03/status - Module status
- GET /api/bionic/p03/test/single - Single integration test
- POST /api/bionic/p03/test/full - Full test suite (async)
- GET /api/bionic/p03/test/result/{task_id} - Async result retrieval
- GET /api/bionic/p03/calibration/quebec - Quebec calibration data
- GET /api/bionic/p03/calibration/region - Region-specific calibration
- GET /api/bionic/p03/coherence/matrix - Coherence matrix analysis
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates for Quebec regions
TEST_LOCATIONS = {
    "laurentides": {"lat": 46.5, "lon": -74.5},
    "saguenay": {"lat": 48.5, "lon": -71.0},
    "outaouais": {"lat": 46.0, "lon": -76.5},
    "abitibi": {"lat": 48.5, "lon": -78.0},
    "gaspesie": {"lat": 48.8, "lon": -66.0}
}

TEST_SPECIES = ["deer", "moose", "bear"]


class TestP03Status:
    """Tests for P0-3 module status endpoint"""
    
    def test_status_returns_200(self):
        """GET /api/bionic/p03/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ GET /api/bionic/p03/status returns 200")
    
    def test_status_contains_required_fields(self):
        """Status response contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/status")
        data = response.json()
        
        required_fields = ["module", "version", "status", "capabilities", 
                          "test_locations", "test_species", "calibration_regions", "timestamp"]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert data["status"] == "operational", f"Expected operational, got {data['status']}"
        assert data["version"] == "1.0.0", f"Expected version 1.0.0, got {data['version']}"
        print("✅ Status contains all required fields")
    
    def test_status_capabilities(self):
        """Status shows correct capabilities"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/status")
        data = response.json()
        
        expected_capabilities = [
            "Integration testing between 6 behavior engines",
            "Coherence matrix validation",
            "ML calibration with Quebec data",
            "Report generation"
        ]
        
        for cap in expected_capabilities:
            assert cap in data["capabilities"], f"Missing capability: {cap}"
        
        print("✅ All 4 capabilities present")
    
    def test_status_test_locations(self):
        """Status shows 5 Quebec test locations"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/status")
        data = response.json()
        
        expected_locations = ["Laurentides", "Saguenay", "Outaouais", "Abitibi", "Gaspésie"]
        
        assert len(data["test_locations"]) == 5, f"Expected 5 locations, got {len(data['test_locations'])}"
        for loc in expected_locations:
            assert loc in data["test_locations"], f"Missing location: {loc}"
        
        print("✅ All 5 Quebec test locations present")
    
    def test_status_test_species(self):
        """Status shows 3 test species"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/status")
        data = response.json()
        
        expected_species = ["deer", "moose", "bear"]
        
        assert len(data["test_species"]) == 3, f"Expected 3 species, got {len(data['test_species'])}"
        for sp in expected_species:
            assert sp in data["test_species"], f"Missing species: {sp}"
        
        print("✅ All 3 test species present (deer, moose, bear)")


class TestP03SingleIntegrationTest:
    """Tests for single integration test endpoint"""
    
    def test_single_test_laurentides_deer(self):
        """Single integration test for Laurentides with deer"""
        loc = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/test/single",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["status"] == "completed", f"Expected completed, got {data['status']}"
        assert "test_result" in data, "Missing test_result"
        
        result = data["test_result"]
        assert result["region"] == "laurentides", f"Expected laurentides, got {result['region']}"
        assert result["species"] == "deer", f"Expected deer, got {result['species']}"
        
        print("✅ Single test Laurentides/deer completed successfully")
    
    def test_single_test_returns_coherence_data(self):
        """Single test returns coherence matrix data"""
        loc = TEST_LOCATIONS["saguenay"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/test/single",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "moose"}
        )
        
        data = response.json()
        result = data["test_result"]
        
        assert "coherence" in result, "Missing coherence data"
        coherence = result["coherence"]
        
        assert "overall_score" in coherence, "Missing overall_score"
        assert "tests" in coherence, "Missing coherence tests"
        assert 0 <= coherence["overall_score"] <= 1, f"Invalid coherence score: {coherence['overall_score']}"
        
        print(f"✅ Coherence score: {coherence['overall_score']:.2%}")
    
    def test_single_test_returns_calibration_data(self):
        """Single test returns calibration data"""
        loc = TEST_LOCATIONS["outaouais"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/test/single",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "bear"}
        )
        
        data = response.json()
        result = data["test_result"]
        
        assert "calibration" in result, "Missing calibration data"
        calibration = result["calibration"]
        
        required_fields = ["expected_activity_level", "expected_probability", 
                          "actual_activity_level", "actual_probability",
                          "probability_deviation", "calibration_status", "region"]
        
        for field in required_fields:
            assert field in calibration, f"Missing calibration field: {field}"
        
        assert calibration["region"] == "outaouais", f"Expected outaouais, got {calibration['region']}"
        print("✅ Calibration data present with all required fields")
    
    def test_single_test_returns_raw_scores(self):
        """Single test returns raw scores from all engines"""
        loc = TEST_LOCATIONS["abitibi"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/test/single",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "moose"}
        )
        
        data = response.json()
        result = data["test_result"]
        
        assert "raw_scores" in result, "Missing raw_scores"
        raw = result["raw_scores"]
        
        expected_scores = ["behavior_activity", "behavior_opportunity", 
                          "seasonal_attractiveness", "activity_probability",
                          "species_habitat", "species_hunting_index"]
        
        for score in expected_scores:
            assert score in raw, f"Missing raw score: {score}"
        
        print("✅ Raw scores from all 6 engines present")
    
    def test_single_test_engines_success_count(self):
        """Single test shows correct engine success count"""
        loc = TEST_LOCATIONS["gaspesie"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/test/single",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "deer"}
        )
        
        data = response.json()
        result = data["test_result"]
        
        assert "engines_success" in result, "Missing engines_success"
        assert "engines_total" in result, "Missing engines_total"
        
        # For deer/moose, should be 6 engines (including rut)
        assert result["engines_total"] == 6, f"Expected 6 engines for deer, got {result['engines_total']}"
        assert result["engines_success"] >= 5, f"Expected at least 5 successful engines, got {result['engines_success']}"
        
        print(f"✅ Engines: {result['engines_success']}/{result['engines_total']} successful")
    
    def test_single_test_invalid_coordinates(self):
        """Single test with invalid coordinates returns 422"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/test/single",
            params={"lat": 100, "lon": -74.5, "species": "deer"}  # Invalid lat > 90
        )
        
        assert response.status_code == 422, f"Expected 422 for invalid lat, got {response.status_code}"
        print("✅ Invalid coordinates return 422")


class TestP03FullIntegrationTest:
    """Tests for full integration test suite (async)"""
    
    def test_full_test_starts_successfully(self):
        """POST /api/bionic/p03/test/full starts async task"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/p03/test/full",
            params={"include_report": True}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "task_id" in data, "Missing task_id"
        assert "status" in data, "Missing status"
        assert data["status"] == "started", f"Expected started, got {data['status']}"
        assert data["task_id"].startswith("p03_"), f"Invalid task_id format: {data['task_id']}"
        
        print(f"✅ Full test started with task_id: {data['task_id']}")
        return data["task_id"]
    
    def test_full_test_result_retrieval(self):
        """GET /api/bionic/p03/test/result/{task_id} retrieves results"""
        # Start a test
        start_response = requests.post(
            f"{BASE_URL}/api/bionic/p03/test/full",
            params={"include_report": True}
        )
        task_id = start_response.json()["task_id"]
        
        # Wait for completion (max 60 seconds)
        max_wait = 60
        wait_time = 0
        status = "running"
        
        while status == "running" and wait_time < max_wait:
            time.sleep(5)
            wait_time += 5
            
            result_response = requests.get(f"{BASE_URL}/api/bionic/p03/test/result/{task_id}")
            assert result_response.status_code == 200, f"Expected 200, got {result_response.status_code}"
            
            result_data = result_response.json()
            status = result_data.get("status", "unknown")
            print(f"  Status after {wait_time}s: {status}")
        
        assert status == "completed", f"Test did not complete in {max_wait}s, status: {status}"
        
        # Verify result structure
        assert "report" in result_data or "results" in result_data, "Missing report or results"
        
        if "report" in result_data:
            report = result_data["report"]
            assert "executive_summary" in report, "Missing executive_summary"
            assert "regional_analysis" in report, "Missing regional_analysis"
            assert "species_analysis" in report, "Missing species_analysis"
            assert "validation" in report, "Missing validation"
            
            print(f"✅ Full test completed with report")
            print(f"   Success rate: {report['executive_summary'].get('success_rate', 'N/A')}")
            print(f"   Coherence: {report['executive_summary'].get('average_coherence', 'N/A')}")
        
        return result_data
    
    def test_full_test_invalid_task_id(self):
        """GET /api/bionic/p03/test/result with invalid task_id returns 404"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/test/result/invalid_task_123")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Invalid task_id returns 404")


class TestP03CalibrationQuebec:
    """Tests for Quebec calibration data endpoint"""
    
    def test_quebec_calibration_returns_200(self):
        """GET /api/bionic/p03/calibration/quebec returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/calibration/quebec")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ GET /api/bionic/p03/calibration/quebec returns 200")
    
    def test_quebec_calibration_regions(self):
        """Quebec calibration contains all 5 regions"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/calibration/quebec")
        data = response.json()
        
        assert "regions" in data, "Missing regions"
        regions = data["regions"]
        
        expected_regions = ["laurentides", "saguenay", "outaouais", "abitibi", "gaspesie"]
        for region in expected_regions:
            assert region in regions, f"Missing region: {region}"
            
            # Verify region data structure
            region_data = regions[region]
            assert "lat_range" in region_data, f"Missing lat_range for {region}"
            assert "lon_range" in region_data, f"Missing lon_range for {region}"
            assert "climate_zone" in region_data, f"Missing climate_zone for {region}"
            assert "primary_species" in region_data, f"Missing primary_species for {region}"
        
        print("✅ All 5 Quebec regions with complete data")
    
    def test_quebec_calibration_thermal_coefficients(self):
        """Quebec calibration contains thermal coefficients"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/calibration/quebec")
        data = response.json()
        
        assert "thermal_coefficients" in data, "Missing thermal_coefficients"
        thermal = data["thermal_coefficients"]
        
        for species in ["deer", "moose", "bear", "turkey"]:
            assert species in thermal, f"Missing thermal coefficients for {species}"
            
            coef = thermal[species]
            assert "optimal_temp_min" in coef, f"Missing optimal_temp_min for {species}"
            assert "optimal_temp_max" in coef, f"Missing optimal_temp_max for {species}"
            assert "activity_boost_cold" in coef, f"Missing activity_boost_cold for {species}"
            assert "activity_penalty_hot" in coef, f"Missing activity_penalty_hot for {species}"
        
        print("✅ Thermal coefficients for all species present")
    
    def test_quebec_calibration_pressure_coefficients(self):
        """Quebec calibration contains pressure coefficients"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/calibration/quebec")
        data = response.json()
        
        assert "pressure_coefficients" in data, "Missing pressure_coefficients"
        pressure = data["pressure_coefficients"]
        
        expected_trends = ["rising_fast", "rising", "stable", "falling", "falling_fast"]
        for trend in expected_trends:
            assert trend in pressure, f"Missing pressure coefficient for {trend}"
            assert isinstance(pressure[trend], (int, float)), f"Invalid coefficient type for {trend}"
        
        print("✅ Pressure coefficients for all trends present")
    
    def test_quebec_calibration_lunar_coefficients(self):
        """Quebec calibration contains lunar coefficients"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/calibration/quebec")
        data = response.json()
        
        assert "lunar_coefficients" in data, "Missing lunar_coefficients"
        lunar = data["lunar_coefficients"]
        
        expected_phases = ["new_moon", "first_quarter", "full_moon", "last_quarter"]
        for phase in expected_phases:
            assert phase in lunar, f"Missing lunar coefficient for {phase}"
        
        print("✅ Lunar coefficients for all phases present")
    
    def test_quebec_calibration_harvest_density(self):
        """Quebec calibration contains harvest density data"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/calibration/quebec")
        data = response.json()
        
        assert "harvest_density" in data, "Missing harvest_density"
        harvest = data["harvest_density"]
        
        for region in ["laurentides", "saguenay", "outaouais", "abitibi", "gaspesie"]:
            assert region in harvest, f"Missing harvest density for {region}"
            
            for species in ["deer", "moose", "bear"]:
                assert species in harvest[region], f"Missing {species} density for {region}"
                density = harvest[region][species]
                assert 0 <= density <= 1, f"Invalid density {density} for {region}/{species}"
        
        print("✅ Harvest density data for all regions and species")
    
    def test_quebec_calibration_data_source(self):
        """Quebec calibration shows data source"""
        response = requests.get(f"{BASE_URL}/api/bionic/p03/calibration/quebec")
        data = response.json()
        
        assert "data_source" in data, "Missing data_source"
        assert "MFFP" in data["data_source"], "Missing MFFP in data source"
        assert "Environnement Canada" in data["data_source"], "Missing Environnement Canada"
        
        print(f"✅ Data source: {data['data_source']}")


class TestP03CalibrationRegion:
    """Tests for region-specific calibration endpoint"""
    
    def test_region_calibration_laurentides(self):
        """Region calibration for Laurentides"""
        loc = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/calibration/region",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["region"] == "laurentides", f"Expected laurentides, got {data['region']}"
        assert data["species"] == "deer", f"Expected deer, got {data['species']}"
        assert "region_data" in data, "Missing region_data"
        assert "thermal_coefficients" in data, "Missing thermal_coefficients"
        assert "expected_activity" in data, "Missing expected_activity"
        
        print("✅ Region calibration for Laurentides/deer")
    
    def test_region_calibration_expected_activity(self):
        """Region calibration returns expected activity data"""
        loc = TEST_LOCATIONS["saguenay"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/calibration/region",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "moose"}
        )
        
        data = response.json()
        activity = data["expected_activity"]
        
        assert "level" in activity, "Missing activity level"
        assert "probability" in activity, "Missing activity probability"
        assert "month" in activity, "Missing month"
        assert "hour" in activity, "Missing hour"
        
        assert activity["level"] in ["very_low", "low", "moderate", "high", "peak"], \
            f"Invalid activity level: {activity['level']}"
        assert 0 <= activity["probability"] <= 1, f"Invalid probability: {activity['probability']}"
        
        print(f"✅ Expected activity: {activity['level']} ({activity['probability']:.1%})")
    
    def test_region_calibration_outside_quebec(self):
        """Region calibration for location outside Quebec"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/calibration/region",
            params={"lat": 40.0, "lon": -74.0, "species": "deer"}  # New York area
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["region"] is None, f"Expected None region, got {data['region']}"
        assert data["using_defaults"] is True, "Expected using_defaults=True"
        
        print("✅ Location outside Quebec returns defaults")
    
    def test_region_calibration_all_regions(self):
        """Region calibration works for all 5 Quebec regions"""
        for region_name, coords in TEST_LOCATIONS.items():
            response = requests.get(
                f"{BASE_URL}/api/bionic/p03/calibration/region",
                params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
            )
            
            assert response.status_code == 200, f"Failed for {region_name}"
            data = response.json()
            assert data["region"] == region_name, f"Expected {region_name}, got {data['region']}"
        
        print("✅ All 5 Quebec regions return correct calibration")


class TestP03CoherenceMatrix:
    """Tests for coherence matrix endpoint"""
    
    def test_coherence_matrix_returns_200(self):
        """GET /api/bionic/p03/coherence/matrix returns 200"""
        loc = TEST_LOCATIONS["laurentides"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/coherence/matrix",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "deer"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ GET /api/bionic/p03/coherence/matrix returns 200")
    
    def test_coherence_matrix_structure(self):
        """Coherence matrix returns correct structure"""
        loc = TEST_LOCATIONS["saguenay"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/coherence/matrix",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "moose"}
        )
        
        data = response.json()
        
        assert "location" in data, "Missing location"
        assert "species" in data, "Missing species"
        assert "coherence" in data, "Missing coherence"
        assert "calibration" in data, "Missing calibration"
        assert "raw_scores" in data, "Missing raw_scores"
        assert data["status"] == "completed", f"Expected completed, got {data['status']}"
        
        print("✅ Coherence matrix structure validated")
    
    def test_coherence_matrix_tests(self):
        """Coherence matrix contains 5 coherence tests"""
        loc = TEST_LOCATIONS["outaouais"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/coherence/matrix",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "bear"}
        )
        
        data = response.json()
        coherence = data["coherence"]
        
        assert "overall_score" in coherence, "Missing overall_score"
        assert "tests" in coherence, "Missing tests"
        
        tests = coherence["tests"]
        assert len(tests) >= 4, f"Expected at least 4 coherence tests, got {len(tests)}"
        
        expected_tests = [
            "activity_movement_correlation",
            "seasonal_behavior_alignment",
            "species_habitat_match",
            "movement_seasonal_pattern"
        ]
        
        test_names = [t["test_name"] for t in tests]
        for expected in expected_tests:
            assert expected in test_names, f"Missing coherence test: {expected}"
        
        print(f"✅ {len(tests)} coherence tests executed")
    
    def test_coherence_matrix_score_validation(self):
        """Coherence matrix score is >= 70% for Quebec regions"""
        for region_name, coords in TEST_LOCATIONS.items():
            response = requests.get(
                f"{BASE_URL}/api/bionic/p03/coherence/matrix",
                params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
            )
            
            data = response.json()
            score = data["coherence"]["overall_score"]
            
            assert score >= 0.70, f"Coherence score {score:.1%} < 70% for {region_name}"
            print(f"  {region_name}: {score:.1%}")
        
        print("✅ All regions have coherence >= 70%")
    
    def test_coherence_test_result_structure(self):
        """Each coherence test has correct structure"""
        loc = TEST_LOCATIONS["abitibi"]
        response = requests.get(
            f"{BASE_URL}/api/bionic/p03/coherence/matrix",
            params={"lat": loc["lat"], "lon": loc["lon"], "species": "moose"}
        )
        
        data = response.json()
        tests = data["coherence"]["tests"]
        
        for test in tests:
            assert "test_name" in test, "Missing test_name"
            assert "engines_compared" in test, "Missing engines_compared"
            assert "is_coherent" in test, "Missing is_coherent"
            assert "score" in test, "Missing score"
            assert "expected" in test, "Missing expected"
            assert "actual" in test, "Missing actual"
            
            assert 0 <= test["score"] <= 1, f"Invalid score: {test['score']}"
            assert isinstance(test["is_coherent"], bool), "is_coherent should be boolean"
        
        print("✅ All coherence test results have correct structure")


class TestP03AllSpecies:
    """Tests for all 3 species across regions"""
    
    def test_deer_all_regions(self):
        """Deer integration test works for all regions"""
        for region_name, coords in TEST_LOCATIONS.items():
            response = requests.get(
                f"{BASE_URL}/api/bionic/p03/test/single",
                params={"lat": coords["lat"], "lon": coords["lon"], "species": "deer"}
            )
            
            assert response.status_code == 200, f"Failed for deer in {region_name}"
            data = response.json()
            assert data["status"] == "completed", f"Test not completed for deer in {region_name}"
        
        print("✅ Deer tests pass for all 5 regions")
    
    def test_moose_all_regions(self):
        """Moose integration test works for all regions"""
        for region_name, coords in TEST_LOCATIONS.items():
            response = requests.get(
                f"{BASE_URL}/api/bionic/p03/test/single",
                params={"lat": coords["lat"], "lon": coords["lon"], "species": "moose"}
            )
            
            assert response.status_code == 200, f"Failed for moose in {region_name}"
            data = response.json()
            assert data["status"] == "completed", f"Test not completed for moose in {region_name}"
        
        print("✅ Moose tests pass for all 5 regions")
    
    def test_bear_all_regions(self):
        """Bear integration test works for all regions"""
        for region_name, coords in TEST_LOCATIONS.items():
            response = requests.get(
                f"{BASE_URL}/api/bionic/p03/test/single",
                params={"lat": coords["lat"], "lon": coords["lon"], "species": "bear"}
            )
            
            assert response.status_code == 200, f"Failed for bear in {region_name}"
            data = response.json()
            assert data["status"] == "completed", f"Test not completed for bear in {region_name}"
            
            # Bear should have 5 engines (no rut)
            result = data["test_result"]
            assert result["engines_total"] == 5, f"Expected 5 engines for bear, got {result['engines_total']}"
        
        print("✅ Bear tests pass for all 5 regions (5 engines, no rut)")


class TestP03ReportSummary:
    """Tests for report summary endpoint"""
    
    def test_report_summary_no_tests(self):
        """Report summary with no tests returns appropriate message"""
        # This test may fail if tests have been run in the session
        response = requests.get(f"{BASE_URL}/api/bionic/p03/report/summary")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Either shows message or summary depending on state
        assert "message" in data or "summary" in data, "Missing message or summary"
        print("✅ Report summary endpoint returns 200")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
