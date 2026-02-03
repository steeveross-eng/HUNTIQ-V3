"""
BIONIC™ Environment Engine - Data Combiner

Combine les données de tous les moteurs d'analyse pour produire
une vue unifiée du territoire.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio


class EnvironmentCombiner:
    """
    Combine les données des différents moteurs BIONIC™.
    """
    
    def __init__(self):
        self.engines_status = {
            "hydro": True,
            "sentinel": True,
            "sigeom": True,
            "weather": True,
            "nutrition": True
        }
        
        # Poids par défaut pour chaque composant
        self.default_weights = {
            "vegetation": 0.35,   # SentinelEngine
            "hydrology": 0.25,   # HydroEngine
            "geology": 0.15,     # SigeomEngine
            "weather": 0.15,     # OpenWeatherMap
            "nutrition": 0.10    # NutritionEngine
        }
        
        # Poids ajustés par espèce
        self.species_weight_adjustments = {
            "deer": {
                "vegetation": 0.35,
                "hydrology": 0.25,
                "geology": 0.15,
                "weather": 0.15,
                "nutrition": 0.10
            },
            "moose": {
                "vegetation": 0.30,
                "hydrology": 0.35,  # L'orignal aime les zones humides
                "geology": 0.10,
                "weather": 0.15,
                "nutrition": 0.10
            },
            "bear": {
                "vegetation": 0.25,
                "hydrology": 0.20,
                "geology": 0.10,
                "weather": 0.15,
                "nutrition": 0.30  # L'ours dépend beaucoup de la nourriture
            },
            "elk": {
                "vegetation": 0.40,  # Le wapiti préfère les prairies
                "hydrology": 0.20,
                "geology": 0.15,
                "weather": 0.15,
                "nutrition": 0.10
            },
            "waterfowl": {
                "vegetation": 0.15,
                "hydrology": 0.50,  # Oiseaux aquatiques
                "geology": 0.05,
                "weather": 0.25,
                "nutrition": 0.05
            }
        }
    
    def get_weights_for_species(self, species: str) -> Dict[str, float]:
        """
        Retourne les poids ajustés pour une espèce donnée.
        """
        return self.species_weight_adjustments.get(
            species, 
            self.default_weights
        )
    
    def combine_analysis_data(
        self,
        hydro_data: Optional[Dict] = None,
        sentinel_data: Optional[Dict] = None,
        sigeom_data: Optional[Dict] = None,
        weather_data: Optional[Dict] = None,
        nutrition_data: Optional[Dict] = None,
        target_species: str = "deer"
    ) -> Dict[str, Any]:
        """
        Combine les données d'analyse de tous les moteurs.
        
        Args:
            hydro_data: Résultats du HydroEngine
            sentinel_data: Résultats du SentinelEngine
            sigeom_data: Résultats du SigeomEngine
            weather_data: Données météo OpenWeatherMap
            nutrition_data: Données du NutritionEngine
            target_species: Espèce cible
            
        Returns:
            Dict avec toutes les données combinées et normalisées
        """
        weights = self.get_weights_for_species(target_species)
        
        combined = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "target_species": target_species,
                "weights_used": weights,
                "data_sources_available": {
                    "hydro": hydro_data is not None,
                    "sentinel": sentinel_data is not None,
                    "sigeom": sigeom_data is not None,
                    "weather": weather_data is not None,
                    "nutrition": nutrition_data is not None
                }
            },
            "components": {},
            "scores": {},
            "recommendations": []
        }
        
        # Traiter les données hydrologiques
        if hydro_data:
            combined["components"]["hydrology"] = self._process_hydro_data(hydro_data)
            combined["scores"]["hydrology"] = combined["components"]["hydrology"].get("score", 0)
        else:
            combined["scores"]["hydrology"] = 50  # Score neutre par défaut
            
        # Traiter les données de végétation
        if sentinel_data:
            combined["components"]["vegetation"] = self._process_sentinel_data(sentinel_data)
            combined["scores"]["vegetation"] = combined["components"]["vegetation"].get("score", 0)
        else:
            combined["scores"]["vegetation"] = 50
            
        # Traiter les données géologiques
        if sigeom_data:
            combined["components"]["geology"] = self._process_sigeom_data(sigeom_data)
            combined["scores"]["geology"] = combined["components"]["geology"].get("score", 0)
        else:
            combined["scores"]["geology"] = 50
            
        # Traiter les données météo
        if weather_data:
            combined["components"]["weather"] = self._process_weather_data(weather_data, target_species)
            combined["scores"]["weather"] = combined["components"]["weather"].get("score", 0)
        else:
            combined["scores"]["weather"] = 50
            
        # Traiter les données nutritionnelles
        if nutrition_data:
            combined["components"]["nutrition"] = self._process_nutrition_data(nutrition_data)
            combined["scores"]["nutrition"] = combined["components"]["nutrition"].get("score", 0)
        else:
            combined["scores"]["nutrition"] = 50
        
        return combined
    
    def _process_hydro_data(self, data: Dict) -> Dict:
        """Normalise les données hydrologiques."""
        score = 50  # Défaut
        
        if "analysis" in data:
            analysis = data["analysis"]
            # Extraire le score global si disponible
            if "overall_score" in analysis:
                score = analysis["overall_score"]
            elif "hydrology_score" in analysis:
                score = analysis["hydrology_score"]
            elif "scores" in analysis:
                scores = analysis["scores"]
                if scores:
                    score = sum(scores.values()) / len(scores)
        
        return {
            "score": min(100, max(0, score)),
            "raw_data": data,
            "features_detected": {
                "rivers": data.get("rivers_count", 0),
                "lakes": data.get("lakes_count", 0),
                "wetlands": data.get("wetlands_count", 0)
            }
        }
    
    def _process_sentinel_data(self, data: Dict) -> Dict:
        """Normalise les données de végétation."""
        score = 50
        
        if "vegetation_score" in data:
            score = data["vegetation_score"]
        elif "hunting_score" in data:
            score = data["hunting_score"]
        elif "analysis" in data and "score" in data["analysis"]:
            score = data["analysis"]["score"]
        elif "ndvi" in data:
            # Convertir NDVI en score (0-1 -> 0-100)
            ndvi = data["ndvi"]
            if -1 <= ndvi <= 1:
                score = (ndvi + 1) * 50
        
        return {
            "score": min(100, max(0, score)),
            "raw_data": data,
            "indices": {
                "ndvi": data.get("ndvi"),
                "evi": data.get("evi"),
                "habitat_type": data.get("habitat_type", "unknown")
            }
        }
    
    def _process_sigeom_data(self, data: Dict) -> Dict:
        """Normalise les données géologiques."""
        score = 50
        
        if "geology_score" in data:
            score = data["geology_score"]
        elif "hunting_score" in data:
            score = data["hunting_score"]
        elif "analysis" in data:
            analysis = data["analysis"]
            if "score" in analysis:
                score = analysis["score"]
        
        return {
            "score": min(100, max(0, score)),
            "raw_data": data,
            "features": {
                "province": data.get("geological_province", "unknown"),
                "deposit_type": data.get("surficial_deposit", "unknown"),
                "terrain_quality": data.get("terrain_quality", "moderate")
            }
        }
    
    def _process_weather_data(self, data: Dict, species: str) -> Dict:
        """Normalise les données météo et calcule un score de chasse."""
        score = 50
        
        # Facteurs météo favorables/défavorables selon l'espèce
        if "main" in data:
            temp = data["main"].get("temp", 15)  # Celsius
            humidity = data["main"].get("humidity", 50)
            
            # Score basé sur la température
            if species in ["deer", "moose", "elk"]:
                # Ces animaux sont plus actifs par temps frais
                if 0 <= temp <= 10:
                    temp_score = 90
                elif 10 < temp <= 20:
                    temp_score = 70
                elif -10 <= temp < 0:
                    temp_score = 60
                else:
                    temp_score = 40
            elif species == "bear":
                # L'ours est actif par temps doux
                if 10 <= temp <= 25:
                    temp_score = 85
                else:
                    temp_score = 50
            else:
                temp_score = 70
                
            # Score basé sur l'humidité
            if 40 <= humidity <= 70:
                humidity_score = 80
            else:
                humidity_score = 60
                
            score = (temp_score * 0.6) + (humidity_score * 0.4)
        
        # Pénalité pour conditions extrêmes
        if "weather" in data:
            weather = data["weather"]
            if isinstance(weather, list) and weather:
                condition = weather[0].get("main", "").lower()
                if condition in ["thunderstorm", "storm"]:
                    score *= 0.3
                elif condition in ["rain", "drizzle"]:
                    score *= 0.7
                elif condition in ["snow"]:
                    score *= 0.8
        
        return {
            "score": min(100, max(0, score)),
            "raw_data": data,
            "conditions": {
                "temperature": data.get("main", {}).get("temp"),
                "humidity": data.get("main", {}).get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "description": data.get("weather", [{}])[0].get("description", "unknown") if data.get("weather") else "unknown"
            }
        }
    
    def _process_nutrition_data(self, data: Dict) -> Dict:
        """Normalise les données nutritionnelles."""
        score = 50
        
        if "nutrition_score" in data:
            score = data["nutrition_score"]
        elif "food_availability" in data:
            score = data["food_availability"]
        
        return {
            "score": min(100, max(0, score)),
            "raw_data": data,
            "food_sources": data.get("food_sources", [])
        }


# Instance singleton
environment_combiner = EnvironmentCombiner()
