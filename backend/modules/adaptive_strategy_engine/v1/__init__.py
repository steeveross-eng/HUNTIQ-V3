"""Adaptive Strategy Engine Module v1

Real-time adaptive hunting strategies.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/v1/adaptive", tags=["Adaptive Strategy Engine"])


class AdaptiveStrategy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    base_strategy: str
    adaptations: List[str] = []
    confidence: float = Field(ge=0, le=100)
    conditions_met: List[str] = []
    recommendations: List[str] = []


STRATEGY_ADAPTATIONS = {
    "wind_shift": {
        "trigger": "wind_direction_change > 45°",
        "adaptations": [
            "Repositionner pour rester sous le vent",
            "Déplacer vers un poste alternatif",
            "Réduire les mouvements pendant le changement"
        ]
    },
    "temperature_drop": {
        "trigger": "temperature_drop > 5°C en 2h",
        "adaptations": [
            "Attendre l'activité accrue post-front",
            "Se positionner près des zones d'alimentation",
            "Prolonger la session de chasse"
        ]
    },
    "rain_start": {
        "trigger": "precipitation_start",
        "adaptations": [
            "Profiter de la couverture olfactive",
            "Se rapprocher des sentiers",
            "Préparer le retrait si pluie forte"
        ]
    },
    "no_activity": {
        "trigger": "no_sighting > 2h",
        "adaptations": [
            "Changer de position",
            "Vérifier le vent",
            "Utiliser un appel léger",
            "Se déplacer vers un autre secteur"
        ]
    },
    "pressure_change": {
        "trigger": "pressure_change > 5 hPa",
        "adaptations": [
            "Maximiser le temps de chasse",
            "Se positionner sur les corridors de déplacement",
            "Être prêt pour une activité soudaine"
        ]
    }
}


def generate_adaptive_strategy(current_conditions: Dict, session_data: Dict) -> AdaptiveStrategy:
    """Generate adaptive strategy based on conditions and session"""
    adaptations = []
    conditions_met = []
    recommendations = []
    confidence = 70.0
    
    # Check wind
    if current_conditions.get("wind_change", 0) > 45:
        adaptations.extend(STRATEGY_ADAPTATIONS["wind_shift"]["adaptations"])
        conditions_met.append("Changement de vent détecté")
        confidence -= 10
    
    # Check temperature
    if current_conditions.get("temp_drop", 0) > 5:
        adaptations.extend(STRATEGY_ADAPTATIONS["temperature_drop"]["adaptations"][:2])
        conditions_met.append("Chute de température")
        confidence += 15
    
    # Check activity
    if session_data.get("sightings", 0) == 0 and session_data.get("duration_hours", 0) > 2:
        adaptations.extend(STRATEGY_ADAPTATIONS["no_activity"]["adaptations"])
        conditions_met.append("Pas d'activité prolongée")
        recommendations.append("Considérer un changement de position")
    
    # Check pressure
    if abs(current_conditions.get("pressure_change", 0)) > 5:
        adaptations.extend(STRATEGY_ADAPTATIONS["pressure_change"]["adaptations"])
        conditions_met.append("Variation de pression significative")
        confidence += 10
    
    if not adaptations:
        adaptations = ["Maintenir la stratégie actuelle", "Rester patient et attentif"]
        recommendations = ["Conditions stables - continuez votre approche"]
    
    return AdaptiveStrategy(
        base_strategy=session_data.get("strategy", "Affût standard"),
        adaptations=list(set(adaptations)),
        confidence=min(100, max(0, confidence)),
        conditions_met=conditions_met,
        recommendations=recommendations if recommendations else ["Suivre les adaptations suggérées"]
    )


@router.get("/")
async def adaptive_strategy_info():
    return {
        "module": "adaptive_strategy_engine",
        "version": "1.0.0",
        "description": "Real-time adaptive hunting strategies",
        "features": ["Condition monitoring", "Strategy adaptation", "Feedback learning", "Real-time recommendations"],
        "adaptation_triggers": list(STRATEGY_ADAPTATIONS.keys())
    }


@router.post("/strategy")
async def get_adaptive_strategy(
    wind_change: float = Query(0, description="Wind direction change in degrees"),
    temp_drop: float = Query(0, description="Temperature drop in °C"),
    pressure_change: float = Query(0, description="Pressure change in hPa"),
    sightings: int = Query(0, ge=0),
    duration_hours: float = Query(1, ge=0),
    current_strategy: str = Query("Affût standard")
):
    conditions = {
        "wind_change": wind_change,
        "temp_drop": temp_drop,
        "pressure_change": pressure_change
    }
    session = {
        "sightings": sightings,
        "duration_hours": duration_hours,
        "strategy": current_strategy
    }
    
    strategy = generate_adaptive_strategy(conditions, session)
    
    return {
        "success": True,
        "adaptive_strategy": strategy.model_dump(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/adjust")
async def request_adjustment(
    current_situation: str,
    problem: str = Query(..., description="What's not working"),
    species: str = Query("deer")
):
    # Generate contextual adjustments
    adjustments = {
        "no_sightings": [
            "Vérifiez votre position par rapport au vent",
            "Déplacez-vous de 200-300m",
            "Changez d'altitude ou de couvert",
            "Essayez un appel léger"
        ],
        "spooked_game": [
            "Restez immobile 30+ minutes",
            "Le gibier reviendra probablement",
            "Évitez tout mouvement",
            "Planifiez une sortie discrète si nécessaire"
        ],
        "wrong_position": [
            "Attendez une opportunité de mouvement",
            "Déplacez-vous uniquement si le vent change",
            "Identifiez un meilleur poste pour la prochaine fois"
        ]
    }
    
    problem_key = "no_sightings"
    if "spook" in problem.lower() or "fuit" in problem.lower():
        problem_key = "spooked_game"
    elif "position" in problem.lower() or "vent" in problem.lower():
        problem_key = "wrong_position"
    
    return {
        "success": True,
        "situation": current_situation,
        "problem": problem,
        "adjustments": adjustments.get(problem_key, adjustments["no_sightings"]),
        "priority_action": adjustments.get(problem_key, adjustments["no_sightings"])[0]
    }


@router.post("/feedback")
async def record_feedback(
    strategy_id: str,
    success: bool,
    notes: str = "",
    sightings: int = 0,
    harvest: bool = False
):
    # Store feedback for learning (in production, this would update ML models)
    return {
        "success": True,
        "message": "Feedback recorded",
        "strategy_id": strategy_id,
        "outcome": "success" if success else "no_success",
        "will_improve": "future recommendations"
    }


@router.get("/triggers")
async def list_adaptation_triggers():
    return {
        "success": True,
        "triggers": [
            {"id": k, "trigger": v["trigger"], "adaptations_count": len(v["adaptations"])}
            for k, v in STRATEGY_ADAPTATIONS.items()
        ]
    }
