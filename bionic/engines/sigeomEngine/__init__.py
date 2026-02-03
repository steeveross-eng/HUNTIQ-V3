"""
BIONIC™ SIGÉOM Engine
=====================

Module de traitement des données géologiques de SIGÉOM (Système d'information
géominière du Québec) pour l'analyse de territoires de chasse.

Fonctionnalités:
- Extraction des données géologiques (roche en place, dépôts de surface)
- Analyse des failles et structures
- Identification des zones minéralisées
- Corrélation avec les habitats de chasse
"""

__version__ = "0.1.0"

def get_extractor():
    from .core.extractor import SigeomExtractor
    return SigeomExtractor

def get_analyzer():
    from .core.analyzer import GeologyAnalyzer
    return GeologyAnalyzer

def get_router():
    from .api.endpoints import sigeom_engine_router
    return sigeom_engine_router
