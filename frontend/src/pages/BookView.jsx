import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  BookOpen, Play, Trash2, CheckCircle, Clock, Loader2, 
  AlertCircle, ChevronLeft, ChevronRight, FileText, Code, FileDown, Image as ImageIcon,
  RefreshCw, Pencil, Check, X
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATUS_CONFIGS = {
  draft: { label: "Brouillon", color: "status-draft" },
  generating_outline: { label: "Création du plan...", color: "status-generating" },
  outline_ready: { label: "Plan prêt", color: "status-draft" },
  generating: { label: "Génération en cours...", color: "status-generating" },
  generating_cover: { label: "Génération couverture...", color: "status-generating" },
  completed: { label: "Terminé", color: "status-completed" },
  error: { label: "Erreur", color: "status-error" }
};

const StatusIndicator = ({ status }) => {
  if (status === "completed" || status === "outline_ready") {
    return <CheckCircle className="w-3 h-3" />;
  }
  if (status === "generating_outline" || status === "generating" || status === "generating_cover") {
    return <Loader2 className="w-3 h-3 animate-spin" />;
  }
  if (status === "error") {
    return <AlertCircle className="w-3 h-3" />;
  }
  return <Clock className="w-3 h-3" />;
};

const ChapterStatusIcon = ({ status }) => {
  if (status === "completed") {
    return <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />;
  }
  if (status === "generating") {
    return <Loader2 className="w-4 h-4 text-primary animate-spin shrink-0" />;
  }
  return null;
};

const calculateProgress = (outline) => {
  if (!outline || outline.length === 0) return 0;
  let completedCount = 0;
  for (let i = 0; i < outline.length; i++) {
    if (outline[i].status === 'completed') {
      completedCount++;
    }
  }
  return Math.round((completedCount / outline.length) * 100);
};

const getCompletedCount = (outline) => {
  if (!outline) return 0;
  let count = 0;
  for (let i = 0; i < outline.length; i++) {
    if (outline[i].status === 'completed') count++;
  }
  return count;
};

export default function BookView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [coverDialogOpen, setCoverDialogOpen] = useState(false);
  const [coverPrompt, setCoverPrompt] = useState("");
  const [generatingCover, setGeneratingCover] = useState(false);
  const [editingTitle, setEditingTitle] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [regeneratingChapter, setRegeneratingChapter] = useState(null);
  const [editingChapter, setEditingChapter] = useState(null);
  const [editedContent, setEditedContent] = useState("");
  const [savingChapter, setSavingChapter] = useState(false);

  const getAuthHeaders = () => {
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

  const fetchBook = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/books/${id}`);
      const bookData = response.data;
      setBook(bookData);
      setNewTitle(bookData.title);
      
      if (selectedChapter === null && bookData.outline && bookData.outline.length > 0) {
        let firstCompletedNum = 1;
        for (let i = 0; i < bookData.outline.length; i++) {
          if (bookData.outline[i].status === 'completed') {
            firstCompletedNum = bookData.outline[i].number;
            break;
          }
        }
        setSelectedChapter(firstCompletedNum);
      }
    } catch (error) {
      console.error("Error fetching book:", error);
      toast.error("Livre introuvable");
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  }, [id, navigate, selectedChapter]);

  useEffect(() => {
    fetchBook();
    const interval = setInterval(fetchBook, 3000);
    return () => clearInterval(interval);
  }, [fetchBook]);

  const generateOutline = async () => {
    setActionLoading(true);
    try {
      await axios.post(`${API}/books/${id}/generate-outline`, {}, { headers: getAuthHeaders() });
      toast.success("Génération du plan lancée !");
      fetchBook();
    } catch (error) {
      toast.error("Erreur lors de la génération du plan");
    } finally {
      setActionLoading(false);
    }
  };

  const generateAllChapters = async () => {
    setActionLoading(true);
    try {
      await axios.post(`${API}/books/${id}/generate-all`, {}, { headers: getAuthHeaders() });
      toast.success("Génération de tous les chapitres lancée !");
      fetchBook();
    } catch (error) {
      toast.error("Erreur lors de la génération");
    } finally {
      setActionLoading(false);
    }
  };

  const generateSingleChapter = async (chapterNum) => {
    try {
      await axios.post(`${API}/books/${id}/generate-chapter/${chapterNum}`, {}, { headers: getAuthHeaders() });
      toast.success(`Génération du chapitre ${chapterNum} lancée !`);
      fetchBook();
    } catch (error) {
      toast.error("Erreur lors de la génération du chapitre");
    }
  };

  const regenerateChapter = async (chapterNum) => {
    setRegeneratingChapter(chapterNum);
    try {
      await axios.post(`${API}/books/${id}/regenerate-chapter/${chapterNum}`, {}, { headers: getAuthHeaders() });
      toast.success(`Régénération du chapitre ${chapterNum} lancée !`);
      fetchBook();
    } catch (error) {
      toast.error("Erreur lors de la régénération du chapitre");
    } finally {
      setRegeneratingChapter(null);
    }
  };

  const startEditingChapter = (chapter) => {
    setEditingChapter(chapter.number);
    setEditedContent(chapter.content || "");
  };

  const cancelEditingChapter = () => {
    setEditingChapter(null);
    setEditedContent("");
  };

  const saveChapterEdit = async (chapterNum) => {
    setSavingChapter(true);
    try {
      await axios.put(`${API}/books/${id}/chapters/${chapterNum}`, 
        { content: editedContent }, 
        { headers: getAuthHeaders() }
      );
      toast.success("Chapitre sauvegardé avec succès !");
      setEditingChapter(null);
      setEditedContent("");
      fetchBook();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Erreur lors de la sauvegarde du chapitre";
      toast.error(errorMsg);
    } finally {
      setSavingChapter(false);
    }
  };

  const generateCover = async () => {
    setGeneratingCover(true);
    try {
      await axios.post(`${API}/books/${id}/generate-cover`, { prompt: coverPrompt || null }, { headers: getAuthHeaders() });
      toast.success("Génération de la couverture lancée !");
      setCoverDialogOpen(false);
      fetchBook();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Erreur lors de la génération de la couverture";
      toast.error(errorMsg);
    } finally {
      setGeneratingCover(false);
    }
  };

  const updateTitle = async () => {
    if (!newTitle.trim() || newTitle === book.title) {
      setEditingTitle(false);
      return;
    }
    
    try {
      await axios.patch(`${API}/books/${id}`, { title: newTitle.trim() }, { headers: getAuthHeaders() });
      toast.success("Titre mis à jour !");
      setEditingTitle(false);
      fetchBook();
    } catch (error) {
      toast.error("Erreur lors de la mise à jour du titre");
    }
  };

  const exportBook = (format) => {
    window.open(`${API}/books/${id}/export/${format}`, '_blank');
    toast.success(`Export ${format.toUpperCase()} en cours...`);
  };

  const deleteBook = async () => {
    try {
      await axios.delete(`${API}/books/${id}`, { headers: getAuthHeaders() });
      toast.success("Livre supprimé");
      navigate('/dashboard');
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handlePrevChapter = () => {
    if (selectedChapter > 1) {
      setSelectedChapter(selectedChapter - 1);
    }
  };

  const handleNextChapter = () => {
    if (book && book.outline && selectedChapter < book.outline.length) {
      setSelectedChapter(selectedChapter + 1);
    }
  };

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

  const statusInfo = STATUS_CONFIGS[book.status] || { label: "Inconnu", color: "status-draft" };
  const progress = calculateProgress(book.outline);
  const completedCount = getCompletedCount(book.outline);
  const isGenerating = book.status && book.status.includes('generating');
  const genreDisplay = book.genre ? book.genre.replace('_', ' ') : '';
  const hasOutline = book.outline && book.outline.length > 0;
  const outlineLength = hasOutline ? book.outline.length : 0;

  let currentChapter = null;
  if (hasOutline && selectedChapter) {
    for (let i = 0; i < book.outline.length; i++) {
      if (book.outline[i].number === selectedChapter) {
        currentChapter = book.outline[i];
        break;
      }
    }
  }

  const renderChapterList = () => {
    if (!hasOutline) return null;
    const items = [];
    for (let i = 0; i < book.outline.length; i++) {
      const chapter = book.outline[i];
      let itemClass = "chapter-item w-full text-left";
      if (selectedChapter === chapter.number) itemClass += " active";
      if (chapter.status === 'completed') itemClass += " completed";
      if (chapter.status === 'generating') itemClass += " generating";
      
      items.push(
        <button
          key={chapter.number}
          onClick={() => setSelectedChapter(chapter.number)}
          data-testid={`chapter-item-${chapter.number}`}
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
            <ChapterStatusIcon status={chapter.status} />
          </div>
        </button>
      );
    }
    return items;
  };

  const renderContentParagraphs = () => {
    if (!currentChapter || !currentChapter.content) return null;
    const paragraphs = currentChapter.content.split('\n\n');
    const elements = [];
    for (let i = 0; i < paragraphs.length; i++) {
      elements.push(<p key={i}>{paragraphs[i]}</p>);
    }
    return elements;
  };

  // Check if user can generate covers
  const canUserGenerateCover = user && (
    user.subscription === 'auteur' || 
    user.subscription === 'ecrivain' || 
    user.single_book_credits > 0
  );

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-6 md:px-12 py-8">
        {/* Header with Cover */}
        <div className="flex flex-col lg:flex-row gap-8 mb-8">
          {/* Cover Image */}
          <div className="lg:w-64 shrink-0">
            <div className="aspect-[2/3] bg-stone-100 rounded-sm border border-stone-200 overflow-hidden relative group">
              {book.cover_image ? (
                <img 
                  src={book.cover_image} 
                  alt={`Couverture de ${book.title}`}
                  className="w-full h-full object-cover"
                  data-testid="book-cover-image"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground">
                  <BookOpen className="w-12 h-12 mb-2" />
                  <span className="text-sm">Pas de couverture</span>
                </div>
              )}
              
              {/* Cover generation button overlay */}
              {canUserGenerateCover && (
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Dialog open={coverDialogOpen} onOpenChange={setCoverDialogOpen}>
                    <DialogTrigger asChild>
                      <Button 
                        variant="secondary" 
                        className="rounded-sm"
                        data-testid="btn-generate-cover"
                      >
                        <ImageIcon className="w-4 h-4 mr-2" />
                        {book.cover_image ? 'Régénérer' : 'Générer'}
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle className="font-serif">Générer une couverture</DialogTitle>
                        <DialogDescription>
                          Décrivez la couverture que vous souhaitez ou laissez vide pour une génération automatique basée sur le livre.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="coverPrompt">Description personnalisée (optionnel)</Label>
                          <Input
                            id="coverPrompt"
                            placeholder="Ex: Une forêt mystérieuse avec une lumière dorée..."
                            value={coverPrompt}
                            onChange={(e) => setCoverPrompt(e.target.value)}
                            className="rounded-sm"
                            data-testid="cover-prompt-input"
                          />
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Genre: {genreDisplay} | Titre: {book.title}
                        </p>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setCoverDialogOpen(false)} className="rounded-sm">
                          Annuler
                        </Button>
                        <Button 
                          onClick={generateCover} 
                          disabled={generatingCover}
                          className="rounded-sm bg-primary text-primary-foreground"
                          data-testid="btn-confirm-generate-cover"
                        >
                          {generatingCover ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Génération...
                            </>
                          ) : (
                            <>
                              <ImageIcon className="w-4 h-4 mr-2" />
                              Générer
                            </>
                          )}
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              )}
              
              {!canUserGenerateCover && (
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <p className="text-white text-sm text-center px-4">
                    Abonnement Auteur ou Écrivain requis
                  </p>
                </div>
              )}
            </div>
          </div>
          
          {/* Book Info */}
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-3">
              <span className={`status-badge ${statusInfo.color}`} data-testid="book-status">
                <StatusIndicator status={book.status} />
                {statusInfo.label}
              </span>
            </div>
            
            {/* Editable Title */}
            {editingTitle ? (
              <div className="flex items-center gap-3">
                <Input
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="font-serif text-3xl font-bold h-14 rounded-sm"
                  autoFocus
                  data-testid="edit-title-input"
                />
                <Button variant="ghost" size="icon" onClick={updateTitle} data-testid="save-title-btn">
                  <Check className="w-5 h-5 text-green-600" />
                </Button>
                <Button variant="ghost" size="icon" onClick={() => { setEditingTitle(false); setNewTitle(book.title); }}>
                  <X className="w-5 h-5 text-destructive" />
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-3 group">
                <h1 className="font-serif text-3xl md:text-4xl font-bold tracking-tight" data-testid="book-title">
                  {book.title}
                </h1>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => setEditingTitle(true)}
                  data-testid="edit-title-btn"
                >
                  <Pencil className="w-4 h-4" />
                </Button>
              </div>
            )}
            
            <p className="text-muted-foreground max-w-2xl">{book.idea}</p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="capitalize">{genreDisplay}</span>
              <span>•</span>
              <span className="capitalize">{book.tone}</span>
              <span>•</span>
              <span>{book.language}</span>
            </div>
            
            {/* Actions */}
            <div className="flex flex-wrap gap-3 pt-4">
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
              
              {hasOutline && (
                <>
                  <Button 
                    variant="outline" 
                    onClick={() => exportBook('txt')}
                    className="export-btn rounded-sm"
                    data-testid="btn-export-txt"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    TXT
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => exportBook('html')}
                    className="export-btn rounded-sm"
                    data-testid="btn-export-html"
                  >
                    <Code className="w-4 h-4 mr-2" />
                    HTML
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => exportBook('pdf')}
                    className="export-btn rounded-sm"
                    data-testid="btn-export-pdf"
                  >
                    <FileDown className="w-4 h-4 mr-2" />
                    PDF
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => exportBook('epub')}
                    className="export-btn rounded-sm"
                    data-testid="btn-export-epub"
                  >
                    <BookOpen className="w-4 h-4 mr-2" />
                    EPUB
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
        </div>
        
        {/* Progress Bar */}
        {hasOutline && (
          <Card className="mb-8 border-stone-200">
            <CardContent className="py-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium">Progression globale</span>
                <span className="text-sm text-muted-foreground">
                  {completedCount} / {outlineLength} chapitres
                  {book.total_word_count > 0 && ` • ${book.total_word_count.toLocaleString()} mots`}
                </span>
              </div>
              <Progress value={progress} className={`h-3 ${isGenerating ? 'progress-generating' : ''}`} />
            </CardContent>
          </Card>
        )}
        
        {/* Content Area */}
        {hasOutline ? (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Chapter List */}
            <div className="md:col-span-4 lg:col-span-3">
              <Card className="border-stone-200 sticky top-24">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg font-serif">Chapitres</CardTitle>
                </CardHeader>
                <ScrollArea className="h-[60vh]">
                  <div className="px-4 pb-4">
                    {renderChapterList()}
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
                          {currentChapter.status === 'completed' && (
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => regenerateChapter(currentChapter.number)}
                              disabled={regeneratingChapter === currentChapter.number}
                              className="rounded-sm"
                              data-testid="btn-regenerate-chapter"
                            >
                              {regeneratingChapter === currentChapter.number ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <>
                                  <RefreshCw className="w-4 h-4 mr-1" />
                                  Régénérer
                                </>
                              )}
                            </Button>
                          )}
                          {currentChapter.content && currentChapter.status === 'completed' && editingChapter !== currentChapter.number && (
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => startEditingChapter(currentChapter)}
                              className="rounded-sm"
                              data-testid="btn-edit-chapter"
                            >
                              <Pencil className="w-4 h-4 mr-1" />
                              Éditer
                            </Button>
                          )}
                          {editingChapter === currentChapter.number && (
                            <>
                              <Button 
                                variant="default" 
                                size="sm"
                                onClick={() => saveChapterEdit(currentChapter.number)}
                                disabled={savingChapter}
                                className="rounded-sm"
                                data-testid="btn-save-chapter"
                              >
                                {savingChapter ? (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                  <>
                                    <Check className="w-4 h-4 mr-1" />
                                    Sauvegarder
                                  </>
                                )}
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="sm"
                                onClick={cancelEditingChapter}
                                disabled={savingChapter}
                                className="rounded-sm"
                                data-testid="btn-cancel-edit"
                              >
                                <X className="w-4 h-4 mr-1" />
                                Annuler
                              </Button>
                            </>
                          )}
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={handlePrevChapter}
                            disabled={selectedChapter === 1}
                            data-testid="btn-prev-chapter"
                          >
                            <ChevronLeft className="w-5 h-5" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon"
                            onClick={handleNextChapter}
                            disabled={selectedChapter === outlineLength}
                            data-testid="btn-next-chapter"
                          >
                            <ChevronRight className="w-5 h-5" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="py-8">
                      {editingChapter === currentChapter.number ? (
                        <div className="max-w-prose mx-auto" data-testid="chapter-editor">
                          <textarea
                            value={editedContent}
                            onChange={(e) => setEditedContent(e.target.value)}
                            className="w-full min-h-[500px] p-4 border border-stone-200 rounded-sm font-serif text-base leading-relaxed resize-y focus:outline-none focus:ring-2 focus:ring-primary/20"
                            placeholder="Contenu du chapitre..."
                            data-testid="chapter-textarea"
                          />
                          <div className="mt-4 text-center text-sm text-muted-foreground">
                            {editedContent.split(/\s+/).filter(w => w).length.toLocaleString()} mots
                            {currentChapter.edited_manually && (
                              <span className="ml-2 text-amber-600">(modifié manuellement)</span>
                            )}
                          </div>
                        </div>
                      ) : currentChapter.content ? (
                        <div className="book-content max-w-prose mx-auto" data-testid="chapter-content">
                          {renderContentParagraphs()}
                          <div className="mt-8 pt-8 border-t border-stone-100 text-center text-sm text-muted-foreground">
                            {currentChapter.word_count ? currentChapter.word_count.toLocaleString() : 0} mots
                            {currentChapter.edited_manually && (
                              <span className="ml-2 text-amber-600">(modifié manuellement)</span>
                            )}
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-16" data-testid="chapter-not-generated">
                          <BookOpen className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                          <p className="text-muted-foreground mb-2">{currentChapter.summary}</p>
                          <p className="text-sm text-muted-foreground mb-6">Ce chapitre n'a pas encore été généré.</p>
                          {(book.status === 'outline_ready' || book.status === 'generating') && (
                            <Button 
                              onClick={() => generateSingleChapter(currentChapter.number)}
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
