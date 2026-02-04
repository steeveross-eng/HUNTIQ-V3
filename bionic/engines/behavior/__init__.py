"""
BIONIC™ Behavior Suite
=======================
Suite de moteurs comportementaux pour l'intelligence faunique.

Version: 1.0 - P0 Étape 1 (Fondations)

Moteurs inclus:
- BehaviorEngine: Analyse comportementale globale
- SeasonalAttractivenessEngine: Attractivité saisonnière
- ActivityProbabilityEngine: Probabilité d'activité
- RutPredictionEngine: Prédiction du rut
- MovementEngine: Analyse des mouvements
- SpeciesModelEngine: Modèle spécifique par espèce
"""

from .core.behavior_engine import behavior_engine, BehaviorEngine
from .core.seasonal_attractiveness_engine import seasonal_attractiveness_engine, SeasonalAttractivenessEngine
from .core.activity_probability_engine import activity_probability_engine, ActivityProbabilityEngine
from .core.rut_prediction_engine import rut_prediction_engine, RutPredictionEngine
from .core.movement_engine import movement_engine, MovementEngine
from .core.species_model_engine import species_model_engine, SpeciesModelEngine

from .api.endpoints import behavior_router

__all__ = [
    # Engines
    "behavior_engine", "BehaviorEngine",
    "seasonal_attractiveness_engine", "SeasonalAttractivenessEngine",
    "activity_probability_engine", "ActivityProbabilityEngine",
    "rut_prediction_engine", "RutPredictionEngine",
    "movement_engine", "MovementEngine",
    "species_model_engine", "SpeciesModelEngine",
    # Router
    "behavior_router"
]

__version__ = "1.0.0"
