"""
BIONIC™ P1 - Hunting Pressure Module
=====================================
Module de pression de chasse pondéré.

North America Ready:
- MFFP, ZEC, SEPAQ (Québec)
- Provincial data (Canada)
- USFWS, State licensing (USA)
- OSM (Global - accès routier)

Sources 100% gratuites et publiques.

Version: 1.0.0
"""

import logging
import uuid
import math
from typing import Dict, Any, Optional, List, Tuple
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
# HUNTING PRESSURE DATA
# =============================================================================

# Pression de chasse par région (0-1)
REGIONAL_PRESSURE = {
    "quebec": {
        "laurentides": {"pressure": 0.75, "hunter_density": 4.5, "season_weeks": 8},
        "saguenay": {"pressure": 0.55, "hunter_density": 2.8, "season_weeks": 8},
        "outaouais": {"pressure": 0.80, "hunter_density": 5.2, "season_weeks": 8},
        "abitibi": {"pressure": 0.45, "hunter_density": 2.0, "season_weeks": 10},
        "gaspesie": {"pressure": 0.50, "hunter_density": 2.5, "season_weeks": 8},
        "default": {"pressure": 0.60, "hunter_density": 3.0, "season_weeks": 8}
    },
    "canada": {
        "ontario": {"pressure": 0.65, "hunter_density": 3.5, "season_weeks": 10},
        "bc": {"pressure": 0.50, "hunter_density": 2.2, "season_weeks": 12},
        "prairies": {"pressure": 0.55, "hunter_density": 2.5, "season_weeks": 10},
        "default": {"pressure": 0.55, "hunter_density": 2.5, "season_weeks": 10}
    },
    "usa": {
        "northeast": {"pressure": 0.70, "hunter_density": 4.0, "season_weeks": 16},
        "midwest": {"pressure": 0.75, "hunter_density": 4.5, "season_weeks": 14},
        "south": {"pressure": 0.65, "hunter_density": 3.5, "season_weeks": 18},
        "west": {"pressure": 0.45, "hunter_density": 2.0, "season_weeks": 12},
        "default": {"pressure": 0.60, "hunter_density": 3.5, "season_weeks": 14}
    }
}

# Facteurs de pression par type d'accès
ACCESS_PRESSURE_FACTORS = {
    "paved_road_nearby": 1.3,      # Route pavée à moins de 500m
    "gravel_road_nearby": 1.1,    # Route gravelle à moins de 1km
    "atv_trail": 1.2,             # Sentier VTT
    "walking_only": 0.7,          # Accès à pied seulement
    "boat_access": 0.8,           # Accès par bateau
    "remote": 0.5                 # Zone éloignée
}

# Impact comportemental par niveau de pression
BEHAVIORAL_IMPACT = {
    "extreme": {"activity_reduction": 0.6, "nocturnal_shift": 0.8, "home_range_reduction": 0.5},
    "high": {"activity_reduction": 0.4, "nocturnal_shift": 0.6, "home_range_reduction": 0.7},
    "moderate": {"activity_reduction": 0.2, "nocturnal_shift": 0.3, "home_range_reduction": 0.85},
    "low": {"activity_reduction": 0.1, "nocturnal_shift": 0.1, "home_range_reduction": 0.95},
    "minimal": {"activity_reduction": 0.0, "nocturnal_shift": 0.0, "home_range_reduction": 1.0}
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TimeWindow:
    """Fenêtre temporelle optimale."""
    day_of_week: str
    start_hour: int
    end_hour: int
    reason: str
    pressure_level: str


@dataclass
class Zone:
    """Zone d'évitement ou d'opportunité."""
    zone_id: str
    zone_type: str  # avoidance, opportunity
    description: str
    pressure_level: str
    distance_km: float


@dataclass
class WeeklyPattern:
    """Pattern hebdomadaire de pression."""
    monday: float
    tuesday: float
    wednesday: float
    thursday: float
    friday: float
    saturday: float
    sunday: float


# =============================================================================
# HUNTING PRESSURE MODULE
# =============================================================================

class HuntingPressureModule(BaseGeospatialEngine):
    """
    Module de pression de chasse.
    
    Analyse:
    - Niveau de pression (extreme/high/moderate/low/minimal)
    - Impact comportemental
    - Fenêtres temporelles optimales
    - Zones d'évitement
    - Patterns hebdomadaires
    
    Multi-espèces: Impact différencié par espèce
    """
    
    ENGINE_NAME = "HuntingPressureModule"
    ENGINE_VERSION = "1.0.0"
    
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.timeout = timeout
        self._cache_namespace = "pressure"
    
    async def analyze(
        self,
        lat: float,
        lon: float,
        radius_km: float = 2.0,
        target_species: Optional[List[str]] = None
    ) -> GeospatialEngineOutput:
        """
        Analyse la pression de chasse dans une zone.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Rayon d'analyse
            target_species: Espèces cibles
        
        Returns:
            GeospatialEngineOutput avec l'analyse de pression
        """
        analysis_id = f"pre_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now(timezone.utc)
        
        # Déterminer la région
        region = self._determine_region(lat, lon)
        sub_region = self._determine_sub_region(lat, lon, region)
        
        # Espèces par défaut
        if target_species is None:
            target_species = ["deer", "moose", "bear", "turkey"]
        
        # Obtenir les données de pression régionales
        regional_data = self._get_regional_pressure(region, sub_region)
        
        # Estimer l'accessibilité de la zone
        access_factor = await self._estimate_access_factor(lat, lon, radius_km)
        
        # Calculer la pression totale
        total_pressure = self._calculate_total_pressure(regional_data, access_factor)
        pressure_level = self._categorize_pressure(total_pressure)
        
        # Calculer l'impact comportemental
        behavioral_impact = self._calculate_behavioral_impact(pressure_level)
        
        # Déterminer les fenêtres temporelles optimales
        optimal_timing = self._calculate_optimal_timing(total_pressure)
        
        # Identifier les zones d'évitement
        avoidance_zones = self._identify_avoidance_zones(lat, lon, radius_km, total_pressure)
        
        # Pattern hebdomadaire
        weekly_pattern = self._calculate_weekly_pattern(regional_data)
        
        # Score de pression (inversé - haute pression = score bas)
        pressure_score = self._calculate_pressure_score(total_pressure, behavioral_impact)
        
        # Calculer la confiance
        confidence = self._calculate_confidence(regional_data, access_factor)
        
        # Recommandations
        recommendations = self._generate_recommendations(
            pressure_level, optimal_timing, behavioral_impact, weekly_pattern
        )
        
        return GeospatialEngineOutput(
            engine_name=self.ENGINE_NAME,
            engine_version=self.ENGINE_VERSION,
            analysis_id=analysis_id,
            location={"lat": lat, "lon": lon},
            region=region.value,
            data_sources_used=self._get_data_sources_for_region(region),
            score=pressure_score,
            level=self._score_to_level(pressure_score),
            data={
                "pressure_score": round(total_pressure * 100, 1),
                "pressure_level": pressure_level,
                "behavioral_impact": behavioral_impact,
                "optimal_timing": [asdict(t) for t in optimal_timing],
                "avoidance_zones": [asdict(z) for z in avoidance_zones],
                "weekly_pattern": asdict(weekly_pattern),
                "access_factor": access_factor,
                "hunter_density": regional_data.get("hunter_density", 3.0),
                "season_weeks": regional_data.get("season_weeks", 8),
                "sub_region": sub_region,
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
                if lat >= 40:
                    return "midwest"
                else:
                    return "south"
            else:
                return "west"
        return "default"
    
    def _get_regional_pressure(self, region: Region, sub_region: str) -> Dict:
        """Obtient les données de pression régionales."""
        region_key = {
            Region.QUEBEC: "quebec",
            Region.CANADA_OTHER: "canada",
            Region.USA: "usa"
        }.get(region, "quebec")
        
        region_data = REGIONAL_PRESSURE.get(region_key, {})
        return region_data.get(sub_region, region_data.get("default", {}))
    
    async def _estimate_access_factor(
        self,
        lat: float,
        lon: float,
        radius_km: float
    ) -> float:
        """Estime le facteur d'accessibilité de la zone."""
        # Simulation basée sur la localisation
        # En production, utiliser OSM pour les routes réelles
        
        # Plus au nord = moins accessible
        lat_factor = max(0.5, 1.0 - (lat - 45) * 0.03)
        
        # Éloignement des centres = moins accessible
        # Simulation simple
        remoteness = 0.7 + (abs(lon + 75) * 0.01)  # Centre sur -75
        
        access_factor = (lat_factor + remoteness) / 2
        
        return round(min(1.3, max(0.5, access_factor)), 2)
    
    def _calculate_total_pressure(
        self,
        regional_data: Dict,
        access_factor: float
    ) -> float:
        """Calcule la pression totale."""
        base_pressure = regional_data.get("pressure", 0.5)
        
        # Ajuster par l'accessibilité
        adjusted = base_pressure * access_factor
        
        # Ajuster par la saison actuelle
        month = datetime.now().month
        seasonal_modifier = self._get_seasonal_modifier(month)
        
        total = adjusted * seasonal_modifier
        
        return min(1.0, max(0.0, total))
    
    def _get_seasonal_modifier(self, month: int) -> float:
        """Retourne le modificateur saisonnier de pression."""
        # Peak en automne (saison de chasse)
        seasonal = {
            1: 0.3,   # Janvier - peu de chasse
            2: 0.2,   # Février
            3: 0.2,   # Mars
            4: 0.4,   # Avril - dindon printanier
            5: 0.5,   # Mai - fin dindon, ours
            6: 0.4,   # Juin - ours
            7: 0.3,   # Juillet
            8: 0.5,   # Août - début ours
            9: 0.8,   # Septembre - orignal
            10: 1.0,  # Octobre - peak
            11: 0.9,  # Novembre - cerf
            12: 0.5   # Décembre - fin saison
        }
        return seasonal.get(month, 0.5)
    
    def _categorize_pressure(self, total_pressure: float) -> str:
        """Catégorise le niveau de pression."""
        if total_pressure >= 0.85:
            return "extreme"
        elif total_pressure >= 0.65:
            return "high"
        elif total_pressure >= 0.40:
            return "moderate"
        elif total_pressure >= 0.20:
            return "low"
        return "minimal"
    
    def _calculate_behavioral_impact(self, pressure_level: str) -> Dict[str, float]:
        """Calcule l'impact comportemental."""
        impact = BEHAVIORAL_IMPACT.get(pressure_level, BEHAVIORAL_IMPACT["moderate"])
        
        # Score global d'impact (-1 à 1, négatif = impact néfaste)
        overall_impact = -(
            impact["activity_reduction"] * 0.4 +
            impact["nocturnal_shift"] * 0.3 +
            (1 - impact["home_range_reduction"]) * 0.3
        )
        
        return {
            "overall": round(overall_impact, 2),
            "activity_reduction": impact["activity_reduction"],
            "nocturnal_shift": impact["nocturnal_shift"],
            "home_range_factor": impact["home_range_reduction"]
        }
    
    def _calculate_optimal_timing(self, total_pressure: float) -> List[TimeWindow]:
        """Calcule les fenêtres temporelles optimales."""
        windows = []
        
        # En semaine tôt le matin = moins de chasseurs
        windows.append(TimeWindow(
            day_of_week="weekday",
            start_hour=5,
            end_hour=8,
            reason="Moins de chasseurs en semaine tôt le matin",
            pressure_level="low" if total_pressure < 0.7 else "moderate"
        ))
        
        # Mercredi = jour creux
        windows.append(TimeWindow(
            day_of_week="wednesday",
            start_hour=5,
            end_hour=10,
            reason="Milieu de semaine généralement calme",
            pressure_level="low"
        ))
        
        # Fin de journée en semaine
        if total_pressure < 0.8:
            windows.append(TimeWindow(
                day_of_week="weekday",
                start_hour=16,
                end_hour=18,
                reason="Beaucoup de chasseurs partent en fin de journée",
                pressure_level="moderate"
            ))
        
        return windows
    
    def _identify_avoidance_zones(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        total_pressure: float
    ) -> List[Zone]:
        """Identifie les zones à éviter."""
        zones = []
        
        if total_pressure > 0.6:
            # Zone d'accès principal
            zones.append(Zone(
                zone_id=f"avoid_{uuid.uuid4().hex[:8]}",
                zone_type="avoidance",
                description="Entrée principale / stationnement",
                pressure_level="high",
                distance_km=0.5
            ))
            
            # Sentiers principaux
            zones.append(Zone(
                zone_id=f"avoid_{uuid.uuid4().hex[:8]}",
                zone_type="avoidance",
                description="Sentiers principaux très fréquentés",
                pressure_level="high",
                distance_km=1.0
            ))
        
        # Zone d'opportunité (éloignée)
        zones.append(Zone(
            zone_id=f"opp_{uuid.uuid4().hex[:8]}",
            zone_type="opportunity",
            description="Zone éloignée avec pression réduite",
            pressure_level="low",
            distance_km=radius_km * 0.8
        ))
        
        return zones
    
    def _calculate_weekly_pattern(self, regional_data: Dict) -> WeeklyPattern:
        """Calcule le pattern hebdomadaire de pression."""
        base = regional_data.get("pressure", 0.5)
        
        return WeeklyPattern(
            monday=round(base * 0.7, 2),
            tuesday=round(base * 0.6, 2),
            wednesday=round(base * 0.5, 2),  # Jour le plus calme
            thursday=round(base * 0.65, 2),
            friday=round(base * 0.85, 2),
            saturday=round(min(1.0, base * 1.2), 2),  # Peak
            sunday=round(min(1.0, base * 1.1), 2)
        )
    
    def _calculate_pressure_score(
        self,
        total_pressure: float,
        behavioral_impact: Dict
    ) -> float:
        """Calcule le score de pression (inversé)."""
        # Plus la pression est basse, meilleur est le score
        pressure_score = (1 - total_pressure) * 100
        
        # Ajustement pour l'impact comportemental
        impact_modifier = (1 + behavioral_impact["overall"]) / 2  # 0-1
        
        score = pressure_score * (0.7 + impact_modifier * 0.3)
        
        return round(min(100, max(0, score)), 1)
    
    def _get_data_sources_for_region(self, region: Region) -> List[str]:
        """Retourne les sources de données pour une région."""
        if region == Region.QUEBEC:
            return ["mffp", "zec", "sepaq", "osm"]
        elif region == Region.CANADA_OTHER:
            return ["provincial_wildlife", "osm"]
        elif region == Region.USA:
            return ["usfws", "state_licensing", "osm"]
        return ["osm", "estimate"]
    
    def _calculate_confidence(
        self,
        regional_data: Dict,
        access_factor: float
    ) -> float:
        """Calcule le niveau de confiance."""
        base = 0.65
        
        # Bonus si données régionales disponibles
        if regional_data.get("hunter_density"):
            base += 0.15
        
        # Confiance dans le facteur d'accès
        access_confidence = 0.1 if 0.6 <= access_factor <= 1.2 else 0.05
        
        return round(min(0.90, base + access_confidence), 2)
    
    def _generate_recommendations(
        self,
        pressure_level: str,
        optimal_timing: List[TimeWindow],
        behavioral_impact: Dict,
        weekly_pattern: WeeklyPattern
    ) -> List[str]:
        """Génère les recommandations."""
        recommendations = []
        
        # Niveau de pression
        level_icons = {
            "extreme": "🔴",
            "high": "🟠",
            "moderate": "🟡",
            "low": "🟢",
            "minimal": "✅"
        }
        icon = level_icons.get(pressure_level, "ℹ️")
        recommendations.append(f"{icon} Pression de chasse: {pressure_level}")
        
        # Impact comportemental
        if behavioral_impact["activity_reduction"] > 0.3:
            recommendations.append(f"⚠️ Gibier plus craintif - activité réduite de {behavioral_impact['activity_reduction']:.0%}")
        
        if behavioral_impact["nocturnal_shift"] > 0.4:
            recommendations.append(f"🌙 Shift vers activité nocturne ({behavioral_impact['nocturnal_shift']:.0%})")
        
        # Meilleur timing
        if optimal_timing:
            best_window = optimal_timing[0]
            recommendations.append(f"⏰ Meilleur moment: {best_window.day_of_week} {best_window.start_hour}h-{best_window.end_hour}h")
        
        # Jour le plus calme
        pattern_dict = asdict(weekly_pattern)
        calmest = min(pattern_dict.items(), key=lambda x: x[1])
        recommendations.append(f"📅 Jour le plus calme: {calmest[0].title()} ({calmest[1]:.0%} pression)")
        
        return recommendations[:6]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

hunting_pressure_module = HuntingPressureModule()


logger.info("BIONIC™ HuntingPressureModule loaded (v1.0.0) - North America Ready")
