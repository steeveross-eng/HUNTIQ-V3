# ═══════════════════════════════════════════════════════════════════════════════
#                    BIONIC™ - SCHÉMA D'ARCHITECTURE FINAL
#                              Version 1.0.0
#                              2026-02-05
# ═══════════════════════════════════════════════════════════════════════════════

## 1. VUE D'ENSEMBLE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BIONIC™ PLATFORM                                  │
│                    Application Géospatiale de Chasse                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND (React 18)                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Territory│  │   WMS    │  │ Waypoint │  │  Design  │            │   │
│  │  │   Page   │  │ Selector │  │  System  │  │  Tokens  │            │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │   │
│  │       │              │              │              │                 │   │
│  │  ┌────┴──────────────┴──────────────┴──────────────┴─────┐         │   │
│  │  │              MapLibre GL JS Engine                    │         │   │
│  │  │   ┌─────────┐  ┌─────────┐  ┌─────────┐              │         │   │
│  │  │   │ Markers │  │  Layers │  │  Tiles  │              │         │   │
│  │  │   └─────────┘  └─────────┘  └─────────┘              │         │   │
│  │  └───────────────────────────────────────────────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                              HTTPS/API                                      │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        BACKEND (FastAPI)                            │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    API Gateway Layer                        │   │   │
│  │  │   /api/geospatial/*  │  /api/bionic/*  │  /api/wms-proxy/*  │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                      │   │
│  │  ┌───────────────┬───────────┴───────────┬───────────────┐         │   │
│  │  │               │                       │               │         │   │
│  │  ▼               ▼                       ▼               ▼         │   │
│  │ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │   │
│  │ │Corridor│  │ Hydro  │  │Nutrition│  │Behavior│  │  WMS   │        │   │
│  │ │ Engine │  │ Engine │  │ Engine │  │Engine  │  │ Proxy  │        │   │
│  │ │  (P1)  │  │  (P1)  │  │  (P1)  │  │V3 (P3) │  │        │        │   │
│  │ └────────┘  └────────┘  └────────┘  └────────┘  └────────┘        │   │
│  │                                                      │             │   │
│  └──────────────────────────────────────────────────────│─────────────┘   │
│                                                         │                  │
│  ┌──────────────────────────────────────────────────────│─────────────┐   │
│  │                    EXTERNAL SERVICES                 │             │   │
│  │                                                      ▼             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐   │   │
│  │  │  OSM    │  │ CanVec  │  │  USGS   │  │    QUÉBEC GOV       │   │   │
│  │  │  WMS    │  │  NRCan  │  │  Topo   │  │ (Auth Required)     │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  │ SIGÉOM│LiDAR│MFFP   │   │   │
│  │                                          └─────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        DATA LAYER                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │  MongoDB    │  │  File Cache │  │  Redis      │                 │   │
│  │  │  (Users,    │  │  (WMS Tiles)│  │  (Futur)    │                 │   │
│  │  │   Config)   │  │             │  │             │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. ARCHITECTURE MODULAIRE

### 2.1 Frontend Modules

```
/app/frontend/src/
├── components/
│   └── geospatial/
│       ├── TerritoryMap.jsx      # Composant carte principal
│       ├── WMSLayerSelector.jsx  # Sélecteur de couches WMS
│       └── BehaviorV3Panel.jsx   # Panneau ML v3
├── pages/
│   └── TerritoryPage.jsx         # Page territoire intégrée
├── lib/
│   ├── maplibre.js               # Configuration MapLibre GL
│   └── designTokens.js           # Tokens UX centralisés
├── hooks/
│   └── useBehaviorV3.js          # Hook ML v3
└── services/
    └── behaviorV3.service.js     # Service API ML v3
```

### 2.2 Backend Modules

```
/app/backend/
├── server.py                     # Point d'entrée FastAPI
├── geospatial/
│   ├── __init__.py
│   ├── controllers/
│   │   └── wms_proxy_controller.py  # Proxy WMS sécurisé
│   └── endpoints/
│       └── __init__.py           # 50+ endpoints géospatiaux
└── wms_proxy_router.py           # Router WMS fallback

/app/bionic/engines/
├── geospatial/                   # P1 Géo-Suite
│   └── api/endpoints.py
├── behaviorV3/                   # P3 ML Engine
│   ├── api/
│   ├── v3_core/
│   ├── v3_data/
│   └── v3_models/
└── [autres engines]/
```

---

## 3. FLUX DE DONNÉES

### 3.1 Chargement des Couches WMS

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Frontend │───▶│ /api/wms │───▶│  Proxy   │───▶│ External │
│ MapLibre │    │ /sources │    │Controller│    │   WMS    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                               │
     │         Configuration         │
     │◀──────────────────────────────│
     │                               │
     │    Tile Request               │
     │──────▶ /api/wms/tile/{src}/{layer}
     │                               │
     │         PNG Response          │
     │◀──────────────────────────────│
```

### 3.2 Analyse ML (BehaviorEngine v3)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Frontend │───▶│/api/bio- │───▶│ Behavior │───▶│ Gradient │
│  Panel   │    │nic/v3/* │    │Engine V3 │    │ Boosting │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                     │
                              ┌──────┴──────┐
                              │ Calibration │
                              │   Matrix    │
                              └─────────────┘
```

---

## 4. SÉPARATION DES RESPONSABILITÉS

| Couche | Responsabilité | Technologies |
|--------|---------------|--------------|
| **Présentation** | UI/UX, interactions utilisateur | React, TailwindCSS, ShadcnUI |
| **Cartographie** | Rendu carte, couches, markers | MapLibre GL JS |
| **API Gateway** | Routage, authentification | FastAPI, Pydantic |
| **Business Logic** | Engines d'analyse | Python, scikit-learn |
| **Data Access** | Proxy WMS, cache | httpx, MongoDB |
| **External Services** | Sources de données | OSM, CanVec, USGS |

---

## 5. ÉVOLUTIVITÉ

### 5.1 Points d'Extension

1. **Nouvelles Couches WMS**
   - Ajouter dans `WMS_SOURCES` dict
   - Support auth automatique si provider configuré

2. **Nouveaux Engines**
   - Créer module dans `/app/bionic/engines/`
   - Enregistrer router dans `server.py`

3. **Nouveaux Modules Frontend**
   - Composants dans `/components/`
   - Services dans `/services/`
   - Hooks dans `/hooks/`

### 5.2 Intégrations Futures

| Module | Statut | Prérequis |
|--------|--------|-----------|
| Redis Cache | Planifié | Installation Redis |
| Couches Québec | En attente | Credentials API |
| Marketplace | Backlog | Stripe intégré |
| Export PDF | Backlog | - |

---

## 6. SÉCURITÉ

### 6.1 Gestion des Credentials

```python
QUEBEC_WMS_CREDENTIALS = {
    "mern": {
        "env_key": "QUEBEC_MERN_API_KEY",
        "env_token": "QUEBEC_MERN_TOKEN",
        "auth_type": "token"
    },
    "mffp": { ... },
    "sigeom": { ... }
}
```

### 6.2 Points de Sécurité

- ✅ Credentials en variables d'environnement
- ✅ Proxy WMS pour masquer URLs externes
- ✅ CORS configuré
- ✅ Validation Pydantic sur inputs

---

## 7. PERFORMANCE

### 7.1 Optimisations Actuelles

- Cache fichier pour tuiles WMS
- Lazy loading des composants
- Debounce sur interactions carte

### 7.2 Optimisations Planifiées

- Redis pour cache distribué
- CDN pour assets statiques
- Service worker pour offline

---

*Document généré automatiquement - BIONIC™ Architecture v1.0.0*
*2026-02-05*
