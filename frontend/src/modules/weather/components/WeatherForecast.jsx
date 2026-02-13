/**
 * WeatherForecast - Multi-day forecast display
 */
import React from 'react';

const weatherIcons = {
  clear: '☀️', sunny: '☀️', cloudy: '☁️', partly_cloudy: '⛅',
  rain: '🌧️', snow: '❄️', storm: '⛈️', fog: '🌫️'
};

export const WeatherForecast = ({ forecast = [], days = 5 }) => {
  const displayForecast = forecast.slice(0, days);

  if (!displayForecast.length) {
    return (
      <div className="text-center text-slate-400 py-4">
        Prévisions non disponibles
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <h3 className="text-white font-medium mb-3 flex items-center gap-2">
        <span>📅</span>
        Prévisions {days} jours
      </h3>
      
      <div className="grid grid-cols-5 gap-2">
        {displayForecast.map((day, index) => {
          const icon = weatherIcons[day.condition?.toLowerCase()] || '🌤️';
          
          return (
            <div 
              key={index}
              className="text-center p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
            >
              <div className="text-xs text-slate-400 mb-1">
                {day.day || `J+${index + 1}`}
              </div>
              <div className="text-2xl mb-1">{icon}</div>
              <div className="text-sm text-white font-medium">
                {day.temp_max || '--'}°
              </div>
              <div className="text-xs text-slate-400">
                {day.temp_min || '--'}°
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WeatherForecast;
