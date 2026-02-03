# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Version: 3.1 (avec IA GPT-5.2)

---

## 1. Énoncé du Problème Original

Fusionner HUNTIQ V1 et V2 + Intégrer l'IA GPT-5.2 pour l'analyse d'attractants.

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

---

## 3. Fonctionnalités Implémentées ✅

### 3.1 AnalyzerModule BIONIC™ Complet
- **13 Critères d'Évaluation** pondérés scientifiquement
  1. Durée d'attraction (15%)
  2. Appétence naturelle (12%)
  3. Puissance olfactive (12%)
  4. Persistance (10%)
  5. Nutrition (10%)
  6. Composés comportementaux (10%)
  7. Résistance intempéries (8%)
  8. Sécurité alimentaire (7%)
  9. Certification ACIA (6%)
  10. Résistance physique (4%)
  11. Pureté ingrédients (3%)
  12. Fidélisation (2%)
  13. Stabilité chimique (1%)

### 3.2 Analyse IA GPT-5.2
- **Paramètres personnalisables**:
  - Espèce cible (cerf, orignal, ours, sanglier, dindon)
  - Saison (printemps, été, automne/rut, hiver)
  - Conditions météo (froid, normal, chaud, pluie, neige)
  - Type de terrain (forêt, champ, marais, montagne)
- **Résultats**: Score, recommandation, meilleur moment, conseils d'application, produits alternatifs, base scientifique

### 3.3 FormationsPage FédéCP & BIONIC™
**Formations FédéCP officielles:**
1. Initiation chasse avec arme à feu (Obligatoire, 8h, ~75$)
2. Initiation chasse à l'arc (Obligatoire arc/arbalète, 4h, ~50$)
3. Formation au piégeage (Obligatoire, 8h, ~60$)
4. Formation chasse à l'orignal (Facultatif, 4h, ~40$)

**Formations BIONIC™ exclusives:**
1. Analyse de territoire BIONIC™
2. Science des attractants
3. Météo et mouvement du gibier

**Types de Territoires au Québec:**
1. Terres publiques (MFFP)
2. ZEC (Zones d'exploitation contrôlée)
3. Pourvoiries (privées avec services)
4. Réserves fauniques (SÉPAQ)
5. Terres privées

---

## 4. APIs Développées

### Endpoints d'Analyse
- `POST /api/analyze` - Analyse standard
- `POST /api/analyze/ai-advanced` - Analyse IA GPT-5.2
- `GET /api/analyze/criteria` - Liste des 13 critères
- `GET /api/analyze/references` - Références scientifiques

### Endpoints Produits
- `GET /api/products/top` - Top produits
- `POST /api/products` - Créer produit
- `GET /api/cart/{session_id}` - Voir panier

---

### 3.4 Module Administration (18 onglets)
**Accès:** Icône cadenas dans la navigation (à droite du sélecteur de langue)
**URL:** `/admin`
**Mot de passe:** `Saturn5858*` (⚠️ À déplacer dans .env)

**Onglets disponibles:**
1. Tableau de bord - Vue d'ensemble
2. Ventes - Gestion des ventes
3. Produits - CRUD produits
4. Partenaires - Gestion partenaires
5. Clients - Base clients
6. Commissions - Calcul commissions
7. Performances - Analytics
8. Catégories - Gestion catégories
9. Contenu SEO - Optimisation SEO
10. BACKUP - Sauvegarde données
11. Accès Site - Contrôle d'accès
12. Terres à louer - Gestion locations
13. Réseautage - Module networking
14. Email - Gestion emails
15. Marketing - Outils marketing
16. Partenaires (2) - Détails partenaires
17. Contrôles - Paramètres système
18. Identité - Branding

---

## 5. Backlog Restant

### P0 - Critique
- [x] ~~Tests fonctionnels~~ ✅ Complétés
- [x] ~~Module Admin accessible depuis UI~~ ✅ (Icône cadenas dans navigation)

### P1 - Important
- [x] ~~Sécuriser mot de passe admin~~ ✅ (déplacé dans .env)
- [ ] Optimiser temps de réponse IA (caching)
- [ ] Ajouter plus d'espèces (faisan, lièvre, etc.)
- [ ] Export PDF des analyses

### P2 - Souhaitable
- [ ] Historique des analyses utilisateur
- [ ] Comparaison multi-produits IA
- [ ] Mode hors-ligne

---

## 6. Configuration

### Variables d'environnement Backend
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
EMERGENT_LLM_KEY="sk-emergent-xxxx"
```

---

*HUNTIQ V3 - Powered by GPT-5.2 & Emergent Platform*
