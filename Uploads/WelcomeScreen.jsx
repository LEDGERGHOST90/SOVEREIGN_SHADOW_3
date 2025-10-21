import React, { useState } from "react";
import { motion } from "framer-motion";
import { LogIn, AlertCircle } from "lucide-react";
import DynamicFloatingCoins from "./DynamicFloatingCoins";
import { isEmail, isStrongEnough } from "../utils/validation";

/**
 * NEXUS PROTOCOL – Premium Welcome + Sign In Experience
 * 
 * Adds a cinematic, attention-snatching entry screen before the Command Center.
 * Includes floating 3D coins, glowing nebula background, and glassmorphism sign-in panel.
 */

const WelcomeScreen = ({ onSignIn }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    const next = {};
    if (!isEmail(email)) next.email = "Enter a valid email";
    if (!isStrongEnough(password)) next.password = "Use at least 8 characters";
    setErrors(next);
    
    if (Object.keys(next).length === 0) {
      setIsLoading(true);
      try {
        // Simulate authentication
        await new Promise(resolve => setTimeout(resolve, 1500));
        // Pass the actual email to show in the signed-in chip
        onSignIn(email === "trader@nexus.com" ? "LedgerGhost90" : email);
      } catch (error) {
        setErrors({ general: "Authentication failed. Please try again." });
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-black text-white">
      {/* Custom Nebula Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,#1a1a1a,#000)]" />
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            radial-gradient(circle at 50% 20%, rgba(255,140,66,0.25), transparent 55%),
            radial-gradient(circle at 20% 80%, rgba(76,145,255,0.18), transparent 55%),
            url("/assets/nebula-01.png")
          `,
          backgroundSize: "cover, cover, cover",
          backgroundPosition: "center, center, center",
          opacity: 0.9,
        }}
      />
      
      {/* Silhouetted Figure Overlay */}
      <div
        className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-64 h-64 opacity-30"
        style={{
          backgroundImage: "url('/assets/silhouette-figure.png')",
          backgroundSize: "contain",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "bottom center",
        }}
      />

      {/* Dynamic Floating Coins System */}
      <DynamicFloatingCoins />

      {/* Glassmorphic Sign-in Panel */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1 }}
        className="relative z-10 w-full max-w-sm rounded-2xl border border-white/20 bg-white/10 p-8 text-center backdrop-blur-xl shadow-2xl"
      >
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="mb-6 text-3xl font-extrabold tracking-tight text-white drop-shadow-lg"
        >
          Welcome to NEXUS
        </motion.h1>

        {errors.general && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 flex items-center gap-2 rounded-xl bg-red-500/10 border border-red-500/20 p-3 text-red-300"
          >
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{errors.general}</span>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) setErrors(prev => ({ ...prev, email: null }));
              }}
              aria-invalid={!!errors.email}
              aria-describedby="email-err"
              className={`w-full rounded-xl border px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 transition-all duration-300 ${
                errors.email 
                  ? 'border-red-500/50 bg-red-500/10 focus:ring-red-400' 
                  : 'border-white/20 bg-white/10 focus:ring-indigo-400'
              }`}
            />
            {errors.email && (
              <motion.p
                id="email-err"
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-xs text-rose-300"
              >
                {errors.email}
              </motion.p>
            )}
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, duration: 0.6 }}
          >
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) setErrors(prev => ({ ...prev, password: null }));
              }}
              aria-invalid={!!errors.password}
              aria-describedby="pw-err"
              className={`w-full rounded-xl border px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 transition-all duration-300 ${
                errors.password 
                  ? 'border-red-500/50 bg-red-500/10 focus:ring-red-400' 
                  : 'border-white/20 bg-white/10 focus:ring-indigo-400'
              }`}
            />
            {errors.password && (
              <motion.p
                id="pw-err"
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-xs text-rose-300"
              >
                {errors.password}
              </motion.p>
            )}
          </motion.div>

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1, duration: 0.6 }}
            type="submit"
            disabled={isLoading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white shadow-lg transition-all duration-300 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="h-5 w-5 border-2 border-white border-t-transparent rounded-full"
              />
            ) : (
              <LogIn className="h-5 w-5" />
            )}
            {isLoading ? "Authenticating..." : "Sign In"}
          </motion.button>
        </form>

        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.3, duration: 0.6 }}
          className="mt-4 text-sm text-white/60"
        >
          Don't have an account? <span className="text-indigo-300 hover:text-indigo-400 cursor-pointer transition-colors">Sign up</span>
        </motion.p>
      </motion.div>
    </div>
  );
};

export default WelcomeScreen;

