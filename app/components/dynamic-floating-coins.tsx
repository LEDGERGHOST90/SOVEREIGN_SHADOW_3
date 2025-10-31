
'use client';

import React from 'react';
import { motion } from 'framer-motion';

const coins = [
  { name: 'BTC', symbol: '₿', color: '#F7931A' },
  { name: 'ETH', symbol: 'Ξ', color: '#627EEA' },
  { name: 'SOL', symbol: '◎', color: '#9945FF' },
  { name: 'XRP', symbol: '✦', color: '#23292F' },
  { name: 'USDT', symbol: '$', color: '#26A17B' },
];

const FloatingCoin = ({ coin, index }: { coin: any; index: number }) => {
  const getRandomPosition = () => {
    if (typeof window === 'undefined') return { x: 100, y: 100 };
    return {
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
    };
  };

  const initialPos = getRandomPosition();
  const targetPos = getRandomPosition();

  return (
    <motion.div
      key={coin.name}
      className="absolute text-4xl font-bold opacity-20"
      style={{ color: coin.color }}
      initial={initialPos}
      animate={{
        x: targetPos.x,
        y: targetPos.y,
        rotate: 360,
      }}
      transition={{
        duration: 20 + Math.random() * 10,
        repeat: Infinity,
        repeatType: "reverse",
        delay: index * 2,
      }}
    >
      {coin.symbol}
    </motion.div>
  );
};

export default function DynamicFloatingCoins() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {coins.map((coin, index) => (
        <FloatingCoin key={coin.name} coin={coin} index={index} />
      ))}
    </div>
  );
}
