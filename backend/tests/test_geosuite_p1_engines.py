"""
BIONIC™ P1 Géo-Suite - Comprehensive API Tests
================================================
Tests for the 5 geospatial engines:
1. corridorEngine - Wildlife corridor detection
2. landcoverEngine - Land cover classification
3. nutritionEngine - Nutritional index analysis
4. populationDensityEngine - Animal population density
5. huntingPressureModule - Hunting pressure analysis

Test locations:
- Quebec: (46.8, -71.2)
- Laurentides: (46.5, -74.5)
- USA (New York): (40.7, -74.0)
"""

import pytest
import requests
import os
from typing import Dict, Any

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates
QUEBEC_COORDS = {"lat": 46.8, "lon": -71.2}
LAURENTIDES_COORDS = {"lat": 46.5, "lon": -74.5}
USA_NY_COORDS = {"lat": 40.7, "lon": -74.0}


class TestGeoSuiteStatus:
    """Test Géo-Suite status endpoint"""
    
    def test_geosuite_status_returns_200(self):
        """GET /api/bionic/geosuite/status - Returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/status")
        assert response.status_code == 200
        
    def test_geosuite_status_structure(self):
        """GET /api/bionic/geosuite/status - Returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/status")
        data = response.json()
        
        # Verify required fields
        assert data["status"] == "operational"
        assert data["version"] == "1.0.0"
        assert data["phase"] == "P1"
        assert "BIONIC" in data["name"]
        assert data["north_america_ready"] == True
        
    def test_geosuite_status_engines(self):
        """GET /api/bionic/geosuite/status - All 5 engines active"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/status")
        data = response.json()
        
        engines = data["engines"]
        expected_engines = [
            "corridorEngine",
            "landcoverEngine", 
            "nutritionEngine",
            "populationDensityEngine",
            "huntingPressureModule"
        ]
        
        for engine in expected_engines:
            assert engine in engines, f"Missing engine: {engine}"
            assert engines[engine]["status"] == "active"
            assert engines[engine]["version"] == "1.0.0"
            
    def test_geosuite_status_data_sources(self):
        """GET /api/bionic/geosuite/status - Data sources configured"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/status")
        data = response.json()
        
        sources = data["data_sources"]
        
        # Quebec sources
        assert "SIGÉOM" in sources["quebec"]
        assert "MFFP" in sources["quebec"]
        
        # Canada sources
        assert "CanVec" in sources["canada"]
        
        # USA sources
        assert "NLCD" in sources["usa"]
        assert "USGS" in sources["usa"]
        
        # Global sources
        assert "OSM" in sources["global"]


class TestCorridorEngine:
    """Test CorridorEngine - Wildlife corridor detection"""
    
    def test_corridor_analyze_quebec_returns_200(self):
        """POST /api/bionic/geosuite/corridor/analyze - Quebec returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        assert response.status_code == 200
        
    def test_corridor_analyze_quebec_structure(self):
        """POST /api/bionic/geosuite/corridor/analyze - Quebec returns correct structure"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Verify engine metadata
        assert data["engine_name"] == "CorridorEngine"
        assert data["engine_version"] == "1.0.0"
        assert "analysis_id" in data
        assert data["analysis_id"].startswith("cor_")
        
        # Verify location
        assert data["location"]["lat"] == QUEBEC_COORDS["lat"]
        assert data["location"]["lon"] == QUEBEC_COORDS["lon"]
        
        # Verify region detection
        assert data["region"] == "quebec"
        
    def test_corridor_analyze_quebec_score_range(self):
        """POST /api/bionic/geosuite/corridor/analyze - Score in valid range 0-100"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert 0 <= data["score"] <= 100
        assert data["level"] in ["excellent", "good", "moderate", "low", "poor"]
        
    def test_corridor_analyze_quebec_corridors_data(self):
        """POST /api/bionic/geosuite/corridor/analyze - Returns corridor data"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Verify corridors data
        assert "corridors_count" in data["data"]
        assert "corridors" in data["data"]
        assert "connectivity_index" in data["data"]
        assert "species_scores" in data["data"]
        
        # Verify connectivity index range
        assert 0 <= data["data"]["connectivity_index"] <= 1
        
    def test_corridor_analyze_quebec_species_scores(self):
        """POST /api/bionic/geosuite/corridor/analyze - Species scores present"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        species_scores = data["data"]["species_scores"]
        expected_species = ["deer", "moose", "bear", "turkey", "caribou", "wolf", "waterfowl", "smallgame"]
        
        for species in expected_species:
            assert species in species_scores, f"Missing species: {species}"
            
    def test_corridor_analyze_usa_returns_200(self):
        """POST /api/bionic/geosuite/corridor/analyze - USA returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=USA_NY_COORDS
        )
        assert response.status_code == 200
        
    def test_corridor_analyze_usa_region_detection(self):
        """POST /api/bionic/geosuite/corridor/analyze - USA region detected"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=USA_NY_COORDS
        )
        data = response.json()
        
        assert data["region"] == "usa"
        
    def test_corridor_analyze_recommendations(self):
        """POST /api/bionic/geosuite/corridor/analyze - Returns recommendations"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)


class TestLandcoverEngine:
    """Test LandcoverEngine - Land cover classification"""
    
    def test_landcover_analyze_quebec_returns_200(self):
        """POST /api/bionic/geosuite/landcover/analyze - Quebec returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/landcover/analyze",
            json=QUEBEC_COORDS
        )
        assert response.status_code == 200
        
    def test_landcover_analyze_quebec_structure(self):
        """POST /api/bionic/geosuite/landcover/analyze - Quebec returns correct structure"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/landcover/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Verify engine metadata
        assert data["engine_name"] == "LandcoverEngine"
        assert data["engine_version"] == "1.0.0"
        assert data["analysis_id"].startswith("lco_")
        
        # Verify region
        assert data["region"] == "quebec"
        
    def test_landcover_analyze_quebec_score_range(self):
        """POST /api/bionic/geosuite/landcover/analyze - Score in valid range"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/landcover/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert 0 <= data["score"] <= 100
        assert data["level"] in ["excellent", "good", "moderate", "low", "poor"]
        
    def test_landcover_analyze_quebec_cover_data(self):
        """POST /api/bionic/geosuite/landcover/analyze - Returns cover composition"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/landcover/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Verify cover data
        assert "dominant_cover" in data["data"]
        assert "cover_composition" in data["data"]
        assert "edge_density_m_ha" in data["data"]
        assert "thermal_cover_percent" in data["data"]
        assert "structural_diversity" in data["data"]
        
    def test_landcover_analyze_quebec_species_habitat(self):
        """POST /api/bionic/geosuite/landcover/analyze - Species habitat scores"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/landcover/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "species_habitat_scores" in data["data"]
        habitat_scores = data["data"]["species_habitat_scores"]
        
        expected_species = ["deer", "moose", "bear", "turkey"]
        for species in expected_species:
            assert species in habitat_scores
            assert 0 <= habitat_scores[species] <= 100
            
    def test_landcover_analyze_usa_returns_200(self):
        """POST /api/bionic/geosuite/landcover/analyze - USA returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/landcover/analyze",
            json=USA_NY_COORDS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["region"] == "usa"


class TestNutritionEngine:
    """Test NutritionEngine - Nutritional index analysis"""
    
    def test_nutrition_analyze_quebec_returns_200(self):
        """POST /api/bionic/geosuite/nutrition/analyze - Quebec returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/nutrition/analyze",
            json=QUEBEC_COORDS
        )
        assert response.status_code == 200
        
    def test_nutrition_analyze_quebec_structure(self):
        """POST /api/bionic/geosuite/nutrition/analyze - Quebec returns correct structure"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/nutrition/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Verify engine metadata
        assert data["engine_name"] == "NutritionEngine"
        assert data["engine_version"] == "1.0.0"
        assert data["analysis_id"].startswith("nut_")
        
        # Verify region
        assert data["region"] == "quebec"
        
    def test_nutrition_analyze_quebec_score_range(self):
        """POST /api/bionic/geosuite/nutrition/analyze - Score in valid range"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/nutrition/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert 0 <= data["score"] <= 100
        
    def test_nutrition_analyze_quebec_food_availability(self):
        """POST /api/bionic/geosuite/nutrition/analyze - Food availability data"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/nutrition/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "food_availability" in data["data"]
        assert data["data"]["food_availability"] in ["abundant", "moderate", "scarce"]
        
    def test_nutrition_analyze_quebec_species_nutrition(self):
        """POST /api/bionic/geosuite/nutrition/analyze - Species nutrition data"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/nutrition/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "species_nutrition" in data["data"]
        species_nutrition = data["data"]["species_nutrition"]
        
        expected_species = ["deer", "moose", "bear", "turkey"]
        for species in expected_species:
            assert species in species_nutrition
            assert "score" in species_nutrition[species]
            assert "food_availability" in species_nutrition[species]
            
    def test_nutrition_analyze_usa_returns_200(self):
        """POST /api/bionic/geosuite/nutrition/analyze - USA returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/nutrition/analyze",
            json=USA_NY_COORDS
        )
        assert response.status_code == 200


class TestPopulationDensityEngine:
    """Test PopulationDensityEngine - Animal population density"""
    
    def test_population_density_quebec_returns_200(self):
        """POST /api/bionic/geosuite/population/density - Quebec returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/population/density",
            json=QUEBEC_COORDS
        )
        assert response.status_code == 200
        
    def test_population_density_quebec_structure(self):
        """POST /api/bionic/geosuite/population/density - Quebec returns correct structure"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/population/density",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Verify engine metadata
        assert data["engine_name"] == "PopulationDensityEngine"
        assert data["engine_version"] == "1.0.0"
        assert data["analysis_id"].startswith("pop_")
        
        # Verify region
        assert data["region"] == "quebec"
        
    def test_population_density_quebec_score_range(self):
        """POST /api/bionic/geosuite/population/density - Score in valid range"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/population/density",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert 0 <= data["score"] <= 100
        
    def test_population_density_quebec_category(self):
        """POST /api/bionic/geosuite/population/density - Density category"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/population/density",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "density_category" in data["data"]
        assert data["data"]["density_category"] in ["high", "medium", "low", "very_low"]
        
    def test_population_density_quebec_species_densities(self):
        """POST /api/bionic/geosuite/population/density - Species densities"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/population/density",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "species_densities" in data["data"]
        species_densities = data["data"]["species_densities"]
        
        expected_species = ["deer", "moose", "bear", "turkey"]
        for species in expected_species:
            assert species in species_densities
            assert "density_per_100km2" in species_densities[species]
            assert "trend" in species_densities[species]
            assert "confidence" in species_densities[species]
            
    def test_population_density_usa_returns_200(self):
        """POST /api/bionic/geosuite/population/density - USA returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/population/density",
            json=USA_NY_COORDS
        )
        assert response.status_code == 200


class TestHuntingPressureModule:
    """Test HuntingPressureModule - Hunting pressure analysis"""
    
    def test_hunting_pressure_quebec_returns_200(self):
        """POST /api/bionic/geosuite/hunting-pressure/analyze - Quebec returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/hunting-pressure/analyze",
            json=QUEBEC_COORDS
        )
        assert response.status_code == 200
        
    def test_hunting_pressure_quebec_structure(self):
        """POST /api/bionic/geosuite/hunting-pressure/analyze - Quebec returns correct structure"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/hunting-pressure/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Verify engine metadata
        assert data["engine_name"] == "HuntingPressureModule"
        assert data["engine_version"] == "1.0.0"
        assert data["analysis_id"].startswith("pre_")
        
        # Verify region
        assert data["region"] == "quebec"
        
    def test_hunting_pressure_quebec_score_range(self):
        """POST /api/bionic/geosuite/hunting-pressure/analyze - Score in valid range"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/hunting-pressure/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert 0 <= data["score"] <= 100
        
    def test_hunting_pressure_quebec_pressure_level(self):
        """POST /api/bionic/geosuite/hunting-pressure/analyze - Pressure level"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/hunting-pressure/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "pressure_level" in data["data"]
        assert data["data"]["pressure_level"] in ["extreme", "high", "moderate", "low", "minimal"]
        
    def test_hunting_pressure_quebec_behavioral_impact(self):
        """POST /api/bionic/geosuite/hunting-pressure/analyze - Behavioral impact"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/hunting-pressure/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "behavioral_impact" in data["data"]
        impact = data["data"]["behavioral_impact"]
        assert "overall" in impact
        assert "activity_reduction" in impact
        
    def test_hunting_pressure_quebec_optimal_timing(self):
        """POST /api/bionic/geosuite/hunting-pressure/analyze - Optimal timing"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/hunting-pressure/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "optimal_timing" in data["data"]
        assert isinstance(data["data"]["optimal_timing"], list)
        
    def test_hunting_pressure_usa_returns_200(self):
        """POST /api/bionic/geosuite/hunting-pressure/analyze - USA returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/hunting-pressure/analyze",
            json=USA_NY_COORDS
        )
        assert response.status_code == 200


class TestFullAnalysis:
    """Test full analysis endpoint with all engines"""
    
    def test_full_analysis_quebec_returns_200(self):
        """POST /api/bionic/geosuite/analyze/full - Quebec returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/analyze/full",
            json=QUEBEC_COORDS
        )
        assert response.status_code == 200
        
    def test_full_analysis_quebec_all_engines_executed(self):
        """POST /api/bionic/geosuite/analyze/full - All 5 engines executed"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/analyze/full",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        expected_engines = [
            "corridorEngine",
            "landcoverEngine",
            "nutritionEngine",
            "populationDensityEngine",
            "huntingPressureModule"
        ]
        
        for engine in expected_engines:
            assert engine in data["engines_executed"]
            
    def test_full_analysis_quebec_analyses_present(self):
        """POST /api/bionic/geosuite/analyze/full - All analyses present"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/analyze/full",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        expected_analyses = ["corridor", "landcover", "nutrition", "population", "pressure"]
        
        for analysis in expected_analyses:
            assert analysis in data["analyses"]
            
    def test_full_analysis_quebec_global_score(self):
        """POST /api/bionic/geosuite/analyze/full - Global score calculated"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/analyze/full",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "global_score" in data
        assert 0 <= data["global_score"] <= 100
        
    def test_full_analysis_quebec_recommendations(self):
        """POST /api/bionic/geosuite/analyze/full - Recommendations aggregated"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/analyze/full",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        
    def test_full_analysis_usa_returns_200(self):
        """POST /api/bionic/geosuite/analyze/full - USA returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/analyze/full",
            json=USA_NY_COORDS
        )
        assert response.status_code == 200


class TestMapStyles:
    """Test map style endpoints"""
    
    def test_map_styles_returns_200(self):
        """GET /api/bionic/geosuite/map/styles - Returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/map/styles")
        assert response.status_code == 200
        
    def test_map_styles_structure(self):
        """GET /api/bionic/geosuite/map/styles - Returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/map/styles")
        data = response.json()
        
        assert "styles" in data
        assert "default" in data
        assert data["default"] == "light"
        
    def test_map_styles_available(self):
        """GET /api/bionic/geosuite/map/styles - All styles available"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/map/styles")
        data = response.json()
        
        style_ids = [s["id"] for s in data["styles"]]
        expected_styles = ["light", "terrain", "hunting", "satellite", "dark"]
        
        for style in expected_styles:
            assert style in style_ids


class TestSpeciesPresets:
    """Test species preset endpoints"""
    
    def test_species_presets_returns_200(self):
        """GET /api/bionic/geosuite/map/species-presets - Returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/map/species-presets")
        assert response.status_code == 200
        
    def test_species_presets_all_species(self):
        """GET /api/bionic/geosuite/map/species-presets - All species present"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/map/species-presets")
        data = response.json()
        
        expected_species = ["deer", "moose", "bear", "turkey", "waterfowl", "smallgame"]
        
        for species in expected_species:
            assert species in data
            assert "name" in data[species]
            assert "icon" in data[species]
            assert "layers" in data[species]
            assert "description" in data[species]


class TestFusionCompatibility:
    """Test fusion compatibility with BehaviorFusionEngine P2"""
    
    def test_fusion_compatibility_returns_200(self):
        """GET /api/bionic/geosuite/fusion/compatibility - Returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/fusion/compatibility")
        assert response.status_code == 200
        
    def test_fusion_compatibility_structure(self):
        """GET /api/bionic/geosuite/fusion/compatibility - Returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/fusion/compatibility")
        data = response.json()
        
        assert data["compatible"] == True
        assert data["interface_version"] == "1.0.0"
        assert data["behavior_suite_hooks"] == True
        assert data["unified_output_format"] == True
        
    def test_fusion_compatibility_engines_ready(self):
        """GET /api/bionic/geosuite/fusion/compatibility - All engines ready"""
        response = requests.get(f"{BASE_URL}/api/bionic/geosuite/fusion/compatibility")
        data = response.json()
        
        expected_engines = ["corridor", "landcover", "nutrition", "population", "pressure"]
        
        for engine in expected_engines:
            assert engine in data["engines_ready"]


class TestMultiTerritory:
    """Test multi-territory support (Quebec, Canada, USA)"""
    
    def test_quebec_region_detection(self):
        """Quebec coordinates detected as quebec region"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        assert data["region"] == "quebec"
        
    def test_laurentides_region_detection(self):
        """Laurentides coordinates detected as quebec region"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=LAURENTIDES_COORDS
        )
        data = response.json()
        assert data["region"] == "quebec"
        
    def test_usa_region_detection(self):
        """USA coordinates detected as usa region"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=USA_NY_COORDS
        )
        data = response.json()
        assert data["region"] == "usa"
        
    def test_quebec_data_sources(self):
        """Quebec uses SIGÉOM/MFFP data sources"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/nutrition/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        # Quebec should use sigeom or mffp
        sources = data["data_sources_used"]
        quebec_sources = ["sigeom", "mffp", "canvec"]
        assert any(s in sources for s in quebec_sources)


class TestErrorHandling:
    """Test error handling for invalid inputs"""
    
    def test_invalid_coordinates_missing_lat(self):
        """Missing lat returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json={"lon": -71.2}
        )
        assert response.status_code == 422
        
    def test_invalid_coordinates_missing_lon(self):
        """Missing lon returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json={"lat": 46.8}
        )
        assert response.status_code == 422
        
    def test_invalid_coordinates_out_of_range_lat(self):
        """Out of range lat returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json={"lat": 200, "lon": -71.2}
        )
        assert response.status_code == 422
        
    def test_invalid_coordinates_out_of_range_lon(self):
        """Out of range lon returns 422"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json={"lat": 46.8, "lon": 500}
        )
        assert response.status_code == 422


class TestDataQuality:
    """Test data quality and confidence levels"""
    
    def test_corridor_confidence_level(self):
        """Corridor analysis returns confidence level"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
        
    def test_landcover_confidence_level(self):
        """Landcover analysis returns confidence level"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/landcover/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
        
    def test_data_sources_used_not_empty(self):
        """Data sources used is not empty"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/geosuite/corridor/analyze",
            json=QUEBEC_COORDS
        )
        data = response.json()
        
        assert "data_sources_used" in data
        assert len(data["data_sources_used"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
