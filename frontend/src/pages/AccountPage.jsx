import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { 
  User, Mail, Lock, CreditCard, Calendar, BookOpen, 
  Loader2, Check, X, AlertTriangle, Crown, Infinity, Eye, EyeOff
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AccountPage() {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  });
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [cancelLoading, setCancelLoading] = useState(false);
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);
  const [showConfirmPw, setShowConfirmPw] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login?redirect=/account');
      return;
    }
    fetchSubscriptionDetails();
  }, [user, navigate]);

  const fetchSubscriptionDetails = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(`${API}/account/subscription`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSubscription(response.data);
    } catch (error) {
      console.error("Error fetching subscription:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error("Les mots de passe ne correspondent pas");
      return;
    }
    
    if (passwordForm.newPassword.length < 6) {
      toast.error("Le nouveau mot de passe doit contenir au moins 6 caractères");
      return;
    }
    
    setPasswordLoading(true);
    try {
      const token = localStorage.getItem('auth_token');
      await axios.post(`${API}/account/change-password`, {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success("Mot de passe modifié avec succès");
      setPasswordForm({ currentPassword: "", newPassword: "", confirmPassword: "" });
    } catch (error) {
      const message = error.response?.data?.detail || "Erreur lors du changement de mot de passe";
      toast.error(message);
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm("Êtes-vous sûr de vouloir annuler votre abonnement ? Vous conserverez l'accès jusqu'à la fin de la période en cours.")) {
      return;
    }
    
    setCancelLoading(true);
    try {
      const token = localStorage.getItem('auth_token');
      await axios.post(`${API}/account/cancel-subscription`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success("Abonnement annulé. Vous conservez l'accès jusqu'à la fin de la période.");
      fetchSubscriptionDetails();
    } catch (error) {
      const message = error.response?.data?.detail || "Erreur lors de l'annulation";
      toast.error(message);
    } finally {
      setCancelLoading(false);
    }
  };

  const handleReactivateSubscription = async () => {
    setCancelLoading(true);
    try {
      const token = localStorage.getItem('auth_token');
      await axios.post(`${API}/account/reactivate-subscription`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success("Abonnement réactivé avec succès");
      fetchSubscriptionDetails();
    } catch (error) {
      const message = error.response?.data?.detail || "Erreur lors de la réactivation";
      toast.error(message);
    } finally {
      setCancelLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="max-w-4xl mx-auto px-6 md:px-12 py-12">
        <h1 className="font-serif text-4xl font-bold mb-8">Mon compte</h1>
        
        <div className="space-y-8">
          {/* Profile Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Informations personnelles
              </CardTitle>
              <CardDescription>
                Vos informations de compte
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Nom</Label>
                  <p className="font-medium">{user.name}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Email</Label>
                  <p className="font-medium flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {user.email}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Subscription Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                Abonnement
              </CardTitle>
              <CardDescription>
                Gérez votre abonnement et vos crédits
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin" />
                </div>
              ) : subscription ? (
                <div className="space-y-6">
                  {/* Current Plan */}
                  <div className="flex items-center justify-between p-4 bg-stone-50 rounded-sm">
                    <div className="flex items-center gap-4">
                      {subscription.is_admin ? (
                        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                          <Crown className="w-6 h-6 text-primary" />
                        </div>
                      ) : subscription.is_active ? (
                        <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                          <Check className="w-6 h-6 text-green-600" />
                        </div>
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-stone-200 flex items-center justify-center">
                          <X className="w-6 h-6 text-stone-500" />
                        </div>
                      )}
                      <div>
                        <h3 className="font-semibold text-lg">
                          {subscription.plan_details?.name || 
                           (subscription.is_admin ? "Administrateur" : "Aucun abonnement")}
                        </h3>
                        {subscription.is_admin ? (
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Infinity className="w-4 h-4" />
                            Accès illimité
                          </p>
                        ) : subscription.is_active && subscription.expires ? (
                          <p className="text-sm text-muted-foreground">
                            Expire le {formatDate(subscription.expires)}
                            {subscription.days_remaining > 0 && ` (${subscription.days_remaining} jours restants)`}
                          </p>
                        ) : null}
                      </div>
                    </div>
                    
                    {!subscription.is_admin && subscription.plan_details && (
                      <div className="text-right">
                        <p className="text-2xl font-bold">{subscription.plan_details.price}€</p>
                        <p className="text-sm text-muted-foreground">/mois</p>
                      </div>
                    )}
                  </div>

                  {/* Usage Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 border border-border rounded-sm">
                      <p className="text-sm text-muted-foreground mb-1">Livres ce mois</p>
                      <p className="text-2xl font-bold">
                        {subscription.books_this_month}
                        {subscription.plan_details?.books_per_month > 0 && (
                          <span className="text-base font-normal text-muted-foreground">
                            /{subscription.plan_details.books_per_month}
                          </span>
                        )}
                        {(subscription.is_admin || subscription.plan_details?.books_per_month === -1) && (
                          <span className="text-base font-normal text-muted-foreground">/∞</span>
                        )}
                      </p>
                    </div>
                    <div className="p-4 border border-border rounded-sm">
                      <p className="text-sm text-muted-foreground mb-1">Chapitres max/livre</p>
                      <p className="text-2xl font-bold">
                        {subscription.is_admin || subscription.plan_details?.max_chapters === -1 
                          ? "∞" 
                          : subscription.plan_details?.max_chapters || 15}
                      </p>
                    </div>
                    <div className="p-4 border border-border rounded-sm">
                      <p className="text-sm text-muted-foreground mb-1">Crédits livres uniques</p>
                      <p className="text-2xl font-bold">{subscription.single_book_credits}</p>
                    </div>
                  </div>

                  {/* Actions */}
                  <Separator />
                  <div className="flex flex-wrap gap-4">
                    {!subscription.is_admin && !subscription.is_active && (
                      <Button onClick={() => navigate('/pricing')} data-testid="btn-subscribe">
                        <CreditCard className="w-4 h-4 mr-2" />
                        S'abonner
                      </Button>
                    )}
                    
                    {!subscription.is_admin && subscription.is_active && subscription.can_cancel && (
                      <>
                        <Button 
                          variant="outline" 
                          onClick={() => navigate('/pricing')}
                          data-testid="btn-upgrade"
                        >
                          Changer de plan
                        </Button>
                        <Button 
                          variant="destructive" 
                          onClick={handleCancelSubscription}
                          disabled={cancelLoading}
                          data-testid="btn-cancel-subscription"
                        >
                          {cancelLoading ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <X className="w-4 h-4 mr-2" />
                          )}
                          Annuler l'abonnement
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">Impossible de charger les informations d'abonnement</p>
              )}
            </CardContent>
          </Card>

          {/* Password Change Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Sécurité
              </CardTitle>
              <CardDescription>
                Modifiez votre mot de passe
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
                <div className="space-y-2">
                  <Label htmlFor="currentPassword">Mot de passe actuel</Label>
                  <div className="relative">
                    <Input
                      id="currentPassword"
                      type={showCurrentPw ? "text" : "password"}
                      value={passwordForm.currentPassword}
                      onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                      required
                      className="pr-10"
                      data-testid="current-password-input"
                    />
                    <button type="button" onClick={() => setShowCurrentPw(!showCurrentPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors" tabIndex={-1} data-testid="toggle-current-pw">
                      {showCurrentPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="newPassword">Nouveau mot de passe</Label>
                  <div className="relative">
                    <Input
                      id="newPassword"
                      type={showNewPw ? "text" : "password"}
                      value={passwordForm.newPassword}
                      onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                      required
                      minLength={6}
                      className="pr-10"
                      data-testid="new-password-input"
                    />
                    <button type="button" onClick={() => setShowNewPw(!showNewPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors" tabIndex={-1} data-testid="toggle-new-pw">
                      {showNewPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirmer le nouveau mot de passe</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPw ? "text" : "password"}
                      value={passwordForm.confirmPassword}
                      onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      required
                      minLength={6}
                      className="pr-10"
                      data-testid="confirm-password-input"
                    />
                    <button type="button" onClick={() => setShowConfirmPw(!showConfirmPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors" tabIndex={-1} data-testid="toggle-confirm-pw">
                      {showConfirmPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                
                <Button type="submit" disabled={passwordLoading} data-testid="btn-change-password">
                  {passwordLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Modification...
                    </>
                  ) : (
                    "Modifier le mot de passe"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
