"""
BIONIC™ Sentinel Engine - Vegetation Indices Calculator

Calcul des indices de végétation à partir des bandes spectrales Sentinel-2.
"""

import math
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class VegetationIndices:
    """
    Calculateur d'indices de végétation pour l'analyse de territoires de chasse.
    
    Indices supportés:
    - NDVI (Normalized Difference Vegetation Index)
    - EVI (Enhanced Vegetation Index)
    - SAVI (Soil Adjusted Vegetation Index)
    - NDWI (Normalized Difference Water Index)
    - NBR (Normalized Burn Ratio)
    """
    
    # Sentinel-2 band wavelengths (nm)
    BANDS = {
        "B02": {"name": "Blue", "wavelength": 490, "resolution": 10},
        "B03": {"name": "Green", "wavelength": 560, "resolution": 10},
        "B04": {"name": "Red", "wavelength": 665, "resolution": 10},
        "B05": {"name": "Red Edge 1", "wavelength": 705, "resolution": 20},
        "B06": {"name": "Red Edge 2", "wavelength": 740, "resolution": 20},
        "B07": {"name": "Red Edge 3", "wavelength": 783, "resolution": 20},
        "B08": {"name": "NIR", "wavelength": 842, "resolution": 10},
        "B8A": {"name": "NIR Narrow", "wavelength": 865, "resolution": 20},
        "B11": {"name": "SWIR 1", "wavelength": 1610, "resolution": 20},
        "B12": {"name": "SWIR 2", "wavelength": 2190, "resolution": 20},
    }
    
    # NDVI thresholds for vegetation classification
    NDVI_THRESHOLDS = {
        "water": (-1.0, 0.0),
        "bare_soil": (0.0, 0.15),
        "sparse_vegetation": (0.15, 0.3),
        "moderate_vegetation": (0.3, 0.5),
        "dense_vegetation": (0.5, 0.7),
        "very_dense_vegetation": (0.7, 1.0)
    }
    
    # Hunting relevance by vegetation type
    HUNTING_VEGETATION_VALUE = {
        "water": {"moose": "high", "deer": "moderate", "waterfowl": "excellent"},
        "bare_soil": {"moose": "low", "deer": "low", "bear": "moderate"},
        "sparse_vegetation": {"moose": "moderate", "deer": "high", "turkey": "high"},
        "moderate_vegetation": {"moose": "high", "deer": "high", "bear": "moderate"},
        "dense_vegetation": {"moose": "excellent", "deer": "excellent", "bear": "high"},
        "very_dense_vegetation": {"moose": "excellent", "deer": "high", "smallgame": "excellent"}
    }
    
    def __init__(self):
        self.thresholds = self.NDVI_THRESHOLDS
        self.hunting_value = self.HUNTING_VEGETATION_VALUE
    
    def calculate_ndvi(
        self,
        red: float,
        nir: float
    ) -> Dict[str, Any]:
        """
        Calculate NDVI (Normalized Difference Vegetation Index).
        
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            red: Red band reflectance (B04)
            nir: Near-infrared reflectance (B08)
            
        Returns:
            NDVI value and classification
        """
        if (nir + red) == 0:
            ndvi = 0
        else:
            ndvi = (nir - red) / (nir + red)
        
        # Clamp to valid range
        ndvi = max(-1, min(1, ndvi))
        
        # Classify
        classification = self._classify_ndvi(ndvi)
        
        return {
            "index": "NDVI",
            "value": round(ndvi, 4),
            "classification": classification,
            "description": self._get_ndvi_description(classification),
            "hunting_value": self.hunting_value.get(classification, {}),
            "bands_used": ["B04 (Red)", "B08 (NIR)"]
        }
    
    def calculate_evi(
        self,
        red: float,
        nir: float,
        blue: float,
        g: float = 2.5,
        c1: float = 6.0,
        c2: float = 7.5,
        l: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate EVI (Enhanced Vegetation Index).
        
        EVI is more sensitive in high biomass areas and reduces
        atmospheric influences.
        
        EVI = G * (NIR - Red) / (NIR + C1*Red - C2*Blue + L)
        """
        denominator = nir + c1 * red - c2 * blue + l
        if denominator == 0:
            evi = 0
        else:
            evi = g * (nir - red) / denominator
        
        evi = max(-1, min(1, evi))
        
        return {
            "index": "EVI",
            "value": round(evi, 4),
            "description": "Enhanced Vegetation Index - Sensible aux zones à forte biomasse",
            "quality": "high" if evi > 0.4 else "moderate" if evi > 0.2 else "low",
            "bands_used": ["B02 (Blue)", "B04 (Red)", "B08 (NIR)"]
        }
    
    def calculate_savi(
        self,
        red: float,
        nir: float,
        l: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calculate SAVI (Soil Adjusted Vegetation Index).
        
        SAVI reduces soil brightness influences.
        
        SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)
        """
        denominator = nir + red + l
        if denominator == 0:
            savi = 0
        else:
            savi = ((nir - red) / denominator) * (1 + l)
        
        savi = max(-1, min(1, savi))
        
        return {
            "index": "SAVI",
            "value": round(savi, 4),
            "description": "Soil Adjusted Vegetation Index - Corrigé pour l'influence du sol",
            "l_factor": l,
            "bands_used": ["B04 (Red)", "B08 (NIR)"]
        }
    
    def calculate_ndwi(
        self,
        green: float,
        nir: float
    ) -> Dict[str, Any]:
        """
        Calculate NDWI (Normalized Difference Water Index).
        
        NDWI detects water bodies and moisture content.
        
        NDWI = (Green - NIR) / (Green + NIR)
        """
        if (green + nir) == 0:
            ndwi = 0
        else:
            ndwi = (green - nir) / (green + nir)
        
        ndwi = max(-1, min(1, ndwi))
        
        # Water detection
        has_water = ndwi > 0.3
        
        return {
            "index": "NDWI",
            "value": round(ndwi, 4),
            "has_water": has_water,
            "water_probability": min(100, max(0, (ndwi + 1) * 50)) if ndwi > 0 else 0,
            "description": "Indice de détection d'eau",
            "hunting_note": "Zones d'abreuvement potentielles" if has_water else "Terrain sec",
            "bands_used": ["B03 (Green)", "B08 (NIR)"]
        }
    
    def calculate_nbr(
        self,
        nir: float,
        swir: float
    ) -> Dict[str, Any]:
        """
        Calculate NBR (Normalized Burn Ratio).
        
        NBR detects burned areas and fire severity.
        
        NBR = (NIR - SWIR) / (NIR + SWIR)
        """
        if (nir + swir) == 0:
            nbr = 0
        else:
            nbr = (nir - swir) / (nir + swir)
        
        nbr = max(-1, min(1, nbr))
        
        # Burn severity
        if nbr < -0.25:
            severity = "high_burn"
        elif nbr < 0.1:
            severity = "moderate_burn"
        elif nbr < 0.27:
            severity = "low_burn"
        else:
            severity = "unburned"
        
        return {
            "index": "NBR",
            "value": round(nbr, 4),
            "burn_severity": severity,
            "description": "Indice de brûlage - Détection des zones incendiées",
            "hunting_note": "Les zones brûlées attirent le gibier pour la repousse" if severity != "unburned" else "Zone non affectée",
            "bands_used": ["B08 (NIR)", "B12 (SWIR)"]
        }
    
    def calculate_all_indices(
        self,
        bands: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate all vegetation indices from band values.
        
        Args:
            bands: Dictionary with band values (B02, B03, B04, B08, B11/B12)
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "indices": {}
        }
        
        # NDVI
        if "B04" in bands and "B08" in bands:
            results["indices"]["ndvi"] = self.calculate_ndvi(
                bands["B04"], bands["B08"]
            )
        
        # EVI
        if all(b in bands for b in ["B02", "B04", "B08"]):
            results["indices"]["evi"] = self.calculate_evi(
                bands["B04"], bands["B08"], bands["B02"]
            )
        
        # SAVI
        if "B04" in bands and "B08" in bands:
            results["indices"]["savi"] = self.calculate_savi(
                bands["B04"], bands["B08"]
            )
        
        # NDWI
        if "B03" in bands and "B08" in bands:
            results["indices"]["ndwi"] = self.calculate_ndwi(
                bands["B03"], bands["B08"]
            )
        
        # NBR
        if "B08" in bands and ("B12" in bands or "B11" in bands):
            swir = bands.get("B12", bands.get("B11", 0))
            results["indices"]["nbr"] = self.calculate_nbr(
                bands["B08"], swir
            )
        
        # Overall vegetation score for hunting
        if "ndvi" in results["indices"]:
            ndvi_val = results["indices"]["ndvi"]["value"]
            results["hunting_score"] = self._calculate_hunting_score(ndvi_val)
        
        return results
    
    def _classify_ndvi(self, ndvi: float) -> str:
        """Classify NDVI value into vegetation category."""
        for category, (low, high) in self.thresholds.items():
            if low <= ndvi < high:
                return category
        return "unknown"
    
    def _get_ndvi_description(self, classification: str) -> str:
        """Get description for NDVI classification."""
        descriptions = {
            "water": "Eau ou surfaces humides",
            "bare_soil": "Sol nu ou très peu de végétation",
            "sparse_vegetation": "Végétation clairsemée",
            "moderate_vegetation": "Végétation modérée",
            "dense_vegetation": "Végétation dense",
            "very_dense_vegetation": "Végétation très dense (forêt mature)"
        }
        return descriptions.get(classification, "Non classifié")
    
    def _calculate_hunting_score(self, ndvi: float) -> Dict[str, Any]:
        """Calculate hunting potential score based on NDVI."""
        # Optimal NDVI for most game: 0.4-0.7 (forest edge/mixed)
        if 0.4 <= ndvi <= 0.7:
            score = 90 + (1 - abs(ndvi - 0.55) / 0.15) * 10
        elif 0.3 <= ndvi < 0.4 or 0.7 < ndvi <= 0.8:
            score = 70 + (min(abs(ndvi - 0.3), abs(ndvi - 0.8)) / 0.1) * 20
        elif ndvi < 0.3:
            score = max(20, ndvi * 200)
        else:
            score = 60
        
        return {
            "score": round(min(100, score), 1),
            "level": "excellent" if score >= 80 else "bon" if score >= 60 else "modéré" if score >= 40 else "faible",
            "interpretation": self._get_hunting_interpretation(ndvi)
        }
    
    def _get_hunting_interpretation(self, ndvi: float) -> str:
        """Get hunting interpretation based on NDVI."""
        if ndvi < 0:
            return "Zone d'eau - Idéal pour sauvagine et orignal"
        elif ndvi < 0.2:
            return "Terrain ouvert - Visibilité excellente mais peu de couvert"
        elif ndvi < 0.4:
            return "Lisière/transition - Excellent pour cerf et dindon"
        elif ndvi < 0.6:
            return "Forêt mixte - Habitat optimal pour cervidés"
        elif ndvi < 0.8:
            return "Forêt dense - Excellent couvert, pistage recommandé"
        else:
            return "Forêt très dense - Déplacement difficile, affût recommandé"


# Singleton instance
vegetation_indices = VegetationIndices()
