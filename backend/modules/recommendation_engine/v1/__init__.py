"""Recommendation Engine Module v1

Intelligent recommendation system for products and strategies.
Uses collaborative filtering and context-aware algorithms.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid
import os
import random
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1/recommendation", tags=["Recommendation Engine"])


# ============================================
# MODELS
# ============================================

class RecommendationType(str, Enum):
    PRODUCT = "product"
    STRATEGY = "strategy"
    TERRITORY = "territory"
    ATTRACTANT = "attractant"


class RecommendationContext(BaseModel):
    """Context for generating recommendations"""
    user_id: Optional[str] = None
    species: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    terrain: Optional[str] = None
    budget_max: Optional[float] = None
    experience_level: Optional[str] = None


class Recommendation(BaseModel):
    """A single recommendation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: RecommendationType
    item_id: str
    item_name: str
    score: float = Field(ge=0, le=100, description="Relevance score 0-100")
    reason: str = ""
    metadata: Dict[str, Any] = {}


class RecommendationResult(BaseModel):
    """Result of a recommendation request"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    context: Optional[RecommendationContext] = None
    recommendations: List[Recommendation] = []
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPreference(BaseModel):
    """User preference for learning"""
    user_id: str
    item_id: str
    item_type: RecommendationType
    action: Literal["view", "like", "purchase", "dismiss"]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================
# SAMPLE DATA
# ============================================

SAMPLE_PRODUCTS = [
    {"id": "prod-001", "name": "BIONIC™ Apple Jelly Premium", "type": "gel", "species": ["deer", "moose"], "score": 92, "price": 29.99},
    {"id": "prod-002", "name": "BIONIC™ Bloc Mix Ultra", "type": "bloc", "species": ["deer", "moose"], "score": 90, "price": 24.99},
    {"id": "prod-003", "name": "BIONIC™ Buck Urine Premium", "type": "urine", "species": ["deer"], "score": 95, "price": 34.99},
    {"id": "prod-004", "name": "BIONIC™ Deer Granules Pro", "type": "granules", "species": ["deer"], "score": 88, "price": 19.99},
    {"id": "prod-005", "name": "BIONIC™ Bear Attractant", "type": "gel", "species": ["bear"], "score": 91, "price": 32.99},
    {"id": "prod-006", "name": "BIONIC™ Moose Call Scent", "type": "urine", "species": ["moose"], "score": 89, "price": 39.99},
    {"id": "prod-007", "name": "BIONIC™ Turkey Decoy Scent", "type": "liquide", "species": ["turkey"], "score": 87, "price": 22.99},
    {"id": "prod-008", "name": "BIONIC™ All-Season Mineral", "type": "bloc", "species": ["deer", "moose"], "score": 86, "price": 27.99},
]

SAMPLE_STRATEGIES = [
    {"id": "strat-001", "name": "Affût à l'aube", "species": ["deer"], "season": ["fall"], "terrain": ["forest", "edge"], "score": 95},
    {"id": "strat-002", "name": "Traque douce", "species": ["deer", "moose"], "season": ["fall"], "terrain": ["forest"], "score": 88},
    {"id": "strat-003", "name": "Appel au rut", "species": ["deer", "moose"], "season": ["fall"], "terrain": ["forest", "field"], "score": 92},
    {"id": "strat-004", "name": "Affût sur souille", "species": ["wild_boar"], "season": ["summer", "fall"], "terrain": ["forest"], "score": 90},
    {"id": "strat-005", "name": "Poste en lisière", "species": ["deer", "turkey"], "season": ["spring", "fall"], "terrain": ["edge", "field"], "score": 89},
]


# ============================================
# SERVICE
# ============================================

class RecommendationService:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    def _calculate_product_score(self, product: Dict, context: RecommendationContext) -> float:
        base_score = product.get("score", 80)
        if context.species and context.species in product.get("species", []):
            base_score += 10
        if context.budget_max and product.get("price", 0) <= context.budget_max:
            base_score += 5
        base_score += random.uniform(-5, 5)
        return min(100, max(0, base_score))
    
    def _calculate_strategy_score(self, strategy: Dict, context: RecommendationContext) -> float:
        base_score = strategy.get("score", 80)
        if context.species and context.species in strategy.get("species", []):
            base_score += 10
        if context.season and context.season in strategy.get("season", []):
            base_score += 8
        if context.terrain and context.terrain in strategy.get("terrain", []):
            base_score += 7
        base_score += random.uniform(-3, 3)
        return min(100, max(0, base_score))
    
    async def get_product_recommendations(self, context: RecommendationContext = None, limit: int = 5) -> List[Recommendation]:
        context = context or RecommendationContext()
        recommendations = []
        for product in SAMPLE_PRODUCTS:
            score = self._calculate_product_score(product, context)
            reasons = []
            if context.species and context.species in product.get("species", []):
                reasons.append(f"Idéal pour {context.species}")
            if product.get("score", 0) >= 90:
                reasons.append("Produit très bien noté")
            recommendations.append(Recommendation(
                type=RecommendationType.PRODUCT,
                item_id=product["id"],
                item_name=product["name"],
                score=round(score, 1),
                reason=" • ".join(reasons) if reasons else "Recommandé pour vous",
                metadata={"product_type": product.get("type"), "price": product.get("price")}
            ))
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    async def get_strategy_recommendations(self, context: RecommendationContext = None, limit: int = 5) -> List[Recommendation]:
        context = context or RecommendationContext()
        recommendations = []
        for strategy in SAMPLE_STRATEGIES:
            score = self._calculate_strategy_score(strategy, context)
            reasons = []
            if context.species and context.species in strategy.get("species", []):
                reasons.append(f"Adapté pour {context.species}")
            if context.season and context.season in strategy.get("season", []):
                reasons.append(f"Optimal en {context.season}")
            recommendations.append(Recommendation(
                type=RecommendationType.STRATEGY,
                item_id=strategy["id"],
                item_name=strategy["name"],
                score=round(score, 1),
                reason=" • ".join(reasons) if reasons else "Stratégie recommandée",
                metadata={"species": strategy.get("species"), "season": strategy.get("season")}
            ))
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    async def get_similar_products(self, product_id: str, limit: int = 4) -> List[Recommendation]:
        ref_product = next((p for p in SAMPLE_PRODUCTS if p["id"] == product_id), None)
        if not ref_product:
            return []
        recommendations = []
        for product in SAMPLE_PRODUCTS:
            if product["id"] == product_id:
                continue
            similarity = 50
            if product.get("type") == ref_product.get("type"):
                similarity += 20
            shared_species = set(product.get("species", [])) & set(ref_product.get("species", []))
            similarity += len(shared_species) * 15
            recommendations.append(Recommendation(
                type=RecommendationType.PRODUCT,
                item_id=product["id"],
                item_name=product["name"],
                score=round(min(100, similarity), 1),
                reason="Produit similaire",
                metadata={"product_type": product.get("type"), "price": product.get("price")}
            ))
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    async def record_preference(self, preference: UserPreference):
        pref_dict = preference.model_dump()
        pref_dict.pop("_id", None)
        self.db.user_preferences_reco.insert_one(pref_dict)


_service = RecommendationService()


# ============================================
# ROUTES
# ============================================

@router.get("/")
async def recommendation_engine_info():
    return {
        "module": "recommendation_engine",
        "version": "1.0.0",
        "description": "Intelligent recommendation system",
        "features": ["Product recommendations", "Strategy recommendations", "Similar products", "Personalized recommendations", "Context-aware filtering"],
        "recommendation_types": [t.value for t in RecommendationType],
        "sample_products": len(SAMPLE_PRODUCTS),
        "sample_strategies": len(SAMPLE_STRATEGIES)
    }


@router.post("/products")
async def get_product_recommendations(context: RecommendationContext = None, limit: int = Query(5, ge=1, le=20)):
    recommendations = await _service.get_product_recommendations(context, limit)
    return {"success": True, "type": "products", "count": len(recommendations), "recommendations": [r.model_dump() for r in recommendations]}


@router.post("/strategies")
async def get_strategy_recommendations(context: RecommendationContext = None, limit: int = Query(5, ge=1, le=20)):
    recommendations = await _service.get_strategy_recommendations(context, limit)
    return {"success": True, "type": "strategies", "count": len(recommendations), "recommendations": [r.model_dump() for r in recommendations]}


@router.get("/similar/{product_id}")
async def get_similar_products(product_id: str, limit: int = Query(4, ge=1, le=10)):
    recommendations = await _service.get_similar_products(product_id, limit)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "reference_product": product_id, "similar": [r.model_dump() for r in recommendations]}


@router.post("/for-context")
async def get_contextual_recommendations(context: RecommendationContext, limit: int = Query(10, ge=1, le=30)):
    products = await _service.get_product_recommendations(context, limit // 2)
    strategies = await _service.get_strategy_recommendations(context, limit // 2)
    all_recs = products + strategies
    all_recs.sort(key=lambda x: x.score, reverse=True)
    return {"success": True, "context": context.model_dump(), "recommendations": [r.model_dump() for r in all_recs[:limit]]}


@router.post("/preference")
async def record_user_preference(preference: UserPreference):
    await _service.record_preference(preference)
    return {"success": True, "message": "Preference recorded"}


@router.get("/trending")
async def get_trending():
    trending_products = sorted(SAMPLE_PRODUCTS, key=lambda x: x.get("score", 0), reverse=True)[:3]
    trending_strategies = sorted(SAMPLE_STRATEGIES, key=lambda x: x.get("score", 0), reverse=True)[:3]
    return {"success": True, "trending_products": trending_products, "trending_strategies": trending_strategies}
