import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { BookOpen, Sparkles, FileText, Download, Clock, Zap, PenTool, Globe } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
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
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent rounded-sm animate-fade-in">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-accent-foreground">Propulsé par l'IA Gemini</span>
              </div>
              
              {/* Main Title */}
              <h1 className="font-serif text-5xl md:text-7xl font-bold tracking-tight leading-tight animate-slide-up" style={{ animationDelay: '0.1s' }}>
                Donnez vie à vos
                <span className="block text-primary">idées de livres</span>
              </h1>
              
              {/* Subtitle */}
              <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-xl animate-slide-up" style={{ animationDelay: '0.2s' }}>
                Transformez une simple idée en un livre complet de fiction ou non-fiction. 
                Sans corrections nécessaires. Sans supervision. Prêt à publier.
              </p>
              
              {/* CTA Buttons */}
              <div className="flex flex-wrap gap-4 animate-slide-up" style={{ animationDelay: '0.3s' }}>
                <Link to="/create" data-testid="hero-cta-create">
                  <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-14 px-10 rounded-sm font-serif text-lg tracking-wide shadow-sm">
                    <PenTool className="w-5 h-5 mr-2" />
                    Créer mon livre
                  </Button>
                </Link>
                <Link to="/library" data-testid="hero-cta-library">
                  <Button variant="outline" className="h-14 px-10 rounded-sm font-medium text-lg border-stone-300 hover:bg-stone-100">
                    Voir la bibliothèque
                  </Button>
                </Link>
              </div>
              
              {/* Stats */}
              <div className="flex gap-12 pt-8 animate-slide-up" style={{ animationDelay: '0.4s' }}>
                <div>
                  <p className="text-3xl font-serif font-bold text-foreground">20-40</p>
                  <p className="text-sm text-muted-foreground">Chapitres générés</p>
                </div>
                <div>
                  <p className="text-3xl font-serif font-bold text-foreground">100%</p>
                  <p className="text-sm text-muted-foreground">Automatique</p>
                </div>
                <div>
                  <p className="text-3xl font-serif font-bold text-foreground">PDF</p>
                  <p className="text-sm text-muted-foreground">Export inclus</p>
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
              <Link to="/create" data-testid="genres-cta">
                <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-serif tracking-wide">
                  Commencer maintenant
                </Button>
              </Link>
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
          <Link to="/create" data-testid="final-cta">
            <Button className="bg-background text-foreground hover:bg-background/90 h-14 px-12 rounded-sm font-serif text-lg tracking-wide">
              Créer mon premier livre
            </Button>
          </Link>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-12 border-t border-border">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-sm flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-primary-foreground" />
              </div>
              <span className="font-serif font-semibold">GlasEditionsLab</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 GlasEditionsLab. Propulsé par Gemini 3 Flash.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
