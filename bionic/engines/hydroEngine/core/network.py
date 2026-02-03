"""
BIONIC™ Hydrology Engine - Stream Network Analyzer

Analyse du réseau hydrographique pour identifier les corridors de déplacement.
"""

import math
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class StreamNetworkAnalyzer:
    """
    Analyseur de réseau hydrographique.
    
    Identifie:
    - Confluences (jonctions de cours d'eau)
    - Corridors naturels le long des vallées
    - Points de traversée potentiels
    - Zones tampons autour des cours d'eau
    """
    
    # Stream order importance for wildlife
    STREAM_ORDER_WEIGHTS = {
        1: 0.3,   # Small streams - minor influence
        2: 0.5,   # Medium streams
        3: 0.7,   # Large streams
        4: 0.85,  # Small rivers
        5: 1.0,   # Major rivers - major corridors
    }
    
    # Buffer distances for wildlife corridors (meters)
    CORRIDOR_BUFFERS = {
        "riparian": 30,      # Riparian zone
        "movement": 100,     # Wildlife movement corridor
        "influence": 500     # Zone of water influence
    }
    
    def __init__(self):
        self.order_weights = self.STREAM_ORDER_WEIGHTS
        self.buffers = self.CORRIDOR_BUFFERS
    
    def analyze_confluence_potential(
        self,
        confluence_point: Dict[str, float],
        stream_orders: List[int]
    ) -> Dict[str, Any]:
        """
        Analyze hunting potential at a stream confluence.
        
        Confluences are natural funneling points for wildlife.
        
        Args:
            confluence_point: Coordinates {lat, lon}
            stream_orders: Stream orders of converging streams
        """
        # Higher order confluences are more significant
        max_order = max(stream_orders) if stream_orders else 1
        sum_orders = sum(stream_orders) if stream_orders else 1
        
        # Score based on stream importance
        base_score = self.order_weights.get(max_order, 0.5) * 100
        
        # Bonus for multiple streams converging
        confluence_bonus = min(20, (len(stream_orders) - 2) * 10)
        
        score = min(100, base_score + confluence_bonus)
        
        return {
            "type": "confluence",
            "location": confluence_point,
            "stream_orders": stream_orders,
            "max_stream_order": max_order,
            "converging_streams": len(stream_orders),
            "score": round(score, 1),
            "hunting_value": self._get_confluence_value(score),
            "recommendations": [
                "Confluences naturelles concentrent les déplacements du gibier",
                "Position d'affût recommandée en aval de la jonction",
                "Les cervidés traversent souvent aux confluences"
            ]
        }
    
    def analyze_crossing_point(
        self,
        crossing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a potential stream crossing point.
        
        Wildlife tends to cross at predictable locations.
        """
        # Factors that make good crossing points
        factors = {
            "shallow_water": crossing.get("depth_m", 1) < 0.5,
            "gradual_banks": crossing.get("bank_slope_deg", 45) < 30,
            "narrow_channel": crossing.get("width_m", 10) < 15,
            "firm_bottom": crossing.get("substrate") in ["gravel", "rock", "sand"],
            "cover_nearby": crossing.get("has_cover", False)
        }
        
        # Score based on factors
        score = sum(20 for k, v in factors.items() if v)
        
        return {
            "type": "crossing_point",
            "location": crossing.get("location", {}),
            "factors": factors,
            "score": score,
            "level": "excellent" if score >= 80 else "bon" if score >= 60 else "modéré",
            "hunting_recommendation": (
                "Point de traverse idéal" if score >= 80 else
                "Bon point de traverse" if score >= 60 else
                "Point de traverse possible"
            )
        }
    
    def calculate_corridor_score(
        self,
        stream_data: Dict[str, Any],
        target_species: str = "deer"
    ) -> Dict[str, Any]:
        """
        Calculate corridor value of a stream segment.
        
        Streams create natural movement corridors through:
        - Valley topography
        - Riparian vegetation
        - Access to water
        """
        stream_order = stream_data.get("order", 2)
        length_km = stream_data.get("length_km", 0)
        
        # Base score from stream order
        order_weight = self.order_weights.get(stream_order, 0.5)
        base_score = order_weight * 70
        
        # Length bonus (longer streams = better corridors)
        length_bonus = min(20, length_km * 2)
        
        # Species-specific adjustments
        species_multiplier = {
            "deer": 1.0,
            "moose": 1.2,  # Moose strongly prefer riparian zones
            "bear": 0.9,
            "elk": 1.1
        }.get(target_species, 1.0)
        
        total_score = min(100, (base_score + length_bonus) * species_multiplier)
        
        return {
            "type": "corridor",
            "stream_order": stream_order,
            "length_km": length_km,
            "species": target_species,
            "score": round(total_score, 1),
            "buffer_zones": {
                "riparian_m": self.buffers["riparian"],
                "movement_m": self.buffers["movement"],
                "influence_m": self.buffers["influence"]
            },
            "corridor_quality": self._score_to_quality(total_score),
            "hunting_tips": self._get_corridor_tips(stream_order, target_species)
        }
    
    def identify_funnel_points(
        self,
        streams: List[Dict[str, Any]],
        terrain: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Identify natural funnel points where streams and terrain
        concentrate wildlife movement.
        """
        funnel_points = []
        
        # Analyze stream convergence patterns
        # This is a simplified implementation - full version would
        # use actual geometry
        
        # Example funnel types
        funnel_types = [
            {
                "type": "valley_narrowing",
                "description": "Vallée qui se rétrécit",
                "hunting_value": "excellent",
                "strategy": "Les animaux sont forcés de passer par un corridor étroit"
            },
            {
                "type": "stream_confluence",
                "description": "Confluence de cours d'eau",
                "hunting_value": "très_bon",
                "strategy": "Point de concentration naturel pour l'abreuvement"
            },
            {
                "type": "ridge_crossing",
                "description": "Col ou passage entre deux crêtes",
                "hunting_value": "excellent",
                "strategy": "Les animaux empruntent le chemin de moindre effort"
            },
            {
                "type": "lake_outlet",
                "description": "Décharge de lac",
                "hunting_value": "bon",
                "strategy": "Zone d'attraction pour la faune"
            }
        ]
        
        return funnel_types
    
    def generate_corridor_layer(
        self,
        streams: List[Dict[str, Any]],
        buffer_type: str = "movement"
    ) -> Dict[str, Any]:
        """
        Generate GeoJSON layer for stream corridors.
        
        Can be used to display corridors on MapLibre GL map.
        """
        buffer_distance = self.buffers.get(buffer_type, 100)
        
        # This would generate actual buffered geometries in full implementation
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {
                "buffer_type": buffer_type,
                "buffer_distance_m": buffer_distance,
                "layer_name": f"corridors_{buffer_type}",
                "style": {
                    "fill_color": "rgba(66, 135, 245, 0.2)",
                    "stroke_color": "rgba(66, 135, 245, 0.8)",
                    "stroke_width": 2
                }
            },
            "note": "Geometry generation requires actual stream coordinates"
        }
    
    def _get_confluence_value(self, score: float) -> str:
        """Get hunting value description for confluence."""
        if score >= 80:
            return "confluence_majeure"
        elif score >= 60:
            return "confluence_importante"
        elif score >= 40:
            return "confluence_mineure"
        else:
            return "confluence_negligeable"
    
    def _score_to_quality(self, score: float) -> str:
        """Convert score to quality string."""
        if score >= 80:
            return "corridor_principal"
        elif score >= 60:
            return "corridor_secondaire"
        elif score >= 40:
            return "corridor_tertiaire"
        else:
            return "corridor_mineur"
    
    def _get_corridor_tips(self, stream_order: int, species: str) -> List[str]:
        """Get hunting tips for stream corridors."""
        tips = []
        
        if stream_order >= 3:
            tips.append(
                "Cours d'eau majeur - Utilisez la vallée comme axe de surveillance"
            )
            tips.append(
                "Positionnez-vous en hauteur pour observer le corridor"
            )
        else:
            tips.append(
                "Petit cours d'eau - Bon pour les embuscades rapprochées"
            )
        
        if species == "moose":
            tips.append(
                "Les orignaux suivent souvent les ruisseaux pour se nourrir"
            )
        elif species == "deer":
            tips.append(
                "Les cerfs utilisent les vallées comme routes de déplacement"
            )
        
        return tips


# Singleton instance  
stream_network_analyzer = StreamNetworkAnalyzer()
