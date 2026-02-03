import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Check, Sparkles, BookOpen, Image as ImageIcon, FileDown, Loader2 } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function PricingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [plans, setPlans] = useState([]);
  const [singleBookPrice, setSingleBookPrice] = useState(9.90);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await axios.get(`${API}/plans`);
      setPlans(response.data.plans);
      setSingleBookPrice(response.data.single_book_price);
    } catch (error) {
      console.error("Error fetching plans:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId) => {
    if (!user) {
      toast.error("Vous devez être connecté pour souscrire");
      navigate('/login');
      return;
    }

    setCheckoutLoading(planId);
    try {
      const response = await axios.post(`${API}/checkout/subscription`, {
        plan_id: planId,
        origin_url: window.location.origin
      }, {
        headers: user ? { Authorization: `Bearer ${localStorage.getItem('auth_token')}` } : {}
      });
      
      window.location.href = response.data.checkout_url;
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de la création du paiement");
      setCheckoutLoading(null);
    }
  };

  const handleSingleBookPurchase = async () => {
    if (!user) {
      toast.error("Vous devez être connecté pour acheter");
      navigate('/login');
      return;
    }

    setCheckoutLoading('single');
    try {
      const response = await axios.post(`${API}/checkout/single-book`, {
        origin_url: window.location.origin
      }, {
        headers: user ? { Authorization: `Bearer ${localStorage.getItem('auth_token')}` } : {}
      });
      
      window.location.href = response.data.checkout_url;
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de la création du paiement");
      setCheckoutLoading(null);
    }
  };

  const getPlanFeatures = (plan) => {
    const features = [];
    
    if (plan.books_per_month === -1) {
      features.push("Livres illimités par mois");
    } else {
      features.push(`${plan.books_per_month} livres par mois`);
    }
    
    if (plan.max_chapters === -1) {
      features.push("Chapitres illimités par livre");
    } else {
      features.push(`Jusqu'à ${plan.max_chapters} chapitres par livre`);
    }
    
    features.push("Export PDF, HTML, TXT");
    
    if (plan.cover_generation) {
      features.push("Génération de couvertures IA");
    }
    
    return features;
  };

  return (
    <div className="min-h-screen bg-background paper-texture">
      <Navbar />
      
      <main className="max-w-6xl mx-auto px-6 md:px-12 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="font-serif text-4xl md:text-5xl font-bold tracking-tight mb-4" data-testid="pricing-title">
            Choisissez votre plan
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Transformez vos idées en livres complets avec l'IA. Choisissez le plan qui correspond à vos besoins.
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="book-loader">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          </div>
        ) : (
          <>
            {/* Plans Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
              {plans.map((plan) => (
                <Card 
                  key={plan.id} 
                  className={`relative border-2 transition-all ${
                    plan.popular 
                      ? 'border-primary shadow-lg scale-105 z-10' 
                      : 'border-stone-200 hover:border-stone-300'
                  }`}
                  data-testid={`plan-${plan.id}`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span className="bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-medium flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        Le plus populaire
                      </span>
                    </div>
                  )}
                  
                  <CardHeader className="text-center pb-4">
                    <CardTitle className="font-serif text-2xl">{plan.name}</CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                  </CardHeader>
                  
                  <CardContent className="text-center">
                    <div className="mb-6">
                      <span className="text-5xl font-serif font-bold">{plan.price}€</span>
                      <span className="text-muted-foreground">/mois</span>
                    </div>
                    
                    <ul className="space-y-3 text-left mb-6">
                      {getPlanFeatures(plan).map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <Check className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                  
                  <CardFooter>
                    <Button 
                      className={`w-full h-12 rounded-sm font-serif ${
                        plan.popular 
                          ? 'bg-primary text-primary-foreground hover:bg-primary/90' 
                          : 'bg-stone-900 text-white hover:bg-stone-800'
                      }`}
                      onClick={() => handleSubscribe(plan.id)}
                      disabled={checkoutLoading === plan.id}
                      data-testid={`subscribe-${plan.id}`}
                    >
                      {checkoutLoading === plan.id ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Chargement...
                        </>
                      ) : (
                        user?.subscription === plan.id ? 'Plan actuel' : 'Souscrire'
                      )}
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>

            {/* Single Book Option */}
            <Card className="max-w-xl mx-auto border-2 border-dashed border-stone-300" data-testid="single-book-option">
              <CardContent className="py-8 text-center">
                <BookOpen className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-serif text-xl font-semibold mb-2">Juste un livre ?</h3>
                <p className="text-muted-foreground mb-4">
                  Achetez un crédit pour un seul livre sans abonnement.
                </p>
                <div className="mb-6">
                  <span className="text-3xl font-serif font-bold">{singleBookPrice}€</span>
                  <span className="text-muted-foreground"> / livre</span>
                </div>
                <ul className="text-sm text-muted-foreground space-y-2 mb-6">
                  <li className="flex items-center justify-center gap-2">
                    <Check className="w-4 h-4 text-primary" />
                    Jusqu'à 30 chapitres
                  </li>
                  <li className="flex items-center justify-center gap-2">
                    <Check className="w-4 h-4 text-primary" />
                    Génération de couverture incluse
                  </li>
                  <li className="flex items-center justify-center gap-2">
                    <Check className="w-4 h-4 text-primary" />
                    Export PDF, HTML, TXT
                  </li>
                </ul>
                <Button 
                  variant="outline" 
                  className="h-11 px-8 rounded-sm"
                  onClick={handleSingleBookPurchase}
                  disabled={checkoutLoading === 'single'}
                  data-testid="buy-single-book"
                >
                  {checkoutLoading === 'single' ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Chargement...
                    </>
                  ) : (
                    'Acheter un livre'
                  )}
                </Button>
              </CardContent>
            </Card>
          </>
        )}
      </main>
    </div>
  );
}
