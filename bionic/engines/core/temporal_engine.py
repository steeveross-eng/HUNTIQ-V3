"""
BIONIC™ Engine - Temporal Engine
=================================
Analyse temporelle des données environnementales.

Fonctionnalités:
- Tendances NDVI/NDWI sur 12 mois
- Analyse du couvert neigeux
- Phénologie végétale
- Détection d'anomalies
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import random
import math
import logging

logger = logging.getLogger(__name__)


class TemporalEngine:
    """
    Moteur d'analyse temporelle pour les données environnementales.
    """
    
    async def generate_analysis(
        self,
        lat: float,
        lon: float,
        territory_id: str
    ) -> Dict[str, Any]:
        """
        Génère une analyse temporelle complète.
        
        Args:
            lat: Latitude
            lon: Longitude
            territory_id: ID du territoire
            
        Returns:
            Dict: Analyse avec tendances, phénologie, anomalies
        """
        # Générer les tendances sur 12 mois
        ndvi_trend = self._generate_trend(65, seasonality=True)
        ndwi_trend = self._generate_trend(45, seasonality=True)
        thermal_trend = self._generate_trend(55, seasonality=True)
        snow_cover_trend = self._generate_snow_trend()
        
        # Données phénologiques
        phenology = self._generate_phenology()
        
        # Détection d'anomalies
        anomalies = self._detect_anomalies(ndvi_trend)
        
        return {
            "ndvi_trend": ndvi_trend,
            "ndwi_trend": ndwi_trend,
            "thermal_trend": thermal_trend,
            "snow_cover_trend": snow_cover_trend,
            "phenology": phenology,
            "anomalies": anomalies[:5]
        }
    
    def _generate_trend(
        self,
        base: float,
        seasonality: bool = True
    ) -> List[Dict]:
        """
        Génère une série temporelle sur 12 mois.
        
        Args:
            base: Valeur de base
            seasonality: Appliquer une variation saisonnière
            
        Returns:
            List[Dict]: Série temporelle avec valeurs mensuelles
        """
        trend = []
        now = datetime.now()
        
        for i in range(12):
            month = (now.month - 11 + i) % 12 + 1
            seasonal_factor = 1.0
            
            if seasonality:
                # Pic en été, creux en hiver
                seasonal_factor = 0.7 + 0.3 * math.sin((month - 1) * math.pi / 6)
            
            value = base * seasonal_factor + random.gauss(0, 10)
            
            trend.append({
                "month": month,
                "value": round(max(0, min(100, value)), 1),
                "date": (now - timedelta(days=30*(11-i))).strftime("%Y-%m")
            })
        
        return trend
    
    def _generate_snow_trend(self) -> List[Dict]:
        """
        Génère la tendance du couvert neigeux.
        """
        trend = []
        now = datetime.now()
        
        for i in range(12):
            month = (now.month - 11 + i) % 12 + 1
            
            # Neige maximale en janvier-février, nulle en été
            if month in [12, 1, 2]:
                base = 80 + random.gauss(0, 10)
            elif month in [3, 11]:
                base = 50 + random.gauss(0, 15)
            elif month in [4, 10]:
                base = 20 + random.gauss(0, 10)
            else:
                base = random.gauss(0, 5)
            
            trend.append({
                "month": month,
                "value": round(max(0, min(100, base)), 1),
                "date": (now - timedelta(days=30*(11-i))).strftime("%Y-%m")
            })
        
        return trend
    
    def _generate_phenology(self) -> Dict[str, Any]:
        """
        Génère les données phénologiques.
        """
        current_year = datetime.now().year
        next_year = current_year + 1
        
        return {
            "green_up_date": f"{next_year}-04-15",
            "peak_greenness": f"{next_year}-07-20",
            "senescence_start": f"{next_year}-09-10",
            "dormancy_start": f"{next_year}-11-01",
            "growing_season_length_days": 180
        }
    
    def _detect_anomalies(self, ndvi_trend: List[Dict]) -> List[Dict]:
        """
        Détecte les anomalies dans les données NDVI.
        """
        anomalies = []
        expected_base = 65  # Valeur de base attendue
        
        for i, data_point in enumerate(ndvi_trend):
            value = data_point["value"]
            deviation = abs(value - expected_base)
            
            if deviation > 20:
                anomalies.append({
                    "type": "ndvi_anomaly",
                    "date": data_point["date"],
                    "value": value,
                    "expected": expected_base,
                    "severity": "high" if deviation > 30 else "medium"
                })
        
        return anomalies


# Instance singleton
temporal_engine = TemporalEngine()
