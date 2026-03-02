import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { BookOpen, Plus, LayoutDashboard, Library as LibraryIcon, LogIn, LogOut, User, CreditCard, Shield, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const isActive = (path) => location.pathname === path;
  const isPricingPage = location.pathname === '/pricing';

  const handleLogout = async () => {
    setMobileOpen(false);
    await logout();
    navigate('/');
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const getSubscriptionLabel = () => {
    if (!user) return null;
    if (user.subscription === 'admin') return 'Admin ∞';
    if (user.subscription === 'debutant') return 'Débutant';
    if (user.subscription === 'auteur') return 'Auteur';
    if (user.subscription === 'ecrivain') return 'Écrivain';
    if (user.single_book_credits > 0) return `${user.single_book_credits} crédit(s)`;
    return null;
  };

  const canCreateBook = () => {
    if (!user) return false;
    if (user.subscription === 'admin') return true;
    if (user.subscription && user.subscription_expires) {
      const expires = new Date(user.subscription_expires);
      if (expires > new Date()) return true;
    }
    if (user.single_book_credits > 0) return true;
    return false;
  };

  const handleCreateBookClick = (e) => {
    setMobileOpen(false);
    if (!user) {
      e.preventDefault();
      navigate('/login?redirect=/pricing&message=subscription');
    } else if (!canCreateBook()) {
      e.preventDefault();
      navigate('/pricing');
    }
  };

  const mobileNav = (path) => {
    setMobileOpen(false);
    navigate(path);
  };

  const showAuthenticatedNav = user || !isPricingPage;
  
  return (
    <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group" data-testid="navbar-logo" onClick={() => setMobileOpen(false)}>
            <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center group-hover:-translate-y-0.5 transition-transform">
              <BookOpen className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-serif text-xl font-semibold tracking-tight">GlasEditionsLab</span>
          </Link>
          
          {/* Desktop Navigation Links */}
          {showAuthenticatedNav && (
            <div className="hidden md:flex items-center gap-8">
              <Link 
                to="/dashboard" 
                className={`nav-link flex items-center gap-2 ${isActive('/dashboard') ? 'active' : ''}`}
                data-testid="nav-dashboard"
              >
                <LayoutDashboard className="w-4 h-4" />
                Tableau de bord
              </Link>
              <Link 
                to="/library" 
                className={`nav-link flex items-center gap-2 ${isActive('/library') ? 'active' : ''}`}
                data-testid="nav-library"
              >
                <LibraryIcon className="w-4 h-4" />
                Bibliothèque
              </Link>
              <Link 
                to="/pricing" 
                className={`nav-link flex items-center gap-2 ${isActive('/pricing') ? 'active' : ''}`}
                data-testid="nav-pricing"
              >
                <CreditCard className="w-4 h-4" />
                Tarifs
              </Link>
            </div>
          )}
          
          {/* Right Side */}
          <div className="flex items-center gap-3">
            {/* Desktop: Nouveau livre button */}
            {showAuthenticatedNav && (
              <Link to="/create" onClick={handleCreateBookClick} data-testid="nav-create-book" className="hidden md:inline-flex">
                <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 rounded-sm font-serif tracking-wide">
                  <Plus className="w-4 h-4 mr-2" />
                  Nouveau livre
                </Button>
              </Link>
            )}
            
            {/* Desktop: User menu */}
            <div className="hidden md:block">
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-10 w-10 rounded-full" data-testid="user-menu-trigger">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={user.picture} alt={user.name} />
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {getInitials(user.name)}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-56" align="end">
                    <div className="flex items-center gap-3 p-3">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={user.picture} alt={user.name} />
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {getInitials(user.name)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex flex-col">
                        <span className="font-medium text-sm">{user.name}</span>
                        <span className="text-xs text-muted-foreground">{user.email}</span>
                        {getSubscriptionLabel() && (
                          <span className="text-xs text-primary font-medium">{getSubscriptionLabel()}</span>
                        )}
                      </div>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => navigate('/dashboard')}>
                      <LayoutDashboard className="w-4 h-4 mr-2" />
                      Tableau de bord
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => navigate('/library')}>
                      <LibraryIcon className="w-4 h-4 mr-2" />
                      Bibliothèque
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => navigate('/pricing')}>
                      <CreditCard className="w-4 h-4 mr-2" />
                      Tarifs
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => navigate('/account')} data-testid="nav-account">
                      <User className="w-4 h-4 mr-2" />
                      Mon compte
                    </DropdownMenuItem>
                    {user.subscription === 'admin' && (
                      <DropdownMenuItem onClick={() => navigate('/admin')} data-testid="nav-admin">
                        <Shield className="w-4 h-4 mr-2" />
                        Administration
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                      <LogOut className="w-4 h-4 mr-2" />
                      Déconnexion
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Link to="/login">
                  <Button variant="outline" className="h-10 px-4 rounded-sm" data-testid="login-btn">
                    <LogIn className="w-4 h-4 mr-2" />
                    Connexion
                  </Button>
                </Link>
              )}
            </div>

            {/* Mobile: Burger button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden h-10 w-10"
              onClick={() => setMobileOpen(!mobileOpen)}
              data-testid="mobile-menu-toggle"
              aria-label="Menu"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-background animate-in slide-in-from-top-2 duration-200">
          <div className="px-6 py-4 space-y-1">
            {/* User info */}
            {user && (
              <div className="flex items-center gap-3 pb-4 mb-3 border-b border-border">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={user.picture} alt={user.name} />
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    {getInitials(user.name)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col">
                  <span className="font-medium text-sm">{user.name}</span>
                  <span className="text-xs text-muted-foreground">{user.email}</span>
                  {getSubscriptionLabel() && (
                    <span className="text-xs text-primary font-medium">{getSubscriptionLabel()}</span>
                  )}
                </div>
              </div>
            )}

            {/* Nav links */}
            {showAuthenticatedNav && (
              <>
                <button
                  onClick={() => mobileNav('/dashboard')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${isActive('/dashboard') ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted'}`}
                  data-testid="mobile-nav-dashboard"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Tableau de bord
                </button>
                <button
                  onClick={() => mobileNav('/library')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${isActive('/library') ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted'}`}
                  data-testid="mobile-nav-library"
                >
                  <LibraryIcon className="w-4 h-4" />
                  Bibliothèque
                </button>
                <button
                  onClick={() => mobileNav('/pricing')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${isActive('/pricing') ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted'}`}
                  data-testid="mobile-nav-pricing"
                >
                  <CreditCard className="w-4 h-4" />
                  Tarifs
                </button>
              </>
            )}

            {user && (
              <>
                <div className="border-t border-border my-2" />
                <button
                  onClick={() => mobileNav('/account')}
                  className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${isActive('/account') ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted'}`}
                  data-testid="mobile-nav-account"
                >
                  <User className="w-4 h-4" />
                  Mon compte
                </button>
                {user.subscription === 'admin' && (
                  <button
                    onClick={() => mobileNav('/admin')}
                    className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${isActive('/admin') ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted'}`}
                    data-testid="mobile-nav-admin"
                  >
                    <Shield className="w-4 h-4" />
                    Administration
                  </button>
                )}
              </>
            )}

            {/* Actions */}
            <div className="border-t border-border my-2 pt-2 space-y-2">
              {showAuthenticatedNav && (
                <Link to="/create" onClick={handleCreateBookClick} className="block">
                  <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10 rounded-sm font-serif tracking-wide" data-testid="mobile-nav-create">
                    <Plus className="w-4 h-4 mr-2" />
                    Nouveau livre
                  </Button>
                </Link>
              )}
              {user ? (
                <Button variant="outline" className="w-full h-10 rounded-sm text-destructive hover:text-destructive" onClick={handleLogout} data-testid="mobile-nav-logout">
                  <LogOut className="w-4 h-4 mr-2" />
                  Déconnexion
                </Button>
              ) : (
                <Link to="/login" onClick={() => setMobileOpen(false)} className="block">
                  <Button variant="outline" className="w-full h-10 rounded-sm" data-testid="mobile-login-btn">
                    <LogIn className="w-4 h-4 mr-2" />
                    Connexion
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
