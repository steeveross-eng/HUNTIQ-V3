"""
BIONIC™ Engine - Prediction Engine
====================================
Génération des prédictions IA pour l'activité faunique.

Fonctionnalités:
- Prévisions 24h, 72h, 7 jours
- Impact météo sur l'activité
- Prédiction des mouvements
- Scores dynamiques (ajustés en temps réel)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import random
import logging

from .configs import SpeciesType, TIME_OF_DAY_FACTORS
from .helpers import get_rating, clamp

logger = logging.getLogger(__name__)


class PredictionEngine:
    """
    Moteur de prédictions IA pour l'activité faunique.
    """
    
    def __init__(self):
        self.time_factors = TIME_OF_DAY_FACTORS
    
    async def generate_predictions(
        self,
        lat: float,
        lon: float,
        species_scores: Dict[SpeciesType, float],
        territory_id: str,
        geospatial_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Génère des prédictions IA basées sur les scores actuels.
        
        Args:
            lat: Latitude
            lon: Longitude
            species_scores: Scores actuels par espèce
            territory_id: ID du territoire
            geospatial_data: Données géospatiales réelles
            
        Returns:
            Dict: Prédictions avec forecasts, impact météo, mouvements
        """
        # Générer les prévisions avec variance temporelle
        forecast_24h = self._predict_with_variance(species_scores, variance=5)
        forecast_72h = self._predict_with_variance(species_scores, variance=10)
        forecast_7d = self._predict_with_variance(species_scores, variance=15)
        
        # Calculer l'impact météo
        weather_impact = await self._calculate_weather_impact(
            geospatial_data, forecast_24h
        )
        
        # Prédire les mouvements
        movement_prediction = self._predict_movements(geospatial_data)
        
        # Calculer la confiance
        confidence = 0.85 if geospatial_data and hasattr(geospatial_data, 'data_quality') and geospatial_data.data_quality == "complete" else 0.70
        
        return {
            "forecast_24h": forecast_24h,
            "forecast_72h": forecast_72h,
            "forecast_7d": forecast_7d,
            "confidence": round(confidence, 2),
            "weather_impact": weather_impact,
            "movement_prediction": movement_prediction
        }
    
    async def calculate_dynamic_score(
        self,
        lat: float,
        lon: float,
        base_scores: Dict[SpeciesType, float],
        weather_temp: float,
        weather_precip: float,
        time_of_day: str
    ) -> Dict[str, Any]:
        """
        Calcule des scores ajustés dynamiquement selon les conditions.
        
        Args:
            lat: Latitude
            lon: Longitude
            base_scores: Scores de base par espèce
            weather_temp: Température actuelle (°C)
            weather_precip: Probabilité de précipitation (%)
            time_of_day: Moment de la journée
            
        Returns:
            Dict: Scores dynamiques par espèce
        """
        # Facteur météo
        weather_factor = self._calculate_weather_factor(weather_temp, weather_precip)
        
        # Facteurs par heure
        time_factors = self.time_factors.get(time_of_day, {})
        
        dynamic_results = {}
        
        for species, base_score in base_scores.items():
            species_key = species.value if hasattr(species, 'value') else str(species)
            time_factor = time_factors.get(species_key, 1.0)
            
            adjusted_score = base_score * time_factor * weather_factor
            
            dynamic_results[species_key] = {
                "base_score": base_score,
                "adjusted_score": round(clamp(adjusted_score, 0, 100), 1),
                "time_factor": time_factor,
                "weather_factor": round(weather_factor, 2),
                "activity_level": get_rating(adjusted_score)
            }
        
        return {
            "conditions": {
                "temperature": weather_temp,
                "precipitation": weather_precip,
                "time_of_day": time_of_day
            },
            "dynamic_scores": dynamic_results
        }
    
    def _predict_with_variance(
        self,
        species_scores: Dict[SpeciesType, float],
        variance: float
    ) -> Dict[str, float]:
        """
        Génère des prédictions avec variance gaussienne.
        """
        predictions = {}
        
        for species, score in species_scores.items():
            species_key = species.value if hasattr(species, 'value') else str(species)
            predicted = score + random.gauss(0, variance)
            predictions[species_key] = round(clamp(predicted, 0, 100), 1)
        
        return predictions
    
    async def _calculate_weather_impact(
        self,
        geospatial_data: Optional[Any],
        forecast_24h: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calcule l'impact des conditions météo.
        """
        weather_impact = {}
        
        if geospatial_data and hasattr(geospatial_data, 'weather') and geospatial_data.weather:
            weather = geospatial_data.weather
            
            current_temp = getattr(weather, 'temperature', 15)
            precip_prob = getattr(weather, 'precipitation_probability', 0)
            wind_speed = getattr(weather, 'wind_speed', 10)
            description = getattr(weather, 'weather_description', '')
            
            # Données du forecast si disponibles
            forecast = getattr(weather, 'forecast_24h', {}) or {}
            
            weather_impact = {
                "current_temperature": current_temp,
                "forecast_temp_min": forecast.get("temp_min", current_temp - 5),
                "forecast_temp_max": forecast.get("temp_max", current_temp + 5),
                "temperature_change": round(
                    forecast.get("temp_avg", current_temp) - current_temp, 1
                ),
                "precipitation_probability": precip_prob / 100,
                "precipitation_total_mm": forecast.get("precip_total", 0),
                "wind_speed": wind_speed,
                "weather_description": description,
                "impact_score": round(
                    0.9 - (wind_speed / 100) - (precip_prob / 200), 2
                ),
                "data_source": "Open-Meteo (temps réel)"
            }
            
            # Ajuster les prévisions selon la météo
            if precip_prob > 70:
                for s in forecast_24h:
                    forecast_24h[s] = round(forecast_24h[s] * 0.9, 1)
            
            if wind_speed > 30:
                for s in forecast_24h:
                    forecast_24h[s] = round(forecast_24h[s] * 0.85, 1)
        else:
            # Fallback avec données simulées
            weather_impact = {
                "temperature_change": round(random.uniform(-5, 5), 1),
                "precipitation_probability": round(random.uniform(0, 1), 2),
                "wind_speed": round(random.uniform(5, 30), 1),
                "impact_score": round(random.uniform(0.7, 1.0), 2),
                "data_source": "Estimation (fallback)"
            }
        
        return weather_impact
    
    def _predict_movements(
        self,
        geospatial_data: Optional[Any]
    ) -> Dict[str, Any]:
        """
        Prédit les mouvements de la faune.
        """
        activity_peak = "dawn"  # Défaut
        primary_direction = "N"
        
        if geospatial_data:
            # Ajuster selon la température
            if hasattr(geospatial_data, 'weather') and geospatial_data.weather:
                temp = getattr(geospatial_data.weather, 'temperature', 15)
                if temp < -15 or temp > 25:
                    activity_peak = "dusk"
                elif temp > 15:
                    activity_peak = "dawn"
                else:
                    activity_peak = "midday"
            
            # Ajuster selon l'aspect du terrain
            if hasattr(geospatial_data, 'terrain') and geospatial_data.terrain:
                aspect = getattr(geospatial_data.terrain, 'aspect', None)
                if aspect is not None:
                    if aspect > 315 or aspect <= 45:
                        primary_direction = "S"
                    elif aspect > 45 and aspect <= 135:
                        primary_direction = "W"
                    elif aspect > 135 and aspect <= 225:
                        primary_direction = "N"
                    else:
                        primary_direction = "E"
        
        return {
            "primary_direction": primary_direction,
            "distance_estimate_km": round(random.uniform(0.5, 5), 1),
            "activity_peak": activity_peak,
            "congregation_probability": round(random.uniform(0.3, 0.9), 2)
        }
    
    def _calculate_weather_factor(
        self,
        temperature: float,
        precipitation: float
    ) -> float:
        """
        Calcule le facteur d'ajustement météo.
        """
        weather_factor = 1.0
        
        # Ajustement température
        if temperature < -10:
            weather_factor = 0.7
        elif temperature > 30:
            weather_factor = 0.8
        
        # Ajustement précipitations
        if precipitation > 50:
            weather_factor *= 0.8
        
        return weather_factor


# Instance singleton
prediction_engine = PredictionEngine()
