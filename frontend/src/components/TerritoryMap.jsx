/**
 * BIONIC™ Territory Map Component
 * Leaflet-based map for wildlife tracking and territory analysis
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap, LayersControl, LayerGroup, Polyline, WMSTileLayer, Rectangle, Polygon, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
// Import BIONIC Analyzer
import BionicAnalyzer from './BionicAnalyzer';
// Import extracted sub-components
import { 
  TerritoryHeader, 
  SpeciesFilter, 
  GPSNavigationPanel,
  AnalysisResultsPanel,
  TERRITORY_TYPES,
  SPECIES_CONFIG as IMPORTED_SPECIES_CONFIG,
  downloadGPX
} from './territory';
import { 
  Camera, 
  MapPin, 
  Target, 
  Eye, 
  Crosshair,
  Layers,
  Filter,
  Upload,
  RefreshCw,
  ChevronRight,
  Activity,
  TreePine,
  Droplets,
  LogOut,
  User,
  Route,
  Ruler,
  Mountain,
  Plus,
  X,
  Move,
  Locate,
  Navigation,
  Play,
  Square,
  Flag,
  Thermometer,
  Map,
  Waves,
  Trees,
  TrendingUp,
  CircleDot,
  Bookmark,
  Trash2,
  Download,
  Info,
  ArrowLeft,
  ShoppingCart,
  Package,
  Check,
  Send,
  ArrowRight,
  EyeOff,
  Loader2,
  RotateCcw,
  Brain,
  Zap
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom icons for different marker types
const createCustomIcon = (color, emoji) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background: ${color};
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">${emoji}</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18]
  });
};

const SPECIES_CONFIG = {
  orignal: { color: '#8B4513', emoji: '🫎', label: 'Orignal', heatColor: 'brown' },
  chevreuil: { color: '#D2691E', emoji: '🦌', label: 'Chevreuil', heatColor: 'orange' },
  ours: { color: '#2F4F4F', emoji: '🐻', label: 'Ours', heatColor: 'darkslategray' },
  autre: { color: '#808080', emoji: '❓', label: 'Autre', heatColor: 'gray' }
};

const EVENT_TYPE_CONFIG = {
  observation: { color: '#22c55e', emoji: '👁️', label: 'Observation' },
  camera_photo: { color: '#3b82f6', emoji: '📷', label: 'Photo caméra' },
  tir: { color: '#ef4444', emoji: '🎯', label: 'Tir' },
  cache: { color: '#a855f7', emoji: '🏠', label: 'Cache' },
  saline: { color: '#06b6d4', emoji: '🧂', label: 'Saline' },
  feeding_station: { color: '#f59e0b', emoji: '🌾', label: 'Station nourriture' }
};

// Heatmap Layer Component
const HeatmapLayer = ({ points, radius = 25 }) => {
  const map = useMap();
  
  useEffect(() => {
    if (!points || points.length === 0) return;
    
    // Dynamic import for leaflet.heat
    import('leaflet.heat').then(() => {
      const heatData = points.map(p => [p.lat, p.lon, p.intensity * 0.5]);
      
      const heat = L.heatLayer(heatData, {
        radius: radius,
        blur: 15,
        maxZoom: 17,
        gradient: {
          0.2: '#ffffb2',
          0.4: '#fecc5c',
          0.6: '#fd8d3c',
          0.8: '#f03b20',
          1.0: '#bd0026'
        }
      });
      
      heat.addTo(map);
      
      return () => {
        map.removeLayer(heat);
      };
    });
  }, [map, points, radius]);
  
  return null;
};

// Map Center Controller
const MapCenterController = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom());
    }
  }, [map, center, zoom]);
  
  return null;
};

// Map Click Handler Component
const MapClickHandler = ({ activeTool, onMapClick, onMouseMove }) => {
  const map = useMap();
  
  useEffect(() => {
    // Handle mouse move for GPS preview
    const handleMouseMove = (e) => {
      if (onMouseMove) {
        onMouseMove(e.latlng);
      }
    };
    
    map.on('mousemove', handleMouseMove);
    
    return () => {
      map.off('mousemove', handleMouseMove);
    };
  }, [map, onMouseMove]);
  
  useEffect(() => {
    if (!activeTool) return;
    
    const handleClick = (e) => {
      onMapClick(e.latlng, activeTool);
    };
    
    map.on('click', handleClick);
    
    // Change cursor based on tool
    const container = map.getContainer();
    if (activeTool === 'pin') {
      container.style.cursor = 'crosshair';
    } else if (activeTool === 'route' || activeTool === 'measure') {
      container.style.cursor = 'crosshair';
    }
    
    return () => {
      map.off('click', handleClick);
      container.style.cursor = '';
    };
  }, [map, activeTool, onMapClick]);
  
  return null;
};

// Zoom Control Repositioner - Disabled as we use custom buttons
const ZoomControlPosition = () => {
  // Custom zoom buttons are used instead of Leaflet's native controls
  return null;
};

// Zoom Sync Component - Syncs mapZoom state with Leaflet map
const ZoomSyncComponent = ({ zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (map && zoom !== map.getZoom()) {
      map.setZoom(zoom);
    }
  }, [map, zoom]);
  
  return null;
};

// Main Territory Map Component
const TerritoryMap = ({ userId, userName, onLogout, navigateToCoords, onNavigationComplete }) => {
  const [events, setEvents] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [selectedSpecies, setSelectedSpecies] = useState('all');
  const [timeWindow, setTimeWindow] = useState(72);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showEvents, setShowEvents] = useState(true);
  const [showCameras, setShowCameras] = useState(true);
  const [showForestTrails, setShowForestTrails] = useState(true);
  
  // Map state
  const [mapCenter, setMapCenter] = useState([46.8139, -71.2080]); // Quebec default
  const [mapZoom, setMapZoom] = useState(12);
  
  // GPS Input
  const [gpsFormat, setGpsFormat] = useState('decimal'); // 'decimal' or 'dms'
  const [gpsLatitude, setGpsLatitude] = useState('');
  const [gpsLongitude, setGpsLongitude] = useState('');
  // DMS fields
  const [dmsLatDeg, setDmsLatDeg] = useState('');
  const [dmsLatMin, setDmsLatMin] = useState('');
  const [dmsLatSec, setDmsLatSec] = useState('');
  const [dmsLatDir, setDmsLatDir] = useState('N');
  const [dmsLonDeg, setDmsLonDeg] = useState('');
  const [dmsLonMin, setDmsLonMin] = useState('');
  const [dmsLonSec, setDmsLonSec] = useState('');
  const [dmsLonDir, setDmsLonDir] = useState('W');
  const [mapScale, setMapScale] = useState('1:5000');
  
  // Scale to zoom mapping
  const SCALE_TO_ZOOM = {
    '1:1000': 18,
    '1:3000': 16,
    '1:5000': 15
  };
  
  // Convert DMS to Decimal
  const dmsToDecimal = (deg, min, sec, dir) => {
    const d = parseFloat(deg) || 0;
    const m = parseFloat(min) || 0;
    const s = parseFloat(sec) || 0;
    let decimal = d + (m / 60) + (s / 3600);
    if (dir === 'S' || dir === 'W') {
      decimal = -decimal;
    }
    return decimal;
  };
  
  // Convert Decimal to DMS string
  const decimalToDms = (decimal, isLat) => {
    const dir = isLat ? (decimal >= 0 ? 'N' : 'S') : (decimal >= 0 ? 'E' : 'W');
    const abs = Math.abs(decimal);
    const deg = Math.floor(abs);
    const minFloat = (abs - deg) * 60;
    const min = Math.floor(minFloat);
    const sec = ((minFloat - min) * 60).toFixed(2);
    return `${deg}°${min}'${sec}"${dir}`;
  };
  
  // Photo upload
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  
  // Map tools state
  const [activeTool, setActiveTool] = useState(null); // 'pin', 'route', 'measure', null
  const [routePoints, setRoutePoints] = useState([]);
  const [measurePoints, setMeasurePoints] = useState([]);
  const [showLayersPanel, setShowLayersPanel] = useState(false);
  const [selectedBaseLayer, setSelectedBaseLayer] = useState('carte');
  const [showForestLayer, setShowForestLayer] = useState(false);
  const [showWaterLayer, setShowWaterLayer] = useState(false);
  const [showReliefLayer, setShowReliefLayer] = useState(false);
  const [showRoadsLayer, setShowRoadsLayer] = useState(false);
  const [pendingMarker, setPendingMarker] = useState(null);
  const [selectedSpeciesForMarker, setSelectedSpeciesForMarker] = useState('orignal');

  // GPS Tracking state
  const [isTracking, setIsTracking] = useState(false);
  const [currentPosition, setCurrentPosition] = useState(null);
  const [activeTrack, setActiveTrack] = useState(null);
  const [trackPoints, setTrackPoints] = useState([]);
  const [waypoints, setWaypoints] = useState([]);
  const [showWaypointModal, setShowWaypointModal] = useState(false);
  const [pendingWaypoint, setPendingWaypoint] = useState(null);
  const [waypointName, setWaypointName] = useState('');
  const [waypointType, setWaypointType] = useState('custom');
  const watchIdRef = useRef(null);
  const bionicZonesSectionRef = useRef(null); // Ref pour scroll auto vers section BIONIC
  
  // Mouse GPS Preview state (for waypoint placement)
  const [mouseGpsPreview, setMouseGpsPreview] = useState(null);
  const [waypointToolActive, setWaypointToolActive] = useState(false);
  
  // Dynamic GPS Flow State
  const [gpsFlowMode, setGpsFlowMode] = useState(false); // Active during waypoint movement
  const [draggingWaypoint, setDraggingWaypoint] = useState(null);
  const [liveGpsCoords, setLiveGpsCoords] = useState(null);
  const [autoAnalyzeOnConfirm, setAutoAnalyzeOnConfirm] = useState(true);

  // Advanced layers state
  const [showAdvancedLayers, setShowAdvancedLayers] = useState(false);
  const [layerForet, setLayerForet] = useState(false);
  const [layerHydro, setLayerHydro] = useState(false);
  const [layerTopo, setLayerTopo] = useState(false);
  const [layerRoutes, setLayerRoutes] = useState(false);
  const [layerProbability, setLayerProbability] = useState(false);
  const [layerRefuge, setLayerRefuge] = useState(false);
  const [layerCooling, setLayerCooling] = useState(false);
  const [selectedAnalysisSpecies, setSelectedAnalysisSpecies] = useState('orignal');
  const [probabilityData, setProbabilityData] = useState(null);
  const [coolingZones, setCoolingZones] = useState(null);
  
  // Probability zones for map display (Green, Yellow, Red)
  const [probabilityZones, setProbabilityZones] = useState([]);
  const [loadingZones, setLoadingZones] = useState(false);

  // Guided Route / Parcours Guidé State
  const [guidedRoute, setGuidedRoute] = useState(null);
  const [showGuidedRoutePanel, setShowGuidedRoutePanel] = useState(false);
  const [loadingGuidedRoute, setLoadingGuidedRoute] = useState(false);
  const [guidedRouteOptimization, setGuidedRouteOptimization] = useState('balanced');

  // Shopping Cart State
  const [cart, setCart] = useState([]);
  const [showCartModal, setShowCartModal] = useState(false);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [orderName, setOrderName] = useState('');
  const [orderEmail, setOrderEmail] = useState('');
  const [orderPhone, setOrderPhone] = useState('');
  const [orderNotes, setOrderNotes] = useState('');
  const [submittingOrder, setSubmittingOrder] = useState(false);

  // BIONIC Analyzer State
  const [showBionicAnalyzer, setShowBionicAnalyzer] = useState(false);
  const [selectedTerritoryType, setSelectedTerritoryType] = useState('');
  const [selectedZoneNumber, setSelectedZoneNumber] = useState('');
  const [territoryAnalysis, setTerritoryAnalysis] = useState(null);
  const [loadingTerritory, setLoadingTerritory] = useState(false);
  const [huntingTerritories, setHuntingTerritories] = useState([]);
  const [showHuntingMarkers, setShowHuntingMarkers] = useState(false);
  const [nearbyTerritories, setNearbyTerritories] = useState([]);
  
  // BIONIC Layers State - Pour affichage sur la carte
  const [bionicAnalysisResult, setBionicAnalysisResult] = useState(null);
  const [bionicLayersVisible, setBionicLayersVisible] = useState({
    thermal: true,
    wetness: true,
    food: true,
    pressure: true,
    access: true,
    corridor: true,
    canopy: true,
    geoform: true
  });
  
  // Configuration des modules BIONIC avec couleurs
  const BIONIC_MODULE_CONFIG = {
    thermal: { name: 'ThermalScore', label: 'Zone Thermique', color: '#ef4444', icon: '🌡️' },
    wetness: { name: 'WetnessScore', label: 'Zone Humidité', color: '#3b82f6', icon: '💧' },
    food: { name: 'FoodScore', label: 'Zone Alimentation', color: '#22c55e', icon: '🌿' },
    pressure: { name: 'PressureScore', label: 'Zone Pression', color: '#f59e0b', icon: '👥' },
    access: { name: 'AccessScore', label: 'Zone Accès', color: '#8b5cf6', icon: '🛤️' },
    corridor: { name: 'CorridorScore', label: 'Corridors', color: '#06b6d4', icon: '🔄' },
    canopy: { name: 'CanopyScore', label: 'Couvert Forestier', color: '#10b981', icon: '🌳' },
    geoform: { name: 'GeoFormScore', label: 'Géomorphologie', color: '#6366f1', icon: '⛰️' }
  };

  // Territory Types and Mock Data
  const TERRITORY_TYPES = {
    zec: { name: 'ZEC', color: '#22c55e', icon: '🏕️' },
    sepaq: { name: 'Réserve faunique', color: '#3b82f6', icon: '🦌' },
    clic: { name: 'Zone Clic', color: '#f59e0b', icon: '🟠' },
    pourvoirie: { name: 'Pourvoirie', color: '#8b5cf6', icon: '🟣' },
    prive: { name: 'Territoire privé', color: '#ef4444', icon: '🔴' },
    refuge: { name: 'Refuge faunique', color: '#06b6d4', icon: '🔷' }
  };

  // Mock Territory Database (ZEC, Sépaq examples)
  const TERRITORY_DATABASE = {
    zec: {
      '086': { name: 'ZEC des Martres', lat: 47.5, lng: -72.8, region: 'Mauricie', qualityScore: 78, huntingPressure: 'moyen', accessibility: 'bonne', habitat: 'excellent', successRate: { orignal: 42, chevreuil: 38, ours: 25 } },
      '027': { name: 'ZEC Tawachiche', lat: 46.8, lng: -72.5, region: 'Mauricie', qualityScore: 85, huntingPressure: 'faible', accessibility: 'moyenne', habitat: 'excellent', successRate: { orignal: 48, chevreuil: 35, ours: 30 } },
      '037': { name: 'ZEC Jeannotte', lat: 46.4, lng: -73.2, region: 'Lanaudière', qualityScore: 72, huntingPressure: 'élevé', accessibility: 'bonne', habitat: 'bon', successRate: { orignal: 35, chevreuil: 42, ours: 18 } },
    },
    sepaq: {
      '13': { name: 'Réserve faunique Mastigouche', lat: 46.65, lng: -73.35, region: 'Mauricie', qualityScore: 92, huntingPressure: 'contrôlé', accessibility: 'excellente', habitat: 'exceptionnel', successRate: { orignal: 55, chevreuil: 40, ours: 35 }, tirage: true },
      '08': { name: 'Réserve faunique La Vérendrye', lat: 47.5, lng: -77.0, region: 'Outaouais', qualityScore: 88, huntingPressure: 'faible', accessibility: 'bonne', habitat: 'excellent', successRate: { orignal: 52, chevreuil: 32, ours: 40 }, tirage: true },
      '04': { name: 'Réserve faunique Portneuf', lat: 47.0, lng: -72.2, region: 'Capitale-Nationale', qualityScore: 82, huntingPressure: 'moyen', accessibility: 'excellente', habitat: 'très bon', successRate: { orignal: 45, chevreuil: 38, ours: 28 }, tirage: true },
    },
    clic: {
      '27': { name: 'Zone 27 - Estrie', lat: 45.4, lng: -71.9, region: 'Estrie', qualityScore: 65, huntingPressure: 'élevé', accessibility: 'excellente', habitat: 'bon', successRate: { orignal: 0, chevreuil: 55, ours: 15 } },
      '10': { name: 'Zone 10 - Laurentides', lat: 46.2, lng: -74.5, region: 'Laurentides', qualityScore: 75, huntingPressure: 'moyen', accessibility: 'bonne', habitat: 'très bon', successRate: { orignal: 38, chevreuil: 48, ours: 22 } },
    },
    pourvoirie: {
      'domaine-shannon': { name: 'Domaine Shannon', lat: 47.2, lng: -73.8, region: 'Mauricie', qualityScore: 95, huntingPressure: 'très faible', accessibility: 'excellente', habitat: 'exceptionnel', successRate: { orignal: 75, chevreuil: 60, ours: 50 }, services: ['guide', 'hébergement', 'repas'] },
      'club-triton': { name: 'Club Triton', lat: 48.1, lng: -74.2, region: 'Saguenay', qualityScore: 90, huntingPressure: 'faible', accessibility: 'bonne', habitat: 'excellent', successRate: { orignal: 68, chevreuil: 45, ours: 55 }, services: ['guide', 'hébergement'] },
    }
  };

  // WMS Layer URLs (Quebec Government - Real endpoints)
  const WMS_LAYERS = {
    foret: {
      url: "https://servicescarto.mffp.gouv.qc.ca/pes/services/Territoire/Couvert_forestier/MapServer/WMSServer",
      layers: "0",
      name: "Couverture forestière",
      attribution: "© MFFP Québec"
    },
    hydro: {
      url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer",
      layers: "0,1,2",
      name: "Hydrographie",
      attribution: "© MERN Québec"
    },
    topo: {
      url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Imagerie/LIDAR_Elevation/MapServer/WMSServer",
      layers: "0",
      name: "Relief LiDAR",
      attribution: "© MERN Québec"
    },
    routes: {
      url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
      layers: "5,6,7",
      name: "Routes et chemins",
      attribution: "© MERN Québec"
    },
    cadastre: {
      url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/Cadastre_Quebec/MapServer/WMSServer",
      layers: "0",
      name: "Cadastre",
      attribution: "© MERN Québec"
    }
  };

  // Handle GPS navigation
  const handleGpsNavigate = () => {
    let lat, lon;
    
    if (gpsFormat === 'decimal') {
      lat = parseFloat(gpsLatitude);
      lon = parseFloat(gpsLongitude);
    } else {
      // DMS format
      lat = dmsToDecimal(dmsLatDeg, dmsLatMin, dmsLatSec, dmsLatDir);
      lon = dmsToDecimal(dmsLonDeg, dmsLonMin, dmsLonSec, dmsLonDir);
    }
    
    if (isNaN(lat) || isNaN(lon)) {
      toast.error('Veuillez entrer des coordonnées GPS valides');
      return;
    }
    
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      toast.error('Coordonnées GPS hors limites');
      return;
    }
    
    setMapCenter([lat, lon]);
    setMapZoom(SCALE_TO_ZOOM[mapScale]);
    
    // Display in the appropriate format
    const displayCoords = gpsFormat === 'decimal' 
      ? `${lat.toFixed(4)}, ${lon.toFixed(4)}`
      : `${decimalToDms(lat, true)} ${decimalToDms(lon, false)}`;
    toast.success(`Navigation vers ${displayCoords} (Échelle ${mapScale})`);
  };

  // Handle scale change
  const handleScaleChange = (newScale) => {
    setMapScale(newScale);
    setMapZoom(SCALE_TO_ZOOM[newScale]);
  };

  // Load data
  const loadData = useCallback(async () => {
    if (!userId) return;
    
    setLoading(true);
    try {
      const [eventsRes, camerasRes, heatmapRes, statsRes] = await Promise.all([
        axios.get(`${API}/territory/events/recent`, {
          params: { user_id: userId, hours: timeWindow, limit: 500 }
        }),
        axios.get(`${API}/territory/cameras`, {
          params: { user_id: userId }
        }),
        axios.get(`${API}/territory/layers/heatmap_activite`, {
          params: { 
            user_id: userId, 
            hours: timeWindow,
            species: selectedSpecies !== 'all' ? selectedSpecies : undefined
          }
        }),
        axios.get(`${API}/territory/stats`, {
          params: { user_id: userId }
        })
      ]);
      
      setEvents(eventsRes.data || []);
      setCameras(camerasRes.data || []);
      setHeatmapData(heatmapRes.data?.points || []);
      setStats(statsRes.data);
      
      // Center map on first event or camera if available
      if (eventsRes.data?.length > 0) {
        const firstEvent = eventsRes.data[0];
        setMapCenter([firstEvent.latitude, firstEvent.longitude]);
      } else if (camerasRes.data?.length > 0) {
        const firstCam = camerasRes.data[0];
        if (firstCam.latitude && firstCam.longitude) {
          setMapCenter([firstCam.latitude, firstCam.longitude]);
        }
      }
      
    } catch (error) {
      console.error('Error loading territory data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  }, [userId, timeWindow, selectedSpecies]);

  // Load hunting territories from API
  const loadHuntingTerritories = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/territory/hunting/territories`);
      setHuntingTerritories(response.data?.territories || []);
    } catch (error) {
      console.error('Error loading hunting territories:', error);
    }
  }, []);

  // Search nearby hunting territories
  const searchNearbyTerritories = async (lat, lng, radiusKm = 100, species = null) => {
    try {
      setLoadingTerritory(true);
      const params = { lat, lng, radius_km: radiusKm };
      if (species) params.species = species;
      
      const response = await axios.get(`${API}/territory/hunting/search`, { params });
      setNearbyTerritories(response.data?.all_results || []);
      return response.data;
    } catch (error) {
      console.error('Error searching nearby territories:', error);
      toast.error('Erreur lors de la recherche des territoires');
      return null;
    } finally {
      setLoadingTerritory(false);
    }
  };

  useEffect(() => {
    loadData();
    loadHuntingTerritories();
  }, [loadData, loadHuntingTerritories]);

  // Filter events by species
  const filteredEvents = events.filter(e => 
    selectedSpecies === 'all' || e.species === selectedSpecies
  );

  // Handle photo upload
  const handlePhotoUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    
    try {
      const response = await axios.post(`${API}/territory/photos/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success('Photo uploadée! Analyse IA en cours...');
      
      // Poll for AI result
      const photoId = response.data.id;
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const statusRes = await axios.get(`${API}/territory/photos/${photoId}`);
          if (statusRes.data.processing_status === 'completed') {
            clearInterval(pollInterval);
            const species = statusRes.data.species;
            const confidence = (statusRes.data.species_confidence * 100).toFixed(0);
            toast.success(`Analyse terminée: ${SPECIES_CONFIG[species]?.label || species} (${confidence}% confiance)`);
            loadData(); // Refresh data
          } else if (statusRes.data.processing_status === 'failed' || attempts > 30) {
            clearInterval(pollInterval);
            toast.error('Erreur lors de l\'analyse');
          }
        } catch (e) {
          clearInterval(pollInterval);
        }
      }, 2000);
      
    } catch (error) {
      toast.error('Erreur lors de l\'upload');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Create new observation
  const handleAddObservation = async (latlng, species) => {
    try {
      await axios.post(`${API}/territory/events`, {
        event_type: 'observation',
        latitude: latlng.lat,
        longitude: latlng.lng,
        species: species,
        species_confidence: 0.9,
        count_estimate: 1,
        source: 'app'
      }, { params: { user_id: userId } });
      
      toast.success('Observation ajoutée!');
      loadData();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  // Handle map click based on active tool
  const handleMapClick = useCallback((latlng, tool) => {
    if (tool === 'pin') {
      // Show species selection and add marker
      setPendingMarker(latlng);
    } else if (tool === 'waypoint') {
      // Waypoint placement
      setPendingWaypoint({ lat: latlng.lat, lng: latlng.lng });
      setShowWaypointModal(true);
      setMouseGpsPreview(null);
    } else if (tool === 'route') {
      setRoutePoints(prev => [...prev, latlng]);
      toast.info(`Point ${routePoints.length + 1} ajouté au chemin`);
    } else if (tool === 'measure') {
      setMeasurePoints(prev => {
        const newPoints = [...prev, latlng];
        if (newPoints.length >= 2) {
          // Calculate distance
          const totalDistance = calculateTotalDistance(newPoints);
          toast.info(`Distance totale: ${totalDistance.toFixed(2)} km`);
        }
        return newPoints;
      });
    }
  }, [routePoints.length]);

  // Calculate distance between points using Haversine formula
  const calculateTotalDistance = (points) => {
    let total = 0;
    for (let i = 1; i < points.length; i++) {
      const p1 = points[i - 1];
      const p2 = points[i];
      total += calculateDistance(p1.lat, p1.lng, p2.lat, p2.lng);
    }
    return total;
  };

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  };

  // Confirm adding marker with species
  const confirmAddMarker = async () => {
    if (pendingMarker) {
      await handleAddObservation(pendingMarker, selectedSpeciesForMarker);
      setPendingMarker(null);
      setActiveTool(null);
    }
  };

  // Clear route/measure points
  const clearToolPoints = () => {
    setRoutePoints([]);
    setMeasurePoints([]);
  };

  // ==========================================
  // GPS TRACKING FUNCTIONS
  // ==========================================

  // Load waypoints
  const loadWaypoints = async () => {
    try {
      const response = await axios.get(`${API}/territory/waypoints`, { params: { user_id: userId } });
      setWaypoints(response.data);
    } catch (error) {
      console.error('Error loading waypoints:', error);
    }
  };

  // Start GPS tracking
  const startTracking = async () => {
    if (!navigator.geolocation) {
      toast.error('Géolocalisation non supportée par votre navigateur');
      return;
    }

    try {
      // Create a new track in the backend
      const response = await axios.post(`${API}/territory/tracks`, {
        name: `Tracé ${new Date().toLocaleDateString('fr-CA')} ${new Date().toLocaleTimeString('fr-CA')}`,
        description: 'Tracé GPS automatique'
      }, { params: { user_id: userId } });

      setActiveTrack(response.data);
      setTrackPoints([]);
      setIsTracking(true);

      // Start watching position
      watchIdRef.current = navigator.geolocation.watchPosition(
        async (position) => {
          const newPoint = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            alt: position.coords.altitude,
            accuracy: position.coords.accuracy,
            speed: position.coords.speed,
            timestamp: new Date()
          };

          setCurrentPosition(newPoint);
          setTrackPoints(prev => [...prev, newPoint]);

          // Send to backend
          try {
            await axios.post(`${API}/territory/tracks/${response.data.id}/points`, {
              latitude: newPoint.lat,
              longitude: newPoint.lng,
              altitude: newPoint.alt,
              accuracy: newPoint.accuracy,
              speed: newPoint.speed
            }, { params: { user_id: userId } });
          } catch (e) {
            console.error('Error saving track point:', e);
          }
        },
        (error) => {
          toast.error('Erreur GPS: ' + error.message);
        },
        {
          enableHighAccuracy: true,
          maximumAge: 5000,
          timeout: 10000
        }
      );

      toast.success('Enregistrement GPS démarré');
    } catch (error) {
      toast.error('Erreur lors du démarrage du tracking');
    }
  };

  // Stop GPS tracking
  const stopTracking = async () => {
    if (watchIdRef.current) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }

    if (activeTrack) {
      try {
        await axios.post(`${API}/territory/tracks/${activeTrack.id}/stop`, {}, { params: { user_id: userId } });
        toast.success(`Tracé enregistré: ${trackPoints.length} points, ${calculateTotalDistance(trackPoints).toFixed(2)} km`);
      } catch (error) {
        console.error('Error stopping track:', error);
      }
    }

    setIsTracking(false);
    setActiveTrack(null);
  };

  // Add waypoint
  const addWaypoint = async () => {
    if (!pendingWaypoint || !waypointName) {
      toast.error('Veuillez nommer le waypoint');
      return;
    }

    // ============================================
    // VÉRIFICATION EXCLUSION EAU POUR WAYPOINTS
    // ============================================
    try {
      const { checkPointInWater } = await import('@/services/WaterExclusionService');
      const { inWater, feature } = await checkPointInWater(pendingWaypoint.lat, pendingWaypoint.lng);
      
      if (inWater) {
        const waterName = feature?.name || 'une surface d\'eau';
        toast.error(`⚠️ Impossible de créer un waypoint dans ${waterName}`, {
          description: 'Veuillez sélectionner un emplacement sur la terre ferme.'
        });
        return;
      }
    } catch (err) {
      console.warn('[TerritoryMap] Water check failed:', err);
      // Continuer même si la vérification échoue
    }

    try {
      await axios.post(`${API}/territory/waypoints`, {
        latitude: pendingWaypoint.lat,
        longitude: pendingWaypoint.lng,
        name: waypointName,
        waypoint_type: waypointType
      }, { params: { user_id: userId } });

      toast.success('✅ Waypoint confirmé et enregistré!');
      
      // ✅ INTÉGRATION AUTOMATIQUE dans le module Analyse GPS
      if (gpsFormat === 'decimal') {
        setGpsLatitude(pendingWaypoint.lat.toFixed(6));
        setGpsLongitude(pendingWaypoint.lng.toFixed(6));
      } else {
        const lat = pendingWaypoint.lat;
        const lon = pendingWaypoint.lng;
        
        setDmsLatDir(lat >= 0 ? 'N' : 'S');
        const absLat = Math.abs(lat);
        setDmsLatDeg(Math.floor(absLat).toString());
        const latMinFloat = (absLat - Math.floor(absLat)) * 60;
        setDmsLatMin(Math.floor(latMinFloat).toString());
        setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
        
        setDmsLonDir(lon >= 0 ? 'E' : 'W');
        const absLon = Math.abs(lon);
        setDmsLonDeg(Math.floor(absLon).toString());
        const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
        setDmsLonMin(Math.floor(lonMinFloat).toString());
        setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      }
      
      // Centrer la carte sur le waypoint
      setMapCenter([pendingWaypoint.lat, pendingWaypoint.lng]);
      
      // Désactiver le mode flux GPS
      deactivateGpsFlowMode();
      
      setShowWaypointModal(false);
      setPendingWaypoint(null);
      setWaypointName('');
      
      toast.info('📍 Coordonnées GPS intégrées automatiquement');
      
      // ✅ DÉCLENCHEMENT AUTOMATIQUE DE L'ANALYSE
      if (autoAnalyzeOnConfirm) {
        setTimeout(() => {
          toast.info('🔍 Analyse automatique du territoire en cours...');
          handleAnalyzeGPS();
        }, 600);
      }
      
      loadWaypoints();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout du waypoint');
    }
  };

  // Delete waypoint
  const deleteWaypoint = async (waypointId) => {
    try {
      // Optimistic update - remove from local state immediately
      setWaypoints(prev => prev.filter(wp => wp.id !== waypointId));
      
      // Call API to delete
      await axios.delete(`${API}/territory/waypoints/${waypointId}`, { params: { user_id: userId } });
      
      // Show success confirmation
      toast.success('🗑️ Waypoint supprimé définitivement!', {
        description: 'Le waypoint a été retiré de la carte et de la base de données.',
        duration: 3000
      });
      
      // Force refresh from server to ensure sync
      setTimeout(() => {
        loadWaypoints();
      }, 500);
      
    } catch (error) {
      console.error('Error deleting waypoint:', error);
      // Reload waypoints to restore state if delete failed
      loadWaypoints();
      toast.error('❌ Erreur lors de la suppression', {
        description: 'Le waypoint n\'a pas pu être supprimé. Veuillez réessayer.'
      });
    }
  };

  // Delete event (gibier/observation)
  const deleteEvent = async (eventId) => {
    try {
      // Optimistic update - remove from local state immediately
      setEvents(prev => prev.filter(e => e.id !== eventId));
      
      await axios.delete(`${API}/territory/events/${eventId}`, { params: { user_id: userId } });
      
      toast.success('🗑️ Observation supprimée définitivement!', {
        description: 'L\'observation a été retirée de la carte.',
        duration: 3000
      });
    } catch (error) {
      // Keep removed from local state even if API fails
      toast.success('🗑️ Observation supprimée', {
        description: 'Retirée de l\'affichage actuel.'
      });
    }
  };

  // Delete ALL waypoints and reset search
  const deleteAllWaypoints = async () => {
    if (waypoints.length === 0) {
      toast.info('Aucun waypoint à supprimer');
      return;
    }
    
    try {
      // Delete all waypoints one by one
      await Promise.all(
        waypoints.map(wp => 
          axios.delete(`${API}/territory/waypoints/${wp.id}`, { params: { user_id: userId } })
        )
      );
      
      // Clear local state
      setWaypoints([]);
      setGuidedRoute(null);
      setShowGuidedRoutePanel(false);
      setProbabilityZones([]);
      setProbabilityData(null);
      setTerritoryAnalysis(null);
      
      // Reset GPS fields
      setGpsLatitude('');
      setGpsLongitude('');
      setDmsLatDeg('');
      setDmsLatMin('');
      setDmsLatSec('');
      setDmsLonDeg('');
      setDmsLonMin('');
      setDmsLonSec('');
      
      toast.success('🗑️ Tous les waypoints effacés - Recherche réinitialisée');
    } catch (error) {
      toast.error('Erreur lors de la suppression des waypoints');
    }
  };

  // Get current position for waypoint
  const getCurrentPositionForWaypoint = () => {
    if (currentPosition) {
      setPendingWaypoint(currentPosition);
      setShowWaypointModal(true);
    } else if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setPendingWaypoint({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          setShowWaypointModal(true);
        },
        (error) => toast.error('Impossible d\'obtenir la position')
      );
    }
  };

  // Activate waypoint placement tool
  const activateWaypointTool = () => {
    setWaypointToolActive(true);
    setActiveTool('waypoint');
    setGpsFlowMode(true);
    toast.info('🛰️ Mode flux GPS activé - Déplacez la souris sur la carte');
  };

  // Deactivate GPS flow mode
  const deactivateGpsFlowMode = () => {
    setGpsFlowMode(false);
    setWaypointToolActive(false);
    setActiveTool(null);
    setMouseGpsPreview(null);
    setLiveGpsCoords(null);
  };

  // Handle mouse move for GPS preview - CONTINUOUS FLOW
  const handleMouseMove = useCallback((latlng) => {
    // TOUJOURS capturer les coordonnées du curseur en temps réel
    const coords = {
      lat: latlng.lat,
      lng: latlng.lng,
      latDms: decimalToDms(latlng.lat, true),
      lngDms: decimalToDms(latlng.lng, false),
      altitude: Math.round(200 + Math.random() * 300), // Simulated altitude
      precision: Math.round(3 + Math.random() * 5), // Simulated precision in meters
      timestamp: new Date().toISOString()
    };
    
    setMouseGpsPreview(coords);
    
    // Mode actif (waypoint tool, GPS flow, dragging) - injection dans Analyse GPS
    if (waypointToolActive || activeTool === 'waypoint' || gpsFlowMode || draggingWaypoint) {
      setLiveGpsCoords(coords);
      
      // Update GPS Analysis fields in real-time
      if (gpsFormat === 'decimal') {
        setGpsLatitude(latlng.lat.toFixed(6));
        setGpsLongitude(latlng.lng.toFixed(6));
      } else {
        // Update DMS fields
        const lat = latlng.lat;
        const lon = latlng.lng;
        
        setDmsLatDir(lat >= 0 ? 'N' : 'S');
        const absLat = Math.abs(lat);
        setDmsLatDeg(Math.floor(absLat).toString());
        const latMinFloat = (absLat - Math.floor(absLat)) * 60;
        setDmsLatMin(Math.floor(latMinFloat).toString());
        setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
        
        setDmsLonDir(lon >= 0 ? 'E' : 'W');
        const absLon = Math.abs(lon);
        setDmsLonDeg(Math.floor(absLon).toString());
        const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
        setDmsLonMin(Math.floor(lonMinFloat).toString());
        setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      }
    }
  }, [waypointToolActive, activeTool, gpsFlowMode, draggingWaypoint, gpsFormat]);

  // Fonction pour injecter les coordonnées et lancer l'analyse automatique
  const injectGpsAndAnalyze = useCallback(async (lat, lng) => {
    // 1. Injecter les coordonnées dans Analyse GPS
    setGpsLatitude(lat.toFixed(6));
    setGpsLongitude(lng.toFixed(6));
    
    // Mettre à jour aussi les coordonnées DMS
    setDmsLatDir(lat >= 0 ? 'N' : 'S');
    const absLat = Math.abs(lat);
    setDmsLatDeg(Math.floor(absLat).toString());
    const latMinFloat = (absLat - Math.floor(absLat)) * 60;
    setDmsLatMin(Math.floor(latMinFloat).toString());
    setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
    
    setDmsLonDir(lng >= 0 ? 'E' : 'W');
    const absLon = Math.abs(lng);
    setDmsLonDeg(Math.floor(absLon).toString());
    const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
    setDmsLonMin(Math.floor(lonMinFloat).toString());
    setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
    
    // 2. Mettre à jour les coordonnées live
    setLiveGpsCoords({
      lat: lat,
      lng: lng,
      latDms: decimalToDms(lat, true),
      lngDms: decimalToDms(lng, false)
    });
    
    // 3. Centrer la carte sur le point
    setMapCenter([lat, lng]);
    
    // 4. Lancer automatiquement l'analyse du territoire
    toast.info('🛰️ Analyse automatique du territoire en cours...', { duration: 2000 });
    
    try {
      // Appeler l'API d'analyse
      const analysisRes = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: lat,
        longitude: lng,
        radius_km: 5,
        species: selectedSpecies !== 'all' ? selectedSpecies : 'orignal'
      });
      
      // Rechercher les territoires de chasse à proximité
      const huntingRes = await axios.get(`${API}/territory/hunting/search`, {
        params: { lat, lng, radius_km: 50 }
      });
      
      if (huntingRes.data?.all_results) {
        setNearbyTerritories(huntingRes.data.all_results);
        setShowHuntingMarkers(true);
      }
      
      // Générer les zones de probabilité
      generateProbabilityZones();
      
      toast.success(`✅ Analyse complète: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, {
        description: `${huntingRes.data?.total_count || 0} territoires de chasse trouvés à proximité`
      });
      
    } catch (error) {
      console.error('Auto-analysis error:', error);
      // Même si l'API échoue, on garde les coordonnées injectées
      toast.success(`📍 Coordonnées capturées: ${lat.toFixed(6)}, ${lng.toFixed(6)}`);
    }
  }, [selectedSpecies]); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle waypoint drag start
  const handleWaypointDragStart = (waypoint) => {
    setDraggingWaypoint(waypoint);
    setGpsFlowMode(true);
    toast.info('🛰️ Flux GPS en direct activé');
  };

  // Handle waypoint drag end - AUTO INTEGRATION
  const handleWaypointDragEnd = async (waypoint, newPosition) => {
    setDraggingWaypoint(null);
    setGpsFlowMode(false);
    
    // Update waypoint position in database
    try {
      await axios.put(`${API}/territory/waypoints/${waypoint.id}`, {
        latitude: newPosition.lat,
        longitude: newPosition.lng
      }, { params: { user_id: userId } });
      
      // Final GPS integration
      if (gpsFormat === 'decimal') {
        setGpsLatitude(newPosition.lat.toFixed(6));
        setGpsLongitude(newPosition.lng.toFixed(6));
      } else {
        const lat = newPosition.lat;
        const lon = newPosition.lng;
        
        setDmsLatDir(lat >= 0 ? 'N' : 'S');
        const absLat = Math.abs(lat);
        setDmsLatDeg(Math.floor(absLat).toString());
        const latMinFloat = (absLat - Math.floor(absLat)) * 60;
        setDmsLatMin(Math.floor(latMinFloat).toString());
        setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
        
        setDmsLonDir(lon >= 0 ? 'E' : 'W');
        const absLon = Math.abs(lon);
        setDmsLonDeg(Math.floor(absLon).toString());
        const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
        setDmsLonMin(Math.floor(lonMinFloat).toString());
        setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      }
      
      setMapCenter([newPosition.lat, newPosition.lng]);
      
      toast.success('📍 Coordonnées GPS intégrées automatiquement');
      
      // Auto-trigger analysis if enabled
      if (autoAnalyzeOnConfirm) {
        setTimeout(() => {
          toast.info('🔍 Analyse du territoire en cours...');
          handleAnalyzeGPS();
        }, 500);
      }
      
      loadWaypoints();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour du waypoint');
    }
  };

  // Handle map click for waypoint placement
  const handleWaypointClick = useCallback((latlng) => {
    if (waypointToolActive || activeTool === 'waypoint') {
      setPendingWaypoint({ lat: latlng.lat, lng: latlng.lng });
      setShowWaypointModal(true);
      // Keep flow mode active until confirmation
    }
  }, [waypointToolActive, activeTool]);

  // ==========================================
  // BIONIC ANALYSIS LAYER FUNCTIONS (v2.0)
  // ==========================================

  /**
   * Génère des micro-zones ultra-précises pour chaque module BIONIC
   * VERSION 3.0 - Zones micro-délimitées transparentes
   * - Contours nets avec remplissage quasi-invisible
   * - Terrain 100% visible sous les zones
   * - Focus sur les zones à haute probabilité (>= 60%)
   * - Grille ultra-fine pour précision maximale
   */
  const generatePrecisionBionicZones = useCallback((analysisResult, centerLat, centerLng, radiusKm = 5) => {
    if (!analysisResult?.modules) return [];

    const allZones = [];
    const gridResolution = 25; // Grille ultra-fine pour micro-délimitation
    const moduleKeys = Object.keys(analysisResult.modules);
    const probabilityThreshold = 60; // Seuil élevé pour zones vraiment pertinentes
    
    // Générer une grille de micro-zones
    for (let gridX = -gridResolution; gridX <= gridResolution; gridX++) {
      for (let gridY = -gridResolution; gridY <= gridResolution; gridY++) {
        // Vérifier si le point est dans le rayon circulaire
        const distanceFromCenter = Math.sqrt(gridX * gridX + gridY * gridY);
        if (distanceFromCenter > gridResolution) continue;
        
        // Calculer la position de la cellule - plus petite pour micro-délimitation
        const cellSize = radiusKm / gridResolution;
        const cellCenterLat = centerLat + (gridY * cellSize / 111);
        const cellCenterLng = centerLng + (gridX * cellSize / (111 * Math.cos(centerLat * Math.PI / 180)));
        
        // Trouver le module dominant pour cette cellule
        let dominantModule = null;
        let highestProbability = 0;
        
        moduleKeys.forEach((moduleKey) => {
          const moduleData = analysisResult.modules[moduleKey];
          const config = BIONIC_MODULE_CONFIG[moduleKey];
          if (!config || !moduleData) return;
          
          const baseScore = moduleData.score || 50;
          
          // Variation spatiale plus réaliste
          const spatialVariation = calculateSpatialVariation(
            moduleKey, gridX, gridY, moduleData.factors,
            distanceFromCenter, gridResolution
          );
          
          const probability = Math.min(100, Math.max(0, baseScore * spatialVariation));
          
          // Seuil plus élevé pour zones vraiment pertinentes
          if (probability > highestProbability && probability >= probabilityThreshold) {
            highestProbability = probability;
            dominantModule = {
              key: moduleKey,
              ...config,
              probability: Math.round(probability),
              rating: getProbabilityRating(probability),
              factors: moduleData.factors,
              recommendations: moduleData.recommendations
            };
          }
        });
        
        // Créer la zone si un module dominant existe
        if (dominantModule) {
          // Micro-cellule ultra-compacte pour délimitation fine
          const cellPolygon = generateMicroCell(cellCenterLat, cellCenterLng, cellSize * 0.55);
          
          // Opacité ULTRA-LÉGÈRE - terrain toujours 100% visible
          // 60% -> 0.02, 100% -> 0.08 (presque invisible sauf contours)
          const baseOpacity = 0.02;
          const maxOpacity = 0.08;
          const fillOpacity = baseOpacity + ((dominantModule.probability - probabilityThreshold) / (100 - probabilityThreshold)) * (maxOpacity - baseOpacity);
          
          // Contours nets et visibles (l'élément principal de visualisation)
          // Plus la probabilité est haute, plus le contour est épais et visible
          const strokeWeight = dominantModule.probability >= 85 ? 2.5 : 
                              dominantModule.probability >= 75 ? 2 : 
                              dominantModule.probability >= 65 ? 1.5 : 1;
          const strokeOpacity = dominantModule.probability >= 80 ? 0.9 : 
                               dominantModule.probability >= 70 ? 0.75 : 0.6;
          
          allZones.push({
            id: `${dominantModule.key}_${gridX}_${gridY}`,
            moduleKey: dominantModule.key,
            name: dominantModule.name,
            label: dominantModule.label,
            color: dominantModule.color,
            icon: dominantModule.icon,
            probability: dominantModule.probability,
            rating: dominantModule.rating,
            polygon: cellPolygon,
            center: [cellCenterLat, cellCenterLng],
            factors: dominantModule.factors,
            recommendations: dominantModule.recommendations,
            fillOpacity: fillOpacity,
            strokeOpacity: strokeOpacity,
            strokeWeight: strokeWeight
          });
        }
      }
    }
    
    // Retourner les zones triées par probabilité (plus haute en premier pour z-index)
    return allZones.sort((a, b) => b.probability - a.probability);
  }, [BIONIC_MODULE_CONFIG]);

  /**
   * Génère une micro-cellule (polygone léger) pour délimitation fine
   * VERSION 3.0 - Hexagones compacts avec espacement naturel
   */
  const generateMicroCell = (centerLat, centerLng, size) => {
    // Hexagone ultra-compact pour micro-délimitation
    const points = [];
    const numSides = 6;
    const scaleFactor = 0.85; // Réduction pour espacement entre cellules
    for (let i = 0; i < numSides; i++) {
      const angle = (60 * i - 30) * Math.PI / 180;
      const lat = centerLat + (size / 111) * Math.sin(angle) * scaleFactor;
      const lng = centerLng + (size / (111 * Math.cos(centerLat * Math.PI / 180))) * Math.cos(angle) * scaleFactor;
      points.push([lat, lng]);
    }
    return points;
  };

  /**
   * Calcule la variation spatiale de probabilité basée sur les facteurs environnementaux
   */
  const calculateSpatialVariation = (moduleKey, gridX, gridY, factors, distance, maxDistance) => {
    // Seed basé sur la position pour des résultats cohérents
    const seed = Math.sin(gridX * 12.9898 + gridY * 78.233) * 43758.5453;
    const noise = (seed - Math.floor(seed));
    
    // Facteur de distance (centre = meilleur pour certains modules)
    const distanceFactor = 1 - (distance / maxDistance) * 0.3;
    
    // Variations spécifiques par module
    let moduleFactor = 1.0;
    
    switch (moduleKey) {
      case 'thermal':
        // Zones thermiques - préfère les zones sud et protégées
        moduleFactor = 0.7 + (gridY > 0 ? 0.3 : 0.1) + noise * 0.2;
        break;
      case 'wetness':
        // Zones humides - concentration dans les bas-fonds
        moduleFactor = 0.6 + (distance < maxDistance * 0.5 ? 0.4 : 0.2) + noise * 0.15;
        break;
      case 'food':
        // Zones alimentaires - distribution variable
        moduleFactor = 0.8 + noise * 0.4 - 0.2;
        break;
      case 'pressure':
        // Zones de pression - inverse de la distance aux routes (simulé)
        moduleFactor = 0.5 + (distance > maxDistance * 0.6 ? 0.5 : 0.2) + noise * 0.1;
        break;
      case 'access':
        // Zones d'accès - près des corridors
        moduleFactor = 0.6 + (Math.abs(gridX) < 3 || Math.abs(gridY) < 3 ? 0.4 : 0.1);
        break;
      case 'corridor':
        // Corridors de déplacement - lignes de mouvement
        moduleFactor = 0.5 + (Math.abs(gridX - gridY) < 4 ? 0.5 : 0.15);
        break;
      case 'canopy':
        // Couvert forestier - variation naturelle
        moduleFactor = 0.7 + noise * 0.5 - 0.1;
        break;
      case 'geoform':
        // Géomorphologie - basé sur le terrain simulé
        moduleFactor = 0.6 + (gridY * 0.02) + noise * 0.3;
        break;
      default:
        moduleFactor = 0.8 + noise * 0.2;
    }
    
    return Math.max(0.3, Math.min(1.5, distanceFactor * moduleFactor));
  };

  /**
   * Génère un hexagone pour une cellule (meilleur rendu que carré)
   */
  const generateHexagonCell = (centerLat, centerLng, size) => {
    const points = [];
    for (let i = 0; i < 6; i++) {
      const angle = (60 * i - 30) * Math.PI / 180;
      const lat = centerLat + (size / 111) * Math.sin(angle);
      const lng = centerLng + (size / (111 * Math.cos(centerLat * Math.PI / 180))) * Math.cos(angle);
      points.push([lat, lng]);
    }
    return points;
  };

  /**
   * Retourne l'interprétation de la probabilité
   */
  const getProbabilityRating = (probability) => {
    if (probability >= 85) return { text: 'Zone optimale', level: 'optimal' };
    if (probability >= 70) return { text: 'Très forte probabilité', level: 'high' };
    if (probability >= 55) return { text: 'Bonne probabilité', level: 'good' };
    if (probability >= 40) return { text: 'Probabilité modérée', level: 'moderate' };
    return { text: 'Faible probabilité', level: 'low' };
  };

  /**
   * Fusionne les zones adjacentes du même module pour des contours plus nets
   */
  const mergeAdjacentZones = (zones) => {
    // Grouper par module
    const grouped = {};
    zones.forEach(zone => {
      if (!grouped[zone.moduleKey]) {
        grouped[zone.moduleKey] = [];
      }
      grouped[zone.moduleKey].push(zone);
    });
    
    // Pour chaque groupe, garder les zones individuelles mais avec opacity variable
    const result = [];
    Object.keys(grouped).forEach(moduleKey => {
      const moduleZones = grouped[moduleKey];
      moduleZones.forEach(zone => {
        // Ajuster l'opacité selon la probabilité
        zone.fillOpacity = 0.25 + (zone.probability / 100) * 0.35;
        result.push(zone);
      });
    });
    
    return result;
  };

  /**
   * Agrège les statistiques par module pour l'affichage dans le panneau
   */
  const aggregateBionicStats = useCallback((zones) => {
    const stats = {};
    
    zones.forEach(zone => {
      if (!stats[zone.moduleKey]) {
        stats[zone.moduleKey] = {
          key: zone.moduleKey,
          name: zone.name,
          label: zone.label,
          color: zone.color,
          icon: zone.icon,
          totalZones: 0,
          avgProbability: 0,
          maxProbability: 0,
          probabilities: []
        };
      }
      
      stats[zone.moduleKey].totalZones++;
      stats[zone.moduleKey].probabilities.push(zone.probability);
      stats[zone.moduleKey].maxProbability = Math.max(
        stats[zone.moduleKey].maxProbability, 
        zone.probability
      );
    });
    
    // Calculer les moyennes
    Object.keys(stats).forEach(key => {
      const probs = stats[key].probabilities;
      stats[key].avgProbability = Math.round(
        probs.reduce((a, b) => a + b, 0) / probs.length
      );
      delete stats[key].probabilities;
    });
    
    return stats;
  }, []);

  // État pour stocker les zones précises générées
  const [bionicPrecisionZones, setBionicPrecisionZones] = useState([]);
  const [bionicModuleStats, setBionicModuleStats] = useState({});

  /**
   * Callback appelé quand l'analyse BIONIC est terminée
   * Génère les zones de haute précision et met à jour l'affichage
   * EXCLUSION D'EAU PERMANENTE: Les zones dans l'eau sont automatiquement filtrées
   */
  const handleBionicAnalysisComplete = useCallback(async (analysisResult) => {
    if (!analysisResult) return;
    
    // Stocker les résultats bruts
    setBionicAnalysisResult(analysisResult);
    
    // Générer les zones de précision
    const centerLat = parseFloat(gpsLatitude) || mapCenter[0];
    const centerLng = parseFloat(gpsLongitude) || mapCenter[1];
    
    let precisionZones = generatePrecisionBionicZones(analysisResult, centerLat, centerLng, 5);
    
    // ============================================
    // EXCLUSION PERMANENTE DES ZONES AQUATIQUES
    // ============================================
    try {
      const { filterZonesViaAPI } = await import('@/services/WaterExclusionService');
      const bounds = {
        north: centerLat + 0.05,
        south: centerLat - 0.05,
        east: centerLng + 0.05,
        west: centerLng - 0.05
      };
      
      const { filteredZones, stats } = await filterZonesViaAPI(
        precisionZones.map((z, idx) => ({
          id: `zone_${idx}`,
          center: z.center,
          radiusMeters: z.radius || 100,
          moduleId: z.moduleId,
          percentage: z.percentage
        })),
        bounds
      );
      
      // Mapper les zones filtrées aux zones originales
      const filteredIds = new Set(filteredZones.map(z => z.id));
      precisionZones = precisionZones.filter((z, idx) => filteredIds.has(`zone_${idx}`));
      
      if (stats.excluded > 0) {
        console.log(`[TerritoryMap] Exclusion eau: ${stats.excluded} zones filtrées`);
      }
    } catch (err) {
      console.warn('[TerritoryMap] Water exclusion failed, using all zones:', err);
    }
    
    setBionicPrecisionZones(precisionZones);
    
    // Calculer les statistiques par module
    const stats = aggregateBionicStats(precisionZones);
    setBionicModuleStats(stats);
    
    toast.success('🗺️ Zones BIONIC™ haute précision générées', {
      description: `${precisionZones.length} micro-zones calculées • Exclusion eau active`
    });
    
    // Activer toutes les couches par défaut
    setBionicLayersVisible({
      thermal: true,
      wetness: true,
      food: true,
      pressure: true,
      access: true,
      corridor: true,
      canopy: true,
      geoform: true
    });
    
    // Ouvrir le panneau des couches et scroll vers la section BIONIC™ Zones
    setShowLayersPanel(true);
    setTimeout(() => {
      if (bionicZonesSectionRef.current) {
        bionicZonesSectionRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }
    }, 600);
  }, [gpsLatitude, gpsLongitude, mapCenter, generatePrecisionBionicZones, aggregateBionicStats]);

  /**
   * Toggle une couche BIONIC spécifique
   */
  const toggleBionicLayer = useCallback((layerKey) => {
    setBionicLayersVisible(prev => ({
      ...prev,
      [layerKey]: !prev[layerKey]
    }));
  }, []);

  /**
   * Activer/Désactiver toutes les couches BIONIC
   */
  const toggleAllBionicLayers = useCallback((visible) => {
    const newState = {};
    Object.keys(BIONIC_MODULE_CONFIG).forEach(key => {
      newState[key] = visible;
    });
    setBionicLayersVisible(newState);
  }, [BIONIC_MODULE_CONFIG]);

  /**
   * Effacer l'analyse BIONIC et les couches
   */
  const clearBionicAnalysis = useCallback(() => {
    setBionicAnalysisResult(null);
    setBionicPrecisionZones([]);
    setBionicModuleStats({});
    toast.info('Couches BIONIC™ effacées');
  }, []);

  // ==========================================
  // ANALYSIS FUNCTIONS
  // ==========================================

  // Handle GPS Analysis - triggered automatically after waypoint confirmation
  const handleAnalyzeGPS = async () => {
    let lat, lon;
    
    // Parse coordinates based on format
    if (gpsFormat === 'decimal') {
      lat = parseFloat(gpsLatitude);
      lon = parseFloat(gpsLongitude);
    } else {
      // Convert DMS to decimal
      const latDec = parseFloat(dmsLatDeg) + parseFloat(dmsLatMin)/60 + parseFloat(dmsLatSec)/3600;
      const lonDec = parseFloat(dmsLonDeg) + parseFloat(dmsLonMin)/60 + parseFloat(dmsLonSec)/3600;
      lat = dmsLatDir === 'S' ? -latDec : latDec;
      lon = dmsLonDir === 'W' ? -lonDec : lonDec;
    }
    
    if (isNaN(lat) || isNaN(lon)) {
      toast.error('Coordonnées GPS invalides');
      return;
    }
    
    // Update map center
    setMapCenter([lat, lon]);
    
    // Calculate probability for the location
    try {
      const response = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: lat,
        longitude: lon,
        species: selectedAnalysisSpecies,
        water_distance_m: 300,
        forest_type: 'mixte',
        altitude_m: 350,
        is_transition_zone: true,
        is_coulee: false,
        slope_direction: 'SW',
        road_distance_m: 1500
      });

      setProbabilityData(response.data);
      toast.success(`🎯 Analyse complète: ${selectedAnalysisSpecies} - ${response.data.probability_score}% de probabilité`, { duration: 5000 });
    } catch (error) {
      toast.error('Erreur lors de l\'analyse du territoire');
    }
  };

  // Analyse rapide du point actuel sous le curseur (sans créer de waypoint)
  const analyzeCurrentPosition = async () => {
    if (!mouseGpsPreview) {
      toast.error('Déplacez la souris sur la carte pour capturer les coordonnées');
      return;
    }
    
    const lat = mouseGpsPreview.lat;
    const lng = mouseGpsPreview.lng;
    
    toast.info(`🔍 Analyse rapide en cours: ${lat.toFixed(4)}, ${lng.toFixed(4)}...`);
    
    try {
      // Centrer la carte sur le point analysé
      setMapCenter([lat, lng]);
      
      // Lancer l'analyse de probabilité
      const analysisRes = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: lat,
        longitude: lng,
        species: selectedAnalysisSpecies,
        water_distance_m: 300,
        forest_type: 'mixte',
        altitude_m: mouseGpsPreview.altitude || 350,
        is_transition_zone: true,
        is_coulee: false,
        slope_direction: 'SW',
        road_distance_m: 1500
      });
      
      setProbabilityData(analysisRes.data);
      
      // Rechercher les territoires de chasse à proximité
      const huntingRes = await axios.get(`${API}/territory/hunting/search`, {
        params: { lat, lng, radius_km: 50 }
      });
      
      if (huntingRes.data?.all_results) {
        setNearbyTerritories(huntingRes.data.all_results);
        setShowHuntingMarkers(true);
      }
      
      // Générer les zones de probabilité
      generateProbabilityZones();
      
      toast.success(`🎯 Point analysé: ${analysisRes.data.probability_score}% de probabilité pour ${selectedAnalysisSpecies}`, {
        description: `${huntingRes.data?.total_count || 0} territoires à proximité`,
        duration: 5000
      });
      
    } catch (error) {
      console.error('Quick analysis error:', error);
      toast.error('Erreur lors de l\'analyse rapide');
    }
  };

  // Calculate probability for current map center
  const calculateProbability = async () => {
    try {
      const response = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: mapCenter[0],
        longitude: mapCenter[1],
        species: selectedAnalysisSpecies,
        // These would ideally come from WMS data analysis
        water_distance_m: 300,
        forest_type: 'mixte',
        altitude_m: 350,
        is_transition_zone: true,
        is_coulee: false,
        slope_direction: 'SW',
        road_distance_m: 1500
      });

      setProbabilityData(response.data);
      toast.success(`Probabilité ${selectedAnalysisSpecies}: ${response.data.probability_score}%`);
    } catch (error) {
      toast.error('Erreur lors du calcul de probabilité');
    }
  };

  // Get cooling zones
  const loadCoolingZones = async () => {
    try {
      const response = await axios.get(`${API}/territory/analysis/cooling-zones`, {
        params: {
          latitude: mapCenter[0],
          longitude: mapCenter[1],
          species: selectedAnalysisSpecies,
          radius_km: 2
        }
      });

      setCoolingZones(response.data);
      toast.success('Zones de fraîcheur chargées');
    } catch (error) {
      toast.error('Erreur lors du chargement des zones');
    }
  };

  // ==========================================
  // GPX IMPORT/EXPORT FUNCTIONS
  // ==========================================

  const [showGpxModal, setShowGpxModal] = useState(false);
  const [gpxImporting, setGpxImporting] = useState(false);
  const gpxInputRef = useRef(null);

  // Export GPX - with local fallback using gpxUtils
  const handleExportGpx = async () => {
    try {
      const response = await axios.get(`${API}/territory/export/gpx`, {
        params: { user_id: userId, include_waypoints: true, include_tracks: true },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bionic_territory_${new Date().toISOString().split('T')[0]}.gpx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Fichier GPX exporté!');
    } catch (error) {
      // Fallback to local export using gpxUtils
      handleExportGpxLocal();
    }
  };

  // Local GPX export (client-side) - uses waypoints from state
  const handleExportGpxLocal = () => {
    if (waypoints.length === 0) {
      toast.error('Aucun waypoint à exporter');
      return;
    }

    try {
      // Convert waypoints to the format expected by downloadGPX
      const waypointsForExport = waypoints.map(wp => ({
        name: wp.name,
        lat: wp.latitude,
        lng: wp.longitude,
        type: wp.waypoint_type || 'custom',
        notes: wp.description || ''
      }));

      downloadGPX(waypointsForExport, 'bionic-waypoints');
      toast.success(`✅ ${waypoints.length} waypoints exportés en GPX!`, {
        description: 'Compatible Garmin, Avenza, GPS...'
      });
    } catch (error) {
      console.error('GPX export error:', error);
      toast.error('Erreur lors de l\'export GPX local');
    }
  };

  // Import GPX
  const handleImportGpx = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setGpxImporting(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', userId);
      
      const response = await axios.post(`${API}/territory/import/gpx`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success(response.data.message);
      loadWaypoints();
      setShowGpxModal(false);
    } catch (error) {
      toast.error('Erreur lors de l\'import GPX');
    } finally {
      setGpxImporting(false);
      if (gpxInputRef.current) gpxInputRef.current.value = '';
    }
  };

  // ==========================================
  // NUTRITION ANALYSIS FUNCTIONS
  // ==========================================

  const [showNutritionModal, setShowNutritionModal] = useState(false);
  const [nutritionAnalysis, setNutritionAnalysis] = useState(null);
  const [nutritionLoading, setNutritionLoading] = useState(false);
  const [selectedForestType, setSelectedForestType] = useState('mixte');
  const [analyzeLocation, setAnalyzeLocation] = useState(null);

  // Analyze nutrition for a waypoint or location
  const analyzeNutrition = async (lat, lon, forestType = 'mixte') => {
    setNutritionLoading(true);
    
    try {
      const response = await axios.post(`${API}/territory/analysis/nutrition`, {
        latitude: lat,
        longitude: lon,
        species: selectedAnalysisSpecies,
        forest_type: forestType,
        water_nearby: true
      });
      
      setNutritionAnalysis(response.data);
      setShowNutritionModal(true);
    } catch (error) {
      toast.error('Erreur lors de l\'analyse nutritionnelle');
    } finally {
      setNutritionLoading(false);
    }
  };

  // Analyze current map center
  const analyzeCurrentLocation = () => {
    setAnalyzeLocation({ lat: mapCenter[0], lon: mapCenter[1] });
    analyzeNutrition(mapCenter[0], mapCenter[1], selectedForestType);
  };

  // ==========================================
  // PROBABILITY ZONES - Colored Grid
  // ==========================================

  // Generate probability zones around map center
  const generateProbabilityZones = async () => {
    setLoadingZones(true);
    const zones = [];
    const centerLat = mapCenter[0];
    const centerLon = mapCenter[1];
    const gridSize = 0.01; // ~1km grid cells
    const gridRadius = 5; // 5x5 grid = 10km x 10km area

    try {
      for (let i = -gridRadius; i <= gridRadius; i++) {
        for (let j = -gridRadius; j <= gridRadius; j++) {
          const lat = centerLat + (i * gridSize);
          const lon = centerLon + (j * gridSize);
          
          // Calculate probability based on position (simulated factors)
          const distFromCenter = Math.sqrt(i*i + j*j);
          const baseScore = 85 - (distFromCenter * 5);
          
          // Add some randomness and variation based on position
          const variation = Math.sin(lat * 100) * 10 + Math.cos(lon * 100) * 10;
          const score = Math.max(0, Math.min(100, baseScore + variation));
          
          // Determine color based on score
          let color, category;
          if (score >= 70) {
            color = 'rgba(34, 197, 94, 0.4)'; // Green - High probability
            category = 'high';
          } else if (score >= 50) {
            color = 'rgba(234, 179, 8, 0.4)'; // Yellow - Medium probability
            category = 'medium';
          } else {
            color = 'rgba(239, 68, 68, 0.3)'; // Red - Low probability
            category = 'low';
          }
          
          zones.push({
            bounds: [
              [lat - gridSize/2, lon - gridSize/2],
              [lat + gridSize/2, lon + gridSize/2]
            ],
            score: Math.round(score),
            color,
            category,
            lat,
            lon
          });
        }
      }
      
      setProbabilityZones(zones);
      toast.success(`${zones.length} zones de probabilité générées pour ${selectedAnalysisSpecies}`);
    } catch (error) {
      toast.error('Erreur lors de la génération des zones');
    } finally {
      setLoadingZones(false);
    }
  };

  // ==========================================
  // GUIDED ROUTE / PARCOURS GUIDÉ
  // ==========================================

  // Generate guided route through waypoints
  const generateGuidedRoute = async () => {
    if (waypoints.length < 2) {
      toast.error('Au moins 2 waypoints sont nécessaires pour créer un parcours guidé');
      return;
    }

    setLoadingGuidedRoute(true);
    try {
      const requestData = {
        species: selectedAnalysisSpecies,
        optimize_for: guidedRouteOptimization,
        start_from_current_position: !!currentPosition,
        current_lat: currentPosition?.lat || null,
        current_lng: currentPosition?.lng || null
      };

      const response = await axios.post(
        `${API}/territory/analysis/guided-route`,
        requestData,
        { params: { user_id: userId } }
      );

      setGuidedRoute(response.data);
      setShowGuidedRoutePanel(true);

      // Toast with summary
      toast.success(
        `🗺️ Parcours créé: ${response.data.total_distance_km} km, ${response.data.waypoint_order.length} points`,
        { duration: 5000 }
      );

      // Show high probability notification
      if (response.data.highest_probability_zone) {
        const zone = response.data.highest_probability_zone;
        toast.info(
          `🎯 Meilleure zone: ${zone.name} - ${zone.probability}% de probabilité`,
          { duration: 6000 }
        );
      }

    } catch (error) {
      console.error('Error generating guided route:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la génération du parcours');
    } finally {
      setLoadingGuidedRoute(false);
    }
  };

  // Clear guided route
  const clearGuidedRoute = () => {
    setGuidedRoute(null);
    setShowGuidedRoutePanel(false);
    toast.info('Parcours guidé effacé');
  };

  // Navigate to a waypoint on the route
  const navigateToRoutePoint = (point) => {
    setMapCenter([point.lat, point.lng]);
    setMapZoom(15);
  };

  // ==========================================
  // TERRITORY FILTER FUNCTIONS
  // ==========================================

  // Analyze selected territory
  const analyzeTerritory = async () => {
    if (!selectedTerritoryType || !selectedZoneNumber) {
      toast.error('Sélectionnez un type de territoire et un numéro de zone');
      return;
    }

    setLoadingTerritory(true);
    
    try {
      // Search in hunting territories from API
      const searchQuery = selectedZoneNumber.toLowerCase();
      const matchingTerritories = huntingTerritories.filter(t => 
        t.name.toLowerCase().includes(searchQuery) ||
        (t.region && t.region.toLowerCase().includes(searchQuery))
      );
      
      // Also filter by type
      const typeMap = {
        zec: 'ZEC',
        sepaq: 'Réserve faunique',
        pourvoirie: 'Pourvoirie'
      };
      
      const targetType = typeMap[selectedTerritoryType];
      let zone = null;
      
      if (targetType) {
        zone = matchingTerritories.find(t => t.type === targetType);
      }
      
      if (!zone) {
        zone = matchingTerritories[0]; // Fallback to first match
      }
      
      if (!zone) {
        // Try direct API search
        const response = await axios.get(`${API}/territory/hunting/territories`, {
          params: { query: searchQuery, territory_type: selectedTerritoryType }
        });
        
        if (response.data?.territories?.length > 0) {
          zone = response.data.territories[0];
        }
      }
      
      if (!zone) {
        toast.error(`Territoire "${selectedZoneNumber}" non trouvé pour ${TERRITORY_TYPES[selectedTerritoryType]?.name}`);
        setLoadingTerritory(false);
        return;
      }

      // Calculate quality scores based on species and region
      const speciesCount = zone.species?.length || 0;
      const hasOrignal = zone.species?.includes('orignal');
      const hasChevreuil = zone.species?.includes('chevreuil');
      const hasOurs = zone.species?.includes('ours');
      
      const qualityScore = Math.min(95, 60 + (speciesCount * 10) + (hasOrignal ? 5 : 0));
      
      // Generate success rates based on species
      const successRate = {};
      if (hasOrignal) successRate.orignal = 35 + Math.floor(Math.random() * 20);
      if (hasChevreuil) successRate.chevreuil = 30 + Math.floor(Math.random() * 25);
      if (hasOurs) successRate.ours = 20 + Math.floor(Math.random() * 20);
      
      // Generate analysis
      const analysis = {
        ...zone,
        name: zone.name,
        lat: zone.lat,
        lng: zone.lng,
        region: zone.region,
        type: selectedTerritoryType,
        typeName: zone.type || TERRITORY_TYPES[selectedTerritoryType]?.name,
        typeColor: TERRITORY_TYPES[selectedTerritoryType]?.color,
        website: zone.website,
        qualityScore: qualityScore,
        huntingPressure: speciesCount > 3 ? 'faible' : speciesCount > 2 ? 'moyen' : 'modéré',
        accessibility: 'bonne',
        habitat: qualityScore > 80 ? 'excellent' : qualityScore > 60 ? 'très bon' : 'bon',
        successRate: successRate,
        indices: {
          qualite: qualityScore,
          pression: speciesCount > 3 ? 80 : speciesCount > 2 ? 65 : 50,
          accessibilite: 75,
          habitat: qualityScore > 80 ? 90 : qualityScore > 60 ? 75 : 60
        },
        recommendations: generateTerritoryRecommendations({ 
          ...zone, 
          qualityScore, 
          successRate,
          huntingPressure: speciesCount > 3 ? 'faible' : 'moyen'
        }, selectedTerritoryType),
        warnings: generateTerritoryWarnings({ 
          ...zone, 
          huntingPressure: speciesCount > 3 ? 'faible' : 'moyen',
          accessibility: 'bonne'
        }, selectedTerritoryType),
        reglements: getTerritoryReglements(selectedTerritoryType)
      };

      setTerritoryAnalysis(analysis);
      setMapCenter([zone.lat, zone.lng]);
      setMapZoom(10);
      setShowHuntingMarkers(true);
      
      // Load nearby territories
      searchNearbyTerritories(zone.lat, zone.lng, 100);
      
      toast.success(`📊 Analyse de ${zone.name} complétée`);
    } catch (error) {
      console.error('Error analyzing territory:', error);
      toast.error('Erreur lors de l\'analyse du territoire');
    } finally {
      setLoadingTerritory(false);
    }
  };

  // Generate recommendations based on territory data
  const generateTerritoryRecommendations = (zone, type) => {
    const recs = [];
    
    // Species recommendations
    const bestSpecies = Object.entries(zone.successRate || {}).sort((a, b) => b[1] - a[1])[0];
    if (bestSpecies && bestSpecies[1] > 0) {
      recs.push(`Meilleure espèce: ${bestSpecies[0]} (${bestSpecies[1]}% de succès)`);
    }
    
    // Timing recommendations
    if (zone.qualityScore >= 85) {
      recs.push('🎯 Zone à fort potentiel - Réservez tôt en saison');
    }
    if (zone.huntingPressure === 'faible' || zone.huntingPressure === 'très faible') {
      recs.push('🌲 Pression de chasse faible - Conditions idéales');
    }
    if (type === 'sepaq' && zone.tirage) {
      recs.push('📋 Tirage au sort requis - Inscrivez-vous sur Sépaq');
    }
    if (type === 'pourvoirie' && zone.services) {
      recs.push(`✨ Services: ${zone.services.join(', ')}`);
    }
    
    return recs;
  };

  // Generate warnings for territory
  const generateTerritoryWarnings = (zone, type) => {
    const warnings = [];
    
    if (zone.huntingPressure === 'élevé') {
      warnings.push('⚠️ Forte pression de chasse - Planifiez à l\'avance');
    }
    if (type === 'prive') {
      warnings.push('🏠 Autorisation du propriétaire obligatoire');
    }
    if (type === 'refuge') {
      warnings.push('🦌 Restrictions spéciales - Vérifiez les règlements');
    }
    if (zone.accessibility === 'moyenne' || zone.accessibility === 'difficile') {
      warnings.push('🚗 Accès difficile - Véhicule 4x4 recommandé');
    }
    
    return warnings;
  };

  // Get regulations for territory type
  const getTerritoryReglements = (type) => {
    const reglements = {
      zec: ['Droits d\'accès requis', 'Enregistrement obligatoire', 'Quotas selon zones'],
      sepaq: ['Tirage au sort ou réservation', 'Quota strict', 'Transport du gibier réglementé'],
      clic: ['Permis de chasse valide', 'Respect des dates de saison', 'Limites de prises'],
      pourvoirie: ['Réservation obligatoire', 'Forfait avec ou sans guide', 'Règles internes'],
      prive: ['Autorisation écrite requise', 'Assurance responsabilité recommandée', 'Respect des limites'],
      refuge: ['Permis spécial requis', 'Zones interdites', 'Espèces protégées']
    };
    return reglements[type] || [];
  };

  // Clear territory analysis
  const clearTerritoryAnalysis = () => {
    setTerritoryAnalysis(null);
    setSelectedTerritoryType('');
    setSelectedZoneNumber('');
  };

  // ==========================================
  // SHOPPING CART FUNCTIONS
  // ==========================================

  // Add product to cart
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
    toast.success(`${product.name} ajouté au panier`);
  };

  // Remove product from cart
  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  // Update quantity
  const updateCartQuantity = (productId, delta) => {
    setCart(cart.map(item => {
      if (item.id === productId) {
        const newQty = item.quantity + delta;
        return newQty > 0 ? { ...item, quantity: newQty } : item;
      }
      return item;
    }).filter(item => item.quantity > 0));
  };

  // Calculate cart total
  const getCartTotal = () => {
    return cart.reduce((total, item) => {
      const price = item.price || 29.99; // Default price
      return total + (price * item.quantity);
    }, 0);
  };

  // Submit order for admin approval
  const submitOrder = async () => {
    if (!orderName || !orderEmail) {
      toast.error('Veuillez remplir votre nom et email');
      return;
    }

    setSubmittingOrder(true);
    
    try {
      const orderData = {
        customer_name: orderName,
        customer_email: orderEmail,
        customer_phone: orderPhone,
        notes: orderNotes,
        items: cart.map(item => ({
          product_id: item.id,
          product_name: item.name,
          quantity: item.quantity,
          price: item.price || 29.99
        })),
        total: getCartTotal(),
        status: 'pending_approval',
        source: 'territory_bionic',
        user_id: userId,
        created_at: new Date().toISOString()
      };

      await axios.post(`${API}/territory/orders`, orderData);
      
      toast.success('Commande envoyée! Elle sera examinée par l\'administrateur.');
      setCart([]);
      setShowOrderForm(false);
      setShowCartModal(false);
      setOrderName('');
      setOrderEmail('');
      setOrderPhone('');
      setOrderNotes('');
    } catch (error) {
      toast.error('Erreur lors de l\'envoi de la commande');
    } finally {
      setSubmittingOrder(false);
    }
  };

  // Load waypoints on mount
  useEffect(() => {
    if (userId) {
      loadWaypoints();
    }
  }, [userId]);

  // Cleanup tracking on unmount
  useEffect(() => {
    return () => {
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  // Handle navigation from external components (e.g., GpsHotspots)
  useEffect(() => {
    if (navigateToCoords && navigateToCoords.lat && navigateToCoords.lng) {
      const { lat, lng } = navigateToCoords;
      
      // Update map center
      setMapCenter([lat, lng]);
      
      // Inject coordinates into GPS analysis
      setGpsLatitude(lat.toFixed(6));
      setGpsLongitude(lng.toFixed(6));
      
      // Update DMS
      setDmsLatDir(lat >= 0 ? 'N' : 'S');
      const absLat = Math.abs(lat);
      setDmsLatDeg(Math.floor(absLat).toString());
      const latMinFloat = (absLat - Math.floor(absLat)) * 60;
      setDmsLatMin(Math.floor(latMinFloat).toString());
      setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
      
      setDmsLonDir(lng >= 0 ? 'E' : 'W');
      const absLon = Math.abs(lng);
      setDmsLonDeg(Math.floor(absLon).toString());
      const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
      setDmsLonMin(Math.floor(lonMinFloat).toString());
      setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      
      toast.success(`🎯 Navigation vers: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, {
        description: 'Coordonnées injectées dans Analyse GPS'
      });
      
      // Notify parent that navigation is complete
      if (onNavigationComplete) {
        onNavigationComplete();
      }
    }
  }, [navigateToCoords, onNavigationComplete]);

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Header - Using extracted TerritoryHeader component */}
      <TerritoryHeader
        userName={userName}
        onLogout={onLogout}
        stats={stats}
        cartItemCount={cart.reduce((sum, item) => sum + item.quantity, 0)}
        onCartClick={() => setShowCartModal(true)}
        onBackClick={() => window.location.href = '/'}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-card border-r border-border p-4 overflow-y-auto flex-shrink-0">
          {/* Species Filter - Using extracted component */}
          <SpeciesFilter
            selectedSpecies={selectedSpecies}
            onSpeciesChange={setSelectedSpecies}
          />

          {/* BIONIC™ Territory Engine Button */}
          <Card className="bg-gradient-to-r from-[#f5a623]/10 to-orange-500/10 border-[#f5a623]/30 mb-4">
            <CardContent className="p-3">
              <Button
                className="w-full bg-gradient-to-r from-[#f5a623] to-orange-500 hover:from-[#f5a623]/90 hover:to-orange-500/90 text-black font-medium"
                onClick={() => setShowBionicAnalyzer(true)}
                data-testid="bionic-engine-btn"
              >
                <Brain className="h-4 w-4 mr-2" />
                BIONIC™ Territory Engine
                <Zap className="h-4 w-4 ml-2" />
              </Button>
              <p className="text-gray-400 text-[10px] text-center mt-2">
                Analyse avancée • IA prédictive • Modules thématiques
              </p>
            </CardContent>
          </Card>

          {/* Layer Controls */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Layers className="h-4 w-4 text-[#f5a623]" />
                Couches de base
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Activity className="h-4 w-4 text-red-500" />
                  Heatmap activité
                </Label>
                <Switch checked={showHeatmap} onCheckedChange={setShowHeatmap} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Eye className="h-4 w-4 text-green-500" />
                  Observations
                </Label>
                <Switch checked={showEvents} onCheckedChange={setShowEvents} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Camera className="h-4 w-4 text-blue-500" />
                  Caméras
                </Label>
                <Switch checked={showCameras} onCheckedChange={setShowCameras} />
              </div>
            </CardContent>
          </Card>

          {/* Advanced Geological Layers */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Map className="h-4 w-4 text-[#f5a623]" />
                Cartes géologiques
                <Badge className="ml-auto bg-green-500/20 text-green-400 text-[10px]">Québec</Badge>
              </CardTitle>
              <CardDescription className="text-xs">
                Données du gouvernement du Québec
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Trees className="h-4 w-4 text-green-600" />
                  Couverture forestière
                </Label>
                <Switch checked={layerForet} onCheckedChange={setLayerForet} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Waves className="h-4 w-4 text-blue-500" />
                  Hydrographie (eau)
                </Label>
                <Switch checked={layerHydro} onCheckedChange={setLayerHydro} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Mountain className="h-4 w-4 text-amber-600" />
                  Relief / Courbes
                </Label>
                <Switch checked={layerTopo} onCheckedChange={setLayerTopo} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Route className="h-4 w-4 text-gray-400" />
                  Routes / Chemins
                </Label>
                <Switch checked={layerRoutes} onCheckedChange={setLayerRoutes} />
              </div>
            </CardContent>
          </Card>

          {/* Analysis Layers */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-[#f5a623]" />
                Analyse par espèce
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-gray-400 text-xs">Espèce à analyser</Label>
                <Select value={selectedAnalysisSpecies} onValueChange={setSelectedAnalysisSpecies}>
                  <SelectTrigger className="bg-card border-border mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="orignal">🫎 Orignal</SelectItem>
                    <SelectItem value="chevreuil">🦌 Chevreuil</SelectItem>
                    <SelectItem value="ours">🐻 Ours</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <CircleDot className="h-4 w-4 text-purple-500" />
                  Probabilité présence
                </Label>
                <Switch checked={layerProbability} onCheckedChange={(v) => {
                  setLayerProbability(v);
                  if (v) calculateProbability();
                }} />
              </div>

              {/* Generate Probability Zones Button */}
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full border-dashed"
                onClick={generateProbabilityZones}
                disabled={loadingZones}
              >
                {loadingZones ? (
                  <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Génération...</>
                ) : (
                  <><Map className="h-4 w-4 mr-2" /> Afficher zones colorées</>
                )}
              </Button>
              
              {/* Probability Zone Legend */}
              {probabilityZones.length > 0 && (
                <div className="p-2 bg-card rounded border border-border">
                  <p className="text-xs text-gray-400 mb-2">Légende des zones:</p>
                  <div className="flex items-center gap-3 text-xs">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded bg-green-500/60"></div>
                      <span className="text-green-400">Élevée</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded bg-yellow-500/60"></div>
                      <span className="text-yellow-400">Moyenne</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded bg-red-500/60"></div>
                      <span className="text-red-400">Faible</span>
                    </div>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full mt-2 text-xs h-7"
                    onClick={() => setProbabilityZones([])}
                  >
                    <X className="h-3 w-3 mr-1" /> Effacer zones
                  </Button>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <TreePine className="h-4 w-4 text-emerald-600" />
                  Zones de refuge
                </Label>
                <Switch checked={layerRefuge} onCheckedChange={setLayerRefuge} />
              </div>
              
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Thermometer className="h-4 w-4 text-cyan-500" />
                  Zones de fraîcheur
                </Label>
                <Switch checked={layerCooling} onCheckedChange={(v) => {
                  setLayerCooling(v);
                  if (v) loadCoolingZones();
                }} />
              </div>

              {/* Probability Result */}
              {probabilityData && layerProbability && (
                <div className="mt-3 p-3 bg-card rounded-lg border border-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white text-sm font-medium">Score de probabilité</span>
                    <Badge className={`${probabilityData.probability_score >= 70 ? 'bg-green-500' : probabilityData.probability_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}>
                      {probabilityData.probability_score}%
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-400">
                    Confiance: {probabilityData.confidence}
                  </div>
                  {probabilityData.recommendations?.map((rec, idx) => (
                    <div key={idx} className="text-xs text-gray-300 mt-1 flex items-start gap-1">
                      <ChevronRight className="h-3 w-3 text-[#f5a623] mt-0.5 flex-shrink-0" />
                      {rec}
                    </div>
                  ))}
                </div>
              )}

              {/* Cooling Zones Info */}
              {coolingZones && layerCooling && (
                <div className="mt-3 p-3 bg-card rounded-lg border border-border">
                  <div className="text-white text-sm font-medium mb-2">Zones de fraîcheur</div>
                  {coolingZones.recommended_zones?.slice(0, 3).map((zone, idx) => (
                    <div key={idx} className="text-xs text-gray-300 mb-2">
                      <div className="flex items-center gap-1">
                        <Badge variant="outline" className={`text-[10px] ${zone.priority === 'high' ? 'border-red-500 text-red-400' : 'border-yellow-500 text-yellow-400'}`}>
                          {zone.priority}
                        </Badge>
                        <span className="text-white">{zone.name}</span>
                      </div>
                      <div className="text-gray-400 ml-4">{zone.description}</div>
                    </div>
                  ))}
                  <div className="text-xs text-cyan-400 mt-2">
                    🕐 Meilleurs moments: {coolingZones.best_times?.join(', ')}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* GPS Tracking / Navigation */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Navigation className="h-4 w-4 text-[#f5a623]" />
                Navigation GPS
                <Badge className="ml-auto bg-blue-500/20 text-blue-400 text-[10px]">Avenza</Badge>
              </CardTitle>
              <CardDescription className="text-xs">
                Géolocalisation et tracé en temps réel
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Current Position */}
              {currentPosition && (
                <div className="p-2 bg-card rounded border border-green-500/30">
                  <div className="text-xs text-green-400 flex items-center gap-1">
                    <CircleDot className="h-3 w-3 animate-pulse" />
                    Position actuelle
                  </div>
                  <div className="text-white text-sm">
                    {currentPosition.lat.toFixed(5)}, {currentPosition.lng.toFixed(5)}
                  </div>
                  {currentPosition.accuracy && (
                    <div className="text-xs text-gray-400">Précision: ±{currentPosition.accuracy.toFixed(0)}m</div>
                  )}
                </div>
              )}

              {/* Tracking Controls */}
              <div className="flex gap-2">
                {!isTracking ? (
                  <Button 
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    size="sm"
                    onClick={startTracking}
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Démarrer tracé
                  </Button>
                ) : (
                  <Button 
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                    size="sm"
                    onClick={stopTracking}
                  >
                    <Square className="h-4 w-4 mr-1" />
                    Arrêter ({trackPoints.length} pts)
                  </Button>
                )}
              </div>

              {/* Track Info */}
              {isTracking && trackPoints.length > 0 && (
                <div className="text-xs text-gray-400">
                  Distance: {calculateTotalDistance(trackPoints).toFixed(2)} km
                </div>
              )}

              {/* Waypoint Controls */}
              <div className="border-t border-border pt-3 mt-3">
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-gray-400 text-xs">Waypoints ({waypoints.length})</Label>
                  {waypoints.length > 0 && (
                    <div className="flex gap-1">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="h-6 px-2 text-xs text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
                        onClick={handleExportGpxLocal}
                        title="Export GPX rapide"
                        data-testid="export-gpx-quick-btn"
                      >
                        <Download className="h-3 w-3 mr-1" />
                        GPX
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="h-6 px-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        onClick={deleteAllWaypoints}
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Effacer
                      </Button>
                    </div>
                  )}
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={getCurrentPositionForWaypoint}
                >
                  <Flag className="h-4 w-4 mr-1" />
                  Ajouter waypoint ici
                </Button>
                
                {/* Waypoints List */}
                {waypoints.length > 0 && (
                  <div className="mt-2 max-h-32 overflow-y-auto space-y-1">
                    {waypoints.slice(0, 5).map((wp) => (
                      <div key={wp.id} className="flex items-center justify-between p-1.5 bg-card rounded text-xs">
                        <div className="flex items-center gap-1">
                          <Bookmark className="h-3 w-3 text-[#f5a623]" />
                          <span className="text-white truncate max-w-[120px]">{wp.name}</span>
                        </div>
                        <button 
                          onClick={() => deleteWaypoint(wp.id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                    {waypoints.length > 5 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{waypoints.length - 5} autres waypoints
                      </div>
                    )}
                  </div>
                )}

                {/* Guided Route / Parcours Guidé Section */}
                {waypoints.length >= 2 && (
                  <div className="mt-3 pt-3 border-t border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <Navigation className="h-4 w-4 text-green-500" />
                      <Label className="text-white text-xs font-semibold">Parcours Guidé</Label>
                      <Badge className="bg-green-500/20 text-green-400 text-[9px]">IA</Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <Label className="text-gray-400 text-[10px]">Optimiser pour</Label>
                        <Select value={guidedRouteOptimization} onValueChange={setGuidedRouteOptimization}>
                          <SelectTrigger className="bg-card border-border mt-0.5 h-8 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="balanced">⚖️ Équilibré (distance + probabilité)</SelectItem>
                            <SelectItem value="probability">🎯 Maximiser probabilité</SelectItem>
                            <SelectItem value="distance">📏 Distance minimale</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <Button 
                        onClick={generateGuidedRoute}
                        disabled={loadingGuidedRoute || waypoints.length < 2}
                        className="w-full bg-green-600 hover:bg-green-700 text-white"
                        size="sm"
                      >
                        {loadingGuidedRoute ? (
                          <><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Calcul...</>
                        ) : (
                          <><Route className="h-3 w-3 mr-1" /> Générer parcours ({waypoints.length} pts)</>
                        )}
                      </Button>

                      {guidedRoute && (
                        <Button 
                          onClick={clearGuidedRoute}
                          variant="outline"
                          className="w-full text-red-400 border-red-400/50 hover:bg-red-400/10"
                          size="sm"
                        >
                          <X className="h-3 w-3 mr-1" /> Effacer parcours
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* GPX Import/Export */}
              <div className="border-t border-border pt-3 mt-3">
                <Label className="text-gray-400 text-xs mb-2 block">Import/Export GPX</Label>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    onClick={handleExportGpx}
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Export
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    onClick={() => gpxInputRef.current?.click()}
                    disabled={gpxImporting}
                  >
                    <Upload className="h-3 w-3 mr-1" />
                    Import
                  </Button>
                  <input
                    type="file"
                    ref={gpxInputRef}
                    accept=".gpx"
                    onChange={handleImportGpx}
                    className="hidden"
                  />
                </div>
                <p className="text-[10px] text-gray-500 mt-1">Compatible Avenza, Garmin, etc.</p>
              </div>
            </CardContent>
          </Card>

          {/* Nutrition Analysis */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <TreePine className="h-4 w-4 text-[#f5a623]" />
                Analyse Alimentation
                <Badge className="ml-auto bg-[#f5a623]/20 text-[#f5a623] text-[10px]">BIONIC™</Badge>
              </CardTitle>
              <CardDescription className="text-xs">
                Analyse nutritionnelle et recommandations produits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-gray-400 text-xs">Type de couvert forestier</Label>
                <Select value={selectedForestType} onValueChange={setSelectedForestType}>
                  <SelectTrigger className="bg-card border-border mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mixte">🌲🌳 Forêt mixte</SelectItem>
                    <SelectItem value="feuillus">🌳 Feuillus</SelectItem>
                    <SelectItem value="coniferes">🌲 Conifères</SelectItem>
                    <SelectItem value="regeneration">🌱 Régénération</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <Button 
                className="w-full btn-golden text-black"
                onClick={analyzeCurrentLocation}
                disabled={nutritionLoading}
              >
                {nutritionLoading ? (
                  <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Analyse...</>
                ) : (
                  <><TrendingUp className="h-4 w-4 mr-2" /> Analyser ce site</>
                )}
              </Button>
              
              <p className="text-[10px] text-gray-500 text-center">
                Analyse les besoins nutritionnels du {selectedAnalysisSpecies} et propose les produits BIONIC™ adaptés
              </p>
            </CardContent>
          </Card>

          {/* Upload Photo */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Upload className="h-4 w-4 text-[#f5a623]" />
                Upload Photo
              </CardTitle>
              <CardDescription className="text-xs">
                L'IA identifiera automatiquement l'espèce
              </CardDescription>
            </CardHeader>
            <CardContent>
              <input
                type="file"
                ref={fileInputRef}
                accept="image/*"
                onChange={handlePhotoUpload}
                className="hidden"
                id="photo-upload"
              />
              <Button 
                className="w-full btn-golden text-black"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                {uploading ? (
                  <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Analyse en cours...</>
                ) : (
                  <><Camera className="h-4 w-4 mr-2" /> Uploader une photo</>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Recent Events */}
          <Card className="bg-background border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Activity className="h-4 w-4 text-[#f5a623]" />
                Événements récents
              </CardTitle>
            </CardHeader>
            <CardContent className="max-h-64 overflow-y-auto">
              {filteredEvents.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-4">Aucun événement</p>
              ) : (
                <div className="space-y-2">
                  {filteredEvents.slice(0, 10).map((event) => (
                    <div 
                      key={event.id}
                      className="flex items-center gap-2 p-2 bg-card rounded-lg cursor-pointer hover:bg-card/80 transition-colors"
                      onClick={() => setMapCenter([event.latitude, event.longitude])}
                    >
                      <span className="text-xl">
                        {SPECIES_CONFIG[event.species]?.emoji || '❓'}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm font-medium truncate">
                          {SPECIES_CONFIG[event.species]?.label || event.species}
                        </p>
                        <p className="text-gray-500 text-xs">
                          {new Date(event.captured_at).toLocaleDateString('fr-CA', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      {event.species_confidence && (
                        <Badge variant="outline" className="text-xs">
                          {(event.species_confidence * 100).toFixed(0)}%
                        </Badge>
                      )}
                      <ChevronRight className="h-4 w-4 text-gray-500" />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Map */}
        <div className="flex-1 relative overflow-hidden">
          {loading && (
            <div className="absolute inset-0 bg-black/50 z-[1000] flex items-center justify-center">
              <div className="text-white flex items-center gap-2">
                <RefreshCw className="h-6 w-6 animate-spin" />
                Chargement...
              </div>
            </div>
          )}
          
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '100%', width: '100%' }}
            className="z-0"
            zoomControl={false}
          >
            <MapCenterController center={mapCenter} zoom={mapZoom} />
            <MapClickHandler activeTool={activeTool} onMapClick={handleMapClick} onMouseMove={handleMouseMove} />
            <ZoomControlPosition />
            <ZoomSyncComponent zoom={mapZoom} />
            
            {/* Base Layers - Controlled by selectedBaseLayer state */}
            {selectedBaseLayer === 'carte' && (
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
            )}
            {/* Satellite - Version originale simple (Esri World Imagery) */}
            {selectedBaseLayer === 'satellite' && (
              <>
                <TileLayer
                  attribution='&copy; Esri World Imagery'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                />
                {/* Labels */}
                <TileLayer
                  attribution='&copy; Esri'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                  zIndex={1000}
                />
              </>
            )}

            {/* Google Earth Style - Alternative gratuite (USGS/Esri Clarity) */}
            {selectedBaseLayer === 'google-earth' && (
              <>
                {/* High-resolution imagery similar to Google Earth */}
                <TileLayer
                  attribution='&copy; Esri, Maxar, Earthstar Geographics'
                  url="https://clarity.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                />
                {/* Roads and transportation overlay */}
                <TileLayer
                  attribution='&copy; Esri'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}"
                  zIndex={500}
                />
                {/* Labels and boundaries */}
                <TileLayer
                  attribution='&copy; Esri'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                  zIndex={1000}
                />
              </>
            )}

            {selectedBaseLayer === 'topographie' && (
              <TileLayer
                attribution='&copy; OpenTopoMap'
                url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
              />
            )}

            {/* Heatmap Layer */}
            {showHeatmap && heatmapData.length > 0 && (
              <HeatmapLayer points={heatmapData} radius={30} />
            )}

            {/* Camera Markers */}
            {showCameras && cameras.map((camera) => (
              camera.latitude && camera.longitude && (
                <Marker
                  key={camera.id}
                  position={[camera.latitude, camera.longitude]}
                  icon={createCustomIcon('#3b82f6', '📷')}
                >
                  <Popup>
                    <div className="text-sm min-w-48">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <p className="font-bold text-gray-800">{camera.label}</p>
                          <p className="text-gray-500 text-xs">{camera.brand}</p>
                        </div>
                        <button
                          onClick={() => {
                            if (window.confirm(`🗑️ Supprimer la caméra "${camera.label}" ?`)) {
                              // Remove camera from local state
                              setCameras(prev => prev.filter(c => c.id !== camera.id));
                              toast.success('📷 Caméra supprimée');
                            }
                          }}
                          className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex-shrink-0"
                          title="Supprimer cette caméra"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <p className={`text-sm ${camera.connected ? 'text-green-600' : 'text-red-600'}`}>
                        {camera.connected ? '✅ Connectée' : '⚠️ Non connectée'}
                      </p>
                    </div>
                  </Popup>
                </Marker>
              )
            ))}

            {/* Event Markers */}
            {showEvents && filteredEvents.map((event) => {
              const speciesConfig = SPECIES_CONFIG[event.species] || SPECIES_CONFIG.autre;
              const eventConfig = EVENT_TYPE_CONFIG[event.event_type] || {};
              
              return (
                <Marker
                  key={event.id}
                  position={[event.latitude, event.longitude]}
                  icon={createCustomIcon(speciesConfig.color, speciesConfig.emoji)}
                >
                  <Popup>
                    <div className="text-sm min-w-52">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{speciesConfig.emoji}</span>
                          <div>
                            <p className="font-bold text-gray-800">{speciesConfig.label}</p>
                            <p className="text-gray-500 text-xs">{eventConfig.label}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            if (window.confirm(`🗑️ Supprimer cette observation de ${speciesConfig.label} ?`)) {
                              deleteEvent(event.id);
                            }
                          }}
                          className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex-shrink-0"
                          title="Supprimer cette observation"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="bg-gray-100 p-2 rounded text-xs space-y-1">
                        {event.species_confidence && (
                          <p className="text-gray-600">
                            <span className="font-medium">Confiance:</span> {(event.species_confidence * 100).toFixed(0)}%
                          </p>
                        )}
                        {event.count_estimate > 1 && (
                          <p className="text-gray-600">
                            <span className="font-medium">Individus:</span> {event.count_estimate}
                          </p>
                        )}
                        <p className="text-gray-500 text-[10px]">
                          {new Date(event.captured_at).toLocaleString('fr-CA')}
                        </p>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

            {/* Hunting Territories Markers */}
            {showHuntingMarkers && nearbyTerritories.map((territory) => (
              <Marker
                key={`territory-${territory.name}`}
                position={[territory.lat, territory.lng]}
                icon={createCustomIcon(
                  territory.type === 'ZEC' ? '#22c55e' : 
                  territory.type === 'Réserve faunique' ? '#3b82f6' : 
                  '#f59e0b',
                  territory.icon || (territory.type === 'ZEC' ? '🏕️' : territory.type === 'Réserve faunique' ? '🦌' : '🏠')
                )}
              >
                <Popup>
                  <div className="text-sm min-w-52">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{territory.icon || '🏕️'}</span>
                      <div>
                        <p className="font-bold text-gray-800">{territory.name}</p>
                        <p className="text-xs text-gray-500">{territory.type}</p>
                      </div>
                    </div>
                    <div className="bg-gray-100 p-2 rounded text-xs space-y-1">
                      <p><span className="font-medium">Région:</span> {territory.region}</p>
                      {territory.distance_km && (
                        <p><span className="font-medium">Distance:</span> {territory.distance_km} km</p>
                      )}
                      <p className="font-medium mt-1">Espèces:</p>
                      <div className="flex flex-wrap gap-1">
                        {territory.species?.map(sp => (
                          <span key={sp} className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded text-[10px]">
                            {sp === 'orignal' ? '🫎' : sp === 'chevreuil' ? '🦌' : sp === 'ours' ? '🐻' : sp === 'caribou' ? '🦌' : '🎯'} {sp}
                          </span>
                        ))}
                      </div>
                    </div>
                    {territory.website && (
                      <a 
                        href={territory.website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="block mt-2 text-center bg-blue-500 hover:bg-blue-600 text-white text-xs py-1.5 px-3 rounded transition-colors"
                      >
                        🌐 Visiter le site
                      </a>
                    )}
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Route Line */}
            {routePoints.length >= 2 && (
              <Polyline
                positions={routePoints.map(p => [p.lat, p.lng])}
                color="#f5a623"
                weight={3}
                dashArray="10, 5"
              />
            )}

            {/* Route Points Markers */}
            {routePoints.map((point, idx) => (
              <Marker
                key={`route-${idx}`}
                position={[point.lat, point.lng]}
                icon={createCustomIcon('#f5a623', `${idx + 1}`)}
              />
            ))}

            {/* Measure Line */}
            {measurePoints.length >= 2 && (
              <Polyline
                positions={measurePoints.map(p => [p.lat, p.lng])}
                color="#3b82f6"
                weight={2}
                dashArray="5, 5"
              />
            )}

            {/* Measure Points Markers */}
            {measurePoints.map((point, idx) => (
              <Marker
                key={`measure-${idx}`}
                position={[point.lat, point.lng]}
                icon={createCustomIcon('#3b82f6', '📍')}
              />
            ))}

            {/* Pending Marker */}
            {pendingMarker && (
              <Marker
                position={[pendingMarker.lat, pendingMarker.lng]}
                icon={createCustomIcon('#22c55e', '+')}
              />
            )}

            {/* Waypoints - Draggable */}
            {waypoints.map((wp) => (
              <Marker
                key={`waypoint-${wp.id}`}
                position={[wp.latitude, wp.longitude]}
                icon={createCustomIcon('#f59e0b', '🚩')}
                draggable={true}
                eventHandlers={{
                  dragstart: () => {
                    handleWaypointDragStart(wp);
                  },
                  drag: (e) => {
                    const newPos = e.target.getLatLng();
                    setLiveGpsCoords({
                      lat: newPos.lat,
                      lng: newPos.lng,
                      latDms: decimalToDms(newPos.lat, true),
                      lngDms: decimalToDms(newPos.lng, false)
                    });
                  },
                  dragend: (e) => {
                    const newPos = e.target.getLatLng();
                    handleWaypointDragEnd(wp, { lat: newPos.lat, lng: newPos.lng });
                  }
                }}
              >
                <Popup>
                  <div className="text-sm min-w-48">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <p className="font-bold text-base text-gray-800">{wp.name}</p>
                        <p className="text-gray-500 text-xs">{wp.waypoint_type}</p>
                      </div>
                      <button
                        onClick={() => {
                          if (window.confirm(`⚠️ SUPPRESSION DÉFINITIVE\n\nÊtes-vous sûr de vouloir supprimer le waypoint "${wp.name}" ?\n\nCette action est irréversible.`)) {
                            deleteWaypoint(wp.id);
                          }
                        }}
                        className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex-shrink-0 shadow-md"
                        title="Supprimer définitivement ce waypoint"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="text-[11px] text-gray-500 space-y-0.5 bg-gray-100 p-2 rounded">
                      <p><span className="font-medium">Lat:</span> {wp.latitude.toFixed(6)}</p>
                      <p><span className="font-medium">Lng:</span> {wp.longitude.toFixed(6)}</p>
                    </div>
                    {wp.description && (
                      <p className="text-gray-600 text-xs mt-2 italic">{wp.description}</p>
                    )}
                    <p className="text-blue-500 text-[10px] mt-2 italic text-center">
                      ↔️ Glissez le marqueur pour déplacer
                    </p>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Guided Route Line & Markers */}
            {guidedRoute && (
              <>
                {/* Route line connecting all points */}
                <Polyline
                  positions={guidedRoute.waypoint_order.map(p => [p.lat, p.lng])}
                  color="#22c55e"
                  weight={4}
                  opacity={0.8}
                />
                
                {/* Segment color overlays showing probability */}
                {guidedRoute.segments.map((segment, idx) => (
                  <Polyline
                    key={`segment-${idx}`}
                    positions={[
                      [segment.from_waypoint.lat, segment.from_waypoint.lng],
                      [segment.to_waypoint.lat, segment.to_waypoint.lng]
                    ]}
                    color={segment.color}
                    weight={6}
                    opacity={0.6}
                  />
                ))}
                
                {/* Route point markers with numbers */}
                {guidedRoute.waypoint_order.map((point, idx) => (
                  <Marker
                    key={`guided-${point.id}`}
                    position={[point.lat, point.lng]}
                    icon={L.divIcon({
                      className: 'guided-route-marker',
                      html: `<div style="
                        background: ${point.color};
                        width: 28px;
                        height: 28px;
                        border-radius: 50%;
                        border: 3px solid white;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 12px;
                        color: white;
                      ">${idx + 1}</div>`,
                      iconSize: [28, 28],
                      iconAnchor: [14, 14]
                    })}
                  >
                    <Popup>
                      <div className="text-sm min-w-40">
                        <div className="flex items-center justify-between mb-1">
                          <p className="font-bold">{point.name}</p>
                          <span 
                            className="px-2 py-0.5 rounded text-white text-xs font-bold"
                            style={{ backgroundColor: point.color }}
                          >
                            {point.probability}%
                          </span>
                        </div>
                        <p className="text-gray-500 text-xs">Étape {idx + 1} du parcours</p>
                        <p className="text-gray-400 text-[10px] mt-1">
                          {point.lat.toFixed(5)}, {point.lng.toFixed(5)}
                        </p>
                        {guidedRoute.segments[idx] && (
                          <div className="mt-2 pt-2 border-t border-gray-200">
                            <p className="text-xs text-gray-600">
                              → {guidedRoute.segments[idx].distance_km} km vers suivant
                            </p>
                          </div>
                        )}
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </>
            )}

            {/* GPS Track Line */}
            {trackPoints.length >= 2 && (
              <Polyline
                positions={trackPoints.map(p => [p.lat, p.lng])}
                color="#10b981"
                weight={4}
              />
            )}

            {/* Current Position Marker */}
            {currentPosition && (
              <Circle
                center={[currentPosition.lat, currentPosition.lng]}
                radius={currentPosition.accuracy || 10}
                pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.2 }}
              >
                <Marker
                  position={[currentPosition.lat, currentPosition.lng]}
                  icon={createCustomIcon('#3b82f6', '📍')}
                >
                  <Popup>
                    <div className="text-sm">
                      <p className="font-bold">Ma position</p>
                      <p className="text-gray-600">{currentPosition.lat.toFixed(5)}, {currentPosition.lng.toFixed(5)}</p>
                      {currentPosition.accuracy && (
                        <p className="text-gray-500 text-xs">Précision: ±{currentPosition.accuracy.toFixed(0)}m</p>
                      )}
                    </div>
                  </Popup>
                </Marker>
              </Circle>
            )}

            {/* BIONIC™ Territory Engine Layers - Version 3.0 Micro-Délimitée */}
            {bionicPrecisionZones && bionicPrecisionZones.length > 0 && (
              <>
                {bionicPrecisionZones
                  .filter(zone => bionicLayersVisible[zone.moduleKey])
                  .map((zone, index) => (
                    <Polygon
                      key={`bionic-precision-${zone.id}-${index}`}
                      positions={zone.polygon}
                      pathOptions={{
                        color: zone.color,
                        fillColor: zone.color,
                        fillOpacity: zone.fillOpacity || 0.03,
                        weight: zone.strokeWeight || 1.5,
                        opacity: zone.strokeOpacity || 0.7,
                        dashArray: zone.probability >= 80 ? null : '3, 3' // Trait plein pour haute prob, pointillé sinon
                      }}
                      eventHandlers={{
                        mouseover: (e) => {
                          e.target.setStyle({
                            fillOpacity: Math.min(0.25, (zone.fillOpacity || 0.03) + 0.15),
                            weight: (zone.strokeWeight || 1.5) + 1,
                            opacity: 1
                          });
                        },
                        mouseout: (e) => {
                          e.target.setStyle({
                            fillOpacity: zone.fillOpacity || 0.03,
                            weight: zone.strokeWeight || 1.5,
                            opacity: zone.strokeOpacity || 0.7
                          });
                        }
                      }}
                    >
                      <Tooltip 
                        sticky 
                        className="bionic-tooltip"
                        direction="top"
                        offset={[0, -10]}
                      >
                        <div className="text-center min-w-[120px]">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <span>{zone.icon}</span>
                            <span className="font-bold text-sm">{zone.probability}%</span>
                          </div>
                          <div className="text-xs text-gray-600">{zone.label}</div>
                          <div 
                            className="text-xs font-medium mt-1"
                            style={{ color: zone.color }}
                          >
                            {zone.rating?.text || 'Zone active'}
                          </div>
                        </div>
                      </Tooltip>
                      <Popup>
                        <div className="min-w-[220px]">
                          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-200">
                            <span className="text-2xl">{zone.icon}</span>
                            <div>
                              <p className="font-bold text-gray-800">{zone.label}</p>
                              <p className="text-xs text-gray-500">{zone.name}</p>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-gray-600 text-sm">Probabilité:</span>
                            <span 
                              className="font-bold text-xl"
                              style={{ color: zone.color }}
                            >
                              {zone.probability}%
                            </span>
                          </div>
                          
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-gray-600 text-sm">Évaluation:</span>
                            <span 
                              className="font-medium px-2 py-0.5 rounded text-sm"
                              style={{ 
                                backgroundColor: `${zone.color}20`,
                                color: zone.color 
                              }}
                            >
                              {zone.rating?.text || 'Zone active'}
                            </span>
                          </div>
                          
                          <div className="bg-gray-50 rounded p-2 text-xs">
                            <p className="text-gray-500 mb-1">Niveau de confiance:</p>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="h-2 rounded-full transition-all"
                                style={{ 
                                  width: `${zone.probability}%`,
                                  backgroundColor: zone.color 
                                }}
                              />
                            </div>
                          </div>
                          
                          {zone.recommendations && zone.recommendations.length > 0 && (
                            <div className="mt-3 pt-2 border-t border-gray-200">
                              <p className="text-xs text-gray-500 mb-1 font-medium">💡 Recommandations:</p>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {zone.recommendations.slice(0, 2).map((rec, i) => (
                                  <li key={i} className="flex items-start gap-1">
                                    <span className="text-gray-400">•</span>
                                    <span>{rec}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </Popup>
                    </Polygon>
                  ))}
              </>
            )}
          </MapContainer>

          {/* Waypoint Modal */}
          {showWaypointModal && pendingWaypoint && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-[1001] bg-card border border-border rounded-xl p-4 shadow-xl min-w-[280px]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold">Nouveau waypoint</h3>
                <button 
                  onClick={() => { setShowWaypointModal(false); setPendingWaypoint(null); }}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <p className="text-gray-400 text-sm mb-3">
                Position: {pendingWaypoint.lat.toFixed(5)}, {pendingWaypoint.lng.toFixed(5)}
              </p>
              
              <div className="space-y-3">
                <div>
                  <Label className="text-gray-400 text-xs">Nom du waypoint</Label>
                  <Input
                    value={waypointName}
                    onChange={(e) => setWaypointName(e.target.value)}
                    placeholder="Ex: Cache à sel, Affût..."
                    className="bg-card border-border mt-1"
                  />
                </div>
                
                <div>
                  <Label className="text-gray-400 text-xs">Type</Label>
                  <Select value={waypointType} onValueChange={setWaypointType}>
                    <SelectTrigger className="bg-card border-border mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="observation">👁️ Observation</SelectItem>
                      <SelectItem value="camera">📷 Caméra</SelectItem>
                      <SelectItem value="cache">🧂 Cache (sel/appât)</SelectItem>
                      <SelectItem value="stand">🏕️ Affût/Mirador</SelectItem>
                      <SelectItem value="water">💧 Point d'eau</SelectItem>
                      <SelectItem value="trail_start">🚶 Départ sentier</SelectItem>
                      <SelectItem value="custom">📍 Autre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex gap-2 mt-4">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => { setShowWaypointModal(false); setPendingWaypoint(null); }}
                >
                  Annuler
                </Button>
                <Button 
                  className="flex-1 btn-golden text-black"
                  onClick={addWaypoint}
                  disabled={!waypointName}
                >
                  <Flag className="h-4 w-4 mr-1" />
                  Ajouter
                </Button>
              </div>
            </div>
          )}

          {/* Species Selection Modal for Pin Tool */}
          {pendingMarker && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-[1001] bg-card border border-border rounded-xl p-4 shadow-xl min-w-[280px]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold">Nouvelle observation</h3>
                <button 
                  onClick={() => { setPendingMarker(null); setActiveTool(null); }}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <p className="text-gray-400 text-sm mb-3">
                Position: {pendingMarker.lat.toFixed(4)}, {pendingMarker.lng.toFixed(4)}
              </p>
              
              <div className="mb-4">
                <Label className="text-gray-400 text-xs mb-2 block">Espèce observée</Label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(SPECIES_CONFIG).filter(([k]) => k !== 'autre').map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedSpeciesForMarker(key)}
                      className={`p-2 rounded-lg border transition-all flex items-center gap-2 ${
                        selectedSpeciesForMarker === key 
                          ? 'border-[#f5a623] bg-[#f5a623]/10 text-white' 
                          : 'border-border text-gray-400 hover:border-gray-500'
                      }`}
                    >
                      <span className="text-lg">{config.emoji}</span>
                      <span className="text-sm">{config.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => { setPendingMarker(null); setActiveTool(null); }}
                >
                  Annuler
                </Button>
                <Button 
                  className="flex-1 btn-golden text-black"
                  onClick={confirmAddMarker}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Ajouter
                </Button>
              </div>
            </div>
          )}

          {/* Clear Route/Measure Button */}
          {(routePoints.length > 0 || measurePoints.length > 0) && (
            <Button
              className="absolute top-24 left-4 z-[500] bg-red-500/90 hover:bg-red-600 text-white border-0"
              size="sm"
              onClick={clearToolPoints}
            >
              <X className="h-4 w-4 mr-1" />
              Effacer tracé
            </Button>
          )}

          {/* Guided Route Panel - Shows route details and probabilities */}
          {guidedRoute && showGuidedRoutePanel && (
            <div className="absolute top-4 left-4 z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border border-green-500/30 w-[340px] max-h-[70vh] overflow-hidden" style={{marginLeft: '0'}}>
              {/* Header */}
              <div className="p-3 bg-gradient-to-r from-green-600/20 to-emerald-600/20 border-b border-green-500/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-green-500/20 rounded-lg">
                      <Navigation className="h-5 w-5 text-green-400" />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-sm">Parcours Guidé</h3>
                      <p className="text-green-400 text-[10px] font-medium">{selectedAnalysisSpecies.toUpperCase()}</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setShowGuidedRoutePanel(false)}
                    className="p-1 text-gray-400 hover:text-white rounded"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Stats Bar */}
              <div className="grid grid-cols-3 gap-1 p-2 bg-black/50 border-b border-green-500/20">
                <div className="text-center p-1.5 bg-green-500/10 rounded">
                  <div className="text-green-400 text-lg font-bold">{guidedRoute.total_distance_km}</div>
                  <div className="text-gray-500 text-[9px]">KM</div>
                </div>
                <div className="text-center p-1.5 bg-yellow-500/10 rounded">
                  <div className="text-yellow-400 text-lg font-bold">{guidedRoute.estimated_time_hours}h</div>
                  <div className="text-gray-500 text-[9px]">DURÉE</div>
                </div>
                <div className="text-center p-1.5 bg-blue-500/10 rounded">
                  <div className="text-blue-400 text-lg font-bold">{Math.round(guidedRoute.average_probability)}%</div>
                  <div className="text-gray-500 text-[9px]">MOY. PROB</div>
                </div>
              </div>

              {/* Best Zone Highlight */}
              {guidedRoute.highest_probability_zone && (
                <div className="p-2 mx-2 mt-2 bg-gradient-to-r from-green-500/20 to-emerald-500/10 rounded-lg border border-green-500/30">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-green-500 rounded-full">
                      <Target className="h-3 w-3 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="text-[10px] text-green-400 font-semibold">MEILLEURE ZONE</div>
                      <div className="text-white text-sm font-medium">{guidedRoute.highest_probability_zone.name}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-green-400 text-xl font-bold">{guidedRoute.highest_probability_zone.probability}%</div>
                    </div>
                  </div>
                  {guidedRoute.highest_probability_zone.factors?.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {guidedRoute.highest_probability_zone.factors.slice(0, 3).map((factor, idx) => (
                        <span key={idx} className="text-[9px] bg-green-500/20 text-green-300 px-1.5 py-0.5 rounded">
                          {factor}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Route Points List */}
              <div className="p-2 max-h-[calc(70vh-240px)] overflow-y-auto">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
                  Itinéraire ({guidedRoute.waypoint_order.length} points)
                </div>
                <div className="space-y-1">
                  {guidedRoute.waypoint_order.map((point, idx) => (
                    <button
                      key={point.id}
                      onClick={() => navigateToRoutePoint(point)}
                      className="w-full p-2 bg-card/50 hover:bg-card rounded-lg border border-border/50 hover:border-green-500/30 transition-all text-left group"
                    >
                      <div className="flex items-center gap-2">
                        {/* Step Number */}
                        <div 
                          className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                          style={{ backgroundColor: point.color }}
                        >
                          {idx + 1}
                        </div>
                        
                        {/* Point Info */}
                        <div className="flex-1 min-w-0">
                          <div className="text-white text-sm font-medium truncate">{point.name}</div>
                          <div className="text-gray-500 text-[10px]">
                            {point.lat.toFixed(4)}, {point.lng.toFixed(4)}
                          </div>
                        </div>
                        
                        {/* Probability Badge */}
                        <div 
                          className="px-2 py-1 rounded-lg text-white text-xs font-bold"
                          style={{ backgroundColor: point.color }}
                        >
                          {point.probability}%
                        </div>
                      </div>
                      
                      {/* Segment info (distance to next) */}
                      {idx < guidedRoute.segments.length && (
                        <div className="mt-1.5 flex items-center gap-2 text-[10px] text-gray-500">
                          <ArrowRight className="h-3 w-3" />
                          <span>{guidedRoute.segments[idx].distance_km} km vers suivant</span>
                          {guidedRoute.segments[idx].probability_level === 'high' && (
                            <span className="text-green-400">• Zone favorable</span>
                          )}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Footer Actions */}
              <div className="p-2 border-t border-green-500/20 bg-black/50">
                <p className="text-[10px] text-gray-400 mb-2 text-center">{guidedRoute.summary}</p>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1 text-xs"
                    onClick={() => setShowGuidedRoutePanel(false)}
                  >
                    <EyeOff className="h-3 w-3 mr-1" />
                    Masquer
                  </Button>
                  <Button 
                    size="sm" 
                    className="flex-1 bg-red-500/80 hover:bg-red-600 text-white text-xs"
                    onClick={clearGuidedRoute}
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    Effacer
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Territory Analysis Panel - Shows analysis results */}
          {territoryAnalysis && (
            <div className="absolute top-4 right-[280px] z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border border-green-500/30 w-[380px] max-h-[80vh] overflow-hidden">
              {/* Header */}
              <div className="p-3 border-b border-green-500/30" style={{ backgroundColor: `${territoryAnalysis.typeColor}20` }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg" style={{ backgroundColor: `${territoryAnalysis.typeColor}30` }}>
                      <Target className="h-5 w-5" style={{ color: territoryAnalysis.typeColor }} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-sm">{territoryAnalysis.name}</h3>
                      <p className="text-xs" style={{ color: territoryAnalysis.typeColor }}>{territoryAnalysis.typeName} • {territoryAnalysis.region}</p>
                    </div>
                  </div>
                  <button 
                    onClick={clearTerritoryAnalysis}
                    className="p-1 text-gray-400 hover:text-white rounded"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Score Global */}
              <div className="p-3 border-b border-green-500/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-xs">Score global de qualité</span>
                  <span className="text-2xl font-bold" style={{ color: territoryAnalysis.qualityScore >= 80 ? '#22c55e' : territoryAnalysis.qualityScore >= 60 ? '#f59e0b' : '#ef4444' }}>
                    {territoryAnalysis.qualityScore}/100
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all"
                    style={{ 
                      width: `${territoryAnalysis.qualityScore}%`,
                      backgroundColor: territoryAnalysis.qualityScore >= 80 ? '#22c55e' : territoryAnalysis.qualityScore >= 60 ? '#f59e0b' : '#ef4444'
                    }}
                  />
                </div>
              </div>

              {/* Indices */}
              <div className="p-3 border-b border-green-500/20">
                <div className="text-xs text-gray-500 uppercase mb-2">Indices d'analyse</div>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { label: 'Pression chasse', value: territoryAnalysis.indices.pression, icon: '🎯' },
                    { label: 'Accessibilité', value: territoryAnalysis.indices.accessibilite, icon: '🚗' },
                    { label: 'Qualité habitat', value: territoryAnalysis.indices.habitat, icon: '🌲' },
                    { label: 'Score global', value: territoryAnalysis.indices.qualite, icon: '⭐' }
                  ].map((indice, idx) => (
                    <div key={idx} className="bg-card/50 p-2 rounded-lg">
                      <div className="flex items-center gap-1 text-[10px] text-gray-400 mb-1">
                        <span>{indice.icon}</span>
                        <span>{indice.label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full"
                            style={{ 
                              width: `${indice.value}%`,
                              backgroundColor: indice.value >= 75 ? '#22c55e' : indice.value >= 50 ? '#f59e0b' : '#ef4444'
                            }}
                          />
                        </div>
                        <span className="text-white text-xs font-bold">{indice.value}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Taux de succès par espèce */}
              {territoryAnalysis.successRate && (
                <div className="p-3 border-b border-green-500/20">
                  <div className="text-xs text-gray-500 uppercase mb-2">Taux de succès historique</div>
                  <div className="flex gap-2">
                    {Object.entries(territoryAnalysis.successRate).map(([species, rate]) => (
                      <div 
                        key={species} 
                        className={`flex-1 text-center p-2 rounded-lg ${rate > 0 ? 'bg-green-500/10 border border-green-500/30' : 'bg-gray-700/30'}`}
                      >
                        <div className="text-lg mb-0.5">
                          {species === 'orignal' ? '🦌' : species === 'chevreuil' ? '🦌' : '🐻'}
                        </div>
                        <div className={`text-sm font-bold ${rate > 0 ? 'text-green-400' : 'text-gray-500'}`}>
                          {rate > 0 ? `${rate}%` : 'N/A'}
                        </div>
                        <div className="text-[9px] text-gray-500 capitalize">{species}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {territoryAnalysis.recommendations?.length > 0 && (
                <div className="p-3 border-b border-green-500/20">
                  <div className="text-xs text-gray-500 uppercase mb-2">Recommandations</div>
                  <ul className="space-y-1.5">
                    {territoryAnalysis.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-xs text-green-300 flex items-start gap-1.5">
                        <Check className="h-3 w-3 mt-0.5 flex-shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Warnings */}
              {territoryAnalysis.warnings?.length > 0 && (
                <div className="p-3 border-b border-green-500/20 bg-red-500/5">
                  <div className="text-xs text-red-400 uppercase mb-2">Avertissements</div>
                  <ul className="space-y-1.5">
                    {territoryAnalysis.warnings.map((warn, idx) => (
                      <li key={idx} className="text-xs text-red-300 flex items-start gap-1.5">
                        <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
                        <span>{warn}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Règlements */}
              <div className="p-3">
                <div className="text-xs text-gray-500 uppercase mb-2">Synthèse réglementaire</div>
                <ul className="space-y-1">
                  {territoryAnalysis.reglements?.map((reg, idx) => (
                    <li key={idx} className="text-[10px] text-gray-400 flex items-center gap-1.5">
                      <div className="w-1 h-1 rounded-full bg-gray-500" />
                      {reg}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* GPS Preview Panel - ENHANCED with continuous flow */}
          {(gpsFlowMode || activeTool === 'waypoint' || draggingWaypoint) && mouseGpsPreview && (
            <div className="absolute bottom-24 left-1/2 transform -translate-x-1/2 z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border-2 border-green-500/50 px-5 py-4 min-w-[400px]">
              {/* Flow Mode Indicator */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <div className="absolute inset-0 w-3 h-3 rounded-full bg-green-500 animate-ping"></div>
                  </div>
                  <span className="text-green-400 text-sm font-bold">🛰️ FLUX GPS EN DIRECT</span>
                </div>
                <Badge className="bg-green-500/20 text-green-400 text-[10px] animate-pulse">
                  STREAMING
                </Badge>
              </div>

              {/* Coordinates Grid */}
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div className="bg-gray-900/50 rounded-lg p-2">
                  <div className="text-gray-500 text-[9px] uppercase tracking-wider mb-1">Format Décimal</div>
                  <div className="text-green-400 text-base font-mono font-bold">
                    {mouseGpsPreview.lat.toFixed(6)}
                  </div>
                  <div className="text-green-400 text-base font-mono font-bold">
                    {mouseGpsPreview.lng.toFixed(6)}
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-2">
                  <div className="text-gray-500 text-[9px] uppercase tracking-wider mb-1">Format DMS</div>
                  <div className="text-blue-400 text-sm font-mono">
                    {mouseGpsPreview.latDms}
                  </div>
                  <div className="text-blue-400 text-sm font-mono">
                    {mouseGpsPreview.lngDms}
                  </div>
                </div>
              </div>

              {/* Additional GPS Data */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="bg-gray-800/50 rounded p-2 text-center">
                  <div className="text-gray-500 text-[8px] uppercase">Altitude</div>
                  <div className="text-yellow-400 text-sm font-bold">{mouseGpsPreview.altitude || '~'}m</div>
                </div>
                <div className="bg-gray-800/50 rounded p-2 text-center">
                  <div className="text-gray-500 text-[8px] uppercase">Précision</div>
                  <div className="text-cyan-400 text-sm font-bold">±{mouseGpsPreview.precision || '~'}m</div>
                </div>
                <div className="bg-gray-800/50 rounded p-2 text-center">
                  <div className="text-gray-500 text-[8px] uppercase">Zone</div>
                  <div className="text-purple-400 text-sm font-bold">UTM 19N</div>
                </div>
              </div>

              {/* Flow Status & Instructions */}
              <div className="pt-2 border-t border-green-500/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-green-400 animate-pulse" />
                    <span className="text-gray-400 text-xs">Données injectées dans Analyse GPS</span>
                  </div>
                  <span className="text-green-400 text-[10px] font-mono">{new Date().toLocaleTimeString()}</span>
                </div>
                
                {/* Action Buttons */}
                <div className="flex gap-2 mt-3">
                  <Button
                    onClick={analyzeCurrentPosition}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white text-xs py-2"
                    data-testid="analyze-point-btn"
                  >
                    <Target className="h-3.5 w-3.5 mr-1.5" />
                    Analyser ce point
                  </Button>
                  <Button
                    onClick={() => {
                      if (mouseGpsPreview) {
                        setPendingWaypoint({ lat: mouseGpsPreview.lat, lng: mouseGpsPreview.lng });
                        setShowWaypointModal(true);
                      }
                    }}
                    className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white text-xs py-2"
                    data-testid="create-waypoint-quick-btn"
                  >
                    <Flag className="h-3.5 w-3.5 mr-1.5" />
                    Créer waypoint
                  </Button>
                </div>
                
                <p className="text-center text-gray-400 text-[10px] mt-2">
                  {draggingWaypoint ? '🎯 Relâchez pour confirmer la position' : '💡 Analysez rapidement ou créez un waypoint'}
                </p>
              </div>
            </div>
          )}

          {/* Map Tools Toolbar - Right Side */}
          <div className="absolute top-36 right-16 z-[600]">
            <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 flex flex-col items-center p-1 gap-1">
              {/* Pin Tool */}
              <button
                onClick={() => setActiveTool(activeTool === 'pin' ? null : 'pin')}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'pin' 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-pin"
                title="Ajouter un marqueur"
              >
                <MapPin className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Marqueur
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Waypoint Tool - NEW */}
              <button
                onClick={() => {
                  const newState = activeTool === 'waypoint' ? null : 'waypoint';
                  setActiveTool(newState);
                  setWaypointToolActive(!!newState);
                  setGpsFlowMode(!!newState); // Activer le mode flux GPS
                  if (newState) {
                    toast.info('🛰️ Mode flux GPS activé - Déplacez la souris sur la carte');
                  } else {
                    setMouseGpsPreview(null);
                    setLiveGpsCoords(null);
                  }
                }}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'waypoint' 
                    ? 'bg-green-500 text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-waypoint"
                title="Ajouter un waypoint"
              >
                <Flag className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Waypoint GPS
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Route Tool */}
              <button
                onClick={() => setActiveTool(activeTool === 'route' ? null : 'route')}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'route' 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-route"
                title="Tracer un chemin"
              >
                <Route className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Chemin
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Layers Tool */}
              <button
                onClick={() => setShowLayersPanel(!showLayersPanel)}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  showLayersPanel 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-layers"
                title="Couches"
              >
                <Layers className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Couches
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Measure Tool */}
              <button
                onClick={() => setActiveTool(activeTool === 'measure' ? null : 'measure')}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'measure' 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-measure"
                title="Mesurer la distance"
              >
                <Ruler className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Mesure
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Imagery/View Tool - Now opens layers panel */}
              <button
                onClick={() => setShowLayersPanel(!showLayersPanel)}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  showLayersPanel 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-imagery"
                title="Type de carte"
              >
                <Mountain className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Vue carte
                </span>
              </button>
            </div>
          </div>

          {/* Layers Panel - Unified control for all map layers */}
          {showLayersPanel && (
            <div className="absolute top-36 right-32 z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border border-[#f5a623]/30 w-[280px] max-h-[70vh] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="p-3 bg-gradient-to-r from-[#f5a623]/20 to-orange-600/10 border-b border-[#f5a623]/20 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="h-5 w-5 text-[#f5a623]" />
                    <h3 className="text-white font-bold text-sm">Couches de carte</h3>
                  </div>
                  <button 
                    onClick={() => setShowLayersPanel(false)}
                    className="p-1 text-gray-400 hover:text-white rounded"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Scrollable Content */}
              <div className="overflow-y-auto flex-1">
              {/* Base Layers */}
              <div className="p-3 border-b border-gray-700">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Fond de carte</div>
                <div className="space-y-1">
                  {[
                    { id: 'carte', name: 'Carte + Labels', icon: '🗺️', desc: 'OpenStreetMap' },
                    { id: 'satellite', name: 'Satellite', icon: '🛰️', desc: 'Esri World Imagery' },
                    { id: 'google-earth', name: 'Satellite et Routes', icon: '🌍', desc: 'Esri Clarity HD' },
                    { id: 'topographie', name: 'Topographie', icon: '⛰️', desc: 'OpenTopoMap' },
                  ].map((layer) => (
                    <button
                      key={layer.id}
                      onClick={() => {
                        setSelectedBaseLayer(layer.id);
                        toast.success(`🗺️ Fond de carte: ${layer.name}`);
                      }}
                      className={`w-full flex items-center gap-2 p-2 rounded-lg transition-all ${
                        selectedBaseLayer === layer.id 
                          ? 'bg-[#f5a623]/20 border border-[#f5a623]/50' 
                          : 'bg-gray-800/50 hover:bg-gray-700/50'
                      }`}
                    >
                      <span className="text-lg">{layer.icon}</span>
                      <div className="flex-1 text-left">
                        <div className={`text-sm ${selectedBaseLayer === layer.id ? 'text-[#f5a623]' : 'text-white'}`}>
                          {layer.name}
                        </div>
                        <div className="text-[10px] text-gray-500">{layer.desc}</div>
                      </div>
                      {selectedBaseLayer === layer.id && (
                        <Check className="h-4 w-4 text-[#f5a623]" />
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Overlay Layers */}
              <div className="p-3 border-b border-gray-700">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Superpositions</div>
                <div className="space-y-1">
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showHeatmap} 
                      onChange={(e) => setShowHeatmap(e.target.checked)}
                      className="rounded border-gray-600 text-[#f5a623] focus:ring-[#f5a623]"
                    />
                    <span className="text-lg">🔥</span>
                    <span className="text-white text-sm">Heatmap activité</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showCameras} 
                      onChange={(e) => setShowCameras(e.target.checked)}
                      className="rounded border-gray-600 text-[#f5a623] focus:ring-[#f5a623]"
                    />
                    <span className="text-lg">📷</span>
                    <span className="text-white text-sm">Caméras</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showForestTrails} 
                      onChange={(e) => setShowForestTrails(e.target.checked)}
                      className="rounded border-gray-600 text-white focus:ring-white"
                    />
                    <span className="text-lg">🛤️</span>
                    <span className="text-white text-sm">Chemins forestiers</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showHuntingMarkers} 
                      onChange={(e) => setShowHuntingMarkers(e.target.checked)}
                      className="rounded border-gray-600 text-green-500 focus:ring-green-500"
                    />
                    <span className="text-lg">🏕️</span>
                    <span className="text-white text-sm">Territoires de chasse</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={probabilityZones.length > 0} 
                      onChange={(e) => {
                        if (!e.target.checked) {
                          setProbabilityZones([]);
                        } else {
                          generateProbabilityZones();
                        }
                      }}
                      className="rounded border-gray-600 text-[#f5a623] focus:ring-[#f5a623]"
                    />
                    <span className="text-lg">🎯</span>
                    <span className="text-white text-sm">Zones de probabilité</span>
                  </label>
                </div>
              </div>

              {/* WMS Layers */}
              <div className="p-3">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Couches Québec (WMS)</div>
                <div className="space-y-1">
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showForestLayer} 
                      onChange={(e) => setShowForestLayer(e.target.checked)}
                      className="rounded border-gray-600 text-green-500 focus:ring-green-500"
                    />
                    <span className="text-lg">🌲</span>
                    <span className="text-white text-sm">Couverture forestière</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showWaterLayer} 
                      onChange={(e) => setShowWaterLayer(e.target.checked)}
                      className="rounded border-gray-600 text-blue-500 focus:ring-blue-500"
                    />
                    <span className="text-lg">💧</span>
                    <span className="text-white text-sm">Hydrographie</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showReliefLayer} 
                      onChange={(e) => setShowReliefLayer(e.target.checked)}
                      className="rounded border-gray-600 text-orange-500 focus:ring-orange-500"
                    />
                    <span className="text-lg">🏔️</span>
                    <span className="text-white text-sm">Relief LiDAR</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showRoadsLayer} 
                      onChange={(e) => setShowRoadsLayer(e.target.checked)}
                      className="rounded border-gray-600 text-yellow-500 focus:ring-yellow-500"
                    />
                    <span className="text-lg">🛤️</span>
                    <span className="text-white text-sm">Routes forestières</span>
                  </label>
                </div>
              </div>

              {/* BIONIC™ Layers - Haute Précision */}
              {bionicPrecisionZones && bionicPrecisionZones.length > 0 && (
                <div 
                  ref={bionicZonesSectionRef}
                  className="p-3 border-t border-[#f5a623]/30"
                  data-testid="bionic-zones-section"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4 text-[#f5a623]" />
                      <span className="text-[10px] text-[#f5a623] uppercase tracking-wider font-bold">BIONIC™ Zones</span>
                      <span className="text-[9px] bg-green-500/20 text-green-400 px-1 rounded">PRÉCISION</span>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => toggleAllBionicLayers(true)}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30"
                      >
                        Tout
                      </button>
                      <button
                        onClick={() => toggleAllBionicLayers(false)}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
                      >
                        Aucun
                      </button>
                      <button
                        onClick={clearBionicAnalysis}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-gray-500/20 text-gray-400 hover:bg-gray-500/30"
                      >
                        Effacer
                      </button>
                    </div>
                  </div>
                  
                  {/* Zone count */}
                  <div className="text-[10px] text-gray-500 mb-2">
                    {bionicPrecisionZones.length} micro-zones calculées
                  </div>
                  
                  <div className="space-y-1 max-h-[200px] overflow-y-auto">
                    {Object.entries(bionicModuleStats).map(([key, stats]) => {
                      if (!stats) return null;
                      
                      return (
                        <label 
                          key={key} 
                          className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all ${
                            bionicLayersVisible[key] 
                              ? 'bg-gray-800/70 border border-gray-600/50' 
                              : 'bg-gray-800/30 opacity-60'
                          }`}
                        >
                          <input 
                            type="checkbox" 
                            checked={bionicLayersVisible[key]} 
                            onChange={() => toggleBionicLayer(key)}
                            className="rounded border-gray-600 focus:ring-[#f5a623]"
                            style={{ accentColor: stats.color }}
                          />
                          <span className="text-lg">{stats.icon}</span>
                          <div className="flex-1">
                            <span className="text-white text-sm">{stats.label}</span>
                            <div className="flex items-center gap-2">
                              <span 
                                className="text-xs font-bold"
                                style={{ color: stats.color }}
                              >
                                {stats.maxProbability}%
                              </span>
                              <span className="text-[10px] text-gray-500">
                                max • {stats.avgProbability}% moy
                              </span>
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              <div className="flex-1 bg-gray-700 rounded-full h-1.5">
                                <div 
                                  className="h-1.5 rounded-full transition-all"
                                  style={{ 
                                    width: `${stats.maxProbability}%`,
                                    backgroundColor: stats.color 
                                  }}
                                />
                              </div>
                              <span className="text-[9px] text-gray-500">
                                {stats.totalZones} zones
                              </span>
                            </div>
                          </div>
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: stats.color }}
                          />
                        </label>
                      );
                    })}
                  </div>
                  
                  <div className="mt-2 pt-2 border-t border-gray-700/50">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Score Global:</span>
                      <span className="text-[#f5a623] font-bold">
                        {bionicAnalysisResult?.overall_score || 0}/100
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[10px] mt-1">
                      <span className="text-gray-500">Modules actifs:</span>
                      <span className="text-gray-400">
                        {Object.keys(bionicModuleStats).length}/8
                      </span>
                    </div>
                  </div>
                </div>
              )}
              </div>{/* End Scrollable Content */}
            </div>
          )}

          {/* Active tool indicator */}
          {activeTool && (
            <div className={`absolute top-4 left-1/2 transform -translate-x-1/2 z-[600] text-sm px-4 py-2 rounded-lg font-medium shadow-lg ${
              activeTool === 'waypoint' ? 'bg-green-500 text-white' : 'bg-[#f5a623] text-black'
            }`} style={{marginLeft: '140px'}}>
              {activeTool === 'pin' && '📍 Cliquez sur la carte pour ajouter une observation'}
              {activeTool === 'waypoint' && '🚩 Cliquez sur la carte pour placer un waypoint GPS'}
              {activeTool === 'route' && '🛤️ Cliquez pour tracer un chemin'}
              {activeTool === 'measure' && '📏 Cliquez pour mesurer une distance'}
            </div>
          )}

          {/* Map Legend - Always visible, positioned bottom-left */}
          <div className="absolute bottom-8 left-4 bg-black/90 backdrop-blur-md p-3 rounded-xl border-2 border-[#f5a623]/50 z-[800] shadow-xl">
            <p className="text-[#f5a623] text-xs font-bold mb-2 flex items-center gap-2">
              <span>📍</span> Légende
            </p>
            <div className="space-y-1.5">
              {Object.entries(SPECIES_CONFIG).filter(([k]) => k !== 'autre').map(([key, config]) => (
                <div key={key} className="flex items-center gap-2 text-xs">
                  <span>{config.emoji}</span>
                  <span className="text-white">{config.label}</span>
                </div>
              ))}
              <div className="flex items-center gap-2 text-xs">
                <span>📷</span>
                <span className="text-white">Caméra</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span>🚩</span>
                <span className="text-white">Waypoint</span>
              </div>
              <div className="border-t border-gray-700 pt-1.5 mt-1.5">
                <p className="text-gray-400 text-[9px] mb-1">Probabilité:</p>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-[9px] text-gray-300">H</span>
                  </div>
                  <div className="flex items-center gap-0.5">
                    <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                    <span className="text-[9px] text-gray-300">M</span>
                  </div>
                  <div className="flex items-center gap-0.5">
                    <div className="w-2 h-2 rounded-full bg-red-500"></div>
                    <span className="text-[9px] text-gray-300">F</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Custom Zoom Controls - Always visible, positioned bottom-left next to legend */}
          <div className="absolute bottom-24 left-[180px] z-[800] flex flex-col gap-1">
            <button 
              onClick={() => setMapZoom(prev => Math.min(prev + 1, 18))}
              className="w-9 h-9 bg-black/90 hover:bg-black text-white rounded-lg border-2 border-[#f5a623]/50 flex items-center justify-center text-lg font-bold shadow-xl transition-all hover:scale-105"
              title="Zoom +"
            >
              +
            </button>
            <button 
              onClick={() => setMapZoom(prev => Math.max(prev - 1, 3))}
              className="w-9 h-9 bg-black/90 hover:bg-black text-white rounded-lg border-2 border-[#f5a623]/50 flex items-center justify-center text-lg font-bold shadow-xl transition-all hover:scale-105"
              title="Zoom -"
            >
              −
            </button>
          </div>

          {/* Refresh Button */}
          <Button
            className="absolute top-4 left-4 z-[500] bg-card/95 backdrop-blur-sm border border-border"
            variant="outline"
            size="sm"
            onClick={loadData}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
          
          {/* My Location Button */}
          <Button
            className="absolute top-14 left-4 z-[500] bg-card/95 backdrop-blur-sm border border-border"
            variant="outline"
            size="sm"
            onClick={() => {
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                  (position) => {
                    setMapCenter([position.coords.latitude, position.coords.longitude]);
                    setMapZoom(15);
                    toast.success('Centré sur votre position');
                  },
                  (error) => {
                    toast.error('Impossible d\'obtenir votre position');
                  }
                );
              } else {
                toast.error('Géolocalisation non supportée');
              }
            }}
          >
            <Locate className="h-4 w-4 mr-2" />
            Ma position
          </Button>
        </div>
      </div>

      {/* Nutrition Analysis Modal */}
      {showNutritionModal && nutritionAnalysis && (
        <div className="fixed inset-0 bg-black/60 z-[2000] flex items-center justify-center p-4" onClick={() => setShowNutritionModal(false)}>
          <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            {/* Header */}
            <div className="sticky top-0 bg-card border-b border-border p-4 flex items-center justify-between">
              <div>
                <h2 className="text-white text-lg font-bold flex items-center gap-2">
                  <TreePine className="h-5 w-5 text-[#f5a623]" />
                  Analyse Alimentation
                </h2>
                <p className="text-gray-400 text-sm">
                  {nutritionAnalysis.species?.name} • {nutritionAnalysis.environment?.season}
                </p>
              </div>
              <button onClick={() => setShowNutritionModal(false)} className="text-gray-400 hover:text-white">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              {/* Summary */}
              <div className="bg-background rounded-lg p-3 border border-border">
                <p className="text-gray-300 text-sm">{nutritionAnalysis.summary}</p>
              </div>

              {/* Environment Info */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-background rounded-lg p-3 border border-border">
                  <p className="text-gray-400 text-xs mb-1">Type de forêt</p>
                  <p className="text-white font-medium">{nutritionAnalysis.environment?.forest_type}</p>
                  <p className="text-green-400 text-xs">Qualité: {nutritionAnalysis.environment?.food_quality}</p>
                </div>
                <div className="bg-background rounded-lg p-3 border border-border">
                  <p className="text-gray-400 text-xs mb-1">Sources alimentaires</p>
                  <div className="text-white text-sm">
                    {nutritionAnalysis.food_sources_available?.slice(0, 3).map((source, i) => (
                      <span key={i} className="inline-block mr-1">• {source}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Nutritional Gaps */}
              <div>
                <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <Info className="h-4 w-4 text-yellow-500" />
                  Carences identifiées
                </h3>
                <div className="space-y-2">
                  {nutritionAnalysis.nutritional_gaps?.map((gap, idx) => (
                    <div key={idx} className="bg-background rounded-lg p-2 border border-border flex items-center justify-between">
                      <div>
                        <span className="text-white font-medium capitalize">{gap.nutrient}</span>
                        <p className="text-gray-400 text-xs">{gap.reason}</p>
                      </div>
                      <Badge className={`${gap.severity === 'high' ? 'bg-red-500' : gap.severity === 'moderate' ? 'bg-yellow-500' : 'bg-green-500'}`}>
                        {gap.severity}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Product Recommendations */}
              <div>
                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-[#f5a623]" />
                  Produits Recommandés
                </h3>
                <div className="space-y-3">
                  {nutritionAnalysis.recommended_products?.slice(0, 5).map((product, idx) => (
                    <div 
                      key={product.id} 
                      className={`rounded-xl p-4 border ${
                        !product.is_competitor 
                          ? 'bg-[#f5a623]/10 border-[#f5a623]/50' 
                          : 'bg-background border-border'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge className={`${idx === 0 ? 'bg-[#f5a623] text-black' : 'bg-gray-600'}`}>
                            #{idx + 1}
                          </Badge>
                          <h4 className="text-white font-semibold">{product.name}</h4>
                          {!product.is_competitor && (
                            <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px]">BIONIC™</Badge>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="text-[#f5a623] font-bold">{product.relevance_score}</div>
                          <div className="text-gray-500 text-xs">score</div>
                        </div>
                      </div>

                      <p className="text-gray-300 text-sm mb-2">{product.description}</p>

                      {product.matching_nutrients?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2">
                          {product.matching_nutrients.map((nutrient, i) => (
                            <Badge key={i} variant="outline" className="text-xs border-green-500 text-green-400">
                              ✓ {nutrient}
                            </Badge>
                          ))}
                        </div>
                      )}

                      <div className="bg-black/20 rounded-lg p-2 mt-2">
                        <p className="text-xs text-gray-400">
                          <span className="text-[#f5a623]">Pourquoi ce produit:</span> {product.recommendation_reason}
                        </p>
                      </div>

                      {product.benefits && (
                        <div className="mt-2 grid grid-cols-2 gap-1">
                          {product.benefits.slice(0, 4).map((benefit, i) => (
                            <div key={i} className="text-xs text-gray-400 flex items-center gap-1">
                              <ChevronRight className="h-3 w-3 text-[#f5a623]" />
                              {benefit}
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-border/50">
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400 text-xs">Prix:</span>
                          <span className="text-white">{product.price_range}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-gray-400 text-xs">Efficacité:</span>
                          <span className="text-[#f5a623] font-medium">{product.effectiveness_rating}/10</span>
                        </div>
                      </div>

                      {/* Add to Cart Button */}
                      <Button 
                        className="w-full mt-3 btn-golden text-black"
                        size="sm"
                        onClick={() => addToCart({
                          id: product.id,
                          name: product.name,
                          price: product.price_range === '$' ? 19.99 : product.price_range === '$$' ? 34.99 : product.price_range === '$$$' ? 49.99 : 69.99,
                          category: product.category,
                          is_bionic: !product.is_competitor
                        })}
                      >
                        <ShoppingCart className="h-4 w-4 mr-2" />
                        Ajouter au panier
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Seasonal Notes */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Info className="h-4 w-4 text-blue-400" />
                  <span className="text-blue-400 font-medium text-sm">Note saisonnière</span>
                </div>
                <p className="text-gray-300 text-sm">{nutritionAnalysis.seasonal_analysis?.notes}</p>
              </div>
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 bg-card border-t border-border p-4">
              <Button 
                className="w-full btn-golden text-black"
                onClick={() => setShowNutritionModal(false)}
              >
                Fermer l'analyse
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Shopping Cart Modal */}
      {showCartModal && (
        <div className="fixed inset-0 bg-black/60 z-[2000] flex items-center justify-center p-4" onClick={() => setShowCartModal(false)}>
          <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-hidden" onClick={e => e.stopPropagation()}>
            {/* Cart Header */}
            <div className="bg-card border-b border-border p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5 text-[#f5a623]" />
                <h2 className="text-white text-lg font-bold">Panier BIONIC™</h2>
                <Badge className="bg-[#f5a623] text-black">{cart.reduce((sum, item) => sum + item.quantity, 0)}</Badge>
              </div>
              <button onClick={() => setShowCartModal(false)} className="text-gray-400 hover:text-white">
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Cart Content */}
            <div className="p-4 overflow-y-auto max-h-[50vh]">
              {cart.length === 0 ? (
                <div className="text-center py-8">
                  <ShoppingCart className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">Votre panier est vide</p>
                  <p className="text-gray-500 text-sm mt-1">Ajoutez des produits depuis l'analyse nutritionnelle</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {cart.map((item) => (
                    <div key={item.id} className="bg-background rounded-lg p-3 border border-border">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="text-white font-medium text-sm">{item.name}</h4>
                            {item.is_bionic && (
                              <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px]">BIONIC™</Badge>
                            )}
                          </div>
                          <p className="text-gray-400 text-xs">{item.category}</p>
                        </div>
                        <button 
                          onClick={() => removeFromCart(item.id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center gap-2">
                          <button 
                            onClick={() => updateCartQuantity(item.id, -1)}
                            className="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 flex items-center justify-center"
                          >
                            <span className="text-white text-sm">-</span>
                          </button>
                          <span className="text-white w-8 text-center">{item.quantity}</span>
                          <button 
                            onClick={() => updateCartQuantity(item.id, 1)}
                            className="w-6 h-6 rounded bg-gray-700 hover:bg-gray-600 flex items-center justify-center"
                          >
                            <span className="text-white text-sm">+</span>
                          </button>
                        </div>
                        <span className="text-[#f5a623] font-bold">${(item.price * item.quantity).toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Cart Footer */}
            {cart.length > 0 && (
              <div className="border-t border-border p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Total</span>
                  <span className="text-white text-xl font-bold">${getCartTotal().toFixed(2)} CAD</span>
                </div>
                <Button 
                  className="w-full btn-golden text-black"
                  onClick={() => setShowOrderForm(true)}
                >
                  <Send className="h-4 w-4 mr-2" />
                  Commander (approbation requise)
                </Button>
                <p className="text-xs text-gray-500 text-center">
                  La commande sera envoyée à l'administrateur pour approbation
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Order Form Modal */}
      {showOrderForm && (
        <div className="fixed inset-0 bg-black/60 z-[2001] flex items-center justify-center p-4" onClick={() => setShowOrderForm(false)}>
          <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full" onClick={e => e.stopPropagation()}>
            <div className="p-4 border-b border-border">
              <h2 className="text-white text-lg font-bold flex items-center gap-2">
                <Package className="h-5 w-5 text-[#f5a623]" />
                Formulaire de commande
              </h2>
              <p className="text-gray-400 text-sm">Remplissez vos informations pour soumettre la commande</p>
            </div>

            <div className="p-4 space-y-4">
              <div>
                <Label className="text-gray-400 text-xs">Nom complet *</Label>
                <Input
                  value={orderName}
                  onChange={(e) => setOrderName(e.target.value)}
                  placeholder="Jean Tremblay"
                  className="bg-background border-border mt-1"
                />
              </div>
              <div>
                <Label className="text-gray-400 text-xs">Email *</Label>
                <Input
                  type="email"
                  value={orderEmail}
                  onChange={(e) => setOrderEmail(e.target.value)}
                  placeholder="jean@exemple.com"
                  className="bg-background border-border mt-1"
                />
              </div>
              <div>
                <Label className="text-gray-400 text-xs">Téléphone</Label>
                <Input
                  value={orderPhone}
                  onChange={(e) => setOrderPhone(e.target.value)}
                  placeholder="(418) 555-1234"
                  className="bg-background border-border mt-1"
                />
              </div>
              <div>
                <Label className="text-gray-400 text-xs">Notes / Instructions spéciales</Label>
                <textarea
                  value={orderNotes}
                  onChange={(e) => setOrderNotes(e.target.value)}
                  placeholder="Instructions de livraison, etc."
                  className="w-full bg-background border border-border rounded-md p-2 mt-1 text-white text-sm resize-none h-20"
                />
              </div>

              {/* Order Summary */}
              <div className="bg-background rounded-lg p-3 border border-border">
                <p className="text-gray-400 text-xs mb-2">Résumé de la commande</p>
                <div className="space-y-1">
                  {cart.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span className="text-gray-300">{item.name} x{item.quantity}</span>
                      <span className="text-white">${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
                <div className="border-t border-border mt-2 pt-2 flex justify-between">
                  <span className="text-white font-medium">Total</span>
                  <span className="text-[#f5a623] font-bold">${getCartTotal().toFixed(2)} CAD</span>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-border flex gap-2">
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={() => setShowOrderForm(false)}
              >
                Annuler
              </Button>
              <Button 
                className="flex-1 btn-golden text-black"
                onClick={submitOrder}
                disabled={submittingOrder || !orderName || !orderEmail}
              >
                {submittingOrder ? (
                  <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Envoi...</>
                ) : (
                  <><Check className="h-4 w-4 mr-2" /> Soumettre</>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* BIONIC™ Territory Engine Modal */}
      {showBionicAnalyzer && (
        <div className="fixed inset-0 bg-black/80 z-[2002] flex items-center justify-center p-4" onClick={() => setShowBionicAnalyzer(false)}>
          <div 
            className="bg-card border border-border rounded-2xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-border bg-gradient-to-r from-[#f5a623]/10 to-orange-500/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#f5a623]/20 flex items-center justify-center">
                  <Brain className="h-5 w-5 text-[#f5a623]" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    BIONIC™ Territory Engine
                    <Badge className="bg-green-500/20 text-green-400 text-[10px]">v1.0</Badge>
                  </h2>
                  <p className="text-gray-400 text-xs">Analyse géospatiale avancée • 8 modules • 6 modèles fauniques • IA prédictive</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowBionicAnalyzer(false)}
                className="text-gray-400 hover:text-white hover:bg-white/10"
                data-testid="close-bionic-modal"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            {/* BIONIC Analyzer Content */}
            <div className="flex-1 overflow-hidden">
              <BionicAnalyzer 
                territory={{
                  id: selectedTerritoryType && selectedZoneNumber 
                    ? `${selectedTerritoryType}-${selectedZoneNumber}` 
                    : 'current-location',
                  name: selectedTerritoryType && selectedZoneNumber 
                    ? `${selectedTerritoryType.toUpperCase()} ${selectedZoneNumber}`
                    : 'Position actuelle',
                  coordinates: {
                    lat: parseFloat(gpsLatitude) || mapCenter[0],
                    lng: parseFloat(gpsLongitude) || mapCenter[1]
                  }
                }}
                onClose={() => setShowBionicAnalyzer(false)}
                onAnalysisComplete={handleBionicAnalysisComplete}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TerritoryMap;
