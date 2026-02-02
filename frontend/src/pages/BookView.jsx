import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  BookOpen, Play, Download, Trash2, CheckCircle, Clock, Loader2, 
  AlertCircle, ChevronLeft, ChevronRight, FileText, Code
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

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

function ChapterIcon({ status }) {
  if (status === "completed") return <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />;
  if (status === "generating") return <Loader2 className="w-4 h-4 text-primary animate-spin shrink-0" />;
  return null;
}

export default function BookView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchBook = useCallback(function() {
    axios.get(API + "/books/" + id)
      .then(function(response) {
        setBook(response.data);
        if (!selectedChapter && response.data.outline && response.data.outline.length > 0) {
          const firstCompleted = response.data.outline.find(function(ch) { return ch.status === 'completed'; });
          if (firstCompleted) {
            setSelectedChapter(firstCompleted.number);
          } else {
            setSelectedChapter(1);
          }
        }
      })
      .catch(function(error) {
        console.error("Error fetching book:", error);
        toast.error("Livre introuvable");
        navigate('/dashboard');
      })
      .finally(function() {
        setLoading(false);
      });
  }, [id, navigate, selectedChapter]);

  useEffect(function() {
    fetchBook();
    const interval = setInterval(fetchBook, 3000);
    return function() { clearInterval(interval); };
  }, [fetchBook]);

  function generateOutline() {
    setActionLoading(true);
    axios.post(API + "/books/" + id + "/generate-outline")
      .then(function() {
        toast.success("Génération du plan lancée !");
        fetchBook();
      })
      .catch(function() {
        toast.error("Erreur lors de la génération du plan");
      })
      .finally(function() {
        setActionLoading(false);
      });
  }

  function generateAllChapters() {
    setActionLoading(true);
    axios.post(API + "/books/" + id + "/generate-all")
      .then(function() {
        toast.success("Génération de tous les chapitres lancée !");
        fetchBook();
      })
      .catch(function() {
        toast.error("Erreur lors de la génération");
      })
      .finally(function() {
        setActionLoading(false);
      });
  }

  function generateSingleChapter(chapterNum) {
    axios.post(API + "/books/" + id + "/generate-chapter/" + chapterNum)
      .then(function() {
        toast.success("Génération du chapitre " + chapterNum + " lancée !");
        fetchBook();
      })
      .catch(function() {
        toast.error("Erreur lors de la génération du chapitre");
      });
  }

  function exportBook(format) {
    window.open(API + "/books/" + id + "/export/" + format, '_blank');
    toast.success("Export " + format.toUpperCase() + " en cours...");
  }

  function deleteBook() {
    axios.delete(API + "/books/" + id)
      .then(function() {
        toast.success("Livre supprimé");
        navigate('/dashboard');
      })
      .catch(function() {
        toast.error("Erreur lors de la suppression");
      });
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="flex items-center justify-center py-24">
          <div className="book-loader">
            <span></span><span></span><span></span><span></span><span></span>
          </div>
        </div>
      </div>
    );
  }

  if (!book) return null;

  const statusInfo = getStatusInfo(book.status);
  const progress = book.outline && book.outline.length > 0 
    ? Math.round((book.outline.filter(function(ch) { return ch.status === 'completed'; }).length / book.outline.length) * 100)
    : 0;
  const currentChapter = book.outline ? book.outline.find(function(ch) { return ch.number === selectedChapter; }) : null;
  const genreDisplay = book.genre ? book.genre.replace('_', ' ') : '';

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-6 md:px-12 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-8">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className={"status-badge " + statusInfo.color} data-testid="book-status">
                <StatusIcon status={book.status} />
                {statusInfo.label}
              </span>
            </div>
            <h1 className="font-serif text-3xl md:text-4xl font-bold tracking-tight" data-testid="book-title">
              {book.title}
            </h1>
            <p className="text-muted-foreground max-w-2xl">{book.idea}</p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="capitalize">{genreDisplay}</span>
              <span>•</span>
              <span className="capitalize">{book.tone}</span>
              <span>•</span>
              <span>{book.language}</span>
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            {book.status === 'draft' && (
              <Button 
                onClick={generateOutline}
                disabled={actionLoading}
                className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-11 px-6 rounded-sm font-serif"
                data-testid="btn-generate-outline"
              >
                {actionLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                Générer le plan
              </Button>
            )}
            
            {book.status === 'outline_ready' && (
              <Button 
                onClick={generateAllChapters}
                disabled={actionLoading}
                className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-11 px-6 rounded-sm font-serif"
                data-testid="btn-generate-all"
              >
                {actionLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                Générer tout le livre
              </Button>
            )}
            
            {book.outline && book.outline.length > 0 && (
              <>
                <Button 
                  variant="outline" 
                  onClick={function() { exportBook('txt'); }}
                  className="export-btn rounded-sm"
                  data-testid="btn-export-txt"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  TXT
                </Button>
                <Button 
                  variant="outline" 
                  onClick={function() { exportBook('html'); }}
                  className="export-btn rounded-sm"
                  data-testid="btn-export-html"
                >
                  <Code className="w-4 h-4 mr-2" />
                  HTML
                </Button>
              </>
            )}
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" className="h-11 px-4 rounded-sm border-destructive/30 text-destructive hover:bg-destructive/10" data-testid="btn-delete">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Supprimer ce livre ?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Cette action est irréversible. Le livre "{book.title}" et tout son contenu seront définitivement supprimés.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="rounded-sm">Annuler</AlertDialogCancel>
                  <AlertDialogAction onClick={deleteBook} className="bg-destructive text-destructive-foreground hover:bg-destructive/90 rounded-sm">
                    Supprimer
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
        
        {/* Progress Bar */}
        {book.outline && book.outline.length > 0 && (
          <Card className="mb-8 border-stone-200">
            <CardContent className="py-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium">Progression globale</span>
                <span className="text-sm text-muted-foreground">
                  {book.outline.filter(function(ch) { return ch.status === 'completed'; }).length} / {book.outline.length} chapitres
                  {book.total_word_count > 0 && (" • " + book.total_word_count.toLocaleString() + " mots")}
                </span>
              </div>
              <Progress value={progress} className={"h-3 " + (book.status.includes('generating') ? 'progress-generating' : '')} />
            </CardContent>
          </Card>
        )}
        
        {/* Content Area */}
        {book.outline && book.outline.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Chapter List */}
            <div className="md:col-span-4 lg:col-span-3">
              <Card className="border-stone-200 sticky top-24">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg font-serif">Chapitres</CardTitle>
                </CardHeader>
                <ScrollArea className="h-[60vh]">
                  <div className="px-4 pb-4">
                    {book.outline.map(function(chapter) {
                      let itemClass = "chapter-item w-full text-left";
                      if (selectedChapter === chapter.number) itemClass += " active";
                      if (chapter.status === 'completed') itemClass += " completed";
                      if (chapter.status === 'generating') itemClass += " generating";
                      
                      return (
                        <button
                          key={chapter.number}
                          onClick={function() { setSelectedChapter(chapter.number); }}
                          data-testid={"chapter-item-" + chapter.number}
                          className={itemClass}
                        >
                          <div className="flex items-start gap-3">
                            <span className="text-xs font-mono text-muted-foreground mt-1">
                              {String(chapter.number).padStart(2, '0')}
                            </span>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-sm line-clamp-1">{chapter.title}</p>
                              <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{chapter.summary}</p>
                            </div>
                            <ChapterIcon status={chapter.status} />
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </ScrollArea>
              </Card>
            </div>
            
            {/* Chapter Content */}
            <div className="md:col-span-8 lg:col-span-9">
              <Card className="border-stone-200">
                {currentChapter && (
                  <>
                    <CardHeader className="border-b border-stone-100">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-muted-foreground mb-1">Chapitre {currentChapter.number}</p>
                          <CardTitle className="font-serif text-2xl">{currentChapter.title}</CardTitle>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={function() { setSelectedChapter(Math.max(1, selectedChapter - 1)); }}
                            disabled={selectedChapter === 1}
                            data-testid="btn-prev-chapter"
                          >
                            <ChevronLeft className="w-5 h-5" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={function() { setSelectedChapter(Math.min(book.outline.length, selectedChapter + 1)); }}
                            disabled={selectedChapter === book.outline.length}
                            data-testid="btn-next-chapter"
                          >
                            <ChevronRight className="w-5 h-5" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="py-8">
                      {currentChapter.content ? (
                        <div className="book-content max-w-prose mx-auto" data-testid="chapter-content">
                          {currentChapter.content.split('\n\n').map(function(paragraph, i) {
                            return <p key={i}>{paragraph}</p>;
                          })}
                          <div className="mt-8 pt-8 border-t border-stone-100 text-center text-sm text-muted-foreground">
                            {currentChapter.word_count ? currentChapter.word_count.toLocaleString() : 0} mots
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-16" data-testid="chapter-not-generated">
                          <BookOpen className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                          <p className="text-muted-foreground mb-2">{currentChapter.summary}</p>
                          <p className="text-sm text-muted-foreground mb-6">Ce chapitre n'a pas encore été généré.</p>
                          {(book.status === 'outline_ready' || book.status === 'generating') && (
                            <Button 
                              onClick={function() { generateSingleChapter(currentChapter.number); }}
                              className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 rounded-sm font-serif"
                              data-testid="btn-generate-chapter"
                            >
                              <Play className="w-4 h-4 mr-2" />
                              Générer ce chapitre
                            </Button>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </>
                )}
              </Card>
            </div>
          </div>
        ) : (
          <Card className="border-stone-200" data-testid="no-outline">
            <CardContent className="py-16 text-center">
              <BookOpen className="w-16 h-16 mx-auto text-muted-foreground mb-6" />
              <h2 className="font-serif text-2xl font-semibold mb-3">
                {book.status === 'generating_outline' ? 'Création du plan en cours...' : 'Prêt à générer le plan'}
              </h2>
              <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                {book.status === 'generating_outline' 
                  ? "L'IA structure votre livre. Cela peut prendre quelques instants."
                  : "Cliquez sur le bouton ci-dessus pour générer la structure de votre livre."
                }
              </p>
              {book.status === 'generating_outline' && (
                <div className="book-loader mx-auto">
                  <span></span><span></span><span></span><span></span><span></span>
                </div>
              )}
              {book.status === 'error' && book.error_message && (
                <div className="mt-4 p-4 bg-destructive/10 rounded-sm text-destructive text-sm">
                  {book.error_message}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
