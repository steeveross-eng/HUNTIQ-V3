/**
 * HUNTIQ V3 - Freemium UI Components
 * Badges PRO, Banners, Upgrade Modals
 * Module isolé - Architecture modulaire stricte
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { 
  Crown, Sparkles, Lock, AlertTriangle, CheckCircle, Star, Zap, 
  TrendingUp, Shield, Gift, Clock, ArrowRight, X
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// PRO BADGE COMPONENT
// ============================================

export const ProBadge = ({ size = "default", showText = true, className = "" }) => {
  const sizeClasses = {
    small: "h-4 w-4",
    default: "h-5 w-5",
    large: "h-6 w-6"
  };

  return (
    <Badge 
      className={`bg-gradient-to-r from-yellow-500 to-amber-600 text-black font-bold gap-1 ${className}`}
      data-testid="pro-badge"
    >
      <Crown className={sizeClasses[size]} />
      {showText && <span>PRO</span>}
    </Badge>
  );
};

// ============================================
// QUOTA INDICATOR COMPONENT
// ============================================

export const QuotaIndicator = ({ feature, userId, onLimitReached }) => {
  const [quota, setQuota] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId && feature) {
      checkQuota();
    }
  }, [userId, feature]);

  const checkQuota = async () => {
    try {
      const response = await axios.post(`${API}/freemium/check`, {
        user_id: userId,
        feature: feature
      });
      setQuota(response.data);
      
      if (!response.data.allowed && onLimitReached) {
        onLimitReached(response.data);
      }
    } catch (error) {
      console.error('Error checking quota:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !quota) return null;

  if (quota.is_pro) {
    return (
      <div className="flex items-center gap-2 text-sm text-yellow-500" data-testid="quota-unlimited">
        <Crown className="h-4 w-4" />
        <span>Illimité</span>
      </div>
    );
  }

  const percent = quota.limit > 0 ? (quota.used / quota.limit) * 100 : 0;
  const isLow = percent >= 80;
  const isExhausted = percent >= 100;

  return (
    <div className="space-y-1" data-testid="quota-indicator">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-400">
          {quota.used}/{quota.limit} utilisé{quota.used > 1 ? 's' : ''}
        </span>
        {quota.reset_at && (
          <span className="text-gray-500 text-xs">
            Reset: {new Date(quota.reset_at).toLocaleDateString('fr-CA')}
          </span>
        )}
      </div>
      <Progress 
        value={percent} 
        className={`h-2 ${isExhausted ? 'bg-red-900' : isLow ? 'bg-yellow-900' : 'bg-gray-700'}`}
      />
      {isExhausted && (
        <p className="text-xs text-red-400 flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          Limite atteinte
        </p>
      )}
    </div>
  );
};

// ============================================
// UPGRADE BANNER COMPONENT
// ============================================

export const UpgradeBanner = ({ feature, message, onUpgrade, variant = "default" }) => {
  const variants = {
    default: "bg-gradient-to-r from-gray-800 to-gray-900 border-yellow-500/30",
    warning: "bg-gradient-to-r from-yellow-900/30 to-orange-900/30 border-yellow-500/50",
    urgent: "bg-gradient-to-r from-red-900/30 to-orange-900/30 border-red-500/50"
  };

  return (
    <div 
      className={`p-4 rounded-lg border ${variants[variant]} flex items-center justify-between gap-4`}
      data-testid="upgrade-banner"
    >
      <div className="flex items-center gap-3">
        <div className="p-2 bg-yellow-500/10 rounded-full">
          <Crown className="h-5 w-5 text-yellow-500" />
        </div>
        <div>
          <p className="text-white font-medium">
            {message || "Passez PRO pour un accès illimité"}
          </p>
          <p className="text-sm text-gray-400">
            À partir de 7.99$ CAD/mois avec 7 jours d'essai gratuit
          </p>
        </div>
      </div>
      <Button 
        onClick={onUpgrade}
        className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold gap-2"
        data-testid="upgrade-btn"
      >
        <Sparkles className="h-4 w-4" />
        Passer PRO
      </Button>
    </div>
  );
};

// ============================================
// UPGRADE MODAL COMPONENT
// ============================================

export const UpgradeModal = ({ isOpen, onClose, feature, reason, auth }) => {
  const [plans, setPlans] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState('yearly');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadPlans();
    }
  }, [isOpen]);

  const loadPlans = async () => {
    try {
      const response = await axios.get(`${API}/freemium/quotas`);
      setPlans(response.data.pricing);
    } catch (error) {
      console.error('Error loading plans:', error);
    }
  };

  const handleUpgrade = async (planId) => {
    if (!auth?.token) {
      toast.error('Veuillez vous connecter pour vous abonner');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/payments/checkout`, {
        package_id: `pro_${planId}`,
        origin_url: window.location.origin,
        seller_id: auth.user?.id
      });

      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error('Erreur lors de la création du paiement');
    } finally {
      setLoading(false);
    }
  };

  const planDetails = [
    {
      id: 'monthly',
      name: 'Mensuel',
      price: plans?.monthly?.amount || 7.99,
      period: '/mois',
      features: ['7 jours d\'essai gratuit', 'Annulation facile']
    },
    {
      id: 'yearly',
      name: 'Annuel',
      price: plans?.yearly?.amount || 79,
      period: '/an',
      features: ['7 jours d\'essai gratuit', 'Économisez 17%', 'Meilleur rapport qualité/prix'],
      popular: true
    },
    {
      id: 'lifetime',
      name: 'À Vie',
      price: plans?.lifetime?.amount || 199,
      period: '',
      features: ['Paiement unique', 'Accès permanent', 'Mises à jour incluses']
    }
  ];

  const proFeatures = [
    'Analyses IA illimitées avec résultats complets',
    'Territoires et waypoints illimités',
    'Annonces Marketplace illimitées',
    'Outils avancés de planification',
    'Conditions optimales de chasse',
    'Notifications avancées',
    'Badge PRO et visibilité accrue',
    'Support prioritaire'
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-gray-900 border-gray-800 max-w-3xl max-h-[90vh] overflow-y-auto" data-testid="upgrade-modal">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2 text-2xl">
            <Crown className="h-7 w-7 text-yellow-500" />
            Passez PRO
          </DialogTitle>
          <DialogDescription>
            {reason || "Débloquez toutes les fonctionnalités HUNTIQ"}
          </DialogDescription>
        </DialogHeader>

        {/* Plans */}
        <div className="grid grid-cols-3 gap-4 my-6">
          {planDetails.map((plan) => (
            <Card 
              key={plan.id}
              className={`cursor-pointer transition-all ${
                selectedPlan === plan.id 
                  ? 'border-yellow-500 bg-yellow-500/10' 
                  : 'border-gray-700 hover:border-gray-600'
              } ${plan.popular ? 'relative' : ''}`}
              onClick={() => setSelectedPlan(plan.id)}
              data-testid={`plan-${plan.id}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-yellow-500 text-black font-bold">
                    <Star className="h-3 w-3 mr-1" />
                    Populaire
                  </Badge>
                </div>
              )}
              <CardHeader className="pb-2">
                <CardTitle className="text-white text-lg">{plan.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <span className="text-3xl font-bold text-white">{plan.price}$</span>
                  <span className="text-gray-400"> CAD{plan.period}</span>
                </div>
                <ul className="space-y-2">
                  {plan.features.map((feat, i) => (
                    <li key={i} className="text-sm text-gray-400 flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      {feat}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features */}
        <div className="bg-gray-800/50 rounded-lg p-4 mb-6">
          <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            Inclus avec PRO
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {proFeatures.map((feat, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-gray-300">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                {feat}
              </div>
            ))}
          </div>
        </div>

        <DialogFooter className="flex gap-3">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Plus tard
          </Button>
          <Button 
            onClick={() => handleUpgrade(selectedPlan)}
            disabled={loading}
            className="flex-1 bg-gradient-to-r from-yellow-500 to-amber-600 text-black font-bold hover:from-yellow-600 hover:to-amber-700"
            data-testid="confirm-upgrade-btn"
          >
            {loading ? (
              'Chargement...'
            ) : (
              <>
                <Crown className="h-4 w-4 mr-2" />
                {selectedPlan === 'lifetime' ? 'Acheter' : 'Commencer l\'essai gratuit'}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// FEATURE LOCK OVERLAY
// ============================================

export const FeatureLock = ({ feature, children, userId, onUpgrade }) => {
  const [isLocked, setIsLocked] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (userId && feature) {
      checkAccess();
    }
  }, [userId, feature]);

  const checkAccess = async () => {
    try {
      const response = await axios.post(`${API}/freemium/check`, {
        user_id: userId,
        feature: feature
      });
      setIsLocked(!response.data.allowed && !response.data.is_pro);
    } catch (error) {
      console.error('Error checking access:', error);
    }
  };

  if (!isLocked) {
    return children;
  }

  return (
    <div className="relative" data-testid="feature-lock">
      <div className="opacity-50 pointer-events-none blur-sm">
        {children}
      </div>
      <div 
        className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm rounded-lg cursor-pointer"
        onClick={() => setShowModal(true)}
      >
        <div className="text-center p-6">
          <Lock className="h-12 w-12 text-yellow-500 mx-auto mb-3" />
          <p className="text-white font-medium mb-2">Fonctionnalité PRO</p>
          <p className="text-gray-400 text-sm mb-4">Passez PRO pour débloquer</p>
          <Button 
            className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold"
            onClick={(e) => {
              e.stopPropagation();
              setShowModal(true);
            }}
          >
            <Crown className="h-4 w-4 mr-2" />
            Débloquer
          </Button>
        </div>
      </div>
      <UpgradeModal 
        isOpen={showModal} 
        onClose={() => setShowModal(false)}
        feature={feature}
      />
    </div>
  );
};

// ============================================
// PRO STATUS CARD
// ============================================

export const ProStatusCard = ({ userId }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      loadStatus();
    }
  }, [userId]);

  const loadStatus = async () => {
    try {
      const response = await axios.get(`${API}/freemium/status/${userId}`);
      setStatus(response.data);
    } catch (error) {
      console.error('Error loading PRO status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return null;

  if (!status?.is_pro) {
    return (
      <Card className="bg-gray-800/50 border-gray-700" data-testid="free-status-card">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-medium">Compte Gratuit</p>
              <p className="text-sm text-gray-400">Fonctionnalités limitées</p>
            </div>
            <Button size="sm" className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold">
              <Crown className="h-4 w-4 mr-1" />
              Passer PRO
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gradient-to-r from-yellow-900/30 to-amber-900/30 border-yellow-500/30" data-testid="pro-status-card">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-full">
              <Crown className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-white font-medium flex items-center gap-2">
                Membre PRO
                <Badge className="bg-yellow-500/20 text-yellow-400 text-xs">
                  {status.pro_type === 'lifetime' ? 'À VIE' : status.pro_type?.toUpperCase()}
                </Badge>
              </p>
              {status.pro_type !== 'lifetime' && status.days_remaining > 0 && (
                <p className="text-sm text-gray-400">
                  {status.days_remaining} jours restants
                </p>
              )}
              {status.pro_type === 'lifetime' && (
                <p className="text-sm text-yellow-500">Accès permanent</p>
              )}
            </div>
          </div>
          <CheckCircle className="h-6 w-6 text-green-500" />
        </div>
      </CardContent>
    </Card>
  );
};

// Named exports for individual components
export { ProBadge, QuotaIndicator, UpgradeBanner, UpgradeModal, FeatureLock, ProStatusCard };

// Default export - main wrapper component for route usage
const FreemiumUI = () => {
  const userId = localStorage.getItem('user_id') || 'guest';
  return (
    <main className="min-h-screen bg-background py-24 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-white mb-8">Gestion Freemium</h1>
        <ProStatusCard userId={userId} />
        <UpgradeBanner userId={userId} />
      </div>
    </main>
  );
};

export default FreemiumUI;
