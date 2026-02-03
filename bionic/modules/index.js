/**
 * BIONIC™ Modules - Index
 * Registry central de tous les modules BIONIC™
 */

// Module imports
import * as nutritionModule from "./nutrition/index.js";

// Registry of all available modules
export const modules = {
  nutrition: nutritionModule
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
