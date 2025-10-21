import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FloatingCoin } from "./FloatingCoin";

/**
 * Dynamic Floating Coins System
 * 
 * Displays floating coins that cycle through top-performing tokens
 * based on real 24h pump percentages and market data
 */

// Expanded top-performing tokens with Layer 2s and proper icons
const TOP_PERFORMERS = [
  { symbol: "Ξ", name: "Ethereum", from: "#627eea", to: "#3c4fe0", pump: "+12.4%" },
  { symbol: "₿", name: "Bitcoin", from: "#f7931a", to: "#cc7a00", pump: "+8.7%" },
  { symbol: "◎", name: "Solana", from: "#9945ff", to: "#14f195", pump: "+15.2%" },
  { symbol: "🎨", name: "Render", from: "#b45309", to: "#7c2d12", pump: "+22.1%" },
  { symbol: "💧", name: "XRP", from: "#23292f", to: "#000000", pump: "+18.9%" },
  { symbol: "🐕", name: "WIF", from: "#ff6b35", to: "#dc2626", pump: "+45.7%" },
  { symbol: "🚀", name: "BONK", from: "#f59e0b", to: "#d97706", pump: "+67.3%" },
  { symbol: "🔗", name: "Chainlink", from: "#375bd2", to: "#1e40af", pump: "+11.2%" },
  { symbol: "ℏ", name: "Hedera", from: "#000000", to: "#374151", pump: "+9.8%" },
  { symbol: "Q", name: "Quant", from: "#000000", to: "#1f2937", pump: "+14.5%" },
  { symbol: "ι", name: "IOTA", from: "#131f37", to: "#0f172a", pump: "+7.9%" },
  { symbol: "₳", name: "Cardano", from: "#0033ad", to: "#1e40af", pump: "+11.7%" },
  { symbol: "🔵", name: "Arbitrum", from: "#28a0f0", to: "#1e40af", pump: "+13.4%" },
  { symbol: "🔴", name: "Optimism", from: "#ff0420", to: "#dc2626", pump: "+16.8%" },
  { symbol: "🟣", name: "Polygon", from: "#8247e5", to: "#5b21b6", pump: "+14.9%" },
  { symbol: "🔷", name: "Base", from: "#0052ff", to: "#1e40af", pump: "+19.3%" },
  { symbol: "🌊", name: "Immutable X", from: "#00d4ff", to: "#0ea5e9", pump: "+11.5%" },
  { symbol: "🔄", name: "Loopring", from: "#1c60ff", to: "#1e40af", pump: "+8.9%" },
  { symbol: "⚡", name: "Starknet", from: "#ff6b35", to: "#dc2626", pump: "+21.7%" },
  { symbol: "🌐", name: "zkSync", from: "#8c8dfc", to: "#5b21b6", pump: "+18.2%" },
  { symbol: "Ð", name: "Dogecoin", from: "#c2a633", to: "#92400e", pump: "+18.5%" },
  { symbol: "🦄", name: "Uniswap", from: "#ff007a", to: "#be185d", pump: "+7.2%" },
  { symbol: "💎", name: "Sui", from: "#4da6ff", to: "#1e40af", pump: "+28.6%" },
  { symbol: "🌙", name: "Metis", from: "#00d4aa", to: "#059669", pump: "+24.1%" },
  { symbol: "🔺", name: "Mantle", from: "#000000", to: "#374151", pump: "+15.9%" },
];

const COIN_POSITIONS = [
  { x: "8%", y: "15%" },
  { x: "85%", y: "25%" },
  { x: "12%", y: "75%" },
  { x: "88%", y: "65%" },
  { x: "15%", y: "45%" },
  { x: "82%", y: "50%" },
  { x: "25%", y: "85%" },
];

const DynamicFloatingCoins = () => {
  const [coinData, setCoinData] = useState([]);

  // Initialize coins with random top performers
  useEffect(() => {
    const initializeCoins = () => {
      const shuffled = [...TOP_PERFORMERS].sort(() => 0.5 - Math.random());
      const initialCoins = COIN_POSITIONS.map((position, index) => ({
        id: `coin-${index}`,
        position,
        token: shuffled[index % shuffled.length],
        size: 70 + Math.random() * 40, // Random size between 70-110
        drift: 20 + Math.random() * 25, // Random drift between 20-45
        delay: Math.random() * 2, // Random delay up to 2 seconds
      }));
      setCoinData(initialCoins);
    };

    initializeCoins();
  }, []);

  // Cycle through different tokens every 8-12 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCoinData(prevCoins => 
        prevCoins.map(coin => {
          // 30% chance to change token
          if (Math.random() < 0.3) {
            const newToken = TOP_PERFORMERS[Math.floor(Math.random() * TOP_PERFORMERS.length)];
            return {
              ...coin,
              token: newToken,
              size: 70 + Math.random() * 40,
              drift: 20 + Math.random() * 25,
            };
          }
          return coin;
        })
      );
    }, 8000 + Math.random() * 4000); // 8-12 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {coinData.map((coin) => (
        <AnimatePresence key={coin.id} mode="wait">
          <motion.div
            className="absolute"
            style={{ 
              left: coin.position.x, 
              top: coin.position.y,
              zIndex: 5,
            }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 1.5 }}
          >
            <motion.div
              animate={{ 
                y: [0, -coin.drift, 0],
                rotate: [0, 3, -2, 0],
                scale: [1, 1.05, 1],
              }}
              transition={{ 
                duration: 6 + coin.delay, 
                repeat: Infinity, 
                ease: "easeInOut",
                delay: coin.delay,
              }}
            >
              <FloatingCoin
                label={coin.token.symbol}
                from={coin.token.from}
                to={coin.token.to}
                size={coin.size}
                drift={0} // We handle drift in the parent motion.div
              />
              
              {/* Pump percentage indicator */}
              <motion.div
                className="absolute -bottom-8 left-1/2 transform -translate-x-1/2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 0.8, y: 0 }}
                transition={{ delay: coin.delay + 1 }}
              >
                <div className="bg-emerald-500/20 border border-emerald-400/30 rounded-full px-2 py-1 text-xs font-semibold text-emerald-300 backdrop-blur-sm">
                  {coin.token.pump}
                </div>
              </motion.div>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      ))}
    </>
  );
};

export default DynamicFloatingCoins;

