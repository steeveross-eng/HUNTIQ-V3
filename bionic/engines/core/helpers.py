"""
BIONIC™ Engine - Helper Functions
==================================
Fonctions utilitaires partagées par tous les modules.
"""

from datetime import datetime
from typing import Dict, List, Optional
import random
import math

from .configs import SeasonType, SpeciesType, SEASON_FACTORS


def get_current_season() -> SeasonType:
    """
    Détermine la saison actuelle basée sur le mois.
    
    Returns:
        SeasonType: La saison actuelle
    """
    month = datetime.now().month
    if month in [3, 4, 5]:
        return SeasonType.SPRING
    elif month in [6, 7, 8]:
        return SeasonType.SUMMER
    elif month in [9, 10, 11]:
        return SeasonType.FALL
    else:
        return SeasonType.WINTER


def get_season_factor(species: SpeciesType, season: SeasonType) -> float:
    """
    Obtient le facteur d'ajustement saisonnier pour une espèce.
    
    Args:
        species: L'espèce cible
        season: La saison actuelle
        
    Returns:
        float: Facteur multiplicatif (0.1 à 1.0)
    """
    factors = SEASON_FACTORS.get(species, {})
    return factors.get(season.value, 0.8)


def get_rating(score: float) -> str:
    """
    Convertit un score numérique en notation textuelle.
    
    Args:
        score: Score de 0 à 100
        
    Returns:
        str: Notation ("Excellent", "Très bon", etc.)
    """
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Très bon"
    elif score >= 55:
        return "Bon"
    elif score >= 40:
        return "Moyen"
    elif score >= 25:
        return "Faible"
    else:
        return "Très faible"


def simulate_factor_value(factor: str, lat: float, lon: float, seed: int = None) -> float:
    """
    Simule une valeur réaliste pour un facteur basée sur la localisation.
    
    Args:
        factor: Nom du facteur
        lat: Latitude
        lon: Longitude
        seed: Graine pour la reproductibilité
        
    Returns:
        float: Valeur simulée (0-100)
    """
    if seed:
        random.seed(seed)
    
    # Valeur de base avec variation basée sur la localisation
    base = 50 + (lat % 10) * 2 + (lon % 10) * 1.5
    noise = random.gauss(0, 10)
    value = max(0, min(100, base + noise))
    
    return round(value, 1)


def generate_hotspots(lat: float, lon: float, count: int = 5) -> List[Dict]:
    """
    Génère des points chauds de présence faunique.
    
    Args:
        lat: Latitude du centre
        lon: Longitude du centre
        count: Nombre de hotspots à générer
        
    Returns:
        List[Dict]: Liste de hotspots avec coordonnées et probabilités
    """
    hotspots = []
    for i in range(count):
        offset_lat = random.uniform(-0.05, 0.05)
        offset_lon = random.uniform(-0.05, 0.05)
        hotspots.append({
            "id": f"hotspot_{i+1}",
            "latitude": round(lat + offset_lat, 6),
            "longitude": round(lon + offset_lon, 6),
            "probability": round(random.uniform(0.6, 0.95), 2),
            "type": random.choice(["feeding", "bedding", "travel", "water"]),
            "confidence": round(random.uniform(0.7, 0.95), 2)
        })
    return sorted(hotspots, key=lambda x: x["probability"], reverse=True)


def aspect_to_direction(aspect: float) -> str:
    """
    Convertit un angle d'aspect en direction cardinale.
    
    Args:
        aspect: Angle en degrés (0-360)
        
    Returns:
        str: Direction cardinale (N, NE, E, SE, S, SW, W, NW)
    """
    if aspect is None:
        return "N/A"
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int((aspect + 22.5) / 45) % 8
    return directions[index]


def interpret_ndvi(ndvi: float) -> str:
    """
    Interprète une valeur NDVI en texte descriptif.
    
    Args:
        ndvi: Valeur NDVI (-1 à 1)
        
    Returns:
        str: Description de la végétation
    """
    if ndvi < 0:
        return "Eau ou sol nu"
    elif ndvi < 0.2:
        return "Végétation clairsemée"
    elif ndvi < 0.4:
        return "Végétation modérée"
    elif ndvi < 0.6:
        return "Végétation dense"
    else:
        return "Végétation très dense"


def calculate_weighted_score(
    values: Dict[str, float],
    weights: Dict[str, float]
) -> float:
    """
    Calcule un score pondéré à partir de valeurs et poids.
    
    Args:
        values: Dictionnaire de valeurs par facteur
        weights: Dictionnaire de poids par facteur
        
    Returns:
        float: Score pondéré (0-100)
    """
    weighted_sum = 0
    total_weight = 0
    
    for factor, weight in weights.items():
        if factor in values:
            weighted_sum += values[factor] * weight
            total_weight += weight
    
    if total_weight == 0:
        return 50.0
    
    return round(weighted_sum / total_weight, 1)


def clamp(value: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Limite une valeur à un intervalle.
    
    Args:
        value: Valeur à limiter
        min_val: Valeur minimale
        max_val: Valeur maximale
        
    Returns:
        float: Valeur limitée
    """
    return max(min_val, min(max_val, value))


def format_weather_for_ai(weather: Optional[Dict]) -> str:
    """
    Formate les données météo pour une requête IA.
    
    Args:
        weather: Dictionnaire de données météo
        
    Returns:
        str: Texte formaté pour prompt IA
    """
    if not weather:
        return "Non disponible"
    
    lines = []
    if "temperature" in weather:
        lines.append(f"- Température: {weather['temperature']}°C")
    if "humidity" in weather:
        lines.append(f"- Humidité: {weather['humidity']}%")
    if "wind_speed" in weather:
        lines.append(f"- Vent: {weather['wind_speed']} km/h")
    if "precipitation_probability" in weather:
        lines.append(f"- Précipitations: {weather['precipitation_probability']}%")
    if "description" in weather:
        lines.append(f"- Conditions: {weather['description']}")
    
    return "\n".join(lines) if lines else "Données partielles"
