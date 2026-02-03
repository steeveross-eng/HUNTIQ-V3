/**
 * HUNTIQ V3 - Data Sources Panel
 * Displays available geospatial data sources with status
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Database, ExternalLink, Globe, Satellite, Mountain, 
  Droplets, Trees, Map, Loader2, CheckCircle, AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useDataSources, useGeospatialStatus } from '@/hooks/geospatial';

// Icons for each data source type
const SOURCE_ICONS = {
  lidar_quebec: Mountain,
  sigeom: Globe,
  sentinel_2: Satellite,
  landsat_8_9: Satellite,
  hydro_quebec: Droplets,
  mne_quebec: Mountain,
  osm: Map,
  mffp_forest: Trees,
};

// Source card component
const DataSourceCard = ({ source, index }) => {
  const Icon = SOURCE_ICONS[source.id] || Database;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="p-4 bg-black/40 rounded-sm border border-white/5 hover:border-white/15 transition-all group"
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-[#f5a623]/10 rounded-sm flex items-center justify-center flex-shrink-0">
          <Icon className="h-5 w-5 text-[#f5a623]" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-white text-sm font-semibold truncate">{source.name}</h4>
            {source.free && (
              <Badge className="bg-green-500/20 text-green-400 text-xs border-green-500/30">
                Gratuit
              </Badge>
            )}
          </div>
          
          <p className="text-gray-500 text-xs mb-2">{source.provider}</p>
          
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-gray-400">
              <span className="text-gray-500">Résolution:</span> {source.resolution}
            </span>
            <span className="text-gray-600">|</span>
            <span className="text-gray-400">
              <span className="text-gray-500">API:</span> {source.api_type}
            </span>
          </div>
          
          <div className="mt-2 flex items-center gap-2">
            <Badge className="bg-white/5 text-gray-400 text-xs">
              {source.license?.split(' ')[0]}
            </Badge>
            {source.note && (
              <span className="text-xs text-yellow-500 truncate">{source.note}</span>
            )}
          </div>
        </div>
        
        <a 
          href={source.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <ExternalLink className="h-4 w-4 text-gray-500 hover:text-[#f5a623]" />
        </a>
      </div>
    </motion.div>
  );
};

// Engine status indicator
const EngineStatus = ({ status }) => {
  if (!status) return null;
  
  const isOperational = status.status === 'operational';
  
  return (
    <div className="flex items-center gap-3 p-4 bg-black/40 rounded-sm border border-white/10">
      <div className={`w-3 h-3 rounded-full ${isOperational ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`} />
      <div className="flex-1">
        <p className="text-white text-sm font-medium">
          Moteur BIONIC™ {isOperational ? 'Opérationnel' : 'En attente'}
        </p>
        <p className="text-gray-500 text-xs">
          Version {status.engine_version || '1.0.0'} • {Object.keys(status.modules || {}).filter(m => status.modules[m] === 'active').length} modules actifs
        </p>
      </div>
      {isOperational ? (
        <CheckCircle className="h-5 w-5 text-green-400" />
      ) : (
        <AlertCircle className="h-5 w-5 text-yellow-400" />
      )}
    </div>
  );
};

// Module status grid
const ModulesGrid = ({ modules }) => {
  if (!modules) return null;
  
  const moduleNames = {
    lidar: 'LiDAR',
    sentinel: 'Sentinel-2',
    landsat: 'Landsat',
    sigeom: 'SIGÉOM',
    hydro: 'Hydrologie',
    geomorphology: 'Géomorphologie',
    forest: 'Forêt',
    ai: 'IA Prédiction',
    potential: 'Potentiel',
  };
  
  const statusColors = {
    active: 'bg-green-500',
    ready: 'bg-blue-500',
    in_development: 'bg-yellow-500',
    inactive: 'bg-gray-500',
  };
  
  return (
    <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
      {Object.entries(modules).map(([key, value]) => (
        <div 
          key={key}
          className="p-2 bg-black/30 rounded-sm border border-white/5 text-center"
        >
          <div className={`w-2 h-2 ${statusColors[value] || statusColors.inactive} rounded-full mx-auto mb-1`} />
          <span className="text-xs text-gray-400">{moduleNames[key] || key}</span>
        </div>
      ))}
    </div>
  );
};

// Main component
const DataSourcesPanel = ({ showModules = true, compact = false }) => {
  const { sources, loading: sourcesLoading, error: sourcesError } = useDataSources();
  const { status, loading: statusLoading } = useGeospatialStatus();
  
  const loading = sourcesLoading || statusLoading;
  
  return (
    <Card className="bg-[#1a1a1a] border-white/10 rounded-md overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="h-5 w-5 text-[#f5a623]" />
            <div>
              <CardTitle className="text-lg text-white">Sources de données</CardTitle>
              <p className="text-xs text-gray-500">
                Données ouvertes Québec • 100% gratuites
              </p>
            </div>
          </div>
          <Badge className="bg-[#f5a623]/20 text-[#f5a623] border-[#f5a623]/30">
            {sources?.length || 0} sources
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="pt-4">
        {/* Engine status */}
        {!compact && <EngineStatus status={status} />}
        
        {/* Modules status */}
        {showModules && status?.modules && !compact && (
          <div className="mt-4">
            <h4 className="text-white text-sm font-semibold mb-3">Modules actifs</h4>
            <ModulesGrid modules={status.modules} />
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 text-[#f5a623] animate-spin" />
          </div>
        )}

        {/* Error state */}
        {sourcesError && !loading && (
          <div className="text-center py-4">
            <AlertCircle className="h-6 w-6 text-red-400 mx-auto mb-2" />
            <p className="text-red-400 text-sm">{sourcesError}</p>
          </div>
        )}

        {/* Data sources list */}
        {sources && sources.length > 0 && !loading && (
          <div className="mt-4">
            <h4 className="text-white text-sm font-semibold mb-3">
              Sources disponibles
            </h4>
            <div className={`space-y-2 ${compact ? 'max-h-[300px] overflow-y-auto' : ''}`}>
              {sources.map((source, i) => (
                <DataSourceCard key={source.id} source={source} index={i} />
              ))}
            </div>
          </div>
        )}

        {/* Attribution */}
        <div className="mt-4 pt-4 border-t border-white/5">
          <p className="text-xs text-gray-600 text-center">
            Données fournies par le Gouvernement du Québec, ESA Copernicus, USGS et OpenStreetMap
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default DataSourcesPanel;
