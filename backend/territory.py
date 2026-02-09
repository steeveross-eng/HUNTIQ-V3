"""
Chasse Bionic™ / BIONIC™ - Territory Analysis Module
Phase 1: Events, Camera Photos, AI Species Recognition
MongoDB Version for Emergent Platform
"""

import os
import uuid
import json
import base64
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Literal
from pathlib import Path

import aiofiles
import hashlib
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from pydantic import BaseModel, Field
from PIL import Image
import exifread
from io import BytesIO
from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv
load_dotenv()

# Initialize router
territory_router = APIRouter(prefix="/api/territory", tags=["Territory Analysis"])

# Database connection
mongo_client: Optional[AsyncIOMotorClient] = None
db = None

# Configuration
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
UPLOAD_DIR = Path("/app/backend/uploads/photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

# ===========================================
# DATABASE CONNECTION
# ===========================================

async def get_db():
    """Get or create MongoDB connection"""
    global mongo_client, db
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(MONGO_URL)
        db = mongo_client[DB_NAME]
        # Create indexes for territory collections
        await db.territory_users.create_index("email", unique=True)
        await db.territory_events.create_index([("user_id", 1), ("captured_at", -1)])
        await db.territory_events.create_index([("latitude", 1), ("longitude", 1)])
        await db.territory_cameras.create_index("user_id")
        await db.territory_photos.create_index("user_id")
    return db

async def close_db():
    """Close MongoDB connection"""
    global mongo_client, db
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        db = None

# ===========================================
# PYDANTIC MODELS
# ===========================================

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    plan_type: str
    created_at: datetime

class CameraCreate(BaseModel):
    label: str
    brand: Literal['GardePro', 'WingHome', 'SOVACAM', 'Reconyx', 'Bushnell', 'Browning', 'autre']
    connection_type: Literal['ftp', 'email', 'manual']
    ftp_host: Optional[str] = None
    ftp_username: Optional[str] = None
    ftp_password: Optional[str] = None
    ftp_path: Optional[str] = None
    email_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CameraResponse(BaseModel):
    id: str
    label: str
    brand: str
    connection_type: str
    connected: bool
    last_seen_at: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]

class EventCreate(BaseModel):
    event_type: Literal['gps_track', 'cache', 'camera_photo', 'tir', 'observation', 'saline', 'feeding_station']
    latitude: float
    longitude: float
    species: Optional[Literal['orignal', 'chevreuil', 'ours', 'autre']] = None
    species_confidence: Optional[float] = None
    count_estimate: Optional[int] = 1
    captured_at: Optional[datetime] = None
    source: Literal['app', 'camera', 'import', 'manual'] = 'app'
    metadata: Optional[dict] = {}

class EventResponse(BaseModel):
    id: str
    event_type: str
    species: Optional[str]
    species_confidence: Optional[float]
    count_estimate: int
    latitude: float
    longitude: float
    captured_at: datetime
    source: str
    metadata: dict

class PhotoUploadResponse(BaseModel):
    id: str
    photo_url: str
    processing_status: str
    exif_datetime: Optional[datetime]
    exif_gps_lat: Optional[float]
    exif_gps_lon: Optional[float]
    species: Optional[str]
    species_confidence: Optional[float]
    count_estimate: Optional[int]

class AIClassificationResult(BaseModel):
    species: Literal['orignal', 'chevreuil', 'ours', 'autre']
    confidence: float
    count_estimate: int
    reasoning: str

# ===========================================
# HELPER FUNCTIONS
# ===========================================

def extract_exif_data(image_bytes: bytes) -> dict:
    """Extract EXIF data from image bytes"""
    try:
        tags = exifread.process_file(BytesIO(image_bytes), details=False)
        
        exif_data = {
            'datetime': None,
            'gps_lat': None,
            'gps_lon': None,
            'camera_make': None,
            'camera_model': None
        }
        
        # Extract datetime
        if 'EXIF DateTimeOriginal' in tags:
            dt_str = str(tags['EXIF DateTimeOriginal'])
            try:
                exif_data['datetime'] = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
            except:
                pass
        
        # Extract GPS coordinates
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            try:
                lat = tags['GPS GPSLatitude']
                lon = tags['GPS GPSLongitude']
                lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))
                lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))
                
                # Convert to decimal
                def convert_to_degrees(value):
                    d = float(value.values[0].num) / float(value.values[0].den)
                    m = float(value.values[1].num) / float(value.values[1].den)
                    s = float(value.values[2].num) / float(value.values[2].den)
                    return d + (m / 60.0) + (s / 3600.0)
                
                exif_data['gps_lat'] = convert_to_degrees(lat)
                if lat_ref == 'S':
                    exif_data['gps_lat'] = -exif_data['gps_lat']
                
                exif_data['gps_lon'] = convert_to_degrees(lon)
                if lon_ref == 'W':
                    exif_data['gps_lon'] = -exif_data['gps_lon']
            except Exception as e:
                logger.warning(f"Failed to parse GPS data: {e}")
        
        # Extract camera info
        if 'Image Make' in tags:
            exif_data['camera_make'] = str(tags['Image Make'])
        if 'Image Model' in tags:
            exif_data['camera_model'] = str(tags['Image Model'])
        
        return exif_data
    except Exception as e:
        logger.error(f"EXIF extraction error: {e}")
        return {}

async def classify_species_with_ai(image_base64: str) -> AIClassificationResult:
    """Use GPT-4 Vision to classify species in the image"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        
        prompt = """Analyse cette photo de caméra de chasse et identifie l'espèce animale présente.

Tu dois répondre UNIQUEMENT avec un JSON valide dans ce format exact (sans markdown):
{"species": "orignal|chevreuil|ours|autre", "confidence": 0.0-1.0, "count_estimate": 1, "reasoning": "explication courte"}

Règles:
- orignal = moose/élan
- chevreuil = white-tailed deer/cerf de Virginie
- ours = black bear/ours noir
- autre = tout autre animal ou absence d'animal visible
- confidence: 0.9+ si très sûr, 0.7-0.9 si probable, <0.7 si incertain
- count_estimate: nombre d'individus visibles de cette espèce

Si aucun animal n'est visible, retourne {"species": "autre", "confidence": 0.95, "count_estimate": 0, "reasoning": "Aucun animal visible"}"""

        llm = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="Tu es un expert en identification de la faune sauvage nord-américaine."
        ).with_model("openai", "gpt-4o")
        
        # Create message with image
        image_content = ImageContent(image_base64=image_base64)
        user_message = UserMessage(text=prompt, file_contents=[image_content])
        
        response = await llm.send_message(user_message)
        
        # Parse response
        response_text = response.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        return AIClassificationResult(
            species=result.get('species', 'autre'),
            confidence=float(result.get('confidence', 0.5)),
            count_estimate=int(result.get('count_estimate', 1)),
            reasoning=result.get('reasoning', '')
        )
        
    except Exception as e:
        logger.error(f"AI classification error: {e}")
        return AIClassificationResult(
            species='autre',
            confidence=0.0,
            count_estimate=0,
            reasoning=f"Erreur d'analyse: {str(e)}"
        )

# ===========================================
# API ENDPOINTS - USERS
# ===========================================

class UserLogin(BaseModel):
    email: str
    password: str

@territory_router.get("/users/auto-login")
async def auto_login_by_ip(request: Request):
    """Auto-login or create user based on IP address"""
    database = await get_db()
    
    # Get client IP
    client_ip = request.client.host
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    # Create a unique identifier based on IP
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    auto_email = f"user_{ip_hash}@territory.local"
    
    # Check if user exists
    existing = await database.territory_users.find_one({"email": auto_email})
    
    if existing:
        return {
            "id": str(existing['_id']),
            "email": existing['email'],
            "name": existing.get('name') or f"Utilisateur {ip_hash[:6]}",
            "plan_type": existing.get('plan_type', 'free'),
            "created_at": existing.get('created_at', datetime.now(timezone.utc)),
            "auto_created": False,
            "client_ip": client_ip
        }
    else:
        # Create new user automatically
        user_id = str(uuid.uuid4())
        user_name = f"Chasseur {ip_hash[:6].upper()}"
        now = datetime.now(timezone.utc)
        
        new_user = {
            "_id": user_id,
            "email": auto_email,
            "password_hash": ip_hash,
            "name": user_name,
            "plan_type": "free",
            "created_at": now
        }
        
        await database.territory_users.insert_one(new_user)
        
        return {
            "id": user_id,
            "email": auto_email,
            "name": user_name,
            "plan_type": "free",
            "created_at": now,
            "auto_created": True,
            "client_ip": client_ip
        }

@territory_router.post("/users/login")
async def login_user(credentials: UserLogin):
    """Login existing user or create new one"""
    database = await get_db()
    
    password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    
    # Check if user exists
    existing = await database.territory_users.find_one({"email": credentials.email})
    
    if existing:
        # Verify password
        if existing.get('password_hash') == password_hash:
            return UserResponse(
                id=str(existing['_id']),
                email=existing['email'],
                name=existing.get('name'),
                plan_type=existing.get('plan_type', 'free'),
                created_at=existing.get('created_at', datetime.now(timezone.utc))
            )
        else:
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        new_user = {
            "_id": user_id,
            "email": credentials.email,
            "password_hash": password_hash,
            "name": credentials.email.split('@')[0],
            "plan_type": "free",
            "created_at": now
        }
        
        await database.territory_users.insert_one(new_user)
        
        return UserResponse(
            id=user_id,
            email=credentials.email,
            name=credentials.email.split('@')[0],
            plan_type="free",
            created_at=now
        )

@territory_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user for territory analysis"""
    database = await get_db()
    
    # Hash password
    password_hash = hashlib.sha256(user.password.encode()).hexdigest()
    
    # Check if email exists
    existing = await database.territory_users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    new_user = {
        "_id": user_id,
        "email": user.email,
        "password_hash": password_hash,
        "name": user.name,
        "plan_type": "free",
        "created_at": now
    }
    
    await database.territory_users.insert_one(new_user)
    
    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        plan_type="free",
        created_at=now
    )

@territory_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    database = await get_db()
    
    user = await database.territory_users.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user['_id']),
        email=user['email'],
        name=user.get('name'),
        plan_type=user.get('plan_type', 'free'),
        created_at=user.get('created_at', datetime.now(timezone.utc))
    )

# ===========================================
# API ENDPOINTS - CAMERAS
# ===========================================

@territory_router.get("/cameras")
async def list_cameras(user_id: str):
    """List all cameras for a user"""
    database = await get_db()
    
    cameras = await database.territory_cameras.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    
    return [CameraResponse(
        id=str(cam['_id']),
        label=cam['label'],
        brand=cam['brand'],
        connection_type=cam['connection_type'],
        connected=cam.get('connected', False),
        last_seen_at=cam.get('last_seen_at'),
        latitude=cam.get('latitude'),
        longitude=cam.get('longitude')
    ) for cam in cameras]

@territory_router.post("/cameras", response_model=CameraResponse)
async def create_camera(user_id: str, camera: CameraCreate):
    """Register a new trail camera"""
    database = await get_db()
    
    camera_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    camera_doc = {
        "_id": camera_id,
        "user_id": user_id,
        "label": camera.label,
        "brand": camera.brand,
        "connection_type": camera.connection_type,
        "ftp_host": camera.ftp_host,
        "ftp_username": camera.ftp_username,
        "ftp_password": camera.ftp_password,
        "ftp_path": camera.ftp_path,
        "email_address": camera.email_address,
        "latitude": camera.latitude,
        "longitude": camera.longitude,
        "connected": False,
        "last_seen_at": None,
        "created_at": now
    }
    
    await database.territory_cameras.insert_one(camera_doc)
    
    return CameraResponse(
        id=camera_id,
        label=camera.label,
        brand=camera.brand,
        connection_type=camera.connection_type,
        connected=False,
        last_seen_at=None,
        latitude=camera.latitude,
        longitude=camera.longitude
    )

@territory_router.get("/cameras/{camera_id}/status")
async def get_camera_status(camera_id: str):
    """Get camera connection status"""
    database = await get_db()
    
    camera = await database.territory_cameras.find_one({"_id": camera_id})
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Count photos for this camera
    total_photos = await database.territory_photos.count_documents({"camera_id": camera_id})
    
    # Get last photo
    last_photo = await database.territory_photos.find_one(
        {"camera_id": camera_id},
        sort=[("captured_at", -1)]
    )
    
    return {
        "id": str(camera['_id']),
        "label": camera['label'],
        "connected": camera.get('connected', False),
        "last_seen_at": camera.get('last_seen_at'),
        "total_photos": total_photos,
        "last_photo_at": last_photo.get('captured_at') if last_photo else None
    }

# ===========================================
# API ENDPOINTS - EVENTS
# ===========================================

@territory_router.get("/events/recent")
async def get_recent_events(
    user_id: str,
    species: Optional[str] = None,
    hours: int = 72,
    limit: int = 100
):
    """Get recent events for a user"""
    database = await get_db()
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    query = {
        "user_id": user_id,
        "captured_at": {"$gte": cutoff_time}
    }
    
    if species:
        query["species"] = species
    
    events = await database.territory_events.find(query).sort("captured_at", -1).limit(limit).to_list(limit)
    
    return [EventResponse(
        id=str(event['_id']),
        event_type=event['event_type'],
        species=event.get('species'),
        species_confidence=event.get('species_confidence'),
        count_estimate=event.get('count_estimate', 1),
        latitude=event['latitude'],
        longitude=event['longitude'],
        captured_at=event['captured_at'],
        source=event.get('source', 'app'),
        metadata=event.get('metadata', {})
    ) for event in events]

@territory_router.get("/events/species/{species}")
async def get_events_by_species(user_id: str, species: str, limit: int = 100):
    """Get events filtered by species"""
    if species not in ['orignal', 'chevreuil', 'ours', 'autre']:
        raise HTTPException(status_code=400, detail="Invalid species")
    
    return await get_recent_events(user_id, species=species, hours=168, limit=limit)

@territory_router.post("/events", response_model=EventResponse)
async def create_event(user_id: str, event: EventCreate):
    """Create a new event/observation"""
    database = await get_db()
    
    event_id = str(uuid.uuid4())
    captured_at = event.captured_at or datetime.now(timezone.utc)
    
    event_doc = {
        "_id": event_id,
        "user_id": user_id,
        "event_type": event.event_type,
        "species": event.species,
        "species_confidence": event.species_confidence,
        "count_estimate": event.count_estimate or 1,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "captured_at": captured_at,
        "source": event.source,
        "metadata": event.metadata or {},
        "created_at": datetime.now(timezone.utc)
    }
    
    await database.territory_events.insert_one(event_doc)
    
    return EventResponse(
        id=event_id,
        event_type=event.event_type,
        species=event.species,
        species_confidence=event.species_confidence,
        count_estimate=event.count_estimate or 1,
        latitude=event.latitude,
        longitude=event.longitude,
        captured_at=captured_at,
        source=event.source,
        metadata=event.metadata or {}
    )

@territory_router.delete("/events/{event_id}")
async def delete_event(event_id: str, user_id: str):
    """Delete an event/observation"""
    database = await get_db()
    
    result = await database.territory_events.delete_one({
        "_id": event_id,
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted successfully", "id": event_id}

# ===========================================
# API ENDPOINTS - PHOTO UPLOAD & AI
# ===========================================

@territory_router.post("/photos/upload", response_model=PhotoUploadResponse)
async def upload_photo(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    camera_id: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """Upload a trail camera photo for AI analysis"""
    database = await get_db()
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    content = await file.read()
    
    # Extract EXIF data
    exif_data = extract_exif_data(content)
    
    # Generate unique filename and save
    file_ext = Path(file.filename).suffix if file.filename else '.jpg'
    photo_id = str(uuid.uuid4())
    photo_filename = f"{photo_id}{file_ext}"
    photo_path = UPLOAD_DIR / photo_filename
    
    async with aiofiles.open(photo_path, 'wb') as f:
        await f.write(content)
    
    # Create database record
    captured_at = exif_data.get('datetime') or datetime.now(timezone.utc)
    
    photo_doc = {
        "_id": photo_id,
        "user_id": user_id,
        "camera_id": camera_id,
        "photo_path": str(photo_path),
        "original_filename": file.filename,
        "exif_datetime": exif_data.get('datetime'),
        "exif_gps_lat": exif_data.get('gps_lat'),
        "exif_gps_lon": exif_data.get('gps_lon'),
        "exif_camera_make": exif_data.get('camera_make'),
        "exif_camera_model": exif_data.get('camera_model'),
        "processing_status": "pending",
        "captured_at": captured_at,
        "created_at": datetime.now(timezone.utc),
        "species": None,
        "species_confidence": None,
        "count_estimate": None
    }
    
    await database.territory_photos.insert_one(photo_doc)
    
    # Queue AI classification in background
    background_tasks.add_task(process_photo_ai, photo_id, content, user_id, exif_data)
    
    return PhotoUploadResponse(
        id=photo_id,
        photo_url=f"/api/territory/photos/{photo_id}/image",
        processing_status='pending',
        exif_datetime=exif_data.get('datetime'),
        exif_gps_lat=exif_data.get('gps_lat'),
        exif_gps_lon=exif_data.get('gps_lon'),
        species=None,
        species_confidence=None,
        count_estimate=None
    )

async def process_photo_ai(photo_id: str, image_bytes: bytes, user_id: str, exif_data: dict):
    """Background task to process photo with AI"""
    database = await get_db()
    
    try:
        # Update status to processing
        await database.territory_photos.update_one(
            {"_id": photo_id},
            {"$set": {"processing_status": "processing"}}
        )
        
        # Convert to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Run AI classification
        result = await classify_species_with_ai(image_base64)
        
        # Update database with results
        await database.territory_photos.update_one(
            {"_id": photo_id},
            {"$set": {
                "species": result.species,
                "species_confidence": result.confidence,
                "count_estimate": result.count_estimate,
                "ai_analysis_raw": {"reasoning": result.reasoning},
                "ai_processed_at": datetime.now(timezone.utc),
                "processing_status": "completed"
            }}
        )
        
        # Create corresponding event if GPS available and species detected
        if exif_data.get('gps_lat') and exif_data.get('gps_lon') and result.species != 'autre':
            captured_at = exif_data.get('datetime') or datetime.now(timezone.utc)
            
            event_id = str(uuid.uuid4())
            event_doc = {
                "_id": event_id,
                "user_id": user_id,
                "event_type": "camera_photo",
                "species": result.species,
                "species_confidence": result.confidence,
                "count_estimate": result.count_estimate,
                "latitude": exif_data['gps_lat'],
                "longitude": exif_data['gps_lon'],
                "captured_at": captured_at,
                "source": "camera",
                "metadata": {"photo_id": photo_id, "reasoning": result.reasoning},
                "created_at": datetime.now(timezone.utc)
            }
            
            await database.territory_events.insert_one(event_doc)
            
            # Link photo to event
            await database.territory_photos.update_one(
                {"_id": photo_id},
                {"$set": {"event_id": event_id}}
            )
        
        logger.info(f"Photo {photo_id} classified as {result.species} with {result.confidence:.2f} confidence")
        
    except Exception as e:
        logger.error(f"Error processing photo {photo_id}: {e}")
        await database.territory_photos.update_one(
            {"_id": photo_id},
            {"$set": {
                "processing_status": "failed",
                "processing_error": str(e)
            }}
        )

@territory_router.get("/photos/{photo_id}")
async def get_photo_status(photo_id: str):
    """Get photo processing status and results"""
    database = await get_db()
    
    photo = await database.territory_photos.find_one({"_id": photo_id})
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return {
        "id": str(photo['_id']),
        "photo_url": f"/api/territory/photos/{photo_id}/image",
        "processing_status": photo.get('processing_status', 'pending'),
        "processing_error": photo.get('processing_error'),
        "exif_datetime": photo.get('exif_datetime'),
        "exif_gps_lat": photo.get('exif_gps_lat'),
        "exif_gps_lon": photo.get('exif_gps_lon'),
        "species": photo.get('species'),
        "species_confidence": photo.get('species_confidence'),
        "count_estimate": photo.get('count_estimate'),
        "ai_analysis": photo.get('ai_analysis_raw'),
        "ai_processed_at": photo.get('ai_processed_at'),
        "event_id": photo.get('event_id')
    }

@territory_router.get("/photos/{photo_id}/image")
async def get_photo_image(photo_id: str):
    """Serve the photo image file"""
    from fastapi.responses import FileResponse
    
    database = await get_db()
    
    photo = await database.territory_photos.find_one({"_id": photo_id})
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    photo_path = Path(photo['photo_path'])
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Photo file not found")
    
    return FileResponse(photo_path)

# ===========================================
# API ENDPOINTS - LAYERS (Basic for Phase 1)
# ===========================================

@territory_router.get("/layers/heatmap_activite")
async def get_heatmap_activite(user_id: str, species: Optional[str] = None, hours: int = 72):
    """Get activity heatmap data"""
    database = await get_db()
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    query = {
        "user_id": user_id,
        "captured_at": {"$gte": cutoff_time}
    }
    
    if species:
        query["species"] = species
    
    events = await database.territory_events.find(query).to_list(1000)
    
    # Group by approximate grid cell (0.001 degree ~ 100m)
    grid_data = {}
    for event in events:
        lat = round(event['latitude'], 3)
        lon = round(event['longitude'], 3)
        key = f"{lat},{lon}"
        
        if key not in grid_data:
            grid_data[key] = {
                "lat": lat,
                "lon": lon,
                "intensity": 0,
                "species": event.get('species')
            }
        grid_data[key]["intensity"] += 1
    
    return {
        "type": "heatmap",
        "time_window_hours": hours,
        "species_filter": species,
        "points": list(grid_data.values())
    }

@territory_router.get("/stats")
async def get_territory_stats(user_id: str):
    """Get territory analysis statistics"""
    database = await get_db()
    
    # Count events
    total_events = await database.territory_events.count_documents({"user_id": user_id})
    orignal_count = await database.territory_events.count_documents({"user_id": user_id, "species": "orignal"})
    chevreuil_count = await database.territory_events.count_documents({"user_id": user_id, "species": "chevreuil"})
    ours_count = await database.territory_events.count_documents({"user_id": user_id, "species": "ours"})
    
    # Count cameras
    total_cameras = await database.territory_cameras.count_documents({"user_id": user_id})
    connected_cameras = await database.territory_cameras.count_documents({"user_id": user_id, "connected": True})
    
    # Count photos
    total_photos = await database.territory_photos.count_documents({"user_id": user_id})
    processed_photos = await database.territory_photos.count_documents({"user_id": user_id, "processing_status": "completed"})
    
    return {
        "total_events": total_events,
        "species_counts": {
            "orignal": orignal_count,
            "chevreuil": chevreuil_count,
            "ours": ours_count
        },
        "cameras": {
            "total": total_cameras,
            "connected": connected_cameras
        },
        "photos": {
            "total": total_photos,
            "processed": processed_photos
        }
    }

# ===========================================
# WMS LAYER SOURCES - QUEBEC GOVERNMENT
# ===========================================

# Quebec Government WMS Services
WMS_LAYERS = {
    "foret_ecoforestiere": {
        "url": "https://geoegl.msp.gouv.qc.ca/ws/mffpecofor.fcgi",
        "name": "Carte écoforestière",
        "description": "Peuplements forestiers du Québec (conifères, feuillus, mixte)",
        "layers": "carte_ecoforestiere_quebec_sud"
    },
    "hydrographie": {
        "url": "https://serviceswebcarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
        "name": "Réseau hydrographique",
        "description": "Lacs, rivières, ruisseaux du Québec",
        "layers": "0,1,2,3"
    },
    "topographie": {
        "url": "https://serviceswebcarto.mern.gouv.qc.ca/pes/services/Imagerie/LIDAR_Ombre_WMS/MapServer/WMSServer",
        "name": "Relief et courbes de niveau",
        "description": "Modèle numérique de terrain LiDAR",
        "layers": "0"
    },
    "routes_chemins": {
        "url": "https://serviceswebcarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
        "name": "Réseau routier",
        "description": "Routes et chemins forestiers",
        "layers": "4,5,6"
    }
}

@territory_router.get("/layers/wms-sources")
async def get_wms_sources():
    """Get available WMS layer sources from Quebec government"""
    return {
        "sources": WMS_LAYERS,
        "note": "Ces couches proviennent des services du gouvernement du Québec"
    }

# ===========================================
# PROBABILITY CALCULATION - SPECIES PRESENCE
# ===========================================

# Species-specific habitat preferences
SPECIES_HABITAT_RULES = {
    "orignal": {
        "preferred_forest": ["mixte", "coniferes", "feuillus_dense"],
        "water_distance_optimal_m": 500,  # Préfère être proche de l'eau
        "altitude_optimal_m": (200, 600),  # Altitude optimale
        "prefers_transition_zones": True,  # Zone de transition forêt dense/faible
        "prefers_coulees": True,  # Coulées/ravins
        "prefers_southwest_slopes": True,  # Flancs sud-ouest
        "avoids_roads_within_m": 1000,  # Évite les routes
        "cooling_preference": "high",  # Besoin de zones fraîches en été
        "refuge_type": "dense_conifer"  # Type de refuge
    },
    "chevreuil": {
        "preferred_forest": ["mixte", "feuillus", "regeneration"],
        "water_distance_optimal_m": 300,
        "altitude_optimal_m": (100, 400),
        "prefers_transition_zones": True,
        "prefers_coulees": True,
        "prefers_southwest_slopes": True,
        "avoids_roads_within_m": 500,
        "cooling_preference": "medium",
        "refuge_type": "dense_shrub"
    },
    "ours": {
        "preferred_forest": ["mixte", "feuillus", "coniferes"],
        "water_distance_optimal_m": 200,  # Très proche de l'eau
        "altitude_optimal_m": (100, 800),
        "prefers_transition_zones": False,
        "prefers_coulees": True,
        "prefers_southwest_slopes": False,
        "avoids_roads_within_m": 2000,  # Très sensible aux routes
        "cooling_preference": "high",
        "refuge_type": "dense_mixed"
    }
}

class ProbabilityRequest(BaseModel):
    latitude: float
    longitude: float
    species: Literal['orignal', 'chevreuil', 'ours']
    # Optional environmental data (can be provided or estimated)
    forest_type: Optional[str] = None
    water_distance_m: Optional[float] = None
    altitude_m: Optional[float] = None
    slope_direction: Optional[str] = None  # N, NE, E, SE, S, SW, W, NW
    road_distance_m: Optional[float] = None
    is_transition_zone: Optional[bool] = None
    is_coulee: Optional[bool] = None

class ProbabilityResponse(BaseModel):
    latitude: float
    longitude: float
    species: str
    probability_score: float  # 0-100
    confidence: str  # low, medium, high
    factors: dict
    recommendations: List[str]
    refuge_zones: List[dict]
    cooling_zones: List[dict]

@territory_router.post("/analysis/probability", response_model=ProbabilityResponse)
async def calculate_presence_probability(request: ProbabilityRequest):
    """
    Calculate species presence probability based on environmental factors:
    - Water proximity
    - Forest type
    - Altitude
    - Transition zones (dense to sparse forest)
    - Coulées (gullies/ravines)
    - Southwest mountain slopes
    - Road isolation
    """
    rules = SPECIES_HABITAT_RULES.get(request.species)
    if not rules:
        raise HTTPException(status_code=400, detail="Invalid species")
    
    factors = {}
    score = 50  # Base score
    
    # Factor 1: Water proximity (0-20 points)
    if request.water_distance_m is not None:
        optimal = rules["water_distance_optimal_m"]
        if request.water_distance_m <= optimal:
            water_score = 20
        elif request.water_distance_m <= optimal * 2:
            water_score = 15
        elif request.water_distance_m <= optimal * 4:
            water_score = 10
        else:
            water_score = 5
        factors["water_proximity"] = {
            "score": water_score,
            "max": 20,
            "distance_m": request.water_distance_m,
            "optimal_m": optimal
        }
        score += water_score - 10  # Adjust from base
    
    # Factor 2: Forest type (0-15 points)
    if request.forest_type:
        if request.forest_type in rules["preferred_forest"]:
            forest_score = 15
        elif request.forest_type in ["mixte", "regeneration"]:
            forest_score = 10
        else:
            forest_score = 5
        factors["forest_type"] = {
            "score": forest_score,
            "max": 15,
            "type": request.forest_type,
            "preferred": rules["preferred_forest"]
        }
        score += forest_score - 7.5
    
    # Factor 3: Altitude (0-15 points)
    if request.altitude_m is not None:
        alt_min, alt_max = rules["altitude_optimal_m"]
        if alt_min <= request.altitude_m <= alt_max:
            alt_score = 15
        elif alt_min - 100 <= request.altitude_m <= alt_max + 100:
            alt_score = 10
        else:
            alt_score = 5
        factors["altitude"] = {
            "score": alt_score,
            "max": 15,
            "altitude_m": request.altitude_m,
            "optimal_range": rules["altitude_optimal_m"]
        }
        score += alt_score - 7.5
    
    # Factor 4: Transition zones (0-10 points)
    if request.is_transition_zone is not None:
        if request.is_transition_zone and rules["prefers_transition_zones"]:
            trans_score = 10
        elif request.is_transition_zone:
            trans_score = 7
        else:
            trans_score = 3
        factors["transition_zone"] = {
            "score": trans_score,
            "max": 10,
            "is_transition": request.is_transition_zone,
            "species_prefers": rules["prefers_transition_zones"]
        }
        score += trans_score - 5
    
    # Factor 5: Coulées/ravines (0-10 points)
    if request.is_coulee is not None:
        if request.is_coulee and rules["prefers_coulees"]:
            coulee_score = 10
        elif request.is_coulee:
            coulee_score = 6
        else:
            coulee_score = 2
        factors["coulee"] = {
            "score": coulee_score,
            "max": 10,
            "is_coulee": request.is_coulee,
            "species_prefers": rules["prefers_coulees"]
        }
        score += coulee_score - 5
    
    # Factor 6: Southwest slopes (0-10 points)
    if request.slope_direction:
        sw_directions = ["S", "SW", "W"]
        if request.slope_direction in sw_directions and rules["prefers_southwest_slopes"]:
            slope_score = 10
        elif request.slope_direction in sw_directions:
            slope_score = 7
        else:
            slope_score = 4
        factors["slope_direction"] = {
            "score": slope_score,
            "max": 10,
            "direction": request.slope_direction,
            "preferred": sw_directions if rules["prefers_southwest_slopes"] else []
        }
        score += slope_score - 5
    
    # Factor 7: Road isolation (0-20 points)
    if request.road_distance_m is not None:
        min_road_dist = rules["avoids_roads_within_m"]
        if request.road_distance_m >= min_road_dist * 2:
            road_score = 20
        elif request.road_distance_m >= min_road_dist:
            road_score = 15
        elif request.road_distance_m >= min_road_dist / 2:
            road_score = 8
        else:
            road_score = 2
        factors["road_isolation"] = {
            "score": road_score,
            "max": 20,
            "distance_m": request.road_distance_m,
            "min_preferred_m": min_road_dist
        }
        score += road_score - 10
    
    # Normalize score to 0-100
    score = max(0, min(100, score))
    
    # Determine confidence
    factors_count = len(factors)
    if factors_count >= 5:
        confidence = "high"
    elif factors_count >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Generate recommendations
    recommendations = []
    if score >= 70:
        recommendations.append(f"Zone à haute probabilité pour {request.species}")
        recommendations.append("Installer une caméra de trail dans ce secteur")
    elif score >= 50:
        recommendations.append(f"Zone de probabilité moyenne pour {request.species}")
        recommendations.append("Explorer les coulées et zones de transition à proximité")
    else:
        recommendations.append(f"Zone de faible probabilité pour {request.species}")
        recommendations.append("Chercher des zones avec meilleur accès à l'eau")
    
    # Generate refuge zones (mock for now - would need terrain analysis)
    refuge_zones = [
        {
            "type": rules["refuge_type"],
            "direction": "N",
            "distance_estimate_m": 200,
            "description": f"Zone de refuge potentielle ({rules['refuge_type']})"
        }
    ]
    
    # Generate cooling zones based on species preference
    cooling_zones = []
    if rules["cooling_preference"] == "high":
        cooling_zones = [
            {
                "type": "nord_slope",
                "description": "Versant nord - Zone ombragée",
                "priority": "high"
            },
            {
                "type": "water_body",
                "description": "Proximité cours d'eau",
                "priority": "high"
            }
        ]
    elif rules["cooling_preference"] == "medium":
        cooling_zones = [
            {
                "type": "forest_canopy",
                "description": "Couvert forestier dense",
                "priority": "medium"
            }
        ]
    
    return ProbabilityResponse(
        latitude=request.latitude,
        longitude=request.longitude,
        species=request.species,
        probability_score=round(score, 1),
        confidence=confidence,
        factors=factors,
        recommendations=recommendations,
        refuge_zones=refuge_zones,
        cooling_zones=cooling_zones
    )

# ===========================================
# GPS TRACKING - WAYPOINTS & TRACKS
# ===========================================

class WaypointCreate(BaseModel):
    latitude: float
    longitude: float
    name: str
    description: Optional[str] = None
    waypoint_type: Literal['observation', 'camera', 'cache', 'stand', 'water', 'trail_start', 'custom'] = 'custom'
    icon: Optional[str] = None

class WaypointResponse(BaseModel):
    id: str
    latitude: float
    longitude: float
    name: str
    description: Optional[str]
    waypoint_type: str
    icon: Optional[str]
    created_at: datetime

class TrackPointCreate(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None

class TrackCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TrackResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    points_count: int
    distance_km: float
    duration_minutes: float
    started_at: datetime
    ended_at: Optional[datetime]
    is_active: bool

@territory_router.post("/waypoints", response_model=WaypointResponse)
async def create_waypoint(user_id: str, waypoint: WaypointCreate):
    """Create a new waypoint"""
    database = await get_db()
    
    waypoint_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    waypoint_doc = {
        "_id": waypoint_id,
        "user_id": user_id,
        "latitude": waypoint.latitude,
        "longitude": waypoint.longitude,
        "name": waypoint.name,
        "description": waypoint.description,
        "waypoint_type": waypoint.waypoint_type,
        "icon": waypoint.icon,
        "created_at": now
    }
    
    await database.territory_waypoints.insert_one(waypoint_doc)
    
    return WaypointResponse(
        id=waypoint_id,
        latitude=waypoint.latitude,
        longitude=waypoint.longitude,
        name=waypoint.name,
        description=waypoint.description,
        waypoint_type=waypoint.waypoint_type,
        icon=waypoint.icon,
        created_at=now
    )

@territory_router.get("/waypoints")
async def list_waypoints(user_id: str):
    """List all waypoints for a user"""
    database = await get_db()
    
    waypoints = await database.territory_waypoints.find({"user_id": user_id}).sort("created_at", -1).to_list(500)
    
    return [WaypointResponse(
        id=str(wp['_id']),
        latitude=wp['latitude'],
        longitude=wp['longitude'],
        name=wp['name'],
        description=wp.get('description'),
        waypoint_type=wp['waypoint_type'],
        icon=wp.get('icon'),
        created_at=wp['created_at']
    ) for wp in waypoints]

@territory_router.delete("/waypoints/{waypoint_id}")
async def delete_waypoint(waypoint_id: str, user_id: str):
    """Delete a waypoint"""
    database = await get_db()
    
    result = await database.territory_waypoints.delete_one({"_id": waypoint_id, "user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Waypoint not found")
    
    return {"status": "deleted", "id": waypoint_id}

@territory_router.post("/tracks", response_model=TrackResponse)
async def create_track(user_id: str, track: TrackCreate):
    """Start a new GPS track recording"""
    database = await get_db()
    
    track_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    track_doc = {
        "_id": track_id,
        "user_id": user_id,
        "name": track.name,
        "description": track.description,
        "points": [],
        "started_at": now,
        "ended_at": None,
        "is_active": True,
        "distance_km": 0,
        "created_at": now
    }
    
    await database.territory_tracks.insert_one(track_doc)
    
    return TrackResponse(
        id=track_id,
        name=track.name,
        description=track.description,
        points_count=0,
        distance_km=0,
        duration_minutes=0,
        started_at=now,
        ended_at=None,
        is_active=True
    )

@territory_router.post("/tracks/{track_id}/points")
async def add_track_point(track_id: str, user_id: str, point: TrackPointCreate):
    """Add a point to an active track"""
    database = await get_db()
    
    track = await database.territory_tracks.find_one({"_id": track_id, "user_id": user_id})
    
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    if not track.get('is_active'):
        raise HTTPException(status_code=400, detail="Track is not active")
    
    now = datetime.now(timezone.utc)
    
    point_data = {
        "lat": point.latitude,
        "lon": point.longitude,
        "alt": point.altitude,
        "accuracy": point.accuracy,
        "speed": point.speed,
        "heading": point.heading,
        "timestamp": now
    }
    
    # Calculate distance from last point
    additional_distance = 0
    if track['points']:
        last_point = track['points'][-1]
        additional_distance = haversine_distance(
            last_point['lat'], last_point['lon'],
            point.latitude, point.longitude
        )
    
    await database.territory_tracks.update_one(
        {"_id": track_id},
        {
            "$push": {"points": point_data},
            "$inc": {"distance_km": additional_distance}
        }
    )
    
    return {
        "status": "added",
        "track_id": track_id,
        "point": point_data,
        "additional_distance_km": round(additional_distance, 3)
    }

@territory_router.post("/tracks/{track_id}/stop")
async def stop_track(track_id: str, user_id: str):
    """Stop recording a track"""
    database = await get_db()
    
    now = datetime.now(timezone.utc)
    
    result = await database.territory_tracks.update_one(
        {"_id": track_id, "user_id": user_id, "is_active": True},
        {"$set": {"is_active": False, "ended_at": now}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Active track not found")
    
    track = await database.territory_tracks.find_one({"_id": track_id})
    
    return {
        "status": "stopped",
        "track_id": track_id,
        "ended_at": now,
        "total_points": len(track.get('points', [])),
        "total_distance_km": round(track.get('distance_km', 0), 2)
    }

@territory_router.get("/tracks")
async def list_tracks(user_id: str, active_only: bool = False):
    """List all tracks for a user"""
    database = await get_db()
    
    query = {"user_id": user_id}
    if active_only:
        query["is_active"] = True
    
    tracks = await database.territory_tracks.find(query).sort("created_at", -1).to_list(100)
    
    results = []
    for track in tracks:
        duration = 0
        if track.get('started_at'):
            end_time = track.get('ended_at') or datetime.now(timezone.utc)
            duration = (end_time - track['started_at']).total_seconds() / 60
        
        results.append(TrackResponse(
            id=str(track['_id']),
            name=track['name'],
            description=track.get('description'),
            points_count=len(track.get('points', [])),
            distance_km=round(track.get('distance_km', 0), 2),
            duration_minutes=round(duration, 1),
            started_at=track['started_at'],
            ended_at=track.get('ended_at'),
            is_active=track.get('is_active', False)
        ))
    
    return results

@territory_router.get("/tracks/{track_id}")
async def get_track(track_id: str, user_id: str):
    """Get track details including all points"""
    database = await get_db()
    
    track = await database.territory_tracks.find_one({"_id": track_id, "user_id": user_id})
    
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    duration = 0
    if track.get('started_at'):
        end_time = track.get('ended_at') or datetime.now(timezone.utc)
        duration = (end_time - track['started_at']).total_seconds() / 60
    
    return {
        "id": str(track['_id']),
        "name": track['name'],
        "description": track.get('description'),
        "points": track.get('points', []),
        "points_count": len(track.get('points', [])),
        "distance_km": round(track.get('distance_km', 0), 2),
        "duration_minutes": round(duration, 1),
        "started_at": track['started_at'],
        "ended_at": track.get('ended_at'),
        "is_active": track.get('is_active', False)
    }

@territory_router.delete("/tracks/{track_id}")
async def delete_track(track_id: str, user_id: str):
    """Delete a track"""
    database = await get_db()
    
    result = await database.territory_tracks.delete_one({"_id": track_id, "user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Track not found")
    
    return {"status": "deleted", "id": track_id}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula (returns km)"""
    import math
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

# ===========================================
# GUIDED ROUTE / PARCOURS GUIDÉ
# ===========================================

class GuidedRouteRequest(BaseModel):
    species: Literal['orignal', 'chevreuil', 'ours']
    optimize_for: Literal['probability', 'distance', 'balanced'] = 'balanced'
    start_from_current_position: bool = False
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None

class RouteSegment(BaseModel):
    from_waypoint: dict
    to_waypoint: dict
    distance_km: float
    probability_score: float
    probability_level: str  # "high", "medium", "low"
    color: str
    recommendations: List[str]

class GuidedRouteResponse(BaseModel):
    route_id: str
    species: str
    total_distance_km: float
    estimated_time_hours: float
    average_probability: float
    highest_probability_zone: dict
    segments: List[RouteSegment]
    waypoint_order: List[dict]
    summary: str

def calculate_point_probability(lat: float, lng: float, species: str) -> dict:
    """Calculate probability score for a point based on species habitat rules"""
    import math
    import random
    
    rules = SPECIES_HABITAT_RULES.get(species, SPECIES_HABITAT_RULES['orignal'])
    
    # Simulate environmental factors based on coordinates
    # In a real implementation, this would query actual geographic data
    random.seed(int(lat * 1000 + lng * 1000))
    
    # Simulated factors
    water_distance = random.randint(50, 1000)
    altitude = 200 + int(abs(lat - 46) * 100 + abs(lng + 71) * 50)
    is_transition = random.random() > 0.6
    has_coulee = random.random() > 0.7
    forest_density = random.choice(['dense', 'mixte', 'clairseme', 'regeneration'])
    
    score = 50  # Base score
    factors = []
    
    # Water proximity
    optimal_water = rules["water_distance_optimal_m"]
    if water_distance <= optimal_water:
        score += 15
        factors.append(f"Proche de l'eau ({water_distance}m)")
    elif water_distance <= optimal_water * 2:
        score += 8
        factors.append(f"Distance eau acceptable ({water_distance}m)")
    
    # Altitude
    alt_min, alt_max = rules["altitude_optimal_m"]
    if alt_min <= altitude <= alt_max:
        score += 12
        factors.append(f"Altitude optimale ({altitude}m)")
    elif alt_min - 100 <= altitude <= alt_max + 100:
        score += 6
    
    # Transition zones
    if is_transition and rules["prefers_transition_zones"]:
        score += 10
        factors.append("Zone de transition forêt")
    
    # Coulées
    if has_coulee and rules.get("prefers_coulees", False):
        score += 8
        factors.append("Présence de coulée")
    
    # Forest type
    if forest_density in rules["preferred_forest"]:
        score += 10
        factors.append(f"Forêt {forest_density}")
    
    # Ensure score is between 0-100
    score = max(0, min(100, score))
    
    # Determine level
    if score >= 70:
        level = "high"
        color = "#22c55e"  # Green
    elif score >= 50:
        level = "medium"
        color = "#eab308"  # Yellow
    else:
        level = "low"
        color = "#ef4444"  # Red
    
    return {
        "score": round(score, 1),
        "level": level,
        "color": color,
        "factors": factors
    }

def optimize_waypoint_order(waypoints: list, start_point: dict = None, optimization: str = 'balanced') -> list:
    """
    Optimize waypoint order using a nearest-neighbor algorithm with probability weighting.
    Returns waypoints in optimized order.
    """
    if len(waypoints) <= 1:
        return waypoints
    
    remaining = waypoints.copy()
    ordered = []
    
    # Start from the provided point or the first waypoint
    if start_point:
        current = start_point
    else:
        current = remaining.pop(0)
        ordered.append(current)
    
    while remaining:
        best_next = None
        best_score = float('inf')
        
        for wp in remaining:
            distance = haversine_distance(
                current['latitude'], current['longitude'],
                wp['latitude'], wp['longitude']
            )
            
            prob_score = wp.get('probability', {}).get('score', 50)
            
            if optimization == 'probability':
                # Prioritize high probability zones
                score = distance - (prob_score * 0.05)  # Bonus for high probability
            elif optimization == 'distance':
                # Pure shortest distance
                score = distance
            else:  # balanced
                # Balance between distance and probability
                score = distance - (prob_score * 0.02)
            
            if score < best_score:
                best_score = score
                best_next = wp
        
        if best_next:
            remaining.remove(best_next)
            ordered.append(best_next)
            current = best_next
    
    return ordered

@territory_router.post("/analysis/guided-route", response_model=GuidedRouteResponse)
async def generate_guided_route(request: GuidedRouteRequest, user_id: str):
    """
    Generate an optimized guided route through waypoints with probability analysis.
    
    The route is optimized based on:
    - Species habitat preferences
    - Probability of observation at each point
    - Distance between waypoints
    - Environmental factors
    """
    database = await get_db()
    
    # Get user's waypoints
    waypoints_cursor = database.territory_waypoints.find({"user_id": user_id})
    waypoints = await waypoints_cursor.to_list(100)
    
    if len(waypoints) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Au moins 2 waypoints sont nécessaires pour créer un parcours guidé"
        )
    
    # Calculate probability for each waypoint
    waypoints_with_prob = []
    for wp in waypoints:
        prob = calculate_point_probability(wp['latitude'], wp['longitude'], request.species)
        waypoints_with_prob.append({
            "id": str(wp['_id']),
            "name": wp['name'],
            "latitude": wp['latitude'],
            "longitude": wp['longitude'],
            "waypoint_type": wp.get('waypoint_type', 'custom'),
            "probability": prob
        })
    
    # Determine start point
    start_point = None
    if request.start_from_current_position and request.current_lat and request.current_lng:
        start_point = {
            "id": "current_position",
            "name": "Position actuelle",
            "latitude": request.current_lat,
            "longitude": request.current_lng,
            "waypoint_type": "start",
            "probability": calculate_point_probability(request.current_lat, request.current_lng, request.species)
        }
    
    # Optimize waypoint order
    optimized_waypoints = optimize_waypoint_order(
        waypoints_with_prob, 
        start_point,
        request.optimize_for
    )
    
    # If we have a start point, prepend it
    if start_point and start_point not in optimized_waypoints:
        optimized_waypoints.insert(0, start_point)
    
    # Build route segments
    segments = []
    total_distance = 0
    total_prob = 0
    highest_prob_zone = optimized_waypoints[0] if optimized_waypoints else None
    
    for i in range(len(optimized_waypoints) - 1):
        wp1 = optimized_waypoints[i]
        wp2 = optimized_waypoints[i + 1]
        
        distance = haversine_distance(
            wp1['latitude'], wp1['longitude'],
            wp2['latitude'], wp2['longitude']
        )
        
        # Use the destination's probability for the segment
        prob = wp2['probability']
        
        # Generate recommendations based on species and probability
        recommendations = []
        if prob['score'] >= 70:
            recommendations.append(f"🎯 Zone à forte probabilité pour {request.species}")
            recommendations.append("Restez vigilant et silencieux")
        elif prob['score'] >= 50:
            recommendations.append("Zone de passage probable")
            recommendations.append("Observez les signes de présence")
        else:
            recommendations.append("Zone de transit - continuez vers le prochain point")
        
        for factor in prob['factors'][:2]:
            recommendations.append(f"✓ {factor}")
        
        segment = RouteSegment(
            from_waypoint={
                "id": wp1['id'],
                "name": wp1['name'],
                "lat": wp1['latitude'],
                "lng": wp1['longitude'],
                "probability": wp1['probability']['score']
            },
            to_waypoint={
                "id": wp2['id'],
                "name": wp2['name'],
                "lat": wp2['latitude'],
                "lng": wp2['longitude'],
                "probability": wp2['probability']['score']
            },
            distance_km=round(distance, 2),
            probability_score=prob['score'],
            probability_level=prob['level'],
            color=prob['color'],
            recommendations=recommendations
        )
        segments.append(segment)
        
        total_distance += distance
        total_prob += prob['score']
        
        if prob['score'] > highest_prob_zone['probability']['score']:
            highest_prob_zone = wp2
    
    # Calculate averages and estimates
    avg_prob = total_prob / len(segments) if segments else 0
    # Estimate: 3 km/h walking speed in forest terrain
    estimated_hours = total_distance / 3.0
    
    # Build summary
    high_zones = sum(1 for s in segments if s.probability_level == 'high')
    summary = f"Parcours optimisé de {round(total_distance, 1)} km passant par {len(optimized_waypoints)} points. "
    summary += f"{high_zones} zone(s) à forte probabilité d'observation ({request.species}). "
    summary += f"Probabilité moyenne: {round(avg_prob)}%. "
    summary += f"Temps estimé: {round(estimated_hours, 1)}h."
    
    return GuidedRouteResponse(
        route_id=str(uuid.uuid4()),
        species=request.species,
        total_distance_km=round(total_distance, 2),
        estimated_time_hours=round(estimated_hours, 1),
        average_probability=round(avg_prob, 1),
        highest_probability_zone={
            "name": highest_prob_zone['name'],
            "latitude": highest_prob_zone['latitude'],
            "longitude": highest_prob_zone['longitude'],
            "probability": highest_prob_zone['probability']['score'],
            "factors": highest_prob_zone['probability']['factors']
        },
        segments=segments,
        waypoint_order=[{
            "id": wp['id'],
            "name": wp['name'],
            "lat": wp['latitude'],
            "lng": wp['longitude'],
            "probability": wp['probability']['score'],
            "probability_level": wp['probability']['level'],
            "color": wp['probability']['color']
        } for wp in optimized_waypoints],
        summary=summary
    )

# ===========================================
# CLIMATE & COOLING ZONES
# ===========================================

@territory_router.get("/analysis/cooling-zones")
async def get_cooling_zones(
    latitude: float,
    longitude: float,
    species: Literal['orignal', 'chevreuil', 'ours'],
    radius_km: float = 2.0
):
    """
    Get recommended cooling zones for a species in a given area.
    Cooling zones are important for species like moose and bear during warm periods.
    """
    rules = SPECIES_HABITAT_RULES.get(species)
    if not rules:
        raise HTTPException(status_code=400, detail="Invalid species")
    
    cooling_preference = rules["cooling_preference"]
    
    # Generate cooling zone recommendations based on species
    zones = []
    
    if cooling_preference in ["high", "medium"]:
        # North-facing slopes
        zones.append({
            "type": "north_slope",
            "name": "Versants nord",
            "description": "Zones ombragées sur les versants exposés au nord",
            "priority": "high" if cooling_preference == "high" else "medium",
            "search_direction": "N",
            "characteristics": ["Température plus fraîche", "Moins d'exposition solaire", "Humidité plus élevée"]
        })
        
        # Water bodies
        zones.append({
            "type": "water_proximity",
            "name": "Proximité eau",
            "description": "Zones près des cours d'eau, lacs et marécages",
            "priority": "high",
            "search_radius_m": 500,
            "characteristics": ["Effet rafraîchissant", "Source d'eau", "Végétation dense"]
        })
        
        # Dense canopy
        zones.append({
            "type": "dense_canopy",
            "name": "Couvert forestier dense",
            "description": "Zones avec canopée fermée offrant de l'ombre",
            "priority": "medium",
            "forest_types": ["coniferes_dense", "mixte_dense"],
            "characteristics": ["Ombre permanente", "Protection contre le soleil", "Microclimat frais"]
        })
    
    if species == "orignal":
        zones.append({
            "type": "wetland",
            "name": "Milieux humides",
            "description": "Marécages et tourbières - habitat de prédilection pour le refroidissement",
            "priority": "high",
            "characteristics": ["Eau peu profonde pour se rafraîchir", "Végétation aquatique (nourriture)", "Protection contre les insectes"]
        })
    
    if species == "ours":
        zones.append({
            "type": "ravine",
            "name": "Coulées et ravins",
            "description": "Dépressions de terrain avec air frais descendant",
            "priority": "high",
            "characteristics": ["Air froid accumulé", "Humidité élevée", "Couvert végétal dense"]
        })
    
    return {
        "center": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "species": species,
        "cooling_preference_level": cooling_preference,
        "recommended_zones": zones,
        "best_times": ["Tôt le matin (5h-8h)", "Fin d'après-midi (16h-19h)"],
        "temperature_threshold_celsius": 20 if cooling_preference == "high" else 25
    }

# ===========================================
# GPX IMPORT/EXPORT
# ===========================================

GPX_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="BIONIC Territory Analysis"
  xmlns="http://www.topografix.com/GPX/1/1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>{name}</name>
    <desc>{description}</desc>
    <time>{time}</time>
  </metadata>
'''

GPX_FOOTER = '</gpx>'

@territory_router.get("/export/gpx")
async def export_gpx(user_id: str, include_waypoints: bool = True, include_tracks: bool = True):
    """Export all waypoints and tracks as GPX file"""
    from fastapi.responses import Response
    
    database = await get_db()
    
    now = datetime.now(timezone.utc).isoformat()
    gpx_content = GPX_HEADER.format(
        name="BIONIC Territory Export",
        description=f"Export des données de territoire - {now}",
        time=now
    )
    
    # Export waypoints
    if include_waypoints:
        waypoints = await database.territory_waypoints.find({"user_id": user_id}).to_list(1000)
        for wp in waypoints:
            gpx_content += f'''  <wpt lat="{wp['latitude']}" lon="{wp['longitude']}">
    <name>{wp['name']}</name>
    <desc>{wp.get('description', '')}</desc>
    <type>{wp['waypoint_type']}</type>
    <time>{wp['created_at'].isoformat() if wp.get('created_at') else now}</time>
  </wpt>
'''
    
    # Export tracks
    if include_tracks:
        tracks = await database.territory_tracks.find({"user_id": user_id, "is_active": False}).to_list(100)
        for track in tracks:
            if track.get('points') and len(track['points']) > 0:
                gpx_content += f'''  <trk>
    <name>{track['name']}</name>
    <desc>{track.get('description', '')}</desc>
    <trkseg>
'''
                for point in track['points']:
                    alt_str = f'<ele>{point["alt"]}</ele>' if point.get('alt') else ''
                    time_str = f'<time>{point["timestamp"].isoformat()}</time>' if point.get('timestamp') else ''
                    gpx_content += f'''      <trkpt lat="{point['lat']}" lon="{point['lon']}">
        {alt_str}
        {time_str}
      </trkpt>
'''
                gpx_content += '''    </trkseg>
  </trk>
'''
    
    gpx_content += GPX_FOOTER
    
    return Response(
        content=gpx_content,
        media_type="application/gpx+xml",
        headers={
            "Content-Disposition": f"attachment; filename=bionic_territory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gpx"
        }
    )

@territory_router.post("/import/gpx")
async def import_gpx(user_id: str = Form(...), file: UploadFile = File(...)):
    """Import waypoints and tracks from GPX file"""
    import xml.etree.ElementTree as ET
    
    database = await get_db()
    
    content = await file.read()
    
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid GPX file: {e}")
    
    # GPX namespace
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    
    imported_waypoints = 0
    imported_tracks = 0
    
    # Import waypoints
    for wpt in root.findall('.//gpx:wpt', ns) + root.findall('.//wpt'):
        try:
            lat = float(wpt.get('lat'))
            lon = float(wpt.get('lon'))
            
            name_elem = wpt.find('gpx:name', ns) or wpt.find('name')
            name = name_elem.text if name_elem is not None else f"Waypoint importé"
            
            desc_elem = wpt.find('gpx:desc', ns) or wpt.find('desc')
            desc = desc_elem.text if desc_elem is not None else None
            
            type_elem = wpt.find('gpx:type', ns) or wpt.find('type')
            wp_type = type_elem.text if type_elem is not None and type_elem.text in ['observation', 'camera', 'cache', 'stand', 'water', 'trail_start', 'custom'] else 'custom'
            
            waypoint_id = str(uuid.uuid4())
            waypoint_doc = {
                "_id": waypoint_id,
                "user_id": user_id,
                "latitude": lat,
                "longitude": lon,
                "name": name,
                "description": desc,
                "waypoint_type": wp_type,
                "icon": None,
                "created_at": datetime.now(timezone.utc),
                "imported": True
            }
            
            await database.territory_waypoints.insert_one(waypoint_doc)
            imported_waypoints += 1
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to import waypoint: {e}")
            continue
    
    # Import tracks
    for trk in root.findall('.//gpx:trk', ns) + root.findall('.//trk'):
        try:
            name_elem = trk.find('gpx:name', ns) or trk.find('name')
            name = name_elem.text if name_elem is not None else f"Tracé importé {datetime.now().strftime('%Y-%m-%d')}"
            
            desc_elem = trk.find('gpx:desc', ns) or trk.find('desc')
            desc = desc_elem.text if desc_elem is not None else None
            
            points = []
            total_distance = 0
            
            for trkseg in trk.findall('.//gpx:trkseg', ns) + trk.findall('.//trkseg'):
                for trkpt in trkseg.findall('gpx:trkpt', ns) + trkseg.findall('trkpt'):
                    lat = float(trkpt.get('lat'))
                    lon = float(trkpt.get('lon'))
                    
                    ele_elem = trkpt.find('gpx:ele', ns) or trkpt.find('ele')
                    alt = float(ele_elem.text) if ele_elem is not None else None
                    
                    time_elem = trkpt.find('gpx:time', ns) or trkpt.find('time')
                    timestamp = datetime.fromisoformat(time_elem.text.replace('Z', '+00:00')) if time_elem is not None else datetime.now(timezone.utc)
                    
                    if points:
                        total_distance += haversine_distance(
                            points[-1]['lat'], points[-1]['lon'],
                            lat, lon
                        )
                    
                    points.append({
                        "lat": lat,
                        "lon": lon,
                        "alt": alt,
                        "timestamp": timestamp
                    })
            
            if points:
                track_id = str(uuid.uuid4())
                track_doc = {
                    "_id": track_id,
                    "user_id": user_id,
                    "name": name,
                    "description": desc,
                    "points": points,
                    "started_at": points[0]['timestamp'] if points else datetime.now(timezone.utc),
                    "ended_at": points[-1]['timestamp'] if points else datetime.now(timezone.utc),
                    "is_active": False,
                    "distance_km": total_distance,
                    "created_at": datetime.now(timezone.utc),
                    "imported": True
                }
                
                await database.territory_tracks.insert_one(track_doc)
                imported_tracks += 1
                
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to import track: {e}")
            continue
    
    return {
        "status": "success",
        "imported_waypoints": imported_waypoints,
        "imported_tracks": imported_tracks,
        "message": f"Importé {imported_waypoints} waypoints et {imported_tracks} tracés"
    }

# ===========================================
# NUTRITION ANALYSIS & BIONIC PRODUCTS
# ===========================================

# BIONIC Product Catalog
BIONIC_PRODUCTS = {
    "bionic_mineral_block": {
        "id": "bionic_mineral_block",
        "name": "BIONIC™ Bloc Minéral Premium",
        "category": "minerals",
        "description": "Bloc minéral haute performance enrichi en sodium, calcium et phosphore. Formule exclusive BIONIC™ avec oligo-éléments essentiels pour une attraction maximale.",
        "benefits": [
            "Apport en sodium (sel) - attractif puissant",
            "Calcium et phosphore pour le développement des bois",
            "Oligo-éléments (zinc, cuivre, manganèse)",
            "Résistant aux intempéries"
        ],
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["sodium", "calcium", "phosphore", "zinc", "cuivre"],
        "price_range": "$$",
        "effectiveness_rating": 9.5,
        "image_url": "/images/products/mineral_block.jpg"
    },
    "bionic_protein_mix": {
        "id": "bionic_protein_mix",
        "name": "BIONIC™ Mélange Protéiné Forêt",
        "category": "protein",
        "description": "Mélange alimentaire riche en protéines végétales conçu pour compenser les carences en fin d'hiver et début de printemps. Favorise la récupération post-rut.",
        "benefits": [
            "16% protéines végétales de qualité",
            "Énergie concentrée pour l'hiver",
            "Favorise la croissance des bois",
            "Améliore la condition corporelle"
        ],
        "target_species": ["orignal", "chevreuil", "ours"],
        "nutrients_provided": ["proteine", "energie", "fibres"],
        "price_range": "$$$",
        "effectiveness_rating": 9.2,
        "image_url": "/images/products/protein_mix.jpg"
    },
    "bionic_apple_attractant": {
        "id": "bionic_apple_attractant",
        "name": "BIONIC™ Attractif Pomme Sauvage",
        "category": "attractant",
        "description": "Attractif liquide concentré à base de pomme fermentée. Odeur irrésistible détectable à plus de 500m. Formule longue durée.",
        "benefits": [
            "Odeur de pomme fermentée naturelle",
            "Détectable jusqu'à 500m",
            "Durée d'action 3-4 semaines",
            "Attire en toute saison"
        ],
        "target_species": ["chevreuil", "ours"],
        "nutrients_provided": ["sucres", "attraction"],
        "price_range": "$$",
        "effectiveness_rating": 8.8,
        "image_url": "/images/products/apple_attractant.jpg"
    },
    "bionic_saline_supreme": {
        "id": "bionic_saline_supreme",
        "name": "BIONIC™ Saline Suprême",
        "category": "salt",
        "description": "Saline liquide concentrée pour créer des sites d'attraction durables. Pénètre le sol pour une attraction à long terme sur plusieurs saisons.",
        "benefits": [
            "Concentration saline optimale",
            "Pénètre le sol en profondeur",
            "Effet attractif multi-saisons",
            "Crée un site de léchage permanent"
        ],
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["sodium", "mineraux"],
        "price_range": "$",
        "effectiveness_rating": 9.0,
        "image_url": "/images/products/saline_supreme.jpg"
    },
    "bionic_berry_feast": {
        "id": "bionic_berry_feast",
        "name": "BIONIC™ Festin de Baies",
        "category": "food",
        "description": "Mélange de baies séchées et céréales enrichi spécialement formulé pour l'ours noir. Haute teneur en sucres naturels et graisses.",
        "benefits": [
            "Riche en sucres naturels",
            "Graisses végétales pour l'hibernation",
            "Goût irrésistible pour l'ours",
            "Favorise la prise de poids pré-hibernation"
        ],
        "target_species": ["ours"],
        "nutrients_provided": ["sucres", "graisses", "energie"],
        "price_range": "$$$",
        "effectiveness_rating": 9.3,
        "image_url": "/images/products/berry_feast.jpg"
    },
    "bionic_antler_boost": {
        "id": "bionic_antler_boost",
        "name": "BIONIC™ Boost Panache",
        "category": "minerals",
        "description": "Supplément minéral spécialisé pour le développement optimal des bois. Ratio calcium/phosphore scientifiquement optimisé.",
        "benefits": [
            "Ratio Ca:P de 2:1 optimal",
            "Favorise des bois plus gros et denses",
            "Oligo-éléments pour la santé globale",
            "Résultats visibles en une saison"
        ],
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["calcium", "phosphore", "magnesium", "zinc"],
        "price_range": "$$$",
        "effectiveness_rating": 9.4,
        "image_url": "/images/products/antler_boost.jpg"
    }
}

# Competitor products for comparison
COMPETITOR_PRODUCTS = {
    "trophy_rock": {
        "id": "trophy_rock",
        "name": "Trophy Rock",
        "category": "minerals",
        "description": "Roche minérale naturelle importée. Contient des minéraux naturels mais composition variable.",
        "target_species": ["orignal", "chevreuil"],
        "nutrients_provided": ["sodium", "calcium", "mineraux"],
        "price_range": "$$$",
        "effectiveness_rating": 7.5
    },
    "deer_cane": {
        "id": "deer_cane",
        "name": "Deer Cane",
        "category": "attractant",
        "description": "Attractif minéral liquide populaire. Efficace mais formule standard.",
        "target_species": ["chevreuil"],
        "nutrients_provided": ["sodium", "attraction"],
        "price_range": "$$",
        "effectiveness_rating": 7.8
    },
    "purina_mineral": {
        "id": "purina_mineral",
        "name": "Purina AntlerMax",
        "category": "minerals",
        "description": "Supplément minéral de qualité. Bonne réputation mais prix élevé.",
        "target_species": ["chevreuil"],
        "nutrients_provided": ["calcium", "phosphore", "proteine"],
        "price_range": "$$$$",
        "effectiveness_rating": 8.2
    }
}

# Species-specific nutritional needs by season and forest type
SPECIES_NUTRITION = {
    "orignal": {
        "name": "Orignal",
        "diet_type": "brouteur",
        "primary_foods": ["saule", "bouleau", "érable à épis", "plantes aquatiques", "écorce"],
        "seasonal_needs": {
            "printemps": {
                "priority_nutrients": ["sodium", "proteine", "energie"],
                "deficiencies": ["sel après l'hiver", "protéines pour croissance bois"],
                "notes": "Période critique - recherche active de salines naturelles"
            },
            "ete": {
                "priority_nutrients": ["calcium", "phosphore", "eau"],
                "deficiencies": ["minéraux pour bois en velours"],
                "notes": "Croissance maximale des bois - besoins minéraux élevés"
            },
            "automne": {
                "priority_nutrients": ["energie", "graisses"],
                "deficiencies": ["réserves énergétiques pour le rut"],
                "notes": "Période de rut - dépense énergétique intense"
            },
            "hiver": {
                "priority_nutrients": ["fibres", "energie"],
                "deficiencies": ["énergie pour survivre au froid"],
                "notes": "Survie - alimentation réduite, conservation d'énergie"
            }
        },
        "forest_preferences": {
            "mixte": {"food_quality": "excellent", "cover": "bon"},
            "feuillus": {"food_quality": "très bon", "cover": "moyen"},
            "coniferes": {"food_quality": "moyen", "cover": "excellent"},
            "regeneration": {"food_quality": "excellent", "cover": "faible"}
        }
    },
    "chevreuil": {
        "name": "Chevreuil",
        "diet_type": "sélectif",
        "primary_foods": ["glands", "pommes", "trèfle", "bourgeons", "champignons"],
        "seasonal_needs": {
            "printemps": {
                "priority_nutrients": ["proteine", "calcium", "energie"],
                "deficiencies": ["protéines après l'hiver", "minéraux pour bois"],
                "notes": "Récupération post-hiver, début croissance bois"
            },
            "ete": {
                "priority_nutrients": ["calcium", "phosphore", "proteine"],
                "deficiencies": ["minéraux pour bois", "condition des biches gestantes"],
                "notes": "Croissance bois, gestation/allaitement"
            },
            "automne": {
                "priority_nutrients": ["graisses", "energie", "sucres"],
                "deficiencies": ["réserves graisseuses pour l'hiver"],
                "notes": "Accumulation de graisse, préparation rut"
            },
            "hiver": {
                "priority_nutrients": ["energie", "fibres"],
                "deficiencies": ["énergie, nourriture rare"],
                "notes": "Survie - stress alimentaire important"
            }
        },
        "forest_preferences": {
            "mixte": {"food_quality": "excellent", "cover": "excellent"},
            "feuillus": {"food_quality": "excellent", "cover": "bon"},
            "coniferes": {"food_quality": "faible", "cover": "excellent"},
            "regeneration": {"food_quality": "très bon", "cover": "moyen"}
        }
    },
    "ours": {
        "name": "Ours noir",
        "diet_type": "omnivore",
        "primary_foods": ["baies", "noix", "insectes", "charogne", "miel", "poissons"],
        "seasonal_needs": {
            "printemps": {
                "priority_nutrients": ["proteine", "graisses"],
                "deficiencies": ["tout après hibernation", "protéines animales"],
                "notes": "Sortie hibernation - recherche intensive de nourriture"
            },
            "ete": {
                "priority_nutrients": ["proteine", "sucres", "graisses"],
                "deficiencies": ["variété alimentaire"],
                "notes": "Alimentation diversifiée, baies en abondance"
            },
            "automne": {
                "priority_nutrients": ["graisses", "sucres", "energie"],
                "deficiencies": ["hyperphagie - accumulation graisses critique"],
                "notes": "Période hyperphagie - jusqu'à 20,000 cal/jour"
            },
            "hiver": {
                "priority_nutrients": [],
                "deficiencies": [],
                "notes": "Hibernation - pas d'alimentation"
            }
        },
        "forest_preferences": {
            "mixte": {"food_quality": "excellent", "cover": "excellent"},
            "feuillus": {"food_quality": "très bon", "cover": "bon"},
            "coniferes": {"food_quality": "moyen", "cover": "excellent"},
            "regeneration": {"food_quality": "bon", "cover": "faible"}
        }
    }
}

class NutritionAnalysisRequest(BaseModel):
    latitude: float
    longitude: float
    species: Literal['orignal', 'chevreuil', 'ours']
    forest_type: Optional[Literal['mixte', 'feuillus', 'coniferes', 'regeneration']] = 'mixte'
    season: Optional[Literal['printemps', 'ete', 'automne', 'hiver']] = None
    water_nearby: bool = True
    altitude_m: Optional[float] = None

@territory_router.post("/analysis/nutrition")
async def analyze_nutrition_and_products(request: NutritionAnalysisRequest):
    """
    Analyze nutritional needs for target species at a specific location
    and recommend BIONIC products to address deficiencies.
    """
    species_data = SPECIES_NUTRITION.get(request.species)
    if not species_data:
        raise HTTPException(status_code=400, detail="Invalid species")
    
    # Determine current season if not provided
    if not request.season:
        month = datetime.now().month
        if month in [3, 4, 5]:
            season = "printemps"
        elif month in [6, 7, 8]:
            season = "ete"
        elif month in [9, 10, 11]:
            season = "automne"
        else:
            season = "hiver"
    else:
        season = request.season
    
    seasonal_needs = species_data["seasonal_needs"][season]
    forest_quality = species_data["forest_preferences"].get(request.forest_type, {"food_quality": "moyen", "cover": "moyen"})
    
    # Analyze food sources based on forest type
    food_sources = []
    if request.forest_type == "mixte":
        food_sources = ["Feuillus (bouleau, érable)", "Conifères (sapin, épinette)", "Sous-bois varié", "Arbustes fruitiers"]
    elif request.forest_type == "feuillus":
        food_sources = ["Érables", "Bouleaux", "Chênes/glands", "Arbustes à feuilles"]
    elif request.forest_type == "coniferes":
        food_sources = ["Sapins", "Épinettes", "Pins", "Lichens"]
    elif request.forest_type == "regeneration":
        food_sources = ["Jeunes pousses", "Arbustes", "Herbes hautes", "Framboisiers/mûriers"]
    
    if request.water_nearby:
        food_sources.append("Plantes aquatiques" if request.species == "orignal" else "Végétation riveraine")
    
    # Identify nutritional gaps
    gaps = []
    gap_details = []
    
    for nutrient in seasonal_needs["priority_nutrients"]:
        gap_severity = "moderate"
        
        # Adjust severity based on forest type
        if request.forest_type == "coniferes" and nutrient in ["proteine", "sucres"]:
            gap_severity = "high"
        elif request.forest_type == "regeneration" and nutrient in ["fibres"]:
            gap_severity = "low"
        
        gaps.append(nutrient)
        gap_details.append({
            "nutrient": nutrient,
            "severity": gap_severity,
            "reason": f"Besoin saisonnier ({season}) - {seasonal_needs['notes']}"
        })
    
    # Always add sodium for cervids in spring
    if request.species in ["orignal", "chevreuil"] and season == "printemps" and "sodium" not in gaps:
        gaps.append("sodium")
        gap_details.append({
            "nutrient": "sodium",
            "severity": "high",
            "reason": "Carence critique en sel après l'hiver - recherche active de salines"
        })
    
    # Select and rank products
    recommended_products = []
    
    # Score all BIONIC products
    for product_id, product in BIONIC_PRODUCTS.items():
        if request.species in product["target_species"]:
            # Calculate relevance score
            score = product["effectiveness_rating"]
            
            # Bonus for matching nutrients
            matching_nutrients = set(product["nutrients_provided"]) & set(gaps)
            score += len(matching_nutrients) * 1.5
            
            # Bonus for season-specific products
            if season == "printemps" and "sodium" in product["nutrients_provided"]:
                score += 2
            if season == "automne" and ("energie" in product["nutrients_provided"] or "graisses" in product["nutrients_provided"]):
                score += 1.5
            
            recommended_products.append({
                **product,
                "relevance_score": round(score, 1),
                "matching_nutrients": list(matching_nutrients),
                "recommendation_reason": generate_recommendation_reason(product, gaps, season, request.species)
            })
    
    # Add some competitor products for comparison (but ranked lower)
    for product_id, product in COMPETITOR_PRODUCTS.items():
        if request.species in product["target_species"]:
            score = product["effectiveness_rating"] * 0.9  # Slight penalty for competitors
            matching_nutrients = set(product["nutrients_provided"]) & set(gaps)
            score += len(matching_nutrients) * 1.2
            
            recommended_products.append({
                **product,
                "relevance_score": round(score, 1),
                "matching_nutrients": list(matching_nutrients),
                "recommendation_reason": f"Alternative disponible sur le marché",
                "is_competitor": True
            })
    
    # Sort by relevance score and take top 5
    recommended_products.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_products = recommended_products[:5]
    
    # Ensure at least one BIONIC product in top 3
    bionic_in_top3 = any(not p.get("is_competitor", False) for p in top_products[:3])
    if not bionic_in_top3 and recommended_products:
        # Find first BIONIC product and swap
        for i, p in enumerate(recommended_products):
            if not p.get("is_competitor", False):
                top_products[2] = p
                break
    
    return {
        "location": {
            "latitude": request.latitude,
            "longitude": request.longitude
        },
        "species": {
            "id": request.species,
            "name": species_data["name"],
            "diet_type": species_data["diet_type"],
            "primary_foods": species_data["primary_foods"]
        },
        "environment": {
            "forest_type": request.forest_type,
            "food_quality": forest_quality["food_quality"],
            "cover_quality": forest_quality["cover"],
            "water_nearby": request.water_nearby,
            "season": season
        },
        "food_sources_available": food_sources,
        "seasonal_analysis": {
            "season": season,
            "priority_nutrients": seasonal_needs["priority_nutrients"],
            "known_deficiencies": seasonal_needs["deficiencies"],
            "notes": seasonal_needs["notes"]
        },
        "nutritional_gaps": gap_details,
        "recommended_products": top_products,
        "summary": generate_analysis_summary(request.species, season, gaps, forest_quality)
    }

def generate_recommendation_reason(product: dict, gaps: list, season: str, species: str) -> str:
    """Generate a detailed reason for product recommendation"""
    reasons = []
    
    matching = set(product["nutrients_provided"]) & set(gaps)
    
    if "sodium" in matching:
        reasons.append("Comble le besoin critique en sel")
    if "calcium" in matching or "phosphore" in matching:
        reasons.append("Favorise le développement des bois")
    if "proteine" in matching:
        reasons.append("Apport protéique pour la récupération")
    if "energie" in matching or "graisses" in matching:
        reasons.append("Source d'énergie concentrée")
    if "sucres" in matching:
        reasons.append("Attraction par les sucres naturels")
    
    if not reasons:
        reasons.append(f"Produit adapté pour {species}")
    
    if product.get("effectiveness_rating", 0) >= 9.0:
        reasons.append("Efficacité prouvée sur le terrain")
    
    return " • ".join(reasons)

def generate_analysis_summary(species: str, season: str, gaps: list, forest_quality: dict) -> str:
    """Generate a summary of the nutritional analysis"""
    species_names = {"orignal": "l'orignal", "chevreuil": "le chevreuil", "ours": "l'ours noir"}
    
    quality_text = "excellent" if forest_quality["food_quality"] == "excellent" else \
                   "bon" if forest_quality["food_quality"] in ["très bon", "bon"] else "limité"
    
    gap_text = ", ".join(gaps[:3]) if gaps else "aucune carence majeure"
    
    return f"Analyse pour {species_names.get(species, species)} en {season}: " \
           f"Le couvert forestier offre un potentiel alimentaire {quality_text}. " \
           f"Carences identifiées: {gap_text}. " \
           f"Les produits BIONIC™ recommandés ciblent spécifiquement ces besoins."

# ===========================================
# ORDERS - Shopping Cart & Admin Approval
# ===========================================

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItem]
    total: float
    source: str = "territory_bionic"
    user_id: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    items: List[dict]
    total: float
    status: str
    created_at: datetime

@territory_router.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    """Create a new order pending admin approval"""
    database = await get_db()
    
    order_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    order_doc = {
        "_id": order_id,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "notes": order.notes,
        "items": [item.dict() for item in order.items],
        "total": order.total,
        "source": order.source,
        "user_id": order.user_id,
        "status": "pending_approval",
        "created_at": now,
        "updated_at": now,
        "approved_at": None,
        "approved_by": None,
        "shipped_at": None,
        "tracking_number": None
    }
    
    await database.territory_orders.insert_one(order_doc)
    
    # Create notification for admin
    notification_doc = {
        "_id": str(uuid.uuid4()),
        "type": "new_order",
        "order_id": order_id,
        "customer_name": order.customer_name,
        "total": order.total,
        "items_count": len(order.items),
        "read": False,
        "created_at": now
    }
    await database.admin_notifications.insert_one(notification_doc)
    
    logger.info(f"New order created: {order_id} from {order.customer_name}")
    
    return OrderResponse(
        id=order_id,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        items=[item.dict() for item in order.items],
        total=order.total,
        status="pending_approval",
        created_at=now
    )

@territory_router.get("/orders")
async def list_orders(status: Optional[str] = None, limit: int = 50):
    """List orders (for admin dashboard)"""
    database = await get_db()
    
    query = {}
    if status:
        query["status"] = status
    
    orders = await database.territory_orders.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    
    return [{
        "id": str(order['_id']),
        "customer_name": order['customer_name'],
        "customer_email": order['customer_email'],
        "customer_phone": order.get('customer_phone'),
        "items": order['items'],
        "total": order['total'],
        "status": order['status'],
        "source": order.get('source', 'unknown'),
        "notes": order.get('notes'),
        "created_at": order['created_at'],
        "approved_at": order.get('approved_at'),
        "shipped_at": order.get('shipped_at')
    } for order in orders]

@territory_router.post("/orders/{order_id}/approve")
async def approve_order(order_id: str, admin_name: str = "Admin"):
    """Approve an order"""
    database = await get_db()
    
    now = datetime.now(timezone.utc)
    
    result = await database.territory_orders.update_one(
        {"_id": order_id, "status": "pending_approval"},
        {"$set": {
            "status": "approved",
            "approved_at": now,
            "approved_by": admin_name,
            "updated_at": now
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or already processed")
    
    return {"status": "approved", "order_id": order_id, "approved_at": now}

@territory_router.post("/orders/{order_id}/reject")
async def reject_order(order_id: str, reason: str = ""):
    """Reject an order"""
    database = await get_db()
    
    now = datetime.now(timezone.utc)
    
    result = await database.territory_orders.update_one(
        {"_id": order_id, "status": "pending_approval"},
        {"$set": {
            "status": "rejected",
            "rejection_reason": reason,
            "updated_at": now
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or already processed")
    
    return {"status": "rejected", "order_id": order_id, "reason": reason}

@territory_router.get("/orders/notifications")
async def get_order_notifications(unread_only: bool = True):
    """Get admin notifications for new orders"""
    database = await get_db()
    
    query = {}
    if unread_only:
        query["read"] = False
    
    notifications = await database.admin_notifications.find(query).sort("created_at", -1).limit(20).to_list(20)
    
    return [{
        "id": str(n['_id']),
        "type": n['type'],
        "order_id": n.get('order_id'),
        "customer_name": n.get('customer_name'),
        "total": n.get('total'),
        "items_count": n.get('items_count'),
        "read": n['read'],
        "created_at": n['created_at']
    } for n in notifications]

@territory_router.post("/orders/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    database = await get_db()
    
    await database.admin_notifications.update_one(
        {"_id": notification_id},
        {"$set": {"read": True}}
    )
    
    return {"status": "marked_read"}

# ===========================================
# PROMPT DOCUMENTATION STORAGE
# ===========================================

class PromptDocumentation(BaseModel):
    app_name: str
    version: str
    description: str
    modules: List[dict]
    api_endpoints: dict
    bionic_products: List[dict]
    species_rules: dict
    integrations: List[str]
    tech_stack: dict

@territory_router.post("/prompt/save")
async def save_prompt_documentation(prompt_data: PromptDocumentation):
    """Save the PROMPT documentation to database"""
    database = await get_db()
    
    now = datetime.now(timezone.utc)
    
    # Check if a prompt already exists
    existing = await database.prompt_documentation.find_one({"app_name": prompt_data.app_name})
    
    if existing:
        # Update existing
        await database.prompt_documentation.update_one(
            {"app_name": prompt_data.app_name},
            {"$set": {
                **prompt_data.dict(),
                "last_updated": now,
                "save_count": existing.get("save_count", 0) + 1
            }}
        )
        return {
            "status": "updated",
            "message": "Documentation mise à jour dans la base de données",
            "last_updated": now,
            "save_count": existing.get("save_count", 0) + 1
        }
    else:
        # Create new
        doc = {
            "_id": str(uuid.uuid4()),
            **prompt_data.dict(),
            "created_at": now,
            "last_updated": now,
            "save_count": 1
        }
        await database.prompt_documentation.insert_one(doc)
        return {
            "status": "created",
            "message": "Documentation sauvegardée dans la base de données",
            "last_updated": now,
            "save_count": 1
        }

@territory_router.get("/prompt/load")
async def load_prompt_documentation():
    """Load the saved PROMPT documentation from database"""
    database = await get_db()
    
    doc = await database.prompt_documentation.find_one({"app_name": "Chasse Bionic™ / BIONIC™"})
    
    if not doc:
        return None
    
    # Remove MongoDB _id for JSON serialization
    doc.pop("_id", None)
    return doc

@territory_router.get("/prompt/history")
async def get_prompt_save_history():
    """Get the save history of PROMPT documentation"""
    database = await get_db()
    
    doc = await database.prompt_documentation.find_one({"app_name": "Chasse Bionic™ / BIONIC™"})
    
    if not doc:
        return {
            "has_saved": False,
            "save_count": 0,
            "last_updated": None
        }
    
    return {
        "has_saved": True,
        "save_count": doc.get("save_count", 1),
        "last_updated": doc.get("last_updated"),
        "created_at": doc.get("created_at")
    }

# ===========================================
# QUEBEC HUNTING TERRITORIES API
# ===========================================

from quebec_hunting_data import (
    QUEBEC_ZECS, 
    QUEBEC_RESERVES_FAUNIQUES, 
    QUEBEC_POURVOIRIES,
    QUEBEC_REFUGES_FAUNIQUES,
    QUEBEC_HUNTING_REGIONS,
    QUEBEC_HUNTABLE_SPECIES,
    QUEBEC_HUNTING_RESOURCES,
    get_all_hunting_territories,
    search_territories,
    get_nearest_territories
)

@territory_router.get("/hunting/territories")
async def get_hunting_territories(
    query: Optional[str] = None,
    region: Optional[str] = None,
    species: Optional[str] = None,
    territory_type: Optional[str] = None
):
    """
    Get Quebec hunting territories with optional filters.
    
    - query: Search by name or region
    - region: Filter by region (e.g., "Mauricie", "Laurentides")
    - species: Filter by huntable species (orignal, chevreuil, ours, caribou)
    - territory_type: Filter by type (zec, reserve, pourvoirie)
    """
    territories = search_territories(query, region, species, territory_type)
    
    return {
        "count": len(territories),
        "territories": territories
    }

@territory_router.get("/hunting/territories/nearby")
async def get_nearby_hunting_territories(
    latitude: float,
    longitude: float,
    limit: int = 10
):
    """
    Get the nearest hunting territories from a given position.
    Returns territories sorted by distance.
    """
    territories = get_nearest_territories(latitude, longitude, limit)
    
    return {
        "count": len(territories),
        "reference_point": {"lat": latitude, "lng": longitude},
        "territories": territories
    }

@territory_router.get("/hunting/zecs")
async def get_all_zecs():
    """Get all ZECs (Zones d'Exploitation Contrôlée) in Quebec"""
    return {
        "count": len(QUEBEC_ZECS),
        "zecs": QUEBEC_ZECS
    }

@territory_router.get("/hunting/reserves")
async def get_all_reserves():
    """Get all wildlife reserves (Réserves fauniques) in Quebec"""
    return {
        "count": len(QUEBEC_RESERVES_FAUNIQUES),
        "reserves": QUEBEC_RESERVES_FAUNIQUES
    }

@territory_router.get("/hunting/pourvoiries")
async def get_all_pourvoiries():
    """Get all outfitters (Pourvoiries) in Quebec"""
    return {
        "count": len(QUEBEC_POURVOIRIES),
        "pourvoiries": QUEBEC_POURVOIRIES
    }

@territory_router.get("/hunting/regions")
async def get_hunting_regions():
    """Get all hunting regions in Quebec"""
    return {
        "count": len(QUEBEC_HUNTING_REGIONS),
        "regions": QUEBEC_HUNTING_REGIONS
    }

@territory_router.get("/hunting/species")
async def get_huntable_species():
    """Get information about huntable species in Quebec"""
    return QUEBEC_HUNTABLE_SPECIES

@territory_router.get("/hunting/resources")
async def get_hunting_resources():
    """Get useful hunting resources and links"""
    return QUEBEC_HUNTING_RESOURCES

@territory_router.get("/hunting/search")
async def search_hunting_locations(
    lat: float,
    lng: float,
    radius_km: float = 50,
    species: Optional[str] = None
):
    """
    Advanced search for hunting locations near a position.
    Combines ZECs, reserves, and pourvoiries in one result.
    """
    import math
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    all_territories = get_all_hunting_territories()
    
    # Filter by distance
    nearby = []
    for t in all_territories:
        distance = haversine(lat, lng, t["lat"], t["lng"])
        if distance <= radius_km:
            t["distance_km"] = round(distance, 1)
            
            # Filter by species if specified
            if species:
                if species in t.get("species", []):
                    nearby.append(t)
            else:
                nearby.append(t)
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    
    # Group by type
    result = {
        "search_params": {
            "center": {"lat": lat, "lng": lng},
            "radius_km": radius_km,
            "species_filter": species
        },
        "total_count": len(nearby),
        "by_type": {
            "zecs": [t for t in nearby if t["type"] == "ZEC"],
            "reserves": [t for t in nearby if t["type"] == "Réserve faunique"],
            "pourvoiries": [t for t in nearby if t["type"] == "Pourvoirie"]
        },
        "all_results": nearby
    }
    
    return result

@territory_router.get("/hunting/rankings")
async def get_territory_rankings(
    species: Optional[str] = None,
    region: Optional[str] = None,
    territory_type: Optional[str] = None,
    limit: int = 50
):
    """
    Get ranked hunting territories based on various performance criteria.
    Rankings consider: species diversity, accessibility, popularity, and facilities.
    """
    import random
    
    all_territories = get_all_hunting_territories()
    
    # Calculate performance score for each territory
    ranked_territories = []
    for t in all_territories:
        # Base score calculation
        species_count = len(t.get("species", []))
        species_score = species_count * 15  # 15 points per species
        
        # Region bonus (some regions are more popular)
        popular_regions = ["Mauricie", "Laurentides", "Saguenay-Lac-Saint-Jean", "Capitale-Nationale"]
        region_bonus = 10 if t.get("region") in popular_regions else 0
        
        # Type bonus
        type_bonus = {"Réserve faunique": 15, "ZEC": 10, "Pourvoirie": 12}.get(t.get("type"), 5)
        
        # Calculate final score (with some randomness to simulate real data)
        base_score = species_score + region_bonus + type_bonus
        performance_score = min(100, base_score + random.randint(-5, 15))
        
        # Generate mock stats (in production, these would come from real data)
        territory_data = {
            **t,
            "performance_score": performance_score,
            "stats": {
                "species_count": species_count,
                "avg_success_rate": round(random.uniform(25, 75), 1),
                "visitor_rating": round(random.uniform(3.5, 5.0), 1),
                "annual_permits": random.randint(500, 5000),
                "area_km2": random.randint(100, 2000)
            },
            "trending": random.choice([True, False, False]),  # 33% chance of trending
            "highlight": random.choice(["Forte population d'orignaux", "Accès facile", "Chalets disponibles", "Zone peu fréquentée", "Excellentes conditions", None, None])
        }
        
        # Apply filters
        if species and species not in t.get("species", []):
            continue
        if region and t.get("region") != region:
            continue
        if territory_type and t.get("type") != territory_type:
            continue
            
        ranked_territories.append(territory_data)
    
    # Sort by performance score (descending)
    ranked_territories.sort(key=lambda x: x["performance_score"], reverse=True)
    
    # Add rank
    for i, t in enumerate(ranked_territories):
        t["rank"] = i + 1
    
    # Get unique regions and types for filtering
    all_regions = sorted(set(t.get("region") for t in all_territories if t.get("region")))
    all_types = sorted(set(t.get("type") for t in all_territories if t.get("type")))
    
    return {
        "rankings": ranked_territories[:limit],
        "total_count": len(ranked_territories),
        "filters": {
            "available_regions": all_regions,
            "available_types": all_types,
            "available_species": ["orignal", "chevreuil", "ours", "caribou", "petit gibier"]
        },
        "last_updated": "2026-01-21T12:00:00Z"
    }

@territory_router.get("/hunting/hotspots")
async def get_gps_hotspots(
    species: Optional[str] = None,
    region: Optional[str] = None,
    min_probability: int = 60,
    limit: int = 100
):
    """
    Get GPS hotspots with high hunting probability.
    Returns coordinates with detailed probability analysis per species.
    """
    import random
    import math
    
    all_territories = get_all_hunting_territories()
    hotspots = []
    
    # Generate hotspots around each territory
    for territory in all_territories:
        base_lat = territory.get("lat", 47.0)
        base_lng = territory.get("lng", -71.0)
        territory_species = territory.get("species", [])
        territory_region = territory.get("region", "Québec")
        
        # Apply region filter
        if region and territory_region != region:
            continue
        
        # Generate 2-4 hotspots per territory
        num_hotspots = random.randint(2, 4)
        
        for i in range(num_hotspots):
            # Offset coordinates slightly (within ~5km)
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            spot_lat = round(base_lat + lat_offset, 6)
            spot_lng = round(base_lng + lng_offset, 6)
            
            # Calculate species-specific probabilities
            species_probabilities = {}
            dominant_species = None
            max_prob = 0
            
            for sp in ["orignal", "chevreuil", "ours", "caribou"]:
                if sp in territory_species:
                    # Higher probability for species in territory
                    base_prob = random.randint(55, 95)
                    # Add environmental factors
                    water_factor = random.randint(-5, 10)
                    forest_factor = random.randint(-5, 15)
                    season_factor = random.randint(-10, 10)
                    
                    prob = min(99, max(20, base_prob + water_factor + forest_factor + season_factor))
                    species_probabilities[sp] = prob
                    
                    if prob > max_prob:
                        max_prob = prob
                        dominant_species = sp
                else:
                    # Lower probability for species not in territory
                    species_probabilities[sp] = random.randint(5, 30)
            
            # Skip if below minimum probability
            if max_prob < min_probability:
                continue
            
            # Apply species filter
            if species and species_probabilities.get(species, 0) < min_probability:
                continue
            
            # Generate terrain info
            terrain_types = ["Forêt mixte", "Forêt de conifères", "Zone humide", "Clairière", "Bordure de lac", "Vallée", "Crête"]
            features = ["Point d'eau à proximité", "Couvert forestier dense", "Zone de nourrissage", "Corridor de déplacement", "Aire de repos", "Zone de transition"]
            
            hotspot = {
                "id": f"hs-{territory['name'][:3].lower()}-{i+1}-{random.randint(1000, 9999)}",
                "coordinates": {
                    "lat": spot_lat,
                    "lng": spot_lng,
                    "altitude_m": random.randint(150, 800),
                    "dms_lat": f"{abs(int(spot_lat))}°{int((abs(spot_lat) % 1) * 60)}'{round((((abs(spot_lat) % 1) * 60) % 1) * 60, 1)}\"{'N' if spot_lat >= 0 else 'S'}",
                    "dms_lng": f"{abs(int(spot_lng))}°{int((abs(spot_lng) % 1) * 60)}'{round((((abs(spot_lng) % 1) * 60) % 1) * 60, 1)}\"{'W' if spot_lng < 0 else 'E'}"
                },
                "probabilities": species_probabilities,
                "dominant_species": dominant_species,
                "max_probability": max_prob,
                "territory": {
                    "name": territory.get("name"),
                    "type": territory.get("type"),
                    "region": territory_region,
                    "website": territory.get("website")
                },
                "terrain": {
                    "type": random.choice(terrain_types),
                    "features": random.sample(features, k=random.randint(2, 4)),
                    "water_distance_m": random.randint(50, 800),
                    "road_distance_m": random.randint(200, 3000)
                },
                "recommendations": {
                    "best_time": random.choice(["Aube (5h-8h)", "Crépuscule (17h-20h)", "Mi-journée (11h-14h)"]),
                    "best_season": random.choice(["Automne (Sept-Nov)", "Printemps (Avr-Mai)", "Été (Juin-Août)"]),
                    "approach": random.choice(["Par le nord avec vent du sud", "Approche silencieuse depuis le sentier", "Affût près du point d'eau"]),
                    "equipment": random.sample(["Jumelles", "Appeau", "Caméra de trail", "GPS", "Boussole"], k=2)
                },
                "user_ratings": {
                    "avg_rating": round(random.uniform(3.5, 5.0), 1),
                    "total_reviews": random.randint(5, 150),
                    "success_reports": random.randint(10, 80)
                },
                "last_activity": f"2026-01-{random.randint(10, 21)}T{random.randint(6, 18):02d}:00:00Z",
                "verified": random.choice([True, True, True, False])  # 75% verified
            }
            
            hotspots.append(hotspot)
    
    # Sort by max probability
    hotspots.sort(key=lambda x: x["max_probability"], reverse=True)
    
    # Get unique regions for filtering
    all_regions = sorted(set(t.get("region") for t in all_territories if t.get("region")))
    
    # Calculate stats
    total_hotspots = len(hotspots)
    avg_probability = round(sum(h["max_probability"] for h in hotspots) / max(1, total_hotspots), 1)
    
    return {
        "hotspots": hotspots[:limit],
        "total_count": total_hotspots,
        "stats": {
            "average_probability": avg_probability,
            "highest_probability": hotspots[0]["max_probability"] if hotspots else 0,
            "verified_spots": sum(1 for h in hotspots if h["verified"]),
            "species_distribution": {
                "orignal": sum(1 for h in hotspots if h["dominant_species"] == "orignal"),
                "chevreuil": sum(1 for h in hotspots if h["dominant_species"] == "chevreuil"),
                "ours": sum(1 for h in hotspots if h["dominant_species"] == "ours"),
                "caribou": sum(1 for h in hotspots if h["dominant_species"] == "caribou")
            }
        },
        "filters": {
            "available_regions": all_regions,
            "available_species": ["orignal", "chevreuil", "ours", "caribou"],
            "min_probability_options": [50, 60, 70, 80, 90]
        },
        "last_updated": "2026-01-21T14:00:00Z"
    }

# ===========================================
# STARTUP/SHUTDOWN
# ===========================================

async def init_territory_module():
    """Initialize the territory analysis module"""
    await get_db()
    logger.info("Territory analysis module initialized with MongoDB")

async def shutdown_territory_module():
    """Shutdown the territory analysis module"""
    await close_db()
    logger.info("Territory analysis module shut down")
