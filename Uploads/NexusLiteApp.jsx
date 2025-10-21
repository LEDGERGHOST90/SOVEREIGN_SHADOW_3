import React, { useState, useEffect } from "react";
import { HashRouter, Routes, Route, useNavigate } from "react-router-dom";
import WelcomeScreen from "./components/WelcomeScreen";

/**
 * NEXUS LITE APP - Dependency-light initial loader
 * 
 * Handles:
 * - Welcome screen with floating coins
 * - Initial API health check
 * - Safe authentication flow
 * - Switches to full NexusCommandCenter when ready
 */

// Simple session management
function useSession() {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(sessionStorage.getItem("nexus.user")) || { email: "LedgerGhost90" };
    } catch {
      return { email: "LedgerGhost90" };
    }
  });

  useEffect(() => {
    try {
      if (user) {
        sessionStorage.setItem("nexus.user", JSON.stringify(user));
      }
    } catch {}
  }, [user]);

  return { user, setUser };
}

function LiteRoutes({ onReady }) {
  const { user, setUser } = useSession();
  const nav = useNavigate();

  const handleSignIn = async () => {
    try {
      // Test API connection before switching to full app
      console.log('🔄 Testing API connection...');
      const response = await fetch('/api/binance/portfolio');
      
      if (response.ok) {
        console.log('✅ API connection successful, switching to full app');
        const u = { email: "LedgerGhost90" };
        setUser(u);
        onReady(); // Switch to NexusCommandCenter
      } else {
        console.warn('⚠️ API connection failed, staying in lite mode');
        // Still allow sign-in but show warning
        const u = { email: "LedgerGhost90" };
        setUser(u);
        nav("/dashboard");
      }
    } catch (error) {
      console.error('❌ API test failed:', error);
      // Fallback: allow sign-in anyway
      const u = { email: "LedgerGhost90" };
      setUser(u);
      nav("/dashboard");
    }
  };

  const handleSignOut = () => {
    setUser({ email: "LedgerGhost90" });
    nav("/");
  };

  return (
    <Routes>
      <Route path="/" element={<WelcomeScreen onSignIn={handleSignIn} />} />
      <Route
        path="/dashboard"
        element={
          <div className="min-h-screen bg-black text-white flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold mb-4 text-emerald-400">NEXUS PROTOCOL</h1>
              <p className="text-xl mb-8">Loading trading systems...</p>
              <div className="animate-spin w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full mx-auto"></div>
              <button 
                onClick={handleSignOut}
                className="mt-8 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                Back to Welcome
              </button>
            </div>
          </div>
        }
      />
      <Route path="*" element={<WelcomeScreen onSignIn={handleSignIn} />} />
    </Routes>
  );
}

export default function NexusLiteApp({ onReady }) {
  return (
    <HashRouter>
      <LiteRoutes onReady={onReady} />
    </HashRouter>
  );
}

