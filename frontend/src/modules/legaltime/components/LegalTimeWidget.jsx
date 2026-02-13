/**
 * LegalTimeWidget - Display legal hunting hours and sun times
 * Shows sunrise/sunset, legal window, and current status
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { LegalTimeService } from '../LegalTimeService';

export const LegalTimeWidget = ({ 
  coordinates = { lat: 46.8139, lng: -71.2080 },
  date = null,
  compact = false,
  showSlots = true
}) => {
  const [data, setData] = useState(null);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [windowResult, slotsResult] = await Promise.all([
        LegalTimeService.getLegalWindow(date, coordinates.lat, coordinates.lng),
        showSlots ? LegalTimeService.getRecommendedSlots(date, coordinates.lat, coordinates.lng) : { slots: [] }
      ]);
      
      if (windowResult.success) {
        setData(windowResult);
      }
      if (slotsResult.success && slotsResult.slots) {
        setSlots(slotsResult.slots);
      }
    } catch (error) {
      console.error('Error loading legal time data:', error);
    } finally {
      setLoading(false);
    }
  }, [coordinates, date, showSlots]);

  useEffect(() => {
    loadData();
    
    // Update current time every minute
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    
    return () => clearInterval(timer);
  }, [loadData]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'legal': return 'bg-green-500';
      case 'before_legal': return 'bg-yellow-500';
      case 'after_legal': return 'bg-red-500';
      default: return 'bg-slate-500';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'legal': return 'Période légale';
      case 'before_legal': return 'Avant ouverture';
      case 'after_legal': return 'Chasse terminée';
      default: return 'Inconnu';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#22c55e';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  if (loading) {
    return (
      <Card className="bg-gradient-to-br from-orange-900/20 to-slate-900 border-orange-700/50">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin text-3xl">☀️</div>
            <span className="ml-3 text-slate-400">Calcul des heures légales...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const { legal_window, status } = data;
  const currentStatus = status?.current_status || 'legal';
  const isLegal = status?.is_currently_legal;

  // Compact version
  if (compact) {
    return (
      <div 
        className={`rounded-lg p-4 border ${
          isLegal 
            ? 'bg-gradient-to-r from-green-900/30 to-slate-900 border-green-700/50' 
            : 'bg-gradient-to-r from-orange-900/30 to-slate-900 border-orange-700/50'
        }`}
        data-testid="legal-time-compact"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{isLegal ? '🟢' : '🔴'}</span>
            <div>
              <p className="text-white font-medium">
                {isLegal ? 'Chasse autorisée' : 'Hors période légale'}
              </p>
              <p className="text-slate-400 text-sm">
                {legal_window?.start_time} - {legal_window?.end_time}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-slate-400 text-xs">Lever/Coucher</p>
            <p className="text-white text-sm">
              ☀️ {legal_window?.sunrise} | 🌙 {legal_window?.sunset}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Card 
      className="bg-gradient-to-br from-orange-900/20 to-slate-900 border-orange-700/50"
      data-testid="legal-time-widget"
    >
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <span className="text-2xl">⏰</span>
            Heures Légales de Chasse
          </span>
          <Badge className="bg-orange-900/50 text-orange-400">
            Québec
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Current Status Banner */}
          <div 
            className={`rounded-lg p-4 ${
              isLegal 
                ? 'bg-green-900/30 border border-green-700/50' 
                : 'bg-red-900/30 border border-red-700/50'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full ${getStatusColor(currentStatus)} animate-pulse`} />
                <div>
                  <p className={`font-bold text-lg ${isLegal ? 'text-green-400' : 'text-red-400'}`}>
                    {getStatusText(currentStatus)}
                  </p>
                  <p className="text-slate-400 text-sm">
                    {currentTime.toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
              <Badge 
                className={`${isLegal ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}
              >
                {isLegal ? '✓ LÉGAL' : '✗ INTERDIT'}
              </Badge>
            </div>
          </div>

          {/* Sun Times Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <p className="text-slate-400 text-xs mb-1">Début légal</p>
              <p className="text-2xl font-bold text-amber-400">
                {legal_window?.start_time}
              </p>
              <p className="text-slate-500 text-xs mt-1">30 min avant lever</p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <p className="text-slate-400 text-xs mb-1">Fin légale</p>
              <p className="text-2xl font-bold text-purple-400">
                {legal_window?.end_time}
              </p>
              <p className="text-slate-500 text-xs mt-1">30 min après coucher</p>
            </div>
          </div>

          {/* Sun Times Row */}
          <div className="bg-slate-800/30 rounded-lg p-3">
            <div className="flex justify-around text-center">
              <div>
                <span className="text-2xl">🌅</span>
                <p className="text-white font-medium">{legal_window?.sunrise}</p>
                <p className="text-slate-500 text-xs">Lever</p>
              </div>
              <div className="border-l border-slate-700" />
              <div>
                <span className="text-2xl">☀️</span>
                <p className="text-white font-medium">{legal_window?.duration_hours}h</p>
                <p className="text-slate-500 text-xs">Durée</p>
              </div>
              <div className="border-l border-slate-700" />
              <div>
                <span className="text-2xl">🌇</span>
                <p className="text-white font-medium">{legal_window?.sunset}</p>
                <p className="text-slate-500 text-xs">Coucher</p>
              </div>
            </div>
          </div>

          {/* Recommended Slots */}
          {showSlots && slots.length > 0 && (
            <div>
              <p className="text-slate-400 text-sm mb-2 flex items-center gap-2">
                <span>📋</span>
                Créneaux recommandés
              </p>
              <div className="space-y-2">
                {slots.slice(0, 3).map((slot, index) => (
                  <div 
                    key={index}
                    className="flex items-center justify-between bg-slate-800/30 rounded-lg p-2"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">
                        {slot.light_condition === 'dawn' ? '🌅' : 
                         slot.light_condition === 'dusk' ? '🌇' : '☀️'}
                      </span>
                      <div>
                        <p className="text-white text-sm font-medium">{slot.period}</p>
                        <p className="text-slate-400 text-xs">
                          {slot.start_time} - {slot.end_time}
                        </p>
                      </div>
                    </div>
                    <Badge 
                      className="text-xs"
                      style={{ 
                        backgroundColor: `${getScoreColor(slot.score)}20`,
                        color: getScoreColor(slot.score)
                      }}
                    >
                      {slot.score}%
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Regulation Note */}
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-3">
            <p className="text-blue-400 text-xs flex items-center gap-2">
              <span>ℹ️</span>
              Règlement Québec: 30 min avant le lever jusqu'à 30 min après le coucher du soleil
            </p>
          </div>

          <Button 
            className="w-full bg-orange-600 hover:bg-orange-700 text-white"
            onClick={loadData}
          >
            🔄 Actualiser
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default LegalTimeWidget;
