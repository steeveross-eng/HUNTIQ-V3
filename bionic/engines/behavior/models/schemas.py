"""
BIONIC™ Behavior Suite - Models
================================
Modèles Pydantic pour les moteurs comportementaux.

Version: 1.0 - P0 Étape 1 (Fondations)
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class SpeciesCode(str, Enum):
    """Codes d'espèces supportées."""
    MOOSE = "moose"
    DEER = "deer"
    BEAR = "bear"
    CARIBOU = "caribou"
    WOLF = "wolf"
    TURKEY = "turkey"
    WATERFOWL = "waterfowl"
    SMALLGAME = "smallgame"


class ActivityLevel(str, Enum):
    """Niveaux d'activité."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    PEAK = "peak"


class RutPhase(str, Enum):
    """Phases du rut."""
    PRE_RUT = "pre_rut"
    SEEKING = "seeking"
    CHASING = "chasing"
    BREEDING = "breeding"
    POST_RUT = "post_rut"
    RECOVERY = "recovery"


class MovementPattern(str, Enum):
    """Patterns de déplacement."""
    SEDENTARY = "sedentary"
    LOCAL = "local"
    REGIONAL = "regional"
    MIGRATORY = "migratory"
    DISPERSAL = "dispersal"


class SeasonalPhase(str, Enum):
    """Phases saisonnières de comportement."""
    WINTER_SURVIVAL = "winter_survival"
    SPRING_DISPERSAL = "spring_dispersal"
    SUMMER_FORAGING = "summer_foraging"
    PRE_RUT_PREPARATION = "pre_rut_preparation"
    RUT_ACTIVE = "rut_active"
    POST_RUT_RECOVERY = "post_rut_recovery"
    FALL_PREPARATION = "fall_preparation"


# =============================================================================
# INPUT MODELS
# =============================================================================

class BehaviorAnalysisInput(BaseModel):
    """Input pour l'analyse comportementale globale."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: SpeciesCode
    analysis_date: Optional[date] = None
    include_predictions: bool = True
    prediction_hours: int = Field(default=24, ge=1, le=168)
    
    # Données environnementales (optionnel, peut être fetché)
    temperature_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    moon_phase: Optional[float] = None  # 0-1
    barometric_pressure_hpa: Optional[float] = None


class SeasonalAttractivenessInput(BaseModel):
    """Input pour l'analyse d'attractivité saisonnière."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: SpeciesCode
    target_date: Optional[date] = None
    radius_km: float = Field(default=5.0, ge=0.5, le=50)
    
    # Données habitat (optionnel)
    ndvi: Optional[float] = None
    water_distance_m: Optional[float] = None
    elevation_m: Optional[float] = None


class ActivityProbabilityInput(BaseModel):
    """Input pour la probabilité d'activité."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: SpeciesCode
    target_datetime: Optional[datetime] = None
    
    # Conditions météo
    temperature_c: Optional[float] = None
    cloud_cover_percent: Optional[float] = None
    precipitation_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    
    # Phase lunaire
    moon_phase: Optional[float] = None
    moon_illumination: Optional[float] = None


class RutPredictionInput(BaseModel):
    """Input pour la prédiction du rut."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: SpeciesCode = Field(default=SpeciesCode.DEER)
    year: Optional[int] = None
    
    # Facteurs environnementaux
    photoperiod_hours: Optional[float] = None
    avg_temperature_30d: Optional[float] = None


class MovementAnalysisInput(BaseModel):
    """Input pour l'analyse de mouvement."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: SpeciesCode
    
    # Zone d'analyse
    bbox_min_lat: Optional[float] = None
    bbox_max_lat: Optional[float] = None
    bbox_min_lon: Optional[float] = None
    bbox_max_lon: Optional[float] = None
    
    # Paramètres corridor
    include_corridors: bool = True
    corridor_resolution_m: int = Field(default=100, ge=10, le=1000)


class SpeciesModelInput(BaseModel):
    """Input pour le modèle spécifique d'espèce."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    species: SpeciesCode
    analysis_type: str = Field(default="full")  # full, habitat, behavior, seasonal
    
    # Données environnementales agrégées
    environment_data: Optional[Dict[str, Any]] = None


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class TimeWindow(BaseModel):
    """Fenêtre temporelle d'activité."""
    start_hour: int = Field(..., ge=0, le=23)
    end_hour: int = Field(..., ge=0, le=23)
    probability: float = Field(..., ge=0, le=1)
    activity_level: ActivityLevel
    notes: Optional[str] = None


class HotspotPrediction(BaseModel):
    """Prédiction de hotspot."""
    latitude: float
    longitude: float
    score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    reason: str
    recommended_time: Optional[str] = None


class BehaviorAnalysisOutput(BaseModel):
    """Output de l'analyse comportementale globale."""
    # Métadonnées
    analysis_id: str
    species: SpeciesCode
    species_name_fr: str
    location: Dict[str, float]
    analyzed_at: datetime
    data_source: str = "BIONIC Behavior Engine"
    
    # Scores globaux
    overall_activity_score: float = Field(..., ge=0, le=100)
    hunting_opportunity_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    
    # Fenêtres d'activité
    peak_activity_windows: List[TimeWindow]
    current_activity_level: ActivityLevel
    
    # Facteurs comportementaux
    behavioral_factors: Dict[str, Any]
    
    # Prédictions
    predictions_24h: Optional[Dict[str, Any]] = None
    
    # Recommandations
    recommendations: List[str]
    
    # Cache info
    from_cache: bool = False


class SeasonalAttractivenessOutput(BaseModel):
    """Output de l'analyse d'attractivité saisonnière."""
    analysis_id: str
    species: SpeciesCode
    location: Dict[str, float]
    analyzed_at: datetime
    
    # Phase saisonnière
    current_phase: SeasonalPhase
    phase_name_fr: str
    days_into_phase: int
    days_remaining: int
    
    # Scores d'attractivité
    overall_attractiveness: float = Field(..., ge=0, le=100)
    food_attractiveness: float = Field(..., ge=0, le=100)
    cover_attractiveness: float = Field(..., ge=0, le=100)
    water_attractiveness: float = Field(..., ge=0, le=100)
    thermal_attractiveness: float = Field(..., ge=0, le=100)
    
    # Hotspots
    hotspots: List[HotspotPrediction]
    
    # Tendance
    trend: str  # increasing, stable, decreasing
    trend_description: str
    
    # Recommandations
    best_hunting_days: List[str]
    recommendations: List[str]
    
    from_cache: bool = False


class ActivityProbabilityOutput(BaseModel):
    """Output de la probabilité d'activité."""
    analysis_id: str
    species: SpeciesCode
    location: Dict[str, float]
    target_datetime: datetime
    analyzed_at: datetime
    
    # Probabilité globale
    activity_probability: float = Field(..., ge=0, le=1)
    activity_level: ActivityLevel
    
    # Probabilités par période
    hourly_probabilities: Dict[str, float]  # "06:00": 0.75
    
    # Facteurs d'influence
    factors: Dict[str, Dict[str, Any]]  # weather, lunar, seasonal
    
    # Fenêtre optimale
    optimal_window: TimeWindow
    
    # Prédiction confiance
    confidence: float = Field(..., ge=0, le=1)
    
    recommendations: List[str]
    from_cache: bool = False


class RutPredictionOutput(BaseModel):
    """Output de la prédiction du rut."""
    analysis_id: str
    species: SpeciesCode
    location: Dict[str, float]
    year: int
    analyzed_at: datetime
    
    # Phase actuelle
    current_phase: RutPhase
    phase_name_fr: str
    phase_intensity: float = Field(..., ge=0, le=1)
    
    # Timeline
    pre_rut_start: date
    seeking_start: date
    peak_breeding: date
    post_rut_start: date
    
    # Jours clés
    days_to_peak: int
    peak_dates: List[date]
    
    # Comportements attendus
    expected_behaviors: List[str]
    buck_activity_level: ActivityLevel
    doe_activity_level: ActivityLevel
    
    # Stratégies recommandées
    recommended_tactics: List[str]
    best_calling_times: List[str]
    
    confidence: float = Field(..., ge=0, le=1)
    from_cache: bool = False


class CorridorSegment(BaseModel):
    """Segment de corridor de déplacement."""
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    width_m: float
    usage_probability: float
    terrain_type: str
    notes: Optional[str] = None


class MovementAnalysisOutput(BaseModel):
    """Output de l'analyse de mouvement."""
    analysis_id: str
    species: SpeciesCode
    location: Dict[str, float]
    analyzed_at: datetime
    
    # Pattern de mouvement
    current_pattern: MovementPattern
    pattern_name_fr: str
    
    # Home range estimé
    home_range_km2: float
    core_area_km2: float
    
    # Corridors
    corridors: List[CorridorSegment]
    primary_corridor_score: float
    
    # Distances typiques
    daily_movement_km: float
    seasonal_range_km: float
    
    # Points d'intérêt
    bedding_areas: List[Dict[str, Any]]
    feeding_areas: List[Dict[str, Any]]
    travel_routes: List[Dict[str, Any]]
    
    # Prédictions de position
    likely_positions: List[HotspotPrediction]
    
    confidence: float = Field(..., ge=0, le=1)
    from_cache: bool = False


class SpeciesModelOutput(BaseModel):
    """Output du modèle spécifique d'espèce."""
    analysis_id: str
    species: SpeciesCode
    species_name_fr: str
    species_name_en: str
    location: Dict[str, float]
    analyzed_at: datetime
    
    # Profil de l'espèce
    species_profile: Dict[str, Any]
    
    # Habitat
    habitat_suitability: float = Field(..., ge=0, le=100)
    habitat_factors: Dict[str, float]
    
    # Comportement
    behavior_summary: Dict[str, Any]
    current_behavior_phase: str
    
    # Saisonnalité
    seasonal_factors: Dict[str, Any]
    
    # Score global
    overall_score: float = Field(..., ge=0, le=100)
    hunting_index: float = Field(..., ge=0, le=100)
    
    # Recommandations spécifiques
    species_specific_tips: List[str]
    optimal_tactics: List[str]
    gear_recommendations: List[str]
    
    confidence: float = Field(..., ge=0, le=1)
    from_cache: bool = False


# =============================================================================
# AGGREGATED OUTPUT FOR BIONIC CORE
# =============================================================================

class BehaviorSuiteOutput(BaseModel):
    """Output agrégé de la Behavior Suite pour BIONIC_CORE."""
    # Métadonnées
    suite_version: str = "1.0.0"
    analysis_id: str
    location: Dict[str, float]
    species: SpeciesCode
    analyzed_at: datetime
    processing_time_ms: int
    
    # Résultats des moteurs
    behavior: Optional[BehaviorAnalysisOutput] = None
    seasonal: Optional[SeasonalAttractivenessOutput] = None
    activity: Optional[ActivityProbabilityOutput] = None
    rut: Optional[RutPredictionOutput] = None
    movement: Optional[MovementAnalysisOutput] = None
    species_model: Optional[SpeciesModelOutput] = None
    
    # Scores consolidés
    global_opportunity_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    
    # Top recommandations
    top_recommendations: List[str]
    
    # Hotspots agrégés
    hotspots: List[HotspotPrediction]
    
    # Status
    engines_executed: List[str]
    from_cache: bool = False
