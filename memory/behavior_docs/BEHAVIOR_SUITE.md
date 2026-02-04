# BIONIC™ Behavior Suite - Documentation

## Vue d'ensemble

La Behavior Suite est un ensemble de 6 moteurs d'intelligence faunique qui analysent le comportement animal pour optimiser les stratégies de chasse.

## Architecture

```
/app/bionic/engines/behavior/
├── __init__.py              # Exports principaux
├── models/
│   └── schemas.py           # Modèles Pydantic (Input/Output)
├── core/
│   ├── behavior_engine.py           # Analyse comportementale globale
│   ├── seasonal_attractiveness_engine.py  # Attractivité saisonnière
│   ├── activity_probability_engine.py     # Probabilité d'activité
│   ├── rut_prediction_engine.py           # Prédiction du rut
│   ├── movement_engine.py                 # Analyse des mouvements
│   └── species_model_engine.py            # Modèle par espèce
└── api/
    └── endpoints.py         # Endpoints FastAPI
```

## Moteurs

### 1. Behavior Engine
**Endpoint:** `GET /api/bionic/behavior/analyze`

Analyse le comportement animal global en fonction des conditions environnementales.

**Paramètres:**
- `lat`, `lon`: Coordonnées
- `species`: Espèce cible (deer, moose, bear, etc.)
- `temperature_c`, `precipitation_mm`, `wind_speed_kmh`: Météo
- `moon_phase`: Phase lunaire (0-1)

**Output:**
- Score d'activité global (0-100)
- Score d'opportunité de chasse
- Fenêtres d'activité optimales
- Recommandations

### 2. Seasonal Attractiveness Engine
**Endpoint:** `GET /api/bionic/behavior/seasonal`

Analyse l'attractivité saisonnière de l'habitat.

**Output:**
- Phase saisonnière actuelle
- Scores d'attractivité (nourriture, couvert, eau, thermique)
- Hotspots identifiés
- Tendance et meilleurs jours

### 3. Activity Probability Engine
**Endpoint:** `GET /api/bionic/behavior/activity`

Calcule la probabilité d'activité animale heure par heure.

**Output:**
- Probabilité d'activité (0-1)
- Probabilités horaires (24h)
- Fenêtre optimale
- Facteurs d'influence (météo, lunaire, saisonnier)

### 4. Rut Prediction Engine
**Endpoint:** `GET /api/bionic/behavior/rut`

Prédit les phases et le timing du rut pour les cervidés.

**Output:**
- Phase actuelle (pré-rut, seeking, breeding, post-rut)
- Dates clés (début, pic, fin)
- Comportements attendus
- Tactiques recommandées
- Meilleurs moments pour les appels

### 5. Movement Engine
**Endpoint:** `GET /api/bionic/behavior/movement`

Analyse les patterns de déplacement et corridors.

**Output:**
- Pattern de mouvement actuel
- Home range estimé (km²)
- Corridors de déplacement
- Zones de repos/alimentation
- Positions probables

### 6. Species Model Engine
**Endpoint:** `GET /api/bionic/behavior/species-model`

Fournit une analyse complète spécifique à l'espèce.

**Output:**
- Profil détaillé de l'espèce
- Compatibilité habitat
- Comportement saisonnier
- Tactiques optimales
- Équipement recommandé

## Endpoint Combiné

### Full Behavior Suite Analysis
**Endpoint:** `GET /api/bionic/behavior/full`

Exécute tous les moteurs en parallèle et agrège les résultats.

**Paramètres:**
- Coordonnées et espèce
- Flags pour inclure/exclure chaque moteur

**Output:**
```json
{
  "suite_version": "1.0.0",
  "global_opportunity_score": 61.5,
  "engines_executed": ["behavior", "seasonal", "activity", "rut", "movement", "species_model"],
  "processing_time_ms": 0,
  "top_recommendations": [...],
  "hotspots": [...]
}
```

## Espèces Supportées

| Code | Nom FR | Nom EN |
|------|--------|--------|
| `deer` | Cerf de Virginie | White-tailed Deer |
| `moose` | Orignal | Moose |
| `bear` | Ours noir | Black Bear |
| `caribou` | Caribou | Caribou |
| `wolf` | Loup | Wolf |
| `turkey` | Dindon sauvage | Wild Turkey |
| `waterfowl` | Sauvagine | Waterfowl |
| `smallgame` | Petit gibier | Small Game |

## Phases Saisonnières

1. **Winter Survival** - Survie hivernale (ravages)
2. **Spring Dispersal** - Dispersion printanière
3. **Summer Foraging** - Alimentation estivale
4. **Pre-Rut Preparation** - Préparation au rut
5. **Rut Active** - Rut actif
6. **Post-Rut Recovery** - Récupération post-rut
7. **Fall Preparation** - Préparation automnale (hyperphagie)

## Phases du Rut

1. **Pre-Rut** - Marquage territorial, hiérarchie
2. **Seeking** - Recherche des femelles
3. **Chasing** - Poursuite active
4. **Breeding** - Reproduction (pic)
5. **Post-Rut** - Recherche des retardataires
6. **Recovery** - Repos et récupération

## Utilisation Frontend

```javascript
import { useBionicEngines } from '@/hooks/useBionicEngines';

const MyComponent = () => {
  const { fetchRealDataAnalysis } = useBionicEngines();
  
  const handleFullAnalysis = async (lat, lon, species) => {
    // Appel à l'analyse comportementale complète
    const response = await fetch(
      `${API_URL}/api/bionic/behavior/full?lat=${lat}&lon=${lon}&species=${species}`
    );
    const data = await response.json();
    console.log('Score opportunité:', data.global_opportunity_score);
  };
};
```

## Prochaines Étapes (P0-2)

### Données Réelles
- Intégration météo temps réel (Open-Meteo)
- Calcul précis phase lunaire
- Données de pression barométrique

### Modèles ML
- Entraînement sur données de télémétrie
- Calibration avec données de récolte Québec
- Modèles prédictifs 24h/72h/7j

### Intégration
- Connexion avec Sentinel Engine (NDVI)
- Connexion avec SIGÉOM Engine (géologie)
- Visualisation sur carte (hotspots, corridors)

---

*BIONIC™ Behavior Suite v1.0.0 - P0 Étape 1 (Fondations)*
*Février 2026*
