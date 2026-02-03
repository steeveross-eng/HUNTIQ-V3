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
          <Link to="/analyze" className="text-gray-400 hover:text-white transition-colors">{t('nav_analyze')}</Link>
          <Link to="/compare" className="text-gray-400 hover:text-white transition-colors">{t('nav_compare')}</Link>
          <Link to="/shop" className="text-gray-400 hover:text-white transition-colors">{t('nav_shop')}</Link>
          <Link to="/territoire" className="text-gray-400 hover:text-white transition-colors">{t('nav_territory')}</Link>
        </nav>
        <div className="flex items-center gap-4">
          <LanguageSwitcher />
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
      <div className="golden-border rounded-2xl p-6 mb-8 bg-black/60">
        <Logo size="large" />
      </div>
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
  return (
    <main className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4">
        <Button variant="ghost" onClick={() => navigate('/')} className="mb-4 text-gray-400 hover:text-white">
          <ArrowLeft className="h-4 w-4 mr-2" /> Retour
        </Button>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3 mb-8">
          <GraduationCap className="h-8 w-8 text-[#f5a623]" />
          Centre de Formations
        </h1>
        <p className="text-gray-400 mb-8">FédéCP & BIONIC™ - Devenez un chasseur expert</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Formation Sécurité</CardTitle>
              <CardDescription>Cours obligatoire pour le permis de chasse</CardDescription>
            </CardHeader>
            <CardContent>
              <a href="https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/" target="_blank" rel="noopener noreferrer">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  <ExternalLink className="h-4 w-4 mr-2" /> Accéder
                </Button>
              </a>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Formation Piégeage</CardTitle>
              <CardDescription>Techniques de piégeage responsable</CardDescription>
            </CardHeader>
            <CardContent>
              <a href="https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/" target="_blank" rel="noopener noreferrer">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                  <ExternalLink className="h-4 w-4 mr-2" /> Accéder
                </Button>
              </a>
            </CardContent>
          </Card>
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="text-white">Formation BIONIC™</CardTitle>
              <CardDescription>Analyse de territoire avancée</CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full btn-golden text-black">Commencer</Button>
            </CardContent>
          </Card>
        </div>
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
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
