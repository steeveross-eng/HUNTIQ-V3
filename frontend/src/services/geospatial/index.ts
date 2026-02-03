/**
 * HUNTIQ V3 - BIONIC™ Geospatial Engine
 * Services Index
 * 
 * Centralized export of all geospatial services
 */

export { default as GeospatialService } from './geospatial.service';

// Individual module exports for tree-shaking
export const LidarService = () => import('./geospatial.service').then(m => m.default.lidar);
export const SentinelService = () => import('./geospatial.service').then(m => m.default.sentinel);
export const LandsatService = () => import('./geospatial.service').then(m => m.default.landsat);
export const SigeomService = () => import('./geospatial.service').then(m => m.default.sigeom);
export const HydroService = () => import('./geospatial.service').then(m => m.default.hydro);
export const GeomorphService = () => import('./geospatial.service').then(m => m.default.geomorph);
export const ForestService = () => import('./geospatial.service').then(m => m.default.forest);
export const AIService = () => import('./geospatial.service').then(m => m.default.ai);
export const PotentialService = () => import('./geospatial.service').then(m => m.default.potential);
