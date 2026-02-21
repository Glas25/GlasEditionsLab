import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, Mail, ArrowLeft, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.detail || "Erreur lors de l'envoi");
        return;
      }

      setSent(true);
    } catch {
      toast.error("Erreur lors de l'envoi. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        <Link to="/" className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 bg-primary rounded-sm flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-primary-foreground" />
          </div>
          <span className="font-serif text-2xl font-semibold tracking-tight">GlasEditionsLab</span>
        </Link>

        <Card className="border-stone-200 shadow-sm">
          <CardHeader className="text-center">
            <CardTitle className="font-serif text-2xl">Mot de passe oublié</CardTitle>
            <CardDescription>
              {sent
                ? "Vérifiez votre boîte de réception"
                : "Entrez votre email pour recevoir un lien de réinitialisation"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {sent ? (
              <div className="text-center space-y-4" data-testid="forgot-password-success">
                <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">
                    Si un compte existe avec l'adresse <strong>{email}</strong>, vous recevrez un email avec un lien pour réinitialiser votre mot de passe.
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Le lien expire dans 1 heure. Pensez à vérifier vos spams.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => { setSent(false); setEmail(""); }}
                  className="rounded-sm"
                  data-testid="resend-btn"
                >
                  Renvoyer un email
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Adresse email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="vous@exemple.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10 h-12 rounded-sm"
                      required
                      data-testid="forgot-email-input"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 rounded-sm bg-primary text-primary-foreground hover:bg-primary/90 font-serif"
                  data-testid="forgot-submit-btn"
                >
                  {loading ? "Envoi en cours..." : "Envoyer le lien de réinitialisation"}
                </Button>
              </form>
            )}

            <div className="text-center">
              <Link to="/login" className="text-sm text-primary hover:underline inline-flex items-center gap-1" data-testid="back-to-login">
                <ArrowLeft className="w-3 h-3" />
                Retour à la connexion
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
