"""
BIONIC™ Pressure Engine - Human Pressure Analyzer
===================================================
Analyse de la pression humaine sur les territoires de chasse.

Version: 1.0 - Phase 3 Real Data Implementation
- Intégration du cache multi-niveaux
- Données réelles via RealDataFetcher (OSM)
- Calcul de densité routière, bâti, remoteness
"""

import logging
import math
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Add core path for imports
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

# Import cache and real data fetcher with fallback
try:
    from core.cache_manager import cache_manager
    from core.real_data_fetcher import real_data_fetcher
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache_manager = None
    real_data_fetcher = None

logger = logging.getLogger(__name__)


class PressureAnalyzer:
    """
    Analyseur de pression humaine pour l'évaluation de territoires de chasse.
    
    Analyse:
    - Densité routière
    - Densité de bâtiments
    - Distance aux agglomérations
    - Niveau de perturbation
    - Impact sur le comportement du gibier
    """
    
    # Pressure level impacts
    PRESSURE_IMPACTS = {
        "very_low": {
            "threshold": 20,
            "animal_behavior": "Gibier peu méfiant, activité diurne normale",
            "hunting_strategy": "Toutes techniques applicables",
            "success_factor": 1.3
        },
        "low": {
            "threshold": 40,
            "animal_behavior": "Gibier légèrement adapté, activité régulière",
            "hunting_strategy": "Techniques standard recommandées",
            "success_factor": 1.15
        },
        "moderate": {
            "threshold": 60,
            "animal_behavior": "Gibier adapté, activité crépusculaire privilégiée",
            "hunting_strategy": "Patience et discrétion requises",
            "success_factor": 1.0
        },
        "high": {
            "threshold": 80,
            "animal_behavior": "Gibier très méfiant, activité principalement nocturne",
            "hunting_strategy": "Aube et crépuscule uniquement, discrétion maximale",
            "success_factor": 0.7
        },
        "very_high": {
            "threshold": 100,
            "animal_behavior": "Gibier extrêmement méfiant, densité réduite",
            "hunting_strategy": "Zone défavorable pour la chasse",
            "success_factor": 0.4
        }
    }
    
    # Distance thresholds from human activity (km)
    DISTANCE_THRESHOLDS = {
        "roads": {
            "critical": 0.1,    # <100m = forte perturbation
            "moderate": 0.5,   # <500m = perturbation modérée
            "low": 2.0         # <2km = légère perturbation
        },
        "buildings": {
            "critical": 0.2,
            "moderate": 0.8,
            "low": 2.5
        },
        "towns": {
            "critical": 2.0,
            "moderate": 10.0,
            "low": 30.0
        }
    }
    
    def __init__(self):
        self._cache_namespace = "pressure"
        self._cache_hits = 0
        self._cache_misses = 0
    
    async def analyze_point_async(
        self,
        lat: float,
        lon: float,
        radius_km: float = 2.0,
        use_cache: bool = True,
        use_real_data: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze human pressure at a specific point (async version).
        """
        cache_key = cache_manager.make_geo_key(lat, lon)
        
        # Check cache first
        if use_cache:
            cached = cache_manager.get(self._cache_namespace, cache_key)
            if cached:
                self._cache_hits += 1
                cached["from_cache"] = True
                return cached
            self._cache_misses += 1
        
        # Fetch real pressure data
        pressure_data = None
        if use_real_data:
            try:
                pressure_data = await real_data_fetcher.fetch_pressure_analysis(lat, lon, radius_km)
            except Exception as e:
                logger.warning(f"Real pressure data fetch failed: {e}")
        
        # Extract or estimate metrics
        if pressure_data and "pressure_metrics" in pressure_data:
            metrics = pressure_data["pressure_metrics"]
            osm_features = pressure_data.get("osm_features", {})
        else:
            osm_features = self._estimate_osm_features(lat, lon)
            metrics = self._calculate_pressure_metrics(osm_features)
        
        # Calculate detailed analysis
        road_analysis = self._analyze_road_pressure(osm_features.get("roads_count", 0), radius_km)
        building_analysis = self._analyze_building_pressure(osm_features.get("buildings_count", 0), radius_km)
        remoteness = self._calculate_remoteness(lat, lon, metrics)
        
        # Determine pressure level
        pressure_level = self._determine_pressure_level(metrics.get("pressure_index", 50))
        
        result = {
            "location": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "data_source": osm_features.get("source", "BIONIC Pressure Model"),
            "confidence": 0.70,
            "osm_features": osm_features,
            "pressure_metrics": metrics,
            "road_analysis": road_analysis,
            "building_analysis": building_analysis,
            "remoteness": remoteness,
            "pressure_level": pressure_level,
            "hunting_impact": self._assess_hunting_impact(pressure_level),
            "overall_score": self._calculate_overall_score(metrics, remoteness),
            "recommendations": self._generate_recommendations(pressure_level, remoteness),
            "from_cache": False
        }
        
        # Store in cache
        if use_cache:
            cache_manager.set(self._cache_namespace, cache_key, result, ttl=3600)  # 1h
        
        return result
    
    def _estimate_osm_features(self, lat: float, lon: float) -> Dict[str, Any]:
        """Estimate OSM features based on location."""
        import random
        random.seed(int(lat * 1000 + lon * 1000))
        
        # Distance to major cities
        dist_montreal = math.sqrt((lat - 45.5)**2 + (lon + 73.6)**2)
        dist_quebec = math.sqrt((lat - 46.8)**2 + (lon + 71.2)**2)
        dist_trois_riv = math.sqrt((lat - 46.35)**2 + (lon + 72.55)**2)
        min_dist = min(dist_montreal, dist_quebec, dist_trois_riv)
        
        # Estimate based on distance to cities
        if min_dist < 0.3:  # Urban core
            roads = random.randint(80, 200)
            buildings = random.randint(300, 800)
            zone = "urban"
        elif min_dist < 0.7:  # Suburban
            roads = random.randint(30, 80)
            buildings = random.randint(80, 250)
            zone = "suburban"
        elif min_dist < 1.5:  # Rural developed
            roads = random.randint(10, 35)
            buildings = random.randint(20, 80)
            zone = "rural_developed"
        elif min_dist < 3.0:  # Rural
            roads = random.randint(3, 15)
            buildings = random.randint(5, 30)
            zone = "rural"
        else:  # Remote
            roads = random.randint(0, 8)
            buildings = random.randint(0, 10)
            zone = "remote"
        
        return {
            "roads_count": roads,
            "buildings_count": buildings,
            "estimated_zone": zone,
            "distance_to_city_deg": min_dist,
            "source": "BIONIC Estimate"
        }
    
    def _calculate_pressure_metrics(self, osm_features: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate pressure metrics from OSM features."""
        roads = osm_features.get("roads_count", 0)
        buildings = osm_features.get("buildings_count", 0)
        
        # Road pressure score (0-100)
        road_pressure = min(100, roads * 1.5)
        
        # Building pressure score
        building_pressure = min(100, buildings * 0.3)
        
        # Combined pressure index
        pressure_index = (road_pressure * 0.6) + (building_pressure * 0.4)
        
        # Hunting suitability (inverse)
        hunting_suitability = max(0, 100 - pressure_index)
        
        return {
            "road_density_score": round(road_pressure, 1),
            "building_density_score": round(building_pressure, 1),
            "pressure_index": round(pressure_index, 1),
            "hunting_suitability": round(hunting_suitability, 1),
            "remoteness_score": round(100 - pressure_index, 1)
        }
    
    def _analyze_road_pressure(self, roads_count: int, radius_km: float) -> Dict[str, Any]:
        """Analyze road pressure."""
        # Normalize by area
        area_km2 = math.pi * radius_km ** 2
        road_density = roads_count / area_km2 if area_km2 > 0 else 0
        
        if road_density < 2:
            level = "minimal"
            impact = "Impact négligeable sur le gibier"
        elif road_density < 10:
            level = "low"
            impact = "Légère perturbation, gibier adapté"
        elif road_density < 25:
            level = "moderate"
            impact = "Perturbation modérée, activité crépusculaire"
        elif road_density < 50:
            level = "high"
            impact = "Forte perturbation, gibier nocturne"
        else:
            level = "very_high"
            impact = "Perturbation maximale, gibier très rare"
        
        return {
            "roads_count": roads_count,
            "density_per_km2": round(road_density, 2),
            "pressure_level": level,
            "impact": impact
        }
    
    def _analyze_building_pressure(self, buildings_count: int, radius_km: float) -> Dict[str, Any]:
        """Analyze building pressure."""
        area_km2 = math.pi * radius_km ** 2
        building_density = buildings_count / area_km2 if area_km2 > 0 else 0
        
        if building_density < 5:
            level = "minimal"
            note = "Zone très peu habitée"
        elif building_density < 20:
            level = "low"
            note = "Zone rurale dispersée"
        elif building_density < 50:
            level = "moderate"
            note = "Zone rurale développée"
        elif building_density < 150:
            level = "high"
            note = "Zone périurbaine"
        else:
            level = "very_high"
            note = "Zone urbaine"
        
        return {
            "buildings_count": buildings_count,
            "density_per_km2": round(building_density, 2),
            "pressure_level": level,
            "note": note
        }
    
    def _calculate_remoteness(
        self, 
        lat: float, 
        lon: float, 
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate remoteness score."""
        # Base remoteness from pressure
        base_remoteness = metrics.get("remoteness_score", 50)
        
        # Latitude bonus (further north = more remote)
        lat_bonus = max(0, (lat - 47) * 5)  # +5 per degree north of 47°
        
        # Longitude adjustment (further west in Quebec = more remote)
        lon_bonus = max(0, (-lon - 70) * 2)  # +2 per degree west of -70°
        
        remoteness = min(100, base_remoteness + lat_bonus + lon_bonus)
        
        if remoteness >= 80:
            level = "very_remote"
            description = "Zone très isolée, faible présence humaine"
        elif remoteness >= 60:
            level = "remote"
            description = "Zone éloignée des activités humaines"
        elif remoteness >= 40:
            level = "moderate"
            description = "Zone à distance modérée des infrastructures"
        elif remoteness >= 20:
            level = "accessible"
            description = "Zone relativement accessible"
        else:
            level = "urban_fringe"
            description = "Zone en périphérie urbaine"
        
        return {
            "score": round(remoteness, 1),
            "level": level,
            "description": description,
            "components": {
                "base": round(base_remoteness, 1),
                "latitude_bonus": round(lat_bonus, 1),
                "longitude_bonus": round(lon_bonus, 1)
            }
        }
    
    def _determine_pressure_level(self, pressure_index: float) -> str:
        """Determine pressure level from index."""
        for level, info in self.PRESSURE_IMPACTS.items():
            if pressure_index < info["threshold"]:
                return level
        return "very_high"
    
    def _assess_hunting_impact(self, pressure_level: str) -> Dict[str, Any]:
        """Assess hunting impact from pressure level."""
        impact = self.PRESSURE_IMPACTS.get(pressure_level, self.PRESSURE_IMPACTS["moderate"])
        
        return {
            "pressure_level": pressure_level,
            "animal_behavior": impact["animal_behavior"],
            "hunting_strategy": impact["hunting_strategy"],
            "success_factor": impact["success_factor"],
            "overall_assessment": "Favorable" if impact["success_factor"] >= 1.0 else "Défavorable"
        }
    
    def _calculate_overall_score(
        self, 
        metrics: Dict[str, Any], 
        remoteness: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall pressure score for hunting."""
        hunting_suitability = metrics.get("hunting_suitability", 50)
        remoteness_score = remoteness.get("score", 50)
        
        # Weighted average
        total = (hunting_suitability * 0.6) + (remoteness_score * 0.4)
        
        return {
            "score": round(total, 1),
            "level": "excellent" if total >= 80 else "bon" if total >= 60 else "modéré" if total >= 40 else "faible",
            "components": {
                "hunting_suitability": hunting_suitability,
                "remoteness": remoteness_score
            },
            "interpretation": f"Zone {'favorable' if total >= 60 else 'acceptable' if total >= 40 else 'défavorable'} pour la chasse"
        }
    
    def _generate_recommendations(
        self, 
        pressure_level: str, 
        remoteness: Dict[str, Any]
    ) -> List[str]:
        """Generate pressure-based hunting recommendations."""
        recommendations = []
        
        if pressure_level in ["very_low", "low"]:
            recommendations.append("Zone à faible pression - Le gibier peut être actif en journée")
            recommendations.append("Excellente zone pour la chasse, toutes techniques applicables")
        elif pressure_level == "moderate":
            recommendations.append("Pression modérée - Privilégiez les heures du matin et du soir")
            recommendations.append("Éloignez-vous des routes et chemins principaux")
        elif pressure_level == "high":
            recommendations.append("Forte pression humaine - Chasse à l'aube et au crépuscule uniquement")
            recommendations.append("Maximisez la discrétion, évitez les bruits et mouvements brusques")
        else:
            recommendations.append("Zone très perturbée - Succès de chasse peu probable")
            recommendations.append("Envisagez de trouver une zone plus éloignée")
        
        # Remoteness-based recommendations
        remoteness_level = remoteness.get("level", "moderate")
        if remoteness_level in ["very_remote", "remote"]:
            recommendations.append("Zone isolée - Prévoyez équipement de sécurité et communication")
        elif remoteness_level == "urban_fringe":
            recommendations.append("Proximité urbaine - Vérifiez la réglementation locale de chasse")
        
        return recommendations
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get analyzer cache statistics."""
        total = self._cache_hits + self._cache_misses
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": self._cache_hits / total if total > 0 else 0
        }


# Singleton instance
pressure_analyzer = PressureAnalyzer()
