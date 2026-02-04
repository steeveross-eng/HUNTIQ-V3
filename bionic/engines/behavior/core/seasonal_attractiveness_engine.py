"""
BIONIC™ Seasonal Attractiveness Engine
========================================
Moteur d'analyse de l'attractivité saisonnière des habitats.

Version: 1.0 - P0 Étape 1 (Fondations)

TODO Phase P0-2:
- Intégrer les données phénologiques réelles
- Modéliser les sources de nourriture par saison
- Ajouter les patterns de migration
- Connecter avec les données Sentinel-2 NDVI
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, date, timedelta
import sys

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import (
    SeasonalAttractivenessInput,
    SeasonalAttractivenessOutput,
    SpeciesCode,
    SeasonalPhase,
    HotspotPrediction
)

logger = logging.getLogger(__name__)


class SeasonalAttractivenessEngine:
    """
    Moteur d'attractivité saisonnière BIONIC™.
    
    Analyse l'attractivité d'une zone en fonction de:
    - Phase saisonnière du cycle de vie
    - Disponibilité des ressources alimentaires
    - Qualité du couvert
    - Conditions thermiques
    - Disponibilité de l'eau
    """
    
    # Phases saisonnières par espèce (jour de l'année)
    SEASONAL_PHASES = {
        SpeciesCode.DEER: {
            SeasonalPhase.WINTER_SURVIVAL: (1, 60),      # Jan 1 - Mar 1
            SeasonalPhase.SPRING_DISPERSAL: (61, 120),   # Mar 2 - Apr 30
            SeasonalPhase.SUMMER_FORAGING: (121, 244),   # May 1 - Sep 1
            SeasonalPhase.PRE_RUT_PREPARATION: (245, 288), # Sep 2 - Oct 15
            SeasonalPhase.RUT_ACTIVE: (289, 335),        # Oct 16 - Dec 1
            SeasonalPhase.POST_RUT_RECOVERY: (336, 366)  # Dec 2 - Dec 31
        },
        SpeciesCode.MOOSE: {
            SeasonalPhase.WINTER_SURVIVAL: (1, 90),
            SeasonalPhase.SPRING_DISPERSAL: (91, 150),
            SeasonalPhase.SUMMER_FORAGING: (151, 244),
            SeasonalPhase.PRE_RUT_PREPARATION: (245, 258),
            SeasonalPhase.RUT_ACTIVE: (259, 305),
            SeasonalPhase.POST_RUT_RECOVERY: (306, 366)
        },
        SpeciesCode.BEAR: {
            SeasonalPhase.WINTER_SURVIVAL: (1, 100),     # Hibernation
            SeasonalPhase.SPRING_DISPERSAL: (101, 150),
            SeasonalPhase.SUMMER_FORAGING: (151, 270),
            SeasonalPhase.FALL_PREPARATION: (271, 320),  # Hyperphagie
            SeasonalPhase.WINTER_SURVIVAL: (321, 366)
        }
    }
    
    # Noms français des phases
    PHASE_NAMES_FR = {
        SeasonalPhase.WINTER_SURVIVAL: "Survie hivernale",
        SeasonalPhase.SPRING_DISPERSAL: "Dispersion printanière",
        SeasonalPhase.SUMMER_FORAGING: "Alimentation estivale",
        SeasonalPhase.PRE_RUT_PREPARATION: "Pré-rut (préparation)",
        SeasonalPhase.RUT_ACTIVE: "Rut actif",
        SeasonalPhase.POST_RUT_RECOVERY: "Récupération post-rut",
        SeasonalPhase.FALL_PREPARATION: "Préparation automnale"
    }
    
    def __init__(self):
        self.version = "1.0.0"
        logger.info("BIONIC™ Seasonal Attractiveness Engine initialized (v%s)", self.version)
    
    async def analyze(
        self,
        input_data: SeasonalAttractivenessInput,
        use_cache: bool = True
    ) -> SeasonalAttractivenessOutput:
        """
        Analyse l'attractivité saisonnière.
        """
        analysis_id = f"seas_{uuid.uuid4().hex[:12]}"
        
        # Déterminer la phase saisonnière
        target_date = input_data.target_date or date.today()
        day_of_year = target_date.timetuple().tm_yday
        
        current_phase = self._get_current_phase(input_data.species, day_of_year)
        phase_info = self._get_phase_info(input_data.species, current_phase, day_of_year)
        
        # Charger données environnementales
        env_data = await self.load_inputs(input_data)
        
        # Calculer les scores d'attractivité
        attractiveness = self._calculate_attractiveness(
            input_data.species, current_phase, env_data
        )
        
        # Identifier les hotspots
        hotspots = self._identify_hotspots(
            input_data.latitude, input_data.longitude,
            input_data.species, current_phase
        )
        
        # Générer recommandations
        recommendations = self._generate_recommendations(
            input_data.species, current_phase, attractiveness
        )
        
        # Déterminer les meilleurs jours
        best_days = self._calculate_best_hunting_days(
            input_data.species, current_phase, target_date
        )
        
        return SeasonalAttractivenessOutput(
            analysis_id=analysis_id,
            species=input_data.species,
            location={"lat": input_data.latitude, "lon": input_data.longitude},
            analyzed_at=datetime.now(timezone.utc),
            current_phase=current_phase,
            phase_name_fr=self.PHASE_NAMES_FR.get(current_phase, "Inconnue"),
            days_into_phase=phase_info["days_into"],
            days_remaining=phase_info["days_remaining"],
            overall_attractiveness=attractiveness["overall"],
            food_attractiveness=attractiveness["food"],
            cover_attractiveness=attractiveness["cover"],
            water_attractiveness=attractiveness["water"],
            thermal_attractiveness=attractiveness["thermal"],
            hotspots=hotspots,
            trend=attractiveness["trend"],
            trend_description=attractiveness["trend_description"],
            best_hunting_days=best_days,
            recommendations=recommendations,
            from_cache=False
        )
    
    async def load_inputs(
        self, 
        input_data: SeasonalAttractivenessInput
    ) -> Dict[str, Any]:
        """
        Charge les données environnementales.
        
        TODO P0-2: Intégrer Sentinel NDVI et données terrain réelles
        """
        return {
            "ndvi": input_data.ndvi or 0.55,
            "water_distance_m": input_data.water_distance_m or 500,
            "elevation_m": input_data.elevation_m or 300,
            "day_of_year": (input_data.target_date or date.today()).timetuple().tm_yday
        }
    
    def _get_current_phase(
        self, 
        species: SpeciesCode, 
        day_of_year: int
    ) -> SeasonalPhase:
        """Détermine la phase saisonnière actuelle."""
        phases = self.SEASONAL_PHASES.get(species, self.SEASONAL_PHASES[SpeciesCode.DEER])
        
        for phase, (start, end) in phases.items():
            if start <= day_of_year <= end:
                return phase
        
        return SeasonalPhase.WINTER_SURVIVAL
    
    def _get_phase_info(
        self,
        species: SpeciesCode,
        phase: SeasonalPhase,
        day_of_year: int
    ) -> Dict[str, int]:
        """Obtient les informations sur la phase actuelle."""
        phases = self.SEASONAL_PHASES.get(species, self.SEASONAL_PHASES[SpeciesCode.DEER])
        
        if phase in phases:
            start, end = phases[phase]
            days_into = day_of_year - start + 1
            days_remaining = end - day_of_year
            return {"days_into": max(0, days_into), "days_remaining": max(0, days_remaining)}
        
        return {"days_into": 0, "days_remaining": 30}
    
    def _calculate_attractiveness(
        self,
        species: SpeciesCode,
        phase: SeasonalPhase,
        env_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcule les scores d'attractivité."""
        ndvi = env_data.get("ndvi", 0.5)
        water_dist = env_data.get("water_distance_m", 500)
        
        # Score nourriture basé sur NDVI et phase
        food_base = {
            SeasonalPhase.WINTER_SURVIVAL: 30,
            SeasonalPhase.SPRING_DISPERSAL: 50,
            SeasonalPhase.SUMMER_FORAGING: 75,
            SeasonalPhase.PRE_RUT_PREPARATION: 70,
            SeasonalPhase.RUT_ACTIVE: 45,
            SeasonalPhase.POST_RUT_RECOVERY: 55,
            SeasonalPhase.FALL_PREPARATION: 85
        }
        food = food_base.get(phase, 50) + (ndvi - 0.5) * 40
        food = max(0, min(100, food))
        
        # Score couvert
        cover = 60 + ndvi * 30
        
        # Score eau
        if water_dist < 100:
            water = 95
        elif water_dist < 300:
            water = 80
        elif water_dist < 500:
            water = 65
        elif water_dist < 1000:
            water = 45
        else:
            water = 25
        
        # Score thermique (basé sur la saison)
        thermal_base = {
            SeasonalPhase.WINTER_SURVIVAL: 35,
            SeasonalPhase.SPRING_DISPERSAL: 65,
            SeasonalPhase.SUMMER_FORAGING: 70,
            SeasonalPhase.PRE_RUT_PREPARATION: 75,
            SeasonalPhase.RUT_ACTIVE: 80,
            SeasonalPhase.POST_RUT_RECOVERY: 55,
            SeasonalPhase.FALL_PREPARATION: 70
        }
        thermal = thermal_base.get(phase, 60)
        
        # Score global
        overall = (food * 0.35 + cover * 0.25 + water * 0.20 + thermal * 0.20)
        
        # Tendance
        day_of_year = env_data.get("day_of_year", 180)
        if 80 <= day_of_year <= 150:
            trend = "increasing"
            trend_desc = "Attractivité en hausse avec le printemps"
        elif 260 <= day_of_year <= 320:
            trend = "increasing"
            trend_desc = "Pic d'activité lié au rut/hyperphagie"
        elif 150 < day_of_year < 260:
            trend = "stable"
            trend_desc = "Conditions estivales stables"
        else:
            trend = "decreasing"
            trend_desc = "Attractivité en baisse (hiver)"
        
        return {
            "overall": round(overall, 1),
            "food": round(food, 1),
            "cover": round(cover, 1),
            "water": round(water, 1),
            "thermal": round(thermal, 1),
            "trend": trend,
            "trend_description": trend_desc
        }
    
    def _identify_hotspots(
        self,
        lat: float,
        lon: float,
        species: SpeciesCode,
        phase: SeasonalPhase
    ) -> List[HotspotPrediction]:
        """Identifie les hotspots potentiels."""
        import random
        random.seed(int(lat * 1000 + lon * 1000))
        
        hotspots = []
        
        # Générer 3-5 hotspots autour du point
        for i in range(random.randint(3, 5)):
            offset_lat = random.uniform(-0.03, 0.03)
            offset_lon = random.uniform(-0.03, 0.03)
            
            score = random.uniform(60, 95)
            
            reasons = {
                SeasonalPhase.RUT_ACTIVE: "Zone de scrapes/frottoirs détectée",
                SeasonalPhase.SUMMER_FORAGING: "Zone d'alimentation principale",
                SeasonalPhase.WINTER_SURVIVAL: "Ravage potentiel",
                SeasonalPhase.FALL_PREPARATION: "Source de nourriture automnale"
            }
            
            hotspots.append(HotspotPrediction(
                latitude=round(lat + offset_lat, 6),
                longitude=round(lon + offset_lon, 6),
                score=round(score, 1),
                confidence=round(random.uniform(0.6, 0.9), 2),
                reason=reasons.get(phase, "Zone d'activité élevée"),
                recommended_time="Aube" if i % 2 == 0 else "Crépuscule"
            ))
        
        return sorted(hotspots, key=lambda x: x.score, reverse=True)
    
    def _calculate_best_hunting_days(
        self,
        species: SpeciesCode,
        phase: SeasonalPhase,
        target_date: date
    ) -> List[str]:
        """Calcule les meilleurs jours de chasse à venir."""
        best_days = []
        
        # Prochains 14 jours
        for i in range(14):
            future_date = target_date + timedelta(days=i)
            day_name = future_date.strftime("%A %d %B")
            
            # Simplification: weekend + certains jours de semaine
            if future_date.weekday() in [4, 5, 6]:  # Ven, Sam, Dim
                best_days.append(day_name)
        
        return best_days[:5]
    
    def _generate_recommendations(
        self,
        species: SpeciesCode,
        phase: SeasonalPhase,
        attractiveness: Dict[str, Any]
    ) -> List[str]:
        """Génère des recommandations saisonnières."""
        recs = []
        
        # Recommandations par phase
        phase_recs = {
            SeasonalPhase.WINTER_SURVIVAL: [
                "Concentrez-vous sur les ravages et aires d'hivernage",
                "Le gibier est regroupé - déplacements réduits"
            ],
            SeasonalPhase.SPRING_DISPERSAL: [
                "Les animaux se dispersent - surveillez les nouveaux territoires",
                "Recherchez les premières pousses vertes"
            ],
            SeasonalPhase.SUMMER_FORAGING: [
                "Ciblez les zones de gagnage actives",
                "Activité concentrée matin et soir"
            ],
            SeasonalPhase.PRE_RUT_PREPARATION: [
                "Les mâles établissent leurs territoires",
                "Surveillez les frottoirs et grattages"
            ],
            SeasonalPhase.RUT_ACTIVE: [
                "Période d'activité maximale des mâles",
                "Les appels et leurres sont très efficaces",
                "Restez en place - le gibier viendra à vous"
            ],
            SeasonalPhase.POST_RUT_RECOVERY: [
                "Mâles épuisés - recherchent nourriture",
                "Retour aux patterns alimentaires"
            ],
            SeasonalPhase.FALL_PREPARATION: [
                "Hyperphagie active - cibler les sources de nourriture",
                "Activité diurne accrue"
            ]
        }
        
        recs.extend(phase_recs.get(phase, []))
        
        # Recommandations basées sur les scores
        if attractiveness["food"] > 70:
            recs.append("Excellente disponibilité alimentaire - postez-vous près des zones de gagnage")
        
        if attractiveness["water"] < 50:
            recs.append("Eau rare dans le secteur - surveillez les points d'eau")
        
        return recs[:5]


# Singleton instance
seasonal_attractiveness_engine = SeasonalAttractivenessEngine()
