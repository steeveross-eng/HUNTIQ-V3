"""
BIONIC™ Stats & WMS Proxy API Tests
====================================
Tests for:
- GET /api/bionic/stats - MongoDB aggregated statistics
- GET /api/stats - Frontend stats with thresholds
- GET /api/wms-proxy/status - WMS sources health status
- POST /api/wms-proxy/reset-circuit-breaker - Reset circuit breakers
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBionicStats:
    """Tests for /api/bionic/stats endpoint - MongoDB aggregated statistics"""
    
    def test_bionic_stats_returns_200(self):
        """GET /api/bionic/stats should return 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/bionic/stats returns 200")
    
    def test_bionic_stats_structure(self):
        """GET /api/bionic/stats should return correct structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        # Required fields
        required_fields = [
            "total_analyses",
            "total_species_models",
            "total_zones_generated",
            "total_waypoints",
            "total_favorites",
            "average_global_score",
            "top_species_frequency",
            "modules_usage",
            "rating_distribution",
            "engine_version",
            "last_update"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✅ /api/bionic/stats has all required fields")
    
    def test_bionic_stats_data_types(self):
        """GET /api/bionic/stats should return correct data types"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        # Integer fields
        assert isinstance(data["total_analyses"], int), "total_analyses should be int"
        assert isinstance(data["total_species_models"], int), "total_species_models should be int"
        assert isinstance(data["total_zones_generated"], int), "total_zones_generated should be int"
        assert isinstance(data["total_waypoints"], int), "total_waypoints should be int"
        assert isinstance(data["total_favorites"], int), "total_favorites should be int"
        
        # Float field
        assert isinstance(data["average_global_score"], (int, float)), "average_global_score should be numeric"
        
        # Dict fields
        assert isinstance(data["top_species_frequency"], dict), "top_species_frequency should be dict"
        assert isinstance(data["modules_usage"], dict), "modules_usage should be dict"
        assert isinstance(data["rating_distribution"], dict), "rating_distribution should be dict"
        
        # String fields
        assert isinstance(data["engine_version"], str), "engine_version should be string"
        assert "BIONIC_CORE" in data["engine_version"], "engine_version should contain BIONIC_CORE"
        
        print(f"✅ /api/bionic/stats data types are correct")
    
    def test_bionic_stats_values_reasonable(self):
        """GET /api/bionic/stats should return reasonable values"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        data = response.json()
        
        # Values should be non-negative
        assert data["total_analyses"] >= 0, "total_analyses should be >= 0"
        assert data["total_species_models"] >= 0, "total_species_models should be >= 0"
        assert data["average_global_score"] >= 0, "average_global_score should be >= 0"
        assert data["average_global_score"] <= 100, "average_global_score should be <= 100"
        
        print(f"✅ /api/bionic/stats values are reasonable")


class TestFrontendStats:
    """Tests for /api/stats endpoint - Frontend stats with thresholds"""
    
    def test_stats_returns_200(self):
        """GET /api/stats should return 200"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/stats returns 200")
    
    def test_stats_structure(self):
        """GET /api/stats should return correct structure"""
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        
        required_fields = [
            "subscribers",
            "zones",
            "territories",
            "activeUsers",
            "attractants",
            "satisfaction",
            "totalProducts",
            "lastUpdated"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✅ /api/stats has all required fields")
    
    def test_stats_threshold_values(self):
        """GET /api/stats should return threshold values when DB is empty"""
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        
        # These are the threshold values defined in stats_router.py
        expected_thresholds = {
            "subscribers": 20017,
            "zones": 2901,
            "territories": 2547,
            "activeUsers": 1247,
            "attractants": 850,
            "satisfaction": 98
        }
        
        for key, expected in expected_thresholds.items():
            actual = data.get(key)
            assert actual is not None, f"Missing {key}"
            assert actual >= expected, f"{key} should be >= {expected}, got {actual}"
        
        print(f"✅ /api/stats returns threshold values correctly")
    
    def test_stats_data_types(self):
        """GET /api/stats should return correct data types"""
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        
        assert isinstance(data["subscribers"], int), "subscribers should be int"
        assert isinstance(data["zones"], int), "zones should be int"
        assert isinstance(data["territories"], int), "territories should be int"
        assert isinstance(data["activeUsers"], int), "activeUsers should be int"
        assert isinstance(data["attractants"], int), "attractants should be int"
        assert isinstance(data["satisfaction"], int), "satisfaction should be int"
        assert isinstance(data["lastUpdated"], str), "lastUpdated should be string"
        
        print(f"✅ /api/stats data types are correct")


class TestWMSProxyStatus:
    """Tests for /api/wms-proxy/status endpoint - WMS sources health"""
    
    def test_wms_status_returns_200(self):
        """GET /api/wms-proxy/status should return 200"""
        response = requests.get(f"{BASE_URL}/api/wms-proxy/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/wms-proxy/status returns 200")
    
    def test_wms_status_structure(self):
        """GET /api/wms-proxy/status should return correct structure"""
        response = requests.get(f"{BASE_URL}/api/wms-proxy/status")
        data = response.json()
        
        required_fields = ["allowed_hosts", "cache_size", "max_cache_size", "sources"]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✅ /api/wms-proxy/status has all required fields")
    
    def test_wms_status_allowed_hosts(self):
        """GET /api/wms-proxy/status should list allowed WMS hosts"""
        response = requests.get(f"{BASE_URL}/api/wms-proxy/status")
        data = response.json()
        
        allowed_hosts = data.get("allowed_hosts", [])
        assert isinstance(allowed_hosts, list), "allowed_hosts should be a list"
        assert len(allowed_hosts) > 0, "allowed_hosts should not be empty"
        
        # Check for expected Quebec government hosts
        expected_hosts = [
            "servicescarto.mern.gouv.qc.ca",
            "servicescarto.mffp.gouv.qc.ca"
        ]
        
        for host in expected_hosts:
            assert host in allowed_hosts, f"Expected host {host} in allowed_hosts"
        
        print(f"✅ /api/wms-proxy/status lists {len(allowed_hosts)} allowed hosts")
    
    def test_wms_status_sources_structure(self):
        """GET /api/wms-proxy/status sources should have correct structure"""
        response = requests.get(f"{BASE_URL}/api/wms-proxy/status")
        data = response.json()
        
        sources = data.get("sources", {})
        assert isinstance(sources, dict), "sources should be a dict"
        
        # Each source should have these fields
        for host, source_data in sources.items():
            assert "available" in source_data, f"Missing 'available' for {host}"
            assert "recent_errors_count" in source_data, f"Missing 'recent_errors_count' for {host}"
            assert "marked_unavailable" in source_data, f"Missing 'marked_unavailable' for {host}"
            assert isinstance(source_data["available"], bool), f"'available' should be bool for {host}"
        
        print(f"✅ /api/wms-proxy/status sources have correct structure")
    
    def test_wms_status_cache_config(self):
        """GET /api/wms-proxy/status should return cache configuration"""
        response = requests.get(f"{BASE_URL}/api/wms-proxy/status")
        data = response.json()
        
        assert isinstance(data["cache_size"], int), "cache_size should be int"
        assert isinstance(data["max_cache_size"], int), "max_cache_size should be int"
        assert data["cache_size"] >= 0, "cache_size should be >= 0"
        assert data["max_cache_size"] > 0, "max_cache_size should be > 0"
        
        print(f"✅ /api/wms-proxy/status cache config: {data['cache_size']}/{data['max_cache_size']}")


class TestWMSProxyCircuitBreaker:
    """Tests for /api/wms-proxy/reset-circuit-breaker endpoint"""
    
    def test_reset_all_circuit_breakers(self):
        """POST /api/wms-proxy/reset-circuit-breaker should reset all breakers"""
        response = requests.post(f"{BASE_URL}/api/wms-proxy/reset-circuit-breaker")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert "message" in data, "Response should have message"
        
        print(f"✅ POST /api/wms-proxy/reset-circuit-breaker resets all breakers")
    
    def test_reset_specific_host_circuit_breaker(self):
        """POST /api/wms-proxy/reset-circuit-breaker?host=xxx should reset specific host"""
        host = "servicescarto.mern.gouv.qc.ca"
        response = requests.post(f"{BASE_URL}/api/wms-proxy/reset-circuit-breaker?host={host}")
        
        # Should return 200 whether host exists or not
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "success" in data, "Response should have success field"
        assert "message" in data, "Response should have message"
        
        print(f"✅ POST /api/wms-proxy/reset-circuit-breaker?host={host} works")
    
    def test_reset_unknown_host(self):
        """POST /api/wms-proxy/reset-circuit-breaker?host=unknown should handle gracefully"""
        response = requests.post(f"{BASE_URL}/api/wms-proxy/reset-circuit-breaker?host=unknown.host.com")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Should return success=False for unknown host
        assert "success" in data, "Response should have success field"
        
        print(f"✅ POST /api/wms-proxy/reset-circuit-breaker handles unknown host gracefully")


class TestStatsLiveEndpoint:
    """Tests for /api/stats/live endpoint - Real-time stats"""
    
    def test_live_stats_returns_200(self):
        """GET /api/stats/live should return 200"""
        response = requests.get(f"{BASE_URL}/api/stats/live")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/stats/live returns 200")
    
    def test_live_stats_structure(self):
        """GET /api/stats/live should return correct structure"""
        response = requests.get(f"{BASE_URL}/api/stats/live")
        data = response.json()
        
        required_fields = ["activeUsers", "todaySales", "activeZones", "alertsToday", "timestamp"]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"✅ /api/stats/live has all required fields")


class TestStatsThresholdsEndpoint:
    """Tests for /api/stats/thresholds endpoint - Admin/debug"""
    
    def test_thresholds_returns_200(self):
        """GET /api/stats/thresholds should return 200"""
        response = requests.get(f"{BASE_URL}/api/stats/thresholds")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ /api/stats/thresholds returns 200")
    
    def test_thresholds_structure(self):
        """GET /api/stats/thresholds should return threshold values"""
        response = requests.get(f"{BASE_URL}/api/stats/thresholds")
        data = response.json()
        
        assert "thresholds" in data, "Response should have thresholds"
        assert "description" in data, "Response should have description"
        
        thresholds = data["thresholds"]
        expected_keys = ["subscribers", "zones", "territories", "activeUsers", "attractants", "satisfaction"]
        
        for key in expected_keys:
            assert key in thresholds, f"Missing threshold: {key}"
        
        print(f"✅ /api/stats/thresholds returns all threshold values")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
