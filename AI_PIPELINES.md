# HUNTIQ V3 - Pipelines IA Géospatiaux

## 🧠 Vue d'ensemble

Ce document décrit les pipelines d'intelligence artificielle prévus pour le moteur géospatial BIONIC™.

**Status:** Architecture préparée - Implémentation en attente

---

## 📋 Table des Matières

1. [Architecture IA](#architecture-ia)
2. [Pipeline de Corridors](#pipeline-de-corridors)
3. [Pipeline de Zones](#pipeline-de-zones)
4. [Pipeline de Score](#pipeline-de-score)
5. [Intégration GPT-5.2](#intégration-gpt-52)
6. [Données d'Entraînement](#données-dentraînement)
7. [Modèles Prévus](#modèles-prévus)

---

## 🏗 Architecture IA

### Vue Globale
```
┌─────────────────────────────────────────────────────────────────┐
│                    DONNÉES GÉOSPATIALES                         │
│  LiDAR │ Sentinel │ Landsat │ SIGÉOM │ Hydro │ Forêt │ MNE    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING                          │
│                                                                 │
│  • Normalisation des données                                    │
│  • Extraction de features                                       │
│  • Création de tenseurs multi-couches                          │
│  • Augmentation de données                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODÈLES ML/DL                                │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CORRIDOR   │  │    ZONE      │  │    SCORE     │          │
│  │   PREDICTOR  │  │  CLASSIFIER  │  │  CALCULATOR  │          │
│  │   (U-Net)    │  │  (ResNet)    │  │  (XGBoost)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POST-PROCESSING                              │
│                                                                 │
│  • Vectorisation des prédictions                               │
│  • Filtrage par seuil de confiance                             │
│  • Fusion multi-échelle                                         │
│  • Validation contextuelle                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GPT-5.2 INTEGRATION                          │
│                                                                 │
│  • Interprétation des résultats                                │
│  • Génération de recommandations                               │
│  • Explication en langage naturel                              │
│  • Conseils personnalisés                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Structure des Fichiers
```
/app/ai/geospatial/
├── models/
│   ├── corridor_predictor/
│   │   ├── model.h5              # Poids U-Net
│   │   ├── config.json           # Configuration
│   │   └── preprocessing.py      # Prétraitement
│   ├── zone_classifier/
│   │   ├── model.h5              # Poids ResNet
│   │   ├── config.json
│   │   └── preprocessing.py
│   └── score_calculator/
│       ├── model.joblib          # Modèle XGBoost
│       ├── config.json
│       └── features.py
├── pipelines/
│   ├── corridor_pipeline.py
│   ├── zone_pipeline.py
│   ├── score_pipeline.py
│   └── gpt_integration.py
└── utils/
    ├── feature_extraction.py
    ├── data_augmentation.py
    └── evaluation.py
```

---

## 🛤 Pipeline de Corridors

### Objectif
Prédire les corridors de déplacement du gibier basé sur les caractéristiques du terrain.

### Architecture du Modèle
```
Modèle: U-Net Modifié
Entrée: Tenseur 256x256x8 (8 couches géospatiales)
Sortie: Masque 256x256x1 (probabilité de corridor)
```

### Couches d'Entrée
| Canal | Donnée | Source | Normalisation |
|-------|--------|--------|---------------|
| 0 | Élévation | MNE | Min-Max [0,1] |
| 1 | Pente | MNE dérivé | [0, 45°] → [0,1] |
| 2 | Aspect | MNE dérivé | Circulaire sin/cos |
| 3 | TPI | MNE dérivé | Z-score |
| 4 | NDVI | Sentinel-2 | [-1,1] → [0,1] |
| 5 | Distance eau | Hydro | Log transform |
| 6 | Type forêt | MFFP | One-hot encoded |
| 7 | Couvert | LiDAR | [0,100] → [0,1] |

### Pseudo-code Pipeline
```python
class CorridorPipeline:
    """
    Pipeline de prédiction des corridors de déplacement.
    ARCHITECTURE PRÉPARÉE - Implémentation en attente.
    """
    
    def __init__(self, model_path: str):
        self.model = None  # À charger
        self.preprocessor = None
        
    def preprocess(self, bbox: BoundingBox) -> np.ndarray:
        """
        Prétraitement des données géospatiales.
        
        1. Télécharger les données pour chaque source
        2. Resampler à 10m de résolution
        3. Aligner les rasters
        4. Normaliser chaque couche
        5. Empiler en tenseur
        """
        pass
        
    def predict(self, tensor: np.ndarray) -> np.ndarray:
        """
        Prédiction des corridors.
        
        1. Passer le tenseur dans U-Net
        2. Seuiller à 0.5
        3. Squelettiser pour obtenir les lignes centrales
        """
        pass
        
    def postprocess(self, mask: np.ndarray, bbox: BoundingBox) -> List[Corridor]:
        """
        Post-traitement des prédictions.
        
        1. Vectoriser les masques
        2. Simplifier les géométries
        3. Calculer les attributs (longueur, direction)
        4. Filtrer par taille minimale
        """
        pass
```

### Métriques d'Évaluation
- IoU (Intersection over Union) > 0.6
- Dice Score > 0.7
- Precision > 0.8
- Recall > 0.7

---

## 🎯 Pipeline de Zones

### Objectif
Classifier les zones en fonction de leur utilisation par le gibier (alimentation, repos, eau).

### Architecture du Modèle
```
Modèle: ResNet-50 Modifié
Entrée: Tenseur 64x64x8 (patch géospatial)
Sortie: 4 classes (feeding, bedding, water, other)
```

### Classes de Sortie
| Classe | Description | Caractéristiques |
|--------|-------------|------------------|
| `feeding` | Zone d'alimentation | NDVI élevé, feuillus, bord |
| `bedding` | Zone de repos | Pente faible, couvert dense |
| `water` | Zone d'eau | Proximité hydro, TWI élevé |
| `other` | Autre | Non classifiable |

### Pseudo-code Pipeline
```python
class ZonePipeline:
    """
    Pipeline de classification des zones de chasse.
    ARCHITECTURE PRÉPARÉE - Implémentation en attente.
    """
    
    def __init__(self, model_path: str):
        self.model = None  # À charger
        self.patch_size = 64
        
    def extract_patches(self, tensor: np.ndarray) -> List[np.ndarray]:
        """
        Extraction des patches pour classification.
        
        1. Découper le raster en patches 64x64
        2. Filtrer les patches avec données manquantes
        3. Augmenter si nécessaire
        """
        pass
        
    def classify(self, patches: List[np.ndarray]) -> List[str]:
        """
        Classification des patches.
        
        1. Batch les patches
        2. Prédire avec ResNet
        3. Retourner les classes
        """
        pass
        
    def aggregate(self, predictions: List, locations: List) -> Dict:
        """
        Agrégation des résultats.
        
        1. Regrouper par classe
        2. Fusionner les patches adjacents
        3. Créer les polygones de zones
        """
        pass
```

### Métriques d'Évaluation
- Accuracy > 0.85
- F1-Score par classe > 0.75
- Confusion Matrix balanced

---

## 📊 Pipeline de Score

### Objectif
Calculer un score de potentiel de chasse (0-100) basé sur toutes les caractéristiques.

### Architecture du Modèle
```
Modèle: XGBoost Regressor
Entrée: Vecteur de 50+ features
Sortie: Score continu [0, 100]
```

### Features d'Entrée

#### Features Terrain (15)
- elevation_mean, elevation_std
- slope_mean, slope_optimal_pct (5-15°)
- aspect_south_pct, aspect_diversity
- tpi_valley_pct, tpi_ridge_pct
- twi_mean, curvature_concave_pct

#### Features Végétation (10)
- ndvi_mean, ndvi_max
- evi_mean, evi_seasonal_change
- vegetation_type_diversity
- edge_density

#### Features Eau (8)
- water_distance_min
- water_count_500m
- wetland_area_pct
- stream_density

#### Features Forêt (10)
- forest_type_mixed_pct
- age_class_mature_pct
- density_optimal_pct
- species_diversity
- mast_producing_pct

#### Features IA (7)
- corridor_probability_max
- feeding_zone_area
- bedding_zone_area
- connectivity_index

### Pseudo-code Pipeline
```python
class ScorePipeline:
    """
    Pipeline de calcul du score de potentiel.
    ARCHITECTURE PRÉPARÉE - Implémentation en attente.
    """
    
    def __init__(self, model_path: str):
        self.model = None  # À charger
        self.feature_names = []
        
    def extract_features(self, bbox: BoundingBox, data: Dict) -> np.ndarray:
        """
        Extraction des features pour le scoring.
        
        1. Calculer les statistiques terrain
        2. Calculer les indices végétation
        3. Calculer les métriques eau
        4. Calculer les métriques forêt
        5. Ajouter les prédictions IA
        """
        pass
        
    def predict_score(self, features: np.ndarray) -> float:
        """
        Prédiction du score.
        
        1. Normaliser les features
        2. Prédire avec XGBoost
        3. Clipper [0, 100]
        """
        pass
        
    def explain(self, features: np.ndarray) -> Dict:
        """
        Explication du score (SHAP values).
        
        1. Calculer les contributions
        2. Identifier les top 5 positifs
        3. Identifier les top 5 négatifs
        """
        pass
```

### Pondération des Composantes
```python
COMPONENT_WEIGHTS = {
    'terrain': 0.20,
    'vegetation': 0.20,
    'water': 0.15,
    'forest': 0.15,
    'geology': 0.10,
    'ai_predictions': 0.10,
    'historical': 0.10
}
```

---

## 🤖 Intégration GPT-5.2

### Objectif
Utiliser GPT-5.2 pour générer des recommandations en langage naturel basées sur les analyses.

### Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Résultats     │────▶│   Prompt        │────▶│   GPT-5.2       │
│   Géospatiaux   │     │   Generator     │     │   (Emergent)    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RECOMMANDATIONS                              │
│  • Meilleurs postes d'affût                                     │
│  • Heures optimales                                             │
│  • Stratégies d'approche                                        │
│  • Adaptation météo                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Template de Prompt
```python
GPT_PROMPT_TEMPLATE = """
Tu es un expert en chasse au Québec. Analyse ces données géospatiales et donne des recommandations.

**Score de Potentiel:** {score}/100 ({level})

**Analyse du Terrain:**
- Élévation moyenne: {elevation}m
- Pente dominante: {slope}°
- Exposition: {aspect}

**Végétation:**
- NDVI moyen: {ndvi}
- Type forestier: {forest_type}
- Couvert: {canopy}%

**Hydrologie:**
- Distance eau: {water_dist}m
- Sources proches: {water_count}

**Prédictions IA:**
- Corridors détectés: {corridors}
- Zones alimentation: {feeding}
- Zones repos: {bedding}

**Espèce cible:** {species}
**Saison:** {season}
**Météo actuelle:** {weather}

Donne 3-5 recommandations précises pour optimiser la chasse dans ce territoire.
"""
```

### Pseudo-code Intégration
```python
class GPTIntegration:
    """
    Intégration GPT-5.2 pour recommandations.
    ARCHITECTURE PRÉPARÉE - Implémentation en attente.
    """
    
    def __init__(self, api_key: str):
        self.client = None  # EmergentIntegrations
        
    def generate_prompt(self, analysis: Dict) -> str:
        """Génère le prompt à partir des analyses."""
        pass
        
    def get_recommendations(self, analysis: Dict) -> str:
        """Obtient les recommandations de GPT-5.2."""
        pass
        
    def parse_response(self, response: str) -> List[str]:
        """Parse la réponse en liste de recommandations."""
        pass
```

---

## 📚 Données d'Entraînement

### Sources Prévues
1. **Données de récolte historiques** - MFFP
2. **Observations utilisateurs** - Base HUNTIQ
3. **Études télémétrie** - Universités QC
4. **Expert labeling** - Annotation manuelle

### Volume Estimé
| Dataset | Échantillons | Status |
|---------|--------------|--------|
| Corridors | 10,000+ segments | À collecter |
| Zones | 50,000+ patches | À collecter |
| Scores | 5,000+ territoires | À collecter |

### Format des Annotations
```json
{
  "sample_id": "COR_001",
  "bbox": [45.5, -73.5, 45.6, -73.4],
  "annotation_type": "corridor",
  "geometry": "LINESTRING(...)",
  "species": "deer",
  "confidence": 0.9,
  "annotator": "expert_01",
  "date": "2025-11-15"
}
```

---

## 🎯 Modèles Prévus

### 1. Corridor Predictor (U-Net)
- **Status:** Architecture définie
- **Entraînement:** À planifier
- **Précision cible:** IoU > 0.6

### 2. Zone Classifier (ResNet-50)
- **Status:** Architecture définie
- **Entraînement:** À planifier
- **Précision cible:** Accuracy > 0.85

### 3. Score Calculator (XGBoost)
- **Status:** Architecture définie
- **Entraînement:** À planifier
- **Précision cible:** R² > 0.8

### 4. GPT-5.2 Recommender
- **Status:** Intégration prête
- **API:** Emergent LLM Key
- **Qualité:** Évaluation humaine

---

## 🚀 Prochaines Étapes

1. **Phase 1:** Collecte de données d'entraînement
2. **Phase 2:** Entraînement modèle corridors
3. **Phase 3:** Entraînement modèle zones
4. **Phase 4:** Calibration modèle score
5. **Phase 5:** Intégration GPT-5.2
6. **Phase 6:** Validation terrain
7. **Phase 7:** Déploiement production

---

*BIONIC™ AI Pipelines - Architecture v1.0.0-alpha*
