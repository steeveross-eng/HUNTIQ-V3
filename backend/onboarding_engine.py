"""
HUNTIQ V3 - Onboarding Engine
Flow d'inscription et configuration du profil chasseur
Module isolé - Architecture modulaire stricte
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, timezone
import uuid
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

onboarding_router = APIRouter(prefix="/api/onboarding", tags=["Onboarding"])

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

client = None
db = None

async def get_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    return db

# ============================================
# CONFIGURATION ONBOARDING
# ============================================

ONBOARDING_STEPS = [
    {
        "id": "welcome",
        "title": "Bienvenue sur HUNTIQ",
        "description": "Votre plateforme de chasse intelligente",
        "type": "info",
        "order": 1
    },
    {
        "id": "profile",
        "title": "Votre profil chasseur",
        "description": "Personnalisez votre expérience",
        "type": "form",
        "order": 2,
        "fields": ["target_species", "region", "experience_level", "hunting_objectives"]
    },
    {
        "id": "preferences",
        "title": "Vos préférences",
        "description": "Configurez vos notifications et paramètres",
        "type": "form",
        "order": 3,
        "fields": ["language", "notifications_weather", "notifications_activity", "notifications_news"]
    },
    {
        "id": "features",
        "title": "Découvrez nos fonctionnalités",
        "description": "Tour rapide des outils HUNTIQ",
        "type": "tour",
        "order": 4,
        "features": ["analyzer", "territory", "marketplace", "freemium"]
    },
    {
        "id": "complete",
        "title": "Vous êtes prêt!",
        "description": "Commencez votre aventure de chasse",
        "type": "completion",
        "order": 5
    }
]

TARGET_SPECIES = [
    {"id": "deer", "name": "Cerf de Virginie", "icon": "🦌"},
    {"id": "moose", "name": "Orignal", "icon": "🫎"},
    {"id": "bear", "name": "Ours noir", "icon": "🐻"},
    {"id": "wild_boar", "name": "Sanglier", "icon": "🐗"},
    {"id": "turkey", "name": "Dindon sauvage", "icon": "🦃"},
    {"id": "waterfowl", "name": "Sauvagine", "icon": "🦆"},
    {"id": "small_game", "name": "Petit gibier", "icon": "🐰"},
    {"id": "other", "name": "Autre", "icon": "🎯"}
]

REGIONS_QUEBEC = [
    {"id": "montreal", "name": "Montréal et environs"},
    {"id": "quebec_city", "name": "Québec et environs"},
    {"id": "laurentides", "name": "Laurentides"},
    {"id": "lanaudiere", "name": "Lanaudière"},
    {"id": "mauricie", "name": "Mauricie"},
    {"id": "outaouais", "name": "Outaouais"},
    {"id": "saguenay", "name": "Saguenay-Lac-Saint-Jean"},
    {"id": "abitibi", "name": "Abitibi-Témiscamingue"},
    {"id": "cote_nord", "name": "Côte-Nord"},
    {"id": "bas_st_laurent", "name": "Bas-Saint-Laurent"},
    {"id": "gaspesie", "name": "Gaspésie"},
    {"id": "estrie", "name": "Estrie"},
    {"id": "monteregie", "name": "Montérégie"},
    {"id": "chaudiere_appalaches", "name": "Chaudière-Appalaches"},
    {"id": "centre_quebec", "name": "Centre-du-Québec"},
    {"id": "nord_quebec", "name": "Nord-du-Québec"}
]

EXPERIENCE_LEVELS = [
    {"id": "beginner", "name": "Débutant", "description": "Moins de 2 ans d'expérience"},
    {"id": "intermediate", "name": "Intermédiaire", "description": "2-5 ans d'expérience"},
    {"id": "advanced", "name": "Avancé", "description": "5-10 ans d'expérience"},
    {"id": "expert", "name": "Expert", "description": "Plus de 10 ans d'expérience"}
]

HUNTING_OBJECTIVES = [
    {"id": "recreation", "name": "Loisir et détente"},
    {"id": "food", "name": "Approvisionnement alimentaire"},
    {"id": "trophy", "name": "Trophée et accomplissement"},
    {"id": "conservation", "name": "Gestion et conservation"},
    {"id": "social", "name": "Activité sociale et familiale"},
    {"id": "learning", "name": "Apprentissage et perfectionnement"}
]

# ============================================
# PYDANTIC MODELS
# ============================================

class HunterProfile(BaseModel):
    target_species: List[str] = []
    region: Optional[str] = None
    experience_level: Optional[str] = None
    hunting_objectives: List[str] = []

class UserPreferences(BaseModel):
    language: str = "fr"
    notifications_weather: bool = True
    notifications_activity: bool = True
    notifications_news: bool = False

class OnboardingProgress(BaseModel):
    user_id: str
    current_step: int = 1
    completed_steps: List[str] = []
    hunter_profile: Optional[HunterProfile] = None
    preferences: Optional[UserPreferences] = None
    is_complete: bool = False
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class StepCompletionRequest(BaseModel):
    user_id: str
    step_id: str
    data: Optional[dict] = None

# ============================================
# API ENDPOINTS
# ============================================

@onboarding_router.get("/config")
async def get_onboarding_config():
    """Retourne la configuration complète de l'onboarding"""
    return {
        "steps": ONBOARDING_STEPS,
        "options": {
            "target_species": TARGET_SPECIES,
            "regions": REGIONS_QUEBEC,
            "experience_levels": EXPERIENCE_LEVELS,
            "hunting_objectives": HUNTING_OBJECTIVES
        }
    }

@onboarding_router.get("/progress/{user_id}")
async def get_onboarding_progress(user_id: str):
    """Récupère la progression d'onboarding d'un utilisateur"""
    database = await get_db()
    
    progress = await database.onboarding_progress.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    if not progress:
        # Créer une nouvelle progression
        progress = {
            "user_id": user_id,
            "current_step": 1,
            "completed_steps": [],
            "hunter_profile": None,
            "preferences": None,
            "is_complete": False,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        await database.onboarding_progress.insert_one(progress)
    
    return progress

@onboarding_router.post("/start/{user_id}")
async def start_onboarding(user_id: str):
    """Démarre l'onboarding pour un utilisateur"""
    database = await get_db()
    
    existing = await database.onboarding_progress.find_one({"user_id": user_id})
    
    if existing and existing.get("is_complete"):
        return {
            "message": "Onboarding déjà complété",
            "is_complete": True,
            "progress": existing
        }
    
    if not existing:
        progress = {
            "user_id": user_id,
            "current_step": 1,
            "completed_steps": [],
            "hunter_profile": None,
            "preferences": None,
            "is_complete": False,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        await database.onboarding_progress.insert_one(progress)
    else:
        progress = existing
    
    return {
        "message": "Onboarding démarré",
        "steps": ONBOARDING_STEPS,
        "current_step": progress.get("current_step", 1),
        "progress": progress
    }

@onboarding_router.post("/step/complete")
async def complete_step(request: StepCompletionRequest):
    """Marque une étape comme complétée"""
    database = await get_db()
    
    progress = await database.onboarding_progress.find_one({"user_id": request.user_id})
    
    if not progress:
        raise HTTPException(status_code=404, detail="Onboarding non démarré")
    
    if progress.get("is_complete"):
        return {"message": "Onboarding déjà complété", "is_complete": True}
    
    # Valider l'étape
    step_config = next((s for s in ONBOARDING_STEPS if s["id"] == request.step_id), None)
    if not step_config:
        raise HTTPException(status_code=400, detail=f"Étape inconnue: {request.step_id}")
    
    update_data = {
        "$addToSet": {"completed_steps": request.step_id},
        "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
    }
    
    # Traiter les données selon l'étape
    if request.step_id == "profile" and request.data:
        hunter_profile = {
            "target_species": request.data.get("target_species", []),
            "region": request.data.get("region"),
            "experience_level": request.data.get("experience_level"),
            "hunting_objectives": request.data.get("hunting_objectives", [])
        }
        update_data["$set"]["hunter_profile"] = hunter_profile
    
    elif request.step_id == "preferences" and request.data:
        preferences = {
            "language": request.data.get("language", "fr"),
            "notifications_weather": request.data.get("notifications_weather", True),
            "notifications_activity": request.data.get("notifications_activity", True),
            "notifications_news": request.data.get("notifications_news", False)
        }
        update_data["$set"]["preferences"] = preferences
    
    # Calculer la prochaine étape
    completed_steps = progress.get("completed_steps", [])
    if request.step_id not in completed_steps:
        completed_steps.append(request.step_id)
    
    current_step_order = step_config["order"]
    next_step_order = current_step_order + 1
    
    if next_step_order <= len(ONBOARDING_STEPS):
        update_data["$set"]["current_step"] = next_step_order
    
    # Vérifier si complété
    if request.step_id == "complete" or len(completed_steps) >= len(ONBOARDING_STEPS):
        update_data["$set"]["is_complete"] = True
        update_data["$set"]["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await database.onboarding_progress.update_one(
        {"user_id": request.user_id},
        update_data
    )
    
    # Récupérer le prochain step
    next_step = None
    if next_step_order <= len(ONBOARDING_STEPS):
        next_step = next((s for s in ONBOARDING_STEPS if s["order"] == next_step_order), None)
    
    return {
        "success": True,
        "completed_step": request.step_id,
        "next_step": next_step,
        "is_complete": request.step_id == "complete" or len(completed_steps) >= len(ONBOARDING_STEPS)
    }

@onboarding_router.post("/skip/{user_id}")
async def skip_onboarding(user_id: str):
    """Permet de sauter l'onboarding"""
    database = await get_db()
    
    await database.onboarding_progress.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "is_complete": True,
                "skipped": True,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    return {"success": True, "message": "Onboarding sauté"}

@onboarding_router.get("/profile/{user_id}")
async def get_hunter_profile(user_id: str):
    """Récupère le profil chasseur d'un utilisateur"""
    database = await get_db()
    
    progress = await database.onboarding_progress.find_one(
        {"user_id": user_id},
        {"_id": 0, "hunter_profile": 1, "preferences": 1}
    )
    
    if not progress:
        return {"hunter_profile": None, "preferences": None}
    
    return {
        "hunter_profile": progress.get("hunter_profile"),
        "preferences": progress.get("preferences")
    }

@onboarding_router.put("/profile/{user_id}")
async def update_hunter_profile(user_id: str, profile: HunterProfile):
    """Met à jour le profil chasseur"""
    database = await get_db()
    
    await database.onboarding_progress.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "hunter_profile": profile.model_dump(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    return {"success": True, "profile": profile.model_dump()}

@onboarding_router.put("/preferences/{user_id}")
async def update_preferences(user_id: str, preferences: UserPreferences):
    """Met à jour les préférences utilisateur"""
    database = await get_db()
    
    await database.onboarding_progress.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "preferences": preferences.model_dump(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    return {"success": True, "preferences": preferences.model_dump()}

logger.info("Onboarding Engine initialized")
