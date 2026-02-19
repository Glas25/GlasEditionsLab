# GlasEditionsLab - PRD (Product Requirements Document)

## Original Problem Statement
Construire un générateur de livres comme OneBookLab, pour écrire des livres de fiction et de non-fiction, sans que l'utilisateur n'ait besoin de corriger aucune phrase, et sans supervision. Juste à partir d'une idée et quelques renseignements de départ.

## User Choices
- **LLM**: Gemini 3 Flash avec Emergent LLM Universal Key
- **Theme**: Thème clair, style riche
- **Features**: Structure/plan, génération chapitre par chapitre, choix du genre/ton, export PDF/TXT/HTML/EPUB
- **Book Length**: 10-50 chapitres (configurable selon abonnement)
- **Language**: Français (configurable)
- **Authentication**: JWT (email/password) + Google OAuth via Emergent
- **Cover Generation**: Gemini Nano Banana avec prompt personnalisable (Auteur/Écrivain)
- **Export**: Style riche (couverture, table des matières, numéros de pages) - 4 formats
- **Monetization**: Stripe avec 3 plans d'abonnement + livre unique
- **Admin Access**: Email glaseditionslab@gmail.com = accès illimité gratuit

## Legal Information
- **Company**: EI Glas25
- **Address**: 1 Ter rue du Cotay, 25300 Arçon, France
- **SIRET**: 520 388 166 00024
- **Contact**: glas25@outlook.fr

## Subscription Plans

| Plan | Prix | Livres/mois | Chapitres/livre | Couvertures IA |
|------|------|-------------|-----------------|----------------|
| **Débutant** | 27€/mois | 3 | 15 max | ❌ |
| **Auteur** ⭐ | 57€/mois | 7 | 30 max | ✅ |
| **Écrivain** | 97€/mois | Illimité | 50 max | ✅ |
| **Livre unique** | 9,90 € | 1 crédit | 12 max | ❌ |
| **Admin** | Gratuit | Illimité | Illimité | ✅ |

## Architecture

### Backend (FastAPI + MongoDB + Stripe)
- **Framework**: FastAPI avec async support
- **Database**: MongoDB via Motor (async driver)
- **AI Integration**: 
  - Gemini 3 Flash pour le texte (emergentintegrations)
  - Gemini Nano Banana pour les couvertures (emergentintegrations)
- **Authentication**: JWT + Google OAuth via Emergent Auth
- **Payments**: Stripe via emergentintegrations
- **Export**: reportlab pour PDF, ebooklib pour EPUB
- **Key Files**:
  - `/app/backend/server.py` - Main API server
  - `/app/backend/.env` - Environment variables

### Frontend (React + Tailwind + Shadcn)
- **Framework**: React 19 with React Router
- **Styling**: Tailwind CSS with custom design system
- **Components**: Shadcn/UI from `/app/frontend/src/components/ui/`

## What's Been Implemented (February 2026)

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
  - Page numbers
  - Professional typography

### Phase 3 - Monetization (February 2026)
- **Stripe Subscription System**:
  - 3 plans d'abonnement (Débutant, Auteur, Écrivain)
  - Option livre unique à 9,90€
  - Checkout sessions via Stripe
  - Webhook handling pour validation paiements
  - Monthly book/chapter limits enforcement
- **Book Editing Features**:
  - Modification du titre du livre
  - Régénération de chapitres individuels
  - Nettoyage automatique du contenu (espaces, tirets)
- **UI Improvements**:
  - Page de tarification avec plans comparatifs
  - Indicateur d'abonnement dans le menu utilisateur
  - Landing page avec statistiques (10-50 chapitres)
- **EPUB Export** (February 3, 2026):
  - Export au format EPUB avec ebooklib
  - Structure standard EPUB (mimetype, META-INF, content.opf)
  - CSS styling pour lecture e-reader
  - Support de la couverture dans l'EPUB
  - 4 formats d'export disponibles: TXT, HTML, PDF, EPUB

### Phase 4 - Account Management & Editing (February 2026)
- **Account Page** (`/account`):
  - Personal info display (name, email)
  - Subscription status with admin badge
  - Usage stats (books this month, chapters per book, credits)
  - Password change form with validation
  - Auth protection (redirect to login if not authenticated)
- **Password Change**:
  - Verifies current password before allowing change
  - New password min 6 characters validation
  - Frontend password match validation
- **Subscription Management**:
  - GET /api/account/subscription endpoint
  - Cancel subscription (Stripe cancel_at_period_end)
  - Reactivate subscription before expiry
  - Admin account: unlimited, cannot cancel
- **Chapter Inline Editing**:
  - Edit button on completed chapters in BookView
  - Textarea editor with word count
  - Save/Cancel buttons
  - "modifié manuellement" indicator on edited chapters
  - Persists edited_manually flag in DB

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register with email/password |
| `/api/auth/login` | POST | Login with email/password |
| `/api/auth/session` | POST | Process Google OAuth session |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/logout` | POST | Logout user |
| `/api/plans` | GET | Get subscription plans |
| `/api/checkout/subscription` | POST | Create Stripe checkout for subscription |
| `/api/checkout/single-book` | POST | Create Stripe checkout for single book |
| `/api/checkout/status/{session_id}` | GET | Check payment status |
| `/api/webhook/stripe` | POST | Stripe webhook handler |
| `/api/books` | POST | Create new book |
| `/api/books` | GET | List all books |
| `/api/books/{id}` | GET | Get book details |
| `/api/books/{id}` | PATCH | Update book title |
| `/api/books/{id}` | DELETE | Delete book |
| `/api/books/{id}/generate-outline` | POST | Generate book outline |
| `/api/books/{id}/generate-chapter/{num}` | POST | Generate single chapter |
| `/api/books/{id}/regenerate-chapter/{num}` | POST | Regenerate chapter |
| `/api/books/{id}/generate-all` | POST | Generate all chapters |
| `/api/books/{id}/generate-cover` | POST | Generate AI cover |
| `/api/books/{id}/export/{format}` | GET | Export (txt/html/pdf/epub) |
| `/api/account/subscription` | GET | Get subscription details |
| `/api/account/change-password` | POST | Change user password |
| `/api/account/cancel-subscription` | POST | Cancel subscription |
| `/api/account/reactivate-subscription` | POST | Reactivate subscription |
| `/api/books/{id}/chapters/{num}` | PUT | Edit chapter content |

### Pages Implemented
- **Landing Page** (`/`) - Hero + features + auth links + stats (4 formats) + footer CGV/Privacy
- **Login** (`/login`) - Email/password + Google OAuth + redirect support
- **Register** (`/register`) - Account creation
- **Pricing** (`/pricing`) - 3 plans + livre unique (9,90 €)
- **Payment Success** (`/payment/success`) - Confirmation paiement
- **Create Book** (`/create`) - 3-step wizard
- **Dashboard** (`/dashboard`) - Active books overview
- **Book View** (`/book/:id`) - Reader + edit title + regenerate chapters + cover + 4 exports + inline chapter editing
- **Library** (`/library`) - All books with filters
- **Account** (`/account`) - Personal info + subscription status + password change
- **Mentions légales** (`/mentions-legales`) - Informations légales complètes
- **CGU** (`/cgu`) - Conditions Générales d'Utilisation (14 articles)
- **CGV** (`/cgv`) - Conditions Générales de Vente (15 articles avec tableau tarifs)
- **Privacy** (`/privacy`) - Politique de Confidentialité RGPD complète

## Prioritized Backlog

### P0 - Critical (Completed ✅)
- [x] Book creation wizard
- [x] AI outline generation
- [x] AI chapter generation
- [x] Book reader interface
- [x] Export functionality (TXT, HTML, PDF, EPUB with page numbers)
- [x] User authentication
- [x] AI cover generation
- [x] Stripe subscription system
- [x] Edit book title
- [x] Regenerate chapters
- [x] EPUB export format
- [x] Admin access (glaseditionslab@gmail.com)
- [x] Landing page Tarifs link
- [x] "Créer mon livre" redirect to login if not connected
- [x] French price format (9,90 €)
- [x] CGV and Privacy Policy pages
- [x] Cookie consent banner (RGPD compliant)
- [x] Single book: 12 chapters max, no AI cover
- [x] Écrivain plan: 50 chapters max (not unlimited)
- [x] Login/Register error handling via toast notifications
- [x] Library requires authentication (redirects to login)
- [x] Dashboard requires authentication (redirects to login)
- [x] Pricing page navbar simplified (no Dashboard/Library/Create buttons when not logged in)
- [x] Users can only see their own books (user_id filtering)
- [x] Complete legal pages (Mentions légales, CGU, CGV, Privacy)

- [x] Chapter content editing (inline editing with save/cancel)
- [x] Subscription management (cancel, reactivate via account page)
- [x] Account page (/account) with password change and subscription details

### P1 - High Priority (Next Phase)
- [ ] Admin dashboard (user management, statistics)
- [ ] GDPR data export (right to data portability)
- [ ] Multiple book versions/drafts

### P2 - Medium Priority
- [ ] Collaborative editing
- [ ] Publishing integration (Amazon KDP, etc.)
- [ ] AI style customization
- [ ] Reading progress tracking
- [ ] Book sharing with public links
- [ ] Fix ESLint warning react-hooks/exhaustive-deps in App.js

### P3 - Refactoring
- [ ] Break down server.py (1700+ lines) into modular routers
- [ ] Break down BookView.jsx into smaller components

## Next Tasks
1. Admin dashboard for user management
2. GDPR data export feature
3. Book sharing with public links
