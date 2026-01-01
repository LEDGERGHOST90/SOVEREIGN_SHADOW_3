
import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { Analyzer } from './components/Analyzer';
import { StrategyDetails } from './components/StrategyDetails';
import { LocalAgent } from './components/LocalAgent';
import { DailyRecorder } from './components/DailyRecorder';
import { KnowledgeGraph } from './components/KnowledgeGraph';
import { SovereignProtocols } from './components/SovereignProtocols';
import { DataScienceLab } from './components/DataScienceLab';
import { CollaborationFramework } from './components/CollaborationFramework';
import { AlphaDigest } from './components/AlphaDigest';
import { StrategyProvider } from './context/StrategyContext';

const App: React.FC = () => {
  return (
    <StrategyProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyzer />} />
            <Route path="/strategy/:id" element={<StrategyDetails />} />
            <Route path="/agent" element={<LocalAgent />} />
            <Route path="/lab" element={<DataScienceLab />} />
            <Route path="/daily-recorder" element={<DailyRecorder />} />
            <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
            <Route path="/protocols" element={<SovereignProtocols />} />
            <Route path="/collaboration" element={<CollaborationFramework />} />
            <Route path="/alpha-hub" element={<AlphaDigest />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </Router>
    </StrategyProvider>
  );
};

export default App;
