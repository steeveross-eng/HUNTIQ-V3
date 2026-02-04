"""
BIONIC™ Behavior Suite - Weather & Environmental Data Fetcher
===============================================================
Module de récupération des données météo temps réel et phase lunaire.

Sources:
- Open-Meteo API (gratuit, pas de clé API requise)
- Algorithme astronomique pour la phase lunaire

Version: 2.0 - P0-2 (Données Réelles)
"""

import logging
import math
import aiohttp
import asyncio
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, date, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)

# Try to import cache manager
try:
    import sys
    if '/app/bionic/engines' not in sys.path:
        sys.path.insert(0, '/app/bionic/engines')
    from core.cache_manager import cache_manager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache_manager = None


class BehaviorWeatherFetcher:
    """
    Fetcher de données environnementales pour la Behavior Suite.
    
    Récupère:
    - Météo temps réel (Open-Meteo)
    - Phase lunaire précise (algorithme astronomique)
    - Pression barométrique
    - Photopériode (lever/coucher du soleil)
    """
    
    # Open-Meteo API (gratuit)
    OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"
    
    # Nouvelle lune de référence (connue astronomiquement)
    # 2024-01-11 11:57 UTC - Nouvelle lune
    REFERENCE_NEW_MOON = datetime(2024, 1, 11, 11, 57, 0, tzinfo=timezone.utc)
    SYNODIC_MONTH = 29.53058770576  # Durée moyenne du cycle lunaire en jours
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._cache_namespace = "behavior_weather"
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtient ou crée une session HTTP."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session
    
    async def close(self):
        """Ferme la session HTTP."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    # =========================================================================
    # WEATHER DATA
    # =========================================================================
    
    async def get_current_weather(
        self, 
        lat: float, 
        lon: float,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Récupère les données météo actuelles depuis Open-Meteo.
        
        Returns:
            Dict avec temperature_c, precipitation_mm, wind_speed_kmh,
            cloud_cover_percent, pressure_hpa, humidity, etc.
        """
        cache_key = f"weather_{lat:.2f}_{lon:.2f}"
        
        # Check cache
        if use_cache and CACHE_AVAILABLE and cache_manager:
            cached = cache_manager.get(self._cache_namespace, cache_key)
            if cached:
                cached["from_cache"] = True
                return cached
        
        try:
            session = await self._get_session()
            
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m", 
                    "precipitation",
                    "rain",
                    "snowfall",
                    "weather_code",
                    "cloud_cover",
                    "pressure_msl",
                    "surface_pressure",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m"
                ],
                "timezone": "auto"
            }
            
            async with session.get(self.OPEN_METEO_BASE, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data.get("current", {})
                    
                    result = {
                        "temperature_c": current.get("temperature_2m", 15.0),
                        "humidity_percent": current.get("relative_humidity_2m", 60),
                        "precipitation_mm": current.get("precipitation", 0.0),
                        "rain_mm": current.get("rain", 0.0),
                        "snowfall_cm": current.get("snowfall", 0.0),
                        "weather_code": current.get("weather_code", 0),
                        "cloud_cover_percent": current.get("cloud_cover", 50),
                        "pressure_hpa": current.get("pressure_msl", 1013.0),
                        "surface_pressure_hpa": current.get("surface_pressure", 1013.0),
                        "wind_speed_kmh": current.get("wind_speed_10m", 10.0),
                        "wind_direction_deg": current.get("wind_direction_10m", 0),
                        "wind_gusts_kmh": current.get("wind_gusts_10m", 15.0),
                        "weather_description": self._decode_weather_code(current.get("weather_code", 0)),
                        "source": "Open-Meteo",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                        "from_cache": False
                    }
                    
                    # Cache result (TTL 15 minutes for weather)
                    if CACHE_AVAILABLE and cache_manager:
                        cache_manager.set(self._cache_namespace, cache_key, result, ttl=900)
                    
                    return result
                else:
                    logger.warning(f"Open-Meteo API returned status {response.status}")
                    return self._get_estimated_weather(lat, lon)
                    
        except asyncio.TimeoutError:
            logger.warning("Open-Meteo API timeout, using estimates")
            return self._get_estimated_weather(lat, lon)
        except Exception as e:
            logger.warning(f"Weather fetch error: {e}, using estimates")
            return self._get_estimated_weather(lat, lon)
    
    async def get_hourly_forecast(
        self,
        lat: float,
        lon: float,
        hours: int = 24,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Récupère les prévisions horaires pour les prochaines heures.
        """
        cache_key = f"forecast_{lat:.2f}_{lon:.2f}_{hours}"
        
        if use_cache and CACHE_AVAILABLE and cache_manager:
            cached = cache_manager.get(self._cache_namespace, cache_key)
            if cached:
                cached["from_cache"] = True
                return cached
        
        try:
            session = await self._get_session()
            
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": [
                    "temperature_2m",
                    "precipitation_probability",
                    "precipitation",
                    "cloud_cover",
                    "pressure_msl",
                    "wind_speed_10m"
                ],
                "forecast_hours": hours,
                "timezone": "auto"
            }
            
            async with session.get(self.OPEN_METEO_BASE, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    hourly = data.get("hourly", {})
                    
                    # Parse hourly data
                    hours_data = []
                    times = hourly.get("time", [])
                    
                    for i, time in enumerate(times[:hours]):
                        hours_data.append({
                            "time": time,
                            "temperature_c": hourly.get("temperature_2m", [15])[i] if hourly.get("temperature_2m") else 15,
                            "precipitation_prob": hourly.get("precipitation_probability", [0])[i] if hourly.get("precipitation_probability") else 0,
                            "precipitation_mm": hourly.get("precipitation", [0])[i] if hourly.get("precipitation") else 0,
                            "cloud_cover": hourly.get("cloud_cover", [50])[i] if hourly.get("cloud_cover") else 50,
                            "pressure_hpa": hourly.get("pressure_msl", [1013])[i] if hourly.get("pressure_msl") else 1013,
                            "wind_speed_kmh": hourly.get("wind_speed_10m", [10])[i] if hourly.get("wind_speed_10m") else 10
                        })
                    
                    result = {
                        "hours": hours_data,
                        "source": "Open-Meteo",
                        "from_cache": False
                    }
                    
                    if CACHE_AVAILABLE and cache_manager:
                        cache_manager.set(self._cache_namespace, cache_key, result, ttl=1800)
                    
                    return result
                    
        except Exception as e:
            logger.warning(f"Forecast fetch error: {e}")
            return {"hours": [], "source": "Error", "from_cache": False}
        
        return {"hours": [], "source": "Error", "from_cache": False}
    
    def _decode_weather_code(self, code: int) -> str:
        """Décode le code météo WMO en description."""
        codes = {
            0: "Ciel dégagé",
            1: "Principalement dégagé",
            2: "Partiellement nuageux",
            3: "Nuageux",
            45: "Brouillard",
            48: "Brouillard givrant",
            51: "Bruine légère",
            53: "Bruine modérée",
            55: "Bruine forte",
            61: "Pluie légère",
            63: "Pluie modérée",
            65: "Pluie forte",
            71: "Neige légère",
            73: "Neige modérée",
            75: "Neige forte",
            77: "Grains de neige",
            80: "Averses légères",
            81: "Averses modérées",
            82: "Averses violentes",
            85: "Averses de neige légères",
            86: "Averses de neige fortes",
            95: "Orage",
            96: "Orage avec grêle légère",
            99: "Orage avec forte grêle"
        }
        return codes.get(code, "Conditions variables")
    
    def _get_estimated_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Retourne des estimations météo basées sur la saison et la latitude."""
        month = datetime.now().month
        day_of_year = datetime.now().timetuple().tm_yday
        
        # Température estimée selon la latitude et la saison (Québec)
        base_temp = 15.0
        if month in [12, 1, 2]:
            base_temp = -10 - (lat - 45) * 0.8
        elif month in [3, 4]:
            base_temp = 2 + (180 - day_of_year) * 0.1
        elif month in [5, 6]:
            base_temp = 15 + (day_of_year - 120) * 0.1
        elif month in [7, 8]:
            base_temp = 22 - (lat - 45) * 0.5
        elif month in [9, 10]:
            base_temp = 15 - (day_of_year - 250) * 0.15
        else:  # November
            base_temp = 3 - (day_of_year - 305) * 0.3
        
        return {
            "temperature_c": round(base_temp, 1),
            "humidity_percent": 65,
            "precipitation_mm": 0.0,
            "cloud_cover_percent": 40,
            "pressure_hpa": 1013.0,
            "wind_speed_kmh": 12.0,
            "wind_direction_deg": 225,
            "weather_description": "Estimé (pas de données)",
            "source": "BIONIC Estimate",
            "from_cache": False
        }
    
    # =========================================================================
    # LUNAR DATA
    # =========================================================================
    
    def get_moon_phase(
        self, 
        target_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calcule la phase lunaire précise pour une date donnée.
        
        Utilise l'algorithme astronomique basé sur la nouvelle lune de référence
        et la durée moyenne du mois synodique (29.53 jours).
        
        Returns:
            Dict avec phase (0-1), illumination (0-1), phase_name, etc.
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc)
        elif target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=timezone.utc)
        
        # Calcul du nombre de jours depuis la nouvelle lune de référence
        delta = target_date - self.REFERENCE_NEW_MOON
        days_since_new_moon = delta.total_seconds() / 86400.0
        
        # Position dans le cycle (0-1, 0 = nouvelle lune, 0.5 = pleine lune)
        cycles_elapsed = days_since_new_moon / self.SYNODIC_MONTH
        phase = cycles_elapsed % 1.0  # Position dans le cycle actuel
        
        # Calcul de l'illumination (0 à pleine lune, puis redescend)
        # Utilise une fonction cosinus pour simuler l'illumination
        illumination = (1 - math.cos(phase * 2 * math.pi)) / 2
        
        # Déterminer le nom de la phase
        phase_name, phase_name_fr = self._get_moon_phase_name(phase)
        
        # Calculer le prochain événement lunaire
        next_event = self._get_next_lunar_event(phase, target_date)
        
        # Impact sur la chasse
        hunting_impact = self._calculate_lunar_hunting_impact(phase, illumination)
        
        return {
            "phase": round(phase, 4),
            "illumination": round(illumination, 4),
            "illumination_percent": round(illumination * 100, 1),
            "phase_name": phase_name,
            "phase_name_fr": phase_name_fr,
            "is_waxing": phase < 0.5,
            "is_full_moon": 0.45 <= phase <= 0.55,
            "is_new_moon": phase < 0.05 or phase > 0.95,
            "days_since_new_moon": round(days_since_new_moon % self.SYNODIC_MONTH, 1),
            "days_to_full_moon": round((0.5 - phase) * self.SYNODIC_MONTH if phase < 0.5 else (1.5 - phase) * self.SYNODIC_MONTH, 1),
            "next_event": next_event,
            "hunting_impact": hunting_impact,
            "source": "BIONIC Astronomical Algorithm",
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _get_moon_phase_name(self, phase: float) -> Tuple[str, str]:
        """Retourne le nom de la phase lunaire en anglais et français."""
        if phase < 0.0625:
            return ("New Moon", "Nouvelle lune")
        elif phase < 0.1875:
            return ("Waxing Crescent", "Premier croissant")
        elif phase < 0.3125:
            return ("First Quarter", "Premier quartier")
        elif phase < 0.4375:
            return ("Waxing Gibbous", "Gibbeuse croissante")
        elif phase < 0.5625:
            return ("Full Moon", "Pleine lune")
        elif phase < 0.6875:
            return ("Waning Gibbous", "Gibbeuse décroissante")
        elif phase < 0.8125:
            return ("Last Quarter", "Dernier quartier")
        elif phase < 0.9375:
            return ("Waning Crescent", "Dernier croissant")
        else:
            return ("New Moon", "Nouvelle lune")
    
    def _get_next_lunar_event(
        self, 
        current_phase: float,
        current_date: datetime
    ) -> Dict[str, Any]:
        """Calcule le prochain événement lunaire significatif."""
        events = [
            (0.0, "Nouvelle lune", "New Moon"),
            (0.25, "Premier quartier", "First Quarter"),
            (0.5, "Pleine lune", "Full Moon"),
            (0.75, "Dernier quartier", "Last Quarter")
        ]
        
        for event_phase, name_fr, name_en in events:
            if current_phase < event_phase:
                days_to_event = (event_phase - current_phase) * self.SYNODIC_MONTH
                event_date = current_date + timedelta(days=days_to_event)
                return {
                    "name_fr": name_fr,
                    "name_en": name_en,
                    "days_away": round(days_to_event, 1),
                    "date": event_date.strftime("%Y-%m-%d")
                }
        
        # Prochain cycle - nouvelle lune
        days_to_new = (1.0 - current_phase) * self.SYNODIC_MONTH
        event_date = current_date + timedelta(days=days_to_new)
        return {
            "name_fr": "Nouvelle lune",
            "name_en": "New Moon",
            "days_away": round(days_to_new, 1),
            "date": event_date.strftime("%Y-%m-%d")
        }
    
    def _calculate_lunar_hunting_impact(
        self, 
        phase: float, 
        illumination: float
    ) -> Dict[str, Any]:
        """
        Calcule l'impact de la phase lunaire sur la chasse.
        
        Théorie:
        - Pleine lune: Plus d'activité nocturne, moins à l'aube/crépuscule
        - Nouvelle lune: Activité concentrée à l'aube et au crépuscule
        - Phases intermédiaires: Meilleur équilibre
        """
        # Score de base (les quartiers sont généralement meilleurs pour la chasse diurne)
        if 0.15 <= phase <= 0.35 or 0.65 <= phase <= 0.85:
            # Quartiers - bon pour la chasse
            score = 80
            impact = "favorable"
            description = "Phase lunaire favorable - bon équilibre d'activité"
        elif 0.45 <= phase <= 0.55:
            # Pleine lune - activité nocturne accrue
            score = 60
            impact = "mixed"
            description = "Pleine lune - arrivez très tôt, activité nocturne élevée"
        elif phase < 0.08 or phase > 0.92:
            # Nouvelle lune - bon pour aube/crépuscule
            score = 75
            impact = "favorable"
            description = "Nouvelle lune - activité concentrée aube/crépuscule"
        else:
            score = 70
            impact = "neutral"
            description = "Phase transitoire - conditions moyennes"
        
        return {
            "score": score,
            "impact": impact,
            "description": description,
            "best_times": ["Aube", "Crépuscule"] if phase < 0.4 or phase > 0.6 else ["Tôt le matin", "Fin d'après-midi"],
            "nocturnal_activity_modifier": round(1.0 + (illumination - 0.5) * 0.4, 2)
        }
    
    # =========================================================================
    # PHOTOPERIOD (Sunrise/Sunset)
    # =========================================================================
    
    async def get_photoperiod(
        self, 
        lat: float, 
        lon: float,
        target_date: Optional[date] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Récupère les données de photopériode (lever/coucher du soleil).
        """
        if target_date is None:
            target_date = date.today()
        
        cache_key = f"photoperiod_{lat:.2f}_{lon:.2f}_{target_date.isoformat()}"
        
        if use_cache and CACHE_AVAILABLE and cache_manager:
            cached = cache_manager.get(self._cache_namespace, cache_key)
            if cached:
                cached["from_cache"] = True
                return cached
        
        try:
            session = await self._get_session()
            
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": ["sunrise", "sunset", "daylight_duration"],
                "timezone": "auto",
                "start_date": target_date.isoformat(),
                "end_date": target_date.isoformat()
            }
            
            async with session.get(self.OPEN_METEO_BASE, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    daily = data.get("daily", {})
                    
                    sunrise = daily.get("sunrise", ["06:00"])[0] if daily.get("sunrise") else "06:00"
                    sunset = daily.get("sunset", ["18:00"])[0] if daily.get("sunset") else "18:00"
                    daylight = daily.get("daylight_duration", [43200])[0] if daily.get("daylight_duration") else 43200
                    
                    result = {
                        "sunrise": sunrise,
                        "sunset": sunset,
                        "daylight_hours": round(daylight / 3600, 2),
                        "golden_hour_morning": self._calculate_golden_hour(sunrise, is_morning=True),
                        "golden_hour_evening": self._calculate_golden_hour(sunset, is_morning=False),
                        "source": "Open-Meteo",
                        "from_cache": False
                    }
                    
                    if CACHE_AVAILABLE and cache_manager:
                        cache_manager.set(self._cache_namespace, cache_key, result, ttl=86400)
                    
                    return result
                    
        except Exception as e:
            logger.warning(f"Photoperiod fetch error: {e}")
        
        # Fallback estimation
        return self._estimate_photoperiod(lat, target_date)
    
    def _calculate_golden_hour(self, time_str: str, is_morning: bool) -> str:
        """Calcule l'heure dorée (30 min après lever / 30 min avant coucher)."""
        try:
            if "T" in time_str:
                time_part = time_str.split("T")[1][:5]
            else:
                time_part = time_str[:5]
            
            hours, minutes = map(int, time_part.split(":"))
            
            if is_morning:
                minutes += 30
                if minutes >= 60:
                    hours += 1
                    minutes -= 60
            else:
                minutes -= 30
                if minutes < 0:
                    hours -= 1
                    minutes += 60
            
            return f"{hours:02d}:{minutes:02d}"
        except:
            return "06:30" if is_morning else "17:30"
    
    def _estimate_photoperiod(self, lat: float, target_date: date) -> Dict[str, Any]:
        """Estime la photopériode basée sur la latitude et le jour de l'année."""
        day_of_year = target_date.timetuple().tm_yday
        
        # Approximation simplifiée pour le Québec (45-52°N)
        # Solstice d'été (~172): ~16h de jour, Solstice d'hiver (~355): ~8h de jour
        avg_daylight = 12  # heures
        amplitude = 4 + (lat - 45) * 0.2  # Plus au nord = plus de variation
        
        daylight_hours = avg_daylight + amplitude * math.cos((day_of_year - 172) * 2 * math.pi / 365)
        
        # Estimer lever/coucher
        noon = 12
        half_day = daylight_hours / 2
        sunrise_hour = noon - half_day
        sunset_hour = noon + half_day
        
        return {
            "sunrise": f"{int(sunrise_hour):02d}:{int((sunrise_hour % 1) * 60):02d}",
            "sunset": f"{int(sunset_hour):02d}:{int((sunset_hour % 1) * 60):02d}",
            "daylight_hours": round(daylight_hours, 2),
            "golden_hour_morning": f"{int(sunrise_hour + 0.5):02d}:{int(((sunrise_hour + 0.5) % 1) * 60):02d}",
            "golden_hour_evening": f"{int(sunset_hour - 0.5):02d}:{int(((sunset_hour - 0.5) % 1) * 60):02d}",
            "source": "BIONIC Estimate",
            "from_cache": False
        }
    
    # =========================================================================
    # PRESSURE TREND
    # =========================================================================
    
    async def get_pressure_trend(
        self,
        lat: float,
        lon: float,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyse la tendance de pression barométrique.
        
        Une pression en hausse favorise généralement l'activité animale,
        tandis qu'une pression en baisse peut déclencher une activité
        frénétique avant une tempête.
        """
        forecast = await self.get_hourly_forecast(lat, lon, hours=12, use_cache=use_cache)
        
        hours_data = forecast.get("hours", [])
        if len(hours_data) < 3:
            return {
                "current_hpa": 1013.0,
                "trend": "stable",
                "change_6h": 0.0,
                "hunting_impact": "neutral",
                "source": "Insufficient data"
            }
        
        # Analyser la tendance
        pressures = [h.get("pressure_hpa", 1013) for h in hours_data]
        current = pressures[0]
        
        # Changement sur 6h
        if len(pressures) >= 6:
            change_6h = pressures[5] - pressures[0]
        else:
            change_6h = pressures[-1] - pressures[0]
        
        # Déterminer la tendance
        if change_6h > 3:
            trend = "rising_fast"
            hunting_impact = "very_favorable"
            description = "Pression en forte hausse - Excellentes conditions à venir"
        elif change_6h > 1:
            trend = "rising"
            hunting_impact = "favorable"
            description = "Pression en hausse - Bonnes conditions"
        elif change_6h < -3:
            trend = "falling_fast"
            hunting_impact = "mixed"
            description = "Pression en forte baisse - Activité frénétique possible avant tempête"
        elif change_6h < -1:
            trend = "falling"
            hunting_impact = "moderate"
            description = "Pression en baisse - Tempête possible"
        else:
            trend = "stable"
            hunting_impact = "neutral"
            description = "Pression stable"
        
        return {
            "current_hpa": round(current, 1),
            "trend": trend,
            "change_6h": round(change_6h, 2),
            "hunting_impact": hunting_impact,
            "description": description,
            "source": "Open-Meteo Forecast"
        }
    
    # =========================================================================
    # COMBINED ENVIRONMENTAL DATA
    # =========================================================================
    
    async def get_all_environmental_data(
        self,
        lat: float,
        lon: float,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Récupère toutes les données environnementales en parallèle.
        
        Returns:
            Dict combiné avec météo, lunaire, photopériode et tendance de pression.
        """
        # Exécuter les requêtes en parallèle
        weather_task = self.get_current_weather(lat, lon, use_cache)
        photoperiod_task = self.get_photoperiod(lat, lon, use_cache=use_cache)
        pressure_task = self.get_pressure_trend(lat, lon, use_cache)
        
        # Données lunaires sont synchrones
        lunar_data = self.get_moon_phase()
        
        weather_data, photoperiod_data, pressure_data = await asyncio.gather(
            weather_task, photoperiod_task, pressure_task
        )
        
        return {
            "weather": weather_data,
            "lunar": lunar_data,
            "photoperiod": photoperiod_data,
            "pressure_trend": pressure_data,
            "location": {"lat": lat, "lon": lon},
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }


# Singleton instance
behavior_weather_fetcher = BehaviorWeatherFetcher()


# Import timedelta at top level
from datetime import timedelta
