"""
BIONIC™ CORE - Modèles Consolidés
bionic_core_models.py

Modèle principal pour l'analyse complète d'un territoire BIONIC™.
Inclut tous les sous-modèles nécessaires pour une analyse territoriale
complète avec modules thématiques, espèces, prédictions et recommandations.

Version: BIONIC_CORE 1.0
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class ModuleType(str, Enum):
    """Types de modules d'analyse thématique"""
    THERMAL = "thermal"
    WETNESS = "wetness"
    FOOD = "food"
    COVER = "cover"
    TERRAIN = "terrain"
    HYDROLOGY = "hydrology"
    VEGETATION = "vegetation"
    GEOLOGY = "geology"
    WEATHER = "weather"
    HUMAN_ACTIVITY = "human_activity"


class SpeciesType(str, Enum):
    """Espèces supportées par BIONIC"""
    MOOSE = "moose"
    DEER = "deer"
    BEAR = "bear"
    ELK = "elk"
    WATERFOWL = "waterfowl"
    TURKEY = "turkey"
    SMALLGAME = "smallgame"


class PredictionHorizon(str, Enum):
    """Horizons de prédiction IA"""
    H24 = "24h"
    H72 = "72h"
    D7 = "7d"


# =============================================================================
# SUB-MODELS
# =============================================================================

class ModuleResult(BaseModel):
    """
    Résultat d'un module d'analyse thématique.
    Chaque module (Thermal, Wetness, Food, etc.) produit ce type de résultat.
    """
    module_type: ModuleType
    module_name: str
    score: float = Field(..., ge=0, le=100)
    rating: str
    details: Dict[str, Any] = {}
    indicators: Dict[str, float] = {}
    recommendations: List[str] = []
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HabitatSuitability(BaseModel):
    """Adéquation de l'habitat pour une espèce"""
    food_score: float = Field(..., ge=0, le=100)
    water_score: float = Field(..., ge=0, le=100)
    cover_score: float = Field(..., ge=0, le=100)
    terrain_score: float = Field(..., ge=0, le=100)
    disturbance_score: float = Field(..., ge=0, le=100)


class SpeciesResult(BaseModel):
    """
    Résultat d'analyse pour une espèce spécifique.
    Combine les données de tous les modules pour cette espèce.
    """
    species: SpeciesType
    species_name_fr: str
    suitability_score: float = Field(..., ge=0, le=100)
    rating: str
    habitat_suitability: Optional[HabitatSuitability] = None
    estimated_density: Optional[str] = None
    recommendations: List[str] = []
    best_hunting_period: Optional[str] = None


class SinglePrediction(BaseModel):
    """Prédiction pour un horizon temporel"""
    horizon: PredictionHorizon
    timestamp: datetime
    predicted_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    key_factors: Dict[str, float] = {}


class PredictionResult(BaseModel):
    """
    Résultat des prédictions IA pour le territoire.
    Inclut les prédictions à 24h, 72h et 7 jours.
    """
    model_name: str = "BIONIC_PREDICTOR"
    model_version: str = "1.0"
    predictions: List[SinglePrediction] = []
    trend: str = "stable"  # "improving", "stable", "declining"
    best_window: Optional[Dict[str, Any]] = None
    alerts: List[str] = []
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NDVITimeSeries(BaseModel):
    """Série temporelle NDVI"""
    dates: List[datetime] = []
    values: List[float] = []
    trend: Optional[str] = None
    anomalies: List[Dict[str, Any]] = []


class SnowAnalysis(BaseModel):
    """Analyse de la couverture neigeuse"""
    snow_coverage_percent: float = Field(..., ge=0, le=100)
    snow_depth_cm: Optional[float] = None
    days_since_last_snow: Optional[int] = None
    melting_status: Optional[str] = None


class PhenologyData(BaseModel):
    """Données phénologiques"""
    current_phase: str
    days_to_next_phase: Optional[int] = None
    green_up_date: Optional[datetime] = None
    peak_green_date: Optional[datetime] = None
    senescence_date: Optional[datetime] = None


class TemporalResult(BaseModel):
    """
    Résultat de l'analyse temporelle.
    Inclut l'évolution des indices de végétation, neige, phénologie.
    """
    analysis_period_start: datetime
    analysis_period_end: datetime
    current_season: str
    ndvi_series: Optional[NDVITimeSeries] = None
    ndwi_series: Optional[NDVITimeSeries] = None
    snow_analysis: Optional[SnowAnalysis] = None
    phenology: Optional[PhenologyData] = None
    compared_to_average: Optional[str] = None
    year_over_year_change: Optional[float] = None
    detected_events: List[Dict[str, Any]] = []


# =============================================================================
# MAIN MODEL: TERRITORY FULL ANALYSIS
# =============================================================================

class TerritoryFullAnalysis(BaseModel):
    """
    Modèle consolidé pour BIONIC_CORE.
    Représente une analyse complète d'un territoire, incluant :
    - modules thématiques (Thermal, Wetness, Food, etc.)
    - modèles fauniques (Moose, Deer, Bear…)
    - prédictions IA (24h, 72h, 7j)
    - analyse temporelle (NDVI, NDWI, neige, phénologie)
    - métadonnées géospatiales
    - scores globaux
    - recommandations consolidées
    """

    # Identité du territoire
    territory_id: str
    latitude: float
    longitude: float
    radius_km: float

    # Métadonnées
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    data_sources: List[str] = []

    # Résultats des modules thématiques
    modules: List[ModuleResult]

    # Résultats par espèce
    species: List[SpeciesResult]

    # Prédictions IA (optionnel)
    predictions: Optional[PredictionResult] = None

    # Analyse temporelle (optionnel)
    temporal: Optional[TemporalResult] = None

    # Score global consolidé
    global_score: float = Field(ge=0, le=100)
    global_rating: str

    # Recommandations consolidées (toutes sources)
    recommendations: List[str]

    # GeoJSON final (zones optimales, corridors, exclusions)
    geojson: Optional[Dict[str, Any]] = None

    # Version du moteur BIONIC
    engine_version: str = "BIONIC_CORE 1.0"
