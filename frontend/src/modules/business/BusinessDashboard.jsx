/**
 * BusinessDashboard - Central dashboard for business modules
 * Phase 9 - Business Modules Integration
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';

// Business Module Imports
import { UserProfile, UserActivity } from '../user';
import { ProductCard, ProductGrid } from '../products';
import { OrderCard, OrdersList } from '../orders';
import { CartWidget } from '../cart';
import { AffiliateStats } from '../affiliate';
import { SupplierCard } from '../suppliers';
import { CustomerCard } from '../customers';

// Services
import { UserService } from '../user/UserService';
import { ProductsService } from '../products/ProductsService';
import { OrdersService } from '../orders/OrdersService';
import { CartService } from '../cart/CartService';
import { AffiliateService } from '../affiliate/AffiliateService';
import { SuppliersService } from '../suppliers/SuppliersService';
import { CustomersService } from '../customers/CustomersService';

export const BusinessDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  
  // Data states
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [stats, setStats] = useState({
    products: { total: 0 },
    orders: { total: 0, pending: 0 },
    cart: { items: 0 },
    affiliate: { clicks: 0, conversion: 0 },
    suppliers: { total: 0 },
    customers: { total: 0 }
  });

  // Load dashboard data
  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    
    try {
      // Load in parallel
      const [
        productsData,
        ordersData,
        cartData,
        affiliateStats,
        suppliersData,
        customersData
      ] = await Promise.all([
        ProductsService.getTopProducts(8).catch(() => []),
        OrdersService.getOrders({ limit: 10 }).catch(() => []),
        CartService.getCart(CartService.getSessionId()).catch(() => ({ items: [] })),
        AffiliateService.getStats().catch(() => ({})),
        SuppliersService.getSuppliers().catch(() => []),
        CustomersService.getCustomers().catch(() => [])
      ]);

      setProducts(productsData);
      setOrders(ordersData);
      setCartItems(cartData.items || []);
      setSuppliers(suppliersData);
      setCustomers(customersData);

      setStats({
        products: { total: productsData.length },
        orders: { 
          total: ordersData.length, 
          pending: ordersData.filter(o => o.status === 'pending').length 
        },
        cart: { items: (cartData.items || []).length },
        affiliate: {
          clicks: affiliateStats.total_clicks || 0,
          conversion: affiliateStats.conversion_rate || 0
        },
        suppliers: { total: suppliersData.length },
        customers: { total: customersData.length }
      });

    } catch (error) {
      console.error('Business dashboard load error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Handlers
  const handleAddToCart = async (product) => {
    try {
      await CartService.addItem(CartService.getSessionId(), product.id, 1);
      const cartData = await CartService.getCart(CartService.getSessionId());
      setCartItems(cartData.items || []);
    } catch (error) {
      console.error('Add to cart error:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">💼</div>
          <p className="text-slate-400">Chargement du dashboard métier...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="business-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <span className="text-3xl">💼</span>
            Dashboard Métier
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Modules Business • Phase 9
          </p>
        </div>
        
        {/* Quick Stats */}
        <div className="flex items-center gap-3">
          <Badge className="bg-blue-900/50 text-blue-400">
            📦 {stats.products.total} produits
          </Badge>
          <Badge className="bg-amber-900/50 text-amber-400">
            📋 {stats.orders.total} commandes
          </Badge>
          <Badge className="bg-emerald-900/50 text-emerald-400">
            👥 {stats.customers.total} clients
          </Badge>
        </div>
      </div>

      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-slate-800 border border-slate-700 w-full justify-start">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            📊 Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="products" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            📦 Produits
          </TabsTrigger>
          <TabsTrigger value="orders" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            📋 Commandes
          </TabsTrigger>
          <TabsTrigger value="customers" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            👥 Clients
          </TabsTrigger>
          <TabsTrigger value="suppliers" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            🏭 Fournisseurs
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Stats Cards */}
            <div className="space-y-4">
              {/* Orders Summary */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-white flex items-center gap-2">
                    <span>📋</span>
                    Commandes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-blue-400">{stats.orders.total}</div>
                      <div className="text-xs text-slate-400">Total</div>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-amber-400">{stats.orders.pending}</div>
                      <div className="text-xs text-slate-400">En attente</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Affiliate Stats */}
              <AffiliateStats stats={{
                total_clicks: stats.affiliate.clicks,
                conversion_rate: stats.affiliate.conversion,
                total_sales: Math.floor(stats.affiliate.clicks * stats.affiliate.conversion / 100),
                total_commission: Math.floor(stats.affiliate.clicks * stats.affiliate.conversion / 100) * 5
              }} />

              {/* Quick Cart */}
              <CartWidget 
                items={cartItems}
                compact={true}
              />
            </div>

            {/* Center Column - Recent Orders */}
            <div className="space-y-4">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-white flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <span>📋</span>
                      Commandes Récentes
                    </span>
                    <Badge className="bg-slate-700">{orders.length}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {orders.length > 0 ? (
                    <div className="space-y-3">
                      {orders.slice(0, 3).map((order) => (
                        <OrderCard key={order.id} order={order} compact />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-slate-400">
                      <span className="text-3xl">📋</span>
                      <p className="text-sm mt-2">Aucune commande</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Top Customers */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-white flex items-center gap-2">
                    <span>👥</span>
                    Clients Récents
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {customers.length > 0 ? (
                    <div className="space-y-2">
                      {customers.slice(0, 3).map((customer) => (
                        <CustomerCard key={customer.id} customer={customer} compact />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-slate-400">
                      <p className="text-sm">Aucun client</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Top Products */}
            <div className="space-y-4">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-white flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <span>📦</span>
                      Top Produits
                    </span>
                    <Badge className="bg-[#f5a623] text-black">{products.length}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {products.length > 0 ? (
                    <div className="space-y-3">
                      {products.slice(0, 4).map((product) => (
                        <ProductCard 
                          key={product.id} 
                          product={product} 
                          compact 
                          onAddToCart={handleAddToCart}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 text-slate-400">
                      <span className="text-3xl">📦</span>
                      <p className="text-sm mt-2">Aucun produit</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Suppliers Quick List */}
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-white flex items-center gap-2">
                    <span>🏭</span>
                    Fournisseurs
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {suppliers.length > 0 ? (
                    <div className="space-y-2">
                      {suppliers.slice(0, 3).map((supplier) => (
                        <SupplierCard key={supplier.id} supplier={supplier} compact />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-slate-400">
                      <p className="text-sm">Aucun fournisseur</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Products Tab */}
        <TabsContent value="products" className="mt-6">
          <ProductGrid 
            products={products}
            onAddToCart={handleAddToCart}
            columns={4}
            emptyMessage="Aucun produit disponible"
          />
        </TabsContent>

        {/* Orders Tab */}
        <TabsContent value="orders" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <OrdersList 
                orders={orders}
                emptyMessage="Aucune commande enregistrée"
              />
            </div>
            <div>
              <CartWidget 
                items={cartItems}
              />
            </div>
          </div>
        </TabsContent>

        {/* Customers Tab */}
        <TabsContent value="customers" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customers.length > 0 ? (
              customers.map((customer) => (
                <CustomerCard key={customer.id} customer={customer} />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <span className="text-5xl">👥</span>
                <p className="text-slate-400 mt-4">Aucun client enregistré</p>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Suppliers Tab */}
        <TabsContent value="suppliers" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {suppliers.length > 0 ? (
              suppliers.map((supplier) => (
                <SupplierCard key={supplier.id} supplier={supplier} />
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <span className="text-5xl">🏭</span>
                <p className="text-slate-400 mt-4">Aucun fournisseur enregistré</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BusinessDashboard;
