# referral_system.py - Système complet de parrainage et partage
import os
import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

# ============================================
# ENUMS & CONSTANTS
# ============================================

class ReferralTier(str, Enum):
    BRONZE = "bronze"      # 0-2 invités
    SILVER = "silver"      # 3-4 invités
    GOLD = "gold"          # 5-9 invités
    PLATINUM = "platinum"  # 10-19 invités
    DIAMOND = "diamond"    # 20+ invités
    PARTNER = "partner"    # Partenaire Privilégié

class SeasonType(str, Enum):
    PRE_SEASON = "pre_season"
    RUT = "rut"
    POST_RUT = "post_rut"
    OPENING = "opening"
    END_SEASON = "end_season"
    OFF_PEAK = "off_peak"
    BLACK_FRIDAY = "black_friday"
    BOXING_DAY = "boxing_day"
    CUSTOM = "custom"

# Default discount tiers (modifiable by admin)
DEFAULT_DISCOUNT_TIERS = {
    "bronze": {"min_buyers": 0, "max_buyers": 2, "discount_percent": 5, "label": "Bronze"},
    "silver": {"min_buyers": 3, "max_buyers": 4, "discount_percent": 10, "label": "Argent"},
    "gold": {"min_buyers": 5, "max_buyers": 9, "discount_percent": 15, "label": "Or"},
    "platinum": {"min_buyers": 10, "max_buyers": 19, "discount_percent": 25, "label": "Platine"},
    "diamond": {"min_buyers": 20, "max_buyers": 999, "discount_percent": 40, "label": "Diamant"},
    "partner": {"min_buyers": 0, "max_buyers": 999, "discount_percent": 50, "label": "Partenaire Privilégié"}
}

# Social platforms configuration
SOCIAL_PLATFORMS = {
    "facebook": {
        "name": "Facebook",
        "icon": "facebook",
        "share_url": "https://www.facebook.com/sharer/sharer.php?u={url}&quote={message}",
        "color": "#1877F2"
    },
    "messenger": {
        "name": "Messenger",
        "icon": "message-circle",
        "share_url": "https://www.facebook.com/dialog/send?link={url}&app_id=1&redirect_uri={url}",
        "color": "#0084FF"
    },
    "instagram": {
        "name": "Instagram",
        "icon": "instagram",
        "share_url": None,  # Instagram doesn't have direct share URL - copy to clipboard
        "color": "#E4405F"
    },
    "tiktok": {
        "name": "TikTok",
        "icon": "music",
        "share_url": None,  # Copy for TikTok
        "color": "#000000"
    },
    "whatsapp": {
        "name": "WhatsApp",
        "icon": "message-circle",
        "share_url": "https://api.whatsapp.com/send?text={message}%20{url}",
        "color": "#25D366"
    },
    "sms": {
        "name": "SMS",
        "icon": "smartphone",
        "share_url": "sms:?body={message}%20{url}",
        "color": "#34C759"
    },
    "email": {
        "name": "Courriel",
        "icon": "mail",
        "share_url": "mailto:?subject={subject}&body={message}%0A%0A{url}",
        "color": "#EA4335"
    },
    "copy": {
        "name": "Copier le lien",
        "icon": "copy",
        "share_url": None,
        "color": "#6B7280"
    }
}

# Pre-formatted messages templates
MESSAGE_TEMPLATES = {
    "facebook": {
        "fr": """🎯 Découvrez SCENT SCIENCE™ - L'analyse scientifique des attractants de chasse!

✅ Score d'efficacité sur 100 points
✅ Comparaison avec les meilleurs produits
✅ Recommandations personnalisées

Utilisez mon lien pour obtenir {discount}% de rabais sur votre première commande! 🦌

#chasse #attractant #hunting #deer""",
        "en": """🎯 Discover SCENT SCIENCE™ - Scientific hunting attractant analysis!

✅ Effectiveness score out of 100
✅ Comparison with top products
✅ Personalized recommendations

Use my link for {discount}% off your first order! 🦌

#hunting #attractant #deer #outdoors"""
    },
    "instagram": {
        "fr": """🦌 SCENT SCIENCE™ - La science au service de votre chasse!

Analysez n'importe quel attractant et obtenez:
📊 Un score sur 100
🏆 Les 3 meilleurs produits
💰 Des rabais exclusifs

Lien dans ma bio ou en story! ⬆️
{discount}% de rabais avec mon code!

#chasse #hunting #chevreuil #orignal #attractant #chasseur""",
        "en": """🦌 SCENT SCIENCE™ - Science for better hunting!

Analyze any attractant and get:
📊 Score out of 100
🏆 Top 3 products
💰 Exclusive discounts

Link in bio or story! ⬆️
{discount}% off with my code!

#hunting #deer #moose #outdoors #hunter"""
    },
    "tiktok": {
        "fr": """POV: Tu découvres que ton attractant ne vaut que 3/10 😱

SCENT SCIENCE™ analyse scientifiquement tous les attractants de chasse.
Score, comparaison, recommandations.

Lien en bio - {discount}% de rabais! 🦌

#chassetiktok #hunting #chevreuil #attractant""",
        "en": """POV: You find out your attractant only scores 3/10 😱

SCENT SCIENCE™ scientifically analyzes all hunting attractants.
Score, comparison, recommendations.

Link in bio - {discount}% off! 🦌

#huntingtiktok #deerhunting #outdoors"""
    },
    "whatsapp": {
        "fr": """Salut! 🦌

J'ai découvert SCENT SCIENCE™ - un labo qui analyse scientifiquement les attractants de chasse.

Tu peux tester n'importe quel produit et voir son score sur 100!

Utilise mon lien pour avoir {discount}% de rabais:""",
        "en": """Hey! 🦌

I found SCENT SCIENCE™ - a lab that scientifically analyzes hunting attractants.

You can test any product and see its score out of 100!

Use my link for {discount}% off:"""
    },
    "sms": {
        "fr": """🦌 SCENT SCIENCE - Analyse tes attractants! Score sur 100, comparaison, recommandations. {discount}% rabais avec mon lien:""",
        "en": """🦌 SCENT SCIENCE - Analyze your attractants! Score out of 100, comparison, recommendations. {discount}% off with my link:"""
    },
    "email": {
        "fr": {
            "subject": "🦌 Découvre SCENT SCIENCE™ - {discount}% de rabais pour toi!",
            "body": """Salut!

Je voulais te partager une découverte géniale pour la chasse: SCENT SCIENCE™

C'est un laboratoire en ligne qui analyse scientifiquement les attractants de chasse. Tu entres le nom d'un produit et tu obtiens:

✅ Un score d'efficacité sur 100 points
✅ Une comparaison avec les meilleurs produits du marché
✅ Des recommandations personnalisées selon l'espèce ciblée
✅ Les ingrédients et la composition analysés

J'ai un lien de parrainage qui te donne {discount}% de rabais sur ta première commande!

Clique ici pour essayer:"""
        },
        "en": {
            "subject": "🦌 Discover SCENT SCIENCE™ - {discount}% off for you!",
            "body": """Hey!

I wanted to share an amazing discovery for hunting: SCENT SCIENCE™

It's an online lab that scientifically analyzes hunting attractants. You enter a product name and get:

✅ Effectiveness score out of 100
✅ Comparison with top market products
✅ Personalized recommendations by target species
✅ Ingredients and composition analysis

I have a referral link that gives you {discount}% off your first order!

Click here to try it:"""
        }
    }
}

# ============================================
# MODELS
# ============================================

class ReferralUser(BaseModel):
    """Utilisateur du système de parrainage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identité
    name: str
    email: str
    phone: Optional[str] = None
    
    # Code de parrainage unique
    referral_code: str = Field(default_factory=lambda: secrets.token_urlsafe(8)[:10].upper())
    referral_link: str = ""  # Generated based on code
    
    # Statistiques
    total_clicks: int = 0
    total_signups: int = 0
    total_buyers: int = 0
    total_revenue_generated: float = 0.0
    
    # Niveau et rabais
    tier: ReferralTier = ReferralTier.BRONZE
    current_discount_percent: int = 5
    
    # Partenaire Privilégié
    is_partner: bool = False
    partner_type: Optional[str] = None  # boutique, pourvoirie, guide, influenceur, revendeur
    partner_approved_at: Optional[datetime] = None
    partner_commission_rate: float = 0.0  # % de commission sur ventes des invités
    
    # Historique
    rewards_history: List[Dict[str, Any]] = []
    
    # Métadonnées
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: Optional[datetime] = None
    is_active: bool = True

class ReferralClick(BaseModel):
    """Suivi des clics sur les liens de parrainage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referral_code: str
    referrer_id: str
    
    # Source
    source_platform: str = "direct"  # facebook, whatsapp, email, etc.
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Conversion
    converted_to_signup: bool = False
    converted_to_purchase: bool = False
    conversion_value: float = 0.0
    
    clicked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReferralInvite(BaseModel):
    """Invité parrainé"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Parrain
    referrer_id: str
    referral_code: str
    
    # Invité
    invitee_email: str
    invitee_name: Optional[str] = None
    
    # Statut
    status: Literal["clicked", "signed_up", "purchased"] = "clicked"
    
    # Achats
    total_purchases: int = 0
    total_spent: float = 0.0
    first_purchase_at: Optional[datetime] = None
    last_purchase_at: Optional[datetime] = None
    
    # Dates
    invited_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signed_up_at: Optional[datetime] = None

class DiscountTierConfig(BaseModel):
    """Configuration d'un niveau de rabais"""
    tier_id: str
    min_buyers: int
    max_buyers: int
    discount_percent: int
    label: str
    is_active: bool = True

class SeasonalPromotion(BaseModel):
    """Promotion saisonnière"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    season_type: SeasonType
    
    # Période
    start_date: datetime
    end_date: datetime
    
    # Rabais
    additional_discount_percent: int = 0
    applies_to_all: bool = True
    applies_to_categories: List[str] = []
    applies_to_products: List[str] = []
    
    # Statut
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductDiscount(BaseModel):
    """Rabais spécifique par produit/catégorie"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Cible
    discount_type: Literal["category", "brand", "product"] = "category"
    target_id: str  # category name, brand name, or product id
    target_name: str
    
    # Rabais
    discount_percent: int = 0
    reason: str = ""  # lancement, forte marge, surstock
    
    # Période
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PartnerApplication(BaseModel):
    """Demande pour devenir Partenaire Privilégié"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Informations
    business_name: str
    business_type: Literal["boutique", "pourvoirie", "guide", "influenceur", "revendeur"]
    website: Optional[str] = None
    social_media: Dict[str, str] = {}  # {platform: url}
    
    # Justification
    estimated_monthly_volume: float = 0
    existing_referrals: int = 0
    motivation: str = ""
    
    # Statut
    status: Literal["pending", "approved", "rejected"] = "pending"
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReferralReward(BaseModel):
    """Récompense attribuée"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Type
    reward_type: Literal["discount_upgrade", "commission", "bonus"] = "discount_upgrade"
    
    # Détails
    description: str
    value: float = 0
    new_tier: Optional[ReferralTier] = None
    new_discount_percent: Optional[int] = None
    
    # Déclencheur
    triggered_by: str = ""  # "invitee_purchase", "tier_upgrade", "seasonal_bonus"
    invitee_id: Optional[str] = None
    order_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_notified: bool = False

# ============================================
# REFERRAL SERVICE
# ============================================

class ReferralService:
    def __init__(self, db, base_url: str):
        self.db = db
        self.base_url = base_url
    
    def generate_referral_link(self, code: str) -> str:
        """Génère le lien de parrainage complet"""
        return f"{self.base_url}?ref={code}"
    
    async def get_discount_tiers(self) -> Dict[str, DiscountTierConfig]:
        """Récupère la configuration des niveaux de rabais"""
        config = await self.db.referral_config.find_one({"type": "discount_tiers"}, {"_id": 0})
        if config:
            return config.get("tiers", DEFAULT_DISCOUNT_TIERS)
        
        # Créer config par défaut
        await self.db.referral_config.insert_one({
            "type": "discount_tiers",
            "tiers": DEFAULT_DISCOUNT_TIERS
        })
        return DEFAULT_DISCOUNT_TIERS
    
    async def update_discount_tiers(self, tiers: Dict[str, Any]) -> Dict:
        """Met à jour les niveaux de rabais"""
        await self.db.referral_config.update_one(
            {"type": "discount_tiers"},
            {"$set": {"tiers": tiers}},
            upsert=True
        )
        return await self.get_discount_tiers()
    
    def calculate_tier(self, total_buyers: int, is_partner: bool = False) -> tuple:
        """Calcule le niveau et rabais basé sur le nombre d'acheteurs"""
        if is_partner:
            return ReferralTier.PARTNER, DEFAULT_DISCOUNT_TIERS["partner"]["discount_percent"]
        
        for tier_id, config in DEFAULT_DISCOUNT_TIERS.items():
            if tier_id == "partner":
                continue
            if config["min_buyers"] <= total_buyers <= config["max_buyers"]:
                return ReferralTier(tier_id), config["discount_percent"]
        
        return ReferralTier.DIAMOND, DEFAULT_DISCOUNT_TIERS["diamond"]["discount_percent"]
    
    async def create_referral_user(self, name: str, email: str, phone: str = None) -> ReferralUser:
        """Crée un nouvel utilisateur de parrainage"""
        # Vérifier si l'email existe déjà
        existing = await self.db.referral_users.find_one({"email": email})
        if existing:
            raise ValueError("Un compte de parrainage existe déjà pour cet email")
        
        user = ReferralUser(name=name, email=email, phone=phone)
        user.referral_link = self.generate_referral_link(user.referral_code)
        
        doc = user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        if doc.get('last_activity'):
            doc['last_activity'] = doc['last_activity'].isoformat()
        if doc.get('partner_approved_at'):
            doc['partner_approved_at'] = doc['partner_approved_at'].isoformat()
        
        await self.db.referral_users.insert_one(doc)
        return user
    
    async def get_user_by_code(self, code: str) -> Optional[Dict]:
        """Récupère un utilisateur par son code de parrainage"""
        return await self.db.referral_users.find_one({"referral_code": code}, {"_id": 0})
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Récupère un utilisateur par son email"""
        return await self.db.referral_users.find_one({"email": email}, {"_id": 0})
    
    async def track_click(self, code: str, source: str = "direct", ip: str = None, user_agent: str = None) -> bool:
        """Enregistre un clic sur un lien de parrainage"""
        user = await self.get_user_by_code(code)
        if not user:
            return False
        
        click = ReferralClick(
            referral_code=code,
            referrer_id=user["id"],
            source_platform=source,
            ip_address=ip,
            user_agent=user_agent
        )
        
        doc = click.model_dump()
        doc['clicked_at'] = doc['clicked_at'].isoformat()
        
        await self.db.referral_clicks.insert_one(doc)
        
        # Incrémenter le compteur
        await self.db.referral_users.update_one(
            {"referral_code": code},
            {
                "$inc": {"total_clicks": 1},
                "$set": {"last_activity": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return True
    
    async def register_invitee(self, referral_code: str, invitee_email: str, invitee_name: str = None) -> Optional[ReferralInvite]:
        """Enregistre un nouvel invité"""
        user = await self.get_user_by_code(referral_code)
        if not user:
            return None
        
        # Vérifier si l'invité existe déjà
        existing = await self.db.referral_invites.find_one({
            "referrer_id": user["id"],
            "invitee_email": invitee_email
        })
        if existing:
            return None
        
        invite = ReferralInvite(
            referrer_id=user["id"],
            referral_code=referral_code,
            invitee_email=invitee_email,
            invitee_name=invitee_name,
            status="signed_up",
            signed_up_at=datetime.now(timezone.utc)
        )
        
        doc = invite.model_dump()
        doc['invited_at'] = doc['invited_at'].isoformat()
        if doc.get('signed_up_at'):
            doc['signed_up_at'] = doc['signed_up_at'].isoformat()
        
        await self.db.referral_invites.insert_one(doc)
        
        # Incrémenter les signups
        await self.db.referral_users.update_one(
            {"referral_code": referral_code},
            {"$inc": {"total_signups": 1}}
        )
        
        return invite
    
    async def record_purchase(self, referral_code: str, invitee_email: str, order_amount: float, order_id: str) -> Dict:
        """Enregistre un achat d'un invité et met à jour les récompenses"""
        user = await self.get_user_by_code(referral_code)
        if not user:
            return {"success": False, "error": "Code invalide"}
        
        # Mettre à jour l'invité
        now = datetime.now(timezone.utc)
        result = await self.db.referral_invites.update_one(
            {"referrer_id": user["id"], "invitee_email": invitee_email},
            {
                "$set": {
                    "status": "purchased",
                    "last_purchase_at": now.isoformat()
                },
                "$inc": {
                    "total_purchases": 1,
                    "total_spent": order_amount
                },
                "$setOnInsert": {
                    "first_purchase_at": now.isoformat()
                }
            }
        )
        
        # Vérifier si c'est le premier achat de cet invité
        invite = await self.db.referral_invites.find_one({
            "referrer_id": user["id"],
            "invitee_email": invitee_email
        })
        
        is_first_purchase = invite and invite.get("total_purchases") == 1
        
        if is_first_purchase:
            # Incrémenter le compteur d'acheteurs
            await self.db.referral_users.update_one(
                {"referral_code": referral_code},
                {"$inc": {"total_buyers": 1}}
            )
        
        # Toujours incrémenter le revenu généré
        await self.db.referral_users.update_one(
            {"referral_code": referral_code},
            {"$inc": {"total_revenue_generated": order_amount}}
        )
        
        # Recalculer le niveau
        updated_user = await self.get_user_by_code(referral_code)
        new_tier, new_discount = self.calculate_tier(
            updated_user["total_buyers"],
            updated_user.get("is_partner", False)
        )
        
        tier_upgraded = new_tier.value != updated_user.get("tier", "bronze")
        
        # Mettre à jour le niveau si changé
        if tier_upgraded or new_discount != updated_user.get("current_discount_percent"):
            await self.db.referral_users.update_one(
                {"referral_code": referral_code},
                {
                    "$set": {
                        "tier": new_tier.value,
                        "current_discount_percent": new_discount
                    }
                }
            )
            
            # Créer une récompense
            reward = ReferralReward(
                user_id=user["id"],
                reward_type="discount_upgrade",
                description=f"Niveau mis à jour: {new_tier.value} - {new_discount}% de rabais",
                new_tier=new_tier,
                new_discount_percent=new_discount,
                triggered_by="invitee_purchase",
                invitee_id=invite["id"] if invite else None,
                order_id=order_id
            )
            
            doc = reward.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await self.db.referral_rewards.insert_one(doc)
        
        # Commission pour les partenaires
        commission_earned = 0
        if updated_user.get("is_partner") and updated_user.get("partner_commission_rate", 0) > 0:
            commission_earned = order_amount * (updated_user["partner_commission_rate"] / 100)
            
            # Enregistrer la commission
            commission_reward = ReferralReward(
                user_id=user["id"],
                reward_type="commission",
                description=f"Commission sur achat: ${commission_earned:.2f}",
                value=commission_earned,
                triggered_by="partner_commission",
                order_id=order_id
            )
            doc = commission_reward.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await self.db.referral_rewards.insert_one(doc)
        
        return {
            "success": True,
            "tier_upgraded": tier_upgraded,
            "new_tier": new_tier.value,
            "new_discount": new_discount,
            "is_first_purchase": is_first_purchase,
            "commission_earned": commission_earned
        }
    
    async def get_user_dashboard(self, user_id: str) -> Dict:
        """Récupère les données du tableau de bord utilisateur"""
        user = await self.db.referral_users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            return None
        
        # Récupérer les invités
        invites = await self.db.referral_invites.find(
            {"referrer_id": user_id},
            {"_id": 0}
        ).to_list(100)
        
        # Récupérer les récompenses
        rewards = await self.db.referral_rewards.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        
        # Calculer la progression vers le prochain niveau
        tiers = await self.get_discount_tiers()
        current_tier = user.get("tier", "bronze")
        total_buyers = user.get("total_buyers", 0)
        
        next_tier_info = None
        tier_order = ["bronze", "silver", "gold", "platinum", "diamond"]
        
        if current_tier in tier_order:
            current_idx = tier_order.index(current_tier)
            if current_idx < len(tier_order) - 1:
                next_tier = tier_order[current_idx + 1]
                next_config = tiers.get(next_tier, {})
                buyers_needed = next_config.get("min_buyers", 0) - total_buyers
                next_tier_info = {
                    "next_tier": next_tier,
                    "next_tier_label": next_config.get("label", next_tier),
                    "next_discount": next_config.get("discount_percent", 0),
                    "buyers_needed": max(0, buyers_needed),
                    "progress_percent": min(100, (total_buyers / max(next_config.get("min_buyers", 1), 1)) * 100)
                }
        
        return {
            "user": user,
            "invites": invites,
            "rewards": rewards,
            "next_tier_info": next_tier_info,
            "share_messages": self.get_share_messages(user.get("current_discount_percent", 5))
        }
    
    def get_share_messages(self, discount_percent: int, lang: str = "fr") -> Dict[str, str]:
        """Génère les messages de partage personnalisés"""
        messages = {}
        for platform, templates in MESSAGE_TEMPLATES.items():
            if lang in templates:
                if isinstance(templates[lang], dict):
                    messages[platform] = {
                        k: v.format(discount=discount_percent)
                        for k, v in templates[lang].items()
                    }
                else:
                    messages[platform] = templates[lang].format(discount=discount_percent)
            elif "fr" in templates:
                if isinstance(templates["fr"], dict):
                    messages[platform] = {
                        k: v.format(discount=discount_percent)
                        for k, v in templates["fr"].items()
                    }
                else:
                    messages[platform] = templates["fr"].format(discount=discount_percent)
        
        return messages
    
    async def get_active_promotions(self) -> List[Dict]:
        """Récupère les promotions saisonnières actives"""
        now = datetime.now(timezone.utc)
        promotions = await self.db.seasonal_promotions.find({
            "is_active": True,
            "start_date": {"$lte": now.isoformat()},
            "end_date": {"$gte": now.isoformat()}
        }, {"_id": 0}).to_list(20)
        
        return promotions
    
    async def get_product_discounts(self, product_id: str = None, category: str = None, brand: str = None) -> List[Dict]:
        """Récupère les rabais applicables pour un produit"""
        query = {"is_active": True}
        
        discounts = []
        
        if product_id:
            product_discount = await self.db.product_discounts.find_one({
                "is_active": True,
                "discount_type": "product",
                "target_id": product_id
            }, {"_id": 0})
            if product_discount:
                discounts.append(product_discount)
        
        if category:
            cat_discount = await self.db.product_discounts.find_one({
                "is_active": True,
                "discount_type": "category",
                "target_id": category
            }, {"_id": 0})
            if cat_discount:
                discounts.append(cat_discount)
        
        if brand:
            brand_discount = await self.db.product_discounts.find_one({
                "is_active": True,
                "discount_type": "brand",
                "target_id": brand
            }, {"_id": 0})
            if brand_discount:
                discounts.append(brand_discount)
        
        return discounts
    
    def calculate_final_discount(
        self,
        base_referral_discount: int,
        product_discounts: List[Dict],
        seasonal_promotions: List[Dict]
    ) -> Dict:
        """Calcule le rabais final cumulé"""
        total_discount = base_referral_discount
        breakdown = [{"type": "referral", "value": base_referral_discount}]
        
        # Ajouter les rabais produit (prendre le meilleur)
        if product_discounts:
            best_product_discount = max(product_discounts, key=lambda x: x.get("discount_percent", 0))
            product_discount_value = best_product_discount.get("discount_percent", 0)
            if product_discount_value > 0:
                total_discount += product_discount_value
                breakdown.append({
                    "type": "product",
                    "value": product_discount_value,
                    "reason": best_product_discount.get("reason", "")
                })
        
        # Ajouter les promotions saisonnières
        for promo in seasonal_promotions:
            promo_value = promo.get("additional_discount_percent", 0)
            if promo_value > 0:
                total_discount += promo_value
                breakdown.append({
                    "type": "seasonal",
                    "value": promo_value,
                    "name": promo.get("name", "")
                })
        
        # Plafonner à 60%
        total_discount = min(total_discount, 60)
        
        return {
            "total_discount": total_discount,
            "breakdown": breakdown
        }
    
    # ---- Partner Management ----
    
    async def apply_for_partner(self, application: PartnerApplication) -> str:
        """Soumet une demande de partenariat"""
        doc = application.model_dump()
        doc['submitted_at'] = doc['submitted_at'].isoformat()
        
        await self.db.partner_applications.insert_one(doc)
        return application.id
    
    async def approve_partner(self, application_id: str, commission_rate: float = 10) -> Dict:
        """Approuve une demande de partenariat"""
        app = await self.db.partner_applications.find_one({"id": application_id})
        if not app:
            return {"success": False, "error": "Application non trouvée"}
        
        now = datetime.now(timezone.utc)
        
        # Mettre à jour l'application
        await self.db.partner_applications.update_one(
            {"id": application_id},
            {
                "$set": {
                    "status": "approved",
                    "reviewed_at": now.isoformat()
                }
            }
        )
        
        # Mettre à jour l'utilisateur
        await self.db.referral_users.update_one(
            {"id": app["user_id"]},
            {
                "$set": {
                    "is_partner": True,
                    "partner_type": app.get("business_type"),
                    "partner_approved_at": now.isoformat(),
                    "partner_commission_rate": commission_rate,
                    "tier": ReferralTier.PARTNER.value,
                    "current_discount_percent": DEFAULT_DISCOUNT_TIERS["partner"]["discount_percent"]
                }
            }
        )
        
        return {"success": True, "user_id": app["user_id"]}
    
    async def reject_partner(self, application_id: str, reason: str) -> Dict:
        """Rejette une demande de partenariat"""
        result = await self.db.partner_applications.update_one(
            {"id": application_id},
            {
                "$set": {
                    "status": "rejected",
                    "reviewed_at": datetime.now(timezone.utc).isoformat(),
                    "rejection_reason": reason
                }
            }
        )
        
        return {"success": result.modified_count > 0}
    
    # ---- Admin Stats ----
    
    async def get_admin_dashboard(self) -> Dict:
        """Récupère les statistiques admin du programme de parrainage"""
        # Totaux
        total_users = await self.db.referral_users.count_documents({})
        total_partners = await self.db.referral_users.count_documents({"is_partner": True})
        total_invites = await self.db.referral_invites.count_documents({})
        total_buyers = await self.db.referral_invites.count_documents({"status": "purchased"})
        
        # Revenue
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$total_revenue_generated"}}}
        ]
        revenue_result = await self.db.referral_users.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Top parrains
        top_referrers = await self.db.referral_users.find(
            {},
            {"_id": 0}
        ).sort("total_buyers", -1).limit(10).to_list(10)
        
        # Par niveau
        tier_counts = {}
        for tier in ReferralTier:
            count = await self.db.referral_users.count_documents({"tier": tier.value})
            tier_counts[tier.value] = count
        
        # Applications partenaires en attente
        pending_applications = await self.db.partner_applications.count_documents({"status": "pending"})
        
        # Promotions actives
        active_promotions = await self.get_active_promotions()
        
        return {
            "total_users": total_users,
            "total_partners": total_partners,
            "total_invites": total_invites,
            "total_buyers": total_buyers,
            "total_revenue": total_revenue,
            "top_referrers": top_referrers,
            "tier_distribution": tier_counts,
            "pending_partner_applications": pending_applications,
            "active_promotions": len(active_promotions)
        }
