"""
HUNTIQ V3 - Admin Top Users Module
Vue complète des membres les plus actifs, engagés et rentables
Module isolé - Architecture modulaire stricte
Accès restreint aux comptes administrateurs autorisés
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime, timezone, timedelta
import csv
import io
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

admin_users_router = APIRouter(prefix="/api/admin/users", tags=["Admin Users"])

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
# PYDANTIC MODELS
# ============================================

class TopUserEntry(BaseModel):
    user_id: str
    name: str
    email: str
    status: str  # FREE, PRO_MONTHLY, PRO_YEARLY, PRO_LIFETIME
    global_activity_score: int = 0
    last_activity: Optional[str] = None
    total_actions: int = 0
    credits_accumulated: int = 0
    network_potential: int = 0  # pré-Affiliate Prime
    region: Optional[str] = None
    user_type: str = "hunter"  # hunter, outfitter, supplier, group
    registration_date: Optional[str] = None
    
    # Category-specific metrics
    marketplace_purchases: int = 0
    marketplace_sales: int = 0
    marketplace_interactions: int = 0
    analyzer_ai_uses: int = 0
    analyzer_products_scanned: int = 0
    territories_created: int = 0
    waypoints_created: int = 0
    heatmaps_generated: int = 0
    suppliers_added: int = 0
    outfitters_added: int = 0
    valid_reports: int = 0
    invitations_sent: int = 0
    referrals_completed: int = 0
    tutorial_progress: int = 0
    onboarding_completed: bool = False

class TopUsersResponse(BaseModel):
    category: str
    users: List[TopUserEntry]
    total_count: int
    page: int
    page_size: int

class TopUsersFilters(BaseModel):
    subscription_type: Optional[str] = None
    region: Optional[str] = None
    registration_after: Optional[str] = None
    registration_before: Optional[str] = None
    min_activity_level: Optional[int] = None
    user_type: Optional[str] = None

# ============================================
# HELPER FUNCTIONS
# ============================================

def calculate_activity_score(user_data: dict) -> int:
    """Calculate global activity score based on all metrics"""
    score = 0
    
    # Marketplace activity (weight: 3)
    score += user_data.get("marketplace_purchases", 0) * 5
    score += user_data.get("marketplace_sales", 0) * 5
    score += user_data.get("marketplace_interactions", 0) * 2
    
    # Analyzer activity (weight: 4)
    score += user_data.get("analyzer_ai_uses", 0) * 10
    score += user_data.get("analyzer_products_scanned", 0) * 3
    
    # Territory activity (weight: 4)
    score += user_data.get("territories_created", 0) * 8
    score += user_data.get("waypoints_created", 0) * 4
    score += user_data.get("heatmaps_generated", 0) * 6
    
    # Contributions (weight: 5)
    score += user_data.get("suppliers_added", 0) * 15
    score += user_data.get("outfitters_added", 0) * 15
    score += user_data.get("valid_reports", 0) * 10
    
    # Growth drivers (weight: 5)
    score += user_data.get("invitations_sent", 0) * 5
    score += user_data.get("referrals_completed", 0) * 20
    
    # Engagement (weight: 2)
    score += user_data.get("tutorial_progress", 0) * 2
    score += 50 if user_data.get("onboarding_completed") else 0
    
    # PRO status bonus
    status = user_data.get("status", "FREE")
    if status == "PRO_LIFETIME":
        score += 100
    elif status == "PRO_YEARLY":
        score += 50
    elif status == "PRO_MONTHLY":
        score += 25
    
    return score

def get_user_status(user_data: dict) -> str:
    """Determine user PRO status"""
    quotas = user_data.get("quotas", {})
    if quotas.get("pro_type") == "lifetime":
        return "PRO_LIFETIME"
    elif quotas.get("pro_type") == "yearly":
        return "PRO_YEARLY"
    elif quotas.get("pro_type") == "monthly":
        return "PRO_MONTHLY"
    elif quotas.get("is_pro"):
        return "PRO"
    return "FREE"

async def get_user_metrics(database, user_id: str) -> dict:
    """Aggregate all metrics for a user"""
    metrics = {
        "marketplace_purchases": 0,
        "marketplace_sales": 0,
        "marketplace_interactions": 0,
        "analyzer_ai_uses": 0,
        "analyzer_products_scanned": 0,
        "territories_created": 0,
        "waypoints_created": 0,
        "heatmaps_generated": 0,
        "suppliers_added": 0,
        "outfitters_added": 0,
        "valid_reports": 0,
        "invitations_sent": 0,
        "referrals_completed": 0,
        "tutorial_progress": 0,
        "onboarding_completed": False,
        "total_actions": 0
    }
    
    # Get user activity from various collections
    try:
        # Marketplace orders
        purchases = await database.orders.count_documents({"buyer_id": user_id})
        sales = await database.orders.count_documents({"seller_id": user_id})
        metrics["marketplace_purchases"] = purchases
        metrics["marketplace_sales"] = sales
        
        # Listings
        listings = await database.listings.count_documents({"seller_id": user_id})
        metrics["marketplace_interactions"] = listings
        
        # Analyzer usage
        analyses = await database.analyses.count_documents({"user_id": user_id})
        metrics["analyzer_ai_uses"] = analyses
        metrics["analyzer_products_scanned"] = analyses
        
        # Territory
        territories = await database.user_territories.count_documents({"user_id": user_id})
        waypoints = await database.waypoints.count_documents({"user_id": user_id})
        metrics["territories_created"] = territories
        metrics["waypoints_created"] = waypoints
        
        # Contributions
        suppliers = await database.suppliers.count_documents({"added_by": user_id})
        outfitters = await database.outfitters.count_documents({"added_by": user_id})
        metrics["suppliers_added"] = suppliers
        metrics["outfitters_added"] = outfitters
        
        # Referrals
        referrals = await database.referrals.count_documents({"referrer_id": user_id, "status": "completed"})
        invitations = await database.referrals.count_documents({"referrer_id": user_id})
        metrics["referrals_completed"] = referrals
        metrics["invitations_sent"] = invitations
        
        # Tutorial progress
        tutorial_progress = await database.tutorial_progress.find_one({"user_id": user_id})
        if tutorial_progress:
            completed_tutorials = len([t for t in await database.tutorial_progress.find(
                {"user_id": user_id, "is_complete": True}
            ).to_list(100)])
            metrics["tutorial_progress"] = completed_tutorials * 33  # 3 tutorials = 99%
        
        # Onboarding
        onboarding = await database.onboarding_progress.find_one({"user_id": user_id})
        metrics["onboarding_completed"] = onboarding.get("is_complete", False) if onboarding else False
        
        # Total actions
        metrics["total_actions"] = sum([
            purchases, sales, listings, analyses, territories, waypoints,
            suppliers, outfitters, referrals
        ])
        
    except Exception as e:
        logger.warning(f"Error getting metrics for user {user_id}: {e}")
    
    return metrics

# ============================================
# API ENDPOINTS
# ============================================

@admin_users_router.get("/top")
async def get_top_users(
    category: str = Query("global", description="Category: global, free, pro_monthly, pro_yearly, pro_lifetime, contributors, marketplace, analyzer, territory, growth, pro_boost_candidates, mastery_candidates"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=10, le=100),
    subscription_type: Optional[str] = None,
    region: Optional[str] = None,
    user_type: Optional[str] = None,
    min_activity: Optional[int] = None,
    sort_by: str = Query("score", description="Sort by: score, last_activity, total_actions, credits"),
    sort_order: str = Query("desc", description="Sort order: asc, desc")
):
    """
    Get top users by category with filtering and sorting
    Categories:
    - global: Top Users (activité globale)
    - free: Top FREE Users (engagement Freemium)
    - pro_monthly: Top PRO Mensuel
    - pro_yearly: Top PRO Annuel
    - pro_lifetime: Top PRO À Vie
    - contributors: Top Contributeurs (fournisseurs, pourvoiries, signalements)
    - marketplace: Top Marketplace Users
    - analyzer: Top Analyzer Users
    - territory: Top Territory Users
    - growth: Top Growth Drivers (invitations, référencements)
    - pro_boost_candidates: Top Candidates PRO Boost
    - mastery_candidates: Top Candidates Mastery Levels
    """
    database = await get_db()
    
    # Build query based on category
    query = {}
    
    if category == "free":
        query["$or"] = [
            {"quotas.is_pro": False},
            {"quotas.is_pro": {"$exists": False}}
        ]
    elif category == "pro_monthly":
        query["quotas.pro_type"] = "monthly"
        query["quotas.is_pro"] = True
    elif category == "pro_yearly":
        query["quotas.pro_type"] = "yearly"
        query["quotas.is_pro"] = True
    elif category == "pro_lifetime":
        query["quotas.pro_type"] = "lifetime"
        query["quotas.is_pro"] = True
    
    # Apply filters
    if subscription_type:
        if subscription_type == "FREE":
            query["$or"] = [{"quotas.is_pro": False}, {"quotas.is_pro": {"$exists": False}}]
        elif subscription_type.startswith("PRO"):
            query["quotas.is_pro"] = True
            if "_" in subscription_type:
                plan_type = subscription_type.split("_")[1].lower()
                query["quotas.pro_type"] = plan_type
    
    if region:
        query["profile.region"] = region
    
    if user_type:
        query["user_type"] = user_type
    
    # Get all users with their data
    users_cursor = database.users.find(query, {"_id": 0, "password": 0})
    users_list = await users_cursor.to_list(1000)
    
    # Enrich with metrics and quotas
    enriched_users = []
    for user in users_list:
        user_id = user.get("id") or user.get("user_id") or str(user.get("_id", ""))
        
        # Get quota data
        quota_data = await database.user_quotas.find_one({"user_id": user_id}, {"_id": 0})
        user["quotas"] = quota_data or {}
        
        # Get metrics
        metrics = await get_user_metrics(database, user_id)
        
        # Get profile data
        profile = await database.onboarding_progress.find_one({"user_id": user_id}, {"_id": 0})
        hunter_profile = profile.get("hunter_profile", {}) if profile else {}
        
        # Build entry
        entry = TopUserEntry(
            user_id=user_id,
            name=user.get("name", user.get("username", "Unknown")),
            email=user.get("email", ""),
            status=get_user_status(user),
            global_activity_score=calculate_activity_score({**user, **metrics}),
            last_activity=user.get("last_activity") or user.get("updated_at"),
            total_actions=metrics["total_actions"],
            credits_accumulated=user.get("credits", 0),
            network_potential=metrics["invitations_sent"] + metrics["referrals_completed"] * 3,
            region=hunter_profile.get("region") or user.get("region"),
            user_type=user.get("user_type", "hunter"),
            registration_date=user.get("created_at"),
            marketplace_purchases=metrics["marketplace_purchases"],
            marketplace_sales=metrics["marketplace_sales"],
            marketplace_interactions=metrics["marketplace_interactions"],
            analyzer_ai_uses=metrics["analyzer_ai_uses"],
            analyzer_products_scanned=metrics["analyzer_products_scanned"],
            territories_created=metrics["territories_created"],
            waypoints_created=metrics["waypoints_created"],
            heatmaps_generated=metrics["heatmaps_generated"],
            suppliers_added=metrics["suppliers_added"],
            outfitters_added=metrics["outfitters_added"],
            valid_reports=metrics["valid_reports"],
            invitations_sent=metrics["invitations_sent"],
            referrals_completed=metrics["referrals_completed"],
            tutorial_progress=metrics["tutorial_progress"],
            onboarding_completed=metrics["onboarding_completed"]
        )
        
        # Filter by category-specific criteria
        if category == "contributors" and (entry.suppliers_added + entry.outfitters_added + entry.valid_reports) == 0:
            continue
        elif category == "marketplace" and (entry.marketplace_purchases + entry.marketplace_sales) == 0:
            continue
        elif category == "analyzer" and entry.analyzer_ai_uses == 0:
            continue
        elif category == "territory" and (entry.territories_created + entry.waypoints_created) == 0:
            continue
        elif category == "growth" and (entry.invitations_sent + entry.referrals_completed) == 0:
            continue
        elif category == "pro_boost_candidates":
            # Users with high activity but not PRO
            if entry.status != "FREE" or entry.global_activity_score < 50:
                continue
        elif category == "mastery_candidates":
            # Users with high engagement potential
            if entry.tutorial_progress < 66 and not entry.onboarding_completed:
                continue
        
        # Apply min_activity filter
        if min_activity and entry.global_activity_score < min_activity:
            continue
        
        enriched_users.append(entry)
    
    # Sort users
    sort_key_map = {
        "score": "global_activity_score",
        "last_activity": "last_activity",
        "total_actions": "total_actions",
        "credits": "credits_accumulated"
    }
    sort_key = sort_key_map.get(sort_by, "global_activity_score")
    reverse = sort_order == "desc"
    
    enriched_users.sort(key=lambda x: getattr(x, sort_key) or 0, reverse=reverse)
    
    # Paginate
    total_count = len(enriched_users)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_users = enriched_users[start_idx:end_idx]
    
    return TopUsersResponse(
        category=category,
        users=paginated_users,
        total_count=total_count,
        page=page,
        page_size=page_size
    )

@admin_users_router.get("/top/categories")
async def get_top_users_categories():
    """Get all available categories for top users view"""
    return {
        "categories": [
            {"id": "global", "name": "Top Users", "description": "Activité globale"},
            {"id": "free", "name": "Top FREE Users", "description": "Engagement Freemium"},
            {"id": "pro_monthly", "name": "Top PRO Mensuel", "description": "Abonnés mensuels"},
            {"id": "pro_yearly", "name": "Top PRO Annuel", "description": "Abonnés annuels"},
            {"id": "pro_lifetime", "name": "Top PRO À Vie", "description": "Membres à vie"},
            {"id": "contributors", "name": "Top Contributeurs", "description": "Fournisseurs, pourvoiries, signalements"},
            {"id": "marketplace", "name": "Top Marketplace", "description": "Achats, ventes, interactions"},
            {"id": "analyzer", "name": "Top Analyzer", "description": "Analyses IA et produits"},
            {"id": "territory", "name": "Top Territory", "description": "Territoires, waypoints, heatmaps"},
            {"id": "growth", "name": "Top Growth Drivers", "description": "Invitations, référencements"},
            {"id": "pro_boost_candidates", "name": "Candidats PRO Boost", "description": "Crédits accumulés, usage intensif"},
            {"id": "mastery_candidates", "name": "Candidats Mastery", "description": "Progression potentielle"}
        ]
    }

@admin_users_router.get("/top/export")
async def export_top_users_csv(
    category: str = Query("global"),
    subscription_type: Optional[str] = None,
    region: Optional[str] = None
):
    """
    Export top users to CSV (admin only)
    Returns CSV file content
    """
    # Get users data
    data = await get_top_users(
        category=category,
        page=1,
        page_size=1000,
        subscription_type=subscription_type,
        region=region
    )
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "User ID", "Nom", "Email", "Statut", "Score Activité", "Dernière Activité",
        "Actions Totales", "Crédits", "Réseau Potentiel", "Région", "Type Utilisateur",
        "Date Inscription", "Achats Marketplace", "Ventes Marketplace", "Analyses IA",
        "Territoires", "Waypoints", "Fournisseurs Ajoutés", "Parrainages Complétés",
        "Progression Tutoriels", "Onboarding Complété"
    ])
    
    # Data rows
    for user in data.users:
        writer.writerow([
            user.user_id, user.name, user.email, user.status, user.global_activity_score,
            user.last_activity, user.total_actions, user.credits_accumulated,
            user.network_potential, user.region, user.user_type, user.registration_date,
            user.marketplace_purchases, user.marketplace_sales, user.analyzer_ai_uses,
            user.territories_created, user.waypoints_created, user.suppliers_added,
            user.referrals_completed, user.tutorial_progress, user.onboarding_completed
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return {
        "filename": f"huntiq_top_users_{category}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
        "content": csv_content,
        "total_records": len(data.users)
    }

@admin_users_router.get("/profile/{user_id}")
async def get_admin_user_profile(user_id: str):
    """Get detailed admin view of a user profile"""
    database = await get_db()
    
    # Get user data
    user = await database.users.find_one({"$or": [{"id": user_id}, {"user_id": user_id}]}, {"_id": 0, "password": 0})
    
    if not user:
        # Create placeholder for new users
        user = {"user_id": user_id, "name": "Unknown", "email": ""}
    
    # Get quota data
    quota_data = await database.user_quotas.find_one({"user_id": user_id}, {"_id": 0})
    
    # Get onboarding data
    onboarding = await database.onboarding_progress.find_one({"user_id": user_id}, {"_id": 0})
    
    # Get tutorial progress
    tutorials = await database.tutorial_progress.find({"user_id": user_id}, {"_id": 0}).to_list(100)
    
    # Get metrics
    metrics = await get_user_metrics(database, user_id)
    
    return {
        "user_id": user_id,
        "basic_info": {
            "name": user.get("name", user.get("username", "Unknown")),
            "email": user.get("email", ""),
            "created_at": user.get("created_at"),
            "last_activity": user.get("last_activity") or user.get("updated_at")
        },
        "status": get_user_status({"quotas": quota_data}),
        "quota_data": quota_data,
        "hunter_profile": onboarding.get("hunter_profile") if onboarding else None,
        "preferences": onboarding.get("preferences") if onboarding else None,
        "onboarding_completed": onboarding.get("is_complete") if onboarding else False,
        "tutorials_completed": [t["tutorial_id"] for t in tutorials if t.get("is_complete")],
        "metrics": metrics,
        "activity_score": calculate_activity_score({**user, **metrics, "quotas": quota_data or {}})
    }

@admin_users_router.get("/stats/summary")
async def get_admin_users_summary():
    """Get summary statistics for admin dashboard"""
    database = await get_db()
    
    # Count users by status
    total_users = await database.users.count_documents({})
    
    # Count PRO users
    pro_monthly = await database.user_quotas.count_documents({"is_pro": True, "pro_type": "monthly"})
    pro_yearly = await database.user_quotas.count_documents({"is_pro": True, "pro_type": "yearly"})
    pro_lifetime = await database.user_quotas.count_documents({"is_pro": True, "pro_type": "lifetime"})
    total_pro = pro_monthly + pro_yearly + pro_lifetime
    
    # Active users (last 30 days)
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    # Note: This would need a last_activity field in users collection
    
    return {
        "total_users": total_users,
        "free_users": total_users - total_pro,
        "pro_users": {
            "total": total_pro,
            "monthly": pro_monthly,
            "yearly": pro_yearly,
            "lifetime": pro_lifetime
        },
        "conversion_rate": round((total_pro / total_users * 100), 2) if total_users > 0 else 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

logger.info("Admin Top Users Module initialized")
