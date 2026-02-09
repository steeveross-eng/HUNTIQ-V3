"""Progression Engine Module v1

Gamification and user progression system.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import os
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1/progression", tags=["Progression Engine"])


LEVELS = [
    {"level": 1, "name": "Débutant", "xp_required": 0, "icon": "🌱"},
    {"level": 2, "name": "Apprenti", "xp_required": 100, "icon": "🎯"},
    {"level": 3, "name": "Chasseur", "xp_required": 300, "icon": "🦌"},
    {"level": 4, "name": "Expert", "xp_required": 600, "icon": "🏹"},
    {"level": 5, "name": "Maître", "xp_required": 1000, "icon": "👑"},
    {"level": 6, "name": "Légende", "xp_required": 2000, "icon": "⭐"},
]

BADGES = [
    {"id": "first_analysis", "name": "Première Analyse", "description": "Effectuer votre première analyse", "xp_reward": 25, "icon": "🔬"},
    {"id": "ten_analyses", "name": "Analyste", "description": "Effectuer 10 analyses", "xp_reward": 100, "icon": "📊"},
    {"id": "perfect_score", "name": "Score Parfait", "description": "Obtenir un score de 9.5+", "xp_reward": 50, "icon": "💯"},
    {"id": "early_bird", "name": "Lève-Tôt", "description": "Analyser avant 6h du matin", "xp_reward": 30, "icon": "🌅"},
    {"id": "all_species", "name": "Multi-Espèces", "description": "Analyser pour toutes les espèces", "xp_reward": 75, "icon": "🦌"},
    {"id": "weather_master", "name": "Météorologue", "description": "Utiliser les prévisions météo 20 fois", "xp_reward": 50, "icon": "🌤️"},
    {"id": "social_hunter", "name": "Chasseur Social", "description": "Rejoindre un groupe de chasse", "xp_reward": 40, "icon": "👥"},
    {"id": "spot_sharer", "name": "Partageur", "description": "Partager 5 spots de chasse", "xp_reward": 60, "icon": "📍"},
]

CHALLENGES = [
    {"id": "weekly_analysis", "name": "Analyste de la Semaine", "description": "Effectuer 5 analyses cette semaine", "xp_reward": 75, "duration": "weekly"},
    {"id": "rut_season", "name": "Spécial Rut", "description": "Analyser 3 produits pour le rut", "xp_reward": 100, "duration": "seasonal"},
    {"id": "perfect_week", "name": "Semaine Parfaite", "description": "Se connecter 7 jours consécutifs", "xp_reward": 50, "duration": "weekly"},
]


class UserProgression(BaseModel):
    user_id: str
    xp: int = 0
    level: int = 1
    badges: List[str] = []
    challenges_completed: List[str] = []
    stats: Dict[str, int] = Field(default_factory=lambda: {
        "analyses_count": 0,
        "login_streak": 0,
        "groups_joined": 0,
        "spots_shared": 0
    })


class ProgressionService:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    def calculate_level(self, xp: int) -> Dict:
        current_level = LEVELS[0]
        for level in LEVELS:
            if xp >= level["xp_required"]:
                current_level = level
            else:
                break
        
        next_level = None
        for level in LEVELS:
            if level["xp_required"] > xp:
                next_level = level
                break
        
        return {
            "current": current_level,
            "next": next_level,
            "progress_to_next": ((xp - current_level["xp_required"]) / (next_level["xp_required"] - current_level["xp_required"]) * 100) if next_level else 100
        }
    
    async def get_user_progression(self, user_id: str) -> Dict:
        prog = self.db.user_progression.find_one({"user_id": user_id}, {"_id": 0})
        if not prog:
            prog = UserProgression(user_id=user_id).model_dump()
            self.db.user_progression.insert_one(prog)
        return prog
    
    async def add_xp(self, user_id: str, amount: int, reason: str) -> Dict:
        prog = await self.get_user_progression(user_id)
        new_xp = prog.get("xp", 0) + amount
        level_info = self.calculate_level(new_xp)
        
        self.db.user_progression.update_one(
            {"user_id": user_id},
            {"$set": {"xp": new_xp, "level": level_info["current"]["level"]}}
        )
        
        return {
            "xp_added": amount,
            "reason": reason,
            "total_xp": new_xp,
            "level": level_info["current"]["level"],
            "level_up": level_info["current"]["level"] > prog.get("level", 1)
        }
    
    async def award_badge(self, user_id: str, badge_id: str) -> Dict:
        badge = next((b for b in BADGES if b["id"] == badge_id), None)
        if not badge:
            return {"success": False, "error": "Badge not found"}
        
        prog = await self.get_user_progression(user_id)
        if badge_id in prog.get("badges", []):
            return {"success": False, "error": "Badge already earned"}
        
        self.db.user_progression.update_one(
            {"user_id": user_id},
            {"$push": {"badges": badge_id}, "$inc": {"xp": badge["xp_reward"]}}
        )
        
        return {"success": True, "badge": badge, "xp_reward": badge["xp_reward"]}


_service = ProgressionService()


@router.get("/")
async def progression_engine_info():
    return {
        "module": "progression_engine",
        "version": "1.0.0",
        "description": "Gamification and progression system",
        "features": ["XP system", "Levels", "Badges", "Challenges", "Leaderboard"],
        "total_levels": len(LEVELS),
        "total_badges": len(BADGES),
        "active_challenges": len(CHALLENGES)
    }


@router.get("/user/{user_id}")
async def get_user_progression(user_id: str):
    prog = await _service.get_user_progression(user_id)
    level_info = _service.calculate_level(prog.get("xp", 0))
    
    return {
        "success": True,
        "user_id": user_id,
        "xp": prog.get("xp", 0),
        "level": level_info["current"],
        "next_level": level_info["next"],
        "progress_percent": round(level_info["progress_to_next"], 1),
        "badges_earned": prog.get("badges", []),
        "stats": prog.get("stats", {})
    }


@router.post("/user/{user_id}/xp")
async def add_xp(user_id: str, amount: int = Query(..., ge=1, le=500), reason: str = "Action"):
    result = await _service.add_xp(user_id, amount, reason)
    return {"success": True, **result}


@router.post("/user/{user_id}/badge/{badge_id}")
async def award_badge(user_id: str, badge_id: str):
    result = await _service.award_badge(user_id, badge_id)
    return result


@router.get("/badges")
async def list_badges():
    return {"success": True, "badges": BADGES}


@router.get("/challenges")
async def list_challenges(active_only: bool = Query(True)):
    return {"success": True, "challenges": CHALLENGES}


@router.get("/levels")
async def list_levels():
    return {"success": True, "levels": LEVELS}


@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(10, ge=1, le=100)):
    # Get top users by XP
    cursor = _service.db.user_progression.find({}, {"_id": 0}).sort("xp", -1).limit(limit)
    leaderboard = list(cursor)
    
    return {
        "success": True,
        "leaderboard": [
            {"rank": i+1, "user_id": u["user_id"], "xp": u.get("xp", 0), "level": u.get("level", 1)}
            for i, u in enumerate(leaderboard)
        ]
    }


@router.get("/rewards")
async def list_rewards():
    return {
        "success": True,
        "rewards": [
            {"level": 2, "reward": "Accès aux analyses avancées"},
            {"level": 3, "reward": "Recommandations personnalisées"},
            {"level": 4, "reward": "Alertes météo prioritaires"},
            {"level": 5, "reward": "Badge Maître exclusif"},
            {"level": 6, "reward": "Statut Légende + avantages VIP"}
        ]
    }
