# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Dernière mise à jour: Décembre 2025
## Version: 3.5 (Architecture Modulaire - Phase 5 Complétée)

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
- **Architecture**: Modulaire v1.4 (Phases 2+3+4+5 complétées)

### Structure Modulaire - 30 Modules Opérationnels

```
/app/backend/modules/
├── [PHASE 2 - CORE] 7 modules ✅
│   ├── nutrition_engine/v1/       ✅
│   ├── scoring_engine/v1/         ✅
│   ├── ai_engine/v1/              ✅
│   ├── weather_engine/v1/         ✅
│   ├── geospatial_engine/v1/      ✅
│   ├── wms_engine/v1/             ✅
│   └── strategy_engine/v1/        ✅
│
├── [PHASE 3 - MÉTIER] 8 modules ✅
│   ├── user_engine/v1/            ✅
│   ├── admin_engine/v1/           ✅
│   ├── notification_engine/v1/    ✅
│   ├── referral_engine/v1/        ✅
│   ├── territory_engine/v1/       ✅
│   ├── tracking_engine/v1/        ✅
│   ├── marketplace_engine/v1/     ✅
│   └── plugins_engine/v1/         ✅
│
├── [PHASE 4 - PLAN MAÎTRE] 10 modules ✅
│   ├── recommendation_engine/v1/   ✅ Priorité 1
│   ├── collaborative_engine/v1/    ✅ Priorité 2
│   ├── ecoforestry_engine/v1/      ✅
│   ├── engine_3d/v1/               ✅
│   ├── wildlife_behavior_engine/v1/ ✅
│   ├── weather_fauna_simulation_engine/v1/ ✅
│   ├── adaptive_strategy_engine/v1/ ✅
│   ├── advanced_geospatial_engine/v1/ ✅
│   ├── progression_engine/v1/      ✅
│   └── networking_engine/v1/       ✅
│
├── [PHASE 5 - DATA LAYERS] 5 modules ✅ (NOUVEAU)
│   ├── data_layers/
│   │   ├── ecoforestry_layers/v1/     ✅ SIEF, inventaire forestier
│   │   ├── behavioral_layers/v1/      ✅ Comportement faune
│   │   ├── simulation_layers/v1/      ✅ Simulation météo-faune
│   │   ├── layers_3d/v1/              ✅ Élévation, terrain 3D
│   │   └── advanced_geospatial_layers/v1/ ✅ Corridors, connectivité
│   │
│   └── __init__.py                ✅ Central registry
│
└── routers.py                     ✅ Point d'entrée central (v1.4)
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

### Phase 4: Moteurs Plan Maître Backend ✅ (NOUVEAU)
| Module | Endpoint | Fonctionnalités |
|--------|----------|-----------------|
| recommendation_engine | /api/v1/recommendation | Recommandations personnalisées, filtrage hybride |
| collaborative_engine | /api/v1/collaborative | Groupes de chasse, chat, partage de spots |
| ecoforestry_engine | /api/v1/ecoforestry | Données SIEF, habitats par espèce |
| engine_3d | /api/v1/3d | MNT, profils élévation, viewshed |
| wildlife_behavior_engine | /api/v1/wildlife | Comportement animalier, prédiction |
| weather_fauna_simulation_engine | /api/v1/simulation | Corrélation météo/faune |
| adaptive_strategy_engine | /api/v1/adaptive | Stratégies adaptatives temps réel |
| advanced_geospatial_engine | /api/v1/advanced-geo | Corridors, zones concentration, heatmaps |
| progression_engine | /api/v1/progression | Gamification, XP, badges, défis |
| networking_engine | /api/v1/network | Réseau social chasseurs |

---

## 4. Documentation

### Swagger/OpenAPI
- **Swagger UI**: /api/docs
- **ReDoc**: /api/redoc
- **OpenAPI JSON**: /api/openapi.json

### Statut des Modules
- **Endpoint**: /api/modules/status
- **Total modules**: 25
- **Phase 2**: 7 modules
- **Phase 3**: 8 modules
- **Phase 4**: 10 modules

---

## 5. Phases Restantes

### P0 - Critique

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
- [x] 25/25 modules opérationnels
- [x] Non-régression validée (monolithe + modules existants)
- [x] Frontend fonctionnel
- [x] Documentation Swagger accessible
- [x] Tous les health checks Phase 4 validés

---

## 7. Changelog Décembre 2025

### Phase 4 Complétée (Décembre 2025)
- ✅ recommendation_engine créé avec filtrage hybride (collaboratif + contenu + contexte)
- ✅ collaborative_engine créé avec groupes, spots, calendrier, chat, positions
- ✅ ecoforestry_engine créé avec données SIEF, analyse habitats
- ✅ engine_3d créé avec MNT, profils élévation, viewshed
- ✅ wildlife_behavior_engine créé avec modélisation comportement 3 espèces
- ✅ weather_fauna_simulation_engine créé avec corrélations météo/activité
- ✅ adaptive_strategy_engine créé avec stratégies adaptatives et feedback
- ✅ advanced_geospatial_engine créé avec corridors, zones, heatmaps
- ✅ progression_engine créé avec XP, niveaux, badges, défis
- ✅ networking_engine créé avec profils, connexions, feed, événements
- ✅ routers.py mis à jour vers v1.3 avec 25 modules
- ✅ Tous endpoints testés et fonctionnels

---

*HUNTIQ V3 - Powered by GPT-5.2 & Emergent Platform*
*Architecture Modulaire v1.3 - 25 Modules Opérationnels*
