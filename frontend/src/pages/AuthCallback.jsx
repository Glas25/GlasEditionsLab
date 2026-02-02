import { useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/App";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double processing in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processCallback = async () => {
      try {
        // Extract session_id from URL fragment
        const hash = location.hash;
        const params = new URLSearchParams(hash.replace('#', ''));
        const sessionId = params.get('session_id');

        if (!sessionId) {
          throw new Error('Session ID non trouvé');
        }

        // Exchange session_id for user data
        const response = await fetch(`${API}/auth/session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ session_id: sessionId })
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Erreur de connexion');
        }

        const userData = await response.json();
        login(userData, null); // Cookie is set by backend
        
        toast.success(`Bienvenue, ${userData.name} !`);
        
        // Navigate to dashboard with user data
        navigate('/dashboard', { state: { user: userData }, replace: true });
        
      } catch (error) {
        console.error('Auth callback error:', error);
        toast.error(error.message);
        navigate('/login', { replace: true });
      }
    };

    processCallback();
  }, [location, login, navigate]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <div className="book-loader mx-auto mb-4">
          <span></span><span></span><span></span><span></span><span></span>
        </div>
        <p className="text-muted-foreground">Connexion en cours...</p>
      </div>
    </div>
  );
}
