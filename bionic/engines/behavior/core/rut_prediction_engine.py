"""
BIONIC™ Rut Prediction Engine
==============================
Moteur de prédiction du rut pour les cervidés.

Version: 1.0 - P0 Étape 1 (Fondations)

TODO Phase P0-2:
- Calibrer avec données historiques québécoises
- Intégrer données de photopériode précises
- Ajouter ajustements météo/températures
- Modèle ML pour prédiction des pics
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, date, timedelta
import sys

if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

from behavior.models.schemas import (
    RutPredictionInput,
    RutPredictionOutput,
    SpeciesCode,
    RutPhase,
    ActivityLevel
)

logger = logging.getLogger(__name__)


class RutPredictionEngine:
    """
    Moteur de prédiction du rut BIONIC™.
    
    Prédit les phases du rut basé sur:
    - Latitude (photopériode)
    - Données historiques de l'espèce
    - Conditions météorologiques
    - Température moyenne
    """
    
    # Dates moyennes du rut par latitude (Québec)
    # Format: latitude -> (pre_rut_start_doy, peak_breeding_doy, post_rut_end_doy)
    RUT_DATES_BY_LATITUDE = {
        # Sud du Québec (45-46°N)
        45: {"pre_rut": 285, "seeking": 295, "peak": 315, "post_rut": 335},
        46: {"pre_rut": 283, "seeking": 293, "peak": 313, "post_rut": 333},
        # Centre du Québec (47-48°N)
        47: {"pre_rut": 280, "seeking": 290, "peak": 310, "post_rut": 330},
        48: {"pre_rut": 278, "seeking": 288, "peak": 308, "post_rut": 328},
        # Nord du Québec (49-52°N)
        49: {"pre_rut": 275, "seeking": 285, "peak": 305, "post_rut": 325},
        50: {"pre_rut": 272, "seeking": 282, "peak": 302, "post_rut": 322},
        51: {"pre_rut": 268, "seeking": 278, "peak": 298, "post_rut": 318},
        52: {"pre_rut": 265, "seeking": 275, "peak": 295, "post_rut": 315}
    }
    
    # Noms français des phases
    PHASE_NAMES_FR = {
        RutPhase.PRE_RUT: "Pré-rut",
        RutPhase.SEEKING: "Recherche",
        RutPhase.CHASING: "Poursuite",
        RutPhase.BREEDING: "Reproduction",
        RutPhase.POST_RUT: "Post-rut",
        RutPhase.RECOVERY: "Récupération"
    }
    
    def __init__(self):
        self.version = "1.0.0"
        logger.info("BIONIC™ Rut Prediction Engine initialized (v%s)", self.version)
    
    async def analyze(
        self,
        input_data: RutPredictionInput,
        use_cache: bool = True
    ) -> RutPredictionOutput:
        """
        Prédit les phases du rut.
        """
        analysis_id = f"rut_{uuid.uuid4().hex[:12]}"
        year = input_data.year or datetime.now().year
        
        # Obtenir les dates du rut pour cette latitude
        rut_dates = self._get_rut_dates(input_data.latitude, year)
        
        # Déterminer la phase actuelle
        current_day = datetime.now().timetuple().tm_yday
        current_phase = self._determine_phase(current_day, rut_dates)
        
        # Calculer l'intensité
        phase_intensity = self._calculate_intensity(current_day, current_phase, rut_dates)
        
        # Calculer les jours jusqu'au pic
        days_to_peak = rut_dates["peak_date"].timetuple().tm_yday - current_day
        
        # Dates clés du pic
        peak_dates = self._get_peak_dates(rut_dates["peak_date"])
        
        # Comportements attendus
        expected_behaviors = self._get_expected_behaviors(current_phase, input_data.species)
        
        # Niveaux d'activité
        buck_activity = self._get_buck_activity(current_phase, phase_intensity)
        doe_activity = self._get_doe_activity(current_phase)
        
        # Tactiques recommandées
        tactics = self._get_recommended_tactics(current_phase, input_data.species)
        calling_times = self._get_best_calling_times(current_phase)
        
        return RutPredictionOutput(
            analysis_id=analysis_id,
            species=input_data.species,
            location={"lat": input_data.latitude, "lon": input_data.longitude},
            year=year,
            analyzed_at=datetime.now(timezone.utc),
            current_phase=current_phase,
            phase_name_fr=self.PHASE_NAMES_FR.get(current_phase, "Inconnue"),
            phase_intensity=round(phase_intensity, 2),
            pre_rut_start=rut_dates["pre_rut_date"],
            seeking_start=rut_dates["seeking_date"],
            peak_breeding=rut_dates["peak_date"],
            post_rut_start=rut_dates["post_rut_date"],
            days_to_peak=days_to_peak,
            peak_dates=peak_dates,
            expected_behaviors=expected_behaviors,
            buck_activity_level=buck_activity,
            doe_activity_level=doe_activity,
            recommended_tactics=tactics,
            best_calling_times=calling_times,
            confidence=0.80,
            from_cache=False
        )
    
    def _get_rut_dates(self, latitude: float, year: int) -> Dict[str, Any]:
        """Obtient les dates du rut pour une latitude donnée."""
        # Trouver la latitude la plus proche
        lat_rounded = min(52, max(45, round(latitude)))
        dates = self.RUT_DATES_BY_LATITUDE.get(lat_rounded, self.RUT_DATES_BY_LATITUDE[47])
        
        # Convertir en dates
        jan1 = date(year, 1, 1)
        
        return {
            "pre_rut_date": jan1 + timedelta(days=dates["pre_rut"] - 1),
            "seeking_date": jan1 + timedelta(days=dates["seeking"] - 1),
            "peak_date": jan1 + timedelta(days=dates["peak"] - 1),
            "post_rut_date": jan1 + timedelta(days=dates["post_rut"] - 1),
            "pre_rut_doy": dates["pre_rut"],
            "seeking_doy": dates["seeking"],
            "peak_doy": dates["peak"],
            "post_rut_doy": dates["post_rut"]
        }
    
    def _determine_phase(self, current_day: int, rut_dates: Dict) -> RutPhase:
        """Détermine la phase actuelle du rut."""
        pre_rut = rut_dates["pre_rut_doy"]
        seeking = rut_dates["seeking_doy"]
        peak = rut_dates["peak_doy"]
        post_rut = rut_dates["post_rut_doy"]
        
        if current_day < pre_rut:
            return RutPhase.PRE_RUT
        elif current_day < seeking:
            return RutPhase.PRE_RUT
        elif current_day < peak - 5:
            return RutPhase.SEEKING
        elif current_day < peak + 5:
            return RutPhase.BREEDING
        elif current_day < post_rut:
            return RutPhase.POST_RUT
        else:
            return RutPhase.RECOVERY
    
    def _calculate_intensity(
        self, 
        current_day: int, 
        phase: RutPhase,
        rut_dates: Dict
    ) -> float:
        """Calcule l'intensité de la phase actuelle."""
        peak = rut_dates["peak_doy"]
        
        # Plus proche du pic = plus intense
        days_from_peak = abs(current_day - peak)
        
        if phase == RutPhase.BREEDING:
            return min(1.0, max(0.0, 0.9 + (5 - days_from_peak) * 0.02))
        elif phase == RutPhase.SEEKING:
            return max(0.0, min(1.0, 0.6 + (1 - days_from_peak / 20) * 0.3))
        elif phase == RutPhase.POST_RUT:
            return max(0.0, min(1.0, 0.6 - days_from_peak * 0.02))
        elif phase == RutPhase.PRE_RUT:
            return max(0.0, min(1.0, 0.3 + (1 - days_from_peak / 30) * 0.2))
        else:
            return 0.2
    
    def _get_peak_dates(self, peak_date: date) -> List[date]:
        """Obtient les dates clés autour du pic."""
        return [
            peak_date - timedelta(days=3),
            peak_date - timedelta(days=1),
            peak_date,
            peak_date + timedelta(days=1),
            peak_date + timedelta(days=3)
        ]
    
    def _get_expected_behaviors(
        self, 
        phase: RutPhase,
        species: SpeciesCode
    ) -> List[str]:
        """Obtient les comportements attendus."""
        behaviors = {
            RutPhase.PRE_RUT: [
                "Marquage territorial (frottoirs, grattages)",
                "Établissement de la hiérarchie entre mâles",
                "Augmentation des déplacements",
                "Séparation des groupes de mâles"
            ],
            RutPhase.SEEKING: [
                "Recherche active des femelles",
                "Augmentation des vocalisations",
                "Réponse aux appels",
                "Déplacements fréquents entre zones"
            ],
            RutPhase.BREEDING: [
                "Poursuite intensive des femelles",
                "Combats entre mâles dominants",
                "Activité diurne accrue",
                "Alimentation réduite (mâles)",
                "Maximum de réponse aux appels"
            ],
            RutPhase.POST_RUT: [
                "Recherche de femelles non fécondées",
                "Reprise graduelle de l'alimentation",
                "Diminution de l'agressivité",
                "Retour vers les zones d'hivernage"
            ],
            RutPhase.RECOVERY: [
                "Repos et récupération",
                "Alimentation intensive",
                "Reformation des groupes",
                "Déplacements vers les ravages"
            ]
        }
        
        return behaviors.get(phase, ["Comportement variable selon les conditions"])
    
    def _get_buck_activity(self, phase: RutPhase, intensity: float) -> ActivityLevel:
        """Obtient le niveau d'activité des mâles."""
        if phase == RutPhase.BREEDING:
            return ActivityLevel.PEAK
        elif phase == RutPhase.SEEKING:
            return ActivityLevel.VERY_HIGH if intensity > 0.7 else ActivityLevel.HIGH
        elif phase == RutPhase.POST_RUT:
            return ActivityLevel.MODERATE
        elif phase == RutPhase.PRE_RUT:
            return ActivityLevel.HIGH
        else:
            return ActivityLevel.LOW
    
    def _get_doe_activity(self, phase: RutPhase) -> ActivityLevel:
        """Obtient le niveau d'activité des femelles."""
        if phase == RutPhase.BREEDING:
            return ActivityLevel.HIGH
        elif phase in [RutPhase.SEEKING, RutPhase.POST_RUT]:
            return ActivityLevel.MODERATE
        else:
            return ActivityLevel.LOW
    
    def _get_recommended_tactics(
        self, 
        phase: RutPhase,
        species: SpeciesCode
    ) -> List[str]:
        """Obtient les tactiques recommandées."""
        tactics = {
            RutPhase.PRE_RUT: [
                "Repérez les frottoirs frais et grattages",
                "Installez-vous près des corridors de déplacement",
                "Utilisez des leurres visuels (appelants)",
                "Appels légers de mâle dominant"
            ],
            RutPhase.SEEKING: [
                "Appels de femelle en chaleur",
                "Positionnez-vous entre les zones de repos et d'alimentation",
                "Rattling modéré efficace",
                "Soyez mobile si pas de résultat après 2h"
            ],
            RutPhase.BREEDING: [
                "Appels agressifs (grunt, snort-wheeze)",
                "Rattling intense - simuler un combat",
                "Restez en place - les mâles sont en mouvement constant",
                "Chassez toute la journée - activité diurne",
                "Leurres de femelle accroupie très efficaces"
            ],
            RutPhase.POST_RUT: [
                "Ciblez les sources de nourriture",
                "Appels de femelle plus subtils",
                "Les mâles cherchent les retardataires",
                "Patience - activité moins prévisible"
            ],
            RutPhase.RECOVERY: [
                "Concentration sur l'alimentation",
                "Techniques classiques d'embuscade",
                "Repérage des zones d'hivernage"
            ]
        }
        
        return tactics.get(phase, ["Adapter les tactiques aux conditions"])
    
    def _get_best_calling_times(self, phase: RutPhase) -> List[str]:
        """Obtient les meilleurs moments pour les appels."""
        calling_times = {
            RutPhase.PRE_RUT: [
                "Aube (6h-8h) - marquage territorial",
                "Crépuscule (17h-19h) - déplacements"
            ],
            RutPhase.SEEKING: [
                "Aube (5h30-8h) - recherche active",
                "Mi-journée (10h-14h) - mâles en mouvement",
                "Crépuscule (16h-19h) - période clé"
            ],
            RutPhase.BREEDING: [
                "Toute la journée - activité maximale",
                "Pic: 8h-10h et 14h-16h",
                "Ne pas hésiter à appeler à midi"
            ],
            RutPhase.POST_RUT: [
                "Aube et crépuscule principalement",
                "Appels plus espacés et subtils"
            ]
        }
        
        return calling_times.get(phase, ["Aube et crépuscule"])


# Singleton instance
rut_prediction_engine = RutPredictionEngine()
