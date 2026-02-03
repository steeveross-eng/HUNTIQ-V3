"""
HUNTIQ V3 - BIONIC™ Geospatial Engine API Tests
Tests for all geospatial endpoints using real Quebec government data sources
"""

import pytest
import requests
import os

# Get BASE_URL from environment - DO NOT add default
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test bounding box for Laurentides region (recommended test coordinates)
TEST_BBOX = {
    "min_lat": 46.0,
    "max_lat": 46.5,
    "min_lon": -74.5,
    "max_lon": -74.0
}


class TestGeospatialStatus:
    """Tests for geospatial engine status endpoint"""
    
    def test_geospatial_status_returns_200(self):
        """Test /api/geospatial/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/geospatial/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/status returned 200")
    
    def test_geospatial_status_is_operational(self):
        """Test that engine status is operational"""
        response = requests.get(f"{BASE_URL}/api/geospatial/status")
        data = response.json()
        
        assert data.get("status") == "operational", f"Expected 'operational', got {data.get('status')}"
        assert data.get("architecture_ready") == True, "Architecture should be ready"
        assert data.get("implementation_status") == "active", "Implementation should be active"
        print(f"✅ Geospatial engine is operational")
    
    def test_geospatial_status_has_data_sources(self):
        """Test that status includes data sources"""
        response = requests.get(f"{BASE_URL}/api/geospatial/status")
        data = response.json()
        
        assert "data_sources" in data, "Response should include data_sources"
        data_sources = data["data_sources"]
        
        # Check for expected data sources
        expected_sources = ["lidar_quebec", "sigeom", "hydro_quebec", "forest_mffp", "sentinel_2", "osm"]
        for source in expected_sources:
            assert source in data_sources, f"Missing data source: {source}"
        
        print(f"✅ All {len(expected_sources)} expected data sources present")
    
    def test_geospatial_status_has_modules(self):
        """Test that status includes modules"""
        response = requests.get(f"{BASE_URL}/api/geospatial/status")
        data = response.json()
        
        assert "modules" in data, "Response should include modules"
        modules = data["modules"]
        
        # Check for expected modules
        expected_modules = ["lidar", "sentinel", "sigeom", "hydro", "forest", "potential"]
        for module in expected_modules:
            assert module in modules, f"Missing module: {module}"
        
        print(f"✅ All {len(expected_modules)} expected modules present")


class TestDataSources:
    """Tests for data sources listing endpoint"""
    
    def test_data_sources_returns_200(self):
        """Test /api/geospatial/data-sources returns 200"""
        response = requests.get(f"{BASE_URL}/api/geospatial/data-sources")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/data-sources returned 200")
    
    def test_data_sources_returns_8_sources(self):
        """Test that 8 data sources are returned"""
        response = requests.get(f"{BASE_URL}/api/geospatial/data-sources")
        data = response.json()
        
        assert "sources" in data, "Response should include 'sources' key"
        sources = data["sources"]
        
        assert len(sources) == 8, f"Expected 8 sources, got {len(sources)}"
        print(f"✅ Returned {len(sources)} data sources")
    
    def test_data_sources_all_free(self):
        """Test that all data sources are free"""
        response = requests.get(f"{BASE_URL}/api/geospatial/data-sources")
        data = response.json()
        sources = data["sources"]
        
        for source in sources:
            assert source.get("free") == True, f"Source {source.get('id')} should be free"
        
        print(f"✅ All {len(sources)} data sources are free")
    
    def test_data_sources_have_required_fields(self):
        """Test that each source has required fields"""
        response = requests.get(f"{BASE_URL}/api/geospatial/data-sources")
        data = response.json()
        sources = data["sources"]
        
        required_fields = ["id", "name", "provider", "url", "license", "free", "api_type"]
        
        for source in sources:
            for field in required_fields:
                assert field in source, f"Source {source.get('id')} missing field: {field}"
        
        print(f"✅ All sources have required fields")
    
    def test_data_sources_include_quebec_sources(self):
        """Test that Quebec government sources are included"""
        response = requests.get(f"{BASE_URL}/api/geospatial/data-sources")
        data = response.json()
        sources = data["sources"]
        
        source_ids = [s["id"] for s in sources]
        
        quebec_sources = ["lidar_quebec", "sigeom", "hydro_quebec", "mne_quebec", "mffp_forest"]
        for qs in quebec_sources:
            assert qs in source_ids, f"Missing Quebec source: {qs}"
        
        print(f"✅ All Quebec government sources present")


class TestHuntingPotentialCalculation:
    """Tests for hunting potential calculation endpoint"""
    
    def test_potential_calculate_returns_200(self):
        """Test /api/geospatial/potential/calculate returns 200"""
        payload = {
            "bbox": TEST_BBOX,
            "target_species": "deer",
            "season": "rut"
        }
        response = requests.post(f"{BASE_URL}/api/geospatial/potential/calculate", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/potential/calculate returned 200")
    
    def test_potential_calculate_returns_score(self):
        """Test that calculation returns a valid score"""
        payload = {
            "bbox": TEST_BBOX,
            "target_species": "deer",
            "season": "rut"
        }
        response = requests.post(f"{BASE_URL}/api/geospatial/potential/calculate", json=payload)
        data = response.json()
        
        assert "overall_score" in data, "Response should include overall_score"
        score = data["overall_score"]
        assert 0 <= score <= 100, f"Score should be 0-100, got {score}"
        print(f"✅ Hunting potential score: {score}")
    
    def test_potential_calculate_returns_level(self):
        """Test that calculation returns a level"""
        payload = {
            "bbox": TEST_BBOX,
            "target_species": "deer",
            "season": "rut"
        }
        response = requests.post(f"{BASE_URL}/api/geospatial/potential/calculate", json=payload)
        data = response.json()
        
        assert "level" in data, "Response should include level"
        valid_levels = ["excellent", "good", "moderate", "low", "poor"]
        assert data["level"] in valid_levels, f"Invalid level: {data['level']}"
        print(f"✅ Hunting potential level: {data['level']}")
    
    def test_potential_calculate_returns_components(self):
        """Test that calculation returns component scores"""
        payload = {
            "bbox": TEST_BBOX,
            "target_species": "deer",
            "season": "rut"
        }
        response = requests.post(f"{BASE_URL}/api/geospatial/potential/calculate", json=payload)
        data = response.json()
        
        assert "component_scores" in data, "Response should include component_scores"
        components = data["component_scores"]
        
        expected_components = ["terrain", "water", "forest", "geology", "vegetation"]
        for comp in expected_components:
            assert comp in components, f"Missing component: {comp}"
        
        print(f"✅ All {len(expected_components)} component scores present")
    
    def test_potential_calculate_returns_recommendations(self):
        """Test that calculation returns recommendations"""
        payload = {
            "bbox": TEST_BBOX,
            "target_species": "deer",
            "season": "rut"
        }
        response = requests.post(f"{BASE_URL}/api/geospatial/potential/calculate", json=payload)
        data = response.json()
        
        assert "recommendations" in data, "Response should include recommendations"
        assert isinstance(data["recommendations"], list), "Recommendations should be a list"
        print(f"✅ Returned {len(data['recommendations'])} recommendations")


class TestHydroRivers:
    """Tests for hydrology rivers endpoint"""
    
    def test_hydro_rivers_returns_200(self):
        """Test /api/geospatial/hydro/rivers returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"],
            "buffer_m": 100
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/hydro/rivers", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/hydro/rivers returned 200")
    
    def test_hydro_rivers_returns_tile_url(self):
        """Test that rivers endpoint returns tile URL"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/hydro/rivers", params=params)
        data = response.json()
        
        assert "tile_url" in data, "Response should include tile_url"
        assert data["tile_url"].startswith("http"), "tile_url should be a valid URL"
        print(f"✅ Rivers tile URL returned")
    
    def test_hydro_rivers_returns_data_source(self):
        """Test that rivers endpoint returns data source info"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/hydro/rivers", params=params)
        data = response.json()
        
        assert "data_source" in data, "Response should include data_source"
        assert "GRHQ" in data["data_source"], "Data source should be GRHQ"
        print(f"✅ Data source: {data['data_source']}")


class TestForestSpecies:
    """Tests for forest species endpoint"""
    
    def test_forest_species_returns_200(self):
        """Test /api/geospatial/forest/species returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/forest/species", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/forest/species returned 200")
    
    def test_forest_species_returns_common_species(self):
        """Test that forest species endpoint returns common species"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/forest/species", params=params)
        data = response.json()
        
        assert "common_species" in data, "Response should include common_species"
        species = data["common_species"]
        
        # Check for expected Quebec tree species codes
        expected_species = ["EPN", "SAB", "BOP"]  # Épinette noire, Sapin baumier, Bouleau
        for sp in expected_species:
            assert sp in species, f"Missing species: {sp}"
        
        print(f"✅ Returned {len(species)} common species")
    
    def test_forest_species_includes_hunting_value(self):
        """Test that species include hunting value info"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/forest/species", params=params)
        data = response.json()
        
        species = data["common_species"]
        for code, info in species.items():
            assert "hunting_value" in info, f"Species {code} missing hunting_value"
        
        print(f"✅ All species include hunting value")


class TestLidarEndpoints:
    """Tests for LiDAR data endpoints"""
    
    def test_lidar_coverage_returns_200(self):
        """Test /api/geospatial/lidar/coverage returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/lidar/coverage", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/lidar/coverage returned 200")
    
    def test_lidar_query_returns_200(self):
        """Test /api/geospatial/lidar/query returns 200"""
        payload = {
            "bbox": TEST_BBOX,
            "include_dtm": True,
            "include_dsm": True,
            "include_chm": False
        }
        response = requests.post(f"{BASE_URL}/api/geospatial/lidar/query", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/lidar/query returned 200")
    
    def test_lidar_query_returns_tile_urls(self):
        """Test that LiDAR query returns tile URLs"""
        payload = {
            "bbox": TEST_BBOX,
            "include_dtm": True,
            "include_dsm": True
        }
        response = requests.post(f"{BASE_URL}/api/geospatial/lidar/query", json=payload)
        data = response.json()
        
        assert "dtm_url" in data, "Response should include dtm_url"
        assert "dsm_url" in data, "Response should include dsm_url"
        print(f"✅ LiDAR tile URLs returned")


class TestSigeomEndpoints:
    """Tests for SIGÉOM geological data endpoints"""
    
    def test_sigeom_bedrock_returns_200(self):
        """Test /api/geospatial/sigeom/bedrock returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/sigeom/bedrock", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/sigeom/bedrock returned 200")
    
    def test_sigeom_surficial_returns_200(self):
        """Test /api/geospatial/sigeom/surficial returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/sigeom/surficial", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/sigeom/surficial returned 200")


class TestPotentialComponents:
    """Tests for hunting potential components endpoint"""
    
    def test_potential_components_returns_200(self):
        """Test /api/geospatial/potential/components returns 200"""
        response = requests.get(f"{BASE_URL}/api/geospatial/potential/components")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/potential/components returned 200")
    
    def test_potential_components_returns_7_components(self):
        """Test that 7 scoring components are returned"""
        response = requests.get(f"{BASE_URL}/api/geospatial/potential/components")
        data = response.json()
        
        assert "components" in data, "Response should include components"
        components = data["components"]
        
        assert len(components) == 7, f"Expected 7 components, got {len(components)}"
        print(f"✅ Returned {len(components)} scoring components")
    
    def test_potential_components_have_weights(self):
        """Test that all components have weights"""
        response = requests.get(f"{BASE_URL}/api/geospatial/potential/components")
        data = response.json()
        components = data["components"]
        
        total_weight = 0
        for comp in components:
            assert "weight" in comp, f"Component {comp.get('name')} missing weight"
            total_weight += comp["weight"]
        
        # Weights should sum to 1.0
        assert abs(total_weight - 1.0) < 0.01, f"Weights should sum to 1.0, got {total_weight}"
        print(f"✅ All components have weights (total: {total_weight})")


class TestSentinelEndpoints:
    """Tests for Sentinel-2 satellite imagery endpoints"""
    
    def test_sentinel_scenes_returns_200(self):
        """Test /api/geospatial/sentinel/scenes returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"],
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "cloud_max": 20.0
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/sentinel/scenes", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/sentinel/scenes returned 200")


class TestGeomorphEndpoints:
    """Tests for geomorphology analysis endpoints"""
    
    def test_geomorph_slope_returns_200(self):
        """Test /api/geospatial/geomorph/slope returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/geomorph/slope", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/geomorph/slope returned 200")
    
    def test_geomorph_features_returns_200(self):
        """Test /api/geospatial/geomorph/features returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"]
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/geomorph/features", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/geomorph/features returned 200")


class TestAIEndpoints:
    """Tests for AI prediction endpoints"""
    
    def test_ai_corridors_returns_200(self):
        """Test /api/geospatial/ai/corridors returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"],
            "species": "deer",
            "season": "rut"
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/ai/corridors", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/ai/corridors returned 200")
    
    def test_ai_bedding_zones_returns_200(self):
        """Test /api/geospatial/ai/bedding-zones returns 200"""
        params = {
            "min_lat": TEST_BBOX["min_lat"],
            "max_lat": TEST_BBOX["max_lat"],
            "min_lon": TEST_BBOX["min_lon"],
            "max_lon": TEST_BBOX["max_lon"],
            "species": "deer"
        }
        response = requests.get(f"{BASE_URL}/api/geospatial/ai/bedding-zones", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/geospatial/ai/bedding-zones returned 200")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
