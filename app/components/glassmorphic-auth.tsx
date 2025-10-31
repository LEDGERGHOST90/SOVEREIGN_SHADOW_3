
'use client';

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { LogIn, AlertCircle, Shield, TrendingUp, Vault } from "lucide-react";
import { toast } from "sonner";
import DynamicFloatingCoins from "./dynamic-floating-coins";

export default function GlassmorphicAuth() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateUsername = (username: string) => {
    return username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const nextErrors: { [key: string]: string } = {};
    if (!validateUsername(username)) nextErrors.username = "Enter a valid username (3+ characters, alphanumeric only)";
    if (password.length < 6) nextErrors.password = "Use at least 6 characters";
    setErrors(nextErrors);
    
    if (Object.keys(nextErrors).length === 0) {
      setIsLoading(true);
      try {
        const result = await signIn("credentials", {
          username,
          password,
          redirect: false,
        });

        if (result?.error) {
          setErrors({ general: "Authentication failed. Please try again." });
        } else {
          toast.success("Welcome to Sovereign Legacy Loop");
          router.replace("/dashboard");
        }
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
            radial-gradient(circle at 80% 20%, rgba(139,69,199,0.15), transparent 55%)
          `,
          backgroundSize: "cover, cover, cover",
          backgroundPosition: "center, center, center",
          opacity: 0.9,
        }}
      />
      
      {/* Dynamic Floating Coins System */}
      <DynamicFloatingCoins />

      {/* Main Content */}
      <div className="relative z-10 flex min-h-screen w-full">
        {/* Left side - Hero */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden items-center justify-center p-12">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1.2 }}
            className="space-y-8 text-center"
          >
            <motion.h1 
              initial={{ opacity: 0, y: -30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 1 }}
              className="text-6xl font-extrabold tracking-tight text-white drop-shadow-2xl"
            >
              Sovereign
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-blue-500 to-purple-600">
                Legacy Loop
              </span>
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="text-xl text-white/80 max-w-md"
            >
              Professional crypto wealth management with dual-tier security architecture
            </motion.p>
            
            <motion.div 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9, duration: 0.8 }}
              className="space-y-4"
            >
              <div className="flex items-center space-x-4 text-white/70">
                <Shield className="h-6 w-6 text-blue-400" />
                <span>Shadow.AI Intelligence & Dark Pool Scanner</span>
              </div>
              <div className="flex items-center space-x-4 text-white/70">
                <TrendingUp className="h-6 w-6 text-green-400" />
                <span>LEDGERGHOSTER90 Stealth Execution</span>
              </div>
              <div className="flex items-center space-x-4 text-white/70">
                <Vault className="h-6 w-6 text-purple-400" />
                <span>Automated Profit Siphoning & Vault Graduation</span>
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Right side - Glassmorphic Sign-in Panel */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="relative z-10 w-full max-w-md rounded-3xl border border-white/20 bg-white/10 p-8 text-center backdrop-blur-xl shadow-2xl"
          >
            <motion.h2 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.8 }}
              className="mb-6 text-3xl font-extrabold tracking-tight text-white drop-shadow-lg"
            >
              Access Your Empire
            </motion.h2>

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

            <form onSubmit={handleSubmit} className="space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7, duration: 0.6 }}
              >
                <input
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => {
                    setUsername(e.target.value);
                    if (errors.username) setErrors(prev => ({ ...prev, username: "" }));
                  }}
                  className={`w-full rounded-xl border px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 transition-all duration-300 ${
                    errors.username 
                      ? 'border-red-500/50 bg-red-500/10 focus:ring-red-400' 
                      : 'border-white/20 bg-white/10 focus:ring-blue-400'
                  }`}
                />
                {errors.username && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-1 text-xs text-rose-300 text-left"
                  >
                    {errors.username}
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
                    if (errors.password) setErrors(prev => ({ ...prev, password: "" }));
                  }}
                  className={`w-full rounded-xl border px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 transition-all duration-300 ${
                    errors.password 
                      ? 'border-red-500/50 bg-red-500/10 focus:ring-red-400' 
                      : 'border-white/20 bg-white/10 focus:ring-blue-400'
                  }`}
                />
                {errors.password && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-1 text-xs text-rose-300 text-left"
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
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-3 font-semibold text-white shadow-lg transition-all duration-300 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
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
                {isLoading ? "Accessing..." : "Enter The Loop"}
              </motion.button>
            </form>

            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.3, duration: 0.6 }}
              className="mt-6 text-sm text-white/60"
            >
              Powered by Shadow.AI Intelligence
            </motion.p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
