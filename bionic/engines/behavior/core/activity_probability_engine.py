"""
BIONIC™ Activity Probability Engine
=====================================
Moteur de calcul de probabilité d'activité animale.

Version: 2.0 - P0-2 (Données Réelles)

Intègre:
- Météo temps réel (Open-Meteo)
- Phase lunaire précise (algorithme astronomique)
- Pression barométrique
- Photopériode réelle
"""

import logging
import uuid
import math
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import sys

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import (
    ActivityProbabilityInput,
    ActivityProbabilityOutput,
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


class ActivityProbabilityEngine:
    """
    Moteur de probabilité d'activité BIONIC™.
    
    Calcule la probabilité d'activité animale pour:
    - Une heure spécifique
    - Les prochaines 24 heures
    - Identification de la fenêtre optimale
    
    Facteurs pris en compte:
    - Rythme circadien de l'espèce
    - Conditions météorologiques
    - Phase lunaire et illumination
    - Saison et photopériode
    - Pression barométrique
    """
    
    # Profils circadiens par espèce (probabilité par heure, 0-1)
    CIRCADIAN_PROFILES = {
        SpeciesCode.DEER: {
            0: 0.15, 1: 0.10, 2: 0.08, 3: 0.08, 4: 0.12, 5: 0.35,
            6: 0.75, 7: 0.85, 8: 0.55, 9: 0.30, 10: 0.15, 11: 0.10,
            12: 0.08, 13: 0.08, 14: 0.12, 15: 0.25, 16: 0.50, 17: 0.80,
            18: 0.90, 19: 0.70, 20: 0.40, 21: 0.25, 22: 0.18, 23: 0.15
        },
        SpeciesCode.MOOSE: {
            0: 0.20, 1: 0.15, 2: 0.12, 3: 0.12, 4: 0.18, 5: 0.40,
            6: 0.70, 7: 0.80, 8: 0.60, 9: 0.35, 10: 0.20, 11: 0.15,
            12: 0.12, 13: 0.12, 14: 0.15, 15: 0.25, 16: 0.45, 17: 0.70,
            18: 0.85, 19: 0.75, 20: 0.50, 21: 0.35, 22: 0.25, 23: 0.22
        },
        SpeciesCode.BEAR: {
            0: 0.10, 1: 0.08, 2: 0.05, 3: 0.05, 4: 0.08, 5: 0.20,
            6: 0.50, 7: 0.70, 8: 0.75, 9: 0.60, 10: 0.40, 11: 0.30,
            12: 0.25, 13: 0.25, 14: 0.30, 15: 0.40, 16: 0.55, 17: 0.70,
            18: 0.75, 19: 0.60, 20: 0.35, 21: 0.20, 22: 0.15, 23: 0.12
        },
        SpeciesCode.TURKEY: {
            0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.05, 5: 0.25,
            6: 0.70, 7: 0.90, 8: 0.85, 9: 0.60, 10: 0.40, 11: 0.30,
            12: 0.25, 13: 0.25, 14: 0.30, 15: 0.45, 16: 0.65, 17: 0.80,
            18: 0.50, 19: 0.15, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0
        }
    }
    
    def __init__(self):
        self.version = "2.0.0"
        logger.info("BIONIC™ Activity Probability Engine initialized (v%s) - Real-time data enabled", self.version)
    
    async def analyze(
        self,
        input_data: ActivityProbabilityInput,
        use_cache: bool = True
    ) -> ActivityProbabilityOutput:
        """
        Calcule la probabilité d'activité.
        """
        analysis_id = f"act_{uuid.uuid4().hex[:12]}"
        target_dt = input_data.target_datetime or datetime.now(timezone.utc)
        
        # Charger et préparer les données
        factors = await self._prepare_factors(input_data)
        
        # Calculer les probabilités horaires
        hourly_probs = self._calculate_hourly_probabilities(
            input_data.species, factors
        )
        
        # Probabilité pour l'heure cible
        target_hour = target_dt.hour
        target_prob = hourly_probs.get(f"{target_hour:02d}:00", 0.5)
        
        # Déterminer le niveau d'activité
        activity_level = self._prob_to_level(target_prob)
        
        # Trouver la fenêtre optimale
        optimal_window = self._find_optimal_window(hourly_probs)
        
        # Générer recommandations
        recommendations = self._generate_recommendations(
            input_data.species, target_prob, factors
        )
        
        return ActivityProbabilityOutput(
            analysis_id=analysis_id,
            species=input_data.species,
            location={"lat": input_data.latitude, "lon": input_data.longitude},
            target_datetime=target_dt,
            analyzed_at=datetime.now(timezone.utc),
            activity_probability=round(target_prob, 3),
            activity_level=activity_level,
            hourly_probabilities=hourly_probs,
            factors=factors,
            optimal_window=optimal_window,
            confidence=0.75,
            recommendations=recommendations,
            from_cache=False
        )
    
    async def _prepare_factors(
        self, 
        input_data: ActivityProbabilityInput
    ) -> Dict[str, Dict[str, Any]]:
        """Prépare les facteurs d'influence avec données temps réel."""
        
        # Fetch real-time data if available
        real_time_weather = None
        real_time_lunar = None
        
        if WEATHER_FETCHER_AVAILABLE and behavior_weather_fetcher:
            try:
                all_data = await behavior_weather_fetcher.get_all_environmental_data(
                    input_data.latitude,
                    input_data.longitude,
                    use_cache=True
                )
                real_time_weather = all_data.get("weather", {})
                real_time_lunar = all_data.get("lunar", {})
                real_time_pressure = all_data.get("pressure_trend", {})
                
                logger.info(f"Fetched real-time data for activity probability: temp={real_time_weather.get('temperature_c')}°C")
            except Exception as e:
                logger.warning(f"Error fetching real-time data: {e}")
        
        # Facteur météo (utilise données réelles si disponibles)
        weather_factor = self._calculate_weather_factor(
            input_data.temperature_c or (real_time_weather.get("temperature_c") if real_time_weather else None),
            input_data.cloud_cover_percent or (real_time_weather.get("cloud_cover_percent") if real_time_weather else None),
            input_data.precipitation_mm or (real_time_weather.get("precipitation_mm") if real_time_weather else None),
            input_data.wind_speed_kmh or (real_time_weather.get("wind_speed_kmh") if real_time_weather else None),
            weather_data=real_time_weather
        )
        
        # Facteur lunaire (utilise données réelles si disponibles)
        lunar_factor = self._calculate_lunar_factor_real(
            input_data.moon_phase,
            input_data.moon_illumination,
            real_time_lunar
        )
        
        # Facteur saisonnier
        seasonal_factor = self._calculate_seasonal_factor(
            input_data.target_datetime or datetime.now()
        )
        
        # Facteur pression (nouveau)
        pressure_factor = self._calculate_pressure_factor(
            real_time_pressure if 'real_time_pressure' in dir() else None,
            real_time_weather
        )
        
        return {
            "weather": weather_factor,
            "lunar": lunar_factor,
            "seasonal": seasonal_factor,
            "pressure": pressure_factor if 'pressure_factor' in dir() else {"modifier": 1.0, "description": "Non disponible"},
            "data_source": "real_time" if real_time_weather else "estimated"
        }
    
    def _calculate_pressure_factor(
        self,
        pressure_trend_data: Optional[Dict],
        weather_data: Optional[Dict]
    ) -> Dict[str, Any]:
        """Calcule l'impact de la pression barométrique."""
        if pressure_trend_data:
            trend = pressure_trend_data.get("trend", "stable")
            change = pressure_trend_data.get("change_6h", 0)
            
            if trend == "rising_fast":
                modifier = 1.20
                description = "Pression en forte hausse - Conditions excellentes"
            elif trend == "rising":
                modifier = 1.10
                description = "Pression en hausse - Bonnes conditions"
            elif trend == "falling_fast":
                modifier = 1.05
                description = "Chute de pression - Activité frénétique possible"
            elif trend == "falling":
                modifier = 0.90
                description = "Pression en baisse - Tempête approche"
            else:
                modifier = 1.0
                description = "Pression stable"
            
            return {
                "modifier": modifier,
                "trend": trend,
                "change_6h": change,
                "description": description
            }
        elif weather_data:
            pressure = weather_data.get("pressure_hpa", 1013)
            if pressure > 1020:
                modifier = 1.10
            elif pressure < 1005:
                modifier = 0.90
            else:
                modifier = 1.0
            
            return {
                "modifier": modifier,
                "current_hpa": pressure,
                "description": "Basé sur pression actuelle"
            }
        
        return {"modifier": 1.0, "description": "Non disponible"}
    
    def _calculate_lunar_factor_real(
        self,
        moon_phase_input: Optional[float],
        moon_illumination_input: Optional[float],
        lunar_data: Optional[Dict]
    ) -> Dict[str, Any]:
        """Calcule l'impact lunaire avec données temps réel."""
        if lunar_data:
            phase = lunar_data.get("phase", 0.5)
            illumination = lunar_data.get("illumination", 0.5)
            phase_name = lunar_data.get("phase_name_fr", "")
            hunting_impact = lunar_data.get("hunting_impact", {})
            
            # Utiliser le score d'impact calculé par l'algorithme astronomique
            base_modifier = 1.0
            if hunting_impact:
                impact_score = hunting_impact.get("score", 70)
                base_modifier = 0.85 + (impact_score / 100) * 0.30
            else:
                # Calcul alternatif
                if 0.4 <= phase <= 0.6:
                    base_modifier = 1.15
                elif phase < 0.1 or phase > 0.9:
                    base_modifier = 0.95
            
            return {
                "modifier": round(base_modifier, 3),
                "phase": round(phase, 4),
                "illumination": round(illumination, 4),
                "phase_name": phase_name,
                "is_full_moon": lunar_data.get("is_full_moon", False),
                "is_new_moon": lunar_data.get("is_new_moon", False),
                "hunting_impact": hunting_impact.get("impact", "neutral"),
                "description": hunting_impact.get("description", "") or f"Phase: {phase_name}",
                "data_source": "real_time_algorithm"
            }
        
        # Fallback to input or estimation
        return self._calculate_lunar_factor(moon_phase_input, moon_illumination_input)
    
    def _calculate_weather_factor(
        self,
        temp: Optional[float],
        clouds: Optional[float],
        precip: Optional[float],
        wind: Optional[float],
        weather_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Calcule l'impact météo avec données enrichies."""
        temp = temp or 15.0
        clouds = clouds or 50.0
        precip = precip or 0.0
        wind = wind or 10.0
        
        # Score température (optimal 5-15°C pour la plupart)
        if 5 <= temp <= 15:
            temp_score = 1.0
        elif 0 <= temp < 5 or 15 < temp <= 25:
            temp_score = 0.8
        else:
            temp_score = 0.5
        
        # Score précipitations
        if precip == 0:
            precip_score = 1.0
        elif precip < 2:
            precip_score = 0.85
        elif precip < 5:
            precip_score = 0.6
        else:
            precip_score = 0.3
        
        # Score vent
        if wind < 15:
            wind_score = 1.0
        elif wind < 25:
            wind_score = 0.7
        elif wind < 35:
            wind_score = 0.4
        else:
            wind_score = 0.2
        
        overall = (temp_score * 0.4 + precip_score * 0.35 + wind_score * 0.25)
        
        result = {
            "modifier": round(overall, 3),
            "temperature_score": temp_score,
            "precipitation_score": precip_score,
            "wind_score": wind_score,
            "description": self._describe_weather_impact(overall)
        }
        
        # Add real-time details if available
        if weather_data:
            result["current_conditions"] = {
                "temperature_c": weather_data.get("temperature_c"),
                "weather_description": weather_data.get("weather_description"),
                "humidity_percent": weather_data.get("humidity_percent"),
                "wind_gusts_kmh": weather_data.get("wind_gusts_kmh")
            }
            result["data_source"] = weather_data.get("source", "Unknown")
        
        return result
    
    def _calculate_lunar_factor(
        self,
        moon_phase: Optional[float],
        moon_illumination: Optional[float]
    ) -> Dict[str, Any]:
        """Calcule l'impact lunaire."""
        # Estimer si non fourni
        if moon_phase is None:
            reference = datetime(2024, 1, 11)
            days_since = (datetime.now() - reference).days
            moon_phase = (days_since % 29.53) / 29.53
        
        if moon_illumination is None:
            # Approximation basée sur la phase
            moon_illumination = abs(math.sin(moon_phase * math.pi))
        
        # Pleine lune augmente l'activité nocturne
        # Nouvelle lune favorise l'activité crépusculaire
        if 0.4 <= moon_phase <= 0.6:  # Pleine lune
            modifier = 1.15
            description = "Pleine lune - activité nocturne accrue"
        elif moon_phase < 0.1 or moon_phase > 0.9:  # Nouvelle lune
            modifier = 0.95
            description = "Nouvelle lune - activité crépusculaire favorisée"
        else:
            modifier = 1.0
            description = "Phase lunaire intermédiaire"
        
        return {
            "modifier": modifier,
            "phase": round(moon_phase, 3),
            "illumination": round(moon_illumination, 3),
            "phase_name": self._get_moon_phase_name(moon_phase),
            "description": description
        }
    
    def _calculate_seasonal_factor(
        self,
        target_datetime: datetime
    ) -> Dict[str, Any]:
        """Calcule le facteur saisonnier."""
        day_of_year = target_datetime.timetuple().tm_yday
        
        # Jours les plus courts = moins d'activité diurne
        # Équinoxes et rut = pics d'activité
        
        if 270 <= day_of_year <= 330:  # Octobre-Novembre (rut)
            modifier = 1.25
            description = "Période de rut - activité maximale"
        elif 90 <= day_of_year <= 150:  # Avril-Mai
            modifier = 1.10
            description = "Printemps - reprise d'activité"
        elif 330 < day_of_year or day_of_year < 60:  # Hiver
            modifier = 0.80
            description = "Hiver - activité réduite"
        else:
            modifier = 1.0
            description = "Saison intermédiaire"
        
        return {
            "modifier": modifier,
            "day_of_year": day_of_year,
            "description": description
        }
    
    def _calculate_hourly_probabilities(
        self,
        species: SpeciesCode,
        factors: Dict[str, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calcule les probabilités horaires avec facteurs réels."""
        base_profile = self.CIRCADIAN_PROFILES.get(
            species, 
            self.CIRCADIAN_PROFILES[SpeciesCode.DEER]
        )
        
        # Appliquer les modificateurs
        weather_mod = factors.get("weather", {}).get("modifier", 1.0)
        lunar_mod = factors.get("lunar", {}).get("modifier", 1.0)
        seasonal_mod = factors.get("seasonal", {}).get("modifier", 1.0)
        pressure_mod = factors.get("pressure", {}).get("modifier", 1.0)
        
        overall_mod = weather_mod * lunar_mod * seasonal_mod * pressure_mod
        
        hourly = {}
        for hour, base_prob in base_profile.items():
            modified_prob = min(1.0, base_prob * overall_mod)
            hourly[f"{hour:02d}:00"] = round(modified_prob, 3)
        
        return hourly
    
    def _find_optimal_window(
        self, 
        hourly_probs: Dict[str, float]
    ) -> TimeWindow:
        """Trouve la fenêtre d'activité optimale."""
        # Trouver l'heure avec la plus haute probabilité
        max_hour = max(hourly_probs, key=hourly_probs.get)
        max_prob = hourly_probs[max_hour]
        
        hour_int = int(max_hour.split(":")[0])
        
        # Étendre la fenêtre aux heures adjacentes avec prob > 50% de max
        threshold = max_prob * 0.5
        
        start_hour = hour_int
        end_hour = hour_int
        
        for h in range(hour_int - 1, -1, -1):
            key = f"{h:02d}:00"
            if hourly_probs.get(key, 0) >= threshold:
                start_hour = h
            else:
                break
        
        for h in range(hour_int + 1, 24):
            key = f"{h:02d}:00"
            if hourly_probs.get(key, 0) >= threshold:
                end_hour = h
            else:
                break
        
        return TimeWindow(
            start_hour=start_hour,
            end_hour=end_hour,
            probability=max_prob,
            activity_level=self._prob_to_level(max_prob),
            notes=f"Fenêtre optimale: {start_hour}h-{end_hour}h"
        )
    
    def _prob_to_level(self, prob: float) -> ActivityLevel:
        """Convertit une probabilité en niveau d'activité."""
        if prob >= 0.8:
            return ActivityLevel.PEAK
        elif prob >= 0.65:
            return ActivityLevel.VERY_HIGH
        elif prob >= 0.5:
            return ActivityLevel.HIGH
        elif prob >= 0.35:
            return ActivityLevel.MODERATE
        elif prob >= 0.2:
            return ActivityLevel.LOW
        else:
            return ActivityLevel.VERY_LOW
    
    def _describe_weather_impact(self, score: float) -> str:
        """Décrit l'impact météo."""
        if score >= 0.9:
            return "Conditions météo excellentes"
        elif score >= 0.7:
            return "Bonnes conditions météo"
        elif score >= 0.5:
            return "Conditions météo acceptables"
        else:
            return "Conditions météo défavorables"
    
    def _get_moon_phase_name(self, phase: float) -> str:
        """Obtient le nom de la phase lunaire."""
        if phase < 0.125 or phase >= 0.875:
            return "Nouvelle lune"
        elif phase < 0.25:
            return "Premier croissant"
        elif phase < 0.375:
            return "Premier quartier"
        elif phase < 0.5:
            return "Gibbeuse croissante"
        elif phase < 0.625:
            return "Pleine lune"
        elif phase < 0.75:
            return "Gibbeuse décroissante"
        elif phase < 0.875:
            return "Dernier quartier"
        return "Dernier croissant"
    
    def _generate_recommendations(
        self,
        species: SpeciesCode,
        target_prob: float,
        factors: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Génère des recommandations enrichies avec données réelles."""
        recs = []
        
        if target_prob >= 0.7:
            recs.append("🎯 Excellente probabilité d'activité - moment idéal pour chasser")
        elif target_prob >= 0.5:
            recs.append("✅ Bonne probabilité d'activité")
        else:
            recs.append("⚠️ Probabilité d'activité faible - patience requise")
        
        # Recommandations météo enrichies
        weather = factors.get("weather", {})
        if weather.get("wind_score", 1) < 0.5:
            recs.append("💨 Vent fort - Le gibier sera nerveux, minimisez vos mouvements")
        
        current = weather.get("current_conditions", {})
        if current:
            weather_desc = current.get("weather_description", "")
            if weather_desc:
                recs.append(f"☁️ Conditions: {weather_desc}")
        
        # Recommandations lunaires enrichies
        lunar = factors.get("lunar", {})
        phase_name = lunar.get("phase_name", "")
        if lunar.get("is_full_moon"):
            recs.append(f"🌕 {phase_name} - Arrivez très tôt, le gibier sera actif avant l'aube")
        elif lunar.get("is_new_moon"):
            recs.append(f"🌑 {phase_name} - Nuits sombres, concentrez-vous sur aube/crépuscule")
        elif phase_name:
            recs.append(f"🌙 {phase_name} ({round(lunar.get('illumination', 0.5) * 100)}% illumination)")
        
        # Recommandations pression
        pressure = factors.get("pressure", {})
        trend = pressure.get("trend", "")
        if trend == "rising_fast":
            recs.append("📈 Pression en forte hausse - Excellentes conditions!")
        elif trend == "falling_fast":
            recs.append("📉 Chute de pression - Activité frénétique possible avant tempête")
        
        # Source des données
        data_source = factors.get("data_source", "estimated")
        if data_source == "real_time":
            recs.append("📡 Données temps réel (Open-Meteo + algorithme astronomique)")
        
        return recs[:6]


# Singleton instance
activity_probability_engine = ActivityProbabilityEngine()
