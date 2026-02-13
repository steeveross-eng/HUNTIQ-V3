/**
 * SightingsMap - Collaborative sightings display
 * Phase 10 - Plan Maître Modules
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { CollaborativeService } from '../CollaborativeService';

export const SightingsFeed = ({ 
  coordinates = null,
  radiusKm = 10,
  limit = 10
}) => {
  const [sightings, setSightings] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('sightings');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (coordinates) {
        const sightResult = await CollaborativeService.getSightings(
          coordinates.lat, 
          coordinates.lng, 
          radiusKm
        );
        if (sightResult.success && sightResult.sightings) {
          setSightings(sightResult.sightings);
        } else {
          setSightings(CollaborativeService.getPlaceholderSightings());
        }
      } else {
        setSightings(CollaborativeService.getPlaceholderSightings());
      }

      const reportsResult = await CollaborativeService.getHuntingReports({ limit });
      if (reportsResult.success && reportsResult.reports) {
        setReports(reportsResult.reports);
      } else {
        setReports(CollaborativeService.getPlaceholderReports());
      }
    } catch (error) {
      console.error('Collaborative load error:', error);
      setSightings(CollaborativeService.getPlaceholderSightings());
      setReports(CollaborativeService.getPlaceholderReports());
    } finally {
      setLoading(false);
    }
  }, [coordinates, radiusKm, limit]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const getSpeciesIcon = (species) => {
    const icons = {
      deer: '🦌', moose: '🫎', bear: '🐻', wild_boar: '🐗',
      turkey: '🦃', duck: '🦆', goose: '🪿'
    };
    return icons[species] || '🎯';
  };

  const formatTimeAgo = (timestamp) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours < 1) return 'Il y a moins d\'1h';
    if (hours < 24) return `Il y a ${hours}h`;
    const days = Math.floor(hours / 24);
    return `Il y a ${days}j`;
  };

  return (
    <Card className="bg-gradient-to-br from-purple-900/20 to-slate-900 border-purple-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <span className="text-2xl">👥</span>
            Communauté
          </span>
          <Badge className="bg-purple-900/50 text-purple-400">
            Collaborative
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <Button
            size="sm"
            variant={activeTab === 'sightings' ? 'default' : 'outline'}
            className={activeTab === 'sightings' ? 'bg-purple-600' : 'border-slate-600'}
            onClick={() => setActiveTab('sightings')}
          >
            👁️ Observations
          </Button>
          <Button
            size="sm"
            variant={activeTab === 'reports' ? 'default' : 'outline'}
            className={activeTab === 'reports' ? 'bg-purple-600' : 'border-slate-600'}
            onClick={() => setActiveTab('reports')}
          >
            📝 Rapports
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-6">
            <div className="animate-spin text-3xl">👥</div>
            <p className="text-slate-400 text-sm mt-2">Chargement...</p>
          </div>
        ) : activeTab === 'sightings' ? (
          <div className="space-y-2">
            {sightings.length > 0 ? sightings.map((sighting, index) => (
              <div 
                key={sighting.id || index}
                className="flex items-center gap-3 bg-slate-800/50 rounded-lg p-3"
              >
                <span className="text-2xl">{getSpeciesIcon(sighting.species)}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium">
                      {sighting.count} {sighting.species}
                    </span>
                    {sighting.verified && (
                      <Badge className="bg-emerald-900/50 text-emerald-400 text-xs">✓</Badge>
                    )}
                  </div>
                  <p className="text-slate-400 text-xs">
                    {formatTimeAgo(sighting.timestamp)}
                  </p>
                </div>
              </div>
            )) : (
              <p className="text-center text-slate-400 py-4">Aucune observation récente</p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {reports.length > 0 ? reports.map((report, index) => (
              <div 
                key={report.id || index}
                className="bg-slate-800/50 rounded-lg p-3"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span>{getSpeciesIcon(report.species)}</span>
                    <span className="text-white font-medium">{report.hunter}</span>
                  </div>
                  <Badge className={report.success ? 'bg-emerald-900/50 text-emerald-400' : 'bg-slate-700 text-slate-400'}>
                    {report.success ? '✓ Succès' : 'Bredouille'}
                  </Badge>
                </div>
                <p className="text-slate-300 text-sm">{report.comment}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-amber-400">{'⭐'.repeat(report.rating)}</span>
                  <span className="text-slate-500 text-xs">{report.date}</span>
                </div>
              </div>
            )) : (
              <p className="text-center text-slate-400 py-4">Aucun rapport récent</p>
            )}
          </div>
        )}

        <Button 
          className="w-full mt-4 bg-purple-600 hover:bg-purple-700 text-white"
          onClick={loadData}
        >
          Actualiser
        </Button>
      </CardContent>
    </Card>
  );
};

export default SightingsFeed;
