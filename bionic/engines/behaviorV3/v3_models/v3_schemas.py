"""
BIONIC™ P3 - BehaviorEngine v3.0 Schemas
=========================================
Modèles Pydantic 100% isolés pour le module v3.0.

Aucune dépendance avec les autres modules BIONIC.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class CalibrationStatus(str, Enum):
    """Statut d'une calibration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class FeedbackType(str, Enum):
    """Types de feedback utilisateur."""
    SUCCESS = "success"           # Chasse réussie
    PARTIAL = "partial"          # Partiellement utile
    FAILURE = "failure"          # Échec / non pertinent
    OBSERVATION = "observation"  # Observation sans chasse
    RATING = "rating"            # Note 1-5


class WeightCategory(str, Enum):
    """Catégories de pondérations."""
    ACTIVITY = "activity"
    SEASONAL = "seasonal"
    MOVEMENT = "movement"
    ENVIRONMENTAL = "environmental"
    TEMPORAL = "temporal"
    PRESSURE = "pressure"


class RollbackReason(str, Enum):
    """Raisons de rollback."""
    PERFORMANCE_DROP = "performance_drop"
    USER_REQUEST = "user_request"
    INVALID_WEIGHTS = "invalid_weights"
    SYSTEM_ERROR = "system_error"
    MAINTENANCE = "maintenance"


# =============================================================================
# INPUT MODELS
# =============================================================================

class FeedbackInput(BaseModel):
    """Input pour soumettre un feedback chasseur."""
    model_config = ConfigDict(extra="ignore")
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    species: str = Field(default="deer", description="Espèce ciblée")
    feedback_type: FeedbackType = Field(..., description="Type de feedback")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Note 1-5")
    observation_date: Optional[datetime] = Field(default=None, description="Date d'observation")
    notes: Optional[str] = Field(default=None, max_length=500, description="Notes")
    
    # Données contextuelles (optionnelles)
    weather_conditions: Optional[str] = Field(default=None, description="Conditions météo")
    time_of_day: Optional[str] = Field(default=None, description="Moment de la journée")
    hunt_duration_hours: Optional[float] = Field(default=None, ge=0, description="Durée chasse")
    animals_observed: Optional[int] = Field(default=None, ge=0, description="Animaux observés")
    harvest_success: Optional[bool] = Field(default=None, description="Récolte réussie")


class TrainingRequest(BaseModel):
    """Requête d'entraînement ML."""
    model_config = ConfigDict(extra="ignore")
    
    use_simulated_data: bool = Field(default=True, description="Utiliser données simulées")
    use_feedback_data: bool = Field(default=True, description="Utiliser feedback utilisateur")
    species_filter: Optional[List[str]] = Field(default=None, description="Filtrer par espèces")
    region_filter: Optional[str] = Field(default=None, description="Filtrer par région")
    min_feedback_count: int = Field(default=10, ge=1, description="Min feedbacks requis")
    max_iterations: int = Field(default=100, ge=10, le=1000, description="Max itérations")
    learning_rate: float = Field(default=0.1, ge=0.01, le=1.0, description="Taux apprentissage")


class CalibrationRequest(BaseModel):
    """Requête de calibration des pondérations."""
    model_config = ConfigDict(extra="ignore")
    
    species: str = Field(default="deer", description="Espèce cible")
    territory: str = Field(default="quebec", description="Territoire")
    season: Optional[str] = Field(default=None, description="Saison (auto-détectée)")
    apply_immediately: bool = Field(default=False, description="Appliquer immédiatement")
    save_to_history: bool = Field(default=True, description="Sauvegarder dans historique")


class RollbackRequest(BaseModel):
    """Requête de rollback vers une calibration précédente."""
    model_config = ConfigDict(extra="ignore")
    
    calibration_id: str = Field(..., description="ID de la calibration cible")
    reason: RollbackReason = Field(..., description="Raison du rollback")
    notes: Optional[str] = Field(default=None, description="Notes additionnelles")


# =============================================================================
# DATA MODELS
# =============================================================================

class WeightSet(BaseModel):
    """Ensemble de pondérations."""
    model_config = ConfigDict(extra="ignore")
    
    # Pondérations par catégorie (0.0 - 1.0)
    activity: float = Field(default=0.20, ge=0, le=1)
    seasonal: float = Field(default=0.20, ge=0, le=1)
    movement: float = Field(default=0.15, ge=0, le=1)
    environmental: float = Field(default=0.20, ge=0, le=1)
    temporal: float = Field(default=0.15, ge=0, le=1)
    pressure: float = Field(default=0.10, ge=0, le=1)
    
    # Métadonnées
    species: str = Field(default="deer")
    territory: str = Field(default="quebec")
    season: str = Field(default="fall")
    
    def to_dict(self) -> Dict[str, float]:
        """Retourne uniquement les poids numériques."""
        return {
            "activity": self.activity,
            "seasonal": self.seasonal,
            "movement": self.movement,
            "environmental": self.environmental,
            "temporal": self.temporal,
            "pressure": self.pressure
        }
    
    def normalize(self) -> "WeightSet":
        """Normalise les poids pour que la somme = 1."""
        weights = self.to_dict()
        total = sum(weights.values())
        if total > 0:
            for key in weights:
                setattr(self, key, weights[key] / total)
        return self


class CalibrationRecord(BaseModel):
    """Enregistrement d'une calibration."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: f"cal_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: CalibrationStatus = Field(default=CalibrationStatus.PENDING)
    
    # Contexte
    species: str
    territory: str
    season: str
    
    # Poids avant/après
    weights_before: Dict[str, float]
    weights_after: Dict[str, float]
    
    # Métriques
    improvement_score: float = Field(default=0.0, description="Amélioration en %")
    confidence: float = Field(default=0.0, ge=0, le=1)
    training_samples: int = Field(default=0)
    feedback_samples: int = Field(default=0)
    
    # Détails
    ml_model_version: str = Field(default="gradient_boosting_v1")
    notes: Optional[str] = None
    error_message: Optional[str] = None
    
    # Rollback info
    is_active: bool = Field(default=True)
    rolled_back_at: Optional[datetime] = None
    rollback_reason: Optional[RollbackReason] = None


class CalibrationHistory(BaseModel):
    """Historique complet des calibrations."""
    model_config = ConfigDict(extra="ignore")
    
    total_calibrations: int = 0
    active_calibration_id: Optional[str] = None
    records: List[CalibrationRecord] = Field(default_factory=list)
    
    # Statistiques
    avg_improvement: float = 0.0
    total_rollbacks: int = 0
    success_rate: float = 0.0


class TrainingMetrics(BaseModel):
    """Métriques d'entraînement ML."""
    model_config = ConfigDict(extra="ignore")
    
    training_id: str = Field(default_factory=lambda: f"train_{uuid.uuid4().hex[:8]}")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Données utilisées
    simulated_samples: int = 0
    feedback_samples: int = 0
    total_samples: int = 0
    
    # Performance
    iterations_completed: int = 0
    loss_initial: float = 0.0
    loss_final: float = 0.0
    accuracy: float = 0.0
    
    # Gradient Boosting specifics
    n_estimators_used: int = 100
    max_depth: int = 5
    learning_rate: float = 0.1
    
    # Validation
    validation_score: float = 0.0
    cross_validation_scores: List[float] = Field(default_factory=list)


class EngineStatus(BaseModel):
    """Statut du BehaviorEngine v3.0."""
    model_config = ConfigDict(extra="ignore")
    
    engine_name: str = "BehaviorEngine"
    version: str = "3.0.0"
    phase: str = "P3"
    status: str = "operational"
    
    # État actuel
    is_calibrated: bool = False
    last_calibration: Optional[datetime] = None
    active_calibration_id: Optional[str] = None
    current_weights: Optional[WeightSet] = None
    
    # Capacités
    capabilities: Dict[str, bool] = Field(default_factory=lambda: {
        "auto_calibration": True,
        "gradient_boosting": True,
        "feedback_collection": True,
        "rollback_support": True,
        "history_tracking": True,
        "simulated_data": True,
        "multi_species": True,
        "maintenance_mode": True
    })
    
    # Statistiques
    total_feedbacks: int = 0
    total_calibrations: int = 0
    total_rollbacks: int = 0


class EngineMetrics(BaseModel):
    """Métriques de performance du moteur."""
    model_config = ConfigDict(extra="ignore")
    
    # Performance générale
    avg_calibration_time_ms: float = 0.0
    avg_training_time_ms: float = 0.0
    avg_prediction_time_ms: float = 0.0
    
    # Qualité des calibrations
    avg_improvement_score: float = 0.0
    avg_confidence: float = 0.0
    calibration_success_rate: float = 0.0
    
    # Feedback
    total_feedbacks: int = 0
    positive_feedbacks: int = 0
    negative_feedbacks: int = 0
    feedback_rate: float = 0.0
    
    # Données
    total_training_samples: int = 0
    simulated_samples_ratio: float = 0.0
    
    # Rollbacks
    total_rollbacks: int = 0
    rollback_rate: float = 0.0


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class CalibrationResponse(BaseModel):
    """Réponse après une calibration."""
    model_config = ConfigDict(extra="ignore")
    
    success: bool
    calibration_id: str
    status: CalibrationStatus
    weights_applied: WeightSet
    improvement_score: float
    confidence: float
    message: str
    processing_time_ms: int


class TrainingResponse(BaseModel):
    """Réponse après un entraînement."""
    model_config = ConfigDict(extra="ignore")
    
    success: bool
    training_id: str
    metrics: TrainingMetrics
    message: str
    new_model_ready: bool


class RollbackResponse(BaseModel):
    """Réponse après un rollback."""
    model_config = ConfigDict(extra="ignore")
    
    success: bool
    rolled_back_from: str
    rolled_back_to: str
    weights_restored: WeightSet
    reason: RollbackReason
    message: str


class FeedbackResponse(BaseModel):
    """Réponse après soumission de feedback."""
    model_config = ConfigDict(extra="ignore")
    
    success: bool
    feedback_id: str
    received_at: datetime
    message: str
    calibration_impact: str  # "immediate", "queued", "minimal"


class WeightsResponse(BaseModel):
    """Réponse avec les pondérations actuelles."""
    model_config = ConfigDict(extra="ignore")
    
    current_weights: WeightSet
    calibration_id: Optional[str]
    last_updated: Optional[datetime]
    is_default: bool
    species_optimized: bool


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "CalibrationStatus",
    "FeedbackType",
    "WeightCategory",
    "RollbackReason",
    
    # Input Models
    "FeedbackInput",
    "TrainingRequest",
    "CalibrationRequest",
    "RollbackRequest",
    
    # Data Models
    "WeightSet",
    "CalibrationRecord",
    "CalibrationHistory",
    "TrainingMetrics",
    "EngineStatus",
    "EngineMetrics",
    
    # Response Models
    "CalibrationResponse",
    "TrainingResponse",
    "RollbackResponse",
    "FeedbackResponse",
    "WeightsResponse"
]
