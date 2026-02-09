"""Collaborative Engine Module v1

Collaboration system for hunting groups.
Enables group management, spot sharing, and real-time communication.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import secrets
import os
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1/collaborative", tags=["Collaborative Engine"])


# ============================================
# MODELS
# ============================================

class GroupRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class GroupPrivacy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"


class Group(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    owner_id: str
    privacy: GroupPrivacy = GroupPrivacy.PRIVATE
    invite_code: str = Field(default_factory=lambda: secrets.token_urlsafe(8))
    max_members: int = 20
    allow_spot_sharing: bool = True
    allow_position_sharing: bool = True
    allow_chat: bool = True
    member_count: int = 1
    spot_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GroupMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    user_name: str
    role: GroupRole = GroupRole.MEMBER
    can_invite: bool = False
    can_add_spots: bool = True
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SharedSpot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    created_by: str
    name: str
    description: str = ""
    latitude: float
    longitude: float
    spot_type: Literal["stand", "blind", "feeder", "trail", "crossing", "bedding", "other"] = "other"
    species: List[str] = []
    best_time: Optional[str] = None
    success_count: int = 0
    photos: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GroupEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    created_by: str
    title: str
    description: str = ""
    start_time: datetime
    end_time: Optional[datetime] = None
    participants: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    sender_id: str
    sender_name: str
    content: str
    message_type: Literal["text", "image", "location", "spot"] = "text"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================
# SERVICE
# ============================================

class CollaborativeService:
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
    
    async def create_group(self, name: str, owner_id: str, owner_name: str, description: str = "", privacy: GroupPrivacy = GroupPrivacy.PRIVATE) -> Group:
        group = Group(name=name, description=description, owner_id=owner_id, privacy=privacy)
        g_dict = group.model_dump()
        g_dict.pop("_id", None)
        self.db.groups.insert_one(g_dict)
        member = GroupMember(group_id=group.id, user_id=owner_id, user_name=owner_name, role=GroupRole.OWNER, can_invite=True)
        m_dict = member.model_dump()
        m_dict.pop("_id", None)
        self.db.group_members.insert_one(m_dict)
        return group
    
    async def get_group(self, group_id: str) -> Optional[Dict]:
        return self.db.groups.find_one({"id": group_id}, {"_id": 0})
    
    async def get_group_by_code(self, invite_code: str) -> Optional[Dict]:
        return self.db.groups.find_one({"invite_code": invite_code}, {"_id": 0})
    
    async def list_user_groups(self, user_id: str) -> List[Dict]:
        memberships = list(self.db.group_members.find({"user_id": user_id}, {"_id": 0}))
        group_ids = [m["group_id"] for m in memberships]
        return list(self.db.groups.find({"id": {"$in": group_ids}}, {"_id": 0}))
    
    async def add_member(self, group_id: str, user_id: str, user_name: str, role: GroupRole = GroupRole.MEMBER) -> GroupMember:
        existing = self.db.group_members.find_one({"group_id": group_id, "user_id": user_id})
        if existing:
            raise ValueError("User is already a member")
        member = GroupMember(group_id=group_id, user_id=user_id, user_name=user_name, role=role)
        m_dict = member.model_dump()
        m_dict.pop("_id", None)
        self.db.group_members.insert_one(m_dict)
        self.db.groups.update_one({"id": group_id}, {"$inc": {"member_count": 1}})
        return member
    
    async def get_members(self, group_id: str) -> List[Dict]:
        return list(self.db.group_members.find({"group_id": group_id}, {"_id": 0}))
    
    async def remove_member(self, group_id: str, user_id: str) -> bool:
        result = self.db.group_members.delete_one({"group_id": group_id, "user_id": user_id})
        if result.deleted_count > 0:
            self.db.groups.update_one({"id": group_id}, {"$inc": {"member_count": -1}})
            return True
        return False
    
    async def add_spot(self, spot: SharedSpot) -> SharedSpot:
        s_dict = spot.model_dump()
        s_dict.pop("_id", None)
        self.db.shared_spots.insert_one(s_dict)
        self.db.groups.update_one({"id": spot.group_id}, {"$inc": {"spot_count": 1}})
        return spot
    
    async def get_spots(self, group_id: str) -> List[Dict]:
        return list(self.db.shared_spots.find({"group_id": group_id}, {"_id": 0}))
    
    async def create_event(self, event: GroupEvent) -> GroupEvent:
        e_dict = event.model_dump()
        e_dict.pop("_id", None)
        self.db.group_events.insert_one(e_dict)
        return event
    
    async def get_events(self, group_id: str, upcoming_only: bool = False) -> List[Dict]:
        query = {"group_id": group_id}
        if upcoming_only:
            query["start_time"] = {"$gte": datetime.now(timezone.utc)}
        return list(self.db.group_events.find(query, {"_id": 0}).sort("start_time", 1))
    
    async def send_message(self, message: ChatMessage) -> ChatMessage:
        m_dict = message.model_dump()
        m_dict.pop("_id", None)
        self.db.chat_messages.insert_one(m_dict)
        return message
    
    async def get_messages(self, group_id: str, limit: int = 50) -> List[Dict]:
        return list(self.db.chat_messages.find({"group_id": group_id}, {"_id": 0}).sort("created_at", -1).limit(limit))


_service = CollaborativeService()


# ============================================
# ROUTES
# ============================================

@router.get("/")
async def collaborative_engine_info():
    return {
        "module": "collaborative_engine",
        "version": "1.0.0",
        "description": "Collaboration system for hunting groups",
        "features": ["Group management", "Member roles", "Shared spots", "Calendar", "Chat", "Invitations"],
        "roles": [r.value for r in GroupRole],
        "privacy_options": [p.value for p in GroupPrivacy]
    }


@router.post("/groups")
async def create_group(name: str, owner_id: str, owner_name: str, description: str = "", privacy: str = "private"):
    try:
        privacy_enum = GroupPrivacy(privacy)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid privacy: {privacy}")
    group = await _service.create_group(name, owner_id, owner_name, description, privacy_enum)
    return {"success": True, "group": group.model_dump()}


@router.get("/groups")
async def list_user_groups(user_id: str):
    groups = await _service.list_user_groups(user_id)
    return {"success": True, "groups": groups}


@router.get("/groups/{group_id}")
async def get_group(group_id: str):
    group = await _service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"success": True, "group": group}


@router.get("/groups/join/{invite_code}")
async def get_group_by_invite(invite_code: str):
    group = await _service.get_group_by_code(invite_code)
    if not group:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    return {"success": True, "group": group}


@router.get("/groups/{group_id}/members")
async def get_members(group_id: str):
    members = await _service.get_members(group_id)
    return {"success": True, "members": members}


@router.post("/groups/{group_id}/members")
async def add_member(group_id: str, user_id: str, user_name: str, role: str = "member"):
    try:
        role_enum = GroupRole(role)
        member = await _service.add_member(group_id, user_id, user_name, role_enum)
        return {"success": True, "member": member.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/groups/{group_id}/members/{user_id}")
async def remove_member(group_id: str, user_id: str):
    success = await _service.remove_member(group_id, user_id)
    return {"success": success}


@router.get("/groups/{group_id}/spots")
async def get_spots(group_id: str):
    spots = await _service.get_spots(group_id)
    return {"success": True, "spots": spots}


@router.post("/groups/{group_id}/spots")
async def add_spot(group_id: str, spot: SharedSpot):
    spot.group_id = group_id
    created = await _service.add_spot(spot)
    return {"success": True, "spot": created.model_dump()}


@router.get("/groups/{group_id}/calendar")
async def get_calendar(group_id: str, upcoming_only: bool = Query(False)):
    events = await _service.get_events(group_id, upcoming_only)
    return {"success": True, "events": events}


@router.post("/groups/{group_id}/calendar")
async def create_event(group_id: str, event: GroupEvent):
    event.group_id = group_id
    created = await _service.create_event(event)
    return {"success": True, "event": created.model_dump()}


@router.get("/groups/{group_id}/chat")
async def get_chat_messages(group_id: str, limit: int = Query(50, ge=1, le=200)):
    messages = await _service.get_messages(group_id, limit)
    return {"success": True, "messages": messages}


@router.post("/groups/{group_id}/chat")
async def send_chat_message(group_id: str, message: ChatMessage):
    message.group_id = group_id
    sent = await _service.send_message(message)
    return {"success": True, "message": sent.model_dump()}
