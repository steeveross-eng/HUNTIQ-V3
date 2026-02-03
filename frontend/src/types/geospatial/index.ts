/**
 * HUNTIQ V3 - BIONIC™ Geospatial Engine
 * TypeScript Type Definitions
 * 
 * This file defines all types for the geospatial engine.
 * NO IMPLEMENTATION - Architecture preparation only.
 */

// =============================================================================
// ENUMS
// =============================================================================

export type DataSourceType =
  | 'lidar_quebec'
  | 'sigeom'
  | 'sentinel_2'
  | 'landsat_8'
  | 'landsat_9'
  | 'hydro_quebec'
  | 'mne_quebec'
  | 'openstreetmap'
  | 'mffp_forest';

export type LayerType =
  | 'elevation'
  | 'slope'
  | 'aspect'
  | 'vegetation'
  | 'hydrology'
  | 'geology'
  | 'forest'
  | 'potential';

export type VegetationIndex = 'ndvi' | 'evi' | 'savi' | 'ndwi';

export type GeologyType = 'igneous' | 'sedimentary' | 'metamorphic' | 'quaternary_deposits';

export type ForestType = 'coniferous' | 'deciduous' | 'mixed' | 'regeneration';

export type HuntingPotentialLevel = 'excellent' | 'good' | 'moderate' | 'low' | 'poor';

export type TargetSpecies = 'moose' | 'deer' | 'bear' | 'turkey' | 'small_game';

export type HuntingSeason = 'pre_rut' | 'rut' | 'post_rut' | 'early' | 'late';

// =============================================================================
// BASE TYPES
// =============================================================================

export interface GeoCoordinate {
  latitude: number;
  longitude: number;
  altitude?: number;
}

export interface BoundingBox {
  minLat: number;
  maxLat: number;
  minLon: number;
  maxLon: number;
}

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface DataSourceMetadata {
  source: DataSourceType;
  url: string;
  license: string;
  lastUpdated?: string;
  resolution?: string;
  coverage?: string;
  notes?: string;
}

// =============================================================================
// LIDAR TYPES - LiDAR Québec
// =============================================================================

export interface LidarDataRequest {
  bbox: BoundingBox;
  resolution?: number;
  includeDsm?: boolean;
  includeDtm?: boolean;
  includeChm?: boolean;
}

export interface LidarDataResponse {
  requestId: string;
  status: string;
  bbox: BoundingBox;
  dtmUrl?: string;
  dsmUrl?: string;
  chmUrl?: string;
  metadata?: Record<string, unknown>;
}

export interface LidarStats {
  minElevation: number;
  maxElevation: number;
  meanElevation: number;
  stdElevation: number;
  minCanopyHeight?: number;
  maxCanopyHeight?: number;
  canopyCoverPercent?: number;
}

// =============================================================================
// SENTINEL-2 TYPES - ESA Copernicus
// =============================================================================

export interface SentinelDataRequest {
  bbox: BoundingBox;
  dateStart: Date;
  dateEnd: Date;
  cloudCoverMax?: number;
  indices?: VegetationIndex[];
  bands?: string[];
}

export interface SentinelDataResponse {
  requestId: string;
  status: string;
  sceneId?: string;
  acquisitionDate?: string;
  cloudCover?: number;
  indices?: Record<string, string>;
  bands?: Record<string, string>;
}

export interface VegetationAnalysis {
  ndviMean: number;
  ndviMin: number;
  ndviMax: number;
  eviMean?: number;
  vegetationHealth: string;
  biomassEstimate?: number;
}

// =============================================================================
// LANDSAT TYPES - USGS
// =============================================================================

export interface LandsatDataRequest {
  bbox: BoundingBox;
  dateStart: Date;
  dateEnd: Date;
  satellite?: 'landsat_8' | 'landsat_9';
  cloudCoverMax?: number;
  includeThermal?: boolean;
}

export interface LandsatDataResponse {
  requestId: string;
  status: string;
  sceneId?: string;
  satellite: string;
  acquisitionDate?: string;
  bands?: Record<string, string>;
}

// =============================================================================
// SIGEOM TYPES - Géologie Québec
// =============================================================================

export interface SigeomDataRequest {
  bbox: BoundingBox;
  includeBedrock?: boolean;
  includeSurficial?: boolean;
  includeFaults?: boolean;
}

export interface SigeomDataResponse {
  requestId: string;
  status: string;
  bedrockGeology?: Record<string, unknown>;
  surficialGeology?: Record<string, unknown>;
  faults?: Array<Record<string, unknown>>;
}

export interface GeologyAnalysis {
  dominantRockType: GeologyType;
  soilPermeability: 'high' | 'medium' | 'low';
  drainageClass: string;
  mineralContent?: Record<string, number>;
  huntingRelevance: string;
}

// =============================================================================
// HYDROLOGY TYPES - Données ouvertes Québec
// =============================================================================

export interface HydrologyDataRequest {
  bbox: BoundingBox;
  includeRivers?: boolean;
  includeLakes?: boolean;
  includeWetlands?: boolean;
  includeWatersheds?: boolean;
  bufferDistance?: number;
}

export interface HydrologyDataResponse {
  requestId: string;
  status: string;
  rivers?: Record<string, unknown>;
  lakes?: Record<string, unknown>;
  wetlands?: Record<string, unknown>;
  watersheds?: Record<string, unknown>;
}

export interface WaterFeature {
  featureType: 'river' | 'lake' | 'wetland' | 'pond';
  name?: string;
  areaM2?: number;
  lengthM?: number;
  distanceFromPoint: number;
  huntingValue: 'high' | 'medium' | 'low';
}

// =============================================================================
// GEOMORPHOLOGY TYPES - Terrain Analysis
// =============================================================================

export interface GeomorphologyRequest {
  bbox: BoundingBox;
  calculateSlope?: boolean;
  calculateAspect?: boolean;
  calculateCurvature?: boolean;
  calculateTpi?: boolean;
  calculateTwi?: boolean;
}

export interface GeomorphologyResponse {
  requestId: string;
  status: string;
  slopeUrl?: string;
  aspectUrl?: string;
  curvatureUrl?: string;
  tpiUrl?: string;
  twiUrl?: string;
  statistics?: Record<string, unknown>;
}

export interface TerrainFeature {
  featureType: 'ridge' | 'valley' | 'saddle' | 'peak' | 'flat';
  elevation: number;
  slopeDegrees: number;
  aspectDegrees: number;
  tpiValue: number;
  huntingSignificance: string;
}

// =============================================================================
// FOREST TYPES - MFFP Québec
// =============================================================================

export interface ForestDataRequest {
  bbox: BoundingBox;
  includeSpecies?: boolean;
  includeAge?: boolean;
  includeDensity?: boolean;
  includeDisturbances?: boolean;
}

export interface ForestDataResponse {
  requestId: string;
  status: string;
  forestStands?: Array<Record<string, unknown>>;
  speciesComposition?: Record<string, number>;
  ageClassDistribution?: Record<string, number>;
}

export interface ForestStand {
  standId: string;
  forestType: ForestType;
  dominantSpecies: string[];
  ageClass: string;
  densityClass: string;
  heightM?: number;
  basalArea?: number;
  huntingValue: 'high' | 'medium' | 'low';
}

// =============================================================================
// AI PREDICTION TYPES
// =============================================================================

export interface AIPredictionRequest {
  bbox: BoundingBox;
  targetSpecies: TargetSpecies;
  season: HuntingSeason;
  layersToInclude?: LayerType[];
  weatherConditions?: Record<string, unknown>;
}

export interface AIPredictionResponse {
  requestId: string;
  status: string;
  corridors?: Array<Record<string, unknown>>;
  feedingZones?: Array<Record<string, unknown>>;
  beddingZones?: Array<Record<string, unknown>>;
  waterZones?: Array<Record<string, unknown>>;
  confidenceScore: number;
}

export interface HuntingCorridor {
  corridorId: string;
  geometry: GeoPolygon;
  corridorType: 'travel' | 'escape' | 'feeding';
  probability: number;
  bestTime: string;
  species: string;
}

export interface PredictionZone {
  zoneId: string;
  geometry: GeoPolygon;
  zoneType: 'feeding' | 'bedding' | 'water' | 'thermal';
  probability: number;
  bestHours: string[];
  terrainFeatures: string[];
}

// =============================================================================
// HUNTING POTENTIAL TYPES
// =============================================================================

export interface HuntingPotentialRequest {
  bbox: BoundingBox;
  centerPoint: GeoCoordinate;
  radiusM?: number;
  targetSpecies: TargetSpecies;
  season: HuntingSeason;
  includeAiPredictions?: boolean;
}

export interface HuntingPotentialResponse {
  requestId: string;
  status: string;
  overallScore: number;
  level: HuntingPotentialLevel;
  componentScores?: Record<string, number>;
  recommendations?: string[];
  hotspots?: Array<Record<string, unknown>>;
  bestStandLocations?: Array<Record<string, unknown>>;
}

export interface PotentialComponent {
  name: string;
  score: number;
  weight: number;
  description: string;
  dataSource: DataSourceType;
}

export interface HuntingHotspot {
  hotspotId: string;
  location: GeoCoordinate;
  score: number;
  radiusM: number;
  primaryFeature: string;
  secondaryFeatures: string[];
  bestApproach: string;
  recommendedTime: string;
}

// =============================================================================
// ENGINE STATUS TYPES
// =============================================================================

export interface GeospatialEngineStatus {
  status: 'ready' | 'initializing' | 'error';
  engineVersion: string;
  architectureReady: boolean;
  implementationPending: boolean;
  dataSources: Record<string, DataSourceStatus>;
  modules: Record<string, ModuleStatus>;
}

export interface DataSourceStatus {
  status: 'ready' | 'architecture_ready' | 'unavailable';
  url: string;
  lastCheck?: string;
}

export interface ModuleStatus {
  status: 'prepared' | 'implemented' | 'testing';
  dependencies?: string[];
}

export interface DataSourceInfo {
  id: DataSourceType;
  name: string;
  provider: string;
  url: string;
  license: string;
  coverage: string;
  resolution: string;
  formats: string[];
  free: boolean;
}
