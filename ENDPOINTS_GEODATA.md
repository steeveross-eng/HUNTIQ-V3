# HUNTIQ V3 - Endpoints Géodonnées

## 🔌 Vue d'ensemble

Ce document liste tous les endpoints API du moteur géospatial BIONIC™.

**Base URL:** `/api/geospatial`
**Status:** Architecture préparée - Réponses placeholder

---

## 📋 Résumé des Endpoints

| Module | Endpoints | Status |
|--------|-----------|--------|
| Status | 2 | ✅ Préparé |
| LiDAR | 3 | ✅ Préparé |
| Sentinel | 3 | ✅ Préparé |
| Landsat | 2 | ✅ Préparé |
| SIGÉOM | 3 | ✅ Préparé |
| Hydro | 4 | ✅ Préparé |
| Géomorph | 4 | ✅ Préparé |
| Forêt | 4 | ✅ Préparé |
| IA | 4 | ✅ Préparé |
| Potentiel | 4 | ✅ Préparé |
| **TOTAL** | **33** | ✅ |

---

## 🔧 Status & Configuration

### GET /api/geospatial/status

Retourne le status du moteur géospatial et la disponibilité des sources.

**Response:**
```json
{
  "status": "ready",
  "engine_version": "1.0.0-alpha",
  "architecture_ready": true,
  "implementation_pending": true,
  "data_sources": {
    "lidar_quebec": {"status": "architecture_ready"},
    "sigeom": {"status": "architecture_ready"},
    "sentinel_2": {"status": "architecture_ready"},
    "landsat": {"status": "architecture_ready"},
    "hydro_quebec": {"status": "architecture_ready"},
    "osm": {"status": "architecture_ready"},
    "mffp_forest": {"status": "architecture_ready"}
  },
  "modules": {
    "lidar": "prepared",
    "sentinel": "prepared",
    "landsat": "prepared",
    "sigeom": "prepared",
    "hydro": "prepared",
    "geomorphology": "prepared",
    "forest": "prepared",
    "ai": "prepared",
    "potential": "prepared"
  }
}
```

---

### GET /api/geospatial/data-sources

Liste toutes les sources de données gratuites disponibles.

**Response:**
```json
{
  "sources": [
    {
      "id": "lidar_quebec",
      "name": "LiDAR Québec",
      "provider": "Gouvernement du Québec",
      "url": "https://www.donneesquebec.ca/",
      "license": "CC-BY 4.0",
      "coverage": "Zones urbaines et périurbaines",
      "resolution": "1m",
      "formats": ["LAZ", "GeoTIFF"],
      "free": true
    }
    // ... autres sources
  ]
}
```

---

## 📡 Module LiDAR

### POST /api/geospatial/lidar/query

Requête de données LiDAR pour une zone.

**Request Body:**
```json
{
  "bbox": {
    "min_lat": 45.5,
    "max_lat": 45.6,
    "min_lon": -73.7,
    "max_lon": -73.6
  },
  "resolution": 1.0,
  "include_dsm": true,
  "include_dtm": true,
  "include_chm": false
}
```

**Response:**
```json
{
  "request_id": "lidar_20260203120000",
  "status": "architecture_ready",
  "bbox": { ... },
  "dtm_url": null,
  "dsm_url": null,
  "chm_url": null,
  "metadata": {"note": "Implementation pending"}
}
```

---

### GET /api/geospatial/lidar/coverage

Retourne les zones de couverture LiDAR disponibles.

**Response:**
```json
{
  "status": "architecture_ready",
  "coverage_areas": [],
  "note": "Implementation pending"
}
```

---

### GET /api/geospatial/lidar/tiles

Liste les tuiles LiDAR disponibles.

**Query Parameters:**
- `bbox` (optional): Bounding box en format WKT

**Response:**
```json
{
  "status": "architecture_ready",
  "tiles": [],
  "note": "Implementation pending"
}
```

---

## 🛰 Module Sentinel-2

### POST /api/geospatial/sentinel/query

Requête d'imagerie Sentinel-2.

**Request Body:**
```json
{
  "bbox": { ... },
  "date_start": "2025-06-01T00:00:00Z",
  "date_end": "2025-09-30T00:00:00Z",
  "cloud_cover_max": 20.0,
  "indices": ["ndvi", "evi"],
  "bands": ["B02", "B03", "B04", "B08"]
}
```

**Response:**
```json
{
  "request_id": "sentinel_20260203120000",
  "status": "architecture_ready",
  "scene_id": null,
  "acquisition_date": null,
  "cloud_cover": null,
  "indices": {},
  "bands": {}
}
```

---

### GET /api/geospatial/sentinel/scenes

Liste les scènes Sentinel-2 disponibles.

**Query Parameters:**
- `bbox` (required): Bounding box
- `date_start` (required): Date de début
- `date_end` (required): Date de fin
- `cloud_max` (optional): Couverture nuageuse max (défaut: 20)

---

### GET /api/geospatial/sentinel/indices/{scene_id}

Calcule les indices de végétation pour une scène.

**Path Parameters:**
- `scene_id`: ID de la scène Sentinel-2

---

## 🛰 Module Landsat

### POST /api/geospatial/landsat/query

Requête d'imagerie Landsat 8/9.

**Request Body:**
```json
{
  "bbox": { ... },
  "date_start": "2025-06-01T00:00:00Z",
  "date_end": "2025-09-30T00:00:00Z",
  "satellite": "landsat_8",
  "cloud_cover_max": 20.0,
  "include_thermal": false
}
```

---

### GET /api/geospatial/landsat/scenes

Liste les scènes Landsat disponibles.

---

## 🪨 Module SIGÉOM

### POST /api/geospatial/sigeom/query

Requête de données géologiques.

**Request Body:**
```json
{
  "bbox": { ... },
  "include_bedrock": true,
  "include_surficial": true,
  "include_faults": false
}
```

---

### GET /api/geospatial/sigeom/bedrock

Retourne la géologie du socle rocheux.

**Query Parameters:**
- `bbox` (required): Bounding box

---

### GET /api/geospatial/sigeom/surficial

Retourne la géologie de surface (dépôts quaternaires).

---

## 💧 Module Hydrologie

### POST /api/geospatial/hydro/query

Requête de données hydrologiques.

**Request Body:**
```json
{
  "bbox": { ... },
  "include_rivers": true,
  "include_lakes": true,
  "include_wetlands": true,
  "include_watersheds": false,
  "buffer_distance": 100.0
}
```

---

### GET /api/geospatial/hydro/rivers

Retourne les cours d'eau.

**Query Parameters:**
- `bbox` (required)
- `buffer_m` (optional): Buffer en mètres (défaut: 100)

---

### GET /api/geospatial/hydro/lakes

Retourne les lacs et plans d'eau.

**Query Parameters:**
- `bbox` (required)
- `min_area_m2` (optional): Superficie minimale (défaut: 1000)

---

### GET /api/geospatial/hydro/wetlands

Retourne les milieux humides.

---

## ⛰ Module Géomorphologie

### POST /api/geospatial/geomorph/analyze

Analyse géomorphologique complète.

**Request Body:**
```json
{
  "bbox": { ... },
  "calculate_slope": true,
  "calculate_aspect": true,
  "calculate_curvature": true,
  "calculate_tpi": true,
  "calculate_twi": true
}
```

---

### GET /api/geospatial/geomorph/slope

Calcule la carte des pentes.

**Query Parameters:**
- `bbox` (required)
- `units` (optional): "degrees" ou "percent" (défaut: degrees)

---

### GET /api/geospatial/geomorph/aspect

Calcule la carte d'exposition.

---

### GET /api/geospatial/geomorph/features

Identifie les caractéristiques du terrain.

---

## 🌲 Module Forêt

### POST /api/geospatial/forest/query

Requête de données forestières MFFP.

**Request Body:**
```json
{
  "bbox": { ... },
  "include_species": true,
  "include_age": true,
  "include_density": true,
  "include_disturbances": false
}
```

---

### GET /api/geospatial/forest/stands

Retourne les peuplements forestiers.

---

### GET /api/geospatial/forest/species

Retourne la composition en espèces.

---

### GET /api/geospatial/forest/age

Retourne la distribution des classes d'âge.

---

## 🤖 Module IA

### POST /api/geospatial/ai/predict

Génère des prédictions IA complètes.

**Request Body:**
```json
{
  "bbox": { ... },
  "target_species": "deer",
  "season": "rut",
  "layers_to_include": ["elevation", "vegetation", "hydrology"],
  "weather_conditions": null
}
```

**Response:**
```json
{
  "request_id": "ai_20260203120000",
  "status": "architecture_ready",
  "corridors": null,
  "feeding_zones": null,
  "bedding_zones": null,
  "water_zones": null,
  "confidence_score": 0.0
}
```

---

### GET /api/geospatial/ai/corridors

Prédit les corridors de déplacement.

**Query Parameters:**
- `bbox` (required)
- `species` (required): moose, deer, bear, turkey
- `season` (required): pre_rut, rut, post_rut, early, late

---

### GET /api/geospatial/ai/feeding-zones

Prédit les zones d'alimentation.

---

### GET /api/geospatial/ai/bedding-zones

Prédit les zones de repos.

---

## 🎯 Module Potentiel de Chasse

### POST /api/geospatial/potential/calculate

Calcule le score de potentiel (0-100).

**Request Body:**
```json
{
  "bbox": { ... },
  "center_point": {
    "latitude": 45.55,
    "longitude": -73.65
  },
  "radius_m": 2000.0,
  "target_species": "deer",
  "season": "rut",
  "include_ai_predictions": true
}
```

**Response:**
```json
{
  "request_id": "potential_20260203120000",
  "status": "architecture_ready",
  "overall_score": 0.0,
  "level": "poor",
  "component_scores": {},
  "recommendations": [],
  "hotspots": [],
  "best_stand_locations": []
}
```

---

### GET /api/geospatial/potential/hotspots

Retourne les meilleurs points de chasse.

**Query Parameters:**
- `bbox` (required)
- `species` (required)
- `season` (required)
- `limit` (optional): Nombre max (défaut: 10)

---

### GET /api/geospatial/potential/stand-locations

Retourne les emplacements recommandés pour les affûts.

**Query Parameters:**
- `lat` (required): Latitude du centre
- `lon` (required): Longitude du centre
- `radius_m` (optional): Rayon de recherche (défaut: 1000)
- `species` (optional): Espèce cible (défaut: deer)

---

### GET /api/geospatial/potential/components

Liste les composantes du calcul de score.

**Response:**
```json
{
  "components": [
    {
      "name": "terrain_suitability",
      "weight": 0.20,
      "description": "Slope, aspect, and elevation analysis",
      "data_sources": ["lidar_quebec", "mne_quebec"]
    },
    {
      "name": "vegetation_quality",
      "weight": 0.20,
      "description": "Vegetation health and food availability",
      "data_sources": ["sentinel_2", "mffp_forest"]
    },
    // ... autres composantes
  ]
}
```

---

## 🔑 Codes d'Erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 400 | Requête invalide |
| 404 | Ressource non trouvée |
| 422 | Erreur de validation |
| 500 | Erreur serveur |
| 503 | Service indisponible |

---

## 📝 Notes

- Tous les endpoints retournent `status: "architecture_ready"` 
- L'implémentation réelle est en attente
- Les bounding boxes utilisent le système de coordonnées WGS84 (EPSG:4326)
- Les dates utilisent le format ISO 8601

---

*BIONIC™ Geospatial API - v1.0.0-alpha*
