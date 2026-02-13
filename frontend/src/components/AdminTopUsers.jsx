/**
 * HUNTIQ V3 - Admin Top Users View
 * Vue complète des membres les plus actifs
 * Module isolé - Accès restreint administrateurs
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Users, Crown, TrendingUp, Download, Search, Filter, Eye, 
  ArrowUpDown, ChevronLeft, ChevronRight, RefreshCw, 
  Target, ShoppingCart, Map, FlaskConical, UserPlus, Gift,
  Star, Shield, Loader2, AlertTriangle, CheckCircle
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Status badge colors
const statusColors = {
  "FREE": "bg-gray-500/20 text-gray-400",
  "PRO_MONTHLY": "bg-blue-500/20 text-blue-400",
  "PRO_YEARLY": "bg-purple-500/20 text-purple-400",
  "PRO_LIFETIME": "bg-yellow-500/20 text-yellow-400",
  "PRO": "bg-green-500/20 text-green-400"
};

// Category icons
const categoryIcons = {
  global: Users,
  free: Users,
  pro_monthly: Crown,
  pro_yearly: Crown,
  pro_lifetime: Star,
  contributors: Gift,
  marketplace: ShoppingCart,
  analyzer: FlaskConical,
  territory: Map,
  growth: TrendingUp,
  pro_boost_candidates: Target,
  mastery_candidates: Shield
};

// ============================================
// ADMIN TOP USERS PAGE
// ============================================

export const AdminTopUsersPage = () => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('global');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [summary, setSummary] = useState(null);
  
  // Filters
  const [subscriptionFilter, setSubscriptionFilter] = useState('');
  const [regionFilter, setRegionFilter] = useState('');
  const [userTypeFilter, setUserTypeFilter] = useState('');
  const [sortBy, setSortBy] = useState('score');
  const [sortOrder, setSortOrder] = useState('desc');
  
  // User detail modal
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDetailOpen, setUserDetailOpen] = useState(false);
  const [userDetail, setUserDetail] = useState(null);

  useEffect(() => {
    loadCategories();
    loadSummary();
  }, []);

  useEffect(() => {
    loadUsers();
  }, [selectedCategory, page, subscriptionFilter, regionFilter, userTypeFilter, sortBy, sortOrder]);

  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API}/admin/users/top/categories`);
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadSummary = async () => {
    try {
      const response = await axios.get(`${API}/admin/users/stats/summary`);
      setSummary(response.data);
    } catch (error) {
      console.error('Error loading summary:', error);
    }
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        category: selectedCategory,
        page: page.toString(),
        page_size: pageSize.toString(),
        sort_by: sortBy,
        sort_order: sortOrder
      });
      
      if (subscriptionFilter) params.append('subscription_type', subscriptionFilter);
      if (regionFilter) params.append('region', regionFilter);
      if (userTypeFilter) params.append('user_type', userTypeFilter);
      
      const response = await axios.get(`${API}/admin/users/top?${params}`);
      setUsers(response.data.users);
      setTotalCount(response.data.total_count);
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Erreur de chargement des utilisateurs');
    } finally {
      setLoading(false);
    }
  };

  const loadUserDetail = async (userId) => {
    try {
      const response = await axios.get(`${API}/admin/users/profile/${userId}`);
      setUserDetail(response.data);
      setUserDetailOpen(true);
    } catch (error) {
      console.error('Error loading user detail:', error);
      toast.error('Erreur de chargement du profil');
    }
  };

  const exportCSV = async () => {
    try {
      const params = new URLSearchParams({
        category: selectedCategory
      });
      if (subscriptionFilter) params.append('subscription_type', subscriptionFilter);
      if (regionFilter) params.append('region', regionFilter);
      
      const response = await axios.get(`${API}/admin/users/top/export?${params}`);
      
      // Create and download CSV file
      const blob = new Blob([response.data.content], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = response.data.filename;
      link.click();
      
      toast.success(`Export réussi: ${response.data.total_records} utilisateurs`);
    } catch (error) {
      console.error('Error exporting CSV:', error);
      toast.error('Erreur lors de l\'export');
    }
  };

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const totalPages = Math.ceil(totalCount / pageSize);
  const CategoryIcon = categoryIcons[selectedCategory] || Users;

  return (
    <div className="min-h-screen bg-gray-900 p-6" data-testid="admin-top-users">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Users className="h-8 w-8 text-[#f5a623]" />
          Top Users - Administration
        </h1>
        <p className="text-gray-400 mt-1">
          Vue complète des membres les plus actifs, engagés et rentables
        </p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-5 gap-4 mb-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Utilisateurs</p>
                  <p className="text-2xl font-bold text-white">{summary.total_users}</p>
                </div>
                <Users className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">FREE</p>
                  <p className="text-2xl font-bold text-gray-400">{summary.free_users}</p>
                </div>
                <Users className="h-8 w-8 text-gray-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-r from-yellow-900/30 to-amber-900/30 border-yellow-500/30">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">PRO Total</p>
                  <p className="text-2xl font-bold text-yellow-400">{summary.pro_users.total}</p>
                </div>
                <Crown className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Taux Conversion</p>
                  <p className="text-2xl font-bold text-green-400">{summary.conversion_rate}%</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="text-sm text-gray-400 mb-1">Répartition PRO</div>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-blue-400">Mensuel</span>
                  <span className="text-white">{summary.pro_users.monthly}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-400">Annuel</span>
                  <span className="text-white">{summary.pro_users.yearly}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-yellow-400">À Vie</span>
                  <span className="text-white">{summary.pro_users.lifetime}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Category Tabs */}
      <Card className="bg-gray-800 border-gray-700 mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => {
              const Icon = categoryIcons[cat.id] || Users;
              return (
                <Button
                  key={cat.id}
                  variant={selectedCategory === cat.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => { setSelectedCategory(cat.id); setPage(1); }}
                  className={selectedCategory === cat.id ? "bg-[#f5a623] text-black" : ""}
                  data-testid={`category-${cat.id}`}
                >
                  <Icon className="h-4 w-4 mr-1" />
                  {cat.name}
                </Button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Filters & Actions */}
      <Card className="bg-gray-800 border-gray-700 mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-400">Filtres:</span>
            </div>
            
            <Select value={subscriptionFilter || "all"} onValueChange={(v) => setSubscriptionFilter(v === "all" ? "" : v)}>
              <SelectTrigger className="w-40 bg-gray-900 border-gray-700">
                <SelectValue placeholder="Abonnement" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous</SelectItem>
                <SelectItem value="FREE">FREE</SelectItem>
                <SelectItem value="PRO_MONTHLY">PRO Mensuel</SelectItem>
                <SelectItem value="PRO_YEARLY">PRO Annuel</SelectItem>
                <SelectItem value="PRO_LIFETIME">PRO À Vie</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={userTypeFilter || "all"} onValueChange={(v) => setUserTypeFilter(v === "all" ? "" : v)}>
              <SelectTrigger className="w-40 bg-gray-900 border-gray-700">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous types</SelectItem>
                <SelectItem value="hunter">Chasseur</SelectItem>
                <SelectItem value="outfitter">Pourvoyeur</SelectItem>
                <SelectItem value="supplier">Fournisseur</SelectItem>
                <SelectItem value="group">Groupe</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="flex-grow" />
            
            <Button variant="outline" onClick={loadUsers} className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Rafraîchir
            </Button>
            
            <Button onClick={exportCSV} className="gap-2 bg-green-600 hover:bg-green-700">
              <Download className="h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader className="border-b border-gray-700">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <CategoryIcon className="h-5 w-5 text-[#f5a623]" />
              {categories.find(c => c.id === selectedCategory)?.name || 'Top Users'}
              <Badge className="ml-2 bg-gray-700">{totalCount} résultats</Badge>
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Aucun utilisateur trouvé pour cette catégorie</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-gray-700 hover:bg-gray-800">
                  <TableHead className="text-gray-400">Utilisateur</TableHead>
                  <TableHead className="text-gray-400">Statut</TableHead>
                  <TableHead 
                    className="text-gray-400 cursor-pointer hover:text-white"
                    onClick={() => toggleSort('score')}
                  >
                    <div className="flex items-center gap-1">
                      Score
                      <ArrowUpDown className="h-4 w-4" />
                    </div>
                  </TableHead>
                  <TableHead 
                    className="text-gray-400 cursor-pointer hover:text-white"
                    onClick={() => toggleSort('total_actions')}
                  >
                    <div className="flex items-center gap-1">
                      Actions
                      <ArrowUpDown className="h-4 w-4" />
                    </div>
                  </TableHead>
                  <TableHead className="text-gray-400">Réseau</TableHead>
                  <TableHead 
                    className="text-gray-400 cursor-pointer hover:text-white"
                    onClick={() => toggleSort('last_activity')}
                  >
                    <div className="flex items-center gap-1">
                      Dernière Activité
                      <ArrowUpDown className="h-4 w-4" />
                    </div>
                  </TableHead>
                  <TableHead className="text-gray-400 text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user, index) => (
                  <TableRow 
                    key={user.user_id} 
                    className="border-gray-700 hover:bg-gray-800/50"
                    data-testid={`user-row-${index}`}
                  >
                    <TableCell>
                      <div>
                        <p className="text-white font-medium">{user.name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusColors[user.status] || statusColors.FREE}>
                        {user.status === 'PRO_LIFETIME' && <Crown className="h-3 w-3 mr-1" />}
                        {user.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="text-white font-bold">{user.global_activity_score}</span>
                        <Progress value={Math.min(user.global_activity_score / 5, 100)} className="w-16 h-2" />
                      </div>
                    </TableCell>
                    <TableCell className="text-white">{user.total_actions}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <span className="text-green-400">{user.network_potential}</span>
                        <span className="text-gray-500"> potentiel</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-gray-400 text-sm">
                      {user.last_activity 
                        ? new Date(user.last_activity).toLocaleDateString('fr-CA')
                        : '-'
                      }
                    </TableCell>
                    <TableCell className="text-right">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => loadUserDetail(user.user_id)}
                        data-testid={`view-profile-${index}`}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        Voir Profil
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-gray-700">
              <p className="text-sm text-gray-400">
                Page {page} sur {totalPages} ({totalCount} utilisateurs)
              </p>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Précédent
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  disabled={page === totalPages}
                  onClick={() => setPage(p => p + 1)}
                >
                  Suivant
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Detail Modal */}
      <Dialog open={userDetailOpen} onOpenChange={setUserDetailOpen}>
        <DialogContent className="bg-gray-900 border-gray-800 max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="user-detail-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Eye className="h-5 w-5 text-[#f5a623]" />
              Profil Admin - {userDetail?.basic_info?.name}
            </DialogTitle>
            <DialogDescription>
              Vue administrative complète de l'utilisateur
            </DialogDescription>
          </DialogHeader>
          
          {userDetail && (
            <div className="space-y-6 mt-4">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <h4 className="text-sm text-gray-400 mb-2">Informations</h4>
                    <p className="text-white font-medium">{userDetail.basic_info.name}</p>
                    <p className="text-sm text-gray-400">{userDetail.basic_info.email}</p>
                    <Badge className={`mt-2 ${statusColors[userDetail.status]}`}>
                      {userDetail.status}
                    </Badge>
                  </CardContent>
                </Card>
                
                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <h4 className="text-sm text-gray-400 mb-2">Score d'Activité</h4>
                    <p className="text-3xl font-bold text-[#f5a623]">{userDetail.activity_score}</p>
                    <Progress value={Math.min(userDetail.activity_score / 3, 100)} className="mt-2" />
                  </CardContent>
                </Card>
              </div>
              
              {/* Metrics */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-white text-lg">Métriques d'Activité</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <ShoppingCart className="h-5 w-5 mx-auto text-purple-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.marketplace_purchases}</p>
                      <p className="text-xs text-gray-500">Achats</p>
                    </div>
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <ShoppingCart className="h-5 w-5 mx-auto text-green-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.marketplace_sales}</p>
                      <p className="text-xs text-gray-500">Ventes</p>
                    </div>
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <FlaskConical className="h-5 w-5 mx-auto text-blue-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.analyzer_ai_uses}</p>
                      <p className="text-xs text-gray-500">Analyses IA</p>
                    </div>
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <Map className="h-5 w-5 mx-auto text-teal-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.territories_created}</p>
                      <p className="text-xs text-gray-500">Territoires</p>
                    </div>
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <Target className="h-5 w-5 mx-auto text-orange-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.waypoints_created}</p>
                      <p className="text-xs text-gray-500">Waypoints</p>
                    </div>
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <Gift className="h-5 w-5 mx-auto text-pink-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.suppliers_added}</p>
                      <p className="text-xs text-gray-500">Fournisseurs</p>
                    </div>
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <UserPlus className="h-5 w-5 mx-auto text-cyan-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.invitations_sent}</p>
                      <p className="text-xs text-gray-500">Invitations</p>
                    </div>
                    <div className="text-center p-3 bg-gray-900 rounded-lg">
                      <CheckCircle className="h-5 w-5 mx-auto text-emerald-400 mb-1" />
                      <p className="text-xl font-bold text-white">{userDetail.metrics.referrals_completed}</p>
                      <p className="text-xs text-gray-500">Parrainages</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              {/* Hunter Profile */}
              {userDetail.hunter_profile && (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-white text-lg">Profil Chasseur</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Espèces ciblées:</span>
                        <p className="text-white">{userDetail.hunter_profile.target_species?.join(', ') || '-'}</p>
                      </div>
                      <div>
                        <span className="text-gray-400">Région:</span>
                        <p className="text-white">{userDetail.hunter_profile.region || '-'}</p>
                      </div>
                      <div>
                        <span className="text-gray-400">Expérience:</span>
                        <p className="text-white">{userDetail.hunter_profile.experience_level || '-'}</p>
                      </div>
                      <div>
                        <span className="text-gray-400">Objectifs:</span>
                        <p className="text-white">{userDetail.hunter_profile.hunting_objectives?.join(', ') || '-'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
              
              {/* Progress */}
              <div className="grid grid-cols-2 gap-4">
                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400">Onboarding</span>
                      {userDetail.onboarding_completed ? (
                        <Badge className="bg-green-500/20 text-green-400">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Complété
                        </Badge>
                      ) : (
                        <Badge className="bg-yellow-500/20 text-yellow-400">
                          En cours
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400">Tutoriels</span>
                      <span className="text-white">
                        {userDetail.tutorials_completed?.length || 0}/3
                      </span>
                    </div>
                    <Progress 
                      value={(userDetail.tutorials_completed?.length || 0) / 3 * 100} 
                      className="h-2" 
                    />
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminTopUsersPage;
