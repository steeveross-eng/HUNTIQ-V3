"""
BIONIC™ Engine - Core Orchestrator
====================================
Orchestrateur principal qui coordonne tous les moteurs d'analyse.

Ce module est le point d'entrée unique pour toutes les analyses BIONIC™.
Il délègue le travail aux moteurs spécialisés et agrège les résultats.

Moteurs orchestrés:
- ModuleRunner: Calcul des scores thématiques (8 modules)
- SpeciesEngine: Calcul des scores d'habitat (6 espèces)
- PredictionEngine: Prédictions IA
- TemporalEngine: Analyses temporelles
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from .configs import ModuleType, SpeciesType, SeasonType
from .helpers import get_current_season, get_rating
from .module_runner import module_runner, ModuleRunner
from .species_engine import species_engine, SpeciesEngine
from .prediction_engine import prediction_engine, PredictionEngine
from .temporal_engine import temporal_engine, TemporalEngine
from .geojson_builder import build_analysis_geojson

logger = logging.getLogger(__name__)


class BionicOrchestrator:
    """
    Orchestrateur central BIONIC™.
    
    Coordonne les différents moteurs pour produire des analyses
    de territoire complètes et cohérentes.
    """
    
    def __init__(self):
        self.module_runner = module_runner
        self.species_engine = species_engine
        self.prediction_engine = prediction_engine
        self.temporal_engine = temporal_engine
        
        self._version = "BIONIC_CORE 2.0"
    
    @property
    def version(self) -> str:
        return self._version
    
    async def analyze_territory(
        self,
        territory_id: str,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        modules: Optional[List[ModuleType]] = None,
        species: Optional[List[SpeciesType]] = None,
        include_predictions: bool = True,
        include_temporal: bool = True,
        geospatial_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Exécute une analyse complète de territoire.
        
        Cette méthode orchestre tous les moteurs BIONIC™ pour produire
        une analyse exhaustive du territoire.
        
        Args:
            territory_id: Identifiant unique du territoire
            latitude: Latitude du centre
            longitude: Longitude du centre
            radius_km: Rayon d'analyse en km
            modules: Liste des modules à exécuter (tous si None)
            species: Liste des espèces à analyser (défaut: moose, deer, bear)
            include_predictions: Inclure les prédictions IA
            include_temporal: Inclure l'analyse temporelle
            geospatial_data: Données géospatiales réelles (optionnel)
            
        Returns:
            Dict: Résultat complet de l'analyse
        """
        logger.info(f"Starting territory analysis for {territory_id} at ({latitude}, {longitude})")
        
        # Définir les modules et espèces par défaut
        if modules is None:
            modules = list(ModuleType)
        
        if species is None:
            species = [SpeciesType.MOOSE, SpeciesType.DEER, SpeciesType.BEAR]
        
        # Obtenir la saison actuelle
        season = get_current_season()
        
        # Déterminer la qualité des données
        data_quality = "complete" if geospatial_data and hasattr(geospatial_data, 'data_quality') else "simulated"
        if geospatial_data and hasattr(geospatial_data, 'data_quality'):
            data_quality = geospatial_data.data_quality
        
        # Initialiser le résultat
        results = {
            "territory_id": territory_id,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "season": season.value,
            "data_quality": data_quality,
            "data_sources": [],
            "modules": {},
            "species": {},
            "predictions": None,
            "temporal": None,
            "overall_score": 0,
            "overall_rating": "",
            "real_conditions": {},
            "engine_version": self._version
        }
        
        # Extraire les conditions réelles si disponibles
        results["real_conditions"] = self._extract_real_conditions(geospatial_data)
        results["data_sources"] = self._get_data_sources(geospatial_data)
        
        # 1. Calculer les scores des modules
        logger.debug(f"Calculating {len(modules)} module scores")
        module_results = await self.module_runner.calculate_all_modules(
            latitude, longitude, territory_id, modules, geospatial_data
        )
        
        # Convertir en format de sortie
        module_scores = {}
        for module_type, result in module_results.items():
            results["modules"][module_type.value] = result
            module_scores[module_type] = result.get("score", 50)
        
        # 2. Calculer les scores des espèces
        logger.debug(f"Calculating {len(species)} species scores")
        species_scores = {}
        species_results = await self.species_engine.calculate_all_species(
            latitude, longitude, module_scores, territory_id, species
        )
        
        for species_type, result in species_results.items():
            results["species"][species_type.value] = result
            species_scores[species_type] = result.get("score", 50)
        
        # 3. Générer les prédictions IA
        if include_predictions and species_scores:
            logger.debug("Generating AI predictions")
            predictions = await self.prediction_engine.generate_predictions(
                latitude, longitude, species_scores, territory_id, geospatial_data
            )
            results["predictions"] = predictions
        
        # 4. Générer l'analyse temporelle
        if include_temporal:
            logger.debug("Generating temporal analysis")
            temporal = await self.temporal_engine.generate_analysis(
                latitude, longitude, territory_id
            )
            results["temporal"] = temporal
        
        # 5. Calculer le score global
        if module_scores:
            results["overall_score"] = round(
                sum(module_scores.values()) / len(module_scores), 1
            )
            results["overall_rating"] = get_rating(results["overall_score"])
        
        logger.info(f"Territory analysis complete: score={results['overall_score']}")
        
        return results
    
    async def quick_analysis(
        self,
        latitude: float,
        longitude: float,
        target_species: str = "deer"
    ) -> Dict[str, Any]:
        """
        Effectue une analyse rapide (score estimé).
        
        Args:
            latitude: Latitude
            longitude: Longitude
            target_species: Espèce cible
            
        Returns:
            Dict: Score rapide avec estimation
        """
        # Générer un ID temporaire
        territory_id = f"quick_{datetime.now().timestamp()}"
        
        # Calculer seulement les modules essentiels
        essential_modules = [ModuleType.FOOD, ModuleType.WETNESS, ModuleType.CANOPY]
        
        module_results = await self.module_runner.calculate_all_modules(
            latitude, longitude, territory_id, essential_modules, None
        )
        
        module_scores = {m: r.get("score", 50) for m, r in module_results.items()}
        
        # Estimer le score global
        avg_score = sum(module_scores.values()) / len(module_scores) if module_scores else 50
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "target_species": target_species,
            "estimated_score": round(avg_score, 1),
            "rating": get_rating(avg_score),
            "confidence": 0.7,
            "note": "Analyse rapide - pour une analyse complète, utilisez /api/bionic/analyze"
        }
    
    def _extract_real_conditions(
        self,
        geospatial_data: Optional[Any]
    ) -> Dict[str, Any]:
        """
        Extrait les conditions réelles depuis les données géospatiales.
        """
        conditions = {}
        
        if geospatial_data is None:
            return conditions
        
        # Conditions météo
        if hasattr(geospatial_data, 'weather') and geospatial_data.weather:
            weather = geospatial_data.weather
            conditions["weather"] = {
                "temperature": getattr(weather, 'temperature', None),
                "feels_like": getattr(weather, 'apparent_temperature', None),
                "humidity": getattr(weather, 'humidity', None),
                "wind_speed": getattr(weather, 'wind_speed', None),
                "precipitation_probability": getattr(weather, 'precipitation_probability', None),
                "description": getattr(weather, 'weather_description', None),
                "source": "Open-Meteo"
            }
        
        # Conditions terrain
        if hasattr(geospatial_data, 'terrain') and geospatial_data.terrain:
            terrain = geospatial_data.terrain
            conditions["terrain"] = {
                "elevation_m": getattr(terrain, 'elevation', None),
                "slope_deg": getattr(terrain, 'slope', None),
                "aspect_deg": getattr(terrain, 'aspect', None),
                "source": "Open-Elevation"
            }
        
        # Conditions végétation
        if hasattr(geospatial_data, 'vegetation') and geospatial_data.vegetation:
            veg = geospatial_data.vegetation
            conditions["vegetation"] = {
                "ndvi": getattr(veg, 'ndvi', None),
                "ndwi": getattr(veg, 'ndwi', None),
                "evi": getattr(veg, 'evi', None),
                "lai": getattr(veg, 'lai', None),
                "data_date": getattr(veg, 'data_date', None),
                "source": getattr(veg, 'source', 'Vegetation data')
            }
        
        return conditions
    
    def _get_data_sources(
        self,
        geospatial_data: Optional[Any]
    ) -> List[str]:
        """
        Détermine les sources de données utilisées.
        """
        sources = []
        
        if geospatial_data is None:
            return ["Simulation BIONIC™"]
        
        if hasattr(geospatial_data, 'weather') and geospatial_data.weather:
            sources.append("Open-Meteo (météo temps réel)")
        
        if hasattr(geospatial_data, 'terrain') and geospatial_data.terrain:
            sources.append("Open-Elevation (terrain)")
        
        if hasattr(geospatial_data, 'vegetation') and geospatial_data.vegetation:
            source = getattr(geospatial_data.vegetation, 'source', 'Vegetation data')
            sources.append(source)
        
        return sources if sources else ["Simulation BIONIC™"]


# Instance singleton
bionic_orchestrator = BionicOrchestrator()


# ============================================
# API EXPORTS
# ============================================

__all__ = [
    'BionicOrchestrator',
    'bionic_orchestrator',
    'ModuleRunner',
    'module_runner',
    'SpeciesEngine',
    'species_engine',
    'PredictionEngine',
    'prediction_engine',
    'TemporalEngine',
    'temporal_engine',
    'ModuleType',
    'SpeciesType',
    'SeasonType',
]
