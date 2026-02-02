# GlasEditionsLab - PRD (Product Requirements Document)

## Original Problem Statement
Construire un générateur de livres comme OneBookLab, pour écrire des livres de fiction et de non-fiction, sans que l'utilisateur n'ait besoin de corriger aucune phrase, et sans supervision. Juste à partir d'une idée et quelques renseignements de départ.

## User Choices
- **LLM**: Gemini 3 Flash avec Emergent LLM Universal Key
- **Theme**: Thème clair, style riche
- **Features**: Structure/plan, génération chapitre par chapitre, choix du genre/ton, export PDF/TXT/HTML
- **Book Length**: Livres moyens (20-40 chapitres)
- **Language**: Français (configurable)
- **Authentication**: JWT (email/password) + Google OAuth via Emergent
- **Cover Generation**: Gemini Nano Banana avec prompt personnalisable
- **Export**: Style riche (couverture, table des matières, mise en page soignée)

## Architecture

### Backend (FastAPI + MongoDB)
- **Framework**: FastAPI avec async support
- **Database**: MongoDB via Motor (async driver)
- **AI Integration**: 
  - Gemini 3 Flash pour le texte (emergentintegrations)
  - Gemini Nano Banana pour les couvertures (emergentintegrations)
- **Authentication**: JWT + Google OAuth via Emergent Auth
- **Export**: reportlab pour PDF
- **Key Files**:
  - `/app/backend/server.py` - Main API server
  - `/app/backend/.env` - Environment variables

### Frontend (React + Tailwind + Shadcn)
- **Framework**: React 19 with React Router
- **Styling**: Tailwind CSS with custom design system
- **Components**: Shadcn/UI from `/app/frontend/src/components/ui/`
- **Key Files**:
  - `/app/frontend/src/App.js` - Main router with AuthProvider
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
- [x] Export to TXT, HTML, PDF formats
- [x] Book library with search/filters
- [x] User authentication (JWT + Google OAuth)
- [x] AI cover generation with custom prompts
- [x] Rich PDF export with cover and TOC

## What's Been Implemented (January-February 2026)

### Phase 1 - MVP (January 2026)
- Book creation wizard (3 steps)
- Gemini 3 Flash integration for text
- Outline and chapter generation
- TXT/HTML export
- Dashboard and Library pages

### Phase 2 - Enhanced Features (February 2026)
- **Authentication System**:
  - JWT-based email/password login/register
  - Google OAuth via Emergent Auth
  - Session management with cookies
  - User-specific book filtering
- **AI Cover Generation**:
  - Gemini Nano Banana integration
  - Custom prompt support
  - Genre-based automatic styling
- **PDF Export**:
  - reportlab integration
  - Cover image inclusion
  - Table of contents
  - Professional typography

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register with email/password |
| `/api/auth/login` | POST | Login with email/password |
| `/api/auth/session` | POST | Process Google OAuth session |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/logout` | POST | Logout user |
| `/api/books` | POST | Create new book |
| `/api/books` | GET | List all books |
| `/api/books/{id}` | GET | Get book details |
| `/api/books/{id}` | DELETE | Delete book |
| `/api/books/{id}/generate-outline` | POST | Generate book outline |
| `/api/books/{id}/generate-chapter/{num}` | POST | Generate single chapter |
| `/api/books/{id}/generate-all` | POST | Generate all chapters |
| `/api/books/{id}/generate-cover` | POST | Generate AI cover |
| `/api/books/{id}/export/{format}` | GET | Export (txt/html/pdf) |

### Pages Implemented
- **Landing Page** (`/`) - Hero + features + auth links
- **Login** (`/login`) - Email/password + Google OAuth
- **Register** (`/register`) - Account creation
- **Create Book** (`/create`) - 3-step wizard
- **Dashboard** (`/dashboard`) - Active books overview
- **Book View** (`/book/:id`) - Reader + cover generation
- **Library** (`/library`) - All books with filters

## Prioritized Backlog

### P0 - Critical (Completed ✅)
- [x] Book creation wizard
- [x] AI outline generation
- [x] AI chapter generation
- [x] Book reader interface
- [x] Export functionality (TXT, HTML, PDF)
- [x] User authentication
- [x] AI cover generation

### P1 - High Priority (Next Phase)
- [ ] EPUB export format
- [ ] Book editing/revision capabilities
- [ ] Multiple book versions/drafts
- [ ] Chapter regeneration options

### P2 - Medium Priority
- [ ] Collaborative editing
- [ ] Publishing integration (Amazon KDP, etc.)
- [ ] AI style customization
- [ ] Reading progress tracking
- [ ] Book sharing with public links

## Next Tasks
1. Add EPUB export using ebooklib
2. Enable chapter content editing
3. Add "Regenerate chapter" feature
4. Implement book sharing with public links
5. Add reading progress tracking
