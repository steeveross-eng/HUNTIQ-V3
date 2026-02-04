"""
BIONIC™ CORE - Territory Full Analysis Models
==============================================
Modèles Pydantic consolidés pour l'analyse complète d'un territoire.
Inclut tous les modules thématiques, modèles fauniques, prédictions IA,
analyse temporelle et recommandations consolidées.

IMPORTANT: Les Enums de base (ModuleType, SpeciesType, SeasonType) sont
définis dans configs.py et réexportés ici pour la compatibilité.

Version: BIONIC_CORE 2.0
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum

# Import des Enums depuis configs.py (source unique)
from .configs import ModuleType, SpeciesType, SeasonType


# =============================================================================
# ENUMS ADDITIONNELS (spécifiques aux modèles)
# =============================================================================

class ScoreRating(str, Enum):
    """Niveaux de classification des scores"""
    EXCEPTIONAL = "exceptional"
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    LOW = "low"
    POOR = "poor"


class PredictionHorizon(str, Enum):
    """Horizons de prédiction IA"""
    H24 = "24h"
    H72 = "72h"
    D7 = "7d"


# Alias pour compatibilité
Season = SeasonType


# =============================================================================
# SUB-MODELS
# =============================================================================

class GeoPoint(BaseModel):
    """Point géographique"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: Optional[float] = None


class BoundingBox(BaseModel):
    """Bounding box géographique"""
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)
    
    @property
    def center(self) -> GeoPoint:
        return GeoPoint(
            latitude=(self.min_lat + self.max_lat) / 2,
            longitude=(self.min_lon + self.max_lon) / 2
        )


class DataSourceInfo(BaseModel):
    """Information sur une source de données"""
    source_id: str
    name: str
    provider: str
    last_updated: Optional[datetime] = None
    coverage_percent: float = Field(default=100.0, ge=0, le=100)
    quality_score: Optional[float] = Field(default=None, ge=0, le=100)


class ScoreBreakdown(BaseModel):
    """Détail d'un score avec composantes"""
    total_score: float = Field(..., ge=0, le=100)
    rating: ScoreRating
    components: Dict[str, float] = {}
    weights: Dict[str, float] = {}
    confidence: float = Field(default=0.8, ge=0, le=1)


class Recommendation(BaseModel):
    """Recommandation consolidée"""
    id: str
    priority: Literal["high", "medium", "low"]
    category: str
    message: str
    source_module: Optional[str] = None
    action_type: Literal["do", "avoid", "consider", "info"] = "info"
    coordinates: Optional[GeoPoint] = None


# =============================================================================
# MODULE RESULTS
# =============================================================================

class ModuleResult(BaseModel):
    """
    Résultat d'un module d'analyse thématique.
    Chaque module (Thermal, Wetness, Food, etc.) produit ce type de résultat.
    """
    module_type: ModuleType
    module_name: str
    
    # Scores
    score: float = Field(..., ge=0, le=100)
    rating: ScoreRating
    score_breakdown: Optional[ScoreBreakdown] = None
    
    # Données analysées
    data_points: int = 0
    coverage_percent: float = Field(default=100.0, ge=0, le=100)
    
    # Détails spécifiques au module
    details: Dict[str, Any] = {}
    
    # Indicateurs clés
    indicators: Dict[str, float] = {}
    
    # Zones identifiées (GeoJSON features)
    zones: Optional[List[Dict[str, Any]]] = None
    
    # Recommandations du module
    recommendations: List[str] = []
    
    # Métadonnées
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: Optional[int] = None
    
    model_config = ConfigDict(use_enum_values=True)


class ThermalModuleResult(ModuleResult):
    """Résultat spécifique du module Thermal"""
    module_type: ModuleType = ModuleType.THERMAL
    module_name: str = "Analyse Thermique"
    
    # Indicateurs thermiques spécifiques
    surface_temperature_c: Optional[float] = None
    thermal_anomalies: List[Dict[str, Any]] = []
    heat_islands: List[GeoPoint] = []
    cold_spots: List[GeoPoint] = []


class WetnessModuleResult(ModuleResult):
    """Résultat spécifique du module Wetness"""
    module_type: ModuleType = ModuleType.WETNESS
    module_name: str = "Analyse Humidité"
    
    # Indicateurs d'humidité
    ndwi: Optional[float] = None
    moisture_index: Optional[float] = None
    wetland_coverage_percent: float = 0.0
    water_bodies_count: int = 0


class FoodModuleResult(ModuleResult):
    """Résultat spécifique du module Food (Sources alimentaires)"""
    module_type: ModuleType = ModuleType.FOOD
    module_name: str = "Sources Alimentaires"
    
    # Sources de nourriture détectées
    food_sources: List[Dict[str, Any]] = []
    mast_availability: Optional[str] = None  # Glands, noisettes, etc.
    browse_quality: Optional[str] = None
    agricultural_fields: List[Dict[str, Any]] = []


class CoverModuleResult(ModuleResult):
    """Résultat spécifique du module Canopy (Couvert forestier)"""
    module_type: ModuleType = ModuleType.CANOPY
    module_name: str = "Analyse Canopée"
    
    # Types de couvert
    forest_coverage_percent: float = 0.0
    canopy_density: Optional[str] = None
    cover_types: Dict[str, float] = {}  # {"coniferous": 40, "deciduous": 30, ...}
    bedding_areas: List[GeoPoint] = []


class PressureModuleResult(ModuleResult):
    """Résultat spécifique du module Pressure (Pression humaine)"""
    module_type: ModuleType = ModuleType.PRESSURE
    module_name: str = "Analyse Pression"
    
    # Indicateurs de pression
    road_density: Optional[float] = None
    building_proximity: Optional[float] = None
    disturbance_level: float = 0.0


class AccessModuleResult(ModuleResult):
    """Résultat spécifique du module Access (Accessibilité)"""
    module_type: ModuleType = ModuleType.ACCESS
    module_name: str = "Analyse Accessibilité"
    
    # Indicateurs d'accès
    trail_proximity: Optional[float] = None
    road_access: Optional[float] = None
    terrain_difficulty: float = 0.0


class CorridorModuleResult(ModuleResult):
    """Résultat spécifique du module Corridor (Corridors fauniques)"""
    module_type: ModuleType = ModuleType.CORRIDOR
    module_name: str = "Analyse Corridors"
    
    # Indicateurs de corridors
    connectivity_score: Optional[float] = None
    bottleneck_count: int = 0
    corridor_length_km: float = 0.0


class GeoformModuleResult(ModuleResult):
    """Résultat spécifique du module Geoform (Géomorphologie)"""
    module_type: ModuleType = ModuleType.GEOFORM
    module_name: str = "Analyse Géomorphologie"
    
    # Indicateurs géomorphologiques
    slope_avg: Optional[float] = None
    aspect_dominant: Optional[str] = None
    roughness_index: float = 0.0


# =============================================================================
# SPECIES RESULTS
# =============================================================================

class HabitatSuitability(BaseModel):
    """Adéquation de l'habitat pour une espèce"""
    food_score: float = Field(..., ge=0, le=100)
    water_score: float = Field(..., ge=0, le=100)
    cover_score: float = Field(..., ge=0, le=100)
    terrain_score: float = Field(..., ge=0, le=100)
    disturbance_score: float = Field(..., ge=0, le=100)  # Inversé: moins = mieux


class ActivityPattern(BaseModel):
    """Pattern d'activité prédit pour une espèce"""
    peak_hours: List[int] = []  # Heures de la journée (0-23)
    activity_level: Literal["very_high", "high", "moderate", "low", "very_low"]
    movement_corridors: List[Dict[str, Any]] = []
    feeding_times: List[str] = []  # "dawn", "dusk", "night", "midday"


class SpeciesResult(BaseModel):
    """
    Résultat d'analyse pour une espèce spécifique.
    Combine les données de tous les modules pour cette espèce.
    """
    species: SpeciesType
    species_name_fr: str
    
    # Score global pour cette espèce
    suitability_score: float = Field(..., ge=0, le=100)
    rating: ScoreRating
    
    # Détail de l'adéquation
    habitat_suitability: HabitatSuitability
    
    # Patterns d'activité
    activity_pattern: Optional[ActivityPattern] = None
    
    # Densité estimée
    estimated_density: Optional[str] = None  # "high", "medium", "low"
    population_trend: Optional[str] = None  # "increasing", "stable", "decreasing"
    
    # Zones optimales pour cette espèce
    optimal_zones: List[Dict[str, Any]] = []
    
    # Recommandations spécifiques à l'espèce
    recommendations: List[str] = []
    
    # Meilleure période de chasse
    best_hunting_period: Optional[str] = None
    current_season_rating: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


# =============================================================================
# PREDICTION RESULTS
# =============================================================================

class SinglePrediction(BaseModel):
    """Prédiction pour un horizon temporel"""
    horizon: PredictionHorizon
    timestamp: datetime
    
    # Scores prédits
    predicted_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    
    # Facteurs influents
    key_factors: Dict[str, float] = {}
    
    # Conditions prédites
    weather_conditions: Optional[Dict[str, Any]] = None
    activity_prediction: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


class PredictionResult(BaseModel):
    """
    Résultat des prédictions IA pour le territoire.
    Inclut les prédictions à 24h, 72h et 7 jours.
    """
    model_name: str = "BIONIC_PREDICTOR"
    model_version: str = "1.0"
    
    # Prédictions par horizon
    predictions: List[SinglePrediction] = []
    
    # Prédiction globale
    best_window: Optional[Dict[str, Any]] = None  # Meilleure fenêtre de chasse
    trend: Literal["improving", "stable", "declining"] = "stable"
    
    # Alertes
    alerts: List[str] = []
    
    # Métadonnées
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(use_enum_values=True)


# =============================================================================
# TEMPORAL ANALYSIS
# =============================================================================

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
    melting_status: Optional[str] = None  # "stable", "melting", "accumulating"


class PhenologyData(BaseModel):
    """Données phénologiques"""
    current_phase: str  # "green_up", "maturity", "senescence", "dormancy"
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
    current_season: Season
    
    # Séries temporelles
    ndvi_series: Optional[NDVITimeSeries] = None
    ndwi_series: Optional[NDVITimeSeries] = None  # Même structure
    
    # Analyse neige
    snow_analysis: Optional[SnowAnalysis] = None
    
    # Phénologie
    phenology: Optional[PhenologyData] = None
    
    # Comparaison historique
    compared_to_average: Optional[str] = None  # "above", "normal", "below"
    year_over_year_change: Optional[float] = None
    
    # Événements détectés
    detected_events: List[Dict[str, Any]] = []
    
    model_config = ConfigDict(use_enum_values=True)


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
    territory_id: str = Field(..., description="Identifiant unique du territoire")
    territory_name: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(..., gt=0, le=100)
    
    # Bounding box calculée
    bbox: Optional[BoundingBox] = None
    
    # Métadonnées
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    analysis_duration_ms: Optional[int] = None
    data_sources: List[DataSourceInfo] = []
    
    # Résultats des modules thématiques
    modules: List[ModuleResult] = []
    
    # Résultats par espèce
    species: List[SpeciesResult] = []
    
    # Prédictions IA (optionnel)
    predictions: Optional[PredictionResult] = None
    
    # Analyse temporelle (optionnel)
    temporal: Optional[TemporalResult] = None
    
    # Score global consolidé
    global_score: float = Field(..., ge=0, le=100, description="Score global 0-100")
    global_rating: ScoreRating = Field(..., description="Classification du score")
    score_breakdown: Optional[ScoreBreakdown] = None
    
    # Recommandations consolidées (toutes sources)
    recommendations: List[Recommendation] = []
    
    # GeoJSON final (zones optimales, corridors, exclusions)
    geojson: Optional[Dict[str, Any]] = None
    
    # Alertes et avertissements
    alerts: List[str] = []
    warnings: List[str] = []
    
    # Version du moteur BIONIC
    engine_version: str = "BIONIC_CORE 2.0"
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "territory_id": "terr_abc123",
                "latitude": 46.8,
                "longitude": -71.2,
                "radius_km": 5.0,
                "global_score": 72.5,
                "global_rating": "good",
                "modules": [],
                "species": [],
                "recommendations": [],
                "engine_version": "BIONIC_CORE 2.0"
            }
        }
    )
    
    def get_module_by_type(self, module_type: ModuleType) -> Optional[ModuleResult]:
        """Récupère un module par son type"""
        for module in self.modules:
            if module.module_type == module_type:
                return module
        return None
    
    def get_species_result(self, species: SpeciesType) -> Optional[SpeciesResult]:
        """Récupère les résultats pour une espèce"""
        for sp in self.species:
            if sp.species == species:
                return sp
        return None
    
    def get_top_recommendations(self, n: int = 5) -> List[Recommendation]:
        """Récupère les N recommandations les plus importantes"""
        sorted_recs = sorted(
            self.recommendations,
            key=lambda r: {"high": 0, "medium": 1, "low": 2}.get(r.priority, 3)
        )
        return sorted_recs[:n]
    
    def to_summary(self) -> Dict[str, Any]:
        """Génère un résumé compact de l'analyse"""
        return {
            "territory_id": self.territory_id,
            "location": {"lat": self.latitude, "lon": self.longitude},
            "radius_km": self.radius_km,
            "global_score": self.global_score,
            "global_rating": self.global_rating,
            "modules_count": len(self.modules),
            "species_analyzed": [s.species for s in self.species],
            "top_species": max(self.species, key=lambda s: s.suitability_score).species if self.species else None,
            "recommendations_count": len(self.recommendations),
            "has_predictions": self.predictions is not None,
            "has_temporal": self.temporal is not None,
            "analyzed_at": self.created_at.isoformat(),
            "engine_version": self.engine_version
        }


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class TerritoryAnalysisRequest(BaseModel):
    """Requête d'analyse de territoire"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, gt=0, le=50)
    
    # Options d'analyse
    target_species: List[SpeciesType] = [SpeciesType.DEER]
    include_modules: List[ModuleType] = [
        ModuleType.VEGETATION,
        ModuleType.HYDROLOGY,
        ModuleType.TERRAIN
    ]
    include_predictions: bool = True
    include_temporal: bool = False
    
    # Filtres temporels
    analysis_date: Optional[datetime] = None
    
    model_config = ConfigDict(use_enum_values=True)


class TerritoryAnalysisSummary(BaseModel):
    """Résumé compact d'une analyse"""
    territory_id: str
    global_score: float
    global_rating: str
    top_species: Optional[str] = None
    top_recommendation: Optional[str] = None
    analyzed_at: datetime
    
    model_config = ConfigDict(use_enum_values=True)
