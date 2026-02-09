"""Modules Router Integration

Central router integration for all HUNTIQ modules.
This file is the single point of import for server.py

Version: 1.4.0 - Phase 5 Complete (Data Layers)
"""

from fastapi import APIRouter
from typing import List, Tuple

# ==============================================
# CORE ENGINE ROUTERS (Phase 2)
# ==============================================
from modules.nutrition_engine.v1 import router as nutrition_router
from modules.scoring_engine.v1 import router as scoring_router
from modules.ai_engine.v1 import router as ai_router
from modules.weather_engine.v1 import router as weather_router
from modules.geospatial_engine.v1 import router as geospatial_router
from modules.wms_engine.v1 import router as wms_router
from modules.strategy_engine.v1 import router as strategy_router

# ==============================================
# BUSINESS ENGINE ROUTERS (Phase 3)
# ==============================================
from modules.user_engine.v1 import router as user_router
from modules.admin_engine.v1 import router as admin_router
from modules.notification_engine.v1 import router as notification_router
from modules.referral_engine.v1 import router as referral_router
from modules.territory_engine.v1 import router as territory_router
from modules.tracking_engine.v1 import router as tracking_router
from modules.marketplace_engine.v1 import router as marketplace_router
from modules.plugins_engine.v1 import router as plugins_router

# ==============================================
# MASTER PLAN ENGINE ROUTERS (Phase 4)
# ==============================================
from modules.recommendation_engine.v1 import router as recommendation_router
from modules.collaborative_engine.v1 import router as collaborative_router
from modules.ecoforestry_engine.v1 import router as ecoforestry_router
from modules.engine_3d.v1 import router as engine_3d_router
from modules.wildlife_behavior_engine.v1 import router as wildlife_router
from modules.weather_fauna_simulation_engine.v1 import router as simulation_router
from modules.adaptive_strategy_engine.v1 import router as adaptive_router
from modules.advanced_geospatial_engine.v1 import router as advanced_geo_router
from modules.progression_engine.v1 import router as progression_router
from modules.networking_engine.v1 import router as networking_router

# ==============================================
# DATA LAYER ROUTERS (Phase 5)
# ==============================================
from modules.data_layers.ecoforestry_layers import router as ecoforestry_data_router
from modules.data_layers.behavioral_layers import router as behavioral_data_router
from modules.data_layers.simulation_layers import router as simulation_data_router
from modules.data_layers.layers_3d import router as layers_3d_data_router
from modules.data_layers.advanced_geospatial_layers import router as advanced_geo_data_router


# List of all available routers with their metadata
CORE_ROUTERS: List[Tuple[APIRouter, dict]] = [
    # ==========================================
    # Phase 2 - Core Engines (7 modules)
    # ==========================================
    (nutrition_router, {
        "name": "nutrition_engine",
        "version": "1.0.0",
        "phase": 2,
        "description": "Nutritional analysis for hunting attractants"
    }),
    (scoring_router, {
        "name": "scoring_engine", 
        "version": "1.0.0",
        "phase": 2,
        "description": "Scientific scoring (13 weighted criteria)"
    }),
    (ai_router, {
        "name": "ai_engine",
        "version": "1.0.0",
        "phase": 2, 
        "description": "AI-powered product analysis using GPT-5.2"
    }),
    (weather_router, {
        "name": "weather_engine",
        "version": "1.0.0",
        "phase": 2,
        "description": "Weather-based hunting condition analysis"
    }),
    (geospatial_router, {
        "name": "geospatial_engine",
        "version": "1.0.0",
        "phase": 2,
        "description": "Geospatial analysis for territory management"
    }),
    (wms_router, {
        "name": "wms_engine",
        "version": "1.0.0",
        "phase": 2,
        "description": "WMS layer management for hunting maps"
    }),
    (strategy_router, {
        "name": "strategy_engine",
        "version": "1.0.0",
        "phase": 2,
        "description": "Hunting strategy generation"
    }),
    
    # ==========================================
    # Phase 3 - Business Engines (8 modules)
    # ==========================================
    (user_router, {
        "name": "user_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "User management and authentication"
    }),
    (admin_router, {
        "name": "admin_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Administration and site management"
    }),
    (notification_router, {
        "name": "notification_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Multi-channel notification system"
    }),
    (referral_router, {
        "name": "referral_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Referral and affiliate system"
    }),
    (territory_router, {
        "name": "territory_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Territory and land management"
    }),
    (tracking_router, {
        "name": "tracking_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "GPS tracking and location sharing"
    }),
    (marketplace_router, {
        "name": "marketplace_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "C2C marketplace for hunting equipment"
    }),
    (plugins_router, {
        "name": "plugins_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Feature flags and plugin management"
    }),
    
    # ==========================================
    # Phase 4 - Master Plan Engines (10 modules)
    # ==========================================
    (recommendation_router, {
        "name": "recommendation_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Intelligent product and strategy recommendations"
    }),
    (collaborative_router, {
        "name": "collaborative_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Hunter collaboration and group management"
    }),
    (ecoforestry_router, {
        "name": "ecoforestry_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Ecoforestry data and habitat analysis"
    }),
    (engine_3d_router, {
        "name": "engine_3d",
        "version": "1.0.0",
        "phase": 4,
        "description": "3D terrain visualization and analysis"
    }),
    (wildlife_router, {
        "name": "wildlife_behavior_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Wildlife behavior modeling and prediction"
    }),
    (simulation_router, {
        "name": "weather_fauna_simulation_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Weather-wildlife correlation simulation"
    }),
    (adaptive_router, {
        "name": "adaptive_strategy_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Adaptive real-time hunting strategies"
    }),
    (advanced_geo_router, {
        "name": "advanced_geospatial_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Advanced geospatial analysis and corridors"
    }),
    (progression_router, {
        "name": "progression_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Gamification and user progression"
    }),
    (networking_router, {
        "name": "networking_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Hunter social network"
    }),
    
    # ==========================================
    # Phase 5 - Data Layers (5 modules)
    # ==========================================
    (ecoforestry_data_router, {
        "name": "ecoforestry_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for SIEF forest inventory and habitat"
    }),
    (behavioral_data_router, {
        "name": "behavioral_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for wildlife behavior patterns"
    }),
    (simulation_data_router, {
        "name": "simulation_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for weather-fauna simulations"
    }),
    (layers_3d_data_router, {
        "name": "3d_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for terrain elevation and 3D analysis"
    }),
    (advanced_geo_data_router, {
        "name": "advanced_geospatial_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for corridors and connectivity"
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


def get_routers_by_phase(phase: int) -> List[dict]:
    """Get routers for a specific phase"""
    return [
        {**meta, "prefix": router.prefix}
        for router, meta in CORE_ROUTERS
        if meta.get("phase") == phase
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
        print(f"✓ Registered module: {meta['name']} v{meta['version']} (Phase {meta.get('phase', '?')})")


# Module status endpoint data
MODULE_STATUS = {
    "total_modules": len(CORE_ROUTERS),
    "phase_2_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 2]),
    "phase_3_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 3]),
    "phase_4_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 4]),
    "modules": [meta["name"] for _, meta in CORE_ROUTERS],
    "status": "operational",
    "architecture_version": "modular_v1.3"
}
