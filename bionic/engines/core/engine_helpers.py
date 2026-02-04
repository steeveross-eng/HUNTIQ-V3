"""
BIONIC™ Core - Engine Helpers
==============================
Helpers et fonctions utilitaires pour tous les moteurs.

Version: 2.0 - Phase 3 Étape 2
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class EngineOutputBuilder:
    """
    Builder pour construire des sorties standardisées de moteur.
    
    Usage:
        builder = EngineOutputBuilder("SentinelEngine", "2.0.0")
        output = builder.build(
            lat=47.5, lon=-72.5,
            score=75.5,
            components={"ndvi": 80, "cover": 70},
            data={...},
            recommendations=[...]
        )
    """
    
    def __init__(self, engine_name: str, engine_version: str):
        self.engine_name = engine_name
        self.engine_version = engine_version
        self._prefix = self._get_prefix(engine_name)
    
    def _get_prefix(self, engine_name: str) -> str:
        """Génère un préfixe pour les IDs d'analyse."""
        prefixes = {
            "SentinelEngine": "sen",
            "SigeomEngine": "geo",
            "TerrainEngine": "ter",
            "PressureEngine": "pre",
            "HydrologyEngine": "hyd",
            "CorridorEngine": "cor",
            "LandcoverEngine": "lnd",
            "BehaviorEngine": "beh",
            "SeasonalAttractivenessEngine": "sea",
            "ActivityProbabilityEngine": "act",
            "RutPredictionEngine": "rut",
            "MovementEngine": "mov",
            "SpeciesModelEngine": "spe"
        }
        return prefixes.get(engine_name, "eng")
    
    def generate_analysis_id(self) -> str:
        """Génère un ID d'analyse unique."""
        return f"{self._prefix}_{uuid.uuid4().hex[:12]}"
    
    def score_to_level(self, score: float) -> str:
        """Convertit un score en niveau textuel."""
        if score >= 90:
            return "exceptional"
        elif score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "moderate"
        elif score >= 20:
            return "low"
        else:
            return "poor"
    
    def confidence_to_level(self, confidence: float) -> str:
        """Convertit une confiance en niveau textuel."""
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.75:
            return "high"
        elif confidence >= 0.5:
            return "moderate"
        elif confidence >= 0.25:
            return "low"
        else:
            return "very_low"
    
    def build_metadata(
        self,
        data_source: str,
        confidence: float,
        processing_time_ms: int = 0,
        from_cache: bool = False,
        cache_age_seconds: Optional[int] = None,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Construit les métadonnées standardisées."""
        return {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "analysis_id": analysis_id or self.generate_analysis_id(),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "processing_time_ms": processing_time_ms,
            "data_source": data_source,
            "data_source_type": "cached" if from_cache else "modeled",
            "confidence": round(confidence, 3),
            "confidence_level": self.confidence_to_level(confidence),
            "from_cache": from_cache,
            "cache_age_seconds": cache_age_seconds
        }
    
    def build_score(
        self,
        score: float,
        components: Dict[str, float] = None,
        interpretation: str = ""
    ) -> Dict[str, Any]:
        """Construit un score standardisé."""
        return {
            "score": round(score, 1),
            "level": self.score_to_level(score),
            "components": components or {},
            "interpretation": interpretation
        }
    
    def build_output(
        self,
        lat: float,
        lon: float,
        score: float,
        data_source: str,
        confidence: float,
        components: Dict[str, float] = None,
        interpretation: str = "",
        recommendations: List[str] = None,
        extra_data: Dict[str, Any] = None,
        processing_time_ms: int = 0,
        from_cache: bool = False,
        analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Construit une sortie complète standardisée.
        
        Returns:
            Dict avec structure:
            - metadata: métadonnées du moteur
            - location: {lat, lon}
            - overall_score: score standardisé
            - recommendations: liste de recommandations
            - ... extra_data
        """
        output = {
            "metadata": self.build_metadata(
                data_source=data_source,
                confidence=confidence,
                processing_time_ms=processing_time_ms,
                from_cache=from_cache,
                analysis_id=analysis_id
            ),
            "location": {"lat": lat, "lon": lon},
            "overall_score": self.build_score(
                score=score,
                components=components,
                interpretation=interpretation
            ),
            "recommendations": recommendations or []
        }
        
        # Ajouter les données supplémentaires
        if extra_data:
            output.update(extra_data)
        
        return output


class EngineValidator:
    """
    Validateur pour vérifier la cohérence des sorties de moteur.
    """
    
    REQUIRED_FIELDS = [
        "location",
        "analyzed_at",
        "data_source",
        "confidence",
        "overall_score",
        "recommendations",
        "from_cache"
    ]
    
    SCORE_FIELDS = ["score", "level"]
    
    @classmethod
    def validate_output(cls, output: Dict[str, Any], engine_name: str) -> List[str]:
        """
        Valide une sortie de moteur.
        
        Returns:
            Liste des erreurs de validation (vide si OK)
        """
        errors = []
        
        # Vérifier les champs requis
        for field in cls.REQUIRED_FIELDS:
            if field not in output:
                errors.append(f"[{engine_name}] Missing required field: {field}")
        
        # Vérifier la structure du score
        if "overall_score" in output:
            score = output["overall_score"]
            if isinstance(score, dict):
                for field in cls.SCORE_FIELDS:
                    if field not in score:
                        errors.append(f"[{engine_name}] Missing score field: {field}")
                
                # Vérifier les bornes du score
                if "score" in score:
                    s = score["score"]
                    if not isinstance(s, (int, float)) or s < 0 or s > 100:
                        errors.append(f"[{engine_name}] Score out of bounds: {s}")
        
        # Vérifier la confiance
        if "confidence" in output:
            conf = output["confidence"]
            if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
                errors.append(f"[{engine_name}] Confidence out of bounds: {conf}")
        
        # Vérifier la localisation
        if "location" in output:
            loc = output["location"]
            if isinstance(loc, dict):
                if "lat" not in loc or "lon" not in loc:
                    errors.append(f"[{engine_name}] Location missing lat/lon")
                else:
                    if not (-90 <= loc["lat"] <= 90):
                        errors.append(f"[{engine_name}] Invalid latitude: {loc['lat']}")
                    if not (-180 <= loc["lon"] <= 180):
                        errors.append(f"[{engine_name}] Invalid longitude: {loc['lon']}")
        
        return errors
    
    @classmethod
    def validate_all(cls, outputs: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Valide plusieurs sorties de moteurs.
        
        Args:
            outputs: Dict {engine_name: output_dict}
        
        Returns:
            Dict {engine_name: [errors]}
        """
        results = {}
        for engine_name, output in outputs.items():
            errors = cls.validate_output(output, engine_name)
            if errors:
                results[engine_name] = errors
        return results


class ScoreAggregator:
    """
    Agrégateur de scores pour combiner les résultats de plusieurs moteurs.
    """
    
    DEFAULT_WEIGHTS = {
        "vegetation": 0.25,
        "geology": 0.15,
        "terrain": 0.15,
        "pressure": 0.20,
        "hydrology": 0.10,
        "landcover": 0.10,
        "corridor": 0.05
    }
    
    @classmethod
    def aggregate(
        cls,
        scores: Dict[str, float],
        weights: Dict[str, float] = None
    ) -> float:
        """
        Agrège plusieurs scores avec pondération.
        
        Args:
            scores: Dict {module_name: score}
            weights: Dict {module_name: weight} (optionnel)
        
        Returns:
            Score agrégé (0-100)
        """
        if not scores:
            return 50.0
        
        weights = weights or cls.DEFAULT_WEIGHTS
        
        total_weight = 0
        weighted_sum = 0
        
        for module, score in scores.items():
            weight = weights.get(module, 0.1)  # Poids par défaut si non spécifié
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 50.0
        
        return round(weighted_sum / total_weight, 1)
    
    @classmethod
    def aggregate_with_confidence(
        cls,
        scores: Dict[str, Dict[str, float]],
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Agrège des scores en tenant compte de la confiance.
        
        Args:
            scores: Dict {module: {"score": float, "confidence": float}}
        
        Returns:
            {"score": float, "confidence": float, "components": {...}}
        """
        if not scores:
            return {"score": 50.0, "confidence": 0.5, "components": {}}
        
        weights = weights or cls.DEFAULT_WEIGHTS
        
        total_weight = 0
        weighted_score_sum = 0
        weighted_conf_sum = 0
        components = {}
        
        for module, data in scores.items():
            score = data.get("score", 50)
            confidence = data.get("confidence", 0.5)
            weight = weights.get(module, 0.1)
            
            # Pondérer aussi par la confiance
            effective_weight = weight * confidence
            weighted_score_sum += score * effective_weight
            weighted_conf_sum += confidence * weight
            total_weight += effective_weight
            
            components[module] = round(score, 1)
        
        if total_weight == 0:
            return {"score": 50.0, "confidence": 0.5, "components": components}
        
        return {
            "score": round(weighted_score_sum / total_weight, 1),
            "confidence": round(weighted_conf_sum / sum(weights.get(m, 0.1) for m in scores), 3),
            "components": components
        }


# Fonctions utilitaires globales
def generate_analysis_id(prefix: str = "eng") -> str:
    """Génère un ID d'analyse unique."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def normalize_score(value: float, min_val: float = 0, max_val: float = 100) -> float:
    """Normalise une valeur entre 0 et 100."""
    if max_val == min_val:
        return 50.0
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return round(max(0, min(100, normalized)), 1)


def get_timestamp() -> str:
    """Retourne un timestamp ISO."""
    return datetime.now(timezone.utc).isoformat()
