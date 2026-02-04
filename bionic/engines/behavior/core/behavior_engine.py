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
        self.version = "2.0.0"
        self._cache_namespace = "behavior"
        self._model_loaded = False
        logger.info("BIONIC™ Behavior Engine initialized (v%s) - Real-time data enabled", self.version)
    
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
        Charge les données environnementales depuis les sources temps réel.
        
        Utilise:
        - Open-Meteo pour la météo
        - Algorithme astronomique pour la phase lunaire
        - Calcul de photopériode
        """
        env_data = {}
        
        # Fetch real-time data if available
        if WEATHER_FETCHER_AVAILABLE and behavior_weather_fetcher:
            try:
                all_data = await behavior_weather_fetcher.get_all_environmental_data(
                    input_data.latitude, 
                    input_data.longitude,
                    use_cache=True
                )
                
                weather = all_data.get("weather", {})
                lunar = all_data.get("lunar", {})
                photoperiod = all_data.get("photoperiod", {})
                pressure_trend = all_data.get("pressure_trend", {})
                
                env_data = {
                    "temperature_c": input_data.temperature_c or weather.get("temperature_c", 15.0),
                    "precipitation_mm": input_data.precipitation_mm or weather.get("precipitation_mm", 0.0),
                    "wind_speed_kmh": input_data.wind_speed_kmh or weather.get("wind_speed_kmh", 10.0),
                    "cloud_cover_percent": weather.get("cloud_cover_percent", 50),
                    "humidity_percent": weather.get("humidity_percent", 60),
                    "weather_description": weather.get("weather_description", ""),
                    "moon_phase": input_data.moon_phase or lunar.get("phase", 0.5),
                    "moon_illumination": lunar.get("illumination", 0.5),
                    "moon_phase_name": lunar.get("phase_name_fr", ""),
                    "lunar_hunting_impact": lunar.get("hunting_impact", {}),
                    "barometric_pressure_hpa": input_data.barometric_pressure_hpa or weather.get("pressure_hpa", 1013.0),
                    "pressure_trend": pressure_trend.get("trend", "stable"),
                    "pressure_change_6h": pressure_trend.get("change_6h", 0.0),
                    "sunrise": photoperiod.get("sunrise", "06:00"),
                    "sunset": photoperiod.get("sunset", "18:00"),
                    "daylight_hours": photoperiod.get("daylight_hours", 12),
                    "golden_hour_morning": photoperiod.get("golden_hour_morning", "06:30"),
                    "golden_hour_evening": photoperiod.get("golden_hour_evening", "17:30"),
                    "day_of_year": (input_data.analysis_date or datetime.now().date()).timetuple().tm_yday,
                    "hour_of_day": datetime.now().hour,
                    "data_source": "real_time",
                    "weather_source": weather.get("source", "Unknown"),
                    "lunar_source": lunar.get("source", "Unknown")
                }
                
                logger.info(f"Loaded real-time environmental data: temp={env_data['temperature_c']}°C, moon={env_data['moon_phase_name']}, pressure={env_data['barometric_pressure_hpa']}hPa")
                
            except Exception as e:
                logger.warning(f"Error fetching real-time data: {e}, using fallback")
                env_data = self._get_fallback_env_data(input_data)
        else:
            logger.info("Weather fetcher not available, using fallback estimates")
            env_data = self._get_fallback_env_data(input_data)
        
        return env_data
    
    def _get_fallback_env_data(self, input_data: BehaviorAnalysisInput) -> Dict[str, Any]:
        """Données environnementales de secours si le fetcher n'est pas disponible."""
        return {
            "temperature_c": input_data.temperature_c or 15.0,
            "precipitation_mm": input_data.precipitation_mm or 0.0,
            "wind_speed_kmh": input_data.wind_speed_kmh or 10.0,
            "cloud_cover_percent": 50,
            "moon_phase": input_data.moon_phase or self._estimate_moon_phase(),
            "moon_illumination": 0.5,
            "moon_phase_name": "",
            "lunar_hunting_impact": {},
            "barometric_pressure_hpa": input_data.barometric_pressure_hpa or 1013.0,
            "pressure_trend": "stable",
            "pressure_change_6h": 0.0,
            "sunrise": "06:00",
            "sunset": "18:00",
            "daylight_hours": 12,
            "day_of_year": (input_data.analysis_date or datetime.now().date()).timetuple().tm_yday,
            "hour_of_day": datetime.now().hour,
            "data_source": "estimated"
        }
    
    def preprocess(
        self,
        input_data: BehaviorAnalysisInput,
        env_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prépare les features pour le modèle avec données réelles.
        """
        features = {
            "species": input_data.species.value,
            "lat": input_data.latitude,
            "lon": input_data.longitude,
            **env_data,
            # Features dérivées
            "temp_comfort": self._calculate_temp_comfort(
                env_data.get("temperature_c", 15.0), 
                input_data.species
            ),
            "precip_impact": self._calculate_precip_impact(
                env_data.get("precipitation_mm", 0.0),
                input_data.species
            ),
            "wind_impact": self._calculate_wind_impact(
                env_data.get("wind_speed_kmh", 10.0),
                input_data.species
            ),
            "lunar_influence": self._calculate_lunar_influence(
                env_data.get("moon_phase", 0.5),
                input_data.species
            ),
            "pressure_trend_score": self._calculate_pressure_trend(
                env_data.get("barometric_pressure_hpa", 1013.0)
            ),
            # Pass through real-time lunar data
            "lunar_hunting_impact": env_data.get("lunar_hunting_impact", {}),
            "moon_illumination": env_data.get("moon_illumination", 0.5),
            "moon_phase_name": env_data.get("moon_phase_name", ""),
            # Pass through pressure trend
            "pressure_trend": env_data.get("pressure_trend", "stable"),
            "pressure_change_6h": env_data.get("pressure_change_6h", 0.0)
        }
        
        return features
    
    def run_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute le modèle comportemental avec données réelles.
        
        Intègre:
        - Température et confort thermique
        - Phase lunaire et illumination
        - Pression barométrique et tendance
        - Précipitations et vent
        - Photopériode (lever/coucher)
        """
        species = SpeciesCode(features["species"])
        
        # Score de base
        base_activity = 50.0
        
        # ===== TEMPÉRATURE =====
        temp_comfort = features.get("temp_comfort", 0)
        base_activity += temp_comfort * 20
        
        # ===== PHASE LUNAIRE (Données réelles) =====
        lunar_influence = features.get("lunar_influence", 0)
        lunar_impact = features.get("lunar_hunting_impact", {})
        if lunar_impact:
            # Utiliser le score d'impact lunaire réel
            lunar_score = lunar_impact.get("score", 70)
            lunar_bonus = (lunar_score - 70) / 5  # -6 à +6
            base_activity += lunar_bonus
        else:
            base_activity += lunar_influence * 15
        
        # ===== PRESSION BAROMÉTRIQUE (Tendance réelle) =====
        pressure_trend = features.get("pressure_trend", "stable")
        pressure_change = features.get("pressure_change_6h", 0)
        
        if pressure_trend == "rising_fast":
            base_activity += 15  # Excellentes conditions
        elif pressure_trend == "rising":
            base_activity += 8
        elif pressure_trend == "falling_fast":
            base_activity += 5  # Activité frénétique avant tempête
        elif pressure_trend == "falling":
            base_activity -= 5
        else:
            base_activity += features.get("pressure_trend_score", 0) * 10
        
        # ===== PRÉCIPITATIONS =====
        precip_impact = features.get("precip_impact", 0)
        base_activity -= precip_impact * 25
        
        # ===== VENT =====
        wind_impact = features.get("wind_impact", 0)
        base_activity -= wind_impact * 15
        
        # ===== COUVERTURE NUAGEUSE =====
        cloud_cover = features.get("cloud_cover_percent", 50)
        if cloud_cover > 80:
            # Nuageux = peut favoriser mouvement diurne
            base_activity += 5
        elif cloud_cover < 20:
            # Très dégagé = gibier plus prudent en journée
            base_activity -= 3
        
        # ===== HEURE DE LA JOURNÉE =====
        hour = features.get("hour_of_day", 12)
        patterns = self.BASE_ACTIVITY_PATTERNS.get(species, {})
        peak_hours = patterns.get("peak_hours", [6, 7, 17, 18])
        
        if hour in peak_hours:
            base_activity += 15
        elif hour in patterns.get("secondary_hours", [5, 8, 16, 20]):
            base_activity += 8
        elif 10 <= hour <= 14:
            base_activity -= 10  # Milieu de journée
        
        # Normaliser entre 0-100
        activity_score = max(0, min(100, base_activity))
        
        # Déterminer les fenêtres d'activité avec données réelles
        activity_windows = self._calculate_activity_windows_real(
            species, features, activity_score
        )
        
        return {
            "activity_score": activity_score,
            "activity_windows": activity_windows,
            "factors": {
                "temperature": round(features.get("temp_comfort", 0), 2),
                "precipitation": round(features.get("precip_impact", 0), 2),
                "wind": round(features.get("wind_impact", 0), 2),
                "lunar": round(features.get("lunar_influence", 0), 2),
                "lunar_phase": features.get("moon_phase_name", ""),
                "lunar_illumination": round(features.get("moon_illumination", 0.5) * 100, 1),
                "pressure": features.get("barometric_pressure_hpa", 1013),
                "pressure_trend": features.get("pressure_trend", "stable"),
                "cloud_cover": features.get("cloud_cover_percent", 50),
                "hour_factor": "peak" if hour in peak_hours else "secondary" if hour in patterns.get("secondary_hours", []) else "low"
            },
            "real_time_data": {
                "temperature_c": features.get("temperature_c", 15),
                "weather": features.get("weather_description", ""),
                "sunrise": features.get("sunrise", "06:00"),
                "sunset": features.get("sunset", "18:00"),
                "daylight_hours": features.get("daylight_hours", 12),
                "data_source": features.get("data_source", "unknown")
            }
        }
    
    def _calculate_activity_windows_real(
        self,
        species: SpeciesCode,
        features: Dict[str, Any],
        base_score: float
    ) -> List[Dict[str, Any]]:
        """Calcule les fenêtres d'activité avec données photoperiod réelles."""
        windows = []
        
        # Extraire heures de lever/coucher du soleil
        sunrise = features.get("sunrise", "06:00")
        sunset = features.get("sunset", "18:00")
        golden_morning = features.get("golden_hour_morning", "06:30")
        golden_evening = features.get("golden_hour_evening", "17:30")
        
        try:
            sunrise_hour = int(sunrise.split(":")[0]) if isinstance(sunrise, str) else 6
            sunset_hour = int(sunset.split(":")[0]) if isinstance(sunset, str) else 18
        except:
            sunrise_hour = 6
            sunset_hour = 18
        
        # Ajustement lunaire pour activité nocturne
        moon_phase = features.get("moon_phase", 0.5)
        nocturnal_tendency = self.BASE_ACTIVITY_PATTERNS.get(species, {}).get("nocturnal_tendency", 0.3)
        
        # Fenêtre matinale (autour du lever du soleil)
        morning_start = max(sunrise_hour - 1, 4)
        morning_end = min(sunrise_hour + 2, 10)
        morning_prob = min(0.95, (base_score / 100) + 0.2)
        
        windows.append({
            "start": morning_start,
            "end": morning_end,
            "probability": morning_prob,
            "level": "peak" if base_score > 70 else "high" if base_score > 50 else "moderate",
            "notes": f"Fenêtre matinale (lever: {sunrise})"
        })
        
        # Fenêtre crépusculaire (autour du coucher du soleil)
        evening_start = max(sunset_hour - 2, 15)
        evening_end = min(sunset_hour + 1, 21)
        evening_prob = min(0.95, (base_score / 100) + 0.15)
        
        windows.append({
            "start": evening_start,
            "end": evening_end,
            "probability": evening_prob,
            "level": "peak" if base_score > 70 else "high" if base_score > 50 else "moderate",
            "notes": f"Fenêtre crépusculaire (coucher: {sunset})"
        })
        
        # Fenêtre nocturne (si pleine lune et espèce nocturne)
        if 0.4 <= moon_phase <= 0.6 and nocturnal_tendency > 0.3:
            windows.append({
                "start": 22,
                "end": 4,
                "probability": min(0.7, nocturnal_tendency + 0.2),
                "level": "moderate",
                "notes": f"Activité nocturne (pleine lune, illumination élevée)"
            })
        
        return windows
    
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
