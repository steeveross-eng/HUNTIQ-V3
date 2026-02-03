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

__version__ = "0.1.0"

# Lazy imports to avoid circular dependencies
def get_extractor():
    from .core.extractor import HydroExtractor
    return HydroExtractor

def get_analyzer():
    from .core.analyzer import HydroAnalyzer
    return HydroAnalyzer

def get_network_analyzer():
    from .core.network import StreamNetworkAnalyzer
    return StreamNetworkAnalyzer

def get_router():
    from .api.endpoints import hydro_engine_router
    return hydro_engine_router
