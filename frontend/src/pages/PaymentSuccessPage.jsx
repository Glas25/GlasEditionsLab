import { useEffect, useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useAuth } from "@/App";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Loader2, BookOpen, ArrowRight } from "lucide-react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function PaymentSuccessPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { checkAuth } = useAuth();
  const [status, setStatus] = useState("loading");
  const [paymentData, setPaymentData] = useState(null);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      pollPaymentStatus(sessionId);
    } else {
      setStatus("error");
    }
  }, [searchParams]);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 10;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      setStatus("timeout");
      return;
    }

    try {
      const response = await axios.get(`${API}/checkout/status/${sessionId}`);
      setPaymentData(response.data);

      if (response.data.payment_status === "paid") {
        setStatus("success");
        // Refresh user auth to get updated subscription
        await checkAuth();
        return;
      } else if (response.data.status === "expired") {
        setStatus("expired");
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error("Error checking payment status:", error);
      if (attempts < maxAttempts - 1) {
        setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
      } else {
        setStatus("error");
      }
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6 py-12">
      <Card className="max-w-md w-full border-stone-200">
        <CardContent className="py-12 text-center">
          {status === "loading" && (
            <>
              <Loader2 className="w-16 h-16 mx-auto text-primary animate-spin mb-6" />
              <h2 className="font-serif text-2xl font-semibold mb-2">Vérification du paiement...</h2>
              <p className="text-muted-foreground">Veuillez patienter quelques instants.</p>
            </>
          )}

          {status === "success" && (
            <>
              <CheckCircle className="w-16 h-16 mx-auto text-green-600 mb-6" />
              <h2 className="font-serif text-2xl font-semibold mb-2">Paiement réussi !</h2>
              <p className="text-muted-foreground mb-8">
                Merci pour votre achat. Vous pouvez maintenant créer vos livres.
              </p>
              <div className="space-y-3">
                <Link to="/create">
                  <Button className="w-full h-12 rounded-sm bg-primary text-primary-foreground hover:bg-primary/90 font-serif">
                    <BookOpen className="w-4 h-4 mr-2" />
                    Créer mon premier livre
                  </Button>
                </Link>
                <Link to="/dashboard">
                  <Button variant="outline" className="w-full h-11 rounded-sm">
                    Aller au tableau de bord
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </>
          )}

          {status === "expired" && (
            <>
              <XCircle className="w-16 h-16 mx-auto text-amber-500 mb-6" />
              <h2 className="font-serif text-2xl font-semibold mb-2">Session expirée</h2>
              <p className="text-muted-foreground mb-8">
                Votre session de paiement a expiré. Veuillez réessayer.
              </p>
              <Link to="/pricing">
                <Button className="h-11 px-8 rounded-sm bg-primary text-primary-foreground hover:bg-primary/90">
                  Retour aux tarifs
                </Button>
              </Link>
            </>
          )}

          {(status === "error" || status === "timeout") && (
            <>
              <XCircle className="w-16 h-16 mx-auto text-destructive mb-6" />
              <h2 className="font-serif text-2xl font-semibold mb-2">
                {status === "timeout" ? "Délai dépassé" : "Erreur"}
              </h2>
              <p className="text-muted-foreground mb-8">
                {status === "timeout" 
                  ? "La vérification du paiement a pris trop de temps. Si vous avez été débité, votre abonnement sera activé sous peu."
                  : "Une erreur est survenue lors de la vérification du paiement."
                }
              </p>
              <div className="space-y-3">
                <Link to="/dashboard">
                  <Button className="w-full h-11 rounded-sm bg-primary text-primary-foreground hover:bg-primary/90">
                    Aller au tableau de bord
                  </Button>
                </Link>
                <Link to="/pricing">
                  <Button variant="outline" className="w-full h-11 rounded-sm">
                    Retour aux tarifs
                  </Button>
                </Link>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
