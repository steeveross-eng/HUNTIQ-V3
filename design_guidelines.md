# BIONIC™ Design Guidelines

## Version: 1.0.0
## Date: 2026-02-05

---

## 1. Principes de Design

### 1.1 Cohérence Visuelle
- Utiliser les tokens de `/app/frontend/src/lib/designTokens.js`
- Couleur primaire: `#f5a623` (Orange BIONIC™)
- Fond principal: `#0a0a0a` (Noir profond)
- Texte principal: `#ffffff` (Blanc)
- Texte secondaire: `#a0a0a0` (Gris)

### 1.2 Ergonomie Standardisée
- **Carte centrale**: 83-85% de l'écran
- **Panneaux latéraux**: 15-17% maximum
- **Typographie réduite**: 50% des valeurs standard

---

## 2. Typographie Compacte

| Élément | Taille CSS | Pixels |
|---------|------------|--------|
| Titre de panneau | `text-[10px]` | 10px |
| Label | `text-[9px]` | 9px |
| Corps de texte | `text-[9px]` | 9px |
| Badge | `text-[8px]` | 8px |
| Info/Hint | `text-[7px]` | 7px |

---

## 3. Dimensions des Panneaux

### 3.1 Panneau WMS (gauche)
```jsx
width: "w-48"          // 192px
maxHeight: "max-h-[55vh]"
scrollHeight: "h-[160px]"
```

### 3.2 Panneau Sidebar (droite)
```jsx
gridCols: "grid-cols-6"
carte: "col-span-5"    // 83%
sidebar: "col-span-1"  // 17%
```

---

## 4. Contrôles de Scroll Accessibles

- Flèches ↑↓ explicites au-dessus/dessous des listes
- Hauteur des boutons: `h-5`
- Style: `bg-black/50 hover:bg-black/70`
- Scroll smooth: `scroll-behavior: smooth`

---

## 5. Composants Compacts

### 5.1 Bouton compact
```jsx
className="h-5 w-5 p-0 text-[9px]"
```

### 5.2 Input compact
```jsx
className="h-6 text-[9px] px-2"
```

### 5.3 Badge compact
```jsx
className="text-[8px] px-1.5 py-0"
```

### 5.4 Card Header compact
```jsx
className="py-1.5 px-2"
```

---

## 6. Tokens de Couleur

```javascript
// Primaires
primary: '#f5a623',
primaryHover: '#d4910f',
primaryLight: 'rgba(245, 166, 35, 0.2)',

// Fonds
bgDark: '#0a0a0a',
bgCard: '#1a1a1a',
bgPanel: 'rgba(0, 0, 0, 0.95)',

// États
success: '#22c55e',
warning: '#f5a623',
error: '#ef4444',
info: '#3b82f6',
```

---

## 7. Accessibilité

- Contrastes minimum WCAG AA
- Focus visible sur tous les éléments interactifs
- Labels explicites pour tous les inputs
- Feedback visuel sur hover/active

---

## 8. Animations

```javascript
transitions: {
  fast: 'duration-150',
  normal: 'duration-200',
  slow: 'duration-300',
}
```

---

## 9. Fichiers de Référence

- `/app/frontend/src/lib/designTokens.js` - Tokens centralisés
- `/app/frontend/src/components/geospatial/WMSLayerSelector.jsx` - Panneau WMS
- `/app/frontend/src/pages/TerritoryPage.jsx` - Page principale
- `/app/frontend/src/lib/maplibre.js` - Configuration carte

---

*BIONIC™ Design System - Cohérence, Ergonomie, Accessibilité*
