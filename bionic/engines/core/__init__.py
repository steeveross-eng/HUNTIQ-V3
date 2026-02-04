"""
BIONIC™ CORE Engine

Moteur central consolidant toutes les analyses de territoire.
Produit des analyses complètes avec modules thématiques,
modèles fauniques et prédictions IA.

Version: BIONIC_CORE 1.0
"""

from .models import (
    # Enums
    ModuleType,
    SpeciesType,
    ScoreRating,
    PredictionHorizon,
    Season,
    
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

__version__ = "1.0.0"
__all__ = [
    # Enums
    "ModuleType",
    "SpeciesType",
    "ScoreRating",
    "PredictionHorizon",
    "Season",
    
    # Sub-models
    "GeoPoint",
    "BoundingBox",
    "DataSourceInfo",
    "ScoreBreakdown",
    "Recommendation",
    
    # Module Results
    "ModuleResult",
    "ThermalModuleResult",
    "WetnessModuleResult",
    "FoodModuleResult",
    "CoverModuleResult",
    
    # Species Results
    "HabitatSuitability",
    "ActivityPattern",
    "SpeciesResult",
    
    # Prediction Results
    "SinglePrediction",
    "PredictionResult",
    
    # Temporal Results
    "NDVITimeSeries",
    "SnowAnalysis",
    "PhenologyData",
    "TemporalResult",
    
    # Main Model
    "TerritoryFullAnalysis",
    
    # Request/Response
    "TerritoryAnalysisRequest",
    "TerritoryAnalysisSummary",
]
