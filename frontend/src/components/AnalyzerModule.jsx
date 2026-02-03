// AnalyzerModule.jsx - Module Click & Analyse simplifié
import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft, Search, FlaskConical, Star, CheckCircle, Loader2, 
  TrendingUp, AlertTriangle, Info, Package, RefreshCw
} from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

// Score Gauge Component
const ScoreGauge = ({ score, size = "default" }) => {
  const getColor = (s) => {
    if (s >= 8) return "text-green-500";
    if (s >= 5) return "text-yellow-500";
    return "text-red-500";
  };
  
  return (
    <div className={`flex items-center gap-2 ${size === "large" ? "text-4xl" : "text-2xl"}`}>
      <Star className={`${getColor(score)} ${size === "large" ? "h-8 w-8" : "h-6 w-6"}`} />
      <span className={`font-bold ${getColor(score)}`}>{score.toFixed(1)}/10</span>
    </div>
  );
};

const AnalyzerModule = () => {
  const navigate = useNavigate();
  const { t, brand } = useLanguage();
  
  // States
  const [productName, setProductName] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const [products, setProducts] = useState([]);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState("input"); // input, analyzing, results

  // Fetch products on mount
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get(`${API}/products/top?limit=20`);
        setProducts(response.data);
      } catch (err) {
        console.error("Error fetching products:", err);
      }
    };
    fetchProducts();
  }, []);

  // Handle analysis
  const handleAnalyze = async () => {
    if (!productName.trim()) {
      toast.error("Veuillez entrer un nom de produit");
      return;
    }

    setAnalyzing(true);
    setActiveView("analyzing");
    setError(null);

    try {
      const response = await axios.post(`${API}/analyze/product`, {
        product_name: productName
      });
      
      setReport(response.data);
      setActiveView("results");
      toast.success("Analyse terminée!");
    } catch (err) {
      console.error("Error analyzing:", err);
      setError("Erreur lors de l'analyse. Veuillez réessayer.");
      setActiveView("input");
      toast.error("Erreur lors de l'analyse");
    } finally {
      setAnalyzing(false);
    }
  };

  // Reset analysis
  const resetAnalysis = () => {
    setProductName("");
    setReport(null);
    setError(null);
    setActiveView("input");
  };

  return (
    <main className="pt-20 min-h-screen bg-background" data-testid="analyzer-module">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold golden-text mb-4 flex items-center justify-center gap-3">
            <FlaskConical className="h-10 w-10 text-[#f5a623]" />
            Analyseur BIONIC™
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Entrez le nom d'un attractant ou leurre pour obtenir une analyse scientifique complète 
            basée sur nos 13 critères d'évaluation.
          </p>
        </div>

        {/* Input View */}
        {activeView === "input" && (
          <Card className="bg-card border-border max-w-2xl mx-auto">
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex gap-4">
                  <Input
                    placeholder="Ex: Buck Bomb, Code Blue, Tink's 69..."
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
                    className="flex-1 bg-background border-border text-white"
                    data-testid="product-input"
                  />
                  <Button 
                    onClick={handleAnalyze} 
                    disabled={analyzing || !productName.trim()}
                    className="btn-golden text-black px-8"
                    data-testid="analyze-button"
                  >
                    {analyzing ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <>
                        <Search className="h-5 w-5 mr-2" />
                        Analyser
                      </>
                    )}
                  </Button>
                </div>
                
                {error && (
                  <div className="flex items-center gap-2 text-red-400 text-sm">
                    <AlertTriangle className="h-4 w-4" />
                    {error}
                  </div>
                )}
              </div>
              
              {/* Popular Products */}
              <div className="mt-8">
                <h3 className="text-white font-semibold mb-4">Produits populaires</h3>
                <div className="flex flex-wrap gap-2">
                  {products.slice(0, 8).map((product) => (
                    <Badge 
                      key={product.id}
                      className="bg-gray-700 hover:bg-[#f5a623] hover:text-black cursor-pointer transition-colors"
                      onClick={() => setProductName(product.name)}
                    >
                      {product.name}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analyzing View */}
        {activeView === "analyzing" && (
          <Card className="bg-card border-border max-w-2xl mx-auto">
            <CardContent className="py-12 text-center">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-[#f5a623]/20 flex items-center justify-center animate-pulse">
                <FlaskConical className="h-12 w-12 text-[#f5a623] animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-4">Analyse en cours...</h2>
              <p className="text-gray-400 mb-6">"{productName}"</p>
              <div className="space-y-3 text-left max-w-sm mx-auto">
                {[
                  "Détection du type de produit",
                  "Analyse des ingrédients",
                  "Calcul du score d'attraction",
                  "Préparation des recommandations"
                ].map((step, index) => (
                  <div key={index} className="flex items-center gap-3 text-gray-400">
                    <div className="w-6 h-6 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                      <Loader2 className="h-4 w-4 animate-spin text-[#f5a623]" />
                    </div>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results View */}
        {activeView === "results" && report && (
          <div className="space-y-8">
            {/* Result Header */}
            <div className="text-center">
              <Badge className="bg-green-500 text-white mb-4 px-4 py-2 text-lg">
                <CheckCircle className="h-5 w-5 mr-2" />
                Analyse complétée
              </Badge>
              <h2 className="text-3xl font-bold text-white mb-2">
                Résultats pour "{report.product_name || productName}"
              </h2>
              <div className="flex items-center justify-center gap-4 mt-4">
                <ScoreGauge score={report.scoring?.total_score || 7.5} size="large" />
              </div>
            </div>

            {/* Score Details */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">Détails de l'analyse</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="p-4 bg-background rounded-lg">
                    <p className="text-gray-400 text-sm">Catégorie</p>
                    <p className="text-white font-semibold">{report.detected_category || "Attractant"}</p>
                  </div>
                  <div className="p-4 bg-background rounded-lg">
                    <p className="text-gray-400 text-sm">Espèce cible</p>
                    <p className="text-white font-semibold">{report.detected_animal || "Cerf"}</p>
                  </div>
                  <div className="p-4 bg-background rounded-lg">
                    <p className="text-gray-400 text-sm">Score qualité</p>
                    <p className="text-[#f5a623] font-semibold">{(report.scoring?.total_score || 7.5).toFixed(1)}/10</p>
                  </div>
                </div>
                
                {/* Recommendation */}
                <div className="mt-6 p-4 bg-[#f5a623]/10 rounded-lg border border-[#f5a623]/30">
                  <div className="flex items-start gap-3">
                    <TrendingUp className="h-6 w-6 text-[#f5a623] mt-1" />
                    <div>
                      <p className="text-white font-semibold">Recommandation</p>
                      <p className="text-gray-400">
                        {report.recommendation || "Ce produit présente de bonnes caractéristiques d'attraction. Idéal pour la chasse au cerf en saison."}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommended Products */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-white">Produits similaires recommandés</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {products.slice(0, 4).map((product) => (
                    <div key={product.id} className="p-4 bg-background rounded-lg text-center">
                      <img 
                        src={product.image_url} 
                        alt={product.name}
                        className="w-20 h-20 object-cover rounded-lg mx-auto mb-2"
                      />
                      <p className="text-white text-sm font-medium truncate">{product.name}</p>
                      <Badge className="bg-[#f5a623] text-black mt-2">Score: {product.score}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex justify-center gap-4">
              <Button variant="outline" onClick={resetAnalysis} className="px-8">
                <RefreshCw className="h-4 w-4 mr-2" />
                Nouvelle analyse
              </Button>
              <Button className="btn-golden text-black px-8" onClick={() => navigate('/compare')}>
                <Package className="h-4 w-4 mr-2" />
                Comparer les produits
              </Button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
};

export default AnalyzerModule;
