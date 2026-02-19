import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, Sparkles, ArrowRight, ArrowLeft, Check } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const genres = [
  { value: "fiction", label: "Fiction", desc: "Histoires imaginaires captivantes" },
  { value: "non_fiction", label: "Non-Fiction", desc: "Contenu informatif et documenté" },
  { value: "romance", label: "Romance", desc: "Amour et relations émotionnelles" },
  { value: "thriller", label: "Thriller", desc: "Suspense et rebondissements" },
  { value: "fantasy", label: "Fantasy", desc: "Mondes magiques et imaginaires" },
  { value: "science_fiction", label: "Science-Fiction", desc: "Futur et technologies" },
  { value: "mystery", label: "Mystère", desc: "Enquêtes et énigmes" },
  { value: "horror", label: "Horreur", desc: "Terreur et atmosphère sombre" },
  { value: "biography", label: "Biographie", desc: "Récits de vie inspirants" },
  { value: "self_help", label: "Développement personnel", desc: "Conseils et croissance" },
  { value: "history", label: "Histoire", desc: "Événements historiques" },
  { value: "business", label: "Business", desc: "Entrepreneuriat et stratégie" }
];

const tones = [
  { value: "formal", label: "Formel", desc: "Professionnel et sérieux" },
  { value: "casual", label: "Décontracté", desc: "Accessible et amical" },
  { value: "literary", label: "Littéraire", desc: "Élégant et raffiné" },
  { value: "humorous", label: "Humoristique", desc: "Léger et amusant" },
  { value: "dramatic", label: "Dramatique", desc: "Intense et émotionnel" },
  { value: "poetic", label: "Poétique", desc: "Lyrique et évocateur" }
];

export default function CreateBook() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login?redirect=/pricing&message=subscription');
      return;
    }
    const hasAccess = user.subscription === 'admin' ||
      (user.subscription && user.subscription_expires && new Date(user.subscription_expires) > new Date()) ||
      user.single_book_credits > 0;
    if (!hasAccess) {
      navigate('/pricing');
    }
  }, [user, navigate]);
  
  const [formData, setFormData] = useState({
    title: "",
    idea: "",
    genre: "",
    tone: "",
    target_chapters: 25,
    language: "français",
    additional_info: ""
  });

  const updateForm = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const canProceed = () => {
    if (step === 1) return formData.title.trim() && formData.idea.trim();
    if (step === 2) return formData.genre && formData.tone;
    return true;
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/books`, formData);
      toast.success("Livre créé avec succès !", {
        description: "Redirection vers le tableau de bord..."
      });
      setTimeout(() => {
        navigate(`/book/${response.data.id}`);
      }, 1000);
    } catch (error) {
      console.error(error);
      toast.error("Erreur lors de la création", {
        description: error.response?.data?.detail || "Veuillez réessayer"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-4xl mx-auto px-6 md:px-12 py-12">
        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-4 mb-12" data-testid="progress-steps">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center gap-4">
              <div 
                className={`w-10 h-10 rounded-full flex items-center justify-center font-serif font-semibold transition-colors ${
                  s < step ? 'bg-primary text-primary-foreground' :
                  s === step ? 'bg-primary text-primary-foreground' :
                  'bg-muted text-muted-foreground'
                }`}
              >
                {s < step ? <Check className="w-5 h-5" /> : s}
              </div>
              {s < 3 && (
                <div className={`w-16 h-0.5 ${s < step ? 'bg-primary' : 'bg-muted'}`} />
              )}
            </div>
          ))}
        </div>
        
        {/* Step 1: Idea */}
        {step === 1 && (
          <div className="animate-fade-in" data-testid="step-1">
            <div className="text-center mb-10">
              <h1 className="font-serif text-4xl md:text-5xl font-bold tracking-tight mb-4">
                Quelle est votre idée ?
              </h1>
              <p className="text-lg text-muted-foreground">
                Donnez un titre et décrivez le concept de votre livre
              </p>
            </div>
            
            <Card className="border-stone-200 shadow-sm">
              <CardContent className="pt-8 space-y-8">
                <div className="space-y-3">
                  <Label htmlFor="title" className="text-base font-medium">Titre du livre</Label>
                  <Input
                    id="title"
                    data-testid="input-title"
                    placeholder="Ex: Les secrets de l'univers"
                    value={formData.title}
                    onChange={(e) => updateForm('title', e.target.value)}
                    className="h-14 text-lg font-serif rounded-sm border-stone-200 focus:border-primary focus:ring-primary"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="idea" className="text-base font-medium">Votre idée</Label>
                  <Textarea
                    id="idea"
                    data-testid="input-idea"
                    placeholder="Décrivez votre idée de livre... Qu'est-ce qui rend cette histoire unique ? Quels sont les thèmes principaux ? Qui sont les personnages clés ?"
                    value={formData.idea}
                    onChange={(e) => updateForm('idea', e.target.value)}
                    className="idea-input min-h-[180px] text-lg rounded-sm border-stone-200 focus:border-primary focus:ring-primary"
                  />
                  <p className="text-sm text-muted-foreground">
                    Plus votre description est détaillée, meilleur sera le résultat.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        {/* Step 2: Genre & Tone */}
        {step === 2 && (
          <div className="animate-fade-in" data-testid="step-2">
            <div className="text-center mb-10">
              <h1 className="font-serif text-4xl md:text-5xl font-bold tracking-tight mb-4">
                Genre & Ton
              </h1>
              <p className="text-lg text-muted-foreground">
                Choisissez le style de votre livre
              </p>
            </div>
            
            <div className="space-y-8">
              {/* Genre Selection */}
              <div className="space-y-4">
                <Label className="text-base font-medium">Genre</Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {genres.map((genre) => (
                    <button
                      key={genre.value}
                      data-testid={`genre-${genre.value}`}
                      onClick={() => updateForm('genre', genre.value)}
                      className={`p-4 text-left rounded-sm border transition-all ${
                        formData.genre === genre.value
                          ? 'border-primary bg-accent'
                          : 'border-stone-200 hover:border-stone-300 bg-card'
                      }`}
                    >
                      <p className="font-serif font-medium">{genre.label}</p>
                      <p className="text-sm text-muted-foreground">{genre.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Tone Selection */}
              <div className="space-y-4">
                <Label className="text-base font-medium">Ton</Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {tones.map((tone) => (
                    <button
                      key={tone.value}
                      data-testid={`tone-${tone.value}`}
                      onClick={() => updateForm('tone', tone.value)}
                      className={`p-4 text-left rounded-sm border transition-all ${
                        formData.tone === tone.value
                          ? 'border-primary bg-accent'
                          : 'border-stone-200 hover:border-stone-300 bg-card'
                      }`}
                    >
                      <p className="font-serif font-medium">{tone.label}</p>
                      <p className="text-sm text-muted-foreground">{tone.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Step 3: Settings */}
        {step === 3 && (
          <div className="animate-fade-in" data-testid="step-3">
            <div className="text-center mb-10">
              <h1 className="font-serif text-4xl md:text-5xl font-bold tracking-tight mb-4">
                Paramètres finaux
              </h1>
              <p className="text-lg text-muted-foreground">
                Personnalisez les derniers détails
              </p>
            </div>
            
            <Card className="border-stone-200 shadow-sm">
              <CardContent className="pt-8 space-y-8">
                {/* Chapter Count */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label className="text-base font-medium">Nombre de chapitres</Label>
                    <span className="font-serif text-2xl font-bold text-primary">{formData.target_chapters}</span>
                  </div>
                  <Slider
                    data-testid="slider-chapters"
                    value={[formData.target_chapters]}
                    onValueChange={(value) => updateForm('target_chapters', value[0])}
                    min={10}
                    max={50}
                    step={1}
                    className="py-4"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>10 (court)</span>
                    <span>30 (moyen)</span>
                    <span>50 (long)</span>
                  </div>
                </div>
                
                {/* Language */}
                <div className="space-y-3">
                  <Label className="text-base font-medium">Langue</Label>
                  <Select 
                    value={formData.language} 
                    onValueChange={(value) => updateForm('language', value)}
                  >
                    <SelectTrigger data-testid="select-language" className="h-12 rounded-sm border-stone-200">
                      <SelectValue placeholder="Choisir une langue" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="français">Français</SelectItem>
                      <SelectItem value="anglais">Anglais</SelectItem>
                      <SelectItem value="espagnol">Espagnol</SelectItem>
                      <SelectItem value="allemand">Allemand</SelectItem>
                      <SelectItem value="italien">Italien</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Additional Info */}
                <div className="space-y-3">
                  <Label htmlFor="additional" className="text-base font-medium">
                    Informations supplémentaires <span className="text-muted-foreground">(optionnel)</span>
                  </Label>
                  <Textarea
                    id="additional"
                    data-testid="input-additional"
                    placeholder="Ajoutez des détails spécifiques : noms de personnages, lieux, époque, style particulier..."
                    value={formData.additional_info}
                    onChange={(e) => updateForm('additional_info', e.target.value)}
                    className="min-h-[120px] rounded-sm border-stone-200 focus:border-primary focus:ring-primary"
                  />
                </div>
                
                {/* Summary */}
                <Card className="bg-accent/50 border-0">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg font-serif">Résumé de votre livre</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <p><strong>Titre :</strong> {formData.title}</p>
                    <p><strong>Genre :</strong> {genres.find(g => g.value === formData.genre)?.label}</p>
                    <p><strong>Ton :</strong> {tones.find(t => t.value === formData.tone)?.label}</p>
                    <p><strong>Chapitres :</strong> {formData.target_chapters}</p>
                    <p><strong>Langue :</strong> {formData.language}</p>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </div>
        )}
        
        {/* Navigation Buttons */}
        <div className="flex justify-between mt-10">
          {step > 1 ? (
            <Button 
              variant="outline" 
              onClick={() => setStep(s => s - 1)}
              className="h-12 px-8 rounded-sm"
              data-testid="btn-back"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour
            </Button>
          ) : (
            <div />
          )}
          
          {step < 3 ? (
            <Button 
              onClick={() => setStep(s => s + 1)}
              disabled={!canProceed()}
              className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-8 rounded-sm font-serif tracking-wide"
              data-testid="btn-next"
            >
              Suivant
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button 
              onClick={handleSubmit}
              disabled={isLoading}
              className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-10 rounded-sm font-serif tracking-wide"
              data-testid="btn-create"
            >
              {isLoading ? (
                <>
                  <div className="book-loader mr-3">
                    <span></span><span></span><span></span>
                  </div>
                  Création...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Créer mon livre
                </>
              )}
            </Button>
          )}
        </div>
      </main>
    </div>
  );
}
