# GlasEditionsLab - PRD (Product Requirements Document)

## Original Problem Statement
Construire un générateur de livres comme GlasEditionsLab, pour écrire des livres de fiction et de non-fiction, sans que l'utilisateur n'ait besoin de corriger aucune phrase, et sans supervision. Juste à partir d'une idée et quelques renseignements de départ.

## User Choices
- **LLM**: Gemini 3 Flash avec Emergent LLM Universal Key
- **Theme**: Thème clair, style riche
- **Features**: Structure/plan, génération chapitre par chapitre, choix du genre/ton, export TXT/HTML
- **Book Length**: Livres moyens (20-40 chapitres)
- **Language**: Français (configurable)

## Architecture

### Backend (FastAPI + MongoDB)
- **Framework**: FastAPI avec async support
- **Database**: MongoDB via Motor (async driver)
- **AI Integration**: Gemini 3 Flash via emergentintegrations library
- **Key Files**:
  - `/app/backend/server.py` - Main API server
  - `/app/backend/.env` - Environment variables

### Frontend (React + Tailwind + Shadcn)
- **Framework**: React 19 with React Router
- **Styling**: Tailwind CSS with custom design system
- **Components**: Shadcn/UI from `/app/frontend/src/components/ui/`
- **Key Files**:
  - `/app/frontend/src/App.js` - Main router
  - `/app/frontend/src/pages/` - All page components

## User Personas
1. **Aspirant Author**: Wants to quickly produce a full book from an idea
2. **Content Creator**: Needs bulk content for publishing platforms
3. **Business Professional**: Needs non-fiction books (self-help, business)

## Core Requirements (Static)
- [x] Create book from idea with genre/tone selection
- [x] Automatic outline/structure generation
- [x] Chapter-by-chapter automatic generation
- [x] Progress tracking and visualization
- [x] Book reader with chapter navigation
- [x] Export to TXT and HTML formats
- [x] Book library with search/filters

## What's Been Implemented (January 2026)

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/books` | POST | Create new book |
| `/api/books` | GET | List all books |
| `/api/books/{id}` | GET | Get book details |
| `/api/books/{id}` | DELETE | Delete book |
| `/api/books/{id}/generate-outline` | POST | Generate book outline with AI |
| `/api/books/{id}/generate-chapter/{num}` | POST | Generate single chapter |
| `/api/books/{id}/generate-all` | POST | Generate all chapters |
| `/api/books/{id}/export/{format}` | GET | Export book (txt/html) |

### Pages Implemented
- **Landing Page** (`/`) - Hero section, features, CTA
- **Create Book** (`/create`) - 3-step wizard
- **Dashboard** (`/dashboard`) - Active books overview
- **Book View** (`/book/:id`) - Reader with chapter list
- **Library** (`/library`) - All books with filters

### Genres Supported
Fiction, Non-Fiction, Romance, Thriller, Fantasy, Science-Fiction, Mystery, Horror, Biography, Self-Help, History, Business

### Tones Supported
Formal, Casual, Literary, Humorous, Dramatic, Poetic

## Prioritized Backlog

### P0 - Critical (Completed ✅)
- [x] Book creation wizard
- [x] AI outline generation
- [x] AI chapter generation
- [x] Book reader interface
- [x] Export functionality

### P1 - High Priority (Next Phase)
- [ ] PDF/EPUB export (requires additional library)
- [ ] User authentication system
- [ ] Book editing/revision capabilities
- [ ] Cover image generation

### P2 - Medium Priority
- [ ] Multiple book versions/drafts
- [ ] Collaborative editing
- [ ] Publishing integration (Amazon KDP, etc.)
- [ ] AI style customization

## Next Tasks
1. Add PDF export using reportlab or weasyprint
2. Implement user authentication (JWT or Google OAuth)
3. Add book cover generation with AI image
4. Enable chapter content editing
5. Add "Continue writing" feature for unfinished books
