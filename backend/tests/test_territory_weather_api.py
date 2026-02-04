"""
HUNTIQ V3 - Territory Page API Tests
Tests for Weather and Hunting Potential APIs
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fauna-analysis.preview.emergentagent.com')

# Test coordinates for Quebec City
TEST_LAT = 46.8139
TEST_LON = -71.2082


class TestWeatherAPI:
    """Tests for /api/geospatial/weather endpoints"""
    
    def test_weather_current_returns_200(self):
        """Test that current weather endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/weather/current",
            params={"lat": TEST_LAT, "lon": TEST_LON, "units": "metric"}
        )
        assert response.status_code == 200
        print(f"✅ Weather current endpoint returned 200")
    
    def test_weather_current_returns_valid_data(self):
        """Test that current weather returns valid data structure"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/weather/current",
            params={"lat": TEST_LAT, "lon": TEST_LON, "units": "metric"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check status
        assert data.get("status") == "success", f"Expected status 'success', got {data.get('status')}"
        
        # Check location
        assert "location" in data
        assert "name" in data["location"]
        print(f"✅ Location: {data['location']['name']}")
        
        # Check current weather
        assert "current" in data
        assert "temperature" in data["current"]
        assert "humidity" in data["current"]
        print(f"✅ Temperature: {data['current']['temperature']}°C")
        
        # Check weather condition
        assert "weather" in data
        assert "condition" in data["weather"]
        print(f"✅ Condition: {data['weather']['condition']}")
    
    def test_weather_hunting_score_present(self):
        """Test that hunting score is calculated and returned"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/weather/current",
            params={"lat": TEST_LAT, "lon": TEST_LON, "units": "metric"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check hunting score
        assert "hunting_score" in data
        score = data["hunting_score"]
        
        assert "score" in score
        assert isinstance(score["score"], (int, float))
        assert 0 <= score["score"] <= 100
        print(f"✅ Hunting score: {score['score']}/100")
        
        assert "level" in score
        assert score["level"] in ["excellent", "bon", "moyen", "faible", "mauvais"]
        print(f"✅ Score level: {score['level']}")
        
        assert "recommendation" in score
        print(f"✅ Recommendation: {score['recommendation'][:50]}...")
        
        assert "factors" in score
        assert len(score["factors"]) > 0
        print(f"✅ Factors count: {len(score['factors'])}")
    
    def test_weather_forecast_returns_200(self):
        """Test that forecast endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/weather/forecast",
            params={"lat": TEST_LAT, "lon": TEST_LON, "units": "metric"}
        )
        assert response.status_code == 200
        print(f"✅ Weather forecast endpoint returned 200")
    
    def test_weather_hunting_score_endpoint(self):
        """Test dedicated hunting score endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/weather/hunting-score",
            params={"lat": TEST_LAT, "lon": TEST_LON}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert "hunting_score" in data
        print(f"✅ Hunting score endpoint working")


class TestHuntingPotentialAPI:
    """Tests for /api/geospatial/potential endpoints"""
    
    def test_potential_calculate_returns_200(self):
        """Test that potential calculate endpoint returns 200"""
        payload = {
            "bbox": {
                "min_lat": TEST_LAT - 0.05,
                "max_lat": TEST_LAT + 0.05,
                "min_lon": TEST_LON - 0.05,
                "max_lon": TEST_LON + 0.05
            },
            "center_point": {
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            },
            "radius_m": 5000,
            "target_species": "deer",
            "season": "rut",
            "include_ai_predictions": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/geospatial/potential/calculate",
            json=payload
        )
        assert response.status_code == 200
        print(f"✅ Potential calculate endpoint returned 200")
    
    def test_potential_calculate_returns_valid_score(self):
        """Test that potential calculate returns valid score"""
        payload = {
            "bbox": {
                "min_lat": TEST_LAT - 0.05,
                "max_lat": TEST_LAT + 0.05,
                "min_lon": TEST_LON - 0.05,
                "max_lon": TEST_LON + 0.05
            },
            "center_point": {
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            },
            "radius_m": 5000,
            "target_species": "deer",
            "season": "rut"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/geospatial/potential/calculate",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check overall score
        assert "overall_score" in data
        assert isinstance(data["overall_score"], (int, float))
        assert 0 <= data["overall_score"] <= 100
        print(f"✅ Overall score: {data['overall_score']}/100")
        
        # Check level
        assert "level" in data
        assert data["level"] in ["excellent", "good", "moderate", "low", "poor"]
        print(f"✅ Level: {data['level']}")
        
        # Check recommendations
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        print(f"✅ Recommendations count: {len(data['recommendations'])}")
    
    def test_potential_calculate_returns_component_scores(self):
        """Test that potential calculate returns component scores"""
        payload = {
            "bbox": {
                "min_lat": TEST_LAT - 0.05,
                "max_lat": TEST_LAT + 0.05,
                "min_lon": TEST_LON - 0.05,
                "max_lon": TEST_LON + 0.05
            },
            "center_point": {
                "latitude": TEST_LAT,
                "longitude": TEST_LON
            },
            "target_species": "deer",
            "season": "rut"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/geospatial/potential/calculate",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check component scores
        assert "component_scores" in data
        components = data["component_scores"]
        
        # Check expected components
        expected_components = ["terrain", "water", "forest", "geology", "vegetation"]
        for comp in expected_components:
            assert comp in components, f"Missing component: {comp}"
            assert "score" in components[comp]
            assert "weight" in components[comp]
            print(f"✅ Component {comp}: score={components[comp]['score']}, weight={components[comp]['weight']}")
    
    def test_potential_components_endpoint(self):
        """Test potential components endpoint"""
        response = requests.get(f"{BASE_URL}/api/geospatial/potential/components")
        assert response.status_code == 200
        data = response.json()
        
        assert "components" in data
        assert len(data["components"]) >= 5
        
        # Check weights sum to 1.0
        total_weight = sum(c["weight"] for c in data["components"])
        assert abs(total_weight - 1.0) < 0.01, f"Weights sum to {total_weight}, expected 1.0"
        print(f"✅ Components count: {len(data['components'])}, total weight: {total_weight}")
    
    def test_potential_requires_center_point(self):
        """Test that potential calculate requires center_point field"""
        payload = {
            "bbox": {
                "min_lat": TEST_LAT - 0.05,
                "max_lat": TEST_LAT + 0.05,
                "min_lon": TEST_LON - 0.05,
                "max_lon": TEST_LON + 0.05
            },
            "target_species": "deer",
            "season": "rut"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/geospatial/potential/calculate",
            json=payload
        )
        # Should return 422 validation error without center_point
        assert response.status_code == 422
        print(f"✅ Correctly returns 422 when center_point is missing")


class TestGeospatialStatus:
    """Tests for geospatial status and data sources"""
    
    def test_geospatial_status(self):
        """Test geospatial status endpoint"""
        response = requests.get(f"{BASE_URL}/api/geospatial/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        print(f"✅ Geospatial status: {data['status']}")
    
    def test_data_sources(self):
        """Test data sources endpoint"""
        response = requests.get(f"{BASE_URL}/api/geospatial/data-sources")
        assert response.status_code == 200
        data = response.json()
        
        assert "sources" in data
        assert len(data["sources"]) >= 6
        
        # Check for Quebec government sources
        source_ids = [s["id"] for s in data["sources"]]
        assert "lidar_quebec" in source_ids
        assert "hydro_quebec" in source_ids
        print(f"✅ Data sources count: {len(data['sources'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
