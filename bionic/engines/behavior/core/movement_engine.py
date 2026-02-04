"""
BIONIC™ Movement Engine
========================
Moteur d'analyse des mouvements et corridors fauniques.

Version: 1.0 - P0 Étape 1 (Fondations)

TODO Phase P0-2:
- Intégrer données LiDAR pour corridors
- Modéliser résistance au déplacement
- Ajouter analyse de connectivité
- Intégrer données de télémétrie historiques
"""

import logging
import uuid
import math
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import sys

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import (
    MovementAnalysisInput,
    MovementAnalysisOutput,
    SpeciesCode,
    MovementPattern,
    CorridorSegment,
    HotspotPrediction
)

logger = logging.getLogger(__name__)


class MovementEngine:
    """
    Moteur d'analyse des mouvements BIONIC™.
    
    Analyse:
    - Patterns de déplacement
    - Corridors de mouvement
    - Home range et aire vitale
    - Zones de repos vs alimentation
    - Prédictions de positions
    """
    
    # Home range typique par espèce (km²)
    TYPICAL_HOME_RANGE = {
        SpeciesCode.DEER: {"male": 8.0, "female": 4.0, "core_ratio": 0.25},
        SpeciesCode.MOOSE: {"male": 25.0, "female": 15.0, "core_ratio": 0.20},
        SpeciesCode.BEAR: {"male": 100.0, "female": 25.0, "core_ratio": 0.15},
        SpeciesCode.CARIBOU: {"male": 500.0, "female": 300.0, "core_ratio": 0.10},
        SpeciesCode.TURKEY: {"male": 2.0, "female": 1.5, "core_ratio": 0.30}
    }
    
    # Distance journalière moyenne (km)
    DAILY_MOVEMENT = {
        SpeciesCode.DEER: {"summer": 2.0, "fall": 3.5, "winter": 1.5, "spring": 2.5},
        SpeciesCode.MOOSE: {"summer": 3.0, "fall": 5.0, "winter": 2.0, "spring": 4.0},
        SpeciesCode.BEAR: {"summer": 5.0, "fall": 8.0, "winter": 0.0, "spring": 6.0},
        SpeciesCode.TURKEY: {"summer": 1.0, "fall": 1.5, "winter": 0.8, "spring": 1.2}
    }
    
    # Noms français des patterns
    PATTERN_NAMES_FR = {
        MovementPattern.SEDENTARY: "Sédentaire",
        MovementPattern.LOCAL: "Local",
        MovementPattern.REGIONAL: "Régional",
        MovementPattern.MIGRATORY: "Migratoire",
        MovementPattern.DISPERSAL: "Dispersion"
    }
    
    def __init__(self):
        self.version = "1.0.0"
        logger.info("BIONIC™ Movement Engine initialized (v%s)", self.version)
    
    async def analyze(
        self,
        input_data: MovementAnalysisInput,
        use_cache: bool = True
    ) -> MovementAnalysisOutput:
        """
        Analyse les mouvements et corridors.
        """
        analysis_id = f"mov_{uuid.uuid4().hex[:12]}"
        random.seed(int(input_data.latitude * 1000 + input_data.longitude * 1000))
        
        # Déterminer le pattern de mouvement
        current_pattern = self._determine_movement_pattern(input_data.species)
        
        # Calculer le home range
        home_range = self._calculate_home_range(input_data.species)
        
        # Générer les corridors
        corridors = []
        if input_data.include_corridors:
            corridors = self._generate_corridors(
                input_data.latitude, input_data.longitude,
                input_data.species
            )
        
        # Distances de mouvement
        daily_km = self._get_daily_movement(input_data.species)
        seasonal_km = daily_km * 30  # Approximation mensuelle
        
        # Identifier les zones
        bedding_areas = self._identify_bedding_areas(
            input_data.latitude, input_data.longitude
        )
        feeding_areas = self._identify_feeding_areas(
            input_data.latitude, input_data.longitude
        )
        travel_routes = self._identify_travel_routes(
            input_data.latitude, input_data.longitude
        )
        
        # Prédire les positions probables
        likely_positions = self._predict_positions(
            input_data.latitude, input_data.longitude,
            input_data.species
        )
        
        return MovementAnalysisOutput(
            analysis_id=analysis_id,
            species=input_data.species,
            location={"lat": input_data.latitude, "lon": input_data.longitude},
            analyzed_at=datetime.now(timezone.utc),
            current_pattern=current_pattern,
            pattern_name_fr=self.PATTERN_NAMES_FR.get(current_pattern, "Inconnu"),
            home_range_km2=home_range["total"],
            core_area_km2=home_range["core"],
            corridors=corridors,
            primary_corridor_score=corridors[0].usage_probability if corridors else 0.0,
            daily_movement_km=daily_km,
            seasonal_range_km=seasonal_km,
            bedding_areas=bedding_areas,
            feeding_areas=feeding_areas,
            travel_routes=travel_routes,
            likely_positions=likely_positions,
            confidence=0.70,
            from_cache=False
        )
    
    def _determine_movement_pattern(self, species: SpeciesCode) -> MovementPattern:
        """Détermine le pattern de mouvement actuel."""
        month = datetime.now().month
        
        # Patterns saisonniers
        if species == SpeciesCode.CARIBOU:
            if month in [4, 5, 10, 11]:
                return MovementPattern.MIGRATORY
            return MovementPattern.REGIONAL
        
        if species == SpeciesCode.MOOSE:
            if month in [11, 12, 1, 2]:
                return MovementPattern.SEDENTARY  # Yards
            return MovementPattern.LOCAL
        
        if species == SpeciesCode.DEER:
            if month in [10, 11]:  # Rut
                return MovementPattern.REGIONAL
            if month in [12, 1, 2]:
                return MovementPattern.SEDENTARY
            return MovementPattern.LOCAL
        
        return MovementPattern.LOCAL
    
    def _calculate_home_range(self, species: SpeciesCode) -> Dict[str, float]:
        """Calcule le home range estimé."""
        ranges = self.TYPICAL_HOME_RANGE.get(species, {"male": 10, "female": 5, "core_ratio": 0.2})
        
        # Moyenne male/female avec variation
        avg_range = (ranges["male"] + ranges["female"]) / 2
        variation = random.uniform(0.8, 1.2)
        
        total = avg_range * variation
        core = total * ranges["core_ratio"]
        
        return {
            "total": round(total, 2),
            "core": round(core, 2)
        }
    
    def _get_daily_movement(self, species: SpeciesCode) -> float:
        """Obtient la distance journalière moyenne."""
        month = datetime.now().month
        
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "fall"
        else:
            season = "winter"
        
        movements = self.DAILY_MOVEMENT.get(species, {"summer": 2, "fall": 3, "winter": 1, "spring": 2})
        base = movements.get(season, 2)
        
        return round(base * random.uniform(0.8, 1.3), 1)
    
    def _generate_corridors(
        self,
        lat: float,
        lon: float,
        species: SpeciesCode
    ) -> List[CorridorSegment]:
        """Génère les corridors de déplacement estimés."""
        corridors = []
        
        # Générer 3-5 corridors
        num_corridors = random.randint(3, 5)
        
        for i in range(num_corridors):
            # Direction aléatoire
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.5, 2.0)  # km
            
            end_lat = lat + distance / 111 * math.cos(angle)
            end_lon = lon + distance / (111 * math.cos(math.radians(lat))) * math.sin(angle)
            
            # Largeur du corridor
            width = random.uniform(50, 200)
            
            # Probabilité d'utilisation
            prob = random.uniform(0.4, 0.9)
            
            # Type de terrain
            terrain_types = ["Esker", "Lisière forestière", "Vallée", "Bordure de tourbière", "Flanc de colline"]
            terrain = random.choice(terrain_types)
            
            corridors.append(CorridorSegment(
                start_lat=round(lat, 6),
                start_lon=round(lon, 6),
                end_lat=round(end_lat, 6),
                end_lon=round(end_lon, 6),
                width_m=round(width, 0),
                usage_probability=round(prob, 2),
                terrain_type=terrain,
                notes=f"Corridor {terrain.lower()} - Usage {'élevé' if prob > 0.7 else 'modéré'}"
            ))
        
        # Trier par probabilité
        return sorted(corridors, key=lambda x: x.usage_probability, reverse=True)
    
    def _identify_bedding_areas(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Identifie les zones de repos potentielles."""
        areas = []
        
        for i in range(random.randint(2, 4)):
            offset_lat = random.uniform(-0.02, 0.02)
            offset_lon = random.uniform(-0.02, 0.02)
            
            areas.append({
                "lat": round(lat + offset_lat, 6),
                "lon": round(lon + offset_lon, 6),
                "type": random.choice(["Couvert dense", "Versant sud", "Sous-bois conifères"]),
                "probability": round(random.uniform(0.5, 0.9), 2),
                "best_time": "Milieu de journée"
            })
        
        return areas
    
    def _identify_feeding_areas(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Identifie les zones d'alimentation potentielles."""
        areas = []
        
        for i in range(random.randint(3, 5)):
            offset_lat = random.uniform(-0.03, 0.03)
            offset_lon = random.uniform(-0.03, 0.03)
            
            areas.append({
                "lat": round(lat + offset_lat, 6),
                "lon": round(lon + offset_lon, 6),
                "type": random.choice(["Clairière", "Bordure de champ", "Jeune repousse", "Friche"]),
                "probability": round(random.uniform(0.5, 0.85), 2),
                "best_time": random.choice(["Aube", "Crépuscule"])
            })
        
        return areas
    
    def _identify_travel_routes(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Identifie les routes de déplacement."""
        routes = []
        
        for i in range(random.randint(2, 4)):
            routes.append({
                "name": f"Route {['principale', 'secondaire', 'tertiaire'][i % 3]}",
                "type": random.choice(["Sentier établi", "Crête", "Fond de vallée", "Bordure eau"]),
                "usage_time": random.choice(["Aube/crépuscule", "Nocturne", "Variable"]),
                "direction": random.choice(["N-S", "E-O", "NE-SO", "NO-SE"])
            })
        
        return routes
    
    def _predict_positions(
        self,
        lat: float,
        lon: float,
        species: SpeciesCode
    ) -> List[HotspotPrediction]:
        """Prédit les positions probables du gibier."""
        positions = []
        
        for i in range(random.randint(3, 5)):
            offset_lat = random.uniform(-0.025, 0.025)
            offset_lon = random.uniform(-0.025, 0.025)
            
            score = random.uniform(55, 90)
            
            positions.append(HotspotPrediction(
                latitude=round(lat + offset_lat, 6),
                longitude=round(lon + offset_lon, 6),
                score=round(score, 1),
                confidence=round(random.uniform(0.5, 0.8), 2),
                reason=random.choice([
                    "Zone d'alimentation matinale",
                    "Corridor de déplacement actif",
                    "Zone de repos diurne",
                    "Point d'eau fréquenté"
                ]),
                recommended_time=random.choice(["06:00-08:00", "17:00-19:00", "10:00-14:00"])
            ))
        
        return sorted(positions, key=lambda x: x.score, reverse=True)


# Singleton instance
movement_engine = MovementEngine()
