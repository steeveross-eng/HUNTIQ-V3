"""
HUNTIQ V3 - Tutorials Engine
Tutoriels interactifs modulaires
Module isolé - Architecture modulaire stricte
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

tutorials_router = APIRouter(prefix="/api/tutorials", tags=["Tutorials"])

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
# TUTORIELS - CONFIGURATION
# ============================================

TUTORIALS = [
    {
        "id": "analyzer_bionic",
        "title": "Analyzer BIONIC™",
        "description": "Apprenez à analyser les attractants avec notre technologie exclusive",
        "icon": "flask",
        "duration_minutes": 5,
        "difficulty": "beginner",
        "category": "core",
        "steps": [
            {
                "id": "intro",
                "title": "Introduction à l'Analyzer",
                "content": "L'Analyzer BIONIC™ utilise 13 critères scientifiques pour évaluer les attractants de chasse.",
                "type": "info",
                "highlight_element": None
            },
            {
                "id": "select_product",
                "title": "Sélectionner un produit",
                "content": "Cliquez sur 'Analyze' dans le menu principal, puis sélectionnez un produit à analyser.",
                "type": "action",
                "highlight_element": "[data-testid='nav-analyze']",
                "action_required": "navigate"
            },
            {
                "id": "view_criteria",
                "title": "Comprendre les critères",
                "content": "Chaque produit est évalué sur 13 critères: durée d'attraction, appétence, puissance olfactive, etc.",
                "type": "info",
                "highlight_element": "[data-testid='criteria-list']"
            },
            {
                "id": "ai_analysis",
                "title": "Analyse IA avancée",
                "content": "Utilisez l'analyse IA pour obtenir des recommandations personnalisées selon votre contexte de chasse.",
                "type": "action",
                "highlight_element": "[data-testid='ai-analysis-btn']",
                "action_required": "click"
            },
            {
                "id": "complete",
                "title": "Félicitations!",
                "content": "Vous maîtrisez maintenant l'Analyzer BIONIC™. Analysez vos produits pour optimiser vos chasses!",
                "type": "completion"
            }
        ]
    },
    {
        "id": "territory_map",
        "title": "Carte Territory",
        "description": "Maîtrisez la navigation et la gestion de vos territoires de chasse",
        "icon": "map",
        "duration_minutes": 7,
        "difficulty": "beginner",
        "category": "core",
        "steps": [
            {
                "id": "intro",
                "title": "Bienvenue sur Territory",
                "content": "La carte Territory vous permet de visualiser et gérer vos zones de chasse au Québec.",
                "type": "info",
                "highlight_element": None
            },
            {
                "id": "navigate_map",
                "title": "Navigation sur la carte",
                "content": "Utilisez la souris pour zoomer et déplacer la carte. Les zones colorées représentent différents types de territoires.",
                "type": "action",
                "highlight_element": "[data-testid='territory-map']",
                "action_required": "interact"
            },
            {
                "id": "add_waypoint",
                "title": "Ajouter un waypoint",
                "content": "Cliquez sur la carte pour ajouter un point d'intérêt. FREE: 2 waypoints max.",
                "type": "action",
                "highlight_element": "[data-testid='add-waypoint-btn']",
                "action_required": "click"
            },
            {
                "id": "view_zones",
                "title": "Zones de chasse",
                "content": "Les zones sont codées par couleur: ZEC, Pourvoiries, Terres publiques, Réserves fauniques.",
                "type": "info",
                "highlight_element": "[data-testid='zone-legend']"
            },
            {
                "id": "hotspots_privacy",
                "title": "Confidentialité des hotspots",
                "content": "⚠️ Vos hotspots sont 100% privés. Personne d'autre ne peut les voir, même les autres membres PRO.",
                "type": "warning",
                "highlight_element": None
            },
            {
                "id": "complete",
                "title": "Vous maîtrisez Territory!",
                "content": "Explorez le Québec et planifiez vos prochaines chasses avec précision.",
                "type": "completion"
            }
        ]
    },
    {
        "id": "marketplace",
        "title": "Hunt Marketplace",
        "description": "Apprenez à publier et acheter sur notre marketplace de chasse",
        "icon": "store",
        "duration_minutes": 6,
        "difficulty": "beginner",
        "category": "core",
        "steps": [
            {
                "id": "intro",
                "title": "Bienvenue sur le Marketplace",
                "content": "Le Hunt Marketplace est votre place de marché pour équipements, terrains et services de chasse.",
                "type": "info",
                "highlight_element": None
            },
            {
                "id": "browse_listings",
                "title": "Parcourir les annonces",
                "content": "Utilisez les filtres pour trouver exactement ce que vous cherchez: catégorie, prix, localisation.",
                "type": "action",
                "highlight_element": "[data-testid='marketplace-filters']",
                "action_required": "interact"
            },
            {
                "id": "create_listing",
                "title": "Créer une annonce",
                "content": "Cliquez sur 'Publier une annonce' pour vendre vos équipements. FREE: 2 annonces max.",
                "type": "action",
                "highlight_element": "[data-testid='create-listing-btn']",
                "action_required": "click"
            },
            {
                "id": "seller_info",
                "title": "Informations vendeur",
                "content": "En mode FREE, les coordonnées vendeur sont partiellement masquées. Passez PRO pour un accès complet.",
                "type": "info",
                "highlight_element": "[data-testid='seller-contact']"
            },
            {
                "id": "hotspot_rules",
                "title": "Vente de hotspots",
                "content": "⚠️ Les hotspots vendus sont anonymisés (zone 10x10km). Localisation exacte débloquée après achat (500$).",
                "type": "warning",
                "highlight_element": None
            },
            {
                "id": "complete",
                "title": "Prêt pour le Marketplace!",
                "content": "Achetez, vendez et échangez en toute confiance sur HUNTIQ.",
                "type": "completion"
            }
        ]
    }
]

# ============================================
# PYDANTIC MODELS
# ============================================

class TutorialProgress(BaseModel):
    user_id: str
    tutorial_id: str
    current_step: int = 0
    completed_steps: List[str] = []
    is_complete: bool = False
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class StepProgressRequest(BaseModel):
    user_id: str
    tutorial_id: str
    step_id: str

# ============================================
# API ENDPOINTS
# ============================================

@tutorials_router.get("/list")
async def get_tutorials_list():
    """Retourne la liste des tutoriels disponibles"""
    tutorials_summary = []
    for tutorial in TUTORIALS:
        tutorials_summary.append({
            "id": tutorial["id"],
            "title": tutorial["title"],
            "description": tutorial["description"],
            "icon": tutorial["icon"],
            "duration_minutes": tutorial["duration_minutes"],
            "difficulty": tutorial["difficulty"],
            "category": tutorial["category"],
            "steps_count": len(tutorial["steps"])
        })
    
    return {
        "tutorials": tutorials_summary,
        "categories": {
            "core": [t for t in tutorials_summary if t["category"] == "core"],
            "advanced": [t for t in tutorials_summary if t["category"] == "advanced"]
        }
    }

@tutorials_router.get("/detail/{tutorial_id}")
async def get_tutorial_detail(tutorial_id: str):
    """Retourne les détails complets d'un tutoriel"""
    tutorial = next((t for t in TUTORIALS if t["id"] == tutorial_id), None)
    
    if not tutorial:
        raise HTTPException(status_code=404, detail=f"Tutoriel non trouvé: {tutorial_id}")
    
    return tutorial

@tutorials_router.get("/progress/{user_id}")
async def get_user_tutorial_progress(user_id: str):
    """Récupère la progression de tous les tutoriels pour un utilisateur"""
    database = await get_db()
    
    progress_list = await database.tutorial_progress.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(100)
    
    # Créer un dictionnaire de progression
    progress_dict = {p["tutorial_id"]: p for p in progress_list}
    
    # Ajouter les infos de progression à chaque tutoriel
    result = []
    for tutorial in TUTORIALS:
        prog = progress_dict.get(tutorial["id"], {})
        result.append({
            "tutorial_id": tutorial["id"],
            "title": tutorial["title"],
            "steps_count": len(tutorial["steps"]),
            "completed_steps": len(prog.get("completed_steps", [])),
            "is_complete": prog.get("is_complete", False),
            "current_step": prog.get("current_step", 0),
            "progress_percent": round(len(prog.get("completed_steps", [])) / len(tutorial["steps"]) * 100) if tutorial["steps"] else 0
        })
    
    total_complete = sum(1 for r in result if r["is_complete"])
    
    return {
        "user_id": user_id,
        "tutorials": result,
        "total_tutorials": len(TUTORIALS),
        "completed_tutorials": total_complete,
        "overall_progress": round(total_complete / len(TUTORIALS) * 100) if TUTORIALS else 0
    }

@tutorials_router.post("/start")
async def start_tutorial(request: StepProgressRequest):
    """Démarre un tutoriel pour un utilisateur"""
    database = await get_db()
    
    tutorial = next((t for t in TUTORIALS if t["id"] == request.tutorial_id), None)
    if not tutorial:
        raise HTTPException(status_code=404, detail=f"Tutoriel non trouvé: {request.tutorial_id}")
    
    existing = await database.tutorial_progress.find_one({
        "user_id": request.user_id,
        "tutorial_id": request.tutorial_id
    })
    
    if existing and existing.get("is_complete"):
        return {
            "message": "Tutoriel déjà complété",
            "is_complete": True,
            "tutorial": tutorial
        }
    
    if not existing:
        progress = {
            "user_id": request.user_id,
            "tutorial_id": request.tutorial_id,
            "current_step": 0,
            "completed_steps": [],
            "is_complete": False,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        await database.tutorial_progress.insert_one(progress)
    
    return {
        "message": "Tutoriel démarré",
        "tutorial": tutorial,
        "current_step": 0,
        "first_step": tutorial["steps"][0] if tutorial["steps"] else None
    }

@tutorials_router.post("/step/complete")
async def complete_tutorial_step(request: StepProgressRequest):
    """Marque une étape de tutoriel comme complétée"""
    database = await get_db()
    
    tutorial = next((t for t in TUTORIALS if t["id"] == request.tutorial_id), None)
    if not tutorial:
        raise HTTPException(status_code=404, detail=f"Tutoriel non trouvé: {request.tutorial_id}")
    
    step = next((s for s in tutorial["steps"] if s["id"] == request.step_id), None)
    if not step:
        raise HTTPException(status_code=400, detail=f"Étape non trouvée: {request.step_id}")
    
    # Récupérer ou créer la progression
    progress = await database.tutorial_progress.find_one({
        "user_id": request.user_id,
        "tutorial_id": request.tutorial_id
    })
    
    if not progress:
        progress = {
            "user_id": request.user_id,
            "tutorial_id": request.tutorial_id,
            "current_step": 0,
            "completed_steps": [],
            "is_complete": False,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        await database.tutorial_progress.insert_one(progress)
    
    completed_steps = progress.get("completed_steps", [])
    if request.step_id not in completed_steps:
        completed_steps.append(request.step_id)
    
    # Calculer la prochaine étape
    current_index = next((i for i, s in enumerate(tutorial["steps"]) if s["id"] == request.step_id), 0)
    next_index = current_index + 1
    
    is_complete = next_index >= len(tutorial["steps"])
    
    update_data = {
        "$set": {
            "completed_steps": completed_steps,
            "current_step": next_index if not is_complete else current_index,
            "is_complete": is_complete,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    if is_complete:
        update_data["$set"]["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await database.tutorial_progress.update_one(
        {"user_id": request.user_id, "tutorial_id": request.tutorial_id},
        update_data
    )
    
    next_step = None
    if not is_complete and next_index < len(tutorial["steps"]):
        next_step = tutorial["steps"][next_index]
    
    return {
        "success": True,
        "completed_step": request.step_id,
        "next_step": next_step,
        "is_complete": is_complete,
        "progress_percent": round(len(completed_steps) / len(tutorial["steps"]) * 100)
    }

@tutorials_router.post("/reset/{tutorial_id}")
async def reset_tutorial(tutorial_id: str, user_id: str):
    """Réinitialise un tutoriel pour un utilisateur"""
    database = await get_db()
    
    await database.tutorial_progress.update_one(
        {"user_id": user_id, "tutorial_id": tutorial_id},
        {
            "$set": {
                "current_step": 0,
                "completed_steps": [],
                "is_complete": False,
                "completed_at": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"success": True, "message": "Tutoriel réinitialisé"}

@tutorials_router.get("/recommended/{user_id}")
async def get_recommended_tutorials(user_id: str):
    """Retourne les tutoriels recommandés basés sur la progression"""
    database = await get_db()
    
    progress_list = await database.tutorial_progress.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(100)
    
    completed_ids = [p["tutorial_id"] for p in progress_list if p.get("is_complete")]
    in_progress_ids = [p["tutorial_id"] for p in progress_list if not p.get("is_complete") and p.get("current_step", 0) > 0]
    
    recommended = []
    
    # D'abord les tutoriels en cours
    for tid in in_progress_ids:
        tutorial = next((t for t in TUTORIALS if t["id"] == tid), None)
        if tutorial:
            recommended.append({
                "tutorial": tutorial,
                "reason": "En cours",
                "priority": 1
            })
    
    # Ensuite les tutoriels non commencés (core d'abord)
    for tutorial in TUTORIALS:
        if tutorial["id"] not in completed_ids and tutorial["id"] not in in_progress_ids:
            priority = 2 if tutorial["category"] == "core" else 3
            recommended.append({
                "tutorial": tutorial,
                "reason": "Recommandé" if tutorial["category"] == "core" else "Suggéré",
                "priority": priority
            })
    
    # Trier par priorité
    recommended.sort(key=lambda x: x["priority"])
    
    return {
        "recommended": recommended[:3],  # Top 3 recommandations
        "all_incomplete": [r for r in recommended]
    }

logger.info("Tutorials Engine initialized")
