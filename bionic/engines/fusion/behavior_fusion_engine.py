"""
BIONIC™ P2 - BehaviorFusionEngine
=================================
Moteur de fusion entre la Behavior Suite et la Géo-Suite.

Fusionne les analyses comportementales avec les analyses géospatiales
pour produire un score global unifié et des heatmaps combinées.

Version: 1.0.0
Phase: P2
Architecture: Découplé, P3-Ready
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
import sys

# Add paths for imports
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class FusionMode(str, Enum):
    """Modes de fusion disponibles."""
    BALANCED = "balanced"           # Équilibré entre Geo et Behavior
    GEO_DOMINANT = "geo_dominant"   # Priorité géospatiale
    BEHAVIOR_DOMINANT = "behavior"  # Priorité comportementale
    ADAPTIVE = "adaptive"           # Auto-ajustement selon les données
    CUSTOM = "custom"               # Poids personnalisés


class FusionQuality(str, Enum):
    """Qualité de la fusion."""
    EXCELLENT = "excellent"  # > 85%
    GOOD = "good"           # 70-85%
    MODERATE = "moderate"   # 55-70%
    LOW = "low"             # 40-55%
    POOR = "poor"           # < 40%


# =============================================================================
# FUSION WEIGHT MANAGER
# =============================================================================

class FusionWeightManager:
    """
    Gestionnaire de pondérations pour la fusion.
    
    Permet l'ajustement dynamique des poids par:
    - Espèce
    - Territoire
    - Saison
    - Mode de fusion
    
    P3-Ready: Hooks pour auto-calibration ML.
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self._custom_weights: Dict[str, Dict] = {}
        self._calibration_history: List[Dict] = []
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialise les poids par défaut."""
        
        # Poids de base Geo vs Behavior
        self.base_weights = {
            "geo_suite": 0.5,
            "behavior_suite": 0.5
        }
        
        # Poids par moteur géospatial
        self.geo_engine_weights = {
            "corridor": 0.25,
            "landcover": 0.20,
            "nutrition": 0.20,
            "population": 0.20,
            "pressure": 0.15
        }
        
        # Poids par moteur comportemental
        self.behavior_engine_weights = {
            "behavior": 0.20,
            "seasonal": 0.20,
            "activity": 0.25,
            "movement": 0.20,
            "rut": 0.10,
            "species_model": 0.05
        }
        
        # Poids par espèce (modifient les poids de base)
        self.species_weights = {
            "deer": {
                "geo_suite": 0.45,
                "behavior_suite": 0.55,
                "geo_override": {"corridor": 0.30, "pressure": 0.20},
                "behavior_override": {"rut": 0.20, "movement": 0.25}
            },
            "moose": {
                "geo_suite": 0.55,
                "behavior_suite": 0.45,
                "geo_override": {"landcover": 0.25, "nutrition": 0.25},
                "behavior_override": {"seasonal": 0.25}
            },
            "bear": {
                "geo_suite": 0.50,
                "behavior_suite": 0.50,
                "geo_override": {"nutrition": 0.30},
                "behavior_override": {"seasonal": 0.30, "activity": 0.20}
            },
            "caribou": {
                "geo_suite": 0.60,
                "behavior_suite": 0.40,
                "geo_override": {"corridor": 0.35, "landcover": 0.25},
                "behavior_override": {"movement": 0.35}
            },
            "turkey": {
                "geo_suite": 0.45,
                "behavior_suite": 0.55,
                "geo_override": {"landcover": 0.30},
                "behavior_override": {"activity": 0.30}
            },
            "waterfowl": {
                "geo_suite": 0.55,
                "behavior_suite": 0.45,
                "geo_override": {"landcover": 0.35},
                "behavior_override": {"seasonal": 0.35}
            }
        }
        
        # Poids par territoire
        self.territory_weights = {
            "quebec": {
                "geo_multiplier": 1.0,
                "behavior_multiplier": 1.0,
                "pressure_boost": 1.1  # Plus de pression de chasse au QC
            },
            "canada": {
                "geo_multiplier": 1.05,
                "behavior_multiplier": 0.95,
                "corridor_boost": 1.1  # Plus de corridors au Canada
            },
            "usa": {
                "geo_multiplier": 0.95,
                "behavior_multiplier": 1.05,
                "pressure_boost": 1.15  # Plus de données de pression aux USA
            }
        }
        
        # Poids saisonniers
        self.seasonal_modifiers = {
            "winter": {
                "nutrition": 1.3,
                "seasonal": 1.2,
                "corridor": 1.1
            },
            "spring": {
                "nutrition": 1.2,
                "movement": 1.3,
                "activity": 1.1
            },
            "summer": {
                "landcover": 1.2,
                "seasonal": 1.1,
                "nutrition": 1.1
            },
            "fall": {
                "rut": 1.4,
                "activity": 1.3,
                "corridor": 1.2,
                "pressure": 1.2
            }
        }
        
        # Presets par mode
        self.mode_presets = {
            FusionMode.BALANCED: {"geo_suite": 0.5, "behavior_suite": 0.5},
            FusionMode.GEO_DOMINANT: {"geo_suite": 0.7, "behavior_suite": 0.3},
            FusionMode.BEHAVIOR_DOMINANT: {"geo_suite": 0.3, "behavior_suite": 0.7},
            FusionMode.ADAPTIVE: {"geo_suite": 0.5, "behavior_suite": 0.5}  # Ajusté dynamiquement
        }
    
    def get_weights(
        self,
        species: str = "deer",
        territory: str = "quebec",
        season: Optional[str] = None,
        mode: FusionMode = FusionMode.BALANCED,
        custom_weights: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Calcule les poids finaux pour la fusion.
        
        Args:
            species: Code de l'espèce
            territory: Territoire (quebec, canada, usa)
            season: Saison actuelle (winter, spring, summer, fall)
            mode: Mode de fusion
            custom_weights: Poids personnalisés (optionnel)
        
        Returns:
            Dictionnaire complet des poids
        """
        # Déterminer la saison si non fournie
        if season is None:
            month = datetime.now().month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "fall"
        
        # Base weights from mode
        if mode == FusionMode.CUSTOM and custom_weights:
            base = custom_weights.copy()
        else:
            base = self.mode_presets.get(mode, self.mode_presets[FusionMode.BALANCED]).copy()
        
        # Apply species weights
        species_config = self.species_weights.get(species, {})
        if species_config:
            base["geo_suite"] = species_config.get("geo_suite", base["geo_suite"])
            base["behavior_suite"] = species_config.get("behavior_suite", base["behavior_suite"])
        
        # Apply territory multipliers
        territory_config = self.territory_weights.get(territory, {})
        if territory_config:
            base["geo_suite"] *= territory_config.get("geo_multiplier", 1.0)
            base["behavior_suite"] *= territory_config.get("behavior_multiplier", 1.0)
        
        # Normalize to sum = 1
        total = base["geo_suite"] + base["behavior_suite"]
        base["geo_suite"] /= total
        base["behavior_suite"] /= total
        
        # Build geo engine weights
        geo_weights = self.geo_engine_weights.copy()
        if species_config.get("geo_override"):
            geo_weights.update(species_config["geo_override"])
        
        # Apply seasonal modifiers to geo weights
        seasonal_mods = self.seasonal_modifiers.get(season, {})
        for engine, modifier in seasonal_mods.items():
            if engine in geo_weights:
                geo_weights[engine] *= modifier
        
        # Apply territory boosts
        if territory_config.get("pressure_boost") and "pressure" in geo_weights:
            geo_weights["pressure"] *= territory_config["pressure_boost"]
        if territory_config.get("corridor_boost") and "corridor" in geo_weights:
            geo_weights["corridor"] *= territory_config["corridor_boost"]
        
        # Normalize geo weights
        geo_total = sum(geo_weights.values())
        geo_weights = {k: v / geo_total for k, v in geo_weights.items()}
        
        # Build behavior engine weights
        behavior_weights = self.behavior_engine_weights.copy()
        if species_config.get("behavior_override"):
            behavior_weights.update(species_config["behavior_override"])
        
        # Apply seasonal modifiers to behavior weights
        for engine, modifier in seasonal_mods.items():
            if engine in behavior_weights:
                behavior_weights[engine] *= modifier
        
        # Normalize behavior weights
        behavior_total = sum(behavior_weights.values())
        behavior_weights = {k: v / behavior_total for k, v in behavior_weights.items()}
        
        return {
            "mode": mode.value,
            "species": species,
            "territory": territory,
            "season": season,
            "suite_weights": {
                "geo_suite": round(base["geo_suite"], 4),
                "behavior_suite": round(base["behavior_suite"], 4)
            },
            "geo_engine_weights": {k: round(v, 4) for k, v in geo_weights.items()},
            "behavior_engine_weights": {k: round(v, 4) for k, v in behavior_weights.items()},
            "computed_at": datetime.now(timezone.utc).isoformat()
        }
    
    def set_custom_weights(self, key: str, weights: Dict):
        """Stocke des poids personnalisés."""
        self._custom_weights[key] = weights
        logger.info(f"Custom weights set for key: {key}")
    
    def get_calibration_placeholder(self) -> Dict:
        """
        P3-Ready: Placeholder pour l'auto-calibration ML.
        
        Cette méthode sera implémentée en P3 pour ajuster
        automatiquement les poids basés sur les données.
        """
        return {
            "status": "placeholder",
            "phase": "P3",
            "description": "Auto-calibration ML sera implémentée en Phase P3",
            "hooks": {
                "feedback_collection": True,
                "weight_adjustment": False,
                "ml_training": False
            }
        }


# =============================================================================
# FUSION READY OUTPUT
# =============================================================================

@dataclass
class FusionReadyOutput:
    """
    Format de sortie normalisé pour les scores fusionnés.
    
    Compatible avec le frontend P1.5 et les composants de visualisation.
    """
    # Identification
    fusion_id: str
    analyzed_at: str
    processing_time_ms: int
    
    # Location
    location: Dict[str, float]
    species: str
    territory: str
    
    # Scores principaux
    global_score: float
    geo_score: float
    behavior_score: float
    
    # Score level
    score_level: str
    
    # Breakdown par moteur
    geo_breakdown: Dict[str, float]
    behavior_breakdown: Dict[str, float]
    
    # Poids utilisés
    weights_used: Dict[str, Any]
    
    # Métriques de fusion
    fusion_quality: str
    fusion_confidence: float
    data_coverage: Dict[str, bool]
    
    # Heatmap data
    heatmap_data: Dict[str, Any]
    
    # Recommendations
    recommendations: List[str]
    
    # P3 Hooks
    adaptive_metrics_placeholder: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def get_frontend_output(self) -> Dict:
        """Format optimisé pour le frontend P1.5."""
        return {
            "fusionId": self.fusion_id,
            "globalScore": self.global_score,
            "scoreLevel": self.score_level,
            "geoScore": self.geo_score,
            "behaviorScore": self.behavior_score,
            "breakdown": {
                "geo": self.geo_breakdown,
                "behavior": self.behavior_breakdown
            },
            "heatmapData": self.heatmap_data,
            "fusionQuality": self.fusion_quality,
            "confidence": self.fusion_confidence,
            "recommendations": self.recommendations[:5],
            "weightsUsed": self.weights_used["suite_weights"]
        }


# =============================================================================
# BEHAVIOR FUSION ENGINE
# =============================================================================

class BehaviorFusionEngine:
    """
    Moteur principal de fusion Behavior + Géo-Suite.
    
    Responsabilités:
    - Collecter les outputs des deux suites
    - Normaliser et pondérer les scores
    - Générer des heatmaps combinées
    - Produire des recommandations fusionnées
    
    P3-Ready: Hooks pour auto-calibration.
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.name = "BehaviorFusionEngine"
        self.weight_manager = FusionWeightManager()
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def fuse(
        self,
        lat: float,
        lon: float,
        species: str = "deer",
        territory: str = "quebec",
        radius_km: float = 2.0,
        mode: FusionMode = FusionMode.BALANCED,
        include_heatmap: bool = True,
        geo_data: Optional[Dict] = None,
        behavior_data: Optional[Dict] = None
    ) -> FusionReadyOutput:
        """
        Fusionne les données Geo et Behavior en un score unifié.
        
        Args:
            lat: Latitude
            lon: Longitude
            species: Code de l'espèce
            territory: Territoire
            radius_km: Rayon d'analyse
            mode: Mode de fusion
            include_heatmap: Inclure les données heatmap
            geo_data: Données géospatiales (optionnel, sera fetché sinon)
            behavior_data: Données comportementales (optionnel)
        
        Returns:
            FusionReadyOutput avec le score fusionné
        """
        start_time = datetime.now(timezone.utc)
        fusion_id = f"fus_{uuid.uuid4().hex[:12]}"
        
        # Get weights for this fusion
        weights = self.weight_manager.get_weights(
            species=species,
            territory=territory,
            mode=mode
        )
        
        # Fetch or use provided data
        geo_results = geo_data or await self._fetch_geo_data(lat, lon, species, territory, radius_km)
        behavior_results = behavior_data or await self._fetch_behavior_data(lat, lon, species)
        
        # Calculate suite scores
        geo_score = self._calculate_geo_score(geo_results, weights["geo_engine_weights"])
        behavior_score = self._calculate_behavior_score(behavior_results, weights["behavior_engine_weights"])
        
        # Calculate global fused score
        suite_weights = weights["suite_weights"]
        global_score = (
            geo_score * suite_weights["geo_suite"] +
            behavior_score * suite_weights["behavior_suite"]
        )
        
        # Calculate breakdowns
        geo_breakdown = self._calculate_breakdown(geo_results, "geo")
        behavior_breakdown = self._calculate_breakdown(behavior_results, "behavior")
        
        # Determine score level
        score_level = self._score_to_level(global_score)
        
        # Calculate fusion quality
        fusion_quality, fusion_confidence = self._calculate_fusion_quality(
            geo_results, behavior_results
        )
        
        # Data coverage
        data_coverage = {
            "geo_corridor": "corridor" in geo_results,
            "geo_landcover": "landcover" in geo_results,
            "geo_nutrition": "nutrition" in geo_results,
            "geo_population": "population" in geo_results,
            "geo_pressure": "pressure" in geo_results,
            "behavior_activity": behavior_results.get("activity") is not None,
            "behavior_seasonal": behavior_results.get("seasonal") is not None,
            "behavior_movement": behavior_results.get("movement") is not None
        }
        
        # Generate heatmap data
        heatmap_data = {}
        if include_heatmap:
            heatmap_data = self._generate_heatmap_data(
                lat, lon, radius_km,
                geo_results, behavior_results,
                weights
            )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            geo_results, behavior_results,
            global_score, species
        )
        
        # Calculate processing time
        end_time = datetime.now(timezone.utc)
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return FusionReadyOutput(
            fusion_id=fusion_id,
            analyzed_at=start_time.isoformat(),
            processing_time_ms=processing_time_ms,
            location={"lat": lat, "lon": lon, "radius_km": radius_km},
            species=species,
            territory=territory,
            global_score=round(global_score, 1),
            geo_score=round(geo_score, 1),
            behavior_score=round(behavior_score, 1),
            score_level=score_level,
            geo_breakdown=geo_breakdown,
            behavior_breakdown=behavior_breakdown,
            weights_used=weights,
            fusion_quality=fusion_quality,
            fusion_confidence=round(fusion_confidence, 3),
            data_coverage=data_coverage,
            heatmap_data=heatmap_data,
            recommendations=recommendations,
            adaptive_metrics_placeholder={
                "p3_ready": True,
                "ml_hooks": ["feedback_loop", "weight_adjustment", "score_validation"],
                "calibration_status": "placeholder"
            }
        )
    
    async def _fetch_geo_data(
        self, lat: float, lon: float, species: str, territory: str, radius_km: float
    ) -> Dict[str, Any]:
        """Fetch data from Geo-Suite engines."""
        results = {}
        
        try:
            # Import engines locally
            from geospatial.corridor_engine import corridor_engine
            from geospatial.landcover_engine import landcover_engine
            from geospatial.nutrition_engine import nutrition_engine
            from geospatial.population_density_engine import population_density_engine
            from geospatial.hunting_pressure_module import hunting_pressure_module
            
            # Run all geo engines in parallel
            tasks = [
                corridor_engine.analyze(lat, lon, radius_km, species),
                landcover_engine.analyze(lat, lon, radius_km),
                nutrition_engine.analyze(lat, lon, species, radius_km),
                population_density_engine.analyze(lat, lon, species),
                hunting_pressure_module.analyze(lat, lon)
            ]
            
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            engine_names = ["corridor", "landcover", "nutrition", "population", "pressure"]
            for name, result in zip(engine_names, engine_results):
                if isinstance(result, Exception):
                    logger.warning(f"Geo engine {name} error: {result}")
                    results[name] = None
                else:
                    # Handle both dict and object results
                    if hasattr(result, 'to_dict'):
                        results[name] = result.to_dict()
                    elif isinstance(result, dict):
                        results[name] = result
                    else:
                        results[name] = {"score": 50, "error": "unknown_format"}
        
        except Exception as e:
            logger.error(f"Failed to fetch geo data: {e}")
        
        return results
    
    async def _fetch_behavior_data(self, lat: float, lon: float, species: str) -> Dict[str, Any]:
        """Fetch data from Behavior Suite engines."""
        from behavior.core.behavior_engine import behavior_engine
        from behavior.core.seasonal_attractiveness_engine import seasonal_attractiveness_engine
        from behavior.core.activity_probability_engine import activity_probability_engine
        from behavior.core.movement_engine import movement_engine
        from behavior.models.schemas import (
            BehaviorAnalysisInput,
            SeasonalAttractivenessInput,
            ActivityProbabilityInput,
            MovementAnalysisInput,
            SpeciesCode
        )
        
        results = {}
        
        try:
            species_code = SpeciesCode(species)
        except ValueError:
            species_code = SpeciesCode.DEER
        
        try:
            # Run behavior engines in parallel
            tasks = [
                behavior_engine.analyze(BehaviorAnalysisInput(
                    latitude=lat, longitude=lon, species=species_code
                )),
                seasonal_attractiveness_engine.analyze(SeasonalAttractivenessInput(
                    latitude=lat, longitude=lon, species=species_code
                )),
                activity_probability_engine.analyze(ActivityProbabilityInput(
                    latitude=lat, longitude=lon, species=species_code
                )),
                movement_engine.analyze(MovementAnalysisInput(
                    latitude=lat, longitude=lon, species=species_code
                ))
            ]
            
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            engine_names = ["behavior", "seasonal", "activity", "movement"]
            for name, result in zip(engine_names, engine_results):
                if isinstance(result, Exception):
                    logger.warning(f"Behavior engine {name} error: {result}")
                    results[name] = None
                else:
                    if hasattr(result, 'model_dump'):
                        results[name] = result.model_dump()
                    elif hasattr(result, 'dict'):
                        results[name] = result.dict()
                    elif isinstance(result, dict):
                        results[name] = result
                    else:
                        results[name] = {"score": 50}
        
        except Exception as e:
            logger.error(f"Failed to fetch behavior data: {e}")
        
        return results
    
    def _calculate_geo_score(self, geo_data: Dict, weights: Dict[str, float]) -> float:
        """Calculate weighted geo score."""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for engine, weight in weights.items():
            data = geo_data.get(engine)
            if data is None:
                continue
            
            # Extract score from various formats
            score = self._extract_score(data)
            
            if score is not None:
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        return 50.0
    
    def _calculate_behavior_score(self, behavior_data: Dict, weights: Dict[str, float]) -> float:
        """Calculate weighted behavior score."""
        total_weight = 0.0
        weighted_sum = 0.0
        
        score_keys = {
            "behavior": ["hunting_opportunity_score", "overall_activity_score"],
            "seasonal": ["overall_attractiveness"],
            "activity": ["activity_probability"],
            "movement": ["primary_corridor_score"],
            "rut": ["phase_intensity"],
            "species_model": ["overall_score", "hunting_index"]
        }
        
        for engine, weight in weights.items():
            data = behavior_data.get(engine)
            if data is None:
                continue
            
            # Find score in various keys
            score = None
            keys_to_try = score_keys.get(engine, [])
            
            for key in keys_to_try:
                if key in data:
                    value = data[key]
                    # Handle probability (0-1) vs score (0-100)
                    if key == "activity_probability":
                        score = value * 100 if value <= 1 else value
                    elif key == "phase_intensity":
                        score = value * 100 if value <= 1 else value
                    else:
                        score = value
                    break
            
            if score is not None:
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        return 50.0
    
    def _extract_score(self, data: Any) -> Optional[float]:
        """Extract score from various data formats."""
        if data is None:
            return None
        
        # Handle direct numeric values
        if isinstance(data, (int, float)):
            return float(data)
        
        # Handle non-dict types
        if not isinstance(data, dict):
            return None
        
        # Try common score keys
        for key in ["score", "value", "overall_score", "hunting_score"]:
            if key in data:
                score = data[key]
                if isinstance(score, (int, float)):
                    return float(score)
                if isinstance(score, dict):
                    return float(score.get("value", 50.0))
        
        # Check nested score structure
        if "score" in data and isinstance(data["score"], dict):
            return float(data["score"].get("value", 50.0))
        
        return None
    
    def _calculate_breakdown(self, data: Dict, prefix: str) -> Dict[str, float]:
        """Calculate score breakdown by engine."""
        breakdown = {}
        
        for engine, engine_data in data.items():
            if engine_data is None:
                breakdown[f"{prefix}_{engine}"] = 0.0
                continue
            
            score = self._extract_score(engine_data)
            if score is not None:
                breakdown[f"{prefix}_{engine}"] = round(score, 1)
            else:
                # Try to extract from behavior-specific keys
                if "hunting_opportunity_score" in engine_data:
                    breakdown[f"{prefix}_{engine}"] = round(engine_data["hunting_opportunity_score"], 1)
                elif "overall_attractiveness" in engine_data:
                    breakdown[f"{prefix}_{engine}"] = round(engine_data["overall_attractiveness"], 1)
                elif "activity_probability" in engine_data:
                    breakdown[f"{prefix}_{engine}"] = round(engine_data["activity_probability"] * 100, 1)
                else:
                    breakdown[f"{prefix}_{engine}"] = 50.0
        
        return breakdown
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to level string."""
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
        return "poor"
    
    def _calculate_fusion_quality(
        self, geo_data: Dict, behavior_data: Dict
    ) -> tuple:
        """Calculate fusion quality and confidence."""
        # Count available data sources
        geo_count = sum(1 for v in geo_data.values() if v is not None)
        behavior_count = sum(1 for v in behavior_data.values() if v is not None)
        
        total_sources = 5 + 4  # 5 geo + 4 behavior
        available = geo_count + behavior_count
        
        coverage = available / total_sources
        
        # Quality based on coverage
        if coverage >= 0.85:
            quality = FusionQuality.EXCELLENT.value
        elif coverage >= 0.70:
            quality = FusionQuality.GOOD.value
        elif coverage >= 0.55:
            quality = FusionQuality.MODERATE.value
        elif coverage >= 0.40:
            quality = FusionQuality.LOW.value
        else:
            quality = FusionQuality.POOR.value
        
        # Confidence based on coverage and balance
        balance = 1 - abs(geo_count/5 - behavior_count/4) * 0.5
        confidence = coverage * 0.7 + balance * 0.3
        
        return quality, confidence
    
    def _generate_heatmap_data(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        geo_data: Dict,
        behavior_data: Dict,
        weights: Dict
    ) -> Dict[str, Any]:
        """Generate combined heatmap data for visualization."""
        # Generate a grid of points
        grid_size = 5  # 5x5 grid
        step_km = radius_km * 2 / grid_size
        step_deg = step_km / 111  # Approximate km to degrees
        
        points = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                point_lat = center_lat - radius_km/111 + i * step_deg
                point_lon = center_lon - radius_km/111 + j * step_deg
                
                # Calculate intensity based on distance and data
                dist = ((point_lat - center_lat)**2 + (point_lon - center_lon)**2)**0.5 * 111
                distance_factor = max(0, 1 - dist / radius_km)
                
                # Base intensity from scores
                geo_score = self._calculate_geo_score(geo_data, weights["geo_engine_weights"])
                behavior_score = self._calculate_behavior_score(
                    behavior_data, weights["behavior_engine_weights"]
                )
                
                # Combined intensity with distance falloff
                intensity = (
                    geo_score * weights["suite_weights"]["geo_suite"] +
                    behavior_score * weights["suite_weights"]["behavior_suite"]
                ) / 100 * distance_factor
                
                # Add some variation
                import random
                variation = random.uniform(-0.1, 0.1)
                intensity = max(0, min(1, intensity + variation))
                
                points.append({
                    "lat": round(point_lat, 5),
                    "lon": round(point_lon, 5),
                    "intensity": round(intensity, 3),
                    "geo_contribution": round(geo_score / 100 * distance_factor, 3),
                    "behavior_contribution": round(behavior_score / 100 * distance_factor, 3)
                })
        
        return {
            "type": "fusion_heatmap",
            "bounds": {
                "min_lat": center_lat - radius_km/111,
                "max_lat": center_lat + radius_km/111,
                "min_lon": center_lon - radius_km/111,
                "max_lon": center_lon + radius_km/111
            },
            "grid_size": grid_size,
            "points": points,
            "color_scale": {
                "0.0": "#2E3440",
                "0.3": "#5E81AC",
                "0.5": "#A3BE8C",
                "0.7": "#EBCB8B",
                "0.9": "#BF616A"
            },
            "legend": {
                "title": "Score Fusionné",
                "levels": [
                    {"range": "0-20", "label": "Pauvre", "color": "#2E3440"},
                    {"range": "20-40", "label": "Faible", "color": "#5E81AC"},
                    {"range": "40-60", "label": "Modéré", "color": "#A3BE8C"},
                    {"range": "60-80", "label": "Bon", "color": "#EBCB8B"},
                    {"range": "80-100", "label": "Excellent", "color": "#BF616A"}
                ]
            }
        }
    
    def _generate_recommendations(
        self,
        geo_data: Dict,
        behavior_data: Dict,
        global_score: float,
        species: str
    ) -> List[str]:
        """Generate fusion-aware recommendations."""
        recommendations = []
        
        # Score-based recommendations
        if global_score >= 80:
            recommendations.append("🎯 Zone à potentiel exceptionnel - Priorité maximale")
        elif global_score >= 60:
            recommendations.append("✅ Bon potentiel de chasse - Conditions favorables")
        elif global_score >= 40:
            recommendations.append("⚠️ Potentiel modéré - Optimisez le timing")
        else:
            recommendations.append("❌ Conditions défavorables - Envisagez une autre zone")
        
        # Geo-based recommendations
        if geo_data.get("corridor"):
            corridor_score = self._extract_score(geo_data["corridor"]) or 50
            if corridor_score >= 70:
                recommendations.append("🦌 Corridors fauniques actifs - Positionnez-vous aux jonctions")
        
        if geo_data.get("nutrition"):
            nutrition_score = self._extract_score(geo_data["nutrition"]) or 50
            if nutrition_score >= 70:
                recommendations.append("🌿 Haute disponibilité alimentaire - Zones d'affût prometteuses")
        
        if geo_data.get("pressure"):
            pressure_data = geo_data["pressure"]
            if isinstance(pressure_data, dict) and pressure_data.get("score", {}).get("value", 50) >= 60:
                recommendations.append("👥 Pression de chasse élevée - Ajustez votre stratégie")
        
        # Behavior-based recommendations
        if behavior_data.get("activity"):
            activity = behavior_data["activity"]
            if isinstance(activity, dict):
                prob = activity.get("activity_probability", 0.5)
                if prob >= 0.7:
                    recommendations.append("⏰ Haute probabilité d'activité - Moment optimal")
                
                if "optimal_window" in activity:
                    window = activity["optimal_window"]
                    if isinstance(window, dict):
                        recommendations.append(
                            f"🕐 Fenêtre optimale: {window.get('start_hour', 6)}h - {window.get('end_hour', 9)}h"
                        )
        
        if behavior_data.get("seasonal"):
            seasonal = behavior_data["seasonal"]
            if isinstance(seasonal, dict):
                phase = seasonal.get("current_phase", "")
                if "rut" in phase.lower():
                    recommendations.append("🔥 Période de rut - Utilisez les appelants")
        
        # Species-specific
        species_tips = {
            "deer": "Surveillez les écotones (lisières) pour le cerf",
            "moose": "Concentrez-vous près des milieux humides pour l'orignal",
            "bear": "Recherchez les sources de nourriture (baies, glands) pour l'ours",
            "turkey": "Prospectez les clairières à l'aube pour le dindon"
        }
        
        if species in species_tips:
            recommendations.append(f"💡 {species_tips[species]}")
        
        return recommendations[:8]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

behavior_fusion_engine = BehaviorFusionEngine()
fusion_weight_manager = FusionWeightManager()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FusionMode",
    "FusionQuality",
    "FusionWeightManager",
    "FusionReadyOutput",
    "BehaviorFusionEngine",
    "behavior_fusion_engine",
    "fusion_weight_manager"
]


logger.info(f"BIONIC™ BehaviorFusionEngine v1.0.0 loaded (P2)")
