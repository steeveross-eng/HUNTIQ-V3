/**
 * HuntingConditions - Hunting conditions assessment widget
 */
import React from 'react';

export const HuntingConditions = ({ 
  conditions = null,
  species = 'deer'
}) => {
  // Handle null/undefined conditions
  const safeConditions = conditions || {};
  
  const {
    overall_score = 0,
    temperature_rating = 'N/A',
    wind_rating = 'N/A',
    pressure_rating = 'N/A',
    recommendation = ''
  } = safeConditions;

  const getScoreColor = (score) => {
    if (score >= 80) return { color: '#10b981', label: 'Excellent', emoji: '🎯' };
    if (score >= 60) return { color: '#22c55e', label: 'Bon', emoji: '👍' };
    if (score >= 40) return { color: '#f59e0b', label: 'Moyen', emoji: '😐' };
    return { color: '#ef4444', label: 'Défavorable', emoji: '⚠️' };
  };

  const { color, label, emoji } = getScoreColor(overall_score);

  const factors = [
    { name: 'Température', value: temperature_rating, icon: '🌡️' },
    { name: 'Vent', value: wind_rating, icon: '💨' },
    { name: 'Pression', value: pressure_rating, icon: '📊' }
  ];

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-medium flex items-center gap-2">
          <span>🦌</span>
          Conditions de Chasse
        </h3>
        <span className="text-xs text-slate-400 capitalize">{species}</span>
      </div>
      
      {/* Overall score */}
      <div className="text-center mb-4">
        <div 
          className="inline-flex items-center justify-center w-20 h-20 rounded-full border-4"
          style={{ borderColor: color, backgroundColor: `${color}20` }}
        >
          <div className="text-center">
            <span className="text-2xl">{emoji}</span>
            <div className="text-lg font-bold" style={{ color }}>
              {overall_score}%
            </div>
          </div>
        </div>
        <p className="text-sm mt-2" style={{ color }}>
          {label}
        </p>
      </div>
      
      {/* Factors */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        {factors.map(factor => (
          <div 
            key={factor.name}
            className="text-center p-2 bg-slate-700/50 rounded-lg"
          >
            <span className="text-lg">{factor.icon}</span>
            <div className="text-xs text-slate-400 mt-1">{factor.name}</div>
            <div className="text-sm text-white font-medium">{factor.value}</div>
          </div>
        ))}
      </div>
      
      {/* Recommendation */}
      {recommendation && (
        <div className="p-3 bg-blue-900/30 rounded-lg border border-blue-700">
          <p className="text-sm text-blue-300">
            💡 {recommendation}
          </p>
        </div>
      )}
    </div>
  );
};

export default HuntingConditions;
