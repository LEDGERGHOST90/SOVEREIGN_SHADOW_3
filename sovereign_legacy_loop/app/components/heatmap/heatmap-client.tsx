
'use client';

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Map, TrendingUp, TrendingDown } from "lucide-react";
import { motion } from "framer-motion";

export default function HeatmapClient() {
  const [portfolioData] = useState([
    { asset: 'BTC', allocation: 45, value: 67500, change: 2.3, color: '#f7931a' },
    { asset: 'ETH', allocation: 30, value: 45000, change: 1.8, color: '#627eea' },
    { asset: 'BNB', allocation: 15, value: 22500, change: -0.5, color: '#f0b90b' },
    { asset: 'ADA', allocation: 5, value: 7500, change: 3.2, color: '#3cc8c8' },
    { asset: 'SOL', allocation: 3, value: 4500, change: 4.1, color: '#9945ff' },
    { asset: 'Others', allocation: 2, value: 3000, change: 0.8, color: '#8b5cf6' }
  ]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            Portfolio Heatmap
          </h1>
          <p className="text-muted-foreground">
            Visual allocation analysis with real-time performance indicators
          </p>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="grid gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Map className="h-5 w-5" />
              Asset Allocation Heatmap
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              {portfolioData.map((asset, index) => (
                <motion.div
                  key={asset.asset}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative"
                >
                  <div 
                    className="p-4 rounded-lg flex items-center justify-between"
                    style={{ 
                      backgroundColor: `${asset.color}20`,
                      borderLeft: `4px solid ${asset.color}`,
                      height: `${Math.max(60, asset.allocation * 2)}px`
                    }}
                  >
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: asset.color }}
                      />
                      <div>
                        <h3 className="font-semibold">{asset.asset}</h3>
                        <p className="text-sm text-muted-foreground">
                          {asset.allocation}% allocation
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-lg font-bold">
                        ${asset.value.toLocaleString()}
                      </div>
                      <div className="flex items-center gap-1">
                        {asset.change >= 0 ? (
                          <TrendingUp className="h-3 w-3 text-green-400" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-400" />
                        )}
                        <Badge variant={asset.change >= 0 ? "default" : "destructive"} className="text-xs">
                          {asset.change >= 0 ? '+' : ''}{asset.change}%
                        </Badge>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
