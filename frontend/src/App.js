import { useEffect, useState, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import AnalyzerModule from "@/components/AnalyzerModule";
import TerritoryMap from "@/components/TerritoryMap";
import HuntMarketplace from "@/components/HuntMarketplace";
import CookieConsent from "@/components/CookieConsent";
import SEOHead from "@/components/SEOHead";
import ContentDepot from "@/components/ContentDepot";
import SiteAccessControl from "@/components/SiteAccessControl";
import MaintenancePage from "@/components/MaintenancePage";
import LandsRental from "@/components/LandsRental";
import LandsPricingAdmin from "@/components/LandsPricingAdmin";
import NetworkingHub from "@/components/NetworkingHub";
import NetworkingAdmin from "@/components/NetworkingAdmin";
import NotificationCenter from "@/components/NotificationCenter";
import EmailAdmin from "@/components/EmailAdmin";
import FeatureControlsAdmin from "@/components/FeatureControlsAdmin";
import ResetPasswordPage from "@/components/ResetPasswordPage";
import AdminPage from "@/pages/AdminPage";
import { AuthProvider, UserMenu, useAuth } from "@/components/GlobalAuth";
import { LanguageProvider, useLanguage, LanguageSwitcher } from "@/contexts/LanguageContext";
import BionicLogo from "@/components/BionicLogo";
import ScrollNavigator from "@/components/ScrollNavigator";
import BecomePartner from "@/components/BecomePartner";
import PartnerDashboard from "@/components/PartnerDashboard";
import MonTerritoireBionic from "@/components/territoire/MonTerritoireBionic";
import MonTerritoireBionicPage from "@/pages/MonTerritoireBionicPage";
import ProductDiscoveryAdmin from "@/components/ProductDiscoveryAdmin";
import ReferralModule from "@/components/ReferralModule";
import ReferralAdminPanel from "@/components/ReferralAdminPanel";
import DynamicReferralWidget from "@/components/DynamicReferralWidget";
import { ShopPage, ComparePage } from "@/pages";
import DashboardPage from "@/pages/DashboardPage";
import BusinessPage from "@/pages/BusinessPage";
import PlanMaitrePage from "@/pages/PlanMaitrePage";
import { NotificationProvider } from "@/modules/notifications";
import { 
  ShoppingCart, FlaskConical, GitCompare, Star, DollarSign, ThumbsUp, Heart, Eye,
  Shield, MousePointer, TrendingUp, CheckCircle, ChevronRight, Menu, X, ArrowLeft,
  Package, Users, Store, Percent, BarChart3, Award, Info, Lock, Clock, AlertTriangle,
  ExternalLink, Trash2, Edit, Plus, Loader2, GraduationCap, BookOpen, Brain,
  Map, Globe, Construction, Power, Mail, Handshake, XCircle, Moon, Sun, Bot,
  Radar, Share2, Gift
} from "lucide-react";
import {
  Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle
} from "@/components/ui/sheet";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Progress } from "@/components/ui/progress";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Session ID helper
const getSessionId = () => {
  let sessionId = localStorage.getItem("session_id");
  if (!sessionId) {
    sessionId = "sess_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("session_id", sessionId);
  }
  return sessionId;
};

// Logo Component
const Logo = ({ size = "default" }) => {
  const { brand } = useLanguage();
  return (
    <div className={`flex items-center gap-2 ${size === "large" ? "scale-125" : ""}`}>
      <BionicLogo className={size === "large" ? "h-10 w-10" : "h-8 w-8"} />
      <span className={`font-bold text-white ${size === "large" ? "text-2xl" : "text-xl"}`}>
        {brand.short}
      </span>
    </div>
  );
};

// Navigation Component
const Navigation = ({ cartCount, onCartOpen }) => {
  const { t } = useLanguage();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/90 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <Logo />
        </Link>
        <nav className="hidden md:flex items-center gap-4">
          <Link to="/" className="text-gray-400 hover:text-white transition-colors">{t('nav_home')}</Link>
          <Link to="/dashboard" className="text-[#f5a623] hover:text-[#d4890e] transition-colors font-medium" data-testid="nav-dashboard">Dashboard</Link>
          <Link to="/business" className="text-purple-400 hover:text-purple-300 transition-colors font-medium" data-testid="nav-business">Business</Link>
          <Link to="/plan-maitre" className="text-emerald-400 hover:text-emerald-300 transition-colors font-medium" data-testid="nav-plan-maitre">Plan Maître</Link>
          <Link to="/analyze" className="text-gray-400 hover:text-white transition-colors">{t('nav_analyze')}</Link>
          <Link to="/shop" className="text-gray-400 hover:text-white transition-colors">{t('nav_shop')}</Link>
          <Link to="/territoire" className="text-gray-400 hover:text-white transition-colors">{t('nav_territory')}</Link>
        </nav>
        <div className="flex items-center gap-4">
          <LanguageSwitcher />
          {/* Admin Link */}
          <Link to="/admin">
            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-[#f5a623]" data-testid="admin-link">
              <Lock className="h-4 w-4" />
            </Button>
          </Link>
          <UserMenu />
          <Button variant="outline" onClick={onCartOpen} className="relative" data-testid="cart-button">
            <ShoppingCart className="h-5 w-5" />
            {cartCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-[#f5a623] text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                {cartCount}
              </span>
            )}
          </Button>
          <button className="md:hidden text-white" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>
    </header>
  );
};

// Footer Component
const Footer = () => (
  <footer className="bg-black py-8 border-t border-border">
    <div className="max-w-7xl mx-auto px-4 text-center">
      <p className="text-gray-400">© 2024 HUNTIQ - Chasse BIONIC™</p>
    </div>
  </footer>
);

// HeroSection Component
const HeroSection = () => {
  const { t, brand } = useLanguage();
  return (
    <section className="hero-bg min-h-screen flex flex-col items-center justify-center text-center px-4 pt-24" data-testid="hero-section">
      <h1 className="text-4xl md:text-5xl golden-text font-bold mb-8 max-w-4xl leading-tight">
        {brand.tagline}
      </h1>
      <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
        <Link to="/analyze">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <FlaskConical className="h-5 w-5" /> {t('nav_analyze')}
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/compare">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <GitCompare className="h-5 w-5" /> {t('nav_compare')}
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/shop">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" /> {t('hero_order')}
          </Button>
        </Link>
      </div>
      <div className="max-w-3xl mx-auto space-y-4">
        <p className="text-gray-300">{t('hero_description')}</p>
        <p className="text-[#f5a623] font-medium">{t('hero_highlight')}</p>
        <p className="text-[#f5a623] font-semibold text-xl mt-6">{brand.slogan}</p>
      </div>
    </section>
  );
};

// ProductCard Component
const ProductCard = ({ product, onAddToCart }) => (
  <Card className="product-card bg-card border-border overflow-hidden" data-testid={`product-card-${product.rank}`}>
    <div className="relative">
      <div className="absolute top-3 left-3 z-10">
        <Badge className="rank-badge text-white font-bold px-3 py-1">#{product.rank}</Badge>
      </div>
      <img src={product.image_url} alt={product.name} className="w-full aspect-square object-cover" />
    </div>
    <CardContent className="p-4">
      <p className="text-[#f5a623] text-sm">{product.brand}</p>
      <h3 className="text-white font-semibold mb-2 truncate">{product.name}</h3>
      <div className="flex items-center gap-2 mb-4">
        <Badge className="bg-[#f5a623] text-black">Score: {product.score}</Badge>
      </div>
      <p className="text-[#f5a623] font-bold text-xl mb-4">${product.price}</p>
      <Button className="w-full btn-golden text-black font-semibold" onClick={() => onAddToCart(product)}>
        <ShoppingCart className="h-4 w-4 mr-2" /> Ajouter
      </Button>
    </CardContent>
  </Card>
);

// ProductsSection Component
const ProductsSection = ({ products, onAddToCart }) => {
  const { t, brand } = useLanguage();
  return (
    <section className="py-16 px-4 bg-background" data-testid="products-section">
      <div className="max-w-7xl mx-auto">
        <h2 className="golden-text text-3xl md:text-4xl font-bold text-center mb-8 italic">
          {t('page_best_choices')} {brand.short}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} />
          ))}
        </div>
      </div>
    </section>
  );
};

// FeaturesSection Component
const FeaturesSection = () => {
  const { t } = useLanguage();
  const features = [
    { icon: FlaskConical, titleKey: "nav_analyze", descKey: "feature_analyze_desc" },
    { icon: GitCompare, titleKey: "nav_compare", descKey: "feature_compare_desc" },
    { icon: ShoppingCart, titleKey: "hero_order", descKey: "feature_order_desc" },
  ];
  return (
    <section className="py-16 px-4 bg-black/50" data-testid="features-section">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="feature-card rounded-xl p-8 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                <feature.icon className="h-8 w-8 text-[#f5a623]" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{t(feature.titleKey)}</h3>
              <p className="text-gray-400">{t(feature.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// CartSheet Component
const CartSheet = ({ isOpen, onOpenChange, cartItems, onUpdateQuantity, onRemoveItem }) => {
  const { t } = useLanguage();
  const total = cartItems.reduce((sum, item) => sum + (item.product?.price || 0) * item.quantity, 0);
  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="text-white flex items-center gap-2">
            <ShoppingCart className="h-5 w-5 text-[#f5a623]" /> {t('nav_cart')}
          </SheetTitle>
        </SheetHeader>
        <div className="mt-6 space-y-4 flex-1 overflow-auto">
          {cartItems.length === 0 ? (
            <p className="text-gray-400 text-center py-8">{t('cart_empty')}</p>
          ) : (
            cartItems.map((item) => (
              <div key={item.id} className="flex items-center gap-4 p-4 bg-background rounded-lg">
                <img src={item.product?.image_url} alt={item.product?.name} className="w-16 h-16 object-cover rounded" />
                <div className="flex-1">
                  <p className="text-white font-medium">{item.product?.name}</p>
                  <p className="text-[#f5a623]">${item.product?.price}</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => onRemoveItem(item.id)}>
                  <Trash2 className="h-4 w-4 text-red-400" />
                </Button>
              </div>
            ))
          )}
        </div>
        {cartItems.length > 0 && (
          <div className="border-t border-border pt-4 mt-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-white font-medium">Total</span>
              <span className="text-[#f5a623] text-xl font-bold">${total.toFixed(2)}</span>
            </div>
            <Button className="w-full btn-golden text-black font-semibold">{t('cart_checkout')}</Button>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
};

// HomePage Component
const HomePage = ({ products, onAddToCart }) => (
  <main>
    <HeroSection />
    <ProductsSection products={products} onAddToCart={onAddToCart} />
    <FeaturesSection />
  </main>
);

// AnalyzePage Component
const AnalyzePage = ({ products }) => (
  <main className="pt-20 min-h-screen bg-background">
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="golden-text text-4xl font-bold mb-4">Analysez</h1>
      <p className="text-gray-400 mb-8">Analysez en profondeur chaque attractant avec nos critères scientifiques.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <Card key={product.id} className="bg-card border-border p-6">
            <div className="flex items-start gap-4">
              <img src={product.image_url} alt={product.name} className="w-24 h-24 object-cover rounded-lg" />
              <div className="flex-1">
                <p className="text-[#f5a623] text-sm">{product.brand}</p>
                <h3 className="text-white font-semibold mb-2">{product.name}</h3>
                <Badge className="bg-[#f5a623]">Score: {product.score}</Badge>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  </main>
);

// TerritoryPage Component
const TerritoryPage = () => (
  <main className="pt-16 min-h-screen bg-background">
    <MonTerritoireBionicPage />
  </main>
);

// MarketplacePage Component
const MarketplacePage = () => (
  <main className="pt-16 min-h-screen bg-background">
    <HuntMarketplace />
  </main>
);

// FormationsPage Component
const FormationsPage = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  
  // Formations FédéCP officielles
  const fedecpFormations = [
    {
      id: "securite",
      title: "Initiation à la chasse avec arme à feu",
      description: "Formation obligatoire pour obtenir le certificat du chasseur au Québec",
      icon: "🔫",
      duration: "8 heures (2 jours)",
      type: "Obligatoire",
      price: "Environ 75$",
      link: "https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/",
      topics: ["Sécurité et manipulation des armes", "Réglementation provinciale", "Éthique de chasse", "Identification du gibier", "Examen théorique et pratique"]
    },
    {
      id: "arc",
      title: "Initiation à la chasse à l'arc",
      description: "Formation pour la chasse à l'arc et à l'arbalète",
      icon: "🏹",
      duration: "4 heures",
      type: "Obligatoire pour arc/arbalète",
      price: "Environ 50$",
      link: "https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/",
      topics: ["Sécurité avec arc et arbalète", "Choix de l'équipement", "Techniques de tir", "Réglementation spécifique"]
    },
    {
      id: "piegeage",
      title: "Formation au piégeage",
      description: "Cours obligatoire pour obtenir le certificat de piégeur",
      icon: "🪤",
      duration: "8 heures",
      type: "Obligatoire",
      price: "Environ 60$",
      link: "https://fedecp.com/le-piegeage/formation-au-piegeage/",
      topics: ["Réglementation sur le piégeage", "Types de pièges autorisés", "Éthique et bien-être animal", "Techniques de capture", "Traitement des fourrures"]
    },
    {
      id: "orignal",
      title: "Formation chasse à l'orignal",
      description: "Techniques avancées pour la chasse au roi de nos forêts",
      icon: "🫎",
      duration: "4 heures",
      type: "Facultatif",
      price: "Environ 40$",
      link: "https://fedecp.com/la-chasse/orignal/",
      topics: ["Comportement de l'orignal", "Appels et leurres", "Stratégies de chasse", "Débitage et conservation"]
    }
  ];
  
  // Formations BIONIC™ exclusives
  const bionicFormations = [
    {
      id: "analyse-territoire",
      title: "Analyse de territoire BIONIC™",
      description: "Maîtrisez les outils d'analyse GPS et cartographique pour optimiser votre territoire de chasse",
      icon: "🗺️",
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Lecture de cartes topographiques", "Identification des corridors", "Placement stratégique des caches", "Analyse des points d'eau"]
    },
    {
      id: "attractants",
      title: "Science des attractants",
      description: "Comprenez la chimie et la biologie derrière les leurres et attractants",
      icon: "🧪",
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Composés olfactifs", "Phéromones et comportement", "Timing et application", "13 critères d'évaluation"]
    },
    {
      id: "meteo",
      title: "Météo et mouvement du gibier",
      description: "Apprenez à prédire le comportement du gibier selon les conditions météo",
      icon: "🌤️",
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Pression atmosphérique", "Phases lunaires", "Front météo et activité", "Prévisions optimales"]
    }
  ];
  
  // Types de territoires au Québec
  const territoireTypes = [
    {
      type: "Terres publiques",
      description: "Territoires libres gérés par le MFFP",
      color: "#22c55e",
      features: ["Accès gratuit avec permis", "Tirage au sort pour certaines zones", "Règles de capacité de support"]
    },
    {
      type: "ZEC",
      description: "Zones d'exploitation contrôlée",
      color: "#3b82f6",
      features: ["Droit d'accès requis", "Gestion par associations", "Quotas et enregistrement obligatoire"]
    },
    {
      type: "Pourvoiries",
      description: "Territoires privés avec services",
      color: "#f59e0b",
      features: ["Hébergement et guidage", "Droits exclusifs", "Forfaits tout inclus"]
    },
    {
      type: "Réserves fauniques",
      description: "Territoires protégés par la SÉPAQ",
      color: "#8b5cf6",
      features: ["Réservation obligatoire", "Secteurs contingentés", "Haute qualité de chasse"]
    },
    {
      type: "Terres privées",
      description: "Propriétés privées avec permission",
      color: "#ef4444",
      features: ["Autorisation du propriétaire", "Ententes de chasse", "Location possible"]
    }
  ];

  return (
    <main className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-formations"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>
        
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <GraduationCap className="h-8 w-8 text-[#f5a623]" />
              Centre de Formations
            </h1>
            <p className="text-gray-400">FédéCP & BIONIC™ - Devenez un chasseur expert</p>
          </div>
        </div>

        {/* FédéCP Section */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <BookOpen className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Formations FédéCP officielles</h2>
              <p className="text-gray-400 text-sm">Fédération québécoise des chasseurs et pêcheurs</p>
            </div>
            <a 
              href="https://fedecp.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="ml-auto"
            >
              <Badge className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 cursor-pointer">
                <ExternalLink className="h-3 w-3 mr-1" /> fedecp.com
              </Badge>
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {fedecpFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-blue-500/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <span className="text-3xl">{formation.icon}</span>
                    <Badge className={formation.type === 'Obligatoire' || formation.type.includes('Obligatoire') ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}>
                      {formation.type}
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
                    <DollarSign className="h-3 w-3" />
                    <span>{formation.price}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.topics.slice(0, 3).map((topic, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        {topic}
                      </li>
                    ))}
                    {formation.topics.length > 3 && (
                      <li className="text-xs text-gray-500">+{formation.topics.length - 3} autres...</li>
                    )}
                  </ul>
                  <a href={formation.link} target="_blank" rel="noopener noreferrer">
                    <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700">
                      <ExternalLink className="h-3 w-3 mr-1" /> S'inscrire
                    </Button>
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* BIONIC Section */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-[#f5a623]/20 rounded-lg">
              <Brain className="h-6 w-6 text-[#f5a623]" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Formations BIONIC™</h2>
              <p className="text-gray-400 text-sm">Maîtrisez les outils d'analyse de territoire</p>
            </div>
            <Badge className="ml-auto bg-[#f5a623]/20 text-[#f5a623]">Exclusif</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {bionicFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-[#f5a623]/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <span className="text-3xl">{formation.icon}</span>
                    <Badge className="bg-[#f5a623]/20 text-[#f5a623]">{formation.type}</Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.modules.map((module, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-[#f5a623]" />
                        {module}
                      </li>
                    ))}
                  </ul>
                  <Button size="sm" className="w-full btn-golden text-black">
                    Commencer
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Territoire Types Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Map className="h-6 w-6 text-green-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Types de Territoires au Québec</h2>
              <p className="text-gray-400 text-sm">Connaissez les différentes zones de chasse</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {territoireTypes.map((territoire) => (
              <Card key={territoire.type} className="bg-card border-border" style={{ borderLeftColor: territoire.color, borderLeftWidth: '4px' }}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg" style={{ color: territoire.color }}>{territoire.type}</CardTitle>
                  <CardDescription className="text-xs">{territoire.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {territoire.features.map((feature, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3" style={{ color: territoire.color }} />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
};

// Main App Component
function App() {
  const [products, setProducts] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const sessionId = getSessionId();

  const fetchProducts = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/products/top?limit=10`);
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
    setLoading(false);
  }, []);

  const handleAddToCart = async (product) => {
    try {
      await axios.post(`${API}/cart`, {
        session_id: sessionId,
        product_id: product.id,
        quantity: 1
      });
      // Fetch updated cart
      const cartResponse = await axios.get(`${API}/cart/${sessionId}`);
      setCartItems(cartResponse.data.items || cartResponse.data || []);
      toast.success("Produit ajouté au panier!");
    } catch (error) {
      console.error("Cart error:", error);
      toast.error("Erreur lors de l'ajout au panier");
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      const response = await axios.delete(`${API}/cart/${sessionId}/item/${itemId}`);
      setCartItems(response.data.items || []);
      toast.success("Produit retiré du panier");
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleUpdateQuantity = async (itemId, quantity) => {
    try {
      const response = await axios.put(`${API}/cart/${sessionId}/item/${itemId}`, { quantity });
      setCartItems(response.data.items || []);
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <LanguageProvider>
      <AuthProvider>
        <NotificationProvider 
          coordinates={{ lat: 46.8139, lng: -71.2080 }}
          enabled={true}
          warningMinutes={15}
        >
        <div className="App min-h-screen bg-background">
          <BrowserRouter>
            <SEOHead />
            <Navigation cartCount={cartCount} onCartOpen={() => setIsCartOpen(true)} />
            <CartSheet 
              isOpen={isCartOpen} 
              onOpenChange={setIsCartOpen} 
              cartItems={cartItems} 
              onUpdateQuantity={handleUpdateQuantity}
              onRemoveItem={handleRemoveItem}
            />
            <Routes>
              <Route path="/" element={<HomePage products={products} onAddToCart={handleAddToCart} />} />
              <Route path="/analyze" element={<AnalyzerModule />} />
              <Route path="/compare" element={<ComparePage products={products} />} />
              <Route path="/shop" element={<ShopPage products={products} onAddToCart={handleAddToCart} />} />
              <Route path="/territoire" element={<TerritoryPage />} />
              <Route path="/mon-territoire-bionic" element={<MonTerritoireBionicPage />} />
              <Route path="/marketplace" element={<MarketplacePage />} />
              <Route path="/formations" element={<FormationsPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/business" element={<BusinessPage />} />
              <Route path="/plan-maitre" element={<PlanMaitrePage />} />
              <Route path="/referral" element={<ReferralModule />} />
              <Route path="/admin" element={<AdminPage onProductsUpdate={fetchProducts} />} />
              <Route path="/networking" element={<NetworkingHub />} />
              <Route path="/lands" element={<LandsRental />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
              <Route path="/become-partner" element={<BecomePartner />} />
              <Route path="/partner/dashboard" element={<PartnerDashboard />} />
            </Routes>
            <Footer />
            <ScrollNavigator />
            <Toaster position="bottom-right" richColors />
            <CookieConsent />
          </BrowserRouter>
        </div>
        </NotificationProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
