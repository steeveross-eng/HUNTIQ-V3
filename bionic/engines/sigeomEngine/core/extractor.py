"""
BIONIC™ SIGÉOM Engine - Data Extractor

Extraction des données géologiques depuis le service WMS de SIGÉOM.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# SIGÉOM WMS Configuration
SIGEOM_CONFIG = {
    "wms_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
    "wfs_url": "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WFS/MapServer/WFSServer",
    "layers": {
        "bedrock": {
            "id": "0",
            "name": "Géologie du socle",
            "description": "Carte géologique des formations rocheuses"
        },
        "surficial": {
            "id": "1",
            "name": "Dépôts de surface",
            "description": "Dépôts meubles (till, sable, argile, tourbe)"
        },
        "faults": {
            "id": "2",
            "name": "Failles",
            "description": "Failles et structures tectoniques"
        },
        "mineralization": {
            "id": "3",
            "name": "Indices minéralisés",
            "description": "Sites d'intérêt minier"
        }
    },
    "attribution": "© SIGÉOM - MERN Québec",
    "license": "Licence du gouvernement ouvert - Québec"
}

# Cache directory
CACHE_DIR = Path("/tmp/bionic_sigeom_cache")
CACHE_DIR.mkdir(exist_ok=True)


class SigeomExtractor:
    """
    Extracteur de données géologiques depuis SIGÉOM.
    
    Récupère les données de géologie pour l'analyse des territoires de chasse:
    - Type de roche (influence sur le drainage et la végétation)
    - Dépôts de surface (influence sur l'accessibilité et les habitats)
    - Structures géologiques (corridors naturels)
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.config = SIGEOM_CONFIG
        self.wms_url = SIGEOM_CONFIG["wms_url"]
        self.layers = SIGEOM_CONFIG["layers"]
    
    def _get_cache_path(self, layer: str, bbox: Dict[str, float]) -> Path:
        """Generate cache file path."""
        bbox_str = f"{bbox['min_lat']:.4f}_{bbox['min_lon']:.4f}_{bbox['max_lat']:.4f}_{bbox['max_lon']:.4f}"
        return CACHE_DIR / f"sigeom_{layer}_{bbox_str}.json"
    
    def extract_bedrock(
        self,
        bbox: Dict[str, float],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract bedrock geology data.
        
        Returns tile URL and metadata for bedrock formations.
        """
        cache_path = self._get_cache_path("bedrock", bbox)
        
        if use_cache and cache_path.exists():
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except Exception:
                pass
        
        tile_url = self._build_wms_url("bedrock", bbox)
        
        result = {
            "layer": "bedrock",
            "type": "geologie_socle",
            "bbox": bbox,
            "tile_url": tile_url,
            "data_source": "SIGÉOM - MERN Québec",
            "license": self.config["license"],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "rock_types": self._get_common_rock_types(),
            "hunting_relevance": {
                "drainage": "Les formations rocheuses influencent le drainage et les sources d'eau",
                "vegetation": "Le type de roche détermine la végétation dominante",
                "terrain": "Les affleurements rocheux créent des points de repère pour le gibier"
            }
        }
        
        if use_cache:
            try:
                with open(cache_path, "w") as f:
                    json.dump(result, f)
            except Exception:
                pass
        
        return result
    
    def extract_surficial(
        self,
        bbox: Dict[str, float],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract surficial deposits data.
        
        Surficial deposits are crucial for hunting as they determine:
        - Soil moisture (wetlands)
        - Accessibility
        - Vegetation types
        """
        cache_path = self._get_cache_path("surficial", bbox)
        
        if use_cache and cache_path.exists():
            try:
                with open(cache_path) as f:
                    return json.load(f)
            except Exception:
                pass
        
        tile_url = self._build_wms_url("surficial", bbox)
        
        result = {
            "layer": "surficial",
            "type": "depots_surface",
            "bbox": bbox,
            "tile_url": tile_url,
            "data_source": "SIGÉOM - MERN Québec",
            "license": self.config["license"],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "deposit_types": self._get_surficial_deposit_types(),
            "hunting_relevance": {
                "till": "Terrain bien drainé - Bon pour cervidés",
                "sand_gravel": "Eskers et dépôts fluvio-glaciaires - Corridors naturels",
                "clay": "Zones humides potentielles - Habitat orignal/sauvagine",
                "peat": "Tourbières - Excellent habitat pour petit gibier et orignal"
            }
        }
        
        if use_cache:
            try:
                with open(cache_path, "w") as f:
                    json.dump(result, f)
            except Exception:
                pass
        
        return result
    
    def extract_faults(
        self,
        bbox: Dict[str, float],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract fault/structure data.
        
        Geological faults create natural corridors and water sources.
        """
        tile_url = self._build_wms_url("faults", bbox)
        
        return {
            "layer": "faults",
            "type": "failles_structures",
            "bbox": bbox,
            "tile_url": tile_url,
            "data_source": "SIGÉOM - MERN Québec",
            "license": self.config["license"],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "structure_types": [
                {"type": "fault", "name": "Faille", "hunting_impact": "Corridors de déplacement"},
                {"type": "fold", "name": "Pli", "hunting_impact": "Variations topographiques"},
                {"type": "lineament", "name": "Linéament", "hunting_impact": "Sources d'eau potentielles"}
            ],
            "hunting_relevance": "Les failles créent des vallées et corridors naturels suivis par le gibier"
        }
    
    def extract_all(
        self,
        bbox: Dict[str, float],
        include_bedrock: bool = True,
        include_surficial: bool = True,
        include_faults: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract all geological data for a bounding box.
        """
        result = {
            "request_id": f"sigeom_extract_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "bbox": bbox,
            "data_source": "SIGÉOM - MERN Québec",
            "license": self.config["license"],
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "layers": {}
        }
        
        if include_bedrock:
            result["layers"]["bedrock"] = self.extract_bedrock(bbox, use_cache)
        
        if include_surficial:
            result["layers"]["surficial"] = self.extract_surficial(bbox, use_cache)
        
        if include_faults:
            result["layers"]["faults"] = self.extract_faults(bbox, use_cache)
        
        return result
    
    def _build_wms_url(
        self,
        layer_key: str,
        bbox: Dict[str, float],
        width: int = 512,
        height: int = 512
    ) -> str:
        """Build WMS GetMap URL."""
        layer = self.layers.get(layer_key, {})
        layer_id = layer.get("id", "0")
        
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.3.0",
            "layers": layer_id,
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "width": str(width),
            "height": str(height),
            "crs": "EPSG:4326",
            "bbox": f"{bbox['min_lat']},{bbox['min_lon']},{bbox['max_lat']},{bbox['max_lon']}"
        }
        
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.wms_url}?{query}"
    
    def _get_common_rock_types(self) -> List[Dict[str, Any]]:
        """Get common rock types in Quebec with hunting relevance."""
        return [
            {
                "type": "granite",
                "name": "Granite",
                "province": "Bouclier canadien",
                "hunting_impact": "Terrain accidenté avec lacs et affleurements"
            },
            {
                "type": "gneiss",
                "name": "Gneiss",
                "province": "Bouclier canadien",
                "hunting_impact": "Similaire au granite, bon drainage"
            },
            {
                "type": "limestone",
                "name": "Calcaire",
                "province": "Basses-Terres du Saint-Laurent",
                "hunting_impact": "Sols riches, bonne végétation pour cervidés"
            },
            {
                "type": "shale",
                "name": "Schiste argileux",
                "province": "Appalaches",
                "hunting_impact": "Terrain ondulé, nombreuses vallées"
            },
            {
                "type": "sandstone",
                "name": "Grès",
                "province": "Diverses régions",
                "hunting_impact": "Bon drainage, végétation mixte"
            }
        ]
    
    def _get_surficial_deposit_types(self) -> List[Dict[str, Any]]:
        """Get surficial deposit types with hunting relevance."""
        return [
            {
                "code": "1a",
                "type": "till",
                "name": "Till glaciaire",
                "description": "Dépôt glaciaire non trié",
                "drainage": "bon",
                "hunting_score": 70,
                "species": ["deer", "moose", "bear"]
            },
            {
                "code": "2a",
                "type": "sand_gravel",
                "name": "Sable et gravier fluvio-glaciaires",
                "description": "Eskers, deltas, terrasses",
                "drainage": "excellent",
                "hunting_score": 80,
                "species": ["deer", "moose", "turkey"]
            },
            {
                "code": "3a",
                "type": "marine_clay",
                "name": "Argile marine",
                "description": "Dépôts de la mer de Champlain",
                "drainage": "mauvais",
                "hunting_score": 50,
                "species": ["waterfowl"]
            },
            {
                "code": "4a",
                "type": "peat",
                "name": "Tourbe",
                "description": "Tourbières et milieux humides",
                "drainage": "très_mauvais",
                "hunting_score": 75,
                "species": ["moose", "waterfowl", "smallgame"]
            },
            {
                "code": "5a",
                "type": "alluvium",
                "name": "Alluvions récentes",
                "description": "Dépôts de plaines inondables",
                "drainage": "variable",
                "hunting_score": 65,
                "species": ["deer", "waterfowl"]
            },
            {
                "code": "R",
                "type": "bedrock",
                "name": "Roc affleurant",
                "description": "Substrat rocheux exposé",
                "drainage": "excellent",
                "hunting_score": 40,
                "species": ["moose", "bear"]
            }
        ]
    
    def clear_cache(self, layer: Optional[str] = None) -> Dict[str, int]:
        """Clear extraction cache."""
        count = 0
        pattern = f"sigeom_{layer}_*.json" if layer else "sigeom_*.json"
        for f in CACHE_DIR.glob(pattern):
            f.unlink()
            count += 1
        return {"cleared": count}


# Singleton instance
sigeom_extractor = SigeomExtractor()
