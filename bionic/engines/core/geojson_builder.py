"""
BIONIC™ Engine - GeoJSON Builder
=================================
Construction des objets GeoJSON pour la visualisation cartographique.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .helpers import get_rating


def build_point_geojson(
    lat: float,
    lon: float,
    score: float,
    module: str,
    properties: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Construit un GeoJSON Point Feature.
    
    Args:
        lat: Latitude
        lon: Longitude
        score: Score associé au point
        module: Nom du module source
        properties: Propriétés additionnelles
        
    Returns:
        Dict: GeoJSON Feature de type Point
    """
    base_properties = {
        "module": module,
        "score": score,
        "rating": get_rating(score),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if properties:
        base_properties.update(properties)
    
    return {
        "type": "Feature",
        "properties": base_properties,
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    }


def build_polygon_geojson(
    coordinates: List[List[float]],
    score: float,
    module: str,
    properties: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Construit un GeoJSON Polygon Feature.
    
    Args:
        coordinates: Liste de coordonnées [[lon, lat], ...]
        score: Score associé à la zone
        module: Nom du module source
        properties: Propriétés additionnelles
        
    Returns:
        Dict: GeoJSON Feature de type Polygon
    """
    base_properties = {
        "module": module,
        "score": score,
        "rating": get_rating(score),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if properties:
        base_properties.update(properties)
    
    return {
        "type": "Feature",
        "properties": base_properties,
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
    }


def build_feature_collection(features: List[Dict]) -> Dict:
    """
    Construit une FeatureCollection GeoJSON.
    
    Args:
        features: Liste de Features GeoJSON
        
    Returns:
        Dict: GeoJSON FeatureCollection
    """
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(features),
            "source": "BIONIC™ Engine"
        }
    }


def build_bounding_box(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float
) -> Dict:
    """
    Construit un objet bounding box.
    
    Args:
        min_lat: Latitude minimale
        min_lon: Longitude minimale
        max_lat: Latitude maximale
        max_lon: Longitude maximale
        
    Returns:
        Dict: Objet bounding box
    """
    return {
        "min_lat": min_lat,
        "min_lon": min_lon,
        "max_lat": max_lat,
        "max_lon": max_lon,
        "center": {
            "lat": (min_lat + max_lat) / 2,
            "lon": (min_lon + max_lon) / 2
        }
    }


def build_hotspot_geojson(
    hotspots: List[Dict],
    territory_id: str
) -> Dict:
    """
    Construit une FeatureCollection de hotspots.
    
    Args:
        hotspots: Liste de points chauds
        territory_id: ID du territoire
        
    Returns:
        Dict: GeoJSON FeatureCollection de hotspots
    """
    features = []
    
    for hotspot in hotspots:
        feature = {
            "type": "Feature",
            "properties": {
                "id": hotspot.get("id"),
                "type": hotspot.get("type", "unknown"),
                "probability": hotspot.get("probability", 0),
                "confidence": hotspot.get("confidence", 0),
                "territory_id": territory_id
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    hotspot.get("longitude", 0),
                    hotspot.get("latitude", 0)
                ]
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "territory_id": territory_id,
            "hotspot_count": len(hotspots),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    }


def build_analysis_geojson(
    lat: float,
    lon: float,
    radius_km: float,
    modules_results: Dict[str, Any],
    species_results: Dict[str, Any],
    overall_score: float
) -> Dict:
    """
    Construit un GeoJSON complet pour une analyse de territoire.
    
    Args:
        lat: Latitude du centre
        lon: Longitude du centre
        radius_km: Rayon en km
        modules_results: Résultats des modules
        species_results: Résultats des espèces
        overall_score: Score global
        
    Returns:
        Dict: GeoJSON FeatureCollection avec toutes les données
    """
    features = []
    
    # Point central avec score global
    center_feature = build_point_geojson(
        lat, lon, overall_score, "analysis_center",
        properties={
            "radius_km": radius_km,
            "is_center": True
        }
    )
    features.append(center_feature)
    
    # Points pour chaque module
    for module_name, module_data in modules_results.items():
        if isinstance(module_data, dict) and "score" in module_data:
            module_feature = build_point_geojson(
                lat, lon, module_data["score"], module_name,
                properties={
                    "factors": module_data.get("factors", {}),
                    "rating": module_data.get("rating", "")
                }
            )
            features.append(module_feature)
    
    return build_feature_collection(features)
