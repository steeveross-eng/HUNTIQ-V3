"""
BIONIC™ SIGÉOM Engine - Geology Analyzer
==========================================
Analyse des données géologiques pour les territoires de chasse.

Version: 2.0 - Phase 3 Real Data Implementation
- Intégration du cache multi-niveaux
- Données réelles via RealDataFetcher
- Modèles géologiques calibrés pour le Québec
"""

import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Add core path for imports
if '/app/bionic/engines' not in sys.path:
    sys.path.insert(0, '/app/bionic/engines')

# Import cache and real data fetcher with fallback
try:
    from core.cache_manager import cache_manager, get_cached, set_cached
    from core.real_data_fetcher import real_data_fetcher
    from core.standardized_models import get_formatter
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache_manager = None
    real_data_fetcher = None
    get_formatter = None

logger = logging.getLogger(__name__)


class GeologyAnalyzer:
    """
    Analyseur géologique pour l'évaluation de territoires de chasse.
    
    Version 2.0 - Intégration données réelles et cache
    
    Corrélations géologie-chasse:
    - Type de roche → Drainage → Végétation → Habitat
    - Dépôts de surface → Accessibilité → Stratégie de chasse
    - Structures géologiques → Corridors → Déplacements du gibier
    
    Cache:
    - L1 (RAM): 5 minutes
    - L2 (Disque): 24 heures (données géologiques statiques)
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
        },
        "fosse_labrador": {
            "name": "Fosse du Labrador",
            "rock_type": "Roches sédimentaires-volcaniques (fer rubané)",
            "terrain": "Collines et plateaux",
            "drainage": "Bon",
            "forest_type": "Taïga et toundra",
            "hunting_score": 70,
            "species": ["caribou", "moose", "bear"],
            "strategy": "Chasse au caribou en migration, orignal près des tourbières"
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
        },
        "colluvium": {
            "base_score": 55,
            "moose": 60,
            "deer": 55,
            "bear": 65,
            "waterfowl": 15,
            "smallgame": 50
        }
    }
    
    def __init__(self):
        self.provinces = self.GEOLOGICAL_PROVINCES
        self.deposit_scores = self.DEPOSIT_HUNTING_SCORES
        self._cache_namespace = "geology"
        self._cache_hits = 0
        self._cache_misses = 0
    
    async def analyze_point_async(
        self,
        lat: float,
        lon: float,
        target_species: str = "deer",
        use_cache: bool = True,
        use_real_data: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze geology at a specific point (async version).
        
        Uses real data from RealDataFetcher with cache support.
        """
        cache_key = None
        
        # Check cache first (geology is static, longer TTL)
        if use_cache and CACHE_AVAILABLE and cache_manager:
            cache_key = f"{cache_manager.make_geo_key(lat, lon)}_{target_species}"
            cached = cache_manager.get(self._cache_namespace, cache_key)
            if cached:
                self._cache_hits += 1
                cached["from_cache"] = True
                return cached
            self._cache_misses += 1
        
        # Fetch real geology data
        geo_data = None
        if use_real_data and CACHE_AVAILABLE and real_data_fetcher:
            try:
                geo_data = await real_data_fetcher.fetch_geology_estimate(lat, lon)
            except Exception as e:
                logger.warning(f"Real geology data fetch failed: {e}")
        
        # Build analysis result
        if geo_data:
            province = geo_data.get("province", {})
            deposit = geo_data.get("surficial_deposit", {})
            bedrock = geo_data.get("bedrock", {})
            relevance = geo_data.get("hunting_relevance", {})
        else:
            # Fallback to local estimation
            province = self._determine_province_dict(lat, lon)
            deposit = self._estimate_deposit(lat, lon, province.get("code", "bouclier_canadien"))
            bedrock = self._get_bedrock_info(province.get("code", "bouclier_canadien"))
            relevance = self._calculate_relevance(province, deposit, target_species)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score_v2(
            province, deposit, target_species
        )
        
        result = {
            "location": {"lat": lat, "lon": lon},
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "target_species": target_species,
            "data_source": geo_data.get("source", "BIONIC Geological Model") if geo_data else "BIONIC Geological Model",
            "confidence": geo_data.get("confidence", 0.70) if geo_data else 0.70,
            "geological_province": province,
            "surficial_deposit": deposit,
            "bedrock": bedrock,
            "hunting_relevance": relevance,
            "overall_score": overall_score,
            "recommendations": self._generate_recommendations_v2(province, deposit, target_species),
            "from_cache": False
        }
        
        # Store in cache with longer TTL for geology
        if use_cache and CACHE_AVAILABLE and cache_manager and cache_key:
            cache_manager.set(self._cache_namespace, cache_key, result, ttl=86400)  # 24h
        
        return result
    
    def _determine_province_dict(self, lat: float, lon: float) -> Dict[str, Any]:
        """Determine geological province and return full dict."""
        province_key = self._determine_province(lat, lon)
        province_info = self.provinces.get(province_key, self.provinces["bouclier_canadien"])
        return {
            "code": province_key,
            **province_info
        }
    
    def _estimate_deposit(
        self, 
        lat: float, 
        lon: float, 
        province_code: str
    ) -> Dict[str, Any]:
        """Estimate surficial deposit type."""
        import random
        random.seed(int(lat * 1000 + lon * 1000))
        
        # Probability distributions by province
        deposits_by_province = {
            "bouclier_canadien": [
                ("till", "Till glaciaire", 0.45),
                ("sand_gravel", "Sable et gravier", 0.20),
                ("bedrock", "Roc affleurant", 0.15),
                ("peat", "Tourbe", 0.12),
                ("alluvium", "Alluvions", 0.08)
            ],
            "basses_terres": [
                ("marine_clay", "Argile marine", 0.40),
                ("till", "Till glaciaire", 0.25),
                ("alluvium", "Alluvions", 0.20),
                ("sand_gravel", "Sable et gravier", 0.10),
                ("peat", "Tourbe", 0.05)
            ],
            "appalaches": [
                ("till", "Till glaciaire", 0.35),
                ("bedrock", "Roc affleurant", 0.25),
                ("colluvium", "Colluvions", 0.20),
                ("alluvium", "Alluvions", 0.15),
                ("peat", "Tourbe", 0.05)
            ],
            "fosse_labrador": [
                ("till", "Till glaciaire", 0.40),
                ("bedrock", "Roc affleurant", 0.30),
                ("sand_gravel", "Sable et gravier", 0.15),
                ("peat", "Tourbe", 0.10),
                ("alluvium", "Alluvions", 0.05)
            ]
        }
        
        deposits = deposits_by_province.get(province_code, deposits_by_province["bouclier_canadien"])
        
        r = random.random()
        cumulative = 0
        selected_code = "till"
        selected_name = "Till glaciaire"
        
        for code, name, prob in deposits:
            cumulative += prob
            if r < cumulative:
                selected_code = code
                selected_name = name
                break
        
        return {
            "code": selected_code,
            "name": selected_name,
            "drainage": self._get_deposit_drainage(selected_code),
            "hunting_score": self.deposit_scores.get(selected_code, {}).get("base_score", 60)
        }
    
    def _get_deposit_drainage(self, deposit_code: str) -> str:
        """Get drainage quality for deposit type."""
        drainage_map = {
            "till": "bon",
            "sand_gravel": "excellent",
            "bedrock": "excellent",
            "marine_clay": "mauvais",
            "peat": "très mauvais",
            "alluvium": "modéré",
            "colluvium": "bon"
        }
        return drainage_map.get(deposit_code, "modéré")
    
    def _get_bedrock_info(self, province_code: str) -> Dict[str, Any]:
        """Get bedrock information for province."""
        bedrock_info = {
            "bouclier_canadien": {
                "type": "crystalline",
                "dominant_rocks": ["granite", "gneiss", "greenstone"],
                "age": "Archéen-Protérozoïque"
            },
            "basses_terres": {
                "type": "sedimentary",
                "dominant_rocks": ["limestone", "dolomite", "shale"],
                "age": "Paléozoïque"
            },
            "appalaches": {
                "type": "metamorphic",
                "dominant_rocks": ["slate", "quartzite", "schist"],
                "age": "Paléozoïque"
            },
            "fosse_labrador": {
                "type": "sedimentary_volcanic",
                "dominant_rocks": ["iron_formation", "quartzite", "basalt"],
                "age": "Protérozoïque"
            }
        }
        return bedrock_info.get(province_code, bedrock_info["bouclier_canadien"])
    
    def _calculate_relevance(
        self, 
        province: Dict, 
        deposit: Dict, 
        target_species: str
    ) -> Dict[str, Any]:
        """Calculate hunting relevance from geology."""
        province_code = province.get("code", "bouclier_canadien")
        deposit_code = deposit.get("code", "till")
        
        # Species affinity
        species_affinity = {
            "moose": "excellent" if province_code == "bouclier_canadien" or deposit_code == "peat" else "bon",
            "deer": "excellent" if province_code == "basses_terres" or deposit_code == "alluvium" else "modéré",
            "bear": "bon" if province_code in ["bouclier_canadien", "appalaches"] else "modéré",
            "waterfowl": "excellent" if deposit_code in ["peat", "marine_clay"] else "faible",
            "turkey": "excellent" if province_code == "basses_terres" else "faible"
        }
        
        target_affinity = species_affinity.get(target_species.lower(), "modéré")
        
        return {
            "species_affinity": species_affinity,
            "target_species_affinity": target_affinity,
            "terrain_assessment": province.get("terrain", "Variable"),
            "drainage_impact": deposit.get("drainage", "modéré"),
            "strategic_note": province.get("strategy", "Adapter selon le terrain")
        }
    
    def _calculate_overall_score_v2(
        self,
        province: Dict,
        deposit: Dict,
        target_species: str
    ) -> Dict[str, Any]:
        """Calculate overall geological hunting score."""
        province_score = province.get("hunting_score", 60)
        
        # Get species-specific deposit score
        deposit_code = deposit.get("code", "till")
        deposit_scores = self.deposit_scores.get(deposit_code, {"base_score": 60})
        species_score = deposit_scores.get(target_species.lower(), deposit_scores.get("base_score", 60))
        
        # Weighted combination
        total = (province_score * 0.5) + (species_score * 0.5)
        
        return {
            "score": round(total, 1),
            "level": self._score_to_level(total),
            "components": {
                "province_score": province_score,
                "deposit_score": species_score
            },
            "interpretation": f"Terrain géologiquement {'favorable' if total >= 70 else 'acceptable' if total >= 50 else 'difficile'} pour {target_species}"
        }
    
    def _generate_recommendations_v2(
        self,
        province: Dict,
        deposit: Dict,
        target_species: str
    ) -> List[str]:
        """Generate hunting recommendations based on geology."""
        recommendations = []
        
        # Province strategy
        if province.get("strategy"):
            recommendations.append(province["strategy"])
        
        # Deposit-specific recommendations
        deposit_code = deposit.get("code", "till")
        deposit_tips = {
            "till": "Terrain bien drainé - Recherchez les ravages dans les secteurs de till",
            "sand_gravel": "Eskers et dépôts sableux - Corridors naturels de déplacement",
            "marine_clay": "Zones d'argile marine - Prudence, terrain humide",
            "peat": "Tourbières - Excellent pour orignal et petit gibier",
            "alluvium": "Plaines alluviales - Boisés riverains à surveiller",
            "bedrock": "Roc affleurant - Points de vue stratégiques",
            "colluvium": "Pentes colluviales - Attention à la stabilité du terrain"
        }
        
        if deposit_code in deposit_tips:
            recommendations.append(deposit_tips[deposit_code])
        
        # Species-specific geology tips
        species_geo_tips = {
            "moose": "L'orignal affectionne les zones de till près des tourbières",
            "deer": "Le cerf préfère les sols bien drainés avec couvert mixte",
            "bear": "L'ours utilise les eskers comme corridors de déplacement",
            "waterfowl": "La sauvagine se concentre sur les argiles marines et tourbières",
            "turkey": "Le dindon privilégie les sols calcaires des basses-terres"
        }
        
        if target_species.lower() in species_geo_tips:
            recommendations.append(species_geo_tips[target_species.lower()])
        
        return recommendations
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get analyzer cache statistics."""
        total = self._cache_hits + self._cache_misses
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": self._cache_hits / total if total > 0 else 0,
            "cache_manager_stats": cache_manager.stats()
        }
    
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
