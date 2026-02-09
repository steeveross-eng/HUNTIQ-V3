"""Networking Engine Module v1

Social networking for hunters.

Version: 1.0.0
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import os
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1/network", tags=["Networking Engine"])


class PublicProfile(BaseModel):
    user_id: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: str = ""
    location: Optional[str] = None
    experience_level: str = "intermediate"
    preferred_species: List[str] = []
    is_public: bool = True
    joined_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stats: Dict[str, int] = Field(default_factory=lambda: {"connections": 0, "posts": 0, "likes": 0})


class Connection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    connected_user_id: str
    status: str = "pending"  # pending, accepted, blocked
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    content: str
    post_type: str = "text"  # text, photo, success, tip
    images: List[str] = []
    location: Optional[str] = None
    species: Optional[str] = None
    likes: int = 0
    comments_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organizer_id: str
    title: str
    description: str
    location: str
    date: datetime
    max_participants: int = 20
    participants: List[str] = []
    event_type: str = "hunt"  # hunt, meetup, workshop, competition
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NetworkingService:
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
    
    async def get_profile(self, user_id: str) -> Optional[Dict]:
        return self.db.public_profiles.find_one({"user_id": user_id}, {"_id": 0})
    
    async def update_profile(self, user_id: str, updates: Dict) -> Dict:
        self.db.public_profiles.update_one({"user_id": user_id}, {"$set": updates}, upsert=True)
        return await self.get_profile(user_id)
    
    async def get_connections(self, user_id: str) -> List[Dict]:
        return list(self.db.connections.find({
            "$or": [{"user_id": user_id}, {"connected_user_id": user_id}],
            "status": "accepted"
        }, {"_id": 0}))
    
    async def send_connection_request(self, from_user: str, to_user: str) -> Connection:
        conn = Connection(user_id=from_user, connected_user_id=to_user)
        c_dict = conn.model_dump()
        c_dict.pop("_id", None)
        self.db.connections.insert_one(c_dict)
        return conn
    
    async def accept_connection(self, connection_id: str) -> bool:
        result = self.db.connections.update_one({"id": connection_id}, {"$set": {"status": "accepted"}})
        return result.modified_count > 0
    
    async def create_post(self, post: Post) -> Post:
        p_dict = post.model_dump()
        p_dict.pop("_id", None)
        self.db.network_posts.insert_one(p_dict)
        return post
    
    async def get_feed(self, user_id: str, limit: int = 20) -> List[Dict]:
        # Get posts from connections + public posts
        connections = await self.get_connections(user_id)
        connected_ids = [c["user_id"] if c["connected_user_id"] == user_id else c["connected_user_id"] for c in connections]
        connected_ids.append(user_id)
        
        return list(self.db.network_posts.find(
            {"$or": [{"user_id": {"$in": connected_ids}}, {"is_public": True}]},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit))
    
    async def like_post(self, post_id: str) -> bool:
        result = self.db.network_posts.update_one({"id": post_id}, {"$inc": {"likes": 1}})
        return result.modified_count > 0
    
    async def get_events(self, location: str = None, event_type: str = None) -> List[Dict]:
        query = {"date": {"$gte": datetime.now(timezone.utc)}}
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        if event_type:
            query["event_type"] = event_type
        return list(self.db.network_events.find(query, {"_id": 0}).sort("date", 1))
    
    async def create_event(self, event: Event) -> Event:
        e_dict = event.model_dump()
        e_dict.pop("_id", None)
        self.db.network_events.insert_one(e_dict)
        return event
    
    async def join_event(self, event_id: str, user_id: str) -> bool:
        result = self.db.network_events.update_one({"id": event_id}, {"$addToSet": {"participants": user_id}})
        return result.modified_count > 0


_service = NetworkingService()


@router.get("/")
async def networking_engine_info():
    return {
        "module": "networking_engine",
        "version": "1.0.0",
        "description": "Social networking for hunters",
        "features": ["Public profiles", "Connections", "Feed", "Posts", "Events", "Achievements sharing"]
    }


@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    profile = await _service.get_profile(user_id)
    if not profile:
        return {"success": False, "error": "Profile not found"}
    return {"success": True, "profile": profile}


@router.put("/profile/{user_id}")
async def update_profile(user_id: str, updates: dict):
    profile = await _service.update_profile(user_id, updates)
    return {"success": True, "profile": profile}


@router.get("/connections/{user_id}")
async def get_connections(user_id: str):
    connections = await _service.get_connections(user_id)
    return {"success": True, "connections": connections}


@router.post("/connections")
async def send_connection_request(from_user: str, to_user: str):
    conn = await _service.send_connection_request(from_user, to_user)
    return {"success": True, "connection": conn.model_dump()}


@router.put("/connections/{connection_id}/accept")
async def accept_connection(connection_id: str):
    success = await _service.accept_connection(connection_id)
    return {"success": success}


@router.get("/feed/{user_id}")
async def get_feed(user_id: str, limit: int = Query(20, ge=1, le=100)):
    feed = await _service.get_feed(user_id, limit)
    return {"success": True, "feed": feed}


@router.post("/posts")
async def create_post(post: Post):
    created = await _service.create_post(post)
    return {"success": True, "post": created.model_dump()}


@router.post("/posts/{post_id}/like")
async def like_post(post_id: str):
    success = await _service.like_post(post_id)
    return {"success": success}


@router.get("/events")
async def list_events(location: Optional[str] = None, event_type: Optional[str] = None):
    events = await _service.get_events(location, event_type)
    return {"success": True, "events": events}


@router.post("/events")
async def create_event(event: Event):
    created = await _service.create_event(event)
    return {"success": True, "event": created.model_dump()}


@router.post("/events/{event_id}/join")
async def join_event(event_id: str, user_id: str):
    success = await _service.join_event(event_id, user_id)
    return {"success": success}


@router.get("/discover")
async def discover_hunters(location: Optional[str] = None, species: Optional[str] = None, limit: int = Query(10)):
    query = {"is_public": True}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if species:
        query["preferred_species"] = species
    
    profiles = list(_service.db.public_profiles.find(query, {"_id": 0}).limit(limit))
    return {"success": True, "hunters": profiles}
