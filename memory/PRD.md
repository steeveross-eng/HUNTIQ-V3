# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Version: 3.4 (Moteur Géospatial BIONIC™)
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
- `mapbox-gl` / `react-map-gl` - Cartes interactives (à configurer)
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
- 🔄 AI Predictions - En développement

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

---

## 5. Backlog Restant

### P0 - Critique
- [x] ~~Fusion V1 + V2~~ ✅
- [x] ~~Module Admin accessible~~ ✅
- [x] ~~Sécuriser mot de passe admin~~ ✅
- [x] ~~Reconstruction Frontpage BIONIC™~~ ✅

### P1 - Important
- [ ] **Mapbox Integration** - Activer carte interactive avec clé API
- [ ] **OpenWeatherMap Integration** - Données météo réelles
- [ ] Optimiser temps de réponse IA (caching)
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

*HUNTIQ V3 BIONIC™ - Powered by GPT-5.2 & Emergent Platform*
*La chasse réinventée au Québec 🦌*
