/**
 * BIONIC™ P1 - HuntingPressureCard
 * ==================================
 * Visualisation des résultats du huntingPressureModule.
 * 
 * @version 1.0.0
 * @architecture P2-Ready avec getFusionOutput()
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { CircularGauge, LinearGauge } from './GeoSuiteScoreGauge';

// Pressure level configurations
const PRESSURE_LEVELS = {
  extreme: { label: 'Extrême', color: '#B71C1C', bgColor: '#FFEBEE', icon: '🔴' },
  high: { label: 'Élevée', color: '#E53935', bgColor: '#FFEBEE', icon: '🟠' },
  moderate: { label: 'Modérée', color: '#FF9800', bgColor: '#FFF3E0', icon: '🟡' },
  low: { label: 'Faible', color: '#4CAF50', bgColor: '#E8F5E9', icon: '🟢' },
  minimal: { label: 'Minimale', color: '#81C784', bgColor: '#E8F5E9', icon: '✅' }
};

// Days of week
const DAYS = {
  monday: 'Lundi',
  tuesday: 'Mardi',
  wednesday: 'Mercredi',
  thursday: 'Jeudi',
  friday: 'Vendredi',
  saturday: 'Samedi',
  sunday: 'Dimanche'
};

// =============================================================================
// WEEKLY PATTERN CHART
// =============================================================================

function WeeklyPatternChart({ pattern }) {
  if (!pattern) return null;
  
  const maxValue = Math.max(...Object.values(pattern));
  
  return (
    <div className="space-y-2">
      {Object.entries(DAYS).map(([key, label]) => {
        const value = pattern[key] ?? 0;
        const percent = maxValue > 0 ? (value / maxValue) * 100 : 0;
        const isWeekend = key === 'saturday' || key === 'sunday';
        
        return (
          <div key={key} className="flex items-center gap-2">
            <span className={`text-xs w-16 ${isWeekend ? 'font-semibold' : ''}`}>
              {label}
            </span>
            <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full transition-all duration-300"
                style={{ 
                  width: `${value * 100}%`,
                  backgroundColor: value > 0.7 ? '#E53935' : value > 0.4 ? '#FF9800' : '#4CAF50'
                }}
              />
            </div>
            <span className="text-xs text-gray-600 w-10 text-right">
              {Math.round(value * 100)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// OPTIMAL TIMING LIST
// =============================================================================

function OptimalTimingList({ timing }) {
  if (!timing || timing.length === 0) return null;
  
  return (
    <div className="space-y-2">
      {timing.map((window, idx) => (
        <div 
          key={idx}
          className="p-3 bg-green-50 rounded-lg border border-green-200"
        >
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">⏰</span>
            <span className="font-medium text-green-800">
              {window.day_of_week === 'weekday' ? 'Jours de semaine' : window.day_of_week}
            </span>
            <span className="text-sm text-green-600">
              {window.start_hour}h - {window.end_hour}h
            </span>
          </div>
          <p className="text-sm text-green-700">{window.reason}</p>
        </div>
      ))}
    </div>
  );
}

// =============================================================================
// BEHAVIORAL IMPACT DISPLAY
// =============================================================================

function BehavioralImpactDisplay({ impact }) {
  if (!impact) return null;
  
  const overall = impact.overall ?? 0;
  const activityReduction = impact.activity_reduction ?? 0;
  const nocturnalShift = impact.nocturnal_shift ?? 0;
  const homeRangeFactor = impact.home_range_factor ?? 1;
  
  const getImpactColor = (value) => {
    if (value <= -0.3) return '#F44336';
    if (value <= -0.1) return '#FF9800';
    return '#4CAF50';
  };
  
  return (
    <div className="space-y-3">
      {/* Overall Impact */}
      <div className="p-3 rounded-lg" style={{ backgroundColor: getImpactColor(overall) + '15' }}>
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Impact global</span>
          <span 
            className="font-bold"
            style={{ color: getImpactColor(overall) }}
          >
            {overall >= 0 ? '+' : ''}{(overall * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      
      {/* Detailed metrics */}
      <div className="grid grid-cols-3 gap-2">
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <span className="text-lg">🦌</span>
          <p className="text-xs text-gray-500 mt-1">Activité</p>
          <p className="font-semibold text-red-600">-{Math.round(activityReduction * 100)}%</p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <span className="text-lg">🌙</span>
          <p className="text-xs text-gray-500 mt-1">Nocturne</p>
          <p className="font-semibold text-orange-600">+{Math.round(nocturnalShift * 100)}%</p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <span className="text-lg">🏠</span>
          <p className="text-xs text-gray-500 mt-1">Territoire</p>
          <p className="font-semibold text-blue-600">{Math.round(homeRangeFactor * 100)}%</p>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// MAIN CARD
// =============================================================================

export function HuntingPressureCard({ data, loading = false, compact = false }) {
  // Extract data safely
  const score = data?.score ?? 0;
  const level = data?.level ?? 'unknown';
  const pressureLevel = data?.data?.pressure_level ?? 'moderate';
  const behavioralImpact = data?.data?.behavioral_impact ?? {};
  const optimalTiming = data?.data?.optimal_timing ?? [];
  const weeklyPattern = data?.data?.weekly_pattern ?? {};
  const avoidanceZones = data?.data?.avoidance_zones ?? [];
  const hunterDensity = data?.data?.hunter_density ?? 0;
  const seasonWeeks = data?.data?.season_weeks ?? 8;
  const recommendations = data?.recommendations ?? [];
  
  const pressureConfig = PRESSURE_LEVELS[pressureLevel] || PRESSURE_LEVELS.moderate;
  
  // Fusion output for P2
  const getFusionOutput = useMemo(() => ({
    score_normalized: score / 100,
    confidence: data?.confidence ?? 0.7,
    engine: 'pressure',
    weight_suggestion: 0.2,
    behavioral_impact: behavioralImpact.overall ?? 0
  }), [score, data?.confidence, behavioralImpact]);
  
  if (loading) {
    return (
      <div className="bg-white rounded-xl border p-4 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-20 bg-gray-200 rounded mb-4" />
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </div>
      </div>
    );
  }
  
  if (!data) {
    return (
      <div className="bg-white rounded-xl border p-4 text-center text-gray-500">
        <span className="text-2xl mb-2 block">🎯</span>
        <p className="text-sm">Analyse de pression non disponible</p>
      </div>
    );
  }
  
  // Compact version
  if (compact) {
    return (
      <div className="bg-white rounded-xl border p-4" data-testid="pressure-card-compact">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <h4 className="font-semibold text-gray-900">Pression</h4>
              <p className="text-xs flex items-center gap-1" style={{ color: pressureConfig.color }}>
                {pressureConfig.icon} {pressureConfig.label}
              </p>
            </div>
          </div>
          <CircularGauge score={score} size={60} strokeWidth={6} />
        </div>
      </div>
    );
  }
  
  // Full version
  return (
    <div className="bg-white rounded-xl border overflow-hidden" data-testid="pressure-card">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-red-50 to-orange-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🎯</span>
            <div>
              <h3 className="font-bold text-gray-900">Pression de Chasse</h3>
              <p className="text-sm flex items-center gap-2">
                <span 
                  className="px-2 py-0.5 rounded-full text-xs flex items-center gap-1"
                  style={{ backgroundColor: pressureConfig.bgColor, color: pressureConfig.color }}
                >
                  {pressureConfig.icon} {pressureConfig.label}
                </span>
                <span className="text-gray-500">•</span>
                <span className="text-gray-500">{seasonWeeks} semaines de saison</span>
              </p>
            </div>
          </div>
          <CircularGauge score={score} size={80} strokeWidth={8} />
        </div>
      </div>
      
      {/* Hunter density */}
      <div className="px-4 py-2 bg-gray-50 border-b flex justify-between text-xs text-gray-500">
        <span>👥 Densité chasseurs: {hunterDensity.toFixed(1)}/100km²</span>
      </div>
      
      {/* Weekly Pattern */}
      {Object.keys(weeklyPattern).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Pattern hebdomadaire</h4>
          <WeeklyPatternChart pattern={weeklyPattern} />
        </div>
      )}
      
      {/* Behavioral Impact */}
      {Object.keys(behavioralImpact).length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Impact comportemental</h4>
          <BehavioralImpactDisplay impact={behavioralImpact} />
        </div>
      )}
      
      {/* Optimal Timing */}
      {optimalTiming.length > 0 && (
        <div className="p-4 border-b">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Fenêtres optimales</h4>
          <OptimalTimingList timing={optimalTiming} />
        </div>
      )}
      
      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="p-4 bg-gray-50">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Recommandations</h4>
          <ul className="space-y-1">
            {recommendations.slice(0, 3).map((rec, idx) => (
              <li key={idx} className="text-sm text-gray-600">{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

HuntingPressureCard.propTypes = {
  data: PropTypes.shape({
    score: PropTypes.number,
    level: PropTypes.string,
    confidence: PropTypes.number,
    data: PropTypes.shape({
      pressure_level: PropTypes.string,
      behavioral_impact: PropTypes.object,
      optimal_timing: PropTypes.array,
      weekly_pattern: PropTypes.object,
      avoidance_zones: PropTypes.array,
      hunter_density: PropTypes.number,
      season_weeks: PropTypes.number
    }),
    recommendations: PropTypes.array
  }),
  loading: PropTypes.bool,
  compact: PropTypes.bool
};

// P2 Interface
HuntingPressureCard.getFusionOutput = (data) => ({
  score_normalized: (data?.score ?? 0) / 100,
  confidence: data?.confidence ?? 0.7,
  engine: 'pressure',
  weight_suggestion: 0.2
});

export default HuntingPressureCard;
