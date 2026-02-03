// AnalyzerModule.jsx - Module Click & Analyse Intelligent avec boutons sticky
import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
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
import { 
  FlaskConical, 
  Search,
  FileText,
  Award,
  Star,
  DollarSign,
  Droplet,
  Leaf,
  Shield,
  Clock,
  CloudRain,
  CheckCircle,
  AlertTriangle,
  ExternalLink,
  Mail,
  Download,
  Loader2,
  ChevronRight,
  Info,
  Users,
  Edit,
  ArrowLeft,
  Home,
  Building2,
  MapPin,
  Tent,
  RefreshCw,
  BookOpen,
  Sparkles,
  Target,
  ShoppingCart,
  GitCompare,
  Zap,
  TrendingUp,
  ArrowRight,
  ScanLine
} from "lucide-react";
import { toast } from "sonner";
import { useLanguage } from '@/contexts/LanguageContext';
import TerritoryInventory from './TerritoryInventory';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Get session ID
const getSessionId = () => {
  let sessionId = localStorage.getItem('scent_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('scent_session_id', sessionId);
  }
  return sessionId;
};

// Pastille Component
const Pastille = ({ type, label, size = "normal" }) => {
  const colors = {
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    red: "bg-red-500"
  };
  const icons = {
    green: "🟢",
    yellow: "🟡",
    red: "🔴"
  };
  
  return (
    <div className={`flex items-center gap-2 ${size === "large" ? "scale-125" : ""}`}>
      <span className={size === "large" ? "text-3xl" : "text-2xl"}>{icons[type]}</span>
      <span className={`px-3 py-1 rounded-full text-white font-semibold ${colors[type]} ${size === "large" ? "text-lg" : ""}`}>
        {label}
      </span>
    </div>
  );
};

// Score Gauge Component
const ScoreGauge = ({ score, maxScore = 10, size = "normal" }) => {
  const percentage = (score / maxScore) * 100;
  const color = score >= 7.5 ? "bg-green-500" : score >= 5 ? "bg-yellow-500" : "bg-red-500";
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className={`font-bold text-white ${size === "large" ? "text-5xl" : "text-4xl"}`}>{score}</span>
        <span className="text-gray-400">/ {maxScore}</span>
      </div>
      <Progress value={percentage} className={`${size === "large" ? "h-4" : "h-3"} ${color}`} />
    </div>
  );
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

// ============================================
// STICKY SIDEBAR BUTTONS COMPONENT - Enhanced
// ============================================
const StickySidebarButtons = ({ 
  onAnalyzeClick, 
  onCompareClick, 
  isAnalyzing, 
  hasDetectedProduct,
  detectedProduct 
}) => {
  const [analyzeClicked, setAnalyzeClicked] = useState(false);
  const [compareClicked, setCompareClicked] = useState(false);

  const handleAnalyzeClick = () => {
    setAnalyzeClicked(true);
    setTimeout(() => setAnalyzeClicked(false), 300);
    onAnalyzeClick();
  };

  const handleCompareClick = () => {
    setCompareClicked(true);
    setTimeout(() => setCompareClicked(false), 300);
    onCompareClick();
  };

  return (
    <>
      {/* Desktop Sidebar - Right side */}
      <div className="fixed right-0 top-1/2 -translate-y-1/2 z-40 hidden md:flex flex-col gap-4 pr-2">
        {/* ANALYSER Button */}
        <button
          onClick={handleAnalyzeClick}
          disabled={isAnalyzing}
          className={`group relative flex flex-col items-center justify-center transition-all duration-300 shadow-2xl
            ${analyzeClicked ? 'scale-90' : 'hover:scale-105'}
            ${hasDetectedProduct ? 'animate-pulse hover:animate-none' : ''}
            w-24 h-36 rounded-l-2xl
            bg-gradient-to-b from-[#f5a623] to-[#d4850e] hover:from-[#f7c857] hover:to-[#f5a623]
          `}
          style={{
            boxShadow: hasDetectedProduct 
              ? '0 0 30px rgba(245, 166, 35, 0.5), -5px 0 20px rgba(245, 166, 35, 0.3)' 
              : '-5px 0 20px rgba(245, 166, 35, 0.2)'
          }}
          data-testid="sticky-analyze-btn"
        >
          {/* Glow indicator */}
          <div className={`absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-16 rounded-l-full transition-all duration-300 ${
            hasDetectedProduct ? 'bg-[#f7c857] opacity-100' : 'bg-[#f5a623] opacity-50 group-hover:opacity-100'
          }`} />
          
          {/* Icon */}
          {isAnalyzing ? (
            <Loader2 className="h-10 w-10 text-black animate-spin" />
          ) : (
            <FlaskConical className={`h-10 w-10 text-black transition-transform duration-300 ${
              analyzeClicked ? 'scale-125' : 'group-hover:scale-110'
            }`} />
          )}
          
          {/* Text */}
          <span className="text-black font-black text-sm mt-3 tracking-wide text-center leading-tight">
            {isAnalyzing ? "EN COURS..." : "ANALYSER"}
          </span>
          
          {/* Ready indicator */}
          {hasDetectedProduct && !isAnalyzing && (
            <div className="absolute -top-2 -left-2 w-7 h-7 bg-white rounded-full flex items-center justify-center shadow-lg animate-bounce">
              <Zap className="h-4 w-4 text-black" />
            </div>
          )}
        </button>

        {/* COMPARER Button */}
        <button
          onClick={handleCompareClick}
          className={`group relative flex flex-col items-center justify-center transition-all duration-300 shadow-2xl
            ${compareClicked ? 'scale-90' : 'hover:scale-105'}
            w-24 h-36 rounded-l-2xl
            bg-gradient-to-b from-blue-700 to-blue-900 hover:from-blue-600 hover:to-blue-800
          `}
          style={{
            boxShadow: '-5px 0 20px rgba(59, 130, 246, 0.2)'
          }}
          data-testid="sticky-compare-btn"
        >
          {/* Glow indicator */}
          <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-2 h-16 bg-blue-500 rounded-l-full opacity-50 group-hover:opacity-100 transition-opacity" />
          
          {/* Icon - Balance/Scale */}
          <svg 
            className={`h-10 w-10 text-white transition-transform duration-300 ${
              compareClicked ? 'scale-125' : 'group-hover:scale-110'
            }`}
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          >
            <path d="M12 3v18" />
            <path d="M4 9l4-6 4 6" />
            <path d="M12 9l4-6 4 6" />
            <circle cx="6" cy="9" r="2" />
            <circle cx="18" cy="9" r="2" />
            <path d="M4 9h4" />
            <path d="M16 9h4" />
          </svg>
          
          {/* Text */}
          <span className="text-white font-black text-sm mt-3 tracking-wide text-center leading-tight">
            COMPARER
          </span>
        </button>
      </div>

      {/* Mobile Bottom Bar */}
      <div className="fixed bottom-16 left-0 right-0 z-40 md:hidden bg-black/95 backdrop-blur-lg border-t border-white/10 p-3">
        <div className="flex gap-3 max-w-lg mx-auto">
          {/* ANALYSER Button - Mobile */}
          <button
            onClick={handleAnalyzeClick}
            disabled={isAnalyzing}
            className={`flex-1 relative flex items-center justify-center gap-2 py-4 rounded-xl font-black text-black transition-all duration-300
              ${analyzeClicked ? 'scale-95' : 'active:scale-95'}
              ${hasDetectedProduct ? 'ring-2 ring-white ring-offset-2 ring-offset-black' : ''}
              bg-gradient-to-r from-[#f5a623] to-[#d4850e]
            `}
            style={{
              boxShadow: hasDetectedProduct 
                ? '0 4px 20px rgba(245, 166, 35, 0.4)' 
                : '0 4px 15px rgba(245, 166, 35, 0.2)'
            }}
          >
            {isAnalyzing ? (
              <Loader2 className="h-6 w-6 animate-spin" />
            ) : (
              <FlaskConical className="h-6 w-6" />
            )}
            <span className="text-sm tracking-wide">
              {isAnalyzing ? "ANALYSE..." : "ANALYSER"}
            </span>
            {hasDetectedProduct && !isAnalyzing && (
              <Zap className="h-4 w-4 text-white absolute -top-1 -right-1 animate-pulse" />
            )}
          </button>

          {/* COMPARER Button - Mobile */}
          <button
            onClick={handleCompareClick}
            className={`flex-1 flex items-center justify-center gap-2 py-4 rounded-xl font-black text-white transition-all duration-300
              ${compareClicked ? 'scale-95' : 'active:scale-95'}
              bg-gradient-to-r from-blue-700 to-blue-800
            `}
            style={{
              boxShadow: '0 4px 15px rgba(59, 130, 246, 0.2)'
            }}
          >
            <GitCompare className="h-6 w-6" />
            <span className="text-sm tracking-wide">COMPARER</span>
          </button>
        </div>
      </div>
    </>
  );
};

// ============================================
// PRODUCT RESULT CARD - Enhanced for conversion
// ============================================
const ProductResultCard = ({ product, rank, isAnalyzed = false, isBionic = false }) => {
  const pastilleType = product.score >= 75 ? "gold" : product.score >= 50 ? "yellow" : "red";
  
  return (
    <Card className={`relative overflow-hidden transition-all duration-300 hover:scale-[1.02] ${
      isBionic 
        ? "bg-gradient-to-br from-[#f5a623]/20 to-transparent border-2 border-[#f5a623] shadow-[0_0_30px_rgba(245,166,35,0.3)]" 
        : isAnalyzed 
          ? "bg-gradient-to-br from-blue-500/10 to-transparent border-2 border-blue-500"
          : "bg-card border-border"
    }`}>
      {/* Rank Badge */}
      <div className={`absolute top-3 left-3 w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg ${
        isBionic ? "bg-[#f5a623] text-black" : isAnalyzed ? "bg-blue-500 text-white" : "bg-gray-700 text-white"
      }`}>
        #{rank}
      </div>

      {/* Special Badges */}
      {isBionic && (
        <div className="absolute top-3 right-3">
          <Badge className="bg-[#f5a623] text-black font-bold px-3 py-1 animate-pulse">
            <Award className="h-4 w-4 mr-1" /> RECOMMANDÉ
          </Badge>
        </div>
      )}
      {isAnalyzed && (
        <div className="absolute top-3 right-3">
          <Badge className="bg-blue-500 text-white font-bold px-3 py-1">
            <Target className="h-4 w-4 mr-1" /> ANALYSÉ
          </Badge>
        </div>
      )}

      <CardContent className="pt-16 pb-6 px-6">
        {/* Product Image */}
        <div className="relative w-full h-40 mb-4 rounded-lg overflow-hidden bg-black/20">
          <img 
            src={product.image_url} 
            alt={product.name} 
            className="w-full h-full object-cover"
          />
          {/* Score Overlay */}
          <div className={`absolute bottom-2 right-2 px-3 py-1 rounded-full font-bold text-sm ${
            pastilleType === "gold" ? "bg-[#f5a623] text-black" :
            pastilleType === "yellow" ? "bg-yellow-500 text-black" :
            "bg-red-500 text-white"
          }`}>
            {product.score}/100
          </div>
        </div>

        {/* Product Info */}
        <div className="space-y-3">
          <div>
            <p className="text-[#f5a623] text-sm font-medium">{product.brand}</p>
            <h3 className="text-white font-bold text-lg leading-tight">{product.name}</h3>
          </div>

          {/* Price Section */}
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">${product.price}</span>
            {product.price_with_shipping && (
              <span className="text-sm text-gray-400">
                (${product.price_with_shipping} avec transport)
              </span>
            )}
          </div>

          {/* Advantages */}
          {product.advantages && product.advantages.length > 0 && (
            <div className="space-y-1 pt-2 border-t border-border">
              {product.advantages.slice(0, 4).map((adv, idx) => (
                <div key={idx} className="flex items-start gap-2 text-sm">
                  <CheckCircle className={`h-4 w-4 flex-shrink-0 mt-0.5 ${isBionic ? "text-[#f5a623]" : "text-green-500"}`} />
                  <span className="text-gray-300">{adv}</span>
                </div>
              ))}
            </div>
          )}

          {/* Category Badge */}
          <div className="flex items-center gap-2 flex-wrap">
            {product.rainproof && <Badge variant="outline" className="text-cyan-400 border-cyan-400"><CloudRain className="h-3 w-3 mr-1" />Rainproof</Badge>}
            {product.certified && <Badge variant="outline" className="text-green-400 border-green-400"><Shield className="h-3 w-3 mr-1" />Certifié</Badge>}
            {product.attraction_days && (
              <Badge variant="outline" className="text-purple-400 border-purple-400">
                <Clock className="h-3 w-3 mr-1" />{product.attraction_days}j
              </Badge>
            )}
          </div>

          {/* CTA Button */}
          <Button 
            className={`w-full mt-4 font-bold text-lg h-14 transition-all duration-300 ${
              isBionic 
                ? "bg-gradient-to-r from-[#f5a623] to-[#d4850e] hover:from-[#d4850e] hover:to-[#f5a623] text-black shadow-lg hover:shadow-[#f5a623]/50" 
                : "bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white"
            } group`}
            onClick={() => product.buy_link && window.open(product.buy_link, '_blank')}
            data-testid={`order-btn-${rank}`}
          >
            <ShoppingCart className="h-5 w-5 mr-2 group-hover:animate-bounce" />
            COMMANDER
            <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// COMPARISON TABLE (Enhanced)
// ============================================
const ComparisonTable = ({ comparison }) => {
  if (!comparison) return null;
  
  const { bionic_product, competitor_1, competitor_2, comparison_table } = comparison;
  
  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="border-border">
            <TableHead className="text-gray-400 w-1/4">Critère</TableHead>
            <TableHead className="text-center bg-green-500/5 border-l-2 border-r-2 border-[#f5a623]">
              <div className="space-y-2">
                <img src={bionic_product.image_url} alt={bionic_product.name} className="w-16 h-16 object-cover rounded-lg mx-auto border-2 border-[#f5a623]" />
                <p className="font-bold text-[#f5a623]">{bionic_product.name}</p>
                <Badge className="bg-[#f5a623]/20 text-[#f5a623]">Profil scientifique complet</Badge>
              </div>
            </TableHead>
            <TableHead className="text-center">
              <div className="space-y-2">
                <img src={competitor_1.image_url} alt={competitor_1.name} className="w-16 h-16 object-cover rounded-lg mx-auto" />
                <p className="font-semibold text-white">{competitor_1.name}</p>
                <Badge variant="outline">{competitor_1.brand}</Badge>
              </div>
            </TableHead>
            <TableHead className="text-center">
              <div className="space-y-2">
                <img src={competitor_2.image_url} alt={competitor_2.name} className="w-16 h-16 object-cover rounded-lg mx-auto" />
                <p className="font-semibold text-white">{competitor_2.name}</p>
                <Badge variant="outline">{competitor_2.brand}</Badge>
              </div>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {comparison_table.map((row, index) => (
            <TableRow key={index} className="border-border">
              <TableCell className="font-medium text-gray-300">{row.criterion}</TableCell>
              <TableCell className="text-center bg-green-500/5 border-l-2 border-r-2 border-[#f5a623] font-bold text-white">
                {row.bionic}
              </TableCell>
              <TableCell className="text-center text-gray-300">{row.competitor_1}</TableCell>
              <TableCell className="text-center text-gray-300">{row.competitor_2}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

// ============================================
// EMAIL CONSENT MODAL
// ============================================
const EmailConsentModal = ({ isOpen, onClose, reportId, onSubmit }) => {
  // Initialize form data from saved profile
  const initializeFormData = () => {
    const savedProfile = getClientProfile();
    return {
      name: savedProfile?.name || "",
      email: savedProfile?.email || "",
      region: savedProfile?.region || "",
      phone: savedProfile?.phone || "",
      consent: false,
      rememberMe: true
    };
  };
  
  const [formData, setFormData] = useState(initializeFormData);
  const [loading, setLoading] = useState(false);
  
  // Check if returning user based on saved profile
  const savedProfile = getClientProfile();
  const isReturningUser = !!savedProfile?.name;
  
  const handleSubmit = async () => {
    if (!formData.consent) {
      toast.error("Veuillez accepter les conditions");
      return;
    }
    
    if (!formData.name || !formData.email) {
      toast.error("Veuillez remplir les champs obligatoires");
      return;
    }
    
    setLoading(true);
    try {
      if (formData.rememberMe) {
        saveClientProfile({
          name: formData.name,
          email: formData.email,
          region: formData.region,
          phone: formData.phone
        });
      }
      
      await axios.post(`${API}/analyze/consent`, {
        name: formData.name,
        email: formData.email,
        region: formData.region,
        consent_marketing: true,
        consent_statistics: true,
        report_id: reportId
      });
      
      toast.success("Rapport envoyé à votre adresse email!");
      onSubmit();
      onClose();
    } catch (error) {
      toast.error("Erreur lors de l'envoi");
    }
    setLoading(false);
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5 text-[#f5a623]" />
            Recevoir votre rapport
          </DialogTitle>
          <DialogDescription>
            {isReturningUser 
              ? "Vos informations ont été reconnues automatiquement."
              : "Entrez vos coordonnées pour recevoir le rapport complet."
            }
          </DialogDescription>
        </DialogHeader>
        
        {isReturningUser && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
            <div>
              <p className="text-green-400 font-medium text-sm">Bienvenue de retour!</p>
              <p className="text-gray-400 text-xs">Informations pré-remplies.</p>
            </div>
          </div>
        )}
        
        <div className="space-y-4 py-4">
          <div>
            <Label>Nom complet *</Label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="bg-background border-border"
              placeholder="Jean Dupont"
            />
          </div>
          <div>
            <Label>Adresse courriel *</Label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="bg-background border-border"
              placeholder="jean@exemple.com"
            />
          </div>
          <div>
            <Label>Région</Label>
            <Select value={formData.region || "none"} onValueChange={(value) => setFormData({...formData, region: value === "none" ? "" : value})}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Sélectionnez votre région" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Sélectionnez votre région</SelectItem>
                <SelectItem value="quebec">Québec</SelectItem>
                <SelectItem value="ontario">Ontario</SelectItem>
                <SelectItem value="alberta">Alberta</SelectItem>
                <SelectItem value="bc">Colombie-Britannique</SelectItem>
                <SelectItem value="other_ca">Autre (Canada)</SelectItem>
                <SelectItem value="usa">États-Unis</SelectItem>
                <SelectItem value="other">Autre</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex items-center gap-2 p-3 bg-[#f5a623]/10 rounded-lg">
            <Checkbox
              checked={formData.rememberMe}
              onCheckedChange={(checked) => setFormData({...formData, rememberMe: checked})}
            />
            <label className="text-[#f5a623] text-sm cursor-pointer flex items-center gap-2">
              <Star className="h-4 w-4" />
              Se souvenir de moi
            </label>
          </div>
          
          <div className="flex items-start gap-2">
            <Checkbox
              checked={formData.consent}
              onCheckedChange={(checked) => setFormData({...formData, consent: checked})}
            />
            <label className="text-gray-300 text-sm cursor-pointer">
              J&apos;accepte l&apos;utilisation de mes données pour l&apos;envoi du rapport et les analyses statistiques. *
            </label>
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Annuler</Button>
          <Button 
            className="btn-golden text-black"
            onClick={handleSubmit}
            disabled={!formData.consent || !formData.name || !formData.email || loading}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Mail className="h-4 w-4 mr-2" />}
            Envoyer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// MAIN ANALYZER MODULE COMPONENT
// ============================================
const AnalyzerModule = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [productName, setProductName] = useState("");
  const [productType, setProductType] = useState("");
  const [categories, setCategories] = useState([]);
  const [analysisCategories, setAnalysisCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedSubcategory, setSelectedSubcategory] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const [displayProducts, setDisplayProducts] = useState(null);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [activeTab, setActiveTab] = useState("categories"); // Start with categories selection
  const [refreshing, setRefreshing] = useState(false);
  
  // Load categories for product type selection
  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API}/analyze/categories`);
      setCategories(response.data.categories);
    } catch (error) {
      console.error("Error loading categories:", error);
    }
  };
  
  // Load analysis categories for menu
  const loadAnalysisCategories = async () => {
    try {
      const response = await axios.get(`${API}/analysis-categories`);
      setAnalysisCategories(response.data.categories);
    } catch (error) {
      console.error("Error loading analysis categories:", error);
    }
  };
  
  // Refresh/Reset function
  const handleRefresh = async () => {
    setRefreshing(true);
    setProductName("");
    setProductType("");
    setSelectedCategory(null);
    setSelectedSubcategory(null);
    setReport(null);
    setActiveTab("categories");
    await loadCategories();
    await loadAnalysisCategories();
    setRefreshing(false);
    toast.success(t('common_refresh') || 'Actualisé');
  };

  const [activeView, setActiveView] = useState("input"); // input, analyzing, results
  const [showCompareModal, setShowCompareModal] = useState(false);
  
  // Smart detection state
  const [smartDetection, setSmartDetection] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);
  
  // Load categories on mount
  useEffect(() => {
    loadCategories();
  }, []);
  
  useEffect(() => {
    loadAnalysisCategories();
  }, []);
  
  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    setSelectedSubcategory(null);
  };
  
  const handleSubcategorySelect = (subcategory) => {
    setSelectedSubcategory(subcategory);
    // Set product type based on subcategory
    setProductType(subcategory.id);
    // Move to input tab
    setActiveTab("input");
  };
  
  const handleBackToCategories = () => {
    setSelectedCategory(null);
    setSelectedSubcategory(null);
    setActiveTab("categories");
  };
  
  // Smart detection when product name changes (debounced)
  useEffect(() => {
    const detectProduct = async () => {
      if (productName.trim().length < 3) {
        setSmartDetection(null);
        return;
      }
      
      setIsDetecting(true);
      try {
        const response = await axios.post(`${API}/analyze/smart-detect`, {
          product_name: productName,
          product_description: "",
          product_tags: []
        });
        setSmartDetection(response.data);
        
        // Auto-set category if confidence is high
        if (response.data.category_confidence > 60) {
          setProductType(response.data.detected_category);
        }
      } catch (error) {
        console.error("Smart detection error:", error);
      }
      setIsDetecting(false);
    };
    
    const timeoutId = setTimeout(detectProduct, 500);
    return () => clearTimeout(timeoutId);
  }, [productName]);
  
  // Main analysis function
  const handleAnalyze = async () => {
    if (!productName.trim()) {
      toast.error("Veuillez entrer le nom du produit");
      return;
    }
    
    setAnalyzing(true);
    setActiveView("analyzing");
    
    try {
      // Use quick analysis for pre-filled data
      const response = await axios.post(`${API}/analyze/quick`, {
        product_name: productName,
        detected_category: productType || smartDetection?.detected_category || "granules",
        session_id: getSessionId()
      });
      
      setReport(response.data.report);
      setDisplayProducts(response.data.display_products);
      setActiveView("results");
      toast.success("Analyse terminée!");
      
      // Learn any new keywords if user corrected the category
      if (smartDetection && productType !== smartDetection.detected_category) {
        try {
          await axios.post(`${API}/analyze/learn-keyword`, {
            keyword: productName.toLowerCase().split(' ')[0],
            category: productType,
            source: "user_correction"
          });
        } catch (e) {
          console.log("Keyword learning skipped");
        }
      }
    } catch (error) {
      toast.error("Erreur lors de l'analyse: " + (error.response?.data?.detail || error.message));
      setActiveView("input");
    }
    
    setAnalyzing(false);
  };
  
  const resetAnalysis = () => {
    setReport(null);
    setDisplayProducts(null);
    setProductName("");
    setProductType("");
    setSelectedCategory(null);
    setSelectedSubcategory(null);
    setActiveTab("categories");
  };
  
  return (
    <main className="pt-20 min-h-screen bg-background relative pb-24 md:pb-8">
      {/* Sticky Sidebar Buttons */}
      <StickySidebarButtons
        onAnalyzeClick={handleStickyAnalyze}
        onCompareClick={handleStickyCompare}
        isAnalyzing={analyzing}
        hasDetectedProduct={smartDetection?.category_confidence > 50}
        detectedProduct={smartDetection}
      />
      
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 md:pr-32">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-[#f5a623]/10 px-4 py-2 rounded-full mb-4">
            <FlaskConical className="h-5 w-5 text-[#f5a623]" />
            <span className="text-[#f5a623] font-semibold">Click & Analyse Intelligent</span>
            <Sparkles className="h-4 w-4 text-[#f5a623] animate-pulse" />
          </div>
          <h1 className="golden-text text-4xl font-bold mb-4">Analysez votre attractant</h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Détection automatique • Catégorisation intelligente • Analyse instantanée • 
            Recommandations personnalisées
          </p>
          {/* Refresh Button */}
          <Button 
            variant="outline" 
            onClick={handleRefresh}
            disabled={refreshing}
            className="mt-3"
            data-testid="refresh-analyzer"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            {t('common_refresh')}
          </Button>
        </div>
        
        {/* Main Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-4 bg-card border border-border">
            <TabsTrigger 
              value="categories" 
              className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
              data-testid="tab-produits"
            >
              <FlaskConical className="h-4 w-4 mr-2" />
              Produits
            </TabsTrigger>
            <TabsTrigger 
              value="pourvoyeurs" 
              className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
              data-testid="tab-pourvoyeurs"
            >
              <Tent className="h-4 w-4 mr-2" />
              Pourvoyeurs
            </TabsTrigger>
          </TabsList>

          {/* Categories Selection Tab */}
          <TabsContent value="categories" className="space-y-3">
            <Card className="bg-card border-border max-w-5xl mx-auto">
              <CardHeader className="pb-2 pt-4">
                <CardTitle className="text-white flex items-center gap-2 text-lg">
                  <FlaskConical className="h-5 w-5 text-[#f5a623]" />
                  {selectedCategory ? `${selectedCategory.icon} ${selectedCategory.name}` : "Que souhaitez-vous analyser?"}
                </CardTitle>
                <CardDescription className="text-sm">
                  {selectedCategory 
                    ? "Sélectionnez une sous-catégorie pour préciser votre recherche"
                    : "Choisissez la catégorie de produit que vous souhaitez analyser"
                  }
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-2 pb-4">
                {/* Back button when subcategories are shown */}
                {selectedCategory && (
                  <Button 
                    variant="ghost" 
                    onClick={() => setSelectedCategory(null)} 
                    className="mb-3 text-[#f5a623] hover:text-[#f5a623]/80 h-8 text-sm"
                  >
                    ← Retour aux catégories
                  </Button>
                )}
                
                {/* Main Categories Grid - Compact */}
                {!selectedCategory ? (
                  <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                    {analysisCategories.map((category) => (
                      <button
                        key={category.id}
                        onClick={() => handleCategorySelect(category)}
                        className="flex flex-col items-center justify-center p-2 md:p-3 rounded-lg border border-border bg-background hover:border-[#f5a623] hover:bg-[#f5a623]/5 transition-all group"
                        data-testid={`category-${category.id}`}
                      >
                        <span className="text-2xl mb-1 group-hover:scale-110 transition-transform">
                          {category.icon}
                        </span>
                        <span className="text-white text-xs font-medium text-center leading-tight">
                          {category.name}
                        </span>
                        <span className="text-gray-500 text-[10px] mt-0.5">
                          {category.subcategories?.length || 0} types
                        </span>
                      </button>
                    ))}
                  </div>
                ) : (
                  /* Subcategories Grid */
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {selectedCategory.subcategories?.map((subcategory) => (
                      <button
                        key={subcategory.id}
                        onClick={() => handleSubcategorySelect(subcategory)}
                        className="flex flex-col items-center justify-center p-3 rounded-lg border border-border bg-background hover:border-[#f5a623] hover:bg-[#f5a623]/5 transition-all group"
                        data-testid={`subcategory-${subcategory.id}`}
                      >
                        <span className="text-xl mb-1 group-hover:scale-110 transition-transform">
                          {subcategory.icon}
                        </span>
                        <span className="text-white text-xs font-medium text-center">
                          {subcategory.name}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
                
                {/* Skip to direct input - Compact inline */}
                <div className="mt-4 pt-3 border-t border-border flex items-center justify-center gap-3">
                  <span className="text-gray-400 text-xs">Vous connaissez déjà le produit?</span>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setActiveTab("input")}
                    className="border-[#f5a623] text-[#f5a623] hover:bg-[#f5a623]/10 h-8 text-xs"
                  >
                    <Search className="h-3 w-3 mr-1" />
                    Entrer le nom
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Input Tab */}
          <TabsContent value="input" className="space-y-6">
        {/* ============================================ */}
        {/* INPUT VIEW */}
        {/* ============================================ */}
        {activeView === "input" && (
          <div className="space-y-6">
            <Card className="bg-card border-border max-w-2xl mx-auto">
              <CardHeader>
                {/* Selected Category/Subcategory Breadcrumb */}
                {(selectedCategory || selectedSubcategory) && (
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={handleBackToCategories}
                      className="text-gray-400 hover:text-white p-0 h-auto"
                    >
                      Catégories
                    </Button>
                    {selectedCategory && (
                      <>
                        <ChevronRight className="h-4 w-4 text-gray-500" />
                        <span className="text-[#f5a623]">{selectedCategory.icon} {selectedCategory.name}</span>
                      </>
                    )}
                    {selectedSubcategory && (
                      <>
                        <ChevronRight className="h-4 w-4 text-gray-500" />
                        <span className="text-white">{selectedSubcategory.icon} {selectedSubcategory.name}</span>
                      </>
                    )}
                  </div>
                )}
                <CardTitle className="text-white flex items-center gap-2">
                  <Search className="h-5 w-5 text-[#f5a623]" />
                  Entrez le nom du produit
                </CardTitle>
                <CardDescription>
                  Notre IA détecte automatiquement le type et prépare l&apos;analyse.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Product Name Input */}
                <div className="space-y-2">
                  <Label className="text-white text-lg">Nom du produit *</Label>
                  <div className="relative">
                    <Input
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      className="bg-background border-border text-white text-lg h-14 pr-12"
                      placeholder="Ex: Tink's #69 Doe-in-Rut, Code Blue Apple Jelly..."
                      data-testid="product-name-input"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && productName.trim()) {
                          handleAnalyze();
                        }
                      }}
                    />
                    {isDetecting && (
                      <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[#f5a623] animate-spin" />
                    )}
                  </div>
                  <p className="text-gray-500 text-sm">
                    Entrez le nom du produit. Notre IA détecte automatiquement le type et prépare l'analyse.
                    <span className="text-[#f5a623] font-medium"> Utilisez les onglets latéraux pour lancer l'analyse.</span>
                  </p>
                </div>
                
                {/* Smart Detection Results */}
                {smartDetection && (
                  <div className={`p-4 rounded-lg border ${
                    smartDetection.category_confidence > 70 
                      ? "bg-[#f5a623]/10 border-[#f5a623]/30" 
                      : "bg-yellow-500/10 border-yellow-500/30"
                  }`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          {smartDetection.category_confidence > 70 ? (
                            <CheckCircle className="h-5 w-5 text-[#f5a623]" />
                          ) : (
                            <AlertTriangle className="h-5 w-5 text-yellow-500" />
                          )}
                          <span className={`font-semibold ${smartDetection.category_confidence > 70 ? "text-[#f5a623]" : "text-yellow-400"}`}>
                            Détection automatique
                          </span>
                        </div>
                        <div className="space-y-1 text-sm">
                          <p className="text-gray-300">
                            <span className="text-gray-500">Catégorie:</span>{" "}
                            <Badge className="ml-1">{smartDetection.detected_category}</Badge>
                            <span className="text-gray-500 ml-2">({smartDetection.category_confidence}% confiance)</span>
                          </p>
                          {smartDetection.detected_animal && (
                            <p className="text-gray-300">
                              <span className="text-gray-500">Animal ciblé:</span>{" "}
                              <Badge variant="outline" className="ml-1">{smartDetection.detected_animal}</Badge>
                            </p>
                          )}
                          {smartDetection.keywords_matched.length > 0 && (
                            <p className="text-gray-400 text-xs mt-2">
                              Mots-clés: {smartDetection.keywords_matched.slice(0, 5).join(", ")}
                            </p>
                          )}
                        </div>
                      </div>
                      <Zap className="h-8 w-8 text-[#f5a623] opacity-50" />
                    </div>
                  </div>
                )}
                
                {/* Category Selection (can override) */}
                <div className="space-y-2">
                  <Label className="text-gray-400 flex items-center gap-2">
                    Type de produit {selectedSubcategory ? "(pré-sélectionné)" : "(optionnel)"}
                    <Info className="h-4 w-4" />
                    Type de produit
                    {smartDetection && <span className="text-xs text-gray-500">(pré-rempli, modifiable)</span>}
                  </Label>
                  <Select value={productType || "auto"} onValueChange={(value) => setProductType(value === "auto" ? "" : value)}>
                    <SelectTrigger className="bg-background border-border">
                      <SelectValue placeholder="Détection automatique" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Détection automatique</SelectItem>
                      {categories.map((cat) => (
                        <SelectItem key={cat.id} value={cat.id}>
                          {cat.icon} {cat.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Category Pills */}
                <div className="flex flex-wrap gap-2">
                  {categories.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => setProductType(productType === cat.id ? "" : cat.id)}
                      className={`px-3 py-1 rounded-full text-sm transition-colors ${
                        productType === cat.id 
                          ? "bg-[#f5a623] text-black" 
                          : "bg-background text-gray-400 hover:bg-gray-800"
                      }`}
                    >
                      {cat.icon} {cat.name}
                    </button>
                  ))}
                </div>
                
                {/* Analyze Button */}
                <Button
                  onClick={handleAnalyze}
                  className="w-full btn-golden text-black font-semibold h-14 text-lg"
                  disabled={!productName.trim() || analyzing}
                  data-testid="analyze-btn"
                >
                  {analyzing ? (
                    <><Loader2 className="h-5 w-5 animate-spin mr-2" /> Analyse en cours...</>
                  ) : (
                    <><FlaskConical className="h-5 w-5 mr-2" /> Analyser le produit</>
                  )}
                </Button>
                
                {/* Back to Categories Button */}
                <Button
                  variant="ghost"
                  onClick={handleBackToCategories}
                  className="w-full text-gray-400 hover:text-white"
                >
                  ← Changer de catégorie
                </Button>
                
                {/* Info Box */}
                {/* Info Box - Updated */}
                <div className="bg-gradient-to-r from-[#f5a623]/10 to-blue-500/10 p-4 rounded-lg border border-[#f5a623]/20">
                  <div className="flex items-start gap-3">
                    <div className="flex gap-2 mt-1">
                      <div className="w-8 h-8 rounded-lg bg-[#f5a623] flex items-center justify-center">
                        <FlaskConical className="h-4 w-4 text-black" />
                      </div>
                      <div className="w-8 h-8 rounded-lg bg-blue-700 flex items-center justify-center">
                        <GitCompare className="h-4 w-4 text-white" />
                      </div>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold mb-1 flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-[#f5a623]" />
                        Utilisez les onglets à droite
                      </h4>
                      <p className="text-gray-400 text-sm">
                        Cliquez sur <span className="text-[#f5a623] font-bold">ANALYSER</span> pour lancer l'analyse instantanée, 
                        ou sur <span className="text-blue-400 font-bold">COMPARER</span> pour voir la comparaison des produits.
                      </p>
                    </div>
                  </div>
                </div>

                {/* What's included */}
                <div className="bg-background p-4 rounded-lg text-sm text-gray-400">
                  <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-[#f5a623]" />
                    Ce que l&apos;analyse intelligente inclut:
                  </h4>
                  <ul className="space-y-1 list-disc list-inside">
                    <li>Détection automatique du type et catégorie</li>
                    <li>Évaluation sur 13 critères scientifiques</li>
                    <li>Score d'attraction sur 10</li>
                    <li>Analyse des prix et rapport performance/prix</li>
                    <li>Recommandations d'amélioration</li>
                    <li>Score d&apos;attraction avec pastille colorée</li>
                    <li>Affichage des 3 meilleurs produits + BIONIC™</li>
                    <li>Boutons de commande intégrés</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        {/* ============================================ */}
        {/* ANALYZING VIEW */}
        {/* ============================================ */}
        {activeView === "analyzing" && (
          <Card className="bg-card border-border max-w-2xl mx-auto">
            <CardContent className="py-12 text-center">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-[#f5a623]/20 flex items-center justify-center animate-pulse">
                <ScanLine className="h-12 w-12 text-[#f5a623] animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-4">Analyse intelligente en cours...</h2>
              <p className="text-gray-400 mb-6">&quot;{productName}&quot;</p>
              <div className="space-y-3 text-left max-w-sm mx-auto">
                {[
                  "Détection du type de produit",
                  "Catégorisation intelligente",
                  "Analyse des ingrédients",
                  "Calcul du score d&apos;attraction",
                  "Identification des meilleurs produits",
                  "Préparation des recommandations"
                ].map((step, index) => (
                  <div key={index} className="flex items-center gap-3 text-gray-400">
                    <div className="w-6 h-6 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                      <Loader2 className="h-4 w-4 animate-spin text-[#f5a623]" />
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Report Tab */}
          <TabsContent value="report" className="space-y-6">
            {report && (
              <>
                {/* Document Header */}
                <Card className="bg-gradient-to-r from-[#f5a623]/20 to-transparent border-[#f5a623] border-2">
                  <CardContent className="py-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <Badge className="bg-[#f5a623] text-black mb-2">DOCUMENT OFFICIEL</Badge>
                        <h2 className="text-2xl font-bold text-white">BIONIC™</h2>
                        <p className="text-gray-400">Rapport d'analyse scientifique</p>
                      </div>
                      <div className="text-right">
                        <p className="text-gray-400 text-sm">Date: {new Date().toLocaleDateString()}</p>
                        <p className="text-gray-400 text-sm">ID: {report.id?.slice(0, 8)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                {/* Product Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Score Card */}
                  <Card className="bg-card border-border">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Award className="h-5 w-5 text-[#f5a623]" />
                        Score d'attraction
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ScoreGauge score={report.scoring?.total_score || 0} />
                      <div className="mt-4">
                        <Pastille type={report.scoring?.pastille} label={report.scoring?.pastille_label} />
                      </div>
                    </CardContent>
                  </Card>
                  
                  {/* Product Info */}
                  <Card className="bg-card border-border">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <FileText className="h-5 w-5 text-[#f5a623]" />
                        Fiche technique
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Produit:</span>
                        <span className="text-white font-semibold">{report.technical_sheet?.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Type détecté:</span>
                        <Badge className="bg-purple-600">{report.technical_sheet?.detected_type}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Marque:</span>
                        <span className="text-white">{report.technical_sheet?.brand || "Non identifiée"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Prix estimé:</span>
                        <span className="text-[#f5a623]">${report.technical_sheet?.estimated_price || "N/A"}</span>
                      </div>
                      {report.technical_sheet?.confidence_level === "estimated" && (
                        <Badge variant="outline" className="w-full justify-center mt-2">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          Données estimées
                        </Badge>
                      )}
                    </CardContent>
                  </Card>
                  
                  {/* Quick Stats */}
                  <Card className="bg-card border-border">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Star className="h-5 w-5 text-[#f5a623]" />
                        Points clés
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-blue-500" />
                        <span className="text-gray-400">Durée:</span>
                        <span className="text-white">{report.scoring?.criteria_scores?.attraction_days?.toFixed(0) * 6 || "N/A"} jours</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CloudRain className="h-4 w-4 text-cyan-500" />
                        <span className="text-gray-400">Rainproof:</span>
                        <span className="text-white">{report.scientific_analysis?.durability_criteria?.rainproof ? "✅" : "❌"}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4 text-green-500" />
                        <span className="text-gray-400">Feed-Proof:</span>
                        <span className="text-white">{report.scientific_analysis?.durability_criteria?.feed_proof ? "✅" : "❌"}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-yellow-500" />
                        <span className="text-gray-400">Certifié:</span>
                        <span className="text-white">{report.scientific_analysis?.durability_criteria?.certified ? "✅" : "❌"}</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
                
                {/* Pastille Legend */}
                <Card className="bg-card border-border">
                  <CardHeader>
                    <CardTitle className="text-white">Charte des pastilles d'attraction</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center gap-3 p-3 bg-green-500/10 rounded-lg">
                        <span className="text-3xl">🟢</span>
                        <div>
                          <p className="text-white font-semibold">Attraction forte</p>
                          <p className="text-gray-400 text-sm">Score ≥ 7.5/10</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-yellow-500/10 rounded-lg">
                        <span className="text-3xl">🟡</span>
                        <div>
                          <p className="text-white font-semibold">Attraction modérée</p>
                          <p className="text-gray-400 text-sm">Score 5.0 - 7.4/10</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-red-500/10 rounded-lg">
                        <span className="text-3xl">🔴</span>
                        <div>
                          <p className="text-white font-semibold">Attraction faible</p>
                          <p className="text-gray-400 text-sm">Score &lt; 5.0/10</p>
                        </div>
                      </div>
                    </div>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
        
        {/* ============================================ */}
        {/* RESULTS VIEW */}
        {/* ============================================ */}
        {activeView === "results" && report && displayProducts && (
          <div className="space-y-8">
            {/* Result Header */}
            <div className="text-center">
              <Badge className="bg-green-500 text-white mb-4 px-4 py-2 text-lg">
                <CheckCircle className="h-5 w-5 mr-2" />
                Analyse complétée
              </Badge>
              <h2 className="text-3xl font-bold text-white mb-2">
                Résultats pour &quot;{report.product_name}&quot;
              </h2>
              <div className="flex items-center justify-center gap-4 mt-4">
                <ScoreGauge score={report.scoring?.total_score || 0} size="large" />
                <Pastille type={report.scoring?.pastille} label={report.scoring?.pastille_label} size="large" />
              </div>
            </div>
            
            {/* TOP 3 PRODUCTS + BIONIC - Horizontal Display */}
            <div className="bg-gradient-to-r from-[#f5a623]/5 via-transparent to-purple-500/5 p-6 rounded-2xl border border-[#f5a623]/20">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-[#f5a623]" />
                Les meilleurs produits pour vous
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Analyzed Product */}
                <ProductResultCard 
                  product={{
                    name: displayProducts.analyzed.name,
                    brand: "Produit analysé",
                    price: report.technical_sheet?.estimated_price || 25,
                    price_with_shipping: (report.technical_sheet?.estimated_price || 25) + 10,
                    score: Math.round(displayProducts.analyzed.score * 10),
                    image_url: "https://images.unsplash.com/photo-1504173010664-32509aeebb62?w=400",
                    advantages: report.recommendations?.slice(0, 3) || [],
                    attraction_days: report.scoring?.criteria_scores?.attraction_days * 6 || 10
                  }}
                  rank={1}
                  isAnalyzed={true}
                />
                
                {/* BIONIC Product - Always included */}
                <ProductResultCard 
                  product={displayProducts.bionic}
                  rank={2}
                  isBionic={true}
                />
                
                {/* Best Competitor */}
                {displayProducts.top_competitors?.[0] && (
                  <ProductResultCard 
                    product={displayProducts.top_competitors[0]}
                    rank={3}
                  />
                )}
              </div>
            </div>
            
            {/* Detailed Report Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Technical Sheet */}
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <FileText className="h-5 w-5 text-[#f5a623]" />
                    Fiche technique
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Type détecté:</span>
                    <Badge className="bg-purple-600">{report.technical_sheet?.detected_type}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Marque:</span>
                    <span className="text-white">{report.technical_sheet?.brand || "Non identifiée"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Prix estimé:</span>
                    <span className="text-[#f5a623]">${report.technical_sheet?.estimated_price || "N/A"}</span>
                  </div>
                  {report.technical_sheet?.estimated_ingredients?.length > 0 && (
                    <div className="pt-3 border-t border-border">
                      <p className="text-gray-400 text-sm mb-2">Ingrédients estimés:</p>
                      <div className="flex flex-wrap gap-1">
                        {report.technical_sheet.estimated_ingredients.slice(0, 6).map((ing, i) => (
                          <Badge key={i} variant="outline" className="text-xs">{ing}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
              
              {/* Quick Stats */}
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Star className="h-5 w-5 text-[#f5a623]" />
                    Caractéristiques clés
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Clock className="h-5 w-5 text-blue-500" />
                    <span className="text-gray-400">Durée d&apos;attraction:</span>
                    <span className="text-white font-semibold">{Math.round(report.scoring?.criteria_scores?.attraction_days * 6) || "N/A"} jours</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CloudRain className="h-5 w-5 text-cyan-500" />
                    <span className="text-gray-400">Rainproof:</span>
                    <span className="text-white">{report.scientific_analysis?.durability_criteria?.rainproof ? "✅ Oui" : "❌ Non"}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Shield className="h-5 w-5 text-green-500" />
                    <span className="text-gray-400">Feed-Proof:</span>
                    <span className="text-white">{report.scientific_analysis?.durability_criteria?.feed_proof ? "✅ Oui" : "❌ Non"}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Award className="h-5 w-5 text-yellow-500" />
                    <span className="text-gray-400">Certifié:</span>
                    <span className="text-white">{report.scientific_analysis?.durability_criteria?.certified ? "✅ Oui" : "❌ Non"}</span>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            {/* Comparison Table */}
            {report.comparison && (
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white">Tableau comparatif détaillé</CardTitle>
                </CardHeader>
                <CardContent>
                  <ComparisonTable comparison={report.comparison} />
                </CardContent>
              </Card>
            )}
            
            {/* BIONIC Arguments */}
            {report.bionic_arguments?.length > 0 && (
              <Card className="bg-gradient-to-r from-[#f5a623]/10 to-transparent border-[#f5a623]">
                <CardHeader>
                  <CardTitle className="text-[#f5a623] flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Pourquoi choisir BIONIC™?
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {report.bionic_arguments.map((arg, index) => (
                      <li key={index} className="flex items-center gap-2 text-white">
                        <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                        {arg}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
            
            {/* Scientific References */}
            {report.scientific_references?.length > 0 && (
              <Card className="bg-card border-border">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-[#f5a623]" />
                    Références scientifiques
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {report.scientific_references.slice(0, 3).map((section, idx) => (
                    <div key={idx} className="space-y-1">
                      <h4 className="text-[#f5a623] font-semibold text-sm">{section.title}</h4>
                      <ul className="text-xs text-gray-400 space-y-0.5">
                        {section.references.slice(0, 2).map((ref, i) => (
                          <li key={i} className="pl-3 border-l-2 border-gray-700">{ref}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Pourvoyeurs Tab - Territory Inventory */}
          <TabsContent value="pourvoyeurs" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Tent className="h-5 w-5 text-[#f5a623]" />
                  Inventaire National des Territoires
                </CardTitle>
                <CardDescription>
                  Explorez et comparez les ZEC, pourvoiries, clubs et outfitters à travers le Canada.
                  Score BIONIC™ basé sur l'habitat, la pression, le succès et l'accessibilité.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TerritoryInventory />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
            
            {/* Action Buttons */}
            <div className="flex flex-wrap gap-4 justify-center pt-6">
              <Button
                className="btn-golden text-black h-12 px-6"
                onClick={() => setShowEmailModal(true)}
              >
                <Mail className="h-5 w-5 mr-2" />
                Recevoir le rapport par email
              </Button>
              <Button variant="outline" onClick={resetAnalysis} className="h-12 px-6">
                <FlaskConical className="h-5 w-5 mr-2" />
                Nouvelle analyse
              </Button>
              <Button variant="outline" onClick={() => window.print()} className="h-12 px-6">
                <Download className="h-5 w-5 mr-2" />
                Imprimer / PDF
              </Button>
            </div>
            
            {/* Email Modal */}
            <EmailConsentModal
              isOpen={showEmailModal}
              onClose={() => setShowEmailModal(false)}
              reportId={report.id}
              onSubmit={() => toast.success("Rapport envoyé!")}
            />
          </div>
        )}
        
        {/* Compare Modal */}
        <Dialog open={showCompareModal} onOpenChange={setShowCompareModal}>
          <DialogContent className="bg-card border-border text-white max-w-4xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <GitCompare className="h-5 w-5 text-purple-500" />
                Comparaison des produits
              </DialogTitle>
            </DialogHeader>
            <div className="py-4">
              {report?.comparison ? (
                <ComparisonTable comparison={report.comparison} />
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <GitCompare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Lancez d&apos;abord une analyse pour voir la comparaison.</p>
                </div>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCompareModal(false)}>Fermer</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </main>
  );
};

export default AnalyzerModule;
