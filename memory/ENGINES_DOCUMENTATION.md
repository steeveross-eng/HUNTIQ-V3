# BIONIC™ Engines Documentation - Phase 3

## Vue d'ensemble

Cette documentation décrit l'implémentation de la Phase 3 des moteurs BIONIC™, incluant l'intégration des données réelles et le système de cache multi-niveaux.

## Moteurs Implémentés

### 1. Sentinel Engine (Végétation)
**Endpoint:** `/api/bionic/sentinel/analyze/point`
**Description:** Analyse de la végétation basée sur les indices spectraux MODIS/Sentinel-2.

**Indices calculés:**
- NDVI (Normalized Difference Vegetation Index)
- NDWI (Normalized Difference Water Index)
- EVI (Enhanced Vegetation Index)
- SAVI (Soil Adjusted Vegetation Index)

**Données:**
- Source: Modèle saisonnier calibré MODIS MOD13Q1 (2015-2023)
- Confiance: 78%

**Sortie:**
```json
{
  "indices": {"ndvi": 0.65, "ndwi": -0.15, "evi": 0.52, "savi": 0.58},
  "hunting_score": {"score": 82, "level": "bon"},
  "habitat": {"type": "mixed_forest", "suitable_species": ["deer", "moose"]},
  "phenology": {"stage": "maturity", "green_percent": 95}
}
```

### 2. SIGÉOM Engine (Géologie)
**Endpoint:** `/api/bionic/sigeom/analyze/point`
**Description:** Analyse géologique basée sur les données SIGÉOM du MERN Québec.

**Données analysées:**
- Province géologique (Bouclier canadien, Basses-Terres, Appalaches, Fosse du Labrador)
- Dépôts de surface (till, sable/gravier, argile marine, tourbe, alluvions, roc)
- Socle rocheux

**Sortie:**
```json
{
  "geological_province": {"code": "bouclier_canadien", "name": "Bouclier canadien"},
  "surficial_deposit": {"code": "till", "drainage": "good"},
  "hunting_relevance": {"species_affinity": {"moose": "excellent", "deer": "moderate"}}
}
```

### 3. Terrain Engine (Topographie)
**Endpoint:** `/api/bionic/terrain/analyze/point`
**Description:** Analyse du terrain incluant élévation, pente, exposition et TPI.

**Métriques:**
- Élévation (m)
- Pente (degrés/pourcentage)
- Exposition (N, NE, E, SE, S, SW, W, NW)
- TPI (Topographic Position Index): vallée, pente, plat, crête

**Sortie:**
```json
{
  "metrics": {"elevation_m": 350, "slope_degrees": 12, "aspect": "SE", "tpi": 0.35},
  "slope_analysis": {"difficulty_level": "modéré", "mobility_score": 75},
  "aspect_analysis": {"thermal_quality": "warm", "hunting_score": 85}
}
```

### 4. Pressure Engine (Pression Humaine)
**Endpoint:** `/api/bionic/pressure/analyze/point`
**Description:** Analyse de la pression humaine basée sur les données OSM.

**Métriques:**
- Densité routière
- Densité de bâtiments
- Indice de remoteness
- Impact sur le comportement du gibier

**Sortie:**
```json
{
  "pressure_metrics": {"pressure_index": 25, "hunting_suitability": 75},
  "remoteness": {"score": 80, "level": "remote"},
  "hunting_impact": {"animal_behavior": "Gibier adapté", "success_factor": 1.15}
}
```

## Endpoint Consolidé

### Real Data Analysis
**Endpoint:** `/api/bionic/core/analyze/real`
**Description:** Analyse complète combinant tous les moteurs avec données réelles et cache.

**Paramètres:**
- `lat`, `lon`: Coordonnées
- `target_species`: Espèce cible (deer, moose, bear, etc.)
- `include_vegetation`, `include_geology`, `include_terrain`, `include_pressure`: Modules à inclure
- `use_cache`: Utiliser le cache (recommandé: true)

**Sortie:**
```json
{
  "location": {"lat": 47.5, "lon": -72.5},
  "modules": {
    "vegetation": {...},
    "geology": {...},
    "terrain": {...},
    "pressure": {...}
  },
  "global_score": 68.5,
  "global_rating": "good",
  "cache_hit_rate": 0.75,
  "processing_time_ms": 450,
  "recommendations": [...]
}
```

## Système de Cache

### Architecture Multi-Niveaux
- **L1 (RAM):** TTL 5 minutes, accès instantané
- **L2 (Disque):** TTL 1 heure (ou 24h pour données géologiques)
- **L3 (Cloud):** Prévu pour implémentation future

### Performance
- Premier appel (cache miss): ~4-5 secondes
- Appels suivants (cache hit): ~0-10 ms
- Taux de hit typique: 75-100%

## Sources de Données

### APIs Utilisées
1. **Open-Meteo** - Météo temps réel
2. **Open-Elevation** - Données d'élévation
3. **NASA GIBS** - MODIS NDVI/EVI
4. **MERN Québec (SIGÉOM)** - Géologie
5. **OpenStreetMap (Overpass)** - Infrastructure humaine

### Modèles Calibrés
- NDVI saisonnier: Basé sur MODIS MOD13Q1 (2015-2023)
- Géologie: Provinces géologiques du Québec
- Dépôts: Distribution probabiliste par province

## Utilisation Frontend

```javascript
import { useBionicEngines } from '@/hooks/useBionicEngines';

const MyComponent = () => {
  const { fetchRealDataAnalysis, loading, data } = useBionicEngines();
  
  const handleAnalyze = async (lat, lon) => {
    const result = await fetchRealDataAnalysis(lat, lon, {
      targetSpecies: 'moose',
      useCache: true
    });
    console.log('Score global:', result.global_score);
  };
};
```

## Prochaines Étapes (Phase 4)

1. **Intelligence Faunique:** Intégration de modèles de comportement animal
2. **Prédictions IA:** Prédictions 24h, 72h, 7j basées sur ML
3. **Corridors Fauniques:** Analyse de connectivité
4. **LandCover Engine:** Classification NLCD/CanLandCover
5. **Cache L3 Cloud:** Cache distribué pour multi-utilisateurs

---
*Documentation BIONIC™ v2.0 - Phase 3 Real Data Implementation*
*Mise à jour: Février 2026*
