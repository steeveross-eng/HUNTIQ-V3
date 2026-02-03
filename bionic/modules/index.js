/**
 * BIONIC™ Modules - Index
 * Registry central de tous les modules BIONIC™
 */

// Module imports
import * as nutritionModule from "./nutrition/index.js";
import * as hydrologyModule from "./hydrology/index.js";
import * as sentinelModule from "./sentinel/index.js";
import * as sigeomModule from "./sigeom/index.js";

// Registry of all available modules
export const modules = {
  nutrition: nutritionModule,
  hydrology: hydrologyModule,
  sentinel: sentinelModule,
  sigeom: sigeomModule
};

// Get module by ID
export function getModule(moduleId) {
  return modules[moduleId] || null;
}

// List all available modules
export function listModules() {
  return Object.entries(modules).map(([id, mod]) => ({
    id,
    ...mod.moduleInfo
  }));
}
