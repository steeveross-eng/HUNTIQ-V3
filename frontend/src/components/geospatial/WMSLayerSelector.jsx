/**
 * HUNTIQ V3 - BIONIC™ WMS Layer Selector
 * 
 * Composant de sélection et gestion des couches WMS
 * - Affiche les 23+ couches disponibles via le proxy
 * - Multi-sélection avec toggle individuel
 * - Gestion de l'opacité par couche
 * - Organisation par catégorie de source
 * - Préréglages par espèce de gibier
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Layers, ChevronDown, ChevronUp, Search, Eye, EyeOff,
  Mountain, Droplets, Trees, Map, Satellite, Globe,
  CloudRain, Compass, Database, Loader2, AlertCircle,
  GripVertical, Minus, Plus, RefreshCw, X, Check, Target
} from 'lucide-react';
import { motion, AnimatePresence, Reorder } from 'framer-motion';
import { api } from '@/services/api.client';

// ============================================================================
// SPECIES LAYER PRESETS - Préréglages de couches par espèce de gibier
// ============================================================================
const SPECIES_PRESETS = {
  moose: {
    name: 'Orignal',
    icon: '🫎',
    description: 'Hydrologie + Forêt + Terrain - Habitat idéal de l\'orignal',
    layers: [
      'wms-grhq-rivers',     // Cours d'eau
      'wms-grhq-lakes',      // Lacs
      'wms-grhq-wetlands',   // Milieux humides
      'wms-forest-stands',   // Peuplements forestiers
      'wms-lidar-dtm',       // Terrain (élévation)
    ],
    opacities: {
      'wms-grhq-rivers': 0.8,
      'wms-grhq-lakes': 0.7,
      'wms-grhq-wetlands': 0.8,
      'wms-forest-stands': 0.6,
      'wms-lidar-dtm': 0.5,
    }
  },
  deer: {
    name: 'Cerf de Virginie',
    icon: '🦌',
    description: 'Forêt mixte + Terrain + Routes - Zones de ravage',
    layers: [
      'wms-forest-stands',   // Peuplements forestiers
      'wms-forest-species',  // Espèces d'arbres
      'wms-lidar-dtm',       // Terrain
      'wms-grhq-rivers',     // Cours d'eau (abreuvement)
      'wms-osm-osm',         // Routes et sentiers
    ],
    opacities: {
      'wms-forest-stands': 0.7,
      'wms-forest-species': 0.6,
      'wms-lidar-dtm': 0.5,
      'wms-grhq-rivers': 0.7,
      'wms-osm-osm': 0.4,
    }
  },
  bear: {
    name: 'Ours noir',
    icon: '🐻',
    description: 'Forêt + Hydrologie + Terrain accidenté',
    layers: [
      'wms-forest-stands',   // Peuplements forestiers
      'wms-grhq-rivers',     // Cours d'eau
      'wms-grhq-wetlands',   // Milieux humides
      'wms-lidar-dtm',       // Terrain
      'wms-nasa_gibs-modis_terra', // Vue satellite
    ],
    opacities: {
      'wms-forest-stands': 0.7,
      'wms-grhq-rivers': 0.7,
      'wms-grhq-wetlands': 0.6,
      'wms-lidar-dtm': 0.5,
      'wms-nasa_gibs-modis_terra': 0.4,
    }
  },
  waterfowl: {
    name: 'Sauvagine',
    icon: '🦆',
    description: 'Milieux humides + Lacs + Bassins versants',
    layers: [
      'wms-grhq-wetlands',   // Milieux humides (priorité)
      'wms-grhq-lakes',      // Lacs
      'wms-grhq-rivers',     // Cours d'eau
      'wms-hydrosheds-basins', // Bassins versants
      'wms-nasa_gibs-modis_terra', // Vue satellite
    ],
    opacities: {
      'wms-grhq-wetlands': 0.9,
      'wms-grhq-lakes': 0.8,
      'wms-grhq-rivers': 0.7,
      'wms-hydrosheds-basins': 0.5,
      'wms-nasa_gibs-modis_terra': 0.3,
    }
  },
  turkey: {
    name: 'Dindon sauvage',
    icon: '🦃',
    description: 'Forêt mixte + Terrain + Agriculture',
    layers: [
      'wms-forest-stands',   // Peuplements
      'wms-forest-species',  // Espèces
      'wms-lidar-dtm',       // Terrain
      'wms-osm-osm',         // Routes/champs
      'wms-nasa_gibs-modis_terra', // Vue satellite
    ],
    opacities: {
      'wms-forest-stands': 0.6,
      'wms-forest-species': 0.6,
      'wms-lidar-dtm': 0.5,
      'wms-osm-osm': 0.5,
      'wms-nasa_gibs-modis_terra': 0.4,
    }
  },
  smallgame: {
    name: 'Petit gibier',
    icon: '🐰',
    description: 'Forêt dense + Milieux humides',
    layers: [
      'wms-forest-stands',   // Peuplements
      'wms-grhq-wetlands',   // Milieux humides
      'wms-grhq-rivers',     // Cours d'eau
      'wms-lidar-chm',       // Canopée (couvert)
    ],
    opacities: {
      'wms-forest-stands': 0.7,
      'wms-grhq-wetlands': 0.7,
      'wms-grhq-rivers': 0.6,
      'wms-lidar-chm': 0.5,
    }
  }
};

// Icon mapping by source type
const SOURCE_ICONS = {
  sigeom: { icon: Compass, color: 'text-purple-400', bg: 'bg-purple-500/20' },
  lidar: { icon: Mountain, color: 'text-orange-400', bg: 'bg-orange-500/20' },
  grhq: { icon: Droplets, color: 'text-blue-400', bg: 'bg-blue-500/20' },
  forest: { icon: Trees, color: 'text-green-400', bg: 'bg-green-500/20' },
  hydrosheds: { icon: Droplets, color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
  osm: { icon: Map, color: 'text-gray-400', bg: 'bg-gray-500/20' },
  canvec: { icon: Globe, color: 'text-indigo-400', bg: 'bg-indigo-500/20' },
  usgs: { icon: Mountain, color: 'text-amber-400', bg: 'bg-amber-500/20' },
  noaa: { icon: CloudRain, color: 'text-sky-400', bg: 'bg-sky-500/20' },
  nasa_gibs: { icon: Satellite, color: 'text-violet-400', bg: 'bg-violet-500/20' },
  sentinel_hub: { icon: Satellite, color: 'text-emerald-400', bg: 'bg-emerald-500/20' },
  default: { icon: Database, color: 'text-gray-400', bg: 'bg-gray-500/20' }
};

// Source display names
const SOURCE_NAMES = {
  sigeom: 'SIGÉOM (Géologie)',
  lidar: 'LiDAR Québec',
  grhq: 'GRHQ (Hydrographie)',
  forest: 'MFFP (Forêt)',
  hydrosheds: 'HydroSHEDS',
  osm: 'OpenStreetMap',
  canvec: 'CanVec (NRCan)',
  usgs: 'USGS',
  noaa: 'NOAA',
  nasa_gibs: 'NASA GIBS',
  sentinel_hub: 'Sentinel Hub'
};

// Layer display names
const LAYER_DISPLAY_NAMES = {
  // SIGÉOM
  bedrock: 'Géologie du socle',
  surficial: 'Dépôts de surface',
  faults: 'Failles géologiques',
  // LiDAR
  dtm: 'Terrain (DTM)',
  dsm: 'Surface (DSM)',
  chm: 'Canopée (CHM)',
  // GRHQ
  rivers: 'Cours d\'eau',
  lakes: 'Lacs',
  wetlands: 'Milieux humides',
  watersheds: 'Bassins versants',
  // Forest
  stands: 'Peuplements',
  species: 'Espèces',
  age: 'Âge',
  // HydroSHEDS
  basins: 'Bassins',
  // OSM
  osm: 'Carte OSM',
  // CanVec
  hydro: 'Hydrographie',
  transport: 'Transport',
  admin: 'Limites admin.',
  // USGS
  topo: 'Topographie',
  // NOAA
  radar: 'Radar météo',
  // NASA
  modis_terra: 'MODIS Terra',
  viirs: 'VIIRS',
  // Sentinel
  true_color: 'Couleur réelle',
  ndvi: 'NDVI'
};

/**
 * Individual layer item component
 */
const LayerItem = ({ 
  layer, 
  isActive, 
  opacity,
  onToggle, 
  onOpacityChange,
  onMoveUp,
  onMoveDown,
  canMoveUp,
  canMoveDown
}) => {
  const [showOpacity, setShowOpacity] = useState(false);
  const sourceInfo = SOURCE_ICONS[layer.sourceId] || SOURCE_ICONS.default;
  const Icon = sourceInfo.icon;
  
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className={`
        p-3 rounded-sm border transition-all group
        ${isActive 
          ? 'bg-[#f5a623]/10 border-[#f5a623]/30' 
          : 'bg-black/30 border-white/5 hover:border-white/15'
        }
      `}
    >
      <div className="flex items-center gap-3">
        {/* Drag handle (visible on active layers) */}
        {isActive && (
          <div className="flex flex-col gap-0.5 opacity-30 hover:opacity-70 cursor-grab">
            <button 
              onClick={onMoveUp} 
              disabled={!canMoveUp}
              className="p-0.5 hover:bg-white/10 rounded disabled:opacity-30"
            >
              <ChevronUp className="h-3 w-3 text-gray-400" />
            </button>
            <button 
              onClick={onMoveDown} 
              disabled={!canMoveDown}
              className="p-0.5 hover:bg-white/10 rounded disabled:opacity-30"
            >
              <ChevronDown className="h-3 w-3 text-gray-400" />
            </button>
          </div>
        )}
        
        {/* Icon */}
        <div className={`w-8 h-8 rounded-sm flex items-center justify-center ${sourceInfo.bg}`}>
          <Icon className={`h-4 w-4 ${sourceInfo.color}`} />
        </div>
        
        {/* Layer info */}
        <div className="flex-1 min-w-0">
          <p className="text-sm text-white font-medium truncate">
            {layer.displayName}
          </p>
          <p className="text-xs text-gray-500 truncate">
            {layer.sourceName}
          </p>
        </div>
        
        {/* Toggle */}
        <Switch
          checked={isActive}
          onCheckedChange={onToggle}
          className="data-[state=checked]:bg-[#f5a623]"
        />
      </div>
      
      {/* Opacity control (when active) */}
      {isActive && (
        <motion.div 
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          className="mt-3 pt-3 border-t border-white/5"
        >
          <div className="flex items-center gap-3">
            <Eye className="h-3 w-3 text-gray-500" />
            <span className="text-xs text-gray-400 w-16">Opacité</span>
            <Slider
              value={[opacity * 100]}
              onValueChange={(value) => onOpacityChange(value[0] / 100)}
              max={100}
              step={5}
              className="flex-1"
            />
            <span className="text-xs text-gray-400 w-8 text-right">
              {Math.round(opacity * 100)}%
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

/**
 * Source group component
 */
const SourceGroup = ({ 
  sourceId, 
  layers, 
  activeLayers,
  layerOpacities,
  onToggleLayer,
  onOpacityChange,
  onMoveLayer 
}) => {
  const [expanded, setExpanded] = useState(true);
  const sourceInfo = SOURCE_ICONS[sourceId] || SOURCE_ICONS.default;
  const Icon = sourceInfo.icon;
  const activeCount = layers.filter(l => activeLayers.includes(l.id)).length;
  
  return (
    <div className="border border-white/5 rounded-sm overflow-hidden">
      {/* Group header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 flex items-center justify-between bg-black/40 hover:bg-black/60 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className={`h-4 w-4 ${sourceInfo.color}`} />
          <span className="text-sm text-white font-medium">
            {SOURCE_NAMES[sourceId] || sourceId}
          </span>
          {activeCount > 0 && (
            <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-xs">
              {activeCount}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">{layers.length} couches</span>
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          )}
        </div>
      </button>
      
      {/* Layers */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="p-2 space-y-2 bg-black/20">
              {layers.map((layer, index) => {
                const isActive = activeLayers.includes(layer.id);
                const activeIndex = activeLayers.indexOf(layer.id);
                
                return (
                  <LayerItem
                    key={layer.id}
                    layer={layer}
                    isActive={isActive}
                    opacity={layerOpacities[layer.id] || 0.7}
                    onToggle={() => onToggleLayer(layer)}
                    onOpacityChange={(opacity) => onOpacityChange(layer.id, opacity)}
                    onMoveUp={() => onMoveLayer(layer.id, -1)}
                    onMoveDown={() => onMoveLayer(layer.id, 1)}
                    canMoveUp={isActive && activeIndex > 0}
                    canMoveDown={isActive && activeIndex < activeLayers.length - 1}
                  />
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

/**
 * Species Preset Selector Component
 */
const SpeciesPresetSelector = ({ 
  onApplyPreset, 
  currentPreset, 
  disabled 
}) => {
  const [selectedSpecies, setSelectedSpecies] = useState(currentPreset || '');
  
  const handlePresetChange = (speciesKey) => {
    setSelectedSpecies(speciesKey);
    if (speciesKey && SPECIES_PRESETS[speciesKey]) {
      onApplyPreset(speciesKey, SPECIES_PRESETS[speciesKey]);
    }
  };
  
  return (
    <div className="p-3 bg-gradient-to-r from-[#f5a623]/10 to-transparent rounded-sm border border-[#f5a623]/20 mb-3">
      <div className="flex items-center gap-2 mb-2">
        <Target className="h-4 w-4 text-[#f5a623]" />
        <span className="text-sm font-medium text-white">Préréglage par gibier</span>
      </div>
      
      <Select value={selectedSpecies} onValueChange={handlePresetChange} disabled={disabled}>
        <SelectTrigger className="bg-black/40 border-white/10 text-white h-9">
          <SelectValue placeholder="Sélectionner une espèce..." />
        </SelectTrigger>
        <SelectContent className="bg-[#1a1a1a] border-white/10">
          {Object.entries(SPECIES_PRESETS).map(([key, preset]) => (
            <SelectItem key={key} value={key} className="text-white">
              <div className="flex items-center gap-2">
                <span className="text-lg">{preset.icon}</span>
                <span>{preset.name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {selectedSpecies && SPECIES_PRESETS[selectedSpecies] && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 text-xs text-gray-400"
        >
          <p>{SPECIES_PRESETS[selectedSpecies].description}</p>
          <p className="mt-1 text-[#f5a623]">
            {SPECIES_PRESETS[selectedSpecies].layers.length} couches activées
          </p>
        </motion.div>
      )}
    </div>
  );
};

/**
 * Main WMS Layer Selector Component
 */
const WMSLayerSelector = ({ 
  map,
  mapLoaded,
  onLayerChange,
  position = 'left',
  initialExpanded = true
}) => {
  const [expanded, setExpanded] = useState(initialExpanded);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wmsConfig, setWmsConfig] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPreset, setCurrentPreset] = useState('');
  
  // Active layers (order matters for z-index)
  const [activeLayers, setActiveLayers] = useState([]);
  const [layerOpacities, setLayerOpacities] = useState({});
  
  // Fetch WMS configuration from backend
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const response = await api.get('/api/geospatial/wms/maplibre-config');
        
        if (response.data?.sources && response.data?.layers) {
          // Get backend URL for building absolute tile URLs
          const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
          
          // Process sources to use absolute URLs
          const processedSources = {};
          Object.entries(response.data.sources).forEach(([sourceKey, sourceConfig]) => {
            processedSources[sourceKey] = {
              ...sourceConfig,
              tiles: sourceConfig.tiles?.map(tileUrl => {
                // If URL is relative, prepend backend URL
                if (tileUrl.startsWith('/')) {
                  return `${backendUrl}${tileUrl}`;
                }
                return tileUrl;
              })
            };
          });
          
          // Process the layers config
          const processedLayers = response.data.layers.map(layer => {
            const sourceId = layer.metadata?.wms_source || 'unknown';
            const layerKey = layer.metadata?.wms_layer || layer.id;
            
            return {
              id: layer.id,
              sourceId,
              layerKey,
              displayName: LAYER_DISPLAY_NAMES[layerKey] || layer.metadata?.display_name || layerKey,
              sourceName: SOURCE_NAMES[sourceId] || sourceId,
              sourceConfig: processedSources[layer.source],
              layerConfig: layer
            };
          });
          
          setWmsConfig({
            sources: processedSources,
            layers: processedLayers
          });
        }
        setError(null);
      } catch (err) {
        console.error('Failed to fetch WMS config:', err);
        setError('Impossible de charger les couches WMS');
      } finally {
        setLoading(false);
      }
    };
    
    fetchConfig();
  }, []);
  
  // Group layers by source
  const groupedLayers = wmsConfig?.layers?.reduce((acc, layer) => {
    if (!acc[layer.sourceId]) {
      acc[layer.sourceId] = [];
    }
    acc[layer.sourceId].push(layer);
    return acc;
  }, {}) || {};
  
  // Filter layers by search
  const filteredGroups = Object.entries(groupedLayers).reduce((acc, [sourceId, layers]) => {
    if (!searchQuery) {
      acc[sourceId] = layers;
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = layers.filter(l => 
        l.displayName.toLowerCase().includes(query) ||
        l.sourceName.toLowerCase().includes(query)
      );
      if (filtered.length > 0) {
        acc[sourceId] = filtered;
      }
    }
    return acc;
  }, {});
  
  // Add layer to map with error handling
  const addLayerToMap = useCallback((layer) => {
    if (!map || !mapLoaded || !layer?.sourceConfig) return false;
    
    try {
      // Check if source exists
      if (!map.getSource(layer.layerConfig.source)) {
        map.addSource(layer.layerConfig.source, layer.sourceConfig);
      }
      
      // Add layer if not exists
      if (!map.getLayer(layer.id)) {
        map.addLayer({
          ...layer.layerConfig,
          layout: {
            ...layer.layerConfig.layout,
            visibility: 'visible'
          },
          paint: {
            ...layer.layerConfig.paint,
            'raster-opacity': layerOpacities[layer.id] || 0.7
          }
        });
        
        // Add error handler for the layer
        map.on('error', (e) => {
          if (e.sourceId === layer.layerConfig.source) {
            console.warn(`WMS layer error (${layer.displayName}):`, e.error?.message || 'Source indisponible');
          }
        });
      } else {
        map.setLayoutProperty(layer.id, 'visibility', 'visible');
      }
      return true;
    } catch (err) {
      console.warn(`Failed to add layer ${layer.id}:`, err.message);
      return false;
    }
  }, [map, mapLoaded, layerOpacities]);
  
  // Remove layer from map
  const removeLayerFromMap = useCallback((layerId) => {
    if (!map || !mapLoaded) return;
    
    try {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(layerId, 'visibility', 'none');
      }
    } catch (err) {
      console.warn(`Failed to hide layer ${layerId}:`, err.message);
    }
  }, [map, mapLoaded]);
  
  // Toggle layer
  const handleToggleLayer = useCallback((layer) => {
    const isActive = activeLayers.includes(layer.id);
    
    if (isActive) {
      // Remove layer
      removeLayerFromMap(layer.id);
      setActiveLayers(prev => prev.filter(id => id !== layer.id));
    } else {
      // Add layer
      addLayerToMap(layer);
      setActiveLayers(prev => [...prev, layer.id]);
    }
    
    if (onLayerChange) {
      onLayerChange(isActive ? 'remove' : 'add', layer.id);
    }
  }, [activeLayers, addLayerToMap, removeLayerFromMap, onLayerChange]);
  
  // Change layer opacity
  const handleOpacityChange = useCallback((layerId, opacity) => {
    setLayerOpacities(prev => ({ ...prev, [layerId]: opacity }));
    
    if (map && map.getLayer(layerId)) {
      map.setPaintProperty(layerId, 'raster-opacity', opacity);
    }
  }, [map]);
  
  // Reorder layers (z-index)
  const handleMoveLayer = useCallback((layerId, direction) => {
    setActiveLayers(prev => {
      const index = prev.indexOf(layerId);
      if (index === -1) return prev;
      
      const newIndex = index + direction;
      if (newIndex < 0 || newIndex >= prev.length) return prev;
      
      const newOrder = [...prev];
      [newOrder[index], newOrder[newIndex]] = [newOrder[newIndex], newOrder[index]];
      
      // Update z-order on map
      if (map && mapLoaded) {
        // Move layer in MapLibre
        const layer = wmsConfig?.layers?.find(l => l.id === layerId);
        if (layer && map.getLayer(layerId)) {
          const beforeLayerId = direction > 0 ? newOrder[newIndex + 1] : newOrder[newIndex - 1];
          if (beforeLayerId && map.getLayer(beforeLayerId)) {
            map.moveLayer(layerId, beforeLayerId);
          }
        }
      }
      
      return newOrder;
    });
  }, [map, mapLoaded, wmsConfig]);
  
  // Clear all layers
  const handleClearAll = useCallback(() => {
    activeLayers.forEach(layerId => {
      removeLayerFromMap(layerId);
    });
    setActiveLayers([]);
    setCurrentPreset('');
  }, [activeLayers, removeLayerFromMap]);
  
  // Apply species preset
  const handleApplyPreset = useCallback((speciesKey, preset) => {
    if (!wmsConfig?.layers || !preset) return;
    
    // Clear existing layers first
    activeLayers.forEach(layerId => {
      removeLayerFromMap(layerId);
    });
    
    // Small delay to let map update before adding new layers
    setTimeout(() => {
      // Find and activate preset layers
      const newActiveLayers = [];
      const newOpacities = { ...layerOpacities };
      
      preset.layers.forEach(presetLayerId => {
        const layer = wmsConfig.layers.find(l => l.id === presetLayerId);
        if (layer) {
          try {
            addLayerToMap(layer);
            newActiveLayers.push(layer.id);
            // Apply preset opacity
            if (preset.opacities && preset.opacities[presetLayerId]) {
              newOpacities[layer.id] = preset.opacities[presetLayerId];
              // Delay opacity setting to ensure layer is added
              setTimeout(() => {
                try {
                  if (map && map.getLayer(layer.id)) {
                    map.setPaintProperty(layer.id, 'raster-opacity', preset.opacities[presetLayerId]);
                  }
                } catch (e) {
                  console.warn('Opacity set error:', e.message);
                }
              }, 100);
            }
          } catch (e) {
            console.warn(`Preset layer ${presetLayerId} error:`, e.message);
          }
        }
      });
      
      setActiveLayers(newActiveLayers);
      setLayerOpacities(newOpacities);
      setCurrentPreset(speciesKey);
      
      // Notify parent
      if (onLayerChange) {
        onLayerChange('preset', speciesKey);
      }
    }, 50);
  }, [wmsConfig, activeLayers, layerOpacities, addLayerToMap, removeLayerFromMap, map, onLayerChange]);
  
  // Panel position styles
  const positionStyles = position === 'left' 
    ? 'left-4 top-4'
    : 'right-4 top-4';
  
  return (
    <Card className={`absolute ${positionStyles} z-10 w-72 max-h-[calc(100vh-250px)] bg-black/95 border-white/10 backdrop-blur-md shadow-xl overflow-hidden`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-[#f5a623]" />
            <CardTitle className="text-sm text-white">Couches WMS BIONIC™</CardTitle>
          </div>
          <div className="flex items-center gap-1">
            {activeLayers.length > 0 && (
              <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-xs mr-2">
                {activeLayers.length} active{activeLayers.length > 1 ? 's' : ''}
              </Badge>
            )}
            <Button
              size="sm"
              variant="ghost"
              className="h-6 w-6 p-0 text-gray-400 hover:text-white"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <Minus className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <CardContent className="pt-2">
              {/* Species Preset Selector */}
              <SpeciesPresetSelector
                onApplyPreset={handleApplyPreset}
                currentPreset={currentPreset}
                disabled={loading}
              />
              
              {/* Base Map Selector */}
              <div className="mb-3 pb-3 border-b border-white/5">
                <label className="text-xs text-gray-400 block mb-2">Fond de carte</label>
                <Select 
                  defaultValue="voyager"
                  onValueChange={(value) => {
                    if (!map) return;
                    
                    // Base map configurations with proper attributions
                    const baseConfigs = {
                      voyager: {
                        url: 'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}@2x.png',
                        attribution: '© CARTO © OpenStreetMap'
                      },
                      light: {
                        url: 'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
                        attribution: '© CARTO'
                      },
                      dark: {
                        url: 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
                        attribution: '© CARTO'
                      },
                      satellite: {
                        url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                        attribution: '© Google'
                      },
                      osm: {
                        url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                        attribution: '© OpenStreetMap contributors'
                      },
                      terrain: {
                        url: 'https://tile.opentopomap.org/{z}/{x}/{y}.png',
                        attribution: '© OpenTopoMap (CC-BY-SA)'
                      }
                    };
                    
                    const config = baseConfigs[value];
                    if (!config) return;
                    
                    try {
                      // Remove old source and layer
                      if (map.getLayer('base-layer')) {
                        map.removeLayer('base-layer');
                      }
                      if (map.getSource('base-tiles')) {
                        map.removeSource('base-tiles');
                      }
                      
                      // Add new source
                      map.addSource('base-tiles', {
                        type: 'raster',
                        tiles: [config.url],
                        tileSize: 256,
                        attribution: config.attribution
                      });
                      
                      // Add new layer at bottom
                      const firstLayerId = map.getStyle().layers[0]?.id;
                      map.addLayer({
                        id: 'base-layer',
                        type: 'raster',
                        source: 'base-tiles',
                        minzoom: 0,
                        maxzoom: 20
                      }, firstLayerId);
                      
                      console.log('Base map changed to:', value);
                    } catch (err) {
                      console.error('Error changing base map:', err);
                    }
                  }}
                >
                  <SelectTrigger className="bg-black/40 border-white/10 text-white text-sm h-9">
                    <SelectValue placeholder="Choisir un style" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1a1a1a] border-white/10">
                    <SelectItem value="voyager" className="text-white">
                      <div className="flex items-center gap-2">
                        <Map className="h-4 w-4 text-blue-400" />
                        Voyager (Couleur)
                      </div>
                    </SelectItem>
                    <SelectItem value="light" className="text-white">
                      <div className="flex items-center gap-2">
                        <Map className="h-4 w-4 text-gray-300" />
                        Clair (Positron)
                      </div>
                    </SelectItem>
                    <SelectItem value="dark" className="text-white">
                      <div className="flex items-center gap-2">
                        <Map className="h-4 w-4 text-gray-600" />
                        Sombre
                      </div>
                    </SelectItem>
                    <SelectItem value="satellite" className="text-white">
                      <div className="flex items-center gap-2">
                        <Satellite className="h-4 w-4 text-green-400" />
                        Satellite
                      </div>
                    </SelectItem>
                    <SelectItem value="osm" className="text-white">
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4 text-orange-400" />
                        OpenStreetMap
                      </div>
                    </SelectItem>
                    <SelectItem value="terrain" className="text-white">
                      <div className="flex items-center gap-2">
                        <Mountain className="h-4 w-4 text-amber-400" />
                        Terrain (Stadia)
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {/* Search */}
              <div className="relative mb-3">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Rechercher une couche..."
                  className="pl-9 bg-black/40 border-white/10 text-white text-sm h-9"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    <X className="h-4 w-4 text-gray-500 hover:text-white" />
                  </button>
                )}
              </div>
              
              {/* Actions */}
              {activeLayers.length > 0 && (
                <div className="flex items-center justify-between mb-3 pb-3 border-b border-white/5">
                  <span className="text-xs text-gray-400">
                    {currentPreset && SPECIES_PRESETS[currentPreset] ? (
                      <span className="flex items-center gap-1">
                        <span>{SPECIES_PRESETS[currentPreset].icon}</span>
                        <span>{SPECIES_PRESETS[currentPreset].name}</span>
                      </span>
                    ) : (
                      `${activeLayers.length} couche${activeLayers.length > 1 ? 's' : ''} active${activeLayers.length > 1 ? 's' : ''}`
                    )}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleClearAll}
                    className="h-7 px-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Tout effacer
                  </Button>
                </div>
              )}
              
              {/* Loading state */}
              {loading && (
                <div className="flex flex-col items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 text-[#f5a623] animate-spin mb-2" />
                  <p className="text-gray-400 text-sm">Chargement des couches...</p>
                </div>
              )}
              
              {/* Error state */}
              {error && (
                <div className="flex flex-col items-center justify-center py-8">
                  <AlertCircle className="h-6 w-6 text-red-400 mb-2" />
                  <p className="text-red-400 text-sm">{error}</p>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => window.location.reload()}
                    className="mt-3 border-white/20"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Réessayer
                  </Button>
                </div>
              )}
              
              {/* Layer groups */}
              {!loading && !error && (
                <ScrollArea className="h-[280px] pr-2">
                  <div className="space-y-2">
                    {Object.entries(filteredGroups).map(([sourceId, layers]) => (
                      <SourceGroup
                        key={sourceId}
                        sourceId={sourceId}
                        layers={layers}
                        activeLayers={activeLayers}
                        layerOpacities={layerOpacities}
                        onToggleLayer={handleToggleLayer}
                        onOpacityChange={handleOpacityChange}
                        onMoveLayer={handleMoveLayer}
                      />
                    ))}
                    
                    {Object.keys(filteredGroups).length === 0 && searchQuery && (
                      <div className="text-center py-8">
                        <Search className="h-8 w-8 text-gray-600 mx-auto mb-2" />
                        <p className="text-gray-400 text-sm">Aucune couche trouvée</p>
                        <p className="text-gray-600 text-xs mt-1">
                          Essayez un autre terme de recherche
                        </p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              )}
              
              {/* Footer info */}
              <div className="mt-3 pt-3 border-t border-white/5">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{wmsConfig?.layers?.length || 0} couches disponibles</span>
                  <span>Données: Open Data Québec</span>
                </div>
              </div>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export default WMSLayerSelector;
