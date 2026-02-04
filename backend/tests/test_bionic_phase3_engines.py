"""
BIONIC™ Phase 3 - Engine Tests
==============================
Tests for Phase 3 implementation:
- Sentinel Engine (vegetation analysis with cache)
- SIGÉOM Engine (geology analysis with cache)
- Terrain Engine (NEW - terrain/slope/aspect analysis)
- Pressure Engine (NEW - human pressure analysis)
- Core Engine consolidated endpoint (/api/bionic/core/analyze/real)
- Multi-level cache verification (L1: RAM, L2: disk)

Version: Phase 3
"""

import pytest
import requests
import os
import time

# Base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates (Quebec City area)
TEST_LAT = 46.8
TEST_LON = -71.2

# Remote area coordinates (for pressure testing)
REMOTE_LAT = 50.5
REMOTE_LON = -74.0


class TestSentinelEngine:
    """Tests for Sentinel Engine - Vegetation Analysis"""
    
    def test_sentinel_status(self):
        """Test Sentinel Engine status endpoint"""
        response = requests.get(f"{BASE_URL}/api/bionic/sentinel/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "active"
        assert data["engine"] == "SentinelEngine"
        assert "capabilities" in data
        assert "ndvi_calculation" in data["capabilities"]
        assert "NDVI" in data["supported_indices"]
    
    def test_sentinel_analyze_point(self):
        """Test Sentinel point analysis endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify location
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        
        # Verify indices
        assert "indices" in data
        assert "ndvi" in data["indices"]
        assert "ndwi" in data["indices"]
        assert "evi" in data["indices"]
        assert "savi" in data["indices"]
        
        # Verify hunting score
        assert "hunting_score" in data
        assert "score" in data["hunting_score"]
        assert 0 <= data["hunting_score"]["score"] <= 100
        
        # Verify habitat classification
        assert "habitat" in data
        assert "type" in data["habitat"]
        
        # Verify recommendations
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_sentinel_cache_functionality(self):
        """Test that cache works - second call should be faster"""
        # Use unique coordinates to ensure fresh cache
        unique_lat = 47.123
        unique_lon = -70.456
        
        # First call - should not be cached
        start1 = time.time()
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon}
        )
        time1 = time.time() - start1
        
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second call - should be cached
        start2 = time.time()
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/sentinel/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon}
        )
        time2 = time.time() - start2
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Verify cache hit
        assert data2.get("from_cache") == True
        
        # Second call should be significantly faster (at least 2x)
        # Note: Network latency may affect this, so we check from_cache flag primarily
        print(f"First call: {time1:.3f}s, Second call: {time2:.3f}s")


class TestSigeomEngine:
    """Tests for SIGÉOM Engine - Geology Analysis"""
    
    def test_sigeom_status(self):
        """Test SIGÉOM Engine status endpoint"""
        response = requests.get(f"{BASE_URL}/api/bionic/sigeom/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "active"
        assert data["engine"] == "SigeomEngine"
        assert "capabilities" in data
        assert "layers" in data
        assert "bedrock" in data["layers"]
    
    def test_sigeom_analyze_point(self):
        """Test SIGÉOM point analysis endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON, "target_species": "deer"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify location
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        
        # Verify geological province
        assert "geological_province" in data
        assert "code" in data["geological_province"]
        assert "name" in data["geological_province"]
        
        # Verify surficial deposit
        assert "surficial_deposit" in data
        assert "code" in data["surficial_deposit"]
        assert "name" in data["surficial_deposit"]
        
        # Verify bedrock
        assert "bedrock" in data
        
        # Verify hunting relevance
        assert "hunting_relevance" in data
        
        # Verify overall score
        assert "overall_score" in data
        assert "score" in data["overall_score"]
        assert 0 <= data["overall_score"]["score"] <= 100
        
        # Verify recommendations
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_sigeom_cache_functionality(self):
        """Test SIGÉOM cache functionality"""
        unique_lat = 47.234
        unique_lon = -70.567
        
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon, "target_species": "moose"}
        )
        assert response1.status_code == 200
        
        # Second call - should be cached
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/sigeom/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon, "target_species": "moose"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data2.get("from_cache") == True


class TestTerrainEngine:
    """Tests for NEW Terrain Engine - Terrain/Slope/Aspect Analysis"""
    
    def test_terrain_status(self):
        """Test Terrain Engine status endpoint"""
        response = requests.get(f"{BASE_URL}/api/bionic/terrain/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "operational"
        assert data["engine"] == "TerrainEngine"
        assert data["version"] == "1.0.0"
        assert "cache_stats" in data
    
    def test_terrain_analyze_point(self):
        """Test Terrain point analysis endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify location
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        
        # Verify metrics
        assert "metrics" in data
        metrics = data["metrics"]
        assert "elevation_m" in metrics
        assert "slope_degrees" in metrics
        assert "slope_percent" in metrics
        assert "aspect" in metrics
        assert "aspect_degrees" in metrics
        assert "tpi" in metrics
        assert "tpi_class" in metrics
        
        # Verify slope analysis
        assert "slope_analysis" in data
        assert "difficulty_level" in data["slope_analysis"]
        assert "mobility_score" in data["slope_analysis"]
        
        # Verify aspect analysis
        assert "aspect_analysis" in data
        assert "thermal_quality" in data["aspect_analysis"]
        assert "hunting_score" in data["aspect_analysis"]
        
        # Verify TPI analysis
        assert "tpi_analysis" in data
        assert "position_class" in data["tpi_analysis"]
        
        # Verify hunting assessment
        assert "hunting_assessment" in data
        assert "overall_score" in data["hunting_assessment"]
        
        # Verify overall score
        assert "overall_score" in data
        assert "score" in data["overall_score"]
        assert 0 <= data["overall_score"]["score"] <= 100
        
        # Verify recommendations
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_terrain_cache_functionality(self):
        """Test Terrain cache functionality"""
        unique_lat = 47.345
        unique_lon = -70.678
        
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second call - should be cached
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data2.get("from_cache") == True
        # Verify same timestamp (cached data)
        assert data1["analyzed_at"] == data2["analyzed_at"]


class TestPressureEngine:
    """Tests for NEW Pressure Engine - Human Pressure Analysis"""
    
    def test_pressure_status(self):
        """Test Pressure Engine status endpoint"""
        response = requests.get(f"{BASE_URL}/api/bionic/pressure/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "operational"
        assert data["engine"] == "PressureEngine"
        assert data["version"] == "1.0.0"
        assert "cache_stats" in data
    
    def test_pressure_analyze_point_urban(self):
        """Test Pressure analysis for urban area (Quebec City)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verify location
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        
        # Verify OSM features
        assert "osm_features" in data
        assert "roads_count" in data["osm_features"]
        assert "buildings_count" in data["osm_features"]
        
        # Verify pressure metrics
        assert "pressure_metrics" in data
        assert "pressure_index" in data["pressure_metrics"]
        assert "hunting_suitability" in data["pressure_metrics"]
        
        # Verify road analysis
        assert "road_analysis" in data
        assert "density_per_km2" in data["road_analysis"]
        
        # Verify building analysis
        assert "building_analysis" in data
        assert "density_per_km2" in data["building_analysis"]
        
        # Verify remoteness
        assert "remoteness" in data
        assert "score" in data["remoteness"]
        assert "level" in data["remoteness"]
        
        # Verify hunting impact
        assert "hunting_impact" in data
        assert "success_factor" in data["hunting_impact"]
        
        # Verify overall score
        assert "overall_score" in data
        assert "score" in data["overall_score"]
        
        # Verify recommendations
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_pressure_analyze_point_remote(self):
        """Test Pressure analysis for remote area (Northern Quebec)"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": REMOTE_LAT, "lon": REMOTE_LON}
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Remote area should have higher remoteness score
        remoteness_score = data["remoteness"]["score"]
        assert remoteness_score > 50, f"Remote area should have high remoteness score, got {remoteness_score}"
        
        # Remote area should have better hunting suitability
        hunting_suitability = data["pressure_metrics"]["hunting_suitability"]
        # Note: This may vary based on the model, but remote areas should generally be better
        print(f"Remote area hunting suitability: {hunting_suitability}")
    
    def test_pressure_cache_functionality(self):
        """Test Pressure cache functionality"""
        unique_lat = 47.456
        unique_lon = -70.789
        
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon}
        )
        assert response1.status_code == 200
        
        # Second call - should be cached
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/pressure/analyze/point",
            params={"lat": unique_lat, "lon": unique_lon}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data2.get("from_cache") == True


class TestCoreConsolidatedEndpoint:
    """Tests for Phase 3 Consolidated Endpoint - /api/bionic/core/analyze/real"""
    
    def test_core_analyze_real_all_modules(self):
        """Test consolidated endpoint with all modules enabled"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "target_species": "deer",
                "include_vegetation": True,
                "include_geology": True,
                "include_terrain": True,
                "include_pressure": True,
                "use_cache": True
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify location
        assert data["location"]["lat"] == TEST_LAT
        assert data["location"]["lon"] == TEST_LON
        assert data["target_species"] == "deer"
        
        # Verify all 4 modules present
        assert "modules" in data
        assert "vegetation" in data["modules"]
        assert "geology" in data["modules"]
        assert "terrain" in data["modules"]
        assert "pressure" in data["modules"]
        
        # Verify no errors in modules
        for module_name, module_data in data["modules"].items():
            assert "error" not in module_data, f"Module {module_name} has error: {module_data.get('error')}"
        
        # Verify global score
        assert "global_score" in data
        assert 0 <= data["global_score"] <= 100
        
        # Verify global rating
        assert "global_rating" in data
        assert data["global_rating"] in ["exceptional", "excellent", "good", "moderate", "low", "poor"]
        
        # Verify modules analyzed count
        assert data["modules_analyzed"] == 4
        
        # Verify cache hit rate
        assert "cache_hit_rate" in data
        assert 0 <= data["cache_hit_rate"] <= 1
        
        # Verify processing time
        assert "processing_time_ms" in data
        
        # Verify recommendations
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_core_analyze_real_selective_modules(self):
        """Test consolidated endpoint with selective modules"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "target_species": "moose",
                "include_vegetation": True,
                "include_geology": False,
                "include_terrain": True,
                "include_pressure": False,
                "use_cache": True
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify only selected modules present
        assert "vegetation" in data["modules"]
        assert "terrain" in data["modules"]
        assert "geology" not in data["modules"]
        assert "pressure" not in data["modules"]
        
        # Verify modules analyzed count
        assert data["modules_analyzed"] == 2
    
    def test_core_analyze_real_cache_performance(self):
        """Test that consolidated endpoint uses cache effectively"""
        unique_lat = 47.567
        unique_lon = -70.890
        
        # First call - may have cache misses
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": unique_lat,
                "lon": unique_lon,
                "target_species": "bear",
                "use_cache": True
            }
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second call - should have high cache hit rate
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/core/analyze/real",
            params={
                "lat": unique_lat,
                "lon": unique_lon,
                "target_species": "bear",
                "use_cache": True
            }
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Second call should have 100% cache hit rate
        assert data2["cache_hit_rate"] == 1.0
        
        # All modules should be cached
        assert len(data2["cached_modules"]) == 4
        
        # Processing time should be very low for cached response
        assert data2["processing_time_ms"] < 100, f"Cached response took {data2['processing_time_ms']}ms"
    
    def test_core_analyze_real_different_species(self):
        """Test consolidated endpoint with different target species"""
        species_list = ["deer", "moose", "bear"]
        
        for species in species_list:
            response = requests.get(
                f"{BASE_URL}/api/bionic/core/analyze/real",
                params={
                    "lat": TEST_LAT,
                    "lon": TEST_LON,
                    "target_species": species,
                    "use_cache": True
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["target_species"] == species
            assert "global_score" in data


class TestCacheSystem:
    """Tests for multi-level cache system (L1: RAM, L2: disk)"""
    
    def test_cache_stats_available(self):
        """Test that cache stats are available in status endpoints"""
        # Terrain engine
        response = requests.get(f"{BASE_URL}/api/bionic/terrain/status")
        assert response.status_code == 200
        data = response.json()
        assert "cache_stats" in data
        assert "hits" in data["cache_stats"]
        assert "misses" in data["cache_stats"]
        assert "hit_rate" in data["cache_stats"]
        
        # Pressure engine
        response = requests.get(f"{BASE_URL}/api/bionic/pressure/status")
        assert response.status_code == 200
        data = response.json()
        assert "cache_stats" in data
    
    def test_cache_hit_rate_increases(self):
        """Test that cache hit rate increases with repeated calls"""
        unique_lat = 47.678
        unique_lon = -70.901
        
        # Make multiple calls to same location
        for i in range(3):
            response = requests.get(
                f"{BASE_URL}/api/bionic/terrain/analyze/point",
                params={"lat": unique_lat, "lon": unique_lon}
            )
            assert response.status_code == 200
        
        # Check status for cache stats
        response = requests.get(f"{BASE_URL}/api/bionic/terrain/status")
        data = response.json()
        
        # Hit rate should be positive after multiple calls
        assert data["cache_stats"]["hits"] > 0


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates"""
        # Latitude out of range
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": 100, "lon": -71.2}
        )
        assert response.status_code == 422  # Validation error
        
        # Longitude out of range
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": 46.8, "lon": 200}
        )
        assert response.status_code == 422
    
    def test_missing_parameters(self):
        """Test handling of missing required parameters"""
        # Missing lat
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lon": -71.2}
        )
        assert response.status_code == 422
        
        # Missing lon
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": 46.8}
        )
        assert response.status_code == 422
    
    def test_extreme_coordinates(self):
        """Test handling of extreme but valid coordinates"""
        # Far north Quebec
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": 55.0, "lon": -77.0}
        )
        assert response.status_code == 200
        
        # Southern Quebec
        response = requests.get(
            f"{BASE_URL}/api/bionic/terrain/analyze/point",
            params={"lat": 45.0, "lon": -73.0}
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
