"""
BIONIC™ Hydrology Engine
========================

Module de traitement des données hydrologiques pour l'analyse de territoires de chasse.

Sources de données:
- GRHQ (Géobase du réseau hydrographique du Québec)
- HydroSHEDS
- OpenStreetMap

Fonctionnalités:
- Extraction des cours d'eau, lacs et milieux humides
- Analyse du réseau hydrographique
- Calcul des scores de proximité à l'eau
- Génération de couches pour MapLibre GL
"""

from .core.extractor import HydroExtractor
from .core.analyzer import HydroAnalyzer
from .core.network import StreamNetworkAnalyzer
from .api.endpoints import hydro_engine_router

__version__ = "0.1.0"
__all__ = ["HydroExtractor", "HydroAnalyzer", "StreamNetworkAnalyzer", "hydro_engine_router"]
