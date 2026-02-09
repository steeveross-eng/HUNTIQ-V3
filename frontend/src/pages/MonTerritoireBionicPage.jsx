/**
 * MonTerritoireBionicPage - Page dédiée Mon Territoire BIONIC™
 * Avec sous-onglets : Carte BIONIC, Waypoints actifs, Lieux enregistrés
 */

import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, WMSTileLayer, Marker, Popup, useMap, useMapEvents, Circle, Tooltip, Polygon } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import { 
  Brain, Map, Crosshair, Wind, Thermometer, Droplets, TrendingUp, 
  ChevronRight, Layers, Activity, Target, Navigation, Settings,
  Sun, Moon, ArrowRight, Zap, Eye, EyeOff, RefreshCw, MapPin,
  Compass, TreePine, Mountain, Waves, Home, Heart, Footprints,
  AlertTriangle, Clock, Calendar, Info, ChevronDown, ChevronUp,
  Play, Pause, BarChart3, PieChart, ArrowLeft, Plus, Trash2,
  Edit2, Save, X, LocateFixed, Building, Trees, Tent, Star,
  BookMarked, List, MapPinned, User, Navigation2, Cloud, Wifi, WifiOff,
  Share2, Users, Bell, Lock, Unlock, Leaf, CheckCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogClose, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import useBionicLayers from '@/hooks/useBionicLayers';
import useBionicWeather from '@/hooks/useBionicWeather';
import useBionicScoring from '@/hooks/useBionicScoring';
import { useUserData } from '@/hooks/useUserData';
import { useNotifications, useHuntingGroups } from '@/hooks/useSharing';
import { ShareWaypointDialog, CreateGroupDialog, NotificationBell } from '@/components/territoire/ShareComponents';
import { GroupDashboard } from '@/components/territoire/GroupDashboard';
import BionicMicroZones, { generateMicroZones, generateMicroZonesForBounds, BIONIC_MODULES } from '@/components/territoire/BionicMicroZones';
import { useZoneFavorites, AddToFavoritesButton, AlertsPanel, FavoritesList } from '@/components/territoire/ZoneFavorites';
import EcoforestryLayers, { 
  EcoforestryLayerControl, 
  EcoMapFallbackNotification,
  useEcoMapFallback,
  BASE_MAPS, 
  ECOFORESTRY_LAYERS,
  EcoMapStatus 
} from '@/components/territoire/EcoforestryLayers';
import { 
  BIONIC_LAYERS, 
  SCORE_CATEGORIES,
  getScoresForWaypoint, 
  adaptWaypointData,
  getWindDirectionText,
  getWeatherDescription
} from '@/core/bionic';
import L from 'leaflet';
import { toast } from 'sonner';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const createCustomIcon = (color, iconType = 'default') => {
  const iconHtml = `
    <div style="
      background-color: ${color};
      width: 32px;
      height: 32px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      border: 3px solid white;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <div style="transform: rotate(45deg); color: white; font-size: 14px;">
        ${iconType === 'user' ? '👤' : iconType === 'waypoint' ? '📍' : '⭐'}
      </div>
    </div>
  `;
  return L.divIcon({
    html: iconHtml,
    className: 'custom-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

// Composant pour centrer la carte
const MapController = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || 12);
    }
  }, [center, zoom, map]);
  return null;
};

// Types de lieux disponibles
const PLACE_TYPES = [
  { id: 'zec', name: 'ZEC', icon: '🏕️', color: '#22c55e' },
  { id: 'pourvoirie', name: 'Pourvoirie', icon: '🏠', color: '#3b82f6' },
  { id: 'prive', name: 'Territoire privé', icon: '🔒', color: '#f59e0b' },
  { id: 'sepaq', name: 'Réserve faunique (Sépaq)', icon: '🦌', color: '#8b5cf6' },
  { id: 'affut', name: 'Affût / Cache', icon: '🎯', color: '#ef4444' },
  { id: 'saline', name: 'Saline', icon: '🧂', color: '#06b6d4' },
  { id: 'observation', name: 'Point d\'observation', icon: '👁️', color: '#ec4899' },
  { id: 'stationnement', name: 'Stationnement', icon: '🅿️', color: '#6b7280' },
  { id: 'camp', name: 'Camp de chasse', icon: '🏕️', color: '#84cc16' },
  { id: 'autre', name: 'Autre lieu', icon: '📌', color: '#a855f7' },
];

// ============================================
// SYSTÈME DE ZONES ADAPTATIVES AU ZOOM
// Limite max: 1 km² par zone
// ============================================

// Constantes pour le calcul des zones
const ZONE_CONFIG = {
  MAX_AREA_KM2: 1.0,           // Superficie max par zone en km²
  MAX_RADIUS_KM: 0.564,        // Rayon max pour 1 km² (√(1/π))
  MIN_RADIUS_KM: 0.05,         // Rayon min (50m)
  EARTH_RADIUS_KM: 6371,       // Rayon terrestre
};

// Convertit le niveau de zoom en rayon de zone (en km)
const getZoneRadiusForZoom = (zoom) => {
  // Plus le zoom est élevé, plus les zones sont petites et détaillées
  // Zoom 8 = grandes zones (~1km), Zoom 18 = petites zones (~50m)
  const zoomFactor = Math.pow(2, 15 - zoom);
  const radius = Math.min(
    ZONE_CONFIG.MAX_RADIUS_KM,
    Math.max(ZONE_CONFIG.MIN_RADIUS_KM, 0.5 * zoomFactor)
  );
  return radius;
};

// Convertit km en degrés de latitude
const kmToLatDegrees = (km) => km / 111.32;

// Convertit km en degrés de longitude (dépend de la latitude)
const kmToLngDegrees = (km, lat) => km / (111.32 * Math.cos(lat * Math.PI / 180));

// Calcule le nombre de zones selon le zoom et l'étendue visible
const getZoneDensityForZoom = (zoom) => {
  // Plus de zones quand on zoome (plus de détails)
  if (zoom >= 16) return { gridSize: 12, subdivisions: 3 };
  if (zoom >= 14) return { gridSize: 10, subdivisions: 2 };
  if (zoom >= 12) return { gridSize: 8, subdivisions: 1 };
  if (zoom >= 10) return { gridSize: 6, subdivisions: 1 };
  return { gridSize: 4, subdivisions: 1 };
};

// Génère un hexagone autour d'un point central
const generateHexagon = (centerLat, centerLng, radiusKm) => {
  const points = [];
  const latRadius = kmToLatDegrees(radiusKm);
  const lngRadius = kmToLngDegrees(radiusKm, centerLat);
  
  for (let i = 0; i < 6; i++) {
    const angle = (60 * i - 30) * Math.PI / 180;
    points.push([
      centerLat + latRadius * Math.sin(angle) * 0.92,
      centerLng + lngRadius * Math.cos(angle) * 0.92
    ]);
  }
  return points;
};

// Calcule un score BIONIC simulé basé sur la position et le type de couche
const calculateZoneScore = (lat, lng, layerType, baseScore = null) => {
  // Utilise une fonction de bruit simplifié pour créer des variations naturelles
  const noise = (x, y) => {
    const n = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453;
    return n - Math.floor(n);
  };
  
  // Score de base avec variation spatiale
  const spatialVariation = noise(lat * 100, lng * 100);
  
  // Différents facteurs selon le type de couche
  const layerFactors = {
    habitats: { base: 70, variance: 25, threshold: 0.45 },
    rut: { base: 65, variance: 30, threshold: 0.50 },
    affuts: { base: 75, variance: 20, threshold: 0.55 },
    corridors: { base: 60, variance: 30, threshold: 0.40 },
    alimentation: { base: 70, variance: 25, threshold: 0.45 },
    repos: { base: 65, variance: 25, threshold: 0.50 },
    salines: { base: 55, variance: 35, threshold: 0.60 },
  };
  
  const factor = layerFactors[layerType] || { base: 60, variance: 25, threshold: 0.50 };
  
  // Seulement générer des zones au-dessus d'un certain seuil
  if (spatialVariation < factor.threshold) return null;
  
  const score = Math.round(
    factor.base + (spatialVariation - factor.threshold) * factor.variance * 2
  );
  
  return Math.min(100, Math.max(0, score));
};

// Types de couches avec configuration (utilisant les modules BIONIC)
const LAYER_TYPES = Object.entries(BIONIC_MODULES).map(([id, config], index) => ({
  id,
  color: config.color,
  label: config.label,
  icon: config.icon,
  priority: index + 1
}));

/**
 * Génère des zones BIONIC adaptatives au zoom
 * @param {number} centerLat - Latitude du centre
 * @param {number} centerLng - Longitude du centre
 * @param {number} zoom - Niveau de zoom actuel
 * @param {Object} layersVisible - État de visibilité des couches
 * @param {Object} targetWaypoint - Waypoint cible optionnel
 */
const generateAdaptiveBionicZones = (centerLat, centerLng, zoom, layersVisible, targetWaypoint = null) => {
  const zones = [];
  
  // Obtenir la configuration pour ce niveau de zoom
  const radiusKm = getZoneRadiusForZoom(zoom);
  const { gridSize, subdivisions } = getZoneDensityForZoom(zoom);
  
  // Centre effectif (waypoint si sélectionné, sinon centre de carte)
  const effectiveCenter = targetWaypoint 
    ? { lat: targetWaypoint.lat, lng: targetWaypoint.lng }
    : { lat: centerLat, lng: centerLng };
  
  // Calculer l'étendue de la grille basée sur le zoom
  const gridExtentKm = radiusKm * gridSize * 2;
  const latStep = kmToLatDegrees(radiusKm * 1.8);
  const lngStep = kmToLngDegrees(radiusKm * 1.8, effectiveCenter.lat);
  
  // Générer une grille hexagonale
  const halfGrid = Math.floor(gridSize / 2);
  let zoneIndex = 0;
  
  for (let row = -halfGrid; row <= halfGrid; row++) {
    for (let col = -halfGrid; col <= halfGrid; col++) {
      // Offset hexagonal (décalage des lignes impaires)
      const hexOffset = (row % 2) * (lngStep / 2);
      
      const zoneLat = effectiveCenter.lat + row * latStep * 0.866; // cos(30°)
      const zoneLng = effectiveCenter.lng + col * lngStep + hexOffset;
      
      // Distance du centre pour limiter la zone circulaire
      const distFromCenter = Math.sqrt(
        Math.pow((zoneLat - effectiveCenter.lat) / latStep, 2) +
        Math.pow((zoneLng - effectiveCenter.lng) / lngStep, 2)
      );
      
      if (distFromCenter > halfGrid) continue;
      
      // Générer les zones pour chaque couche visible
      LAYER_TYPES.forEach((layerType) => {
        if (!layersVisible[layerType.id]) return;
        
        // Calculer le score pour cette position et ce type
        const score = calculateZoneScore(zoneLat, zoneLng, layerType.id);
        
        // Ignorer si score trop bas ou null
        if (score === null || score < 55) return;
        
        // Générer l'hexagone
        const hexPoints = generateHexagon(zoneLat, zoneLng, radiusKm);
        
        // Calculer la superficie réelle (vérification)
        const areaKm2 = Math.PI * radiusKm * radiusKm;
        
        zones.push({
          id: `${layerType.id}-${zoneIndex}-${row}-${col}`,
          layerId: layerType.id,
          positions: hexPoints,
          color: layerType.color,
          score,
          label: layerType.label,
          center: [zoneLat, zoneLng],
          radiusKm,
          areaKm2: Math.min(areaKm2, ZONE_CONFIG.MAX_AREA_KM2),
          zoom,
          priority: layerType.priority
        });
        
        zoneIndex++;
      });
    }
  }
  
  // Trier par score décroissant pour affichage correct (z-index)
  zones.sort((a, b) => b.score - a.score);
  
  // Limiter le nombre total de zones pour les performances
  const maxZones = zoom >= 14 ? 150 : zoom >= 12 ? 100 : 60;
  return zones.slice(0, maxZones);
};

/**
 * Génère des zones autour d'un waypoint spécifique
 */
const generateWaypointZones = (waypoint, zoom, layersVisible) => {
  return generateAdaptiveBionicZones(
    waypoint.lat,
    waypoint.lng,
    Math.max(zoom, 13), // Au moins zoom 13 pour les waypoints
    layersVisible,
    waypoint
  );
};

/**
 * Génère des zones BIONIC qui couvrent TOUTE l'étendue visible de la carte
 * @param {Object} bounds - Limites de la carte { north, south, east, west }
 * @param {number} zoom - Niveau de zoom actuel
 * @param {Object} layersVisible - Couches actives
 */
const generateAdaptiveBionicZonesForBounds = (bounds, zoom, layersVisible) => {
  const zones = [];
  
  if (!bounds) return zones;
  
  // Obtenir la configuration pour ce niveau de zoom
  const radiusKm = getZoneRadiusForZoom(zoom);
  
  // Calculer l'espacement de la grille en degrés
  const latStep = kmToLatDegrees(radiusKm * 1.8);
  const centerLat = (bounds.north + bounds.south) / 2;
  const lngStep = kmToLngDegrees(radiusKm * 1.8, centerLat);
  
  // Calculer le nombre de cellules nécessaires pour couvrir la zone visible
  const latRange = bounds.north - bounds.south;
  const lngRange = bounds.east - bounds.west;
  
  const numRows = Math.ceil(latRange / latStep) + 2; // +2 pour marge
  const numCols = Math.ceil(lngRange / lngStep) + 2;
  
  // Limiter pour les performances
  const maxCells = zoom >= 14 ? 20 : zoom >= 12 ? 15 : 10;
  const effectiveRows = Math.min(numRows, maxCells);
  const effectiveCols = Math.min(numCols, maxCells);
  
  let zoneIndex = 0;
  
  // Parcourir toute la zone visible
  for (let row = 0; row < effectiveRows; row++) {
    for (let col = 0; col < effectiveCols; col++) {
      // Offset hexagonal (décalage des lignes impaires)
      const hexOffset = (row % 2) * (lngStep / 2);
      
      // Position dans la zone visible
      const zoneLat = bounds.south + (row + 0.5) * (latRange / effectiveRows);
      const zoneLng = bounds.west + (col + 0.5) * (lngRange / effectiveCols) + hexOffset;
      
      // Vérifier que le point est dans les limites
      if (zoneLat < bounds.south || zoneLat > bounds.north) continue;
      if (zoneLng < bounds.west || zoneLng > bounds.east) continue;
      
      // Générer les zones pour chaque couche visible
      LAYER_TYPES.forEach((layerType) => {
        if (!layersVisible[layerType.id]) return;
        
        // Calculer le score pour cette position et ce type
        const score = calculateZoneScore(zoneLat, zoneLng, layerType.id);
        
        // Ignorer si score trop bas ou null
        if (score === null || score < 50) return;
        
        // Générer l'hexagone
        const hexPoints = generateHexagon(zoneLat, zoneLng, radiusKm);
        
        // Calculer la superficie réelle
        const areaKm2 = Math.PI * radiusKm * radiusKm;
        
        zones.push({
          id: `bounds-${layerType.id}-${zoneIndex}-${row}-${col}`,
          layerId: layerType.id,
          positions: hexPoints,
          color: layerType.color,
          score,
          label: layerType.label,
          center: [zoneLat, zoneLng],
          radiusKm,
          areaKm2: Math.min(areaKm2, ZONE_CONFIG.MAX_AREA_KM2),
          zoom,
          priority: layerType.priority
        });
        
        zoneIndex++;
      });
    }
  }
  
  // Trier par score décroissant
  zones.sort((a, b) => b.score - a.score);
  
  // Limiter le nombre total de zones pour les performances
  const maxZones = zoom >= 14 ? 200 : zoom >= 12 ? 150 : 100;
  return zones.slice(0, maxZones);
};

// Composant pour détecter les changements de zoom et position
const ZoomHandler = ({ onZoomChange, onMapMove, onBoundsChange }) => {
  const map = useMap();
  
  useEffect(() => {
    const handleZoomEnd = () => {
      const center = map.getCenter();
      const bounds = map.getBounds();
      onZoomChange(map.getZoom());
      if (onMapMove) {
        onMapMove({ lat: center.lat, lng: center.lng });
      }
      if (onBoundsChange) {
        onBoundsChange({
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest()
        });
      }
    };
    
    const handleMoveEnd = () => {
      const center = map.getCenter();
      const bounds = map.getBounds();
      if (onMapMove) {
        onMapMove({ lat: center.lat, lng: center.lng });
      }
      if (onBoundsChange) {
        onBoundsChange({
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest()
        });
      }
    };
    
    map.on('zoomend', handleZoomEnd);
    map.on('moveend', handleMoveEnd);
    
    // Initial call
    handleZoomEnd();
    
    return () => {
      map.off('zoomend', handleZoomEnd);
      map.off('moveend', handleMoveEnd);
    };
  }, [map, onZoomChange, onMapMove, onBoundsChange]);
  
  return null;
};

// Composant pour capturer les clics sur la carte et créer des waypoints
// Rendu conditionnel: ce composant n'existe que quand mapClickMode est actif
const MapClickHandler = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      console.log('[MapClickHandler] Click detected at:', e.latlng.lat, e.latlng.lng);
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    }
  });
  return null;
};

const MonTerritoireBionicPage = () => {
  const navigate = useNavigate();
  
  // Onglet actif
  const [activeTab, setActiveTab] = useState('carte');
  
  // État de la carte
  const [mapCenter, setMapCenter] = useState([46.8139, -71.2080]);
  const [mapZoom, setMapZoom] = useState(12);
  const [currentZoom, setCurrentZoom] = useState(12); // Zoom actuel pour les zones adaptatives
  const [currentMapCenter, setCurrentMapCenter] = useState({ lat: 46.8139, lng: -71.2080 }); // Centre actuel
  const [currentMapBounds, setCurrentMapBounds] = useState(null); // Limites visibles de la carte
  const [selectedZone, setSelectedZone] = useState(null);
  const [selectedWaypointForZones, setSelectedWaypointForZones] = useState(null); // Waypoint cible pour les zones
  
  // Position de l'utilisateur
  const [userPosition, setUserPosition] = useState(null);
  const [watchingPosition, setWatchingPosition] = useState(false);
  const watchIdRef = useRef(null);
  
  // Récupérer l'utilisateur connecté (si disponible)
  // On utilise un userId stable basé sur localStorage ou "anonymous"
  const getUserId = useCallback(() => {
    try {
      const storedUser = localStorage.getItem('auth_user');
      if (storedUser) {
        const user = JSON.parse(storedUser);
        return user.id || user.email || 'anonymous';
      }
    } catch (e) {
      console.log('No stored user');
    }
    return 'anonymous';
  }, []);
  
  const userId = useMemo(() => getUserId(), [getUserId]);
  
  // Hook pour les waypoints et lieux avec sync backend
  const {
    waypoints,
    places: savedPlaces,
    activeWaypoints,
    stats: userDataStats,
    loading: userDataLoading,
    syncing,
    isOnline,
    addWaypoint,
    updateWaypoint,
    deleteWaypoint,
    toggleWaypointActive,
    addPlace,
    updatePlace,
    deletePlace,
    syncToBackend
  } = useUserData(userId, { autoSync: true });
  
  // Notifications
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications(userId);
  
  // Groupes de chasse
  const { allGroups: myGroups, loading: groupsLoading, refresh: refreshGroups } = useHuntingGroups(userId);
  
  // Dialog de partage
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [waypointToShare, setWaypointToShare] = useState(null);
  const [showCreateGroupDialog, setShowCreateGroupDialog] = useState(false);
  const [showNotificationsPanel, setShowNotificationsPanel] = useState(false);
  
  // Tableau de bord de groupe (tracking live + chat)
  const [showGroupDashboard, setShowGroupDashboard] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  
  // Dialog pour ajouter un lieu
  const [showAddPlaceDialog, setShowAddPlaceDialog] = useState(false);
  const [newPlace, setNewPlace] = useState({ name: '', type: 'autre', lat: '', lng: '', notes: '' });
  const [editingPlace, setEditingPlace] = useState(null);
  
  // Dialog pour ajouter un waypoint (contrôlé pour accès depuis le bouton rapide)
  const [showAddWaypointDialog, setShowAddWaypointDialog] = useState(false);
  const [newWaypoint, setNewWaypoint] = useState({ name: '', type: 'autre', lat: '', lng: '' });
  
  // Mode création de waypoint par clic sur la carte
  const [mapClickMode, setMapClickMode] = useState(false);
  
  // Panneaux
  const [showLayersPanel, setShowLayersPanel] = useState(true);
  const [showAnalysisPanel, setShowAnalysisPanel] = useState(true);
  const [liveMode, setLiveMode] = useState(false);
  
  // Mode d'affichage des zones BIONIC
  const [zoneDisplayMode, setZoneDisplayMode] = useState('micro'); // 'micro' ou 'classic'
  const [showConcentricCircles, setShowConcentricCircles] = useState(true);
  const [showCorridors, setShowCorridors] = useState(true);
  const [minPercentageFilter, setMinPercentageFilter] = useState(50);
  
  // ============================================
  // CARTE ÉCOFORESTIÈRE - État des couches
  // ============================================
  const [showEcoforestryPanel, setShowEcoforestryPanel] = useState(false);
  const [activeEcoLayers, setActiveEcoLayers] = useState({
    baseMap: 'terrain', // Fond de carte terrain (topographique HD) par défaut
    peuplements: false,
    essences: false,
    perturbations: false,
    densite: false,
    hauteur: false,
    lidar_chm: false,
    lidar_volume: false,
    lidar_st: false,
    courbes_niveau: false
  });
  const [ecoLayerOpacities, setEcoLayerOpacities] = useState({});
  
  // ============================================
  // SYSTÈME DE FALLBACK - Carte écoforestière
  // ============================================
  const isEcoMapSelected = activeEcoLayers.baseMap === 'ecoforestry';
  const {
    status: ecoMapStatus,
    activeFallback,
    retryCount,
    lastCheck,
    isAvailable: isEcoMapAvailable,
    isUnavailable: isEcoMapUnavailable,
    forceCheck: forceEcoMapCheck,
    setFallbackMap
  } = useEcoMapFallback(isEcoMapSelected);
  
  // Gestionnaire de toggle des couches écoforestières
  const handleEcoLayerToggle = useCallback((layerId, value) => {
    if (layerId === 'baseMap') {
      setActiveEcoLayers(prev => ({ ...prev, baseMap: value }));
    } else {
      setActiveEcoLayers(prev => ({ ...prev, [layerId]: !prev[layerId] }));
    }
  }, []);
  
  // Gestionnaire d'opacité des couches
  const handleEcoOpacityChange = useCallback((layerId, opacity) => {
    setEcoLayerOpacities(prev => ({ ...prev, [layerId]: opacity }));
  }, []);
  
  // Mode confidentialité (seul l'utilisateur et l'admin peuvent voir les données privées)
  const [privacyMode, setPrivacyMode] = useState(false);
  const isPrivateDataVisible = !privacyMode; // Les waypoints, recherches, annotations sont visibles
  
  // ============================================
  // EXCLUSION PERMANENTE DES ZONES AQUATIQUES
  // Service TOUJOURS ACTIF - Impossible à désactiver
  // ============================================
  const [waterExclusionStats, setWaterExclusionStats] = useState(null);
  const [filteredMicroZones, setFilteredMicroZones] = useState([]);
  const [isFilteringWater, setIsFilteringWater] = useState(false);
  
  // Import du service d'exclusion permanent
  const filterWaterZonesRef = useRef(null);
  
  useEffect(() => {
    // Charger le service d'exclusion d'eau (toujours actif)
    import('@/services/WaterExclusionService').then(module => {
      filterWaterZonesRef.current = module.filterZonesViaAPI;
      console.log('[BIONIC] Water exclusion service loaded - PERMANENT ACTIVE');
    });
  }, []);
  
  // Hooks BIONIC
  const { 
    layersVisible, 
    toggleLayer, 
    showAllLayers, 
    hideAllLayers,
    activeCount,
    allLayers
  } = useBionicLayers({ habitats: true, affuts: true, corridors: true, alimentation: true });
  
  const { 
    weather, 
    isLoading: weatherLoading,
    temperature,
    windInfo,
    thermalInfo,
    huntingScore,
    nextOptimalWindow,
    sunrise,
    sunset,
    refresh: refreshWeather
  } = useBionicWeather(mapCenter[0], mapCenter[1], { autoFetch: true, pollInterval: liveMode ? 60000 : 600000 });
  
  const { scores, calculateHybridScores, globalScore } = useBionicScoring();
  
  // Hook pour les zones favorites et alertes
  const {
    favorites,
    alerts,
    unreadAlertCount,
    loading: favoritesLoading,
    addFavorite,
    removeFavorite,
    updateAlertSettings,
    markAlertRead,
    markAllAlertsRead,
    checkOptimalConditions,
    getZoneConditions,
    refresh: refreshFavorites
  } = useZoneFavorites(userId);
  
  // Vérifier si une zone est favorite
  const isZoneFavorite = useCallback((zone) => {
    return favorites.some(f => 
      Math.abs(f.location.lat - zone.center[0]) < 0.0001 &&
      Math.abs(f.location.lng - zone.center[1]) < 0.0001 &&
      f.module_id === zone.moduleId
    );
  }, [favorites]);
  
  // Trouver l'ID du favori pour une zone
  const getFavoriteId = useCallback((zone) => {
    const fav = favorites.find(f => 
      Math.abs(f.location.lat - zone.center[0]) < 0.0001 &&
      Math.abs(f.location.lng - zone.center[1]) < 0.0001 &&
      f.module_id === zone.moduleId
    );
    return fav?.id;
  }, [favorites]);
  
  // Callback pour le changement de zoom
  const handleZoomChange = useCallback((newZoom) => {
    setCurrentZoom(newZoom);
  }, []);
  
  // Callback pour le déplacement de la carte
  const handleMapMove = useCallback((newCenter) => {
    setCurrentMapCenter(newCenter);
  }, []);
  
  // Callback pour le changement des limites visibles
  const handleBoundsChange = useCallback((newBounds) => {
    setCurrentMapBounds(newBounds);
  }, []);
  
  // ============================================
  // ZONES BIONIC - GÉNÉRÉES UNIQUEMENT AUTOUR DES WAYPOINTS ACTIFS
  // Performance optimisée: pas de zones si aucun waypoint
  // ============================================
  const bionicZonesData = useMemo(() => {
    // Si aucun waypoint actif, ne pas générer de zones
    if (!activeWaypoints || activeWaypoints.length === 0) {
      return { microZones: [], corridors: [], bufferZones: [], classicZones: [] };
    }
    
    const zoom = selectedWaypointForZones ? Math.max(currentZoom, 13) : currentZoom;
    
    // Générer des zones autour de chaque waypoint actif
    let allMicroZones = [];
    let allClassicZones = [];
    
    // Liste des waypoints à analyser (soit le sélectionné, soit tous les actifs)
    const waypointsToAnalyze = selectedWaypointForZones 
      ? [selectedWaypointForZones]
      : activeWaypoints;
    
    for (const wp of waypointsToAnalyze) {
      if (zoneDisplayMode === 'micro') {
        // Générer des micro-zones autour de ce waypoint
        const wpZones = generateMicroZones(wp.lat || wp.latitude, wp.lng || wp.longitude, zoom, layersVisible);
        allMicroZones = [...allMicroZones, ...wpZones.microZones];
      } else {
        // Mode classique - zones hexagonales autour du waypoint
        const wpZones = generateAdaptiveBionicZones(
          wp.lat || wp.latitude,
          wp.lng || wp.longitude,
          zoom,
          layersVisible,
          wp
        );
        allClassicZones = [...allClassicZones, ...wpZones];
      }
    }
    
    return { 
      microZones: allMicroZones, 
      corridors: [], 
      bufferZones: [], 
      classicZones: allClassicZones 
    };
  }, [activeWaypoints, selectedWaypointForZones, currentZoom, layersVisible, zoneDisplayMode]);
  
  // ============================================
  // FILTRAGE PERMANENT DES ZONES AQUATIQUES
  // TOUJOURS ACTIF - Appliqué automatiquement à chaque génération
  // ============================================
  useEffect(() => {
    const applyWaterExclusion = async () => {
      // EXCLUSION TOUJOURS ACTIVE - Pas de condition de désactivation
      if (!currentMapBounds) {
        setFilteredMicroZones(bionicZonesData.microZones || []);
        return;
      }
      
      const zonesToFilter = bionicZonesData.microZones || [];
      if (zonesToFilter.length === 0) {
        setFilteredMicroZones([]);
        return;
      }
      
      setIsFilteringWater(true);
      
      try {
        // Utiliser le service d'exclusion permanent
        const filterFunc = filterWaterZonesRef.current;
        if (filterFunc) {
          const { filteredZones, stats } = await filterFunc(zonesToFilter, currentMapBounds);
          setFilteredMicroZones(filteredZones);
          setWaterExclusionStats(stats);
          
          if (stats && stats.excluded > 0) {
            console.log(`[BIONIC] Exclusion eau PERMANENTE: ${stats.excluded} zones exclues sur ${stats.total}`);
          }
        } else {
          // Fallback direct si service pas encore chargé
          const { filterZonesViaAPI } = await import('@/services/WaterExclusionService');
          filterWaterZonesRef.current = filterZonesViaAPI;
          const { filteredZones, stats } = await filterZonesViaAPI(zonesToFilter, currentMapBounds);
          setFilteredMicroZones(filteredZones);
          setWaterExclusionStats(stats);
        }
      } catch (err) {
        console.error('[BIONIC] Erreur filtrage eau:', err);
        // En cas d'erreur, utiliser les zones non filtrées temporairement
        setFilteredMicroZones(zonesToFilter);
      } finally {
        setIsFilteringWater(false);
      }
    };
    
    applyWaterExclusion();
  }, [bionicZonesData.microZones, currentMapBounds]);
  
  // Extraire les données pour le rendu (TOUJOURS utiliser les zones filtrées)
  const { corridors = [], bufferZones = [], classicZones = [] } = bionicZonesData;
  const microZones = filteredMicroZones; // EXCLUSION PERMANENTE - Toujours les zones filtrées
  
  // Compter les zones visibles (pour l'affichage du badge)
  const visibleZonesCount = useMemo(() => {
    if (zoneDisplayMode === 'micro') {
      return microZones.filter(z => z.percentage >= minPercentageFilter).length;
    }
    return classicZones.length;
  }, [zoneDisplayMode, microZones, classicZones, minPercentageFilter]);
  
  // Score global (valeur stable basée sur position)
  const displayScore = useMemo(() => {
    if (globalScore) return globalScore;
    // Score déterministe basé sur la position de la carte
    const seed = (currentMapCenter.lat * 1000 + currentMapCenter.lng * 100) % 100;
    return Math.round(65 + (seed % 25));
  }, [globalScore, currentMapCenter.lat, currentMapCenter.lng]);
  
  const getScoreRating = (score) => {
    if (score >= 85) return { label: 'Exceptionnel', color: 'bg-green-500', textColor: 'text-green-400' };
    if (score >= 70) return { label: 'Excellent', color: 'bg-lime-500', textColor: 'text-lime-400' };
    if (score >= 55) return { label: 'Bon', color: 'bg-yellow-500', textColor: 'text-yellow-400' };
    return { label: 'Modéré', color: 'bg-orange-500', textColor: 'text-orange-400' };
  };
  
  const rating = getScoreRating(displayScore);
  
  // Géolocalisation
  const startWatchingPosition = useCallback(() => {
    if (!navigator.geolocation) {
      toast.error('Géolocalisation non supportée');
      return;
    }
    
    setWatchingPosition(true);
    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        setUserPosition({ lat: latitude, lng: longitude, accuracy });
        toast.success('Position mise à jour', { description: `Précision: ${Math.round(accuracy)}m` });
      },
      (error) => {
        toast.error('Erreur de géolocalisation', { description: error.message });
        setWatchingPosition(false);
      },
      { enableHighAccuracy: true, maximumAge: 10000, timeout: 10000 }
    );
  }, []);
  
  const stopWatchingPosition = useCallback(() => {
    if (watchIdRef.current) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
    setWatchingPosition(false);
  }, []);
  
  const centerOnUser = useCallback(() => {
    if (userPosition) {
      setMapCenter([userPosition.lat, userPosition.lng]);
      setMapZoom(14);
    } else {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserPosition({ lat: latitude, lng: longitude });
          setMapCenter([latitude, longitude]);
          setMapZoom(14);
          toast.success('Centré sur votre position');
        },
        () => toast.error('Impossible d\'obtenir votre position')
      );
    }
  }, [userPosition]);
  
  // Sélectionner un waypoint comme cible pour les zones BIONIC
  const selectWaypointAsTarget = useCallback((waypoint) => {
    setSelectedWaypointForZones(waypoint);
    setMapCenter([waypoint.lat, waypoint.lng]);
    setMapZoom(14);
    toast.success(`Zones BIONIC centrées sur ${waypoint.name}`, { 
      description: 'Les zones s\'adaptent autour de ce waypoint' 
    });
  }, []);
  
  // Effacer la cible waypoint
  const clearWaypointTarget = useCallback(() => {
    setSelectedWaypointForZones(null);
    toast.info('Zones BIONIC en mode libre');
  }, []);
  
  // Wrapper pour supprimer waypoint (gère aussi la cible)
  const handleDeleteWaypoint = useCallback((id) => {
    if (selectedWaypointForZones?.id === id) {
      setSelectedWaypointForZones(null);
    }
    deleteWaypoint(id);
  }, [selectedWaypointForZones, deleteWaypoint]);
  
  // Wrapper pour ajouter un waypoint avec coordonnées par défaut
  const handleAddWaypoint = useCallback((data) => {
    addWaypoint({
      name: data.name || 'Nouveau waypoint',
      lat: parseFloat(data.lat) || mapCenter[0],
      lng: parseFloat(data.lng) || mapCenter[1],
      type: data.type || 'autre',
      active: true
    });
  }, [mapCenter, addWaypoint]);
  
  // Gestion des lieux
  const handleAddPlace = useCallback(() => {
    if (!newPlace.name) {
      toast.error('Veuillez entrer un nom');
      return;
    }
    
    addPlace({
      name: newPlace.name,
      lat: parseFloat(newPlace.lat) || mapCenter[0],
      lng: parseFloat(newPlace.lng) || mapCenter[1],
      type: newPlace.type,
      notes: newPlace.notes
    });
    
    setNewPlace({ name: '', type: 'autre', lat: '', lng: '', notes: '' });
    setShowAddPlaceDialog(false);
  }, [newPlace, mapCenter, addPlace]);
  
  const handleUpdatePlace = useCallback(() => {
    if (!editingPlace) return;
    
    updatePlace(editingPlace.id, {
      name: editingPlace.name,
      type: editingPlace.type,
      notes: editingPlace.notes
    });
    setEditingPlace(null);
  }, [editingPlace, updatePlace]);
  
  // Ouvrir le dialog de partage pour un waypoint
  const openShareDialog = useCallback((waypoint) => {
    setWaypointToShare(waypoint);
    setShowShareDialog(true);
  }, []);
  
  const useCurrentPositionForNewPlace = useCallback(() => {
    if (userPosition) {
      setNewPlace(prev => ({ ...prev, lat: userPosition.lat.toFixed(6), lng: userPosition.lng.toFixed(6) }));
    } else {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setNewPlace(prev => ({ 
            ...prev, 
            lat: position.coords.latitude.toFixed(6), 
            lng: position.coords.longitude.toFixed(6) 
          }));
        },
        () => toast.error('Impossible d\'obtenir votre position')
      );
    }
  }, [userPosition]);
  
  // Utiliser la position actuelle pour le nouveau waypoint
  const useCurrentPositionForNewWaypoint = useCallback(() => {
    if (userPosition) {
      setNewWaypoint(prev => ({ ...prev, lat: userPosition.lat.toFixed(6), lng: userPosition.lng.toFixed(6) }));
    } else {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setNewWaypoint(prev => ({ 
            ...prev, 
            lat: position.coords.latitude.toFixed(6), 
            lng: position.coords.longitude.toFixed(6) 
          }));
        },
        () => toast.error('Impossible d\'obtenir votre position')
      );
    }
  }, [userPosition]);
  
  // Fonction pour ajouter un waypoint depuis le dialog contrôlé
  const handleAddWaypointFromDialog = useCallback(() => {
    if (!newWaypoint.name) {
      toast.error('Veuillez entrer un nom');
      return;
    }
    
    addWaypoint({
      name: newWaypoint.name,
      lat: parseFloat(newWaypoint.lat) || mapCenter[0],
      lng: parseFloat(newWaypoint.lng) || mapCenter[1],
      type: newWaypoint.type || 'autre',
      active: true
    });
    
    setNewWaypoint({ name: '', type: 'autre', lat: '', lng: '' });
    setShowAddWaypointDialog(false);
    toast.success('Waypoint créé avec succès !');
  }, [newWaypoint, mapCenter, addWaypoint]);
  
  // Callback pour créer un waypoint en cliquant sur la carte
  const handleMapClickForWaypoint = useCallback((lat, lng) => {
    // Pré-remplir les coordonnées et ouvrir le dialog
    setNewWaypoint(prev => ({
      ...prev,
      lat: lat.toFixed(6),
      lng: lng.toFixed(6)
    }));
    setShowAddWaypointDialog(true);
    setMapClickMode(false); // Désactiver le mode après le clic
    toast.info('Coordonnées capturées !', {
      description: `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
    });
  }, []);
  
  // Scores par catégorie (valeurs stables basées sur la position)
  const categoryScores = useMemo(() => {
    if (scores?.breakdown) return scores.breakdown;
    // Scores déterministes basés sur la position
    const baseSeed = Math.abs(Math.round(currentMapCenter.lat * 100 + currentMapCenter.lng * 50));
    return {
      habitat: 75 + (baseSeed % 15),
      rut: 68 + ((baseSeed + 1) % 20),
      salines: 60 + ((baseSeed + 2) % 25),
      affuts: 80 + ((baseSeed + 3) % 15),
      trajets: 65 + ((baseSeed + 4) % 20),
      peuplements: 70 + ((baseSeed + 5) % 15)
    };
  }, [scores?.breakdown, currentMapCenter.lat, currentMapCenter.lng]);

  return (
    <div className="min-h-screen bg-black pt-16" data-testid="mon-territoire-bionic-page">
      {/* Header de la page */}
      <div className="bg-gradient-to-r from-black via-gray-900 to-black border-b border-[#f5a623]/30">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="text-gray-400 hover:text-white">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Retour
              </Button>
              <div className="h-6 w-px bg-gray-700" />
              <div className="flex items-center gap-3">
                <Brain className="h-6 w-6 text-[#f5a623]" />
                <div>
                  <h1 className="text-lg font-bold text-white">Mon Territoire BIONIC™</h1>
                  <p className="text-[10px] text-gray-400">Analyse • Waypoints • Lieux</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Score Global */}
              <div className="bg-gray-900/80 rounded-lg px-3 py-1.5 border border-gray-700">
                <div className="flex items-center gap-2">
                  <span className="text-xl font-bold text-white">{displayScore}</span>
                  <span className="text-gray-500 text-sm">/100</span>
                  <Badge className={`${rating.color} text-white text-[10px]`}>{rating.label}</Badge>
                </div>
              </div>
              
              {/* Mode LIVE */}
              <div className="flex items-center gap-2 bg-gray-900/80 rounded-lg px-3 py-1.5 border border-gray-700">
                <Zap className={`h-4 w-4 ${liveMode ? 'text-green-400' : 'text-gray-500'}`} />
                <span className="text-xs text-gray-400">LIVE</span>
                <Switch checked={liveMode} onCheckedChange={setLiveMode} className="data-[state=checked]:bg-green-500" />
              </div>
              
              {/* Statut Sync */}
              <div className={`flex items-center gap-2 bg-gray-900/80 rounded-lg px-3 py-1.5 border ${isOnline ? 'border-green-700/50' : 'border-red-700/50'}`}>
                {isOnline ? (
                  <Wifi className="h-4 w-4 text-green-400" />
                ) : (
                  <WifiOff className="h-4 w-4 text-red-400" />
                )}
                {syncing ? (
                  <RefreshCw className="h-3 w-3 text-blue-400 animate-spin" />
                ) : (
                  <Cloud className={`h-3 w-3 ${isOnline ? 'text-green-400' : 'text-red-400'}`} />
                )}
                <span className="text-[10px] text-gray-400">
                  {syncing ? 'Sync...' : isOnline ? 'Sync' : 'Offline'}
                </span>
              </div>
              
              {/* Notifications */}
              <div className="relative">
                <NotificationBell 
                  count={unreadCount} 
                  onClick={() => setShowNotificationsPanel(!showNotificationsPanel)}
                />
                
                {/* Panel de notifications */}
                {showNotificationsPanel && (
                  <div className="absolute right-0 top-12 w-80 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50">
                    <div className="p-3 border-b border-gray-700 flex items-center justify-between">
                      <span className="text-sm font-medium text-white">Notifications</span>
                      {unreadCount > 0 && (
                        <button 
                          onClick={markAllAsRead}
                          className="text-xs text-[#f5a623] hover:underline"
                        >
                          Tout marquer lu
                        </button>
                      )}
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                      {notifications.length === 0 ? (
                        <div className="p-4 text-center text-gray-500 text-sm">
                          Aucune notification
                        </div>
                      ) : (
                        notifications.slice(0, 10).map(notif => (
                          <div 
                            key={notif.id}
                            className={`p-3 border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer ${!notif.read ? 'bg-[#f5a623]/5' : ''}`}
                            onClick={() => markAsRead(notif.id)}
                          >
                            <div className="flex items-start gap-2">
                              {!notif.read && (
                                <span className="w-2 h-2 bg-[#f5a623] rounded-full mt-1.5 flex-shrink-0" />
                              )}
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-white truncate">{notif.title}</p>
                                <p className="text-xs text-gray-400 mt-0.5">{notif.message}</p>
                                <p className="text-[10px] text-gray-600 mt-1">
                                  {new Date(notif.created_at).toLocaleDateString('fr-FR')}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Menu Groupes de Chasse */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-[#f5a623]/50 text-[#f5a623] hover:bg-[#f5a623]/10"
                    data-testid="group-menu-btn"
                  >
                    <Users className="h-4 w-4 mr-1" />
                    Groupe
                    {myGroups.length > 0 && (
                      <Badge className="ml-1 bg-[#f5a623] text-black text-[10px]">{myGroups.length}</Badge>
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="bg-gray-900 border-gray-700 min-w-[200px]">
                  <DropdownMenuItem 
                    onClick={() => setShowCreateGroupDialog(true)}
                    className="text-[#f5a623] cursor-pointer"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Créer un groupe
                  </DropdownMenuItem>
                  
                  {myGroups.length > 0 && (
                    <>
                      <DropdownMenuSeparator className="bg-gray-700" />
                      <div className="px-2 py-1 text-xs text-gray-500">Mes groupes</div>
                      {myGroups.map(group => (
                        <DropdownMenuItem 
                          key={group.id}
                          onClick={() => {
                            setSelectedGroup(group);
                            setShowGroupDashboard(true);
                          }}
                          className="text-white cursor-pointer hover:bg-gray-800"
                        >
                          <Users className="h-4 w-4 mr-2 text-gray-400" />
                          <span className="flex-1 truncate">{group.name}</span>
                          {group.member_count && (
                            <Badge className="ml-1 bg-gray-700 text-gray-300 text-[10px]">{group.member_count}</Badge>
                          )}
                        </DropdownMenuItem>
                      ))}
                    </>
                  )}
                  
                  {myGroups.length === 0 && (
                    <div className="px-3 py-2 text-xs text-gray-500 text-center">
                      Aucun groupe pour l'instant
                    </div>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          
          {/* Sous-onglets */}
          <div className="mt-3">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <div className="flex items-center gap-3">
                <TabsList className="bg-gray-900/50 border border-gray-800">
                  <TabsTrigger value="carte" className="data-[state=active]:bg-[#f5a623]/20 data-[state=active]:text-[#f5a623]">
                    <Map className="h-4 w-4 mr-2" />
                    Carte BIONIC™
                  </TabsTrigger>
                  <TabsTrigger value="waypoints" className="data-[state=active]:bg-[#f5a623]/20 data-[state=active]:text-[#f5a623]">
                    <MapPin className="h-4 w-4 mr-2" />
                    Waypoints actifs
                    {activeWaypoints.length > 0 && (
                      <Badge className="ml-2 bg-[#f5a623] text-black text-[10px]">{activeWaypoints.length}</Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="lieux" className="data-[state=active]:bg-[#f5a623]/20 data-[state=active]:text-[#f5a623]">
                    <BookMarked className="h-4 w-4 mr-2" />
                    Lieux enregistrés
                    {savedPlaces.length > 0 && (
                      <Badge className="ml-2 bg-blue-500 text-white text-[10px]">{savedPlaces.length}</Badge>
                    )}
                  </TabsTrigger>
                </TabsList>
                
                {/* Bouton Enregistrer un Waypoint avec menu déroulant */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      className={`${mapClickMode ? 'bg-green-500 hover:bg-green-600' : 'bg-[#f5a623] hover:bg-[#f5a623]/80'} text-black font-medium`}
                      data-testid="add-waypoint-quick-btn"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      {mapClickMode ? 'Cliquez sur la carte...' : 'Enregistrer un Waypoint'}
                      <ChevronDown className="h-4 w-4 ml-2" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-gray-900 border-gray-700">
                    <DropdownMenuItem 
                      onClick={() => setShowAddWaypointDialog(true)}
                      className="text-white hover:bg-gray-800 cursor-pointer"
                    >
                      <Edit2 className="h-4 w-4 mr-2 text-[#f5a623]" />
                      Saisir les coordonnées
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => {
                        setMapClickMode(true);
                        toast.info('Mode création activé', {
                          description: 'Cliquez sur la carte pour placer votre waypoint'
                        });
                      }}
                      className="text-white hover:bg-gray-800 cursor-pointer"
                    >
                      <Crosshair className="h-4 w-4 mr-2 text-green-500" />
                      Cliquer sur la carte
                    </DropdownMenuItem>
                    {mapClickMode && (
                      <>
                        <DropdownMenuSeparator className="bg-gray-700" />
                        <DropdownMenuItem 
                          onClick={() => setMapClickMode(false)}
                          className="text-red-400 hover:bg-gray-800 cursor-pointer"
                        >
                          <X className="h-4 w-4 mr-2" />
                          Annuler le mode clic
                        </DropdownMenuItem>
                      </>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </Tabs>
          </div>
        </div>
      </div>
      
      {/* Contenu des onglets */}
      <div className="h-[calc(100vh-180px)]">
        {/* Onglet Carte BIONIC */}
        {activeTab === 'carte' && (
          <div className="flex h-full">
            {/* Panneau Couches */}
            <div className={`${showLayersPanel ? 'w-64' : 'w-10'} bg-gray-900/95 border-r border-gray-800 transition-all duration-300 flex flex-col`}>
              <button onClick={() => setShowLayersPanel(!showLayersPanel)} className="p-2 border-b border-gray-800 flex items-center justify-between hover:bg-gray-800/50">
                <div className="flex items-center gap-2">
                  <Layers className="h-4 w-4 text-[#f5a623]" />
                  {showLayersPanel && <span className="text-white text-sm">Couches</span>}
                </div>
              </button>
              
              {showLayersPanel && (
                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                  <div className="flex gap-1">
                    <Button size="sm" variant="outline" onClick={showAllLayers} className="flex-1 text-[10px] h-7 border-gray-700">Tout</Button>
                    <Button size="sm" variant="outline" onClick={hideAllLayers} className="flex-1 text-[10px] h-7 border-gray-700">Aucun</Button>
                  </div>
                  <div className="text-[10px] text-gray-500">{activeCount}/{allLayers.length} actives</div>
                  <div className="space-y-1">
                    {allLayers.slice(0, 10).map(layer => (
                      <button
                        key={layer.id}
                        onClick={() => toggleLayer(layer.id)}
                        className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-[11px] transition-all ${
                          layersVisible[layer.id] ? 'bg-[#f5a623]/10 text-white border border-[#f5a623]/30' : 'bg-gray-800/50 text-gray-400'
                        }`}
                      >
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: layersVisible[layer.id] ? layer.color : '#4b5563' }} />
                        <span className="flex-1 text-left truncate">{layer.name}</span>
                      </button>
                    ))}
                  </div>
                  
                  {/* Séparateur */}
                  <div className="border-t border-gray-700 pt-2 mt-3">
                    <div className="text-[10px] text-[#f5a623] uppercase mb-2 flex items-center gap-1">
                      <Settings className="h-3 w-3" />
                      Affichage zones
                    </div>
                    
                    {/* Mode d'affichage */}
                    <div className="flex gap-1 mb-2">
                      <Button 
                        size="sm" 
                        variant={zoneDisplayMode === 'micro' ? 'default' : 'outline'} 
                        onClick={() => setZoneDisplayMode('micro')} 
                        className={`flex-1 text-[9px] h-6 ${zoneDisplayMode === 'micro' ? 'bg-[#f5a623] text-black' : 'border-gray-700 text-gray-400'}`}
                      >
                        Micro
                      </Button>
                      <Button 
                        size="sm" 
                        variant={zoneDisplayMode === 'classic' ? 'default' : 'outline'} 
                        onClick={() => setZoneDisplayMode('classic')} 
                        className={`flex-1 text-[9px] h-6 ${zoneDisplayMode === 'classic' ? 'bg-[#f5a623] text-black' : 'border-gray-700 text-gray-400'}`}
                      >
                        Classique
                      </Button>
                    </div>
                    
                    {/* Options micro-zones */}
                    {zoneDisplayMode === 'micro' && (
                      <div className="space-y-2">
                        {/* Cercles concentriques */}
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-400">Cercles concentriques</span>
                          <Switch 
                            checked={showConcentricCircles} 
                            onCheckedChange={setShowConcentricCircles}
                            className="scale-75"
                          />
                        </div>
                        
                        {/* Corridors */}
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-gray-400">Corridors & Tampons</span>
                          <Switch 
                            checked={showCorridors} 
                            onCheckedChange={setShowCorridors}
                            className="scale-75"
                          />
                        </div>
                        
                        {/* Seuil minimum */}
                        <div className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-gray-400">Seuil min.</span>
                            <span className="text-[10px] text-[#f5a623]">{minPercentageFilter}%</span>
                          </div>
                          <input 
                            type="range" 
                            min="30" 
                            max="80" 
                            step="5"
                            value={minPercentageFilter}
                            onChange={(e) => setMinPercentageFilter(parseInt(e.target.value))}
                            className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[#f5a623]"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Mode confidentialité */}
                  <div className="border-t border-gray-700 pt-2 mt-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1">
                        {privacyMode ? <Lock className="h-3 w-3 text-red-400" /> : <Unlock className="h-3 w-3 text-green-400" />}
                        <span className="text-[10px] text-gray-400">Mode privé</span>
                      </div>
                      <Switch 
                        checked={privacyMode} 
                        onCheckedChange={setPrivacyMode}
                        className="scale-75"
                      />
                    </div>
                    <div className="text-[9px] text-gray-500 mt-1">
                      {privacyMode ? 'Données personnelles masquées' : 'Waypoints et lieux visibles'}
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Carte */}
            <div className="flex-1 relative">
              {/* Indicateur du mode création de waypoint */}
              {mapClickMode && (
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-green-500 text-black px-4 py-2 rounded-full shadow-lg flex items-center gap-2 animate-pulse">
                  <Crosshair className="h-5 w-5" />
                  <span className="font-medium">Cliquez sur la carte pour placer votre waypoint</span>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    className="h-6 w-6 p-0 hover:bg-green-600 ml-2"
                    onClick={() => setMapClickMode(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
              
              <MapContainer center={mapCenter} zoom={mapZoom} className={`h-full w-full ${mapClickMode ? 'cursor-crosshair' : ''}`} zoomControl={false}>
                {/* COUCHES ÉCOFORESTIÈRES DYNAMIQUES avec FALLBACK */}
                <EcoforestryLayers 
                  activeLayers={activeEcoLayers}
                  layerOpacities={ecoLayerOpacities}
                  baseMapId={activeEcoLayers.baseMap}
                  fallbackStatus={ecoMapStatus}
                  activeFallback={activeFallback}
                />
                
                <MapController center={mapCenter} zoom={mapZoom} />
                <ZoomHandler onZoomChange={handleZoomChange} onMapMove={handleMapMove} onBoundsChange={handleBoundsChange} />
                
                {/* Gestionnaire de clic pour créer des waypoints */}
                {mapClickMode && (
                  <MapClickHandler onMapClick={handleMapClickForWaypoint} enabled={true} />
                )}
                
                {/* Zones BIONIC - Mode Micro-délimitation (cercles fins) */}
                {zoneDisplayMode === 'micro' && (
                  <BionicMicroZones
                    zones={microZones}
                    corridors={corridors}
                    bufferZones={bufferZones}
                    minPercentage={minPercentageFilter}
                    showConcentricCircles={showConcentricCircles}
                    showCorridors={showCorridors}
                    showBufferZones={showCorridors}
                    onZoneClick={setSelectedZone}
                    isZoneFavorite={isZoneFavorite}
                    onAddFavorite={async (zone) => {
                      // Ouvrir un dialog pour nommer la zone
                      const name = prompt(`Nom pour cette zone ${BIONIC_MODULES[zone.moduleId]?.label || zone.moduleId} (${zone.percentage}%) ?`, `Zone ${BIONIC_MODULES[zone.moduleId]?.label}`);
                      if (name) {
                        await addFavorite({
                          name,
                          module_id: zone.moduleId,
                          location: {
                            lat: zone.center[0],
                            lng: zone.center[1],
                            radius_meters: zone.radiusMeters
                          },
                          notes: null,
                          alert_enabled: true,
                          alert_days_before: 3
                        });
                      }
                    }}
                    onRemoveFavorite={(zone) => {
                      const favId = getFavoriteId(zone);
                      if (favId) removeFavorite(favId);
                    }}
                  />
                )}
                
                {/* Zones BIONIC - Mode Classique (hexagones) */}
                {zoneDisplayMode === 'classic' && classicZones.map(zone => (
                  <Polygon
                    key={zone.id}
                    positions={zone.positions}
                    pathOptions={{ 
                      color: zone.color, 
                      fillColor: zone.color, 
                      fillOpacity: zone.score >= 80 ? 0.35 : zone.score >= 65 ? 0.25 : 0.18, 
                      weight: zone.score >= 80 ? 2 : 1.5, 
                      opacity: 0.9 
                    }}
                    eventHandlers={{
                      click: () => setSelectedZone(zone)
                    }}
                  >
                    <Tooltip sticky>
                      <div className="text-center">
                        <div className="font-bold">{zone.label}</div>
                        <div className="text-sm">Score: {zone.score}%</div>
                        <div className="text-xs text-gray-500">≈{zone.areaKm2.toFixed(2)} km²</div>
                      </div>
                    </Tooltip>
                  </Polygon>
                ))}
                
                {/* Cercle indiquant le waypoint cible */}
                {selectedWaypointForZones && (
                  <Circle
                    center={[selectedWaypointForZones.lat, selectedWaypointForZones.lng]}
                    radius={100}
                    pathOptions={{ color: '#f5a623', fillColor: '#f5a623', fillOpacity: 0.3, weight: 2, dashArray: '5, 5' }}
                  />
                )}
                
                {/* Position utilisateur */}
                {userPosition && (
                  <Marker position={[userPosition.lat, userPosition.lng]} icon={createCustomIcon('#3b82f6', 'user')}>
                    <Popup><div className="text-center font-bold">Ma position</div></Popup>
                  </Marker>
                )}
                
                {/* Waypoints actifs (visibles selon mode confidentialité) */}
                {isPrivateDataVisible && activeWaypoints.map(wp => (
                  <Marker 
                    key={wp.id} 
                    position={[wp.lat, wp.lng]} 
                    icon={createCustomIcon(selectedWaypointForZones?.id === wp.id ? '#22c55e' : '#f5a623', 'waypoint')}
                    eventHandlers={{
                      click: () => selectWaypointAsTarget(wp)
                    }}
                  >
                    <Popup>
                      <div className="text-center">
                        <div className="font-bold">{wp.name}</div>
                        <div className="text-xs text-gray-500">{PLACE_TYPES.find(t => t.id === wp.type)?.name}</div>
                        <button 
                          className="mt-2 px-2 py-1 bg-[#f5a623] text-black text-xs rounded"
                          onClick={() => selectWaypointAsTarget(wp)}
                        >
                          Cibler pour analyse
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                ))}
                
                {/* Lieux enregistrés (visibles selon mode confidentialité) */}
                {isPrivateDataVisible && savedPlaces.map(place => (
                  <Marker key={place.id} position={[place.lat, place.lng]} icon={createCustomIcon(PLACE_TYPES.find(t => t.id === place.type)?.color || '#6b7280', 'place')}>
                    <Popup><div className="text-center"><div className="font-bold">{place.name}</div><div className="text-xs">{PLACE_TYPES.find(t => t.id === place.type)?.icon} {PLACE_TYPES.find(t => t.id === place.type)?.name}</div></div></Popup>
                  </Marker>
                ))}
                
                {/* Overlay de confidentialité activé */}
                {privacyMode && (
                  <div className="bionic-private-overlay" />
                )}
              </MapContainer>
              
              {/* Contrôles carte */}
              <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
                <Button size="sm" className="bg-black/80 text-white border border-gray-700 h-8 w-8 p-0" onClick={() => setMapZoom(z => Math.min(18, z + 1))}>+</Button>
                <Button size="sm" className="bg-black/80 text-white border border-gray-700 h-8 w-8 p-0" onClick={() => setMapZoom(z => Math.max(5, z - 1))}>-</Button>
                <Button size="sm" className={`${userPosition ? 'bg-blue-600' : 'bg-black/80'} text-white border border-gray-700 h-8 w-8 p-0`} onClick={centerOnUser}>
                  <LocateFixed className="h-4 w-4" />
                </Button>
                <div className="h-px bg-gray-700 my-1" />
                {/* Toggle panneau écoforestier */}
                <Button 
                  size="sm" 
                  className={`${showEcoforestryPanel ? 'bg-green-600' : 'bg-black/80'} text-white border border-gray-700 h-8 w-8 p-0`}
                  onClick={() => setShowEcoforestryPanel(!showEcoforestryPanel)}
                  title="Carte écoforestière"
                >
                  <Leaf className="h-4 w-4" />
                </Button>
              </div>
              
              {/* PANNEAU DE CONTRÔLE ÉCOFORESTIER */}
              {showEcoforestryPanel && (
                <div className="absolute top-4 left-14 z-[1000] w-72">
                  <EcoforestryLayerControl
                    activeLayers={activeEcoLayers}
                    onToggleLayer={handleEcoLayerToggle}
                    layerOpacities={ecoLayerOpacities}
                    onOpacityChange={handleEcoOpacityChange}
                    expanded={showEcoforestryPanel}
                    onToggleExpand={() => setShowEcoforestryPanel(!showEcoforestryPanel)}
                    // Props du système de fallback
                    fallbackStatus={ecoMapStatus}
                    activeFallback={activeFallback}
                    retryCount={retryCount}
                    onForceCheck={forceEcoMapCheck}
                    onChangeFallback={setFallbackMap}
                  />
                </div>
              )}
              
              {/* NOTIFICATION DE FALLBACK (non intrusive) */}
              {isEcoMapSelected && (
                <EcoMapFallbackNotification
                  status={ecoMapStatus}
                  activeFallback={activeFallback}
                  retryCount={retryCount}
                  onForceCheck={forceEcoMapCheck}
                  onChangeFallback={setFallbackMap}
                />
              )}
              
              {/* Indicateur de zoom et cible */}
              <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
                {/* Badge niveau de zoom */}
                <div className="bg-black/90 backdrop-blur-sm rounded-lg px-3 py-1.5 border border-gray-700">
                  <div className="text-[10px] text-gray-400 uppercase">Zoom</div>
                  <div className="text-lg font-bold text-white text-center">{currentZoom}</div>
                </div>
                
                {/* Nombre de zones */}
                <div className="bg-black/90 backdrop-blur-sm rounded-lg px-3 py-1.5 border border-gray-700">
                  <div className="text-[10px] text-gray-400 uppercase">Zones</div>
                  <div className="text-lg font-bold text-[#f5a623] text-center">{visibleZonesCount}</div>
                  <div className="text-[9px] text-gray-500 text-center">
                    {zoneDisplayMode === 'micro' ? 'Micro' : 'Classique'}
                  </div>
                </div>
                
                {/* Waypoint cible */}
                {selectedWaypointForZones && (
                  <div className="bg-green-900/80 backdrop-blur-sm rounded-lg px-3 py-2 border border-green-500/50">
                    <div className="text-[10px] text-green-400 uppercase flex items-center gap-1">
                      <Target className="h-3 w-3" />
                      Cible
                    </div>
                    <div className="text-xs font-medium text-white truncate max-w-[100px]">{selectedWaypointForZones.name}</div>
                    <button 
                      onClick={clearWaypointTarget}
                      className="mt-1 text-[10px] text-red-400 hover:text-red-300 flex items-center gap-1"
                    >
                      <X className="h-3 w-3" /> Effacer cible
                    </button>
                  </div>
                )}
              </div>
              
              {/* Bandeau météo */}
              {weather && (
                <div className="absolute bottom-4 left-4 right-4 z-[1000] bg-black/90 backdrop-blur-sm rounded-lg border border-gray-700 p-2">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1"><Thermometer className="h-4 w-4 text-blue-400" /><span className="text-white">{Math.round(temperature)}°C</span></div>
                      <div className="flex items-center gap-1"><Wind className="h-4 w-4 text-gray-400" /><span className="text-white">{windInfo?.direction} {Math.round(windInfo?.speed)} km/h</span></div>
                      <div className="flex items-center gap-1"><Target className="h-4 w-4 text-[#f5a623]" /><span className="text-white">Chasse: {huntingScore}/100</span></div>
                    </div>
                    {liveMode && <Badge className="bg-green-500/20 text-green-400 animate-pulse"><Zap className="h-3 w-3 mr-1" />LIVE</Badge>}
                  </div>
                </div>
              )}
            </div>
            
            {/* Panneau Analyse */}
            <div className={`${showAnalysisPanel ? 'w-72' : 'w-10'} bg-gray-900/95 border-l border-gray-800 transition-all flex flex-col`}>
              <button onClick={() => setShowAnalysisPanel(!showAnalysisPanel)} className="p-2 border-b border-gray-800 flex items-center justify-end hover:bg-gray-800/50">
                <BarChart3 className="h-4 w-4 text-[#f5a623]" />
              </button>
              
              {showAnalysisPanel && (
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {/* MESSAGE SI AUCUN WAYPOINT ACTIF */}
                  {(!activeWaypoints || activeWaypoints.length === 0) && (
                    <div className="bg-amber-900/30 rounded-lg p-3 border border-amber-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <MapPin className="h-4 w-4 text-amber-400" />
                        <span className="text-xs font-medium text-amber-400">Analyse inactive</span>
                      </div>
                      <p className="text-[10px] text-gray-400 leading-relaxed">
                        Ajoutez un ou plusieurs waypoints pour activer l'analyse BIONIC™ des zones fauniques.
                      </p>
                      <p className="text-[10px] text-amber-300/70 mt-2">
                        → Cliquez sur "Waypoints actifs" pour en ajouter
                      </p>
                    </div>
                  )}
                  
                  {/* EXCLUSION PERMANENTE DES ZONES AQUATIQUES */}
                  <div className="bg-cyan-900/40 rounded-lg p-3 border border-cyan-500/40">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Waves className="h-4 w-4 text-cyan-400" />
                        <span className="text-xs font-medium text-cyan-400">Exclusion Eau</span>
                      </div>
                      <Badge className="bg-cyan-500/20 text-cyan-300 text-[9px] px-1.5">
                        PERMANENT
                      </Badge>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="text-gray-400">Tolérance rivage</span>
                        <span className="text-cyan-300">5m</span>
                      </div>
                      {activeWaypoints?.length > 0 && isFilteringWater ? (
                        <div className="flex items-center gap-2 text-[10px] text-cyan-300">
                          <RefreshCw className="h-3 w-3 animate-spin" />
                          Analyse hydrographique...
                        </div>
                      ) : activeWaypoints?.length > 0 && waterExclusionStats ? (
                        <>
                          <div className="flex items-center justify-between text-[10px]">
                            <span className="text-gray-400">Zones filtrées</span>
                            <span className={waterExclusionStats.excluded > 0 ? "text-orange-400" : "text-green-400"}>
                              {waterExclusionStats.excluded} / {waterExclusionStats.total}
                            </span>
                          </div>
                          {waterExclusionStats.sources_used && (
                            <div className="text-[9px] text-gray-500 mt-1">
                              Sources: {waterExclusionStats.sources_used.join(', ')}
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="text-[10px] text-green-400 flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" />
                          Actif sur toutes les couches
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Alertes conditions optimales */}
                  <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                    <AlertsPanel
                      alerts={alerts}
                      unreadCount={unreadAlertCount}
                      onMarkRead={markAlertRead}
                      onMarkAllRead={markAllAlertsRead}
                      onRefresh={checkOptimalConditions}
                      loading={favoritesLoading}
                    />
                  </div>
                  
                  {/* Zones favorites */}
                  <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                    <FavoritesList
                      favorites={favorites}
                      onRemove={removeFavorite}
                      onUpdateAlerts={updateAlertSettings}
                      onViewConditions={getZoneConditions}
                    />
                  </div>
                  
                  {/* Séparateur */}
                  <div className="border-t border-gray-700 my-2" />
                  
                  <div className="bg-[#f5a623]/10 rounded-lg p-3 border border-[#f5a623]/30">
                    <div className="text-[10px] text-gray-400 uppercase">Score Global</div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl font-bold text-white">{displayScore}</span>
                      <span className="text-gray-500">/100</span>
                    </div>
                  </div>
                  
                  {SCORE_CATEGORIES.map((cat) => {
                    const score = categoryScores[cat.id] || 0;
                    return (
                      <div key={cat.id} className="bg-gray-800/50 rounded p-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-gray-300">{cat.icon} {cat.name}</span>
                          <span className="text-xs font-bold text-white">{score}%</span>
                        </div>
                        <div className="h-1 bg-gray-700 rounded-full">
                          <div className="h-full bg-[#f5a623] rounded-full" style={{ width: `${score}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Onglet Waypoints actifs */}
        {activeTab === 'waypoints' && (
          <div className="flex h-full">
            {/* Liste des waypoints */}
            <div className="w-96 bg-gray-900/95 border-r border-gray-800 flex flex-col">
              <div className="p-4 border-b border-gray-800">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-white font-semibold flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-[#f5a623]" />
                    Waypoints actifs
                  </h2>
                  <span className="text-xs text-gray-500">
                    Utilisez le bouton "Enregistrer un Waypoint" ci-dessus
                  </span>
                </div>
                
                {/* Position actuelle */}
                <div className="bg-blue-900/20 rounded-lg p-3 border border-blue-500/30">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
                      <span className="text-blue-400 text-sm font-medium">Ma position actuelle</span>
                    </div>
                    <Switch checked={watchingPosition} onCheckedChange={(checked) => checked ? startWatchingPosition() : stopWatchingPosition()} className="data-[state=checked]:bg-blue-500" />
                  </div>
                  {userPosition && (
                    <div className="mt-2 text-xs text-gray-400">
                      {userPosition.lat.toFixed(6)}, {userPosition.lng.toFixed(6)}
                      {userPosition.accuracy && <span className="ml-2">±{Math.round(userPosition.accuracy)}m</span>}
                    </div>
                  )}
                </div>
              </div>
              
              {/* Liste */}
              <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {waypoints.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <MapPin className="h-12 w-12 mx-auto mb-3 opacity-30" />
                    <p>Aucun waypoint</p>
                    <p className="text-xs mt-1">Ajoutez votre premier waypoint</p>
                  </div>
                ) : (
                  waypoints.map(wp => {
                    const typeInfo = PLACE_TYPES.find(t => t.id === wp.type);
                    return (
                      <div 
                        key={wp.id} 
                        className={`bg-gray-800/50 rounded-lg p-3 border ${wp.active ? 'border-[#f5a623]/50' : 'border-gray-700'} transition-all hover:bg-gray-800`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <div className="w-10 h-10 rounded-lg flex items-center justify-center text-xl" style={{ backgroundColor: `${typeInfo?.color}20` }}>
                              {typeInfo?.icon || '📍'}
                            </div>
                            <div>
                              <div className="text-white font-medium">{wp.name}</div>
                              <div className="text-xs text-gray-400 mt-0.5">{typeInfo?.name}</div>
                              <div className="text-[10px] text-gray-500 mt-1">
                                {wp.lat.toFixed(4)}, {wp.lng.toFixed(4)}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => openShareDialog(wp)} 
                              className="text-[#f5a623] hover:text-[#f5a623]/80 h-8 w-8 p-0"
                              title="Partager"
                            >
                              <Share2 className="h-4 w-4" />
                            </Button>
                            <Switch checked={wp.active} onCheckedChange={() => toggleWaypointActive(wp.id)} className="data-[state=checked]:bg-[#f5a623]" />
                            <Button variant="ghost" size="sm" onClick={() => handleDeleteWaypoint(wp.id)} className="text-red-400 hover:text-red-300 h-8 w-8 p-0">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
            
            {/* Carte des waypoints */}
            <div className="flex-1 relative">
              <MapContainer center={mapCenter} zoom={11} className="h-full w-full" zoomControl={false}>
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                
                {userPosition && (
                  <Marker position={[userPosition.lat, userPosition.lng]} icon={createCustomIcon('#3b82f6', 'user')}>
                    <Popup><b>Ma position</b></Popup>
                  </Marker>
                )}
                
                {waypoints.map(wp => {
                  const typeInfo = PLACE_TYPES.find(t => t.id === wp.type);
                  return (
                    <Marker 
                      key={wp.id} 
                      position={[wp.lat, wp.lng]} 
                      icon={createCustomIcon(wp.active ? (typeInfo?.color || '#f5a623') : '#6b7280', 'waypoint')}
                      opacity={wp.active ? 1 : 0.5}
                    >
                      <Popup>
                        <div className="text-center">
                          <div className="font-bold">{wp.name}</div>
                          <div className="text-xs">{typeInfo?.icon} {typeInfo?.name}</div>
                          <Badge className={wp.active ? 'bg-green-500' : 'bg-gray-500'}>{wp.active ? 'Actif' : 'Inactif'}</Badge>
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MapContainer>
            </div>
          </div>
        )}
        
        {/* Onglet Lieux enregistrés */}
        {activeTab === 'lieux' && (
          <div className="flex h-full">
            {/* Liste des lieux */}
            <div className="w-96 bg-gray-900/95 border-r border-gray-800 flex flex-col">
              <div className="p-4 border-b border-gray-800">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-white font-semibold flex items-center gap-2">
                    <BookMarked className="h-5 w-5 text-blue-400" />
                    Lieux enregistrés
                  </h2>
                  <Dialog open={showAddPlaceDialog} onOpenChange={setShowAddPlaceDialog}>
                    <DialogTrigger asChild>
                      <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                        <Plus className="h-4 w-4 mr-1" /> Ajouter un lieu
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-gray-900 border-gray-700">
                      <DialogHeader>
                        <DialogTitle className="text-white">Ajouter un lieu</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div>
                          <Label className="text-gray-300">Nom du lieu *</Label>
                          <Input 
                            placeholder="Ex: ZEC Batiscan-Neilson" 
                            className="bg-gray-800 border-gray-700 text-white"
                            value={newPlace.name}
                            onChange={(e) => setNewPlace(p => ({ ...p, name: e.target.value }))} 
                          />
                        </div>
                        <div>
                          <Label className="text-gray-300">Type de lieu</Label>
                          <Select value={newPlace.type} onValueChange={(v) => setNewPlace(p => ({ ...p, type: v }))}>
                            <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent className="bg-gray-800 border-gray-700">
                              {PLACE_TYPES.map(type => (
                                <SelectItem key={type.id} value={type.id} className="text-white">
                                  <span className="flex items-center gap-2">{type.icon} {type.name}</span>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <Label className="text-gray-300">Latitude</Label>
                            <Input 
                              placeholder="46.8139" 
                              className="bg-gray-800 border-gray-700 text-white"
                              value={newPlace.lat}
                              onChange={(e) => setNewPlace(p => ({ ...p, lat: e.target.value }))} 
                            />
                          </div>
                          <div>
                            <Label className="text-gray-300">Longitude</Label>
                            <Input 
                              placeholder="-71.2080" 
                              className="bg-gray-800 border-gray-700 text-white"
                              value={newPlace.lng}
                              onChange={(e) => setNewPlace(p => ({ ...p, lng: e.target.value }))} 
                            />
                          </div>
                        </div>
                        <Button variant="outline" size="sm" onClick={useCurrentPositionForNewPlace} className="w-full border-gray-700 text-gray-300">
                          <LocateFixed className="h-4 w-4 mr-2" /> Utiliser ma position actuelle
                        </Button>
                        <div>
                          <Label className="text-gray-300">Notes (optionnel)</Label>
                          <Input 
                            placeholder="Ex: Zone 15, secteur lac Blanc" 
                            className="bg-gray-800 border-gray-700 text-white"
                            value={newPlace.notes}
                            onChange={(e) => setNewPlace(p => ({ ...p, notes: e.target.value }))} 
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setShowAddPlaceDialog(false)} className="border-gray-700">Annuler</Button>
                        <Button onClick={handleAddPlace} className="bg-blue-600 hover:bg-blue-700 text-white">Enregistrer</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
                
                {/* Types rapides */}
                <div className="flex flex-wrap gap-1">
                  {PLACE_TYPES.slice(0, 5).map(type => (
                    <button
                      key={type.id}
                      onClick={() => { setNewPlace({ name: '', type: type.id, lat: '', lng: '', notes: '' }); setShowAddPlaceDialog(true); }}
                      className="px-2 py-1 rounded text-[10px] bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
                    >
                      {type.icon} {type.name}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Liste des lieux */}
              <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {savedPlaces.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <BookMarked className="h-12 w-12 mx-auto mb-3 opacity-30" />
                    <p>Aucun lieu enregistré</p>
                    <p className="text-xs mt-1">Ajoutez vos ZEC, pourvoiries et territoires</p>
                  </div>
                ) : (
                  savedPlaces.map(place => {
                    const typeInfo = PLACE_TYPES.find(t => t.id === place.type);
                    return (
                      <div 
                        key={place.id} 
                        className="bg-gray-800/50 rounded-lg p-3 border border-gray-700 hover:border-gray-600 transition-all"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <div 
                              className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
                              style={{ backgroundColor: `${typeInfo?.color}20` }}
                            >
                              {typeInfo?.icon || '📌'}
                            </div>
                            <div className="flex-1">
                              <div className="text-white font-medium">{place.name}</div>
                              <div className="text-xs text-gray-400 mt-0.5">{typeInfo?.name}</div>
                              {place.notes && (
                                <div className="text-[10px] text-gray-500 mt-1 italic">"{place.notes}"</div>
                              )}
                              <div className="text-[10px] text-gray-500 mt-1">
                                {place.lat.toFixed(4)}, {place.lng.toFixed(4)}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => { setMapCenter([place.lat, place.lng]); setMapZoom(13); }}
                              className="text-gray-400 hover:text-white h-8 w-8 p-0"
                            >
                              <Navigation2 className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => setEditingPlace(place)}
                              className="text-blue-400 hover:text-blue-300 h-8 w-8 p-0"
                            >
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => deletePlace(place.id)}
                              className="text-red-400 hover:text-red-300 h-8 w-8 p-0"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
            
            {/* Carte des lieux */}
            <div className="flex-1 relative">
              <MapContainer center={mapCenter} zoom={8} className="h-full w-full" zoomControl={false}>
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                <MapController center={mapCenter} zoom={mapZoom} />
                
                {userPosition && (
                  <Marker position={[userPosition.lat, userPosition.lng]} icon={createCustomIcon('#3b82f6', 'user')}>
                    <Popup><b>Ma position</b></Popup>
                  </Marker>
                )}
                
                {savedPlaces.map(place => {
                  const typeInfo = PLACE_TYPES.find(t => t.id === place.type);
                  return (
                    <Marker 
                      key={place.id} 
                      position={[place.lat, place.lng]} 
                      icon={createCustomIcon(typeInfo?.color || '#6b7280', 'place')}
                    >
                      <Popup>
                        <div className="text-center min-w-[150px]">
                          <div className="text-lg mb-1">{typeInfo?.icon}</div>
                          <div className="font-bold">{place.name}</div>
                          <div className="text-xs text-gray-500">{typeInfo?.name}</div>
                          {place.notes && <div className="text-xs mt-1 italic">"{place.notes}"</div>}
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MapContainer>
              
              {/* Légende */}
              <div className="absolute bottom-4 left-4 z-[1000] bg-black/90 backdrop-blur-sm rounded-lg border border-gray-700 p-3">
                <div className="text-[10px] text-gray-400 uppercase mb-2">Types de lieux</div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                  {PLACE_TYPES.slice(0, 6).map(type => (
                    <div key={type.id} className="flex items-center gap-2 text-xs">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: type.color }} />
                      <span className="text-gray-300">{type.icon} {type.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Dialog d'édition de lieu */}
      {editingPlace && (
        <Dialog open={!!editingPlace} onOpenChange={() => setEditingPlace(null)}>
          <DialogContent className="bg-gray-900 border-gray-700">
            <DialogHeader>
              <DialogTitle className="text-white">Modifier le lieu</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label className="text-gray-300">Nom du lieu</Label>
                <Input 
                  value={editingPlace.name}
                  className="bg-gray-800 border-gray-700 text-white"
                  onChange={(e) => setEditingPlace(p => ({ ...p, name: e.target.value }))} 
                />
              </div>
              <div>
                <Label className="text-gray-300">Type</Label>
                <Select value={editingPlace.type} onValueChange={(v) => setEditingPlace(p => ({ ...p, type: v }))}>
                  <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    {PLACE_TYPES.map(type => (
                      <SelectItem key={type.id} value={type.id} className="text-white">{type.icon} {type.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-gray-300">Notes</Label>
                <Input 
                  value={editingPlace.notes || ''}
                  className="bg-gray-800 border-gray-700 text-white"
                  onChange={(e) => setEditingPlace(p => ({ ...p, notes: e.target.value }))} 
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditingPlace(null)} className="border-gray-700">Annuler</Button>
              <Button onClick={handleUpdatePlace} className="bg-blue-600 hover:bg-blue-700 text-white">Sauvegarder</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      
      {/* Dialog contrôlé pour ajouter un waypoint (accessible depuis le bouton rapide) */}
      <Dialog open={showAddWaypointDialog} onOpenChange={setShowAddWaypointDialog}>
        <DialogContent className="bg-gray-900 border-gray-700 z-[9999]">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <MapPin className="h-5 w-5 text-[#f5a623]" />
              Nouveau waypoint
            </DialogTitle>
            <DialogDescription className="text-gray-400">
              Créez un point d'intérêt pour générer automatiquement des zones d'analyse BIONIC™
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label className="text-gray-300">Nom du waypoint</Label>
              <Input 
                placeholder="Ex: Affût secteur nord" 
                className="bg-gray-800 border-gray-700 text-white mt-1" 
                value={newWaypoint.name}
                onChange={(e) => setNewWaypoint(p => ({ ...p, name: e.target.value }))} 
              />
            </div>
            <div>
              <Label className="text-gray-300">Type</Label>
              <Select value={newWaypoint.type} onValueChange={(v) => setNewWaypoint(p => ({ ...p, type: v }))}>
                <SelectTrigger className="bg-gray-800 border-gray-700 text-white mt-1">
                  <SelectValue placeholder="Sélectionner un type" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {PLACE_TYPES.map(type => (
                    <SelectItem key={type.id} value={type.id} className="text-white">{type.icon} {type.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label className="text-gray-300">Latitude</Label>
                <Input 
                  placeholder="46.8139" 
                  className="bg-gray-800 border-gray-700 text-white mt-1" 
                  value={newWaypoint.lat}
                  onChange={(e) => setNewWaypoint(p => ({ ...p, lat: e.target.value }))} 
                />
              </div>
              <div>
                <Label className="text-gray-300">Longitude</Label>
                <Input 
                  placeholder="-71.2080" 
                  className="bg-gray-800 border-gray-700 text-white mt-1" 
                  value={newWaypoint.lng}
                  onChange={(e) => setNewWaypoint(p => ({ ...p, lng: e.target.value }))} 
                />
              </div>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={useCurrentPositionForNewWaypoint} 
              className="w-full border-gray-700 text-gray-300 hover:bg-gray-800"
            >
              <LocateFixed className="h-4 w-4 mr-2" /> Utiliser ma position actuelle
            </Button>
            <div className="bg-[#f5a623]/10 border border-[#f5a623]/30 rounded-lg p-3">
              <p className="text-xs text-[#f5a623]">
                💡 Astuce : Un waypoint actif génère automatiquement des zones d'analyse BIONIC™ autour de sa position.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-gray-700" onClick={() => setShowAddWaypointDialog(false)}>
              Annuler
            </Button>
            <Button 
              onClick={handleAddWaypointFromDialog} 
              className="bg-[#f5a623] hover:bg-[#f5a623]/90 text-black"
              data-testid="confirm-add-waypoint-btn"
            >
              <Plus className="h-4 w-4 mr-1" /> Ajouter le waypoint
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Dialog de partage de waypoint */}
      <ShareWaypointDialog
        open={showShareDialog}
        onOpenChange={setShowShareDialog}
        waypoint={waypointToShare}
        userId={userId}
        onShared={() => {
          setShowShareDialog(false);
          setWaypointToShare(null);
        }}
      />
      
      {/* Dialog de création de groupe */}
      <CreateGroupDialog
        open={showCreateGroupDialog}
        onOpenChange={setShowCreateGroupDialog}
        userId={userId}
        onCreated={(group) => {
          toast.success(`Groupe "${group.name}" créé !`, {
            description: `Code d'invitation: ${group.invite_code}`
          });
          refreshGroups(); // Rafraîchir la liste des groupes
        }}
      />
      
      {/* Tableau de bord du groupe (tracking live + chat) */}
      {showGroupDashboard && selectedGroup && (
        <Dialog open={showGroupDashboard} onOpenChange={setShowGroupDashboard}>
          <DialogContent className="bg-gray-900 border-gray-700 max-w-4xl max-h-[90vh] p-0 overflow-hidden">
            <GroupDashboard 
              group={selectedGroup}
              userId={userId}
              onClose={() => {
                setShowGroupDashboard(false);
                setSelectedGroup(null);
              }}
              initialTab="map"
            />
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default MonTerritoireBionicPage;
