"""
BIONIC™ P1 - Map Style Manager
===============================
Gestionnaire de styles de carte pour une lisibilité optimale.

Fonctionnalités:
- Style de base clair (OSM Bright / MapLibre Light)
- Gestion de la transparence des couches
- Légendes dynamiques
- Ordre des superpositions

Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class MapStyle(Enum):
    """Styles de carte disponibles."""
    LIGHT = "light"           # Style clair par défaut
    SATELLITE = "satellite"   # Imagerie satellite
    TERRAIN = "terrain"       # Relief et contours
    HUNTING = "hunting"       # Optimisé pour la chasse
    DARK = "dark"             # Style sombre


class LayerType(Enum):
    """Types de couches."""
    BASE = "base"             # Couche de fond
    OVERLAY = "overlay"       # Superposition
    DATA = "data"             # Données analysées
    HIGHLIGHT = "highlight"   # Mise en évidence


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class LayerConfig:
    """Configuration d'une couche de carte."""
    id: str
    name: str
    type: LayerType
    source: str
    opacity: float = 0.8
    visible: bool = True
    z_index: int = 0
    legend: Optional[Dict] = None
    style: Optional[Dict] = None


@dataclass
class LegendItem:
    """Élément de légende."""
    label: str
    color: str
    symbol: str = "square"
    value_range: Optional[str] = None


# =============================================================================
# MAP STYLE CONFIGURATIONS
# =============================================================================

# Style clair (OSM Bright / MapLibre Light)
LIGHT_STYLE = {
    "version": 8,
    "name": "BIONIC Light",
    "sources": {
        "osm-bright": {
            "type": "raster",
            "tiles": [
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png"
            ],
            "tileSize": 256,
            "attribution": "© OpenStreetMap contributors"
        }
    },
    "layers": [
        {
            "id": "osm-bright-layer",
            "type": "raster",
            "source": "osm-bright",
            "minzoom": 0,
            "maxzoom": 19
        }
    ],
    "glyphs": "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf"
}

# Style terrain
TERRAIN_STYLE = {
    "version": 8,
    "name": "BIONIC Terrain",
    "sources": {
        "terrain": {
            "type": "raster",
            "tiles": [
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
            ],
            "tileSize": 256,
            "attribution": "© Esri"
        }
    },
    "layers": [
        {
            "id": "terrain-layer",
            "type": "raster",
            "source": "terrain"
        }
    ]
}

# Style optimisé chasse
HUNTING_STYLE = {
    "version": 8,
    "name": "BIONIC Hunting",
    "sources": {
        "hunting-base": {
            "type": "raster",
            "tiles": [
                "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
            ],
            "tileSize": 256
        }
    },
    "layers": [
        {
            "id": "hunting-base-layer",
            "type": "raster",
            "source": "hunting-base",
            "paint": {
                "raster-saturation": -0.3,
                "raster-brightness-min": 0.1,
                "raster-contrast": 0.1
            }
        }
    ]
}


# =============================================================================
# LAYER PRESETS FOR SPECIES
# =============================================================================

SPECIES_LAYER_PRESETS = {
    "deer": {
        "name": "Cerf de Virginie",
        "icon": "🦌",
        "layers": [
            {"id": "forest", "opacity": 0.7},
            {"id": "water", "opacity": 0.6},
            {"id": "terrain", "opacity": 0.5},
            {"id": "corridors", "opacity": 0.8}
        ],
        "description": "Lisières forestières et bordures agricoles"
    },
    "moose": {
        "name": "Orignal",
        "icon": "🫎",
        "layers": [
            {"id": "wetlands", "opacity": 0.8},
            {"id": "water", "opacity": 0.7},
            {"id": "forest", "opacity": 0.6},
            {"id": "terrain", "opacity": 0.5}
        ],
        "description": "Milieux humides et plans d'eau"
    },
    "bear": {
        "name": "Ours noir",
        "icon": "🐻",
        "layers": [
            {"id": "forest", "opacity": 0.8},
            {"id": "nutrition", "opacity": 0.7},
            {"id": "terrain", "opacity": 0.5},
            {"id": "water", "opacity": 0.5}
        ],
        "description": "Zones forestières avec nourriture abondante"
    },
    "turkey": {
        "name": "Dindon sauvage",
        "icon": "🦃",
        "layers": [
            {"id": "forest", "opacity": 0.7},
            {"id": "agricultural", "opacity": 0.6},
            {"id": "terrain", "opacity": 0.4}
        ],
        "description": "Forêts mixtes et bordures de champs"
    },
    "waterfowl": {
        "name": "Sauvagine",
        "icon": "🦆",
        "layers": [
            {"id": "wetlands", "opacity": 0.9},
            {"id": "water", "opacity": 0.8},
            {"id": "vegetation", "opacity": 0.5}
        ],
        "description": "Milieux humides et plans d'eau"
    },
    "smallgame": {
        "name": "Petit gibier",
        "icon": "🐰",
        "layers": [
            {"id": "forest", "opacity": 0.6},
            {"id": "agricultural", "opacity": 0.6},
            {"id": "wetlands", "opacity": 0.5}
        ],
        "description": "Habitat varié avec couvert"
    }
}


# =============================================================================
# BIONIC DATA LAYERS
# =============================================================================

BIONIC_DATA_LAYERS = {
    "corridors": {
        "id": "bionic-corridors",
        "name": "Corridors fauniques",
        "source": "corridorEngine",
        "type": "line",
        "default_opacity": 0.8,
        "colors": {
            "riparian": "#2196F3",
            "ridgeline": "#4CAF50",
            "forest_edge": "#8BC34A",
            "valley": "#009688",
            "agricultural_edge": "#FFC107"
        },
        "legend": [
            {"label": "Riparian", "color": "#2196F3"},
            {"label": "Crête", "color": "#4CAF50"},
            {"label": "Lisière", "color": "#8BC34A"},
            {"label": "Vallée", "color": "#009688"},
            {"label": "Agricole", "color": "#FFC107"}
        ]
    },
    "landcover": {
        "id": "bionic-landcover",
        "name": "Couvert végétal",
        "source": "landcoverEngine",
        "type": "fill",
        "default_opacity": 0.6,
        "colors": {
            "deciduous_forest": "#228B22",
            "coniferous_forest": "#006400",
            "mixed_forest": "#2E8B57",
            "shrubland": "#9ACD32",
            "grassland": "#90EE90",
            "wetland": "#4682B4",
            "agricultural": "#F4A460",
            "water": "#1E90FF"
        },
        "legend": [
            {"label": "Feuillus", "color": "#228B22"},
            {"label": "Conifères", "color": "#006400"},
            {"label": "Mixte", "color": "#2E8B57"},
            {"label": "Arbustes", "color": "#9ACD32"},
            {"label": "Milieu humide", "color": "#4682B4"}
        ]
    },
    "nutrition": {
        "id": "bionic-nutrition",
        "name": "Indice nutritionnel",
        "source": "nutritionEngine",
        "type": "heatmap",
        "default_opacity": 0.7,
        "colors": {
            "high": "#00E676",
            "medium": "#FFEB3B",
            "low": "#FF5722"
        },
        "legend": [
            {"label": "Élevé", "color": "#00E676", "value_range": "80-100"},
            {"label": "Moyen", "color": "#FFEB3B", "value_range": "40-79"},
            {"label": "Faible", "color": "#FF5722", "value_range": "0-39"}
        ]
    },
    "population": {
        "id": "bionic-population",
        "name": "Densité de population",
        "source": "populationDensityEngine",
        "type": "circle",
        "default_opacity": 0.7,
        "colors": {
            "high": "#E91E63",
            "medium": "#FF9800",
            "low": "#CDDC39"
        },
        "legend": [
            {"label": "Haute densité", "color": "#E91E63"},
            {"label": "Densité moyenne", "color": "#FF9800"},
            {"label": "Faible densité", "color": "#CDDC39"}
        ]
    },
    "pressure": {
        "id": "bionic-pressure",
        "name": "Pression de chasse",
        "source": "huntingPressureModule",
        "type": "fill",
        "default_opacity": 0.5,
        "colors": {
            "extreme": "#B71C1C",
            "high": "#E53935",
            "moderate": "#FF9800",
            "low": "#4CAF50",
            "minimal": "#81C784"
        },
        "legend": [
            {"label": "Extrême", "color": "#B71C1C"},
            {"label": "Élevée", "color": "#E53935"},
            {"label": "Modérée", "color": "#FF9800"},
            {"label": "Faible", "color": "#4CAF50"},
            {"label": "Minimale", "color": "#81C784"}
        ]
    }
}


# =============================================================================
# MAP STYLE MANAGER
# =============================================================================

class MapStyleManager:
    """
    Gestionnaire de styles de carte BIONIC™.
    
    Usage:
        manager = MapStyleManager()
        style = manager.get_style("light")
        layers = manager.get_species_layers("deer")
    """
    
    def __init__(self):
        self._styles = {
            MapStyle.LIGHT: LIGHT_STYLE,
            MapStyle.TERRAIN: TERRAIN_STYLE,
            MapStyle.HUNTING: HUNTING_STYLE
        }
        self._species_presets = SPECIES_LAYER_PRESETS
        self._data_layers = BIONIC_DATA_LAYERS
        self._active_style = MapStyle.LIGHT
        self._active_layers: List[str] = []
        
        logger.info("BIONIC™ MapStyleManager initialized")
    
    def get_style(self, style_name: str = "light") -> Dict[str, Any]:
        """Retourne la configuration de style."""
        try:
            style_enum = MapStyle(style_name.lower())
            return self._styles.get(style_enum, LIGHT_STYLE)
        except ValueError:
            return LIGHT_STYLE
    
    def get_available_styles(self) -> List[Dict[str, str]]:
        """Retourne la liste des styles disponibles."""
        return [
            {"id": "light", "name": "Clair (OSM Bright)", "description": "Style clair pour une lisibilité optimale"},
            {"id": "terrain", "name": "Terrain", "description": "Carte topographique avec relief"},
            {"id": "hunting", "name": "Chasse", "description": "Style optimisé pour la chasse"},
            {"id": "satellite", "name": "Satellite", "description": "Imagerie satellite"},
            {"id": "dark", "name": "Sombre", "description": "Style sombre pour usage nocturne"}
        ]
    
    def get_species_preset(self, species: str) -> Dict[str, Any]:
        """Retourne le préréglage de couches pour une espèce."""
        return self._species_presets.get(species, {
            "name": species.title(),
            "icon": "🎯",
            "layers": [],
            "description": "Configuration par défaut"
        })
    
    def get_all_species_presets(self) -> Dict[str, Dict[str, Any]]:
        """Retourne tous les préréglages d'espèces."""
        return self._species_presets
    
    def get_data_layer_config(self, layer_id: str) -> Optional[Dict[str, Any]]:
        """Retourne la configuration d'une couche de données."""
        return self._data_layers.get(layer_id)
    
    def get_all_data_layers(self) -> Dict[str, Dict[str, Any]]:
        """Retourne toutes les couches de données disponibles."""
        return self._data_layers
    
    def get_legend(self, layer_id: str) -> List[Dict]:
        """Retourne la légende pour une couche."""
        layer = self._data_layers.get(layer_id, {})
        return layer.get("legend", [])
    
    def build_maplibre_style(
        self,
        base_style: str = "light",
        active_layers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Construit un style MapLibre complet avec les couches actives.
        """
        base = self.get_style(base_style).copy()
        
        if active_layers:
            for layer_id in active_layers:
                layer_config = self.get_data_layer_config(layer_id)
                if layer_config:
                    # Ajouter la source
                    source_id = f"bionic-{layer_id}"
                    base.setdefault("sources", {})[source_id] = {
                        "type": "geojson",
                        "data": {"type": "FeatureCollection", "features": []}
                    }
                    
                    # Ajouter la couche
                    layer_def = {
                        "id": layer_config["id"],
                        "type": layer_config["type"],
                        "source": source_id,
                        "paint": self._get_layer_paint(layer_config)
                    }
                    base.setdefault("layers", []).append(layer_def)
        
        return base
    
    def _get_layer_paint(self, layer_config: Dict) -> Dict:
        """Génère les propriétés de peinture pour une couche."""
        layer_type = layer_config.get("type", "fill")
        opacity = layer_config.get("default_opacity", 0.7)
        colors = layer_config.get("colors", {})
        
        if layer_type == "fill":
            return {
                "fill-color": list(colors.values())[0] if colors else "#888888",
                "fill-opacity": opacity
            }
        elif layer_type == "line":
            return {
                "line-color": list(colors.values())[0] if colors else "#888888",
                "line-width": 2,
                "line-opacity": opacity
            }
        elif layer_type == "circle":
            return {
                "circle-radius": 8,
                "circle-color": list(colors.values())[0] if colors else "#888888",
                "circle-opacity": opacity
            }
        
        return {}
    
    def get_layer_opacity_config(self) -> Dict[str, float]:
        """Retourne les opacités par défaut pour toutes les couches."""
        return {
            layer_id: config.get("default_opacity", 0.7)
            for layer_id, config in self._data_layers.items()
        }
    
    def get_layer_z_order(self) -> List[str]:
        """Retourne l'ordre d'affichage des couches (z-index)."""
        return [
            "landcover",    # Base
            "nutrition",    # Heatmap par-dessus le landcover
            "corridors",    # Lignes de corridors
            "population",   # Points de densité
            "pressure"      # Zones de pression en overlay
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

map_style_manager = MapStyleManager()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MapStyle",
    "LayerType",
    "LayerConfig",
    "LegendItem",
    "MapStyleManager",
    "map_style_manager",
    "SPECIES_LAYER_PRESETS",
    "BIONIC_DATA_LAYERS"
]


logger.info("BIONIC™ Map Style Manager loaded (v1.0.0)")
