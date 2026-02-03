"""
BIONIC™ SIGÉOM Engine - Geology Analyzer

Analyse des données géologiques pour les territoires de chasse.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GeologyAnalyzer:
    """
    Analyseur géologique pour l'évaluation de territoires de chasse.
    
    Corrélations géologie-chasse:
    - Type de roche → Drainage → Végétation → Habitat
    - Dépôts de surface → Accessibilité → Stratégie de chasse
    - Structures géologiques → Corridors → Déplacements du gibier
    """
    
    # Geological province hunting characteristics
    GEOLOGICAL_PROVINCES = {
        "bouclier_canadien": {
            "name": "Bouclier canadien",
            "rock_type": "Roches cristallines (granite, gneiss)",
            "terrain": "Accidenté avec nombreux lacs",
            "drainage": "Excellent",
            "forest_type": "Forêt boréale (conifères)",
            "hunting_score": 85,
            "species": ["moose", "bear", "smallgame"],
            "strategy": "Chasse à l'orignal près des plans d'eau, affût sur les eskers"
        },
        "basses_terres": {
            "name": "Basses-Terres du Saint-Laurent",
            "rock_type": "Roches sédimentaires (calcaire, shale)",
            "terrain": "Plat à légèrement ondulé",
            "drainage": "Variable (argiles marines)",
            "forest_type": "Forêt mixte à feuillus",
            "hunting_score": 75,
            "species": ["deer", "turkey", "waterfowl"],
            "strategy": "Chasse au cerf dans les boisés agricoles, sauvagine dans les zones humides"
        },
        "appalaches": {
            "name": "Appalaches",
            "rock_type": "Roches métamorphiques et sédimentaires",
            "terrain": "Montagnes et vallées",
            "drainage": "Bon à excellent",
            "forest_type": "Forêt mixte",
            "hunting_score": 80,
            "species": ["deer", "moose", "bear", "turkey"],
            "strategy": "Chasse en montagne, surveillance des vallées et cols"
        }
    }
    
    # Surficial deposit hunting scores
    DEPOSIT_HUNTING_SCORES = {
        "till": {
            "base_score": 70,
            "moose": 75,
            "deer": 80,
            "bear": 70,
            "waterfowl": 30,
            "turkey": 60
        },
        "sand_gravel": {
            "base_score": 80,
            "moose": 85,
            "deer": 75,
            "bear": 65,
            "waterfowl": 25,
            "turkey": 70
        },
        "marine_clay": {
            "base_score": 45,
            "moose": 50,
            "deer": 40,
            "bear": 35,
            "waterfowl": 90,
            "turkey": 30
        },
        "peat": {
            "base_score": 70,
            "moose": 90,
            "deer": 40,
            "bear": 60,
            "waterfowl": 85,
            "smallgame": 75
        },
        "alluvium": {
            "base_score": 65,
            "moose": 60,
            "deer": 75,
            "bear": 55,
            "waterfowl": 70,
            "turkey": 65
        },
        "bedrock": {
            "base_score": 40,
            "moose": 50,
            "deer": 35,
            "bear": 55,
            "waterfowl": 10,
            "smallgame": 30
        }
    }
    
    def __init__(self):
        self.provinces = self.GEOLOGICAL_PROVINCES
        self.deposit_scores = self.DEPOSIT_HUNTING_SCORES
    
    def analyze_territory(
        self,
        geology_data: Dict[str, Any],
        bbox: Dict[str, float],
        target_species: str = "deer"
    ) -> Dict[str, Any]:
        """
        Perform complete geological analysis of a territory.
        """
        # Calculate area
        lat_diff = bbox["max_lat"] - bbox["min_lat"]
        lon_diff = bbox["max_lon"] - bbox["min_lon"]
        area_km2 = lat_diff * 111 * lon_diff * 75
        
        # Determine geological province from coordinates
        center_lat = (bbox["min_lat"] + bbox["max_lat"]) / 2
        center_lon = (bbox["min_lon"] + bbox["max_lon"]) / 2
        province = self._determine_province(center_lat, center_lon)
        
        # Analyze each geological layer
        bedrock_analysis = None
        surficial_analysis = None
        
        if "bedrock" in geology_data.get("layers", {}):
            bedrock_analysis = self._analyze_bedrock(
                geology_data["layers"]["bedrock"],
                target_species
            )
        
        if "surficial" in geology_data.get("layers", {}):
            surficial_analysis = self._analyze_surficial(
                geology_data["layers"]["surficial"],
                target_species
            )
        
        # Calculate overall geological hunting score
        overall_score = self._calculate_overall_score(
            province,
            bedrock_analysis,
            surficial_analysis,
            target_species
        )
        
        return {
            "analysis_id": f"geology_analysis_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "bbox": bbox,
            "area_km2": round(area_km2, 2),
            "center": {"lat": center_lat, "lon": center_lon},
            "target_species": target_species,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "geological_province": province,
            "bedrock_analysis": bedrock_analysis,
            "surficial_analysis": surficial_analysis,
            "overall_score": overall_score,
            "recommendations": self._generate_recommendations(
                province, surficial_analysis, target_species
            )
        }
    
    def calculate_deposit_score(
        self,
        deposit_type: str,
        target_species: str
    ) -> Dict[str, Any]:
        """
        Calculate hunting score for a surficial deposit type.
        """
        deposit_scores = self.deposit_scores.get(deposit_type, {})
        
        species_score = deposit_scores.get(
            target_species.lower(),
            deposit_scores.get("base_score", 50)
        )
        
        return {
            "deposit_type": deposit_type,
            "target_species": target_species,
            "score": species_score,
            "level": self._score_to_level(species_score),
            "interpretation": self._get_deposit_interpretation(deposit_type, target_species)
        }
    
    def get_province_info(
        self,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """
        Get geological province information for a location.
        """
        province_key = self._determine_province(lat, lon)
        province_info = self.provinces.get(province_key, {})
        
        return {
            "location": {"lat": lat, "lon": lon},
            "province": province_key,
            "info": province_info
        }
    
    def _determine_province(self, lat: float, lon: float) -> str:
        """
        Determine geological province from coordinates.
        
        Simplified classification for Quebec.
        """
        # Basses-Terres du Saint-Laurent (roughly)
        if lat < 47.0 and lon > -74.5 and lon < -70.0:
            return "basses_terres"
        
        # Appalaches (south and east of St. Lawrence)
        if lat < 48.5 and lon > -70.0:
            return "appalaches"
        
        # Default to Canadian Shield (most of Quebec)
        return "bouclier_canadien"
    
    def _analyze_bedrock(
        self,
        bedrock_data: Dict[str, Any],
        target_species: str
    ) -> Dict[str, Any]:
        """Analyze bedrock geology for hunting."""
        return {
            "available": True,
            "tile_url": bedrock_data.get("tile_url"),
            "rock_types": bedrock_data.get("rock_types", []),
            "hunting_relevance": bedrock_data.get("hunting_relevance", {}),
            "note": "La géologie du socle influence le drainage et la végétation"
        }
    
    def _analyze_surficial(
        self,
        surficial_data: Dict[str, Any],
        target_species: str
    ) -> Dict[str, Any]:
        """Analyze surficial deposits for hunting."""
        deposit_types = surficial_data.get("deposit_types", [])
        
        # Calculate average score for deposit types
        total_score = 0
        scored_types = []
        
        for deposit in deposit_types:
            deposit_type = deposit.get("type", "")
            score_info = self.calculate_deposit_score(deposit_type, target_species)
            scored_types.append({
                **deposit,
                "hunting_score": score_info
            })
            total_score += score_info["score"]
        
        avg_score = total_score / len(deposit_types) if deposit_types else 50
        
        return {
            "available": True,
            "tile_url": surficial_data.get("tile_url"),
            "deposit_types": scored_types,
            "average_score": round(avg_score, 1),
            "level": self._score_to_level(avg_score),
            "hunting_relevance": surficial_data.get("hunting_relevance", {})
        }
    
    def _calculate_overall_score(
        self,
        province: str,
        bedrock_analysis: Optional[Dict],
        surficial_analysis: Optional[Dict],
        target_species: str
    ) -> Dict[str, Any]:
        """Calculate overall geological hunting score."""
        province_info = self.provinces.get(province, {})
        province_score = province_info.get("hunting_score", 60)
        
        # Weight components
        weights = {
            "province": 0.4,
            "surficial": 0.4,
            "bedrock": 0.2
        }
        
        total = province_score * weights["province"]
        
        if surficial_analysis and "average_score" in surficial_analysis:
            total += surficial_analysis["average_score"] * weights["surficial"]
        else:
            total += 50 * weights["surficial"]
        
        # Bedrock influence is indirect
        total += 60 * weights["bedrock"]
        
        return {
            "score": round(total, 1),
            "level": self._score_to_level(total),
            "components": {
                "province": province_score,
                "surficial": surficial_analysis.get("average_score") if surficial_analysis else None,
                "bedrock": "indirect"
            },
            "interpretation": f"Terrain géologiquement {'favorable' if total >= 70 else 'acceptable' if total >= 50 else 'difficile'} pour la chasse au {target_species}"
        }
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to level string."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "bon"
        elif score >= 40:
            return "modéré"
        else:
            return "faible"
    
    def _get_deposit_interpretation(
        self,
        deposit_type: str,
        species: str
    ) -> str:
        """Get interpretation for deposit type and species."""
        interpretations = {
            ("till", "moose"): "Till glaciaire - Bon drainage, végétation de repousse attrayante pour l'orignal",
            ("till", "deer"): "Till glaciaire - Forêts matures sur till, excellent habitat pour le cerf",
            ("sand_gravel", "moose"): "Eskers et deltas - Corridors naturels utilisés par les orignaux",
            ("sand_gravel", "deer"): "Dépôts sableux - Bonne visibilité, ravages potentiels",
            ("peat", "moose"): "Tourbières - Habitat de choix pour l'orignal (alimentation aquatique)",
            ("peat", "waterfowl"): "Tourbières - Excellent pour la sauvagine",
            ("marine_clay", "waterfowl"): "Argiles marines - Zones humides idéales pour la sauvagine",
            ("alluvium", "deer"): "Plaines alluviales - Boisés riverains, habitat cerf"
        }
        
        key = (deposit_type, species.lower())
        return interpretations.get(
            key,
            f"Type de dépôt {deposit_type} - Évaluer le terrain sur place"
        )
    
    def _generate_recommendations(
        self,
        province: str,
        surficial_analysis: Optional[Dict],
        target_species: str
    ) -> List[str]:
        """Generate hunting recommendations based on geology."""
        recommendations = []
        
        province_info = self.provinces.get(province, {})
        if province_info.get("strategy"):
            recommendations.append(province_info["strategy"])
        
        if surficial_analysis:
            scored_types = surficial_analysis.get("deposit_types", [])
            
            # Find best deposit types
            high_score_deposits = [
                d for d in scored_types
                if d.get("hunting_score", {}).get("score", 0) >= 70
            ]
            
            for deposit in high_score_deposits[:2]:
                deposit_name = deposit.get("name", "")
                if deposit_name:
                    recommendations.append(
                        f"Ciblez les zones de {deposit_name} - Score élevé pour {target_species}"
                    )
        
        # Province-specific tips
        if province == "bouclier_canadien":
            recommendations.append(
                "Bouclier canadien: Utilisez les eskers comme axes de surveillance"
            )
        elif province == "basses_terres":
            recommendations.append(
                "Basses-Terres: Recherchez les îlots boisés dans les zones agricoles"
            )
        elif province == "appalaches":
            recommendations.append(
                "Appalaches: Surveillez les cols et passages entre vallées"
            )
        
        return recommendations


# Singleton instance
geology_analyzer = GeologyAnalyzer()
