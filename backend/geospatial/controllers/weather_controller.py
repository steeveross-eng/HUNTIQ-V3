"""
HUNTIQ V3 - BIONIC™ Weather Controller
Real-time weather data from OpenWeatherMap API
Includes hunting score calculation based on weather conditions
"""

import httpx
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# OpenWeatherMap API Configuration
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherController:
    """
    Controller for weather data from OpenWeatherMap
    Calculates hunting scores based on weather conditions
    """
    
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = OPENWEATHER_BASE_URL
    
    async def get_current_weather(
        self, 
        lat: float, 
        lon: float,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get current weather for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            units: metric (Celsius) or imperial (Fahrenheit)
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "OpenWeatherMap API key not configured",
                "mock_data": self._get_mock_weather(lat, lon)
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": units,
                        "lang": "fr"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._format_current_weather(data, units)
                else:
                    logger.error(f"OpenWeatherMap error: {response.status_code}")
                    return {
                        "status": "error",
                        "code": response.status_code,
                        "message": "Failed to fetch weather data"
                    }
                    
            except Exception as e:
                logger.error(f"Weather API error: {e}")
                return {
                    "status": "error",
                    "message": str(e)
                }
    
    async def get_forecast(
        self,
        lat: float,
        lon: float,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """
        Get 5-day forecast for a location
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "OpenWeatherMap API key not configured"
            }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": units,
                        "lang": "fr"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._format_forecast(data, units)
                else:
                    return {
                        "status": "error",
                        "code": response.status_code
                    }
                    
            except Exception as e:
                logger.error(f"Forecast API error: {e}")
                return {"status": "error", "message": str(e)}
    
    def _format_current_weather(self, data: Dict, units: str) -> Dict[str, Any]:
        """Format raw API response into structured weather data"""
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})
        sys = data.get("sys", {})
        
        temp_unit = "°C" if units == "metric" else "°F"
        wind_unit = "km/h" if units == "metric" else "mph"
        
        # Calculate hunting score
        hunting_score = self.calculate_hunting_score({
            "temperature": main.get("temp", 15),
            "humidity": main.get("humidity", 50),
            "wind_speed": wind.get("speed", 0),
            "cloud_cover": clouds.get("all", 0),
            "pressure": main.get("pressure", 1013),
            "condition": weather.get("main", "Clear")
        })
        
        return {
            "status": "success",
            "location": {
                "name": data.get("name", "Unknown"),
                "country": sys.get("country", ""),
                "coordinates": {
                    "lat": data.get("coord", {}).get("lat"),
                    "lon": data.get("coord", {}).get("lon")
                }
            },
            "current": {
                "temperature": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "temp_min": main.get("temp_min"),
                "temp_max": main.get("temp_max"),
                "temp_unit": temp_unit,
                "humidity": main.get("humidity"),
                "pressure": main.get("pressure"),
                "visibility": data.get("visibility", 10000) / 1000,  # Convert to km
            },
            "weather": {
                "condition": weather.get("main"),
                "description": weather.get("description"),
                "icon": weather.get("icon"),
                "icon_url": f"https://openweathermap.org/img/wn/{weather.get('icon', '01d')}@2x.png"
            },
            "wind": {
                "speed": wind.get("speed"),
                "direction": wind.get("deg"),
                "gust": wind.get("gust"),
                "unit": wind_unit
            },
            "clouds": {
                "coverage": clouds.get("all")
            },
            "sun": {
                "sunrise": datetime.fromtimestamp(sys.get("sunrise", 0), tz=timezone.utc).isoformat() if sys.get("sunrise") else None,
                "sunset": datetime.fromtimestamp(sys.get("sunset", 0), tz=timezone.utc).isoformat() if sys.get("sunset") else None
            },
            "hunting_score": hunting_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_source": "OpenWeatherMap",
            "units": units
        }
    
    def _format_forecast(self, data: Dict, units: str) -> Dict[str, Any]:
        """Format forecast data"""
        forecasts = []
        temp_unit = "°C" if units == "metric" else "°F"
        
        for item in data.get("list", []):
            weather = item.get("weather", [{}])[0]
            main = item.get("main", {})
            wind = item.get("wind", {})
            
            hunting_score = self.calculate_hunting_score({
                "temperature": main.get("temp", 15),
                "humidity": main.get("humidity", 50),
                "wind_speed": wind.get("speed", 0),
                "cloud_cover": item.get("clouds", {}).get("all", 0),
                "pressure": main.get("pressure", 1013),
                "condition": weather.get("main", "Clear")
            })
            
            forecasts.append({
                "datetime": item.get("dt_txt"),
                "timestamp": item.get("dt"),
                "temperature": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "temp_unit": temp_unit,
                "humidity": main.get("humidity"),
                "condition": weather.get("main"),
                "description": weather.get("description"),
                "icon": weather.get("icon"),
                "wind_speed": wind.get("speed"),
                "hunting_score": hunting_score
            })
        
        # Group by day
        daily_forecasts = self._group_forecasts_by_day(forecasts)
        
        return {
            "status": "success",
            "city": {
                "name": data.get("city", {}).get("name"),
                "country": data.get("city", {}).get("country")
            },
            "forecasts": forecasts,
            "daily_summary": daily_forecasts,
            "data_source": "OpenWeatherMap"
        }
    
    def _group_forecasts_by_day(self, forecasts: List[Dict]) -> List[Dict]:
        """Group 3-hour forecasts into daily summaries"""
        days = {}
        
        for f in forecasts:
            if not f.get("datetime"):
                continue
            date = f["datetime"].split(" ")[0]
            
            if date not in days:
                days[date] = {
                    "date": date,
                    "temps": [],
                    "conditions": [],
                    "scores": []
                }
            
            days[date]["temps"].append(f.get("temperature", 0))
            days[date]["conditions"].append(f.get("condition", ""))
            days[date]["scores"].append(f.get("hunting_score", {}).get("score", 50))
        
        daily = []
        for date, data in days.items():
            temps = [t for t in data["temps"] if t is not None]
            scores = [s for s in data["scores"] if s is not None]
            
            daily.append({
                "date": date,
                "temp_min": min(temps) if temps else None,
                "temp_max": max(temps) if temps else None,
                "temp_avg": sum(temps) / len(temps) if temps else None,
                "dominant_condition": max(set(data["conditions"]), key=data["conditions"].count) if data["conditions"] else None,
                "avg_hunting_score": round(sum(scores) / len(scores)) if scores else 50
            })
        
        return daily
    
    def calculate_hunting_score(self, conditions: Dict) -> Dict[str, Any]:
        """
        Calculate hunting score based on weather conditions
        
        Factors considered:
        - Temperature: Optimal 5-15°C for deer
        - Wind: Low wind preferred (< 15 km/h)
        - Pressure: Rising/stable pressure is favorable
        - Humidity: Moderate humidity preferred
        - Cloud cover: Light overcast can be favorable
        - Precipitation: Light rain can help, heavy rain is bad
        """
        score = 100
        factors = []
        
        temp = conditions.get("temperature", 15)
        humidity = conditions.get("humidity", 50)
        wind_speed = conditions.get("wind_speed", 0)
        cloud_cover = conditions.get("cloud_cover", 0)
        pressure = conditions.get("pressure", 1013)
        condition = conditions.get("condition", "Clear")
        
        # Temperature scoring (optimal: 5-15°C)
        if 5 <= temp <= 15:
            temp_score = 100
            factors.append({"factor": "Température", "status": "optimal", "impact": 0})
        elif 0 <= temp < 5 or 15 < temp <= 20:
            temp_score = 80
            score -= 10
            factors.append({"factor": "Température", "status": "acceptable", "impact": -10})
        elif -5 <= temp < 0 or 20 < temp <= 25:
            temp_score = 60
            score -= 20
            factors.append({"factor": "Température", "status": "suboptimal", "impact": -20})
        else:
            temp_score = 40
            score -= 30
            factors.append({"factor": "Température", "status": "défavorable", "impact": -30})
        
        # Wind scoring (optimal: < 10 km/h)
        if wind_speed < 10:
            factors.append({"factor": "Vent", "status": "calme", "impact": 0})
        elif wind_speed < 20:
            score -= 10
            factors.append({"factor": "Vent", "status": "modéré", "impact": -10})
        elif wind_speed < 30:
            score -= 20
            factors.append({"factor": "Vent", "status": "fort", "impact": -20})
        else:
            score -= 35
            factors.append({"factor": "Vent", "status": "très fort", "impact": -35})
        
        # Pressure scoring (rising pressure is good)
        if pressure >= 1020:
            factors.append({"factor": "Pression", "status": "haute (favorable)", "impact": +5})
            score += 5
        elif pressure >= 1010:
            factors.append({"factor": "Pression", "status": "normale", "impact": 0})
        else:
            score -= 5
            factors.append({"factor": "Pression", "status": "basse", "impact": -5})
        
        # Weather condition scoring
        condition_impacts = {
            "Clear": (0, "dégagé"),
            "Clouds": (-5, "nuageux"),
            "Drizzle": (-10, "bruine"),
            "Rain": (-20, "pluie"),
            "Thunderstorm": (-40, "orage"),
            "Snow": (-15, "neige"),
            "Mist": (-5, "brume"),
            "Fog": (-15, "brouillard")
        }
        
        impact, status = condition_impacts.get(condition, (0, condition))
        score += impact
        factors.append({"factor": "Conditions", "status": status, "impact": impact})
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Determine level
        if score >= 80:
            level = "excellent"
            recommendation = "Conditions idéales pour la chasse. Profitez-en!"
        elif score >= 60:
            level = "bon"
            recommendation = "Bonnes conditions. Les animaux devraient être actifs."
        elif score >= 40:
            level = "moyen"
            recommendation = "Conditions acceptables. Soyez patient."
        elif score >= 20:
            level = "faible"
            recommendation = "Conditions difficiles. Concentrez-vous sur les heures de pointe."
        else:
            level = "mauvais"
            recommendation = "Conditions défavorables. Considérez reporter votre sortie."
        
        return {
            "score": score,
            "level": level,
            "recommendation": recommendation,
            "factors": factors,
            "optimal_hours": self._get_optimal_hours(conditions)
        }
    
    def _get_optimal_hours(self, conditions: Dict) -> List[str]:
        """Determine optimal hunting hours based on conditions"""
        hours = []
        
        # Dawn and dusk are always good
        hours.append("Aube (30 min avant lever du soleil)")
        hours.append("Crépuscule (1h avant coucher du soleil)")
        
        # Mid-morning if cool
        temp = conditions.get("temperature", 15)
        if temp < 10:
            hours.append("Mi-matinée (9h-11h)")
        
        # Afternoon if overcast
        cloud_cover = conditions.get("cloud_cover", 0)
        if cloud_cover > 50:
            hours.append("Après-midi (14h-16h) - ciel couvert")
        
        return hours
    
    def _get_mock_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Return mock weather data when API key is not available"""
        return {
            "current": {
                "temperature": 12,
                "feels_like": 10,
                "humidity": 65,
                "temp_unit": "°C"
            },
            "weather": {
                "condition": "Clouds",
                "description": "Partiellement nuageux"
            },
            "wind": {
                "speed": 15,
                "unit": "km/h"
            },
            "hunting_score": {
                "score": 72,
                "level": "bon",
                "recommendation": "Bonnes conditions pour la chasse"
            },
            "note": "Données simulées - Clé API non configurée"
        }


# Singleton instance
weather_controller = WeatherController()
