"""Weather Engine Models - CORE

Pydantic models for weather-related hunting analysis.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone


class WeatherCondition(BaseModel):
    """Current weather conditions"""
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(ge=0, description="Wind speed in km/h")
    wind_direction: str = Field(description="Cardinal direction")
    pressure: float = Field(description="Atmospheric pressure in hPa")
    precipitation: float = Field(ge=0, description="Precipitation in mm")
    condition: str = Field(description="Weather condition text")
    icon: Optional[str] = None


class HuntingForecast(BaseModel):
    """Hunting conditions forecast"""
    date: datetime
    overall_score: float = Field(ge=0, le=10, description="Overall hunting score")
    deer_activity: Literal["low", "moderate", "high", "peak"] = "moderate"
    best_times: List[str] = Field(default_factory=list, description="Best hunting times")
    wind_advice: str = ""
    pressure_trend: Literal["rising", "stable", "falling"] = "stable"
    recommendations: List[str] = Field(default_factory=list)


class WeatherRequest(BaseModel):
    """Request for weather data"""
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    days: int = Field(default=3, ge=1, le=7)


class MoonPhase(BaseModel):
    """Moon phase information"""
    phase: Literal["new", "waxing_crescent", "first_quarter", "waxing_gibbous", 
                   "full", "waning_gibbous", "third_quarter", "waning_crescent"]
    illumination: float = Field(ge=0, le=100)
    rise_time: Optional[str] = None
    set_time: Optional[str] = None
    hunting_impact: str = ""
