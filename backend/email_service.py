# email_service.py - Service d'envoi d'emails avec Resend
import os
import logging
from typing import List, Optional

# Resend is optional - emails will be logged if not configured
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'SCENT SCIENCE™ <noreply@scentscience.com>')

def is_email_configured() -> bool:
    """Vérifie si le service email est configuré"""
    return RESEND_AVAILABLE and bool(RESEND_API_KEY)

def init_resend():
    """Initialise Resend avec la clé API"""
    if RESEND_AVAILABLE and RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
        return True
    return False

async def send_cancellation_email(
    to_email: str,
    customer_name: str,
    products: List[str],
    order_id: str
) -> dict:
    """
    Envoie un email d'annulation de commande
    
    Args:
        to_email: Email du client
        customer_name: Nom du client
        products: Liste des noms de produits
        order_id: ID de la commande
    
    Returns:
        dict avec status et message
    """
    
    # Construire la liste des produits HTML
    products_html = "".join([f"<li style='margin: 5px 0; color: #333;'>{product}</li>" for product in products])
    products_text = "\n".join([f"• {product}" for product in products])
    
    # Template HTML de l'email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; }}
            .header h1 {{ color: #f5a623; margin: 0; font-size: 24px; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .products-list {{ background: #fff; padding: 15px 25px; border-left: 4px solid #f5a623; margin: 20px 0; }}
            .footer {{ background: #1a1a2e; color: #888; padding: 20px; text-align: center; font-size: 12px; }}
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SCENT SCIENCE™ Laboratory</h1>
            </div>
            <div class="content">
                <p>Bonjour <strong>{customer_name}</strong>,</p>
                
                <p>Nous vous remercions pour votre commande et la confiance que vous nous accordez.</p>
                
                <p>Malheureusement, nous ne serons pas en mesure d'acheminer les produits suivants :</p>
                
                <div class="products-list">
                    <ul style="margin: 0; padding-left: 20px;">
                        {products_html}
                    </ul>
                </div>
                
                <p>Nous nous excusons pour ce contretemps et restons à votre disposition pour vous proposer des alternatives ou convenir d'une solution adaptée à vos besoins.</p>
                
                <p>N'hésitez pas à nous contacter pour toute question ou assistance.</p>
                
                <div class="signature">
                    <p>Cordialement,</p>
                    <p><strong>L'équipe SCENT SCIENCE™</strong></p>
                </div>
            </div>
            <div class="footer">
                <p>Référence commande: {order_id}</p>
                <p>© 2024 SCENT SCIENCE™ Laboratory - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Version texte de l'email
    text_content = f"""
Bonjour {customer_name},

Nous vous remercions pour votre commande et la confiance que vous nous accordez.

Malheureusement, nous ne serons pas en mesure d'acheminer les produits suivants :

{products_text}

Nous nous excusons pour ce contretemps et restons à votre disposition pour vous proposer des alternatives ou convenir d'une solution adaptée à vos besoins.

N'hésitez pas à nous contacter pour toute question ou assistance.

Cordialement,
L'équipe SCENT SCIENCE™

---
Référence commande: {order_id}
    """
    
    # Si Resend n'est pas configuré, logger l'email
    if not is_email_configured():
        logger.warning(f"Email service not configured. Would have sent cancellation email to {to_email}")
        logger.info(f"Email content:\n{text_content}")
        return {
            "status": "simulated",
            "message": f"Email simulé envoyé à {to_email} (service non configuré)",
            "to": to_email,
            "subject": "Annulation de votre commande - SCENT SCIENCE™"
        }
    
    try:
        init_resend()
        
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": "Annulation de votre commande - SCENT SCIENCE™",
            "html": html_content,
            "text": text_content
        }
        
        email_response = resend.Emails.send(params)
        
        logger.info(f"Cancellation email sent successfully to {to_email}")
        return {
            "status": "sent",
            "message": f"Email d'annulation envoyé à {to_email}",
            "to": to_email,
            "email_id": email_response.get("id") if isinstance(email_response, dict) else str(email_response)
        }
        
    except Exception as e:
        logger.error(f"Failed to send cancellation email: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de l'envoi: {str(e)}",
            "to": to_email
        }

async def send_analysis_report_email(
    to_email: str,
    customer_name: str,
    product_name: str,
    score: float,
    report_summary: str,
    report_id: str
) -> dict:
    """
    Envoie un rapport d'analyse par email
    """
    
    # Déterminer la couleur du score
    if score >= 7.5:
        score_color = "#22c55e"
        score_label = "Attraction forte"
    elif score >= 5:
        score_color = "#eab308"
        score_label = "Attraction modérée"
    else:
        score_color = "#ef4444"
        score_label = "Attraction faible"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; }}
            .header h1 {{ color: #f5a623; margin: 0; font-size: 24px; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .score-box {{ background: #fff; padding: 20px; text-align: center; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .score {{ font-size: 48px; font-weight: bold; color: {score_color}; }}
            .footer {{ background: #1a1a2e; color: #888; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SCENT SCIENCE™ Laboratory</h1>
                <p style="color: #888; margin-top: 10px;">Rapport d'analyse scientifique</p>
            </div>
            <div class="content">
                <p>Bonjour <strong>{customer_name}</strong>,</p>
                
                <p>Voici votre rapport d'analyse pour le produit <strong>{product_name}</strong>.</p>
                
                <div class="score-box">
                    <p style="margin: 0; color: #666;">Score d'attraction</p>
                    <p class="score">{score}/10</p>
                    <p style="margin: 0; color: {score_color}; font-weight: bold;">{score_label}</p>
                </div>
                
                <h3>Résumé de l'analyse:</h3>
                <p>{report_summary}</p>
                
                <p style="margin-top: 30px;">
                    <a href="#" style="background: #f5a623; color: #000; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Voir le rapport complet
                    </a>
                </p>
            </div>
            <div class="footer">
                <p>Référence rapport: {report_id}</p>
                <p>© 2024 SCENT SCIENCE™ Laboratory - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    if not is_email_configured():
        logger.warning(f"Email service not configured. Would have sent report to {to_email}")
        return {
            "status": "simulated",
            "message": f"Email simulé envoyé à {to_email} (service non configuré)",
            "to": to_email
        }
    
    try:
        init_resend()
        
        params = {
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": f"Rapport d'analyse: {product_name} - SCENT SCIENCE™",
            "html": html_content
        }
        
        email_response = resend.Emails.send(params)
        
        return {
            "status": "sent",
            "message": f"Rapport envoyé à {to_email}",
            "to": to_email,
            "email_id": email_response.get("id") if isinstance(email_response, dict) else str(email_response)
        }
        
    except Exception as e:
        logger.error(f"Failed to send report email: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de l'envoi: {str(e)}",
            "to": to_email
        }
