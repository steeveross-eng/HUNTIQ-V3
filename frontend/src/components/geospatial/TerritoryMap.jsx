/**
 * HUNTIQ V3 - BIONIC™ Territory Map Component
 * Interactive map using MapLibre GL (open-source)
 * Displays Quebec government WMS layers
 */

import { useRef, useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import {
  Layers, Map, Mountain, Droplets, Trees, Compass, Target,
  Crosshair, MapPin, Plus, Minus, Loader2, AlertCircle, Maximize2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import useMapLibre, { 
  addWMSLayer, 
  addMarker, 
  toggleLayerVisibility,
  QUEBEC_WMS_LAYERS,
  QUEBEC_CENTER 
} from '@/lib/maplibre';
import WMSLayerSelector from './WMSLayerSelector';

// Layer configuration with icons
const AVAILABLE_LAYERS = [
  { 
    ...QUEBEC_WMS_LAYERS.lidar, 
    icon: Mountain, 
    color: 'text-orange-400',
    description: 'Modèle numérique d\'élévation'
  },
  { 
    ...QUEBEC_WMS_LAYERS.hydro_rivers, 
    icon: Droplets, 
    color: 'text-blue-400',
    description: 'Rivières et ruisseaux'
  },
  { 
    ...QUEBEC_WMS_LAYERS.hydro_lakes, 
    icon: Droplets, 
    color: 'text-cyan-400',
    description: 'Lacs et plans d\'eau'
  },
  { 
    ...QUEBEC_WMS_LAYERS.hydro_wetlands, 
    icon: Droplets, 
    color: 'text-teal-400',
    description: 'Marais et tourbières'
  },
  { 
    ...QUEBEC_WMS_LAYERS.forest, 
    icon: Trees, 
    color: 'text-green-400',
    description: 'Inventaire écoforestier'
  },
  { 
    ...QUEBEC_WMS_LAYERS.geology_bedrock, 
    icon: Compass, 
    color: 'text-purple-400',
    description: 'Géologie du socle rocheux'
  }
];

// Layer panel component
const LayerPanel = ({ layers, activeLayers, onToggle, onOpacityChange }) => {
  const [expanded, setExpanded] = useState(true);

  return (
    <Card className="absolute left-4 top-4 z-10 w-72 bg-black/90 border-white/10 backdrop-blur-sm">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-[#f5a623]" />
            <CardTitle className="text-sm text-white">Couches BIONIC™</CardTitle>
          </div>
          <Button
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 text-gray-400"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <Minus className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          </Button>
        </div>
      </CardHeader>
      
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            <CardContent className="pt-2 space-y-2 max-h-[400px] overflow-y-auto">
              {layers.map((layer) => {
                const isActive = activeLayers.includes(layer.id);
                const Icon = layer.icon;
                
                return (
                  <div
                    key={layer.id}
                    className={`p-3 rounded-sm border transition-all ${
                      isActive 
                        ? 'bg-[#f5a623]/10 border-[#f5a623]/30' 
                        : 'bg-black/40 border-white/5 hover:border-white/10'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Icon className={`h-4 w-4 ${layer.color}`} />
                        <span className="text-sm text-white font-medium">{layer.name}</span>
                      </div>
                      <Switch
                        checked={isActive}
                        onCheckedChange={() => onToggle(layer)}
                        className="data-[state=checked]:bg-[#f5a623]"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mb-2">{layer.description}</p>
                    
                    {isActive && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-400">Opacité</span>
                        <Slider
                          defaultValue={[70]}
                          max={100}
                          step={10}
                          className="flex-1"
                          onValueChange={(value) => onOpacityChange(layer.id, value[0] / 100)}
                        />
                      </div>
                    )}
                    
                    <Badge className="mt-2 bg-white/5 text-gray-400 text-xs">
                      {layer.license}
                    </Badge>
                  </div>
                );
              })}
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

// Coordinates display
const CoordinatesDisplay = ({ coordinates }) => {
  if (!coordinates) return null;
  
  return (
    <div className="absolute bottom-4 right-4 z-10 px-3 py-2 bg-black/80 rounded-sm border border-white/10 backdrop-blur-sm">
      <div className="flex items-center gap-2 text-xs font-mono">
        <Crosshair className="h-3 w-3 text-[#f5a623]" />
        <span className="text-gray-400">
          {coordinates.lat.toFixed(5)}°N, {Math.abs(coordinates.lng).toFixed(5)}°W
        </span>
      </div>
    </div>
  );
};

// Main Territory Map Component
const TerritoryMap = ({ 
  onLocationSelect,
  initialCenter = [QUEBEC_CENTER.lng, QUEBEC_CENTER.lat],
  initialZoom = 7,
  showLayerPanel = true,
  height = '600px'
}) => {
  const mapContainerRef = useRef(null);
  const { map, mapLoaded, mapError } = useMapLibre(mapContainerRef, {
    center: initialCenter,
    zoom: initialZoom
  });
  
  const [activeLayers, setActiveLayers] = useState([]);
  const [mouseCoordinates, setMouseCoordinates] = useState(null);
  const [markers, setMarkers] = useState([]);
  const markersRef = useRef([]);

  // Handle mouse move for coordinates display
  useEffect(() => {
    if (!map || !mapLoaded) return;

    const handleMouseMove = (e) => {
      setMouseCoordinates({
        lat: e.lngLat.lat,
        lng: e.lngLat.lng
      });
    };

    const handleClick = (e) => {
      if (onLocationSelect) {
        onLocationSelect({
          lat: e.lngLat.lat,
          lng: e.lngLat.lng
        });
      }
    };

    map.on('mousemove', handleMouseMove);
    map.on('click', handleClick);

    return () => {
      map.off('mousemove', handleMouseMove);
      map.off('click', handleClick);
    };
  }, [map, mapLoaded, onLocationSelect]);

  // Toggle WMS layer
  const handleLayerToggle = useCallback((layer) => {
    if (!map || !mapLoaded) return;

    if (activeLayers.includes(layer.id)) {
      // Remove layer
      if (map.getLayer(layer.id)) {
        map.removeLayer(layer.id);
      }
      if (map.getSource(layer.id)) {
        map.removeSource(layer.id);
      }
      setActiveLayers(prev => prev.filter(id => id !== layer.id));
    } else {
      // Add layer
      addWMSLayer(map, layer.id, layer.url, layer.layer);
      setActiveLayers(prev => [...prev, layer.id]);
    }
  }, [map, mapLoaded, activeLayers]);

  // Change layer opacity
  const handleOpacityChange = useCallback((layerId, opacity) => {
    if (!map || !map.getLayer(layerId)) return;
    map.setPaintProperty(layerId, 'raster-opacity', opacity);
  }, [map]);

  // Add waypoint marker
  const addWaypoint = useCallback((coordinates, name = 'Waypoint') => {
    if (!map) return;

    const marker = addMarker(map, coordinates, {
      color: '#f5a623',
      popup: `<div class="p-2"><strong>${name}</strong><br/>
        ${coordinates[1].toFixed(5)}°N, ${Math.abs(coordinates[0]).toFixed(5)}°W
      </div>`
    });

    markersRef.current.push(marker);
    setMarkers(prev => [...prev, { coordinates, name, marker }]);
  }, [map]);

  // Error state
  if (mapError) {
    return (
      <Card className="bg-[#1a1a1a] border-white/10">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
          <p className="text-red-400 text-sm">{mapError}</p>
          <Button 
            variant="outline" 
            className="mt-4 border-white/20"
            onClick={() => window.location.reload()}
          >
            Recharger
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="relative w-full rounded-md overflow-hidden" style={{ height }}>
      {/* Map container */}
      <div 
        ref={mapContainerRef} 
        className="absolute inset-0 w-full h-full"
        style={{ width: '100%', height: '100%' }}
        data-testid="territory-map-container"
      />

      {/* Loading overlay */}
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0d1117] z-20">
          <div className="text-center">
            <Loader2 className="h-8 w-8 text-[#f5a623] animate-spin mx-auto mb-3" />
            <p className="text-gray-400 text-sm">Chargement de la carte...</p>
          </div>
        </div>
      )}

      {/* Layer panel */}
      {mapLoaded && showLayerPanel && (
        <LayerPanel
          layers={AVAILABLE_LAYERS}
          activeLayers={activeLayers}
          onToggle={handleLayerToggle}
          onOpacityChange={handleOpacityChange}
        />
      )}

      {/* Engine badge */}
      {mapLoaded && (
        <div className="absolute top-4 right-16 z-10">
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
            MapLibre GL
          </Badge>
        </div>
      )}

      {/* Coordinates display */}
      <CoordinatesDisplay coordinates={mouseCoordinates} />

      {/* Active layers indicator */}
      {mapLoaded && activeLayers.length > 0 && (
        <div className="absolute bottom-4 left-4 z-10">
          <Badge className="bg-[#f5a623]/20 text-[#f5a623] border-[#f5a623]/30">
            {activeLayers.length} couche{activeLayers.length > 1 ? 's' : ''} active{activeLayers.length > 1 ? 's' : ''}
          </Badge>
        </div>
      )}
    </div>
  );
};

export default TerritoryMap;
