import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BookOpen, Plus, Search, CheckCircle, Clock, Loader2, AlertCircle, Filter } from "lucide-react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const statusConfig = {
  draft: { label: "Brouillon", color: "status-draft", icon: Clock },
  generating_outline: { label: "Création du plan", color: "status-generating", icon: Loader2 },
  outline_ready: { label: "Plan prêt", color: "status-draft", icon: CheckCircle },
  generating: { label: "En cours", color: "status-generating", icon: Loader2 },
  completed: { label: "Terminé", color: "status-completed", icon: CheckCircle },
  error: { label: "Erreur", color: "status-error", icon: AlertCircle }
};

const genres = [
  { value: "all", label: "Tous les genres" },
  { value: "fiction", label: "Fiction" },
  { value: "non_fiction", label: "Non-Fiction" },
  { value: "romance", label: "Romance" },
  { value: "thriller", label: "Thriller" },
  { value: "fantasy", label: "Fantasy" },
  { value: "science_fiction", label: "Science-Fiction" },
  { value: "mystery", label: "Mystère" },
  { value: "horror", label: "Horreur" },
  { value: "biography", label: "Biographie" },
  { value: "self_help", label: "Développement personnel" },
  { value: "history", label: "Histoire" },
  { value: "business", label: "Business" }
];

export default function Library() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const response = await axios.get(`${API}/books`);
      setBooks(response.data);
    } catch (error) {
      console.error("Error fetching books:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredBooks = books.filter(book => {
    const matchesSearch = book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          book.idea.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGenre = selectedGenre === "all" || book.genre === selectedGenre;
    const matchesStatus = selectedStatus === "all" || book.status === selectedStatus;
    return matchesSearch && matchesGenre && matchesStatus;
  });

  const getProgress = (book) => {
    if (!book.outline || book.outline.length === 0) return 0;
    const completed = book.outline.filter(ch => ch.status === 'completed').length;
    return Math.round((completed / book.outline.length) * 100);
  };

  return (
    <div className="min-h-screen bg-background paper-texture">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-6 md:px-12 py-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
          <div>
            <h1 className="font-serif text-4xl font-bold tracking-tight mb-2" data-testid="library-title">
              Bibliothèque
            </h1>
            <p className="text-muted-foreground">
              {books.length} livre{books.length !== 1 ? 's' : ''} au total
            </p>
          </div>
          <Link to="/create">
            <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-serif tracking-wide" data-testid="library-create-btn">
              <Plus className="w-4 h-4 mr-2" />
              Nouveau livre
            </Button>
          </Link>
        </div>
        
        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              data-testid="search-input"
              placeholder="Rechercher un livre..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-11 rounded-sm border-stone-200"
            />
          </div>
          <Select value={selectedGenre} onValueChange={setSelectedGenre}>
            <SelectTrigger className="w-full md:w-48 h-11 rounded-sm border-stone-200" data-testid="filter-genre">
              <SelectValue placeholder="Genre" />
            </SelectTrigger>
            <SelectContent>
              {genres.map(genre => (
                <SelectItem key={genre.value} value={genre.value}>{genre.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={selectedStatus} onValueChange={setSelectedStatus}>
            <SelectTrigger className="w-full md:w-48 h-11 rounded-sm border-stone-200" data-testid="filter-status">
              <SelectValue placeholder="Statut" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les statuts</SelectItem>
              <SelectItem value="draft">Brouillon</SelectItem>
              <SelectItem value="generating_outline">Création du plan</SelectItem>
              <SelectItem value="outline_ready">Plan prêt</SelectItem>
              <SelectItem value="generating">En cours</SelectItem>
              <SelectItem value="completed">Terminé</SelectItem>
              <SelectItem value="error">Erreur</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="book-loader">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          </div>
        ) : filteredBooks.length === 0 ? (
          <Card className="border-dashed border-2 border-stone-200" data-testid="empty-library">
            <CardContent className="py-16 text-center">
              <BookOpen className="w-16 h-16 mx-auto text-muted-foreground mb-6" />
              <h2 className="font-serif text-2xl font-semibold mb-3">
                {books.length === 0 ? "Votre bibliothèque est vide" : "Aucun résultat"}
              </h2>
              <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                {books.length === 0 
                  ? "Commencez par créer votre premier livre pour le voir apparaître ici."
                  : "Essayez de modifier vos filtres de recherche."
                }
              </p>
              {books.length === 0 && (
                <Link to="/create">
                  <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-serif tracking-wide">
                    <Plus className="w-4 h-4 mr-2" />
                    Créer mon premier livre
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBooks.map((book) => {
              const status = statusConfig[book.status];
              const StatusIcon = status?.icon || Clock;
              const progress = getProgress(book);
              
              return (
                <Link to={`/book/${book.id}`} key={book.id} data-testid={`library-book-${book.id}`}>
                  <Card className="book-card card-hover h-full">
                    <CardHeader>
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1 min-w-0">
                          <CardTitle className="font-serif text-lg line-clamp-2">{book.title}</CardTitle>
                          <CardDescription className="line-clamp-2">{book.idea}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {/* Status & Genre */}
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`status-badge ${status?.color}`}>
                            <StatusIcon className={`w-3 h-3 ${book.status.includes('generating') ? 'animate-spin' : ''}`} />
                            {status?.label}
                          </span>
                          <span className="text-xs px-2 py-1 bg-stone-100 rounded-full capitalize">
                            {book.genre?.replace('_', ' ')}
                          </span>
                        </div>
                        
                        {/* Progress */}
                        {book.outline?.length > 0 && (
                          <div className="space-y-2">
                            <div className="flex justify-between text-xs text-muted-foreground">
                              <span>{book.outline.filter(ch => ch.status === 'completed').length}/{book.outline.length} chapitres</span>
                              <span>{progress}%</span>
                            </div>
                            <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                              <div 
                                className={`h-full bg-primary rounded-full transition-all duration-500 ${book.status.includes('generating') ? 'progress-generating' : ''}`}
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                          </div>
                        )}
                        
                        {/* Meta */}
                        <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t border-stone-100">
                          <span>{book.total_word_count?.toLocaleString() || 0} mots</span>
                          <span>•</span>
                          <span className="capitalize">{book.tone}</span>
                          <span>•</span>
                          <span>{book.language}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
