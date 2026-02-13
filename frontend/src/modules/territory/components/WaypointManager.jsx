/**
 * WaypointManager - Waypoint management component
 * Allows users to save and manage hunting waypoints
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Input } from '../../../components/ui/input';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const WAYPOINT_TYPES = [
  { id: 'hunting', label: 'Spot de chasse', icon: '🎯' },
  { id: 'stand', label: 'Mirador/Affût', icon: '🪵' },
  { id: 'camera', label: 'Caméra trail', icon: '📷' },
  { id: 'feeder', label: 'Nourrisseur', icon: '🌾' },
  { id: 'sighting', label: 'Observation', icon: '👁️' },
  { id: 'parking', label: 'Stationnement', icon: '🅿️' },
  { id: 'custom', label: 'Autre', icon: '📍' }
];

export const WaypointManager = ({ coordinates = { lat: 46.8139, lng: -71.2080 } }) => {
  const [waypoints, setWaypoints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [newWaypoint, setNewWaypoint] = useState({
    name: '',
    type: 'hunting',
    notes: '',
    lat: coordinates.lat,
    lng: coordinates.lng
  });

  // Load waypoints
  const loadWaypoints = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/user/waypoints`);
      const data = await response.json();
      if (data.success && data.waypoints) {
        setWaypoints(data.waypoints);
      }
    } catch (error) {
      console.error('Error loading waypoints:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWaypoints();
  }, [loadWaypoints]);

  // Save waypoint
  const handleSaveWaypoint = async () => {
    if (!newWaypoint.name.trim()) {
      toast.error('Veuillez entrer un nom pour le waypoint');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/user/waypoints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newWaypoint,
          active: true
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('Waypoint enregistré !');
        setWaypoints(prev => [data.waypoint, ...prev]);
        setNewWaypoint({
          name: '',
          type: 'hunting',
          notes: '',
          lat: coordinates.lat,
          lng: coordinates.lng
        });
        setShowForm(false);
      } else {
        toast.error(data.error || 'Erreur lors de l\'enregistrement');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
      console.error('Save waypoint error:', error);
    }
  };

  // Delete waypoint
  const handleDeleteWaypoint = async (waypointId) => {
    try {
      const response = await fetch(`${API_URL}/api/user/waypoints/${waypointId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast.success('Waypoint supprimé');
        setWaypoints(prev => prev.filter(w => w.id !== waypointId));
      } else {
        toast.error(data.error || 'Erreur lors de la suppression');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const getTypeInfo = (typeId) => {
    return WAYPOINT_TYPES.find(t => t.id === typeId) || WAYPOINT_TYPES[6];
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <span className="text-2xl">📍</span>
            Mes Waypoints
          </span>
          <div className="flex items-center gap-2">
            <Badge className="bg-slate-700">{waypoints.length}</Badge>
            <Button 
              size="sm"
              className="bg-[#f5a623] hover:bg-[#e09000] text-black"
              onClick={() => setShowForm(!showForm)}
              data-testid="add-waypoint-btn"
            >
              {showForm ? '✕ Annuler' : '+ Nouveau'}
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Add Form */}
        {showForm && (
          <div className="mb-4 p-4 bg-slate-700/50 rounded-lg space-y-3" data-testid="waypoint-form">
            <Input
              placeholder="Nom du waypoint"
              value={newWaypoint.name}
              onChange={(e) => setNewWaypoint(prev => ({ ...prev, name: e.target.value }))}
              className="bg-slate-700 border-slate-600"
              data-testid="waypoint-name-input"
            />
            
            <div className="flex flex-wrap gap-2">
              {WAYPOINT_TYPES.map(type => (
                <button
                  key={type.id}
                  onClick={() => setNewWaypoint(prev => ({ ...prev, type: type.id }))}
                  className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1 transition-all ${
                    newWaypoint.type === type.id 
                      ? 'bg-[#f5a623] text-black' 
                      : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                  }`}
                >
                  <span>{type.icon}</span>
                  {type.label}
                </button>
              ))}
            </div>
            
            <Input
              placeholder="Notes (optionnel)"
              value={newWaypoint.notes}
              onChange={(e) => setNewWaypoint(prev => ({ ...prev, notes: e.target.value }))}
              className="bg-slate-700 border-slate-600"
            />
            
            <div className="grid grid-cols-2 gap-2">
              <Input
                type="number"
                step="0.0001"
                placeholder="Latitude"
                value={newWaypoint.lat}
                onChange={(e) => setNewWaypoint(prev => ({ ...prev, lat: parseFloat(e.target.value) }))}
                className="bg-slate-700 border-slate-600"
              />
              <Input
                type="number"
                step="0.0001"
                placeholder="Longitude"
                value={newWaypoint.lng}
                onChange={(e) => setNewWaypoint(prev => ({ ...prev, lng: parseFloat(e.target.value) }))}
                className="bg-slate-700 border-slate-600"
              />
            </div>
            
            <Button 
              className="w-full bg-green-600 hover:bg-green-700"
              onClick={handleSaveWaypoint}
              data-testid="save-waypoint-btn"
            >
              💾 Enregistrer le waypoint
            </Button>
          </div>
        )}

        {/* Waypoints List */}
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse bg-slate-700 rounded-lg h-16" />
            ))}
          </div>
        ) : waypoints.length > 0 ? (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {waypoints.map(waypoint => {
              const typeInfo = getTypeInfo(waypoint.type);
              return (
                <div 
                  key={waypoint.id}
                  className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-colors"
                  data-testid={`waypoint-${waypoint.id}`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{typeInfo.icon}</span>
                    <div>
                      <p className="text-white font-medium">{waypoint.name}</p>
                      <p className="text-slate-400 text-xs">
                        {waypoint.lat?.toFixed(4)}, {waypoint.lng?.toFixed(4)}
                        {waypoint.notes && ` • ${waypoint.notes}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className="bg-slate-600 text-slate-300 text-xs">
                      {typeInfo.label}
                    </Badge>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8 text-red-400 hover:text-red-300 hover:bg-red-900/20"
                      onClick={() => handleDeleteWaypoint(waypoint.id)}
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <span className="text-4xl">📍</span>
            <p className="text-slate-400 mt-2">Aucun waypoint enregistré</p>
            <p className="text-slate-500 text-sm">Cliquez sur "+ Nouveau" pour ajouter votre premier spot</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WaypointManager;
