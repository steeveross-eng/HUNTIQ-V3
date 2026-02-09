# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Dernière mise à jour: Décembre 2025
## Version: 3.3 (Architecture Modulaire - Phase 3 Complétée)

---

## 1. Énoncé du Problème Original

Fusionner HUNTIQ V1 et V2 + Intégrer l'IA GPT-5.2 pour l'analyse d'attractants.
Refactorisation majeure vers une architecture modulaire stricte ("PLAN MAÎTRE BIONIC").

---

## 2. Architecture

### Stack Technique
- **Frontend**: React 18 + Tailwind CSS + ShadCN UI
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB
- **IA**: GPT-5.2 via Emergent LLM Key
- **Architecture**: Modulaire v1.2 (Phases 2+3 complétées)

### Structure Modulaire - 15 Modules Opérationnels

```
/app/backend/modules/
├── [PHASE 2 - CORE] 7 modules
│   ├── nutrition_engine/v1/       ✅
│   ├── scoring_engine/v1/         ✅
│   ├── ai_engine/v1/              ✅
│   ├── weather_engine/v1/         ✅
│   ├── geospatial_engine/v1/      ✅
│   ├── wms_engine/v1/             ✅
│   └── strategy_engine/v1/        ✅
│
├── [PHASE 3 - MÉTIER] 8 modules
│   ├── user_engine/v1/            ✅
│   ├── admin_engine/v1/           ✅
│   ├── notification_engine/v1/    ✅
│   ├── referral_engine/v1/        ✅
│   ├── territory_engine/v1/       ✅
│   ├── tracking_engine/v1/        ✅
│   ├── marketplace_engine/v1/     ✅
│   └── plugins_engine/v1/         ✅
│
└── routers.py                     ✅ Point d'entrée central
```

---

## 3. Fonctionnalités Implémentées ✅

### Phase 1: Infrastructure Modulaire ✅
- Structure des répertoires créée pour 26 modules backend
- Documentation et configuration

### Phase 2: Moteurs Core Backend ✅
| Module | Endpoint | Fonctionnalités |
|--------|----------|-----------------|
| nutrition_engine | /api/v1/nutrition | 29 ingrédients, analyse nutritionnelle |
| scoring_engine | /api/v1/scoring | 13 critères pondérés |
| ai_engine | /api/v1/ai | GPT-5.2, comparaisons |
| weather_engine | /api/v1/weather | Score météo, lune |
| geospatial_engine | /api/v1/geospatial | 17 régions Québec |
| wms_engine | /api/v1/wms | 10 couches WMS |
| strategy_engine | /api/v1/strategy | Stratégies de chasse |

### Phase 3: Moteurs Métier Backend ✅
| Module | Endpoint | Fonctionnalités |
|--------|----------|-----------------|
| user_engine | /api/v1/user | Auth, profils, préférences |
| admin_engine | /api/v1/admin | Dashboard, maintenance |
| notification_engine | /api/v1/notification | Multi-canal |
| referral_engine | /api/v1/referral | Parrainage, commissions |
| territory_engine | /api/v1/territory | Territoires, locations |
| tracking_engine | /api/v1/tracking | GPS temps réel |
| marketplace_engine | /api/v1/marketplace | C2C équipement |
| plugins_engine | /api/v1/plugins | Feature flags |

---

## 4. Documentation

### Swagger/OpenAPI
- **Swagger UI**: /api/docs
- **ReDoc**: /api/redoc
- **OpenAPI JSON**: /api/openapi.json

---

## 5. Phases Restantes

### P0 - Critique

#### Phase 4: Moteurs Plan Maître Backend (10 modules)
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

#### Phase 5: Couches de Données (5 modules)
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

### Rapports de Test
- `/app/test_reports/iteration_1.json` - Phase 2
- `/app/test_reports/iteration_2.json` - Phase 3

### Statut
- [x] 15/15 modules opérationnels
- [x] Non-régression validée
- [x] Frontend fonctionnel
- [x] Documentation Swagger accessible

---

*HUNTIQ V3 - Powered by GPT-5.2 & Emergent Platform*
*Architecture Modulaire v1.2 - 15 Modules Opérationnels*
