"""
BIONIC™ P3 - BehaviorEngine v3.0 Loader
========================================
Point d'entrée pour charger le module P3 depuis server.py.
Gère les imports et le path correctement.
"""

import sys
import os

# Add the module path BEFORE any other imports
_module_path = os.path.dirname(os.path.abspath(__file__))
if _module_path not in sys.path:
    sys.path.insert(0, _module_path)

# Now import the router
from api.endpoints import behavior_v3_router

__all__ = ["behavior_v3_router"]
