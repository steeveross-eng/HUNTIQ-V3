"""
User Waypoints and Saved Places API
Persistance backend pour les waypoints et lieux enregistrés de l'utilisateur
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user-data", tags=["User Waypoints & Places"])

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'hunttrack')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
waypoints_collection = db['user_waypoints']
places_collection = db['user_places']


# ============================================
# PYDANTIC MODELS
# ============================================

class WaypointBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    type: str = Field(default="autre")
    active: bool = Field(default=True)
    notes: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class WaypointCreate(WaypointBase):
    pass


class WaypointUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    type: Optional[str] = None
    active: Optional[bool] = None
    notes: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class Waypoint(WaypointBase):
    id: str
    user_id: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class PlaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    type: str = Field(default="autre")
    notes: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    type: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None


class Place(PlaceBase):
    id: str
    user_id: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    waypoints: List[WaypointCreate] = []
    places: List[PlaceCreate] = []


class SyncResponse(BaseModel):
    waypoints_synced: int
    places_synced: int
    message: str


# ============================================
# HELPER FUNCTIONS
# ============================================

def serialize_waypoint(doc: dict) -> dict:
    """Convertit un document MongoDB en dict sérialisable"""
    return {
        "id": str(doc.get("_id", doc.get("id", ""))),
        "user_id": doc.get("user_id", ""),
        "name": doc.get("name", ""),
        "lat": doc.get("lat", 0),
        "lng": doc.get("lng", 0),
        "type": doc.get("type", "autre"),
        "active": doc.get("active", True),
        "notes": doc.get("notes"),
        "icon": doc.get("icon"),
        "color": doc.get("color"),
        "created_at": doc.get("created_at", ""),
        "updated_at": doc.get("updated_at")
    }


def serialize_place(doc: dict) -> dict:
    """Convertit un document MongoDB en dict sérialisable"""
    return {
        "id": str(doc.get("_id", doc.get("id", ""))),
        "user_id": doc.get("user_id", ""),
        "name": doc.get("name", ""),
        "lat": doc.get("lat", 0),
        "lng": doc.get("lng", 0),
        "type": doc.get("type", "autre"),
        "notes": doc.get("notes"),
        "address": doc.get("address"),
        "phone": doc.get("phone"),
        "website": doc.get("website"),
        "rating": doc.get("rating"),
        "created_at": doc.get("created_at", ""),
        "updated_at": doc.get("updated_at")
    }


# ============================================
# WAYPOINTS ENDPOINTS
# ============================================

@router.get("/waypoints/{user_id}", response_model=List[Waypoint])
async def get_user_waypoints(
    user_id: str,
    active_only: bool = Query(False, description="Retourner uniquement les waypoints actifs")
):
    """Récupère tous les waypoints d'un utilisateur"""
    try:
        query = {"user_id": user_id}
        if active_only:
            query["active"] = True
        
        cursor = waypoints_collection.find(query).sort("created_at", -1)
        waypoints = await cursor.to_list(length=500)
        
        return [serialize_waypoint(wp) for wp in waypoints]
    except Exception as e:
        logger.error(f"Error fetching waypoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/waypoints/{user_id}", response_model=Waypoint)
async def create_waypoint(user_id: str, waypoint: WaypointCreate):
    """Crée un nouveau waypoint pour l'utilisateur"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        doc = {
            "user_id": user_id,
            "name": waypoint.name,
            "lat": waypoint.lat,
            "lng": waypoint.lng,
            "type": waypoint.type,
            "active": waypoint.active,
            "notes": waypoint.notes,
            "icon": waypoint.icon,
            "color": waypoint.color,
            "created_at": now,
            "updated_at": None
        }
        
        result = await waypoints_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Created waypoint {result.inserted_id} for user {user_id}")
        return serialize_waypoint(doc)
    except Exception as e:
        logger.error(f"Error creating waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/waypoints/{user_id}/{waypoint_id}", response_model=Waypoint)
async def update_waypoint(user_id: str, waypoint_id: str, update: WaypointUpdate):
    """Met à jour un waypoint existant"""
    try:
        # Vérifier que le waypoint appartient à l'utilisateur
        existing = await waypoints_collection.find_one({
            "_id": ObjectId(waypoint_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(status_code=404, detail="Waypoint non trouvé")
        
        # Préparer les champs à mettre à jour
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await waypoints_collection.update_one(
            {"_id": ObjectId(waypoint_id)},
            {"$set": update_data}
        )
        
        # Récupérer le document mis à jour
        updated = await waypoints_collection.find_one({"_id": ObjectId(waypoint_id)})
        
        logger.info(f"Updated waypoint {waypoint_id} for user {user_id}")
        return serialize_waypoint(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Bulk delete must be defined BEFORE single delete to avoid route conflict
@router.delete("/waypoints/{user_id}/bulk")
async def delete_all_waypoints(user_id: str):
    """Supprime tous les waypoints d'un utilisateur"""
    try:
        result = await waypoints_collection.delete_many({"user_id": user_id})
        return {"deleted": result.deleted_count}
    except Exception as e:
        logger.error(f"Error deleting all waypoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/waypoints/{user_id}/{waypoint_id}")
async def delete_waypoint(user_id: str, waypoint_id: str):
    """Supprime un waypoint"""
    try:
        result = await waypoints_collection.delete_one({
            "_id": ObjectId(waypoint_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Waypoint non trouvé")
        
        logger.info(f"Deleted waypoint {waypoint_id} for user {user_id}")
        return {"message": "Waypoint supprimé", "id": waypoint_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/waypoints/{user_id}/{waypoint_id}/toggle")
async def toggle_waypoint_active(user_id: str, waypoint_id: str):
    """Active/désactive un waypoint"""
    try:
        existing = await waypoints_collection.find_one({
            "_id": ObjectId(waypoint_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(status_code=404, detail="Waypoint non trouvé")
        
        new_active = not existing.get("active", True)
        
        await waypoints_collection.update_one(
            {"_id": ObjectId(waypoint_id)},
            {"$set": {
                "active": new_active,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {"id": waypoint_id, "active": new_active}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PLACES ENDPOINTS
# ============================================

@router.get("/places/{user_id}", response_model=List[Place])
async def get_user_places(
    user_id: str,
    type: Optional[str] = Query(None, description="Filtrer par type de lieu")
):
    """Récupère tous les lieux enregistrés d'un utilisateur"""
    try:
        query = {"user_id": user_id}
        if type:
            query["type"] = type
        
        cursor = places_collection.find(query).sort("created_at", -1)
        places = await cursor.to_list(length=500)
        
        return [serialize_place(p) for p in places]
    except Exception as e:
        logger.error(f"Error fetching places: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/places/{user_id}", response_model=Place)
async def create_place(user_id: str, place: PlaceCreate):
    """Crée un nouveau lieu enregistré"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        doc = {
            "user_id": user_id,
            "name": place.name,
            "lat": place.lat,
            "lng": place.lng,
            "type": place.type,
            "notes": place.notes,
            "address": place.address,
            "phone": place.phone,
            "website": place.website,
            "rating": place.rating,
            "created_at": now,
            "updated_at": None
        }
        
        result = await places_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        logger.info(f"Created place {result.inserted_id} for user {user_id}")
        return serialize_place(doc)
    except Exception as e:
        logger.error(f"Error creating place: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/places/{user_id}/{place_id}", response_model=Place)
async def update_place(user_id: str, place_id: str, update: PlaceUpdate):
    """Met à jour un lieu existant"""
    try:
        existing = await places_collection.find_one({
            "_id": ObjectId(place_id),
            "user_id": user_id
        })
        
        if not existing:
            raise HTTPException(status_code=404, detail="Lieu non trouvé")
        
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await places_collection.update_one(
            {"_id": ObjectId(place_id)},
            {"$set": update_data}
        )
        
        updated = await places_collection.find_one({"_id": ObjectId(place_id)})
        
        logger.info(f"Updated place {place_id} for user {user_id}")
        return serialize_place(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating place: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Bulk delete must be defined BEFORE single delete to avoid route conflict
@router.delete("/places/{user_id}/bulk")
async def delete_all_places(user_id: str):
    """Supprime tous les lieux d'un utilisateur"""
    try:
        result = await places_collection.delete_many({"user_id": user_id})
        return {"deleted": result.deleted_count}
    except Exception as e:
        logger.error(f"Error deleting all places: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/places/{user_id}/{place_id}")
async def delete_place(user_id: str, place_id: str):
    """Supprime un lieu"""
    try:
        result = await places_collection.delete_one({
            "_id": ObjectId(place_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lieu non trouvé")
        
        logger.info(f"Deleted place {place_id} for user {user_id}")
        return {"message": "Lieu supprimé", "id": place_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting place: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SYNC ENDPOINTS
# ============================================

@router.post("/sync/{user_id}", response_model=SyncResponse)
async def sync_user_data(user_id: str, data: SyncRequest):
    """
    Synchronise les données locales avec le backend.
    Utilisé pour migrer les données localStorage vers MongoDB.
    """
    try:
        now = datetime.now(timezone.utc).isoformat()
        waypoints_synced = 0
        places_synced = 0
        
        # Sync waypoints
        for wp in data.waypoints:
            # Vérifier si ce waypoint existe déjà (même nom + coords proches)
            existing = await waypoints_collection.find_one({
                "user_id": user_id,
                "name": wp.name,
                "lat": {"$gte": wp.lat - 0.0001, "$lte": wp.lat + 0.0001},
                "lng": {"$gte": wp.lng - 0.0001, "$lte": wp.lng + 0.0001}
            })
            
            if not existing:
                doc = {
                    "user_id": user_id,
                    "name": wp.name,
                    "lat": wp.lat,
                    "lng": wp.lng,
                    "type": wp.type,
                    "active": wp.active,
                    "notes": wp.notes,
                    "icon": wp.icon,
                    "color": wp.color,
                    "created_at": now,
                    "updated_at": None
                }
                await waypoints_collection.insert_one(doc)
                waypoints_synced += 1
        
        # Sync places
        for place in data.places:
            existing = await places_collection.find_one({
                "user_id": user_id,
                "name": place.name,
                "lat": {"$gte": place.lat - 0.0001, "$lte": place.lat + 0.0001},
                "lng": {"$gte": place.lng - 0.0001, "$lte": place.lng + 0.0001}
            })
            
            if not existing:
                doc = {
                    "user_id": user_id,
                    "name": place.name,
                    "lat": place.lat,
                    "lng": place.lng,
                    "type": place.type,
                    "notes": place.notes,
                    "address": place.address,
                    "phone": place.phone,
                    "website": place.website,
                    "rating": place.rating,
                    "created_at": now,
                    "updated_at": None
                }
                await places_collection.insert_one(doc)
                places_synced += 1
        
        logger.info(f"Synced {waypoints_synced} waypoints and {places_synced} places for user {user_id}")
        
        return SyncResponse(
            waypoints_synced=waypoints_synced,
            places_synced=places_synced,
            message=f"Synchronisation terminée : {waypoints_synced} waypoints et {places_synced} lieux ajoutés"
        )
    except Exception as e:
        logger.error(f"Error syncing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{user_id}")
async def get_user_data_stats(user_id: str):
    """Récupère les statistiques des données utilisateur"""
    try:
        waypoints_count = await waypoints_collection.count_documents({"user_id": user_id})
        active_waypoints = await waypoints_collection.count_documents({"user_id": user_id, "active": True})
        places_count = await places_collection.count_documents({"user_id": user_id})
        
        # Types de lieux
        place_types = await places_collection.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]).to_list(length=20)
        
        return {
            "user_id": user_id,
            "waypoints": {
                "total": waypoints_count,
                "active": active_waypoints,
                "inactive": waypoints_count - active_waypoints
            },
            "places": {
                "total": places_count,
                "by_type": {t["_id"]: t["count"] for t in place_types}
            }
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
