'use client';

import React, { useState } from 'react';
import { useStrategyStore } from '@/lib/stores/strategy-store';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StrategyDashboard } from './strategy-dashboard';
import { StrategyAnalyzer } from './strategy-analyzer';
import { LocalAgent } from './local-agent';

export default function StrategyScoutClient() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex-1 p-8 overflow-auto bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              Strategy Scout
            </h1>
            <p className="text-slate-400 mt-2">
              AI-powered trading strategy analyzer • Powered by Gemini & Shadow.AI
            </p>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-white/5 border border-white/10">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="analyze">Analyze Strategy</TabsTrigger>
            <TabsTrigger value="agent">Local Agent</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="mt-6">
            <StrategyDashboard />
          </TabsContent>

          <TabsContent value="analyze" className="mt-6">
            <StrategyAnalyzer />
          </TabsContent>

          <TabsContent value="agent" className="mt-6">
            <LocalAgent />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
