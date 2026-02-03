/**
 * HUNTIQ V3 - Hooks Index
 * Centralized export of all custom hooks
 */

// UI Hooks
export { useToast, toast } from './use-toast';

// Data Hooks
export { default as useProducts } from './useProducts';
export { default as useCart } from './useCart';
export { default as useWeather } from './useWeather';
export { default as useCommunity } from './useCommunity';
export { default as useBlog } from './useBlog';
export { default as usePartners } from './usePartners';

// BIONIC Hooks
export { default as useBionicLayers } from './useBionicLayers';
export { default as useBionicScoring } from './useBionicScoring';
export { default as useBionicStrategy } from './useBionicStrategy';
export { default as useBionicWeather } from './useBionicWeather';

// Feature Hooks
export { default as useAnalytics } from './useAnalytics';
export { default as useLiveTracking } from './useLiveTracking';
export { default as useSharing } from './useSharing';
export { default as useUserData } from './useUserData';
export { default as useWaterExclusion } from './useWaterExclusion';
