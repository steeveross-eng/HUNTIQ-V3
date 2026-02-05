"""
BIONIC™ P2 - Fusion Module
===========================
BehaviorFusionEngine pour la fusion Geo-Suite + Behavior-Suite.
"""

from .behavior_fusion_engine import (
    FusionMode,
    FusionQuality,
    FusionWeightManager,
    FusionReadyOutput,
    BehaviorFusionEngine,
    behavior_fusion_engine,
    fusion_weight_manager
)

__all__ = [
    "FusionMode",
    "FusionQuality",
    "FusionWeightManager",
    "FusionReadyOutput",
    "BehaviorFusionEngine",
    "behavior_fusion_engine",
    "fusion_weight_manager"
]
