from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Request, Response, Depends, Cookie
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
import io
import asyncio
import base64
import httpx
import bcrypt
from jose import jwt, JWTError

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# LLM Setup
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

# Stripe Setup
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
JWT_SECRET = os.environ.get('JWT_SECRET', 'glaseditions-secret-key-2025')
JWT_ALGORITHM = "HS256"

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ==================== SUBSCRIPTION PLANS ====================

# Admin emails with unlimited free access
ADMIN_EMAILS = ["glaseditionslab@gmail.com"]
SUPER_ADMIN_EMAILS = ["glaseditionslab@gmail.com"]

SUBSCRIPTION_PLANS = {
    "debutant": {
        "name": "Débutant",
        "price": 27.00,
        "books_per_month": 3,
        "max_chapters": 15,
        "cover_generation": False,
        "description": "Parfait pour commencer"
    },
    "auteur": {
        "name": "Auteur",
        "price": 57.00,
        "books_per_month": 7,
        "max_chapters": 30,
        "cover_generation": True,
        "popular": True,
        "description": "Le plus populaire"
    },
    "ecrivain": {
        "name": "Écrivain",
        "price": 97.00,
        "books_per_month": -1,  # -1 = unlimited
        "max_chapters": 50,  # Up to 50 chapters per book
        "cover_generation": True,
        "description": "Pour les professionnels"
    },
    "admin": {
        "name": "Administrateur",
        "price": 0,
        "books_per_month": -1,  # unlimited
        "max_chapters": -1,  # unlimited
        "cover_generation": True,
        "description": "Accès administrateur"
    }
}

SINGLE_BOOK_PRICE = 9.90
SINGLE_BOOK_MAX_CHAPTERS = 12
SINGLE_BOOK_COVER_GENERATION = False


# ==================== AUTH MODELS ====================

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    subscription: Optional[str] = None
    subscription_expires: Optional[str] = None
    books_this_month: int = 0
    single_book_credits: int = 0
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None

class ChapterEditRequest(BaseModel):
    content: str


# ==================== BOOK MODELS ====================

class Genre(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    ROMANCE = "romance"
    THRILLER = "thriller"
    FANTASY = "fantasy"
    SCIFI = "science_fiction"
    MYSTERY = "mystery"
    HORROR = "horror"
    BIOGRAPHY = "biography"
    SELF_HELP = "self_help"
    HISTORY = "history"
    BUSINESS = "business"


class Tone(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    LITERARY = "literary"
    HUMOROUS = "humorous"
    DRAMATIC = "dramatic"
    POETIC = "poetic"


class BookStatus(str, Enum):
    DRAFT = "draft"
    GENERATING_OUTLINE = "generating_outline"
    OUTLINE_READY = "outline_ready"
    GENERATING = "generating"
    GENERATING_COVER = "generating_cover"
    COMPLETED = "completed"
    ERROR = "error"


class Chapter(BaseModel):
    number: int
    title: str
    summary: str
    content: Optional[str] = None
    word_count: int = 0
    status: str = "pending"
    edited_manually: Optional[bool] = None


class BookCreate(BaseModel):
    title: str
    idea: str
    genre: Genre
    tone: Tone
    target_chapters: int = Field(default=25, ge=10, le=50)
    language: str = "français"
    additional_info: Optional[str] = None
    cover_prompt: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None


class Book(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    title: str
    idea: str
    genre: Genre
    tone: Tone
    target_chapters: int
    language: str
    additional_info: Optional[str] = None
    cover_prompt: Optional[str] = None
    cover_image: Optional[str] = None
    status: BookStatus = BookStatus.DRAFT
    outline: List[Chapter] = []
    current_chapter: int = 0
    total_word_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None


class BookResponse(BaseModel):
    id: str
    user_id: Optional[str]
    title: str
    idea: str
    genre: str
    tone: str
    target_chapters: int
    language: str
    additional_info: Optional[str]
    cover_prompt: Optional[str]
    cover_image: Optional[str]
    status: str
    outline: List[Chapter]
    current_chapter: int
    total_word_count: int
    created_at: str
    updated_at: str
    error_message: Optional[str]


class CoverGenerateRequest(BaseModel):
    prompt: Optional[str] = None


class CheckoutRequest(BaseModel):
    plan_id: str
    origin_url: str


class SingleBookCheckoutRequest(BaseModel):
    origin_url: str


# ==================== AUTH HELPERS ====================

def is_user_admin(user: dict) -> bool:
    """Check if a user is admin (super-admin by email OR promoted via is_admin flag)"""
    if not user:
        return False
    if user.get("email") in ADMIN_EMAILS:
        return True
    return user.get("is_admin", False) is True

def is_super_admin(user: dict) -> bool:
    """Check if user is the protected super-admin"""
    return user.get("email") in SUPER_ADMIN_EMAILS

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request, session_token: Optional[str] = Cookie(default=None)) -> Optional[dict]:
    token = None
    
    if session_token:
        token = session_token
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        token = request.query_params.get("token")
    
    if not token:
        return None
    
    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if session:
        expires_at = session.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return None
        user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
        return user
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
            return user
    except JWTError:
        pass
    
    return None

async def require_auth(request: Request, session_token: Optional[str] = Cookie(default=None)) -> dict:
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user


def user_to_response(user: dict) -> UserResponse:
    # Check if user is admin
    subscription = user.get("subscription")
    if is_user_admin(user):
        subscription = "admin"
    
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        name=user["name"],
        picture=user.get("picture"),
        subscription=subscription,
        subscription_expires=user.get("subscription_expires"),
        books_this_month=user.get("books_this_month", 0),
        single_book_credits=user.get("single_book_credits", 0),
        created_at=user["created_at"]
    )


async def check_user_can_create_book(user: dict) -> tuple:
    """Check if user can create a book based on subscription"""
    if not user:
        return False, "Vous devez être connecté pour créer un livre", None
    
    # Check if user is admin (unlimited free access)
    if is_user_admin(user):
        admin_plan = SUBSCRIPTION_PLANS.get("admin")
        return True, None, admin_plan
    
    subscription = user.get("subscription")
    subscription_expires = user.get("subscription_expires")
    books_this_month = user.get("books_this_month", 0)
    single_book_credits = user.get("single_book_credits", 0)
    
    # Check subscription validity
    if subscription and subscription_expires:
        expires = datetime.fromisoformat(subscription_expires) if isinstance(subscription_expires, str) else subscription_expires
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        if expires > datetime.now(timezone.utc):
            plan = SUBSCRIPTION_PLANS.get(subscription)
            if plan:
                max_books = plan["books_per_month"]
                if max_books == -1 or books_this_month < max_books:
                    return True, None, plan
                else:
                    return False, f"Limite mensuelle atteinte ({max_books} livres). Passez à un plan supérieur.", plan
    
    # Check single book credits
    if single_book_credits > 0:
        return True, None, {"max_chapters": SINGLE_BOOK_MAX_CHAPTERS, "cover_generation": SINGLE_BOOK_COVER_GENERATION, "name": "Livre unique"}
    
    return False, "Abonnement requis ou achetez un livre unique", None


async def get_user_max_chapters(user: dict) -> int:
    """Get max chapters based on user's subscription"""
    if not user:
        return 15
    
    # Admin has unlimited chapters
    if is_user_admin(user):
        return -1
    
    subscription = user.get("subscription")
    subscription_expires = user.get("subscription_expires")
    single_book_credits = user.get("single_book_credits", 0)
    
    if subscription and subscription_expires:
        expires = datetime.fromisoformat(subscription_expires) if isinstance(subscription_expires, str) else subscription_expires
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        if expires > datetime.now(timezone.utc):
            plan = SUBSCRIPTION_PLANS.get(subscription)
            if plan:
                return plan["max_chapters"]
    
    if single_book_credits > 0:
        return SINGLE_BOOK_MAX_CHAPTERS
    
    return 15


async def can_generate_cover(user: dict) -> bool:
    """Check if user can generate covers"""
    if not user:
        return False
    
    # Admin can always generate covers
    if is_user_admin(user):
        return True
    
    subscription = user.get("subscription")
    subscription_expires = user.get("subscription_expires")
    single_book_credits = user.get("single_book_credits", 0)
    
    if subscription and subscription_expires:
        expires = datetime.fromisoformat(subscription_expires) if isinstance(subscription_expires, str) else subscription_expires
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        if expires > datetime.now(timezone.utc):
            plan = SUBSCRIPTION_PLANS.get(subscription)
            if plan:
                return plan.get("cover_generation", False)
    
    # Single book credits do NOT include cover generation
    if single_book_credits > 0:
        return SINGLE_BOOK_COVER_GENERATION
    
    return False


# ==================== BOOK HELPERS ====================

def book_to_response(book: dict) -> BookResponse:
    return BookResponse(
        id=book['id'],
        user_id=book.get('user_id'),
        title=book['title'],
        idea=book['idea'],
        genre=book['genre'],
        tone=book['tone'],
        target_chapters=book['target_chapters'],
        language=book['language'],
        additional_info=book.get('additional_info'),
        cover_prompt=book.get('cover_prompt'),
        cover_image=book.get('cover_image'),
        status=book['status'],
        outline=book.get('outline', []),
        current_chapter=book.get('current_chapter', 0),
        total_word_count=book.get('total_word_count', 0),
        created_at=book['created_at'] if isinstance(book['created_at'], str) else book['created_at'].isoformat(),
        updated_at=book['updated_at'] if isinstance(book['updated_at'], str) else book['updated_at'].isoformat(),
        error_message=book.get('error_message')
    )


async def get_llm_chat(session_id: str, system_message: str) -> LlmChat:
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=session_id,
        system_message=system_message
    )
    chat.with_model("gemini", "gemini-3-flash-preview")
    return chat


def get_genre_description(genre: Genre) -> str:
    descriptions = {
        Genre.FICTION: "fiction générale avec des personnages et une intrigue captivante",
        Genre.NON_FICTION: "non-fiction informative et bien documentée",
        Genre.ROMANCE: "romance avec des relations émotionnelles profondes",
        Genre.THRILLER: "thriller haletant avec suspense et rebondissements",
        Genre.FANTASY: "fantasy avec des éléments magiques et des mondes imaginaires",
        Genre.SCIFI: "science-fiction avec technologies avancées et exploration",
        Genre.MYSTERY: "mystère avec enquête et résolution d'énigmes",
        Genre.HORROR: "horreur avec atmosphère terrifiante et tension",
        Genre.BIOGRAPHY: "biographie détaillée et captivante",
        Genre.SELF_HELP: "développement personnel avec conseils pratiques",
        Genre.HISTORY: "histoire documentée avec narration engageante",
        Genre.BUSINESS: "business et entrepreneuriat avec insights pratiques"
    }
    return descriptions.get(genre, "contenu de qualité")


def get_tone_description(tone: Tone) -> str:
    descriptions = {
        Tone.FORMAL: "un ton formel et professionnel",
        Tone.CASUAL: "un ton décontracté et accessible",
        Tone.LITERARY: "un ton littéraire et élégant",
        Tone.HUMOROUS: "un ton humoristique et léger",
        Tone.DRAMATIC: "un ton dramatique et intense",
        Tone.POETIC: "un ton poétique et lyrique"
    }
    return descriptions.get(tone, "un ton approprié")


# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_pw = hash_password(user_data.password)
    
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_pw,
        "picture": None,
        "subscription": None,
        "subscription_expires": None,
        "books_this_month": 0,
        "single_book_credits": 0,
        "month_reset": datetime.now(timezone.utc).strftime("%Y-%m"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_jwt_token(user_id, user_data.email)
    
    return TokenResponse(
        access_token=token,
        user=user_to_response(user_doc)
    )


@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Reset monthly counter if new month
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    if user.get("month_reset") != current_month:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"books_this_month": 0, "month_reset": current_month}}
        )
        user["books_this_month"] = 0
    
    token = create_jwt_token(user["user_id"], user["email"])
    
    return TokenResponse(
        access_token=token,
        user=user_to_response(user)
    )


@api_router.post("/auth/session")
async def process_google_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Session invalide")
        
        oauth_data = resp.json()
    
    email = oauth_data.get("email")
    name = oauth_data.get("name")
    picture = oauth_data.get("picture")
    session_token = oauth_data.get("session_token")
    
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture}}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "subscription": None,
            "subscription_expires": None,
            "books_this_month": 0,
            "single_book_credits": 0,
            "month_reset": datetime.now(timezone.utc).strftime("%Y-%m"),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    
    return user_to_response(user).model_dump()


@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(request: Request, session_token: Optional[str] = Cookie(default=None)):
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Reset monthly counter if new month
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    if user.get("month_reset") != current_month:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"books_this_month": 0, "month_reset": current_month}}
        )
        user["books_this_month"] = 0
    
    return user_to_response(user)


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, session_token: Optional[str] = Cookie(default=None)):
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Déconnecté"}


# ==================== USER ACCOUNT ROUTES ====================

@api_router.put("/account/profile")
async def update_profile(profile_data: ProfileUpdateRequest, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Update user profile information"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    update_fields = {}
    if profile_data.name:
        update_fields["name"] = profile_data.name
    
    if update_fields:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": update_fields}
        )
    
    updated_user = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return user_to_response(updated_user)


@api_router.post("/account/change-password")
async def change_password(password_data: PasswordChangeRequest, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Change user password"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Check if user has a password (not Google-only account)
    if not user.get("password_hash"):
        raise HTTPException(status_code=400, detail="Ce compte utilise uniquement la connexion Google")
    
    # Verify current password
    if not verify_password(password_data.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    # Validate new password
    if len(password_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit contenir au moins 6 caractères")
    
    # Hash and save new password
    new_hashed = hash_password(password_data.new_password)
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"password_hash": new_hashed}}
    )
    
    return {"message": "Mot de passe modifié avec succès"}


@api_router.get("/account/subscription")
async def get_subscription_details(request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Get detailed subscription information"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Check if admin
    is_admin = user.get("email") in ADMIN_EMAILS
    
    subscription = user.get("subscription")
    subscription_expires = user.get("subscription_expires")
    stripe_subscription_id = user.get("stripe_subscription_id")
    
    # Calculate subscription status
    is_active = False
    days_remaining = 0
    
    if is_admin:
        is_active = True
        subscription = "admin"
        days_remaining = -1  # Unlimited
    elif subscription and subscription_expires:
        expires = datetime.fromisoformat(subscription_expires) if isinstance(subscription_expires, str) else subscription_expires
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        if expires > now:
            is_active = True
            days_remaining = (expires - now).days
    
    plan_details = None
    if subscription and subscription in SUBSCRIPTION_PLANS:
        plan = SUBSCRIPTION_PLANS[subscription]
        plan_details = {
            "id": subscription,
            "name": plan["name"],
            "price": plan["price"],
            "books_per_month": plan["books_per_month"],
            "max_chapters": plan["max_chapters"],
            "cover_generation": plan["cover_generation"]
        }
    
    return {
        "is_active": is_active,
        "is_admin": is_admin,
        "subscription": subscription,
        "plan_details": plan_details,
        "expires": subscription_expires,
        "days_remaining": days_remaining,
        "books_this_month": user.get("books_this_month", 0),
        "single_book_credits": user.get("single_book_credits", 0),
        "stripe_subscription_id": stripe_subscription_id,
        "can_cancel": bool(stripe_subscription_id) and is_active and not is_admin
    }


@api_router.post("/account/cancel-subscription")
async def cancel_subscription(request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Cancel the current subscription"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Admin cannot cancel
    if user.get("email") in ADMIN_EMAILS:
        raise HTTPException(status_code=400, detail="Les comptes admin ne peuvent pas être annulés")
    
    stripe_subscription_id = user.get("stripe_subscription_id")
    if not stripe_subscription_id:
        raise HTTPException(status_code=400, detail="Aucun abonnement actif à annuler")
    
    try:
        # Cancel at period end (user keeps access until expiration)
        import stripe
        stripe.api_key = STRIPE_API_KEY
        stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"subscription_cancel_at_period_end": True}}
        )
        
        return {"message": "Abonnement annulé. Vous conservez l'accès jusqu'à la fin de la période en cours."}
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation de l'abonnement")


@api_router.post("/account/reactivate-subscription")
async def reactivate_subscription(request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Reactivate a canceled subscription (before it expires)"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    stripe_subscription_id = user.get("stripe_subscription_id")
    if not stripe_subscription_id:
        raise HTTPException(status_code=400, detail="Aucun abonnement à réactiver")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$unset": {"subscription_cancel_at_period_end": ""}}
        )
        
        return {"message": "Abonnement réactivé avec succès"}
    except Exception as e:
        logger.error(f"Error reactivating subscription: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la réactivation de l'abonnement")


# ==================== SUBSCRIPTION & PAYMENT ROUTES ====================

@api_router.get("/plans")
async def get_plans():
    """Get available subscription plans (excluding admin plan)"""
    plans = []
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        # Don't expose admin plan publicly
        if plan_id == "admin":
            continue
        plans.append({
            "id": plan_id,
            "name": plan["name"],
            "price": plan["price"],
            "books_per_month": plan["books_per_month"],
            "max_chapters": plan["max_chapters"],
            "cover_generation": plan["cover_generation"],
            "description": plan["description"],
            "popular": plan.get("popular", False)
        })
    return {
        "plans": plans,
        "single_book_price": SINGLE_BOOK_PRICE,
        "single_book_max_chapters": SINGLE_BOOK_MAX_CHAPTERS,
        "single_book_cover_generation": SINGLE_BOOK_COVER_GENERATION
    }


@api_router.post("/checkout/subscription")
async def create_subscription_checkout(checkout_req: CheckoutRequest, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Create Stripe checkout session for subscription"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Vous devez être connecté pour souscrire")
    
    plan_id = checkout_req.plan_id
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Plan invalide")
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{checkout_req.origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{checkout_req.origin_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=plan["price"],
        currency="eur",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["user_id"],
            "plan_id": plan_id,
            "type": "subscription"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    await db.payment_transactions.insert_one({
        "session_id": session.session_id,
        "user_id": user["user_id"],
        "plan_id": plan_id,
        "type": "subscription",
        "amount": plan["price"],
        "currency": "eur",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}


@api_router.post("/checkout/single-book")
async def create_single_book_checkout(checkout_req: SingleBookCheckoutRequest, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Create Stripe checkout session for single book purchase"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Vous devez être connecté pour acheter")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    success_url = f"{checkout_req.origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{checkout_req.origin_url}/pricing"
    
    checkout_request = CheckoutSessionRequest(
        amount=SINGLE_BOOK_PRICE,
        currency="eur",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["user_id"],
            "type": "single_book"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    await db.payment_transactions.insert_one({
        "session_id": session.session_id,
        "user_id": user["user_id"],
        "type": "single_book",
        "amount": SINGLE_BOOK_PRICE,
        "currency": "eur",
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}


@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, request: Request):
    """Get checkout session status and process payment"""
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Get transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    
    if transaction and transaction.get("payment_status") != "paid" and status.payment_status == "paid":
        # Update transaction
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "paid", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        user_id = transaction.get("user_id")
        payment_type = transaction.get("type")
        
        if payment_type == "subscription":
            plan_id = transaction.get("plan_id")
            expires = datetime.now(timezone.utc) + timedelta(days=30)
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "subscription": plan_id,
                    "subscription_expires": expires.isoformat(),
                    "books_this_month": 0
                }}
            )
        elif payment_type == "single_book":
            await db.users.update_one(
                {"user_id": user_id},
                {"$inc": {"single_book_credits": 1}}
            )
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount": status.amount_total,
        "currency": status.currency
    }


@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            session_id = webhook_response.session_id
            transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
            
            if transaction and transaction.get("payment_status") != "paid":
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"payment_status": "paid", "updated_at": datetime.now(timezone.utc).isoformat()}}
                )
                
                user_id = webhook_response.metadata.get("user_id")
                payment_type = webhook_response.metadata.get("type")
                
                if payment_type == "subscription":
                    plan_id = webhook_response.metadata.get("plan_id")
                    expires = datetime.now(timezone.utc) + timedelta(days=30)
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$set": {
                            "subscription": plan_id,
                            "subscription_expires": expires.isoformat(),
                            "books_this_month": 0
                        }}
                    )
                elif payment_type == "single_book":
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$inc": {"single_book_credits": 1}}
                    )
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


# ==================== BOOK ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "GlasEditionsLab API - Générateur de livres IA"}


@api_router.post("/books", response_model=BookResponse)
async def create_book(book_data: BookCreate, request: Request, session_token: Optional[str] = Cookie(default=None)):
    user = await get_current_user(request, session_token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Vous devez être connecté pour créer un livre")
    
    can_create, error_msg, plan = await check_user_can_create_book(user)
    if not can_create:
        raise HTTPException(status_code=403, detail=error_msg)
    
    # Check max chapters
    max_chapters = await get_user_max_chapters(user)
    if max_chapters != -1 and book_data.target_chapters > max_chapters:
        raise HTTPException(status_code=403, detail=f"Votre plan limite à {max_chapters} chapitres par livre")
    
    user_id = user["user_id"]
    
    book = Book(**book_data.model_dump(), user_id=user_id)
    doc = book.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.books.insert_one(doc)
    
    # Increment books count or decrement single book credit
    if user.get("single_book_credits", 0) > 0 and not user.get("subscription"):
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"single_book_credits": -1}}
        )
    else:
        await db.users.update_one(
            {"user_id": user_id},
            {"$inc": {"books_this_month": 1}}
        )
    
    return book_to_response(doc)


@api_router.get("/books", response_model=List[BookResponse])
async def get_books(request: Request, session_token: Optional[str] = Cookie(default=None)):
    user = await get_current_user(request, session_token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Vous devez être connecté pour voir vos livres")
    
    query = {"user_id": user["user_id"]}
    books = await db.books.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [book_to_response(b) for b in books]


@api_router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book_to_response(book)


@api_router.patch("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: str, update_data: BookUpdate, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Update book title"""
    user = await get_current_user(request, session_token)
    
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if user and book.get("user_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    update_fields = {}
    if update_data.title:
        update_fields["title"] = update_data.title
    
    if update_fields:
        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.books.update_one({"id": book_id}, {"$set": update_fields})
    
    updated_book = await db.books.find_one({"id": book_id}, {"_id": 0})
    return book_to_response(updated_book)


@api_router.delete("/books/{book_id}")
async def delete_book(book_id: str):
    result = await db.books.delete_one({"id": book_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return {"message": "Livre supprimé avec succès"}


@api_router.post("/books/{book_id}/generate-outline", response_model=BookResponse)
async def generate_outline(book_id: str, background_tasks: BackgroundTasks):
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    await db.books.update_one(
        {"id": book_id},
        {"$set": {"status": BookStatus.GENERATING_OUTLINE, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    background_tasks.add_task(generate_outline_task, book_id, book)
    
    book['status'] = BookStatus.GENERATING_OUTLINE
    return book_to_response(book)


async def generate_outline_task(book_id: str, book: dict):
    try:
        genre_desc = get_genre_description(Genre(book['genre']))
        tone_desc = get_tone_description(Tone(book['tone']))
        
        system_message = f"""Tu es un auteur professionnel expert en {genre_desc}. 
Tu dois créer des plans de livres détaillés et captivants avec {tone_desc}.
Tu réponds toujours en {book['language']}.
Tu génères UNIQUEMENT le contenu demandé, sans commentaires supplémentaires."""

        chat = await get_llm_chat(f"outline-{book_id}", system_message)
        
        additional = f"\nInformations supplémentaires: {book['additional_info']}" if book.get('additional_info') else ""
        
        prompt = f"""Crée un plan détaillé pour un livre avec les caractéristiques suivantes:

Titre: {book['title']}
Idée principale: {book['idea']}
Genre: {book['genre']}
Ton: {book['tone']}
Nombre de chapitres: {book['target_chapters']}{additional}

Pour chaque chapitre, fournis:
1. Un numéro
2. Un titre accrocheur
3. Un résumé de 2-3 phrases décrivant le contenu

Réponds UNIQUEMENT avec le format suivant pour chaque chapitre (un par ligne):
CHAPITRE [numéro] | [titre] | [résumé]

Génère exactement {book['target_chapters']} chapitres."""

        response = await chat.send_message(UserMessage(text=prompt))
        
        chapters = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('CHAPITRE'):
                parts = line.split('|')
                if len(parts) >= 3:
                    try:
                        num_part = parts[0].replace('CHAPITRE', '').strip()
                        num = int(num_part)
                        title = parts[1].strip()
                        summary = parts[2].strip()
                        chapters.append(Chapter(
                            number=num,
                            title=title,
                            summary=summary,
                            status="pending"
                        ).model_dump())
                    except (ValueError, IndexError):
                        continue
        
        if len(chapters) < 5:
            raise Exception("Impossible de parser le plan correctement")
        
        await db.books.update_one(
            {"id": book_id},
            {"$set": {
                "outline": chapters,
                "status": BookStatus.OUTLINE_READY,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        logger.info(f"Outline generated for book {book_id} with {len(chapters)} chapters")
        
    except Exception as e:
        logger.error(f"Error generating outline: {str(e)}")
        await db.books.update_one(
            {"id": book_id},
            {"$set": {
                "status": BookStatus.ERROR,
                "error_message": str(e),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )


@api_router.post("/books/{book_id}/generate-chapter/{chapter_num}", response_model=BookResponse)
async def generate_chapter(book_id: str, chapter_num: int, background_tasks: BackgroundTasks):
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if not book.get('outline'):
        raise HTTPException(status_code=400, detail="Le plan du livre doit d'abord être généré")
    
    if chapter_num < 1 or chapter_num > len(book['outline']):
        raise HTTPException(status_code=400, detail="Numéro de chapitre invalide")
    
    background_tasks.add_task(generate_chapter_task, book_id, book, chapter_num)
    
    return book_to_response(book)


async def generate_chapter_task(book_id: str, book: dict, chapter_num: int):
    try:
        chapter_index = chapter_num - 1
        chapter = book['outline'][chapter_index]
        
        genre_desc = get_genre_description(Genre(book['genre']))
        tone_desc = get_tone_description(Tone(book['tone']))
        
        previous_context = ""
        for i in range(max(0, chapter_index - 2), chapter_index):
            prev_ch = book['outline'][i]
            if prev_ch.get('content'):
                previous_context += f"\n--- Chapitre {prev_ch['number']}: {prev_ch['title']} ---\n"
                previous_context += prev_ch['content'][:2000] + "...\n"
        
        system_message = f"""Tu es un auteur professionnel expert en {genre_desc}.
Tu écris avec {tone_desc} en {book['language']}.
Tu produis un texte de haute qualité, prêt à être publié, sans erreurs.
Tu ne fais AUCUN commentaire sur ton travail, tu fournis uniquement le contenu du chapitre."""

        chat = await get_llm_chat(f"chapter-{book_id}-{chapter_num}-{datetime.now().timestamp()}", system_message)
        
        outline_summary = "\n".join([f"Ch.{ch['number']}: {ch['title']} - {ch['summary']}" for ch in book['outline']])
        
        prompt = f"""Écris le chapitre complet suivant pour le livre "{book['title']}":

PLAN GLOBAL DU LIVRE:
{outline_summary}

{f"CONTEXTE DES CHAPITRES PRÉCÉDENTS:{previous_context}" if previous_context else ""}

CHAPITRE À ÉCRIRE:
Numéro: {chapter['number']}
Titre: {chapter['title']}
Résumé: {chapter['summary']}

INSTRUCTIONS:
- Écris un chapitre complet d'environ 2000-3000 mots
- Commence directement par le contenu du chapitre (pas de "Chapitre X" en titre)
- Utilise des dialogues, des descriptions vivantes et une narration engageante
- Assure la cohérence avec les chapitres précédents
- Le texte doit être prêt à être publié, sans corrections nécessaires
- Écris en {book['language']}

Écris maintenant le chapitre complet:"""

        content = await chat.send_message(UserMessage(text=prompt))
        
        # Clean content - remove excessive whitespace and dashes
        content = clean_chapter_content(content)
        
        word_count = len(content.split())
        
        # Get current word count to subtract if regenerating
        old_word_count = chapter.get('word_count', 0)
        
        update_path = f"outline.{chapter_index}"
        await db.books.update_one(
            {"id": book_id},
            {"$set": {
                f"{update_path}.content": content,
                f"{update_path}.word_count": word_count,
                f"{update_path}.status": "completed",
                "current_chapter": chapter_num,
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "$inc": {"total_word_count": word_count - old_word_count}}
        )
        
        updated_book = await db.books.find_one({"id": book_id}, {"_id": 0})
        all_complete = all(ch.get('status') == 'completed' for ch in updated_book.get('outline', []))
        
        if all_complete:
            await db.books.update_one(
                {"id": book_id},
                {"$set": {"status": BookStatus.COMPLETED}}
            )
        
        logger.info(f"Chapter {chapter_num} generated for book {book_id}")
        
    except Exception as e:
        logger.error(f"Error generating chapter {chapter_num}: {str(e)}")
        await db.books.update_one(
            {"id": book_id},
            {"$set": {
                f"outline.{chapter_num-1}.status": "error",
                "status": BookStatus.ERROR,
                "error_message": f"Erreur chapitre {chapter_num}: {str(e)}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )


def clean_chapter_content(content: str) -> str:
    """Clean chapter content - remove excessive whitespace, dashes, etc."""
    import re
    
    # Remove lines that are just dashes or asterisks
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just separators
        if re.match(r'^[-*=_]{3,}$', stripped):
            continue
        # Skip empty lines at start/end but keep paragraph breaks
        cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Remove multiple consecutive blank lines (keep max 2)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # Remove leading/trailing whitespace
    content = content.strip()
    
    return content


@api_router.put("/books/{book_id}/chapters/{chapter_num}")
async def edit_chapter_content(book_id: str, chapter_num: int, chapter_data: ChapterEditRequest, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Edit the content of a specific chapter"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    # Check ownership
    if book.get("user_id") != user["user_id"] and user.get("email") not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire de ce livre")
    
    if not book.get('outline'):
        raise HTTPException(status_code=400, detail="Le plan du livre doit d'abord être généré")
    
    if chapter_num < 1 or chapter_num > len(book['outline']):
        raise HTTPException(status_code=400, detail="Numéro de chapitre invalide")
    
    chapter_index = chapter_num - 1
    
    # Calculate word count
    word_count = len(chapter_data.content.split()) if chapter_data.content else 0
    
    # Update chapter content
    await db.books.update_one(
        {"id": book_id},
        {"$set": {
            f"outline.{chapter_index}.content": chapter_data.content,
            f"outline.{chapter_index}.word_count": word_count,
            f"outline.{chapter_index}.status": "completed",
            f"outline.{chapter_index}.edited_manually": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Refresh book data
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    
    return book_to_response(book)


@api_router.post("/books/{book_id}/regenerate-chapter/{chapter_num}", response_model=BookResponse)
async def regenerate_chapter(book_id: str, chapter_num: int, background_tasks: BackgroundTasks, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Regenerate a specific chapter"""
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if not book.get('outline'):
        raise HTTPException(status_code=400, detail="Le plan du livre doit d'abord être généré")
    
    if chapter_num < 1 or chapter_num > len(book['outline']):
        raise HTTPException(status_code=400, detail="Numéro de chapitre invalide")
    
    # Mark chapter as pending/regenerating
    chapter_index = chapter_num - 1
    await db.books.update_one(
        {"id": book_id},
        {"$set": {
            f"outline.{chapter_index}.status": "generating",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Refresh book data
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    
    background_tasks.add_task(generate_chapter_task, book_id, book, chapter_num)
    
    return book_to_response(book)


@api_router.post("/books/{book_id}/generate-all", response_model=BookResponse)
async def generate_all_chapters(book_id: str, background_tasks: BackgroundTasks):
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if not book.get('outline'):
        raise HTTPException(status_code=400, detail="Le plan du livre doit d'abord être généré")
    
    await db.books.update_one(
        {"id": book_id},
        {"$set": {"status": BookStatus.GENERATING, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    background_tasks.add_task(generate_all_chapters_task, book_id)
    
    book['status'] = BookStatus.GENERATING
    return book_to_response(book)


async def generate_all_chapters_task(book_id: str):
    try:
        book = await db.books.find_one({"id": book_id}, {"_id": 0})
        
        for chapter in book['outline']:
            if chapter.get('status') != 'completed':
                current_book = await db.books.find_one({"id": book_id}, {"_id": 0})
                await generate_chapter_task(book_id, current_book, chapter['number'])
                await asyncio.sleep(2)
        
        await db.books.update_one(
            {"id": book_id},
            {"$set": {"status": BookStatus.COMPLETED, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
    except Exception as e:
        logger.error(f"Error in generate_all: {str(e)}")
        await db.books.update_one(
            {"id": book_id},
            {"$set": {
                "status": BookStatus.ERROR,
                "error_message": str(e),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )


# ==================== COVER GENERATION ====================

@api_router.post("/books/{book_id}/generate-cover", response_model=BookResponse)
async def generate_cover(book_id: str, cover_request: CoverGenerateRequest, background_tasks: BackgroundTasks, request: Request, session_token: Optional[str] = Cookie(default=None)):
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    # Check if user can generate covers
    user = await get_current_user(request, session_token)
    if not await can_generate_cover(user):
        raise HTTPException(status_code=403, detail="La génération de couvertures nécessite un abonnement Auteur ou Écrivain")
    
    custom_prompt = cover_request.prompt
    
    await db.books.update_one(
        {"id": book_id},
        {"$set": {
            "status": BookStatus.GENERATING_COVER,
            "cover_prompt": custom_prompt if custom_prompt else book.get('cover_prompt'),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    background_tasks.add_task(generate_cover_task, book_id, custom_prompt)
    
    book['status'] = BookStatus.GENERATING_COVER
    return book_to_response(book)


async def generate_cover_task(book_id: str, custom_prompt: Optional[str] = None):
    try:
        book = await db.books.find_one({"id": book_id}, {"_id": 0})
        
        genre_visual = {
            "fiction": "elegant literary design",
            "non_fiction": "professional and clean design",
            "romance": "romantic and emotional atmosphere with soft colors",
            "thriller": "dark and suspenseful atmosphere",
            "fantasy": "magical and mystical elements with epic scenery",
            "science_fiction": "futuristic and technological design",
            "mystery": "mysterious and intriguing atmosphere",
            "horror": "dark and eerie atmosphere",
            "biography": "portrait style with elegant typography",
            "self_help": "inspiring and uplifting design",
            "history": "historical and classic design",
            "business": "professional and modern corporate style"
        }
        
        genre_style = genre_visual.get(book['genre'], "elegant book cover design")
        
        if custom_prompt:
            prompt = f"Create a professional book cover image: {custom_prompt}. Style: {genre_style}. The image should be suitable for a book titled '{book['title']}'. High quality, artistic, no text on the image."
        else:
            prompt = f"Create a professional book cover image for a {book['genre']} book titled '{book['title']}'. The book is about: {book['idea'][:200]}. Style: {genre_style}. High quality, artistic, evocative imagery that captures the essence of the story. No text on the image, just visual imagery."
        
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"cover-{book_id}",
            system_message="You are an expert book cover designer creating stunning visual imagery."
        )
        chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
        
        text_response, images = await chat.send_message_multimodal_response(UserMessage(text=prompt))
        
        if images and len(images) > 0:
            cover_base64 = images[0]['data']
            mime_type = images[0].get('mime_type', 'image/png')
            cover_data_url = f"data:{mime_type};base64,{cover_base64}"
            
            previous_status = book.get('status', BookStatus.DRAFT)
            if previous_status == BookStatus.GENERATING_COVER:
                if book.get('outline') and all(ch.get('status') == 'completed' for ch in book['outline']):
                    previous_status = BookStatus.COMPLETED
                elif book.get('outline'):
                    previous_status = BookStatus.OUTLINE_READY
                else:
                    previous_status = BookStatus.DRAFT
            
            await db.books.update_one(
                {"id": book_id},
                {"$set": {
                    "cover_image": cover_data_url,
                    "status": previous_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.info(f"Cover generated for book {book_id}")
        else:
            raise Exception("No image generated")
            
    except Exception as e:
        logger.error(f"Error generating cover: {str(e)}")
        await db.books.update_one(
            {"id": book_id},
            {"$set": {
                "status": BookStatus.ERROR,
                "error_message": f"Erreur génération couverture: {str(e)}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )


# ==================== EXPORT ROUTES ====================

@api_router.get("/books/{book_id}/export/{format}")
async def export_book(book_id: str, format: str):
    if format not in ['txt', 'html', 'pdf', 'epub']:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'txt', 'html', 'pdf' ou 'epub'")
    
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    if format == 'txt':
        content = f"{book['title']}\n{'=' * len(book['title'])}\n\n"
        content += f"Genre: {book['genre']} | Ton: {book['tone']}\n"
        content += f"Idée: {book['idea']}\n\n"
        content += "=" * 50 + "\n\n"
        
        for chapter in book.get('outline', []):
            content += f"\nCHAPITRE {chapter['number']}: {chapter['title']}\n"
            content += "-" * 40 + "\n\n"
            if chapter.get('content'):
                content += chapter['content'] + "\n\n"
            else:
                content += "[Chapitre non encore généré]\n\n"
        
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={book['title']}.txt"}
        )
    
    elif format == 'html':
        html = generate_html_export(book)
        return StreamingResponse(
            io.BytesIO(html.encode('utf-8')),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={book['title']}.html"}
        )
    
    elif format == 'pdf':
        pdf_bytes = generate_pdf_export(book)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={book['title']}.pdf"}
        )
    
    elif format == 'epub':
        epub_bytes = generate_epub_export(book)
        return StreamingResponse(
            io.BytesIO(epub_bytes),
            media_type="application/epub+zip",
            headers={"Content-Disposition": f"attachment; filename={book['title']}.epub"}
        )


def generate_html_export(book: dict) -> str:
    cover_html = ""
    if book.get('cover_image'):
        cover_html = f'<div class="cover"><img src="{book["cover_image"]}" alt="Couverture" /></div>'
    
    toc_html = "<div class='toc'><h2>Table des matières</h2><ul>"
    for ch in book.get('outline', []):
        toc_html += f"<li><a href='#chapter-{ch['number']}'>Chapitre {ch['number']}: {ch['title']}</a></li>"
    toc_html += "</ul></div>"
    
    chapters_html = ""
    for chapter in book.get('outline', []):
        chapters_html += f"<div class='chapter' id='chapter-{chapter['number']}'>"
        chapters_html += f"<h2>Chapitre {chapter['number']}</h2>"
        chapters_html += f"<h3>{chapter['title']}</h3>"
        if chapter.get('content'):
            paragraphs = chapter['content'].split('\n\n')
            for p in paragraphs:
                if p.strip():
                    chapters_html += f"<p>{p.strip()}</p>"
        else:
            chapters_html += "<p><em>[Chapitre non encore généré]</em></p>"
        chapters_html += "</div>"
    
    html = f"""<!DOCTYPE html>
<html lang="{book['language']}">
<head>
    <meta charset="UTF-8">
    <title>{book['title']}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Playfair+Display:wght@400;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Merriweather', Georgia, serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.9; color: #1C1917; background: #FDFBF7; }}
        .cover {{ text-align: center; margin-bottom: 60px; page-break-after: always; }}
        .cover img {{ max-width: 100%; max-height: 600px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
        h1 {{ font-family: 'Playfair Display', serif; font-size: 3em; text-align: center; margin: 40px 0 20px; }}
        .meta {{ text-align: center; color: #78716C; margin-bottom: 40px; font-style: italic; }}
        .toc {{ margin: 40px 0; padding: 30px; background: #F5F5F4; page-break-after: always; }}
        .toc h2 {{ font-family: 'Playfair Display', serif; margin-bottom: 20px; }}
        .toc ul {{ list-style: none; }}
        .toc li {{ padding: 8px 0; border-bottom: 1px solid #E7E5E4; }}
        .toc a {{ color: #1C1917; text-decoration: none; }}
        .toc a:hover {{ color: #B45309; }}
        .chapter {{ margin: 60px 0; page-break-before: always; }}
        .chapter h2 {{ font-family: 'Playfair Display', serif; font-size: 1.2em; color: #78716C; margin-bottom: 10px; }}
        .chapter h3 {{ font-family: 'Playfair Display', serif; font-size: 2em; margin-bottom: 30px; }}
        p {{ text-indent: 2em; margin: 1em 0; text-align: justify; }}
        p:first-of-type {{ text-indent: 0; }}
        @media print {{
            body {{ padding: 0; }}
            .chapter {{ page-break-before: always; }}
        }}
    </style>
</head>
<body>
    {cover_html}
    <h1>{book['title']}</h1>
    <p class="meta">Genre: {book['genre']} | Ton: {book['tone']}</p>
    {toc_html}
    {chapters_html}
</body>
</html>"""
    return html


def generate_pdf_export(book: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
    import tempfile
    
    buffer = io.BytesIO()
    
    # Custom page template for page numbers
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"- {page_num} -"
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawCentredString(A4[0] / 2, 1.5 * cm, text)
        canvas.restoreState()
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        leftMargin=2.5*cm, 
        rightMargin=2.5*cm, 
        topMargin=2*cm, 
        bottomMargin=2.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'BookTitle',
        parent=styles['Title'],
        fontSize=28,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    chapter_title_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceBefore=30,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BookBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        firstLineIndent=1*cm,
        spaceBefore=0,
        spaceAfter=8
    )
    
    first_para_style = ParagraphStyle(
        'FirstPara',
        parent=body_style,
        firstLineIndent=0
    )
    
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor='grey'
    )
    
    toc_style = ParagraphStyle(
        'TOC',
        parent=styles['Normal'],
        fontSize=12,
        spaceBefore=8,
        spaceAfter=8
    )
    
    story = []
    tmp_path = None
    
    # Cover image if exists
    if book.get('cover_image') and book['cover_image'].startswith('data:'):
        try:
            header, data = book['cover_image'].split(',', 1)
            img_data = base64.b64decode(data)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(img_data)
                tmp_path = tmp.name
            
            img = RLImage(tmp_path, width=14*cm, height=18*cm)
            story.append(Spacer(1, 1*cm))
            story.append(img)
            story.append(PageBreak())
        except Exception as e:
            logger.error(f"Error adding cover to PDF: {e}")
    
    # Title page
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph(book['title'], title_style))
    story.append(Spacer(1, 1*cm))
    genre_display = book['genre'].replace('_', ' ').title()
    tone_display = book['tone'].title()
    story.append(Paragraph(f"Genre: {genre_display} | Ton: {tone_display}", meta_style))
    story.append(Spacer(1, 0.5*cm))
    idea_text = book['idea'][:300] + "..." if len(book['idea']) > 300 else book['idea']
    story.append(Paragraph(f"<i>{idea_text}</i>", meta_style))
    story.append(PageBreak())
    
    # Table of contents
    story.append(Paragraph("Table des matières", chapter_title_style))
    story.append(Spacer(1, 1*cm))
    
    for ch in book.get('outline', []):
        story.append(Paragraph(f"Chapitre {ch['number']}: {ch['title']}", toc_style))
    
    story.append(PageBreak())
    
    # Chapters
    for chapter in book.get('outline', []):
        story.append(Paragraph(f"Chapitre {chapter['number']}", meta_style))
        story.append(Paragraph(chapter['title'], chapter_title_style))
        story.append(Spacer(1, 0.5*cm))
        
        if chapter.get('content'):
            paragraphs = chapter['content'].split('\n\n')
            first_para = True
            for p in paragraphs:
                p = p.strip()
                if p:
                    # Clean the text for PDF
                    clean_text = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    # Remove excessive dashes or asterisks
                    if not clean_text.startswith('---') and not clean_text.startswith('***'):
                        if first_para:
                            story.append(Paragraph(clean_text, first_para_style))
                            first_para = False
                        else:
                            story.append(Paragraph(clean_text, body_style))
        else:
            story.append(Paragraph("<i>[Chapitre non encore généré]</i>", body_style))
        
        story.append(PageBreak())
    
    # Build PDF with page numbers
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    # Clean up temp file
    if tmp_path:
        try:
            import os
            os.unlink(tmp_path)
        except:
            pass
    
    return buffer.getvalue()


def generate_epub_export(book: dict) -> bytes:
    """Generate EPUB export using ebooklib"""
    from ebooklib import epub
    
    # Create EPUB book
    epub_book = epub.EpubBook()
    
    # Set metadata
    epub_book.set_identifier(book['id'])
    epub_book.set_title(book['title'])
    epub_book.set_language(book.get('language', 'fr'))
    epub_book.add_author('GlasEditionsLab')
    
    # Add description
    epub_book.add_metadata('DC', 'description', book.get('idea', '')[:500])
    epub_book.add_metadata('DC', 'subject', book.get('genre', 'fiction').replace('_', ' '))
    
    # Cover image if exists
    if book.get('cover_image') and book['cover_image'].startswith('data:'):
        try:
            header, data = book['cover_image'].split(',', 1)
            img_data = base64.b64decode(data)
            epub_book.set_cover("cover.png", img_data)
        except Exception as e:
            logger.warning(f"Could not add cover to EPUB: {e}")
    
    # CSS for styling
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        margin: 1em;
    }
    h1 {
        text-align: center;
        font-size: 2em;
        margin-bottom: 1em;
    }
    h2 {
        text-align: center;
        font-size: 1.5em;
        color: #666;
        margin-bottom: 0.5em;
    }
    h3 {
        text-align: center;
        font-size: 1.3em;
        margin-bottom: 1.5em;
    }
    p {
        text-indent: 1.5em;
        margin: 0.5em 0;
        text-align: justify;
    }
    p.first {
        text-indent: 0;
    }
    .meta {
        text-align: center;
        color: #888;
        font-style: italic;
        margin: 1em 0;
    }
    .toc-title {
        text-align: center;
        font-size: 1.5em;
        margin-bottom: 1em;
    }
    .toc-item {
        margin: 0.5em 0;
    }
    '''
    
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    epub_book.add_item(nav_css)
    
    # Title page
    title_content = f'''
    <html>
    <head><link href="style/nav.css" rel="stylesheet" type="text/css"/></head>
    <body>
        <h1>{book['title']}</h1>
        <p class="meta">Genre: {book.get('genre', '').replace('_', ' ').title()}</p>
        <p class="meta">Ton: {book.get('tone', '').title()}</p>
        <p class="meta">{book.get('idea', '')[:300]}{'...' if len(book.get('idea', '')) > 300 else ''}</p>
    </body>
    </html>
    '''
    title_page = epub.EpubHtml(title='Titre', file_name='title.xhtml', lang='fr')
    title_page.content = title_content
    title_page.add_item(nav_css)
    epub_book.add_item(title_page)
    
    # Chapters
    chapters = []
    spine = ['nav', title_page]
    
    for chapter in book.get('outline', []):
        ch_num = chapter['number']
        ch_title = chapter['title']
        ch_content = chapter.get('content', '[Chapitre non encore généré]')
        
        # Format paragraphs
        paragraphs = ch_content.split('\n\n') if ch_content else []
        para_html = ""
        first_para = True
        for p in paragraphs:
            p = p.strip()
            if p:
                # Skip separator lines
                if p.startswith('---') or p.startswith('***'):
                    continue
                css_class = ' class="first"' if first_para else ''
                para_html += f'<p{css_class}>{p}</p>\n'
                first_para = False
        
        chapter_content = f'''
        <html>
        <head><link href="style/nav.css" rel="stylesheet" type="text/css"/></head>
        <body>
            <h2>Chapitre {ch_num}</h2>
            <h3>{ch_title}</h3>
            {para_html}
        </body>
        </html>
        '''
        
        epub_chapter = epub.EpubHtml(
            title=f'Chapitre {ch_num}: {ch_title}',
            file_name=f'chapter_{ch_num}.xhtml',
            lang='fr'
        )
        epub_chapter.content = chapter_content
        epub_chapter.add_item(nav_css)
        epub_book.add_item(epub_chapter)
        chapters.append(epub_chapter)
        spine.append(epub_chapter)
    
    # Table of contents
    epub_book.toc = [title_page] + chapters
    
    # Add navigation files
    epub_book.add_item(epub.EpubNcx())
    epub_book.add_item(epub.EpubNav())
    
    # Set spine
    epub_book.spine = spine
    
    # Write to bytes
    buffer = io.BytesIO()
    epub.write_epub(buffer, epub_book, {})
    return buffer.getvalue()


# Include router and middleware

# ==================== ADMIN ROUTES ====================

async def require_admin(request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Helper to verify admin access"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    if user.get("email") not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return user


@api_router.get("/admin/stats")
async def get_admin_stats(request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Get global platform statistics"""
    await require_admin(request, session_token)
    
    total_users = await db.users.count_documents({})
    total_books = await db.books.count_documents({})
    
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    books_this_month = await db.books.count_documents({
        "created_at": {"$gte": month_start.isoformat()}
    })
    
    # Subscription distribution
    pipeline = [
        {"$group": {"_id": "$subscription", "count": {"$sum": 1}}}
    ]
    sub_cursor = db.users.aggregate(pipeline)
    sub_dist = {}
    async for doc in sub_cursor:
        key = doc["_id"] if doc["_id"] else "sans_abonnement"
        sub_dist[key] = doc["count"]
    
    # Users without any subscription AND no single book credits
    no_plan_users = await db.users.count_documents({
        "$and": [
            {"$or": [{"subscription": None}, {"subscription": {"$exists": False}}]},
            {"$or": [{"single_book_credits": 0}, {"single_book_credits": {"$exists": False}}]}
        ],
        "email": {"$nin": ADMIN_EMAILS}
    })
    
    # Revenue estimation
    revenue = 0
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        if plan_id in sub_dist and plan_id != "admin":
            revenue += sub_dist.get(plan_id, 0) * plan["price"]
    
    return {
        "total_users": total_users,
        "total_books": total_books,
        "books_this_month": books_this_month,
        "subscription_distribution": sub_dist,
        "no_plan_users": no_plan_users,
        "estimated_monthly_revenue": revenue
    }


@api_router.get("/admin/users")
async def get_admin_users(
    request: Request,
    session_token: Optional[str] = Cookie(default=None),
    search: Optional[str] = None,
    plan: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get paginated user list with filters"""
    await require_admin(request, session_token)
    
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if plan:
        if plan == "sans_abonnement":
            query["$and"] = query.get("$and", []) + [
                {"$or": [{"subscription": None}, {"subscription": {"$exists": False}}]},
                {"$or": [{"single_book_credits": 0}, {"single_book_credits": {"$exists": False}}]}
            ]
            query["email"] = {"$nin": ADMIN_EMAILS}
        elif plan == "credits_only":
            query["single_book_credits"] = {"$gt": 0}
            if "$or" not in query:
                query["$or"] = [{"subscription": None}, {"subscription": {"$exists": False}}]
        else:
            query["subscription"] = plan
    
    skip = (page - 1) * limit
    total = await db.users.count_documents(query)
    
    users_cursor = db.users.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    users = []
    async for u in users_cursor:
        book_count = await db.books.count_documents({"user_id": u.get("user_id")})
        users.append({
            "user_id": u.get("user_id"),
            "name": u.get("name", ""),
            "email": u.get("email", ""),
            "subscription": u.get("subscription"),
            "subscription_expires": u.get("subscription_expires"),
            "single_book_credits": u.get("single_book_credits", 0),
            "books_count": book_count,
            "books_this_month": u.get("books_this_month", 0),
            "created_at": u.get("created_at", ""),
            "is_admin": u.get("email") in ADMIN_EMAILS
        })
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": max(1, -(-total // limit))
    }


@api_router.get("/admin/users/export")
async def export_admin_users(
    request: Request,
    session_token: Optional[str] = Cookie(default=None),
    search: Optional[str] = None,
    plan: Optional[str] = None
):
    """Export filtered users as CSV"""
    await require_admin(request, session_token)
    
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if plan:
        if plan == "sans_abonnement":
            query["$and"] = query.get("$and", []) + [
                {"$or": [{"subscription": None}, {"subscription": {"$exists": False}}]},
                {"$or": [{"single_book_credits": 0}, {"single_book_credits": {"$exists": False}}]}
            ]
            query["email"] = {"$nin": ADMIN_EMAILS}
        elif plan == "credits_only":
            query["single_book_credits"] = {"$gt": 0}
            if "$or" not in query:
                query["$or"] = [{"subscription": None}, {"subscription": {"$exists": False}}]
        else:
            query["subscription"] = plan
    
    users_cursor = db.users.find(query, {"_id": 0}).sort("created_at", -1)
    
    import csv
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["Nom", "Email", "Abonnement", "Crédits livres", "Livres créés", "Livres ce mois", "Date d'inscription"])
    
    async for u in users_cursor:
        book_count = await db.books.count_documents({"user_id": u.get("user_id")})
        sub = u.get("subscription") or "Aucun"
        if u.get("email") in ADMIN_EMAILS:
            sub = "Admin"
        writer.writerow([
            u.get("name", ""),
            u.get("email", ""),
            sub,
            u.get("single_book_credits", 0),
            book_count,
            u.get("books_this_month", 0),
            u.get("created_at", "")[:10] if u.get("created_at") else ""
        ])
    
    csv_content = output.getvalue().encode('utf-8-sig')
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=utilisateurs_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@api_router.delete("/admin/users/{user_id}")
async def delete_admin_user(user_id: str, request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Delete a user and their books"""
    admin = await require_admin(request, session_token)
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.get("email") in ADMIN_EMAILS:
        raise HTTPException(status_code=400, detail="Impossible de supprimer un compte administrateur")
    
    await db.books.delete_many({"user_id": user_id})
    await db.users.delete_one({"user_id": user_id})
    
    return {"message": f"Utilisateur {user.get('email')} et ses livres supprimés"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
