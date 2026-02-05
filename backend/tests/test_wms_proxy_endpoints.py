"""
BIONIC™ WMS Proxy Endpoints Test Suite
Tests for WMS proxy functionality including:
- GET /api/geospatial/wms/sources
- GET /api/geospatial/wms/maplibre-config
- GET /api/geospatial/wms/tile/{source}/{layer}
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Quebec region bbox for testing
QUEBEC_BBOX = "-7983694,5792092,-7827151,5948635"


class TestWMSSourcesEndpoint:
    """Tests for GET /api/geospatial/wms/sources"""
    
    def test_wms_sources_returns_200(self):
        """Test that WMS sources endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources")
        assert response.status_code == 200
        
    def test_wms_sources_returns_available_sources(self):
        """Test that WMS sources returns list of available sources"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "success"
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0
        
    def test_wms_sources_contains_osm(self):
        """Test that OSM source is available"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources")
        data = response.json()
        
        source_ids = [s["id"] for s in data["sources"]]
        assert "osm" in source_ids
        
    def test_wms_sources_contains_canvec(self):
        """Test that CanVec source is available"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources")
        data = response.json()
        
        source_ids = [s["id"] for s in data["sources"]]
        assert "canvec" in source_ids
        
    def test_wms_sources_contains_usgs(self):
        """Test that USGS source is available"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources")
        data = response.json()
        
        source_ids = [s["id"] for s in data["sources"]]
        assert "usgs" in source_ids
        
    def test_wms_sources_structure(self):
        """Test that each source has required fields"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources")
        data = response.json()
        
        for source in data["sources"]:
            assert "id" in source
            assert "name" in source
            assert "layers" in source
            assert "status" in source
            assert isinstance(source["layers"], list)
            
    def test_wms_sources_excludes_unavailable_by_default(self):
        """Test that unavailable sources are excluded by default"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources")
        data = response.json()
        
        # Quebec government sources should be excluded (unavailable)
        source_ids = [s["id"] for s in data["sources"]]
        assert "sigeom" not in source_ids  # Requires auth
        assert "lidar" not in source_ids   # Requires auth
        assert "grhq" not in source_ids    # Requires auth
        
    def test_wms_sources_include_unavailable_param(self):
        """Test that include_unavailable=true shows all sources"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/sources?include_unavailable=true")
        data = response.json()
        
        source_ids = [s["id"] for s in data["sources"]]
        # Should now include unavailable sources
        assert "sigeom" in source_ids or "lidar" in source_ids or "grhq" in source_ids


class TestWMSMaplibreConfigEndpoint:
    """Tests for GET /api/geospatial/wms/maplibre-config"""
    
    def test_maplibre_config_returns_200(self):
        """Test that maplibre-config endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/maplibre-config")
        assert response.status_code == 200
        
    def test_maplibre_config_structure(self):
        """Test that maplibre-config returns proper structure"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/maplibre-config")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "success"
        assert "sources" in data
        assert "layers" in data
        assert isinstance(data["sources"], dict)
        assert isinstance(data["layers"], list)
        
    def test_maplibre_config_sources_format(self):
        """Test that sources have correct MapLibre format"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/maplibre-config")
        data = response.json()
        
        for source_key, source_config in data["sources"].items():
            assert "type" in source_config
            assert source_config["type"] == "raster"
            assert "tiles" in source_config
            assert "tileSize" in source_config
            assert source_config["tileSize"] == 256
            
    def test_maplibre_config_layers_format(self):
        """Test that layers have correct MapLibre format"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/maplibre-config")
        data = response.json()
        
        for layer in data["layers"]:
            assert "id" in layer
            assert "type" in layer
            assert layer["type"] == "raster"
            assert "source" in layer
            assert "paint" in layer
            assert "layout" in layer
            assert "metadata" in layer
            
    def test_maplibre_config_contains_osm_layer(self):
        """Test that OSM layer is included"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/maplibre-config")
        data = response.json()
        
        layer_ids = [l["id"] for l in data["layers"]]
        assert "wms-osm-osm" in layer_ids
        
    def test_maplibre_config_contains_canvec_hydro(self):
        """Test that CanVec hydro layer is included"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/maplibre-config")
        data = response.json()
        
        layer_ids = [l["id"] for l in data["layers"]]
        assert "wms-canvec-hydro" in layer_ids


class TestWMSTileEndpoint:
    """Tests for GET /api/geospatial/wms/tile/{source}/{layer}"""
    
    def test_canvec_hydro_tile_returns_200(self):
        """Test that CanVec hydro tile returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/canvec/hydro",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        assert response.status_code == 200
        
    def test_canvec_hydro_tile_returns_png(self):
        """Test that CanVec hydro tile returns PNG image"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/canvec/hydro",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "image/png" in content_type
        
        # Check PNG magic bytes
        assert response.content[:8] == b'\x89PNG\r\n\x1a\n'
        
    def test_canvec_hydro_tile_has_data(self):
        """Test that CanVec hydro tile has actual image data"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/canvec/hydro",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        
        # Should have reasonable size (not empty)
        assert len(response.content) > 100
        
    def test_osm_tile_returns_200(self):
        """Test that OSM tile returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/osm/osm",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        assert response.status_code == 200
        
    def test_osm_tile_returns_png(self):
        """Test that OSM tile returns PNG image"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/osm/osm",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "image/png" in content_type
        
        # Check PNG magic bytes
        assert response.content[:8] == b'\x89PNG\r\n\x1a\n'
        
    def test_usgs_topo_tile_returns_200(self):
        """Test that USGS topo tile returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/usgs/topo",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        assert response.status_code == 200
        
    def test_invalid_source_returns_error(self):
        """Test that invalid source returns error"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/invalid_source/layer",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        # Should return 400 or 404
        assert response.status_code in [400, 404, 502]
        
    def test_invalid_layer_returns_error(self):
        """Test that invalid layer returns error"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/osm/invalid_layer",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        # Should return 400 or 404
        assert response.status_code in [400, 404, 502]
        
    def test_tile_cache_headers(self):
        """Test that tile response has cache headers"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/canvec/hydro",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        
        # Should have cache control header
        assert "cache-control" in response.headers or "Cache-Control" in response.headers
        
    def test_tile_wms_source_header(self):
        """Test that tile response has WMS source header"""
        response = requests.get(
            f"{BASE_URL}/api/geospatial/wms/tile/canvec/hydro",
            params={"bbox": QUEBEC_BBOX, "width": 256, "height": 256}
        )
        
        # Should have X-WMS-Source header
        assert "x-wms-source" in response.headers or "X-WMS-Source" in response.headers


class TestWMSSourceInfoEndpoint:
    """Tests for GET /api/geospatial/wms/source/{source_id}"""
    
    def test_source_info_osm(self):
        """Test getting OSM source info"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/source/osm")
        assert response.status_code == 200
        
        data = response.json()
        assert data["source_id"] == "osm"
        assert "name" in data
        assert "layers" in data
        assert "base_url" in data
        
    def test_source_info_canvec(self):
        """Test getting CanVec source info"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/source/canvec")
        assert response.status_code == 200
        
        data = response.json()
        assert data["source_id"] == "canvec"
        assert "hydro" in data["layers"]
        
    def test_source_info_invalid(self):
        """Test getting invalid source info returns 404"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/source/invalid_source")
        assert response.status_code == 404


class TestWMSTileURLTemplate:
    """Tests for GET /api/geospatial/wms/tile-url/{source_id}/{layer}"""
    
    def test_tile_url_template_osm(self):
        """Test getting OSM tile URL template"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/tile-url/osm/osm")
        assert response.status_code == 200
        
        data = response.json()
        assert "tile_url_template" in data
        assert "{bbox-epsg-3857}" in data["tile_url_template"]
        
    def test_tile_url_template_canvec(self):
        """Test getting CanVec tile URL template"""
        response = requests.get(f"{BASE_URL}/api/geospatial/wms/tile-url/canvec/hydro")
        assert response.status_code == 200
        
        data = response.json()
        assert "tile_url_template" in data


class TestWMSCacheClear:
    """Tests for POST /api/geospatial/wms/cache/clear"""
    
    def test_cache_clear_all(self):
        """Test clearing all WMS cache"""
        response = requests.post(f"{BASE_URL}/api/geospatial/wms/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "cleared" in data
        
    def test_cache_clear_specific_source(self):
        """Test clearing cache for specific source"""
        response = requests.post(
            f"{BASE_URL}/api/geospatial/wms/cache/clear",
            params={"source_id": "osm"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
