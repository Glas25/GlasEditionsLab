import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { BookOpen, Plus, Clock, CheckCircle, AlertCircle, Loader2, ArrowRight } from "lucide-react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function getStatusInfo(status) {
  const configs = {
    draft: { label: "Brouillon", color: "status-draft" },
    generating_outline: { label: "Création du plan...", color: "status-generating" },
    outline_ready: { label: "Plan prêt", color: "status-draft" },
    generating: { label: "Génération en cours...", color: "status-generating" },
    completed: { label: "Terminé", color: "status-completed" },
    error: { label: "Erreur", color: "status-error" }
  };
  return configs[status] || { label: "Inconnu", color: "status-draft" };
}

function StatusIcon({ status }) {
  if (status === "completed" || status === "outline_ready") return <CheckCircle className="w-3 h-3" />;
  if (status === "generating_outline" || status === "generating") return <Loader2 className="w-3 h-3 animate-spin" />;
  if (status === "error") return <AlertCircle className="w-3 h-3" />;
  return <Clock className="w-3 h-3" />;
}

function BookCard({ book }) {
  const statusInfo = getStatusInfo(book.status);
  const progress = book.outline && book.outline.length > 0 
    ? Math.round((book.outline.filter(function(ch) { return ch.status === 'completed'; }).length / book.outline.length) * 100)
    : 0;

  return (
    <Link to={"/book/" + book.id} data-testid={"book-card-" + book.id}>
      <Card className="book-card card-hover h-full">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="font-serif text-xl">{book.title}</CardTitle>
              <CardDescription className="line-clamp-2">{book.idea}</CardDescription>
            </div>
            <span className={"status-badge " + statusInfo.color}>
              <StatusIcon status={book.status} />
              {statusInfo.label}
            </span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Progression</span>
                <span className="font-medium">{progress}%</span>
              </div>
              <Progress 
                value={progress} 
                className={"h-2 " + (book.status.includes('generating') ? 'progress-generating' : '')}
              />
            </div>
            
            {book.outline && book.outline.length > 0 && (
              <div className="chapter-progress">
                {book.outline.map(function(ch, i) {
                  let dotClass = "chapter-dot";
                  if (ch.status === 'completed') dotClass += " completed";
                  else if (i === book.current_chapter - 1 && book.status.includes('generating')) dotClass += " current";
                  return <div key={i} className={dotClass} title={"Chapitre " + ch.number + ": " + ch.title} />;
                })}
              </div>
            )}
            
            <div className="flex items-center gap-4 text-sm text-muted-foreground pt-2">
              <span>{book.outline ? book.outline.length : 0} chapitres</span>
              <span>•</span>
              <span>{book.total_word_count ? book.total_word_count.toLocaleString() : 0} mots</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function CompletedBookCard({ book }) {
  return (
    <Link to={"/book/" + book.id} data-testid={"completed-book-" + book.id}>
      <Card className="book-card card-hover">
        <CardHeader className="pb-3">
          <CardTitle className="font-serif text-lg line-clamp-1">{book.title}</CardTitle>
          <CardDescription className="line-clamp-1">{book.genre}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="status-badge status-completed">
              <CheckCircle className="w-3 h-3" />
              Terminé
            </span>
            <span>{book.total_word_count ? book.total_word_count.toLocaleString() : 0} mots</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

export default function Dashboard() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(function() {
    fetchBooks();
    const interval = setInterval(fetchBooks, 5000);
    return function() { clearInterval(interval); };
  }, []);

  function fetchBooks() {
    axios.get(API + "/books")
      .then(function(response) {
        setBooks(response.data);
      })
      .catch(function(error) {
        console.error("Error fetching books:", error);
      })
      .finally(function() {
        setLoading(false);
      });
  }

  const activeBooks = books.filter(function(b) { return b.status !== 'completed'; });
  const recentCompleted = books.filter(function(b) { return b.status === 'completed'; }).slice(0, 3);

  return (
    <div className="min-h-screen bg-background paper-texture">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-6 md:px-12 py-12">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="font-serif text-4xl font-bold tracking-tight mb-2" data-testid="dashboard-title">
              Tableau de bord
            </h1>
            <p className="text-muted-foreground">
              Suivez la progression de vos livres en cours
            </p>
          </div>
          <Link to="/create">
            <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-serif tracking-wide" data-testid="dashboard-create-btn">
              <Plus className="w-4 h-4 mr-2" />
              Nouveau livre
            </Button>
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="book-loader">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          </div>
        ) : books.length === 0 ? (
          <Card className="border-dashed border-2 border-stone-200" data-testid="empty-state">
            <CardContent className="py-16 text-center">
              <BookOpen className="w-16 h-16 mx-auto text-muted-foreground mb-6" />
              <h2 className="font-serif text-2xl font-semibold mb-3">Aucun livre en cours</h2>
              <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                Commencez par créer votre premier livre. L'IA s'occupera du reste.
              </p>
              <Link to="/create">
                <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-serif tracking-wide">
                  <Plus className="w-4 h-4 mr-2" />
                  Créer mon premier livre
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-10">
            {activeBooks.length > 0 && (
              <section>
                <h2 className="font-serif text-2xl font-semibold mb-6">En cours</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {activeBooks.map(function(book) {
                    return <BookCard key={book.id} book={book} />;
                  })}
                </div>
              </section>
            )}
            
            {recentCompleted.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="font-serif text-2xl font-semibold">Récemment terminés</h2>
                  <Link to="/library" className="text-sm text-primary hover:underline flex items-center gap-1">
                    Voir tout <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {recentCompleted.map(function(book) {
                    return <CompletedBookCard key={book.id} book={book} />;
                  })}
                </div>
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
