/**
 * BionicMicroZones.jsx
 * 
 * Composant de rendu des zones BIONIC micro-délimitées
 * Style visuel "DANY LAVOIE" - SEGMENTATION AVANCÉE avec CLIPPING GÉOMÉTRIQUE
 * 
 * RÈGLES CLÉS DE RENDU :
 * 1. Chaque zone = entité graphique INDÉPENDANTE
 * 2. Superpositions = couches DISTINCTES visibles simultanément
 * 3. AUCUNE fusion, aplatissement ou simplification
 * 4. Chaque segment conserve : contour propre, couleur thématique, pourcentage, attributs
 * 5. CLIPPING GÉOMÉTRIQUE : Segments visuels distincts aux intersections
 * 6. LIGNES DE DÉLIMITATION SPÉCIALES aux croisements entre zones
 * 7. Lignes vectorielles ULTRA-FINES et ADAPTATIVES selon le zoom :
 *    - Fort zoom (analyse locale) : épaisseur augmentée pour précision visuelle
 *    - Faible zoom (vue globale) : réduction drastique pour carte non saturée
 * 8. Lisibilité parfaite même en superposition multiple
 */

import React, { useMemo, useState, useCallback, useEffect } from 'react';
import { Circle, CircleMarker, Polyline, Tooltip, useMap, Polygon } from 'react-leaflet';
import { Badge } from '@/components/ui/badge';

// Configuration des modules thématiques - Style "Dany Lavoie"
// Couleurs vives et saturées pour contraste optimal sur carte topo
export const BIONIC_MODULES = {
  habitats: { 
    color: '#00CC00', // Vert vif (style Dany Lavoie)
    label: 'Habitat optimal', 
    icon: '🌲',
    interpretation: { high: 'Zone de refuge idéale', medium: 'Habitat favorable', low: 'Habitat secondaire' }
  },
  rut: { 
    color: '#FF0066', // Rose/magenta vif
    label: 'Zone de rut', 
    icon: '💕',
    interpretation: { high: 'Activité intense', medium: 'Zone de reproduction', low: 'Passage occasionnel' }
  },
  affuts: { 
    color: '#9900FF', // Violet vif
    label: 'Affût potentiel', 
    icon: '🎯',
    interpretation: { high: 'Position stratégique', medium: 'Bon potentiel', low: 'Point d\'observation' }
  },
  corridors: { 
    color: '#FF9900', // Orange vif (style Dany Lavoie)
    label: 'Corridor faunique', 
    icon: '🦌',
    interpretation: { high: 'Passage principal', medium: 'Route fréquente', low: 'Itinéraire secondaire' }
  },
  alimentation: { 
    color: '#66CC00', // Vert lime
    label: 'Zone alimentation', 
    icon: '🌿',
    interpretation: { high: 'Gagnage optimal', medium: 'Zone de nourrissage', low: 'Ressource limitée' }
  },
  repos: { 
    color: '#996633', // Brun/terre
    label: 'Zone de repos', 
    icon: '💤',
    interpretation: { high: 'Remise principale', medium: 'Zone de couche', low: 'Repos temporaire' }
  },
  fraicheur: { 
    color: '#00CCFF', // Cyan vif
    label: 'Zone de fraîcheur', 
    icon: '💧',
    interpretation: { high: 'Point d\'eau vital', medium: 'Zone humide', low: 'Fraîcheur relative' }
  },
  salines: { 
    color: '#FFFF00', // Jaune vif (style Dany Lavoie)
    label: 'Saline potentielle', 
    icon: '🧂',
    interpretation: { high: 'Saline active', medium: 'Zone minérale', low: 'Présence possible' }
  },
  transition: { 
    color: '#999999', // Gris moyen
    label: 'Zone tampon', 
    icon: '↔️',
    interpretation: { high: 'Transition clé', medium: 'Zone intermédiaire', low: 'Bordure de territoire' }
  }
};

// Obtenir l'interprétation basée sur le pourcentage
const getInterpretation = (moduleId, percentage) => {
  const module = BIONIC_MODULES[moduleId];
  if (!module) return 'Zone analysée';
  
  if (percentage >= 80) return module.interpretation.high;
  if (percentage >= 60) return module.interpretation.medium;
  return module.interpretation.low;
};

// ============================================
// GÉOMÉTRIE - CALCUL DES INTERSECTIONS ET CLIPPING
// Style "DANY LAVOIE" avec segments distincts
// ============================================

/**
 * Calcule la distance entre deux points [lat, lng]
 */
const getDistance = (p1, p2) => {
  const R = 6371000; // Rayon de la Terre en mètres
  const lat1 = p1[0] * Math.PI / 180;
  const lat2 = p2[0] * Math.PI / 180;
  const dLat = (p2[0] - p1[0]) * Math.PI / 180;
  const dLng = (p2[1] - p1[1]) * Math.PI / 180;
  
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1) * Math.cos(lat2) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  
  return R * c;
};

/**
 * Calcule les points d'intersection entre deux cercles
 * Retourne les deux points où les cercles se croisent
 */
const calculateCircleIntersections = (center1, radius1, center2, radius2) => {
  const d = getDistance(center1, center2);
  
  // Pas d'intersection si les cercles sont trop éloignés ou l'un contient l'autre
  if (d > radius1 + radius2 || d < Math.abs(radius1 - radius2) || d === 0) {
    return null;
  }
  
  // Calcul des points d'intersection en coordonnées cartésiennes locales
  const a = (radius1 * radius1 - radius2 * radius2 + d * d) / (2 * d);
  const h = Math.sqrt(Math.max(0, radius1 * radius1 - a * a));
  
  // Vecteur direction entre les centres
  const lat1 = center1[0], lng1 = center1[1];
  const lat2 = center2[0], lng2 = center2[1];
  
  // Approximation locale pour petites distances
  const dLat = lat2 - lat1;
  const dLng = (lng2 - lng1) * Math.cos(lat1 * Math.PI / 180);
  const norm = Math.sqrt(dLat * dLat + dLng * dLng);
  
  if (norm === 0) return null;
  
  // Point milieu sur la ligne entre les centres
  const ratio = a / d;
  const midLat = lat1 + dLat * ratio;
  const midLng = lng1 + (lng2 - lng1) * ratio;
  
  // Perpendiculaire
  const perpLat = -dLng / norm;
  const perpLng = dLat / norm / Math.cos(midLat * Math.PI / 180);
  
  // Conversion de h en degrés (approximatif)
  const hDeg = h / 111320; // ~111km par degré
  
  return {
    point1: [midLat + perpLat * hDeg, midLng + perpLng * hDeg],
    point2: [midLat - perpLat * hDeg, midLng - perpLng * hDeg],
    midpoint: [midLat, midLng]
  };
};

/**
 * Génère un arc de cercle entre deux angles
 * Utilisé pour créer les segments de clipping
 */
const generateArc = (center, radius, startAngle, endAngle, segments = 32) => {
  const points = [];
  const step = (endAngle - startAngle) / segments;
  
  for (let i = 0; i <= segments; i++) {
    const angle = startAngle + i * step;
    const lat = center[0] + (radius / 111320) * Math.cos(angle);
    const lng = center[1] + (radius / (111320 * Math.cos(center[0] * Math.PI / 180))) * Math.sin(angle);
    points.push([lat, lng]);
  }
  
  return points;
};

/**
 * Calcule l'angle entre le centre d'un cercle et un point
 */
const getAngleFromCenter = (center, point) => {
  const dLat = point[0] - center[0];
  const dLng = (point[1] - center[1]) * Math.cos(center[0] * Math.PI / 180);
  return Math.atan2(dLng, dLat);
};

// ============================================
// STYLE "DANY LAVOIE" - SEGMENTATION AVANCÉE
// Lignes vectorielles ultra-fines et adaptatives
// Épaisseur recalculée dynamiquement selon le zoom
// ============================================

/**
 * Épaisseur du contour adaptative au zoom - ALGORITHME VECTORIEL "DANY LAVOIE"
 * 
 * COMPORTEMENT DYNAMIQUE :
 * - Fort zoom (≥16) : Épaisseur AUGMENTÉE pour précision visuelle maximale
 * - Zoom moyen (12-15) : Épaisseur ÉQUILIBRÉE pour lecture confortable
 * - Faible zoom (≤11) : Réduction DRASTIQUE pour carte propre et non saturée
 * 
 * La formule utilise une courbe exponentielle pour une transition fluide
 */
const getStrokeWeight = (percentage, isHovered, zoom = 12) => {
  // Facteur d'épaisseur VECTORIEL selon le zoom (courbe exponentielle)
  // Plus le zoom est élevé, plus l'épaisseur augmente pour la précision
  // Plus le zoom est bas, plus l'épaisseur est réduite drastiquement
  
  let zoomFactor;
  if (zoom >= 18) {
    zoomFactor = 0.70;     // Ultra zoomé : précision maximale
  } else if (zoom >= 16) {
    zoomFactor = 0.55;     // Très zoomé : haute précision
  } else if (zoom >= 14) {
    zoomFactor = 0.38;     // Zoomé : lecture détaillée
  } else if (zoom >= 12) {
    zoomFactor = 0.22;     // Moyen : équilibré
  } else if (zoom >= 10) {
    zoomFactor = 0.12;     // Éloigné : fin
  } else if (zoom >= 8) {
    zoomFactor = 0.06;     // Très éloigné : ultra-fin
  } else {
    zoomFactor = 0.03;     // Vue globale : quasi invisible (réduction drastique)
  }
  
  // Calcul de base selon le pourcentage et l'état hover
  // Les zones à fort pourcentage ont des contours légèrement plus marqués
  let baseWeight;
  if (isHovered) {
    baseWeight = 5.5;      // Survol : rétroaction visuelle claire
  } else if (percentage >= 90) {
    baseWeight = 5.0;      // Zone très haute priorité
  } else if (percentage >= 75) {
    baseWeight = 4.5;
  } else if (percentage >= 60) {
    baseWeight = 4.0;
  } else if (percentage >= 45) {
    baseWeight = 3.5;
  } else {
    baseWeight = 3.0;
  }
  
  // Application du facteur de zoom
  const weight = baseWeight * zoomFactor;
  
  // Limites adaptatives au zoom pour garantir la lisibilité
  // Fort zoom : permet des bordures plus épaisses pour la précision
  // Faible zoom : force des bordures très fines pour éviter saturation
  const minWeight = zoom >= 16 ? 1.2 : zoom >= 14 ? 0.6 : zoom >= 12 ? 0.3 : 0.1;
  const maxWeight = zoom >= 16 ? 4.0 : zoom >= 14 ? 2.5 : zoom >= 12 ? 1.5 : 0.5;
  
  return Math.max(minWeight, Math.min(maxWeight, weight));
};

/**
 * Épaisseur des cercles concentriques adaptative au zoom - STYLE VECTORIEL
 * Suit la même logique que les contours principaux avec atténuation progressive
 */
const getConcentricStrokeWeight = (zoom = 12, index = 0) => {
  // Atténuation progressive pour chaque cercle concentrique
  const attenuation = 1 - (index * 0.25);
  
  let baseWeight;
  if (zoom >= 16) {
    baseWeight = 1.8 * attenuation;
  } else if (zoom >= 14) {
    baseWeight = 1.0 * attenuation;
  } else if (zoom >= 12) {
    baseWeight = 0.5 * attenuation;
  } else if (zoom >= 10) {
    baseWeight = 0.25 * attenuation;
  } else {
    baseWeight = 0.1 * attenuation;
  }
  return Math.max(0.08, baseWeight);
};

/**
 * Opacité du remplissage - STYLE "DANY LAVOIE"
 * Semi-transparent pour voir le terrain sous-jacent
 * Légèrement plus opaque pour les zones à fort pourcentage
 */
const getFillOpacity = (percentage, isHovered) => {
  if (isHovered) return 0.45; // Survol : mise en évidence
  if (percentage >= 90) return 0.38;
  if (percentage >= 75) return 0.32;
  if (percentage >= 60) return 0.26;
  if (percentage >= 45) return 0.22;
  return 0.18;
};

/**
 * Opacité du contour - STYLE VECTORIEL
 * Toujours bien visible pour garantir la segmentation
 */
const getStrokeOpacity = (percentage, isHovered) => {
  if (isHovered) return 1;
  if (percentage >= 75) return 0.95;
  if (percentage >= 60) return 0.90;
  return 0.85;
};

/**
 * Épaisseur des lignes d'intersection adaptative au zoom
 * Ces lignes marquent les croisements entre zones
 */
const getIntersectionStrokeWeight = (zoom = 12) => {
  if (zoom >= 16) return 2.0;
  if (zoom >= 14) return 1.2;
  if (zoom >= 12) return 0.6;
  if (zoom >= 10) return 0.3;
  return 0.15;
};

/**
 * Composant IntersectionLine - LIGNE DE DÉLIMITATION SPÉCIALE
 * Affiche une ligne aux points de croisement entre deux zones
 */
const IntersectionLine = ({ intersection, zoom }) => {
  if (!intersection || !intersection.point1 || !intersection.point2) return null;
  
  const weight = getIntersectionStrokeWeight(zoom);
  
  // Couleur spéciale pour les lignes d'intersection (blanc/gris clair)
  // Permet de distinguer clairement les croisements
  return (
    <Polyline
      positions={[intersection.point1, intersection.point2]}
      pathOptions={{
        color: '#FFFFFF',
        weight: weight,
        opacity: 0.85,
        dashArray: zoom >= 14 ? '4, 2' : '2, 1',
        lineCap: 'round',
        lineJoin: 'round'
      }}
    />
  );
};

/**
 * Composant MicroZone - SEGMENTATION AVANCÉE "DANY LAVOIE"
 * 
 * RÈGLES DE RENDU :
 * 1. Chaque zone = entité graphique INDÉPENDANTE
 * 2. Contour propre, couleur thématique, pourcentage et attributs conservés
 * 3. Lignes vectorielles ultra-fines et adaptatives au zoom
 * 4. Aucune fusion avec les zones voisines
 * 5. CLIPPING GÉOMÉTRIQUE : contours distincts même en superposition
 */
const MicroZone = ({ zone, isHovered, onHover, onLeave, showConcentric, isFavorite, onToggleFavorite, currentZoom }) => {
  const { center, radiusMeters, moduleId, percentage, isOverlap, neighboringModules, overlapCount, renderPriority } = zone;
  
  // Zoom actuel pour calcul vectoriel des épaisseurs
  const zoom = currentZoom || zone.zoom || 12;
  const module = BIONIC_MODULES[moduleId] || BIONIC_MODULES.habitats;
  
  // STYLE "DANY LAVOIE" : Chaque zone conserve SON PROPRE pourcentage (AUCUNE fusion)
  const displayPercentage = percentage;
  
  // Calculs vectoriels adaptatifs au zoom
  const fillOpacity = getFillOpacity(displayPercentage, isHovered);
  const strokeWeight = getStrokeWeight(displayPercentage, isHovered, zoom);
  const strokeOpacity = getStrokeOpacity(displayPercentage, isHovered);
  
  // Cercles concentriques avec épaisseur adaptative au zoom
  const concentricRadii = useMemo(() => {
    if (!showConcentric || displayPercentage < 70 || zoom < 12) return [];
    const radii = [];
    if (displayPercentage >= 85) {
      radii.push({ radius: radiusMeters * 0.70, weight: getConcentricStrokeWeight(zoom, 0) });
      radii.push({ radius: radiusMeters * 0.40, weight: getConcentricStrokeWeight(zoom, 1) });
    } else if (displayPercentage >= 70) {
      radii.push({ radius: radiusMeters * 0.60, weight: getConcentricStrokeWeight(zoom, 0) });
    }
    return radii;
  }, [showConcentric, displayPercentage, radiusMeters, zoom]);

  return (
    <>
      {/* 
        STYLE "DANY LAVOIE" - SEGMENTATION AVANCÉE :
        - Entité graphique INDÉPENDANTE (pas de fusion)
        - Contour VECTORIEL ultra-fin et adaptatif au zoom
        - Remplissage SEMI-TRANSPARENT (voir le terrain)
        - Couleurs VIVES et SATURÉES pour distinction claire
        - Superpositions = couches DISTINCTES visibles simultanément
      */}
      
      {/* Cercle principal - Entité indépendante avec contour vectoriel adaptatif */}
      <Circle
        center={center}
        radius={radiusMeters}
        pathOptions={{
          color: module.color,
          weight: strokeWeight,
          opacity: strokeOpacity,
          fillColor: module.color,
          fillOpacity: fillOpacity,
          // Style vectoriel : contours nets et précis
          lineCap: 'round',
          lineJoin: 'round',
          // Pas de dashArray pour contour solide
        }}
        eventHandlers={{
          mouseover: () => onHover(zone.id),
          mouseout: onLeave
        }}
      >
        <Tooltip 
          sticky 
          direction="top" 
          offset={[0, -10]}
          className="bionic-zone-tooltip"
        >
          <div className="bg-gray-900/95 border border-gray-700 rounded-lg p-3 min-w-[220px] shadow-xl">
            {/* En-tête avec icône et label */}
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">{module.icon}</span>
              <span className="font-bold text-white flex-1">{module.label}</span>
              {isFavorite && (
                <span className="text-yellow-400" title="Zone favorite">⭐</span>
              )}
            </div>
            
            {/* Pourcentage propre à cette zone (AUCUNE fusion) */}
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Probabilité</span>
              <span 
                className="font-bold text-lg"
                style={{ color: module.color }}
              >
                {displayPercentage}%
              </span>
            </div>
            
            {/* Interprétation */}
            <div 
              className="text-sm py-1 px-2 rounded text-center"
              style={{ 
                backgroundColor: `${module.color}20`,
                color: module.color,
                border: `1px solid ${module.color}40`
              }}
            >
              {getInterpretation(moduleId, displayPercentage)}
            </div>
            
            {/* Zones voisines distinctes (informatif - pas de fusion) */}
            {isOverlap && neighboringModules && neighboringModules.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-xs text-gray-500 mb-1">
                  Couches adjacentes ({overlapCount}) :
                </div>
                <div className="flex flex-wrap gap-1">
                  {neighboringModules.slice(0, 4).map((m, idx) => (
                    <Badge 
                      key={idx} 
                      className="text-xs"
                      style={{ 
                        backgroundColor: `${m.color || '#666'}30`,
                        color: m.color || '#fff',
                        border: `1px solid ${m.color || '#666'}50`
                      }}
                    >
                      {BIONIC_MODULES[m.id]?.icon} {m.percentage}%
                    </Badge>
                  ))}
                  {neighboringModules.length > 4 && (
                    <Badge className="text-xs bg-gray-700 text-gray-400">
                      +{neighboringModules.length - 4}
                    </Badge>
                  )}
                </div>
              </div>
            )}
            
            <div className="text-xs text-gray-500 mt-2 text-center">
              Rayon: {(radiusMeters / 1000).toFixed(2)} km
            </div>
            
            {/* Bouton ajouter/retirer favoris */}
            {onToggleFavorite && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleFavorite(zone);
                  }}
                  className={`w-full text-xs py-1.5 px-2 rounded transition-colors ${
                    isFavorite 
                      ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {isFavorite ? '⭐ Retirer des favoris' : '☆ Ajouter aux favoris'}
                </button>
              </div>
            )}
          </div>
        </Tooltip>
      </Circle>
      
      {/* 
        Cercles concentriques - Style "Dany Lavoie"
        Contours ÉPAIS et SOLIDES (pas de pointillés)
        Même couleur que le cercle principal
      */}
      {concentricRadii.map((config, idx) => (
        <Circle
          key={`concentric-${zone.id}-${idx}`}
          center={center}
          radius={config.radius}
          pathOptions={{
            color: module.color,
            weight: config.weight,
            opacity: strokeOpacity - (idx * 0.15),
            fill: false,
            // Style Dany Lavoie: contour SOLIDE (pas de dashArray)
            lineCap: 'round',
            lineJoin: 'round',
            interactive: false
          }}
        />
      ))}
    </>
  );
};

/**
 * Composant CorridorLine - LIGNES VECTORIELLES ADAPTATIVES
 * 
 * Épaisseur recalculée dynamiquement selon le zoom :
 * - Fort zoom (analyse locale) : augmentation pour précision visuelle
 * - Faible zoom (vue globale) : réduction drastique pour carte propre
 */
const CorridorLine = ({ start, end, moduleId, percentage, label, zoom = 12 }) => {
  const module = BIONIC_MODULES[moduleId] || BIONIC_MODULES.corridors;
  const [isHovered, setIsHovered] = useState(false);
  
  /**
   * Épaisseur vectorielle adaptative au zoom
   * Courbe progressive pour transition fluide
   */
  const getCorridorWeight = (z, hovered) => {
    let baseWeight;
    if (z >= 16) {
      // Fort zoom : corridors bien visibles pour analyse locale
      baseWeight = hovered ? 2.5 : 2.0;
    } else if (z >= 14) {
      baseWeight = hovered ? 1.6 : 1.2;
    } else if (z >= 12) {
      baseWeight = hovered ? 1.0 : 0.7;
    } else if (z >= 10) {
      // Faible zoom : réduction pour carte propre
      baseWeight = hovered ? 0.5 : 0.35;
    } else {
      // Vue globale : réduction drastique
      baseWeight = hovered ? 0.25 : 0.15;
    }
    return baseWeight;
  };
  
  /**
   * DashArray adaptatif au zoom
   * Espacements proportionnels pour lisibilité
   */
  const getDashArray = (z) => {
    if (z >= 16) return '10, 6';
    if (z >= 14) return '8, 5';
    if (z >= 12) return '6, 4';
    if (z >= 10) return '4, 3';
    return '3, 2';
  };
  
  return (
    <Polyline
      positions={[start, end]}
      pathOptions={{
        color: module.color,
        weight: getCorridorWeight(zoom, isHovered),
        opacity: isHovered ? 1 : 0.85,
        dashArray: getDashArray(zoom),
        lineCap: 'round',
        lineJoin: 'round'
      }}
      eventHandlers={{
        mouseover: () => setIsHovered(true),
        mouseout: () => setIsHovered(false)
      }}
    >
      <Tooltip sticky direction="top" offset={[0, -5]}>
        <div className="bg-gray-900/95 border border-gray-700 rounded-lg p-2 shadow-xl">
          <div className="flex items-center gap-2">
            <span>{module.icon}</span>
            <span className="font-semibold text-white">{label || module.label}</span>
          </div>
          <div className="text-sm mt-1" style={{ color: module.color }}>
            Probabilité de passage: {percentage}%
          </div>
        </div>
      </Tooltip>
    </Polyline>
  );
};

// Composant principal
const BionicMicroZones = ({ 
  zones = [], 
  corridors = [],
  bufferZones = [],
  minPercentage = 50,
  showConcentricCircles = true,
  showCorridors = true,
  showBufferZones = true,
  onZoneClick,
  // Props pour les favoris
  isZoneFavorite = () => false,
  onAddFavorite = null,
  onRemoveFavorite = null
}) => {
  const [hoveredZoneId, setHoveredZoneId] = useState(null);
  const map = useMap();
  
  // Initialiser le zoom avec la valeur actuelle de la carte
  const [currentZoom, setCurrentZoom] = useState(() => {
    return map ? map.getZoom() : 12;
  });
  
  // Écouter les changements de zoom pour mettre à jour l'épaisseur des bordures
  useEffect(() => {
    if (!map) return;
    
    // Écouter les événements de zoom
    const handleZoomEnd = () => {
      setCurrentZoom(map.getZoom());
    };
    
    map.on('zoomend', handleZoomEnd);
    
    return () => {
      map.off('zoomend', handleZoomEnd);
    };
  }, [map]);
  
  /**
   * ALGORITHME DE SEGMENTATION AVANCÉE - STYLE "DANY LAVOIE"
   * 
   * RÈGLES FONDAMENTALES :
   * 1. Chaque zone = entité graphique INDÉPENDANTE
   * 2. AUCUNE fusion, aplatissement ou simplification
   * 3. Superpositions = couches DISTINCTES visibles simultanément
   * 4. Chaque segment conserve : contour propre, couleur thématique, pourcentage, attributs
   * 5. Tri par couches pour une segmentation intacte même en superposition multiple
   * 6. CLIPPING GÉOMÉTRIQUE : Lignes de délimitation aux intersections
   * 
   * STRATÉGIE DE RENDU :
   * - Zones faibles (base) → rendues EN PREMIER (couche inférieure)
   * - Zones fortes (prioritaires) → rendues EN DERNIER (couche supérieure)
   * - Lignes d'intersection → rendues PAR-DESSUS toutes les zones
   * - Résultat : toutes les portions restent visibles et distinctes
   */
  const { visibleZones, intersections } = useMemo(() => {
    const processedZones = [];
    const calculatedIntersections = [];
    const processedPairs = new Set();
    
    zones.forEach(zone => {
      // Filtre de base : inclure si pourcentage >= seuil minimum
      if (zone.percentage < minPercentage) return;
      
      // Identifier les zones qui se superposent (informatif uniquement)
      // AUCUNE fusion - chaque zone reste une entité indépendante
      const overlappingZones = zones.filter(other =>
        other.id !== zone.id &&
        other.percentage >= minPercentage &&
        getDistance(zone.center, other.center) < (zone.radiusMeters + other.radiusMeters) * 0.95
      );
      
      const hasOverlap = overlappingZones.length > 0;
      const overlapCount = overlappingZones.length;
      
      // CLIPPING GÉOMÉTRIQUE : Calculer les points d'intersection pour chaque paire
      if (hasOverlap) {
        overlappingZones.forEach(other => {
          // Éviter de traiter la même paire deux fois
          const pairKey = [zone.id, other.id].sort().join('-');
          if (!processedPairs.has(pairKey)) {
            processedPairs.add(pairKey);
            
            // Calculer les points d'intersection entre les deux cercles
            const intersection = calculateCircleIntersections(
              zone.center,
              zone.radiusMeters,
              other.center,
              other.radiusMeters
            );
            
            if (intersection) {
              calculatedIntersections.push({
                id: pairKey,
                ...intersection,
                zone1: { id: zone.id, moduleId: zone.moduleId, color: BIONIC_MODULES[zone.moduleId]?.color },
                zone2: { id: other.id, moduleId: other.moduleId, color: BIONIC_MODULES[other.moduleId]?.color }
              });
            }
          }
        });
      }
      
      // SEGMENTATION : Chaque zone conserve son identité propre
      // Pas de modification des attributs (couleur, %, contour)
      processedZones.push({
        ...zone,
        isOverlap: hasOverlap,
        overlapCount,
        // Couches adjacentes (informatif - pas de fusion)
        neighboringModules: hasOverlap ? overlappingZones.map(z => ({
          id: z.moduleId,
          percentage: z.percentage,
          color: BIONIC_MODULES[z.moduleId]?.color,
          icon: BIONIC_MODULES[z.moduleId]?.icon
        })) : [],
        // Priorité de rendu (stratégie multi-couches)
        // Zones fortes au-dessus, zones isolées bonus de visibilité
        renderPriority: zone.percentage + (hasOverlap ? 0 : 10)
      });
    });
    
    /**
     * TRI PAR COUCHES - Garantit la segmentation intacte
     * 
     * Ordre de rendu SVG/Canvas :
     * - Premier rendu = couche inférieure (arrière-plan)
     * - Dernier rendu = couche supérieure (premier plan)
     * 
     * Résultat visuel :
     * - Zones faibles dessinent leurs contours d'abord
     * - Zones fortes dessinent PAR-DESSUS mais SANS effacer les contours existants
     * - Lignes d'intersection marquent les croisements
     * - Toutes les portions restent visibles et distinctes
     */
    const sortedZones = processedZones.sort((a, b) => {
      return a.renderPriority - b.renderPriority;
    });
    
    return { 
      visibleZones: sortedZones, 
      intersections: calculatedIntersections 
    };
  }, [zones, minPercentage]);
  
  const handleHover = useCallback((zoneId) => {
    setHoveredZoneId(zoneId);
  }, []);
  
  const handleLeave = useCallback(() => {
    setHoveredZoneId(null);
  }, []);

  return (
    <>
      {/* COUCHE 1 : Zones micro-délimitées (entités indépendantes) */}
      {visibleZones.map(zone => (
        <MicroZone
          key={zone.id}
          zone={zone}
          isHovered={hoveredZoneId === zone.id}
          onHover={handleHover}
          onLeave={handleLeave}
          showConcentric={showConcentricCircles}
          isFavorite={isZoneFavorite(zone)}
          currentZoom={currentZoom}
          onToggleFavorite={onAddFavorite ? (z) => {
            if (isZoneFavorite(z)) {
              onRemoveFavorite && onRemoveFavorite(z);
            } else {
              onAddFavorite(z);
            }
          } : null}
        />
      ))}
      
      {/* COUCHE 2 : LIGNES DE DÉLIMITATION AUX INTERSECTIONS */}
      {/* Style "Dany Lavoie" : lignes blanches/claires marquant les croisements */}
      {currentZoom >= 12 && intersections.map(intersection => (
        <IntersectionLine
          key={intersection.id}
          intersection={intersection}
          zoom={currentZoom}
        />
      ))}
      
      {/* COUCHE 3 : Corridors de déplacement (lignes pointillées) */}
      {showCorridors && corridors.map((corridor, idx) => (
        <CorridorLine
          key={`corridor-${idx}`}
          start={corridor.start}
          end={corridor.end}
          moduleId="corridors"
          percentage={corridor.percentage}
          label={corridor.label || "Corridor de déplacement"}
          zoom={currentZoom}
        />
      ))}
      
      {/* COUCHE 4 : Zones tampons / transitions (lignes pointillées) */}
      {showBufferZones && bufferZones.map((buffer, idx) => (
        <CorridorLine
          key={`buffer-${idx}`}
          start={buffer.start}
          end={buffer.end}
          moduleId="transition"
          percentage={buffer.percentage}
          label={buffer.label || "Zone de transition"}
          zoom={currentZoom}
        />
      ))}
    </>
  );
};

/**
 * Génère des zones micro-délimitées circulaires basées sur les données BIONIC
 */
export const generateMicroZones = (centerLat, centerLng, zoom, layersVisible, existingZones = []) => {
  const microZones = [];
  const corridors = [];
  const bufferZones = [];
  
  // Configuration basée sur le zoom
  const getRadiusForZoom = (z) => {
    if (z >= 16) return 50;    // 50m - très précis
    if (z >= 14) return 100;   // 100m
    if (z >= 12) return 200;   // 200m
    if (z >= 10) return 400;   // 400m
    return 800;                // 800m
  };
  
  const radiusMeters = getRadiusForZoom(zoom);
  const gridSpacing = radiusMeters * 2.2;
  
  // Convertir en degrés
  const latStep = gridSpacing / 111320;
  const lngStep = gridSpacing / (111320 * Math.cos(centerLat * Math.PI / 180));
  
  // Grille adaptative
  const gridSize = zoom >= 14 ? 5 : zoom >= 12 ? 4 : 3;
  const halfGrid = Math.floor(gridSize / 2);
  
  // Fonction de bruit pour variation naturelle
  const noise = (x, y, seed = 0) => {
    const n = Math.sin((x + seed) * 12.9898 + y * 78.233) * 43758.5453;
    return n - Math.floor(n);
  };
  
  // Générer les zones pour chaque module visible
  Object.entries(layersVisible).forEach(([moduleId, isVisible]) => {
    if (!isVisible || !BIONIC_MODULES[moduleId]) return;
    
    for (let row = -halfGrid; row <= halfGrid; row++) {
      for (let col = -halfGrid; col <= halfGrid; col++) {
        const zoneLat = centerLat + row * latStep;
        const zoneLng = centerLng + col * lngStep;
        
        // Variation naturelle basée sur position
        const noiseFactor = noise(zoneLat * 1000, zoneLng * 1000, moduleId.charCodeAt(0));
        
        // Seuil de génération (pas toutes les cellules ont des zones)
        if (noiseFactor < 0.35) continue;
        
        // Calculer le pourcentage de probabilité
        const basePercentage = 45 + noiseFactor * 55;
        const percentage = Math.round(Math.min(98, Math.max(30, basePercentage)));
        
        // Ne pas créer si < 50% (sera filtré de toute façon)
        if (percentage < 45) continue;
        
        // Variation du rayon pour aspect naturel
        const radiusVariation = 0.85 + (noiseFactor * 0.3);
        
        microZones.push({
          id: `micro-${moduleId}-${row}-${col}`,
          moduleId,
          center: [zoneLat, zoneLng],
          radiusMeters: radiusMeters * radiusVariation,
          percentage,
          zoom
        });
      }
    }
  });
  
  // Générer des corridors entre zones d'alimentation et de repos
  if (layersVisible.corridors || layersVisible.alimentation) {
    const alimentationZones = microZones.filter(z => z.moduleId === 'alimentation' && z.percentage >= 60);
    const reposZones = microZones.filter(z => z.moduleId === 'repos' && z.percentage >= 60);
    
    // Connecter les zones proches
    alimentationZones.slice(0, 3).forEach((alim, i) => {
      reposZones.slice(0, 2).forEach((repos, j) => {
        const distance = getDistance(alim.center, repos.center);
        if (distance < 2000 && distance > 200) { // Entre 200m et 2km
          corridors.push({
            start: alim.center,
            end: repos.center,
            percentage: Math.round((alim.percentage + repos.percentage) / 2),
            label: "Corridor alimentation ↔ repos"
          });
        }
      });
    });
  }
  
  // Générer des zones tampons autour des habitats principaux
  if (layersVisible.transition || layersVisible.habitats) {
    const habitatZones = microZones.filter(z => z.moduleId === 'habitats' && z.percentage >= 70);
    
    habitatZones.slice(0, 3).forEach((habitat, i) => {
      // Créer une ligne de transition vers le nord et le sud
      const offset = radiusMeters * 2.5 / 111320;
      bufferZones.push({
        start: [habitat.center[0] + offset, habitat.center[1] - offset * 0.5],
        end: [habitat.center[0] + offset, habitat.center[1] + offset * 0.5],
        percentage: Math.round(habitat.percentage * 0.7),
        label: "Zone tampon habitat"
      });
    });
  }
  
  return { microZones, corridors, bufferZones };
};

/**
 * Génère des zones micro-délimitées qui couvrent TOUTE l'étendue visible de la carte
 * @param {Object} bounds - Limites de la carte { north, south, east, west }
 * @param {number} zoom - Niveau de zoom actuel
 * @param {Object} layersVisible - Couches actives
 */
export const generateMicroZonesForBounds = (bounds, zoom, layersVisible) => {
  const microZones = [];
  const corridors = [];
  const bufferZones = [];
  
  if (!bounds) return { microZones, corridors, bufferZones };
  
  // Configuration basée sur le zoom
  const getRadiusForZoom = (z) => {
    if (z >= 16) return 50;    // 50m - très précis
    if (z >= 14) return 100;   // 100m
    if (z >= 12) return 200;   // 200m
    if (z >= 10) return 400;   // 400m
    return 800;                // 800m
  };
  
  const radiusMeters = getRadiusForZoom(zoom);
  const gridSpacing = radiusMeters * 2.2;
  
  // Calculer le centre pour les conversions
  const centerLat = (bounds.north + bounds.south) / 2;
  
  // Convertir en degrés
  const latStep = gridSpacing / 111320;
  const lngStep = gridSpacing / (111320 * Math.cos(centerLat * Math.PI / 180));
  
  // Calculer le nombre de cellules pour couvrir la zone visible
  const latRange = bounds.north - bounds.south;
  const lngRange = bounds.east - bounds.west;
  
  const numRows = Math.ceil(latRange / latStep) + 1;
  const numCols = Math.ceil(lngRange / lngStep) + 1;
  
  // Limiter pour les performances
  const maxCells = zoom >= 14 ? 25 : zoom >= 12 ? 18 : 12;
  const effectiveRows = Math.min(numRows, maxCells);
  const effectiveCols = Math.min(numCols, maxCells);
  
  // Fonction de bruit pour variation naturelle
  const noise = (x, y, seed = 0) => {
    const n = Math.sin((x + seed) * 12.9898 + y * 78.233) * 43758.5453;
    return n - Math.floor(n);
  };
  
  // Générer les zones pour chaque module visible sur TOUTE la carte
  Object.entries(layersVisible).forEach(([moduleId, isVisible]) => {
    if (!isVisible || !BIONIC_MODULES[moduleId]) return;
    
    for (let row = 0; row < effectiveRows; row++) {
      for (let col = 0; col < effectiveCols; col++) {
        // Position dans la zone visible (répartition uniforme)
        const zoneLat = bounds.south + (row + 0.5) * (latRange / effectiveRows);
        const zoneLng = bounds.west + (col + 0.5) * (lngRange / effectiveCols);
        
        // Vérifier que le point est dans les limites
        if (zoneLat < bounds.south || zoneLat > bounds.north) continue;
        if (zoneLng < bounds.west || zoneLng > bounds.east) continue;
        
        // Variation naturelle basée sur position
        const noiseFactor = noise(zoneLat * 1000, zoneLng * 1000, moduleId.charCodeAt(0));
        
        // Seuil de génération variable selon le type de zone
        const threshold = moduleId === 'habitats' ? 0.25 : 
                         moduleId === 'corridors' ? 0.30 :
                         moduleId === 'alimentation' ? 0.28 : 0.35;
        if (noiseFactor < threshold) continue;
        
        // Calculer le pourcentage de probabilité
        const basePercentage = 40 + noiseFactor * 60;
        const percentage = Math.round(Math.min(98, Math.max(35, basePercentage)));
        
        // Ne pas créer si < 45% (sera filtré de toute façon)
        if (percentage < 45) continue;
        
        // Variation du rayon pour aspect naturel
        const radiusVariation = 0.80 + (noiseFactor * 0.40);
        
        microZones.push({
          id: `bounds-micro-${moduleId}-${row}-${col}`,
          moduleId,
          center: [zoneLat, zoneLng],
          radiusMeters: radiusMeters * radiusVariation,
          percentage,
          zoom
        });
      }
    }
  });
  
  // Générer des corridors entre zones d'alimentation et de repos
  if (layersVisible.corridors || layersVisible.alimentation) {
    const alimentationZones = microZones.filter(z => z.moduleId === 'alimentation' && z.percentage >= 60);
    const reposZones = microZones.filter(z => z.moduleId === 'repos' && z.percentage >= 60);
    
    // Connecter les zones proches (limité à 5 corridors)
    let corridorCount = 0;
    alimentationZones.slice(0, 5).forEach((alim) => {
      reposZones.slice(0, 3).forEach((repos) => {
        if (corridorCount >= 8) return; // Max 8 corridors
        const distance = getDistance(alim.center, repos.center);
        if (distance < 3000 && distance > 300) { // Entre 300m et 3km
          corridors.push({
            start: alim.center,
            end: repos.center,
            percentage: Math.round((alim.percentage + repos.percentage) / 2),
            label: "Corridor alimentation ↔ repos"
          });
          corridorCount++;
        }
      });
    });
  }
  
  // Générer des zones tampons autour des habitats principaux
  if (layersVisible.transition || layersVisible.habitats) {
    const habitatZones = microZones.filter(z => z.moduleId === 'habitats' && z.percentage >= 70);
    
    habitatZones.slice(0, 5).forEach((habitat) => {
      // Créer une ligne de transition
      const offset = radiusMeters * 2.5 / 111320;
      bufferZones.push({
        start: [habitat.center[0] + offset, habitat.center[1] - offset * 0.5],
        end: [habitat.center[0] + offset, habitat.center[1] + offset * 0.5],
        percentage: Math.round(habitat.percentage * 0.7),
        label: "Zone tampon habitat"
      });
    });
  }
  
  return { microZones, corridors, bufferZones };
};

export default BionicMicroZones;
