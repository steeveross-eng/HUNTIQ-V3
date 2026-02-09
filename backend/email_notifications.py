"""
Email Notifications Module
- Send notification digest emails to users
- Support for daily and weekly digests
- HTML email templates with French localization
"""

import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, BackgroundTasks

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/email", tags=["Email Notifications"])

# Database connection
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'scentscience')]

# Resend configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
APP_NAME = "Chasse Bionic™"
APP_NAME_EN = "Bionic Hunt™"
APP_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000').replace('/api', '').rstrip('/')

# Initialize Resend if API key is available
resend = None
if RESEND_API_KEY:
    try:
        import resend as resend_module
        resend_module.api_key = RESEND_API_KEY
        resend = resend_module
        logger.info("Resend email service initialized")
    except ImportError:
        logger.warning("Resend module not installed")
else:
    logger.warning("RESEND_API_KEY not configured - email notifications disabled")


# ============================================
# EMAIL TEMPLATES
# ============================================

def get_email_template(content: str, preheader: str = "") -> str:
    """Generate base HTML email template"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{APP_NAME}</title>
        <!--[if mso]>
        <style type="text/css">
            table {{ border-collapse: collapse; }}
            td {{ padding: 0; }}
        </style>
        <![endif]-->
    </head>
    <body style="margin: 0; padding: 0; background-color: #0a0a0a; font-family: Arial, sans-serif;">
        <!-- Preheader text -->
        <div style="display: none; max-height: 0; overflow: hidden;">
            {preheader}
        </div>
        
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0a0a0a; padding: 20px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #1a1a1a; border-radius: 12px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #f5a623 0%, #d4891c 100%); padding: 30px; text-align: center;">
                                <h1 style="margin: 0; color: #000; font-size: 24px; font-weight: bold;">
                                    🎯 {APP_NAME}
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px; color: #ffffff;">
                                {content}
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px 30px; background-color: #111; border-top: 1px solid #333; text-align: center;">
                                <p style="margin: 0 0 10px; color: #888; font-size: 12px;">
                                    Cet email a été envoyé par {APP_NAME}
                                </p>
                                <p style="margin: 0; color: #666; font-size: 11px;">
                                    <a href="{APP_URL}/network" style="color: #f5a623; text-decoration: none;">
                                        Gérer mes préférences de notification
                                    </a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def generate_notification_digest_email(user_name: str, notifications: List[dict], period: str = "quotidien") -> str:
    """Generate notification digest email content"""
    
    # Group notifications by type
    likes = [n for n in notifications if n.get('type') in ['like_post', 'like_comment']]
    comments = [n for n in notifications if n.get('type') in ['comment', 'reply']]
    groups = [n for n in notifications if n.get('type') in ['group_join', 'group_invite', 'group_post']]
    referrals = [n for n in notifications if n.get('type') in ['referral_signup', 'referral_rewarded']]
    wallet = [n for n in notifications if n.get('type') in ['wallet_credit', 'wallet_transfer']]
    
    sections = []
    
    # Greeting
    greeting = f"""
    <h2 style="margin: 0 0 20px; color: #f5a623; font-size: 22px;">
        Bonjour {user_name}! 👋
    </h2>
    <p style="margin: 0 0 25px; color: #ccc; font-size: 15px; line-height: 1.6;">
        Voici votre résumé {period} d'activité sur {APP_NAME}.
        Vous avez <strong style="color: #f5a623;">{len(notifications)} nouvelle(s) notification(s)</strong>.
    </p>
    """
    sections.append(greeting)
    
    # Likes section
    if likes:
        likes_html = f"""
        <div style="margin-bottom: 25px; padding: 20px; background-color: #222; border-radius: 8px; border-left: 4px solid #e74c3c;">
            <h3 style="margin: 0 0 15px; color: #e74c3c; font-size: 16px;">
                ❤️ J'aime reçus ({len(likes)})
            </h3>
            <ul style="margin: 0; padding: 0 0 0 20px; color: #ddd; font-size: 14px; line-height: 1.8;">
        """
        for notif in likes[:5]:  # Max 5 items
            likes_html += f'<li>{notif.get("message", "")}</li>'
        if len(likes) > 5:
            likes_html += f'<li style="color: #888;">...et {len(likes) - 5} autres</li>'
        likes_html += "</ul></div>"
        sections.append(likes_html)
    
    # Comments section
    if comments:
        comments_html = f"""
        <div style="margin-bottom: 25px; padding: 20px; background-color: #222; border-radius: 8px; border-left: 4px solid #3498db;">
            <h3 style="margin: 0 0 15px; color: #3498db; font-size: 16px;">
                💬 Commentaires ({len(comments)})
            </h3>
            <ul style="margin: 0; padding: 0 0 0 20px; color: #ddd; font-size: 14px; line-height: 1.8;">
        """
        for notif in comments[:5]:
            comments_html += f'<li>{notif.get("message", "")}</li>'
        if len(comments) > 5:
            comments_html += f'<li style="color: #888;">...et {len(comments) - 5} autres</li>'
        comments_html += "</ul></div>"
        sections.append(comments_html)
    
    # Groups section
    if groups:
        groups_html = f"""
        <div style="margin-bottom: 25px; padding: 20px; background-color: #222; border-radius: 8px; border-left: 4px solid #9b59b6;">
            <h3 style="margin: 0 0 15px; color: #9b59b6; font-size: 16px;">
                👥 Activité des groupes ({len(groups)})
            </h3>
            <ul style="margin: 0; padding: 0 0 0 20px; color: #ddd; font-size: 14px; line-height: 1.8;">
        """
        for notif in groups[:5]:
            groups_html += f'<li>{notif.get("message", "")}</li>'
        if len(groups) > 5:
            groups_html += f'<li style="color: #888;">...et {len(groups) - 5} autres</li>'
        groups_html += "</ul></div>"
        sections.append(groups_html)
    
    # Referrals section
    if referrals:
        referrals_html = f"""
        <div style="margin-bottom: 25px; padding: 20px; background-color: #222; border-radius: 8px; border-left: 4px solid #f5a623;">
            <h3 style="margin: 0 0 15px; color: #f5a623; font-size: 16px;">
                🎁 Parrainages ({len(referrals)})
            </h3>
            <ul style="margin: 0; padding: 0 0 0 20px; color: #ddd; font-size: 14px; line-height: 1.8;">
        """
        for notif in referrals[:5]:
            referrals_html += f'<li>{notif.get("message", "")}</li>'
        referrals_html += "</ul></div>"
        sections.append(referrals_html)
    
    # Wallet section
    if wallet:
        wallet_html = f"""
        <div style="margin-bottom: 25px; padding: 20px; background-color: #222; border-radius: 8px; border-left: 4px solid #2ecc71;">
            <h3 style="margin: 0 0 15px; color: #2ecc71; font-size: 16px;">
                💰 Portefeuille ({len(wallet)})
            </h3>
            <ul style="margin: 0; padding: 0 0 0 20px; color: #ddd; font-size: 14px; line-height: 1.8;">
        """
        for notif in wallet[:5]:
            wallet_html += f'<li>{notif.get("message", "")}</li>'
        wallet_html += "</ul></div>"
        sections.append(wallet_html)
    
    # CTA Button
    cta = f"""
    <div style="text-align: center; margin-top: 30px;">
        <a href="{APP_URL}/network" style="display: inline-block; padding: 14px 30px; background-color: #f5a623; color: #000; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px;">
            Voir toutes mes notifications →
        </a>
    </div>
    """
    sections.append(cta)
    
    return ''.join(sections)


def generate_welcome_email(user_name: str, user_email: str = None, user_password: str = None, referral_code: str = None) -> str:
    """Generate welcome email for new users with login credentials"""
    
    content = f"""
    <h2 style="margin: 0 0 20px; color: #f5a623; font-size: 22px;">
        Bienvenue {user_name}! 🎉
    </h2>
    <p style="margin: 0 0 20px; color: #ccc; font-size: 15px; line-height: 1.6;">
        Merci de rejoindre la communauté {APP_NAME}! Nous sommes ravis de vous compter parmi nous.
    </p>
    """
    
    # Add login credentials section if provided
    if user_email and user_password:
        content += f"""
    <div style="margin: 25px 0; padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 8px; border: 1px solid #f5a623;">
        <h3 style="margin: 0 0 15px; color: #f5a623; font-size: 16px;">
            🔐 Vos identifiants de connexion
        </h3>
        <p style="margin: 0 0 10px; color: #aaa; font-size: 13px;">
            Conservez ces informations pour vous reconnecter facilement:
        </p>
        <table style="width: 100%; margin-top: 10px;">
            <tr>
                <td style="padding: 10px; background: #000; border-radius: 6px 6px 0 0; border-bottom: 1px solid #333;">
                    <span style="color: #888; font-size: 12px;">📧 Email:</span><br>
                    <span style="color: #fff; font-size: 15px; font-family: monospace;">{user_email}</span>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; background: #000; border-radius: 0 0 6px 6px;">
                    <span style="color: #888; font-size: 12px;">🔑 Mot de passe:</span><br>
                    <span style="color: #f5a623; font-size: 15px; font-family: monospace;">{user_password}</span>
                </td>
            </tr>
        </table>
        <p style="margin: 15px 0 0; color: #888; font-size: 11px; font-style: italic;">
            ⚠️ Pour votre sécurité, nous vous recommandons de supprimer cet email après avoir noté vos identifiants.
        </p>
    </div>
    """
    
    content += f"""
    <div style="margin: 25px 0; padding: 20px; background-color: #222; border-radius: 8px;">
        <h3 style="margin: 0 0 15px; color: #fff; font-size: 16px;">
            🚀 Commencez maintenant
        </h3>
        <ul style="margin: 0; padding: 0 0 0 20px; color: #ddd; font-size: 14px; line-height: 2;">
            <li>Explorez la carte interactive des territoires</li>
            <li>Partagez vos expériences de chasse</li>
            <li>Connectez-vous avec d'autres chasseurs</li>
            <li>Découvrez le Marketplace</li>
        </ul>
    </div>
    """
    
    if referral_code:
        content += f"""
        <div style="margin: 25px 0; padding: 20px; background: linear-gradient(135deg, #f5a623 0%, #d4891c 100%); border-radius: 8px;">
            <h3 style="margin: 0 0 10px; color: #000; font-size: 16px;">
                🎁 Parrainez vos amis!
            </h3>
            <p style="margin: 0 0 15px; color: #333; font-size: 14px;">
                Partagez votre code et gagnez des crédits!
            </p>
            <div style="background: #000; padding: 15px; border-radius: 6px; text-align: center;">
                <span style="font-size: 24px; font-family: monospace; color: #f5a623; letter-spacing: 3px;">
                    {referral_code}
                </span>
            </div>
        </div>
        """
    
    content += f"""
    <div style="text-align: center; margin-top: 30px;">
        <a href="{APP_URL}" style="display: inline-block; padding: 14px 30px; background-color: #f5a623; color: #000; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px;">
            Découvrir l'application →
        </a>
    </div>
    """
    
    return content


# ============================================
# EMAIL SENDING FUNCTIONS
# ============================================

async def send_email(to_email: str, subject: str, html_content: str) -> dict:
    """Send email using Resend API"""
    if not resend:
        logger.warning(f"Email not sent (Resend not configured): {subject} to {to_email}")
        return {"status": "skipped", "reason": "Resend not configured"}
    
    params = {
        "from": f"{APP_NAME} <{SENDER_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email_result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {subject}")
        return {
            "status": "success",
            "email_id": email_result.get("id"),
            "to": to_email
        }
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "to": to_email
        }


async def send_notification_digest(user_id: str, period: str = "daily") -> dict:
    """Send notification digest to a user"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user or not user.get("email"):
        return {"status": "skipped", "reason": "User not found or no email"}
    
    # Check user preferences
    prefs = await db.notification_preferences.find_one({"user_id": user_id}, {"_id": 0})
    if prefs and not prefs.get("email_notifications", True):
        return {"status": "skipped", "reason": "Email notifications disabled"}
    
    # Get unread notifications
    since = datetime.now(timezone.utc) - (timedelta(days=1) if period == "daily" else timedelta(days=7))
    notifications = await db.notifications.find({
        "user_id": user_id,
        "created_at": {"$gte": since.isoformat()}
    }, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    if not notifications:
        return {"status": "skipped", "reason": "No notifications"}
    
    # Generate email
    period_label = "quotidien" if period == "daily" else "hebdomadaire"
    content = generate_notification_digest_email(user.get("name", "Chasseur"), notifications, period_label)
    html = get_email_template(content, f"Vous avez {len(notifications)} nouvelles notifications")
    
    subject = f"📬 Votre résumé {period_label} - {len(notifications)} notification(s)"
    
    return await send_email(user["email"], subject, html)


async def send_welcome_email(user_id: str, user_email: str = None, user_password: str = None) -> dict:
    """Send welcome email to a new user with login credentials"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return {"status": "skipped", "reason": "User not found"}
    
    email = user_email or user.get("email")
    if not email:
        return {"status": "skipped", "reason": "No email"}
    
    # Get user's referral code
    referral = await db.referral_codes.find_one({"owner_id": user_id, "is_active": True}, {"_id": 0})
    referral_code = referral.get("code") if referral else None
    
    # Generate email with credentials
    content = generate_welcome_email(
        user_name=user.get("name", "Chasseur"),
        user_email=email,
        user_password=user_password,  # Will be None if not provided
        referral_code=referral_code
    )
    html = get_email_template(content, f"Bienvenue sur {APP_NAME}!")
    
    subject = f"🎉 Bienvenue sur {APP_NAME}, {user.get('name', 'Chasseur')}!"
    
    return await send_email(email, subject, html)


async def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> dict:
    """Send password reset email with link"""
    
    reset_url = f"{APP_URL}/reset-password?token={reset_token}"
    
    content = f"""
    <h2 style="margin: 0 0 20px; color: #f5a623; font-size: 22px;">
        Réinitialisation de mot de passe 🔐
    </h2>
    <p style="margin: 0 0 20px; color: #ccc; font-size: 15px; line-height: 1.6;">
        Bonjour {user_name},
    </p>
    <p style="margin: 0 0 20px; color: #ccc; font-size: 15px; line-height: 1.6;">
        Vous avez demandé la réinitialisation de votre mot de passe pour votre compte {APP_NAME}.
    </p>
    
    <div style="margin: 25px 0; padding: 20px; background-color: #222; border-radius: 8px; text-align: center;">
        <p style="margin: 0 0 15px; color: #fff;">Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe:</p>
        <a href="{reset_url}" style="display: inline-block; padding: 14px 30px; background-color: #f5a623; color: #000; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px;">
            Réinitialiser mon mot de passe →
        </a>
    </div>
    
    <div style="margin: 25px 0; padding: 15px; background-color: #1a1a1a; border-radius: 8px; border-left: 4px solid #f5a623;">
        <p style="margin: 0 0 10px; color: #888; font-size: 13px;">
            <strong style="color: #f5a623;">Ou copiez ce lien:</strong>
        </p>
        <p style="margin: 0; color: #aaa; font-size: 12px; word-break: break-all; font-family: monospace;">
            {reset_url}
        </p>
    </div>
    
    <p style="margin: 20px 0; color: #888; font-size: 13px;">
        ⚠️ Ce lien est valide pendant <strong>1 heure</strong>. Après ce délai, vous devrez faire une nouvelle demande.
    </p>
    
    <p style="margin: 20px 0; color: #666; font-size: 12px;">
        Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email. Votre mot de passe restera inchangé.
    </p>
    """
    
    html = get_email_template(content, "Réinitialisez votre mot de passe")
    subject = f"🔐 Réinitialisation de mot de passe - {APP_NAME}"
    
    return await send_email(user_email, subject, html)


async def send_password_changed_email(user_email: str, user_name: str, new_password: str = None) -> dict:
    """Send confirmation email after password change with new credentials"""
    
    content = f"""
    <h2 style="margin: 0 0 20px; color: #2ecc71; font-size: 22px;">
        Mot de passe modifié ✅
    </h2>
    <p style="margin: 0 0 20px; color: #ccc; font-size: 15px; line-height: 1.6;">
        Bonjour {user_name},
    </p>
    <p style="margin: 0 0 20px; color: #ccc; font-size: 15px; line-height: 1.6;">
        Votre mot de passe {APP_NAME} a été modifié avec succès.
    </p>
    """
    
    # Add new credentials if provided
    if new_password:
        content += f"""
    <div style="margin: 25px 0; padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 8px; border: 1px solid #2ecc71;">
        <h3 style="margin: 0 0 15px; color: #2ecc71; font-size: 16px;">
            🔐 Vos nouveaux identifiants
        </h3>
        <table style="width: 100%; margin-top: 10px;">
            <tr>
                <td style="padding: 10px; background: #000; border-radius: 6px 6px 0 0; border-bottom: 1px solid #333;">
                    <span style="color: #888; font-size: 12px;">📧 Email:</span><br>
                    <span style="color: #fff; font-size: 15px; font-family: monospace;">{user_email}</span>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; background: #000; border-radius: 0 0 6px 6px;">
                    <span style="color: #888; font-size: 12px;">🔑 Nouveau mot de passe:</span><br>
                    <span style="color: #2ecc71; font-size: 15px; font-family: monospace;">{new_password}</span>
                </td>
            </tr>
        </table>
        <p style="margin: 15px 0 0; color: #888; font-size: 11px; font-style: italic;">
            ⚠️ Pour votre sécurité, nous vous recommandons de supprimer cet email après avoir noté vos identifiants.
        </p>
    </div>
        """
    
    content += f"""
    <div style="margin: 25px 0; padding: 15px; background-color: #1a1a1a; border-radius: 8px;">
        <p style="margin: 0; color: #888; font-size: 13px;">
            Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement.
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 30px;">
        <a href="{APP_URL}" style="display: inline-block; padding: 14px 30px; background-color: #f5a623; color: #000; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px;">
            Se connecter →
        </a>
    </div>
    """
    
    html = get_email_template(content, "Votre mot de passe a été modifié")
    subject = f"✅ Mot de passe modifié - {APP_NAME}"
    
    return await send_email(user_email, subject, html)


# ============================================
# API ENDPOINTS
# ============================================

class EmailDigestRequest(BaseModel):
    user_id: str
    period: str = "daily"  # daily or weekly

class BulkDigestRequest(BaseModel):
    period: str = "daily"
    limit: int = 100

class TestEmailRequest(BaseModel):
    recipient_email: EmailStr
    subject: str = "Test Email"

@router.post("/send-digest")
async def api_send_digest(request: EmailDigestRequest, background_tasks: BackgroundTasks):
    """Send notification digest to a specific user"""
    result = await send_notification_digest(request.user_id, request.period)
    return result

@router.post("/send-welcome/{user_id}")
async def api_send_welcome(user_id: str):
    """Send welcome email to a user"""
    result = await send_welcome_email(user_id)
    return result


class WelcomeEmailWithCredentials(BaseModel):
    recipient_email: EmailStr
    user_name: str
    password: str


@router.post("/send-welcome-demo")
async def api_send_welcome_demo(request: WelcomeEmailWithCredentials):
    """Send a demo welcome email with credentials (for testing)"""
    
    # Generate email with credentials
    content = generate_welcome_email(
        user_name=request.user_name,
        user_email=request.recipient_email,
        user_password=request.password,
        referral_code="DEMO1234"
    )
    html = get_email_template(content, f"Bienvenue sur {APP_NAME}!")
    
    subject = f"🎉 Bienvenue sur {APP_NAME}, {request.user_name}!"
    
    return await send_email(request.recipient_email, subject, html)


@router.post("/send-bulk-digest")
async def api_send_bulk_digest(request: BulkDigestRequest, background_tasks: BackgroundTasks):
    """Send digest to all users with unread notifications (background task)"""
    
    # Get users with unread notifications
    since = datetime.now(timezone.utc) - (timedelta(days=1) if request.period == "daily" else timedelta(days=7))
    
    pipeline = [
        {"$match": {"created_at": {"$gte": since.isoformat()}, "is_read": False}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 0}}},
        {"$limit": request.limit}
    ]
    
    users_with_notifications = await db.notifications.aggregate(pipeline).to_list(request.limit)
    
    if not users_with_notifications:
        return {"status": "no_users", "message": "No users with unread notifications"}
    
    # Send digests in background
    async def send_all_digests():
        results = []
        for user_doc in users_with_notifications:
            result = await send_notification_digest(user_doc["_id"], request.period)
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Log results
        success = len([r for r in results if r.get("status") == "success"])
        logger.info(f"Bulk digest sent: {success}/{len(results)} successful")
    
    background_tasks.add_task(send_all_digests)
    
    return {
        "status": "processing",
        "users_queued": len(users_with_notifications),
        "period": request.period
    }

@router.post("/test")
async def api_send_test_email(request: TestEmailRequest):
    """Send a test email"""
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    content = f"""
    <h2 style="margin: 0 0 20px; color: #f5a623; font-size: 22px;">
        Test Email ✅
    </h2>
    <p style="margin: 0 0 20px; color: #ccc; font-size: 15px; line-height: 1.6;">
        Ceci est un email de test. Si vous recevez ce message, la configuration email fonctionne correctement!
    </p>
    <p style="margin: 0; color: #888; font-size: 13px;">
        Envoyé le: {now_str} UTC
    </p>
    """
    
    html = get_email_template(content, "Test email from BIONIC")
    
    return await send_email(request.recipient_email, request.subject, html)

@router.get("/config")
async def get_email_config():
    """Get email configuration status"""
    return {
        "resend_configured": bool(RESEND_API_KEY),
        "sender_email": SENDER_EMAIL if RESEND_API_KEY else "Not configured",
        "app_name": APP_NAME,
        "app_url": APP_URL
    }
