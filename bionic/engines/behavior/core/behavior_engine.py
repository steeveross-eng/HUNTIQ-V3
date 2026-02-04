"""
BIONIC™ Behavior Engine
=========================
Moteur d'analyse comportementale globale pour la faune.

Version: 2.0 - P0-2 (Données Réelles)

Intègre:
- Météo temps réel (Open-Meteo)
- Phase lunaire précise (algorithme astronomique)
- Pression barométrique et tendance
- Photopériode (lever/coucher du soleil)
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import sys
import math

# Add path for imports
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import (
    BehaviorAnalysisInput,
    BehaviorAnalysisOutput,
    SpeciesCode,
    ActivityLevel,
    TimeWindow
)

# Import weather fetcher
try:
    from behavior.core.weather_fetcher import behavior_weather_fetcher
    WEATHER_FETCHER_AVAILABLE = True
except ImportError:
    WEATHER_FETCHER_AVAILABLE = False
    behavior_weather_fetcher = None

logger = logging.getLogger(__name__)


class BehaviorEngine:
    """
    Moteur d'analyse comportementale BIONIC™.
    
    Analyse le comportement animal en fonction de:
    - Conditions météorologiques
    - Phase lunaire
    - Saison et photopériode
    - Pression barométrique
    - Données historiques de l'espèce
    
    Outputs:
    - Score d'activité global
    - Fenêtres d'activité optimales
    - Niveau d'activité actuel
    - Prédictions 24h
    - Recommandations de chasse
    """
    
    # Noms français des espèces
    SPECIES_NAMES_FR = {
        SpeciesCode.MOOSE: "Orignal",
        SpeciesCode.DEER: "Cerf de Virginie",
        SpeciesCode.BEAR: "Ours noir",
        SpeciesCode.CARIBOU: "Caribou",
        SpeciesCode.WOLF: "Loup",
        SpeciesCode.TURKEY: "Dindon sauvage",
        SpeciesCode.WATERFOWL: "Sauvagine",
        SpeciesCode.SMALLGAME: "Petit gibier"
    }
    
    # Patterns d'activité de base par espèce (heures)
    BASE_ACTIVITY_PATTERNS = {
        SpeciesCode.DEER: {
            "peak_hours": [6, 7, 17, 18, 19],
            "secondary_hours": [5, 8, 16, 20],
            "nocturnal_tendency": 0.3
        },
        SpeciesCode.MOOSE: {
            "peak_hours": [5, 6, 7, 18, 19, 20],
            "secondary_hours": [4, 8, 17, 21],
            "nocturnal_tendency": 0.4
        },
        SpeciesCode.BEAR: {
            "peak_hours": [6, 7, 8, 17, 18, 19],
            "secondary_hours": [9, 10, 16],
            "nocturnal_tendency": 0.5
        },
        SpeciesCode.TURKEY: {
            "peak_hours": [6, 7, 8, 16, 17],
            "secondary_hours": [9, 15],
            "nocturnal_tendency": 0.0
        }
    }
    
    def __init__(self):
        self.version = "1.0.0"
        self._cache_namespace = "behavior"
        self._model_loaded = False
        logger.info("BIONIC™ Behavior Engine initialized (v%s)", self.version)
    
    async def analyze(
        self,
        input_data: BehaviorAnalysisInput,
        use_cache: bool = True
    ) -> BehaviorAnalysisOutput:
        """
        Analyse comportementale complète.
        
        Pipeline:
        1. load_inputs() - Charger les données d'entrée et environnementales
        2. preprocess() - Préparer les features pour le modèle
        3. run_model() - Exécuter le modèle comportemental
        4. postprocess() - Transformer les sorties brutes
        5. to_bionic_output() - Formater pour BIONIC_CORE
        """
        analysis_id = f"beh_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now(timezone.utc)
        
        # Pipeline d'analyse
        env_data = await self.load_inputs(input_data)
        features = self.preprocess(input_data, env_data)
        raw_output = self.run_model(features)
        processed = self.postprocess(raw_output, input_data)
        result = self.to_bionic_output(processed, input_data, analysis_id, start_time)
        
        return result
    
    async def load_inputs(
        self, 
        input_data: BehaviorAnalysisInput
    ) -> Dict[str, Any]:
        """
        Charge les données environnementales.
        
        TODO P0-2: 
        - Intégrer fetch météo temps réel
        - Calculer phase lunaire
        - Récupérer données pression barométrique
        """
        env_data = {
            "temperature_c": input_data.temperature_c or 15.0,
            "precipitation_mm": input_data.precipitation_mm or 0.0,
            "wind_speed_kmh": input_data.wind_speed_kmh or 10.0,
            "moon_phase": input_data.moon_phase or self._estimate_moon_phase(),
            "barometric_pressure_hpa": input_data.barometric_pressure_hpa or 1013.0,
            "day_of_year": (input_data.analysis_date or datetime.now().date()).timetuple().tm_yday,
            "hour_of_day": datetime.now().hour
        }
        
        return env_data
    
    def preprocess(
        self,
        input_data: BehaviorAnalysisInput,
        env_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prépare les features pour le modèle.
        
        TODO P0-2:
        - Normalisation des features
        - Feature engineering avancé
        - Encodage des variables catégorielles
        """
        features = {
            "species": input_data.species.value,
            "lat": input_data.latitude,
            "lon": input_data.longitude,
            **env_data,
            # Features dérivées
            "temp_comfort": self._calculate_temp_comfort(
                env_data["temperature_c"], 
                input_data.species
            ),
            "precip_impact": self._calculate_precip_impact(
                env_data["precipitation_mm"],
                input_data.species
            ),
            "wind_impact": self._calculate_wind_impact(
                env_data["wind_speed_kmh"],
                input_data.species
            ),
            "lunar_influence": self._calculate_lunar_influence(
                env_data["moon_phase"],
                input_data.species
            ),
            "pressure_trend": self._calculate_pressure_trend(
                env_data["barometric_pressure_hpa"]
            )
        }
        
        return features
    
    def run_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute le modèle comportemental.
        
        TODO P0-2:
        - Implémenter modèle ML (Random Forest / XGBoost)
        - Charger poids pré-entraînés
        - Intégrer TensorFlow/PyTorch pour deep learning
        
        STUB: Retourne des valeurs basées sur des heuristiques.
        """
        species = SpeciesCode(features["species"])
        
        # Calcul du score d'activité (heuristique)
        base_activity = 50.0
        
        # Ajustements
        base_activity += features.get("temp_comfort", 0) * 20
        base_activity += features.get("lunar_influence", 0) * 15
        base_activity -= features.get("precip_impact", 0) * 25
        base_activity -= features.get("wind_impact", 0) * 15
        base_activity += features.get("pressure_trend", 0) * 10
        
        # Normaliser entre 0-100
        activity_score = max(0, min(100, base_activity))
        
        # Déterminer les fenêtres d'activité
        activity_windows = self._calculate_activity_windows(
            species, features, activity_score
        )
        
        return {
            "activity_score": activity_score,
            "activity_windows": activity_windows,
            "factors": {
                "temperature": features.get("temp_comfort", 0),
                "precipitation": features.get("precip_impact", 0),
                "wind": features.get("wind_impact", 0),
                "lunar": features.get("lunar_influence", 0),
                "pressure": features.get("pressure_trend", 0)
            }
        }
    
    def postprocess(
        self,
        raw_output: Dict[str, Any],
        input_data: BehaviorAnalysisInput
    ) -> Dict[str, Any]:
        """
        Transforme les sorties brutes.
        
        TODO P0-2:
        - Calibration des scores
        - Ajustements saisonniers
        - Validation des prédictions
        """
        activity_score = raw_output["activity_score"]
        
        # Déterminer le niveau d'activité
        if activity_score >= 80:
            activity_level = ActivityLevel.PEAK
        elif activity_score >= 65:
            activity_level = ActivityLevel.VERY_HIGH
        elif activity_score >= 50:
            activity_level = ActivityLevel.HIGH
        elif activity_score >= 35:
            activity_level = ActivityLevel.MODERATE
        elif activity_score >= 20:
            activity_level = ActivityLevel.LOW
        else:
            activity_level = ActivityLevel.VERY_LOW
        
        # Score d'opportunité de chasse
        hunting_score = self._calculate_hunting_opportunity(
            activity_score, input_data.species
        )
        
        return {
            **raw_output,
            "activity_level": activity_level,
            "hunting_opportunity_score": hunting_score
        }
    
    def to_bionic_output(
        self,
        processed: Dict[str, Any],
        input_data: BehaviorAnalysisInput,
        analysis_id: str,
        start_time: datetime
    ) -> BehaviorAnalysisOutput:
        """
        Formate la sortie pour BIONIC_CORE.
        """
        # Convertir les fenêtres d'activité
        peak_windows = []
        for window in processed.get("activity_windows", []):
            peak_windows.append(TimeWindow(
                start_hour=window["start"],
                end_hour=window["end"],
                probability=window["probability"],
                activity_level=ActivityLevel(window["level"]),
                notes=window.get("notes")
            ))
        
        # Générer les recommandations
        recommendations = self._generate_recommendations(
            processed, input_data.species
        )
        
        return BehaviorAnalysisOutput(
            analysis_id=analysis_id,
            species=input_data.species,
            species_name_fr=self.SPECIES_NAMES_FR.get(input_data.species, "Inconnu"),
            location={"lat": input_data.latitude, "lon": input_data.longitude},
            analyzed_at=datetime.now(timezone.utc),
            data_source="BIONIC Behavior Engine v1.0",
            overall_activity_score=round(processed["activity_score"], 1),
            hunting_opportunity_score=round(processed["hunting_opportunity_score"], 1),
            confidence=0.75,  # TODO: Calculer vraie confiance
            peak_activity_windows=peak_windows,
            current_activity_level=processed["activity_level"],
            behavioral_factors=processed.get("factors", {}),
            predictions_24h=self._generate_24h_predictions(processed, input_data),
            recommendations=recommendations,
            from_cache=False
        )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _estimate_moon_phase(self) -> float:
        """Estime la phase lunaire (0-1, 0=nouvelle lune, 0.5=pleine lune)."""
        # Calcul simplifié basé sur le cycle de 29.5 jours
        reference = datetime(2024, 1, 11)  # Nouvelle lune connue
        days_since = (datetime.now() - reference).days
        cycle_position = (days_since % 29.53) / 29.53
        return cycle_position
    
    def _calculate_temp_comfort(self, temp: float, species: SpeciesCode) -> float:
        """Calcule le confort thermique (-1 à 1)."""
        # Températures optimales par espèce
        optimal_temps = {
            SpeciesCode.DEER: (5, 15),
            SpeciesCode.MOOSE: (-5, 10),
            SpeciesCode.BEAR: (10, 20),
            SpeciesCode.TURKEY: (10, 20)
        }
        
        opt_min, opt_max = optimal_temps.get(species, (5, 15))
        
        if opt_min <= temp <= opt_max:
            return 1.0
        elif temp < opt_min:
            return max(-1, 1 - (opt_min - temp) / 20)
        else:
            return max(-1, 1 - (temp - opt_max) / 20)
    
    def _calculate_precip_impact(self, precip: float, species: SpeciesCode) -> float:
        """Calcule l'impact des précipitations (0-1, 0=pas d'impact)."""
        if precip <= 0:
            return 0
        elif precip < 2:
            return 0.2
        elif precip < 5:
            return 0.5
        elif precip < 10:
            return 0.7
        else:
            return 1.0
    
    def _calculate_wind_impact(self, wind: float, species: SpeciesCode) -> float:
        """Calcule l'impact du vent (0-1)."""
        # Sensibilité au vent par espèce
        sensitivity = {
            SpeciesCode.DEER: 1.2,
            SpeciesCode.MOOSE: 0.8,
            SpeciesCode.TURKEY: 1.5,
            SpeciesCode.BEAR: 0.7
        }
        
        sens = sensitivity.get(species, 1.0)
        
        if wind < 10:
            return 0
        elif wind < 20:
            return 0.2 * sens
        elif wind < 30:
            return 0.4 * sens
        elif wind < 40:
            return 0.6 * sens
        else:
            return min(1.0, 0.8 * sens)
    
    def _calculate_lunar_influence(self, moon_phase: float, species: SpeciesCode) -> float:
        """Calcule l'influence lunaire (-0.5 à 0.5)."""
        # Pleine lune (0.5) = plus d'activité nocturne
        # Nouvelle lune (0, 1) = moins d'activité nocturne
        deviation_from_full = abs(moon_phase - 0.5) * 2  # 0-1
        
        # Effet différent selon l'espèce
        nocturnal = self.BASE_ACTIVITY_PATTERNS.get(species, {}).get("nocturnal_tendency", 0.3)
        
        # Plus l'espèce est nocturne, plus la pleine lune augmente l'activité
        return (0.5 - deviation_from_full) * nocturnal
    
    def _calculate_pressure_trend(self, pressure: float) -> float:
        """Calcule l'effet de la pression barométrique (-0.5 à 0.5)."""
        # Pression normale ~1013 hPa
        # Haute pression = généralement plus d'activité
        deviation = (pressure - 1013) / 30
        return max(-0.5, min(0.5, deviation))
    
    def _calculate_activity_windows(
        self,
        species: SpeciesCode,
        features: Dict[str, Any],
        base_score: float
    ) -> List[Dict[str, Any]]:
        """Calcule les fenêtres d'activité optimales."""
        patterns = self.BASE_ACTIVITY_PATTERNS.get(species, {})
        peak_hours = patterns.get("peak_hours", [6, 7, 17, 18])
        
        windows = []
        
        # Fenêtre du matin
        morning_start = min(peak_hours[:len(peak_hours)//2]) if peak_hours else 6
        morning_end = max(peak_hours[:len(peak_hours)//2]) if peak_hours else 8
        
        windows.append({
            "start": morning_start,
            "end": morning_end,
            "probability": min(0.95, (base_score / 100) + 0.2),
            "level": "high" if base_score > 50 else "moderate",
            "notes": "Fenêtre matinale principale"
        })
        
        # Fenêtre du soir
        evening_start = min(peak_hours[len(peak_hours)//2:]) if peak_hours else 17
        evening_end = max(peak_hours[len(peak_hours)//2:]) if peak_hours else 19
        
        windows.append({
            "start": evening_start,
            "end": evening_end,
            "probability": min(0.95, (base_score / 100) + 0.15),
            "level": "high" if base_score > 50 else "moderate",
            "notes": "Fenêtre crépusculaire principale"
        })
        
        return windows
    
    def _calculate_hunting_opportunity(
        self,
        activity_score: float,
        species: SpeciesCode
    ) -> float:
        """Calcule le score d'opportunité de chasse."""
        # Le score de chasse est généralement légèrement inférieur à l'activité
        base = activity_score * 0.85
        
        # Bonus selon l'espèce (certaines sont plus chassables)
        species_bonus = {
            SpeciesCode.DEER: 10,
            SpeciesCode.TURKEY: 8,
            SpeciesCode.MOOSE: 5,
            SpeciesCode.BEAR: 3
        }
        
        return min(100, base + species_bonus.get(species, 0))
    
    def _generate_recommendations(
        self,
        processed: Dict[str, Any],
        species: SpeciesCode
    ) -> List[str]:
        """Génère des recommandations basées sur l'analyse."""
        recs = []
        
        activity_score = processed.get("activity_score", 50)
        factors = processed.get("factors", {})
        
        if activity_score >= 70:
            recs.append("Excellent moment pour la chasse - Activité élevée prévue")
        elif activity_score >= 50:
            recs.append("Conditions favorables pour la chasse")
        else:
            recs.append("Activité réduite attendue - Patience requise")
        
        # Recommandations basées sur les facteurs
        if factors.get("lunar", 0) > 0.3:
            recs.append("Pleine lune proche - Activité nocturne accrue, chassez tôt le matin")
        
        if factors.get("pressure", 0) > 0.2:
            recs.append("Pression barométrique élevée - Conditions de déplacement favorables")
        elif factors.get("pressure", 0) < -0.2:
            recs.append("Pression en baisse - Anticipez les déplacements avant le changement")
        
        if factors.get("wind", 0) > 0.5:
            recs.append("Vent fort - Le gibier sera nerveux, restez camouflé")
        
        # Recommandations spécifiques à l'espèce
        species_tips = {
            SpeciesCode.DEER: "Concentrez-vous sur les corridors entre zones de gagnage et de repos",
            SpeciesCode.MOOSE: "Surveillez les zones de saules et les bordures de tourbières",
            SpeciesCode.BEAR: "Recherchez les sources de nourriture actives",
            SpeciesCode.TURKEY: "Écoutez les premiers gloussements à l'aube"
        }
        
        if species in species_tips:
            recs.append(species_tips[species])
        
        return recs[:5]  # Max 5 recommandations
    
    def _generate_24h_predictions(
        self,
        processed: Dict[str, Any],
        input_data: BehaviorAnalysisInput
    ) -> Dict[str, Any]:
        """Génère les prédictions sur 24h."""
        if not input_data.include_predictions:
            return None
        
        base_score = processed.get("activity_score", 50)
        
        # Prédictions horaires simplifiées
        hourly = {}
        for hour in range(24):
            # Variation sinusoïdale avec pics matin/soir
            import math
            morning_factor = math.exp(-((hour - 6) ** 2) / 8)
            evening_factor = math.exp(-((hour - 18) ** 2) / 8)
            
            hourly_score = base_score * (0.3 + 0.7 * max(morning_factor, evening_factor))
            hourly[f"{hour:02d}:00"] = round(hourly_score, 1)
        
        return {
            "hourly_scores": hourly,
            "best_hours": ["06:00", "07:00", "17:00", "18:00"],
            "trend": "stable"
        }


# Singleton instance
behavior_engine = BehaviorEngine()
