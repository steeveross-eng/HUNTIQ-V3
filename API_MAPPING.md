# HUNTIQ V3 - API Mapping Documentation

## 📋 Vue d'ensemble

Ce document décrit le mapping complet entre les endpoints backend et les services/hooks frontend de HUNTIQ V3.

---

## 1. Architecture Modulaire

### Structure Backend
```
/app/backend/
├── server.py          # API endpoints FastAPI
├── analyzer.py        # BIONIC analysis logic
└── .env               # Configuration
```

### Structure Frontend Services
```
/app/frontend/src/services/
├── api.config.js      # Configuration API & endpoints
├── api.client.js      # Client HTTP axios centralisé
├── products.service.js
├── cart.service.js
├── analysis.service.js
├── territory.service.js
├── weather.service.js
├── admin.service.js
├── community.service.js
├── blog.service.js
├── partners.service.js
├── newsletter.service.js
└── index.js           # Export centralisé
```

### Structure Frontend Hooks
```
/app/frontend/src/hooks/
├── useProducts.js
├── useCart.js
├── useWeather.js
├── useCommunity.js
├── useBlog.js
├── usePartners.js
└── index.js           # Export centralisé
```

---

## 2. Mapping Endpoints ↔ Services

### Products Module

| Endpoint | Méthode | Service | Hook | Composant Frontend |
|----------|---------|---------|------|-------------------|
| `/api/products` | GET | `ProductsService.getAll()` | `useProducts()` | ShopPage, BionicHomePage |
| `/api/products/top` | GET | `ProductsService.getTop()` | `useProducts().topProducts` | ProductCarousel |
| `/api/products/{id}` | GET | `ProductsService.getById()` | `useProducts().getProduct()` | ProductDetails |
| `/api/products/search` | POST | `ProductsService.search()` | `useProducts().searchProducts()` | ShopPage |
| `/api/products/filter` | POST | `ProductsService.filter()` | `useProducts().filterProducts()` | ShopPage |
| `/api/products/brands` | GET | `ProductsService.getBrands()` | - | Filters |
| `/api/products/categories` | GET | `ProductsService.getCategories()` | - | Filters |
| `/api/products/filters/options` | GET | `ProductsService.getFilterOptions()` | - | Filters |

### Cart Module

| Endpoint | Méthode | Service | Hook | Composant Frontend |
|----------|---------|---------|------|-------------------|
| `/api/cart/{session_id}` | GET | `CartService.getItems()` | `useCart().cartItems` | CartSheet |
| `/api/cart` | POST | `CartService.addItem()` | `useCart().addToCart()` | ProductCarousel, ShopPage |
| `/api/cart/{item_id}` | PUT | `CartService.updateQuantity()` | `useCart().updateQuantity()` | CartSheet |
| `/api/cart/{item_id}` | DELETE | `CartService.removeItem()` | `useCart().removeItem()` | CartSheet |
| `/api/cart/session/{session_id}` | DELETE | `CartService.clearCart()` | `useCart().clearCart()` | CartSheet |

### Analysis Module

| Endpoint | Méthode | Service | Hook | Composant Frontend |
|----------|---------|---------|------|-------------------|
| `/api/analyze` | POST | `AnalysisService.analyze()` | - | AnalyzerModule |
| `/api/analyze/ai-advanced` | POST | `AnalysisService.analyzeAI()` | - | AnalyzerModule |
| `/api/analyze/criteria` | GET | `AnalysisService.getCriteria()` | - | AnalyzerModule |
| `/api/analyze/categories` | GET | `AnalysisService.getCategories()` | - | AnalyzerModule |
| `/api/analyze/references` | GET | `AnalysisService.getReferences()` | - | AnalyzerModule |
| `/api/analyze/bionic-products` | GET | `AnalysisService.getBionicProducts()` | - | AnalyzerModule |
| `/api/analyze/reports` | GET | `AnalysisService.getReports()` | - | AdminPage |

### Territory Module

| Endpoint | Méthode | Service | Hook | Composant Frontend |
|----------|---------|---------|------|-------------------|
| `/api/territory/categories` | GET | `TerritoryService.getCategories()` | - | TerritoryMap |
| `/api/territory/species-rules` | GET | `TerritoryService.getSpeciesRules()` | - | TerritoryMap |
| `/api/territory/probability` | POST | `TerritoryService.calculateProbability()` | - | MapModule |
| `/api/territory/heatmap` | POST | `TerritoryService.generateHeatmap()` | - | MapModule |
| `/api/territory/action-plan` | POST | `TerritoryService.createActionPlan()` | - | TerritoryAdvanced |
| `/api/territory/cameras` | GET/POST | `TerritoryService.getCameras()` | - | TerritoryInventory |
| `/api/territory/events` | GET/POST | `TerritoryService.getEvents()` | - | TerritoryMap |

### Weather Module (Simulated → OpenWeatherMap Ready)

| Source | Service | Hook | Composant Frontend |
|--------|---------|------|-------------------|
| Simulated/OpenWeatherMap | `WeatherService.getRegionWeather()` | `useWeather()` | WeatherModule |
| Simulated/OpenWeatherMap | `WeatherService.getForecast()` | `useWeather().forecast` | WeatherModule |
| Calculated | `WeatherService.calculateHuntingScore()` | `useWeather().huntingScore` | WeatherModule |

### Admin Module

| Endpoint | Méthode | Service | Hook | Composant Frontend |
|----------|---------|---------|------|-------------------|
| `/api/admin/login` | POST | `AdminService.login()` | - | AdminPage |
| `/api/admin/stats` | GET | `AdminService.getStats()` | - | AdminPage Dashboard |
| `/api/admin/products` | GET | `AdminService.getProducts()` | - | AdminPage Products |
| `/api/admin/products` | POST | `AdminService.createProduct()` | - | AdminPage Products |
| `/api/admin/products/{id}` | PUT | `AdminService.updateProduct()` | - | AdminPage Products |
| `/api/admin/products/{id}` | DELETE | `AdminService.deleteProduct()` | - | AdminPage Products |
| `/api/admin/reports/sales` | GET | `AdminService.getSalesReports()` | - | AdminPage Reports |
| `/api/admin/alerts` | GET | `AdminService.getAlerts()` | - | AdminPage |

### Community Module (Simulated → Backend Ready)

| Source | Service | Hook | Composant Frontend |
|--------|---------|------|-------------------|
| Simulated | `CommunityService.getPosts()` | `useCommunity().posts` | CommunitySection |
| Simulated | `CommunityService.getLeaderboard()` | `useCommunity().leaderboard` | CommunitySection |
| Simulated | `CommunityService.getStats()` | `useCommunity().stats` | CommunitySection |

### Blog Module (Simulated → Backend Ready)

| Source | Service | Hook | Composant Frontend |
|--------|---------|------|-------------------|
| Simulated | `BlogService.getArticles()` | `useBlog().articles` | BlogSection |
| Simulated | `BlogService.getFeaturedArticle()` | `useBlog().featuredArticle` | BlogSection |
| Simulated | `BlogService.getCategories()` | `useBlog().categories` | BlogSection |

### Partners Module (Simulated → Backend Ready)

| Source | Service | Hook | Composant Frontend |
|--------|---------|------|-------------------|
| Simulated | `PartnersService.getPartners()` | `usePartners().partners` | PartnersSection |
| Simulated | `PartnersService.getPourvoiries()` | `usePartners().pourvoiries` | PartnersSection |
| Simulated | `PartnersService.getFeaturedPourvoiries()` | `usePartners().featuredPourvoiries` | PartnersSection |

### Newsletter Module (Simulated → Backend Ready)

| Source | Service | Hook | Composant Frontend |
|--------|---------|------|-------------------|
| Simulated | `NewsletterService.subscribe()` | - | NewsletterSection |

---

## 3. Frontpage Sections → Data Sources

| Section | Composant | Service(s) | Status |
|---------|-----------|------------|--------|
| 1. Hero | HeroSection | Statique | ✅ Complet |
| 2. Carrousel Produits | ProductCarousel | ProductsService | ✅ Backend connecté |
| 3. Carte Interactive | MapModule | TerritoryService | ⚠️ Mapbox à configurer |
| 4. Météo | WeatherModule | WeatherService | ⚠️ OpenWeatherMap à configurer |
| 5-8. Bento Grid | BentoGridSection | Statique/Multiple | ✅ Complet |
| 9. Marketplace | MarketplaceSection | ProductsService | ✅ Backend connecté |
| 10-11. Media/Formations | MediaFormationsSection | BlogService | ⚠️ Données simulées |
| 12-13. Stats Live | LiveStatsSection | AdminService | ⚠️ Données simulées |
| 14. Partenaires | PartnersSection | PartnersService | ⚠️ Données simulées |
| 15. Blog | BlogSection | BlogService | ⚠️ Données simulées |
| 16. Communauté | CommunitySection | CommunityService | ⚠️ Données simulées |
| 17. App Mobile | MobileAppSection | Statique | ✅ Complet |
| 18. Newsletter | NewsletterSection | NewsletterService | ⚠️ Données simulées |
| 19. Footer | FooterSection | Statique | ✅ Complet |

---

## 4. Flux de Données

### Flux Panier (Cart Flow)
```
User Click → ProductCarousel/ShopPage
     ↓
CartService.addItem()
     ↓
POST /api/cart
     ↓
MongoDB cart_items collection
     ↓
useCart().fetchCart()
     ↓
CartSheet UI Updated
```

### Flux Analyse IA (AI Analysis Flow)
```
User Select Product → AnalyzerModule
     ↓
AnalysisService.analyzeAI({ product, species, season, weather })
     ↓
POST /api/analyze/ai-advanced
     ↓
Backend GPT-5.2 Integration
     ↓
Response with AI recommendations
     ↓
AnalyzerModule UI Updated
```

### Flux Météo (Weather Flow)
```
WeatherModule Mount
     ↓
WeatherService.getRegionWeather('laurentides')
     ↓
[OpenWeatherMap API if configured]
     ↓
[Simulated data fallback]
     ↓
Calculate hunting score
     ↓
WeatherModule UI Updated
```

---

## 5. Endpoints Backend Existants (75+)

### Catégorie: Products (8 endpoints)
- ✅ GET `/api/products`
- ✅ GET `/api/products/top`
- ✅ GET `/api/products/{id}`
- ✅ POST `/api/products`
- ✅ POST `/api/products/search`
- ✅ POST `/api/products/filter`
- ✅ GET `/api/products/brands`
- ✅ GET `/api/products/categories`

### Catégorie: Cart (5 endpoints)
- ✅ GET `/api/cart/{session_id}`
- ✅ POST `/api/cart`
- ✅ PUT `/api/cart/{item_id}`
- ✅ DELETE `/api/cart/{item_id}`
- ✅ DELETE `/api/cart/session/{session_id}`

### Catégorie: Analysis (8 endpoints)
- ✅ POST `/api/analyze`
- ✅ POST `/api/analyze/ai-advanced`
- ✅ GET `/api/analyze/criteria`
- ✅ GET `/api/analyze/categories`
- ✅ GET `/api/analyze/references`
- ✅ GET `/api/analyze/bionic-products`
- ✅ GET `/api/analyze/reports`
- ✅ GET `/api/analyze/reports/{id}`

### Catégorie: Territory (10 endpoints)
- ✅ GET `/api/territory/categories`
- ✅ GET `/api/territory/species-rules`
- ✅ POST `/api/territory/probability`
- ✅ POST `/api/territory/heatmap`
- ✅ POST `/api/territory/action-plan`
- ✅ GET `/api/territory/action-plans`
- ✅ GET/POST `/api/territory/cameras`
- ✅ GET/POST `/api/territory/events`
- ✅ POST `/api/territory/classify-photo`

### Catégorie: Admin (15+ endpoints)
- ✅ POST `/api/admin/login`
- ✅ GET `/api/admin/stats`
- ✅ GET/POST/PUT/DELETE `/api/admin/products`
- ✅ GET `/api/admin/reports/*`
- ✅ GET `/api/admin/alerts`

### Catégorie: Orders (5 endpoints)
- ✅ GET `/api/orders`
- ✅ GET `/api/orders/{id}`
- ✅ POST `/api/orders`
- ✅ PUT `/api/orders/{id}`
- ✅ POST `/api/orders/{id}/cancel`

### Catégorie: Referral (15+ endpoints)
- ✅ POST `/api/referral/calculate-discount`
- ✅ POST `/api/referral/apply-partner`
- ✅ GET/PUT `/api/referral/admin/tiers`
- ✅ CRUD `/api/referral/admin/promotions`
- ✅ GET `/api/referral/admin/partners`

---

## 6. Endpoints Backend Manquants (À Créer)

### Community Endpoints (Recommandé)
- `GET /api/community/posts`
- `POST /api/community/posts`
- `POST /api/community/posts/{id}/like`
- `POST /api/community/posts/{id}/comment`
- `GET /api/community/leaderboard`

### Blog Endpoints (Recommandé)
- `GET /api/blog/articles`
- `GET /api/blog/articles/{slug}`
- `GET /api/blog/categories`
- `GET /api/blog/articles/featured`

### Newsletter Endpoints (Recommandé)
- `POST /api/newsletter/subscribe`
- `POST /api/newsletter/unsubscribe`

### Partners Endpoints (Optionnel)
- `GET /api/partners`
- `GET /api/pourvoiries`
- `GET /api/pourvoiries/{id}`

---

## 7. Conformité Modulaire

### Règles Respectées ✅
1. Aucun appel axios direct dans les composants (via Services)
2. Configuration centralisée dans `api.config.js`
3. Client HTTP unique dans `api.client.js`
4. Services par domaine métier
5. Hooks pour la gestion d'état réactive
6. Index pour exports centralisés
7. data-testid sur tous les éléments interactifs

### Points d'Attention ⚠️
1. Certains services utilisent des données simulées (Community, Blog, Partners, Newsletter)
2. WeatherService prêt pour OpenWeatherMap mais utilise fallback
3. MapModule prêt pour Mapbox mais utilise placeholder

---

## 8. Résumé

| Métrique | Valeur |
|----------|--------|
| Endpoints Backend | 75+ |
| Services Frontend | 11 |
| Hooks Frontend | 15+ |
| Composants Frontpage | 14 |
| Endpoints avec service | 100% |
| Données simulées | 4 services |

---

*HUNTIQ V3 - Architecture Modulaire en Cascade*
*Généré le: $(date)*
