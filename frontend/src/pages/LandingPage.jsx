import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { BookOpen, Sparkles, FileText, Download, Clock, Zap, PenTool, Globe, LogIn, UserPlus, Menu, X } from "lucide-react";

export default function LandingPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const handleCreateBook = () => {
    if (!user) {
      navigate('/login?redirect=/pricing&message=subscription');
    } else if (
      user.subscription === 'admin' ||
      (user.subscription && user.subscription_expires && new Date(user.subscription_expires) > new Date()) ||
      user.single_book_credits > 0
    ) {
      navigate('/create');
    } else {
      navigate('/pricing');
    }
  };
  
  const handleViewLibrary = () => {
    if (user) {
      navigate('/library');
    } else {
      navigate('/login?redirect=/library');
    }
  };
  
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Bar */}
      <nav className="absolute top-0 left-0 right-0 z-20 px-6 md:px-12 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-serif text-xl font-semibold tracking-tight">GlasEditionsLab</span>
          </Link>
          
          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-4">
            <Link to="/pricing" data-testid="nav-pricing-btn">
              <Button variant="ghost" className="h-10 px-4 rounded-sm">
                Tarifs
              </Button>
            </Link>
            {user ? (
              <Link to="/dashboard">
                <Button variant="outline" className="h-10 px-6 rounded-sm bg-background/50 backdrop-blur-sm" data-testid="nav-dashboard-btn">
                  Tableau de bord
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login" data-testid="nav-login-btn">
                  <Button variant="ghost" className="h-10 px-4 rounded-sm">
                    <LogIn className="w-4 h-4 mr-2" />
                    Connexion
                  </Button>
                </Link>
                <Link to="/register" data-testid="nav-register-btn">
                  <Button className="h-10 px-6 rounded-sm bg-primary text-primary-foreground hover:bg-primary/90">
                    <UserPlus className="w-4 h-4 mr-2" />
                    S'inscrire
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile burger */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden h-10 w-10"
            onClick={() => setMobileOpen(!mobileOpen)}
            data-testid="landing-mobile-menu-toggle"
            aria-label="Menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden mt-3 bg-background/95 backdrop-blur-sm rounded-md border border-border shadow-lg p-4 space-y-2 animate-in slide-in-from-top-2 duration-200">
            <Link to="/pricing" onClick={() => setMobileOpen(false)} className="block">
              <Button variant="ghost" className="w-full justify-start h-10 rounded-sm">
                Tarifs
              </Button>
            </Link>
            {user ? (
              <Link to="/dashboard" onClick={() => setMobileOpen(false)} className="block">
                <Button variant="outline" className="w-full h-10 rounded-sm">
                  Tableau de bord
                </Button>
              </Link>
            ) : (
              <>
                <Link to="/login" onClick={() => setMobileOpen(false)} className="block">
                  <Button variant="ghost" className="w-full justify-start h-10 rounded-sm">
                    <LogIn className="w-4 h-4 mr-2" />
                    Connexion
                  </Button>
                </Link>
                <Link to="/register" onClick={() => setMobileOpen(false)} className="block">
                  <Button className="w-full h-10 rounded-sm bg-primary text-primary-foreground hover:bg-primary/90">
                    <UserPlus className="w-4 h-4 mr-2" />
                    S'inscrire
                  </Button>
                </Link>
              </>
            )}
          </div>
        )}
      </nav>
      
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center" data-testid="hero-section">
        {/* Background Image */}
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1543320996-542b8a0e022c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODl8MHwxfHNlYXJjaHwxfHxtaW5pbWFsaXN0JTIwb3BlbiUyMGJvb2slMjBlbGVnYW50JTIwbGlnaHRpbmd8ZW58MHx8fHwxNzcwMDUyMjg5fDA&ixlib=rb-4.1.0&q=85')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-background/10 via-background/80 to-background" />
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-12 py-24">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12">
            <div className="md:col-span-7 space-y-8">
              {/* Main Title */}
              <h1 className="font-serif text-5xl md:text-7xl font-bold tracking-tight leading-tight animate-slide-up" style={{ animationDelay: '0.1s' }}>
                Donnez vie à vos
                <span className="block text-primary">idées de livres</span>
              </h1>
              
              {/* Subtitle */}
              <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-xl animate-slide-up" style={{ animationDelay: '0.2s' }}>
                Transformez une simple idée en un livre complet de fiction ou non-fiction. 
                Sans corrections nécessaires. Prêt à publier.
              </p>
              
              {/* CTA Buttons */}
              <div className="flex flex-wrap gap-4 animate-slide-up" style={{ animationDelay: '0.3s' }}>
                <Button 
                  onClick={handleCreateBook}
                  className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-14 px-10 rounded-sm font-serif text-lg tracking-wide shadow-sm"
                  data-testid="hero-cta-create"
                >
                  <PenTool className="w-5 h-5 mr-2" />
                  Créer mon livre
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleViewLibrary}
                  className="h-14 px-10 rounded-sm font-medium text-lg border-stone-300 hover:bg-stone-100"
                  data-testid="hero-cta-library"
                >
                  Voir la bibliothèque
                </Button>
              </div>
              
              {/* Stats */}
              <div className="flex gap-12 pt-8 animate-slide-up" style={{ animationDelay: '0.4s' }}>
                <div>
                  <p className="text-3xl font-serif font-bold text-foreground">10-50</p>
                  <p className="text-sm text-muted-foreground">Chapitres générés</p>
                </div>
                <div>
                  <p className="text-3xl font-serif font-bold text-foreground">100%</p>
                  <p className="text-sm text-muted-foreground">Automatique</p>
                </div>
                <div>
                  <p className="text-3xl font-serif font-bold text-foreground">4 formats</p>
                  <p className="text-sm text-muted-foreground">PDF, EPUB, HTML, TXT</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="py-24 md:py-32 bg-card paper-texture" data-testid="features-section">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="text-center mb-16">
            <h2 className="font-serif text-4xl md:text-5xl font-semibold tracking-tight mb-4">
              Comment ça fonctionne
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              De l'idée au livre complet en quelques clics
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Feature 1 */}
            <div className="feature-card group" data-testid="feature-idea">
              <div className="w-12 h-12 bg-accent rounded-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-semibold mb-3">1. Votre idée</h3>
              <p className="text-muted-foreground leading-relaxed">
                Décrivez votre concept, choisissez le genre et le ton. C'est tout ce dont nous avons besoin.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="feature-card group" data-testid="feature-outline">
              <div className="w-12 h-12 bg-accent rounded-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-semibold mb-3">2. Plan structuré</h3>
              <p className="text-muted-foreground leading-relaxed">
                L'IA génère un plan détaillé avec tous les chapitres et leur contenu prévu.
              </p>
            </div>
            
            {/* Feature 3 */}
            <div className="feature-card group" data-testid="feature-generation">
              <div className="w-12 h-12 bg-accent rounded-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-semibold mb-3">3. Génération auto</h3>
              <p className="text-muted-foreground leading-relaxed">
                Chaque chapitre est rédigé automatiquement, en maintenant la cohérence narrative.
              </p>
            </div>
            
            {/* Feature 4 */}
            <div className="feature-card group" data-testid="feature-export">
              <div className="w-12 h-12 bg-accent rounded-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Download className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-semibold mb-3">4. Export & Publish</h3>
              <p className="text-muted-foreground leading-relaxed">
                Exportez en TXT ou HTML, prêt pour la publication ou la conversion.
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Genres Section */}
      <section className="py-24 md:py-32" data-testid="genres-section">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
            <div className="md:col-span-5">
              <h2 className="font-serif text-4xl md:text-5xl font-semibold tracking-tight mb-6">
                Tous les genres à portée de main
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed mb-8">
                Fiction, non-fiction, romance, thriller, fantasy, science-fiction, mystère, horreur, biographie, 
                développement personnel, histoire, business... Votre imagination est la seule limite.
              </p>
              <Button 
                onClick={handleCreateBook}
                className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-serif tracking-wide"
                data-testid="genres-cta"
              >
                Commencer maintenant
              </Button>
            </div>
            <div className="md:col-span-7">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {['Fiction', 'Romance', 'Thriller', 'Fantasy', 'Sci-Fi', 'Mystère', 'Biographie', 'Business', 'Histoire'].map((genre, i) => (
                  <div 
                    key={genre}
                    className="p-6 bg-card border border-border rounded-sm hover:border-primary/50 transition-colors cursor-default"
                    style={{ animationDelay: `${i * 0.05}s` }}
                  >
                    <span className="font-serif text-lg">{genre}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-24 md:py-32 bg-foreground text-background" data-testid="cta-section">
        <div className="max-w-7xl mx-auto px-6 md:px-12 text-center">
          <BookOpen className="w-16 h-16 mx-auto mb-8 opacity-80" />
          <h2 className="font-serif text-4xl md:text-5xl font-semibold tracking-tight mb-6">
            Prêt à écrire votre prochain best-seller ?
          </h2>
          <p className="text-lg opacity-80 max-w-2xl mx-auto mb-10">
            Rejoignez GlasEditionsLab et laissez l'intelligence artificielle transformer vos idées en livres complets.
          </p>
          <Button 
            onClick={handleCreateBook}
            className="bg-background text-foreground hover:bg-background/90 h-14 px-12 rounded-sm font-serif text-lg tracking-wide"
            data-testid="final-cta"
          >
            Créer mon premier livre
          </Button>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-12 border-t border-border">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="flex flex-col gap-8">
            {/* Top row */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-primary rounded-sm flex items-center justify-center">
                  <BookOpen className="w-4 h-4 text-primary-foreground" />
                </div>
                <span className="font-serif font-semibold">GlasEditionsLab</span>
              </div>
              <p className="text-sm text-muted-foreground">
                © 2025 GlasEditionsLab - EI Glas25
              </p>
            </div>
            
            {/* Legal links */}
            <div className="flex flex-wrap items-center justify-center gap-4 md:gap-6 text-sm">
              <Link to="/mentions-legales" className="text-muted-foreground hover:text-foreground transition-colors" data-testid="footer-mentions">
                Mentions légales
              </Link>
              <span className="text-muted-foreground/30">•</span>
              <Link to="/cgu" className="text-muted-foreground hover:text-foreground transition-colors" data-testid="footer-cgu">
                CGU
              </Link>
              <span className="text-muted-foreground/30">•</span>
              <Link to="/cgv" className="text-muted-foreground hover:text-foreground transition-colors" data-testid="footer-cgv">
                CGV
              </Link>
              <span className="text-muted-foreground/30">•</span>
              <Link to="/privacy" className="text-muted-foreground hover:text-foreground transition-colors" data-testid="footer-privacy">
                Politique de confidentialité
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
