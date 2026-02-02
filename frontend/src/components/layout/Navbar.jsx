import { Link, useLocation } from "react-router-dom";
import { BookOpen, Plus, LayoutDashboard, Library as LibraryIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Navbar = () => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group" data-testid="navbar-logo">
            <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center group-hover:-translate-y-0.5 transition-transform">
              <BookOpen className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-serif text-xl font-semibold tracking-tight">GlasEditionsLab</span>
          </Link>
          
          {/* Navigation Links */}
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
          </div>
          
          {/* CTA Button */}
          <Link to="/create" data-testid="nav-create-book">
            <Button className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-6 rounded-sm font-serif tracking-wide">
              <Plus className="w-4 h-4 mr-2" />
              Nouveau livre
            </Button>
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
