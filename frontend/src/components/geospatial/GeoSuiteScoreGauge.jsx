/**
 * BIONIC™ P1 - GeoSuiteScoreGauge
 * ================================
 * Jauge de score visuelle réutilisable.
 * Affiche scores 0-100 avec niveaux et couleurs.
 * 
 * @version 1.0.0
 * @architecture Réutilisable, P2-Ready
 */

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';

// Score level configurations
const SCORE_LEVELS = {
  exceptional: { min: 90, color: '#00C853', bgColor: '#E8F5E9', label: 'Exceptionnel' },
  excellent: { min: 80, color: '#2196F3', bgColor: '#E3F2FD', label: 'Excellent' },
  good: { min: 60, color: '#4CAF50', bgColor: '#E8F5E9', label: 'Bon' },
  moderate: { min: 40, color: '#FF9800', bgColor: '#FFF3E0', label: 'Modéré' },
  low: { min: 20, color: '#FF5722', bgColor: '#FBE9E7', label: 'Faible' },
  poor: { min: 0, color: '#F44336', bgColor: '#FFEBEE', label: 'Faible' }
};

const getScoreLevel = (score) => {
  if (score >= 90) return SCORE_LEVELS.exceptional;
  if (score >= 80) return SCORE_LEVELS.excellent;
  if (score >= 60) return SCORE_LEVELS.good;
  if (score >= 40) return SCORE_LEVELS.moderate;
  if (score >= 20) return SCORE_LEVELS.low;
  return SCORE_LEVELS.poor;
};

// =============================================================================
// CIRCULAR GAUGE
// =============================================================================

export function CircularGauge({ score, size = 120, strokeWidth = 10, showLabel = true }) {
  const level = useMemo(() => getScoreLevel(score), [score]);
  
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const offset = circumference - progress;
  
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={level.color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700 ease-out"
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span 
          className="text-2xl font-bold"
          style={{ color: level.color }}
        >
          {Math.round(score)}
        </span>
        {showLabel && (
          <span className="text-xs text-gray-500 mt-0.5">/100</span>
        )}
      </div>
    </div>
  );
}

CircularGauge.propTypes = {
  score: PropTypes.number.isRequired,
  size: PropTypes.number,
  strokeWidth: PropTypes.number,
  showLabel: PropTypes.bool
};

// =============================================================================
// LINEAR GAUGE
// =============================================================================

export function LinearGauge({ score, height = 8, showValue = true, showLevel = true, animated = true }) {
  const level = useMemo(() => getScoreLevel(score), [score]);
  
  return (
    <div className="w-full">
      {/* Header */}
      {(showValue || showLevel) && (
        <div className="flex justify-between items-center mb-1">
          {showValue && (
            <span className="text-lg font-semibold" style={{ color: level.color }}>
              {Math.round(score)}/100
            </span>
          )}
          {showLevel && (
            <span 
              className="text-xs px-2 py-0.5 rounded-full"
              style={{ 
                backgroundColor: level.bgColor,
                color: level.color
              }}
            >
              {level.label}
            </span>
          )}
        </div>
      )}
      
      {/* Bar */}
      <div 
        className="w-full bg-gray-200 rounded-full overflow-hidden"
        style={{ height }}
      >
        <div
          className={`h-full rounded-full ${animated ? 'transition-all duration-700 ease-out' : ''}`}
          style={{
            width: `${score}%`,
            backgroundColor: level.color
          }}
        />
      </div>
    </div>
  );
}

LinearGauge.propTypes = {
  score: PropTypes.number.isRequired,
  height: PropTypes.number,
  showValue: PropTypes.bool,
  showLevel: PropTypes.bool,
  animated: PropTypes.bool
};

// =============================================================================
// MINI GAUGE (for cards)
// =============================================================================

export function MiniGauge({ score, label, icon }) {
  const level = useMemo(() => getScoreLevel(score), [score]);
  
  return (
    <div 
      className="flex items-center gap-2 px-3 py-2 rounded-lg"
      style={{ backgroundColor: level.bgColor }}
    >
      {icon && <span className="text-lg">{icon}</span>}
      <div className="flex flex-col">
        {label && <span className="text-xs text-gray-600">{label}</span>}
        <span className="font-semibold" style={{ color: level.color }}>
          {Math.round(score)}
        </span>
      </div>
    </div>
  );
}

MiniGauge.propTypes = {
  score: PropTypes.number.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string
};

// =============================================================================
// MULTI-SCORE GAUGE (5 engines)
// =============================================================================

export function MultiScoreGauge({ scores, compact = false }) {
  const engines = [
    { key: 'corridor', label: 'Corridors', icon: '🛤️' },
    { key: 'landcover', label: 'Couvert', icon: '🌲' },
    { key: 'nutrition', label: 'Nutrition', icon: '🍎' },
    { key: 'population', label: 'Population', icon: '📊' },
    { key: 'pressure', label: 'Pression', icon: '🎯' }
  ];
  
  // Calculate global score
  const validScores = engines
    .map(e => scores[e.key])
    .filter(s => s !== undefined && s !== null);
  
  const globalScore = validScores.length > 0
    ? validScores.reduce((a, b) => a + b, 0) / validScores.length
    : null;
  
  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {engines.map(engine => {
          const score = scores[engine.key];
          if (score === undefined || score === null) return null;
          
          return (
            <MiniGauge
              key={engine.key}
              score={score}
              label={engine.label}
              icon={engine.icon}
            />
          );
        })}
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {/* Global Score */}
      {globalScore !== null && (
        <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
          <CircularGauge score={globalScore} size={80} strokeWidth={8} />
          <div>
            <h4 className="font-semibold text-gray-900">Score Global</h4>
            <p className="text-sm text-gray-500">Moyenne des 5 moteurs</p>
          </div>
        </div>
      )}
      
      {/* Individual Scores */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {engines.map(engine => {
          const score = scores[engine.key];
          
          return (
            <div 
              key={engine.key}
              className="p-3 bg-white border rounded-lg"
            >
              <div className="flex items-center gap-2 mb-2">
                <span>{engine.icon}</span>
                <span className="text-sm font-medium text-gray-700">{engine.label}</span>
              </div>
              {score !== undefined && score !== null ? (
                <LinearGauge 
                  score={score} 
                  height={6} 
                  showValue={true} 
                  showLevel={false}
                />
              ) : (
                <span className="text-xs text-gray-400">Non analysé</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

MultiScoreGauge.propTypes = {
  scores: PropTypes.shape({
    corridor: PropTypes.number,
    landcover: PropTypes.number,
    nutrition: PropTypes.number,
    population: PropTypes.number,
    pressure: PropTypes.number
  }).isRequired,
  compact: PropTypes.bool
};

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  CircularGauge,
  LinearGauge,
  MiniGauge,
  MultiScoreGauge,
  getScoreLevel,
  SCORE_LEVELS
};
