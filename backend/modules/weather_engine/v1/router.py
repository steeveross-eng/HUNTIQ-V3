"""Weather Engine Router - CORE

FastAPI router for weather-based hunting analysis.

Version: 1.0.0
API Prefix: /api/v1/weather
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone
from .service import WeatherService
from .models import WeatherCondition, WeatherRequest

router = APIRouter(prefix="/api/v1/weather", tags=["Weather Engine"])

# Initialize service
_service = WeatherService()


@router.get("/")
async def weather_engine_info():
    """Get weather engine information"""
    return {
        "module": "weather_engine",
        "version": "1.0.0",
        "description": "Weather-based hunting condition analysis",
        "features": [
            "Hunting score calculation",
            "Deer activity prediction",
            "Best hunting times",
            "Moon phase analysis",
            "Wind strategy advice"
        ],
        "optimal_conditions": _service.OPTIMAL_CONDITIONS
    }


@router.post("/analyze")
async def analyze_conditions(weather: WeatherCondition):
    """
    Analyze weather conditions and get hunting forecast.
    
    Provide current weather data to receive:
    - Overall hunting score (0-10)
    - Predicted deer activity level
    - Best hunting times
    - Strategic recommendations
    """
    forecast = _service.generate_forecast(weather)
    
    return {
        "success": True,
        "input": weather.model_dump(),
        "forecast": {
            "date": forecast.date.isoformat(),
            "overall_score": forecast.overall_score,
            "deer_activity": forecast.deer_activity,
            "best_times": forecast.best_times,
            "wind_advice": forecast.wind_advice,
            "pressure_trend": forecast.pressure_trend,
            "recommendations": forecast.recommendations
        }
    }


@router.get("/score")
async def calculate_quick_score(
    temperature: float = Query(..., description="Temperature in Celsius"),
    humidity: float = Query(60, ge=0, le=100, description="Humidity %"),
    wind_speed: float = Query(10, ge=0, description="Wind speed km/h"),
    wind_direction: str = Query("N", description="Wind direction"),
    pressure: float = Query(1013, description="Pressure hPa"),
    precipitation: float = Query(0, ge=0, description="Precipitation mm")
):
    """Quick hunting score calculation from weather parameters"""
    weather = WeatherCondition(
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        pressure=pressure,
        precipitation=precipitation,
        condition="Custom input"
    )
    
    score = _service.calculate_hunting_score(weather)
    activity = _service.get_deer_activity_level(score)
    
    return {
        "success": True,
        "score": score,
        "activity_level": activity,
        "rating": _get_score_rating(score)
    }


@router.get("/moon")
async def get_moon_phase(date: Optional[str] = None):
    """
    Get moon phase for hunting analysis.
    
    Args:
        date: Optional ISO date string (defaults to today)
    """
    if date:
        try:
            target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format.")
    else:
        target_date = datetime.now(timezone.utc)
    
    moon = _service.get_moon_phase(target_date)
    
    return {
        "success": True,
        "date": target_date.isoformat(),
        "moon": {
            "phase": moon.phase,
            "phase_name": _get_phase_name(moon.phase),
            "illumination": moon.illumination,
            "hunting_impact": moon.hunting_impact
        }
    }


@router.get("/optimal")
async def get_optimal_conditions():
    """Get optimal hunting conditions reference"""
    return {
        "success": True,
        "optimal_conditions": {
            "temperature": {
                **_service.OPTIMAL_CONDITIONS["temperature"],
                "unit": "°C",
                "note": "Cervidés plus actifs par temps frais"
            },
            "humidity": {
                **_service.OPTIMAL_CONDITIONS["humidity"],
                "unit": "%",
                "note": "Humidité modérée favorise la diffusion des odeurs"
            },
            "wind_speed": {
                **_service.OPTIMAL_CONDITIONS["wind_speed"],
                "unit": "km/h",
                "note": "Vent léger aide à masquer votre présence"
            },
            "pressure": {
                "note": "Changements de pression déclenchent l'activité",
                "change_threshold": f"{_service.OPTIMAL_CONDITIONS['pressure_change']} hPa"
            }
        }
    }


@router.get("/times")
async def get_best_times(
    temperature: float = Query(10, description="Current temperature"),
    wind_speed: float = Query(10, description="Wind speed"),
    precipitation: float = Query(0, description="Precipitation")
):
    """Get recommended hunting times for current conditions"""
    weather = WeatherCondition(
        temperature=temperature,
        humidity=60,
        wind_speed=wind_speed,
        wind_direction="N",
        pressure=1013,
        precipitation=precipitation,
        condition="Calculated"
    )
    
    times = _service.get_best_hunting_times(weather)
    
    return {
        "success": True,
        "best_times": times,
        "note": "Horaires basés sur les conditions fournies"
    }


def _get_score_rating(score: float) -> str:
    """Convert score to text rating"""
    if score >= 8:
        return "🟢 Excellent"
    elif score >= 6:
        return "🟡 Bon"
    elif score >= 4:
        return "🟠 Moyen"
    else:
        return "🔴 Défavorable"


def _get_phase_name(phase: str) -> str:
    """Get French name for moon phase"""
    names = {
        "new": "Nouvelle lune",
        "waxing_crescent": "Premier croissant",
        "first_quarter": "Premier quartier",
        "waxing_gibbous": "Gibbeuse croissante",
        "full": "Pleine lune",
        "waning_gibbous": "Gibbeuse décroissante",
        "third_quarter": "Dernier quartier",
        "waning_crescent": "Dernier croissant"
    }
    return names.get(phase, phase)
