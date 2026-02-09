"""Notification Engine Router - MÉTIER

FastAPI router for notification endpoints.

Version: 1.0.0
API Prefix: /api/v1/notification
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from .service import NotificationService
from .models import (
    Notification, NotificationPreferences,
    NotificationType, NotificationChannel,
    SendNotificationRequest, BroadcastRequest
)

router = APIRouter(prefix="/api/v1/notification", tags=["Notification Engine"])

# Initialize service
_service = NotificationService()


@router.get("/")
async def notification_engine_info():
    """Get notification engine information"""
    return {
        "module": "notification_engine",
        "version": "1.0.0",
        "description": "Multi-channel notification system",
        "features": [
            "In-app notifications",
            "Email notifications",
            "Push notifications",
            "SMS notifications",
            "Notification preferences",
            "Templates"
        ],
        "types": [t.value for t in NotificationType],
        "channels": [c.value for c in NotificationChannel]
    }


@router.post("/send")
async def send_notification(request: SendNotificationRequest):
    """Send a notification to a user"""
    notification = await _service.send_notification(
        user_id=request.user_id,
        notification_type=request.type,
        title=request.title,
        message=request.message,
        channels=request.channels,
        priority=request.priority,
        data=request.data,
        action_url=request.action_url
    )
    
    return {
        "success": True,
        "notification": notification.model_dump()
    }


@router.post("/broadcast")
async def broadcast_notification(request: BroadcastRequest):
    """Broadcast notification to multiple users"""
    if not request.user_ids:
        raise HTTPException(status_code=400, detail="User IDs required for broadcast")
    
    sent_count = await _service.broadcast(
        user_ids=request.user_ids,
        notification_type=request.type,
        title=request.title,
        message=request.message,
        channels=request.channels
    )
    
    return {
        "success": True,
        "sent_count": sent_count,
        "total_users": len(request.user_ids)
    }


@router.get("/user/{user_id}")
async def get_user_notifications(
    user_id: str,
    unread_only: bool = Query(False),
    type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get notifications for a user"""
    notification_type = None
    if type:
        try:
            notification_type = NotificationType(type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid notification type: {type}")
    
    notifications = await _service.get_notifications(
        user_id=user_id,
        unread_only=unread_only,
        notification_type=notification_type,
        limit=limit
    )
    
    unread_count = await _service.get_unread_count(user_id)
    
    return {
        "success": True,
        "total": len(notifications),
        "unread_count": unread_count,
        "notifications": [n.model_dump() for n in notifications]
    }


@router.get("/user/{user_id}/unread-count")
async def get_unread_count(user_id: str):
    """Get unread notification count"""
    count = await _service.get_unread_count(user_id)
    
    return {
        "success": True,
        "unread_count": count
    }


@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: str, user_id: str = Query(...)):
    """Mark notification as read"""
    success = await _service.mark_as_read(notification_id, user_id)
    
    return {
        "success": success,
        "message": "Notification marked as read" if success else "Notification not found"
    }


@router.put("/user/{user_id}/read-all")
async def mark_all_as_read(user_id: str):
    """Mark all notifications as read"""
    count = await _service.mark_all_as_read(user_id)
    
    return {
        "success": True,
        "marked_count": count
    }


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, user_id: str = Query(...)):
    """Delete a notification"""
    success = await _service.delete_notification(notification_id, user_id)
    
    return {
        "success": success,
        "message": "Notification deleted" if success else "Notification not found"
    }


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user notification preferences"""
    prefs = await _service.get_preferences(user_id)
    
    return {
        "success": True,
        "preferences": prefs.model_dump()
    }


@router.put("/preferences/{user_id}")
async def update_preferences(user_id: str, prefs_data: dict):
    """Update notification preferences"""
    prefs = await _service.update_preferences(user_id, prefs_data)
    
    return {
        "success": True,
        "preferences": prefs.model_dump()
    }


@router.get("/templates")
async def get_templates(type: Optional[str] = None):
    """Get notification templates"""
    notification_type = None
    if type:
        try:
            notification_type = NotificationType(type)
        except ValueError:
            pass
    
    templates = await _service.get_templates(notification_type)
    
    return {
        "success": True,
        "templates": [t.model_dump() for t in templates]
    }


@router.get("/types")
async def list_types():
    """List all notification types"""
    return {
        "success": True,
        "types": [
            {"id": t.value, "name": _get_type_name(t)}
            for t in NotificationType
        ]
    }


@router.get("/channels")
async def list_channels():
    """List all notification channels"""
    return {
        "success": True,
        "channels": [
            {"id": c.value, "name": _get_channel_name(c)}
            for c in NotificationChannel
        ]
    }


def _get_type_name(t: NotificationType) -> str:
    names = {
        NotificationType.SYSTEM: "Système",
        NotificationType.ORDER: "Commande",
        NotificationType.PROMOTION: "Promotion",
        NotificationType.ALERT: "Alerte",
        NotificationType.MESSAGE: "Message",
        NotificationType.REMINDER: "Rappel"
    }
    return names.get(t, t.value)


def _get_channel_name(c: NotificationChannel) -> str:
    names = {
        NotificationChannel.IN_APP: "Dans l'application",
        NotificationChannel.EMAIL: "Courriel",
        NotificationChannel.PUSH: "Notification push",
        NotificationChannel.SMS: "SMS"
    }
    return names.get(c, c.value)
