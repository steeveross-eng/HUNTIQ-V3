/**
 * HUNTIQ V3 - Weather Service
 * API service for weather and hunting conditions
 * 
 * Note: Currently using simulated data until OpenWeatherMap API is configured
 */

import { api } from './api.client';

// OpenWeatherMap configuration (to be enabled with API key)
const OPENWEATHER_API_KEY = process.env.REACT_APP_OPENWEATHER_API_KEY;
const OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5';

// Quebec hunting regions with coordinates
const QUEBEC_REGIONS = {
  laurentides: { lat: 46.0, lon: -74.5, name: 'Laurentides' },
  abitibi: { lat: 48.5, lon: -78.0, name: 'Abitibi' },
  saguenay: { lat: 48.4, lon: -71.0, name: 'Saguenay' },
  outaouais: { lat: 46.5, lon: -76.0, name: 'Outaouais' },
  mauricie: { lat: 46.8, lon: -73.0, name: 'Mauricie' },
  estrie: { lat: 45.4, lon: -71.9, name: 'Estrie' },
  lanaudiere: { lat: 46.2, lon: -73.5, name: 'Lanaudière' },
  monteregie: { lat: 45.5, lon: -73.2, name: 'Montérégie' },
};

// Calculate hunting score based on weather conditions
const calculateHuntingScore = (weather) => {
  let score = 70; // Base score

  // Temperature impact (ideal: -5 to 5°C)
  const temp = weather.temp || 0;
  if (temp >= -10 && temp <= 10) score += 15;
  else if (temp < -20 || temp > 20) score -= 15;

  // Wind impact (ideal: < 15 km/h)
  const wind = weather.wind_speed || 0;
  if (wind < 10) score += 10;
  else if (wind > 25) score -= 15;

  // Pressure impact (stable or rising)
  const pressure = weather.pressure || 1013;
  if (pressure > 1020) score += 10;
  else if (pressure < 1000) score -= 10;

  // Humidity impact
  const humidity = weather.humidity || 50;
  if (humidity >= 60 && humidity <= 80) score += 5;

  return Math.max(0, Math.min(100, score));
};

// Get hunting status based on score
const getHuntingStatus = (score) => {
  if (score >= 85) return { status: 'Excellent', color: 'green' };
  if (score >= 70) return { status: 'Bon', color: 'blue' };
  if (score >= 50) return { status: 'Moyen', color: 'yellow' };
  return { status: 'Difficile', color: 'red' };
};

// Generate hunting advice based on conditions
const generateHuntingAdvice = (weather, score) => {
  const advice = [];
  
  if (weather.pressure > 1020) {
    advice.push('Pression en hausse - Excellente activité prévue.');
  }
  
  if (weather.wind_speed < 10) {
    advice.push('Vent faible - Conditions idéales pour l\'approche.');
  } else if (weather.wind_speed > 20) {
    advice.push('Vent fort - Privilégiez les zones abritées.');
  }
  
  if (weather.temp >= -10 && weather.temp <= 5) {
    advice.push('Température optimale pour l\'activité du gibier.');
  }
  
  if (advice.length === 0) {
    advice.push('Conditions moyennes - Restez patient et attentif.');
  }
  
  return advice.join(' ');
};

export const WeatherService = {
  /**
   * Get weather for a Quebec region
   * @param {string} regionKey - Region key (e.g., 'laurentides')
   * @returns {Promise<Object>} Weather data with hunting score
   */
  getRegionWeather: async (regionKey = 'laurentides') => {
    const region = QUEBEC_REGIONS[regionKey] || QUEBEC_REGIONS.laurentides;
    
    // If API key is configured, use real data
    if (OPENWEATHER_API_KEY) {
      try {
        const response = await fetch(
          `${OPENWEATHER_BASE_URL}/weather?lat=${region.lat}&lon=${region.lon}&appid=${OPENWEATHER_API_KEY}&units=metric&lang=fr`
        );
        const data = await response.json();
        
        const weather = {
          location: region.name,
          temp: Math.round(data.main.temp),
          feels_like: Math.round(data.main.feels_like),
          humidity: data.main.humidity,
          pressure: data.main.pressure,
          wind_speed: Math.round(data.wind.speed * 3.6), // m/s to km/h
          wind_dir: getWindDirection(data.wind.deg),
          visibility: Math.round(data.visibility / 1000),
          condition: data.weather[0].description,
          icon: mapWeatherIcon(data.weather[0].icon),
        };
        
        const score = calculateHuntingScore(weather);
        const { status } = getHuntingStatus(score);
        
        return {
          ...weather,
          hunting: {
            score,
            status,
            advice: generateHuntingAdvice(weather, score),
          },
        };
      } catch (error) {
        console.error('OpenWeatherMap API error:', error);
        // Fall back to simulated data
      }
    }
    
    // Simulated data (fallback)
    return WeatherService.getSimulatedWeather(region.name);
  },

  /**
   * Get simulated weather data
   * @param {string} location - Location name
   * @returns {Object} Simulated weather data
   */
  getSimulatedWeather: (location = 'Laurentides') => {
    const weather = {
      location,
      temp: Math.round(-5 + Math.random() * 10),
      feels_like: Math.round(-12 + Math.random() * 8),
      humidity: Math.round(60 + Math.random() * 30),
      pressure: Math.round(1010 + Math.random() * 20),
      wind_speed: Math.round(5 + Math.random() * 20),
      wind_dir: ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'][Math.floor(Math.random() * 8)],
      visibility: 10,
      condition: 'Partiellement nuageux',
      icon: 'cloud-sun',
    };
    
    const score = calculateHuntingScore(weather);
    const { status } = getHuntingStatus(score);
    
    return {
      ...weather,
      hunting: {
        score,
        status,
        advice: generateHuntingAdvice(weather, score),
      },
      sunrise: '07:15',
      sunset: '16:45',
      moon_phase: 'Croissant',
      forecast: generateForecast(),
    };
  },

  /**
   * Get 5-day forecast for region
   * @param {string} regionKey - Region key
   * @returns {Promise<Array>} Forecast data
   */
  getForecast: async (regionKey = 'laurentides') => {
    const region = QUEBEC_REGIONS[regionKey] || QUEBEC_REGIONS.laurentides;
    
    if (OPENWEATHER_API_KEY) {
      try {
        const response = await fetch(
          `${OPENWEATHER_BASE_URL}/forecast?lat=${region.lat}&lon=${region.lon}&appid=${OPENWEATHER_API_KEY}&units=metric&lang=fr&cnt=40`
        );
        const data = await response.json();
        
        // Group by day and get daily forecast
        const dailyForecasts = [];
        const days = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
        
        for (let i = 0; i < data.list.length; i += 8) {
          const item = data.list[i];
          const date = new Date(item.dt * 1000);
          
          dailyForecasts.push({
            day: days[date.getDay()],
            temp_high: Math.round(item.main.temp_max),
            temp_low: Math.round(item.main.temp_min),
            icon: mapWeatherIcon(item.weather[0].icon),
            condition: item.weather[0].description,
          });
        }
        
        return dailyForecasts.slice(0, 5);
      } catch (error) {
        console.error('OpenWeatherMap forecast error:', error);
      }
    }
    
    return generateForecast();
  },

  /**
   * Get all Quebec regions
   * @returns {Object} Regions data
   */
  getRegions: () => QUEBEC_REGIONS,

  /**
   * Calculate hunting score from weather
   * @param {Object} weather - Weather data
   * @returns {number} Hunting score (0-100)
   */
  calculateHuntingScore,

  /**
   * Get hunting status from score
   * @param {number} score - Hunting score
   * @returns {Object} Status object
   */
  getHuntingStatus,
};

// Helper: Get wind direction from degrees
const getWindDirection = (deg) => {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'];
  return directions[Math.round(deg / 45) % 8];
};

// Helper: Map OpenWeatherMap icon to local icon
const mapWeatherIcon = (owIcon) => {
  const iconMap = {
    '01d': 'sun', '01n': 'moon',
    '02d': 'cloud-sun', '02n': 'cloud-moon',
    '03d': 'cloud', '03n': 'cloud',
    '04d': 'cloud', '04n': 'cloud',
    '09d': 'cloud-rain', '09n': 'cloud-rain',
    '10d': 'cloud-rain', '10n': 'cloud-rain',
    '11d': 'storm', '11n': 'storm',
    '13d': 'cloud-snow', '13n': 'cloud-snow',
    '50d': 'fog', '50n': 'fog',
  };
  return iconMap[owIcon] || 'cloud';
};

// Helper: Generate simulated forecast
const generateForecast = () => {
  const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven'];
  const icons = ['sun', 'cloud', 'cloud-rain', 'cloud-snow', 'sun'];
  
  return days.map((day, i) => ({
    day,
    temp_high: Math.round(-3 + Math.random() * 8),
    temp_low: Math.round(-12 + Math.random() * 5),
    icon: icons[i],
  }));
};

export default WeatherService;
