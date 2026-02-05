/**
 * BIONIC™ Design System - UX Harmonization Tokens
 * 
 * Ce fichier centralise tous les tokens de design pour garantir:
 * - Cohérence visuelle sur toutes les pages
 * - Ergonomie standardisée (tailles, marges, typographies)
 * - Accessibilité minimale (lisibilité, scroll, contrôles visibles)
 * - Expérience utilisateur fluide et "idiot proof"
 * 
 * @version 1.0.0
 * @date 2026-02-05
 */

// =============================================================================
// COULEURS BIONIC™
// =============================================================================
export const COLORS = {
  // Primaires
  primary: '#f5a623',        // Orange BIONIC™
  primaryHover: '#d4910f',
  primaryLight: 'rgba(245, 166, 35, 0.2)',
  
  // Fonds
  bgDark: '#0a0a0a',
  bgCard: '#1a1a1a',
  bgPanel: 'rgba(0, 0, 0, 0.95)',
  bgOverlay: 'rgba(0, 0, 0, 0.7)',
  
  // Textes
  textPrimary: '#ffffff',
  textSecondary: '#a0a0a0',
  textMuted: '#666666',
  
  // Bordures
  borderLight: 'rgba(255, 255, 255, 0.1)',
  borderMedium: 'rgba(255, 255, 255, 0.2)',
  
  // États
  success: '#22c55e',
  warning: '#f5a623',
  error: '#ef4444',
  info: '#3b82f6',
};

// =============================================================================
// TYPOGRAPHIE - Réduite de 50% par rapport aux valeurs standard
// =============================================================================
export const TYPOGRAPHY = {
  // Titres de panneaux (compact)
  panelTitle: {
    size: 'text-[10px]',      // Réduit de text-sm
    weight: 'font-medium',
    lineHeight: 'leading-tight',
  },
  
  // Labels et texte de formulaire
  label: {
    size: 'text-[9px]',       // Réduit de text-xs
    weight: 'font-medium',
    color: 'text-gray-400',
  },
  
  // Texte de contenu compact
  body: {
    size: 'text-[9px]',       // Réduit de text-sm
    weight: 'font-normal',
    lineHeight: 'leading-snug',
  },
  
  // Badges et étiquettes
  badge: {
    size: 'text-[8px]',       // Très petit
    weight: 'font-medium',
  },
  
  // Boutons compacts
  button: {
    size: 'text-[9px]',
    weight: 'font-medium',
  },
};

// =============================================================================
// ESPACEMENTS COMPACTS
// =============================================================================
export const SPACING = {
  // Padding des panneaux
  panelPadding: 'p-2',
  panelPaddingX: 'px-2',
  panelPaddingY: 'py-1.5',
  
  // Gaps entre éléments
  gapTiny: 'gap-0.5',
  gapSmall: 'gap-1',
  gapMedium: 'gap-2',
  
  // Marges
  marginTiny: 'm-0.5',
  marginSmall: 'm-1',
  marginMedium: 'm-2',
};

// =============================================================================
// DIMENSIONS DES PANNEAUX LATÉRAUX
// =============================================================================
export const PANEL_DIMENSIONS = {
  // Panneau WMS (gauche) - Ultra compact
  wmsPanel: {
    width: 'w-48',            // 192px (réduit de 288px)
    maxHeight: 'max-h-[50vh]',
    scrollHeight: 'h-[180px]',
  },
  
  // Panneau de droite (sidebar)
  sidebarWidth: 'w-56',       // 224px (réduit)
  
  // Grille principale
  gridCols: 'grid-cols-6',    // Carte: 5 cols, Sidebar: 1 col
  mapCols: 'col-span-5',      // 83% pour la carte
  sidebarCols: 'col-span-1',  // 17% pour le panneau
};

// =============================================================================
// CLASSES CSS PRÉCOMPOSÉES
// =============================================================================
export const PANEL_CLASSES = {
  // Card de base pour panneaux
  card: 'bg-black/95 border-white/10 backdrop-blur-md shadow-lg',
  
  // En-tête de panneau compact
  cardHeader: 'pb-1 pt-2 px-2',
  
  // Contenu de panneau
  cardContent: 'px-2 pb-2',
  
  // Bouton icône compact
  iconButton: 'h-5 w-5 p-0',
  
  // Badge compact
  badge: 'text-[8px] px-1.5 py-0.5',
  
  // Input compact
  input: 'h-7 text-[9px] px-2',
  
  // Select compact
  select: 'h-7 text-[9px]',
  
  // Bouton de scroll
  scrollButton: 'h-5 w-full flex items-center justify-center bg-black/50 hover:bg-black/70 text-gray-400 hover:text-white transition-colors',
};

// =============================================================================
// CONTRÔLES DE SCROLL ACCESSIBLES
// =============================================================================
export const SCROLL_CONTROLS = {
  // Hauteur des boutons de navigation
  buttonHeight: 'h-5',
  
  // Classes pour les flèches
  arrowUp: 'rotate-180',
  arrowDown: '',
  
  // Icône
  iconSize: 'h-3 w-3',
};

// =============================================================================
// ANIMATIONS ET TRANSITIONS
// =============================================================================
export const TRANSITIONS = {
  fast: 'duration-150',
  normal: 'duration-200',
  slow: 'duration-300',
  
  ease: 'ease-out',
  easeInOut: 'ease-in-out',
};

// =============================================================================
// BREAKPOINTS RESPONSIVE
// =============================================================================
export const BREAKPOINTS = {
  mobile: 'max-w-sm',
  tablet: 'sm:max-w-md',
  desktop: 'lg:max-w-lg',
  wide: 'xl:max-w-xl',
};

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Génère les classes CSS pour un panneau latéral standard
 */
export const getPanelClasses = (position = 'left') => {
  const positionClass = position === 'left' ? 'left-2 top-2' : 'right-2 top-2';
  return `absolute ${positionClass} z-10 ${PANEL_DIMENSIONS.wmsPanel.width} ${PANEL_DIMENSIONS.wmsPanel.maxHeight} ${PANEL_CLASSES.card} overflow-hidden`;
};

/**
 * Génère les classes CSS pour un texte selon son rôle
 */
export const getTextClasses = (role = 'body') => {
  const config = TYPOGRAPHY[role] || TYPOGRAPHY.body;
  return `${config.size} ${config.weight} ${config.lineHeight || ''} ${config.color || ''}`.trim();
};

export default {
  COLORS,
  TYPOGRAPHY,
  SPACING,
  PANEL_DIMENSIONS,
  PANEL_CLASSES,
  SCROLL_CONTROLS,
  TRANSITIONS,
  BREAKPOINTS,
  getPanelClasses,
  getTextClasses,
};
