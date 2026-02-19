import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { useState, useEffect, createContext, useContext } from "react";
import LandingPage from "@/pages/LandingPage";
import CreateBook from "@/pages/CreateBook";
import Dashboard from "@/pages/Dashboard";
import BookView from "@/pages/BookView";
import Library from "@/pages/Library";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import AuthCallback from "@/pages/AuthCallback";
import PricingPage from "@/pages/PricingPage";
import PaymentSuccessPage from "@/pages/PaymentSuccessPage";
import CGVPage from "@/pages/CGVPage";
import CGUPage from "@/pages/CGUPage";
import PrivacyPage from "@/pages/PrivacyPage";
import MentionsLegalesPage from "@/pages/MentionsLegalesPage";
import AccountPage from "@/pages/AccountPage";
import AdminDashboard from "@/pages/AdminDashboard";
import CookieConsent from "@/components/CookieConsent";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(`${API}/auth/me`, {
        credentials: 'include',
        headers
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
        localStorage.removeItem('auth_token');
        setToken(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = (userData, authToken) => {
    setUser(userData);
    if (authToken) {
      localStorage.setItem('auth_token', authToken);
      setToken(authToken);
    }
  };

  const logout = async () => {
    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      await fetch(`${API}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    setUser(null);
    localStorage.removeItem('auth_token');
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, checkAuth, token }}>
      {children}
    </AuthContext.Provider>
  );
};

function AppRouter() {
  const location = useLocation();
  
  // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
  // Check URL fragment for session_id (Google OAuth callback)
  if (location.hash && location.hash.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/payment/success" element={<PaymentSuccessPage />} />
      <Route path="/create" element={<CreateBook />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/book/:id" element={<BookView />} />
      <Route path="/library" element={<Library />} />
      <Route path="/account" element={<AccountPage />} />
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/cgv" element={<CGVPage />} />
      <Route path="/cgu" element={<CGUPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/mentions-legales" element={<MentionsLegalesPage />} />
    </Routes>
  );
}

function App() {
  return (
    <div className="min-h-screen bg-background">
      <BrowserRouter>
        <AuthProvider>
          <AppRouter />
          <CookieConsent />
        </AuthProvider>
      </BrowserRouter>
      <Toaster position="bottom-right" richColors />
    </div>
  );
}

export default App;
