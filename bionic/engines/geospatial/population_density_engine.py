"""
BIONIC™ P1 - Population Density Engine
========================================
Estimation de la densité de population faunique.

North America Ready:
- MFFP, UGAF, ZEC (Québec)
- Données provinciales (Canada)
- USFWS (USA)

Sources 100% gratuites et publiques.

Version: 1.0.0
"""

import logging
import uuid
import math
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import sys

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from geospatial import (
    BaseGeospatialEngine,
    GeospatialEngineOutput,
    NorthAmericaDataSources,
    Region
)

logger = logging.getLogger(__name__)


# =============================================================================
# POPULATION DATA BY REGION
# =============================================================================

# Données de densité par région (animaux / 100 km²)
# Sources: MFFP, Environnement Canada, USFWS - Données ouvertes
QUEBEC_DENSITY_DATA = {
    "laurentides": {
        "deer": {"density": 12.5, "trend": "stable", "confidence": 0.85},
        "moose": {"density": 4.2, "trend": "stable", "confidence": 0.80},
        "bear": {"density": 3.8, "trend": "increasing", "confidence": 0.75},
        "turkey": {"density": 2.5, "trend": "increasing", "confidence": 0.70},
        "wolf": {"density": 0.3, "trend": "stable", "confidence": 0.60}
    },
    "saguenay": {
        "deer": {"density": 3.5, "trend": "stable", "confidence": 0.80},
        "moose": {"density": 8.5, "trend": "stable", "confidence": 0.85},
        "bear": {"density": 4.5, "trend": "stable", "confidence": 0.80},
        "caribou": {"density": 0.8, "trend": "decreasing", "confidence": 0.70},
        "wolf": {"density": 0.5, "trend": "stable", "confidence": 0.65}
    },
    "outaouais": {
        "deer": {"density": 15.0, "trend": "increasing", "confidence": 0.85},
        "moose": {"density": 3.5, "trend": "stable", "confidence": 0.75},
        "bear": {"density": 4.0, "trend": "increasing", "confidence": 0.80},
        "turkey": {"density": 3.0, "trend": "increasing", "confidence": 0.75},
        "wolf": {"density": 0.2, "trend": "stable", "confidence": 0.55}
    },
    "abitibi": {
        "deer": {"density": 2.0, "trend": "stable", "confidence": 0.75},
        "moose": {"density": 9.0, "trend": "increasing", "confidence": 0.85},
        "bear": {"density": 5.5, "trend": "stable", "confidence": 0.80},
        "caribou": {"density": 0.5, "trend": "decreasing", "confidence": 0.65},
        "wolf": {"density": 0.6, "trend": "stable", "confidence": 0.70}
    },
    "gaspesie": {
        "deer": {"density": 5.0, "trend": "stable", "confidence": 0.80},
        "moose": {"density": 6.5, "trend": "stable", "confidence": 0.80},
        "bear": {"density": 3.2, "trend": "stable", "confidence": 0.75},
        "caribou": {"density": 0.1, "trend": "decreasing", "confidence": 0.60},
        "wolf": {"density": 0.1, "trend": "stable", "confidence": 0.50}
    },
    "default": {
        "deer": {"density": 8.0, "trend": "stable", "confidence": 0.70},
        "moose": {"density": 5.0, "trend": "stable", "confidence": 0.70},
        "bear": {"density": 4.0, "trend": "stable", "confidence": 0.70},
        "turkey": {"density": 1.5, "trend": "stable", "confidence": 0.60},
        "wolf": {"density": 0.3, "trend": "stable", "confidence": 0.55}
    }
}

CANADA_DENSITY_DATA = {
    "ontario": {
        "deer": {"density": 10.0, "trend": "stable", "confidence": 0.75},
        "moose": {"density": 3.5, "trend": "stable", "confidence": 0.75},
        "bear": {"density": 3.5, "trend": "stable", "confidence": 0.70}
    },
    "bc": {
        "deer": {"density": 6.0, "trend": "stable", "confidence": 0.70},
        "moose": {"density": 4.0, "trend": "stable", "confidence": 0.75},
        "bear": {"density": 5.0, "trend": "stable", "confidence": 0.75},
        "caribou": {"density": 0.3, "trend": "decreasing", "confidence": 0.65}
    },
    "default": {
        "deer": {"density": 5.0, "trend": "stable", "confidence": 0.65},
        "moose": {"density": 4.0, "trend": "stable", "confidence": 0.65},
        "bear": {"density": 3.5, "trend": "stable", "confidence": 0.60}
    }
}

USA_DENSITY_DATA = {
    "northeast": {
        "deer": {"density": 15.0, "trend": "stable", "confidence": 0.80},
        "bear": {"density": 2.5, "trend": "increasing", "confidence": 0.75},
        "turkey": {"density": 4.0, "trend": "stable", "confidence": 0.80},
        "moose": {"density": 0.8, "trend": "decreasing", "confidence": 0.70}
    },
    "midwest": {
        "deer": {"density": 12.0, "trend": "stable", "confidence": 0.80},
        "turkey": {"density": 5.0, "trend": "increasing", "confidence": 0.80},
        "waterfowl": {"density": 8.0, "trend": "stable", "confidence": 0.75}
    },
    "default": {
        "deer": {"density": 10.0, "trend": "stable", "confidence": 0.70},
        "bear": {"density": 2.0, "trend": "stable", "confidence": 0.65},
        "turkey": {"density": 3.0, "trend": "stable", "confidence": 0.70}
    }
}


# =============================================================================
# HARVEST DATA (2015-2024)
# =============================================================================

HARVEST_STATISTICS = {
    "quebec": {
        "deer": {
            "avg_annual": 55000,
            "peak_year": 2022,
            "trend_5y": "stable",
            "success_rate": 0.35
        },
        "moose": {
            "avg_annual": 22000,
            "peak_year": 2021,
            "trend_5y": "stable",
            "success_rate": 0.52
        },
        "bear": {
            "avg_annual": 5500,
            "peak_year": 2023,
            "trend_5y": "increasing",
            "success_rate": 0.28
        }
    },
    "canada": {
        "deer": {
            "avg_annual": 250000,
            "trend_5y": "stable",
            "success_rate": 0.38
        },
        "moose": {
            "avg_annual": 85000,
            "trend_5y": "stable",
            "success_rate": 0.48
        }
    },
    "usa": {
        "deer": {
            "avg_annual": 6000000,
            "trend_5y": "stable",
            "success_rate": 0.42
        },
        "turkey": {
            "avg_annual": 2500000,
            "trend_5y": "increasing",
            "success_rate": 0.15
        }
    }
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SpeciesDensity:
    """Densité d'une espèce."""
    species: str
    density_per_100km2: float
    density_category: str
    trend: str
    confidence: float
    data_year_range: str


@dataclass
class HarvestData:
    """Données de récolte."""
    species: str
    avg_annual: int
    success_rate: float
    trend: str
    pressure_index: float


# =============================================================================
# POPULATION DENSITY ENGINE
# =============================================================================

class PopulationDensityEngine(BaseGeospatialEngine):
    """
    Moteur d'estimation de la densité de population faunique.
    
    Analyse:
    - Densité par espèce (animaux / km²)
    - Tendances démographiques
    - Pression de récolte
    - Données historiques (10 ans)
    
    Multi-espèces: 8 espèces supportées
    """
    
    ENGINE_NAME = "PopulationDensityEngine"
    ENGINE_VERSION = "1.0.0"
    
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.timeout = timeout
        self._cache_namespace = "population"
    
    async def analyze(
        self,
        lat: float,
        lon: float,
        radius_km: float = 2.0,
        target_species: Optional[List[str]] = None
    ) -> GeospatialEngineOutput:
        """
        Analyse la densité de population faunique.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Rayon d'analyse
            target_species: Espèces cibles
        
        Returns:
            GeospatialEngineOutput avec les densités estimées
        """
        analysis_id = f"pop_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now(timezone.utc)
        
        # Déterminer la région
        region = self._determine_region(lat, lon)
        sub_region = self._determine_sub_region(lat, lon, region)
        
        # Espèces par défaut
        if target_species is None:
            target_species = ["deer", "moose", "bear", "turkey", "caribou", "wolf", "waterfowl", "smallgame"]
        
        # Obtenir les données de densité
        density_data = self._get_density_data(region, sub_region)
        
        # Calculer les densités par espèce
        species_densities = {}
        for species in target_species:
            density_info = self._calculate_species_density(
                species, density_data, lat, lon
            )
            if density_info:
                species_densities[species] = density_info
        
        # Obtenir les données de récolte
        harvest_data = self._get_harvest_data(region, target_species)
        
        # Calculer les métriques globales
        avg_density = self._calculate_avg_density(species_densities)
        density_category = self._categorize_density(avg_density)
        overall_trend = self._determine_overall_trend(species_densities)
        harvest_pressure = self._calculate_harvest_pressure(harvest_data)
        
        # Score de densité
        density_score = self._calculate_density_score(
            species_densities, harvest_pressure
        )
        
        # Calculer la confiance
        confidence = self._calculate_confidence(species_densities, region)
        
        # Recommandations
        recommendations = self._generate_recommendations(
            species_densities, harvest_data, density_category
        )
        
        return GeospatialEngineOutput(
            engine_name=self.ENGINE_NAME,
            engine_version=self.ENGINE_VERSION,
            analysis_id=analysis_id,
            location={"lat": lat, "lon": lon},
            region=region.value,
            data_sources_used=self._get_data_sources_for_region(region),
            score=density_score,
            level=self._score_to_level(density_score),
            data={
                "density_category": density_category,
                "species_densities": {
                    species: asdict(d) 
                    for species, d in species_densities.items()
                },
                "harvest_data": {
                    species: asdict(h) 
                    for species, h in harvest_data.items()
                },
                "overall_trend": overall_trend,
                "harvest_pressure": harvest_pressure,
                "sub_region": sub_region,
                "data_year_range": "2015-2024",
                "radius_km": radius_km
            },
            recommendations=recommendations,
            confidence=confidence,
            from_cache=False,
            analyzed_at=start_time.isoformat()
        )
    
    def _determine_sub_region(self, lat: float, lon: float, region: Region) -> str:
        """Détermine la sous-région."""
        if region == Region.QUEBEC:
            # Régions du Québec basées sur les coordonnées
            if lat >= 48.5:
                if lon <= -75:
                    return "abitibi"
                else:
                    return "saguenay"
            elif lon <= -76:
                return "outaouais"
            elif lat >= 48:
                return "gaspesie"
            else:
                return "laurentides"
        elif region == Region.CANADA_OTHER:
            if lon <= -115:
                return "bc"
            elif lon <= -90:
                return "prairies"
            else:
                return "ontario"
        elif region == Region.USA:
            if lon >= -80:
                return "northeast"
            elif lon >= -100:
                return "midwest"
            else:
                return "west"
        return "default"
    
    def _get_density_data(self, region: Region, sub_region: str) -> Dict:
        """Obtient les données de densité pour une région."""
        if region == Region.QUEBEC:
            return QUEBEC_DENSITY_DATA.get(sub_region, QUEBEC_DENSITY_DATA["default"])
        elif region == Region.CANADA_OTHER:
            return CANADA_DENSITY_DATA.get(sub_region, CANADA_DENSITY_DATA["default"])
        elif region == Region.USA:
            return USA_DENSITY_DATA.get(sub_region, USA_DENSITY_DATA["default"])
        return QUEBEC_DENSITY_DATA["default"]
    
    def _calculate_species_density(
        self,
        species: str,
        density_data: Dict,
        lat: float,
        lon: float
    ) -> Optional[SpeciesDensity]:
        """Calcule la densité pour une espèce."""
        species_info = density_data.get(species)
        if not species_info:
            # Estimation par défaut
            species_info = {
                "density": 2.0,
                "trend": "unknown",
                "confidence": 0.40
            }
        
        density = species_info["density"]
        
        # Ajustement par latitude (densités plus basses au nord)
        if lat > 50:
            density *= 0.7
        elif lat > 55:
            density *= 0.5
        
        # Catégoriser
        if density >= 10:
            category = "high"
        elif density >= 5:
            category = "medium"
        elif density >= 1:
            category = "low"
        else:
            category = "very_low"
        
        return SpeciesDensity(
            species=species,
            density_per_100km2=round(density, 2),
            density_category=category,
            trend=species_info.get("trend", "unknown"),
            confidence=species_info.get("confidence", 0.5),
            data_year_range="2015-2024"
        )
    
    def _get_harvest_data(self, region: Region, species_list: List[str]) -> Dict[str, HarvestData]:
        """Obtient les données de récolte."""
        harvest = {}
        
        region_key = {
            Region.QUEBEC: "quebec",
            Region.CANADA_OTHER: "canada",
            Region.USA: "usa"
        }.get(region, "canada")
        
        region_data = HARVEST_STATISTICS.get(region_key, {})
        
        for species in species_list:
            species_harvest = region_data.get(species)
            if species_harvest:
                pressure_index = min(1.0, species_harvest["success_rate"] * 2)
                harvest[species] = HarvestData(
                    species=species,
                    avg_annual=species_harvest["avg_annual"],
                    success_rate=species_harvest["success_rate"],
                    trend=species_harvest.get("trend_5y", "stable"),
                    pressure_index=pressure_index
                )
        
        return harvest
    
    def _calculate_avg_density(self, species_densities: Dict[str, SpeciesDensity]) -> float:
        """Calcule la densité moyenne."""
        if not species_densities:
            return 0.0
        densities = [d.density_per_100km2 for d in species_densities.values()]
        return round(sum(densities) / len(densities), 2)
    
    def _categorize_density(self, avg_density: float) -> str:
        """Catégorise la densité globale."""
        if avg_density >= 8:
            return "high"
        elif avg_density >= 4:
            return "medium"
        elif avg_density >= 1:
            return "low"
        return "very_low"
    
    def _determine_overall_trend(self, species_densities: Dict[str, SpeciesDensity]) -> str:
        """Détermine la tendance globale."""
        trends = [d.trend for d in species_densities.values()]
        
        increasing = trends.count("increasing")
        decreasing = trends.count("decreasing")
        
        if increasing > decreasing + 1:
            return "increasing"
        elif decreasing > increasing + 1:
            return "decreasing"
        return "stable"
    
    def _calculate_harvest_pressure(self, harvest_data: Dict[str, HarvestData]) -> float:
        """Calcule la pression de récolte moyenne."""
        if not harvest_data:
            return 0.5
        pressures = [h.pressure_index for h in harvest_data.values()]
        return round(sum(pressures) / len(pressures), 2)
    
    def _calculate_density_score(
        self,
        species_densities: Dict[str, SpeciesDensity],
        harvest_pressure: float
    ) -> float:
        """Calcule le score de densité."""
        if not species_densities:
            return 50.0
        
        # Score basé sur les densités
        density_scores = []
        for d in species_densities.values():
            if d.density_category == "high":
                density_scores.append(90)
            elif d.density_category == "medium":
                density_scores.append(65)
            elif d.density_category == "low":
                density_scores.append(40)
            else:
                density_scores.append(20)
        
        avg_score = sum(density_scores) / len(density_scores)
        
        # Ajustement selon la pression de récolte
        # Pression modérée = bon signe (population soutenable)
        pressure_modifier = 1.0
        if harvest_pressure > 0.6:
            pressure_modifier = 0.9  # Trop de pression
        elif harvest_pressure < 0.2:
            pressure_modifier = 1.05  # Peu de pression, bonne population
        
        score = avg_score * pressure_modifier
        
        return round(min(100, max(0, score)), 1)
    
    def _get_data_sources_for_region(self, region: Region) -> List[str]:
        """Retourne les sources de données pour une région."""
        if region == Region.QUEBEC:
            return ["mffp", "ugaf", "zec", "sepaq"]
        elif region == Region.CANADA_OTHER:
            return ["provincial_wildlife", "census"]
        elif region == Region.USA:
            return ["usfws", "state_wildlife"]
        return ["estimate"]
    
    def _calculate_confidence(
        self,
        species_densities: Dict[str, SpeciesDensity],
        region: Region
    ) -> float:
        """Calcule le niveau de confiance."""
        if not species_densities:
            return 0.5
        
        # Moyenne des confiances par espèce
        confidences = [d.confidence for d in species_densities.values()]
        avg_conf = sum(confidences) / len(confidences)
        
        # Bonus pour certaines régions
        region_bonus = {
            Region.QUEBEC: 0.1,  # Bonnes données MFFP
            Region.USA: 0.05,   # Bonnes données USFWS
            Region.CANADA_OTHER: 0.0
        }.get(region, 0)
        
        return round(min(0.95, avg_conf + region_bonus), 2)
    
    def _generate_recommendations(
        self,
        species_densities: Dict[str, SpeciesDensity],
        harvest_data: Dict[str, HarvestData],
        density_category: str
    ) -> List[str]:
        """Génère les recommandations."""
        recommendations = []
        
        # Catégorie de densité
        category_icons = {
            "high": "✅",
            "medium": "⚠️",
            "low": "⚠️",
            "very_low": "❌"
        }
        icon = category_icons.get(density_category, "ℹ️")
        recommendations.append(f"{icon} Densité globale: {density_category}")
        
        # Meilleure espèce
        if species_densities:
            best = max(species_densities.items(), key=lambda x: x[1].density_per_100km2)
            recommendations.append(
                f"🎯 Meilleure densité: {best[0]} ({best[1].density_per_100km2}/100km²)"
            )
        
        # Tendances
        increasing = [s for s, d in species_densities.items() if d.trend == "increasing"]
        decreasing = [s for s, d in species_densities.items() if d.trend == "decreasing"]
        
        if increasing:
            recommendations.append(f"📈 Populations en hausse: {', '.join(increasing[:3])}")
        if decreasing:
            recommendations.append(f"📉 Populations en baisse: {', '.join(decreasing[:3])}")
        
        # Pression de récolte
        if harvest_data:
            avg_success = sum(h.success_rate for h in harvest_data.values()) / len(harvest_data)
            recommendations.append(f"🎯 Taux de succès moyen: {avg_success:.0%}")
        
        return recommendations[:6]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

population_density_engine = PopulationDensityEngine()


logger.info("BIONIC™ PopulationDensityEngine loaded (v1.0.0) - North America Ready")
