# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Dernière mise à jour: Décembre 2025
## Version: 3.2 (Architecture Modulaire)

---

## 1. Énoncé du Problème Original

Fusionner HUNTIQ V1 et V2 + Intégrer l'IA GPT-5.2 pour l'analyse d'attractants.
Refactorisation majeure vers une architecture modulaire stricte ("PLAN MAÎTRE BIONIC").

### Sources
- **HUNTIQ V2** (base): https://github.com/steeveross-eng/HUNTIQ-V2
- **HUNTIQ V1** (à fusionner): https://github.com/steeveross-eng/HUNTIQ

---

## 2. Architecture

### Stack Technique
- **Frontend**: React 18 + Tailwind CSS + ShadCN UI
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB
- **IA**: GPT-5.2 via Emergent LLM Key
- **Hébergement**: Emergent Platform
- **Architecture**: Modulaire v1 (Phase 2 complétée)

### Structure Modulaire Backend
```
/app/backend/modules/
├── nutrition_engine/v1/       ✅ Complété
├── scoring_engine/v1/         ✅ Complété
├── ai_engine/v1/              ✅ Complété
├── weather_engine/v1/         ✅ Complété
├── geospatial_engine/v1/      ✅ Complété
├── wms_engine/v1/             ✅ Complété
├── strategy_engine/v1/        ✅ Complété
├── routers.py                 ✅ Point d'entrée central
└── (autres moteurs à venir)
```

---

## 3. Fonctionnalités Implémentées ✅

### 3.1 Phase 1: Infrastructure Modulaire ✅
- Structure des répertoires créée pour 26 modules backend
- Structure des répertoires créée pour 20 modules frontend
- Fichiers de configuration (settings.py, manifest.json)
- Documentation (README.md)

### 3.2 Phase 2: Moteurs Core Backend ✅ (Décembre 2025)

#### 7 Moteurs CORE Extraits et Opérationnels:

1. **nutrition_engine** (`/api/v1/nutrition`)
   - Base de données de 29 ingrédients
   - Analyse nutritionnelle des attractants
   - Recherche et filtrage par type/catégorie

2. **scoring_engine** (`/api/v1/scoring`)
   - 13 critères pondérés scientifiquement
   - Calcul de score normalisé (0-10)
   - Système de pastilles (vert/jaune/rouge)

3. **ai_engine** (`/api/v1/ai`)
   - Intégration GPT-5.2 via Emergent
   - Analyse de produits avec contexte de chasse
   - Comparaison avec produits BIONIC™
   - Références scientifiques

4. **weather_engine** (`/api/v1/weather`)
   - Calcul de score de chasse par météo
   - Prédiction d'activité du gibier
   - Phases lunaires
   - Recommandations de timing

5. **geospatial_engine** (`/api/v1/geospatial`)
   - 17 régions du Québec
   - Calcul de distances (Haversine)
   - Analyse de terrain
   - Recherche de zones de chasse

6. **wms_engine** (`/api/v1/wms`)
   - 10 couches WMS pré-configurées
   - Sources gouvernementales du Québec
   - Génération d'URLs WMS GetMap
   - Recommandations par cas d'usage

7. **strategy_engine** (`/api/v1/strategy`)
   - Génération de stratégies complètes
   - Recommandations de placement
   - Stratégies d'attractants
   - Conseils d'équipement

### 3.3 Fonctionnalités Legacy (Monolithe)
- AnalyzerModule BIONIC™ (13 critères)
- Analyse IA GPT-5.2 avancée
- Formations FédéCP & BIONIC™
- Système de produits hybride
- Marketplace
- Gestion de territoire

---

## 4. APIs Développées

### Nouveaux Endpoints Modulaires (Phase 2)
```
GET  /api/modules/status              # Statut de tous les modules

# Nutrition Engine
GET  /api/v1/nutrition/               # Info du module
GET  /api/v1/nutrition/ingredients    # Liste des ingrédients
POST /api/v1/nutrition/analyze        # Analyse d'ingrédients
POST /api/v1/nutrition/score          # Score nutritionnel

# Scoring Engine
GET  /api/v1/scoring/                 # Info du module
GET  /api/v1/scoring/criteria         # 13 critères
POST /api/v1/scoring/calculate        # Calcul de score
POST /api/v1/scoring/quick-score      # Score rapide

# AI Engine
GET  /api/v1/ai/                      # Info du module
POST /api/v1/ai/analyze               # Analyse IA
POST /api/v1/ai/analyze/advanced      # Analyse contextuelle
GET  /api/v1/ai/references            # Références scientifiques

# Weather Engine
GET  /api/v1/weather/                 # Info du module
POST /api/v1/weather/analyze          # Analyse météo
GET  /api/v1/weather/score            # Score rapide
GET  /api/v1/weather/moon             # Phase lunaire

# Geospatial Engine
GET  /api/v1/geospatial/              # Info du module
POST /api/v1/geospatial/distance      # Calcul de distance
POST /api/v1/geospatial/terrain       # Analyse terrain
GET  /api/v1/geospatial/regions       # Régions du Québec

# WMS Engine
GET  /api/v1/wms/                     # Info du module
GET  /api/v1/wms/layers               # Toutes les couches
POST /api/v1/wms/url                  # Génération URL WMS
GET  /api/v1/wms/recommend            # Recommandations

# Strategy Engine
GET  /api/v1/strategy/                # Info du module
POST /api/v1/strategy/generate        # Stratégie complète
GET  /api/v1/strategy/quick           # Stratégie rapide
POST /api/v1/strategy/stand-placement # Placement de poste
```

### Endpoints Legacy (Inchangés)
- `POST /api/analyze` - Analyse standard
- `POST /api/analyze/ai-advanced` - Analyse IA GPT-5.2
- `GET /api/products/*` - Gestion produits
- `GET /api/cart/*` - Panier

---

## 5. Phases Restantes

### P0 - Critique (Prochaines étapes)

#### Phase 3: Moteurs Métier Backend
- [ ] marketplace_engine
- [ ] user_engine
- [ ] admin_engine
- [ ] territory_engine
- [ ] referral_engine
- [ ] tracking_engine
- [ ] notification_engine
- [ ] plugins_engine

#### Phase 4: Moteurs Plan Maître Backend
- [ ] ecoforestry_engine
- [ ] engine_3d
- [ ] wildlife_behavior_engine
- [ ] weather_fauna_simulation_engine
- [ ] adaptive_strategy_engine
- [ ] advanced_geospatial_engine
- [ ] collaborative_engine
- [ ] recommendation_engine
- [ ] progression_engine
- [ ] networking_engine

#### Phase 5: Couches de Données
- [ ] ecoforestry_layers
- [ ] behavioral_layers
- [ ] simulation_layers
- [ ] layers_3d
- [ ] advanced_geospatial_layers

#### Phase 6: Module Live Heading View
- [ ] Backend complet
- [ ] Frontend immersif

#### Phase 7: Découplage server.py
- [ ] Migration des routes vers modules
- [ ] server.py devient orchestrateur pur

### P1 - Important (Phases 8-11)
- [ ] Phase 8: Modularisation Frontend Core
- [ ] Phase 9: Modularisation Frontend Métier
- [ ] Phase 10: Modules Frontend Plan Maître
- [ ] Phase 11: Tests & Documentation complète

---

## 6. Tests et Validation

### Phase 2 - Tests Effectués ✅
- [x] Import des modules (7/7)
- [x] Enregistrement des routers (7/7)
- [x] Endpoints nutrition_engine (OK)
- [x] Endpoints scoring_engine (OK)
- [x] Endpoints weather_engine (OK)
- [x] Endpoints geospatial_engine (OK)
- [x] Endpoints wms_engine (OK)
- [x] Endpoints strategy_engine (OK)
- [x] Endpoints ai_engine (OK)
- [x] Non-régression API legacy (OK)
- [x] Frontend fonctionnel (OK)

---

## 7. Configuration

### Variables d'environnement Backend
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
EMERGENT_LLM_KEY="sk-emergent-xxxx"
```

### Structure des modules
Chaque module suit la structure:
```
module_name/
├── __init__.py      # Exports
├── v1/
│   ├── __init__.py  # Version exports
│   ├── router.py    # FastAPI router
│   ├── service.py   # Business logic
│   ├── models.py    # Pydantic models
│   └── data/        # Static data
│       └── *.py
```

---

*HUNTIQ V3 - Powered by GPT-5.2 & Emergent Platform*
*Architecture Modulaire v1 - Phase 2 Complétée*
