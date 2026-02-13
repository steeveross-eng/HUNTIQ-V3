# Territory Analysis Service
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import math
import random

logger = logging.getLogger(__name__)


# ============================================
# SPECIES BUSINESS RULES
# ============================================

SPECIES_RULES = {
    "orignal": {
        "name_fr": "Orignal",
        "water_distance_optimal": 300,
        "road_distance_min": 400,
        "edge_distance_optimal": 200,
        "slope_max": 15,
        "preferred_terrain": ["vallée", "plaine", "marécage"],
        "preferred_cover": ["forêt_mature", "mixte", "conifères"],
        "activity_hours": {
            "matin": 0.85,
            "jour": 0.40,
            "soir": 0.90,
            "nuit": 0.70
        },
        "recent_activity_window_hours": 72,
        "pressure_sensitivity": 0.7,
        "attractants": ["saline", "urine_femelle", "appel"],
        "season_modifiers": {
            "pre_rut": 0.8,
            "rut": 1.2,
            "post_rut": 0.9
        }
    },
    "chevreuil": {
        "name_fr": "Chevreuil",
        "water_distance_optimal": 500,
        "road_distance_min": 200,
        "edge_distance_optimal": 150,
        "slope_max": 25,
        "preferred_terrain": ["lisière", "friche", "coupe_récente"],
        "preferred_cover": ["régénération", "friche", "feuillus"],
        "activity_hours": {
            "matin": 0.90,
            "jour": 0.35,
            "soir": 0.95,
            "nuit": 0.60
        },
        "recent_activity_window_hours": 48,
        "pressure_sensitivity": 0.8,
        "attractants": ["maïs", "pommes", "urine_doe", "sel"],
        "season_modifiers": {
            "pre_rut": 0.9,
            "rut": 1.3,
            "post_rut": 0.85
        }
    },
    "ours": {
        "name_fr": "Ours",
        "water_distance_optimal": 500,
        "road_distance_min": 500,
        "edge_distance_optimal": 300,
        "slope_max": 35,
        "preferred_terrain": ["friche", "coupe", "baies"],
        "preferred_cover": ["mixte", "dense", "régénération"],
        "activity_hours": {
            "matin": 0.75,
            "jour": 0.50,
            "soir": 0.85,
            "nuit": 0.80
        },
        "recent_activity_window_hours": 168,  # 7 jours
        "pressure_sensitivity": 0.6,
        "attractants": ["appât_sucré", "miel", "bacon", "poisson"],
        "season_modifiers": {
            "printemps": 1.1,
            "été": 1.0,
            "automne": 1.2
        }
    }
}


class TerritoryAnalysisService:
    """
    Service d'analyse de territoire pour la chasse.
    Calcule les probabilités de présence, zones de refuge, et génère des plans d'action.
    """
    
    def __init__(self, db):
        self.db = db
    
    # ============================================
    # SPECIES PROBABILITY CALCULATION
    # ============================================
    
    def calculate_species_probability(
        self,
        species: str,
        location: Dict[str, float],
        time_period: str = "tous",
        recent_events: List[Dict] = None,
        terrain_data: Dict = None
    ) -> Dict[str, Any]:
        """
        Calcule la probabilité de présence d'une espèce à un point donné.
        
        Args:
            species: "orignal", "chevreuil", ou "ours"
            location: {lat, lng}
            time_period: "matin", "jour", "soir", "nuit", "tous"
            recent_events: Événements récents dans la zone
            terrain_data: Données de terrain (pente, couvert, etc.)
        
        Returns:
            {probability, factors, recommendations}
        """
        rules = SPECIES_RULES.get(species, SPECIES_RULES["chevreuil"])
        
        # Base probability
        base_prob = 0.5
        factors = []
        
        # Time period modifier
        if time_period != "tous":
            time_modifier = rules["activity_hours"].get(time_period, 0.5)
            base_prob *= time_modifier
            factors.append({
                "name": f"Période ({time_period})",
                "impact": time_modifier,
                "description": f"Activité {time_period}: {int(time_modifier * 100)}%"
            })
        
        # Recent activity modifier
        if recent_events:
            species_events = [e for e in recent_events if e.get("species") == species]
            window_hours = rules["recent_activity_window_hours"]
            recent_count = len(species_events)
            
            if recent_count > 0:
                activity_boost = min(0.3, recent_count * 0.05)
                base_prob += activity_boost
                factors.append({
                    "name": "Activité récente",
                    "impact": 1 + activity_boost,
                    "description": f"{recent_count} observation(s) dans les {window_hours}h"
                })
        
        # Terrain modifiers (simulated if no real data)
        if terrain_data:
            # Water proximity
            water_dist = terrain_data.get("water_distance", 500)
            optimal_water = rules["water_distance_optimal"]
            if water_dist <= optimal_water:
                water_boost = 0.15
                base_prob += water_boost
                factors.append({
                    "name": "Proximité eau",
                    "impact": 1.15,
                    "description": f"À {int(water_dist)}m de l'eau (optimal: <{optimal_water}m)"
                })
            
            # Road distance
            road_dist = terrain_data.get("road_distance", 300)
            min_road = rules["road_distance_min"]
            if road_dist >= min_road:
                road_boost = 0.1
                base_prob += road_boost
                factors.append({
                    "name": "Distance routes",
                    "impact": 1.1,
                    "description": f"À {int(road_dist)}m des chemins (sécurité: >{min_road}m)"
                })
            else:
                road_penalty = -0.15
                base_prob += road_penalty
                factors.append({
                    "name": "Proximité routes",
                    "impact": 0.85,
                    "description": f"Trop proche des chemins ({int(road_dist)}m)"
                })
        
        # Hunting pressure modifier
        pressure = terrain_data.get("hunting_pressure", 0.3) if terrain_data else 0.3
        pressure_impact = -pressure * rules["pressure_sensitivity"]
        base_prob += pressure_impact
        if abs(pressure_impact) > 0.05:
            factors.append({
                "name": "Pression de chasse",
                "impact": 1 + pressure_impact,
                "description": f"Niveau de pression: {int(pressure * 100)}%"
            })
        
        # Clamp probability
        final_prob = max(0.05, min(0.98, base_prob))
        
        # Generate recommendations
        recommendations = self._generate_point_recommendations(
            species, final_prob, factors, rules
        )
        
        return {
            "species": species,
            "species_name": rules["name_fr"],
            "location": location,
            "probability": round(final_prob, 2),
            "probability_percent": int(final_prob * 100),
            "confidence": "high" if len(factors) >= 3 else "medium",
            "time_period": time_period,
            "factors": factors,
            "recommendations": recommendations
        }
    
    def _generate_point_recommendations(
        self,
        species: str,
        probability: float,
        factors: List[Dict],
        rules: Dict
    ) -> List[Dict[str, Any]]:
        """Génère des recommandations pour un point donné."""
        recommendations = []
        
        if probability >= 0.7:
            recommendations.append({
                "type": "camera",
                "priority": "high",
                "text": f"Installer une caméra de surveillance orientée vers les zones d'activité"
            })
            recommendations.append({
                "type": "attractant",
                "priority": "high",
                "text": f"Placer {rules['attractants'][0]} BIONIC™ (estimé: 25-50$)"
            })
        elif probability >= 0.5:
            recommendations.append({
                "type": "camera",
                "priority": "medium",
                "text": "Zone prometteuse - caméra recommandée pour validation"
            })
            if len(rules['attractants']) > 1:
                recommendations.append({
                    "type": "attractant",
                    "priority": "medium",
                    "text": f"Considérer {rules['attractants'][1]} pour attirer l'espèce"
                })
        
        if probability >= 0.6:
            recommendations.append({
                "type": "cache",
                "priority": "medium" if probability < 0.8 else "high",
                "text": "Cache surélevée recommandée pour observation/tir"
            })
        
        return recommendations
    
    # ============================================
    # HEATMAP GENERATION
    # ============================================
    
    def generate_activity_heatmap(
        self,
        user_id: str,
        center: Dict[str, float],
        radius_km: float = 5.0,
        species: str = None,
        time_window_hours: int = 72
    ) -> Dict[str, Any]:
        """
        Génère une heatmap d'activité basée sur les événements récents.
        """
        # Simulation de points de chaleur
        # En production, cela viendrait des vraies données d'événements
        points = []
        
        for i in range(50):
            # Générer des points aléatoires dans le rayon
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius_km) * 0.009  # Conversion approx en degrés
            
            lat = center["lat"] + distance * math.cos(angle)
            lng = center["lng"] + distance * math.sin(angle)
            
            # Intensité basée sur la distance au centre (plus dense au centre)
            intensity = max(0.1, 1 - (distance / (radius_km * 0.009)))
            intensity *= random.uniform(0.5, 1.0)
            
            points.append({
                "lat": lat,
                "lng": lng,
                "intensity": round(intensity, 2)
            })
        
        return {
            "layer_type": "activity",
            "species": species,
            "center": center,
            "radius_km": radius_km,
            "points": points,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def generate_probability_heatmap(
        self,
        user_id: str,
        center: Dict[str, float],
        radius_km: float = 5.0,
        species: str = "chevreuil",
        time_period: str = "tous"
    ) -> Dict[str, Any]:
        """
        Génère une heatmap de probabilité de présence.
        """
        rules = SPECIES_RULES.get(species, SPECIES_RULES["chevreuil"])
        points = []
        
        # Grille de points
        grid_size = 20
        step = (radius_km * 0.009 * 2) / grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                lat = center["lat"] - radius_km * 0.009 + i * step
                lng = center["lng"] - radius_km * 0.009 + j * step
                
                # Calcul simplifié de probabilité
                dist_to_center = math.sqrt(
                    (lat - center["lat"])**2 + (lng - center["lng"])**2
                )
                
                # Simulation de facteurs terrain
                base_prob = 0.5 + random.uniform(-0.2, 0.3)
                
                # Modifier par période
                if time_period != "tous":
                    base_prob *= rules["activity_hours"].get(time_period, 0.5)
                
                # Zones de refuge simulées (clusters)
                if random.random() < 0.15:
                    base_prob += 0.25
                
                probability = max(0.05, min(0.95, base_prob))
                
                points.append({
                    "lat": lat,
                    "lng": lng,
                    "probability": round(probability, 2)
                })
        
        return {
            "layer_type": "probability",
            "species": species,
            "species_name": rules["name_fr"],
            "center": center,
            "radius_km": radius_km,
            "time_period": time_period,
            "points": points,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    # ============================================
    # ACTION PLAN GENERATION
    # ============================================
    
    async def generate_action_plan(
        self,
        user_id: str,
        species_target: str,
        zone_center: Dict[str, float],
        zone_radius_km: float = 5.0,
        time_period: str = "tous"
    ) -> Dict[str, Any]:
        """
        Génère un plan d'action complet pour la chasse.
        """
        rules = SPECIES_RULES.get(species_target, SPECIES_RULES["chevreuil"])
        
        # Générer la heatmap de probabilité
        prob_heatmap = self.generate_probability_heatmap(
            user_id, zone_center, zone_radius_km, species_target, time_period
        )
        
        # Trouver les meilleurs emplacements
        high_prob_points = sorted(
            prob_heatmap["points"],
            key=lambda p: p["probability"],
            reverse=True
        )[:10]
        
        # Recommandations de caméras
        camera_placements = []
        for i, point in enumerate(high_prob_points[:3]):
            camera_placements.append({
                "id": f"cam_{i+1}",
                "location": {"lat": point["lat"], "lng": point["lng"]},
                "probability": point["probability"],
                "orientation": random.choice(["N", "NE", "E", "SE", "S", "SO", "O", "NO"]),
                "priority": "high" if i == 0 else "medium",
                "notes": f"Emplacement #{i+1} - Probabilité {int(point['probability']*100)}%"
            })
        
        # Recommandations d'attractants
        attractant_placements = []
        for i, point in enumerate(high_prob_points[1:4]):
            attractant = rules["attractants"][i % len(rules["attractants"])]
            attractant_placements.append({
                "id": f"attr_{i+1}",
                "location": {"lat": point["lat"], "lng": point["lng"]},
                "product": attractant,
                "product_bionic": f"BIONIC™ {attractant.replace('_', ' ').title()}",
                "quantity": "2-5 kg",
                "estimated_cost": f"{25 + i*10}-{50 + i*15}$",
                "priority": "high" if point["probability"] > 0.7 else "medium"
            })
        
        # Recommandations de caches
        cache_recommendations = []
        for i, point in enumerate(high_prob_points[:2]):
            cache_recommendations.append({
                "id": f"cache_{i+1}",
                "location": {"lat": point["lat"], "lng": point["lng"]},
                "type": "surélevée" if rules["pressure_sensitivity"] > 0.6 else "au_sol",
                "height_m": 3.5 if rules["pressure_sensitivity"] > 0.6 else 0,
                "visibility_rating": "excellent" if point["probability"] > 0.75 else "bonne",
                "wind_consideration": "Installer dos au vent dominant (NO)"
            })
        
        # Recommandations générales
        general_recommendations = [
            {
                "category": "timing",
                "text": f"Meilleure période: {max(rules['activity_hours'], key=rules['activity_hours'].get)}",
                "detail": f"Activité maximale: {int(max(rules['activity_hours'].values())*100)}%"
            },
            {
                "category": "approach",
                "text": f"Approche silencieuse recommandée - {rules['name_fr']} sensible à la pression",
                "detail": f"Sensibilité à la pression: {int(rules['pressure_sensitivity']*100)}%"
            },
            {
                "category": "equipment",
                "text": f"Attractants recommandés: {', '.join(rules['attractants'][:3])}",
                "detail": "Produits BIONIC™ disponibles dans le magasin"
            }
        ]
        
        plan = {
            "id": str(__import__('uuid').uuid4()),
            "user_id": user_id,
            "species_target": species_target,
            "species_name": rules["name_fr"],
            "zone_center": zone_center,
            "zone_radius_km": zone_radius_km,
            "time_period": time_period,
            "recommendations": general_recommendations,
            "camera_placements": camera_placements,
            "attractant_placements": attractant_placements,
            "cache_recommendations": cache_recommendations,
            "high_probability_zones": [
                {"lat": p["lat"], "lng": p["lng"], "probability": p["probability"]}
                for p in high_prob_points[:5]
            ],
            "probability_summary": {
                "average": round(sum(p["probability"] for p in prob_heatmap["points"]) / len(prob_heatmap["points"]), 2),
                "max": round(max(p["probability"] for p in prob_heatmap["points"]), 2),
                "high_prob_area_percent": round(len([p for p in prob_heatmap["points"] if p["probability"] > 0.6]) / len(prob_heatmap["points"]) * 100, 1)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Sauvegarder le plan
        await self.db.action_plans.insert_one(plan)
        
        return plan
    
    # ============================================
    # SPECIES CLASSIFICATION (AI SIMULATION)
    # ============================================
    
    async def classify_photo_species(
        self,
        photo_path: str,
        photo_metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Classifie l'espèce sur une photo de caméra.
        En production, utiliserait un vrai modèle ML.
        """
        # Simulation de classification IA
        species_options = ["orignal", "chevreuil", "ours", "autre", "aucun"]
        weights = [0.25, 0.35, 0.15, 0.15, 0.10]  # Probabilités simulées
        
        detected_species = random.choices(species_options, weights=weights)[0]
        
        if detected_species == "aucun":
            confidence = 0.95
            count = 0
        else:
            confidence = random.uniform(0.65, 0.98)
            count = random.randint(1, 3) if detected_species != "autre" else 0
        
        return {
            "species": detected_species,
            "species_confidence": round(confidence, 2),
            "count_estimate": count,
            "processed": True,
            "model_version": "bionic-wildlife-v1.0",
            "processing_time_ms": random.randint(150, 500)
        }


# ============================================
# ANALYSIS CATEGORIES FOR UI
# ============================================

ANALYSIS_CATEGORIES = {
    "produits": {
        "name": "Produits de chasse",
        "icon": "🎯",
        "description": "Analysez et comparez les produits de chasse",
        "subcategories": [
            {
                "id": "attractants",
                "name": "Attractants & Leurres",
                "icon": "💧",
                "description": "Urines, gels, blocs, appâts",
                "actions": ["analyser", "comparer", "acheter"]
            },
            {
                "id": "cameras",
                "name": "Caméras de chasse",
                "icon": "📷",
                "description": "Trail cameras, détecteurs de mouvement",
                "actions": ["connecter", "analyser", "configurer"]
            },
            {
                "id": "equipement",
                "name": "Équipement",
                "icon": "🎒",
                "description": "Bottes, vêtements, accessoires",
                "actions": ["analyser", "comparer"]
            },
            {
                "id": "optiques",
                "name": "Optiques & Viseurs",
                "icon": "🔭",
                "description": "Jumelles, lunettes de visée, télémètres",
                "actions": ["analyser", "comparer"]
            },
            {
                "id": "appels",
                "name": "Appels & Sons",
                "icon": "📢",
                "description": "Appels originaux, électroniques",
                "actions": ["analyser", "écouter"]
            }
        ]
    },
    "territoire": {
        "name": "Analyse de territoire",
        "icon": "🗺️",
        "description": "Analysez votre territoire de chasse avec l'IA",
        "subcategories": [
            {
                "id": "cartographie",
                "name": "Cartographie IA",
                "icon": "📍",
                "description": "Zones de probabilité, corridors, refuges",
                "actions": ["analyser", "planifier"]
            },
            {
                "id": "cameras_territoire",
                "name": "Réseau de caméras",
                "icon": "📸",
                "description": "Connectez et analysez vos caméras",
                "actions": ["connecter", "visualiser", "analyser"]
            },
            {
                "id": "evenements",
                "name": "Événements & Observations",
                "icon": "👁️",
                "description": "Tirs, observations, traces",
                "actions": ["ajouter", "visualiser"]
            },
            {
                "id": "plan_action",
                "name": "Plan d'action",
                "icon": "📋",
                "description": "Générez un plan de chasse personnalisé",
                "actions": ["générer", "exporter"]
            }
        ]
    },
    "especes": {
        "name": "Espèces cibles",
        "icon": "🦌",
        "description": "Sélectionnez et analysez par espèce",
        "subcategories": [
            {
                "id": "orignal",
                "name": "Orignal",
                "icon": "🫎",
                "description": "Analyse spécifique orignal",
                "rules_summary": "Proximité eau, forêt mature, vallées"
            },
            {
                "id": "chevreuil",
                "name": "Chevreuil",
                "icon": "🦌",
                "description": "Analyse spécifique chevreuil",
                "rules_summary": "Lisières, friches, régénération"
            },
            {
                "id": "ours",
                "name": "Ours",
                "icon": "🐻",
                "description": "Analyse spécifique ours noir",
                "rules_summary": "Zones isolées, nourriture, eau"
            }
        ]
    }
}
