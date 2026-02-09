"""Modules Router Integration

Central router integration for all HUNTIQ modules.
This file is the single point of import for server.py

Version: 1.0.0
"""

from fastapi import APIRouter
from typing import List, Tuple

# Import all core engine routers
from modules.nutrition_engine.v1 import router as nutrition_router
from modules.scoring_engine.v1 import router as scoring_router
from modules.ai_engine.v1 import router as ai_router
from modules.weather_engine.v1 import router as weather_router
from modules.geospatial_engine.v1 import router as geospatial_router
from modules.wms_engine.v1 import router as wms_router
from modules.strategy_engine.v1 import router as strategy_router


# List of all available routers with their metadata
CORE_ROUTERS: List[Tuple[APIRouter, dict]] = [
    (nutrition_router, {
        "name": "nutrition_engine",
        "version": "1.0.0",
        "description": "Nutritional analysis for hunting attractants"
    }),
    (scoring_router, {
        "name": "scoring_engine", 
        "version": "1.0.0",
        "description": "Scientific scoring (13 weighted criteria)"
    }),
    (ai_router, {
        "name": "ai_engine",
        "version": "1.0.0", 
        "description": "AI-powered product analysis using GPT-5.2"
    }),
    (weather_router, {
        "name": "weather_engine",
        "version": "1.0.0",
        "description": "Weather-based hunting condition analysis"
    }),
    (geospatial_router, {
        "name": "geospatial_engine",
        "version": "1.0.0",
        "description": "Geospatial analysis for territory management"
    }),
    (wms_router, {
        "name": "wms_engine",
        "version": "1.0.0",
        "description": "WMS layer management for hunting maps"
    }),
    (strategy_router, {
        "name": "strategy_engine",
        "version": "1.0.0",
        "description": "Hunting strategy generation"
    }),
]


def get_all_routers() -> List[APIRouter]:
    """Get all router instances"""
    return [router for router, _ in CORE_ROUTERS]


def get_router_info() -> List[dict]:
    """Get information about all available routers"""
    return [
        {
            **meta,
            "prefix": router.prefix
        }
        for router, meta in CORE_ROUTERS
    ]


def register_routers(app):
    """
    Register all module routers with a FastAPI app.
    
    Usage in server.py:
        from modules.routers import register_routers
        register_routers(app)
    """
    for router, meta in CORE_ROUTERS:
        app.include_router(router)
        print(f"✓ Registered module: {meta['name']} v{meta['version']}")


# Module status endpoint data
MODULE_STATUS = {
    "total_modules": len(CORE_ROUTERS),
    "modules": [meta["name"] for _, meta in CORE_ROUTERS],
    "status": "operational"
}
