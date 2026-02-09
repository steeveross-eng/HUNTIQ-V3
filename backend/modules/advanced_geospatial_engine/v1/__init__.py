"""Advanced Geospatial Engine Module v1

Advanced geospatial analysis for hunting.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import math
import random

router = APIRouter(prefix="/api/v1/advanced-geo", tags=["Advanced Geospatial Engine"])


class Corridor(BaseModel):
    id: str
    name: str
    start_point: Dict[str, float]
    end_point: Dict[str, float]
    width_meters: float
    species: List[str]
    usage_score: float


class ConcentrationZone(BaseModel):
    id: str
    center: Dict[str, float]
    radius_meters: float
    density_score: float
    species: str
    reason: str


SAMPLE_CORRIDORS = [
    {"id": "corr-001", "name": "Corridor Nord-Sud Forêt", "start_point": {"lat": 46.85, "lon": -71.25}, "end_point": {"lat": 46.80, "lon": -71.23}, "width_meters": 150, "species": ["deer", "moose"], "usage_score": 85},
    {"id": "corr-002", "name": "Passage Ruisseau", "start_point": {"lat": 46.82, "lon": -71.30}, "end_point": {"lat": 46.81, "lon": -71.28}, "width_meters": 80, "species": ["deer"], "usage_score": 92},
    {"id": "corr-003", "name": "Lisière Champ-Forêt", "start_point": {"lat": 46.78, "lon": -71.22}, "end_point": {"lat": 46.76, "lon": -71.20}, "width_meters": 200, "species": ["deer", "turkey"], "usage_score": 78},
]

SAMPLE_CONCENTRATION_ZONES = [
    {"id": "zone-001", "center": {"lat": 46.83, "lon": -71.27}, "radius_meters": 300, "density_score": 88, "species": "deer", "reason": "Zone de gagnage - chênes"},
    {"id": "zone-002", "center": {"lat": 46.80, "lon": -71.25}, "radius_meters": 400, "species": "moose", "density_score": 82, "reason": "Zone humide - alimentation"},
    {"id": "zone-003", "center": {"lat": 46.85, "lon": -71.30}, "radius_meters": 250, "species": "deer", "density_score": 75, "reason": "Couvert thermique hivernal"},
]


def calculate_connectivity(point1: Dict, point2: Dict, terrain_factor: float = 0.8) -> float:
    """Calculate habitat connectivity between two points"""
    # Simplified connectivity based on distance and terrain
    dlat = point2["lat"] - point1["lat"]
    dlon = point2["lon"] - point1["lon"]
    distance = math.sqrt(dlat**2 + dlon**2) * 111  # Rough km conversion
    
    # Connectivity decreases with distance, modified by terrain
    base_connectivity = 100 * math.exp(-distance / 5)
    return round(base_connectivity * terrain_factor, 1)


def generate_heatmap_data(center_lat: float, center_lon: float, radius_km: float, resolution: int = 10) -> List[Dict]:
    """Generate simulated heatmap data"""
    points = []
    for i in range(resolution):
        for j in range(resolution):
            lat = center_lat + (i - resolution/2) * (radius_km / 111 / resolution * 2)
            lon = center_lon + (j - resolution/2) * (radius_km / 85 / resolution * 2)  # Adjust for latitude
            
            # Simulate density based on distance from center + random variation
            dist_from_center = math.sqrt((lat - center_lat)**2 + (lon - center_lon)**2) * 111
            density = max(0, 100 - dist_from_center * 20 + random.uniform(-15, 15))
            
            points.append({"lat": round(lat, 5), "lon": round(lon, 5), "density": round(density, 1)})
    
    return points


@router.get("/")
async def advanced_geo_info():
    return {
        "module": "advanced_geospatial_engine",
        "version": "1.0.0",
        "description": "Advanced geospatial analysis",
        "features": ["Movement corridors", "Concentration zones", "Habitat connectivity", "Density heatmaps"],
        "corridors_count": len(SAMPLE_CORRIDORS),
        "zones_count": len(SAMPLE_CONCENTRATION_ZONES)
    }


@router.get("/corridors")
async def list_corridors(species: Optional[str] = None, min_score: float = Query(0, ge=0, le=100)):
    corridors = SAMPLE_CORRIDORS.copy()
    if species:
        corridors = [c for c in corridors if species in c["species"]]
    corridors = [c for c in corridors if c["usage_score"] >= min_score]
    
    return {"success": True, "corridors": corridors}


@router.get("/corridors/{corridor_id}")
async def get_corridor(corridor_id: str):
    corridor = next((c for c in SAMPLE_CORRIDORS if c["id"] == corridor_id), None)
    if not corridor:
        return {"success": False, "error": "Corridor not found"}
    return {"success": True, "corridor": corridor}


@router.get("/concentration-zones")
async def list_concentration_zones(species: Optional[str] = None, min_density: float = Query(0, ge=0, le=100)):
    zones = SAMPLE_CONCENTRATION_ZONES.copy()
    if species:
        zones = [z for z in zones if z["species"] == species]
    zones = [z for z in zones if z["density_score"] >= min_density]
    
    return {"success": True, "zones": zones}


@router.post("/connectivity")
async def analyze_connectivity(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    terrain_quality: float = Query(0.8, ge=0, le=1, description="Terrain traversability 0-1")
):
    connectivity = calculate_connectivity(
        {"lat": lat1, "lon": lon1},
        {"lat": lat2, "lon": lon2},
        terrain_quality
    )
    
    return {
        "success": True,
        "point1": {"lat": lat1, "lon": lon1},
        "point2": {"lat": lat2, "lon": lon2},
        "connectivity_score": connectivity,
        "interpretation": "Forte connectivité" if connectivity >= 70 else "Connectivité moyenne" if connectivity >= 40 else "Faible connectivité",
        "recommendation": "Bon axe de déplacement" if connectivity >= 60 else "Corridor fragmenté"
    }


@router.get("/heatmap")
async def get_density_heatmap(
    center_lat: float = Query(..., ge=44, le=63),
    center_lon: float = Query(..., ge=-80, le=-57),
    radius_km: float = Query(2, ge=0.5, le=10),
    species: str = Query("deer"),
    resolution: int = Query(10, ge=5, le=20)
):
    heatmap_data = generate_heatmap_data(center_lat, center_lon, radius_km, resolution)
    
    return {
        "success": True,
        "center": {"lat": center_lat, "lon": center_lon},
        "radius_km": radius_km,
        "species": species,
        "resolution": resolution,
        "heatmap": heatmap_data,
        "legend": {
            "high": "80-100 (Rouge)",
            "medium": "50-79 (Orange)",
            "low": "20-49 (Jaune)",
            "very_low": "0-19 (Vert)"
        }
    }


@router.get("/optimal-positions")
async def find_optimal_positions(
    center_lat: float = Query(...),
    center_lon: float = Query(...),
    species: str = Query("deer"),
    radius_km: float = Query(2)
):
    # Find positions near corridors and concentration zones
    positions = [
        {
            "id": "pos-001",
            "lat": center_lat + 0.005,
            "lon": center_lon - 0.003,
            "score": 88,
            "reason": "Intersection de corridors",
            "recommended_time": "Aube"
        },
        {
            "id": "pos-002",
            "lat": center_lat - 0.008,
            "lon": center_lon + 0.002,
            "score": 82,
            "reason": "Proximité zone de concentration",
            "recommended_time": "Crépuscule"
        },
        {
            "id": "pos-003",
            "lat": center_lat + 0.002,
            "lon": center_lon + 0.007,
            "score": 75,
            "reason": "Point de passage",
            "recommended_time": "Toute la journée"
        }
    ]
    
    return {
        "success": True,
        "search_area": {"center": {"lat": center_lat, "lon": center_lon}, "radius_km": radius_km},
        "species": species,
        "optimal_positions": positions
    }
