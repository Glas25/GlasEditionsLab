from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
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
from datetime import datetime, timezone
from enum import Enum
import io
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# LLM Setup
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Enums
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
    COMPLETED = "completed"
    ERROR = "error"


# Pydantic Models
class ChapterOutline(BaseModel):
    number: int
    title: str
    summary: str


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


class Book(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    idea: str
    genre: Genre
    tone: Tone
    target_chapters: int
    language: str
    additional_info: Optional[str] = None
    status: BookStatus = BookStatus.DRAFT
    outline: List[Chapter] = []
    current_chapter: int = 0
    total_word_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None


class BookResponse(BaseModel):
    id: str
    title: str
    idea: str
    genre: str
    tone: str
    target_chapters: int
    language: str
    additional_info: Optional[str]
    status: str
    outline: List[Chapter]
    current_chapter: int
    total_word_count: int
    created_at: str
    updated_at: str
    error_message: Optional[str]


# Helper Functions
def book_to_response(book: dict) -> BookResponse:
    return BookResponse(
        id=book['id'],
        title=book['title'],
        idea=book['idea'],
        genre=book['genre'],
        tone=book['tone'],
        target_chapters=book['target_chapters'],
        language=book['language'],
        additional_info=book.get('additional_info'),
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


# API Routes
@api_router.get("/")
async def root():
    return {"message": "GlasEditionsLab API - Générateur de livres IA"}


@api_router.post("/books", response_model=BookResponse)
async def create_book(book_data: BookCreate):
    book = Book(**book_data.model_dump())
    doc = book.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.books.insert_one(doc)
    return book_to_response(doc)


@api_router.get("/books", response_model=List[BookResponse])
async def get_books():
    books = await db.books.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
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
    
    # Update status
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
        
        # Parse response
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
        
        # Get previous chapters context
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
        
        # Update the specific chapter
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
        
        # Check if all chapters are complete
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
                # Refresh book data for each chapter
                current_book = await db.books.find_one({"id": book_id}, {"_id": 0})
                await generate_chapter_task(book_id, current_book, chapter['number'])
                await asyncio.sleep(2)  # Small delay between chapters
        
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


@api_router.get("/books/{book_id}/export/{format}")
async def export_book(book_id: str, format: str):
    if format not in ['txt', 'html']:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'txt' ou 'html'")
    
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
    
    else:  # HTML
        html = f"""<!DOCTYPE html>
<html lang="{book['language']}">
<head>
    <meta charset="UTF-8">
    <title>{book['title']}</title>
    <style>
        body {{ font-family: 'Merriweather', Georgia, serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.8; color: #1C1917; background: #FDFBF7; }}
        h1 {{ font-family: 'Playfair Display', serif; font-size: 2.5em; text-align: center; margin-bottom: 0.5em; }}
        .meta {{ text-align: center; color: #78716C; margin-bottom: 3em; }}
        h2 {{ font-family: 'Playfair Display', serif; margin-top: 3em; page-break-before: always; }}
        p {{ text-indent: 2em; margin: 1em 0; }}
    </style>
</head>
<body>
    <h1>{book['title']}</h1>
    <p class="meta">Genre: {book['genre']} | Ton: {book['tone']}</p>
"""
        for chapter in book.get('outline', []):
            html += f"<h2>Chapitre {chapter['number']}: {chapter['title']}</h2>\n"
            if chapter.get('content'):
                paragraphs = chapter['content'].split('\n\n')
                for p in paragraphs:
                    if p.strip():
                        html += f"<p>{p.strip()}</p>\n"
            else:
                html += "<p><em>[Chapitre non encore généré]</em></p>\n"
        
        html += "</body></html>"
        
        return StreamingResponse(
            io.BytesIO(html.encode('utf-8')),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={book['title']}.html"}
        )


# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
