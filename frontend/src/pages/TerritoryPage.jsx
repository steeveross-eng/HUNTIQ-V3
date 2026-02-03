/**
 * HUNTIQ V3 - BIONIC™ Territory Page
 * Page complète de gestion du territoire avec:
 * - Carte interactive MapLibre GL
 * - Gestion des waypoints
 * - Couches environnementales WMS
 * - Algorithmes de scoring
 * - Recommandations équipements
 */

import { useState, useCallback, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Map, Layers, MapPin, Target, Camera, Eye, Navigation,
  Crosshair, TreePine, Droplets, Mountain, Compass, Plus,
  Trash2, Save, Download, Settings, Info, ChevronRight,
  AlertTriangle, CheckCircle, Loader2, RefreshCw, Maximize2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import TerritoryMap from '@/components/geospatial/TerritoryMap';
import WeatherPanel from '@/components/geospatial/WeatherPanel';
import HydroAnalysisPanel from '@/components/geospatial/HydroAnalysisPanel';
import { HuntingPotentialAnalysis } from '@/components/geospatial';
import { api } from '@/services/api.client';

// Waypoint types with icons and colors
const WAYPOINT_TYPES = {
  camera: { label: 'Caméra', icon: Camera, color: '#22c55e', description: 'Caméra de surveillance' },
  mirador: { label: 'Mirador', icon: Eye, color: '#f5a623', description: 'Poste d\'observation' },
  affut: { label: 'Affût', icon: Target, color: '#ef4444', description: 'Position de tir' },
  saline: { label: 'Saline', icon: Droplets, color: '#3b82f6', description: 'Bloc minéral / Saline' },
  sentier: { label: 'Sentier', icon: Navigation, color: '#8b5cf6', description: 'Point de sentier' },
  observation: { label: 'Observation', icon: Crosshair, color: '#ec4899', description: 'Observation faune' },
};

// Score level colors
const SCORE_COLORS = {
  excellent: 'bg-green-500 text-green-400 border-green-500',
  bon: 'bg-blue-500 text-blue-400 border-blue-500',
  moyen: 'bg-yellow-500 text-yellow-400 border-yellow-500',
  faible: 'bg-orange-500 text-orange-400 border-orange-500',
  mauvais: 'bg-red-500 text-red-400 border-red-500',
};

// Waypoint form component
const WaypointForm = ({ onAdd, selectedLocation }) => {
  const [name, setName] = useState('');
  const [type, setType] = useState('camera');
  const [notes, setNotes] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedLocation || !name) return;

    onAdd({
      id: Date.now(),
      name,
      type,
      notes,
      coordinates: selectedLocation,
      createdAt: new Date().toISOString()
    });

    setName('');
    setNotes('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label className="text-gray-300">Nom du waypoint</Label>
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ex: Caméra Nord"
          className="bg-black/40 border-white/10 text-white mt-1"
          required
        />
      </div>

      <div>
        <Label className="text-gray-300">Type</Label>
        <Select value={type} onValueChange={setType}>
          <SelectTrigger className="bg-black/40 border-white/10 text-white mt-1">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-[#1a1a1a] border-white/10">
            {Object.entries(WAYPOINT_TYPES).map(([key, val]) => (
              <SelectItem key={key} value={key} className="text-white">
                <div className="flex items-center gap-2">
                  <val.icon className="h-4 w-4" style={{ color: val.color }} />
                  {val.label}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label className="text-gray-300">Notes (optionnel)</Label>
        <Input
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Notes additionnelles..."
          className="bg-black/40 border-white/10 text-white mt-1"
        />
      </div>

      {selectedLocation && (
        <div className="p-3 bg-[#f5a623]/10 rounded-sm border border-[#f5a623]/20">
          <p className="text-xs text-gray-400">Position sélectionnée:</p>
          <p className="text-sm text-white font-mono">
            {selectedLocation.lat.toFixed(5)}°N, {Math.abs(selectedLocation.lng).toFixed(5)}°W
          </p>
        </div>
      )}

      <Button
        type="submit"
        disabled={!selectedLocation || !name}
        className="w-full bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm"
      >
        <Plus className="h-4 w-4 mr-2" />
        Ajouter le waypoint
      </Button>
    </form>
  );
};

// Waypoint list component
const WaypointList = ({ waypoints, onDelete, onSelect }) => {
  if (waypoints.length === 0) {
    return (
      <div className="text-center py-8">
        <MapPin className="h-12 w-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400 text-sm">Aucun waypoint</p>
        <p className="text-gray-600 text-xs mt-1">
          Cliquez sur la carte pour ajouter un point
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-[300px]">
      <div className="space-y-2">
        {waypoints.map((wp) => {
          const typeInfo = WAYPOINT_TYPES[wp.type];
          const Icon = typeInfo?.icon || MapPin;

          return (
            <motion.div
              key={wp.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-3 bg-black/40 rounded-sm border border-white/5 hover:border-white/15 transition-all group cursor-pointer"
              onClick={() => onSelect(wp)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-8 h-8 rounded-sm flex items-center justify-center"
                    style={{ backgroundColor: `${typeInfo?.color}20` }}
                  >
                    <Icon className="h-4 w-4" style={{ color: typeInfo?.color }} />
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">{wp.name}</p>
                    <p className="text-gray-500 text-xs">{typeInfo?.label}</p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  className="opacity-0 group-hover:opacity-100 h-8 w-8 p-0 text-red-400 hover:text-red-300"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(wp.id);
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              {wp.notes && (
                <p className="text-gray-400 text-xs mt-2 pl-11">{wp.notes}</p>
              )}
              <p className="text-gray-600 text-xs mt-1 pl-11 font-mono">
                {wp.coordinates.lat.toFixed(4)}°N, {Math.abs(wp.coordinates.lng).toFixed(4)}°W
              </p>
            </motion.div>
          );
        })}
      </div>
    </ScrollArea>
  );
};

// Territory scoring panel
const TerritoryScoring = ({ selectedLocation, onCalculate }) => {
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState(null);
  const [error, setError] = useState(null);

  const calculateScore = async () => {
    if (!selectedLocation) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/geospatial/potential/calculate', {
        bbox: {
          min_lat: selectedLocation.lat - 0.05,
          max_lat: selectedLocation.lat + 0.05,
          min_lon: selectedLocation.lng - 0.05,
          max_lon: selectedLocation.lng + 0.05
        },
        center_point: {
          latitude: selectedLocation.lat,
          longitude: selectedLocation.lng
        },
        radius_m: 5000,
        target_species: 'deer',
        season: 'rut',
        include_ai_predictions: true
      });

      setScore(response.data);
      if (onCalculate) onCalculate(response.data);
    } catch (err) {
      setError(err.message || 'Erreur de calcul');
    } finally {
      setLoading(false);
    }
  };

  const scoreColors = score?.level ? SCORE_COLORS[score.level] : null;

  return (
    <Card className="bg-[#1a1a1a] border-white/10">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-[#f5a623]" />
            <CardTitle className="text-sm text-white">Score du Territoire</CardTitle>
          </div>
          {score && (
            <Badge className={`${scoreColors?.split(' ')[0]}/20 ${scoreColors?.split(' ')[1]}`}>
              {score.level}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        {!selectedLocation ? (
          <p className="text-gray-500 text-sm text-center py-4">
            Sélectionnez un point sur la carte
          </p>
        ) : !score ? (
          <div className="text-center py-4">
            <Button
              onClick={calculateScore}
              disabled={loading}
              className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Compass className="h-4 w-4 mr-2" />
              )}
              Analyser le territoire
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Score display */}
            <div className="flex items-center justify-between">
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{score.overall_score}</div>
                <p className="text-xs text-gray-500">/ 100</p>
              </div>
              <div className="flex-1 ml-4">
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${scoreColors?.split(' ')[0]} rounded-full transition-all`}
                    style={{ width: `${score.overall_score}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {score.recommendations?.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs text-gray-400 uppercase">Recommandations</p>
                {score.recommendations.slice(0, 2).map((rec, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <CheckCircle className="h-3 w-3 text-green-400 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-300">{rec}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Recalculate */}
            <Button
              onClick={calculateScore}
              variant="outline"
              size="sm"
              className="w-full border-white/10 text-white"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Recalculer
            </Button>
          </div>
        )}

        {error && (
          <p className="text-red-400 text-xs text-center mt-2">{error}</p>
        )}
      </CardContent>
    </Card>
  );
};

// Equipment recommendations panel
const EquipmentRecommendations = ({ waypoints, score }) => {
  const recommendations = [];

  // Based on waypoints
  const cameraCount = waypoints.filter(w => w.type === 'camera').length;
  const miradorCount = waypoints.filter(w => w.type === 'mirador').length;
  const salineCount = waypoints.filter(w => w.type === 'saline').length;

  if (cameraCount === 0) {
    recommendations.push({
      type: 'camera',
      priority: 'high',
      text: 'Installez au moins 2-3 caméras sur les corridors identifiés'
    });
  }

  if (miradorCount === 0 && score?.overall_score >= 60) {
    recommendations.push({
      type: 'mirador',
      priority: 'medium',
      text: 'Zone favorable - Un mirador améliorerait la visibilité'
    });
  }

  if (salineCount === 0) {
    recommendations.push({
      type: 'saline',
      priority: 'medium',
      text: 'Une saline attirerait le gibier vers vos positions'
    });
  }

  // Based on score
  if (score?.overall_score >= 80) {
    recommendations.push({
      type: 'affut',
      priority: 'high',
      text: 'Territoire excellent - Installez un affût permanent'
    });
  }

  return (
    <Card className="bg-[#1a1a1a] border-white/10">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Settings className="h-5 w-5 text-[#f5a623]" />
          <CardTitle className="text-sm text-white">Recommandations</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        {recommendations.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">
            Ajoutez des waypoints pour obtenir des recommandations
          </p>
        ) : (
          <div className="space-y-3">
            {recommendations.map((rec, i) => {
              const typeInfo = WAYPOINT_TYPES[rec.type];
              const Icon = typeInfo?.icon || Info;
              const priorityColor = rec.priority === 'high' ? 'text-red-400' : 'text-yellow-400';

              return (
                <div
                  key={i}
                  className="p-3 bg-black/40 rounded-sm border border-white/5"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className="w-8 h-8 rounded-sm flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: `${typeInfo?.color}20` }}
                    >
                      <Icon className="h-4 w-4" style={{ color: typeInfo?.color }} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={`text-xs ${priorityColor} bg-transparent border-current`}>
                          {rec.priority === 'high' ? 'Prioritaire' : 'Suggéré'}
                        </Badge>
                      </div>
                      <p className="text-gray-300 text-sm">{rec.text}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Main Territory Page
const TerritoryPage = () => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [waypoints, setWaypoints] = useState([]);
  const [territoryScore, setTerritoryScore] = useState(null);
  const [activeTab, setActiveTab] = useState('map');
  const [showHydroPanel, setShowHydroPanel] = useState(true);
  
  // Build bbox from selected location
  const currentBbox = selectedLocation ? {
    min_lat: selectedLocation.lat - 0.1,
    max_lat: selectedLocation.lat + 0.1,
    min_lon: selectedLocation.lng - 0.1,
    max_lon: selectedLocation.lng + 0.1
  } : null;

  // Handle location selection from map
  const handleLocationSelect = useCallback((location) => {
    setSelectedLocation(location);
  }, []);

  // Add waypoint
  const handleAddWaypoint = useCallback((waypoint) => {
    setWaypoints(prev => [...prev, waypoint]);
  }, []);

  // Delete waypoint
  const handleDeleteWaypoint = useCallback((id) => {
    setWaypoints(prev => prev.filter(w => w.id !== id));
  }, []);

  // Select waypoint (center map)
  const handleSelectWaypoint = useCallback((waypoint) => {
    setSelectedLocation(waypoint.coordinates);
  }, []);

  // Export waypoints
  const handleExport = () => {
    const data = JSON.stringify(waypoints, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `huntiq-waypoints-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Header */}
      <div className="border-b border-white/10 bg-black/40 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-[1800px] mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <Map className="h-6 w-6 text-[#f5a623]" />
                <div>
                  <h1 className="text-xl font-bold text-white">Territoire BIONIC™</h1>
                  <p className="text-xs text-gray-500">Gestion et analyse du territoire</p>
                </div>
              </div>
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                MapLibre GL Actif
              </Badge>
            </div>

            <div className="flex items-center gap-2">
              <Badge className="bg-white/5 text-gray-400">
                {waypoints.length} waypoint{waypoints.length !== 1 ? 's' : ''}
              </Badge>
              {waypoints.length > 0 && (
                <Button
                  size="sm"
                  variant="outline"
                  className="border-white/10 text-white"
                  onClick={handleExport}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Exporter
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-[1800px] mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Map - 3 columns */}
          <div className="lg:col-span-3">
            <Card className="bg-[#1a1a1a] border-white/10 overflow-hidden">
              <CardContent className="p-0">
                <TerritoryMap
                  height="calc(100vh - 200px)"
                  onLocationSelect={handleLocationSelect}
                  showLayerPanel={true}
                />
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-4">
            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="w-full bg-black/40 border border-white/10">
                <TabsTrigger value="map" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
                  <MapPin className="h-4 w-4 mr-1" />
                  Waypoints
                </TabsTrigger>
                <TabsTrigger value="score" className="flex-1 data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
                  <Target className="h-4 w-4 mr-1" />
                  Score
                </TabsTrigger>
              </TabsList>

              <TabsContent value="map" className="mt-4 space-y-4">
                {/* Add waypoint form */}
                <Card className="bg-[#1a1a1a] border-white/10">
                  <CardHeader className="pb-2">
                    <div className="flex items-center gap-2">
                      <Plus className="h-5 w-5 text-[#f5a623]" />
                      <CardTitle className="text-sm text-white">Nouveau Waypoint</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <WaypointForm
                      onAdd={handleAddWaypoint}
                      selectedLocation={selectedLocation}
                    />
                  </CardContent>
                </Card>

                {/* Waypoint list */}
                <Card className="bg-[#1a1a1a] border-white/10">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-5 w-5 text-[#f5a623]" />
                        <CardTitle className="text-sm text-white">Mes Waypoints</CardTitle>
                      </div>
                      <Badge className="bg-white/5 text-gray-400 text-xs">
                        {waypoints.length}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <WaypointList
                      waypoints={waypoints}
                      onDelete={handleDeleteWaypoint}
                      onSelect={handleSelectWaypoint}
                    />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="score" className="mt-4 space-y-4">
                {/* Territory scoring */}
                <TerritoryScoring
                  selectedLocation={selectedLocation}
                  onCalculate={setTerritoryScore}
                />

                {/* Weather panel */}
                {selectedLocation && (
                  <WeatherPanel
                    latitude={selectedLocation.lat}
                    longitude={selectedLocation.lng}
                    compact={true}
                  />
                )}

                {/* Equipment recommendations */}
                <EquipmentRecommendations
                  waypoints={waypoints}
                  score={territoryScore}
                />
              </TabsContent>
            </Tabs>

            {/* Quick info */}
            <Card className="bg-[#1a1a1a] border-white/10">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Info className="h-5 w-5 text-[#f5a623] flex-shrink-0 mt-0.5" />
                  <div className="text-xs text-gray-400">
                    <p className="mb-2">
                      <strong className="text-white">Cliquez sur la carte</strong> pour sélectionner un emplacement et ajouter des waypoints.
                    </p>
                    <p>
                      Activez les <strong className="text-white">couches WMS</strong> pour visualiser l'hydrologie, la forêt et l'élévation.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TerritoryPage;
