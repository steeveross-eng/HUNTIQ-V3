# HUNTIQ V3 - Sources de Données Géospatiales Gratuites

## 📋 Vue d'ensemble

Ce document répertorie toutes les sources de données géospatiales **gratuites et ouvertes** 
utilisables pour le moteur BIONIC™.

---

## 1. LiDAR Québec

### Description
Données LiDAR (Light Detection and Ranging) du Gouvernement du Québec.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | Gouvernement du Québec |
| **URL** | https://www.donneesquebec.ca/recherche/dataset/produits-derives-de-base-du-lidar |
| **Licence** | Creative Commons CC-BY 4.0 |
| **Format** | LAZ, GeoTIFF |
| **Résolution** | 1 mètre |
| **Couverture** | Zones urbaines et périurbaines |
| **Mise à jour** | Variable selon région |

### Produits Disponibles
- **MNT (DTM)** - Modèle numérique de terrain
- **MNS (DSM)** - Modèle numérique de surface
- **MHC (CHM)** - Modèle de hauteur de canopée
- **Pente** - Carte des pentes
- **Exposition** - Carte des expositions
- **Classification** - Points classifiés

### Utilisation pour la Chasse
- Identification des crêtes et vallées
- Analyse de la canopée forestière
- Détection des chemins et sentiers
- Identification des obstacles naturels

### Accès API
```
WMS: https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WMSServer
WCS: https://servicescarto.mern.gouv.qc.ca/pes/services/Elevation/LIDAR/MapServer/WCSServer
```

---

## 2. SIGÉOM - Système d'Information Géominière

### Description
Base de données géoscientifiques du Ministère de l'Énergie et des Ressources naturelles.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | MERN Québec |
| **URL** | https://sigeom.mines.gouv.qc.ca/ |
| **Licence** | Données ouvertes Québec |
| **Format** | Shapefile, GeoJSON, WMS |
| **Résolution** | Variable (1:50000 à 1:250000) |
| **Couverture** | Tout le Québec |

### Produits Disponibles
- **Géologie du socle** - Roches ignées, sédimentaires, métamorphiques
- **Géologie de surface** - Dépôts quaternaires
- **Failles** - Lignes de fracture
- **Gîtes minéraux** - Localisation des minéraux

### Utilisation pour la Chasse
- Identification des affleurements rocheux (salines naturelles)
- Analyse de la perméabilité des sols
- Drainage naturel
- Zones de minéralisation (attractif pour cervidés)

### Accès API
```
WMS: https://sigeom.mines.gouv.qc.ca/geoserver/ows?service=WMS
WFS: https://sigeom.mines.gouv.qc.ca/geoserver/ows?service=WFS
```

---

## 3. Sentinel-2 (ESA Copernicus)

### Description
Imagerie satellite multispectrale de l'Agence Spatiale Européenne.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | ESA / Copernicus |
| **URL** | https://scihub.copernicus.eu/dhus/ |
| **Licence** | Free and Open |
| **Format** | SAFE, GeoTIFF |
| **Résolution** | 10m (B2,B3,B4,B8), 20m (autres), 60m (atmo) |
| **Couverture** | Globale |
| **Revisite** | 5 jours |

### Bandes Spectrales
| Bande | Nom | Résolution | Usage |
|-------|-----|------------|-------|
| B02 | Blue | 10m | Couleur vraie |
| B03 | Green | 10m | Couleur vraie |
| B04 | Red | 10m | NDVI |
| B08 | NIR | 10m | NDVI, végétation |
| B11 | SWIR1 | 20m | Humidité |
| B12 | SWIR2 | 20m | Végétation sèche |

### Indices Calculables
- **NDVI** = (B08 - B04) / (B08 + B04) → Santé végétale
- **EVI** = 2.5 × (B08 - B04) / (B08 + 6×B04 - 7.5×B02 + 1) → Végétation amélioré
- **NDWI** = (B03 - B08) / (B03 + B08) → Humidité
- **SAVI** = (B08 - B04) / (B08 + B04 + L) × (1 + L) → Ajusté sol

### Utilisation pour la Chasse
- Identification des zones de nourriture (NDVI élevé)
- Détection des coupes forestières récentes
- Suivi saisonnier de la végétation
- Identification des zones humides

### Accès API
```python
# Via sentinelsat
from sentinelsat import SentinelAPI
api = SentinelAPI('user', 'password', 'https://scihub.copernicus.eu/dhus')
```

---

## 4. Landsat 8/9 (USGS)

### Description
Programme satellite américain de longue durée pour l'observation terrestre.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | USGS / NASA |
| **URL** | https://earthexplorer.usgs.gov/ |
| **Licence** | Public Domain |
| **Format** | GeoTIFF |
| **Résolution** | 30m (multispectral), 100m (thermal) |
| **Couverture** | Globale |
| **Revisite** | 16 jours |

### Bandes Landsat 8/9
| Bande | Nom | Résolution | Longueur d'onde |
|-------|-----|------------|-----------------|
| B1 | Coastal | 30m | 0.43-0.45 µm |
| B2 | Blue | 30m | 0.45-0.51 µm |
| B3 | Green | 30m | 0.53-0.59 µm |
| B4 | Red | 30m | 0.64-0.67 µm |
| B5 | NIR | 30m | 0.85-0.88 µm |
| B6 | SWIR1 | 30m | 1.57-1.65 µm |
| B7 | SWIR2 | 30m | 2.11-2.29 µm |
| B10 | TIRS1 | 100m | 10.6-11.2 µm |

### Utilisation pour la Chasse
- Analyse historique de la végétation (archives depuis 1984)
- Détection thermique des zones d'activité
- Changements d'utilisation des terres
- Stress hydrique de la végétation

### Accès API
```
USGS EarthExplorer: https://earthexplorer.usgs.gov/
Landsat on AWS: s3://usgs-landsat/
Google Earth Engine: ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
```

---

## 5. Hydrographie Québec (GRHQ)

### Description
Réseau hydrographique du Québec - cours d'eau et plans d'eau.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | Gouvernement du Québec |
| **URL** | https://www.donneesquebec.ca/recherche/dataset/grhq |
| **Licence** | Creative Commons CC-BY 4.0 |
| **Format** | Shapefile, GeoJSON, GPKG |
| **Échelle** | 1:20000 |
| **Couverture** | Tout le Québec |

### Couches Disponibles
- **Cours d'eau** - Rivières, ruisseaux, fossés
- **Plans d'eau** - Lacs, étangs, réservoirs
- **Milieux humides** - Marais, tourbières, marécages
- **Bassins versants** - Délimitation des bassins

### Attributs
- Nom du cours d'eau
- Ordre de Strahler
- Type de plan d'eau
- Superficie
- Périmètre
- Connectivité

### Utilisation pour la Chasse
- Identification des sources d'eau pour le gibier
- Corridors de déplacement le long des cours d'eau
- Zones d'alimentation (milieux humides)
- Planification des postes d'affût

### Accès
```
Téléchargement: https://www.donneesquebec.ca/recherche/dataset/grhq
WMS: https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer
```

---

## 6. Modèle Numérique d'Élévation (MNE) Québec

### Description
Données d'élévation du territoire québécois.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | Gouvernement du Québec |
| **URL** | https://www.donneesquebec.ca/recherche/dataset/modeles-numeriques-d-elevation |
| **Licence** | Creative Commons CC-BY 4.0 |
| **Format** | GeoTIFF |
| **Résolution** | 1m à 10m selon la source |
| **Couverture** | Tout le Québec |

### Produits Dérivables
- Pente (degrés ou pourcentage)
- Exposition (aspect)
- Courbure (convexe/concave)
- TPI - Topographic Position Index
- TWI - Topographic Wetness Index
- Hillshade (ombrage)

### Utilisation pour la Chasse
- Identification des postes d'affût en hauteur
- Corridors naturels (vallées, cols)
- Zones thermiques (expositions sud)
- Analyse de visibilité

---

## 7. OpenStreetMap (OSM)

### Description
Base de données géographiques collaborative mondiale.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | Communauté OSM |
| **URL** | https://www.openstreetmap.org/ |
| **Licence** | ODbL (Open Database License) |
| **Format** | PBF, XML, GeoJSON |
| **Résolution** | Variable |
| **Couverture** | Globale |

### Données Disponibles
- Routes et chemins forestiers
- Bâtiments et structures
- Utilisation des terres
- Points d'intérêt
- Limites administratives

### Utilisation pour la Chasse
- Planification des accès
- Identification des zones bâties
- Chemins forestiers
- Limites de propriétés

### Accès API
```
Overpass API: https://overpass-api.de/api/interpreter
Geofabrik: https://download.geofabrik.de/north-america/canada/quebec.html
```

---

## 8. MFFP - Carte Écoforestière

### Description
Inventaire forestier du Ministère des Forêts, de la Faune et des Parcs.

### Informations
| Attribut | Valeur |
|----------|--------|
| **Fournisseur** | MFFP Québec |
| **URL** | https://www.donneesquebec.ca/recherche/dataset/carte-ecoforestiere-avec-perturbations |
| **Licence** | Creative Commons CC-BY 4.0 |
| **Format** | Shapefile, GDB |
| **Échelle** | 1:20000 |
| **Couverture** | Forêts publiques du Québec |

### Attributs Principaux
- Type de peuplement (résineux, feuillus, mixte)
- Espèces dominantes
- Classe d'âge
- Classe de densité
- Hauteur
- Perturbations (coupes, feux, épidémies)

### Codes Espèces Communs
| Code | Espèce |
|------|--------|
| EPN | Épinette noire |
| SAB | Sapin baumier |
| BOP | Bouleau à papier |
| PET | Peuplier faux-tremble |
| ERS | Érable à sucre |
| THO | Thuya occidental |

### Utilisation pour la Chasse
- Identification des peuplements alimentaires
- Corridors de couvert
- Âge et structure forestière
- Régénération après perturbation

### Accès
```
Téléchargement: https://www.donneesquebec.ca/recherche/dataset/carte-ecoforestiere-avec-perturbations
```

---

## 📊 Résumé des Sources

| Source | Licence | Résolution | Mise à jour | Coût |
|--------|---------|------------|-------------|------|
| LiDAR Québec | CC-BY 4.0 | 1m | Variable | Gratuit |
| SIGÉOM | Ouvert QC | Variable | Continue | Gratuit |
| Sentinel-2 | Free/Open | 10-60m | 5 jours | Gratuit |
| Landsat 8/9 | Public Domain | 30m | 16 jours | Gratuit |
| GRHQ | CC-BY 4.0 | 1:20000 | Annuelle | Gratuit |
| MNE Québec | CC-BY 4.0 | 1-10m | Variable | Gratuit |
| OSM | ODbL | Variable | Continue | Gratuit |
| MFFP Forêt | CC-BY 4.0 | 1:20000 | ~10 ans | Gratuit |

---

## 🔗 Liens Utiles

### Portails de Données
- [Données Québec](https://www.donneesquebec.ca/)
- [Copernicus Open Access Hub](https://scihub.copernicus.eu/)
- [USGS EarthExplorer](https://earthexplorer.usgs.gov/)
- [SIGÉOM](https://sigeom.mines.gouv.qc.ca/)

### Documentation Technique
- [Sentinel-2 User Guide](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi)
- [Landsat Science](https://landsat.gsfc.nasa.gov/)
- [QGIS Documentation](https://docs.qgis.org/)

### Outils Open Source
- [GDAL](https://gdal.org/) - Traitement raster/vecteur
- [Rasterio](https://rasterio.readthedocs.io/) - Python raster
- [GeoPandas](https://geopandas.org/) - Python vecteur
- [SentinelSat](https://sentinelsat.readthedocs.io/) - API Sentinel

---

*BIONIC™ - 100% Gratuit, 100% Ouvert, 100% Québécois*
