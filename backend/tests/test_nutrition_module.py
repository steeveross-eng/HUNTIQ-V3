"""
Tests for BIONIC™ Nutrition Module
"""

import pytest
import asyncio
from geospatial.controllers.nutrition_controller import (
    nutrition_engine,
    get_species_profile,
    classify_resources,
    detect_deficiencies,
    generate_recommendations,
    SPECIES_PROFILES
)


class TestSpeciesProfiles:
    """Tests for species profiles"""
    
    def test_get_cerf_profile(self):
        profile = get_species_profile("cerf")
        assert profile is not None
        assert profile["id"] == "cerf"
        assert profile["energy"] == 100
        assert profile["protein"] == 18
    
    def test_get_orignal_profile(self):
        profile = get_species_profile("orignal")
        assert profile is not None
        assert profile["id"] == "orignal"
        assert profile["energy"] == 160
    
    def test_get_profile_english_mapping(self):
        """Test English to French species mapping"""
        profile = get_species_profile("deer")
        assert profile is not None
        assert profile["id"] == "cerf"
        
        profile = get_species_profile("moose")
        assert profile is not None
        assert profile["id"] == "orignal"
    
    def test_unknown_species_returns_none(self):
        profile = get_species_profile("unknown_species")
        assert profile is None


class TestResourceClassifier:
    """Tests for resource classification"""
    
    def test_classify_feuillus(self):
        data = [{"type": "feuillus", "area": 1000}]
        result = classify_resources(data)
        
        assert len(result) == 1
        assert result[0]["nutrition_flag"] == "ok"
        assert result[0]["nutrition"]["energy"] == 80
    
    def test_classify_unknown_type(self):
        data = [{"type": "unknown_type", "area": 500}]
        result = classify_resources(data)
        
        assert len(result) == 1
        assert result[0]["nutrition_flag"] == "unknown_landcover_type"
        assert result[0]["nutrition"] is None
    
    def test_classify_multiple_zones(self):
        data = [
            {"type": "feuillus", "area": 1000},
            {"type": "coniferes", "area": 2000},
            {"type": "milieu_humide", "area": 500}
        ]
        result = classify_resources(data)
        
        assert len(result) == 3
        assert all(r["nutrition_flag"] == "ok" for r in result)


class TestDeficiencyDetector:
    """Tests for deficiency detection"""
    
    def test_detect_deficiencies_cerf(self):
        species_needs = SPECIES_PROFILES["cerf"]
        resources = classify_resources([
            {"type": "feuillus", "area": 1000},
            {"type": "coniferes", "area": 1000}
        ])
        
        result = detect_deficiencies(species_needs, resources)
        
        assert result["status"] in ["deficiencies_detected", "no_deficiency"]
        assert "site_avg" in result
        assert "details" in result
    
    def test_detect_no_data(self):
        species_needs = SPECIES_PROFILES["cerf"]
        resources = []
        
        result = detect_deficiencies(species_needs, resources)
        
        assert result["status"] == "no_data"
    
    def test_detect_energy_deficiency(self):
        species_needs = {"energy": 100, "protein": 10, "calcium": 0.3, "phosphorus": 0.2}
        resources = [{"nutrition": {"energy": 60, "protein": 12, "calcium": 0.4, "phosphorus": 0.3}}]
        
        result = detect_deficiencies(species_needs, resources)
        
        assert result["details"]["energy"]["status"] == "carence"
        assert result["details"]["protein"]["status"] == "ok"


class TestRecommendationEngine:
    """Tests for recommendation generation"""
    
    def test_generate_recommendations_with_deficiencies(self):
        deficiency_report = {
            "status": "deficiencies_detected",
            "details": {
                "energy": {"status": "carence"},
                "protein": {"status": "ok"},
                "calcium": {"status": "carence"},
                "phosphorus": {"status": "ok"}
            }
        }
        species_profile = SPECIES_PROFILES["cerf"]
        
        recs = generate_recommendations(deficiency_report, species_profile)
        
        assert len(recs) == 2
        assert any("Énergie" in r for r in recs)
        assert any("Calcium" in r for r in recs)
    
    def test_generate_recommendations_no_deficiency(self):
        deficiency_report = {
            "status": "no_deficiency",
            "details": {
                "energy": {"status": "ok"},
                "protein": {"status": "ok"},
                "calcium": {"status": "ok"},
                "phosphorus": {"status": "ok"}
            }
        }
        species_profile = SPECIES_PROFILES["cerf"]
        
        recs = generate_recommendations(deficiency_report, species_profile)
        
        assert len(recs) == 1
        assert "Aucune carence" in recs[0]


class TestNutritionEngine:
    """Tests for main nutrition engine"""
    
    @pytest.mark.asyncio
    async def test_run_full_analysis(self):
        landcover_data = [
            {"type": "feuillus", "area": 5000},
            {"type": "coniferes", "area": 3000}
        ]
        
        result = await nutrition_engine.run("cerf", landcover_data)
        
        assert "species" in result
        assert "resources" in result
        assert "deficiency_report" in result
        assert "recommendations" in result
        assert "meta" in result
        
        assert result["species"]["key"] == "cerf"
        assert result["meta"]["module"] == "NutritionEngine"
    
    @pytest.mark.asyncio
    async def test_run_with_invalid_species(self):
        with pytest.raises(ValueError):
            await nutrition_engine.run("invalid_species", [])
    
    def test_list_species(self):
        species = nutrition_engine.list_species()
        assert len(species) == 3
        assert all("id" in s for s in species)
    
    def test_list_landcover_types(self):
        types = nutrition_engine.list_landcover_types()
        assert "feuillus" in types
        assert "coniferes" in types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
