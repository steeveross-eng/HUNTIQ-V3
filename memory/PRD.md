# HUNTIQ V3 - Product Requirements Document

## Date de mise à jour: 2026-02-13
## Version: 3.3 (Modules Freemium, Onboarding, Tutorials)

---

## 1. Énoncé du Problème Original

Intégration et complétion de HUNTIQ V3 - Plateforme premium pour chasseurs, gestionnaires de territoires et utilisateurs de caméras de chasse.

### Sources
- **Repository GitHub**: https://github.com/steeveross-eng/HUNTIQ-V3
- **Plateforme Emergent**: Pod d'intégration

---

## 2. Architecture

### Stack Technique
- **Frontend**: React 18 + Tailwind CSS + ShadCN UI + Leaflet Maps
- **Backend**: FastAPI (Python) avec modules multiples
- **Base de données**: MongoDB
- **Paiements**: Stripe (via emergentintegrations)
- **Hébergement**: Emergent Platform

### Structure Backend
```
/app/backend/
├── server.py          # Serveur principal FastAPI
├── payments.py        # Payment Engine (Stripe)
├── analyzer.py        # Module d'analyse BIONIC™
├── marketplace.py     # Hunt Marketplace
├── territories.py     # Gestion territoires
├── user_auth.py       # Authentification
├── networking.py      # Module réseau
├── referral_system.py # Système de parrainage
├── lands_rental.py    # Location de terres
└── ...
```

---

## 3. Fonctionnalités Implémentées ✅

### 3.1 Modules Core
- ✅ Authentification (inscription/connexion/réinitialisation)
- ✅ Gestion des utilisateurs et profils
- ✅ Cookie Consent / GDPR compliance
- ✅ Maintenance Mode

### 3.2 AnalyzerModule BIONIC™
- ✅ 13 critères d'évaluation pondérés
- ✅ Analyse IA avancée (GPT-5.2)
- ✅ Comparaison de produits
- ✅ Scoring scientifique

### 3.3 Hunt Marketplace
- ✅ Listings (vente, location, échange)
- ✅ Filtres et recherche avancée
- ✅ Favoris et notifications
- ✅ Système de messagerie

### 3.4 Territory Module
- ✅ Carte interactive (Leaflet)
- ✅ Données géospatiales Québec
- ✅ Zones de chasse

### 3.5 Formations
- ✅ Formations FédéCP officielles
- ✅ Formations BIONIC™ exclusives
- ✅ Types de territoires Québec

### 3.6 Payment Engine (Phase 13) ✅ COMPLÉTÉ
- ✅ Stripe Checkout intégré
- ✅ Tarifs PRO validés:
  - PRO Mensuel: 7.99 CAD (essai 7 jours)
  - PRO Annuel: 79.00 CAD (essai 7 jours)
  - PRO À Vie: 199.00 CAD
- ✅ Packages Marketplace (featured, auto-bump, renewal)
- ✅ Webhooks Stripe
- ✅ Pages Success/Cancel

### 3.7 Freemium Engine ✅ COMPLÉTÉ
- ✅ Quotas FREE validés:
  - Marketplace: 2 annonces (infos vendeur floutées)
  - Analyzer IA: 1 analyse/semaine (résultats partiels)
  - Territoires: 1
  - Waypoints: 2
  - Hotspots import: 1
  - Notifications: météo générale
- ✅ PRO = illimité + outils avancés
- ✅ API /api/freemium/* (quotas, check, use, upgrade, status)

### 3.8 Onboarding Engine ✅ COMPLÉTÉ
- ✅ 5 étapes: welcome, profile, preferences, features, complete
- ✅ Profil chasseur: espèces, région, expérience, objectifs
- ✅ Préférences: langue, notifications (météo, activité, news)
- ✅ Tour des fonctionnalités (Analyzer, Territory, Marketplace, PRO)
- ✅ 8 espèces cibles, 16 régions Québec, 4 niveaux d'expérience

### 3.9 Tutoriels Interactifs ✅ COMPLÉTÉ
- ✅ 3 tutoriels core:
  - Analyzer BIONIC™ (5 étapes)
  - Territory Map (6 étapes)
  - Marketplace (6 étapes)
- ✅ Système de progression persistant
- ✅ Types d'étapes: info, action, warning, completion
- ✅ Confidentialité hotspots intégrée dans tutoriels

### 3.10 Networking Hub
- ✅ Guides et pourvoyeurs
- ✅ Système de parrainage
- ✅ Partenariats

---

## 4. Tests Passés ✅

### Backend (96%)
- API root endpoint
- Payment packages (PRO pricing correct)
- Products endpoint
- Admin statistics
- Marketplace categories/listings
- Suppliers, customers, orders, commissions
- **Freemium Engine** (quotas, check, status, user)
- **Onboarding Engine** (config, progress, step complete)
- **Tutorials Engine** (list, detail, progress)

### Frontend (85%)
- Homepage navigation
- Analyze page (13 critères BIONIC™)
- Shop page
- Territory page
- Formations page
- Cart functionality
- Cookie consent
- Composants Freemium/Onboarding/Tutorials (conditionnels)

---

## 5. Backlog & Préparation Audit

### P0 - Critique (Pré-Audit)
- [x] Payment Engine Phase 13 complété
- [ ] Tests terrain offline (à valider)

### P1 - Important
- [ ] Onboarding Engine complet
- [ ] Tutoriels interactifs
- [ ] Freemium Engine (quotas, badges, modals)
- [ ] Analytics Dashboard complet

### P2 - Souhaitable
- [ ] Mode hors-ligne
- [ ] Export PDF des analyses
- [ ] Historique des analyses utilisateur

---

## 6. Configuration Environnement

### Variables Backend (.env)
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
STRIPE_API_KEY=sk_test_emergent
```

### Variables Frontend (.env)
```
REACT_APP_BACKEND_URL=https://global-audit-v3.preview.emergentagent.com
```

---

## 7. URLs & Accès

- **Preview**: https://global-audit-v3.preview.emergentagent.com
- **API**: https://global-audit-v3.preview.emergentagent.com/api

---

## 8. Prochaines Étapes

1. Compléter les modules Onboarding, Tutoriels, Freemium
2. Audit Global complet
3. Tests terrain et offline
4. Stabilisation finale
5. GO-LIVE (après validation exécutive)

---

*HUNTIQ V3 - Powered by Emergent Platform*
*Phase 13 Payment Engine - COMPLÉTÉ*
