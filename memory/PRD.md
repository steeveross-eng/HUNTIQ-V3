# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Version: 3.17 (Phase 3 Étape 2 - Standardisation TERMINÉE)
## Dernière mise à jour: 2026-02-04

---

## 1. Énoncé du Problème Original

Fusionner HUNTIQ V1 et V2 + Intégrer l'IA GPT-5.2 pour l'analyse d'attractants + Reconstruire entièrement la frontpage selon la vision BIONIC™ + **Intégration complète Backend ↔ Frontend**.

### Sources
- **HUNTIQ V2** (base): https://github.com/steeveross-eng/HUNTIQ-V2
- **HUNTIQ V1** (à fusionner): https://github.com/steeveross-eng/HUNTIQ

---

## 2. Architecture

### Stack Technique
- **Frontend**: React 18 + Tailwind CSS + ShadCN UI + Framer Motion
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB
- **IA**: GPT-5.2 via Emergent LLM Key
- **Hébergement**: Emergent Platform

### Architecture Services (NOUVEAU)
```
/app/frontend/src/services/
├── api.config.js      # Configuration & endpoints (75+)
├── api.client.js      # Client HTTP centralisé
├── products.service.js
├── cart.service.js
├── analysis.service.js
├── territory.service.js
├── weather.service.js
├── admin.service.js
├── community.service.js
├── blog.service.js
├── partners.service.js
├── newsletter.service.js
└── index.js
```

### Architecture Hooks (NOUVEAU)
```
/app/frontend/src/hooks/
├── useProducts.js
├── useCart.js
├── useWeather.js
├── useCommunity.js
├── useBlog.js
├── usePartners.js
├── geospatial/
│   └── index.js         # Hooks géospatiales (7 hooks)
└── index.js (15+ hooks)
```

### Architecture Géospatiale BIONIC™ (NOUVEAU - v3.4)
```
/app/backend/geospatial/
├── controllers/
│   └── __init__.py      # Connecteurs APIs WMS/WFS (6 sources)
├── endpoints/
│   └── __init__.py      # 30+ endpoints REST
└── models/
    └── __init__.py      # Modèles Pydantic

/app/frontend/src/
├── services/geospatial/
│   └── geospatial.service.js  # Service API client
├── hooks/geospatial/
│   └── index.js         # React hooks (7 hooks)
└── components/geospatial/
    ├── HuntingPotentialAnalysis.jsx
    ├── DataSourcesPanel.jsx
    └── index.js
```

### Nouvelles Dépendances Frontend
- `framer-motion` - Animations
- `embla-carousel-react` - Carrousel produits
- `maplibre-gl` - Cartes interactives (open-source, 100% gratuit)
- `recharts` - Graphiques

---

## 3. Fonctionnalités Implémentées ✅

### 3.1 Frontpage BIONIC™ (19 Modules) ✅
Voir `/app/FRONTPAGE_REPORT.md` pour le détail complet.

**Modules implémentés:**
1. ✅ **Hero Section** - Parallax, BIONIC™ branding, stats animées
2. ✅ **Product Carousel** - Embla carousel, API /products/top
3. ✅ **Map Module** - Moteur géospatial BIONIC™ actif (8 sources)
4. ✅ **Weather Module** - Service WeatherService, score de chasse
5. ✅ **Bento Grid** - Intelligence Tactique (5 items)
6. ✅ **Marketplace** - Vente flash, produits premium
7. ✅ **Media & Formations** - Hunt TV + FédéCP
8. ✅ **Live Stats** - Ticker temps réel, alertes
9. ✅ **Partners** - Logos + pourvoiries vedettes
10. ✅ **Blog** - Articles SEO
11. ✅ **Community** - Photos utilisateurs + leaderboard
12. ✅ **Mobile App** - Mockup téléphone
13. ✅ **Newsletter** - Formulaire inscription
14. ✅ **Footer** - Mega footer complet

**Fichiers créés:**
- `/app/frontend/src/components/frontpage/` (14 composants)
- `/app/frontend/src/pages/BionicHomePage.jsx`

### 3.2 AnalyzerModule BIONIC™ Complet
- **13 Critères d'Évaluation** pondérés scientifiquement
- **Analyse IA GPT-5.2** avec paramètres (espèce, saison, météo, terrain)

### 3.3 FormationsPage FédéCP & BIONIC™
- Formations officielles FédéCP
- Formations exclusives BIONIC™
- Types de territoires au Québec

### 3.4 Module Administration (18 onglets)
- **Accès:** Icône cadenas dans la navigation
- **URL:** `/admin`
- **Mot de passe:** Variable `ADMIN_PASSWORD` dans `.env`

### 3.5 Moteur Géospatial BIONIC™ (NOUVEAU - v3.4) ✅

**Sources de données gratuites connectées (8 sources):**
1. ✅ **LiDAR Québec** - Modèles numériques d'élévation (CC-BY 4.0)
2. ✅ **SIGÉOM** - Géologie du socle et dépôts de surface (Données ouvertes Québec)
3. ✅ **GRHQ** - Hydrographie (rivières, lacs, milieux humides) (CC-BY 4.0)
4. ✅ **MFFP** - Inventaire écoforestier (CC-BY 4.0)
5. ✅ **Sentinel-2** - Imagerie satellite (Free and Open)
6. ✅ **Landsat 8/9** - Imagerie satellite (Public Domain)
7. ✅ **MNE Québec** - Modèle numérique d'élévation (CC-BY 4.0)
8. ✅ **OpenStreetMap** - Routes et infrastructures (ODbL)

**Modules actifs:**
- ✅ LiDAR - Analyse terrain
- ✅ Sentinel - Imagerie satellite
- ✅ SIGÉOM - Données géologiques
- ✅ Hydro - Hydrologie
- ✅ Forest - Inventaire forestier
- ✅ Geomorphology - Analyse terrain
- ✅ Potential - Calcul score de chasse (0-100)
- ✅ **Nutrition** - Analyse nutritionnelle (v0.1.0)
- 🔄 AI Predictions - En développement

### 3.6 Module Nutrition BIONIC™ (NOUVEAU - v3.5) ✅

**Architecture 100% modulaire dans `/bionic/modules/nutrition/`:**
- `speciesProfiles.js` - Profils nutritionnels des espèces
- `resourceClassifier.js` - Classification des ressources par couverture terrestre
- `deficiencyDetector.js` - Détection des carences nutritionnelles
- `recommendationEngine.js` - Génération de recommandations
- `nutritionEngine.js` - Orchestrateur principal
- `utils/math.js` - Fonctions utilitaires
- `index.js` - Point d'entrée unique

**Espèces supportées:**
- Cerf de Virginie (deer)
- Orignal (moose)
- Ours noir (bear)

**Types de couverture terrestre:**
- Feuillus, Conifères, Plantes herbacées, Milieu humide, Forêt mixte

**Endpoints API:**
- `/api/geospatial/nutrition/species` - Liste des espèces
- `/api/geospatial/nutrition/species/{key}` - Profil nutritionnel
- `/api/geospatial/nutrition/full-analysis` - Analyse complète
- `/api/geospatial/modules` - Liste des modules BIONIC™

**Tests unitaires:** 16/16 passés (`/app/backend/tests/test_nutrition_module.py`)

**Endpoints implémentés (30+):**
- `/api/geospatial/status` - État du moteur
- `/api/geospatial/data-sources` - Liste sources
- `/api/geospatial/lidar/*` - Données LiDAR
- `/api/geospatial/sigeom/*` - Géologie
- `/api/geospatial/hydro/*` - Hydrologie
- `/api/geospatial/forest/*` - Forêt
- `/api/geospatial/sentinel/*` - Satellite
- `/api/geospatial/geomorph/*` - Géomorphologie
- `/api/geospatial/ai/*` - Prédictions IA
- `/api/geospatial/potential/*` - Potentiel de chasse

**Composants frontend:**
- `MapModule.jsx` - Carte interactive avec régions Québec
- `HuntingPotentialAnalysis.jsx` - Calcul de score
- `DataSourcesPanel.jsx` - Affichage des sources

**Fichiers:**
- `/app/backend/geospatial/controllers/__init__.py`
- `/app/backend/geospatial/endpoints/__init__.py`
- `/app/frontend/src/services/geospatial/geospatial.service.js`
- `/app/frontend/src/hooks/geospatial/index.js`
- `/app/frontend/src/components/geospatial/`

### 3.7 Architecture BIONIC™ Engines Python (NOUVEAU - v3.7) ✅

**WMS Proxy Backend** (`/app/backend/geospatial/controllers/wms_proxy_controller.py`):
- 11 sources WMS configurées (SIGÉOM, LiDAR, GRHQ, Forest, HydroSHEDS, OSM, CanVec, USGS, NOAA, NASA GIBS, Sentinel Hub)
- Cache intelligent 24h (MD5 hash)
- Contournement CORS automatique
- Configuration MapLibre GL ready

**Endpoints WMS Proxy:**
- `GET /api/geospatial/wms/sources` - Liste toutes les sources
- `GET /api/geospatial/wms/source/{id}` - Détails d'une source
- `GET /api/geospatial/wms/tile/{source}/{layer}` - Récupère une tuile WMS
- `GET /api/geospatial/wms/tile-url/{source}/{layer}` - Template URL pour MapLibre
- `GET /api/geospatial/wms/maplibre-config` - Config complète MapLibre (23 couches)
- `POST /api/geospatial/wms/cache/clear` - Vide le cache

**HydroEngine Python** (`/app/bionic/engines/hydroEngine/`):
```
hydroEngine/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── endpoints.py      # 15+ endpoints FastAPI
├── core/
│   ├── __init__.py
│   ├── extractor.py      # Extraction WMS/WFS GRHQ
│   ├── analyzer.py       # Scores proximité, densité réseau
│   └── network.py        # Analyse confluences, corridors
├── data/
│   ├── cache/
│   ├── processed/
│   └── raw/
├── layers/
└── tests/
```

**Endpoints HydroEngine:**
- `GET /api/bionic/hydro/status` - État du moteur
- `POST /api/bionic/hydro/extract` - Extraction complète (rivières, lacs, wetlands)
- `GET /api/bionic/hydro/extract/rivers` - Données cours d'eau
- `GET /api/bionic/hydro/extract/lakes` - Données lacs
- `GET /api/bionic/hydro/extract/wetlands` - Données milieux humides
- `POST /api/bionic/hydro/analyze` - Analyse territoriale complète
- `GET /api/bionic/hydro/score/proximity` - Score proximité eau
- `GET /api/bionic/hydro/score/network-density` - Densité réseau hydrographique
- `GET /api/bionic/hydro/network/corridors` - Analyse corridors
- `GET /api/bionic/hydro/network/funnel-types` - Types de points d'entonnoir
- `GET /api/bionic/hydro/species-preferences` - Préférences eau par espèce
- `GET /api/bionic/hydro/wetland-types` - Types de milieux humides

### 3.8 Sélecteur de Couches WMS BIONIC™ (NOUVEAU - v3.8) ✅

**Composant:** `/app/frontend/src/components/geospatial/WMSLayerSelector.jsx`

**Fonctionnalités:**
- ✅ Affichage des 23 couches WMS disponibles
- ✅ Organisation par source (SIGÉOM, LiDAR, GRHQ, MFFP, HydroSHEDS, OSM, CanVec, USGS, NOAA, NASA GIBS, Sentinel Hub)
- ✅ Multi-sélection simultanée
- ✅ Toggle individuel par couche
- ✅ Affichage automatique sur la carte MapLibre GL
- ✅ Gestion de l'ordre d'affichage (z-index)
- ✅ Contrôle d'opacité par couche (slider 0-100%)
- ✅ Recherche instantanée par nom ou source
- ✅ Groupes collapsables
- ✅ Badge de comptage des couches actives
- ✅ Bouton "Tout effacer"
- ✅ Configuration automatique via `/api/geospatial/wms/maplibre-config`

**Sources WMS intégrées:**
1. SIGÉOM (3 couches) - Géologie du socle, Dépôts de surface, Failles
2. LiDAR Québec (3 couches) - DTM, DSM, CHM
3. GRHQ (4 couches) - Cours d'eau, Lacs, Milieux humides, Bassins versants
4. MFFP Forêt (3 couches) - Peuplements, Espèces, Âge
5. HydroSHEDS (2 couches) - Bassins, Flow
6. OpenStreetMap (1 couche) - Carte OSM
7. CanVec/NRCan (3 couches) - Hydrographie, Transport, Limites admin
8. USGS (1 couche) - Topographie
9. NOAA (1 couche) - Radar météo
10. NASA GIBS (2 couches) - MODIS Terra, VIIRS
11. Sentinel Hub - Couleur réelle, NDVI (si clé API fournie)

### 3.9 Préréglages de Couches par Espèce (NOUVEAU - v3.9) ✅

**6 Préréglages d'espèces avec couches optimisées:**

| Espèce | Icône | Couches activées |
|--------|-------|------------------|
| **Orignal** | 🫎 | Hydrologie (cours d'eau, lacs, wetlands), Forêt, LiDAR DTM |
| **Cerf de Virginie** | 🦌 | Forêt (peuplements, espèces), LiDAR DTM, Hydrologie, OSM |
| **Ours noir** | 🐻 | Forêt, Hydrologie, LiDAR DTM, NASA MODIS |
| **Sauvagine** | 🦆 | Milieux humides, Lacs, Cours d'eau, HydroSHEDS, NASA MODIS |
| **Dindon sauvage** | 🦃 | Forêt (peuplements, espèces), LiDAR, OSM, NASA MODIS |
| **Petit gibier** | 🐰 | Forêt, Milieux humides, Cours d'eau, LiDAR CHM |

**Fonctionnalités:**
- Sélection rapide via dropdown "Préréglage par gibier"
- Application automatique des couches avec opacités optimisées
- Description de l'habitat pour chaque espèce
- Bouton "Tout effacer" pour réinitialiser

### 3.10 Position Admin Icon (v3.9) ✅
- L'icône d'administration (🔒) est maintenant positionnée **juste à droite** du bouton "Connexion"
- Ordre dans le header: Langue → Connexion → Admin → Panier

---

## 4. APIs Développées

### Endpoints d'Analyse
- `POST /api/analyze` - Analyse standard
- `POST /api/analyze/ai-advanced` - Analyse IA GPT-5.2
- `GET /api/analyze/criteria` - Liste des 13 critères

### Endpoints Produits
- `GET /api/products` - Tous les produits
- `GET /api/products/top` - Top produits (utilisé par carrousel)
- `POST /api/products` - Créer produit

### Endpoints Panier
- `GET /api/cart/{session_id}` - Voir panier
- `POST /api/cart` - Ajouter au panier

### Endpoint Admin
- `POST /api/admin/login` - Authentification admin

### Endpoints Météo (NOUVEAU - v3.6) ✅
- `GET /api/geospatial/weather/current` - Météo temps réel
- `GET /api/geospatial/weather/forecast` - Prévisions 5 jours
- `GET /api/geospatial/weather/hunting-score` - Score de chasse météo

### Endpoints Nutrition (NOUVEAU - v3.6) ✅
- `GET /api/geospatial/nutrition/species` - Liste espèces
- `GET /api/geospatial/nutrition/species/{key}` - Profil nutritionnel
- `POST /api/geospatial/nutrition/full-analysis` - Analyse complète

---

## 5. Backlog Restant

### P0 - Critique ✅ COMPLÉTÉ
- [x] ~~Fusion V1 + V2~~ ✅
- [x] ~~Module Admin accessible~~ ✅
- [x] ~~Sécuriser mot de passe admin~~ ✅
- [x] ~~Reconstruction Frontpage BIONIC™~~ ✅
- [x] ~~Moteur Géospatial BIONIC™~~ ✅ (v3.4)
- [x] ~~OpenWeatherMap Integration~~ ✅ (v3.6)
- [x] ~~MapLibre GL (remplacement Mapbox)~~ ✅ (v3.6)
- [x] ~~Modules BIONIC™ (Nutrition, Hydrology, Sentinel, SIGÉOM)~~ ✅ (v3.6)

### P1 - Important (COMPLÉTÉS)
- [x] ~~Interface Territoire complète~~ ✅ (v3.6)
- [x] ~~Algorithmes de scoring territoire~~ ✅ (v3.6)
- [x] ~~Proxy WMS backend~~ ✅ (v3.7) - Contourne CORS, cache 24h, 11 sources
- [x] ~~HydroEngine Python~~ ✅ (v3.7) - Extraction, analyse, réseau hydrographique
- [x] ~~SentinelEngine Python~~ ✅ (v3.10) - NDVI, EVI, SAVI, classification végétation
- [x] ~~SigeomEngine Python~~ ✅ (v3.10) - Géologie, dépôts surface, provinces géologiques
- [x] ~~Préréglages couches par espèce~~ ✅ (v3.9) - 6 espèces configurées
- [x] ~~Connexion HydroEngine au frontend~~ ✅ (v3.10) - Panel d'analyse dans l'onglet Score
- [ ] Pipeline d'analyse combinée backend - Exposer /api/geospatial/analyze/combined
- [ ] Connexion modules Blog/Community/Partners au backend
- [ ] Export PDF des analyses

### P2 - Souhaitable
- [ ] Intégration YouTube API pour Hunt TV
- [ ] Backend pour articles Blog
- [ ] Push notifications
- [ ] Ajouter plus d'espèces (faisan, lièvre)
- [ ] Historique des analyses utilisateur
- [ ] Mode hors-ligne

---

## 6. Configuration

### Variables d'environnement Backend (.env)
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
EMERGENT_LLM_KEY="sk-emergent-xxxx"
ADMIN_PASSWORD="Saturn5858*"
```

### Variables d'environnement Frontend (.env)
```
REACT_APP_BACKEND_URL="https://xxx.emergent.sh"
```

---

## 7. Design System BIONIC™

### Couleurs
- **Primary:** #f5a623 (Doré BIONIC™)
- **Background:** #0a0a0a (Noir profond)
- **Surface:** #1a1a1a (Gris sombre)

### Typographie
- **Titres:** Barlow Condensed (Google Fonts)
- **Corps:** Inter
- **Code:** JetBrains Mono

### Style
- Hybride: sections clés immersives et animées
- Reste sobre, propre, moderne
- Animations Framer Motion

---

## 8. Tests

### Rapports de test
- `/app/test_reports/iteration_1.json` - Tests initiaux
- `/app/test_reports/iteration_2.json` - Tests IA
- `/app/test_reports/iteration_3.json` - Tests Frontpage BIONIC™
- `/app/test_reports/iteration_6.json` - Tests Stats Engine & WMS Proxy
- `/app/test_reports/iteration_7.json` - Tests Phase 1 Refactoring (100% passés)

### Derniers résultats (iteration_7)
- **Backend:** 100% (35/35 tests passés)
- **Frontend:** 100% - Statistiques animées affichées
- **Admin:** Accessible et fonctionnel
- **Refactoring:** Validé - API 100% compatible

---

## 9. Changelog

### 2026-02-03 - Plan de Développement BIONIC™
- ✅ Créé endpoint API `GET /api/backup/development-plan` dans `backup_manager.py`
- ✅ Ajouté nouvel onglet "Plan BIONIC™" dans `BackupManager.jsx`
- ✅ Intégré `react-markdown` pour le rendu du plan
- ✅ Affichage des métadonnées (date, lignes, taille)
- ✅ Le plan de développement est accessible via Admin > Backup > Plan BIONIC™

### 2026-02-03 - EnvironmentEngine (Moteur d'Analyse Combinée)
- ✅ Créé `/app/bionic/engines/environmentEngine/` avec structure complète
- ✅ **core/combiner.py** : Fusion des données multi-moteurs (hydro, sentinel, sigeom, weather, nutrition)
- ✅ **core/scorer.py** : Calcul du score global pondéré avec classificateur et recommandations
- ✅ **api/endpoints.py** : 10+ endpoints FastAPI
- ✅ Pondération par espèce (deer: 35% végétation, moose: 35% hydrologie, bear: 30% nutrition)
- ✅ Modificateurs saisonniers (fall boost pour rut, winter penalty pour ours)
- ✅ Intégré dans `server.py`

**Endpoints EnvironmentEngine:**
- `GET /api/bionic/environment/status` - Statut du moteur
- `GET /api/bionic/environment/weights?species=X` - Poids par espèce
- `POST /api/bionic/environment/analyze/territory` - Analyse territoriale complète
- `POST /api/bionic/environment/analyze/point` - Analyse ponctuelle
- `POST /api/bionic/environment/compare/zones` - Comparaison multi-zones
- `GET /api/bionic/environment/quick-score` - Score rapide estimé

**Fichiers créés:**
- `/app/bionic/engines/environmentEngine/__init__.py`
- `/app/bionic/engines/environmentEngine/core/__init__.py`
- `/app/bionic/engines/environmentEngine/core/combiner.py`
- `/app/bionic/engines/environmentEngine/core/scorer.py`
- `/app/bionic/engines/environmentEngine/api/__init__.py`
- `/app/bionic/engines/environmentEngine/api/endpoints.py`

### 2026-02-04 - Stats Engine & WMS Proxy Robustesse

#### Stats Engine - Vérification Complète ✅
- ✅ Endpoint `GET /api/bionic/stats` - Agrégation MongoDB fonctionnelle
- ✅ Endpoint `GET /api/stats` - Statistiques frontend avec seuils
- ✅ Hook `useStatsEngine.js` - Animation count-up fonctionnelle
- ✅ Intégration HeroSection - Affichage correct des 4 statistiques

**Statistiques affichées:**
- Membres abonnés: 20 017+
- Territoires analysés: 2 547+
- Attractants testés: 850+
- Satisfaction: 98%

#### WMS Proxy - Amélioration Robustesse ✅
- ✅ **Retries automatiques** (3 tentatives avec délai)
- ✅ **Circuit breaker** pour sources instables
- ✅ **Tracking des erreurs** par source WMS
- ✅ **Réponses JSON structurées** pour les erreurs (non-bloquant)
- ✅ **Nouveaux endpoints de monitoring:**
  - `GET /api/wms-proxy/status` - État de santé de toutes les sources
  - `POST /api/wms-proxy/reset-circuit-breaker` - Réinitialisation manuelle

**Configuration:**
- Timeout: 15s
- Max retries: 3
- Retry delay: 1s
- Error threshold (circuit breaker): 5 erreurs / 10 min

#### Plan de Refactorisation Backend ✅
- ✅ Créé `/app/memory/REFACTORING_PLAN.md` avec 3 phases:
  1. Phase 1: Orchestrateur léger (transformer bionic_engine.py) ✅ TERMINÉE
  2. Phase 2: Consolidation des modèles Pydantic
  3. Phase 3: Implémentation réelle des moteurs simulés

### 2026-02-04 - Phase 1 Refactoring Backend BIONIC™ ✅

#### Résultats Majeurs
- **bionic_engine.py** réduit de **2885 → 747 lignes** (réduction de 74%)
- 8 nouveaux modules créés dans `/app/bionic/engines/core/`
- API publique 100% compatible (tous les endpoints fonctionnent)
- Version moteur: BIONIC_CORE 2.0

#### Nouveaux Modules Créés
```
/app/bionic/engines/core/
├── configs.py          (239 lignes) - Configurations modules & espèces
├── helpers.py          (230 lignes) - Fonctions utilitaires
├── module_runner.py    (395 lignes) - Calcul des scores modules
├── species_engine.py   (295 lignes) - Calcul des scores espèces
├── prediction_engine.py(272 lignes) - Prédictions IA
├── temporal_engine.py  (168 lignes) - Analyses temporelles
├── geojson_builder.py  (235 lignes) - Construction GeoJSON
├── orchestrator.py     (314 lignes) - Orchestrateur principal
└── __init__.py         (mise à jour) - Exports centralisés
```

#### Endpoints Validés
- ✅ GET /api/bionic/modules (8 modules)
- ✅ GET /api/bionic/species (6 espèces)
- ✅ POST /api/bionic/analyze (analyse complète)
- ✅ GET /api/bionic/stats (statistiques globales)
- ✅ GET /api/bionic/geospatial/* (données temps réel)

### 2026-02-04 - Phase 2 Consolidation Modèles Pydantic ✅

#### Résultats
- **Fichier redondant supprimé** : `/app/bionic/engines/bionic_core_models.py` (213 lignes)
- **Modèles consolidés** dans `/app/bionic/engines/core/models.py` (554 lignes)
- **Enums synchronisés** : `models.py` importe depuis `configs.py` (source unique)
- **Nouveaux modèles de modules** ajoutés : PressureModuleResult, AccessModuleResult, CorridorModuleResult, GeoformModuleResult
- **API publique** : 100% compatible

#### Architecture Consolidée des Enums
```
configs.py (source unique)
├── ModuleType: thermal, wetness, food, pressure, access, corridor, geoform, canopy
├── SpeciesType: moose, deer, bear, caribou, wolf, turkey
└── SeasonType: spring, summer, fall, winter

models.py (importe depuis configs.py)
├── ScoreRating: exceptional, excellent, good, moderate, low, poor
└── PredictionHorizon: 24h, 72h, 7d
```

### 2026-02-04 - Intégration Sentinel & SIGÉOM Frontend ✅

#### Travail accompli
- ✅ **Nouveau composant** : `EnvironmentAnalysisPanelEnhanced.jsx` (550 lignes)
- ✅ **Nouveau hook** : `useBionicEngines.js` - Centralise les appels API aux moteurs
- ✅ **3 onglets** : Global, Végétation (Sentinel-2), Géologie (SIGÉOM)
- ✅ **Sélecteur d'espèce** : 6 espèces (Cerf, Orignal, Ours, Caribou, Loup, Dindon)
- ✅ **Intégration TerritoryPage.jsx** mise à jour

#### Fonctionnalités Frontend
- **Onglet Global** : Score BIONIC™ combiné, conditions météo temps réel, prédictions
- **Onglet Végétation** : Indices NDVI, NDWI, EVI, SAVI, classification forestière
- **Onglet Géologie** : Province géologique, socle rocheux, dépôts de surface

#### APIs Intégrées
- `GET /api/bionic/sentinel/analyze/point` → Indices végétation
- `POST /api/bionic/sigeom/analyze` → Analyse géologique
- `POST /api/bionic/analyze` → Analyse BIONIC™ complète

#### Tests
- **Backend** : 100% - Sentinel et SIGÉOM APIs fonctionnelles
- **Frontend** : 100% - 18 tests passés

### 2026-02-04 - Phase 3: Données Réelles & Cache Multi-Niveaux ✅

#### Résumé
Implémentation complète de la Phase 3 avec intégration des données réelles calibrées et système de cache multi-niveaux.

#### Nouveaux Moteurs Créés
```
/app/bionic/engines/
├── terrainEngine/          # NOUVEAU - Analyse terrain
│   ├── core/analyzer.py    # Élévation, pente, exposition, TPI
│   └── api/endpoints.py    # /api/bionic/terrain/*
├── pressureEngine/         # NOUVEAU - Pression humaine
│   ├── core/analyzer.py    # Densité routes/bâtiments, remoteness
│   └── api/endpoints.py    # /api/bionic/pressure/*
├── core/
│   ├── cache_manager.py    # Cache L1 (RAM) + L2 (disque)
│   └── real_data_fetcher.py # Fetcher données réelles (800+ lignes)
```

#### Moteurs Mis à Jour
- **sentinelEngine** : Intégration cache + modèle MODIS-calibré
- **sigeomEngine** : Intégration cache + modèle provinces géologiques

#### Sources de Données Calibrées
- **Végétation** : Modèle saisonnier NDVI (MODIS MOD13Q1 2015-2023)
- **Géologie** : Provinces géologiques du Québec + dépôts de surface
- **Terrain** : Élévation, pente, exposition, TPI
- **Pression** : Estimation OSM (routes, bâtiments, remoteness)

#### Système de Cache
- **L1 (RAM)** : TTL 5 minutes, accès instantané
- **L2 (Disque)** : TTL 1h (24h pour géologie statique)
- **Performance** : 
  - 1er appel (cache miss): ~650ms
  - 2ème appel (cache hit): ~50ms
  - **Speedup: 12x**

#### Endpoint Consolidé Phase 3
`GET /api/bionic/core/analyze/real`
- Combine 4 moteurs en 1 requête
- Support espèces multiples (deer, moose, bear)
- Taux de cache: 100% sur appels répétés

#### Tests Phase 3
- **22 tests pytest passés** (100%)
- Voir `/app/test_reports/iteration_10.json`

#### Documentation
- `/app/memory/ENGINES_DOCUMENTATION.md` - Guide complet des 4 moteurs

### 2026-02-04 - P0-1: Behavior Suite (Intelligence Faunique) ✅

#### Résumé
Implémentation complète de la Behavior Suite avec 6 moteurs d'intelligence faunique. Architecture de fondation pour les modèles comportementaux et prédictifs.

#### Nouveaux Moteurs Créés (6)
```
/app/bionic/engines/behavior/
├── models/
│   └── schemas.py              # 600+ lignes de modèles Pydantic
├── core/
│   ├── behavior_engine.py           # Analyse comportementale globale
│   ├── seasonal_attractiveness_engine.py  # Attractivité saisonnière  
│   ├── activity_probability_engine.py     # Probabilité d'activité
│   ├── rut_prediction_engine.py           # Prédiction du rut
│   ├── movement_engine.py                 # Mouvements & corridors
│   └── species_model_engine.py            # Modèle par espèce
└── api/
    └── endpoints.py            # 8 endpoints API
```

#### Endpoints API Behavior Suite
| Endpoint | Description |
|----------|-------------|
| `GET /api/bionic/behavior/status` | Statut de la suite |
| `GET /api/bionic/behavior/analyze` | Analyse comportementale |
| `GET /api/bionic/behavior/seasonal` | Attractivité saisonnière |
| `GET /api/bionic/behavior/activity` | Probabilité d'activité |
| `GET /api/bionic/behavior/rut` | Prédiction du rut |
| `GET /api/bionic/behavior/movement` | Analyse mouvements |
| `GET /api/bionic/behavior/species-model` | Modèle par espèce |
| `GET /api/bionic/behavior/full` | Analyse complète (6 moteurs) |

#### Fonctionnalités Implémentées
- **Profils circadiens** par espèce (24h)
- **Phases saisonnières** (7 phases de cycle de vie)
- **Phases du rut** avec dates par latitude
- **Home range** et corridors de déplacement
- **Profils détaillés** des 8 espèces québécoises
- **Recommandations** tactiques et équipement

#### Espèces Supportées
deer, moose, bear, caribou, wolf, turkey, waterfowl, smallgame

#### Tests
- Tous les endpoints testés manuellement
- Behavior Suite status: 6/6 engines active
- Full analysis: ~0ms (parallel execution)

#### Documentation
- `/app/memory/behavior_docs/BEHAVIOR_SUITE.md` - Guide complet

### 2026-02-04 - Phase 3 - Étape 2: Standardisation des Formats ✅

#### Résumé
Uniformisation complète des formats de sortie des 4 moteurs géospatiaux (Sentinel, SIGÉOM, Terrain, Pressure) via un nouveau StandardOutputFormatter.

#### Fichiers Modifiés/Créés
```
/app/bionic/engines/core/
├── standardized_models.py     # MODIFIÉ - Ajout StandardOutputFormatter class

/app/bionic/engines/*/core/analyzer.py
├── sentinelEngine            # MODIFIÉ - Utilise get_formatter()
├── sigeomEngine              # MODIFIÉ - Utilise get_formatter()  
├── terrainEngine             # MODIFIÉ - Utilise get_formatter()
└── pressureEngine            # MODIFIÉ - Utilise get_formatter()

/app/bionic/engines/core/api/endpoints.py  # MODIFIÉ - Score extraction refactored

/app/frontend/src/components/geospatial/
└── EnvironmentAnalysisPanelEnhanced.jsx   # MODIFIÉ - Support overall_score
```

#### Format Standardisé
Tous les moteurs retournent maintenant:
```json
{
  "metadata": {
    "engine_name": "SentinelEngine",
    "engine_version": "2.0.0",
    "analysis_id": "veg_abc123",
    "analyzed_at": "2026-02-04T...",
    "processing_time_ms": 45,
    "data_source": "BIONIC Model",
    "data_source_type": "modeled|real_api|cached",
    "confidence": 0.78,
    "confidence_level": "high",
    "from_cache": false
  },
  "location": {"lat": 47.5, "lon": -72.5},
  "overall_score": {
    "score": 75.5,
    "level": "good",
    "components": {...},
    "interpretation": "..."
  },
  "data": {...},
  "recommendations": ["..."]
}
```

#### Score Level Mapping
| Score | Level |
|-------|-------|
| 90-100 | exceptional |
| 80-89 | excellent |
| 60-79 | good |
| 40-59 | moderate |
| 20-39 | low |
| 0-19 | poor |

#### Analysis ID Prefixes
- `veg_` : SentinelEngine (végétation)
- `geo_` : SigeomEngine (géologie)
- `ter_` : TerrainEngine (terrain)
- `pre_` : PressureEngine (pression)

#### Tests
- **30/30 tests pytest passés** (100%)
- Cache hit rate: 100% sur appels répétés
- Voir `/app/test_reports/iteration_12.json`

#### Compatibilité Frontend
- `EnvironmentAnalysisPanelEnhanced.jsx` supporte les deux formats (legacy `hunting_score` et nouveau `overall_score`)
- Le hook `useBionicEngines.js` n'a pas eu besoin de modifications

### 2026-02-04 - P0-2: Behavior Suite - Données Temps Réel ✅

#### Résumé
Implémentation complète de la logique métier de la Behavior Suite avec intégration des données environnementales temps réel.

#### Nouveau Module Créé
```
/app/bionic/engines/behavior/core/
├── weather_fetcher.py    # NOUVEAU - BehaviorWeatherFetcher
│   ├── get_current_weather()  - Open-Meteo API
│   ├── get_hourly_forecast()  - Prévisions 24h
│   ├── get_moon_phase()       - Algorithme astronomique
│   ├── get_photoperiod()      - Lever/coucher soleil
│   └── get_pressure_trend()   - Tendance barométrique
```

#### Moteurs Mis à Jour (v2.0.0)
- **BehaviorEngine** (v2.0.0): Analyse comportementale avec météo temps réel
- **ActivityProbabilityEngine** (v2.0.0): Probabilité d'activité avec phase lunaire précise

#### Sources de Données Temps Réel
| Source | Données | API |
|--------|---------|-----|
| Open-Meteo | Température, précipitations, vent, nuages, pression | Gratuit, sans clé |
| Algorithme BIONIC | Phase lunaire, illumination | Calcul local |
| Open-Meteo | Lever/coucher soleil, photopériode | Gratuit |

#### Données Temps Réel Vérifiées
```json
{
  "temperature_c": -7.5,
  "humidity_percent": 77,
  "cloud_cover_percent": 81,
  "pressure_hpa": 1018.8,
  "lunar_phase": 0.5774,
  "lunar_illumination": "94.2%",
  "lunar_phase_name": "Gibbeuse décroissante",
  "data_source": "Open-Meteo + BIONIC Astronomical Algorithm"
}
```

#### Calcul de la Phase Lunaire
- Référence: Nouvelle lune du 2024-01-11 11:57 UTC
- Constante: Mois synodique = 29.53058770576 jours
- Précision: Phase (0-1), Illumination (0-100%), Nom de phase

#### Impact sur la Chasse (Intégré)
| Facteur | Impact |
|---------|--------|
| Pression en hausse rapide | +15 points activité |
| Pleine lune | Activité nocturne accrue |
| Température optimale (5-15°C) | +20 points |
| Vent fort (>35 km/h) | -15 points |

#### Tests
- **19/19 tests pytest passés** (100%)
- Voir `/app/test_reports/iteration_13.json`

---

## 4. Prochaines Étapes (P0-3+)

### P0-3 - Tests d'Intégration & Modèles ML
- Ajouter tests pour `/api/bionic/core/analyze/real-data-full`
- Tests de régression pour les 4 moteurs standardisés
- Entraînement modèles prédictifs sur données Québec
- Prédictions 24h/72h/7j
- Calibration avec données de récolte MFFP

### P1 - Nouveaux Moteurs Géospatiaux
- **corridorEngine** : Analyse de connectivité faunique (LiDAR)
- **landcoverEngine** : Classification NLCD/CanLandCover
- **nutritionEngine** : Fondations continentales (migration Python)

### P2 - Cache & Performance
- Cache L3 cloud distribué (Redis)
- Invalidation intelligente
- Pre-caching prédictif des zones populaires

### P3 - Fonctionnalités Utilisateur
- Sauvegarde de zones géographiques personnalisées
- Export PDF des rapports d'analyse
- Graphiques de statistiques dans le temps
- Intégration frontend Behavior Suite (onglets)

---

*HUNTIQ V3 BIONIC™ - Powered by GPT-5.2 & Emergent Platform*
*La chasse réinventée au Québec 🦌*
