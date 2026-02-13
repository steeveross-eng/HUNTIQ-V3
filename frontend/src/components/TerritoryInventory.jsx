/**
 * TerritoryInventory - Component for browsing and analyzing hunting territories
 * Integrates with AnalyzerModule under "Pourvoyeurs" category
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import TerritoryAdvanced from './TerritoryAdvanced';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Search,
  MapPin,
  Target,
  Trees,
  Mountain,
  Building2,
  Star,
  TrendingUp,
  Filter,
  ChevronRight,
  ExternalLink,
  Phone,
  Mail,
  Globe,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Users,
  Tent,
  Navigation,
  Award,
  Sparkles,
  Database,
  Handshake,
  BarChart3,
  Map,
  Compass,
  RefreshCw,
  Eye,
  Bookmark,
  Share2
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// TYPE ICONS & LABELS
// ============================================

const TYPE_CONFIG = {
  zec: { icon: '🏕️', label: 'ZEC', color: 'bg-green-500/20 text-green-400 border-green-500/50' },
  sepaq: { icon: '🦌', label: 'Sépaq', color: 'bg-blue-500/20 text-blue-400 border-blue-500/50' },
  pourvoirie: { icon: '🏠', label: 'Pourvoirie', color: 'bg-purple-500/20 text-purple-400 border-purple-500/50' },
  club: { icon: '🎯', label: 'Club', color: 'bg-orange-500/20 text-orange-400 border-orange-500/50' },
  outfitter: { icon: '🦬', label: 'Outfitter', color: 'bg-amber-500/20 text-amber-400 border-amber-500/50' },
  private: { icon: '🔒', label: 'Privé', color: 'bg-gray-500/20 text-gray-400 border-gray-500/50' },
  anticosti: { icon: '🏝️', label: 'Anticosti', color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/50' },
  reserve: { icon: '🌲', label: 'Réserve', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50' },
  indigenous: { icon: '🪶', label: 'Autochtone', color: 'bg-red-500/20 text-red-400 border-red-500/50' }
};

const SPECIES_CONFIG = {
  orignal: { icon: '🫎', label: 'Orignal' },
  chevreuil: { icon: '🦌', label: 'Chevreuil' },
  ours: { icon: '🐻', label: 'Ours' },
  caribou: { icon: '🦌', label: 'Caribou' },
  wapiti: { icon: '🦌', label: 'Wapiti' },
  cerf_mulet: { icon: '🦌', label: 'Cerf mulet' },
  dindon: { icon: '🦃', label: 'Dindon' },
  petit_gibier: { icon: '🐰', label: 'Petit gibier' },
  sauvagine: { icon: '🦆', label: 'Sauvagine' },
  grizzly: { icon: '🐻', label: 'Grizzly' }
};

const PROVINCE_NAMES = {
  QC: 'Québec',
  ON: 'Ontario',
  NB: 'Nouveau-Brunswick',
  NS: 'Nouvelle-Écosse',
  PE: 'Î.-P.-É.',
  NL: 'Terre-Neuve',
  MB: 'Manitoba',
  SK: 'Saskatchewan',
  AB: 'Alberta',
  BC: 'Colombie-Britannique',
  YT: 'Yukon',
  NT: 'T.N.-O.'
};

// ============================================
// SCORE BADGE COMPONENT
// ============================================

const ScoreBadge = ({ score, size = 'md' }) => {
  const getScoreColor = (s) => {
    if (s >= 80) return 'bg-green-500 text-white';
    if (s >= 60) return 'bg-yellow-500 text-black';
    if (s >= 40) return 'bg-orange-500 text-white';
    return 'bg-red-500 text-white';
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-lg px-4 py-2 font-bold'
  };

  return (
    <span className={`rounded-full ${getScoreColor(score)} ${sizeClasses[size]}`}>
      {score.toFixed(1)}
    </span>
  );
};

// ============================================
// TERRITORY CARD COMPONENT
// ============================================

const TerritoryCard = ({ territory, onClick }) => {
  const typeConfig = TYPE_CONFIG[territory.establishment_type] || TYPE_CONFIG.outfitter;
  
  return (
    <Card 
      className="bg-card border-border hover:border-[#f5a623]/50 transition-all cursor-pointer group"
      onClick={() => onClick(territory)}
      data-testid={`territory-card-${territory.id}`}
    >
      <CardContent className="p-2">
        <div className="flex items-start justify-between mb-1">
          <div className="flex items-center gap-1">
            <span className="text-lg">{typeConfig.icon}</span>
            <Badge variant="outline" className={`${typeConfig.color} text-[10px] px-1 py-0`}>
              {typeConfig.label}
            </Badge>
          </div>
          <ScoreBadge score={territory.scoring?.global_score || 0} />
        </div>
        
        <h3 className="text-white font-semibold text-sm mb-0.5 group-hover:text-[#f5a623] transition-colors line-clamp-1">
          {territory.name}
        </h3>
        
        <div className="flex items-center gap-1 text-gray-400 text-xs mb-1">
          <MapPin className="h-2.5 w-2.5" />
          <span className="truncate">{territory.region || PROVINCE_NAMES[territory.province] || territory.province}</span>
          {territory.is_verified && (
            <CheckCircle className="h-3 w-3 text-green-400 ml-auto flex-shrink-0" />
          )}
        </div>
        
        {/* Species - Compact */}
        <div className="flex flex-wrap gap-0.5 mb-1">
          {(territory.species || []).slice(0, 3).map(species => (
            <span key={species} className="text-sm" title={SPECIES_CONFIG[species]?.label}>
              {SPECIES_CONFIG[species]?.icon || '🎯'}
            </span>
          ))}
          {(territory.species || []).length > 3 && (
            <span className="text-gray-500 text-[10px]">+{territory.species.length - 3}</span>
          )}
        </div>
        
        {/* Quick stats - Single line */}
        <div className="flex items-center gap-2 text-[10px] text-gray-400">
          <span className="flex items-center gap-0.5">
            <Target className="h-2.5 w-2.5 text-green-400" />
            {territory.success_rate ? `${territory.success_rate}%` : 'N/D'}
          </span>
          <span className="flex items-center gap-0.5">
            <Trees className="h-2.5 w-2.5 text-blue-400" />
            {territory.hunting_zones?.length || 0} zones
          </span>
          {territory.price_range && (
            <span className="text-[#f5a623] ml-auto">{territory.price_range}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// TERRITORY DETAIL MODAL
// ============================================

const TerritoryDetailModal = ({ territory, open, onClose }) => {
  if (!territory) return null;
  
  const typeConfig = TYPE_CONFIG[territory.establishment_type] || TYPE_CONFIG.outfitter;
  const scoring = territory.scoring || {};
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto bg-card border-border">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <span className="text-3xl">{typeConfig.icon}</span>
            <div>
              <DialogTitle className="text-white text-xl">{territory.name}</DialogTitle>
              <DialogDescription className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                {territory.region}, {PROVINCE_NAMES[territory.province] || territory.province}
                {territory.is_verified && (
                  <Badge className="bg-green-500/20 text-green-400 text-xs ml-2">
                    <CheckCircle className="h-3 w-3 mr-1" /> Vérifié
                  </Badge>
                )}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>
        
        <div className="space-y-6 py-4">
          {/* Score Section */}
          <div className="bg-background p-4 rounded-lg border border-border">
            <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-[#f5a623]" />
              Score BIONIC™
            </h4>
            
            <div className="flex items-center justify-center mb-6">
              <div className="text-center">
                <ScoreBadge score={scoring.global_score || 0} size="lg" />
                <p className="text-gray-400 text-sm mt-2">Score Global</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Habitat (H)</span>
                  <span className="text-white">{scoring.habitat_index || 0}%</span>
                </div>
                <Progress value={scoring.habitat_index || 0} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Pression (P)</span>
                  <span className="text-white">{scoring.pressure_index || 0}%</span>
                </div>
                <Progress value={scoring.pressure_index || 0} className="h-2 [&>div]:bg-orange-500" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Succès (S)</span>
                  <span className="text-white">{scoring.success_index || 0}%</span>
                </div>
                <Progress value={scoring.success_index || 0} className="h-2 [&>div]:bg-green-500" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Accessibilité (A)</span>
                  <span className="text-white">{scoring.accessibility_index || 0}%</span>
                </div>
                <Progress value={scoring.accessibility_index || 0} className="h-2 [&>div]:bg-blue-500" />
              </div>
            </div>
          </div>
          
          {/* Description */}
          {territory.description && (
            <div>
              <h4 className="text-white font-semibold mb-2">Description</h4>
              <p className="text-gray-400">{territory.description}</p>
            </div>
          )}
          
          {/* Species */}
          <div>
            <h4 className="text-white font-semibold mb-2">Espèces disponibles</h4>
            <div className="flex flex-wrap gap-2">
              {(territory.species || []).map(species => (
                <Badge key={species} variant="outline" className="text-white border-border">
                  {SPECIES_CONFIG[species]?.icon} {SPECIES_CONFIG[species]?.label || species}
                </Badge>
              ))}
            </div>
          </div>
          
          {/* Hunting Zones */}
          {territory.hunting_zones && territory.hunting_zones.length > 0 && (
            <div>
              <h4 className="text-white font-semibold mb-2">Zones de chasse</h4>
              <div className="flex flex-wrap gap-2">
                {territory.hunting_zones.map((zone, idx) => (
                  <Badge key={idx} className="bg-[#f5a623]/20 text-[#f5a623]">
                    {zone}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          
          {/* Services */}
          {territory.services && Object.values(territory.services).some(v => v) && (
            <div>
              <h4 className="text-white font-semibold mb-2">Services</h4>
              <div className="grid grid-cols-2 gap-2">
                {territory.services.accommodation && (
                  <div className="flex items-center gap-2 text-gray-300 text-sm">
                    <Tent className="h-4 w-4 text-green-400" /> Hébergement
                  </div>
                )}
                {territory.services.guided_hunts && (
                  <div className="flex items-center gap-2 text-gray-300 text-sm">
                    <Users className="h-4 w-4 text-green-400" /> Chasse guidée
                  </div>
                )}
                {territory.services.meals_included && (
                  <div className="flex items-center gap-2 text-gray-300 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-400" /> Repas inclus
                  </div>
                )}
                {territory.services.meat_processing && (
                  <div className="flex items-center gap-2 text-gray-300 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-400" /> Traitement gibier
                  </div>
                )}
                {territory.services.transportation && (
                  <div className="flex items-center gap-2 text-gray-300 text-sm">
                    <Navigation className="h-4 w-4 text-green-400" /> Transport
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Contact Info */}
          <div className="bg-background p-4 rounded-lg border border-border">
            <h4 className="text-white font-semibold mb-3">Contact</h4>
            <div className="space-y-2">
              {territory.website && (
                <a 
                  href={territory.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-[#f5a623] hover:underline"
                >
                  <Globe className="h-4 w-4" />
                  {territory.website}
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
              {territory.email && (
                <a 
                  href={`mailto:${territory.email}`}
                  className="flex items-center gap-2 text-gray-300 hover:text-white"
                >
                  <Mail className="h-4 w-4" />
                  {territory.email}
                </a>
              )}
              {territory.phone && (
                <a 
                  href={`tel:${territory.phone}`}
                  className="flex items-center gap-2 text-gray-300 hover:text-white"
                >
                  <Phone className="h-4 w-4" />
                  {territory.phone}
                </a>
              )}
            </div>
          </div>
          
          {/* Internal ID */}
          <div className="text-xs text-gray-500 text-center">
            ID: {territory.internal_id}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================

const TerritoryInventory = () => {
  const { t, language } = useLanguage();
  const [territories, setTerritories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTerritory, setSelectedTerritory] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterProvince, setFilterProvince] = useState('all');
  const [filterSpecies, setFilterSpecies] = useState('all');
  const [sortBy, setSortBy] = useState('global_score');
  const [showFilters, setShowFilters] = useState(false);
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const loadTerritories = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '12',
        sort_by: sortBy
      });
      
      if (searchQuery) params.append('search', searchQuery);
      if (filterType !== 'all') params.append('establishment_type', filterType);
      if (filterProvince !== 'all') params.append('province', filterProvince);
      if (filterSpecies !== 'all') params.append('species', filterSpecies);
      
      const response = await axios.get(`${API}/territories?${params}`);
      
      if (response.data.success) {
        setTerritories(response.data.territories);
        setTotal(response.data.pagination.total);
        setTotalPages(response.data.pagination.pages);
      }
    } catch (error) {
      console.error('Error loading territories:', error);
      toast.error('Erreur lors du chargement des territoires');
    }
    setLoading(false);
  }, [page, searchQuery, filterType, filterProvince, filterSpecies, sortBy]);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/territories/stats`);
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    loadTerritories();
  }, [loadTerritories]);

  useEffect(() => {
    loadStats();
  }, []);

  const handleTerritoryClick = (territory) => {
    setSelectedTerritory(territory);
    setShowDetail(true);
  };

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      setPage(1);
      loadTerritories();
    }
  };

  const resetFilters = () => {
    setSearchQuery('');
    setFilterType('all');
    setFilterProvince('all');
    setFilterSpecies('all');
    setSortBy('global_score');
    setPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Main Tabs - Inventory vs Advanced */}
      <Tabs defaultValue="inventory" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2 mb-4 bg-card border border-border">
          <TabsTrigger 
            value="inventory" 
            className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
          >
            <Map className="h-4 w-4 mr-2" />
            Inventaire
          </TabsTrigger>
          <TabsTrigger 
            value="advanced" 
            className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            IA & Scraping
          </TabsTrigger>
        </TabsList>

        <TabsContent value="inventory" className="space-y-3">
          {/* Stats Overview - Compact */}
          {stats && (
            <div className="grid grid-cols-4 gap-2">
              <Card className="bg-card border-border">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-[#f5a623]">{stats.total}</div>
                  <div className="text-gray-400 text-xs">Territoires</div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-green-400">{stats.verified}</div>
                  <div className="text-gray-400 text-xs">Vérifiés</div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-blue-400">{Object.keys(stats.by_province || {}).length}</div>
                  <div className="text-gray-400 text-xs">Provinces</div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-purple-400">{stats.avg_score}</div>
                  <div className="text-gray-400 text-xs">Score moyen</div>
                </CardContent>
              </Card>
            </div>
          )}

      {/* Search & Filters - Compact */}
      <Card className="bg-card border-border">
        <CardContent className="p-3">
          <div className="flex flex-col md:flex-row gap-2">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
              <Input
                placeholder="Rechercher un territoire, une région..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleSearch}
                className="pl-10 bg-background h-9 text-sm"
                data-testid="territory-search"
              />
            </div>
            
            {/* Quick Filters - Compact */}
            <Select value={filterType} onValueChange={(v) => { setFilterType(v); setPage(1); }}>
              <SelectTrigger className="w-[130px] bg-background h-9 text-sm">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous types</SelectItem>
                {Object.entries(TYPE_CONFIG).map(([key, config]) => (
                  <SelectItem key={key} value={key}>
                    {config.icon} {config.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={filterProvince} onValueChange={(v) => { setFilterProvince(v); setPage(1); }}>
              <SelectTrigger className="w-[130px] bg-background h-9 text-sm">
                <SelectValue placeholder="Province" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes provinces</SelectItem>
                {Object.entries(PROVINCE_NAMES).map(([code, name]) => (
                  <SelectItem key={code} value={code}>{name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={filterSpecies} onValueChange={(v) => { setFilterSpecies(v); setPage(1); }}>
              <SelectTrigger className="w-[130px] bg-background h-9 text-sm">
                <SelectValue placeholder="Espèce" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes espèces</SelectItem>
                {Object.entries(SPECIES_CONFIG).map(([key, config]) => (
                  <SelectItem key={key} value={key}>
                    {config.icon} {config.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={sortBy} onValueChange={(v) => { setSortBy(v); setPage(1); }}>
              <SelectTrigger className="w-[120px] bg-background h-9 text-sm">
                <SelectValue placeholder="Trier" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="global_score">Score ↓</SelectItem>
                <SelectItem value="name">Nom A-Z</SelectItem>
                <SelectItem value="success_rate">Succès ↓</SelectItem>
                <SelectItem value="created_at">Récent</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" size="sm" onClick={resetFilters} className="h-9" title="Réinitialiser les filtres">
              <RefreshCw className="h-4 w-4 mr-1" />
              {t('common_refresh')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results - Compact */}
      <div className="flex items-center justify-between">
        <p className="text-gray-400 text-xs">
          {total} territoire{total !== 1 ? 's' : ''} trouvé{total !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Territory Grid - Compact 5 columns */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-[#f5a623]" />
        </div>
      ) : territories.length === 0 ? (
        <Card className="bg-card border-border">
          <CardContent className="p-8 text-center">
            <Map className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <h3 className="text-white text-base font-semibold mb-1">Aucun territoire trouvé</h3>
            <p className="text-gray-400 text-sm">Modifiez vos filtres ou essayez une autre recherche</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
          {territories.map((territory) => (
            <TerritoryCard
              key={territory.id}
              territory={territory}
              onClick={handleTerritoryClick}
            />
          ))}
        </div>
      )}

      {/* Pagination - Compact */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            ← Préc
          </Button>
          <span className="text-gray-400 text-sm px-2">
            {page}/{totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Suiv →
          </Button>
        </div>
      )}

      {/* Detail Modal */}
      <TerritoryDetailModal
        territory={selectedTerritory}
        open={showDetail}
        onClose={() => setShowDetail(false)}
      />
        </TabsContent>

        {/* Advanced Tab - AI & Scraping */}
        <TabsContent value="advanced">
          <TerritoryAdvanced />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TerritoryInventory;
