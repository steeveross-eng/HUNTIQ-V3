"""
BIONIC™ CORE Engine
====================
Moteur central consolidant toutes les analyses de territoire.
Produit des analyses complètes avec modules thématiques,
modèles fauniques et prédictions IA.

Architecture:
- configs.py: Configurations des modules et espèces
- helpers.py: Fonctions utilitaires partagées
- module_runner.py: Calcul des scores de modules
- species_engine.py: Calcul des scores d'espèces
- prediction_engine.py: Prédictions IA
- temporal_engine.py: Analyses temporelles
- geojson_builder.py: Construction GeoJSON
- orchestrator.py: Orchestrateur principal

Version: BIONIC_CORE 2.0
"""

# Import configs
from .configs import (
    ModuleType,
    SpeciesType,
    SeasonType,
    MODULE_CONFIGS,
    SPECIES_CONFIGS,
    SEASON_FACTORS,
    TIME_OF_DAY_FACTORS,
)

# Import helpers
from .helpers import (
    get_current_season,
    get_season_factor,
    get_rating,
    simulate_factor_value,
    generate_hotspots,
    aspect_to_direction,
    interpret_ndvi,
    calculate_weighted_score,
    clamp,
    format_weather_for_ai,
)

# Import engines
from .module_runner import ModuleRunner, module_runner
from .species_engine import SpeciesEngine, species_engine
from .prediction_engine import PredictionEngine, prediction_engine
from .temporal_engine import TemporalEngine, temporal_engine
from .geojson_builder import (
    build_point_geojson,
    build_polygon_geojson,
    build_feature_collection,
    build_bounding_box,
    build_hotspot_geojson,
    build_analysis_geojson,
)

# Import orchestrator
from .orchestrator import BionicOrchestrator, bionic_orchestrator

# Import Pydantic models for API responses
try:
    from .models import (
        # Enums additionnels (spécifiques aux modèles)
        ScoreRating,
        PredictionHorizon,
        Season,  # Alias de SeasonType
        
        # Sub-models
        GeoPoint,
        BoundingBox,
        DataSourceInfo,
        ScoreBreakdown,
        Recommendation,
        
        # Module Results
        ModuleResult,
        ThermalModuleResult,
        WetnessModuleResult,
        FoodModuleResult,
        CoverModuleResult,
        
        # Species Results
        HabitatSuitability,
        ActivityPattern,
        SpeciesResult,
        
        # Prediction Results
        SinglePrediction,
        PredictionResult,
        
        # Temporal Results
        NDVITimeSeries,
        SnowAnalysis,
        PhenologyData,
        TemporalResult,
        
        # Main Model
        TerritoryFullAnalysis,
        
        # Request/Response
        TerritoryAnalysisRequest,
        TerritoryAnalysisSummary,
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

__version__ = "2.0.0"
__all__ = [
    # Configs
    "ModuleType",
    "SpeciesType",
    "SeasonType",
    "MODULE_CONFIGS",
    "SPECIES_CONFIGS",
    "SEASON_FACTORS",
    "TIME_OF_DAY_FACTORS",
    
    # Helpers
    "get_current_season",
    "get_season_factor",
    "get_rating",
    "simulate_factor_value",
    "generate_hotspots",
    "aspect_to_direction",
    "interpret_ndvi",
    "calculate_weighted_score",
    "clamp",
    "format_weather_for_ai",
    
    # Engines
    "ModuleRunner",
    "module_runner",
    "SpeciesEngine",
    "species_engine",
    "PredictionEngine",
    "prediction_engine",
    "TemporalEngine",
    "temporal_engine",
    
    # GeoJSON
    "build_point_geojson",
    "build_polygon_geojson",
    "build_feature_collection",
    "build_bounding_box",
    "build_hotspot_geojson",
    "build_analysis_geojson",
    
    # Orchestrator
    "BionicOrchestrator",
    "bionic_orchestrator",
]
