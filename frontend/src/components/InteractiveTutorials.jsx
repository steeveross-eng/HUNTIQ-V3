/**
 * HUNTIQ V3 - Interactive Tutorials Component
 * Tutoriels interactifs modulaires
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
  Play, CheckCircle, ChevronRight, ChevronLeft, X, 
  FlaskConical, Map, Store, Clock, Target, AlertTriangle,
  GraduationCap, Loader2, RotateCcw
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Icon mapping
const iconMap = {
  flask: FlaskConical,
  map: Map,
  store: Store
};

// ============================================
// TUTORIALS LIST COMPONENT
// ============================================

export const TutorialsList = ({ userId, onStartTutorial }) => {
  const [tutorials, setTutorials] = useState(null);
  const [userProgress, setUserProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [userId]);

  const loadData = async () => {
    try {
      const [tutorialsRes, progressRes] = await Promise.all([
        axios.get(`${API}/tutorials/list`),
        userId ? axios.get(`${API}/tutorials/progress/${userId}`) : Promise.resolve({ data: null })
      ]);
      
      setTutorials(tutorialsRes.data.tutorials);
      setUserProgress(progressRes.data);
    } catch (error) {
      console.error('Error loading tutorials:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  const getProgressForTutorial = (tutorialId) => {
    if (!userProgress?.tutorials) return null;
    return userProgress.tutorials.find(t => t.tutorial_id === tutorialId);
  };

  return (
    <div className="space-y-6" data-testid="tutorials-list">
      {/* Overall Progress */}
      {userProgress && (
        <Card className="bg-gradient-to-r from-[#f5a623]/10 to-amber-500/10 border-[#f5a623]/30">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5 text-[#f5a623]" />
                <span className="text-white font-medium">Votre progression</span>
              </div>
              <span className="text-[#f5a623] font-bold">
                {userProgress.completed_tutorials}/{userProgress.total_tutorials} complétés
              </span>
            </div>
            <Progress value={userProgress.overall_progress} className="h-2" />
          </CardContent>
        </Card>
      )}

      {/* Tutorials Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tutorials?.map((tutorial) => {
          const progress = getProgressForTutorial(tutorial.id);
          const Icon = iconMap[tutorial.icon] || Target;
          
          return (
            <Card 
              key={tutorial.id}
              className={`bg-gray-800 border-gray-700 hover:border-[#f5a623]/50 transition-all cursor-pointer ${
                progress?.is_complete ? 'border-green-500/30' : ''
              }`}
              onClick={() => onStartTutorial(tutorial.id)}
              data-testid={`tutorial-card-${tutorial.id}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="p-2 bg-[#f5a623]/10 rounded-lg">
                    <Icon className="h-6 w-6 text-[#f5a623]" />
                  </div>
                  {progress?.is_complete && (
                    <Badge className="bg-green-500/20 text-green-400">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Complété
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-white text-lg mt-2">{tutorial.title}</CardTitle>
                <CardDescription className="text-gray-400">
                  {tutorial.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {tutorial.duration_minutes} min
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {tutorial.difficulty === 'beginner' ? 'Débutant' : 
                     tutorial.difficulty === 'intermediate' ? 'Intermédiaire' : 'Avancé'}
                  </Badge>
                </div>
                
                {progress && !progress.is_complete && progress.completed_steps > 0 && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>En cours</span>
                      <span>{progress.progress_percent}%</span>
                    </div>
                    <Progress value={progress.progress_percent} className="h-1" />
                  </div>
                )}
                
                <Button 
                  className="w-full mt-3 bg-[#f5a623]/10 hover:bg-[#f5a623]/20 text-[#f5a623]"
                  variant="ghost"
                >
                  {progress?.is_complete ? (
                    <>
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Refaire
                    </>
                  ) : progress?.completed_steps > 0 ? (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Continuer
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Commencer
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

// ============================================
// INTERACTIVE TUTORIAL COMPONENT
// ============================================

export const InteractiveTutorial = ({ tutorialId, userId, onComplete, onClose }) => {
  const [tutorial, setTutorial] = useState(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);

  useEffect(() => {
    if (tutorialId) {
      loadTutorial();
    }
  }, [tutorialId]);

  const loadTutorial = async () => {
    try {
      const [detailRes] = await Promise.all([
        axios.get(`${API}/tutorials/detail/${tutorialId}`),
        axios.post(`${API}/tutorials/start`, {
          user_id: userId,
          tutorial_id: tutorialId,
          step_id: ''
        }).catch(() => {}) // Ignore start errors
      ]);
      
      setTutorial(detailRes.data);
    } catch (error) {
      console.error('Error loading tutorial:', error);
      toast.error('Erreur de chargement du tutoriel');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (!tutorial?.steps) return;
    
    const currentStep = tutorial.steps[currentStepIndex];
    setCompleting(true);
    
    try {
      const response = await axios.post(`${API}/tutorials/step/complete`, {
        user_id: userId,
        tutorial_id: tutorialId,
        step_id: currentStep.id
      });
      
      if (response.data.is_complete) {
        toast.success('Tutoriel complété!');
        onComplete?.();
      } else {
        setCurrentStepIndex(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error completing step:', error);
    } finally {
      setCompleting(false);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  if (!tutorial?.steps) return null;

  const currentStep = tutorial.steps[currentStepIndex];
  const progressPercent = ((currentStepIndex + 1) / tutorial.steps.length) * 100;
  const Icon = iconMap[tutorial.icon] || Target;

  const getStepIcon = (type) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-12 w-12 text-yellow-500" />;
      case 'completion':
        return <CheckCircle className="h-12 w-12 text-green-500" />;
      case 'action':
        return <Target className="h-12 w-12 text-blue-500" />;
      default:
        return <Icon className="h-12 w-12 text-[#f5a623]" />;
    }
  };

  return (
    <div className="space-y-4" data-testid="interactive-tutorial">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-[#f5a623]/10 rounded-lg">
            <Icon className="h-6 w-6 text-[#f5a623]" />
          </div>
          <div>
            <h3 className="text-white font-semibold">{tutorial.title}</h3>
            <p className="text-sm text-gray-400">
              Étape {currentStepIndex + 1} sur {tutorial.steps.length}
            </p>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Progress */}
      <Progress value={progressPercent} className="h-2" />

      {/* Step Content */}
      <Card className={`bg-gray-800 border-gray-700 ${
        currentStep.type === 'warning' ? 'border-yellow-500/30' :
        currentStep.type === 'completion' ? 'border-green-500/30' : ''
      }`}>
        <CardContent className="p-6">
          <div className="text-center mb-6">
            {getStepIcon(currentStep.type)}
          </div>
          
          <h4 className="text-xl font-semibold text-white text-center mb-3">
            {currentStep.title}
          </h4>
          
          <p className={`text-center ${
            currentStep.type === 'warning' ? 'text-yellow-400' : 'text-gray-400'
          }`}>
            {currentStep.content}
          </p>
          
          {currentStep.highlight_element && (
            <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <p className="text-blue-400 text-sm text-center">
                👆 Élément à trouver: <code className="bg-gray-900 px-1 rounded">{currentStep.highlight_element}</code>
              </p>
            </div>
          )}
          
          {currentStep.action_required && (
            <Badge className="block mx-auto mt-4 bg-blue-500/20 text-blue-400 w-fit">
              Action requise: {currentStep.action_required}
            </Badge>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button 
          variant="outline" 
          onClick={handleBack}
          disabled={currentStepIndex === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Précédent
        </Button>
        
        <Button 
          onClick={handleNext}
          disabled={completing}
          className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black font-bold"
          data-testid="tutorial-next-btn"
        >
          {completing && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
          {currentStepIndex === tutorial.steps.length - 1 ? 'Terminer' : 'Suivant'}
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </div>
  );
};

// ============================================
// TUTORIAL MODAL
// ============================================

export const TutorialModal = ({ isOpen, onClose, tutorialId, userId }) => {
  const [showList, setShowList] = useState(!tutorialId);
  const [selectedTutorial, setSelectedTutorial] = useState(tutorialId);

  useEffect(() => {
    if (tutorialId) {
      setSelectedTutorial(tutorialId);
      setShowList(false);
    }
  }, [tutorialId]);

  const handleStartTutorial = (id) => {
    setSelectedTutorial(id);
    setShowList(false);
  };

  const handleComplete = () => {
    setShowList(true);
    setSelectedTutorial(null);
  };

  const handleBack = () => {
    setShowList(true);
    setSelectedTutorial(null);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-gray-900 border-gray-800 max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="tutorial-modal">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <GraduationCap className="h-6 w-6 text-[#f5a623]" />
            {showList ? 'Tutoriels HUNTIQ' : 'Tutoriel en cours'}
          </DialogTitle>
          <DialogDescription>
            {showList 
              ? 'Apprenez à utiliser toutes les fonctionnalités de HUNTIQ'
              : 'Suivez les instructions étape par étape'
            }
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4">
          {showList ? (
            <TutorialsList 
              userId={userId} 
              onStartTutorial={handleStartTutorial}
            />
          ) : (
            <InteractiveTutorial
              tutorialId={selectedTutorial}
              userId={userId}
              onComplete={handleComplete}
              onClose={handleBack}
            />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// TUTORIAL TRIGGER BUTTON
// ============================================

export const TutorialTrigger = ({ userId, className = "" }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button 
        variant="outline"
        onClick={() => setIsOpen(true)}
        className={`gap-2 ${className}`}
        data-testid="tutorial-trigger"
      >
        <GraduationCap className="h-4 w-4" />
        Tutoriels
      </Button>
      
      <TutorialModal 
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        userId={userId}
      />
    </>
  );
};

// Named exports
export { TutorialsList, InteractiveTutorial, TutorialModal, TutorialTrigger };

// Page wrapper for route usage
const InteractiveTutorials = () => {
  const userId = localStorage.getItem('user_id') || 'guest';
  const [selectedTutorial, setSelectedTutorial] = useState(null);

  const handleStartTutorial = (tutorialId) => {
    setSelectedTutorial(tutorialId);
  };

  const handleComplete = () => {
    setSelectedTutorial(null);
  };

  return (
    <main className="min-h-screen bg-background py-24 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <GraduationCap className="h-8 w-8 text-[#f5a623]" />
          <h1 className="text-3xl font-bold text-white">Tutoriels HUNTIQ</h1>
        </div>
        
        {selectedTutorial ? (
          <InteractiveTutorial
            tutorialId={selectedTutorial}
            userId={userId}
            onComplete={handleComplete}
            onClose={() => setSelectedTutorial(null)}
          />
        ) : (
          <TutorialsList 
            userId={userId} 
            onStartTutorial={handleStartTutorial}
          />
        )}
      </div>
    </main>
  );
};

export default InteractiveTutorials;
