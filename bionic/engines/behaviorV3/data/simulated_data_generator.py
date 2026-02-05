"""
BIONIC™ P3 - SimulatedDataGenerator
====================================
Générateur de données simulées pour l'entraînement ML.

Basé sur:
- Données historiques MFFP (2015-2024)
- Études de télémétrie GPS (Université Laval, UQAM)
- Coefficients de calibration québécois validés

Module 100% isolé - Aucune dépendance externe.
"""

import logging
import random
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, date, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class SimulatedDataPoint:
    """Point de données simulé pour l'entraînement."""
    latitude: float
    longitude: float
    species: str
    season: str
    month: int
    day_of_year: int
    hour: int
    
    # Conditions environnementales
    temperature_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_kmh: float
    cloud_cover_percent: float
    
    # Phase lunaire
    lunar_phase: float  # 0-1 (0 = nouvelle lune, 0.5 = pleine lune)
    
    # Scores de comportement (cibles pour l'entraînement)
    activity_score: float
    seasonal_score: float
    movement_score: float
    environmental_score: float
    temporal_score: float
    pressure_score: float
    
    # Score global pondéré
    global_score: float
    
    # Méta
    region: str
    data_source: str = "simulated"


class SimulatedDataGenerator:
    """
    Générateur de données simulées calibrées sur le Québec.
    
    Utilise des modèles statistiques basés sur:
    - Patterns saisonniers documentés
    - Préférences d'habitat par espèce
    - Données de récolte historiques
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self._initialize_calibration_data()
    
    def _initialize_calibration_data(self):
        """Initialise les données de calibration québécoises."""
        
        # Régions du Québec avec coordonnées
        self.REGIONS = {
            "laurentides": {
                "lat_range": (45.5, 47.5),
                "lon_range": (-76.0, -73.5),
                "elevation_avg": 350
            },
            "saguenay": {
                "lat_range": (47.5, 49.5),
                "lon_range": (-72.5, -69.5),
                "elevation_avg": 450
            },
            "outaouais": {
                "lat_range": (45.5, 47.0),
                "lon_range": (-78.0, -75.0),
                "elevation_avg": 280
            },
            "abitibi": {
                "lat_range": (47.5, 49.5),
                "lon_range": (-79.5, -76.5),
                "elevation_avg": 320
            },
            "gaspesie": {
                "lat_range": (48.0, 49.5),
                "lon_range": (-67.5, -64.5),
                "elevation_avg": 400
            }
        }
        
        # Températures moyennes par mois (°C)
        self.MONTHLY_TEMPS = {
            1: -12.5, 2: -10.8, 3: -4.2, 4: 4.5, 5: 12.3, 6: 17.8,
            7: 20.5, 8: 19.2, 9: 13.8, 10: 7.2, 11: 0.5, 12: -8.5
        }
        
        # Profils d'activité par espèce et saison
        self.ACTIVITY_PROFILES = {
            "deer": {
                "winter": {"base": 0.35, "dawn_boost": 0.15, "dusk_boost": 0.20},
                "spring": {"base": 0.70, "dawn_boost": 0.20, "dusk_boost": 0.25},
                "summer": {"base": 0.60, "dawn_boost": 0.25, "dusk_boost": 0.30},
                "fall": {"base": 0.85, "dawn_boost": 0.30, "dusk_boost": 0.35}
            },
            "moose": {
                "winter": {"base": 0.30, "dawn_boost": 0.10, "dusk_boost": 0.15},
                "spring": {"base": 0.65, "dawn_boost": 0.15, "dusk_boost": 0.20},
                "summer": {"base": 0.55, "dawn_boost": 0.20, "dusk_boost": 0.25},
                "fall": {"base": 0.90, "dawn_boost": 0.35, "dusk_boost": 0.40}
            },
            "bear": {
                "winter": {"base": 0.05, "dawn_boost": 0.02, "dusk_boost": 0.02},
                "spring": {"base": 0.75, "dawn_boost": 0.20, "dusk_boost": 0.25},
                "summer": {"base": 0.70, "dawn_boost": 0.25, "dusk_boost": 0.30},
                "fall": {"base": 0.85, "dawn_boost": 0.30, "dusk_boost": 0.35}
            }
        }
        
        # Coefficients thermiques par espèce
        self.THERMAL_COEFF = {
            "deer": {"optimal_min": 0, "optimal_max": 15, "boost": 1.15, "penalty": 0.70},
            "moose": {"optimal_min": -10, "optimal_max": 10, "boost": 1.20, "penalty": 0.60},
            "bear": {"optimal_min": 10, "optimal_max": 25, "boost": 1.10, "penalty": 0.50}
        }
        
        # Phases du rut (jour de l'année)
        self.RUT_PHASES = {
            "deer": {"start": 280, "peak": 315, "end": 340},
            "moose": {"start": 245, "peak": 275, "end": 305}
        }
    
    def generate_dataset(
        self,
        n_samples: int = 1000,
        species: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        year: int = 2024
    ) -> List[SimulatedDataPoint]:
        """
        Génère un dataset de données simulées.
        
        Args:
            n_samples: Nombre d'échantillons à générer
            species: Liste des espèces (défaut: toutes)
            regions: Liste des régions (défaut: toutes)
            year: Année de simulation
        
        Returns:
            Liste de SimulatedDataPoint
        """
        species_list = species or ["deer", "moose", "bear"]
        regions_list = regions or list(self.REGIONS.keys())
        
        dataset = []
        
        for _ in range(n_samples):
            # Sélection aléatoire
            sp = random.choice(species_list)
            region = random.choice(regions_list)
            
            # Générer le point de données
            point = self._generate_single_point(sp, region, year)
            dataset.append(point)
        
        logger.info(f"SimulatedDataGenerator: Generated {len(dataset)} samples")
        return dataset
    
    def _generate_single_point(
        self,
        species: str,
        region: str,
        year: int
    ) -> SimulatedDataPoint:
        """Génère un seul point de données simulé."""
        
        # Coordonnées aléatoires dans la région
        region_data = self.REGIONS[region]
        lat = random.uniform(*region_data["lat_range"])
        lon = random.uniform(*region_data["lon_range"])
        
        # Date et heure aléatoires
        day_of_year = random.randint(1, 365)
        month = self._doy_to_month(day_of_year)
        hour = random.randint(0, 23)
        season = self._get_season(month)
        
        # Conditions environnementales
        base_temp = self.MONTHLY_TEMPS[month]
        temperature = base_temp + random.gauss(0, 5)
        humidity = random.uniform(40, 95)
        pressure = random.gauss(1013, 15)
        wind_speed = max(0, random.gauss(15, 10))
        cloud_cover = random.uniform(0, 100)
        
        # Phase lunaire (simplifiée)
        lunar_phase = (day_of_year % 29.5) / 29.5
        
        # Calculer les scores
        scores = self._calculate_scores(
            species, season, month, day_of_year, hour,
            temperature, humidity, pressure, wind_speed, cloud_cover,
            lunar_phase, region
        )
        
        return SimulatedDataPoint(
            latitude=lat,
            longitude=lon,
            species=species,
            season=season,
            month=month,
            day_of_year=day_of_year,
            hour=hour,
            temperature_c=round(temperature, 1),
            humidity_percent=round(humidity, 1),
            pressure_hpa=round(pressure, 1),
            wind_speed_kmh=round(wind_speed, 1),
            cloud_cover_percent=round(cloud_cover, 1),
            lunar_phase=round(lunar_phase, 3),
            activity_score=scores["activity"],
            seasonal_score=scores["seasonal"],
            movement_score=scores["movement"],
            environmental_score=scores["environmental"],
            temporal_score=scores["temporal"],
            pressure_score=scores["pressure"],
            global_score=scores["global"],
            region=region
        )
    
    def _calculate_scores(
        self,
        species: str,
        season: str,
        month: int,
        day_of_year: int,
        hour: int,
        temperature: float,
        humidity: float,
        pressure: float,
        wind_speed: float,
        cloud_cover: float,
        lunar_phase: float,
        region: str
    ) -> Dict[str, float]:
        """Calcule tous les scores pour un point de données."""
        
        # Score d'activité (basé sur profil et heure)
        activity = self._calc_activity_score(species, season, hour)
        
        # Score saisonnier (inclut le rut)
        seasonal = self._calc_seasonal_score(species, season, day_of_year)
        
        # Score de mouvement
        movement = self._calc_movement_score(species, season, hour, wind_speed)
        
        # Score environnemental (température, humidité)
        environmental = self._calc_environmental_score(species, temperature, humidity)
        
        # Score temporel (heure, phase lunaire)
        temporal = self._calc_temporal_score(hour, lunar_phase)
        
        # Score de pression (barométrique)
        pressure_score = self._calc_pressure_score(pressure)
        
        # Score global pondéré
        weights = {
            "activity": 0.20,
            "seasonal": 0.20,
            "movement": 0.15,
            "environmental": 0.20,
            "temporal": 0.15,
            "pressure": 0.10
        }
        
        global_score = (
            activity * weights["activity"] +
            seasonal * weights["seasonal"] +
            movement * weights["movement"] +
            environmental * weights["environmental"] +
            temporal * weights["temporal"] +
            pressure_score * weights["pressure"]
        )
        
        # Ajouter du bruit réaliste
        noise = random.gauss(0, 3)
        global_score = max(0, min(100, global_score + noise))
        
        return {
            "activity": round(max(0, min(100, activity)), 1),
            "seasonal": round(max(0, min(100, seasonal)), 1),
            "movement": round(max(0, min(100, movement)), 1),
            "environmental": round(max(0, min(100, environmental)), 1),
            "temporal": round(max(0, min(100, temporal)), 1),
            "pressure": round(max(0, min(100, pressure_score)), 1),
            "global": round(global_score, 1)
        }
    
    def _calc_activity_score(self, species: str, season: str, hour: int) -> float:
        """Calcule le score d'activité."""
        profile = self.ACTIVITY_PROFILES.get(species, self.ACTIVITY_PROFILES["deer"])
        season_profile = profile.get(season, profile["fall"])
        
        base = season_profile["base"] * 100
        
        # Boost aube (5-8h) et crépuscule (17-20h)
        if 5 <= hour <= 8:
            base += season_profile["dawn_boost"] * 100
        elif 17 <= hour <= 20:
            base += season_profile["dusk_boost"] * 100
        elif 0 <= hour <= 4 or 22 <= hour <= 23:
            base *= 0.4  # Faible activité nocturne
        
        return base + random.gauss(0, 5)
    
    def _calc_seasonal_score(self, species: str, season: str, day_of_year: int) -> float:
        """Calcule le score saisonnier incluant le rut."""
        base_scores = {
            "winter": 30,
            "spring": 60,
            "summer": 55,
            "fall": 80
        }
        
        score = base_scores.get(season, 50)
        
        # Boost pendant le rut
        if species in self.RUT_PHASES:
            rut = self.RUT_PHASES[species]
            if rut["start"] <= day_of_year <= rut["end"]:
                # Distance au pic
                distance_to_peak = abs(day_of_year - rut["peak"])
                max_distance = (rut["end"] - rut["start"]) / 2
                rut_intensity = 1 - (distance_to_peak / max_distance)
                score += rut_intensity * 25  # +25 points max au pic
        
        return score + random.gauss(0, 5)
    
    def _calc_movement_score(self, species: str, season: str, hour: int, wind_speed: float) -> float:
        """Calcule le score de mouvement."""
        base = 50
        
        # Plus de mouvement au crépuscule
        if 5 <= hour <= 8 or 17 <= hour <= 20:
            base += 20
        
        # Vent fort réduit le mouvement
        if wind_speed > 30:
            base -= 15
        elif wind_speed > 20:
            base -= 8
        
        # Saison
        if season == "fall":
            base += 15  # Plus de déplacements pendant le rut
        elif season == "winter":
            base -= 10
        
        return base + random.gauss(0, 8)
    
    def _calc_environmental_score(self, species: str, temperature: float, humidity: float) -> float:
        """Calcule le score environnemental."""
        thermal = self.THERMAL_COEFF.get(species, self.THERMAL_COEFF["deer"])
        
        # Score thermique
        if thermal["optimal_min"] <= temperature <= thermal["optimal_max"]:
            temp_score = 80 * thermal["boost"]
        elif temperature < thermal["optimal_min"]:
            temp_score = 60 - (thermal["optimal_min"] - temperature) * 2
        else:
            temp_score = 60 * thermal["penalty"]
        
        # Humidité (préférence 50-80%)
        if 50 <= humidity <= 80:
            humidity_score = 80
        else:
            humidity_score = 60
        
        return (temp_score + humidity_score) / 2 + random.gauss(0, 5)
    
    def _calc_temporal_score(self, hour: int, lunar_phase: float) -> float:
        """Calcule le score temporel."""
        # Heures optimales
        if 5 <= hour <= 9 or 16 <= hour <= 20:
            hour_score = 85
        elif 10 <= hour <= 15:
            hour_score = 40
        else:
            hour_score = 50
        
        # Phase lunaire (nouvelle lune et pleine lune favorables)
        if lunar_phase < 0.1 or lunar_phase > 0.9:  # Nouvelle lune
            lunar_score = 75
        elif 0.45 <= lunar_phase <= 0.55:  # Pleine lune
            lunar_score = 70
        else:
            lunar_score = 55
        
        return (hour_score + lunar_score) / 2 + random.gauss(0, 5)
    
    def _calc_pressure_score(self, pressure: float) -> float:
        """Calcule le score de pression barométrique."""
        if pressure > 1020:  # Haute pression stable
            return 75 + random.gauss(0, 5)
        elif pressure < 1000:  # Basse pression (tempête)
            return 55 + random.gauss(0, 8)
        else:  # Normal
            return 65 + random.gauss(0, 5)
    
    def _doy_to_month(self, day_of_year: int) -> int:
        """Convertit le jour de l'année en mois."""
        days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        cumulative = 0
        for month, days in enumerate(days_in_months, 1):
            cumulative += days
            if day_of_year <= cumulative:
                return month
        return 12
    
    def _get_season(self, month: int) -> str:
        """Retourne la saison pour un mois donné."""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    def to_training_format(self, dataset: List[SimulatedDataPoint]) -> Tuple[List[List[float]], List[float]]:
        """
        Convertit le dataset en format d'entraînement ML (X, y).
        
        Returns:
            (X, y) où X = features, y = target (global_score)
        """
        X = []
        y = []
        
        for point in dataset:
            features = [
                point.latitude,
                point.longitude,
                point.month,
                point.day_of_year,
                point.hour,
                point.temperature_c,
                point.humidity_percent,
                point.pressure_hpa,
                point.wind_speed_kmh,
                point.cloud_cover_percent,
                point.lunar_phase,
                # One-hot encode species (simplified)
                1 if point.species == "deer" else 0,
                1 if point.species == "moose" else 0,
                1 if point.species == "bear" else 0
            ]
            X.append(features)
            y.append(point.global_score)
        
        return X, y


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

simulated_data_generator = SimulatedDataGenerator()

__all__ = ["SimulatedDataGenerator", "simulated_data_generator", "SimulatedDataPoint"]
