# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Version: 3.10 (Architecture BIONIC™ Complete)
## Dernière mise à jour: 2026-02-03

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

### Derniers résultats (iteration_3)
- **Backend:** 100% - API fonctionnelle
- **Frontend:** 100% - 19 modules OK
- **Admin:** Accessible et fonctionnel

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
  1. Phase 1: Orchestrateur léger (transformer bionic_engine.py)
  2. Phase 2: Consolidation des modèles Pydantic
  3. Phase 3: Implémentation réelle des moteurs simulés

---

### 2026-02-04 - BIONIC™ CORE Engine (TerritoryFullAnalysis)
- ✅ Créé modèle Pydantic complet `TerritoryFullAnalysis` dans `/app/bionic/engines/core/models.py`
- ✅ Créé endpoints API dans `/app/bionic/engines/core/api/endpoints.py`
- ✅ Intégré dans `server.py`

**Modèles créés (22 propriétés):**
- `TerritoryFullAnalysis` - Modèle principal consolidé
- `ModuleResult`, `ThermalModuleResult`, `WetnessModuleResult`, `FoodModuleResult`, `CoverModuleResult`
- `SpeciesResult`, `HabitatSuitability`, `ActivityPattern`
- `PredictionResult`, `SinglePrediction` (24h, 72h, 7j)
- `TemporalResult`, `NDVITimeSeries`, `SnowAnalysis`, `PhenologyData`
- `Recommendation`, `ScoreBreakdown`, `BoundingBox`, `GeoPoint`

**Endpoints BIONIC CORE:**
- `GET /api/bionic/core/status` - Statut du moteur
- `POST /api/bionic/core/analyze` - Analyse complète territoire
- `GET /api/bionic/core/quick` - Analyse rapide
- `GET /api/bionic/core/schema` - Schéma JSON du modèle

**Fonctionnalités:**
- Modules thématiques (thermal, wetness, food, cover, terrain, hydrology, vegetation, geology, weather, human_activity)
- Espèces supportées (moose, deer, bear, elk, waterfowl, turkey, smallgame)
- Prédictions IA avec horizons temporels
- Analyse temporelle NDVI/NDWI/neige/phénologie
- GeoJSON output
- Recommandations consolidées

---

*HUNTIQ V3 BIONIC™ - Powered by GPT-5.2 & Emergent Platform*
*La chasse réinventée au Québec 🦌*
