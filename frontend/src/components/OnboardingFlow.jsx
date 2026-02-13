/**
 * HUNTIQ V3 - Onboarding Flow Component
 * Flow d'inscription et configuration du profil chasseur
 * Module isolé - Architecture modulaire stricte
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { 
  ChevronRight, ChevronLeft, CheckCircle, Target, MapPin, Compass,
  Bell, Globe, FlaskConical, Map, Store, Crown, Sparkles, X, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import BionicLogo from '@/components/BionicLogo';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// ONBOARDING FLOW COMPONENT
// ============================================

export const OnboardingFlow = ({ userId, onComplete, onSkip }) => {
  const [config, setConfig] = useState(null);
  const [progress, setProgress] = useState(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Form data
  const [selectedSpecies, setSelectedSpecies] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [huntingObjectives, setHuntingObjectives] = useState([]);
  const [language, setLanguage] = useState('fr');
  const [notifications, setNotifications] = useState({
    weather: true,
    activity: true,
    news: false
  });

  useEffect(() => {
    loadOnboardingData();
  }, [userId]);

  const loadOnboardingData = async () => {
    try {
      const [configRes, progressRes] = await Promise.all([
        axios.get(`${API}/onboarding/config`),
        axios.get(`${API}/onboarding/progress/${userId}`)
      ]);
      
      setConfig(configRes.data);
      setProgress(progressRes.data);
      
      // Restore saved data
      if (progressRes.data.hunter_profile) {
        const profile = progressRes.data.hunter_profile;
        setSelectedSpecies(profile.target_species || []);
        setSelectedRegion(profile.region || '');
        setExperienceLevel(profile.experience_level || '');
        setHuntingObjectives(profile.hunting_objectives || []);
      }
      
      if (progressRes.data.preferences) {
        const prefs = progressRes.data.preferences;
        setLanguage(prefs.language || 'fr');
        setNotifications({
          weather: prefs.notifications_weather ?? true,
          activity: prefs.notifications_activity ?? true,
          news: prefs.notifications_news ?? false
        });
      }
      
      // Set current step
      if (progressRes.data.current_step) {
        setCurrentStepIndex(progressRes.data.current_step - 1);
      }
      
      // If already complete, call onComplete
      if (progressRes.data.is_complete) {
        onComplete?.();
      }
    } catch (error) {
      console.error('Error loading onboarding:', error);
      toast.error('Erreur de chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (!config?.steps) return;
    
    const currentStep = config.steps[currentStepIndex];
    setSaving(true);
    
    try {
      let stepData = null;
      
      if (currentStep.id === 'profile') {
        stepData = {
          target_species: selectedSpecies,
          region: selectedRegion,
          experience_level: experienceLevel,
          hunting_objectives: huntingObjectives
        };
      } else if (currentStep.id === 'preferences') {
        stepData = {
          language: language,
          notifications_weather: notifications.weather,
          notifications_activity: notifications.activity,
          notifications_news: notifications.news
        };
      }
      
      const response = await axios.post(`${API}/onboarding/step/complete`, {
        user_id: userId,
        step_id: currentStep.id,
        data: stepData
      });
      
      if (response.data.is_complete) {
        toast.success('Bienvenue sur HUNTIQ!');
        onComplete?.();
      } else {
        setCurrentStepIndex(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error completing step:', error);
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };

  const handleSkip = async () => {
    try {
      await axios.post(`${API}/onboarding/skip/${userId}`);
      toast.info('Vous pouvez configurer votre profil plus tard');
      onSkip?.();
    } catch (error) {
      console.error('Error skipping onboarding:', error);
    }
  };

  const toggleSpecies = (speciesId) => {
    setSelectedSpecies(prev => 
      prev.includes(speciesId) 
        ? prev.filter(s => s !== speciesId)
        : [...prev, speciesId]
    );
  };

  const toggleObjective = (objectiveId) => {
    setHuntingObjectives(prev =>
      prev.includes(objectiveId)
        ? prev.filter(o => o !== objectiveId)
        : [...prev, objectiveId]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  if (!config?.steps) return null;

  const currentStep = config.steps[currentStepIndex];
  const progressPercent = ((currentStepIndex + 1) / config.steps.length) * 100;

  // Render step content based on type
  const renderStepContent = () => {
    switch (currentStep.id) {
      case 'welcome':
        return (
          <div className="text-center py-8" data-testid="onboarding-welcome">
            <div className="mb-6">
              <BionicLogo className="h-20 w-20 mx-auto" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">
              Bienvenue sur HUNTIQ
            </h2>
            <p className="text-gray-400 text-lg max-w-md mx-auto">
              Votre plateforme de chasse intelligente pour analyser, planifier et réussir vos chasses.
            </p>
            <div className="flex justify-center gap-4 mt-8">
              <Badge className="bg-green-500/20 text-green-400 px-4 py-2">
                <FlaskConical className="h-4 w-4 mr-2" />
                Analyzer BIONIC™
              </Badge>
              <Badge className="bg-blue-500/20 text-blue-400 px-4 py-2">
                <Map className="h-4 w-4 mr-2" />
                Territory Map
              </Badge>
              <Badge className="bg-purple-500/20 text-purple-400 px-4 py-2">
                <Store className="h-4 w-4 mr-2" />
                Marketplace
              </Badge>
            </div>
          </div>
        );

      case 'profile':
        return (
          <div className="space-y-6" data-testid="onboarding-profile">
            {/* Target Species */}
            <div>
              <Label className="text-white text-lg mb-3 block">
                <Target className="h-5 w-5 inline mr-2 text-[#f5a623]" />
                Espèces ciblées
              </Label>
              <div className="grid grid-cols-4 gap-3">
                {config.options.target_species.map((species) => (
                  <div
                    key={species.id}
                    onClick={() => toggleSpecies(species.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all text-center ${
                      selectedSpecies.includes(species.id)
                        ? 'border-[#f5a623] bg-[#f5a623]/10'
                        : 'border-gray-700 hover:border-gray-600'
                    }`}
                    data-testid={`species-${species.id}`}
                  >
                    <span className="text-2xl block mb-1">{species.icon}</span>
                    <span className="text-sm text-white">{species.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Region */}
            <div>
              <Label className="text-white text-lg mb-3 block">
                <MapPin className="h-5 w-5 inline mr-2 text-[#f5a623]" />
                Région principale
              </Label>
              <RadioGroup value={selectedRegion} onValueChange={setSelectedRegion} className="grid grid-cols-2 gap-2">
                {config.options.regions.map((region) => (
                  <div key={region.id} className="flex items-center space-x-2">
                    <RadioGroupItem value={region.id} id={region.id} />
                    <Label htmlFor={region.id} className="text-gray-300 cursor-pointer">
                      {region.name}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            {/* Experience Level */}
            <div>
              <Label className="text-white text-lg mb-3 block">
                <Compass className="h-5 w-5 inline mr-2 text-[#f5a623]" />
                Niveau d'expérience
              </Label>
              <RadioGroup value={experienceLevel} onValueChange={setExperienceLevel} className="space-y-2">
                {config.options.experience_levels.map((level) => (
                  <div 
                    key={level.id} 
                    className={`p-3 rounded-lg border cursor-pointer ${
                      experienceLevel === level.id 
                        ? 'border-[#f5a623] bg-[#f5a623]/10' 
                        : 'border-gray-700'
                    }`}
                    onClick={() => setExperienceLevel(level.id)}
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value={level.id} id={level.id} />
                      <div>
                        <Label htmlFor={level.id} className="text-white cursor-pointer">{level.name}</Label>
                        <p className="text-sm text-gray-500">{level.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </RadioGroup>
            </div>

            {/* Hunting Objectives */}
            <div>
              <Label className="text-white text-lg mb-3 block">
                🎯 Objectifs de chasse
              </Label>
              <div className="grid grid-cols-2 gap-2">
                {config.options.hunting_objectives.map((obj) => (
                  <div
                    key={obj.id}
                    onClick={() => toggleObjective(obj.id)}
                    className={`p-3 rounded-lg border cursor-pointer flex items-center gap-2 ${
                      huntingObjectives.includes(obj.id)
                        ? 'border-[#f5a623] bg-[#f5a623]/10'
                        : 'border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <Checkbox checked={huntingObjectives.includes(obj.id)} />
                    <span className="text-gray-300">{obj.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'preferences':
        return (
          <div className="space-y-6" data-testid="onboarding-preferences">
            {/* Language */}
            <div>
              <Label className="text-white text-lg mb-3 block">
                <Globe className="h-5 w-5 inline mr-2 text-[#f5a623]" />
                Langue
              </Label>
              <RadioGroup value={language} onValueChange={setLanguage} className="flex gap-4">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="fr" id="lang-fr" />
                  <Label htmlFor="lang-fr" className="text-gray-300">🇨🇦 Français</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="en" id="lang-en" />
                  <Label htmlFor="lang-en" className="text-gray-300">🇬🇧 English</Label>
                </div>
              </RadioGroup>
            </div>

            {/* Notifications */}
            <div>
              <Label className="text-white text-lg mb-3 block">
                <Bell className="h-5 w-5 inline mr-2 text-[#f5a623]" />
                Notifications
              </Label>
              <div className="space-y-3">
                <div 
                  className={`p-4 rounded-lg border cursor-pointer ${
                    notifications.weather ? 'border-green-500 bg-green-500/10' : 'border-gray-700'
                  }`}
                  onClick={() => setNotifications(prev => ({ ...prev, weather: !prev.weather }))}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">🌤️ Météo de chasse</p>
                      <p className="text-sm text-gray-400">Alertes conditions optimales</p>
                    </div>
                    <Checkbox checked={notifications.weather} />
                  </div>
                </div>
                
                <div 
                  className={`p-4 rounded-lg border cursor-pointer ${
                    notifications.activity ? 'border-green-500 bg-green-500/10' : 'border-gray-700'
                  }`}
                  onClick={() => setNotifications(prev => ({ ...prev, activity: !prev.activity }))}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">🦌 Activité du gibier</p>
                      <p className="text-sm text-gray-400">Alertes périodes de rut et activité</p>
                    </div>
                    <Checkbox checked={notifications.activity} />
                  </div>
                </div>
                
                <div 
                  className={`p-4 rounded-lg border cursor-pointer ${
                    notifications.news ? 'border-green-500 bg-green-500/10' : 'border-gray-700'
                  }`}
                  onClick={() => setNotifications(prev => ({ ...prev, news: !prev.news }))}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">📰 Actualités HUNTIQ</p>
                      <p className="text-sm text-gray-400">Nouveautés et promotions</p>
                    </div>
                    <Checkbox checked={notifications.news} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'features':
        return (
          <div className="space-y-6" data-testid="onboarding-features">
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <FlaskConical className="h-10 w-10 text-[#f5a623] mb-4" />
                  <h3 className="text-white font-semibold text-lg mb-2">Analyzer BIONIC™</h3>
                  <p className="text-gray-400 text-sm">
                    Analysez vos attractants avec 13 critères scientifiques et l'IA.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <Map className="h-10 w-10 text-blue-500 mb-4" />
                  <h3 className="text-white font-semibold text-lg mb-2">Territory Map</h3>
                  <p className="text-gray-400 text-sm">
                    Explorez et gérez vos territoires de chasse au Québec.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <Store className="h-10 w-10 text-purple-500 mb-4" />
                  <h3 className="text-white font-semibold text-lg mb-2">Marketplace</h3>
                  <p className="text-gray-400 text-sm">
                    Achetez, vendez et échangez équipements et services.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-yellow-900/30 to-amber-900/30 border-yellow-500/30">
                <CardContent className="p-6">
                  <Crown className="h-10 w-10 text-yellow-500 mb-4" />
                  <h3 className="text-white font-semibold text-lg mb-2 flex items-center gap-2">
                    PRO
                    <Badge className="bg-yellow-500 text-black text-xs">Recommandé</Badge>
                  </h3>
                  <p className="text-gray-400 text-sm">
                    Accès illimité et outils avancés. À partir de 7.99$/mois.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        );

      case 'complete':
        return (
          <div className="text-center py-8" data-testid="onboarding-complete">
            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="h-10 w-10 text-green-500" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">
              Vous êtes prêt!
            </h2>
            <p className="text-gray-400 text-lg max-w-md mx-auto mb-6">
              Votre profil est configuré. Commencez votre aventure de chasse avec HUNTIQ.
            </p>
            <div className="flex justify-center gap-4">
              <Button className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-bold">
                <FlaskConical className="h-4 w-4 mr-2" />
                Analyser un produit
              </Button>
              <Button variant="outline">
                <Map className="h-4 w-4 mr-2" />
                Explorer la carte
              </Button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4" data-testid="onboarding-flow">
      <Card className="w-full max-w-3xl bg-gray-800 border-gray-700">
        <CardHeader className="border-b border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <CardTitle className="text-white">{currentStep.title}</CardTitle>
            <Button variant="ghost" size="sm" onClick={handleSkip} className="text-gray-400">
              Passer <X className="h-4 w-4 ml-1" />
            </Button>
          </div>
          <CardDescription>{currentStep.description}</CardDescription>
          <Progress value={progressPercent} className="h-2 mt-4" />
          <p className="text-xs text-gray-500 mt-2">
            Étape {currentStepIndex + 1} sur {config.steps.length}
          </p>
        </CardHeader>
        
        <CardContent className="p-6">
          {renderStepContent()}
        </CardContent>

        <div className="p-6 border-t border-gray-700 flex justify-between">
          <Button 
            variant="outline" 
            onClick={handleBack}
            disabled={currentStepIndex === 0}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Retour
          </Button>
          <Button 
            onClick={handleNext}
            disabled={saving}
            className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-bold"
            data-testid="next-step-btn"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : null}
            {currentStepIndex === config.steps.length - 1 ? 'Terminer' : 'Continuer'}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </Card>
    </div>
  );
};

// ============================================
// ONBOARDING MODAL (for existing users)
// ============================================

export const OnboardingModal = ({ isOpen, onClose, userId, onComplete }) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto p-0 bg-transparent border-none">
        <OnboardingFlow 
          userId={userId} 
          onComplete={() => {
            onComplete?.();
            onClose();
          }}
          onSkip={onClose}
        />
      </DialogContent>
    </Dialog>
  );
};

export default OnboardingFlow;
