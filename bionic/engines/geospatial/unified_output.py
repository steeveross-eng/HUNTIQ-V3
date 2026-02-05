"""
BIONIC™ P1 - Unified Output Contracts
======================================
Contrats de sortie unifiés pour garantir la compatibilité
avec BehaviorFusionEngine (P2).

Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ScoreLevel(str, Enum):
    """Niveaux de score standardisés."""
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


class DataQuality(str, Enum):
    """Qualité des données sources."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"


# =============================================================================
# BASE STRUCTURES
# =============================================================================

@dataclass
class UnifiedMetadata:
    """Métadonnées standardisées pour tous les moteurs P1."""
    engine_name: str
    engine_version: str
    analysis_id: str
    analyzed_at: str
    processing_time_ms: int
    data_sources_used: List[str]
    region: str
    confidence: float
    confidence_level: str
    data_quality: str = "good"
    from_cache: bool = False
    cache_age_seconds: Optional[int] = None
    
    @classmethod
    def create(
        cls,
        engine_name: str,
        engine_version: str,
        data_sources: List[str],
        region: str,
        confidence: float,
        processing_time_ms: int = 0,
        from_cache: bool = False
    ) -> "UnifiedMetadata":
        """Factory method pour créer des métadonnées."""
        prefix = engine_name[:3].lower()
        analysis_id = f"{prefix}_{uuid.uuid4().hex[:12]}"
        
        return cls(
            engine_name=engine_name,
            engine_version=engine_version,
            analysis_id=analysis_id,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
            processing_time_ms=processing_time_ms,
            data_sources_used=data_sources,
            region=region,
            confidence=round(confidence, 3),
            confidence_level=cls._confidence_to_level(confidence),
            from_cache=from_cache
        )
    
    @staticmethod
    def _confidence_to_level(confidence: float) -> str:
        """Convertit une confiance en niveau."""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH.value
        elif confidence >= 0.75:
            return ConfidenceLevel.HIGH.value
        elif confidence >= 0.5:
            return ConfidenceLevel.MODERATE.value
        elif confidence >= 0.25:
            return ConfidenceLevel.LOW.value
        return ConfidenceLevel.VERY_LOW.value


@dataclass
class UnifiedLocation:
    """Localisation standardisée."""
    lat: float
    lon: float
    radius_km: float = 2.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UnifiedScore:
    """Score standardisé."""
    value: float  # 0-100
    level: str
    components: Dict[str, float] = field(default_factory=dict)
    interpretation: str = ""
    
    @classmethod
    def create(
        cls,
        value: float,
        components: Optional[Dict[str, float]] = None,
        interpretation: str = ""
    ) -> "UnifiedScore":
        """Factory method pour créer un score."""
        level = cls._value_to_level(value)
        return cls(
            value=round(value, 1),
            level=level,
            components=components or {},
            interpretation=interpretation
        )
    
    @staticmethod
    def _value_to_level(value: float) -> str:
        """Convertit une valeur en niveau."""
        if value >= 90:
            return ScoreLevel.EXCEPTIONAL.value
        elif value >= 80:
            return ScoreLevel.EXCELLENT.value
        elif value >= 60:
            return ScoreLevel.GOOD.value
        elif value >= 40:
            return ScoreLevel.MODERATE.value
        elif value >= 20:
            return ScoreLevel.LOW.value
        return ScoreLevel.POOR.value
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FusionHooks:
    """
    Hooks pour l'intégration avec BehaviorFusionEngine (P2).
    
    Ces données permettent la fusion avec la Behavior Suite.
    """
    behavior_compatibility: float = 0.75  # Compatibilité avec les scores comportementaux
    seasonal_modifier: float = 1.0        # Modificateur saisonnier à appliquer
    activity_correlation: float = 0.7     # Corrélation avec l'activité
    movement_correlation: float = 0.6     # Corrélation avec le mouvement
    species_factors: Dict[str, float] = field(default_factory=dict)  # Facteurs par espèce
    
    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# UNIFIED OUTPUT CONTRACT
# =============================================================================

@dataclass
class UnifiedOutput:
    """
    Contrat de sortie unifié pour tous les moteurs géospatiaux P1.
    
    Ce format garantit la compatibilité avec:
    - BehaviorFusionEngine (P2)
    - Frontend BIONIC™
    - Cache multi-niveaux
    - Tests d'intégration
    """
    metadata: UnifiedMetadata
    location: UnifiedLocation
    score: UnifiedScore
    data: Dict[str, Any]
    recommendations: List[str]
    fusion_hooks: FusionHooks
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire JSON-serializable."""
        return {
            "metadata": asdict(self.metadata),
            "location": asdict(self.location),
            "score": asdict(self.score),
            "data": self.data,
            "recommendations": self.recommendations,
            "fusion_hooks": asdict(self.fusion_hooks),
            "warnings": self.warnings,
            "errors": self.errors
        }
    
    def get_fusion_output(self) -> Dict[str, Any]:
        """
        Retourne une sortie compatible avec BehaviorFusionEngine.
        
        Cette méthode est appelée lors de la fusion P2.
        """
        return {
            "score_normalized": self.score.value / 100,
            "confidence": self.metadata.confidence,
            "weight_suggestion": self._calculate_fusion_weight(),
            "seasonal_factor": self.fusion_hooks.seasonal_modifier,
            "species_factors": self.fusion_hooks.species_factors,
            "behavior_correlation": self.fusion_hooks.behavior_compatibility,
            "activity_correlation": self.fusion_hooks.activity_correlation,
            "movement_correlation": self.fusion_hooks.movement_correlation,
            "engine_name": self.metadata.engine_name,
            "analysis_id": self.metadata.analysis_id
        }
    
    def _calculate_fusion_weight(self) -> float:
        """Calcule le poids suggéré pour la fusion."""
        # Basé sur la confiance et la qualité des données
        base_weight = 0.2  # Poids de base
        confidence_bonus = self.metadata.confidence * 0.1
        return min(0.4, base_weight + confidence_bonus)


# =============================================================================
# OUTPUT BUILDER
# =============================================================================

class UnifiedOutputBuilder:
    """
    Builder pour construire des UnifiedOutput de manière fluide.
    
    Usage:
        output = (UnifiedOutputBuilder("CorridorEngine", "1.0.0")
            .set_location(47.5, -72.5, 2.0)
            .set_score(75.5, {"connectivity": 80, "diversity": 70})
            .set_data({"corridors": [...]})
            .add_recommendation("Focus on riparian corridors")
            .build())
    """
    
    def __init__(self, engine_name: str, engine_version: str):
        self.engine_name = engine_name
        self.engine_version = engine_version
        self._location: Optional[UnifiedLocation] = None
        self._score: Optional[UnifiedScore] = None
        self._data: Dict[str, Any] = {}
        self._recommendations: List[str] = []
        self._warnings: List[str] = []
        self._errors: List[str] = []
        self._data_sources: List[str] = []
        self._region: str = "unknown"
        self._confidence: float = 0.7
        self._processing_time_ms: int = 0
        self._from_cache: bool = False
        self._fusion_hooks: Optional[FusionHooks] = None
    
    def set_location(self, lat: float, lon: float, radius_km: float = 2.0) -> "UnifiedOutputBuilder":
        """Définit la localisation."""
        self._location = UnifiedLocation(lat=lat, lon=lon, radius_km=radius_km)
        return self
    
    def set_score(
        self,
        value: float,
        components: Optional[Dict[str, float]] = None,
        interpretation: str = ""
    ) -> "UnifiedOutputBuilder":
        """Définit le score."""
        self._score = UnifiedScore.create(value, components, interpretation)
        return self
    
    def set_data(self, data: Dict[str, Any]) -> "UnifiedOutputBuilder":
        """Définit les données."""
        self._data = data
        return self
    
    def add_data(self, key: str, value: Any) -> "UnifiedOutputBuilder":
        """Ajoute une donnée."""
        self._data[key] = value
        return self
    
    def add_recommendation(self, recommendation: str) -> "UnifiedOutputBuilder":
        """Ajoute une recommandation."""
        self._recommendations.append(recommendation)
        return self
    
    def set_recommendations(self, recommendations: List[str]) -> "UnifiedOutputBuilder":
        """Définit toutes les recommandations."""
        self._recommendations = recommendations
        return self
    
    def add_warning(self, warning: str) -> "UnifiedOutputBuilder":
        """Ajoute un avertissement."""
        self._warnings.append(warning)
        return self
    
    def add_error(self, error: str) -> "UnifiedOutputBuilder":
        """Ajoute une erreur."""
        self._errors.append(error)
        return self
    
    def set_data_sources(self, sources: List[str]) -> "UnifiedOutputBuilder":
        """Définit les sources de données."""
        self._data_sources = sources
        return self
    
    def set_region(self, region: str) -> "UnifiedOutputBuilder":
        """Définit la région."""
        self._region = region
        return self
    
    def set_confidence(self, confidence: float) -> "UnifiedOutputBuilder":
        """Définit la confiance."""
        self._confidence = max(0.0, min(1.0, confidence))
        return self
    
    def set_processing_time(self, ms: int) -> "UnifiedOutputBuilder":
        """Définit le temps de traitement."""
        self._processing_time_ms = ms
        return self
    
    def set_from_cache(self, from_cache: bool) -> "UnifiedOutputBuilder":
        """Indique si les données viennent du cache."""
        self._from_cache = from_cache
        return self
    
    def set_fusion_hooks(
        self,
        behavior_compatibility: float = 0.75,
        seasonal_modifier: float = 1.0,
        activity_correlation: float = 0.7,
        movement_correlation: float = 0.6,
        species_factors: Optional[Dict[str, float]] = None
    ) -> "UnifiedOutputBuilder":
        """Définit les hooks de fusion."""
        self._fusion_hooks = FusionHooks(
            behavior_compatibility=behavior_compatibility,
            seasonal_modifier=seasonal_modifier,
            activity_correlation=activity_correlation,
            movement_correlation=movement_correlation,
            species_factors=species_factors or {}
        )
        return self
    
    def build(self) -> UnifiedOutput:
        """Construit le UnifiedOutput."""
        if self._location is None:
            raise ValueError("Location must be set")
        
        if self._score is None:
            self._score = UnifiedScore.create(50.0, {}, "Score par défaut")
        
        metadata = UnifiedMetadata.create(
            engine_name=self.engine_name,
            engine_version=self.engine_version,
            data_sources=self._data_sources,
            region=self._region,
            confidence=self._confidence,
            processing_time_ms=self._processing_time_ms,
            from_cache=self._from_cache
        )
        
        if self._fusion_hooks is None:
            self._fusion_hooks = FusionHooks()
        
        return UnifiedOutput(
            metadata=metadata,
            location=self._location,
            score=self._score,
            data=self._data,
            recommendations=self._recommendations[:10],
            fusion_hooks=self._fusion_hooks,
            warnings=self._warnings,
            errors=self._errors
        )


# =============================================================================
# FUSION INTERFACE
# =============================================================================

class FusionInterface:
    """
    Interface pour la fusion avec BehaviorFusionEngine (P2).
    
    Tous les moteurs géospatiaux P1 implémentent cette interface.
    """
    
    @staticmethod
    def get_fusion_weights() -> Dict[str, Dict[str, float]]:
        """
        Retourne les poids de fusion par moteur.
        
        Ces poids définissent comment chaque moteur géospatial
        se combine avec les moteurs comportementaux.
        """
        return {
            "corridor": {
                "behavior": 0.25,
                "seasonal": 0.20,
                "activity": 0.20,
                "movement": 0.35
            },
            "landcover": {
                "behavior": 0.25,
                "seasonal": 0.30,
                "activity": 0.15,
                "movement": 0.30
            },
            "nutrition": {
                "behavior": 0.20,
                "seasonal": 0.35,
                "activity": 0.15,
                "movement": 0.30
            },
            "population": {
                "behavior": 0.30,
                "seasonal": 0.25,
                "activity": 0.25,
                "movement": 0.20
            },
            "pressure": {
                "behavior": 0.35,
                "seasonal": 0.20,
                "activity": 0.30,
                "movement": 0.15
            }
        }
    
    @staticmethod
    def calculate_fusion_score(
        geospatial_outputs: Dict[str, UnifiedOutput],
        behavior_scores: Dict[str, float]
    ) -> float:
        """
        Calcule le score de fusion entre géospatial et comportement.
        
        Cette méthode sera utilisée par BehaviorFusionEngine (P2).
        """
        weights = FusionInterface.get_fusion_weights()
        total_weight = 0.0
        weighted_sum = 0.0
        
        for engine_name, output in geospatial_outputs.items():
            engine_key = engine_name.replace("Engine", "").lower()
            engine_weights = weights.get(engine_key, {})
            
            if not engine_weights:
                continue
            
            # Score géospatial normalisé
            geo_score = output.score.value / 100
            
            # Combiner avec les scores comportementaux
            combined = geo_score * 0.5
            
            for behavior_key, weight in engine_weights.items():
                if behavior_key in behavior_scores:
                    combined += behavior_scores[behavior_key] * weight * 0.5
            
            # Pondérer par la confiance
            confidence = output.metadata.confidence
            weighted_sum += combined * confidence
            total_weight += confidence
        
        if total_weight > 0:
            return round((weighted_sum / total_weight) * 100, 1)
        
        return 50.0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ScoreLevel",
    "ConfidenceLevel",
    "DataQuality",
    "UnifiedMetadata",
    "UnifiedLocation",
    "UnifiedScore",
    "FusionHooks",
    "UnifiedOutput",
    "UnifiedOutputBuilder",
    "FusionInterface"
]


logger.info("BIONIC™ Unified Output Contracts loaded (v1.0.0)")
