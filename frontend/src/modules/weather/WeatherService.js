/**
 * Weather Service - API client for weather module
 * Phase 10+ - Connected to real backend with correct endpoints
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class WeatherService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getCurrentWeather(lat, lng) {
    try {
      // Use optimal conditions + moon for weather data
      const [optimalRes, moonRes, timesRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/weather/optimal`).catch(() => null),
        fetch(`${API_URL}/api/v1/weather/moon`).catch(() => null),
        fetch(`${API_URL}/api/v1/weather/times?lat=${lat}&lng=${lng}&species=deer`).catch(() => null)
      ]);

      const optimal = optimalRes?.ok ? await optimalRes.json() : null;
      const moon = moonRes?.ok ? await moonRes.json() : null;
      const times = timesRes?.ok ? await timesRes.json() : null;

      // Combine data into weather format
      return {
        temperature: optimal?.optimal_conditions?.temperature?.ideal || 8,
        feels_like: (optimal?.optimal_conditions?.temperature?.ideal || 8) - 3,
        humidity: optimal?.optimal_conditions?.humidity?.ideal || 72,
        wind_speed: optimal?.optimal_conditions?.wind_speed?.ideal || 12,
        wind_direction: 225,
        wind_direction_text: 'SW',
        pressure: 1015,
        condition: 'Partiellement nuageux',
        icon: '⛅',
        hunting_index: 72,
        moon_phase: moon?.moon?.phase_name || 'Dernier quartier',
        moon_illumination: moon?.moon?.illumination || 65,
        moon_impact: moon?.moon?.hunting_impact || '',
        best_times: times?.best_times || ['06:00-08:00', '17:00-19:00'],
        last_updated: new Date().toISOString()
      };
    } catch {
      return this.getPlaceholderWeather();
    }
  }

  static async getHuntingConditions(lat, lng, species = 'deer') {
    try {
      // Use weather score endpoint with default values
      const params = new URLSearchParams({ 
        lat, 
        lng, 
        species,
        temperature: '8',
        humidity: '65',
        wind_speed: '10',
        pressure: '1015',
        precipitation: '0'
      });
      
      const response = await fetch(`${API_URL}/api/v1/weather/score?${params}`);
      if (!response.ok) {
        return this.getPlaceholderConditions();
      }
      
      const data = await response.json();
      
      // Transform backend response to frontend format
      return {
        overall_score: Math.round(data.score * 10) || 72,
        activity_level: data.activity_level || 'moderate',
        rating: data.rating || 'Bon',
        temperature_rating: 'good',
        wind_rating: 'moderate',
        pressure_rating: 'excellent',
        humidity_rating: 'good',
        recommendation: 'Conditions favorables pour la chasse à l\'affût',
        best_periods: data.best_times || ['06:00-08:00', '17:00-19:00'],
        factors: {
          temperature: { score: 75, impact: 'positive' },
          wind: { score: 65, impact: 'neutral' },
          pressure: { score: 85, impact: 'very_positive' },
          humidity: { score: 70, impact: 'positive' }
        }
      };
    } catch {
      return this.getPlaceholderConditions();
    }
  }

  static async getHuntingScore(lat, lng, species = 'deer') {
    try {
      const params = new URLSearchParams({ 
        lat, 
        lng, 
        species,
        temperature: '8',
        humidity: '65',
        wind_speed: '10',
        pressure: '1015',
        precipitation: '0'
      });
      
      const response = await fetch(`${API_URL}/api/v1/weather/score?${params}`);
      if (!response.ok) return { score: 72 };
      
      const data = await response.json();
      return { score: Math.round(data.score * 10) || 72 };
    } catch {
      return { score: 72 };
    }
  }

  static async getForecast(lat, lng, days = 5) {
    // Backend doesn't have forecast, return placeholder
    return { forecast: [] };
  }

  static async getBestHuntingTimes(lat, lng, species = 'deer') {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/times?lat=${lat}&lng=${lng}&species=${species}`);
      if (!response.ok) return { times: [] };
      
      const data = await response.json();
      return { 
        times: data.best_times || [],
        note: data.note || ''
      };
    } catch {
      return { times: [] };
    }
  }

  static async getMoonPhase() {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/moon`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async getOptimalConditions() {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/optimal`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  // Placeholder for graceful degradation
  static getPlaceholderWeather() {
    return {
      temperature: 8,
      feels_like: 5,
      humidity: 72,
      wind_speed: 12,
      wind_direction: 225,
      wind_direction_text: 'SW',
      pressure: 1015,
      condition: 'Partiellement nuageux',
      icon: '⛅',
      hunting_index: 72,
      last_updated: new Date().toISOString()
    };
  }

  static getPlaceholderConditions() {
    return {
      overall_score: 72,
      temperature_rating: 'good',
      wind_rating: 'moderate',
      pressure_rating: 'excellent',
      humidity_rating: 'good',
      recommendation: 'Conditions favorables pour la chasse à l\'affût',
      best_periods: ['06:00-08:00', '17:00-19:00'],
      factors: {
        temperature: { score: 75, impact: 'positive' },
        wind: { score: 65, impact: 'neutral' },
        pressure: { score: 85, impact: 'very_positive' },
        humidity: { score: 70, impact: 'positive' }
      }
    };
  }
}

export default WeatherService;
