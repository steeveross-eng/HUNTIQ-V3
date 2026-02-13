# BIONIC V3 - Frontend Modules

## Overview

This directory contains the modular frontend architecture for BIONIC V3.
Each module is isolated and follows strict architectural rules.

## Architecture Version: 3.0.0

## Module Categories

### CORE MODULES (9)

| Module | Description |
|--------|-------------|
| `weather` | Weather display and widgets |
| `scoring` | Score visualization |
| `strategy` | Strategy panel |
| `geospatial` | Map layers |
| `ai` | AI analysis UI |
| `wms` | WMS layer management |
| `marketplace` | E-commerce components |
| `admin` | Admin dashboard |
| `tracking` | Live tracking UI |

### ADVANCED MODULES (10)

| Module | Description |
|--------|-------------|
| `ecoforestry` | Ecoforestry visualization |
| `advanced_geospatial` | Advanced geospatial UI |
| `engine_3d` | 3D terrain viewer |
| `wildlife_behavior` | Wildlife behavior patterns |
| `simulation` | Simulation controls |
| `adaptive_strategy` | Adaptive strategy UI |
| `recommendation` | Recommendation widgets |
| `progression` | User progression UI |
| `collaborative` | Collaboration features |
| `plugins` | Plugin manager |

### SPECIAL MODULES (1)

| Module | Description |
|--------|-------------|
| `live_heading_view` | Immersive live heading view |

## Module Structure

```
module_name/
├── index.js              # Module entry point and exports
├── ModuleEngine.js       # Core logic (optional)
├── ModuleService.js      # API service (optional)
└── components/           # React components
    ├── Component1.jsx
    └── Component2.jsx
```

## Development Rules

1. **NO CROSS-MODULE IMPORTS** - Modules are isolated
2. **NO MODIFICATION** - Never modify existing module code
3. **NEW FEATURE = NEW MODULE** - Always create new modules
4. **USE COMPONENTS FROM CORE** - Use `/components/ui/` for base UI

## Usage

```javascript
import { WeatherWidget } from '@/modules/weather';
import { ScoreDisplay } from '@/modules/scoring';
import { LiveHeadingView } from '@/modules/live_heading_view';
```

---

*BIONIC V3 - Frontend Modules - Created 2026-02-09*
