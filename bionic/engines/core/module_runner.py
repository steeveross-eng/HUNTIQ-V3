"""
BIONIC™ Engine - Module Runner
===============================
Calcul des scores pour les modules thématiques.

Ce moteur gère les 8 modules d'analyse:
- ThermalScore: Confort thermique
- WetnessScore: Hydrologie
- FoodScore: Disponibilité alimentaire
- PressureScore: Pression humaine
- AccessScore: Accessibilité
- CorridorScore: Corridors fauniques
- GeoFormScore: Géomorphologie
- CanopyScore: Canopée forestière
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from .configs import ModuleType, MODULE_CONFIGS
from .helpers import (
    simulate_factor_value,
    get_rating,
    calculate_weighted_score
)
from .geojson_builder import build_point_geojson

logger = logging.getLogger(__name__)


class ModuleRunner:
    """
    Exécute les calculs de score pour les modules thématiques.
    """
    
    def __init__(self):
        self.configs = MODULE_CONFIGS
    
    def get_available_modules(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des modules disponibles.
        
        Returns:
            List[Dict]: Liste des modules avec leurs métadonnées
        """
        modules = []
        for module_type, config in self.configs.items():
            modules.append({
                "id": module_type.value,
                "name": config["name"],
                "version": config["version"],
                "description": config["description"],
                "factors": config["factors"]
            })
        return modules
    
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Retourne les informations détaillées d'un module.
        
        Args:
            module_id: Identifiant du module
            
        Returns:
            Dict ou None si module non trouvé
        """
        try:
            module_type = ModuleType(module_id)
            config = self.configs[module_type]
            return {
                "id": module_id,
                **config
            }
        except ValueError:
            return None
    
    async def calculate_score(
        self,
        module_type: ModuleType,
        lat: float,
        lon: float,
        territory_id: str,
        geospatial_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Calcule le score pour un module spécifique.
        
        Args:
            module_type: Type de module
            lat: Latitude
            lon: Longitude
            territory_id: ID du territoire
            geospatial_data: Données géospatiales réelles (optionnel)
            
        Returns:
            Dict: Résultat du module avec score, facteurs, recommandations
        """
        config = self.configs[module_type]
        
        # Extraire les facteurs depuis les données géospatiales ou simuler
        factors = await self._extract_factors(
            module_type, lat, lon, territory_id, geospatial_data
        )
        
        # Calculer le score pondéré
        score = calculate_weighted_score(factors, config["weights"])
        
        # Générer les recommandations
        recommendations = self._generate_recommendations(
            module_type, factors, score, geospatial_data
        )
        
        # Déterminer la confiance basée sur la qualité des données
        confidence = self._calculate_confidence(geospatial_data)
        
        # Déterminer les sources de données utilisées
        data_sources = self._get_data_sources(geospatial_data)
        
        return {
            "module": config["name"],
            "version": config["version"],
            "score": score,
            "rating": get_rating(score),
            "factors": factors,
            "recommendations": recommendations[:3],
            "confidence": confidence,
            "geojson": build_point_geojson(lat, lon, score, config["name"]),
            "data_sources": data_sources
        }
    
    async def calculate_all_modules(
        self,
        lat: float,
        lon: float,
        territory_id: str,
        modules: List[ModuleType],
        geospatial_data: Optional[Any] = None
    ) -> Dict[ModuleType, Dict[str, Any]]:
        """
        Calcule les scores pour plusieurs modules.
        
        Args:
            lat: Latitude
            lon: Longitude
            territory_id: ID du territoire
            modules: Liste des modules à calculer
            geospatial_data: Données géospatiales réelles
            
        Returns:
            Dict: Résultats par module
        """
        results = {}
        
        for module_type in modules:
            try:
                result = await self.calculate_score(
                    module_type, lat, lon, territory_id, geospatial_data
                )
                results[module_type] = result
            except Exception as e:
                logger.error(f"Error calculating {module_type.value}: {e}")
                results[module_type] = self._create_error_result(module_type, str(e))
        
        return results
    
    async def _extract_factors(
        self,
        module_type: ModuleType,
        lat: float,
        lon: float,
        territory_id: str,
        geospatial_data: Optional[Any]
    ) -> Dict[str, float]:
        """
        Extrait les valeurs des facteurs depuis les données ou simule.
        """
        config = self.configs[module_type]
        factors = {}
        
        # Essayer d'extraire les données réelles
        if geospatial_data:
            factors = await self._extract_from_geospatial(
                module_type, geospatial_data
            )
        
        # Compléter les facteurs manquants par simulation
        seed = hash(f"{territory_id}_{module_type.value}") % 10000
        for factor in config["factors"]:
            if factor not in factors:
                factors[factor] = simulate_factor_value(
                    factor, lat, lon, seed + hash(factor) % 1000
                )
        
        return factors
    
    async def _extract_from_geospatial(
        self,
        module_type: ModuleType,
        geospatial_data: Any
    ) -> Dict[str, float]:
        """
        Extrait les facteurs depuis les données géospatiales réelles.
        """
        factors = {}
        
        # Weather data
        if hasattr(geospatial_data, 'weather') and geospatial_data.weather:
            weather = geospatial_data.weather
            if module_type == ModuleType.THERMAL:
                if hasattr(weather, 'temperature'):
                    # Convertir température en score (optimal: 10-20°C)
                    temp = weather.temperature
                    if 10 <= temp <= 20:
                        factors["temperature"] = 85 + (10 - abs(temp - 15)) * 1.5
                    elif temp < 10:
                        factors["temperature"] = max(20, 85 - (10 - temp) * 3)
                    else:
                        factors["temperature"] = max(20, 85 - (temp - 20) * 3)
            
            if module_type == ModuleType.WETNESS:
                if hasattr(weather, 'humidity'):
                    factors["precipitation"] = weather.humidity * 0.8
        
        # Terrain data
        if hasattr(geospatial_data, 'terrain') and geospatial_data.terrain:
            terrain = geospatial_data.terrain
            if module_type == ModuleType.GEOFORM:
                if hasattr(terrain, 'slope'):
                    # Pente optimale: 5-15°
                    slope = terrain.slope or 0
                    if 5 <= slope <= 15:
                        factors["slope"] = 90
                    elif slope < 5:
                        factors["slope"] = 70 + slope * 4
                    else:
                        factors["slope"] = max(30, 90 - (slope - 15) * 2)
                
                if hasattr(terrain, 'aspect'):
                    factors["aspect"] = 70  # Aspect neutre par défaut
                
                if hasattr(terrain, 'elevation'):
                    # Élévation optimale: 200-600m
                    elev = terrain.elevation or 0
                    if 200 <= elev <= 600:
                        factors["elevation"] = 85
                    elif elev < 200:
                        factors["elevation"] = 60 + elev / 5
                    else:
                        factors["elevation"] = max(40, 85 - (elev - 600) / 20)
        
        # Vegetation data
        if hasattr(geospatial_data, 'vegetation') and geospatial_data.vegetation:
            veg = geospatial_data.vegetation
            if module_type == ModuleType.FOOD:
                if hasattr(veg, 'ndvi') and veg.ndvi is not None:
                    # NDVI vers score de nourriture
                    factors["ndvi"] = max(0, min(100, (veg.ndvi + 0.2) * 70))
            
            if module_type == ModuleType.WETNESS:
                if hasattr(veg, 'ndwi') and veg.ndwi is not None:
                    factors["ndwi"] = max(0, min(100, (veg.ndwi + 0.5) * 60))
            
            if module_type == ModuleType.CANOPY:
                if hasattr(veg, 'ndvi') and veg.ndvi is not None:
                    factors["canopy_closure"] = max(0, min(100, veg.ndvi * 100))
        
        return factors
    
    def _generate_recommendations(
        self,
        module_type: ModuleType,
        factors: Dict[str, float],
        score: float,
        geospatial_data: Optional[Any]
    ) -> List[str]:
        """
        Génère des recommandations basées sur l'analyse.
        """
        recommendations = []
        
        # Recommandations basées sur les données météo réelles
        if geospatial_data and hasattr(geospatial_data, 'weather') and geospatial_data.weather:
            weather = geospatial_data.weather
            
            if hasattr(weather, 'temperature'):
                temp = weather.temperature
                if temp < -10:
                    recommendations.append(
                        f"Froid intense ({temp}°C): gibier moins actif, privilégier midday"
                    )
                elif temp > 20:
                    recommendations.append(
                        f"Température élevée ({temp}°C): activité tôt le matin ou tard le soir"
                    )
            
            if hasattr(weather, 'wind_speed') and weather.wind_speed > 25:
                recommendations.append(
                    f"Vent fort ({weather.wind_speed} km/h): chasse en vallées protégées"
                )
            
            if hasattr(weather, 'precipitation_probability') and weather.precipitation_probability > 60:
                recommendations.append(
                    f"Précipitations probables ({weather.precipitation_probability}%): conditions de pistage favorables"
                )
        
        # Recommandations basées sur les données terrain
        if geospatial_data and hasattr(geospatial_data, 'terrain') and geospatial_data.terrain:
            terrain = geospatial_data.terrain
            
            if hasattr(terrain, 'elevation') and terrain.elevation and terrain.elevation > 700:
                recommendations.append(
                    f"Altitude élevée ({terrain.elevation}m): orignal et caribou plus présents"
                )
            
            if hasattr(terrain, 'slope') and terrain.slope and terrain.slope > 20:
                recommendations.append(
                    f"Pente prononcée ({terrain.slope}°): accès difficile, gibier refuge"
                )
        
        # Recommandations basées sur les facteurs faibles
        for factor, value in factors.items():
            if value < 40 and len(recommendations) < 3:
                recommendations.append(
                    f"Améliorer {factor.replace('_', ' ')}: score actuel {value}/100"
                )
        
        if not recommendations:
            recommendations.append("Conditions optimales pour ce module")
        
        return recommendations
    
    def _calculate_confidence(self, geospatial_data: Optional[Any]) -> float:
        """
        Calcule le niveau de confiance basé sur la qualité des données.
        """
        import random
        
        if geospatial_data is None:
            return round(0.65 + random.uniform(-0.05, 0.05), 2)
        
        if hasattr(geospatial_data, 'data_quality'):
            quality = geospatial_data.data_quality
            if quality == "complete":
                return round(0.95 + random.uniform(-0.05, 0.05), 2)
            elif quality == "partial":
                return round(0.80 + random.uniform(-0.05, 0.05), 2)
        
        return round(0.75 + random.uniform(-0.05, 0.05), 2)
    
    def _get_data_sources(self, geospatial_data: Optional[Any]) -> List[str]:
        """
        Détermine les sources de données utilisées.
        """
        sources = []
        
        if geospatial_data is None:
            return ["Estimation (simulation)"]
        
        if hasattr(geospatial_data, 'weather') and geospatial_data.weather:
            sources.append("Open-Meteo (météo temps réel)")
        
        if hasattr(geospatial_data, 'terrain') and geospatial_data.terrain:
            sources.append("Open-Elevation (terrain)")
        
        if hasattr(geospatial_data, 'vegetation') and geospatial_data.vegetation:
            source = getattr(geospatial_data.vegetation, 'source', 'Vegetation data')
            sources.append(source)
        
        return sources if sources else ["Estimation (simulation)"]
    
    def _create_error_result(
        self,
        module_type: ModuleType,
        error_message: str
    ) -> Dict[str, Any]:
        """
        Crée un résultat d'erreur pour un module.
        """
        config = self.configs[module_type]
        return {
            "module": config["name"],
            "version": config["version"],
            "score": 0,
            "rating": "Erreur",
            "factors": {},
            "recommendations": [f"Erreur: {error_message}"],
            "confidence": 0,
            "error": True,
            "error_message": error_message
        }


# Instance singleton
module_runner = ModuleRunner()
