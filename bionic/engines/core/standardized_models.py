"""
BIONIC™ Core - Standardized Output Models
==========================================
Modèles standardisés pour uniformiser les sorties de tous les moteurs.

Version: 2.0 - Phase 3 Étape 2 (Uniformisation)

Ce fichier définit:
- BaseEngineOutput: Structure de base pour tous les moteurs
- StandardScore: Format uniforme pour les scores
- StandardMetadata: Métadonnées communes
- Structures préparées pour les futurs moteurs
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS STANDARDISÉS
# =============================================================================

class ScoreLevel(str, Enum):
    """Niveaux de score normalisés (0-100)."""
    EXCEPTIONAL = "exceptional"  # 90-100
    EXCELLENT = "excellent"      # 80-89
    GOOD = "good"               # 60-79
    MODERATE = "moderate"       # 40-59
    LOW = "low"                 # 20-39
    POOR = "poor"               # 0-19


class ConfidenceLevel(str, Enum):
    """Niveaux de confiance."""
    VERY_HIGH = "very_high"   # > 0.9
    HIGH = "high"             # 0.75-0.9
    MODERATE = "moderate"     # 0.5-0.75
    LOW = "low"               # 0.25-0.5
    VERY_LOW = "very_low"     # < 0.25


class DataSourceType(str, Enum):
    """Types de sources de données."""
    REAL_API = "real_api"           # Données temps réel d'API externe
    CACHED = "cached"               # Données en cache
    MODELED = "modeled"             # Données modélisées/estimées
    HISTORICAL = "historical"       # Données historiques
    HYBRID = "hybrid"               # Combinaison de sources


# =============================================================================
# MODÈLES DE BASE STANDARDISÉS
# =============================================================================

class StandardLocation(BaseModel):
    """Localisation standardisée."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    
    class Config:
        json_schema_extra = {
            "example": {"lat": 47.5, "lon": -72.5}
        }


class StandardScore(BaseModel):
    """
    Score standardisé pour tous les moteurs.
    
    Tous les scores doivent suivre ce format pour garantir
    la cohérence dans TerritoryFullAnalysis.
    """
    score: float = Field(..., ge=0, le=100, description="Score normalisé 0-100")
    level: ScoreLevel = Field(..., description="Niveau qualitatif")
    components: Dict[str, float] = Field(default_factory=dict, description="Composantes du score")
    interpretation: str = Field(default="", description="Interprétation textuelle")
    
    @classmethod
    def from_value(cls, value: float, components: Dict[str, float] = None, interpretation: str = "") -> "StandardScore":
        """Crée un score standardisé à partir d'une valeur."""
        level = cls._value_to_level(value)
        return cls(
            score=round(value, 1),
            level=level,
            components=components or {},
            interpretation=interpretation
        )
    
    @staticmethod
    def _value_to_level(value: float) -> ScoreLevel:
        """Convertit une valeur en niveau."""
        if value >= 90:
            return ScoreLevel.EXCEPTIONAL
        elif value >= 80:
            return ScoreLevel.EXCELLENT
        elif value >= 60:
            return ScoreLevel.GOOD
        elif value >= 40:
            return ScoreLevel.MODERATE
        elif value >= 20:
            return ScoreLevel.LOW
        else:
            return ScoreLevel.POOR


class StandardMetadata(BaseModel):
    """
    Métadonnées standardisées pour tous les moteurs.
    
    Chaque sortie de moteur DOIT inclure ces métadonnées.
    """
    engine_name: str = Field(..., description="Nom du moteur (ex: SentinelEngine)")
    engine_version: str = Field(..., description="Version du moteur (ex: 2.0.0)")
    analysis_id: str = Field(..., description="ID unique de l'analyse (ex: sen_abc123)")
    analyzed_at: datetime = Field(..., description="Timestamp de l'analyse")
    processing_time_ms: int = Field(default=0, ge=0, description="Temps de traitement en ms")
    data_source: str = Field(..., description="Source des données")
    data_source_type: DataSourceType = Field(default=DataSourceType.MODELED)
    confidence: float = Field(..., ge=0, le=1, description="Niveau de confiance 0-1")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.MODERATE)
    from_cache: bool = Field(default=False, description="Données issues du cache")
    cache_age_seconds: Optional[int] = Field(default=None, description="Âge du cache en secondes")


class BaseEngineOutput(BaseModel):
    """
    Sortie de base standardisée pour tous les moteurs BIONIC™.
    
    Tous les moteurs doivent hériter de cette classe ou inclure ces champs.
    
    Structure obligatoire:
    - metadata: StandardMetadata
    - location: StandardLocation
    - overall_score: StandardScore
    - recommendations: List[str]
    """
    metadata: StandardMetadata
    location: StandardLocation
    overall_score: StandardScore
    recommendations: List[str] = Field(default_factory=list, max_length=10)
    
    # Champs optionnels communs
    warnings: List[str] = Field(default_factory=list, description="Avertissements")
    errors: List[str] = Field(default_factory=list, description="Erreurs non-bloquantes")


# =============================================================================
# STRUCTURES POUR MOTEURS GÉOSPATIAUX EXISTANTS
# =============================================================================

class VegetationIndices(BaseModel):
    """Indices de végétation standardisés (SentinelEngine)."""
    ndvi: float = Field(..., ge=-1, le=1, description="NDVI")
    ndwi: float = Field(..., ge=-1, le=1, description="NDWI")
    evi: float = Field(..., ge=-1, le=1, description="EVI")
    savi: float = Field(..., ge=-1, le=1, description="SAVI")
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "ndvi": round(self.ndvi, 4),
            "ndwi": round(self.ndwi, 4),
            "evi": round(self.evi, 4),
            "savi": round(self.savi, 4)
        }


class GeologicalInfo(BaseModel):
    """Information géologique standardisée (SigeomEngine)."""
    province_code: str
    province_name: str
    deposit_type: str
    deposit_name: str
    drainage_quality: str
    bedrock_type: str


class TerrainMetrics(BaseModel):
    """Métriques de terrain standardisées (TerrainEngine)."""
    elevation_m: float = Field(..., ge=-500, le=10000)
    slope_degrees: float = Field(..., ge=0, le=90)
    slope_percent: float = Field(..., ge=0)
    aspect: str = Field(..., pattern="^(N|NE|E|SE|S|SW|W|NW)$")
    aspect_degrees: int = Field(..., ge=0, le=360)
    tpi: float = Field(..., ge=-1, le=1, description="Topographic Position Index")
    tpi_class: str
    roughness_index: float = Field(..., ge=0, le=1)


class PressureMetrics(BaseModel):
    """Métriques de pression humaine standardisées (PressureEngine)."""
    pressure_index: float = Field(..., ge=0, le=100)
    remoteness_score: float = Field(..., ge=0, le=100)
    road_density_score: float = Field(..., ge=0, le=100)
    building_density_score: float = Field(..., ge=0, le=100)
    hunting_suitability: float = Field(..., ge=0, le=100)


# =============================================================================
# STRUCTURES POUR FUTURS MOTEURS
# =============================================================================

class CorridorSegment(BaseModel):
    """Segment de corridor faunique (CorridorEngine - À VENIR)."""
    id: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    width_m: float = Field(..., ge=10, le=1000)
    length_m: float = Field(..., ge=0)
    usage_probability: float = Field(..., ge=0, le=1)
    terrain_type: str
    connectivity_score: float = Field(..., ge=0, le=100)
    species_suitability: Dict[str, float] = Field(default_factory=dict)


class HydrologyInfo(BaseModel):
    """Information hydrologique (HydrologyEngine - À VENIR)."""
    distance_to_water_m: float = Field(..., ge=0)
    water_body_type: str  # lake, river, stream, wetland, pond
    water_body_name: Optional[str] = None
    watershed_id: Optional[str] = None
    flow_direction: Optional[str] = None
    wetland_percent: float = Field(default=0, ge=0, le=100)
    flood_risk: str = Field(default="low")  # low, moderate, high


class LandcoverInfo(BaseModel):
    """Information de couverture terrestre (LandcoverEngine - À VENIR)."""
    landcover_class: str  # NLCD or CanLandCover code
    landcover_name: str
    landcover_percent: float = Field(..., ge=0, le=100)
    forest_type: Optional[str] = None  # deciduous, coniferous, mixed
    forest_density: Optional[float] = None  # 0-1
    agriculture_type: Optional[str] = None
    urban_density: Optional[float] = None


# =============================================================================
# STRUCTURE CONSOLIDÉE POUR TERRITOIRE
# =============================================================================

class TerritoryAnalysisModule(BaseModel):
    """
    Module d'analyse pour TerritoryFullAnalysis.
    
    Chaque moteur produit un module qui peut être intégré
    dans l'analyse complète du territoire.
    """
    module_name: str = Field(..., description="Nom du module (ex: vegetation)")
    engine_name: str = Field(..., description="Moteur source")
    score: StandardScore
    data: Dict[str, Any] = Field(default_factory=dict, description="Données spécifiques au module")
    recommendations: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1)
    weight_in_global: float = Field(default=0.25, ge=0, le=1, description="Poids dans le score global")


class TerritoryFullAnalysisV2(BaseModel):
    """
    Analyse complète du territoire (Version 2 - Standardisée).
    
    Agrège les résultats de tous les moteurs dans un format uniforme.
    """
    # Métadonnées
    territory_id: str
    analysis_version: str = "2.0.0"
    analyzed_at: datetime
    processing_time_ms: int
    
    # Localisation
    location: StandardLocation
    target_species: str
    radius_km: float = Field(default=5.0)
    
    # Modules d'analyse
    modules: Dict[str, TerritoryAnalysisModule] = Field(default_factory=dict)
    modules_executed: List[str] = Field(default_factory=list)
    modules_failed: List[str] = Field(default_factory=list)
    
    # Scores consolidés
    global_score: StandardScore
    hunting_opportunity_index: float = Field(..., ge=0, le=100)
    
    # Résumé
    top_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Top 5 facteurs influençant le score")
    recommendations: List[str] = Field(default_factory=list, max_length=10)
    hotspots: List[Dict[str, Any]] = Field(default_factory=list, max_length=5)
    
    # Cache et performance
    cache_hit_rate: float = Field(default=0, ge=0, le=1)
    from_cache: bool = Field(default=False)


# =============================================================================
# HELPERS DE CONVERSION
# =============================================================================

def score_to_level(score: float) -> ScoreLevel:
    """Convertit un score numérique en niveau."""
    return StandardScore._value_to_level(score)


def confidence_to_level(confidence: float) -> ConfidenceLevel:
    """Convertit une confiance numérique en niveau."""
    if confidence >= 0.9:
        return ConfidenceLevel.VERY_HIGH
    elif confidence >= 0.75:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.5:
        return ConfidenceLevel.MODERATE
    elif confidence >= 0.25:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.VERY_LOW


def normalize_score(value: float, min_val: float = 0, max_val: float = 100) -> float:
    """Normalise une valeur entre 0 et 100."""
    if max_val == min_val:
        return 50.0
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return round(max(0, min(100, normalized)), 1)


def create_standard_score(
    score: float,
    components: Dict[str, float] = None,
    interpretation: str = ""
) -> Dict[str, Any]:
    """Crée un dictionnaire de score standardisé."""
    level = score_to_level(score)
    return {
        "score": round(score, 1),
        "level": level.value,
        "components": components or {},
        "interpretation": interpretation
    }


def create_standard_metadata(
    engine_name: str,
    engine_version: str,
    analysis_id: str,
    data_source: str,
    confidence: float,
    processing_time_ms: int = 0,
    from_cache: bool = False
) -> Dict[str, Any]:
    """Crée un dictionnaire de métadonnées standardisées."""
    return {
        "engine_name": engine_name,
        "engine_version": engine_version,
        "analysis_id": analysis_id,
        "analyzed_at": datetime.now().isoformat(),
        "processing_time_ms": processing_time_ms,
        "data_source": data_source,
        "data_source_type": DataSourceType.MODELED.value,
        "confidence": round(confidence, 3),
        "confidence_level": confidence_to_level(confidence).value,
        "from_cache": from_cache
    }


# =============================================================================
# CONSTANTES ET POIDS DES MODULES
# =============================================================================

# Poids par défaut des modules dans le score global
MODULE_WEIGHTS = {
    "vegetation": 0.25,    # SentinelEngine
    "geology": 0.15,       # SigeomEngine
    "terrain": 0.15,       # TerrainEngine
    "pressure": 0.20,      # PressureEngine
    "hydrology": 0.10,     # HydrologyEngine (à venir)
    "landcover": 0.10,     # LandcoverEngine (à venir)
    "corridor": 0.05       # CorridorEngine (à venir)
}

# Poids par défaut pour la Behavior Suite
BEHAVIOR_MODULE_WEIGHTS = {
    "behavior": 0.20,
    "seasonal": 0.15,
    "activity": 0.20,
    "rut": 0.15,
    "movement": 0.15,
    "species_model": 0.15
}

# Espèces supportées
SUPPORTED_SPECIES = [
    "deer", "moose", "bear", "caribou", 
    "wolf", "turkey", "waterfowl", "smallgame"
]

# Saisons
SEASONS = ["spring", "summer", "fall", "winter"]


# =============================================================================
# OUTPUT FORMATTER MIXIN / HELPER CLASS
# =============================================================================

class StandardOutputFormatter:
    """
    Mixin/Helper pour formater les sorties des moteurs de manière standardisée.
    
    Usage:
        formatter = StandardOutputFormatter("SentinelEngine", "2.0.0", "vegetation")
        output = formatter.format_output(
            lat=47.5, lon=-72.5,
            score=75.5,
            components={"base": 70, "bonus": 5.5},
            interpretation="Zone favorable",
            raw_data={"indices": {...}},
            recommendations=["Tip 1", "Tip 2"],
            confidence=0.85,
            data_source="NASA MODIS",
            from_cache=False
        )
    """
    
    def __init__(
        self, 
        engine_name: str, 
        engine_version: str, 
        module_name: str
    ):
        self.engine_name = engine_name
        self.engine_version = engine_version
        self.module_name = module_name
    
    def format_output(
        self,
        lat: float,
        lon: float,
        score: float,
        components: Dict[str, Any] = None,
        interpretation: str = "",
        raw_data: Dict[str, Any] = None,
        recommendations: List[str] = None,
        confidence: float = 0.70,
        data_source: str = "BIONIC Model",
        data_source_type: str = "modeled",
        from_cache: bool = False,
        cache_age_seconds: Optional[int] = None,
        processing_time_ms: int = 0,
        extra_fields: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Formate la sortie d'un moteur selon le standard BIONIC™.
        
        Args:
            lat, lon: Coordonnées
            score: Score global (0-100)
            components: Composantes du score
            interpretation: Texte d'interprétation
            raw_data: Données brutes spécifiques au moteur
            recommendations: Liste de recommandations
            confidence: Niveau de confiance (0-1)
            data_source: Nom de la source de données
            data_source_type: Type de source (real_api, cached, modeled, etc.)
            from_cache: Si les données viennent du cache
            cache_age_seconds: Âge du cache si applicable
            processing_time_ms: Temps de traitement
            extra_fields: Champs additionnels spécifiques au moteur
        
        Returns:
            Dict standardisé conforme à BaseEngineOutput
        """
        import uuid
        
        # Generate analysis ID
        prefix = self.module_name[:3].lower()
        analysis_id = f"{prefix}_{uuid.uuid4().hex[:12]}"
        
        # Build metadata
        metadata = {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "analysis_id": analysis_id,
            "analyzed_at": datetime.now().isoformat(),
            "processing_time_ms": processing_time_ms,
            "data_source": data_source,
            "data_source_type": data_source_type,
            "confidence": round(confidence, 3),
            "confidence_level": confidence_to_level(confidence).value,
            "from_cache": from_cache,
            "cache_age_seconds": cache_age_seconds
        }
        
        # Build standardized score
        overall_score = {
            "score": round(score, 1),
            "level": score_to_level(score).value,
            "components": components or {},
            "interpretation": interpretation
        }
        
        # Build output
        output = {
            "metadata": metadata,
            "location": {"lat": lat, "lon": lon},
            "overall_score": overall_score,
            "data": raw_data or {},
            "recommendations": (recommendations or [])[:10],
            "warnings": [],
            "errors": [],
            "from_cache": from_cache
        }
        
        # Add extra fields at top level
        if extra_fields:
            for key, value in extra_fields.items():
                if key not in output:
                    output[key] = value
        
        return output
    
    def format_territory_module(
        self,
        score: float,
        data: Dict[str, Any],
        recommendations: List[str] = None,
        confidence: float = 0.70,
        weight: float = 0.25
    ) -> Dict[str, Any]:
        """
        Formate un module pour TerritoryFullAnalysis.
        
        Retourne un TerritoryAnalysisModule standardisé.
        """
        return {
            "module_name": self.module_name,
            "engine_name": self.engine_name,
            "score": {
                "score": round(score, 1),
                "level": score_to_level(score).value,
                "components": {},
                "interpretation": ""
            },
            "data": data,
            "recommendations": recommendations or [],
            "confidence": round(confidence, 3),
            "weight_in_global": weight
        }


# Factory function for formatters
def get_formatter(engine_name: str, engine_version: str, module_name: str) -> StandardOutputFormatter:
    """
    Factory pour créer un formatter standardisé.
    
    Example:
        formatter = get_formatter("SentinelEngine", "2.0.0", "vegetation")
    """
    return StandardOutputFormatter(engine_name, engine_version, module_name)
