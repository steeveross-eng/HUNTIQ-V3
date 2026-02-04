# Plan de Refactorisation Backend BIONIC™

## Objectif
Transformer l'architecture backend de monolithique vers modulaire, en utilisant les moteurs existants dans `/app/bionic/engines/`.

## État Actuel

### Problème Identifié
- **`/app/backend/bionic_engine.py`** : 2885 lignes (MONOLITHIQUE)
- Contient une logique d'analyse complète dupliquée
- Les moteurs modulaires dans `/app/bionic/engines/` sont sous-utilisés

### Architecture Modulaire Existante
```
/app/bionic/engines/
├── core/                    # Modèles Pydantic (TerritoryFullAnalysis)
├── environmentEngine/       # Combinaison des scores ✅ FONCTIONNEL
├── hydroEngine/             # Analyse hydrologique ✅ FONCTIONNEL
├── sentinelEngine/          # Analyse végétation ✅ FONCTIONNEL
├── sigeomEngine/            # Analyse géologique ⚠️ SIMULÉ
├── nutritionEngine/         # Analyse nutritionnelle ⚠️ JS MIGRATION REQUISE
├── geoEngine/               # Moteur géospatial
└── wmsProxy/                # Proxy WMS ✅ AMÉLIORÉ
```

## Plan de Refactorisation (3 Phases)

### Phase 1 : Orchestrateur Léger (Priorité HAUTE)

**Objectif**: Transformer `bionic_engine.py` en orchestrateur qui délègue aux moteurs

#### Étapes
1. Créer `/app/bionic/engines/orchestrator.py`
   - Import et instantiation de tous les moteurs
   - Méthode `analyze_territory()` qui appelle chaque moteur
   - Agrégation des résultats via `EnvironmentCombiner`

2. Refactorer les endpoints dans `bionic_engine.py`
   - `POST /api/bionic/analyze` → appelle `orchestrator.analyze_territory()`
   - Supprimer la logique d'analyse dupliquée (fonctions `calculate_module_score`, etc.)
   - Conserver uniquement le routage FastAPI

3. Tests de non-régression
   - Vérifier que les endpoints existants retournent les mêmes structures

#### Fichiers à modifier
- `/app/backend/bionic_engine.py` (réduire de ~2000 lignes)
- `/app/bionic/engines/orchestrator.py` (nouveau)

### Phase 2 : Consolidation des Modèles (Priorité MOYENNE)

**Objectif**: Unifier les modèles Pydantic

#### Étapes
1. Supprimer les fichiers redondants:
   - `/app/bionic/engines/bionic_core_models.py` → fusionner avec `/app/bionic/engines/core/models.py`

2. Créer un package `bionic_models` centralisé
   - Tous les moteurs importent depuis ce package
   - Export unique pour le backend

3. Vérifier les imports dans tous les moteurs

### Phase 3 : Implémentation Réelle des Moteurs (Priorité BASSE)

**Objectif**: Remplacer les simulations par de vraies données

#### Moteurs à compléter
1. **sigeomEngine** : Intégrer API SIGEOM du Québec
2. **nutritionEngine** : Migrer la logique JS vers Python
3. **geoEngine** : Ajouter analyses géomorphologiques avancées

---

## API Publique (À Préserver)

Ces endpoints DOIVENT rester stables pendant la refactorisation :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/bionic/analyze` | POST | Analyse complète de territoire |
| `/api/bionic/stats` | GET | Statistiques globales |
| `/api/bionic/modules` | GET | Liste des modules disponibles |
| `/api/bionic/species` | GET | Liste des espèces |
| `/api/bionic/geospatial/complete` | GET | Données géospatiales combinées |

---

## Risques et Mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Régression des endpoints | ÉLEVÉ | Tests automatisés avant/après |
| Perte de performances | MOYEN | Profiling et cache |
| Conflits de merge | FAIBLE | Branches dédiées |

---

## Métriques de Succès

- [ ] `bionic_engine.py` < 500 lignes
- [ ] Tous les endpoints passent les tests
- [ ] Temps de réponse `/api/bionic/analyze` < 3s
- [ ] 0 import circulaire
- [ ] Documentation à jour

---

## Timeline Suggérée

| Phase | Durée estimée | Dépendances |
|-------|---------------|-------------|
| Phase 1 | 2-3 sessions | Aucune |
| Phase 2 | 1 session | Phase 1 |
| Phase 3 | Variable | Phases 1+2, accès APIs externes |

---

*Document créé le 2026-02-04*
*Dernière mise à jour : 2026-02-04*
