
import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { Analyzer } from './components/Analyzer';
import { StrategyDetails } from './components/StrategyDetails';
import { LocalAgent } from './components/LocalAgent';
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
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </Router>
    </StrategyProvider>
  );
};

export default App;
