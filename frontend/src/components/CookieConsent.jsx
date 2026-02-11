import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Cookie, X } from "lucide-react";
import { Link } from "react-router-dom";

export default function CookieConsent() {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Check if user has already consented
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) {
      // Small delay to avoid flash on page load
      const timer = setTimeout(() => setShowBanner(true), 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const acceptCookies = () => {
    localStorage.setItem('cookie_consent', JSON.stringify({
      essential: true,
      analytics: true,
      timestamp: new Date().toISOString()
    }));
    setShowBanner(false);
  };

  const acceptEssentialOnly = () => {
    localStorage.setItem('cookie_consent', JSON.stringify({
      essential: true,
      analytics: false,
      timestamp: new Date().toISOString()
    }));
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div 
      className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-background border-t border-border shadow-lg animate-in slide-in-from-bottom duration-300"
      role="dialog"
      aria-label="Consentement aux cookies"
      data-testid="cookie-consent-banner"
    >
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
          {/* Icon and Text */}
          <div className="flex items-start gap-3 flex-1">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <Cookie className="w-5 h-5 text-primary" />
            </div>
            <div className="space-y-1">
              <h3 className="font-semibold text-foreground">
                Nous utilisons des cookies
              </h3>
              <p className="text-sm text-muted-foreground">
                GlasEditionsLab utilise des cookies essentiels pour assurer le bon fonctionnement du site 
                (authentification, session). Nous n'utilisons pas de cookies publicitaires.{" "}
                <Link 
                  to="/privacy" 
                  className="text-primary hover:underline"
                  data-testid="cookie-privacy-link"
                >
                  En savoir plus
                </Link>
              </p>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex items-center gap-3 w-full md:w-auto">
            <Button
              variant="outline"
              onClick={acceptEssentialOnly}
              className="flex-1 md:flex-none rounded-sm"
              data-testid="cookie-reject-btn"
            >
              Essentiels uniquement
            </Button>
            <Button
              onClick={acceptCookies}
              className="flex-1 md:flex-none rounded-sm bg-primary text-primary-foreground hover:bg-primary/90"
              data-testid="cookie-accept-btn"
            >
              Accepter tout
            </Button>
          </div>

          {/* Close button (mobile) */}
          <button
            onClick={acceptEssentialOnly}
            className="absolute top-2 right-2 md:hidden p-2 text-muted-foreground hover:text-foreground"
            aria-label="Fermer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
