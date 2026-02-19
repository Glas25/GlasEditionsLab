import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger
} from "@/components/ui/alert-dialog";
import {
  Users, BookOpen, TrendingUp, CreditCard, Search, Download, Trash2,
  ChevronLeft, ChevronRight, Loader2, Shield, UserX, Crown
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PLAN_LABELS = {
  admin: "Admin",
  debutant: "Débutant",
  auteur: "Auteur",
  ecrivain: "Écrivain",
  sans_abonnement: "Sans abonnement",
  credits_only: "Crédits uniquement"
};

const PLAN_COLORS = {
  admin: "bg-violet-100 text-violet-800",
  debutant: "bg-blue-100 text-blue-800",
  auteur: "bg-amber-100 text-amber-800",
  ecrivain: "bg-emerald-100 text-emerald-800"
};

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <Card data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="text-3xl font-bold mt-1">{value}</p>
            {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
          </div>
          <div className={`w-12 h-12 rounded-sm flex items-center justify-center ${color || 'bg-primary/10'}`}>
            <Icon className="w-6 h-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function UserRow({ user, onDelete }) {
  const planLabel = user.is_admin ? "Admin" : (PLAN_LABELS[user.subscription] || "Sans abonnement");
  const planColor = user.is_admin ? PLAN_COLORS.admin : (PLAN_COLORS[user.subscription] || "bg-stone-100 text-stone-600");
  const hasNoPlan = !user.is_admin && !user.subscription && user.single_book_credits === 0;

  return (
    <tr className={`border-b border-stone-100 hover:bg-stone-50/50 transition-colors ${hasNoPlan ? 'bg-red-50/30' : ''}`} data-testid={`user-row-${user.user_id}`}>
      <td className="py-3 px-4">
        <div>
          <p className="font-medium text-sm">{user.name}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
      </td>
      <td className="py-3 px-4">
        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${planColor}`}>
          {planLabel}
        </span>
        {user.single_book_credits > 0 && !user.subscription && (
          <span className="ml-1 text-xs font-medium px-2 py-1 rounded-full bg-sky-100 text-sky-800">
            {user.single_book_credits} crédit(s)
          </span>
        )}
      </td>
      <td className="py-3 px-4 text-sm text-center">{user.books_count}</td>
      <td className="py-3 px-4 text-sm text-center">{user.books_this_month}</td>
      <td className="py-3 px-4 text-sm text-muted-foreground">
        {user.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : 'N/A'}
      </td>
      <td className="py-3 px-4 text-right">
        {!user.is_admin && (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10" data-testid={`delete-user-${user.user_id}`}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Supprimer cet utilisateur ?</AlertDialogTitle>
                <AlertDialogDescription>
                  Cette action est irréversible. L'utilisateur <strong>{user.name}</strong> ({user.email}) et tous ses livres ({user.books_count}) seront définitivement supprimés.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel className="rounded-sm">Annuler</AlertDialogCancel>
                <AlertDialogAction onClick={() => onDelete(user.user_id)} className="bg-destructive text-destructive-foreground hover:bg-destructive/90 rounded-sm">
                  Supprimer
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
      </td>
    </tr>
  );
}

export default function AdminDashboard() {
  const { user, token, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usersLoading, setUsersLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [planFilter, setPlanFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    if (authLoading) return;
    if (!user || user.subscription !== 'admin') {
      navigate('/');
      return;
    }
    fetchStats();
  }, [user, navigate, authLoading]);

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API}/admin/stats`, { headers });
      setStats(res.data);
    } catch (err) {
      toast.error("Erreur lors du chargement des statistiques");
    }
  };

  const fetchUsers = useCallback(async () => {
    setUsersLoading(true);
    try {
      const params = { page, limit: 20 };
      if (search) params.search = search;
      if (planFilter !== "all") params.plan = planFilter;
      const res = await axios.get(`${API}/admin/users`, { headers, params });
      setUsers(res.data.users);
      setTotalPages(res.data.total_pages);
      setTotalUsers(res.data.total);
    } catch (err) {
      toast.error("Erreur lors du chargement des utilisateurs");
    } finally {
      setUsersLoading(false);
      setLoading(false);
    }
  }, [page, search, planFilter]);

  useEffect(() => {
    if (!authLoading && user && user.subscription === 'admin') {
      fetchUsers();
    }
  }, [fetchUsers, user, authLoading]);

  const handleSearch = (value) => {
    setSearch(value);
    setPage(1);
  };

  const handleFilterChange = (value) => {
    setPlanFilter(value);
    setPage(1);
  };

  const handleDeleteUser = async (userId) => {
    try {
      await axios.delete(`${API}/admin/users/${userId}`, { headers });
      toast.success("Utilisateur supprimé");
      fetchUsers();
      fetchStats();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erreur lors de la suppression");
    }
  };

  const handleExport = () => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (planFilter !== "all") params.set("plan", planFilter);
    const tokenParam = token ? `&token=${token}` : '';
    window.open(`${API}/admin/users/export?${params.toString()}${tokenParam}`, '_blank');
    toast.success("Export CSV en cours...");
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="flex items-center justify-center py-24">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (!user || user.subscription !== 'admin') return null;

  return (
    <div className="min-h-screen bg-background" data-testid="admin-dashboard">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 md:px-12 py-12">
        <div className="flex items-center gap-3 mb-10">
          <div className="w-10 h-10 bg-violet-100 rounded-sm flex items-center justify-center">
            <Shield className="w-5 h-5 text-violet-700" />
          </div>
          <div>
            <h1 className="font-serif text-4xl font-bold tracking-tight" data-testid="admin-title">
              Administration
            </h1>
            <p className="text-muted-foreground">Gestion de la plateforme GlasEditionsLab</p>
          </div>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10" data-testid="stats-grid">
            <StatCard icon={Users} label="Utilisateurs" value={stats.total_users} color="bg-blue-50" />
            <StatCard icon={BookOpen} label="Livres créés" value={stats.total_books} sub={`${stats.books_this_month} ce mois`} color="bg-emerald-50" />
            <StatCard icon={UserX} label="Sans abonnement" value={stats.no_plan_users} sub="Inscrits sans plan" color="bg-red-50" />
            <StatCard icon={TrendingUp} label="Revenus estimés" value={`${stats.estimated_monthly_revenue}€`} sub="/mois" color="bg-amber-50" />
          </div>
        )}

        {/* Subscription Breakdown */}
        {stats && (
          <Card className="mb-10" data-testid="subscription-breakdown">
            <CardHeader>
              <CardTitle className="text-lg font-serif flex items-center gap-2">
                <Crown className="w-5 h-5" />
                Répartition des abonnements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                {Object.entries(stats.subscription_distribution).map(([key, count]) => {
                  const label = PLAN_LABELS[key] || key;
                  const color = PLAN_COLORS[key] || "bg-stone-100 text-stone-600";
                  return (
                    <div key={key} className="text-center p-4 rounded-sm border border-stone-100" data-testid={`sub-dist-${key}`}>
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${color}`}>{label}</span>
                      <p className="text-2xl font-bold mt-3">{count}</p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Users Table */}
        <Card data-testid="users-table-card">
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <CardTitle className="text-lg font-serif flex items-center gap-2">
                <Users className="w-5 h-5" />
                Utilisateurs ({totalUsers})
              </CardTitle>
              <Button variant="outline" onClick={handleExport} className="rounded-sm" data-testid="btn-export-users">
                <Download className="w-4 h-4 mr-2" />
                Exporter CSV
              </Button>
            </div>

            <div className="flex flex-col md:flex-row gap-3 mt-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher par nom ou email..."
                  value={search}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10 h-10 rounded-sm"
                  data-testid="admin-search-input"
                />
              </div>
              <Select value={planFilter} onValueChange={handleFilterChange}>
                <SelectTrigger className="w-full md:w-52 h-10 rounded-sm" data-testid="admin-plan-filter">
                  <SelectValue placeholder="Filtrer par plan" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les plans</SelectItem>
                  <SelectItem value="sans_abonnement">Sans abonnement</SelectItem>
                  <SelectItem value="debutant">Débutant</SelectItem>
                  <SelectItem value="auteur">Auteur</SelectItem>
                  <SelectItem value="ecrivain">Écrivain</SelectItem>
                  <SelectItem value="credits_only">Crédits uniquement</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>

          <CardContent>
            {usersLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
              </div>
            ) : users.length === 0 ? (
              <div className="text-center py-16 text-muted-foreground">
                <UserX className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Aucun utilisateur trouvé</p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full" data-testid="users-table">
                    <thead>
                      <tr className="border-b-2 border-stone-200 text-left">
                        <th className="py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Utilisateur</th>
                        <th className="py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Plan</th>
                        <th className="py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider text-center">Livres</th>
                        <th className="py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider text-center">Ce mois</th>
                        <th className="py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Inscription</th>
                        <th className="py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map(u => <UserRow key={u.user_id} user={u} onDelete={handleDeleteUser} />)}
                    </tbody>
                  </table>
                </div>

                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-6 pt-4 border-t border-stone-100">
                    <p className="text-sm text-muted-foreground">
                      Page {page} sur {totalPages}
                    </p>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="rounded-sm" data-testid="btn-prev-page">
                        <ChevronLeft className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="rounded-sm" data-testid="btn-next-page">
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
