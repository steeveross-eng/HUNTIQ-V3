"""
BIONIC™ P1 - Geospatial API Endpoints
======================================
Endpoints FastAPI pour la Géo-Suite complète.

Version: 1.0.0
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

# Import des moteurs
from geospatial.corridor_engine import corridor_engine
from geospatial.landcover_engine import landcover_engine
from geospatial.nutrition_engine import nutrition_engine
from geospatial.population_density_engine import population_density_engine
from geospatial.hunting_pressure_module import hunting_pressure_module
from geospatial.map_style_manager import map_style_manager
from geospatial.unified_output import FusionInterface

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bionic/geosuite", tags=["P1 Géo-Suite"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalysisRequest(BaseModel):
    """Requête d'analyse standard."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    radius_km: float = Field(default=2.0, ge=0.5, le=50, description="Rayon d'analyse en km")
    target_species: Optional[List[str]] = Field(default=None, description="Espèces cibles")


class SuiteAnalysisRequest(BaseModel):
    """Requête d'analyse pour la suite complète."""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=2.0, ge=0.5, le=50)
    target_species: Optional[List[str]] = None
    include_corridors: bool = True
    include_landcover: bool = True
    include_nutrition: bool = True
    include_population: bool = True
    include_pressure: bool = True


# =============================================================================
# STATUS ENDPOINT
# =============================================================================

@router.get("/status")
async def get_geosuite_status():
    """Retourne le statut de la Géo-Suite P1."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "phase": "P1",
        "name": "BIONIC™ Géo-Suite Nord-Américaine",
        "engines": {
            "corridorEngine": {"status": "active", "version": "1.0.0"},
            "landcoverEngine": {"status": "active", "version": "1.0.0"},
            "nutritionEngine": {"status": "active", "version": "1.0.0"},
            "populationDensityEngine": {"status": "active", "version": "1.0.0"},
            "huntingPressureModule": {"status": "active", "version": "1.0.0"}
        },
        "data_sources": {
            "quebec": ["SIGÉOM", "MFFP", "UGAF", "ZEC"],
            "canada": ["CanVec", "NRCan"],
            "usa": ["NLCD", "USGS", "USDA", "USFWS"],
            "global": ["OSM", "NASA MODIS", "NOAA"]
        },
        "north_america_ready": True,
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# CORRIDOR ENGINE ENDPOINTS
# =============================================================================

@router.post("/corridor/analyze")
async def analyze_corridors(request: AnalysisRequest):
    """
    Analyse les corridors fauniques autour d'un point.
    
    Détecte les corridors de type:
    - Riparian (cours d'eau)
    - Ridgeline (crêtes)
    - Forest edge (lisières)
    - Valley (vallées)
    - Agricultural edge (bordures agricoles)
    """
    try:
        result = await corridor_engine.analyze(
            lat=request.lat,
            lon=request.lon,
            radius_km=request.radius_km,
            target_species=request.target_species
        )
        return result.__dict__ if hasattr(result, '__dict__') else result
    except Exception as e:
        logger.error(f"Corridor analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/corridor/species/{species}")
async def get_corridor_species_score(
    species: str,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=2.0, ge=0.5, le=50)
):
    """Retourne le score de corridor pour une espèce spécifique."""
    try:
        result = await corridor_engine.analyze(
            lat=lat, lon=lon, radius_km=radius_km, target_species=[species]
        )
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        species_score = data.get("data", {}).get("seasonal_scores", {}).get(species, 50)
        
        return {
            "species": species,
            "corridor_score": species_score,
            "location": {"lat": lat, "lon": lon},
            "corridors_count": data.get("data", {}).get("corridors_count", 0),
            "connectivity_index": data.get("data", {}).get("connectivity_index", 0.5)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# LANDCOVER ENGINE ENDPOINTS
# =============================================================================

@router.post("/landcover/analyze")
async def analyze_landcover(request: AnalysisRequest):
    """
    Analyse le couvert végétal autour d'un point.
    
    Retourne:
    - Couvert dominant
    - Composition (% par type)
    - Densité de lisières
    - Couvert thermique
    - Diversité structurelle
    """
    try:
        result = await landcover_engine.analyze(
            lat=request.lat,
            lon=request.lon,
            radius_km=request.radius_km,
            target_species=request.target_species
        )
        return result.__dict__ if hasattr(result, '__dict__') else result
    except Exception as e:
        logger.error(f"Landcover analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/landcover/composition")
async def get_landcover_composition(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=2.0, ge=0.5, le=50)
):
    """Retourne la composition du couvert végétal."""
    try:
        result = await landcover_engine.analyze(lat=lat, lon=lon, radius_km=radius_km)
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        return {
            "location": {"lat": lat, "lon": lon},
            "dominant_cover": data.get("data", {}).get("dominant_cover"),
            "composition": data.get("data", {}).get("cover_composition", []),
            "thermal_cover_percent": data.get("data", {}).get("thermal_cover_percent", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/landcover/edge-density")
async def get_edge_density(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=2.0, ge=0.5, le=50)
):
    """Retourne la densité de lisières."""
    try:
        result = await landcover_engine.analyze(lat=lat, lon=lon, radius_km=radius_km)
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        return {
            "location": {"lat": lat, "lon": lon},
            "edge_density_m_ha": data.get("data", {}).get("edge_density_m_ha", 0),
            "edge_types": data.get("data", {}).get("edge_types", {}),
            "fragmentation_index": data.get("data", {}).get("fragmentation_index", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# NUTRITION ENGINE ENDPOINTS
# =============================================================================

@router.post("/nutrition/analyze")
async def analyze_nutrition(request: AnalysisRequest):
    """
    Analyse la qualité nutritionnelle d'une zone.
    
    Retourne:
    - Score nutritionnel global
    - Disponibilité alimentaire par espèce
    - Indice de glandée (mast index)
    - Qualité du brout
    """
    try:
        result = await nutrition_engine.analyze(
            lat=request.lat,
            lon=request.lon,
            radius_km=request.radius_km,
            target_species=request.target_species
        )
        return result.__dict__ if hasattr(result, '__dict__') else result
    except Exception as e:
        logger.error(f"Nutrition analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nutrition/species/{species}")
async def get_species_nutrition(
    species: str,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=2.0, ge=0.5, le=50)
):
    """Retourne le score nutritionnel pour une espèce."""
    try:
        result = await nutrition_engine.analyze(
            lat=lat, lon=lon, radius_km=radius_km, target_species=[species]
        )
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        species_data = data.get("data", {}).get("species_nutrition", {}).get(species, {})
        
        return {
            "species": species,
            "location": {"lat": lat, "lon": lon},
            "nutrition_score": species_data.get("score", 50),
            "food_availability": species_data.get("food_availability", "moderate"),
            "primary_foods": species_data.get("primary_foods_available", []),
            "deficiencies": species_data.get("deficiencies", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nutrition/mast-index")
async def get_mast_index(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=2.0, ge=0.5, le=50)
):
    """Retourne l'indice de glandée."""
    try:
        result = await nutrition_engine.analyze(lat=lat, lon=lon, radius_km=radius_km)
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        mast = data.get("data", {}).get("mast_index", {})
        
        return {
            "location": {"lat": lat, "lon": lon},
            "mast_score": mast.get("score", 50),
            "mast_types": mast.get("mast_types", {}),
            "year_trend": mast.get("year_trend", "average"),
            "species_impact": mast.get("species_impact", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POPULATION DENSITY ENGINE ENDPOINTS
# =============================================================================

@router.post("/population/density")
async def analyze_population_density(request: AnalysisRequest):
    """
    Analyse la densité de population faunique.
    
    Retourne:
    - Densité par espèce (animaux/100km²)
    - Tendances démographiques
    - Pression de récolte
    """
    try:
        result = await population_density_engine.analyze(
            lat=request.lat,
            lon=request.lon,
            radius_km=request.radius_km,
            target_species=request.target_species
        )
        return result.__dict__ if hasattr(result, '__dict__') else result
    except Exception as e:
        logger.error(f"Population density analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/population/trend/{species}")
async def get_population_trend(
    species: str,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    """Retourne la tendance de population pour une espèce."""
    try:
        result = await population_density_engine.analyze(
            lat=lat, lon=lon, radius_km=5.0, target_species=[species]
        )
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        species_data = data.get("data", {}).get("species_densities", {}).get(species, {})
        
        return {
            "species": species,
            "location": {"lat": lat, "lon": lon},
            "density_per_100km2": species_data.get("density_per_100km2", 0),
            "trend": species_data.get("trend", "unknown"),
            "confidence": species_data.get("confidence", 0.5),
            "data_year_range": species_data.get("data_year_range", "2015-2024")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/population/harvest")
async def get_harvest_data(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    """Retourne les données de récolte historiques."""
    try:
        result = await population_density_engine.analyze(lat=lat, lon=lon, radius_km=10.0)
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        return {
            "location": {"lat": lat, "lon": lon},
            "harvest_data": data.get("data", {}).get("harvest_data", {}),
            "harvest_pressure": data.get("data", {}).get("harvest_pressure", 0.5),
            "sub_region": data.get("data", {}).get("sub_region", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# HUNTING PRESSURE MODULE ENDPOINTS
# =============================================================================

@router.post("/hunting-pressure/analyze")
async def analyze_hunting_pressure(request: AnalysisRequest):
    """
    Analyse la pression de chasse dans une zone.
    
    Retourne:
    - Niveau de pression
    - Impact comportemental
    - Fenêtres temporelles optimales
    - Zones à éviter
    """
    try:
        result = await hunting_pressure_module.analyze(
            lat=request.lat,
            lon=request.lon,
            radius_km=request.radius_km,
            target_species=request.target_species
        )
        return result.__dict__ if hasattr(result, '__dict__') else result
    except Exception as e:
        logger.error(f"Hunting pressure analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hunting-pressure/impact")
async def get_behavioral_impact(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    """Retourne l'impact comportemental de la pression de chasse."""
    try:
        result = await hunting_pressure_module.analyze(lat=lat, lon=lon, radius_km=5.0)
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        return {
            "location": {"lat": lat, "lon": lon},
            "pressure_level": data.get("data", {}).get("pressure_level", "moderate"),
            "behavioral_impact": data.get("data", {}).get("behavioral_impact", {}),
            "weekly_pattern": data.get("data", {}).get("weekly_pattern", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hunting-pressure/optimal-timing")
async def get_optimal_hunting_timing(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    """Retourne les fenêtres temporelles optimales."""
    try:
        result = await hunting_pressure_module.analyze(lat=lat, lon=lon, radius_km=5.0)
        data = result.__dict__ if hasattr(result, '__dict__') else result
        
        return {
            "location": {"lat": lat, "lon": lon},
            "optimal_timing": data.get("data", {}).get("optimal_timing", []),
            "weekly_pattern": data.get("data", {}).get("weekly_pattern", {}),
            "recommendations": data.get("recommendations", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# FULL SUITE ANALYSIS
# =============================================================================

@router.post("/analyze/full")
async def run_full_geosuite_analysis(request: SuiteAnalysisRequest):
    """
    Exécute une analyse complète avec tous les moteurs de la Géo-Suite.
    
    Combine:
    - Corridors fauniques
    - Couvert végétal
    - Nutrition
    - Densité de population
    - Pression de chasse
    """
    try:
        results = {
            "location": {"lat": request.lat, "lon": request.lon},
            "radius_km": request.radius_km,
            "engines_executed": [],
            "analyses": {},
            "global_score": 0,
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        scores = []
        all_recommendations = []
        
        # Corridors
        if request.include_corridors:
            corridor_result = await corridor_engine.analyze(
                request.lat, request.lon, request.radius_km, request.target_species
            )
            results["analyses"]["corridor"] = corridor_result.__dict__ if hasattr(corridor_result, '__dict__') else corridor_result
            results["engines_executed"].append("corridorEngine")
            scores.append(corridor_result.score if hasattr(corridor_result, 'score') else results["analyses"]["corridor"].get("score", 50))
            all_recommendations.extend(corridor_result.recommendations if hasattr(corridor_result, 'recommendations') else [])
        
        # Landcover
        if request.include_landcover:
            landcover_result = await landcover_engine.analyze(
                request.lat, request.lon, request.radius_km, request.target_species
            )
            results["analyses"]["landcover"] = landcover_result.__dict__ if hasattr(landcover_result, '__dict__') else landcover_result
            results["engines_executed"].append("landcoverEngine")
            scores.append(landcover_result.score if hasattr(landcover_result, 'score') else results["analyses"]["landcover"].get("score", 50))
            all_recommendations.extend(landcover_result.recommendations if hasattr(landcover_result, 'recommendations') else [])
        
        # Nutrition
        if request.include_nutrition:
            nutrition_result = await nutrition_engine.analyze(
                request.lat, request.lon, request.radius_km, request.target_species
            )
            results["analyses"]["nutrition"] = nutrition_result.__dict__ if hasattr(nutrition_result, '__dict__') else nutrition_result
            results["engines_executed"].append("nutritionEngine")
            scores.append(nutrition_result.score if hasattr(nutrition_result, 'score') else results["analyses"]["nutrition"].get("score", 50))
            all_recommendations.extend(nutrition_result.recommendations if hasattr(nutrition_result, 'recommendations') else [])
        
        # Population
        if request.include_population:
            population_result = await population_density_engine.analyze(
                request.lat, request.lon, request.radius_km, request.target_species
            )
            results["analyses"]["population"] = population_result.__dict__ if hasattr(population_result, '__dict__') else population_result
            results["engines_executed"].append("populationDensityEngine")
            scores.append(population_result.score if hasattr(population_result, 'score') else results["analyses"]["population"].get("score", 50))
            all_recommendations.extend(population_result.recommendations if hasattr(population_result, 'recommendations') else [])
        
        # Pressure
        if request.include_pressure:
            pressure_result = await hunting_pressure_module.analyze(
                request.lat, request.lon, request.radius_km, request.target_species
            )
            results["analyses"]["pressure"] = pressure_result.__dict__ if hasattr(pressure_result, '__dict__') else pressure_result
            results["engines_executed"].append("huntingPressureModule")
            scores.append(pressure_result.score if hasattr(pressure_result, 'score') else results["analyses"]["pressure"].get("score", 50))
            all_recommendations.extend(pressure_result.recommendations if hasattr(pressure_result, 'recommendations') else [])
        
        # Score global
        if scores:
            results["global_score"] = round(sum(scores) / len(scores), 1)
        
        # Top recommandations
        results["recommendations"] = list(dict.fromkeys(all_recommendations))[:10]
        
        return results
        
    except Exception as e:
        logger.error(f"Full geosuite analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MAP STYLE ENDPOINTS
# =============================================================================

@router.get("/map/styles")
async def get_available_map_styles():
    """Retourne les styles de carte disponibles."""
    return {
        "styles": map_style_manager.get_available_styles(),
        "default": "light"
    }


@router.get("/map/style/{style_id}")
async def get_map_style(style_id: str):
    """Retourne la configuration d'un style de carte."""
    style = map_style_manager.get_style(style_id)
    return {"style_id": style_id, "config": style}


@router.get("/map/species-presets")
async def get_species_layer_presets():
    """Retourne les préréglages de couches par espèce."""
    return map_style_manager.get_all_species_presets()


@router.get("/map/species-preset/{species}")
async def get_species_preset(species: str):
    """Retourne le préréglage de couches pour une espèce."""
    return map_style_manager.get_species_preset(species)


@router.get("/map/data-layers")
async def get_data_layers():
    """Retourne les couches de données BIONIC™ disponibles."""
    return map_style_manager.get_all_data_layers()


# =============================================================================
# FUSION INTERFACE ENDPOINTS
# =============================================================================

@router.get("/fusion/weights")
async def get_fusion_weights():
    """Retourne les poids de fusion pour l'intégration avec BehaviorFusionEngine (P2)."""
    return FusionInterface.get_fusion_weights()


@router.get("/fusion/compatibility")
async def check_fusion_compatibility():
    """Vérifie la compatibilité avec BehaviorFusionEngine (P2)."""
    return {
        "compatible": True,
        "interface_version": "1.0.0",
        "behavior_suite_hooks": True,
        "unified_output_format": True,
        "engines_ready": ["corridor", "landcover", "nutrition", "population", "pressure"]
    }


logger.info("BIONIC™ P1 Géo-Suite API endpoints loaded")
