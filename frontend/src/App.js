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
import { 
  ShoppingCart, 
  FlaskConical, 
  GitCompare, 
  Star,
  DollarSign,
  ThumbsUp,
  Heart,
  Award,
  ChevronRight,
  Menu,
  X,
  Settings,
  Plus,
  Minus,
  Trash2,
  Lock,
  LogOut,
  Edit,
  Save,
  Package,
  Users,
  TrendingUp,
  Store,
  Percent,
  Link as LinkIcon,
  Eye,
  EyeOff,
  MousePointer,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  Truck,
  ExternalLink,
  RefreshCw,
  FileText,
  Bell,
  Loader2,
  Info,
  MapPin,
  Target,
  ArrowLeft,
  FolderOpen,
  Copy,
  Download,
  BookOpen,
  GraduationCap,
  Map,
  Filter,
  Building2,
  Trees,
  Mountain,
  Compass,
  Crosshair,
  Sparkles,
  Globe,
  Construction,
  Power,
  Mail,
  Handshake,
  XCircle,
  Moon,
  Sun,
  Bot,
  Radar,
  Share2,
  Gift
} from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============================================
// CLIENT PROFILE MANAGEMENT
// ============================================

// Get or create session ID
const getSessionId = () => {
  let sessionId = localStorage.getItem('scent_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('scent_session_id', sessionId);
  }
  return sessionId;
};

// Client Profile Management
const CLIENT_PROFILE_KEY = 'scent_client_profile';

const getClientProfile = () => {
  try {
    const profile = localStorage.getItem(CLIENT_PROFILE_KEY);
    return profile ? JSON.parse(profile) : null;
  } catch {
    return null;
  }
};

const saveClientProfile = (profile) => {
  try {
    const existingProfile = getClientProfile() || {};
    const updatedProfile = {
      ...existingProfile,
      ...profile,
      lastUpdated: new Date().toISOString(),
      visitCount: (existingProfile.visitCount || 0) + 1
    };
    localStorage.setItem(CLIENT_PROFILE_KEY, JSON.stringify(updatedProfile));
    return updatedProfile;
  } catch {
    return null;
  }
};

const clearClientProfile = () => {
  localStorage.removeItem(CLIENT_PROFILE_KEY);
};

// Logo Component - Now uses BionicLogo with language support
const Logo = ({ size = "default", fillContainer = false }) => {
  return <BionicLogo size={size === "large" ? "xlarge" : "default"} fillContainer={fillContainer} />;
};

// Back Button Component
const BackButton = ({ to = "/", label = "Retour" }) => {
  const navigate = useNavigate();
  
  const handleBack = () => {
    if (to === "back") {
      navigate(-1);
    } else {
      navigate(to);
    }
  };
  
  return (
    <Button 
      variant="ghost" 
      size="sm" 
      onClick={handleBack}
      className="text-gray-400 hover:text-white hover:bg-white/10 gap-2"
      data-testid="back-button"
    >
      <ArrowLeft className="h-4 w-4" />
      {label}
    </Button>
  );
};

// Sale Mode Badge Component
const SaleModeBadge = ({ mode }) => {
  const config = {
    dropshipping: { color: "bg-blue-600", label: "Dropshipping" },
    affiliation: { color: "bg-purple-600", label: "Affiliation" },
    hybrid: { color: "bg-gradient-to-r from-blue-600 to-purple-600", label: "Hybride" }
  };
  const { color, label } = config[mode] || config.dropshipping;
  return <Badge className={`${color} text-white text-xs`}>{label}</Badge>;
};

// Welcome Back Banner Component
const WelcomeBackBanner = ({ profile, onEdit }) => {
  if (!profile?.name) return null;
  
  return (
    <div className="bg-gradient-to-r from-[#f5a623]/20 to-transparent border border-[#f5a623]/30 rounded-lg p-3 mb-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
          <Users className="h-5 w-5 text-[#f5a623]" />
        </div>
        <div>
          <p className="text-white font-medium">Bon retour, {profile.name}! 👋</p>
          <p className="text-gray-400 text-sm">{profile.email}</p>
        </div>
      </div>
      <Button variant="ghost" size="sm" onClick={onEdit} className="text-[#f5a623]">
        <Edit className="h-4 w-4 mr-1" /> Modifier
      </Button>
    </div>
  );
};

// Navigation Component
const Navigation = ({ cartCount, onCartOpen }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const { t } = useLanguage();
  
  const navLinks = [
    { path: "/", labelKey: "nav_home" },
    { path: "/analyze", labelKey: "nav_analyze" },
    { path: "/compare", labelKey: "nav_compare" },
    { path: "/shop", labelKey: "nav_shop" },
    { path: "/mon-territoire-bionic", labelKey: "nav_mon_territoire_bionic", highlight: true },
    { path: "/territory", labelKey: "nav_territory" },
    { path: "/marketplace", labelKey: "nav_marketplace" },
    { path: "/network", labelKey: "nav_network" },
    { path: "/formations", labelKey: "nav_formations" },
    { path: "/", label: "Accueil" },
    { path: "/analyze", label: "Analysez" },
    { path: "/compare", label: "Comparez" },
    { path: "/shop", label: "Magasin" },
    { path: "/referral", label: "Parrainage", icon: Gift },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-md border-b border-border" data-testid="navigation">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-[72px]">
          <Link to="/" className="flex items-center flex-shrink-0">
            {/* Logo with golden frame - enlarged */}
            <div className="golden-border rounded-lg px-3 py-2 bg-black/60">
              <Logo size="default" />
            </div>
          </Link>

          <div className="hidden lg:flex items-center space-x-5 ml-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`nav-link text-sm font-medium transition-colors ${
                  link.highlight 
                    ? `${location.pathname === link.path ? "text-[#f5a623] bg-[#f5a623]/20" : "text-[#f5a623] hover:bg-[#f5a623]/10"} px-3 py-1.5 rounded-full border border-[#f5a623]/50`
                    : location.pathname === link.path ? "text-[#f5a623]" : "text-white hover:text-[#f5a623]"
                }`}
              >
                {t(link.labelKey)}
              </Link>
            ))}
          </div>

          <div className="flex items-center space-x-3">
            {/* Notifications */}
            <NotificationCenter />

            {/* User Login Button */}
            <UserMenu />

            {/* Language Switcher */}
            <LanguageSwitcher />

            <Link to="/admin">
              <Button variant="ghost" size="icon" className="text-white" data-testid="settings-btn">
                <Settings className="h-5 w-5" />
              </Button>
            </Link>

            <Button variant="ghost" className="text-white flex items-center gap-2" onClick={onCartOpen} data-testid="cart-button">
              <ShoppingCart className="h-5 w-5" />
              <span className="hidden sm:inline">{t('nav_cart')}</span>
              {cartCount > 0 && <Badge className="bg-[#f5a623] text-black ml-1">{cartCount}</Badge>}
            </Button>

            <Button variant="ghost" size="icon" className="lg:hidden text-white" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>

      {isMenuOpen && (
        <div className="lg:hidden bg-black/95 border-t border-border">
          <div className="px-4 py-4 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`block px-4 py-2 rounded-lg ${
                  location.pathname === link.path ? "bg-[#f5a623]/10 text-[#f5a623]" : "text-white hover:bg-white/5"
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                {t(link.labelKey)}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};

// Hero Section
const HeroSection = () => {
  const { brand, t } = useLanguage();
  
  return (
    <section className="hero-bg min-h-screen flex flex-col items-center justify-center text-center px-4 pt-24" data-testid="hero-section">
      <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-8">
        {brand.tagline}
      </h1>
      <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
        <Link to="/analyze">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2" data-testid="hero-analyze-btn">
            <FlaskConical className="h-5 w-5" /> {t('nav_analyze')}
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/compare">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2" data-testid="hero-compare-btn">
            <GitCompare className="h-5 w-5" /> {t('nav_compare')}
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/shop">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2" data-testid="hero-shop-btn">
            <ShoppingCart className="h-5 w-5" /> {t('hero_order')}
          </Button>
        </Link>
      </div>
      <div className="max-w-3xl mx-auto space-y-4">
        <p className="text-gray-300 text-lg">
          {t('hero_description')}
        </p>
        <p className="text-[#f5a623] font-medium">
          {t('hero_highlight')}
        </p>
        <p className="text-gray-400 italic">{t('hero_subtitle')}</p>
        <p className="text-[#f5a623] font-semibold text-xl mt-6">
          {brand.slogan}
        </p>
      </div>
    </section>
  );
};

// Product Card Component
const ProductCard = ({ product, onAddToCart, onAffiliateClick }) => {
  const isAffiliate = product.sale_mode === "affiliation" || 
    (product.sale_mode === "hybrid" && !product.dropshipping_available);

  const handleBuyClick = async () => {
    if (isAffiliate && product.affiliate_link) {
      // Record affiliate click and redirect
      if (onAffiliateClick) {
        await onAffiliateClick(product);
      }
    } else {
      onAddToCart(product);
    }
  };

  return (
    <Card className="product-card bg-card border-border overflow-hidden" data-testid={`product-card-${product.rank}`}>
      <div className="relative">
        <div className="absolute top-3 left-3 z-10">
          <Badge className="rank-badge text-white font-bold px-3 py-1">#{product.rank}</Badge>
        </div>
        <div className="absolute top-3 right-3 z-10">
          <SaleModeBadge mode={product.sale_mode} />
        </div>
        <div className="aspect-[4/3] overflow-hidden">
          <img src={product.image_url} alt={product.name} className="w-full h-full object-cover transition-transform duration-300 hover:scale-110" />
        </div>
      </div>
      <CardContent className="p-4">
        <p className="text-[#f5a623] text-sm font-medium mb-1">{product.brand}</p>
        <h3 className="text-white font-semibold text-lg mb-3">{product.name}</h3>
        <div className="flex items-center justify-between mb-4">
          <span className="text-[#f5a623] font-bold text-xl">${product.price}</span>
          <Badge className="score-badge bg-[#f5a623] text-white font-bold px-3 py-1">{product.score}</Badge>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="flex-1 border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623]/10">
            <FlaskConical className="h-4 w-4" />
          </Button>
          <Button className="flex-1 btn-golden text-black font-semibold" onClick={handleBuyClick}>
            {isAffiliate ? <ExternalLink className="h-4 w-4" /> : <ShoppingCart className="h-4 w-4" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Filter Tabs Component
const FilterTabs = ({ activeFilter, onFilterChange }) => {
  const filters = [
    { id: "top", label: "5", icon: Star },
    { id: "price", label: "5", icon: DollarSign },
    { id: "value", label: "5", icon: ThumbsUp },
    { id: "favorite", label: "5", icon: Heart },
    { id: "awarded", label: "5", icon: Award },
  ];

  return (
    <div className="flex flex-wrap justify-center gap-2 mb-8">
      {filters.map((filter) => (
        <button
          key={filter.id}
          onClick={() => onFilterChange(filter.id)}
          className={`filter-tab flex items-center gap-2 px-4 py-2 rounded-full border transition-colors ${
            activeFilter === filter.id ? "active border-[#f5a623] bg-[#f5a623]/10 text-[#f5a623]" : "border-border text-gray-400 hover:border-gray-500"
          }`}
        >
          <filter.icon className="h-4 w-4" />
          <span>{filter.label}</span>
        </button>
      ))}
    </div>
  );
};

// Products Section
const ProductsSection = ({ products, onAddToCart, onAffiliateClick }) => {
  const [activeFilter, setActiveFilter] = useState("top");
  const { t, brand } = useLanguage();
  
  return (
    <section className="py-16 px-4 bg-background" data-testid="products-section">
      <div className="max-w-7xl mx-auto">
        <h2 className="golden-text text-3xl md:text-4xl font-bold text-center mb-8 italic">
          {t('page_best_choices')} {brand.short}
        </h2>
        <FilterTabs activeFilter={activeFilter} onFilterChange={setActiveFilter} />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 sm:gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} onAffiliateClick={onAffiliateClick} />
          ))}
        </div>
      </div>
    </section>
  );
};

// Features Section
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          {features.map((feature, index) => (
            <div key={index} className="feature-card rounded-xl p-6 sm:p-8 text-center">
              <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-3 sm:mb-4 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                <feature.icon className="h-6 w-6 sm:h-8 sm:w-8 text-[#f5a623]" />
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

// Cart Sheet
const CartSheet = ({ isOpen, onOpenChange, cartItems, onUpdateQuantity, onRemoveItem }) => {
  const { t, language } = useLanguage();
  const total = cartItems.reduce((sum, item) => sum + (item.product?.price || 0) * item.quantity, 0);
  const itemCount = cartItems.length;
  const itemText = language === 'fr' 
    ? `${itemCount} article${itemCount !== 1 ? 's' : ''} dans votre panier`
    : `${itemCount} item${itemCount !== 1 ? 's' : ''} in your cart`;
  
  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="text-white flex items-center gap-2">
            <ShoppingCart className="h-5 w-5 text-[#f5a623]" /> {t('nav_cart')}
          </SheetTitle>
          <SheetDescription>{itemText}</SheetDescription>
        </SheetHeader>
        <div className="mt-6 space-y-4 flex-1 overflow-auto">
          {cartItems.length === 0 ? (
            <p className="text-gray-400 text-center py-8">{t('cart_empty')}</p>
          ) : (
            cartItems.map((item) => (
              <div key={item.id} className="flex items-center gap-4 p-4 bg-background rounded-lg">
                <img src={item.product?.image_url} alt={item.product?.name} className="w-16 h-16 object-cover rounded" />
                <div className="flex-1">
                  <h4 className="text-white font-medium text-sm">{item.product?.name}</h4>
                  <p className="text-[#f5a623] font-semibold">${item.product?.price}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => onUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}>
                    <Minus className="h-4 w-4" />
                  </Button>
                  <span className="text-white w-8 text-center">{item.quantity}</span>
                  <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}>
                    <Plus className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500" onClick={() => onRemoveItem(item.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
        {cartItems.length > 0 && (
          <div className="mt-6 pt-6 border-t border-border">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-400">{t('cart_total')}</span>
              <span className="text-[#f5a623] font-bold text-xl">${total.toFixed(2)}</span>
            </div>
            <Button className="w-full btn-golden text-black font-semibold">{t('hero_order')}</Button>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
};

// Footer
const Footer = () => {
  const { t } = useLanguage();
  return (
    <footer className="py-8 px-4 bg-black border-t border-border">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <h3 className="text-white font-bold mb-3">Bionic™</h3>
            <p className="text-gray-500 text-sm">
              {t('footer_tagline')}
            </p>
          </div>
          {/* Links */}
          <div>
            <h4 className="text-gray-400 font-medium mb-3 text-sm">{t('footer_quick_links')}</h4>
            <div className="space-y-2">
              <Link to="/territory" className="block text-gray-500 hover:text-[#f5a623] text-sm transition-colors">{t('nav_territory')}</Link>
              <Link to="/marketplace" className="block text-gray-500 hover:text-[#f5a623] text-sm transition-colors">{t('nav_marketplace')}</Link>
              <Link to="/formations" className="block text-gray-500 hover:text-[#f5a623] text-sm transition-colors">{t('nav_formations')}</Link>
            </div>
          </div>
          {/* Partner CTA */}
          <div>
            <h4 className="text-gray-400 font-medium mb-3 text-sm">{t('footer_partners')}</h4>
            <p className="text-gray-500 text-sm mb-3">{t('footer_partner_join')}</p>
            <Link to="/become-partner">
              <Button size="sm" className="btn-golden text-black">
                <Handshake className="h-4 w-4 mr-2" />
                {t('footer_become_partner')}
              </Button>
            </Link>
          </div>
        </div>
        <div className="border-t border-border pt-6 flex items-center justify-center">
          <a href="https://app.emergent.sh/?utm_source=emergent-badge" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
            <img src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4" alt="Emergent" className="h-6 w-6 rounded-full" />
            <span>Made with Emergent</span>
          </a>
        </div>
      </div>
    </footer>
  );
};

// Home Page
const HomePage = ({ products, onAddToCart, onAffiliateClick }) => {
  return (
    <main>
      <HeroSection />
      <ProductsSection products={products} onAddToCart={onAddToCart} onAffiliateClick={onAffiliateClick} />
    </main>
  );
};

// Analyze Page
const AnalyzePage = ({ products }) => (
  <main className="pt-20 min-h-screen bg-background">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <h1 className="golden-text text-4xl font-bold mb-4">Analysez</h1>
      <p className="text-gray-400 mb-8">Analysez en profondeur chaque attractant avec nos 13 critères scientifiques évalués par IA.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
        {products.map((product) => (
          <Card key={product.id} className="bg-card border-border p-4 sm:p-6">
            <div className="flex items-start gap-3 sm:gap-4">
              <img src={product.image_url} alt={product.name} className="w-20 h-20 sm:w-24 sm:h-24 object-cover rounded-lg" />
              <div className="flex-1 min-w-0">
                <p className="text-[#f5a623] text-xs sm:text-sm">{product.brand}</p>
                <h3 className="text-white font-semibold mb-2 text-sm sm:text-base truncate">{product.name}</h3>
                <div className="flex items-center gap-1 sm:gap-2 flex-wrap">
                  <Badge className="bg-[#f5a623] text-xs">Score: {product.score}</Badge>
                  <Badge variant="outline" className="border-[#f5a623] text-[#f5a623] text-xs">#{product.rank}</Badge>
                  <SaleModeBadge mode={product.sale_mode} />
                </div>
              </div>
            </div>
            <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-border">
              <p className="text-gray-400 text-xs sm:text-sm line-clamp-2">{product.description}</p>
              <div className="mt-2 flex items-center gap-3 sm:gap-4 text-xs text-gray-500">
                <span><Eye className="h-3 w-3 inline mr-1" />{product.views || 0} vues</span>
                <span><MousePointer className="h-3 w-3 inline mr-1" />{product.clicks || 0} clics</span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  </main>
);

// ============================================
// TERRITORY PAGE - Map Interface
// ============================================

import TerritoryRankings from "@/components/TerritoryRankings";
import GpsHotspots from "@/components/GpsHotspots";

const TerritoryPage = () => {
  const [userId, setUserId] = useState(null);
  const [userName, setUserName] = useState('');
  const [loading, setLoading] = useState(true);
  const [autoLoginFailed, setAutoLoginFailed] = useState(false);
  const [activeTab, setActiveTab] = useState('map'); // 'map', 'rankings', or 'hotspots'
  const [navigateToCoords, setNavigateToCoords] = useState(null);

  // Function to navigate to map with specific coordinates
  const handleNavigateToMap = (lat, lng) => {
    setNavigateToCoords({ lat, lng });
    setActiveTab('map');
  };

  // Auto-login with saved credentials
  useEffect(() => {
    // Auto-login based on IP address
    const autoLogin = async () => {
      try {
        const response = await axios.get(`${API}/territory/users/auto-login`);
        const userData = response.data;
        
        setUserId(userData.id);
        setUserName(userData.name);
        localStorage.setItem('territory_user_id', userData.id);
        
        if (userData.auto_created) {
          toast.success(`Bienvenue ${userData.name}! Compte créé automatiquement.`);
        } else {
          toast.success(`Bon retour, ${userData.name}!`);
        }
      } catch (error) {
        console.error('Auto-login failed:', error);
        setAutoLoginFailed(true);
        // Fallback to localStorage
        const savedUserId = localStorage.getItem('territory_user_id');
        if (savedUserId) {
          setUserId(savedUserId);
        }
      } finally {
        setLoading(false);
      }
    };
    
    autoLogin();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('territory_user_id');
    setUserId(null);
    setUserName('');
    toast.success('Déconnexion réussie');
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-[#f5a623] mx-auto mb-4" />
          <p className="text-gray-400">Reconnaissance automatique en cours...</p>
        </div>
      </div>
    );
  }

  if (!userId && autoLoginFailed) {
    return (
      <main className="pt-20 min-h-screen bg-background">
        <div className="max-w-md mx-auto px-4 py-16">
          <Card className="bg-card border-border">
            <CardHeader className="text-center">
              <div className="mx-auto bg-red-500 p-4 rounded-full w-fit mb-4">
                <AlertTriangle className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-white text-2xl">Erreur de connexion</CardTitle>
              <CardDescription>
                La reconnaissance automatique a échoué. Veuillez réessayer.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                className="w-full btn-golden text-black font-semibold"
                onClick={() => window.location.reload()}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Réessayer
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  return (
    <div className="pt-16 min-h-screen bg-background">
      {/* Tab Navigation */}
      <div className="fixed top-16 left-0 right-0 z-[500] bg-background/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-screen-2xl mx-auto px-4">
          <div className="flex items-center gap-1 py-2">
            <button
              onClick={() => setActiveTab('map')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === 'map'
                  ? 'bg-[#f5a623] text-black font-semibold'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
              data-testid="tab-map"
            >
              <Map className="h-4 w-4" />
              Carte Interactive
            </button>
            <button
              onClick={() => setActiveTab('hotspots')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === 'hotspots'
                  ? 'bg-[#f5a623] text-black font-semibold'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
              data-testid="tab-hotspots"
            >
              <Crosshair className="h-4 w-4" />
              Meilleurs Spots GPS
            </button>
            <button
              onClick={() => setActiveTab('rankings')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === 'rankings'
                  ? 'bg-[#f5a623] text-black font-semibold'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
              data-testid="tab-rankings"
            >
              <TrendingUp className="h-4 w-4" />
              Classement Territoires
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className={activeTab === 'map' ? 'pt-12' : 'pt-12 px-4 pb-8 max-w-screen-2xl mx-auto'}>
        {activeTab === 'map' ? (
          <TerritoryMap 
            userId={userId} 
            userName={userName} 
            onLogout={handleLogout}
            navigateToCoords={navigateToCoords}
            onNavigationComplete={() => setNavigateToCoords(null)}
          />
        ) : activeTab === 'rankings' ? (
          <TerritoryRankings />
        ) : (
          <GpsHotspots onNavigateToMap={handleNavigateToMap} />
        )}
      </div>
    </div>
  );
};




// ============================================
// MARKETPLACE PAGE
// ============================================

const MarketplacePage = () => {
  return (
    <main className="pt-16 min-h-screen bg-background">
      <HuntMarketplace />
    </main>
  );
};

// ============================================
// FORMATIONS PAGE - FédéCP & BIONIC™
// ============================================

const FormationsPage = () => {
  const navigate = useNavigate();
  
  // FédéCP Formation Categories
  const fedecpFormations = [
    {
      id: 'securite',
      title: 'Sécurité à la chasse',
      description: 'Cours obligatoire pour l\'obtention du permis de chasse au Québec.',
      icon: '🛡️',
      duration: '8 heures',
      type: 'Obligatoire',
      link: 'https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/',
      topics: ['Maniement sécuritaire des armes', 'Règles de sécurité', 'Éthique du chasseur', 'Réglementation']
    },
    {
      id: 'piegeage',
      title: 'Formation au piégeage',
      description: 'Techniques de piégeage responsable et réglementation.',
      icon: '🪤',
      duration: '6 heures',
      type: 'Spécialisé',
      link: 'https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/',
      topics: ['Types de pièges', 'Espèces ciblées', 'Réglementation', 'Éthique']
    },
    {
      id: 'arbalete',
      title: 'Formation arbalète',
      description: 'Utilisation sécuritaire de l\'arbalète pour la chasse.',
      icon: '🏹',
      duration: '4 heures',
      type: 'Spécialisé',
      link: 'https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/',
      topics: ['Équipement', 'Technique de tir', 'Sécurité', 'Réglementation']
    },
    {
      id: 'terres-privees',
      title: 'Accès aux terres privées',
      description: 'Bonnes pratiques et ententes chasseur/propriétaire.',
      icon: '🏠',
      duration: '2 heures',
      type: 'Recommandé',
      link: 'https://fedecp.com/la-chasse/je-pratique/ou-chasser/',
      topics: ['Demande d\'autorisation', 'Respect des propriétés', 'Ententes écrites', 'Assurances']
    }
  ];

  // BIONIC™ Internal Formations
  const bionicFormations = [
    {
      id: 'analyse-territoire',
      title: 'Analyse de territoire BIONIC™',
      description: 'Maîtrisez les outils d\'analyse géospatiale pour optimiser vos chasses.',
      icon: '🗺️',
      duration: '3 heures',
      type: 'BIONIC™',
      modules: [
        'Lecture des heatmaps d\'activité',
        'Interprétation des zones de probabilité',
        'Utilisation des couches WMS',
        'Analyse par espèce'
      ]
    },
    {
      id: 'parcours-guide',
      title: 'Parcours guidé optimisé',
      description: 'Apprenez à créer et suivre des parcours de chasse intelligents.',
      icon: '🧭',
      duration: '2 heures',
      type: 'BIONIC™',
      modules: [
        'Création de waypoints stratégiques',
        'Génération de parcours optimisés',
        'Interprétation des probabilités',
        'Navigation GPS terrain'
      ]
    },
    {
      id: 'attractants',
      title: 'Science des attractants',
      description: 'Comprendre la composition et l\'utilisation des produits BIONIC™.',
      icon: '🧪',
      duration: '2 heures',
      type: 'BIONIC™',
      modules: [
        'Types d\'attractants par espèce',
        'Analyse nutritionnelle du gibier',
        'Placement stratégique',
        'Saisons et timing'
      ]
    }
  ];

  // Territoire Types from FédéCP
  const territoireTypes = [
    {
      type: 'Sépaq',
      description: 'Réserves fauniques gérées par la Société des établissements de plein air du Québec.',
      color: '#3b82f6',
      features: ['Tirage au sort', 'Hébergement disponible', 'Aménagements fauniques']
    },
    {
      type: 'ZEC',
      description: 'Zones d\'exploitation contrôlée accessibles à tous.',
      color: '#22c55e',
      features: ['Accès libre avec droits', 'Camping disponible', 'Statistiques publiques']
    },
    {
      type: 'Pourvoiries',
      description: 'Établissements privés offrant services de chasse guidée.',
      color: '#f59e0b',
      features: ['Services complets', 'Guides professionnels', 'Hébergement inclus']
    },
    {
      type: 'Terres privées',
      description: 'Terrains appartenant à des particuliers ou entreprises.',
      color: '#ef4444',
      features: ['Autorisation requise', 'Entente écrite recommandée', 'Respect des propriétés']
    },
    {
      type: 'Refuges fauniques',
      description: 'Territoires protégés avec réglementation spéciale.',
      color: '#8b5cf6',
      features: ['Accès restreint', 'Espèces protégées', 'Permis spéciaux']
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
              <h2 className="text-xl font-bold text-white">Formations FédéCP</h2>
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
                    <Badge className={formation.type === 'Obligatoire' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}>
                      {formation.type}
                    </Badge>
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
                    {formation.topics.slice(0, 3).map((topic, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        {topic}
                      </li>
                    ))}
                  </ul>
                  <a href={formation.link} target="_blank" rel="noopener noreferrer">
                    <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700">
                      <ExternalLink className="h-3 w-3 mr-1" /> Accéder
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
              <h2 className="text-xl font-bold text-white">Types de Territoires</h2>
              <p className="text-gray-400 text-sm">Connaissez les différentes zones de chasse au Québec</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {territoireTypes.map((territoire) => (
              <Card key={territoire.type} className="bg-card border-border" style={{ borderLeftColor: territoire.color, borderLeftWidth: '4px' }}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-white text-lg" style={{ color: territoire.color }}>{territoire.type}</CardTitle>
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


// Main App
function App() {
  const [products, setProducts] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Site access control state
  const [siteStatus, setSiteStatus] = useState(null);
  const [siteStatusLoading, setSiteStatusLoading] = useState(true);
  const [bypassMaintenance, setBypassMaintenance] = useState(false);

  const sessionId = getSessionId();

  // Réduire la vitesse de défilement au clavier (flèches haut/bas)
  useEffect(() => {
    const SCROLL_STEP = 40; // Réduit de ~100px par défaut à 40px (environ moitié)
    
    const handleKeyDown = (e) => {
      // Ignorer si on est dans un input/textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
        return;
      }
      
      // Flèche haut
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        window.scrollBy({ top: -SCROLL_STEP, behavior: 'smooth' });
      }
      // Flèche bas
      else if (e.key === 'ArrowDown') {
        e.preventDefault();
        window.scrollBy({ top: SCROLL_STEP, behavior: 'smooth' });
      }
      // Page Up - réduit aussi
      else if (e.key === 'PageUp') {
        e.preventDefault();
        window.scrollBy({ top: -window.innerHeight * 0.4, behavior: 'smooth' }); // 40% au lieu de 100%
      }
      // Page Down - réduit aussi
      else if (e.key === 'PageDown') {
        e.preventDefault();
        window.scrollBy({ top: window.innerHeight * 0.4, behavior: 'smooth' }); // 40% au lieu de 100%
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Check site status on mount - SECURE MAINTENANCE CHECK
  useEffect(() => {
    const checkSiteStatus = async () => {
      try {
        // Use the NEW secure maintenance endpoint
        const response = await axios.get(`${API}/maintenance/status`);
        
        // Convert to expected format
        const maintenanceStatus = {
          mode: response.data.is_active ? 'maintenance' : 'live',
          is_accessible: !response.data.is_active,
          message: response.data.message,
          show_progress: response.data.show_progress,
          progress_percent: response.data.progress_percent,
          estimated_completion: response.data.estimated_completion,
          contact_email: response.data.contact_email,
          activated_at: response.data.activated_at
        };
        
        setSiteStatus(maintenanceStatus);
        
        // Check for valid bypass token (stored server-side validated)
        const bypassToken = localStorage.getItem('maintenance_bypass_token');
        
        if (bypassToken && response.data.is_active) {
          // Verify token with server
          try {
            const verifyResponse = await axios.post(`${API}/maintenance/verify-bypass`, null, {
              params: { token: bypassToken }
            });
            
            if (verifyResponse.data.valid) {
              setBypassMaintenance(true);
            } else {
              // Token invalid, remove it
              localStorage.removeItem('maintenance_bypass_token');
              setBypassMaintenance(false);
            }
          } catch (verifyError) {
            // Token verification failed, remove it
            localStorage.removeItem('maintenance_bypass_token');
            setBypassMaintenance(false);
          }
        } else if (!response.data.is_active) {
          // Maintenance not active, clear any bypass token
          localStorage.removeItem('maintenance_bypass_token');
          setBypassMaintenance(false);
        } else {
          // Admin route bypass (always allow admin page access)
          const isAdminRoute = window.location.pathname === '/admin';
          setBypassMaintenance(isAdminRoute);
        }
      } catch (error) {
        console.error('Error checking maintenance status:', error);
        // SECURITY: On error, do NOT allow access - show error state
        setSiteStatus({ 
          mode: 'error', 
          is_accessible: false,
          message: 'Impossible de vérifier l\'état du site. Veuillez réessayer.'
        });
        setBypassMaintenance(false);
      } finally {
        setSiteStatusLoading(false);
      }
    };
    checkSiteStatus();
  }, []);

  const fetchProducts = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/products/top?limit=10`);
      setProducts(response.data);
    } catch (error) {
      try {
        await axios.post(`${API}/seed`);
        const response = await axios.get(`${API}/products/top?limit=10`);
        setProducts(response.data);
      } catch (seedError) {
        console.error("Error seeding products:", seedError);
      }
    }
  }, []);

  const fetchCart = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/cart/${sessionId}`);
      setCartItems(response.data);
    } catch (error) {
      console.error("Error fetching cart:", error);
    }
  }, [sessionId]);

  useEffect(() => {
    checkSiteStatus();
  }, [checkSiteStatus]);

  useEffect(() => {
    const initData = async () => {
      setLoading(true);
      await fetchProducts();
      await fetchCart();
      setLoading(false);
    };
    
    // Only load data if not in maintenance mode OR if admin is authenticated
    const isAdminAuthenticated = localStorage.getItem('admin_authenticated') === 'true';
    if (!siteStatus.maintenance_mode || isAdminAuthenticated) {
      initData();
    } else {
      setLoading(false);
    }
  }, [fetchProducts, fetchCart, siteStatus.maintenance_mode]);

  const handleAddToCart = async (product) => {
    try {
      await axios.post(`${API}/cart`, {
        product_id: product.id,
        quantity: 1,
        session_id: sessionId
      });
      await fetchCart();
      toast.success(`${product.name} ajouté au panier`);
    } catch (error) {
      toast.error("Erreur lors de l'ajout au panier");
    }
  };

  const handleAffiliateClick = async (product) => {
    try {
      const response = await axios.post(`${API}/affiliate/click?product_id=${product.id}&session_id=${sessionId}`);
      if (response.data.redirect_url) {
        toast.info("Redirection vers le partenaire...");
        window.open(response.data.redirect_url, '_blank');
      }
    } catch (error) {
      toast.error("Erreur de redirection");
    }
  };

  const handleUpdateQuantity = async (itemId, quantity) => {
    try {
      await axios.put(`${API}/cart/${itemId}`, { quantity });
      await fetchCart();
    } catch (error) {
      console.error("Error updating cart:", error);
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      await axios.delete(`${API}/cart/${itemId}`);
      await fetchCart();
      toast.success("Article supprimé");
    } catch (error) {
      console.error("Error removing from cart:", error);
    }
  };

  const handleAdminAccess = () => {
    // Navigate to admin page where they can login
    window.location.href = '/admin';
  };

  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  
  // Check if admin is authenticated (allow bypass)
  const isAdminAuthenticated = localStorage.getItem('admin_authenticated') === 'true';

  // Show loading while checking status
  if (checkingStatus) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Logo size="large" />
          <p className="text-gray-400 mt-4">Vérification...</p>
        </div>
      </div>
    );
  }

  // Show maintenance page if in maintenance mode and not admin
  if (siteStatus.maintenance_mode && !isAdminAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center max-w-lg">
          <div className="mb-8">
            <Logo size="large" />
          </div>
          
          <div className="bg-card border border-border rounded-2xl p-8 shadow-2xl">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-yellow-500/20 flex items-center justify-center">
              <Moon className="h-10 w-10 text-yellow-500" />
            </div>
            
            <h1 className="text-3xl font-bold text-white mb-4">
              {siteStatus.maintenance_title || "Site en maintenance"}
            </h1>
            
            <p className="text-gray-400 text-lg mb-6">
              {siteStatus.maintenance_message || "Nous effectuons actuellement des mises à jour. Veuillez revenir plus tard."}
            </p>
            
            {siteStatus.estimated_return && (
              <div className="bg-background rounded-lg p-4 mb-6">
                <p className="text-gray-500 text-sm">Retour estimé</p>
                <p className="text-[#f5a623] font-semibold">{siteStatus.estimated_return}</p>
              </div>
            )}
            
            <div className="flex flex-col gap-3">
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => window.location.reload()}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Actualiser la page
              </Button>
              
              <a 
                href="/admin" 
                className="text-gray-500 text-sm hover:text-[#f5a623] transition-colors"
              >
                Accès administrateur →
              </a>
            </div>
          </div>
          
          <p className="text-gray-600 text-sm mt-8">
            © {new Date().getFullYear()} SCENT SCIENCE™ Laboratory
          </p>
        </div>
        <Toaster position="bottom-right" richColors />
      </div>
    );
  }

  // Show loading while checking site status
  if (siteStatusLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Logo size="large" />
          <p className="text-gray-400 mt-4">Vérification de l'accès...</p>
        </div>
      </div>
    );
  }

  // Show maintenance page if site is not live and user is not admin
  if (siteStatus && !siteStatus.is_accessible && !bypassMaintenance) {
    return (
      <MaintenancePage 
        siteStatus={siteStatus} 
        onAdminAccess={handleAdminAccess}
      />
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Logo size="large" />
          <p className="text-gray-400 mt-4">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <LanguageProvider>
      <AuthProvider>
        <div className="App min-h-screen bg-background">
          <BrowserRouter>
            <SEOHead />
            <Navigation cartCount={cartCount} onCartOpen={() => setIsCartOpen(true)} />
            <CartSheet isOpen={isCartOpen} onOpenChange={setIsCartOpen} cartItems={cartItems} onUpdateQuantity={handleUpdateQuantity} onRemoveItem={handleRemoveItem} />
            <Routes>
              <Route path="/" element={<HomePage products={products} onAddToCart={handleAddToCart} onAffiliateClick={handleAffiliateClick} />} />
              <Route path="/analyze" element={<AnalyzerModule />} />
              <Route path="/compare" element={<ComparePage products={products} />} />
              <Route path="/shop" element={<ShopPage products={products} onAddToCart={handleAddToCart} onAffiliateClick={handleAffiliateClick} />} />
              <Route path="/mon-territoire-bionic" element={<MonTerritoireBionicPage />} />
              <Route path="/admin" element={<AdminPage onProductsUpdate={fetchProducts} />} />
              <Route path="/territory" element={<TerritoryPage />} />
              <Route path="/marketplace" element={<MarketplacePage />} />
              <Route path="/network" element={<NetworkingHub />} />
              <Route path="/formations" element={<FormationsPage />} />
              <Route path="/terres" element={<LandsRental />} />
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
      </AuthProvider>
    </LanguageProvider>
    <div className="App min-h-screen bg-background">
      <BrowserRouter>
        <Navigation cartCount={cartCount} onCartOpen={() => setIsCartOpen(true)} />
        <CartSheet isOpen={isCartOpen} onOpenChange={setIsCartOpen} cartItems={cartItems} onUpdateQuantity={handleUpdateQuantity} onRemoveItem={handleRemoveItem} />
        <Routes>
          <Route path="/" element={<HomePage products={products} onAddToCart={handleAddToCart} onAffiliateClick={handleAffiliateClick} />} />
          <Route path="/analyze" element={<AnalyzerModule />} />
          <Route path="/compare" element={<ComparePage products={products} />} />
          <Route path="/shop" element={<ShopPage products={products} onAddToCart={handleAddToCart} onAffiliateClick={handleAffiliateClick} />} />
          <Route path="/referral" element={<ReferralModule />} />
          <Route path="/admin" element={<AdminPage onProductsUpdate={fetchProducts} />} />
        </Routes>
        <DynamicReferralWidget />
        <Footer />
        <Toaster position="bottom-right" richColors />
      </BrowserRouter>
    </div>
  );
}

export default App;
