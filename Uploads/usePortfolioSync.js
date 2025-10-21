/**
 * usePortfolioSync() React Hook
 * =============================
 * Auto-polls portfolio data and provides clean state management with venue-specific error handling
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchCompletePortfolio, summarizePortfolio, convertToNexusFormat } from '../services/portfolioSync';

export function usePortfolioSync({ 
  pollInterval = 30000, // 30 seconds default
  includeCoinbase = false,
  autoStart = true 
} = {}) {
  const [items, setItems] = useState([]);
  const [totalValue, setTotalValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [venueErrors, setVenueErrors] = useState({});
  const [lastUpdate, setLastUpdate] = useState(null);

  const reload = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 usePortfolioSync: Reloading portfolio data...');
      
      // Fetch raw portfolio data from all venues
      const { assets, errors } = await fetchCompletePortfolio({ includeCoinbase });
      
      // Track venue-specific errors
      const venueErrorMap = {};
      if (errors.length > 0) {
        errors.forEach((err, idx) => {
          const venues = ['binance', 'okx', 'coinbase'];
          if (venues[idx]) {
            venueErrorMap[venues[idx]] = err.error;
          }
        });
        setVenueErrors(venueErrorMap);
        console.warn('⚠️ Portfolio sync venue errors:', venueErrorMap);
      } else {
        setVenueErrors({});
      }
      
      // Summarize and calculate total value
      const { items: mergedItems, totalValue: calculatedTotal } = summarizePortfolio(assets);
      
      // Convert to NEXUS format for display
      const nexusAssets = convertToNexusFormat(mergedItems);
      
      setItems(nexusAssets);
      setTotalValue(calculatedTotal);
      setLastUpdate(new Date());
      
      // Set general error only if ALL venues failed
      const allVenuesFailed = Object.keys(venueErrorMap).length === 3;
      if (allVenuesFailed) {
        setError(new Error('All portfolio sources failed'));
      }
      
      console.log(`✅ usePortfolioSync: Loaded ${nexusAssets.length} assets, $${calculatedTotal.toFixed(2)} total`);
      
    } catch (err) {
      console.error('❌ usePortfolioSync: Portfolio reload failed:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [includeCoinbase]);

  // Auto-polling effect
  useEffect(() => {
    if (!autoStart) return;
    
    // Initial load
    reload();
    
    // Set up polling interval
    const interval = setInterval(reload, pollInterval);
    
    // Cleanup
    return () => clearInterval(interval);
  }, [reload, pollInterval, autoStart]);

  return {
    items,
    totalValue,
    loading,
    error,
    venueErrors, // New: venue-specific errors
    reload,
    lastUpdate,
    // Utility getters
    get isEmpty() { return items.length === 0; },
    get hasError() { return !!error; },
    get hasVenueErrors() { return Object.keys(venueErrors).length > 0; },
    get isStale() { 
      return lastUpdate && (Date.now() - lastUpdate.getTime()) > pollInterval * 2; 
    }
  };
}

