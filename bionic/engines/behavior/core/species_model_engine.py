"""
BIONIC™ Species Model Engine
=============================
Moteur de modèle spécifique par espèce.

Version: 1.0 - P0 Étape 1 (Fondations)

TODO Phase P0-2:
- Intégrer profils détaillés par espèce
- Ajouter données population Québec
- Modèles ML spécifiques
- Calibration avec données de récolte
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import sys

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import (
    SpeciesModelInput,
    SpeciesModelOutput,
    SpeciesCode
)

logger = logging.getLogger(__name__)


class SpeciesModelEngine:
    """
    Moteur de modèle spécifique BIONIC™.
    
    Fournit une analyse complète et adaptée pour chaque espèce:
    - Profil comportemental
    - Habitat préféré
    - Facteurs saisonniers
    - Tactiques de chasse optimales
    """
    
    # Profils détaillés par espèce
    SPECIES_PROFILES = {
        SpeciesCode.DEER: {
            "name_fr": "Cerf de Virginie",
            "name_en": "White-tailed Deer",
            "scientific_name": "Odocoileus virginianus",
            "family": "Cervidés",
            "weight_range_kg": {"male": (90, 140), "female": (55, 90)},
            "lifespan_years": 10,
            "habitat_preference": ["Forêt mixte", "Lisières", "Friches agricoles"],
            "diet": ["Rameaux", "Feuilles", "Glands", "Pommes", "Herbes"],
            "activity_pattern": "Crépusculaire",
            "group_size": {"winter": "5-15", "summer": "1-5"},
            "hunting_season_qc": {"start": "Septembre", "end": "Novembre"},
            "population_qc": "Environ 300,000",
            "preferred_terrain": "Vallées et collines boisées",
            "water_dependency": "Modérée",
            "human_tolerance": "Élevée",
            "calling_effectiveness": 0.85,
            "decoy_effectiveness": 0.80
        },
        SpeciesCode.MOOSE: {
            "name_fr": "Orignal",
            "name_en": "Moose",
            "scientific_name": "Alces alces",
            "family": "Cervidés",
            "weight_range_kg": {"male": (380, 535), "female": (270, 360)},
            "lifespan_years": 15,
            "habitat_preference": ["Forêt boréale", "Tourbières", "Bordures de lacs"],
            "diet": ["Saules", "Plantes aquatiques", "Écorce", "Ramilles"],
            "activity_pattern": "Crépusculaire/Nocturne",
            "group_size": {"winter": "1-3", "summer": "1-2"},
            "hunting_season_qc": {"start": "Septembre", "end": "Octobre"},
            "population_qc": "Environ 125,000",
            "preferred_terrain": "Zones humides et forêt mixte",
            "water_dependency": "Élevée",
            "human_tolerance": "Faible",
            "calling_effectiveness": 0.90,
            "decoy_effectiveness": 0.70
        },
        SpeciesCode.BEAR: {
            "name_fr": "Ours noir",
            "name_en": "Black Bear",
            "scientific_name": "Ursus americanus",
            "family": "Ursidés",
            "weight_range_kg": {"male": (115, 270), "female": (90, 140)},
            "lifespan_years": 25,
            "habitat_preference": ["Forêt dense", "Zones montagneuses", "Marécages"],
            "diet": ["Baies", "Noix", "Insectes", "Poissons", "Charognes"],
            "activity_pattern": "Diurne/Crépusculaire",
            "group_size": {"all": "1 (solitaire)"},
            "hunting_season_qc": {"start": "Mai", "end": "Juin"},
            "population_qc": "Environ 70,000",
            "preferred_terrain": "Forêt dense avec sources de nourriture",
            "water_dependency": "Modérée",
            "human_tolerance": "Variable",
            "calling_effectiveness": 0.40,
            "decoy_effectiveness": 0.30
        },
        SpeciesCode.TURKEY: {
            "name_fr": "Dindon sauvage",
            "name_en": "Wild Turkey",
            "scientific_name": "Meleagris gallopavo",
            "family": "Phasianidés",
            "weight_range_kg": {"male": (7, 11), "female": (3.5, 5.5)},
            "lifespan_years": 5,
            "habitat_preference": ["Forêt de feuillus", "Champs agricoles", "Lisières"],
            "diet": ["Glands", "Baies", "Insectes", "Graines"],
            "activity_pattern": "Diurne",
            "group_size": {"winter": "20-200", "spring": "5-20"},
            "hunting_season_qc": {"start": "Avril", "end": "Mai"},
            "population_qc": "Environ 35,000 (en croissance)",
            "preferred_terrain": "Vallées agricoles boisées",
            "water_dependency": "Faible",
            "human_tolerance": "Modérée",
            "calling_effectiveness": 0.95,
            "decoy_effectiveness": 0.85
        },
        SpeciesCode.CARIBOU: {
            "name_fr": "Caribou",
            "name_en": "Caribou",
            "scientific_name": "Rangifer tarandus",
            "family": "Cervidés",
            "weight_range_kg": {"male": (150, 200), "female": (80, 120)},
            "lifespan_years": 12,
            "habitat_preference": ["Toundra", "Taïga", "Tourbières"],
            "diet": ["Lichens", "Carex", "Saules", "Champignons"],
            "activity_pattern": "Diurne",
            "group_size": {"winter": "50-200", "summer": "10-50"},
            "hunting_season_qc": {"start": "Août", "end": "Septembre"},
            "population_qc": "Variable (populations menacées)",
            "preferred_terrain": "Toundra alpine et forêt boréale ouverte",
            "water_dependency": "Modérée",
            "human_tolerance": "Très faible",
            "calling_effectiveness": 0.50,
            "decoy_effectiveness": 0.40
        }
    }
    
    def __init__(self):
        self.version = "1.0.0"
        logger.info("BIONIC™ Species Model Engine initialized (v%s)", self.version)
    
    async def analyze(
        self,
        input_data: SpeciesModelInput,
        use_cache: bool = True
    ) -> SpeciesModelOutput:
        """
        Analyse complète spécifique à l'espèce.
        """
        analysis_id = f"spe_{uuid.uuid4().hex[:12]}"
        
        # Obtenir le profil de l'espèce
        profile = self.SPECIES_PROFILES.get(input_data.species, self.SPECIES_PROFILES[SpeciesCode.DEER])
        
        # Calculer la compatibilité habitat
        habitat_analysis = self._analyze_habitat_suitability(
            input_data.species,
            input_data.environment_data or {}
        )
        
        # Résumé comportemental
        behavior_summary = self._get_behavior_summary(input_data.species)
        
        # Facteurs saisonniers
        seasonal_factors = self._get_seasonal_factors(input_data.species)
        
        # Scores globaux
        overall_score = self._calculate_overall_score(habitat_analysis, seasonal_factors)
        hunting_index = self._calculate_hunting_index(input_data.species, habitat_analysis)
        
        # Conseils spécifiques
        tips = self._generate_species_tips(input_data.species, seasonal_factors)
        tactics = self._get_optimal_tactics(input_data.species)
        gear = self._get_gear_recommendations(input_data.species)
        
        return SpeciesModelOutput(
            analysis_id=analysis_id,
            species=input_data.species,
            species_name_fr=profile["name_fr"],
            species_name_en=profile["name_en"],
            location={"lat": input_data.latitude, "lon": input_data.longitude},
            analyzed_at=datetime.now(timezone.utc),
            species_profile=profile,
            habitat_suitability=habitat_analysis["overall"],
            habitat_factors=habitat_analysis["factors"],
            behavior_summary=behavior_summary,
            current_behavior_phase=behavior_summary.get("current_phase", "Normal"),
            seasonal_factors=seasonal_factors,
            overall_score=overall_score,
            hunting_index=hunting_index,
            species_specific_tips=tips,
            optimal_tactics=tactics,
            gear_recommendations=gear,
            confidence=0.75,
            from_cache=False
        )
    
    def _analyze_habitat_suitability(
        self,
        species: SpeciesCode,
        env_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyse la compatibilité de l'habitat."""
        profile = self.SPECIES_PROFILES.get(species, {})
        
        # Scores par défaut (à remplacer par analyse réelle)
        ndvi = env_data.get("ndvi", 0.55)
        elevation = env_data.get("elevation", 300)
        water_dist = env_data.get("water_distance", 500)
        
        # Score végétation
        veg_score = min(100, ndvi * 120)
        
        # Score eau (selon dépendance de l'espèce)
        water_dep = profile.get("water_dependency", "Modérée")
        if water_dep == "Élevée":
            water_score = max(0, 100 - water_dist / 10)
        elif water_dep == "Modérée":
            water_score = max(0, 100 - water_dist / 20)
        else:
            water_score = max(0, 100 - water_dist / 50)
        
        # Score couvert
        cover_score = veg_score * 0.9
        
        # Score élévation (simplifié)
        if species == SpeciesCode.CARIBOU:
            elev_score = 100 if elevation > 500 else 50
        else:
            elev_score = 80 if 100 < elevation < 600 else 60
        
        overall = (veg_score * 0.3 + water_score * 0.25 + cover_score * 0.25 + elev_score * 0.2)
        
        return {
            "overall": round(overall, 1),
            "factors": {
                "vegetation": round(veg_score, 1),
                "water": round(water_score, 1),
                "cover": round(cover_score, 1),
                "elevation": round(elev_score, 1)
            }
        }
    
    def _get_behavior_summary(self, species: SpeciesCode) -> Dict[str, Any]:
        """Obtient le résumé comportemental actuel."""
        month = datetime.now().month
        
        # Phase comportementale selon la saison
        if species in [SpeciesCode.DEER, SpeciesCode.MOOSE]:
            if month in [10, 11]:
                phase = "Rut"
                description = "Période de reproduction - Activité maximale des mâles"
            elif month in [12, 1, 2]:
                phase = "Hivernage"
                description = "Regroupement en ravages, déplacements réduits"
            elif month in [3, 4, 5]:
                phase = "Dispersion printanière"
                description = "Établissement des territoires"
            else:
                phase = "Estival"
                description = "Alimentation active, croissance des bois"
        elif species == SpeciesCode.BEAR:
            if month in [11, 12, 1, 2, 3]:
                phase = "Hibernation"
                description = "Inactif en tanière"
            elif month in [4, 5]:
                phase = "Sortie d'hibernation"
                description = "Recherche active de nourriture"
            elif month in [9, 10]:
                phase = "Hyperphagie"
                description = "Alimentation intensive pré-hibernation"
            else:
                phase = "Actif"
                description = "Activité normale, recherche de nourriture"
        else:
            phase = "Normal"
            description = "Comportement saisonnier standard"
        
        return {
            "current_phase": phase,
            "description": description,
            "activity_pattern": self.SPECIES_PROFILES.get(species, {}).get("activity_pattern", "Variable")
        }
    
    def _get_seasonal_factors(self, species: SpeciesCode) -> Dict[str, Any]:
        """Obtient les facteurs saisonniers."""
        month = datetime.now().month
        
        # Facteur d'opportunité saisonnier
        opportunity_by_month = {
            SpeciesCode.DEER: {
                9: 0.7, 10: 0.95, 11: 1.0, 12: 0.6, 1: 0.4, 2: 0.3,
                3: 0.4, 4: 0.5, 5: 0.6, 6: 0.5, 7: 0.5, 8: 0.6
            },
            SpeciesCode.MOOSE: {
                9: 1.0, 10: 0.9, 11: 0.5, 12: 0.3, 1: 0.3, 2: 0.3,
                3: 0.4, 4: 0.5, 5: 0.6, 6: 0.5, 7: 0.5, 8: 0.7
            },
            SpeciesCode.BEAR: {
                5: 0.9, 6: 1.0, 7: 0.8, 8: 0.7, 9: 0.8, 10: 0.6,
                11: 0.2, 12: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.3
            }
        }
        
        opp = opportunity_by_month.get(species, {}).get(month, 0.5)
        
        return {
            "month": month,
            "opportunity_factor": opp,
            "is_peak_season": opp > 0.8,
            "season_quality": "Excellente" if opp > 0.8 else "Bonne" if opp > 0.5 else "Difficile"
        }
    
    def _calculate_overall_score(
        self,
        habitat: Dict[str, Any],
        seasonal: Dict[str, Any]
    ) -> float:
        """Calcule le score global."""
        habitat_score = habitat.get("overall", 50)
        seasonal_factor = seasonal.get("opportunity_factor", 0.5)
        
        return round(habitat_score * seasonal_factor, 1)
    
    def _calculate_hunting_index(
        self,
        species: SpeciesCode,
        habitat: Dict[str, Any]
    ) -> float:
        """Calcule l'indice de chasse."""
        profile = self.SPECIES_PROFILES.get(species, {})
        
        base_score = habitat.get("overall", 50)
        calling_eff = profile.get("calling_effectiveness", 0.5) * 100
        
        return round((base_score + calling_eff) / 2, 1)
    
    def _generate_species_tips(
        self,
        species: SpeciesCode,
        seasonal: Dict[str, Any]
    ) -> List[str]:
        """Génère des conseils spécifiques à l'espèce."""
        tips = {
            SpeciesCode.DEER: [
                "Le cerf utilise son odorat comme défense principale - Jouez le vent",
                "En période de rut, les mâles répondent aux appels de provocation",
                "Repérez les frottoirs et grattages pour identifier les corridors",
                "Les femelles guident les déplacements - Suivez-les pour trouver les mâles"
            ],
            SpeciesCode.MOOSE: [
                "L'orignal a une ouïe exceptionnelle - Minimisez tout bruit",
                "Les appels de femelle sont très efficaces en rut",
                "Surveillez les bordures de lacs et tourbières à l'aube",
                "Approchez toujours contre le vent"
            ],
            SpeciesCode.BEAR: [
                "L'ours est imprévisible - Restez vigilant",
                "Utilisez des appâts naturels (baies, poisson)",
                "Chassez près des sources de nourriture automnales",
                "L'affût à l'aube/crépuscule est très efficace"
            ],
            SpeciesCode.TURKEY: [
                "Le dindon a une vision exceptionnelle - Camouflage essentiel",
                "Les appels de poule attirent les mâles au printemps",
                "Repérez les zones de grattage et les dortoirs",
                "Patience et immobilité sont cruciales"
            ]
        }
        
        base_tips = tips.get(species, ["Adapter les techniques selon le comportement observé"])
        
        # Ajouter conseil saisonnier
        if seasonal.get("is_peak_season"):
            base_tips.insert(0, "Période de chasse optimale - Maximisez votre temps sur le terrain")
        
        return base_tips[:5]
    
    def _get_optimal_tactics(self, species: SpeciesCode) -> List[str]:
        """Obtient les tactiques optimales."""
        tactics = {
            SpeciesCode.DEER: ["Affût sur corridor", "Appel au grunt", "Rattling", "Chasse à l'approche"],
            SpeciesCode.MOOSE: ["Appel à la vache", "Affût aux salines", "Chasse en canot", "Appel au bull"],
            SpeciesCode.BEAR: ["Affût sur appât", "Chasse aux baies", "Affût à l'eau", "Chasse aux champs"],
            SpeciesCode.TURKEY: ["Affût au rappel", "Course et appel", "Affût de dortoir", "Chasse aux champs"]
        }
        
        return tactics.get(species, ["Affût", "Approche", "Appel"])
    
    def _get_gear_recommendations(self, species: SpeciesCode) -> List[str]:
        """Obtient les recommandations d'équipement."""
        gear = {
            SpeciesCode.DEER: [
                "Appel grunt tube",
                "Bois de rattling",
                "Leurre de cerf",
                "Spray anti-odeur",
                "Jumelles 10x42"
            ],
            SpeciesCode.MOOSE: [
                "Cornet d'appel orignal",
                "Canot ou kayak",
                "Bottes cuissardes",
                "Jumelles longue portée",
                "GPS fiable"
            ],
            SpeciesCode.BEAR: [
                "Spray au poivre",
                "Appâts légaux",
                "Affût portable",
                "Lampe frontale",
                "Couteau de qualité"
            ],
            SpeciesCode.TURKEY: [
                "Appels à friction",
                "Appels à boîte",
                "Leurre de poule/mâle",
                "Camouflage complet",
                "Siège portable bas"
            ]
        }
        
        return gear.get(species, ["Équipement de base", "Jumelles", "GPS"])


# Singleton instance
species_model_engine = SpeciesModelEngine()
