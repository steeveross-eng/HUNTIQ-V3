"""
BIONIC™ Sentinel Engine
========================

Module de traitement des images Sentinel-2 pour l'analyse de végétation.

Fonctionnalités:
- Calcul des indices de végétation (NDVI, EVI, SAVI)
- Analyse de la couverture forestière
- Détection des changements saisonniers
- Classification des types de végétation
"""

__version__ = "0.1.0"

def get_analyzer():
    from .core.analyzer import SentinelAnalyzer
    return SentinelAnalyzer

def get_indices():
    from .core.indices import VegetationIndices
    return VegetationIndices

def get_router():
    from .api.endpoints import sentinel_engine_router
    return sentinel_engine_router
