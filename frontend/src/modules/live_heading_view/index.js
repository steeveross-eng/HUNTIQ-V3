/**
 * Live Heading View Module - PHASE 6
 * 
 * Immersive live heading view for hunting navigation.
 * 
 * Features:
 * - GPS-based travelling view
 * - Forward cone (30-60°)
 * - Direction line
 * - Wind overlay (real-time)
 * - POI markers
 * - Alerts overlay
 * - Compass widget
 * 
 * @module live_heading_view
 * @version 1.0.0
 */

export const MODULE_NAME = 'live_heading_view';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'special';

// Component exports
export { LiveHeadingView } from './components/LiveHeadingView';
export { CompassWidget } from './components/CompassWidget';
export { ForwardCone } from './components/ForwardCone';
export { WindIndicator } from './components/WindIndicator';
export { POIMarker } from './components/POIMarker';
export { AlertToast } from './components/AlertToast';
export { SessionControls } from './components/SessionControls';
export { SessionStats } from './components/SessionStats';
