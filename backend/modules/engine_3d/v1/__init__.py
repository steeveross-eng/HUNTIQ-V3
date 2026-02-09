"""3D Engine Module v1

3D terrain visualization and analysis.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import math

router = APIRouter(prefix="/api/v1/3d", tags=["3D Engine"])


class ElevationPoint(BaseModel):
    latitude: float
    longitude: float
    elevation: float  # meters


class TerrainProfile(BaseModel):
    points: List[ElevationPoint]
    distance_km: float
    elevation_gain: float
    elevation_loss: float
    max_elevation: float
    min_elevation: float


def simulate_elevation(lat: float, lon: float) -> float:
    """Simulate elevation based on coordinates (for demo)"""
    # Simulated Quebec terrain: ~200-800m elevation
    base = 300
    variation = math.sin(lat * 10) * 150 + math.cos(lon * 8) * 100
    return round(base + variation, 1)


def calculate_viewshed_radius(observer_height: float, elevation: float) -> float:
    """Calculate approximate viewshed radius in km"""
    # Simplified formula: d = sqrt(2 * R * h) where R is Earth radius
    earth_radius = 6371  # km
    total_height = (elevation + observer_height) / 1000  # convert to km
    return round(math.sqrt(2 * earth_radius * total_height), 2)


@router.get("/")
async def engine_3d_info():
    return {
        "module": "engine_3d",
        "version": "1.0.0",
        "description": "3D terrain visualization and analysis",
        "features": ["Elevation data", "Terrain profiles", "Viewshed analysis", "Line of sight", "Slope analysis"],
        "data_source": "Simulated (Production: MNT Quebec)"
    }


@router.get("/elevation")
async def get_elevation(latitude: float = Query(..., ge=44, le=63), longitude: float = Query(..., ge=-80, le=-57)):
    elevation = simulate_elevation(latitude, longitude)
    return {
        "success": True,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "elevation": elevation,
        "unit": "meters"
    }


@router.post("/profile")
async def get_terrain_profile(start_lat: float, start_lon: float, end_lat: float, end_lon: float, num_points: int = Query(20, ge=5, le=100)):
    points = []
    elevations = []
    
    for i in range(num_points):
        t = i / (num_points - 1)
        lat = start_lat + t * (end_lat - start_lat)
        lon = start_lon + t * (end_lon - start_lon)
        elev = simulate_elevation(lat, lon)
        points.append(ElevationPoint(latitude=lat, longitude=lon, elevation=elev))
        elevations.append(elev)
    
    # Calculate distance (simplified Haversine)
    dlat = math.radians(end_lat - start_lat)
    dlon = math.radians(end_lon - start_lon)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat)) * math.sin(dlon/2)**2
    distance = 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Calculate gains/losses
    gain = sum(max(0, elevations[i+1] - elevations[i]) for i in range(len(elevations)-1))
    loss = sum(max(0, elevations[i] - elevations[i+1]) for i in range(len(elevations)-1))
    
    return {
        "success": True,
        "profile": {
            "points": [p.model_dump() for p in points],
            "distance_km": round(distance, 2),
            "elevation_gain": round(gain, 1),
            "elevation_loss": round(loss, 1),
            "max_elevation": max(elevations),
            "min_elevation": min(elevations)
        }
    }


@router.get("/viewshed")
async def calculate_viewshed(latitude: float, longitude: float, observer_height: float = Query(1.7, ge=0, le=50)):
    elevation = simulate_elevation(latitude, longitude)
    viewshed_radius = calculate_viewshed_radius(observer_height, elevation)
    
    return {
        "success": True,
        "observer_position": {"latitude": latitude, "longitude": longitude, "elevation": elevation},
        "observer_height": observer_height,
        "viewshed_radius_km": viewshed_radius,
        "visible_area_km2": round(math.pi * viewshed_radius**2, 2),
        "note": "Theoretical maximum in open terrain"
    }


@router.post("/line-of-sight")
async def check_line_of_sight(observer_lat: float, observer_lon: float, target_lat: float, target_lon: float, observer_height: float = 1.7, target_height: float = 1.5):
    obs_elev = simulate_elevation(observer_lat, observer_lon)
    tgt_elev = simulate_elevation(target_lat, target_lon)
    
    # Check intermediate points
    visible = True
    num_checks = 10
    obs_total = obs_elev + observer_height
    tgt_total = tgt_elev + target_height
    
    for i in range(1, num_checks):
        t = i / num_checks
        lat = observer_lat + t * (target_lat - observer_lat)
        lon = observer_lon + t * (target_lon - observer_lon)
        terrain_elev = simulate_elevation(lat, lon)
        
        # Line height at this point
        line_height = obs_total + t * (tgt_total - obs_total)
        
        if terrain_elev > line_height:
            visible = False
            break
    
    return {
        "success": True,
        "observer": {"lat": observer_lat, "lon": observer_lon, "elevation": obs_elev},
        "target": {"lat": target_lat, "lon": target_lon, "elevation": tgt_elev},
        "line_of_sight": visible,
        "recommendation": "Position avec vue dégagée" if visible else "Obstacles présents - changer de position"
    }


@router.get("/slope")
async def analyze_slope(latitude: float, longitude: float):
    # Simulate slope by checking nearby elevations
    elev_center = simulate_elevation(latitude, longitude)
    elev_n = simulate_elevation(latitude + 0.001, longitude)
    elev_s = simulate_elevation(latitude - 0.001, longitude)
    elev_e = simulate_elevation(latitude, longitude + 0.001)
    elev_w = simulate_elevation(latitude, longitude - 0.001)
    
    slope_ns = abs(elev_n - elev_s) / 222  # ~111m per 0.001 degree * 2
    slope_ew = abs(elev_e - elev_w) / 222
    slope_percent = max(slope_ns, slope_ew) * 100
    
    # Determine aspect (direction of steepest descent)
    if elev_n < elev_s:
        aspect = "N" if abs(elev_n - elev_s) > abs(elev_e - elev_w) else ("E" if elev_e < elev_w else "W")
    else:
        aspect = "S" if abs(elev_n - elev_s) > abs(elev_e - elev_w) else ("E" if elev_e < elev_w else "W")
    
    return {
        "success": True,
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "elevation": elev_center,
        "slope_percent": round(slope_percent, 1),
        "slope_category": "Plat" if slope_percent < 5 else "Faible" if slope_percent < 15 else "Modéré" if slope_percent < 30 else "Fort",
        "aspect": aspect,
        "hunting_note": "Pentes faibles = meilleur pour affût" if slope_percent < 15 else "Utiliser le terrain pour approche"
    }
