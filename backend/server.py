from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Request, Response, Depends, Cookie
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
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

EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')
JWT_SECRET = os.environ.get('JWT_SECRET', 'glaseditions-secret-key-2025')
JWT_ALGORITHM = "HS256"

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


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


class BookCreate(BaseModel):
    title: str
    idea: str
    genre: Genre
    tone: Tone
    target_chapters: int = Field(default=25, ge=10, le=50)
    language: str = "français"
    additional_info: Optional[str] = None
    cover_prompt: Optional[str] = None


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


# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request, session_token: Optional[str] = Cookie(default=None)) -> Optional[dict]:
    """Get current user from session cookie or Authorization header"""
    token = None
    
    # Check cookie first
    if session_token:
        token = session_token
    else:
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return None
    
    # Check if it's a Google OAuth session token
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
    
    # Check if it's a JWT token
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
    """Require authentication - raises 401 if not authenticated"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user


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
    """Register a new user with email/password"""
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
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_jwt_token(user_id, user_data.email)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user_id,
            email=user_data.email,
            name=user_data.name,
            picture=None,
            created_at=user_doc["created_at"]
        )
    )


@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email/password"""
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_jwt_token(user["user_id"], user["email"])
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            name=user["name"],
            picture=user.get("picture"),
            created_at=user["created_at"]
        )
    )


@api_router.post("/auth/session")
async def process_google_session(request: Request, response: Response):
    """Process Google OAuth session_id and create session"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")
    
    # Exchange session_id for user data
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
    
    # Find or create user
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        # Update user info
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
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Store session
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Set cookie
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
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user["name"],
        "picture": user.get("picture"),
        "created_at": user["created_at"]
    }


@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Get current authenticated user"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        name=user["name"],
        picture=user.get("picture"),
        created_at=user["created_at"]
    )


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, session_token: Optional[str] = Cookie(default=None)):
    """Logout user"""
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Déconnecté"}


# ==================== BOOK ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "GlasEditionsLab API - Générateur de livres IA"}


@api_router.post("/books", response_model=BookResponse)
async def create_book(book_data: BookCreate, request: Request, session_token: Optional[str] = Cookie(default=None)):
    user = await get_current_user(request, session_token)
    user_id = user["user_id"] if user else None
    
    book = Book(**book_data.model_dump(), user_id=user_id)
    doc = book.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.books.insert_one(doc)
    return book_to_response(doc)


@api_router.get("/books", response_model=List[BookResponse])
async def get_books(request: Request, session_token: Optional[str] = Cookie(default=None)):
    user = await get_current_user(request, session_token)
    
    query = {}
    if user:
        # Show user's books + public books (no user_id)
        query = {"$or": [{"user_id": user["user_id"]}, {"user_id": None}]}
    
    books = await db.books.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [book_to_response(b) for b in books]


@api_router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str):
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return book_to_response(book)


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

Exemple:
CHAPITRE 1 | Le commencement | Description du début de l'histoire où le protagoniste découvre...
CHAPITRE 2 | La révélation | Suite de l'histoire avec...

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

        chat = await get_llm_chat(f"chapter-{book_id}-{chapter_num}", system_message)
        
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
        
        word_count = len(content.split())
        
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
            "$inc": {"total_word_count": word_count}}
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
async def generate_cover(book_id: str, cover_request: CoverGenerateRequest, background_tasks: BackgroundTasks):
    book = await db.books.find_one({"id": book_id}, {"_id": 0})
    if not book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
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
    if format not in ['txt', 'html', 'pdf']:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'txt', 'html' ou 'pdf'")
    
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
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import tempfile
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2.5*cm, rightMargin=2.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    
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
        spaceBefore=6,
        spaceAfter=6
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
    
    # Cover image if exists
    if book.get('cover_image') and book['cover_image'].startswith('data:'):
        try:
            header, data = book['cover_image'].split(',', 1)
            img_data = base64.b64decode(data)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(img_data)
                tmp_path = tmp.name
            
            img = RLImage(tmp_path, width=14*cm, height=18*cm)
            story.append(img)
            story.append(PageBreak())
            
            import os
            os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"Error adding cover to PDF: {e}")
    
    # Title page
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph(book['title'], title_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Genre: {book['genre']} | Ton: {book['tone']}", meta_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<i>{book['idea'][:200]}...</i>", meta_style))
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
            for p in paragraphs:
                if p.strip():
                    clean_text = p.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(clean_text, body_style))
        else:
            story.append(Paragraph("<i>[Chapitre non encore généré]</i>", body_style))
        
        story.append(PageBreak())
    
    doc.build(story)
    return buffer.getvalue()


# Include router and middleware
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
