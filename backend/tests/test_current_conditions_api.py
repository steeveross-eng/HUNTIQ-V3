"""
BIONIC™ Current Conditions API Tests
=====================================
Tests for the Current Conditions Panel endpoints:
- GET /api/bionic/conditions/current
- GET /api/bionic/conditions/lunar
- GET /api/bionic/conditions/export-data

Test coordinates: lat=47.5, lon=-72.5 (Québec)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCurrentConditionsEndpoint:
    """Tests for /api/bionic/conditions/current endpoint"""
    
    def test_current_conditions_returns_200(self):
        """Test that current conditions endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["request_id"].startswith("cond_")
    
    def test_current_conditions_location_data(self):
        """Test that location data is correctly returned"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "location" in data
        assert data["location"]["lat"] == 47.5
        assert data["location"]["lon"] == -72.5
    
    def test_current_conditions_lunar_data(self):
        """Test lunar data structure and values"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        lunar = data.get("lunar")
        assert lunar is not None
        
        # Required fields
        assert "phase_name" in lunar
        assert "illumination_percent" in lunar
        assert "is_waxing" in lunar
        assert "is_full_moon" in lunar
        assert "is_new_moon" in lunar
        assert "hunting_impact" in lunar
        assert "hunting_description" in lunar
        
        # Value validation
        assert 0 <= lunar["illumination_percent"] <= 100
        assert lunar["hunting_impact"] in ["favorable", "mixed", "neutral"]
    
    def test_current_conditions_pressure_data(self):
        """Test pressure data structure and values"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        pressure = data.get("pressure")
        assert pressure is not None
        
        # Required fields
        assert "value_hpa" in pressure
        assert "trend" in pressure
        assert "trend_icon" in pressure
        assert "change_6h" in pressure
        
        # Value validation
        assert 900 <= pressure["value_hpa"] <= 1100  # Reasonable pressure range
        assert pressure["trend"] in ["rising_fast", "rising", "stable", "falling", "falling_fast"]
        assert pressure["trend_icon"] in ["↑↑", "↑", "→", "↓", "↓↓"]
    
    def test_current_conditions_weather_data(self):
        """Test weather data structure"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        weather = data.get("weather")
        assert weather is not None
        
        # Required fields
        assert "temperature_c" in weather
        assert "humidity_percent" in weather
        assert "wind_speed_kmh" in weather
        assert "cloud_cover_percent" in weather
        assert "weather_description" in weather
        assert "weather_icon" in weather
        
        # Value validation
        assert -50 <= weather["temperature_c"] <= 50  # Reasonable temp range
        assert 0 <= weather["humidity_percent"] <= 100
        assert weather["wind_speed_kmh"] >= 0
    
    def test_current_conditions_photoperiod_data(self):
        """Test photoperiod data structure"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        photoperiod = data.get("photoperiod")
        assert photoperiod is not None
        
        # Required fields
        assert "sunrise" in photoperiod
        assert "sunset" in photoperiod
        assert "daylight_hours" in photoperiod
        assert "golden_hour_morning" in photoperiod
        assert "golden_hour_evening" in photoperiod
        
        # Value validation - time format HH:MM
        assert ":" in photoperiod["sunrise"]
        assert ":" in photoperiod["sunset"]
        assert 0 <= photoperiod["daylight_hours"] <= 24
    
    def test_current_conditions_hunting_impact(self):
        """Test hunting impact score structure"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        hunting_impact = data.get("hunting_impact")
        assert hunting_impact is not None
        
        # Required fields
        assert "score" in hunting_impact
        assert "level" in hunting_impact
        assert "icon" in hunting_impact
        assert "summary" in hunting_impact
        assert "factors" in hunting_impact
        
        # Value validation
        assert 0 <= hunting_impact["score"] <= 100
        assert hunting_impact["level"] in ["excellent", "good", "moderate", "poor"]
        assert hunting_impact["icon"] in ["🎯", "✅", "⚠️", "❌"]
    
    def test_current_conditions_cache_miss_then_hit(self):
        """Test cache functionality - first call miss, second call hit"""
        # First call with use_cache=false
        response1 = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5, "use_cache": "false"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["cache_status"] == "miss"
        
        # Second call with use_cache=true
        response2 = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5, "use_cache": "true"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["cache_status"] == "hit"
    
    def test_current_conditions_export_summary(self):
        """Test export summary is present"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "exportable" in data
        assert data["exportable"] is True
        assert "export_summary" in data
        assert len(data["export_summary"]) > 0
    
    def test_current_conditions_invalid_lat(self):
        """Test validation for invalid latitude"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 100, "lon": -72.5}  # Invalid lat > 90
        )
        assert response.status_code == 422
    
    def test_current_conditions_invalid_lon(self):
        """Test validation for invalid longitude"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -200}  # Invalid lon < -180
        )
        assert response.status_code == 422
    
    def test_current_conditions_missing_params(self):
        """Test validation for missing required params"""
        response = requests.get(f"{BASE_URL}/api/bionic/conditions/current")
        assert response.status_code == 422


class TestLunarEndpoint:
    """Tests for /api/bionic/conditions/lunar endpoint"""
    
    def test_lunar_returns_200(self):
        """Test that lunar endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/bionic/conditions/lunar")
        assert response.status_code == 200
    
    def test_lunar_data_structure(self):
        """Test lunar data structure"""
        response = requests.get(f"{BASE_URL}/api/bionic/conditions/lunar")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "phase" in data
        assert "illumination" in data
        assert "phase_name_fr" in data
        assert "is_waxing" in data
        assert "hunting_impact" in data
        
        # Value validation
        assert 0 <= data["phase"] <= 1
        assert 0 <= data["illumination"] <= 1


class TestExportDataEndpoint:
    """Tests for /api/bionic/conditions/export-data endpoint"""
    
    def test_export_data_returns_200(self):
        """Test that export-data endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/export-data",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
    
    def test_export_data_structure(self):
        """Test export data structure for PDF generation"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/export-data",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "title" in data
        assert "generated_at" in data
        assert "location" in data
        assert "sections" in data
        assert "hunting_score" in data
        assert "raw_summary" in data
        
        # Sections validation
        assert len(data["sections"]) == 4  # Lunar, Pressure, Weather, Photoperiod
        
        section_titles = [s["title"] for s in data["sections"]]
        assert "Phase Lunaire" in section_titles
        assert "Pression Barométrique" in section_titles
        assert "Météo" in section_titles
        assert "Photopériode" in section_titles
    
    def test_export_data_hunting_score(self):
        """Test hunting score in export data"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/export-data",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        hunting_score = data.get("hunting_score")
        assert hunting_score is not None
        assert "value" in hunting_score
        assert "level" in hunting_score
        assert "icon" in hunting_score
        assert "summary" in hunting_score
        
        assert 0 <= hunting_score["value"] <= 100
        assert hunting_score["level"] in ["excellent", "good", "moderate", "poor"]


class TestHuntingImpactScoring:
    """Tests for hunting impact score calculation"""
    
    def test_hunting_impact_score_range(self):
        """Test that hunting impact score is within 0-100"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        score = data["hunting_impact"]["score"]
        assert 0 <= score <= 100
    
    def test_hunting_impact_level_mapping(self):
        """Test that level correctly maps to score"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        score = data["hunting_impact"]["score"]
        level = data["hunting_impact"]["level"]
        
        # Verify level matches score range
        if score >= 75:
            assert level == "excellent"
        elif score >= 55:
            assert level == "good"
        elif score >= 35:
            assert level == "moderate"
        else:
            assert level == "poor"
    
    def test_hunting_impact_factors_present(self):
        """Test that all impact factors are present"""
        response = requests.get(
            f"{BASE_URL}/api/bionic/conditions/current",
            params={"lat": 47.5, "lon": -72.5}
        )
        assert response.status_code == 200
        data = response.json()
        
        factors = data["hunting_impact"]["factors"]
        assert "lunar" in factors
        assert "pressure" in factors
        assert "weather" in factors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
