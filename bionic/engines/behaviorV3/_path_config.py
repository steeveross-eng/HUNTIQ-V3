"""
BIONIC™ P3 - Path Configuration
================================
Ce module DOIT être importé en premier pour configurer les paths.
"""

import sys
import os

# Configuration du path pour le module P3
_BASE_PATH = '/app/bionic/engines/behaviorV3'

if _BASE_PATH not in sys.path:
    sys.path.insert(0, _BASE_PATH)
