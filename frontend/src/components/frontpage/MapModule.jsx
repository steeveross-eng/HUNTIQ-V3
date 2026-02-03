import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Map, Layers, Navigation, Satellite, Mountain, Trees, Target, MapPin, Maximize2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

// Placeholder for when Mapbox is not configured
const MapPlaceholder = ({ onExpand }) => {
  const zones = [
    { id: 1, name: 'Laurentides', coords: '46.0°N, 74.5°W', status: 'Optimal' },
    { id: 2, name: 'Abitibi', coords: '48.5°N, 78.0°W', status: 'Bon' },
    { id: 3, name: 'Saguenay', coords: '48.4°N, 71.0°W', status: 'Excellent' },
    { id: 4, name: 'Outaouais', coords: '46.5°N, 76.0°W', status: 'Optimal' },
  ];

  return (
    <div className="relative w-full h-full min-h-[500px] bg-[#0d1117] rounded-md overflow-hidden">
      {/* Simulated map background */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1524661135-423995f22d0b?w=1200&auto=format&fit=crop')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'saturate(0.3) brightness(0.5)'
        }}
      />
      
      {/* Grid overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(245,166,35,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(245,166,35,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      {/* Quebec zones visualization */}
      <div className="relative z-10 p-6 h-full flex flex-col">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-[#f5a623] rounded-full animate-pulse" />
            <span className="text-[#f5a623] font-mono text-sm">LIVE TRACKING</span>
          </div>
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
            29 zones actives
          </Badge>
        </div>

        {/* Zone markers */}
        <div className="flex-1 relative">
          {zones.map((zone, i) => (
            <motion.div
              key={zone.id}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.2 }}
              className="absolute cursor-pointer group"
              style={{
                top: `${20 + i * 20}%`,
                left: `${15 + i * 18}%`,
              }}
            >
              <div className="relative">
                <div className="w-4 h-4 bg-[#f5a623] rounded-full animate-ping absolute" />
                <div className="w-4 h-4 bg-[#f5a623] rounded-full relative z-10" />
              </div>
              {/* Tooltip */}
              <div className="absolute left-6 top-0 opacity-0 group-hover:opacity-100 transition-opacity bg-black/90 backdrop-blur-sm px-3 py-2 rounded-sm border border-white/10 whitespace-nowrap z-20">
                <p className="text-white font-semibold text-sm">{zone.name}</p>
                <p className="text-gray-400 text-xs font-mono">{zone.coords}</p>
                <Badge className={`mt-1 text-xs ${zone.status === 'Excellent' ? 'bg-green-500/20 text-green-400' : 'bg-[#f5a623]/20 text-[#f5a623]'}`}>
                  {zone.status}
                </Badge>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom controls */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/10">
          <div className="flex gap-2">
            <Button size="sm" variant="outline" className="border-white/20 text-white hover:bg-white/10 rounded-sm">
              <Layers className="h-4 w-4 mr-1" /> Couches
            </Button>
            <Button size="sm" variant="outline" className="border-white/20 text-white hover:bg-white/10 rounded-sm">
              <Satellite className="h-4 w-4 mr-1" /> Satellite
            </Button>
          </div>
          <Button 
            size="sm" 
            className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm"
            onClick={onExpand}
          >
            <Maximize2 className="h-4 w-4 mr-1" /> Plein écran
          </Button>
        </div>
      </div>
    </div>
  );
};

const MapModule = () => {
  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#0a0a0a] to-[#0d1117]" data-testid="map-module-section">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Map className="h-6 w-6 text-[#f5a623]" />
              <span className="text-[#f5a623] uppercase tracking-wider text-sm font-bold">Carte Interactive</span>
            </div>
            <h2 className="font-barlow text-3xl md:text-4xl font-bold text-white uppercase tracking-tight">
              Territoires du <span className="text-[#f5a623]">Québec</span>
            </h2>
            <p className="text-gray-400 mt-2">Explorez les 29 zones de chasse avec données en temps réel</p>
          </div>
          <Link to="/territoire">
            <Button className="bg-[#f5a623] text-black hover:bg-[#d9901c] rounded-sm hidden md:flex">
              <Navigation className="h-4 w-4 mr-2" />
              Explorer la carte
            </Button>
          </Link>
        </div>

        {/* Map Container */}
        <Card className="bg-[#1a1a1a] border-white/5 rounded-md overflow-hidden">
          <CardContent className="p-0">
            <MapPlaceholder onExpand={() => window.location.href = '/territoire'} />
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          {[
            { icon: Mountain, label: 'Zones montagneuses', value: '12' },
            { icon: Trees, label: 'Zones forestières', value: '15' },
            { icon: Target, label: 'Points chauds actifs', value: '847' },
            { icon: MapPin, label: 'Pourvoiries partenaires', value: '156' },
          ].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-md p-4 text-center"
            >
              <stat.icon className="h-6 w-6 text-[#f5a623] mx-auto mb-2" />
              <div className="font-barlow text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-gray-400 text-xs uppercase tracking-wider">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default MapModule;
