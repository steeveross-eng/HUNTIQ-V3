"""
HUNTIQ V3 - BIONIC™ Nutrition Module Controller
Backend controller for nutrition analysis integration

This module mirrors the JavaScript nutrition engine for backend execution.
It can be called from the geospatial orchestrator.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SPECIES PROFILES
# =============================================================================

SPECIES_PROFILES = {
    "cerf": {
        "id": "cerf",
        "label": "Cerf de Virginie",
        "energy": 100,
        "protein": 18,
        "calcium": 0.6,
        "phosphorus": 0.3,
        "notes": "Besoins variables selon la saison, la condition corporelle et la reproduction."
    },
    "orignal": {
        "id": "orignal",
        "label": "Orignal",
        "energy": 160,
        "protein": 20,
        "calcium": 0.8,
        "phosphorus": 0.4,
        "notes": "Fortement dépendant des feuillus, régénération et zones humides."
    },
    "ours_noir": {
        "id": "ours_noir",
        "label": "Ours noir",
        "energy": 180,
        "protein": 16,
        "calcium": 0.5,
        "phosphorus": 0.3,
        "notes": "Régime opportuniste, dépendance aux petits fruits et sources énergétiques."
    }
}

# Map English species names to French
SPECIES_MAPPING = {
    "deer": "cerf",
    "moose": "orignal",
    "black_bear": "ours_noir",
    "bear": "ours_noir",
}


def get_species_profile(species_key: str) -> Optional[Dict]:
    """Get species profile by key"""
    # Normalize key
    normalized_key = SPECIES_MAPPING.get(species_key.lower(), species_key.lower())
    return SPECIES_PROFILES.get(normalized_key)


# =============================================================================
# NUTRITION PROFILES BY LANDCOVER
# =============================================================================

NUTRITION_BY_LANDCOVER = {
    "feuillus": {"energy": 80, "protein": 12, "calcium": 0.4, "phosphorus": 0.25},
    "coniferes": {"energy": 60, "protein": 8, "calcium": 0.2, "phosphorus": 0.18},
    "plantes_herbacees": {"energy": 110, "protein": 20, "calcium": 0.5, "phosphorus": 0.3},
    "milieu_humide": {"energy": 90, "protein": 16, "calcium": 0.45, "phosphorus": 0.28},
    # English mappings
    "deciduous": {"energy": 80, "protein": 12, "calcium": 0.4, "phosphorus": 0.25},
    "coniferous": {"energy": 60, "protein": 8, "calcium": 0.2, "phosphorus": 0.18},
    "herbaceous": {"energy": 110, "protein": 20, "calcium": 0.5, "phosphorus": 0.3},
    "wetland": {"energy": 90, "protein": 16, "calcium": 0.45, "phosphorus": 0.28},
    "mixed_forest": {"energy": 70, "protein": 10, "calcium": 0.3, "phosphorus": 0.22},
}


# =============================================================================
# RESOURCE CLASSIFIER
# =============================================================================

def classify_resources(landcover_data: List[Dict]) -> List[Dict]:
    """Classify landcover data with nutrition profiles"""
    results = []
    
    for zone in landcover_data:
        zone_type = zone.get("type", "").lower()
        profile = NUTRITION_BY_LANDCOVER.get(zone_type)
        
        if not profile:
            results.append({
                **zone,
                "nutrition": None,
                "nutrition_flag": "unknown_landcover_type"
            })
        else:
            results.append({
                **zone,
                "nutrition": {
                    **profile,
                    "area": zone.get("area")
                },
                "nutrition_flag": "ok"
            })
    
    return results


# =============================================================================
# DEFICIENCY DETECTOR
# =============================================================================

def safe_average(values: List[float]) -> Optional[float]:
    """Calculate safe average of numeric values"""
    valid = [v for v in values if isinstance(v, (int, float)) and v is not None]
    if not valid:
        return None
    return sum(valid) / len(valid)


def round_value(value: Optional[float], decimals: int = 2) -> Optional[float]:
    """Round value safely"""
    if value is None:
        return None
    return round(value, decimals)


def compute_site_averages(site_resources: List[Dict]) -> Dict[str, Optional[float]]:
    """Compute average nutrition values for a site"""
    energy_vals = []
    protein_vals = []
    calcium_vals = []
    phosphorus_vals = []
    
    for r in site_resources:
        nutrition = r.get("nutrition")
        if not nutrition:
            continue
        
        if nutrition.get("energy") is not None:
            energy_vals.append(nutrition["energy"])
        if nutrition.get("protein") is not None:
            protein_vals.append(nutrition["protein"])
        if nutrition.get("calcium") is not None:
            calcium_vals.append(nutrition["calcium"])
        if nutrition.get("phosphorus") is not None:
            phosphorus_vals.append(nutrition["phosphorus"])
    
    return {
        "energy": round_value(safe_average(energy_vals)),
        "protein": round_value(safe_average(protein_vals)),
        "calcium": round_value(safe_average(calcium_vals)),
        "phosphorus": round_value(safe_average(phosphorus_vals))
    }


def detect_deficiencies(species_needs: Dict, site_resources: List[Dict]) -> Dict:
    """Detect nutritional deficiencies"""
    site_avg = compute_site_averages(site_resources)
    
    # Check if we have any data
    if all(v is None for v in site_avg.values()):
        return {
            "status": "no_data",
            "message": "Aucune donnée nutritionnelle exploitable pour ce territoire.",
            "site_avg": site_avg,
            "details": {}
        }
    
    details = {}
    
    for nutrient in ["energy", "protein", "calcium", "phosphorus"]:
        site_value = site_avg.get(nutrient)
        need_value = species_needs.get(nutrient)
        
        if site_value is not None and need_value is not None:
            status = "carence" if site_value < need_value else "ok"
        else:
            status = "unknown"
        
        details[nutrient] = {
            "status": status,
            "site": site_value,
            "need": need_value
        }
    
    has_deficiency = any(d.get("status") == "carence" for d in details.values())
    
    return {
        "status": "deficiencies_detected" if has_deficiency else "no_deficiency",
        "site_avg": site_avg,
        "details": details
    }


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

def generate_recommendations(deficiency_report: Dict, species_profile: Dict) -> List[str]:
    """Generate recommendations based on deficiencies"""
    if not deficiency_report or deficiency_report.get("status") == "no_data":
        return [
            "Impossible de générer des recommandations : données nutritionnelles insuffisantes."
        ]
    
    recs = []
    details = deficiency_report.get("details", {})
    
    if details.get("energy", {}).get("status") == "carence":
        recs.append(
            "Énergie : Ajouter des sources énergétiques "
            "(grains, blocs énergétiques, coupes favorisant les rejets)."
        )
    
    if details.get("protein", {}).get("status") == "carence":
        recs.append(
            "Protéines : Favoriser les légumineuses, herbacées, "
            "ou installer des suppléments protéinés."
        )
    
    if details.get("calcium", {}).get("status") == "carence":
        recs.append(
            "Calcium : Installer des blocs minéraux riches en calcium."
        )
    
    if details.get("phosphorus", {}).get("status") == "carence":
        recs.append(
            "Phosphore : Utiliser des minéraux complets avec ratio Ca/P équilibré."
        )
    
    if not recs:
        label = species_profile.get("label", "cette espèce")
        recs.append(
            f"Aucune carence majeure détectée pour {label}. "
            "Optimiser la tranquillité et la répartition spatiale."
        )
    
    return recs


# =============================================================================
# MAIN NUTRITION ENGINE
# =============================================================================

class NutritionEngine:
    """
    BIONIC™ Nutrition Engine
    Analyzes territory nutrition potential for hunting
    """
    
    VERSION = "0.1.0"
    MODULE_NAME = "NutritionEngine"
    
    def __init__(self):
        self.species_profiles = SPECIES_PROFILES
        self.landcover_profiles = NUTRITION_BY_LANDCOVER
    
    def get_species_profile(self, species_key: str) -> Optional[Dict]:
        """Get species nutritional needs profile"""
        return get_species_profile(species_key)
    
    def list_species(self) -> List[Dict]:
        """List all supported species"""
        return list(SPECIES_PROFILES.values())
    
    def list_landcover_types(self) -> List[str]:
        """List supported landcover types"""
        return list(NUTRITION_BY_LANDCOVER.keys())
    
    async def run(
        self,
        species_key: str,
        landcover_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Run full nutrition analysis
        
        Args:
            species_key: Species identifier (cerf, orignal, ours_noir, deer, moose, bear)
            landcover_data: List of landcover zones with type and area
        
        Returns:
            Complete nutrition analysis report
        """
        # Get species profile
        species_profile = self.get_species_profile(species_key)
        
        if not species_profile:
            raise ValueError(f"Espèce inconnue ou non supportée : {species_key}")
        
        # Classify resources
        resources = classify_resources(landcover_data)
        
        # Detect deficiencies
        deficiency_report = detect_deficiencies(species_profile, resources)
        
        # Generate recommendations
        recommendations = generate_recommendations(deficiency_report, species_profile)
        
        return {
            "species": {
                "key": species_key,
                "profile": species_profile
            },
            "resources": resources,
            "deficiency_report": deficiency_report,
            "recommendations": recommendations,
            "meta": {
                "module": self.MODULE_NAME,
                "version": self.VERSION,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }


# Singleton instance
nutrition_engine = NutritionEngine()
