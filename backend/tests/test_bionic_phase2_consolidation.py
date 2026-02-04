"""
BIONIC™ Phase 2 Consolidation Tests
====================================
Tests for verifying API compatibility after Pydantic model consolidation.
- bionic_core_models.py removed (redundant)
- Enums synchronized between configs.py and models.py
- All 8 modules and 6 species must work correctly

Version: BIONIC_CORE 2.0
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBionicModulesEndpoint:
    """Test GET /api/bionic/modules - Must return 8 modules"""
    
    def test_modules_endpoint_returns_success(self):
        """Verify modules endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_modules_returns_8_modules(self):
        """Verify exactly 8 modules are returned"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        data = response.json()
        assert data.get("total") == 8
        assert len(data.get("modules", [])) == 8
    
    def test_modules_have_correct_names(self):
        """Verify all 8 module names are correct"""
        expected_modules = ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"]
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        data = response.json()
        
        module_ids = [m.get("id") for m in data.get("modules", [])]
        for expected in expected_modules:
            assert expected in module_ids, f"Module '{expected}' not found in response"
    
    def test_each_module_has_required_fields(self):
        """Verify each module has id, name, description, factors"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        data = response.json()
        
        for module in data.get("modules", []):
            assert "id" in module, f"Module missing 'id' field"
            assert "name" in module, f"Module {module.get('id')} missing 'name' field"
            assert "description" in module, f"Module {module.get('id')} missing 'description' field"
            assert "factors" in module, f"Module {module.get('id')} missing 'factors' field"
            # Note: weights may be in individual module info endpoint, not list endpoint


class TestBionicSpeciesEndpoint:
    """Test GET /api/bionic/species - Must return 6 species"""
    
    def test_species_endpoint_returns_success(self):
        """Verify species endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_species_returns_6_species(self):
        """Verify exactly 6 species are returned"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        data = response.json()
        assert data.get("total") == 6
        assert len(data.get("species", [])) == 6
    
    def test_species_have_correct_names(self):
        """Verify all 6 species names are correct"""
        expected_species = ["moose", "deer", "bear", "caribou", "wolf", "turkey"]
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        data = response.json()
        
        species_ids = [s.get("id") for s in data.get("species", [])]
        for expected in expected_species:
            assert expected in species_ids, f"Species '{expected}' not found in response"
    
    def test_each_species_has_required_fields(self):
        """Verify each species has id, name, common_name, module_weights"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        data = response.json()
        
        for species in data.get("species", []):
            assert "id" in species, f"Species missing 'id' field"
            assert "name" in species, f"Species {species.get('id')} missing 'name' field"
            assert "common_name" in species, f"Species {species.get('id')} missing 'common_name' field"
            assert "module_weights" in species, f"Species {species.get('id')} missing 'module_weights' field"


class TestBionicAnalyzeEndpoint:
    """Test POST /api/bionic/analyze - Complete analysis"""
    
    def test_analyze_endpoint_returns_success(self):
        """Verify analyze endpoint returns 200 with valid request"""
        payload = {
            "territory_id": "test_phase2_consolidation",
            "latitude": 46.8,
            "longitude": -71.2,
            "radius_km": 5.0,
            "modules": ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"],
            "species": ["moose", "deer", "bear"],
            "include_ai_predictions": True,
            "include_temporal": True
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
    
    def test_analyze_returns_all_8_modules(self):
        """Verify analysis returns results for all 8 modules"""
        payload = {
            "territory_id": "test_phase2_modules",
            "latitude": 46.8,
            "longitude": -71.2,
            "radius_km": 5.0,
            "modules": ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"],
            "species": ["moose"],
            "include_ai_predictions": False,
            "include_temporal": False
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data.get("analysis", {})
        modules = analysis.get("modules", {})
        
        expected_modules = ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"]
        for module_name in expected_modules:
            assert module_name in modules, f"Module '{module_name}' not in analysis results"
            assert "score" in modules[module_name], f"Module '{module_name}' missing 'score'"
    
    def test_analyze_returns_species_scores(self):
        """Verify analysis returns species scores"""
        payload = {
            "territory_id": "test_phase2_species",
            "latitude": 46.8,
            "longitude": -71.2,
            "radius_km": 5.0,
            "modules": ["food", "wetness"],
            "species": ["moose", "deer", "bear", "caribou", "wolf", "turkey"],
            "include_ai_predictions": False,
            "include_temporal": False
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data.get("analysis", {})
        species = analysis.get("species", {})
        
        expected_species = ["moose", "deer", "bear", "caribou", "wolf", "turkey"]
        for species_name in expected_species:
            assert species_name in species, f"Species '{species_name}' not in analysis results"
            assert "score" in species[species_name], f"Species '{species_name}' missing 'score'"
    
    def test_analyze_returns_predictions(self):
        """Verify analysis returns AI predictions when requested"""
        payload = {
            "territory_id": "test_phase2_predictions",
            "latitude": 46.8,
            "longitude": -71.2,
            "radius_km": 5.0,
            "modules": ["food"],
            "species": ["moose"],
            "include_ai_predictions": True,
            "include_temporal": False
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data.get("analysis", {})
        predictions = analysis.get("predictions", {})
        
        assert predictions is not None, "Predictions should be present"
        # API returns forecast_24h, forecast_72h, forecast_7d format
        has_forecasts = "forecast_24h" in predictions or "forecast_72h" in predictions or "forecast_7d" in predictions
        assert has_forecasts, f"Predictions should have forecast time horizons, got: {list(predictions.keys())}"
    
    def test_analyze_returns_global_score(self):
        """Verify analysis returns global score and rating"""
        payload = {
            "territory_id": "test_phase2_global",
            "latitude": 46.8,
            "longitude": -71.2,
            "radius_km": 5.0,
            "modules": ["food", "wetness", "thermal"],
            "species": ["moose", "deer"],
            "include_ai_predictions": False,
            "include_temporal": False
        }
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        data = response.json()
        
        analysis = data.get("analysis", {})
        
        # Check for global score (could be overall_score or global_score)
        has_score = "overall_score" in analysis or "global_score" in analysis
        assert has_score, "Analysis should have overall_score or global_score"
        
        # Check for rating
        has_rating = "overall_rating" in analysis or "global_rating" in analysis
        assert has_rating, "Analysis should have overall_rating or global_rating"


class TestBionicStatsEndpoint:
    """Test GET /api/bionic/stats - Must return BIONIC_CORE 2.0"""
    
    def test_stats_endpoint_returns_success(self):
        """Verify stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        assert response.status_code == 200
    
    def test_stats_returns_bionic_core_2_version(self):
        """Verify engine_version is BIONIC_CORE 2.0"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        engine_version = data.get("engine_version", "")
        assert engine_version == "BIONIC_CORE 2.0", f"Expected 'BIONIC_CORE 2.0', got '{engine_version}'"
    
    def test_stats_has_required_fields(self):
        """Verify stats has all required fields"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        required_fields = [
            "total_analyses",
            "total_species_models",
            "total_zones_generated",
            "total_waypoints",
            "total_favorites",
            "average_global_score",
            "engine_version"
        ]
        
        for field in required_fields:
            assert field in data, f"Stats missing required field: {field}"


class TestIndividualModuleEndpoints:
    """Test individual module info endpoints"""
    
    @pytest.mark.parametrize("module_id", ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"])
    def test_get_module_info(self, module_id):
        """Verify each module info endpoint works"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules/{module_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("module", {}).get("id") == module_id


class TestIndividualSpeciesEndpoints:
    """Test individual species info endpoints"""
    
    @pytest.mark.parametrize("species_id", ["moose", "deer", "bear", "caribou", "wolf", "turkey"])
    def test_get_species_info(self, species_id):
        """Verify each species info endpoint works"""
        response = requests.get(f"{BASE_URL}/api/bionic/species/{species_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("species", {}).get("id") == species_id


class TestEnumSynchronization:
    """Test that Enums are properly synchronized between configs.py and models.py"""
    
    def test_module_types_match_api_response(self):
        """Verify ModuleType enum values match API response"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        data = response.json()
        
        api_module_ids = set(m.get("id") for m in data.get("modules", []))
        expected_enum_values = {"thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"}
        
        assert api_module_ids == expected_enum_values, f"Module IDs mismatch: API={api_module_ids}, Expected={expected_enum_values}"
    
    def test_species_types_match_api_response(self):
        """Verify SpeciesType enum values match API response"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        data = response.json()
        
        api_species_ids = set(s.get("id") for s in data.get("species", []))
        expected_enum_values = {"moose", "deer", "bear", "caribou", "wolf", "turkey"}
        
        assert api_species_ids == expected_enum_values, f"Species IDs mismatch: API={api_species_ids}, Expected={expected_enum_values}"


class TestNewPydanticModels:
    """Test that new Pydantic models (PressureModuleResult, AccessModuleResult, etc.) work correctly"""
    
    def test_pressure_module_returns_valid_result(self):
        """Verify pressure module returns valid result structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules/pressure")
        assert response.status_code == 200
        data = response.json()
        
        module = data.get("module", {})
        assert module.get("id") == "pressure"
        assert "factors" in module
        assert "weights" in module
    
    def test_access_module_returns_valid_result(self):
        """Verify access module returns valid result structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules/access")
        assert response.status_code == 200
        data = response.json()
        
        module = data.get("module", {})
        assert module.get("id") == "access"
        assert "factors" in module
        assert "weights" in module
    
    def test_corridor_module_returns_valid_result(self):
        """Verify corridor module returns valid result structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules/corridor")
        assert response.status_code == 200
        data = response.json()
        
        module = data.get("module", {})
        assert module.get("id") == "corridor"
        assert "factors" in module
        assert "weights" in module
    
    def test_geoform_module_returns_valid_result(self):
        """Verify geoform module returns valid result structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules/geoform")
        assert response.status_code == 200
        data = response.json()
        
        module = data.get("module", {})
        assert module.get("id") == "geoform"
        assert "factors" in module
        assert "weights" in module


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
