"""
WMS Proxy Router - Proxy pour les services WMS qui ne supportent pas CORS

Ce module permet de:
1. Proxifier les requêtes WMS depuis le frontend
2. Contourner les restrictions CORS des services gouvernementaux
3. Ajouter du cache pour les tuiles fréquemment demandées
4. Gérer les timeouts et retries de manière robuste
5. Logger les erreurs de manière structurée

Auteur: BIONIC™ Team
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import logging
from typing import Optional, Dict, Any
import hashlib
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wms-proxy", tags=["WMS Proxy"])

# Configuration robuste
WMS_CONFIG = {
    "timeout_seconds": 15,
    "max_retries": 3,
    "retry_delay_seconds": 1,
    "cache_duration_hours": 1,
    "max_cache_size": 500,
}

# Cache simple pour les tuiles WMS (en mémoire)
WMS_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_DURATION = timedelta(hours=WMS_CONFIG["cache_duration_hours"])
MAX_CACHE_SIZE = WMS_CONFIG["max_cache_size"]

# Tracking des erreurs par source (pour circuit breaker basique)
WMS_ERROR_TRACKING: Dict[str, Dict[str, Any]] = {}
ERROR_THRESHOLD = 5  # Nombre d'erreurs avant de marquer comme indisponible
ERROR_WINDOW = timedelta(minutes=10)  # Fenêtre de temps pour compter les erreurs

# Services WMS autorisés (whitelist)
ALLOWED_WMS_HOSTS = [
    "servicescarto.mern.gouv.qc.ca",
    "servicescarto.mffp.gouv.qc.ca",
    "ca.nfis.org",
    "geo.api.gov.bc.ca",
    "maps.geogratis.gc.ca",
    "hydro.nationalmap.gov",
    "geoegl.msp.gouv.qc.ca"
]

def is_host_allowed(url: str) -> bool:
    """Vérifie si l'hôte de l'URL est dans la whitelist"""
    for host in ALLOWED_WMS_HOSTS:
        if host in url:
            return True
    return False


def get_host_from_url(url: str) -> str:
    """Extrait l'hôte depuis une URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or "unknown"
    except Exception:
        return "unknown"


def get_cache_key(url: str, params: dict) -> str:
    """Génère une clé de cache unique pour la requête"""
    key_str = url + str(sorted(params.items()))
    return hashlib.md5(key_str.encode()).hexdigest()


def clean_cache():
    """Nettoie les entrées expirées du cache"""
    global WMS_CACHE
    now = datetime.now()
    expired_keys = [k for k, v in WMS_CACHE.items() if now - v['timestamp'] > CACHE_DURATION]
    for k in expired_keys:
        del WMS_CACHE[k]
    
    # Limiter la taille du cache
    if len(WMS_CACHE) > MAX_CACHE_SIZE:
        oldest_keys = sorted(WMS_CACHE.keys(), key=lambda k: WMS_CACHE[k]['timestamp'])[:100]
        for k in oldest_keys:
            del WMS_CACHE[k]


def track_error(host: str, error_type: str, error_message: str):
    """
    Enregistre une erreur pour un hôte WMS.
    Permet de détecter les sources instables.
    """
    global WMS_ERROR_TRACKING
    now = datetime.now()
    
    if host not in WMS_ERROR_TRACKING:
        WMS_ERROR_TRACKING[host] = {
            "errors": [],
            "last_success": None,
            "marked_unavailable": False
        }
    
    # Nettoyer les vieilles erreurs
    WMS_ERROR_TRACKING[host]["errors"] = [
        e for e in WMS_ERROR_TRACKING[host]["errors"]
        if now - e["timestamp"] < ERROR_WINDOW
    ]
    
    # Ajouter la nouvelle erreur
    WMS_ERROR_TRACKING[host]["errors"].append({
        "timestamp": now,
        "type": error_type,
        "message": error_message[:200]  # Limiter la taille
    })
    
    # Vérifier si on dépasse le seuil
    if len(WMS_ERROR_TRACKING[host]["errors"]) >= ERROR_THRESHOLD:
        WMS_ERROR_TRACKING[host]["marked_unavailable"] = True
        logger.warning(f"WMS source marked as unavailable: {host} ({len(WMS_ERROR_TRACKING[host]['errors'])} errors)")


def track_success(host: str):
    """Enregistre un succès pour un hôte WMS"""
    global WMS_ERROR_TRACKING
    if host in WMS_ERROR_TRACKING:
        WMS_ERROR_TRACKING[host]["last_success"] = datetime.now()
        WMS_ERROR_TRACKING[host]["marked_unavailable"] = False


def is_source_available(host: str) -> bool:
    """Vérifie si une source WMS est considérée comme disponible"""
    if host not in WMS_ERROR_TRACKING:
        return True
    
    tracking = WMS_ERROR_TRACKING[host]
    
    # Si marquée indisponible, vérifier si on peut réessayer (après 5 min)
    if tracking["marked_unavailable"]:
        if tracking["errors"]:
            last_error = tracking["errors"][-1]["timestamp"]
            if datetime.now() - last_error < timedelta(minutes=5):
                return False
            # Réinitialiser après 5 minutes
            tracking["marked_unavailable"] = False
    
    return True


async def fetch_wms_with_retry(
    wms_url: str,
    max_retries: int = WMS_CONFIG["max_retries"],
    timeout: int = WMS_CONFIG["timeout_seconds"]
) -> tuple[bytes, bool, str]:
    """
    Récupère une tuile WMS avec gestion des retries.
    
    Returns:
        tuple: (content, success, error_message)
    """
    import subprocess
    
    host = get_host_from_url(wms_url)
    last_error = ""
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ['curl', '-s', '-L', wms_url, '--connect-timeout', str(timeout)],
                capture_output=True,
                timeout=timeout + 5
            )
            
            if result.returncode == 0 and result.stdout:
                # Vérifier que c'est bien une image (pas une erreur XML)
                content = result.stdout
                if content[:4] == b'\x89PNG' or content[:2] in [b'\xff\xd8', b'GI']:
                    track_success(host)
                    return content, True, ""
                elif b'<ServiceException' in content or b'<ExceptionReport' in content:
                    last_error = "WMS service returned exception"
                    logger.warning(f"WMS exception on attempt {attempt+1}: {content[:200]}")
                else:
                    track_success(host)
                    return content, True, ""
            else:
                last_error = f"curl returned code {result.returncode}"
                
        except subprocess.TimeoutExpired:
            last_error = "timeout"
            logger.warning(f"WMS timeout on attempt {attempt+1}/{max_retries} for {host}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"WMS error on attempt {attempt+1}/{max_retries}: {e}")
        
        # Attendre avant le prochain retry
        if attempt < max_retries - 1:
            await asyncio.sleep(WMS_CONFIG["retry_delay_seconds"])
    
    # Tous les retries ont échoué
    track_error(host, "fetch_failed", last_error)
    return b"", False, last_error

@router.get("/tile")
async def proxy_wms_tile(
    url: str,
    service: str = "WMS",
    request: str = "GetMap",
    version: str = "1.3.0",
    layers: str = "0",
    styles: str = "",
    format: str = "image/png",
    transparent: str = "true",
    width: int = 256,
    height: int = 256,
    crs: str = "EPSG:4326",
    bbox: str = ""
):
    """
    Proxy une requête WMS GetMap avec gestion robuste des erreurs.
    
    Features:
    - Retries automatiques (3 tentatives)
    - Circuit breaker pour sources instables
    - Cache en mémoire
    - Logging structuré
    - Réponses JSON claires en cas d'erreur
    
    Returns:
        Image tile ou JSON avec détails de l'erreur
    """
    # Vérification de sécurité
    if not is_host_allowed(url):
        logger.warning(f"WMS host blocked: {url}")
        return JSONResponse(
            status_code=403,
            content={"error": "wms_host_not_allowed", "message": "Ce service WMS n'est pas autorisé", "url": url}
        )
    
    if not bbox:
        return JSONResponse(
            status_code=400,
            content={"error": "missing_bbox", "message": "Paramètre BBOX requis"}
        )
    
    host = get_host_from_url(url)
    
    # Vérifier le circuit breaker
    if not is_source_available(host):
        logger.info(f"WMS source temporarily unavailable (circuit breaker): {host}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "source_unavailable",
                "message": f"Le service {host} est temporairement indisponible",
                "retry_after_seconds": 300,
                "host": host
            }
        )
    
    # Construire l'URL complète
    wms_url = f"{url}?SERVICE={service}&REQUEST={request}&VERSION={version}&LAYERS={layers}&STYLES={styles}&FORMAT={format}&TRANSPARENT={transparent}&WIDTH={width}&HEIGHT={height}&CRS={crs}&BBOX={bbox}"
    
    # Vérifier le cache
    wms_params = {"url": wms_url}
    cache_key = get_cache_key(url, wms_params)
    if cache_key in WMS_CACHE:
        cached = WMS_CACHE[cache_key]
        if datetime.now() - cached['timestamp'] < CACHE_DURATION:
            logger.debug(f"WMS cache hit for {layers}")
            return Response(
                content=cached['data'],
                media_type=format,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=3600",
                    "X-WMS-Cache": "HIT"
                }
            )
    
    # Nettoyer le cache périodiquement
    if len(WMS_CACHE) > MAX_CACHE_SIZE * 0.9:
        clean_cache()
    
    # Récupérer la tuile avec retries
    content, success, error_message = await fetch_wms_with_retry(wms_url)
    
    if success and content:
        # Mettre en cache
        WMS_CACHE[cache_key] = {
            'data': content,
            'timestamp': datetime.now()
        }
        
        logger.debug(f"WMS proxy success: {layers} - {len(content)} bytes from {host}")
        
        return Response(
            content=content,
            media_type=format,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=3600",
                "X-WMS-Cache": "MISS",
                "X-WMS-Source": host
            }
        )
    else:
        # Échec après tous les retries
        logger.error(f"WMS proxy failed for {host}/{layers}: {error_message}")
        return JSONResponse(
            status_code=502,
            content={
                "error": "wms_fetch_failed",
                "message": "Impossible de récupérer la tuile après plusieurs tentatives",
                "details": error_message,
                "host": host,
                "layer": layers
            }
        )

@router.get("/capabilities")
async def proxy_wms_capabilities(url: str):
    """
    Proxy une requête WMS GetCapabilities avec gestion robuste.
    """
    if not is_host_allowed(url):
        return JSONResponse(
            status_code=403,
            content={"error": "wms_host_not_allowed", "message": "Ce service WMS n'est pas autorisé"}
        )
    
    host = get_host_from_url(url)
    
    # Vérifier le circuit breaker
    if not is_source_available(host):
        return JSONResponse(
            status_code=503,
            content={
                "error": "source_unavailable",
                "message": f"Le service {host} est temporairement indisponible",
                "retry_after_seconds": 300
            }
        )
    
    try:
        async with httpx.AsyncClient(timeout=WMS_CONFIG["timeout_seconds"]) as client:
            params = {
                "SERVICE": "WMS",
                "REQUEST": "GetCapabilities",
                "VERSION": "1.3.0"
            }
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            track_success(host)
            
            return Response(
                content=response.content,
                media_type="application/xml",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "X-WMS-Source": host
                }
            )
            
    except httpx.TimeoutException:
        track_error(host, "timeout", "GetCapabilities timeout")
        return JSONResponse(
            status_code=504,
            content={"error": "timeout", "message": "Le service WMS n'a pas répondu à temps"}
        )
    except Exception as e:
        track_error(host, "error", str(e))
        logger.error(f"WMS capabilities proxy error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": "fetch_failed", "message": str(e)}
        )

@router.get("/check")
async def check_wms_availability(url: str):
    """
    Vérifie la disponibilité d'un service WMS avec retries.
    
    Returns:
        JSON avec statut de disponibilité et métriques
    """
    logger.info(f"Checking WMS availability for: {url}")
    
    if not is_host_allowed(url):
        logger.warning(f"WMS host not allowed: {url}")
        return {"available": False, "error": "host_not_allowed", "message": "Ce service WMS n'est pas autorisé"}
    
    host = get_host_from_url(url)
    
    try:
        import time
        import subprocess
        
        start_time = time.time()
        
        # Utiliser curl en subprocess avec timeout réduit pour le check
        result = subprocess.run(
            [
                'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                f"{url}?SERVICE=WMS&REQUEST=GetCapabilities&VERSION=1.3.0",
                '--connect-timeout', '10'
            ],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        status_code = int(result.stdout) if result.stdout.isdigit() else 0
        
        logger.info(f"WMS check response: host={host}, status={status_code}, time={elapsed_ms}ms")
        
        is_available = status_code == 200
        
        if is_available:
            track_success(host)
        else:
            track_error(host, "check_failed", f"HTTP {status_code}")
        
        return {
            "available": is_available,
            "host": host,
            "status_code": status_code,
            "response_time_ms": elapsed_ms,
            "circuit_breaker_status": "open" if not is_source_available(host) else "closed"
        }
            
    except subprocess.TimeoutExpired:
        track_error(host, "timeout", "Check timeout")
        logger.warning(f"WMS check timeout for {host}")
        return {
            "available": False,
            "host": host,
            "error": "timeout",
            "message": "Le service n'a pas répondu dans les délais"
        }
    except Exception as e:
        track_error(host, "error", str(e))
        logger.error(f"WMS check error: {type(e).__name__}: {e}")
        return {
            "available": False,
            "host": host,
            "error": "check_error",
            "message": str(e)
        }


@router.get("/status")
async def get_wms_status():
    """
    Retourne le statut de santé de tous les services WMS trackés.
    
    Utile pour:
    - Monitoring administratif
    - Debug des problèmes de couches
    - Visualisation des sources instables
    """
    status = {
        "allowed_hosts": ALLOWED_WMS_HOSTS,
        "cache_size": len(WMS_CACHE),
        "max_cache_size": MAX_CACHE_SIZE,
        "sources": {}
    }
    
    for host in ALLOWED_WMS_HOSTS:
        tracking = WMS_ERROR_TRACKING.get(host, {})
        recent_errors = tracking.get("errors", [])
        
        status["sources"][host] = {
            "available": is_source_available(host),
            "recent_errors_count": len(recent_errors),
            "last_success": tracking.get("last_success").isoformat() if tracking.get("last_success") else None,
            "marked_unavailable": tracking.get("marked_unavailable", False)
        }
    
    return status


@router.post("/reset-circuit-breaker")
async def reset_circuit_breaker(host: str = None):
    """
    Réinitialise le circuit breaker pour un hôte spécifique ou tous les hôtes.
    
    Args:
        host: Hôte spécifique à réinitialiser (optionnel, tous si non spécifié)
    """
    global WMS_ERROR_TRACKING
    
    if host:
        if host in WMS_ERROR_TRACKING:
            WMS_ERROR_TRACKING[host] = {
                "errors": [],
                "last_success": None,
                "marked_unavailable": False
            }
            logger.info(f"Circuit breaker reset for {host}")
            return {"success": True, "message": f"Circuit breaker réinitialisé pour {host}"}
        else:
            return {"success": False, "message": f"Hôte {host} non trouvé dans le tracking"}
    else:
        WMS_ERROR_TRACKING = {}
        logger.info("All circuit breakers reset")
        return {"success": True, "message": "Tous les circuit breakers ont été réinitialisés"}

logger.info('WMS Proxy Router initialized with robust error handling')
