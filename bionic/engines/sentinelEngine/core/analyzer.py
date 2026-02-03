"""
BIONIC™ Sentinel Engine - Vegetation Analyzer

Analyse de la végétation pour les territoires de chasse.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx

from .indices import vegetation_indices

logger = logging.getLogger(__name__)


# Sentinel Hub WMS endpoints (free tier with limited access)
SENTINEL_SOURCES = {
    "copernicus": {
        "name": "Copernicus Open Access Hub",
        "wms_url": "https://services.sentinel-hub.com/ogc/wms",
        "requires_key": True,
        "layers": {
            "true_color": "TRUE-COLOR-S2L2A",
            "ndvi": "NDVI",
            "moisture": "MOISTURE-INDEX",
            "scene_classification": "SCENE-CLASSIFICATION"
        }
    },
    "nasa_gibs": {
        "name": "NASA GIBS (MODIS)",
        "wms_url": "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi",
        "requires_key": False,
        "layers": {
            "modis_ndvi": "MODIS_Terra_NDVI_8Day",
            "modis_evi": "MODIS_Terra_EVI_8Day",
            "modis_lai": "MODIS_Terra_Leaf_Area_Index_8Day"
        }
    }
}


class SentinelAnalyzer:
    """
    Analyseur de données Sentinel-2 pour l'évaluation de territoires de chasse.
    
    Utilise les indices de végétation pour:
    - Identifier les zones de couvert (cover)
    - Détecter les lisières forêt/clairière
    - Évaluer la densité de végétation
    - Identifier les sources d'eau
    """
    
    # Season-specific NDVI expectations for Quebec
    SEASONAL_NDVI = {
        "spring": {"min": 0.2, "max": 0.5, "months": [4, 5]},
        "summer": {"min": 0.5, "max": 0.8, "months": [6, 7, 8]},
        "fall": {"min": 0.3, "max": 0.6, "months": [9, 10]},
        "winter": {"min": -0.1, "max": 0.2, "months": [11, 12, 1, 2, 3]}
    }
    
    # Habitat types based on vegetation indices
    HABITAT_TYPES = {
        "wetland": {
            "ndvi_range": (0.2, 0.5),
            "ndwi_range": (0.0, 0.5),
            "species": ["moose", "waterfowl", "bear"]
        },
        "dense_forest": {
            "ndvi_range": (0.6, 1.0),
            "ndwi_range": (-0.5, 0.0),
            "species": ["moose", "deer", "bear", "smallgame"]
        },
        "mixed_forest": {
            "ndvi_range": (0.4, 0.6),
            "ndwi_range": (-0.3, 0.1),
            "species": ["deer", "moose", "turkey", "bear"]
        },
        "forest_edge": {
            "ndvi_range": (0.3, 0.5),
            "ndwi_range": (-0.2, 0.1),
            "species": ["deer", "turkey", "smallgame"]
        },
        "open_field": {
            "ndvi_range": (0.1, 0.3),
            "ndwi_range": (-0.3, 0.0),
            "species": ["turkey", "waterfowl"]
        },
        "water": {
            "ndvi_range": (-1.0, 0.1),
            "ndwi_range": (0.3, 1.0),
            "species": ["waterfowl", "moose"]
        }
    }
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.sources = SENTINEL_SOURCES
        self.indices = vegetation_indices
    
    def analyze_point(
        self,
        lat: float,
        lon: float,
        bands: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze vegetation at a specific point.
        
        If band values are not provided, returns estimated values
        based on typical Quebec forest conditions.
        """
        # Use provided bands or estimate from typical values
        if bands is None:
            # Typical Quebec mixed forest values (summer)
            bands = {
                "B02": 0.05,   # Blue
                "B03": 0.08,   # Green
                "B04": 0.06,   # Red
                "B08": 0.35,   # NIR
                "B11": 0.15,   # SWIR1
                "B12": 0.10    # SWIR2
            }
        
        # Calculate all indices
        indices_result = self.indices.calculate_all_indices(bands)
        
        # Determine habitat type
        ndvi = indices_result.get("indices", {}).get("ndvi", {}).get("value", 0.5)
        ndwi = indices_result.get("indices", {}).get("ndwi", {}).get("value", -0.1)
        habitat = self._classify_habitat(ndvi, ndwi)
        
        # Get season context
        current_month = datetime.now().month
        season = self._get_season(current_month)
        seasonal_context = self._get_seasonal_context(ndvi, season)
        
        return {
            "location": {"lat": lat, "lon": lon},
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "indices": indices_result.get("indices", {}),
            "hunting_score": indices_result.get("hunting_score", {}),
            "habitat": habitat,
            "season": season,
            "seasonal_context": seasonal_context,
            "recommendations": self._generate_recommendations(habitat, ndvi, season)
        }
    
    def analyze_territory(
        self,
        bbox: Dict[str, float],
        target_species: str = "deer"
    ) -> Dict[str, Any]:
        """
        Analyze vegetation across a territory bounding box.
        """
        # Calculate area
        lat_diff = bbox["max_lat"] - bbox["min_lat"]
        lon_diff = bbox["max_lon"] - bbox["min_lon"]
        area_km2 = lat_diff * 111 * lon_diff * 75  # Approximate at 47° latitude
        
        # Sample center point for now (full implementation would sample grid)
        center_lat = (bbox["min_lat"] + bbox["max_lat"]) / 2
        center_lon = (bbox["min_lon"] + bbox["max_lon"]) / 2
        
        # Analyze center point
        point_analysis = self.analyze_point(center_lat, center_lon)
        
        # Generate territory-wide insights
        return {
            "analysis_id": f"sentinel_territory_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "bbox": bbox,
            "area_km2": round(area_km2, 2),
            "center": {"lat": center_lat, "lon": center_lon},
            "target_species": target_species,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "vegetation_analysis": point_analysis,
            "wms_layers": self._get_available_layers(),
            "species_suitability": self._assess_species_suitability(
                point_analysis["habitat"], 
                target_species
            ),
            "recommendations": point_analysis.get("recommendations", [])
        }
    
    def get_wms_tile_url(
        self,
        source: str,
        layer: str,
        bbox: Dict[str, float],
        width: int = 512,
        height: int = 512
    ) -> Optional[str]:
        """
        Get WMS tile URL for vegetation layer.
        """
        source_config = self.sources.get(source)
        if not source_config:
            return None
        
        layer_name = source_config["layers"].get(layer)
        if not layer_name:
            return None
        
        # Build WMS URL
        bbox_str = f"{bbox['min_lon']},{bbox['min_lat']},{bbox['max_lon']},{bbox['max_lat']}"
        
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": layer_name,
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": str(width),
            "height": str(height),
            "crs": "EPSG:4326",
            "bbox": bbox_str
        }
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{source_config['wms_url']}?{query}"
    
    def _classify_habitat(self, ndvi: float, ndwi: float) -> Dict[str, Any]:
        """Classify habitat type based on vegetation indices."""
        best_match = None
        best_score = -1
        
        for habitat_type, criteria in self.HABITAT_TYPES.items():
            ndvi_min, ndvi_max = criteria["ndvi_range"]
            ndwi_min, ndwi_max = criteria["ndwi_range"]
            
            # Check if values fall within range
            ndvi_match = ndvi_min <= ndvi <= ndvi_max
            ndwi_match = ndwi_min <= ndwi <= ndwi_max
            
            if ndvi_match and ndwi_match:
                # Calculate match score
                ndvi_center = (ndvi_min + ndvi_max) / 2
                ndwi_center = (ndwi_min + ndwi_max) / 2
                score = 1 - (abs(ndvi - ndvi_center) + abs(ndwi - ndwi_center)) / 2
                
                if score > best_score:
                    best_score = score
                    best_match = habitat_type
        
        if not best_match:
            # Default classification based on NDVI alone
            if ndvi < 0:
                best_match = "water"
            elif ndvi < 0.3:
                best_match = "open_field"
            elif ndvi < 0.5:
                best_match = "forest_edge"
            elif ndvi < 0.7:
                best_match = "mixed_forest"
            else:
                best_match = "dense_forest"
        
        habitat_info = self.HABITAT_TYPES.get(best_match, {})
        
        return {
            "type": best_match,
            "display_name": self._get_habitat_display_name(best_match),
            "confidence": round(max(0.5, best_score) * 100, 1) if best_score > 0 else 70,
            "suitable_species": habitat_info.get("species", []),
            "description": self._get_habitat_description(best_match)
        }
    
    def _get_habitat_display_name(self, habitat_type: str) -> str:
        """Get French display name for habitat type."""
        names = {
            "wetland": "Milieu humide",
            "dense_forest": "Forêt dense",
            "mixed_forest": "Forêt mixte",
            "forest_edge": "Lisière forestière",
            "open_field": "Terrain ouvert",
            "water": "Plan d'eau"
        }
        return names.get(habitat_type, habitat_type)
    
    def _get_habitat_description(self, habitat_type: str) -> str:
        """Get description for habitat type."""
        descriptions = {
            "wetland": "Zone humide avec végétation aquatique - Habitat privilégié pour orignal et sauvagine",
            "dense_forest": "Forêt mature à couvert dense - Excellent pour l'affût et le pistage",
            "mixed_forest": "Mélange de conifères et feuillus - Habitat diversifié, riche en nourriture",
            "forest_edge": "Transition forêt/clairière - Zone de haute activité pour cervidés",
            "open_field": "Terrain dégagé avec peu de couvert - Bonne visibilité",
            "water": "Surface d'eau - Point d'attraction pour la faune"
        }
        return descriptions.get(habitat_type, "Habitat non classifié")
    
    def _get_season(self, month: int) -> str:
        """Determine current season from month."""
        for season, config in self.SEASONAL_NDVI.items():
            if month in config["months"]:
                return season
        return "summer"
    
    def _get_seasonal_context(self, ndvi: float, season: str) -> Dict[str, Any]:
        """Get seasonal context for vegetation analysis."""
        seasonal_config = self.SEASONAL_NDVI.get(season, self.SEASONAL_NDVI["summer"])
        expected_min = seasonal_config["min"]
        expected_max = seasonal_config["max"]
        
        if ndvi < expected_min:
            status = "below_normal"
            note = "Végétation moins dense que la normale saisonnière"
        elif ndvi > expected_max:
            status = "above_normal"
            note = "Végétation plus dense que la normale saisonnière"
        else:
            status = "normal"
            note = "Végétation dans la normale saisonnière"
        
        return {
            "season": season,
            "status": status,
            "expected_ndvi_range": [expected_min, expected_max],
            "actual_ndvi": ndvi,
            "note": note
        }
    
    def _assess_species_suitability(
        self,
        habitat: Dict[str, Any],
        target_species: str
    ) -> Dict[str, Any]:
        """Assess habitat suitability for target species."""
        suitable_species = habitat.get("suitable_species", [])
        
        if target_species.lower() in [s.lower() for s in suitable_species]:
            suitability = "excellent"
            score = 85 + (len(suitable_species) * 3)
        elif any(s in target_species.lower() for s in ["deer", "cerf"]) and "deer" in suitable_species:
            suitability = "excellent"
            score = 90
        else:
            suitability = "modéré"
            score = 50
        
        return {
            "species": target_species,
            "suitability": suitability,
            "score": min(100, score),
            "habitat_type": habitat.get("type"),
            "note": f"Ce type d'habitat ({habitat.get('display_name')}) est {'idéal' if suitability == 'excellent' else 'acceptable'} pour {target_species}"
        }
    
    def _get_available_layers(self) -> List[Dict[str, Any]]:
        """Get list of available WMS layers."""
        layers = []
        for source_id, source_config in self.sources.items():
            for layer_key, layer_name in source_config["layers"].items():
                layers.append({
                    "source": source_id,
                    "key": layer_key,
                    "name": layer_name,
                    "requires_key": source_config.get("requires_key", False),
                    "provider": source_config["name"]
                })
        return layers
    
    def _generate_recommendations(
        self,
        habitat: Dict[str, Any],
        ndvi: float,
        season: str
    ) -> List[str]:
        """Generate hunting recommendations based on analysis."""
        recommendations = []
        habitat_type = habitat.get("type", "")
        
        # Habitat-specific recommendations
        if habitat_type == "forest_edge":
            recommendations.append(
                "Zone de lisière idéale - Installez-vous face à la lisière tôt le matin"
            )
        elif habitat_type == "dense_forest":
            recommendations.append(
                "Forêt dense - Privilégiez l'approche lente et le pistage"
            )
        elif habitat_type == "wetland":
            recommendations.append(
                "Milieu humide - Excellent pour l'orignal, vérifiez les traces de passage"
            )
        elif habitat_type == "mixed_forest":
            recommendations.append(
                "Forêt mixte - Recherchez les zones de nourriture (glands, bourgeons)"
            )
        
        # Season-specific recommendations
        season_tips = {
            "spring": "Au printemps, les animaux cherchent les nouvelles pousses",
            "summer": "En été, concentrez-vous près des sources d'eau",
            "fall": "À l'automne, les cervidés sont actifs pendant le rut",
            "winter": "En hiver, recherchez les ravages et aires d'hivernage"
        }
        if season in season_tips:
            recommendations.append(season_tips[season])
        
        # NDVI-based tip
        if ndvi > 0.6:
            recommendations.append(
                "Végétation dense - Utilisez des appelants pour attirer le gibier"
            )
        elif ndvi < 0.3:
            recommendations.append(
                "Terrain ouvert - Bonne visibilité, camouflage essentiel"
            )
        
        return recommendations


# Singleton instance
sentinel_analyzer = SentinelAnalyzer()
