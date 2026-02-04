# Plan de Refactorisation Backend BIONIC™

## Objectif
Transformer l'architecture backend de monolithique vers modulaire, en utilisant les moteurs existants dans `/app/bionic/engines/`.

## ✅ Phase 1 TERMINÉE - Orchestrateur Léger (2026-02-04)

### Résultats
- **bionic_engine.py** réduit de **2885 → 747 lignes** (réduction de 74%)
- 8 nouveaux modules créés dans `/app/bionic/engines/core/`
- API publique 100% compatible (tous les endpoints fonctionnent)
- Tests validés avec succès

### Modules Créés
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

### Endpoints Validés
- ✅ GET /api/bionic/modules (8 modules)
- ✅ GET /api/bionic/species (6 espèces)
- ✅ POST /api/bionic/analyze (analyse complète)
- ✅ GET /api/bionic/stats (statistiques globales)
- ✅ GET /api/bionic/geospatial/* (données temps réel)

---

## ✅ Phase 2 TERMINÉE - Consolidation des Modèles Pydantic (2026-02-04)

### Résultats
- **Fichier redondant supprimé** : `/app/bionic/engines/bionic_core_models.py` (213 lignes)
- **Modèles consolidés** dans `/app/bionic/engines/core/models.py` (554 lignes)
- **Enums synchronisés** : `models.py` importe depuis `configs.py` (source unique)
- **Nouveaux modèles de modules** ajoutés : PressureModuleResult, AccessModuleResult, CorridorModuleResult, GeoformModuleResult
- **API publique** : 100% compatible, tous les tests passent

### Changements clés
1. Les Enums `ModuleType`, `SpeciesType`, `SeasonType` sont maintenant définis UNIQUEMENT dans `configs.py`
2. `models.py` importe ces Enums depuis `configs.py` (évite la duplication)
3. Ajout de modèles Pydantic spécialisés pour les nouveaux types de modules
4. Version du moteur : BIONIC_CORE 2.0

### Structure finale des modèles
```
/app/bionic/engines/core/models.py (554 lignes)
├── Enums additionnels: ScoreRating, PredictionHorizon
├── Sub-models: GeoPoint, BoundingBox, DataSourceInfo, ScoreBreakdown, Recommendation
├── Module Results: ThermalModuleResult, WetnessModuleResult, FoodModuleResult, 
│                   CoverModuleResult, PressureModuleResult, AccessModuleResult,
│                   CorridorModuleResult, GeoformModuleResult
├── Species Results: HabitatSuitability, ActivityPattern, SpeciesResult
├── Prediction Results: SinglePrediction, PredictionResult
├── Temporal Results: NDVITimeSeries, SnowAnalysis, PhenologyData, TemporalResult
├── Main Model: TerritoryFullAnalysis (avec méthodes utilitaires)
└── Request/Response: TerritoryAnalysisRequest, TerritoryAnalysisSummary
```

---

## Phase 3 : Implémentation Réelle des Moteurs (PROCHAINE ÉTAPE)

**Objectif**: Remplacer les simulations par de vraies données

### Moteurs à Compléter
1. **sigeomEngine** : Intégrer API SIGEOM du Québec
2. **nutritionEngine** : Migrer la logique JS vers Python
3. **geoEngine** : Ajouter analyses géomorphologiques avancées

---

## API Publique (Préservée)

Ces endpoints SONT stables après la refactorisation :

| Endpoint | Méthode | Status |
|----------|---------|--------|
| `/api/bionic/analyze` | POST | ✅ Fonctionne |
| `/api/bionic/stats` | GET | ✅ Fonctionne |
| `/api/bionic/modules` | GET | ✅ Fonctionne |
| `/api/bionic/species` | GET | ✅ Fonctionne |
| `/api/bionic/geospatial/complete` | GET | ✅ Fonctionne |

---

## Métriques de Succès Phase 1

- [x] `bionic_engine.py` < 800 lignes ✅ (747 lignes)
- [x] Tous les endpoints passent les tests ✅
- [x] Temps de réponse `/api/bionic/analyze` < 3s ✅
- [x] 0 import circulaire ✅
- [ ] Documentation à jour (en cours)

---

*Document créé le 2026-02-04*
*Phase 1 terminée : 2026-02-04*
