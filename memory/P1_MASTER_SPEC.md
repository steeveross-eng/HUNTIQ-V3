# BIONIC™ P1 - Master Specification Document
## Géo-Suite Nord-Américaine

**Version:** 1.0.0  
**Date:** 2026-02-04  
**Statut:** En cours d'implémentation

---

## 1. Vue d'Ensemble

La Phase P1 introduit une nouvelle suite de 5 moteurs géospatiaux conçus pour être **100% North America Ready**. Tous les moteurs utilisent exclusivement des sources de données gratuites, ouvertes et publiques.

### 1.1 Contrainte Absolue
> **AUCUNE** dépendance à des API payantes ou à des licences commerciales.

### 1.2 Moteurs de la Suite
| # | Moteur | Description | Priorité |
|---|--------|-------------|----------|
| 1 | `corridorEngine` | Détection de corridors fauniques | P1 |
| 2 | `landcoverEngine` | Classification du couvert végétal | P2 |
| 3 | `nutritionEngine` | Indice nutritionnel par espèce | P3 |
| 4 | `populationDensityEngine` | Densité de population animale | P4 |
| 5 | `huntingPressureModule` | Modélisation pression de chasse | P5 |

---

## 2. Sources de Données (100% Gratuites)

### 2.1 Québec
| Source | Type | URL | Licence |
|--------|------|-----|---------|
| SIGÉOM | WMS | servicescarto.mern.gouv.qc.ca | Données ouvertes Québec |
| MFFP | GeoJSON | donneesquebec.ca | CC-BY 4.0 |
| GRHQ | WMS | Cartes Québec | CC-BY 4.0 |
| LiDAR QC | WMS | Forêt ouverte | CC-BY 4.0 |

### 2.2 Canada
| Source | Type | URL | Licence |
|--------|------|-----|---------|
| CanVec | WMS | maps.geogratis.gc.ca | Open Government Licence |
| NRCan DEM | WMS | geogratis.gc.ca | Open Government Licence |
| GéoBase | WFS | geogratis.gc.ca | Open Government Licence |

### 2.3 États-Unis
| Source | Type | URL | Licence |
|--------|------|-----|---------|
| NLCD | WMS | mrlc.gov | Public Domain |
| USGS | REST API | nationalmap.gov | Public Domain |
| USDA Plants | REST API | plants.usda.gov | Public Domain |
| USFWS | Data Portal | fws.gov | Public Domain |

### 2.4 Global
| Source | Type | URL | Licence |
|--------|------|-----|---------|
| OpenStreetMap | Overpass API | overpass-api.de | ODbL |
| NASA MODIS | REST API | earthdata.nasa.gov | Public Domain |
| NOAA | REST API | weather.gov | Public Domain |

---

## 3. Architecture Technique

### 3.1 Structure des Fichiers
```
/app/bionic/engines/geospatial/
├── __init__.py                    # Base classes & enums
├── geo_core/                      # Module commun GeoCore
│   ├── __init__.py
│   ├── normalizer.py             # Normalisation géospatiale
│   ├── tiler.py                  # Tuilage des données
│   ├── indexer.py                # Indexation spatiale
│   └── loaders/                  # Chargeurs de données
│       ├── __init__.py
│       ├── sigeom_loader.py
│       ├── canvec_loader.py
│       ├── nlcd_loader.py
│       └── usgs_loader.py
├── corridor_engine.py             # corridorEngine (existant)
├── landcover_engine.py            # landcoverEngine
├── nutrition_engine.py            # nutritionEngine
├── population_density_engine.py   # populationDensityEngine
├── hunting_pressure_module.py     # huntingPressureModule
├── map_style_manager.py           # Map Style Manager
├── unified_output.py              # Unified Output Contracts
└── api/
    └── endpoints.py               # Tous les endpoints FastAPI
```

### 3.2 Module GeoCore (Commun)

Le module GeoCore centralise:
- **Normalisation**: CRS unifié (EPSG:4326), formats standardisés
- **Tuilage**: Découpage en tuiles pour performance
- **Indexation**: Index spatial pour requêtes rapides
- **Loaders**: Chargeurs spécifiques par source

```python
# Utilisation type
from geospatial.geo_core import GeoCore

core = GeoCore()
data = await core.load_landcover(lat, lon, radius_km)
normalized = core.normalize(data, target_crs="EPSG:4326")
indexed = core.index_spatial(normalized)
```

---

## 4. Unified Output Contracts

### 4.1 Format de Base
Tous les moteurs produisent des sorties compatibles avec `BehaviorFusionEngine` (P2).

```json
{
  "metadata": {
    "engine_name": "string",
    "engine_version": "string",
    "analysis_id": "string",
    "analyzed_at": "ISO8601",
    "processing_time_ms": "int",
    "data_sources_used": ["string"],
    "region": "quebec|canada_other|usa",
    "confidence": "float (0-1)",
    "confidence_level": "very_high|high|moderate|low|very_low"
  },
  "location": {
    "lat": "float",
    "lon": "float",
    "radius_km": "float"
  },
  "score": {
    "value": "float (0-100)",
    "level": "exceptional|excellent|good|moderate|low|poor",
    "components": {},
    "interpretation": "string"
  },
  "data": {},
  "recommendations": ["string"],
  "fusion_hooks": {
    "behavior_compatibility": "float (0-1)",
    "seasonal_modifier": "float",
    "activity_correlation": "float"
  }
}
```

### 4.2 Interface de Fusion P2
Chaque moteur expose une méthode `get_fusion_output()`:

```python
def get_fusion_output(self) -> FusionCompatibleOutput:
    """Retourne une sortie compatible avec BehaviorFusionEngine."""
    return {
        "score_normalized": self.score / 100,
        "confidence": self.confidence,
        "weight_suggestion": self.fusion_weight,
        "seasonal_factor": self.seasonal_modifier,
        "species_factors": self.species_scores
    }
```

---

## 5. Spécifications par Moteur

### 5.1 corridorEngine

**Objectif:** Détecter les corridors de déplacement fauniques.

**Sources de données:**
- Québec: SIGÉOM (géologie), GRHQ (hydrographie)
- Canada: CanVec (hydrographie, transport)
- USA: USGS (élévation), NLCD (couvert)
- Global: OSM (routes, forêts)

**Types de corridors:**
| Type | Description | Largeur typique |
|------|-------------|-----------------|
| `riparian` | Cours d'eau | 50-500m |
| `ridgeline` | Crêtes | 100-300m |
| `forest_edge` | Lisières | 30-100m |
| `valley` | Vallées | 200-1000m |
| `agricultural_edge` | Bordures agricoles | 20-80m |

**Modèle Pydantic:**
```python
class CorridorAnalysis(BaseModel):
    corridor_score: float = Field(ge=0, le=100)
    corridors: List[Corridor]
    connectivity_index: float = Field(ge=0, le=1)
    bottlenecks: List[Bottleneck]
    species_scores: Dict[str, float]
    seasonal_scores: Dict[str, float]
    current_season: str
```

**Endpoints:**
| Route | Method | Description |
|-------|--------|-------------|
| `/api/bionic/corridor/analyze` | POST | Analyse complète |
| `/api/bionic/corridor/species/{species}` | GET | Score par espèce |
| `/api/bionic/corridor/connectivity` | GET | Indice de connectivité |
| `/api/bionic/corridor/bottlenecks` | GET | Goulots détectés |

**KPIs:**
- Précision détection: >85%
- Couverture espèces: 8
- Temps réponse P95: <500ms

---

### 5.2 landcoverEngine

**Objectif:** Classifier le couvert végétal et analyser la structure forestière.

**Sources de données:**
- Québec: SIGÉOM (peuplements), Forêt ouverte
- Canada: CanVec (zones boisées), NRCan (couvert terrestre)
- USA: NLCD (couvert 2021), USDA (inventaire forestier)
- Global: OSM, NASA MODIS (NDVI)

**Types de couvert:**
| Code | Type | Qualité habitat |
|------|------|-----------------|
| `deciduous_forest` | Feuillus | Haute (deer) |
| `coniferous_forest` | Conifères | Haute (moose) |
| `mixed_forest` | Mixte | Haute (bear) |
| `shrubland` | Arbustes | Moyenne |
| `grassland` | Prairies | Basse |
| `wetland` | Milieux humides | Haute (waterfowl) |
| `agricultural` | Agricole | Variable |

**Modèle Pydantic:**
```python
class LandcoverAnalysis(BaseModel):
    cover_score: float = Field(ge=0, le=100)
    dominant_cover: LandCoverType
    cover_composition: Dict[str, float]
    edge_density_m_ha: float
    thermal_cover_percent: float
    structural_diversity: float = Field(ge=0, le=1)
    species_habitat_scores: Dict[str, float]
```

**Endpoints:**
| Route | Method | Description |
|-------|--------|-------------|
| `/api/bionic/landcover/analyze` | POST | Analyse complète |
| `/api/bionic/landcover/composition` | GET | Composition % |
| `/api/bionic/landcover/edge-density` | GET | Densité de lisières |
| `/api/bionic/landcover/thermal-cover` | GET | Couvert thermique |

**KPIs:**
- Précision classification: >90%
- Résolution: 30m (NLCD) / 10m (SIGÉOM)
- Temps réponse P95: <400ms

---

### 5.3 nutritionEngine

**Objectif:** Calculer l'indice nutritionnel par espèce et saison.

**Sources de données:**
- Québec: SIGÉOM (végétation), MFFP (peuplements)
- Canada: NRCan (couvert), CanVec
- USA: USDA Plants, NLCD, USGS
- Global: NASA MODIS (NDVI saisonnier)

**Facteurs nutritionnels:**
| Espèce | Printemps | Été | Automne | Hiver |
|--------|-----------|-----|---------|-------|
| deer | Herbacées | Feuillage | Glands | Brout |
| moose | Aquatiques | Feuillage | Brout | Brout |
| bear | Racines | Baies | Glands/Baies | N/A |
| turkey | Insectes | Fruits | Glands | Graines |

**Modèle Pydantic:**
```python
class NutritionAnalysis(BaseModel):
    nutrition_score: float = Field(ge=0, le=100)
    food_availability: str  # abundant/moderate/scarce
    species_nutrition: Dict[str, float]
    mast_index: float = Field(ge=0, le=100)
    browse_quality: float = Field(ge=0, le=100)
    seasonal_variation: Dict[str, float]
    deficiencies: List[str]
```

**Endpoints:**
| Route | Method | Description |
|-------|--------|-------------|
| `/api/bionic/nutrition/analyze` | POST | Analyse complète |
| `/api/bionic/nutrition/species/{species}` | GET | Nutrition par espèce |
| `/api/bionic/nutrition/mast-index` | GET | Indice de glandée |
| `/api/bionic/nutrition/browse-quality` | GET | Qualité brout |

**KPIs:**
- Couverture espèces: 8
- Précision saisonnière: >80%
- Temps réponse P95: <450ms

---

### 5.4 populationDensityEngine

**Objectif:** Estimer la densité de population animale et les tendances.

**Sources de données:**
- Québec: MFFP (récoltes), UGAF, ZEC, Réserves
- Canada: Données provinciales de récolte
- USA: USFWS (harvest survey), State wildlife agencies
- Global: Études scientifiques

**Données historiques (2015-2024):**
| Région | Espèce | Tendance |
|--------|--------|----------|
| Laurentides | deer | Stable |
| Saguenay | moose | Stable |
| Outaouais | deer | Croissante |
| Abitibi | moose | Croissante |
| Vermont | deer | Stable |

**Modèle Pydantic:**
```python
class PopulationDensityAnalysis(BaseModel):
    density_score: float = Field(ge=0, le=100)
    density_category: str  # high/medium/low/very_low
    species_densities: Dict[str, float]  # per km²
    trend: str  # increasing/stable/decreasing
    confidence_level: float = Field(ge=0, le=1)
    harvest_pressure: float = Field(ge=0, le=1)
    data_year_range: str
```

**Endpoints:**
| Route | Method | Description |
|-------|--------|-------------|
| `/api/bionic/population/density` | POST | Densité estimée |
| `/api/bionic/population/trend/{species}` | GET | Tendance par espèce |
| `/api/bionic/population/harvest` | GET | Données de récolte |
| `/api/bionic/population/regional` | GET | Comparaison régionale |

**KPIs:**
- Couverture espèces: 8
- Données historiques: 10 ans
- Temps réponse P95: <350ms

---

### 5.5 huntingPressureModule

**Objectif:** Modéliser la pression de chasse et son impact comportemental.

**Sources de données:**
- Québec: MFFP (permis), ZEC (fréquentation), SEPAQ
- Canada: Données provinciales
- USA: USFWS, State licensing data
- Global: OSM (accès routier)

**Facteurs de pression:**
| Facteur | Poids | Source |
|---------|-------|--------|
| Densité routes | 0.25 | OSM |
| Permis vendus | 0.30 | MFFP/USFWS |
| Distance ZEC | 0.20 | MFFP |
| Population humaine | 0.15 | Census |
| Historique récolte | 0.10 | Données ouvertes |

**Modèle Pydantic:**
```python
class HuntingPressureAnalysis(BaseModel):
    pressure_score: float = Field(ge=0, le=100)
    pressure_level: str  # extreme/high/moderate/low/minimal
    behavioral_impact: float = Field(ge=-1, le=1)
    optimal_timing: List[TimeWindow]
    avoidance_zones: List[Zone]
    weekly_pattern: Dict[str, float]
```

**Endpoints:**
| Route | Method | Description |
|-------|--------|-------------|
| `/api/bionic/hunting-pressure/analyze` | POST | Analyse complète |
| `/api/bionic/hunting-pressure/impact` | GET | Impact comportemental |
| `/api/bionic/hunting-pressure/optimal-timing` | GET | Fenêtres optimales |
| `/api/bionic/hunting-pressure/zones` | GET | Zones à éviter |

**KPIs:**
- Précision: >85%
- Résolution temporelle: Hebdomadaire
- Temps réponse P95: <300ms

---

## 6. Pipelines de Données

### 6.1 Pipeline d'Ingestion
```
Source (WMS/API) → Extraction → Validation → Normalisation → Stockage
```

### 6.2 Pipeline de Traitement
```
Données brutes → Tuilage → Indexation → Calcul scores → Cache
```

### 6.3 Configuration du Cache
| Niveau | TTL | Type |
|--------|-----|------|
| L1 (RAM) | 5 min | Résultats récents |
| L2 (Disk) | 1-24h | Données statiques |
| L3 (Redis) | 7 jours | Données partagées |

---

## 7. Tests d'Intégration

### 7.1 Scénarios de Test Multi-Territoires
| ID | Territoire | Coordonnées | Espèce |
|----|------------|-------------|--------|
| QC-01 | Laurentides | 46.5, -74.5 | deer |
| QC-02 | Saguenay | 48.5, -71.0 | moose |
| CA-01 | Ontario | 45.5, -78.0 | deer |
| CA-02 | BC | 49.5, -123.0 | bear |
| US-01 | Vermont | 44.5, -72.5 | deer |
| US-02 | Maine | 45.0, -69.5 | moose |

### 7.2 Métriques de Cohérence
| Paire de Moteurs | Cohérence Cible |
|------------------|-----------------|
| corridor ↔ landcover | >85% |
| nutrition ↔ landcover | >80% |
| population ↔ pressure | >90% |
| tous ↔ behavior_suite | >75% |

---

## 8. Map Style Manager

### 8.1 Configuration
Le `MapStyleManager` gère:
- Style de base clair (OSM Bright)
- Transparence des couches
- Légendes dynamiques
- Ordre des superpositions

### 8.2 Styles Disponibles
| ID | Nom | Description |
|----|-----|-------------|
| `light` | OSM Bright | Style clair par défaut |
| `satellite` | Satellite | Imagerie satellite |
| `terrain` | Terrain | Relief et contours |
| `hunting` | Chasse | Optimisé pour la chasse |

---

## 9. Intégration avec BehaviorFusionEngine (P2)

### 9.1 Interface de Fusion
Les 5 moteurs géospatiaux exposent une interface commune pour la fusion avec la `Behavior Suite`:

```python
class FusionInterface:
    def get_fusion_output(self) -> Dict:
        """Sortie compatible avec BehaviorFusionEngine."""
        pass
    
    def get_behavior_correlation(self) -> float:
        """Corrélation avec les scores comportementaux."""
        pass
    
    def get_seasonal_modifier(self, season: str) -> float:
        """Modificateur saisonnier pour la fusion."""
        pass
```

### 9.2 Poids de Fusion par Moteur
| Moteur | Behavior | Seasonal | Activity | Movement |
|--------|----------|----------|----------|----------|
| corridor | 0.25 | 0.20 | 0.20 | 0.35 |
| landcover | 0.25 | 0.30 | 0.15 | 0.30 |
| nutrition | 0.20 | 0.35 | 0.15 | 0.30 |
| population | 0.30 | 0.25 | 0.25 | 0.20 |
| pressure | 0.35 | 0.20 | 0.30 | 0.15 |

---

## 10. Checklist d'Implémentation

### 10.1 Module GeoCore
- [ ] `normalizer.py` - Normalisation CRS/formats
- [ ] `tiler.py` - Tuilage des données
- [ ] `indexer.py` - Indexation spatiale
- [ ] `loaders/sigeom_loader.py` - Loader SIGÉOM
- [ ] `loaders/canvec_loader.py` - Loader CanVec
- [ ] `loaders/nlcd_loader.py` - Loader NLCD
- [ ] `loaders/usgs_loader.py` - Loader USGS

### 10.2 Moteurs
- [x] `corridor_engine.py` - En cours
- [ ] `landcover_engine.py` - À faire
- [ ] `nutrition_engine.py` - À faire
- [ ] `population_density_engine.py` - À faire
- [ ] `hunting_pressure_module.py` - À faire

### 10.3 Infrastructure
- [ ] `unified_output.py` - Contracts de sortie
- [ ] `map_style_manager.py` - Gestionnaire de styles
- [ ] `api/endpoints.py` - Endpoints FastAPI

### 10.4 Tests
- [ ] Tests unitaires par moteur
- [ ] Tests d'intégration multi-territoires
- [ ] Tests de cohérence inter-moteurs
- [ ] Tests de performance (P95)

---

*Document généré automatiquement par BIONIC™ P1 Builder*
*Contrainte: Sources 100% gratuites et publiques uniquement*
