# HUNTIQ V3 - BIONIC™ Geospatial Engine

## 🌍 Vue d'ensemble

Le moteur géospatial BIONIC™ est une architecture modulaire conçue pour analyser des données
géospatiales gratuites et ouvertes afin de calculer le potentiel de chasse d'un territoire.

**Version:** 1.0.0-alpha (Architecture préparée)
**Status:** Préparation architecturale complète - Implémentation en attente

---

## 📋 Table des Matières

1. [Architecture](#architecture)
2. [Sources de Données](#sources-de-données)
3. [Modules](#modules)
4. [Flux de Données](#flux-de-données)
5. [Score de Potentiel](#score-de-potentiel)
6. [API Endpoints](#api-endpoints)
7. [Frontend Integration](#frontend-integration)
8. [Prochaines Étapes](#prochaines-étapes)

---

## 🏗 Architecture

### Structure Backend
```
/app/backend/geospatial/
├── endpoints/          # API FastAPI routes
│   └── __init__.py     # 35+ endpoints préparés
├── models/             # Pydantic data models
│   └── __init__.py     # 50+ modèles définis
├── controllers/        # Business logic (à implémenter)
├── processors/         # Data processing (à implémenter)
└── pipelines/          # ETL pipelines (à implémenter)
```

### Structure Frontend
```
/app/frontend/src/
├── modules/geospatial/
│   ├── lidar/          # LiDAR Quebec components
│   ├── sentinel/       # Sentinel-2 components
│   ├── landsat/        # Landsat components
│   ├── sigeom/         # Geology components
│   ├── hydro/          # Hydrology components
│   ├── geology/        # Geology analysis
│   ├── geomorphology/  # Terrain analysis
│   ├── forest/         # Forest inventory
│   ├── ai/             # AI predictions
│   └── potential/      # Hunting potential
├── services/geospatial/
│   ├── geospatial.service.ts  # API service
│   └── index.ts
├── hooks/geospatial/
│   └── index.ts        # 9 hooks React
├── types/geospatial/
│   └── index.ts        # TypeScript definitions
└── utils/geospatial/   # Utility functions
```

### Data & AI
```
/app/data/geospatial/
├── cache/              # Cached API responses
└── tiles/              # Map tile cache

/app/ai/geospatial/
├── models/             # ML model weights
└── pipelines/          # AI processing pipelines
```

---

## 📊 Sources de Données

Toutes les sources sont **100% gratuites et ouvertes**.

### 1. LiDAR Québec
- **URL:** https://www.donneesquebec.ca/
- **Licence:** CC-BY 4.0
- **Produits:** DTM, DSM, CHM
- **Résolution:** 1m
- **Couverture:** Zones urbaines et périurbaines

### 2. SIGÉOM (Géologie)
- **URL:** https://sigeom.mines.gouv.qc.ca/
- **Licence:** Données ouvertes Québec
- **Produits:** Géologie du socle, dépôts de surface, failles
- **Couverture:** Tout le Québec

### 3. Sentinel-2 (ESA)
- **URL:** https://scihub.copernicus.eu/
- **Licence:** Free and Open
- **Produits:** NDVI, EVI, SAVI, NDWI
- **Résolution:** 10-60m
- **Couverture:** Globale

### 4. Landsat 8/9 (USGS)
- **URL:** https://earthexplorer.usgs.gov/
- **Licence:** Public Domain
- **Produits:** Multispectral, thermique
- **Résolution:** 30m
- **Couverture:** Globale

### 5. Hydrographie Québec
- **URL:** https://www.donneesquebec.ca/
- **Licence:** CC-BY 4.0
- **Produits:** Rivières, lacs, milieux humides
- **Échelle:** 1:20000

### 6. MNE Québec
- **URL:** https://www.donneesquebec.ca/
- **Licence:** CC-BY 4.0
- **Produits:** Modèles numériques d'élévation
- **Résolution:** 1-10m

### 7. OpenStreetMap
- **URL:** https://www.openstreetmap.org/
- **Licence:** ODbL
- **Produits:** Routes, bâtiments, POI
- **Couverture:** Globale

### 8. MFFP Forêt
- **URL:** https://www.donneesquebec.ca/
- **Licence:** CC-BY 4.0
- **Produits:** Peuplements, espèces, âge, densité
- **Échelle:** 1:20000

---

## 🧩 Modules

### Module LiDAR
Analyse des données LiDAR pour extraction de:
- Modèle numérique de terrain (DTM)
- Modèle numérique de surface (DSM)
- Modèle de hauteur de canopée (CHM)
- Statistiques d'élévation

### Module Sentinel-2
Calcul des indices de végétation:
- NDVI (santé végétale)
- EVI (végétation amélioré)
- SAVI (ajusté au sol)
- NDWI (humidité)

### Module Landsat
Analyse multitemporelle:
- Changements de végétation
- Données thermiques
- Historique saisonnier

### Module SIGÉOM
Analyse géologique:
- Types de roches
- Perméabilité des sols
- Classes de drainage
- Impact sur la faune

### Module Hydrologie
Analyse des eaux:
- Proximité des cours d'eau
- Taille des plans d'eau
- Types de milieux humides
- Bassins versants

### Module Géomorphologie
Analyse du terrain:
- Pente (degrés/pourcentage)
- Exposition (aspect)
- Courbure
- TPI (Position topographique)
- TWI (Humidité topographique)
- Identification des crêtes/vallées

### Module Forêt
Analyse forestière:
- Types de peuplements
- Composition en espèces
- Classes d'âge
- Densité de couvert

### Module IA
Prédictions intelligentes:
- Corridors de déplacement
- Zones d'alimentation
- Aires de repos
- Zones thermiques

### Module Potentiel
Calcul du score final:
- Score 0-100
- Composantes pondérées
- Recommandations
- Hotspots identifiés

---

## 🔄 Flux de Données

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCES DE DONNÉES                           │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────┤
│  LiDAR   │ Sentinel │ Landsat  │  SIGÉOM  │  Hydro   │  MFFP   │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE D'EXTRACTION                          │
│  • API Copernicus  • API USGS  • WMS/WFS Québec  • OSM API     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE DE TRAITEMENT                         │
│  • Rasterio  • GeoPandas  • NumPy  • Rasterio  • GDAL          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE D'ANALYSE                             │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────┤
│ Terrain  │ Végétat. │ Hydro    │ Géologie │  Forêt   │   IA    │
│ Analysis │ Indices  │ Proxim.  │ Factors  │ Struct.  │ Predict │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬────┘
     │          │          │          │          │          │
     └──────────┴──────────┴────┬─────┴──────────┴──────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                SCORE DE POTENTIEL (0-100)                       │
│                                                                 │
│  Score = Σ (Composante_i × Poids_i)                            │
│                                                                 │
│  Composantes:                                                   │
│  • Terrain (20%)  • Végétation (20%)  • Eau (15%)              │
│  • Forêt (15%)    • Géologie (10%)    • IA (10%)               │
│  • Historique (10%)                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 Score de Potentiel

### Formule de Calcul
```
Score = (terrain × 0.20) + (vegetation × 0.20) + (water × 0.15) +
        (forest × 0.15) + (geology × 0.10) + (ai × 0.10) +
        (historical × 0.10)
```

### Niveaux
| Score | Niveau | Description |
|-------|--------|-------------|
| 80-100 | Excellent | Conditions optimales |
| 60-79 | Bon | Bonnes conditions |
| 40-59 | Moyen | Conditions acceptables |
| 20-39 | Faible | Conditions limitées |
| 0-19 | Pauvre | Conditions défavorables |

### Composantes Détaillées

#### 1. Terrain (20%)
- Pente: 5-15° optimal
- Exposition: Sud/Sud-Ouest favorable
- Élévation relative
- TPI: Fond de vallée ou mi-pente

#### 2. Végétation (20%)
- NDVI: > 0.4 favorable
- Type de couvert
- Santé de la végétation
- Disponibilité alimentaire

#### 3. Eau (15%)
- Distance < 500m: favorable
- Type (lac, rivière, marais)
- Accessibilité

#### 4. Forêt (15%)
- Mixte: optimal pour cervidés
- Âge: mature > jeune
- Densité: semi-ouverte favorable
- Espèces: présence de feuillus

#### 5. Géologie (10%)
- Drainage: bon à moyen
- Perméabilité: moyenne
- Minéraux: présence de sel

#### 6. IA (10%)
- Probabilité de corridor
- Zone d'alimentation prédite
- Zone de repos prédite

#### 7. Historique (10%)
- Observations passées
- Récoltes documentées
- Données utilisateurs

---

## 🔌 API Endpoints

### Status & Configuration
- `GET /api/geospatial/status`
- `GET /api/geospatial/data-sources`

### LiDAR
- `POST /api/geospatial/lidar/query`
- `GET /api/geospatial/lidar/coverage`
- `GET /api/geospatial/lidar/tiles`

### Sentinel-2
- `POST /api/geospatial/sentinel/query`
- `GET /api/geospatial/sentinel/scenes`
- `GET /api/geospatial/sentinel/indices/{scene_id}`

### Landsat
- `POST /api/geospatial/landsat/query`
- `GET /api/geospatial/landsat/scenes`

### SIGÉOM
- `POST /api/geospatial/sigeom/query`
- `GET /api/geospatial/sigeom/bedrock`
- `GET /api/geospatial/sigeom/surficial`

### Hydrologie
- `POST /api/geospatial/hydro/query`
- `GET /api/geospatial/hydro/rivers`
- `GET /api/geospatial/hydro/lakes`
- `GET /api/geospatial/hydro/wetlands`

### Géomorphologie
- `POST /api/geospatial/geomorph/analyze`
- `GET /api/geospatial/geomorph/slope`
- `GET /api/geospatial/geomorph/aspect`
- `GET /api/geospatial/geomorph/features`

### Forêt
- `POST /api/geospatial/forest/query`
- `GET /api/geospatial/forest/stands`
- `GET /api/geospatial/forest/species`
- `GET /api/geospatial/forest/age`

### IA
- `POST /api/geospatial/ai/predict`
- `GET /api/geospatial/ai/corridors`
- `GET /api/geospatial/ai/feeding-zones`
- `GET /api/geospatial/ai/bedding-zones`

### Potentiel
- `POST /api/geospatial/potential/calculate`
- `GET /api/geospatial/potential/hotspots`
- `GET /api/geospatial/potential/stand-locations`
- `GET /api/geospatial/potential/components`

**Total: 35+ endpoints préparés**

---

## 🖥 Frontend Integration

### Services
```typescript
import { GeospatialService } from '@/services/geospatial';

// Status
const status = await GeospatialService.getStatus();

// LiDAR
const lidar = await GeospatialService.lidar.query({ bbox });

// Sentinel
const scenes = await GeospatialService.sentinel.listScenes(bbox, start, end);

// Hunting Potential
const hotspots = await GeospatialService.potential.getHotspots(bbox, 'deer', 'rut');
```

### Hooks
```typescript
import {
  useGeospatialStatus,
  useLidar,
  useSentinel,
  useHydrology,
  useHuntingPotential,
} from '@/hooks/geospatial';

// In component
const { status, loading } = useGeospatialStatus();
const { hotspots, calculate } = useHuntingPotential();
```

---

## 🚀 Prochaines Étapes

### Phase 1: Infrastructure (À faire)
1. [ ] Installer dépendances Python (rasterio, geopandas, gdal)
2. [ ] Configurer cache de tuiles
3. [ ] Implémenter connecteurs API sources

### Phase 2: Modules de Base (À faire)
1. [ ] Implémenter extraction LiDAR
2. [ ] Implémenter calcul indices Sentinel
3. [ ] Implémenter requêtes SIGÉOM
4. [ ] Implémenter analyse hydrologique

### Phase 3: Analyse Avancée (À faire)
1. [ ] Implémenter analyse géomorphologique
2. [ ] Implémenter analyse forestière
3. [ ] Implémenter calcul de score

### Phase 4: IA (À faire)
1. [ ] Entraîner modèle de corridors
2. [ ] Implémenter prédictions zones
3. [ ] Intégrer GPT-5.2 pour recommandations

### Phase 5: Frontend (À faire)
1. [ ] Créer composants de visualisation
2. [ ] Intégrer avec Mapbox
3. [ ] Créer dashboard de potentiel

---

*BIONIC™ Geospatial Engine - Architecture v1.0.0-alpha*
*100% Gratuit • 100% Modulaire • 100% Évolutif*
