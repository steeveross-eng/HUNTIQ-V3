/**
 * EcoforestryDataSources.jsx
 * 
 * Configuration centralisée des sources de données écoforestières
 * officielles du Canada et des États-Unis pour BIONIC™
 * 
 * SOURCES LÉGALES ET OFFICIELLES :
 * 
 * CANADA :
 * - Québec : MRNF via NFIS, Forêt Ouverte, Données Québec
 * - National : Natural Resources Canada (NRCan), NFI (National Forest Inventory)
 * - Ontario : Ontario GeoHub
 * - British Columbia : BC Data Catalogue
 * - Alberta : Alberta Open Data
 * - Nouveau-Brunswick : GNB Open Data
 * 
 * ÉTATS-UNIS :
 * - USDA Forest Service : EDW Map Services
 * - USGS : National Map Services
 * 
 * Documentation : https://www.quebec.ca/agriculture-environnement-et-ressources-naturelles/forets/recherche-connaissances/inventaire-forestier/donnees-cartes-resultats
 */

// ============================================
// CONFIGURATION DES SOURCES DE DONNÉES
// ============================================

/**
 * Sources de données écoforestières du CANADA
 */
export const CANADA_FOREST_SERVICES = {
  // ============================================
  // QUÉBEC - Sources principales
  // ============================================
  quebec: {
    id: 'quebec',
    name: 'Québec',
    flag: '🇨🇦',
    region: 'QC',
    authority: 'Ministère des Ressources naturelles et des Forêts (MRNF)',
    contact: 'inventaires.forestiers@mrnf.gouv.qc.ca',
    documentation: 'https://www.quebec.ca/agriculture-environnement-et-ressources-naturelles/forets/recherche-connaissances/inventaire-forestier/donnees-cartes-resultats',
    services: {
      // Service NFIS (National Forest Information System) - Principal
      nfis: {
        name: 'NFIS Québec',
        type: 'WMS',
        url: 'https://ca.nfis.org/cubewerx/cubeserv',
        datastore: 'NFIS-QC',
        versions: ['1.3.0', '1.1.1', '1.1.0'],
        layers: {
          carte_ecoforestiere: {
            id: 'qc_5einv_index_carte_ecoforestiere',
            name: 'Index carte écoforestière',
            description: 'Index des feuillets de la carte écoforestière du 5e inventaire',
            scale: '1:20000'
          },
          disponibilite: {
            id: 'qc_5einv_disponibilite',
            name: 'Disponibilité des données',
            description: 'État de disponibilité des inventaires écoforestiers'
          },
          volume_forestier: {
            id: 'qc_volumeforestier',
            name: 'Volume forestier',
            description: 'Volume marchand (7m+) par essence'
          },
          vegetation_potentielle: {
            id: 'qc_vegetation_potentielle',
            name: 'Végétation potentielle',
            description: 'Classification de la végétation potentielle'
          },
          classification_ecologique: {
            id: 'qc_classification_ecologique',
            name: 'Classification écologique',
            description: 'Types écologiques du territoire'
          },
          depots_surface: {
            id: 'qc_depots_surface',
            name: 'Dépôts de surface',
            description: 'Classification des dépôts de surface'
          },
          interventions_sylvicoles: {
            id: 'qc_interventions_sylvicoles',
            name: 'Interventions sylvicoles 2016-2023',
            description: 'Travaux sylvicoles réalisés'
          },
          pien: {
            id: 'qc_pien_inventaire',
            name: 'Inventaire écoforestier nordique (PIEN)',
            description: 'Programme d\'inventaire écoforestier nordique'
          },
          placettes_echantillonnage: {
            id: 'qc_placettes_terrestres',
            name: 'Placettes d\'échantillonnage',
            description: 'Points de relevés terrestres'
          }
        }
      },
      // Données Québec - Carte écoforestière avec perturbations
      donnees_quebec: {
        name: 'Données Québec - Carte écoforestière',
        type: 'WMS',
        url: 'https://servicescarto.mffp.gouv.qc.ca/pes/services/Inventaire/CarteEcoforestiere/MapServer/WMSServer',
        description: 'Carte écoforestière à jour avec perturbations',
        lastUpdate: '2025-07-14',
        layers: {
          peuplements: {
            id: '0',
            name: 'Peuplements forestiers',
            description: 'Types de peuplements et caractéristiques'
          },
          perturbations: {
            id: '1',
            name: 'Perturbations récentes',
            description: 'Feux, coupes, épidémies, chablis'
          }
        }
      },
      // Service alternatif - MSP
      msp: {
        name: 'MSP Géoportail',
        type: 'WMS',
        url: 'https://geoegl.msp.gouv.qc.ca/ws/mffpecofor.fcgi',
        description: 'Service WMS du Ministère de la Sécurité publique',
        layers: {
          carte_ecoforestiere: {
            id: 'carte_ecoforestiere',
            name: 'Carte écoforestière complète'
          }
        }
      }
    },
    bounds: {
      north: 62.5,
      south: 45.0,
      west: -79.5,
      east: -57.0
    }
  },

  // ============================================
  // ONTARIO
  // ============================================
  ontario: {
    id: 'ontario',
    name: 'Ontario',
    flag: '🇨🇦',
    region: 'ON',
    authority: 'Ministry of Natural Resources and Forestry (MNRF)',
    documentation: 'https://geohub.lio.gov.on.ca/',
    services: {
      geohub: {
        name: 'Ontario GeoHub',
        type: 'REST',
        url: 'https://ws.lioservices.lrc.gov.on.ca/arcgis1061a/rest/services/LIO_Open_Data',
        layers: {
          forest_resource_inventory: {
            id: 'LIO_Open_Data/Forest_Resources_Inventory',
            name: 'Forest Resources Inventory',
            description: 'Inventaire des ressources forestières de l\'Ontario'
          },
          forest_management_units: {
            id: 'LIO_Open_Data/Forest_Management_Unit',
            name: 'Forest Management Units',
            description: 'Unités de gestion forestière'
          },
          fire_management: {
            id: 'LIO_Open_Data/Fire_Management_Zone',
            name: 'Fire Management Zones',
            description: 'Zones de gestion des incendies'
          }
        }
      }
    },
    bounds: {
      north: 56.9,
      south: 41.7,
      west: -95.2,
      east: -74.3
    }
  },

  // ============================================
  // COLOMBIE-BRITANNIQUE
  // ============================================
  british_columbia: {
    id: 'british_columbia',
    name: 'Colombie-Britannique',
    flag: '🇨🇦',
    region: 'BC',
    authority: 'Ministry of Forests',
    documentation: 'https://catalogue.data.gov.bc.ca/',
    services: {
      bcgw: {
        name: 'BC Geographic Warehouse',
        type: 'WMS',
        url: 'https://openmaps.gov.bc.ca/geo/pub/wms',
        layers: {
          vri: {
            id: 'WHSE_FOREST_VEGETATION.VEG_COMP_LYR_R1_POLY',
            name: 'Vegetation Resource Inventory (VRI)',
            description: 'Inventaire des ressources végétales'
          },
          fire_perimeters: {
            id: 'WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_POLYS_SP',
            name: 'Current Fire Perimeters',
            description: 'Périmètres des feux actifs'
          },
          forest_tenure: {
            id: 'WHSE_FOREST_TENURE.FTEN_HARVEST_AUTH_POLY_SVW',
            name: 'Forest Tenure Harvest',
            description: 'Autorisations de récolte forestière'
          },
          cutblocks: {
            id: 'WHSE_FOREST_VEGETATION.RSLT_OPENING_SVW',
            name: 'Cutblocks/Openings',
            description: 'Blocs de coupe et ouvertures'
          }
        }
      }
    },
    bounds: {
      north: 60.0,
      south: 48.3,
      west: -139.1,
      east: -114.0
    }
  },

  // ============================================
  // ALBERTA
  // ============================================
  alberta: {
    id: 'alberta',
    name: 'Alberta',
    flag: '🇨🇦',
    region: 'AB',
    authority: 'Alberta Environment and Protected Areas',
    documentation: 'https://open.alberta.ca/opendata',
    services: {
      ags: {
        name: 'Alberta Geospatial Services',
        type: 'REST',
        url: 'https://maps.alberta.ca/genesis/rest/services',
        layers: {
          forest_management_agreement: {
            id: 'Alberta_FMA_Areas',
            name: 'Forest Management Agreement Areas',
            description: 'Zones d\'entente de gestion forestière'
          },
          vegetation_inventory: {
            id: 'Alberta_Vegetation_Inventory',
            name: 'Alberta Vegetation Inventory (AVI)',
            description: 'Inventaire de végétation'
          }
        }
      }
    },
    bounds: {
      north: 60.0,
      south: 49.0,
      west: -120.0,
      east: -110.0
    }
  },

  // ============================================
  // NOUVEAU-BRUNSWICK
  // ============================================
  new_brunswick: {
    id: 'new_brunswick',
    name: 'Nouveau-Brunswick',
    flag: '🇨🇦',
    region: 'NB',
    authority: 'Department of Natural Resources and Energy Development',
    documentation: 'https://www2.gnb.ca/content/gnb/en/departments/erd/open-data/forestry.html',
    services: {
      gnb: {
        name: 'GNB Open Data WMS',
        type: 'WMS',
        url: 'https://geonb.snb.ca/arcgis/services/GeoNB_ENR_ForestManagement/MapServer/WMSServer',
        layers: {
          forest_inventory: {
            id: 'Forest_Inventory',
            name: 'Forest Inventory',
            description: 'Inventaire forestier du Nouveau-Brunswick'
          },
          vegetation_management: {
            id: 'Vegetation_Management',
            name: 'Vegetation Management',
            description: 'Gestion de la végétation'
          },
          reforestation: {
            id: 'Reforestation',
            name: 'Reforestation',
            description: 'Zones de reboisement'
          },
          silviculture: {
            id: 'Silviculture',
            name: 'Silviculture',
            description: 'Interventions sylvicoles'
          }
        }
      }
    },
    bounds: {
      north: 48.1,
      south: 44.6,
      west: -69.1,
      east: -63.8
    }
  },

  // ============================================
  // CANADA NATIONAL - NRCan / NFI
  // ============================================
  canada_national: {
    id: 'canada_national',
    name: 'Canada National (NFI)',
    flag: '🇨🇦',
    region: 'CA',
    authority: 'Natural Resources Canada (NRCan) / Canadian Forest Service',
    documentation: 'https://nfi.nfis.org/en/maps',
    services: {
      nfi: {
        name: 'National Forest Inventory',
        type: 'WMS/WFS',
        url: 'https://ca.nfis.org/mapserver/cgi-bin/ccfm_managed_forests_eng.cgi',
        description: 'Inventaire forestier national du Canada',
        layers: {
          managed_forests: {
            id: 'managed_forests',
            name: 'Managed Forests of Canada',
            description: 'Forêts aménagées du Canada'
          },
          forest_management: {
            id: 'forest_management_classification',
            name: 'Forest Management Classification',
            description: 'Classification de la gestion forestière'
          }
        }
      },
      scanfi: {
        name: 'SCANFI - Spatialized Canadian NFI',
        type: 'WMS',
        url: 'https://ca.nfis.org/cubewerx/cubeserv',
        datastore: 'SCANFI',
        description: 'Cartes raster 30m du couvert terrestre et hauteur de canopée (2020)',
        layers: {
          land_cover: {
            id: 'scanfi_landcover_2020',
            name: 'Land Cover 2020',
            description: 'Couverture terrestre 30m'
          },
          canopy_height: {
            id: 'scanfi_canopy_height_2020',
            name: 'Canopy Height 2020',
            description: 'Hauteur de canopée 30m'
          }
        }
      }
    },
    bounds: {
      north: 83.0,
      south: 41.7,
      west: -141.0,
      east: -52.6
    }
  }
};

/**
 * Sources de données écoforestières des ÉTATS-UNIS
 */
export const USA_FOREST_SERVICES = {
  // ============================================
  // USDA FOREST SERVICE
  // ============================================
  usfs: {
    id: 'usfs',
    name: 'USDA Forest Service',
    flag: '🇺🇸',
    region: 'US',
    authority: 'United States Department of Agriculture - Forest Service',
    documentation: 'https://data.fs.usda.gov/geodata/edw/mapServices.php',
    services: {
      edw: {
        name: 'Enterprise Data Warehouse (EDW)',
        type: 'REST',
        url: 'https://apps.fs.usda.gov/arcx/rest/services/EDW',
        layers: {
          national_forests: {
            id: 'EDW_ForestSystemBoundaries_01/MapServer',
            name: 'National Forest System Boundaries',
            description: 'Limites des forêts nationales'
          },
          wilderness_areas: {
            id: 'EDW_WildernessAreas_01/MapServer',
            name: 'National Wilderness Areas',
            description: 'Zones de nature sauvage désignées'
          },
          fire_perimeters: {
            id: 'EDW_FireOccurrencePoint_01/MapServer',
            name: 'Fire Occurrence Points',
            description: 'Points d\'occurrence des incendies'
          },
          roads: {
            id: 'EDW_RoadCore_01/MapServer',
            name: 'Forest Roads',
            description: 'Routes forestières'
          },
          trails: {
            id: 'EDW_TrailNFSPublish_01/MapServer',
            name: 'National Forest System Trails',
            description: 'Sentiers du système forestier national'
          }
        }
      },
      hub: {
        name: 'USFS ArcGIS Hub',
        type: 'REST',
        url: 'https://data-usfs.hub.arcgis.com/api',
        searchEndpoint: 'https://data-usfs.hub.arcgis.com/api/search/definition/',
        description: 'Portail de découverte de données géospatiales USFS'
      }
    },
    bounds: {
      north: 49.4,
      south: 24.4,
      west: -124.8,
      east: -66.9
    }
  },

  // ============================================
  // USGS - US GEOLOGICAL SURVEY
  // ============================================
  usgs: {
    id: 'usgs',
    name: 'US Geological Survey',
    flag: '🇺🇸',
    region: 'US',
    authority: 'United States Geological Survey',
    documentation: 'https://www.usgs.gov/products/web-tools/apis',
    services: {
      national_map: {
        name: 'The National Map',
        type: 'WMS',
        url: 'https://basemap.nationalmap.gov/arcgis/services',
        layers: {
          topo: {
            id: 'USGSTopo/MapServer',
            name: 'USGS Topo',
            description: 'Cartes topographiques USGS'
          },
          imagery: {
            id: 'USGSImageryTopo/MapServer',
            name: 'USGS Imagery Topo',
            description: 'Imagerie avec couches topographiques'
          },
          hydro: {
            id: 'USGSHydroCached/MapServer',
            name: 'USGS Hydro',
            description: 'Hydrographie nationale'
          }
        }
      },
      landcover: {
        name: 'National Land Cover Database',
        type: 'WMS',
        url: 'https://www.mrlc.gov/geoserver/wms',
        layers: {
          nlcd: {
            id: 'nlcd_2021',
            name: 'NLCD 2021',
            description: 'Base de données nationale de couverture terrestre 2021'
          }
        }
      }
    },
    bounds: {
      north: 49.4,
      south: 24.4,
      west: -124.8,
      east: -66.9
    }
  }
};

/**
 * Toutes les sources combinées
 */
export const ALL_FOREST_SERVICES = {
  ...CANADA_FOREST_SERVICES,
  ...USA_FOREST_SERVICES
};

/**
 * Configuration des couches par catégorie
 */
export const LAYER_CATEGORIES = {
  inventory: {
    id: 'inventory',
    name: 'Inventaires forestiers',
    icon: '📊',
    description: 'Données d\'inventaire forestier'
  },
  classification: {
    id: 'classification',
    name: 'Classifications de peuplements',
    icon: '🌲',
    description: 'Types de peuplements et essences'
  },
  disturbances: {
    id: 'disturbances',
    name: 'Perturbations récentes',
    icon: '🔥',
    description: 'Feux, coupes, épidémies, chablis'
  },
  dendrometric: {
    id: 'dendrometric',
    name: 'Données dendrométriques',
    icon: '📏',
    description: 'Volume, hauteur, surface terrière'
  },
  lidar: {
    id: 'lidar',
    name: 'Couches LiDAR',
    icon: '🛰️',
    description: 'Données LiDAR haute résolution'
  },
  boundaries: {
    id: 'boundaries',
    name: 'Limites administratives',
    icon: '🗺️',
    description: 'Forêts nationales, unités de gestion'
  }
};

/**
 * Statut de disponibilité des services
 */
export const ServiceStatus = {
  AVAILABLE: 'available',
  CHECKING: 'checking',
  UNAVAILABLE: 'unavailable',
  ERROR: 'error',
  RATE_LIMITED: 'rate_limited'
};

/**
 * Mapping des couches par région et catégorie
 */
export const getLayersByRegion = (regionId) => {
  return ALL_FOREST_SERVICES[regionId] || null;
};

/**
 * Obtenir toutes les couches d'une catégorie spécifique
 */
export const getLayersByCategory = (categoryId) => {
  const layers = [];
  
  Object.values(ALL_FOREST_SERVICES).forEach(region => {
    if (region.services) {
      Object.values(region.services).forEach(service => {
        if (service.layers) {
          Object.entries(service.layers).forEach(([layerId, layer]) => {
            // Ajouter une logique de catégorisation basée sur le nom/description
            const isMatch = 
              (categoryId === 'inventory' && (layerId.includes('inventory') || layerId.includes('inventaire'))) ||
              (categoryId === 'disturbances' && (layerId.includes('fire') || layerId.includes('perturbation'))) ||
              (categoryId === 'lidar' && layerId.includes('lidar')) ||
              (categoryId === 'dendrometric' && (layerId.includes('volume') || layerId.includes('height')));
            
            if (isMatch) {
              layers.push({
                ...layer,
                regionId: region.id,
                regionName: region.name,
                serviceUrl: service.url,
                serviceType: service.type
              });
            }
          });
        }
      });
    }
  });
  
  return layers;
};

export default ALL_FOREST_SERVICES;
