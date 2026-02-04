"""
BIONIC™ Current Conditions API
================================
Endpoint dédié pour le panneau "Conditions actuelles" du frontend.

Module 100% indépendant alimenté par BehaviorWeatherFetcher.
Préparé pour cache L3 (Redis) et export PDF.

Version: 1.0.0
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

import sys
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

# Import weather fetcher
try:
    from behavior.core.weather_fetcher import behavior_weather_fetcher
    FETCHER_AVAILABLE = True
except ImportError:
    FETCHER_AVAILABLE = False
    behavior_weather_fetcher = None

logger = logging.getLogger(__name__)

# Router
conditions_router = APIRouter(prefix="/api/bionic/conditions", tags=["BIONIC Conditions"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class LunarCondition(BaseModel):
    """Phase lunaire actuelle."""
    phase: float = Field(..., description="Phase 0-1 (0=nouvelle, 0.5=pleine)")
    phase_name: str = Field(..., description="Nom de la phase en français")
    illumination_percent: float = Field(..., description="Illumination 0-100%")
    is_waxing: bool = Field(..., description="Lune croissante")
    is_full_moon: bool
    is_new_moon: bool
    days_to_next_event: float
    next_event_name: str
    hunting_impact: str = Field(..., description="favorable/mixed/neutral")
    hunting_description: str


class PressureCondition(BaseModel):
    """Pression barométrique actuelle."""
    value_hpa: float = Field(..., description="Pression en hPa")
    trend: str = Field(..., description="rising_fast/rising/stable/falling/falling_fast")
    trend_icon: str = Field(..., description="↑↑/↑/→/↓/↓↓")
    change_6h: float = Field(..., description="Changement sur 6h en hPa")
    hunting_impact: str
    hunting_description: str


class PhotoperiodCondition(BaseModel):
    """Photopériode actuelle."""
    sunrise: str = Field(..., description="Heure du lever HH:MM")
    sunset: str = Field(..., description="Heure du coucher HH:MM")
    daylight_hours: float = Field(..., description="Durée du jour en heures")
    golden_hour_morning: str
    golden_hour_evening: str
    optimal_hunting_windows: list


class WeatherCondition(BaseModel):
    """Conditions météo actuelles."""
    temperature_c: float
    feels_like_c: Optional[float] = None
    humidity_percent: float
    wind_speed_kmh: float
    wind_direction: str
    cloud_cover_percent: float
    precipitation_mm: float
    weather_description: str
    weather_icon: str


class HuntingImpact(BaseModel):
    """Impact global sur l'activité faunique."""
    score: float = Field(..., ge=0, le=100, description="Score global 0-100")
    level: str = Field(..., description="excellent/good/moderate/poor")
    icon: str
    summary: str = Field(..., description="Phrase courte d'impact")
    factors: Dict[str, Any]


class CurrentConditionsResponse(BaseModel):
    """Réponse complète des conditions actuelles."""
    # Metadata
    request_id: str
    location: Dict[str, float]
    fetched_at: str
    data_source: str
    cache_status: str = "miss"
    
    # Conditions
    lunar: LunarCondition
    pressure: PressureCondition
    photoperiod: PhotoperiodCondition
    weather: WeatherCondition
    
    # Impact global
    hunting_impact: HuntingImpact
    
    # Pour export PDF
    exportable: bool = True
    export_summary: str


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_trend_icon(trend: str) -> str:
    """Retourne l'icône de tendance."""
    icons = {
        "rising_fast": "↑↑",
        "rising": "↑",
        "stable": "→",
        "falling": "↓",
        "falling_fast": "↓↓"
    }
    return icons.get(trend, "→")


def get_weather_icon(code: int, description: str) -> str:
    """Retourne l'icône météo."""
    desc_lower = description.lower()
    if "soleil" in desc_lower or "dégagé" in desc_lower or "clear" in desc_lower:
        return "☀️"
    elif "nuage" in desc_lower or "cloud" in desc_lower:
        return "☁️"
    elif "pluie" in desc_lower or "rain" in desc_lower:
        return "🌧️"
    elif "neige" in desc_lower or "snow" in desc_lower:
        return "❄️"
    elif "orage" in desc_lower or "storm" in desc_lower:
        return "⛈️"
    elif "brouillard" in desc_lower or "fog" in desc_lower:
        return "🌫️"
    return "🌤️"


def calculate_hunting_impact(
    lunar: Dict,
    pressure: Dict,
    weather: Dict,
    photoperiod: Dict
) -> Dict[str, Any]:
    """Calcule l'impact global sur la chasse."""
    score = 50.0
    factors = {}
    
    # Impact lunaire (20% du score)
    lunar_impact = lunar.get("hunting_impact", {})
    lunar_score = lunar_impact.get("score", 70)
    lunar_contrib = (lunar_score - 50) * 0.4
    score += lunar_contrib
    factors["lunar"] = {
        "contribution": round(lunar_contrib, 1),
        "description": lunar_impact.get("description", "")
    }
    
    # Impact pression (25% du score)
    pressure_trend = pressure.get("trend", "stable")
    if pressure_trend == "rising_fast":
        pressure_contrib = 20
    elif pressure_trend == "rising":
        pressure_contrib = 10
    elif pressure_trend == "falling_fast":
        pressure_contrib = 5  # Activité frénétique possible
    elif pressure_trend == "falling":
        pressure_contrib = -10
    else:
        pressure_contrib = 0
    score += pressure_contrib
    factors["pressure"] = {
        "contribution": pressure_contrib,
        "trend": pressure_trend
    }
    
    # Impact météo (35% du score)
    temp = weather.get("temperature_c", 15)
    wind = weather.get("wind_speed_kmh", 10)
    precip = weather.get("precipitation_mm", 0)
    
    # Température
    if 5 <= temp <= 15:
        temp_contrib = 15
    elif 0 <= temp < 5 or 15 < temp <= 20:
        temp_contrib = 8
    elif -10 <= temp < 0 or 20 < temp <= 25:
        temp_contrib = 0
    else:
        temp_contrib = -10
    
    # Vent
    if wind < 15:
        wind_contrib = 5
    elif wind < 25:
        wind_contrib = 0
    elif wind < 35:
        wind_contrib = -8
    else:
        wind_contrib = -15
    
    # Précipitations
    if precip == 0:
        precip_contrib = 5
    elif precip < 2:
        precip_contrib = 0
    elif precip < 5:
        precip_contrib = -5
    else:
        precip_contrib = -15
    
    weather_contrib = temp_contrib + wind_contrib + precip_contrib
    score += weather_contrib
    factors["weather"] = {
        "contribution": weather_contrib,
        "temperature": temp_contrib,
        "wind": wind_contrib,
        "precipitation": precip_contrib
    }
    
    # Normaliser
    score = max(0, min(100, score))
    
    # Déterminer le niveau
    if score >= 75:
        level = "excellent"
        icon = "🎯"
        summary = "Conditions excellentes pour la chasse"
    elif score >= 55:
        level = "good"
        icon = "✅"
        summary = "Bonnes conditions, activité attendue"
    elif score >= 35:
        level = "moderate"
        icon = "⚠️"
        summary = "Conditions moyennes, patience requise"
    else:
        level = "poor"
        icon = "❌"
        summary = "Conditions difficiles, envisagez reporter"
    
    return {
        "score": round(score, 1),
        "level": level,
        "icon": icon,
        "summary": summary,
        "factors": factors
    }


def generate_export_summary(
    lunar: Dict,
    pressure: Dict,
    weather: Dict,
    hunting_impact: Dict
) -> str:
    """Génère un résumé pour l'export PDF."""
    lines = [
        f"📍 Conditions actuelles - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"🌡️ Température: {weather.get('temperature_c', 'N/A')}°C",
        f"🌙 Lune: {lunar.get('phase_name_fr', 'N/A')} ({lunar.get('illumination_percent', 0):.0f}%)",
        f"📊 Pression: {pressure.get('current_hpa', 'N/A')} hPa ({pressure.get('trend', 'stable')})",
        "",
        f"🎯 Score de chasse: {hunting_impact.get('score', 50)}/100 ({hunting_impact.get('level', 'moderate')})",
        f"📝 {hunting_impact.get('summary', '')}"
    ]
    return "\n".join(lines)


# =============================================================================
# ENDPOINTS
# =============================================================================

@conditions_router.get(
    "/current",
    response_model=CurrentConditionsResponse,
    summary="Conditions actuelles pour la chasse",
    description="Récupère les conditions météo, lunaires, barométriques et leur impact sur la chasse."
)
async def get_current_conditions(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    use_cache: bool = Query(True, description="Utiliser le cache")
):
    """
    Endpoint principal pour le panneau "Conditions actuelles".
    
    Retourne:
    - Phase lunaire avec impact chasse
    - Pression barométrique avec tendance
    - Météo actuelle
    - Photopériode (lever/coucher)
    - Score d'impact global sur la chasse
    """
    request_id = f"cond_{uuid.uuid4().hex[:12]}"
    
    if not FETCHER_AVAILABLE or not behavior_weather_fetcher:
        raise HTTPException(
            status_code=503,
            detail="Weather fetcher not available"
        )
    
    try:
        # Fetch all environmental data
        all_data = await behavior_weather_fetcher.get_all_environmental_data(
            lat, lon, use_cache=use_cache
        )
        
        weather_data = all_data.get("weather", {})
        lunar_data = all_data.get("lunar", {})
        pressure_data = all_data.get("pressure_trend", {})
        photoperiod_data = all_data.get("photoperiod", {})
        
        # Build lunar condition
        lunar_impact = lunar_data.get("hunting_impact", {})
        lunar = LunarCondition(
            phase=lunar_data.get("phase", 0.5),
            phase_name=lunar_data.get("phase_name_fr", "Inconnue"),
            illumination_percent=round(lunar_data.get("illumination", 0.5) * 100, 1),
            is_waxing=lunar_data.get("is_waxing", True),
            is_full_moon=lunar_data.get("is_full_moon", False),
            is_new_moon=lunar_data.get("is_new_moon", False),
            days_to_next_event=lunar_data.get("next_event", {}).get("days_away", 7),
            next_event_name=lunar_data.get("next_event", {}).get("name_fr", ""),
            hunting_impact=lunar_impact.get("impact", "neutral"),
            hunting_description=lunar_impact.get("description", "")
        )
        
        # Build pressure condition
        trend = pressure_data.get("trend", "stable")
        pressure = PressureCondition(
            value_hpa=pressure_data.get("current_hpa", weather_data.get("pressure_hpa", 1013)),
            trend=trend,
            trend_icon=get_trend_icon(trend),
            change_6h=pressure_data.get("change_6h", 0),
            hunting_impact=pressure_data.get("hunting_impact", "neutral"),
            hunting_description=pressure_data.get("description", "")
        )
        
        # Build photoperiod condition
        sunrise = photoperiod_data.get("sunrise", "06:00")
        sunset = photoperiod_data.get("sunset", "18:00")
        
        # Extract time part if full datetime
        if "T" in str(sunrise):
            sunrise = str(sunrise).split("T")[1][:5]
        if "T" in str(sunset):
            sunset = str(sunset).split("T")[1][:5]
        
        photoperiod = PhotoperiodCondition(
            sunrise=sunrise,
            sunset=sunset,
            daylight_hours=photoperiod_data.get("daylight_hours", 12),
            golden_hour_morning=photoperiod_data.get("golden_hour_morning", "06:30"),
            golden_hour_evening=photoperiod_data.get("golden_hour_evening", "17:30"),
            optimal_hunting_windows=[
                {"start": sunrise, "end": photoperiod_data.get("golden_hour_morning", "07:00"), "type": "Aube"},
                {"start": photoperiod_data.get("golden_hour_evening", "17:00"), "end": sunset, "type": "Crépuscule"}
            ]
        )
        
        # Build weather condition
        weather_desc = weather_data.get("weather_description", "")
        weather = WeatherCondition(
            temperature_c=weather_data.get("temperature_c", 15),
            humidity_percent=weather_data.get("humidity_percent", 60),
            wind_speed_kmh=weather_data.get("wind_speed_kmh", 10),
            wind_direction=f"{weather_data.get('wind_direction_deg', 0)}°",
            cloud_cover_percent=weather_data.get("cloud_cover_percent", 50),
            precipitation_mm=weather_data.get("precipitation_mm", 0),
            weather_description=weather_desc,
            weather_icon=get_weather_icon(weather_data.get("weather_code", 0), weather_desc)
        )
        
        # Calculate hunting impact
        impact_data = calculate_hunting_impact(
            lunar_data, pressure_data, weather_data, photoperiod_data
        )
        
        hunting_impact = HuntingImpact(
            score=impact_data["score"],
            level=impact_data["level"],
            icon=impact_data["icon"],
            summary=impact_data["summary"],
            factors=impact_data["factors"]
        )
        
        # Generate export summary
        export_summary = generate_export_summary(
            lunar_data, pressure_data, weather_data, impact_data
        )
        
        # Determine cache status
        cache_status = "hit" if weather_data.get("from_cache", False) else "miss"
        
        return CurrentConditionsResponse(
            request_id=request_id,
            location={"lat": lat, "lon": lon},
            fetched_at=datetime.now(timezone.utc).isoformat(),
            data_source=f"Open-Meteo + BIONIC Algorithm ({weather_data.get('source', 'Unknown')})",
            cache_status=cache_status,
            lunar=lunar,
            pressure=pressure,
            photoperiod=photoperiod,
            weather=weather,
            hunting_impact=hunting_impact,
            exportable=True,
            export_summary=export_summary
        )
        
    except Exception as e:
        logger.error(f"Current conditions error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch current conditions: {str(e)}"
        )


@conditions_router.get(
    "/lunar",
    summary="Phase lunaire uniquement",
    description="Récupère uniquement les données de phase lunaire."
)
async def get_lunar_only():
    """Endpoint rapide pour la phase lunaire seule."""
    if not FETCHER_AVAILABLE or not behavior_weather_fetcher:
        raise HTTPException(status_code=503, detail="Fetcher not available")
    
    lunar_data = behavior_weather_fetcher.get_moon_phase()
    return lunar_data


@conditions_router.get(
    "/export-data",
    summary="Données pour export PDF",
    description="Retourne les données formatées pour l'export PDF."
)
async def get_export_data(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    """Retourne les données dans un format optimisé pour l'export PDF."""
    conditions = await get_current_conditions(lat, lon, use_cache=True)
    
    return {
        "title": "Conditions de Chasse - BIONIC™",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": conditions.location,
        "sections": [
            {
                "title": "Phase Lunaire",
                "icon": "🌙",
                "content": [
                    f"Phase: {conditions.lunar.phase_name}",
                    f"Illumination: {conditions.lunar.illumination_percent}%",
                    f"Prochain événement: {conditions.lunar.next_event_name} dans {conditions.lunar.days_to_next_event:.0f} jours"
                ]
            },
            {
                "title": "Pression Barométrique",
                "icon": "📊",
                "content": [
                    f"Valeur: {conditions.pressure.value_hpa} hPa",
                    f"Tendance: {conditions.pressure.trend_icon} {conditions.pressure.trend}",
                    f"Impact: {conditions.pressure.hunting_description}"
                ]
            },
            {
                "title": "Météo",
                "icon": conditions.weather.weather_icon,
                "content": [
                    f"Température: {conditions.weather.temperature_c}°C",
                    f"Vent: {conditions.weather.wind_speed_kmh} km/h",
                    f"Conditions: {conditions.weather.weather_description}"
                ]
            },
            {
                "title": "Photopériode",
                "icon": "☀️",
                "content": [
                    f"Lever: {conditions.photoperiod.sunrise}",
                    f"Coucher: {conditions.photoperiod.sunset}",
                    f"Durée du jour: {conditions.photoperiod.daylight_hours:.1f}h"
                ]
            }
        ],
        "hunting_score": {
            "value": conditions.hunting_impact.score,
            "level": conditions.hunting_impact.level,
            "icon": conditions.hunting_impact.icon,
            "summary": conditions.hunting_impact.summary
        },
        "raw_summary": conditions.export_summary
    }


# Log initialization
logger.info("BIONIC™ Current Conditions Router initialized (v1.0.0)")
