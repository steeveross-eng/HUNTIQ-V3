"""
HUNTIQ V3 - Freemium Engine
Gestion des quotas, limites et fonctionnalités PRO
Module isolé - Architecture modulaire stricte
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Literal
from datetime import datetime, timezone, timedelta
import uuid
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

freemium_router = APIRouter(prefix="/api/freemium", tags=["Freemium"])

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
# QUOTAS OFFICIELS - HUNTIQ V3
# ============================================

FREE_QUOTAS = {
    "marketplace_listings": {
        "limit": 2,
        "period": "unlimited",
        "description": "Annonces Marketplace (infos vendeur floutées)",
        "pro_value": "unlimited"
    },
    "analyzer_ai": {
        "limit": 1,
        "period": "week",
        "description": "Analyses IA BIONIC™ (résultats partiels)",
        "pro_value": "unlimited"
    },
    "territories": {
        "limit": 1,
        "period": "unlimited",
        "description": "Territoires enregistrés",
        "pro_value": "unlimited"
    },
    "waypoints": {
        "limit": 2,
        "period": "unlimited",
        "description": "Points d'intérêt",
        "pro_value": "unlimited"
    },
    "hotspots_import": {
        "limit": 1,
        "period": "unlimited",
        "description": "Import de hotspots personnels",
        "pro_value": "unlimited"
    },
    "notifications": {
        "limit": 1,
        "period": "unlimited",
        "description": "Météo générale uniquement",
        "pro_value": "all"
    }
}

PRO_FEATURES = [
    "Analyses IA illimitées avec résultats complets",
    "Territoires et waypoints illimités",
    "Outils avancés de planification",
    "Conditions optimales de chasse",
    "Packs hotspots premium",
    "Notifications avancées (activité, météo détaillée)",
    "Badge PRO et visibilité accrue",
    "Support prioritaire"
]

# ============================================
# PYDANTIC MODELS
# ============================================

class UserQuotas(BaseModel):
    user_id: str
    is_pro: bool = False
    pro_until: Optional[datetime] = None
    pro_type: Optional[Literal["monthly", "yearly", "lifetime"]] = None
    quotas_used: Dict[str, int] = {}
    quotas_reset_at: Dict[str, str] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuotaCheckResponse(BaseModel):
    feature: str
    allowed: bool
    used: int
    limit: int
    remaining: int
    is_pro: bool
    reset_at: Optional[str] = None
    upgrade_message: Optional[str] = None

class QuotaUsageRequest(BaseModel):
    user_id: str
    feature: str

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_week_start():
    """Retourne le début de la semaine actuelle (lundi)"""
    now = datetime.now(timezone.utc)
    days_since_monday = now.weekday()
    week_start = now - timedelta(days=days_since_monday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

def should_reset_quota(feature: str, reset_at: Optional[str]) -> bool:
    """Vérifie si le quota doit être réinitialisé"""
    quota_config = FREE_QUOTAS.get(feature)
    if not quota_config or quota_config["period"] == "unlimited":
        return False
    
    if not reset_at:
        return True
    
    try:
        reset_datetime = datetime.fromisoformat(reset_at)
        now = datetime.now(timezone.utc)
        
        if quota_config["period"] == "week":
            week_start = get_week_start()
            return reset_datetime < week_start
        elif quota_config["period"] == "day":
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return reset_datetime < today_start
        elif quota_config["period"] == "month":
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return reset_datetime < month_start
    except:
        return True
    
    return False

def get_next_reset(period: str) -> str:
    """Retourne la date du prochain reset"""
    now = datetime.now(timezone.utc)
    
    if period == "week":
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_reset = now + timedelta(days=days_until_monday)
        return next_reset.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    elif period == "day":
        next_reset = now + timedelta(days=1)
        return next_reset.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    elif period == "month":
        if now.month == 12:
            next_reset = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_reset = now.replace(month=now.month + 1, day=1)
        return next_reset.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    return None

# ============================================
# API ENDPOINTS
# ============================================

@freemium_router.get("/quotas")
async def get_quotas_config():
    """Retourne la configuration des quotas FREE vs PRO"""
    return {
        "free_quotas": FREE_QUOTAS,
        "pro_features": PRO_FEATURES,
        "pricing": {
            "monthly": {"amount": 7.99, "currency": "CAD", "trial_days": 7},
            "yearly": {"amount": 79.00, "currency": "CAD", "trial_days": 7},
            "lifetime": {"amount": 199.00, "currency": "CAD"}
        }
    }

@freemium_router.get("/user/{user_id}")
async def get_user_quotas(user_id: str):
    """Récupère les quotas d'un utilisateur"""
    database = await get_db()
    
    user_quotas = await database.user_quotas.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    if not user_quotas:
        # Créer les quotas par défaut
        user_quotas = {
            "user_id": user_id,
            "is_pro": False,
            "pro_until": None,
            "pro_type": None,
            "quotas_used": {},
            "quotas_reset_at": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await database.user_quotas.insert_one(user_quotas)
    
    # Vérifier si PRO a expiré
    if user_quotas.get("is_pro") and user_quotas.get("pro_until"):
        try:
            pro_until = user_quotas["pro_until"]
            if isinstance(pro_until, str):
                pro_until = datetime.fromisoformat(pro_until)
            
            if pro_until < datetime.now(timezone.utc) and user_quotas.get("pro_type") != "lifetime":
                # PRO expiré - réinitialiser
                await database.user_quotas.update_one(
                    {"user_id": user_id},
                    {"$set": {"is_pro": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                user_quotas["is_pro"] = False
        except:
            pass
    
    # Calculer les quotas restants
    quotas_status = {}
    for feature, config in FREE_QUOTAS.items():
        used = user_quotas.get("quotas_used", {}).get(feature, 0)
        reset_at = user_quotas.get("quotas_reset_at", {}).get(feature)
        
        # Reset si nécessaire
        if should_reset_quota(feature, reset_at):
            used = 0
        
        limit = config["limit"] if not user_quotas.get("is_pro") else 999999
        remaining = max(0, limit - used)
        
        quotas_status[feature] = {
            "used": used,
            "limit": limit if not user_quotas.get("is_pro") else "unlimited",
            "remaining": remaining if not user_quotas.get("is_pro") else "unlimited",
            "description": config["description"],
            "period": config["period"],
            "reset_at": get_next_reset(config["period"]) if config["period"] != "unlimited" else None
        }
    
    return {
        "user_id": user_id,
        "is_pro": user_quotas.get("is_pro", False),
        "pro_until": user_quotas.get("pro_until"),
        "pro_type": user_quotas.get("pro_type"),
        "quotas": quotas_status
    }

@freemium_router.post("/check")
async def check_quota(request: QuotaUsageRequest):
    """Vérifie si l'utilisateur peut utiliser une fonctionnalité"""
    database = await get_db()
    
    if request.feature not in FREE_QUOTAS:
        raise HTTPException(status_code=400, detail=f"Fonctionnalité inconnue: {request.feature}")
    
    config = FREE_QUOTAS[request.feature]
    
    user_quotas = await database.user_quotas.find_one(
        {"user_id": request.user_id},
        {"_id": 0}
    )
    
    # Utilisateur PRO = toujours autorisé
    is_pro = user_quotas.get("is_pro", False) if user_quotas else False
    
    # Vérifier expiration PRO
    if is_pro and user_quotas.get("pro_until"):
        try:
            pro_until = user_quotas["pro_until"]
            if isinstance(pro_until, str):
                pro_until = datetime.fromisoformat(pro_until)
            if pro_until < datetime.now(timezone.utc) and user_quotas.get("pro_type") != "lifetime":
                is_pro = False
        except:
            pass
    
    if is_pro:
        return QuotaCheckResponse(
            feature=request.feature,
            allowed=True,
            used=0,
            limit=999999,
            remaining=999999,
            is_pro=True,
            reset_at=None,
            upgrade_message=None
        )
    
    # Utilisateur FREE - vérifier quota
    used = 0
    if user_quotas:
        used = user_quotas.get("quotas_used", {}).get(request.feature, 0)
        reset_at = user_quotas.get("quotas_reset_at", {}).get(request.feature)
        
        if should_reset_quota(request.feature, reset_at):
            used = 0
    
    limit = config["limit"]
    remaining = max(0, limit - used)
    allowed = remaining > 0
    
    upgrade_message = None
    if not allowed:
        upgrade_message = f"Vous avez atteint votre limite de {config['description'].lower()}. Passez PRO pour un accès illimité!"
    
    return QuotaCheckResponse(
        feature=request.feature,
        allowed=allowed,
        used=used,
        limit=limit,
        remaining=remaining,
        is_pro=False,
        reset_at=get_next_reset(config["period"]) if config["period"] != "unlimited" else None,
        upgrade_message=upgrade_message
    )

@freemium_router.post("/use")
async def use_quota(request: QuotaUsageRequest):
    """Consomme un quota pour une fonctionnalité"""
    database = await get_db()
    
    # Vérifier d'abord
    check_result = await check_quota(request)
    
    if not check_result.allowed:
        raise HTTPException(
            status_code=403, 
            detail={
                "error": "quota_exceeded",
                "message": check_result.upgrade_message,
                "feature": request.feature
            }
        )
    
    if check_result.is_pro:
        return {"success": True, "is_pro": True, "message": "Accès PRO illimité"}
    
    # Consommer le quota
    config = FREE_QUOTAS[request.feature]
    now = datetime.now(timezone.utc)
    
    await database.user_quotas.update_one(
        {"user_id": request.user_id},
        {
            "$inc": {f"quotas_used.{request.feature}": 1},
            "$set": {
                f"quotas_reset_at.{request.feature}": now.isoformat(),
                "updated_at": now.isoformat()
            }
        },
        upsert=True
    )
    
    return {
        "success": True,
        "is_pro": False,
        "feature": request.feature,
        "used": check_result.used + 1,
        "remaining": check_result.remaining - 1,
        "reset_at": get_next_reset(config["period"]) if config["period"] != "unlimited" else None
    }

@freemium_router.post("/upgrade/{user_id}")
async def upgrade_to_pro(user_id: str, plan: Literal["monthly", "yearly", "lifetime"]):
    """Upgrade un utilisateur vers PRO (appelé après paiement réussi)"""
    database = await get_db()
    
    now = datetime.now(timezone.utc)
    
    if plan == "monthly":
        pro_until = now + timedelta(days=30)
    elif plan == "yearly":
        pro_until = now + timedelta(days=365)
    else:  # lifetime
        pro_until = now + timedelta(days=36500)  # ~100 ans
    
    await database.user_quotas.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "is_pro": True,
                "pro_until": pro_until.isoformat(),
                "pro_type": plan,
                "updated_at": now.isoformat()
            }
        },
        upsert=True
    )
    
    logger.info(f"User {user_id} upgraded to PRO ({plan})")
    
    return {
        "success": True,
        "user_id": user_id,
        "is_pro": True,
        "pro_type": plan,
        "pro_until": pro_until.isoformat()
    }

@freemium_router.get("/status/{user_id}")
async def get_pro_status(user_id: str):
    """Récupère le statut PRO d'un utilisateur"""
    database = await get_db()
    
    user_quotas = await database.user_quotas.find_one(
        {"user_id": user_id},
        {"_id": 0}
    )
    
    if not user_quotas:
        return {
            "user_id": user_id,
            "is_pro": False,
            "pro_type": None,
            "pro_until": None,
            "days_remaining": 0
        }
    
    is_pro = user_quotas.get("is_pro", False)
    pro_until = user_quotas.get("pro_until")
    pro_type = user_quotas.get("pro_type")
    
    days_remaining = 0
    if is_pro and pro_until:
        try:
            if isinstance(pro_until, str):
                pro_until_dt = datetime.fromisoformat(pro_until)
            else:
                pro_until_dt = pro_until
            
            delta = pro_until_dt - datetime.now(timezone.utc)
            days_remaining = max(0, delta.days)
            
            if days_remaining == 0 and pro_type != "lifetime":
                is_pro = False
        except:
            pass
    
    if pro_type == "lifetime":
        days_remaining = 36500
    
    return {
        "user_id": user_id,
        "is_pro": is_pro,
        "pro_type": pro_type,
        "pro_until": pro_until,
        "days_remaining": days_remaining
    }

logger.info("Freemium Engine initialized")
