import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import LandingPage from "@/pages/LandingPage";
import CreateBook from "@/pages/CreateBook";
import Dashboard from "@/pages/Dashboard";
import BookView from "@/pages/BookView";
import Library from "@/pages/Library";

function App() {
  return (
    <div className="min-h-screen bg-background">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/create" element={<CreateBook />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/book/:id" element={<BookView />} />
          <Route path="/library" element={<Library />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="bottom-right" richColors />
    </div>
  );
}

export default App;
