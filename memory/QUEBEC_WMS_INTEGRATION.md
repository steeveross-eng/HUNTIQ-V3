# BIONIC™ - Intégration des Couches Écoforestières du Québec

## Date: 2026-02-05
## Version: 1.0

---

## 1. Résumé

L'infrastructure backend est prête pour l'intégration des couches WMS gouvernementales du Québec. Dès que les credentials API seront disponibles, il suffira de les configurer dans les variables d'environnement.

---

## 2. Sources WMS Québec - En Attente de Credentials

### 2.1 MERN (Ministère de l'Énergie et des Ressources naturelles)

| Service | URL WMS | Couches |
|---------|---------|---------|
| **LiDAR Québec** | `https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer` | DTM, DSM, CHM, Hillshade, Slope |
| **GRHQ Hydrographie** | `https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer` | Rivières, Lacs, Milieux humides, Bassins versants |
| **Limites admin** | `https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer` | MRC, Municipalités, Régions |

**Authentification MERN:**
- Type: OAuth2 Bearer Token
- Variable d'environnement: `QUEBEC_MERN_TOKEN`
- Token endpoint: `https://servicescarto.mern.gouv.qc.ca/pes/token`

### 2.2 MFFP (Ministère des Forêts, de la Faune et des Parcs)

| Service | URL WMS | Couches |
|---------|---------|---------|
| **Inventaire écoforestier** | `https://servicescarto.mffp.gouv.qc.ca/Inventaire_Ecoforestier/VerificationInventaire/MapServer/WMSServer` | Peuplements, Espèces, Âge, Densité, Hauteur, Perturbations |

**Authentification MFFP:**
- Type: OAuth2 Bearer Token
- Variable d'environnement: `QUEBEC_MFFP_TOKEN`
- Token endpoint: `https://servicescarto.mffp.gouv.qc.ca/token`

### 2.3 SIGÉOM (Système d'information géominière)

| Service | URL WMS | Couches |
|---------|---------|---------|
| **Géologie** | `https://sigeom.mines.gouv.qc.ca/geoserver/SIGEOM_GEOSCIENCES/wms` | Socle rocheux, Dépôts surface, Failles, Gîtes minéraux |

**Authentification SIGÉOM:**
- Type: HTTP Basic Authentication
- Variable d'environnement: `QUEBEC_SIGEOM_API_KEY` (format: `username:password`)
- Portal: https://sigeom.mines.gouv.qc.ca/

---

## 3. Configuration des Credentials

### 3.1 Variables d'environnement à configurer

Ajoutez ces variables dans `/app/backend/.env`:

```bash
# MERN - LiDAR, GRHQ, Limites administratives
QUEBEC_MERN_TOKEN=your_bearer_token_here

# MFFP - Inventaire écoforestier
QUEBEC_MFFP_TOKEN=your_bearer_token_here

# SIGÉOM - Géologie
QUEBEC_SIGEOM_API_KEY=username:password
```

### 3.2 Obtention des credentials

1. **MERN et MFFP**: 
   - Portail: https://www.donneesquebec.ca/
   - Créer un compte développeur
   - Demander accès aux API WMS cartographiques
   - Récupérer le Bearer Token

2. **SIGÉOM**:
   - Portal: https://sigeom.mines.gouv.qc.ca/
   - Demander accès au service WMS GeoServer
   - Utiliser le format Basic Auth (username:password)

---

## 4. Endpoints API Disponibles

### Vérifier le statut des credentials
```bash
GET /api/geospatial/wms/quebec-credentials-status
```

### Voir toutes les sources (incluant celles en attente)
```bash
GET /api/geospatial/wms/sources-all
```

### Documentation complète des URLs
```bash
GET /api/geospatial/wms/quebec-urls
```

---

## 5. Cas d'utilisation BIONIC™

| Source | Engines BIONIC™ | Usage |
|--------|-----------------|-------|
| LiDAR | CorridorEngine, TerrainEngine | Modélisation terrain, analyse pente |
| GRHQ | HydroEngine, CorridorEngine | Corridors fauniques, zones humides |
| Écoforestier | NutritionEngine, BehaviorEngine | Qualité habitat, nourriture gibier |
| SIGÉOM | TerrainEngine | Analyse sols, géologie |

---

## 6. Test de Validation

Une fois les credentials configurés, redémarrez le backend:
```bash
sudo supervisorctl restart backend
```

Puis testez:
```bash
curl http://localhost:8001/api/geospatial/wms/quebec-credentials-status
```

Les services passeront automatiquement de `"configured": false` à `"configured": true`.

---

## 7. Prochaines Étapes

1. ✅ Infrastructure backend prête (auth sécurisée)
2. ✅ Endpoints WMS configurés avec placeholders
3. ✅ Documentation des URLs complète
4. ⏳ **EN ATTENTE**: Credentials API du gouvernement
5. ⏳ Test avec credentials réels
6. ⏳ Activation dans le frontend WMSLayerSelector

---

*Document généré automatiquement par BIONIC™ GeoEngine*
