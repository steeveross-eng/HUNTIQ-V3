"""
BIONIC™ Phase 3 - Étape 2: Standardized Output Format Tests
============================================================
Tests for validating that all 4 engines (Sentinel, SIGÉOM, Terrain, Pressure)
return data in the uniform standardized format with:
- metadata (engine_name, engine_version, analysis_id, confidence)
- location (lat, lon)
- overall_score (score, level, components, interpretation)
- data (engine-specific data)
- recommendations (list of strings)

Test coordinates: lat=47.5, lon=-72.5 (Quebec)
"""

import pytest
import requests
import os
import time

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates (Quebec)
TEST_LAT = 47.5
TEST_LON = -72.5


class TestStandardizedMetadata:
    """Test that all engines return proper metadata structure."""
    
    def test_sentinel_metadata_structure(self):
        """Sentinel engine should return standardized metadata."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check metadata exists
        assert "metadata" in data, "Missing 'metadata' field in Sentinel response"
        metadata = data["metadata"]
        
        # Validate required metadata fields
        assert "engine_name" in metadata, "Missing engine_name in metadata"
        assert metadata["engine_name"] == "SentinelEngine"
        
        assert "engine_version" in metadata, "Missing engine_version in metadata"
        assert metadata["engine_version"] == "2.0.0"
        
        assert "analysis_id" in metadata, "Missing analysis_id in metadata"
        assert metadata["analysis_id"].startswith("veg_"), f"analysis_id should start with 'veg_', got {metadata['analysis_id']}"
        
        assert "confidence" in metadata, "Missing confidence in metadata"
        assert 0 <= metadata["confidence"] <= 1, "confidence should be between 0 and 1"
        
        assert "confidence_level" in metadata, "Missing confidence_level in metadata"
        assert metadata["confidence_level"] in ["very_high", "high", "moderate", "low", "very_low"]
        
        assert "analyzed_at" in metadata, "Missing analyzed_at in metadata"
        assert "data_source" in metadata, "Missing data_source in metadata"
        assert "data_source_type" in metadata, "Missing data_source_type in metadata"
        assert "from_cache" in metadata, "Missing from_cache in metadata"
    
    def test_sigeom_metadata_structure(self):
        """SIGÉOM engine should return standardized metadata."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check metadata exists
        assert "metadata" in data, "Missing 'metadata' field in SIGÉOM response"
        metadata = data["metadata"]
        
        # Validate required metadata fields
        assert "engine_name" in metadata, "Missing engine_name in metadata"
        assert metadata["engine_name"] == "SigeomEngine"
        
        assert "engine_version" in metadata, "Missing engine_version in metadata"
        assert metadata["engine_version"] == "2.0.0"
        
        assert "analysis_id" in metadata, "Missing analysis_id in metadata"
        assert metadata["analysis_id"].startswith("geo_"), f"analysis_id should start with 'geo_', got {metadata['analysis_id']}"
        
        assert "confidence" in metadata, "Missing confidence in metadata"
        assert "confidence_level" in metadata, "Missing confidence_level in metadata"
    
    def test_terrain_metadata_structure(self):
        """Terrain engine should return standardized metadata."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check metadata exists
        assert "metadata" in data, "Missing 'metadata' field in Terrain response"
        metadata = data["metadata"]
        
        # Validate required metadata fields
        assert "engine_name" in metadata, "Missing engine_name in metadata"
        assert metadata["engine_name"] == "TerrainEngine"
        
        assert "engine_version" in metadata, "Missing engine_version in metadata"
        assert metadata["engine_version"] == "1.0.0"
        
        assert "analysis_id" in metadata, "Missing analysis_id in metadata"
        assert metadata["analysis_id"].startswith("ter_"), f"analysis_id should start with 'ter_', got {metadata['analysis_id']}"
        
        assert "confidence" in metadata, "Missing confidence in metadata"
        assert "confidence_level" in metadata, "Missing confidence_level in metadata"
    
    def test_pressure_metadata_structure(self):
        """Pressure engine should return standardized metadata."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check metadata exists
        assert "metadata" in data, "Missing 'metadata' field in Pressure response"
        metadata = data["metadata"]
        
        # Validate required metadata fields
        assert "engine_name" in metadata, "Missing engine_name in metadata"
        assert metadata["engine_name"] == "PressureEngine"
        
        assert "engine_version" in metadata, "Missing engine_version in metadata"
        assert metadata["engine_version"] == "1.0.0"
        
        assert "analysis_id" in metadata, "Missing analysis_id in metadata"
        assert metadata["analysis_id"].startswith("pre_"), f"analysis_id should start with 'pre_', got {metadata['analysis_id']}"
        
        assert "confidence" in metadata, "Missing confidence in metadata"
        assert "confidence_level" in metadata, "Missing confidence_level in metadata"


class TestStandardizedOverallScore:
    """Test that all engines return proper overall_score structure."""
    
    def test_sentinel_overall_score_structure(self):
        """Sentinel engine should return standardized overall_score."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check overall_score exists
        assert "overall_score" in data, "Missing 'overall_score' field in Sentinel response"
        score = data["overall_score"]
        
        # Validate required score fields
        assert "score" in score, "Missing score in overall_score"
        assert isinstance(score["score"], (int, float)), "score should be numeric"
        assert 0 <= score["score"] <= 100, "score should be between 0 and 100"
        
        assert "level" in score, "Missing level in overall_score"
        assert score["level"] in ["exceptional", "excellent", "good", "moderate", "low", "poor"]
        
        assert "components" in score, "Missing components in overall_score"
        assert isinstance(score["components"], dict), "components should be a dict"
        
        assert "interpretation" in score, "Missing interpretation in overall_score"
        assert isinstance(score["interpretation"], str), "interpretation should be a string"
    
    def test_sigeom_overall_score_structure(self):
        """SIGÉOM engine should return standardized overall_score."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check overall_score exists
        assert "overall_score" in data, "Missing 'overall_score' field in SIGÉOM response"
        score = data["overall_score"]
        
        # Validate required score fields
        assert "score" in score, "Missing score in overall_score"
        assert 0 <= score["score"] <= 100, "score should be between 0 and 100"
        
        assert "level" in score, "Missing level in overall_score"
        assert "components" in score, "Missing components in overall_score"
        assert "interpretation" in score, "Missing interpretation in overall_score"
    
    def test_terrain_overall_score_structure(self):
        """Terrain engine should return standardized overall_score."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check overall_score exists
        assert "overall_score" in data, "Missing 'overall_score' field in Terrain response"
        score = data["overall_score"]
        
        # Validate required score fields
        assert "score" in score, "Missing score in overall_score"
        assert 0 <= score["score"] <= 100, "score should be between 0 and 100"
        
        assert "level" in score, "Missing level in overall_score"
        assert "components" in score, "Missing components in overall_score"
    
    def test_pressure_overall_score_structure(self):
        """Pressure engine should return standardized overall_score."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check overall_score exists
        assert "overall_score" in data, "Missing 'overall_score' field in Pressure response"
        score = data["overall_score"]
        
        # Validate required score fields
        assert "score" in score, "Missing score in overall_score"
        assert 0 <= score["score"] <= 100, "score should be between 0 and 100"
        
        assert "level" in score, "Missing level in overall_score"
        assert "components" in score, "Missing components in overall_score"


class TestStandardizedLocation:
    """Test that all engines return proper location structure."""
    
    def test_sentinel_location_structure(self):
        """Sentinel engine should return standardized location."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check location exists
        assert "location" in data, "Missing 'location' field in Sentinel response"
        location = data["location"]
        
        assert "lat" in location, "Missing lat in location"
        assert "lon" in location, "Missing lon in location"
        assert location["lat"] == TEST_LAT, f"lat should be {TEST_LAT}"
        assert location["lon"] == TEST_LON, f"lon should be {TEST_LON}"
    
    def test_sigeom_location_structure(self):
        """SIGÉOM engine should return standardized location."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "location" in data, "Missing 'location' field in SIGÉOM response"
        location = data["location"]
        assert "lat" in location and "lon" in location
    
    def test_terrain_location_structure(self):
        """Terrain engine should return standardized location."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "location" in data, "Missing 'location' field in Terrain response"
        location = data["location"]
        assert "lat" in location and "lon" in location
    
    def test_pressure_location_structure(self):
        """Pressure engine should return standardized location."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "location" in data, "Missing 'location' field in Pressure response"
        location = data["location"]
        assert "lat" in location and "lon" in location


class TestStandardizedDataAndRecommendations:
    """Test that all engines return proper data and recommendations."""
    
    def test_sentinel_data_and_recommendations(self):
        """Sentinel engine should return data and recommendations."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check data exists
        assert "data" in data, "Missing 'data' field in Sentinel response"
        assert isinstance(data["data"], dict), "data should be a dict"
        
        # Check recommendations exists
        assert "recommendations" in data, "Missing 'recommendations' field in Sentinel response"
        assert isinstance(data["recommendations"], list), "recommendations should be a list"
    
    def test_sigeom_data_and_recommendations(self):
        """SIGÉOM engine should return data and recommendations."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data, "Missing 'data' field in SIGÉOM response"
        assert "recommendations" in data, "Missing 'recommendations' field in SIGÉOM response"
    
    def test_terrain_data_and_recommendations(self):
        """Terrain engine should return data and recommendations."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data, "Missing 'data' field in Terrain response"
        assert "recommendations" in data, "Missing 'recommendations' field in Terrain response"
    
    def test_pressure_data_and_recommendations(self):
        """Pressure engine should return data and recommendations."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data, "Missing 'data' field in Pressure response"
        assert "recommendations" in data, "Missing 'recommendations' field in Pressure response"


class TestConsolidatedEndpoint:
    """Test the consolidated /api/bionic/core/analyze/real endpoint."""
    
    def test_consolidated_endpoint_returns_all_modules(self):
        """Consolidated endpoint should return all 4 modules."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "target_species": "deer",
                "include_vegetation": True,
                "include_geology": True,
                "include_terrain": True,
                "include_pressure": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check modules exist
        assert "modules" in data, "Missing 'modules' field"
        modules = data["modules"]
        
        # All 4 modules should be present
        assert "vegetation" in modules, "Missing vegetation module"
        assert "geology" in modules, "Missing geology module"
        assert "terrain" in modules, "Missing terrain module"
        assert "pressure" in modules, "Missing pressure module"
    
    def test_consolidated_endpoint_global_score(self):
        """Consolidated endpoint should return global_score and module_scores."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "target_species": "deer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check global score
        assert "global_score" in data, "Missing global_score"
        assert isinstance(data["global_score"], (int, float)), "global_score should be numeric"
        assert 0 <= data["global_score"] <= 100, "global_score should be between 0 and 100"
        
        # Check global rating
        assert "global_rating" in data, "Missing global_rating"
        assert data["global_rating"] in ["exceptional", "excellent", "good", "moderate", "low", "poor"]
        
        # Check module_scores
        assert "module_scores" in data, "Missing module_scores"
        module_scores = data["module_scores"]
        assert isinstance(module_scores, dict), "module_scores should be a dict"
    
    def test_consolidated_endpoint_modules_have_standardized_format(self):
        """Each module in consolidated response should have standardized format."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "target_species": "deer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        modules = data["modules"]
        
        for module_name in ["vegetation", "geology", "terrain", "pressure"]:
            if module_name in modules:
                module = modules[module_name]
                
                # Each module should have standardized fields
                assert "metadata" in module, f"Missing metadata in {module_name} module"
                assert "location" in module, f"Missing location in {module_name} module"
                assert "overall_score" in module, f"Missing overall_score in {module_name} module"
                assert "data" in module, f"Missing data in {module_name} module"
                assert "recommendations" in module, f"Missing recommendations in {module_name} module"
    
    def test_consolidated_endpoint_recommendations(self):
        """Consolidated endpoint should return aggregated recommendations."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "target_species": "deer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendations" in data, "Missing recommendations"
        assert isinstance(data["recommendations"], list), "recommendations should be a list"
        # Should have recommendations from multiple modules
        assert len(data["recommendations"]) > 0, "Should have at least one recommendation"


class TestCacheFunctionality:
    """Test cache functionality with from_cache flag."""
    
    def test_sentinel_cache_second_call(self):
        """Second call to Sentinel should return from_cache=true."""
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response1.status_code == 200
        
        # Second call (should be cached)
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Check from_cache flag
        assert "from_cache" in data2, "Missing from_cache flag"
        assert data2["from_cache"] == True, "Second call should return from_cache=true"
    
    def test_sigeom_cache_second_call(self):
        """Second call to SIGÉOM should return from_cache=true."""
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response1.status_code == 200
        
        # Second call (should be cached)
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert "from_cache" in data2, "Missing from_cache flag"
        assert data2["from_cache"] == True, "Second call should return from_cache=true"
    
    def test_terrain_cache_second_call(self):
        """Second call to Terrain should return from_cache=true."""
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response1.status_code == 200
        
        # Second call (should be cached)
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert "from_cache" in data2, "Missing from_cache flag"
        assert data2["from_cache"] == True, "Second call should return from_cache=true"
    
    def test_pressure_cache_second_call(self):
        """Second call to Pressure should return from_cache=true."""
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response1.status_code == 200
        
        # Second call (should be cached)
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert "from_cache" in data2, "Missing from_cache flag"
        assert data2["from_cache"] == True, "Second call should return from_cache=true"
    
    def test_consolidated_cache_hit_rate(self):
        """Consolidated endpoint should report cache_hit_rate on second call."""
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response1.status_code == 200
        
        # Second call (should have cache hits)
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert "cache_hit_rate" in data2, "Missing cache_hit_rate"
        assert data2["cache_hit_rate"] == 1.0, f"Second call should have 100% cache hit rate, got {data2['cache_hit_rate']}"


class TestScoreLevelConsistency:
    """Test that score levels are consistent across all engines."""
    
    def test_score_level_mapping(self):
        """Score levels should follow the standard mapping."""
        # Test all 4 engines
        endpoints = [
            ("/api/bionic/sentinel/analyze/point", {"lat": TEST_LAT, "lon": TEST_LON}),
            ("/api/bionic/sigeom/analyze/point", {"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}),
            ("/api/bionic/terrain/analyze/point", {"lat": TEST_LAT, "lon": TEST_LON}),
            ("/api/bionic/pressure/analyze/point", {"lat": TEST_LAT, "lon": TEST_LON}),
        ]
        
        for endpoint, params in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
            assert response.status_code == 200
            data = response.json()
            
            score = data["overall_score"]["score"]
            level = data["overall_score"]["level"]
            
            # Verify level matches score
            if score >= 90:
                expected_level = "exceptional"
            elif score >= 80:
                expected_level = "excellent"
            elif score >= 60:
                expected_level = "good"
            elif score >= 40:
                expected_level = "moderate"
            elif score >= 20:
                expected_level = "low"
            else:
                expected_level = "poor"
            
            assert level == expected_level, f"Score {score} should have level '{expected_level}', got '{level}' for {endpoint}"


class TestDifferentSpecies:
    """Test that endpoints work with different target species."""
    
    def test_sigeom_different_species(self):
        """SIGÉOM should work with different species."""
        species_list = ["deer", "moose", "bear"]
        
        for species in species_list:
            response = requests.get(
                f"{BASE_URL}/api/bionic/sigeom/analyze/point",
                params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": species}
            )
            assert response.status_code == 200, f"Failed for species: {species}"
            data = response.json()
            
            # Should have target_species in response
            assert "target_species" in data, f"Missing target_species for {species}"
            assert data["target_species"] == species
    
    def test_consolidated_different_species(self):
        """Consolidated endpoint should work with different species."""
        species_list = ["deer", "moose", "bear"]
        
        for species in species_list:
            response = requests.get(
                f"{BASE_URL}/api/bionic/core/analyze/real",
                params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": species}
            )
            assert response.status_code == 200, f"Failed for species: {species}"
            data = response.json()
            
            assert "target_species" in data, f"Missing target_species for {species}"
            assert data["target_species"] == species


class TestSelectiveModules:
    """Test selective module execution in consolidated endpoint."""
    
    def test_vegetation_only(self):
        """Should be able to request only vegetation module."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "include_vegetation": True,
                "include_geology": False,
                "include_terrain": False,
                "include_pressure": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        modules = data["modules"]
        assert "vegetation" in modules, "Should have vegetation module"
        assert "geology" not in modules, "Should not have geology module"
        assert "terrain" not in modules, "Should not have terrain module"
        assert "pressure" not in modules, "Should not have pressure module"
    
    def test_geology_and_terrain_only(self):
        """Should be able to request only geology and terrain modules."""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "include_vegetation": False,
                "include_geology": True,
                "include_terrain": True,
                "include_pressure": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        modules = data["modules"]
        assert "vegetation" not in modules, "Should not have vegetation module"
        assert "geology" in modules, "Should have geology module"
        assert "terrain" in modules, "Should have terrain module"
        assert "pressure" not in modules, "Should not have pressure module"


# Fixtures
@pytest.fixture(scope="module")
def api_client():
    """Shared requests session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session
