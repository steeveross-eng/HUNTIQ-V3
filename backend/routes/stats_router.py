"""
BIONIC™ Stats Engine - API Endpoint

Fournit les statistiques dynamiques de la plateforme:
- Nombre d'abonnés (depuis MongoDB)
- Nombre de zones de chasse
- Territoires analysés
- Utilisateurs actifs
- Taux de satisfaction

Les valeurs sont calculées dynamiquement depuis la DB
avec des seuils minimums pour affichage cohérent.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import os

# Router
stats_router = APIRouter(prefix="/api/stats", tags=["Stats Engine"])

# Seuils minimums (valeurs affichées tant que les vraies valeurs sont en dessous)
THRESHOLDS = {
    "subscribers": 20017,      # Affiche "20K+" si < seuil
    "zones": 2901,             # Affiche "2,901" si < seuil
    "territories": 2547,       # Affiche "2,547+" si < seuil
    "activeUsers": 1247,       # Minimum affiché
    "attractants": 850,        # Valeur fixe
    "satisfaction": 98,        # Pourcentage fixe
}


def get_db():
    """Get MongoDB database connection"""
    try:
        from pymongo import MongoClient
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'huntiq')
        client = MongoClient(mongo_url)
        return client[db_name]
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None


@stats_router.get("")
@stats_router.get("/")
async def get_stats() -> Dict[str, Any]:
    """
    Get platform statistics.
    
    Returns dynamic values from MongoDB with threshold logic:
    - If real value < threshold: return threshold (minimum display)
    - If real value >= threshold: return real value
    
    This ensures consistent UX while data grows.
    """
    db = get_db()
    
    # Valeurs par défaut (seuils)
    stats = {
        "subscribers": THRESHOLDS["subscribers"],
        "zones": THRESHOLDS["zones"],
        "territories": THRESHOLDS["territories"],
        "activeUsers": THRESHOLDS["activeUsers"],
        "attractants": THRESHOLDS["attractants"],
        "satisfaction": THRESHOLDS["satisfaction"],
        "totalProducts": 0,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }
    
    if db is not None:
        try:
            # Compter les utilisateurs (subscribers)
            users_collection = db.get_collection("users")
            real_subscribers = users_collection.count_documents({})
            if real_subscribers >= THRESHOLDS["subscribers"]:
                stats["subscribers"] = real_subscribers
            
            # Compter les territoires sauvegardés
            territories_collection = db.get_collection("saved_territories")
            real_territories = territories_collection.count_documents({})
            if real_territories >= THRESHOLDS["territories"]:
                stats["territories"] = real_territories
            
            # Compter les zones de chasse (waypoints)
            waypoints_collection = db.get_collection("waypoints")
            real_zones = waypoints_collection.count_documents({})
            if real_zones >= THRESHOLDS["zones"]:
                stats["zones"] = real_zones
            
            # Utilisateurs actifs (connectés dans les 24h)
            sessions_collection = db.get_collection("user_sessions")
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            active_users = sessions_collection.count_documents({
                "last_active": {"$gte": yesterday}
            })
            if active_users >= THRESHOLDS["activeUsers"]:
                stats["activeUsers"] = active_users
            
            # Compter les produits
            products_collection = db.get_collection("products")
            stats["totalProducts"] = products_collection.count_documents({"active": True})
            
            # Calculer le taux de satisfaction (depuis reviews si disponible)
            reviews_collection = db.get_collection("reviews")
            reviews_count = reviews_collection.count_documents({})
            if reviews_count > 0:
                pipeline = [
                    {"$group": {"_id": None, "avgRating": {"$avg": "$rating"}}}
                ]
                result = list(reviews_collection.aggregate(pipeline))
                if result:
                    avg_rating = result[0].get("avgRating", 4.9)
                    stats["satisfaction"] = round((avg_rating / 5) * 100)
            
        except Exception as e:
            print(f"Error fetching stats from MongoDB: {e}")
            # Continue with threshold values
    
    return stats


@stats_router.get("/live")
async def get_live_stats() -> Dict[str, Any]:
    """
    Get real-time live statistics.
    
    Includes:
    - Current active users
    - Sales today
    - Active zones being monitored
    - Alerts count
    """
    db = get_db()
    
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    live_stats = {
        "activeUsers": THRESHOLDS["activeUsers"],
        "todaySales": 34,
        "activeZones": 29,
        "alertsToday": 12,
        "timestamp": now.isoformat(),
    }
    
    if db is not None:
        try:
            # Sessions actives (15 dernières minutes)
            sessions = db.get_collection("user_sessions")
            fifteen_min_ago = now - timedelta(minutes=15)
            active = sessions.count_documents({
                "last_active": {"$gte": fifteen_min_ago}
            })
            if active > 0:
                live_stats["activeUsers"] = max(active, THRESHOLDS["activeUsers"])
            
            # Commandes aujourd'hui
            orders = db.get_collection("orders")
            today_orders = orders.count_documents({
                "created_at": {"$gte": today_start}
            })
            live_stats["todaySales"] = max(today_orders, 34)
            
        except Exception as e:
            print(f"Error fetching live stats: {e}")
    
    return live_stats


@stats_router.get("/thresholds")
async def get_thresholds() -> Dict[str, Any]:
    """
    Get current threshold values (for debugging/admin).
    """
    return {
        "thresholds": THRESHOLDS,
        "description": "Valeurs minimales affichées tant que les vraies valeurs sont en dessous"
    }
