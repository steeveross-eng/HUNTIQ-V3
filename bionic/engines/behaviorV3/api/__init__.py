"""
BIONIC™ P3 - BehaviorEngine v3.0 API Module
============================================
Endpoints FastAPI pour le module v3.
"""

from .endpoints import router, behavior_v3_router

__all__ = ["router", "behavior_v3_router"]
