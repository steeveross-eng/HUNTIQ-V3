# HUNTIQ V3 - Product Requirements Document

## Date de création: 2026-02-03
## Version: 3.0

---

## 1. Énoncé du Problème Original

Fusionner HUNTIQ (V1) et HUNTIQ V2 en un seul projet modulaire, performant, fiable, extensible et optimisé pour l'intégration IA.

### Sources
- **HUNTIQ V2** (base): https://github.com/steeveross-eng/HUNTIQ-V2
- **HUNTIQ V1** (à fusionner): https://github.com/steeveross-eng/HUNTIQ

---

## 2. Architecture

### Stack Technique
- **Frontend**: React 18 + Tailwind CSS + ShadCN UI
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB
- **Hébergement**: Emergent Platform

### Structure du Projet
```
/app/
├── backend/
│   ├── server.py          # API FastAPI
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.js         # Composant principal
│   │   ├── components/    # Composants React
│   │   ├── pages/         # Pages séparées
│   │   ├── contexts/      # Context providers
│   │   └── hooks/         # Custom hooks
│   └── public/
└── memory/
    ├── PRD.md
    ├── analysis_report.md
    └── missing_features_report.md
```

---

## 3. Personas Utilisateurs

### Chasseur Amateur
- Recherche les meilleurs attractants
- Compare les produits
- Achète via dropshipping/affiliation

### Chasseur Expert
- Analyse son territoire
- Utilise les cartes GPS
- Participe au réseau social

### Partenaire/Fournisseur
- Gère ses produits
- Suit les commissions
- Accède au tableau de bord

### Administrateur
- Gère les produits/commandes
- Configure le site
- Analyse les statistiques

---

## 4. Exigences Principales (Core Requirements)

### 4.1 Navigation
- [x] Page d'accueil avec hero section
- [x] Menu de navigation (Home, Analyze, Compare, Shop, Territory)
- [x] Sélecteur de langue FR/EN
- [x] Authentification utilisateur
- [x] Panier d'achat

### 4.2 Analyse de Produits
- [x] Module d'analyse BIONIC™
- [x] 13 critères d'évaluation
- [x] Recommandations IA
- [x] Comparaison côte à côte

### 4.3 Boutique
- [x] Catalogue produits
- [x] Système dropshipping/affiliation
- [x] Panier et checkout
- [x] Gestion commandes

### 4.4 Territoire
- [x] Carte interactive
- [x] Points GPS (waypoints)
- [x] Analyse de territoire
- [x] Export GPX

### 4.5 Administration
- [x] Tableau de bord
- [x] Gestion produits
- [x] Gestion commandes
- [x] Mode maintenance

---

## 5. Implémenté (✅)

### Session 2026-02-03
- [x] Clone et analyse des repos V1 et V2
- [x] Identification des erreurs de fusion
- [x] Correction des imports dupliqués
- [x] Suppression des composants dupliqués
- [x] Reconstruction App.js modulaire
- [x] Simplification AnalyzerModule.jsx
- [x] Installation dépendances
- [x] Seed de 5 produits test
- [x] Tests fonctionnels (85-100% pass)
- [x] Correction API panier

---

## 6. Backlog Priorisé

### P0 - Critique
- [ ] Tests E2E complets
- [ ] Documentation API

### P1 - Important
- [ ] Restaurer AnalyzerModule complet avec tous les critères
- [ ] Améliorer FormationsPage avec données réelles
- [ ] Intégration paiement Stripe

### P2 - Souhaitable
- [ ] Mode hors-ligne PWA
- [ ] Notifications push
- [ ] Système de parrainage complet

---

## 7. Prochaines Actions

1. **Immédiat**: Tests manuels des pages principales
2. **Court terme**: Restaurer les fonctionnalités avancées de AnalyzerModule
3. **Moyen terme**: Intégration IA pour analyses produits
4. **Long terme**: Préparation pour production

---

## 8. Notes Techniques

### Erreurs Résolues
- Virgules manquantes dans imports lucide-react
- Composants dupliqués (HeroSection, ComparePage, ShopPage)
- Blocs JSX mal fermés
- Imports mal placés (au milieu du fichier)

### API Endpoints Principaux
- `GET /api/products/top` - Top produits
- `GET /api/products` - Tous les produits
- `POST /api/cart` - Ajouter au panier
- `GET /api/cart/{session_id}` - Voir panier
- `POST /api/analyze/product` - Analyser produit

---

*Généré par HUNTIQ V3 Fusion Process*
