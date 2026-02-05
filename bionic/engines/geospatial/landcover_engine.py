"""
BIONIC™ P1 - Landcover Engine
==============================
Classification du couvert végétal et analyse de la structure forestière.

North America Ready:
- SIGÉOM (Québec)
- CanVec (Canada)
- NLCD (USA)

Sources 100% gratuites et publiques.

Version: 1.0.0
"""

import logging
import uuid
import math
import asyncio
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
    Region,
    LandCoverType
)
from geospatial.unified_output import UnifiedOutputBuilder, FusionHooks
from geospatial.geo_core import geo_core
from geospatial.geo_core.loaders import LoaderFactory

logger = logging.getLogger(__name__)


# =============================================================================
# LANDCOVER CLASSIFICATIONS
# =============================================================================

# Classification NLCD vers LandCoverType
NLCD_TO_LANDCOVER = {
    11: LandCoverType.WATER,
    21: LandCoverType.URBAN,
    22: LandCoverType.URBAN,
    23: LandCoverType.URBAN,
    24: LandCoverType.URBAN,
    31: LandCoverType.BARREN,
    41: LandCoverType.DECIDUOUS_FOREST,
    42: LandCoverType.CONIFEROUS_FOREST,
    43: LandCoverType.MIXED_FOREST,
    52: LandCoverType.SHRUBLAND,
    71: LandCoverType.GRASSLAND,
    81: LandCoverType.AGRICULTURAL,
    82: LandCoverType.AGRICULTURAL,
    90: LandCoverType.WETLAND,
    95: LandCoverType.WETLAND
}

# Scores d'habitat par type de couvert et espèce
HABITAT_SCORES = {
    LandCoverType.DECIDUOUS_FOREST: {
        "deer": 90, "moose": 70, "bear": 85, "turkey": 95,
        "caribou": 40, "wolf": 75, "waterfowl": 20, "smallgame": 70
    },
    LandCoverType.CONIFEROUS_FOREST: {
        "deer": 70, "moose": 90, "bear": 80, "turkey": 60,
        "caribou": 85, "wolf": 85, "waterfowl": 15, "smallgame": 60
    },
    LandCoverType.MIXED_FOREST: {
        "deer": 95, "moose": 85, "bear": 90, "turkey": 85,
        "caribou": 60, "wolf": 80, "waterfowl": 25, "smallgame": 75
    },
    LandCoverType.SHRUBLAND: {
        "deer": 75, "moose": 60, "bear": 70, "turkey": 70,
        "caribou": 55, "wolf": 60, "waterfowl": 30, "smallgame": 80
    },
    LandCoverType.GRASSLAND: {
        "deer": 50, "moose": 30, "bear": 40, "turkey": 60,
        "caribou": 70, "wolf": 65, "waterfowl": 40, "smallgame": 65
    },
    LandCoverType.WETLAND: {
        "deer": 60, "moose": 95, "bear": 75, "turkey": 40,
        "caribou": 45, "wolf": 55, "waterfowl": 95, "smallgame": 70
    },
    LandCoverType.WATER: {
        "deer": 40, "moose": 80, "bear": 60, "turkey": 20,
        "caribou": 30, "wolf": 40, "waterfowl": 100, "smallgame": 30
    },
    LandCoverType.AGRICULTURAL: {
        "deer": 65, "moose": 25, "bear": 55, "turkey": 80,
        "caribou": 15, "wolf": 30, "waterfowl": 60, "smallgame": 75
    },
    LandCoverType.URBAN: {
        "deer": 20, "moose": 5, "bear": 15, "turkey": 30,
        "caribou": 5, "wolf": 10, "waterfowl": 25, "smallgame": 35
    },
    LandCoverType.BARREN: {
        "deer": 15, "moose": 10, "bear": 20, "turkey": 15,
        "caribou": 60, "wolf": 50, "waterfowl": 10, "smallgame": 20
    }
}

# Couvert thermique par type
THERMAL_COVER = {
    LandCoverType.CONIFEROUS_FOREST: 0.95,
    LandCoverType.MIXED_FOREST: 0.80,
    LandCoverType.DECIDUOUS_FOREST: 0.60,  # Réduit en hiver
    LandCoverType.SHRUBLAND: 0.40,
    LandCoverType.WETLAND: 0.30,
    LandCoverType.GRASSLAND: 0.10,
    LandCoverType.AGRICULTURAL: 0.15,
    LandCoverType.WATER: 0.0,
    LandCoverType.URBAN: 0.20,
    LandCoverType.BARREN: 0.05
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class LandcoverComposition:
    """Composition du couvert végétal."""
    cover_type: str
    percent: float
    area_km2: float
    habitat_score: float


@dataclass
class EdgeAnalysis:
    """Analyse des lisières."""
    edge_density_m_ha: float
    edge_types: Dict[str, float]
    fragmentation_index: float


# =============================================================================
# LANDCOVER ENGINE
# =============================================================================

class LandcoverEngine(BaseGeospatialEngine):
    """
    Moteur de classification du couvert végétal.
    
    Analyse:
    - Type de couvert dominant
    - Composition (% par type)
    - Densité de lisières
    - Couvert thermique
    - Diversité structurelle
    
    Multi-espèces: 8 espèces supportées
    """
    
    ENGINE_NAME = "LandcoverEngine"
    ENGINE_VERSION = "1.0.0"
    
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.timeout = timeout
        self._cache_namespace = "landcover"
    
    async def analyze(
        self,
        lat: float,
        lon: float,
        radius_km: float = 2.0,
        target_species: Optional[List[str]] = None
    ) -> GeospatialEngineOutput:
        """
        Analyse le couvert végétal autour d'un point.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Rayon d'analyse en km
            target_species: Espèces cibles (défaut: toutes)
        
        Returns:
            GeospatialEngineOutput avec l'analyse du couvert
        """
        analysis_id = f"lco_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now(timezone.utc)
        
        # Déterminer la région
        region = self._determine_region(lat, lon)
        sources = self._get_data_sources(lat, lon)
        
        # Espèces par défaut
        if target_species is None:
            target_species = list(HABITAT_SCORES[LandCoverType.MIXED_FOREST].keys())
        
        # Charger les données selon la région
        landcover_data = await self._load_landcover_data(lat, lon, radius_km, region)
        
        # Analyser la composition
        composition = self._analyze_composition(landcover_data, radius_km)
        
        # Déterminer le couvert dominant
        dominant_cover = self._get_dominant_cover(composition)
        
        # Calculer la densité de lisières
        edge_analysis = self._analyze_edges(composition)
        
        # Calculer le couvert thermique
        thermal_percent = self._calculate_thermal_cover(composition)
        
        # Calculer la diversité structurelle
        structural_diversity = self._calculate_structural_diversity(composition)
        
        # Calculer les scores d'habitat par espèce
        species_scores = self._calculate_species_habitat_scores(composition, target_species)
        
        # Score global
        cover_score = self._calculate_cover_score(
            composition, species_scores, structural_diversity
        )
        
        # Générer les recommandations
        recommendations = self._generate_recommendations(
            dominant_cover, composition, species_scores, thermal_percent
        )
        
        # Calculer la confiance
        confidence = self._calculate_confidence(landcover_data)
        
        # Temps de traitement
        processing_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        return GeospatialEngineOutput(
            engine_name=self.ENGINE_NAME,
            engine_version=self.ENGINE_VERSION,
            analysis_id=analysis_id,
            location={"lat": lat, "lon": lon},
            region=region.value,
            data_sources_used=landcover_data.get("sources", ["estimate"]),
            score=cover_score,
            level=self._score_to_level(cover_score),
            data={
                "dominant_cover": dominant_cover.value if dominant_cover else "unknown",
                "cover_composition": [asdict(c) for c in composition],
                "edge_density_m_ha": edge_analysis.edge_density_m_ha,
                "edge_types": edge_analysis.edge_types,
                "fragmentation_index": edge_analysis.fragmentation_index,
                "thermal_cover_percent": thermal_percent,
                "structural_diversity": structural_diversity,
                "species_habitat_scores": species_scores,
                "radius_km": radius_km
            },
            recommendations=recommendations,
            confidence=confidence,
            from_cache=landcover_data.get("from_cache", False),
            analyzed_at=start_time.isoformat()
        )
    
    async def _load_landcover_data(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        region: Region
    ) -> Dict[str, Any]:
        """Charge les données de couvert selon la région."""
        data = {
            "sources": [],
            "raw_data": {},
            "from_cache": False
        }
        
        try:
            loaders = LoaderFactory.get_loaders_for_region(lat, lon)
            
            for loader in loaders:
                try:
                    result = await loader.load(lat, lon, radius_km)
                    if result.get("success"):
                        data["sources"].append(loader.SOURCE_NAME)
                        data["raw_data"][loader.SOURCE_NAME] = result.get("data", {})
                except Exception as e:
                    logger.warning(f"Loader {loader.SOURCE_NAME} failed: {e}")
                finally:
                    await loader.close()
            
        except Exception as e:
            logger.warning(f"Error loading landcover data: {e}")
        
        # Fallback si aucune donnée
        if not data["sources"]:
            data["sources"] = ["estimate"]
            data["raw_data"]["estimate"] = self._generate_estimated_data(lat, lon, region)
        
        return data
    
    def _generate_estimated_data(self, lat: float, lon: float, region: Region) -> Dict:
        """Génère des données estimées basées sur la localisation."""
        # Estimation basée sur la latitude et la région
        if region == Region.QUEBEC:
            if lat > 50:
                # Nord du Québec - conifères dominants
                return {
                    "dominant": "coniferous_forest",
                    "composition": {
                        "coniferous_forest": 60,
                        "mixed_forest": 15,
                        "wetland": 15,
                        "water": 10
                    }
                }
            else:
                # Sud du Québec - mixte
                return {
                    "dominant": "mixed_forest",
                    "composition": {
                        "mixed_forest": 40,
                        "deciduous_forest": 25,
                        "agricultural": 20,
                        "wetland": 10,
                        "water": 5
                    }
                }
        elif region == Region.USA:
            return {
                "dominant": "mixed_forest",
                "composition": {
                    "mixed_forest": 35,
                    "deciduous_forest": 30,
                    "agricultural": 20,
                    "grassland": 10,
                    "water": 5
                }
            }
        else:
            # Canada général
            return {
                "dominant": "coniferous_forest",
                "composition": {
                    "coniferous_forest": 50,
                    "mixed_forest": 20,
                    "wetland": 15,
                    "water": 10,
                    "shrubland": 5
                }
            }
    
    def _analyze_composition(
        self,
        landcover_data: Dict,
        radius_km: float
    ) -> List[LandcoverComposition]:
        """Analyse la composition du couvert."""
        compositions = []
        total_area = math.pi * radius_km ** 2
        
        # Extraire les données de composition
        raw = landcover_data.get("raw_data", {})
        
        # Chercher les données de composition dans les sources
        comp_data = {}
        for source, source_data in raw.items():
            if isinstance(source_data, dict):
                if "composition" in source_data:
                    comp_data = source_data["composition"]
                    break
                elif "landcover" in source_data:
                    comp_data = source_data["landcover"].get("composition", {})
                    break
        
        # Fallback
        if not comp_data:
            comp_data = {
                "mixed_forest": 40,
                "deciduous_forest": 25,
                "wetland": 15,
                "agricultural": 15,
                "water": 5
            }
        
        for cover_name, percent in comp_data.items():
            try:
                cover_type = LandCoverType(cover_name)
            except ValueError:
                cover_type = LandCoverType.MIXED_FOREST
            
            # Score d'habitat moyen pour ce type
            habitat_scores = HABITAT_SCORES.get(cover_type, {})
            avg_score = sum(habitat_scores.values()) / len(habitat_scores) if habitat_scores else 50
            
            compositions.append(LandcoverComposition(
                cover_type=cover_type.value,
                percent=percent,
                area_km2=round(total_area * percent / 100, 2),
                habitat_score=avg_score
            ))
        
        # Trier par pourcentage décroissant
        compositions.sort(key=lambda x: x.percent, reverse=True)
        
        return compositions
    
    def _get_dominant_cover(self, composition: List[LandcoverComposition]) -> Optional[LandCoverType]:
        """Retourne le type de couvert dominant."""
        if composition:
            try:
                return LandCoverType(composition[0].cover_type)
            except ValueError:
                return LandCoverType.MIXED_FOREST
        return None
    
    def _analyze_edges(self, composition: List[LandcoverComposition]) -> EdgeAnalysis:
        """Analyse les lisières entre types de couvert."""
        # Estimation de la densité de lisières basée sur la fragmentation
        num_types = len([c for c in composition if c.percent >= 5])
        
        # Plus de types = plus de lisières potentielles
        base_density = 50  # m/ha
        diversity_bonus = num_types * 15
        
        edge_density = min(200, base_density + diversity_bonus)
        
        # Types de lisières
        edge_types = {}
        for i, comp in enumerate(composition[:-1]):
            for next_comp in composition[i+1:]:
                edge_key = f"{comp.cover_type}_{next_comp.cover_type}"
                # Estimation du % de lisière
                edge_types[edge_key] = round(min(comp.percent, next_comp.percent) / 10, 1)
        
        # Index de fragmentation (0-1, 1 = très fragmenté)
        fragmentation = min(1.0, num_types / 6)
        
        return EdgeAnalysis(
            edge_density_m_ha=edge_density,
            edge_types=edge_types,
            fragmentation_index=round(fragmentation, 2)
        )
    
    def _calculate_thermal_cover(self, composition: List[LandcoverComposition]) -> float:
        """Calcule le pourcentage de couvert thermique."""
        total_thermal = 0.0
        
        for comp in composition:
            try:
                cover_type = LandCoverType(comp.cover_type)
                thermal_factor = THERMAL_COVER.get(cover_type, 0.0)
                total_thermal += (comp.percent / 100) * thermal_factor
            except ValueError:
                pass
        
        return round(total_thermal * 100, 1)
    
    def _calculate_structural_diversity(self, composition: List[LandcoverComposition]) -> float:
        """Calcule la diversité structurelle (Shannon index simplifié)."""
        if not composition:
            return 0.0
        
        # Shannon diversity index
        shannon = 0.0
        for comp in composition:
            if comp.percent > 0:
                p = comp.percent / 100
                shannon -= p * math.log(p)
        
        # Normaliser entre 0 et 1
        max_shannon = math.log(len(composition)) if len(composition) > 1 else 1
        normalized = shannon / max_shannon if max_shannon > 0 else 0
        
        return round(normalized, 3)
    
    def _calculate_species_habitat_scores(
        self,
        composition: List[LandcoverComposition],
        target_species: List[str]
    ) -> Dict[str, float]:
        """Calcule les scores d'habitat par espèce."""
        species_scores = {}
        
        for species in target_species:
            score = 0.0
            total_weight = 0.0
            
            for comp in composition:
                try:
                    cover_type = LandCoverType(comp.cover_type)
                    habitat_score = HABITAT_SCORES.get(cover_type, {}).get(species, 50)
                    weight = comp.percent / 100
                    score += habitat_score * weight
                    total_weight += weight
                except ValueError:
                    pass
            
            species_scores[species] = round(score / total_weight if total_weight > 0 else 50, 1)
        
        return species_scores
    
    def _calculate_cover_score(
        self,
        composition: List[LandcoverComposition],
        species_scores: Dict[str, float],
        structural_diversity: float
    ) -> float:
        """Calcule le score global de couvert."""
        # Score basé sur la qualité moyenne d'habitat
        avg_habitat = sum(c.habitat_score * c.percent / 100 for c in composition)
        
        # Score basé sur les espèces
        avg_species = sum(species_scores.values()) / len(species_scores) if species_scores else 50
        
        # Bonus diversité
        diversity_bonus = structural_diversity * 15
        
        # Score combiné
        score = (avg_habitat * 0.4) + (avg_species * 0.4) + diversity_bonus + 10
        
        return round(min(100, max(0, score)), 1)
    
    def _generate_recommendations(
        self,
        dominant_cover: Optional[LandCoverType],
        composition: List[LandcoverComposition],
        species_scores: Dict[str, float],
        thermal_percent: float
    ) -> List[str]:
        """Génère les recommandations."""
        recommendations = []
        
        if dominant_cover:
            recommendations.append(f"🌲 Couvert dominant: {dominant_cover.value.replace('_', ' ').title()}")
        
        # Meilleure espèce
        if species_scores:
            best_species = max(species_scores.items(), key=lambda x: x[1])
            recommendations.append(f"🎯 Meilleur habitat pour: {best_species[0]} ({best_species[1]:.0f}/100)")
        
        # Couvert thermique
        if thermal_percent >= 50:
            recommendations.append(f"✅ Excellent couvert thermique ({thermal_percent:.0f}%)")
        elif thermal_percent >= 30:
            recommendations.append(f"⚠️ Couvert thermique modéré ({thermal_percent:.0f}%)")
        else:
            recommendations.append(f"❌ Couvert thermique insuffisant ({thermal_percent:.0f}%)")
        
        # Diversité
        num_types = len([c for c in composition if c.percent >= 10])
        if num_types >= 4:
            recommendations.append(f"✅ Haute diversité d'habitats ({num_types} types)")
        elif num_types >= 2:
            recommendations.append(f"⚠️ Diversité modérée ({num_types} types)")
        
        return recommendations[:6]
    
    def _calculate_confidence(self, landcover_data: Dict) -> float:
        """Calcule le niveau de confiance."""
        sources = landcover_data.get("sources", [])
        
        # Plus de sources = plus de confiance
        source_factor = min(1.0, len(sources) / 3)
        
        # Bonus si sources réelles (non estimées)
        real_sources = [s for s in sources if s != "estimate"]
        real_factor = len(real_sources) / len(sources) if sources else 0
        
        confidence = 0.5 + (source_factor * 0.25) + (real_factor * 0.25)
        
        return round(confidence, 2)


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

landcover_engine = LandcoverEngine()


logger.info("BIONIC™ LandcoverEngine loaded (v1.0.0) - North America Ready")
