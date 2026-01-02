/**
 * Options Analytics Page - Pro Tier Feature
 * Real-time options data with Greeks calculations
 * MVP2 v3.4 - Complete Options Analytics Interface
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  Calculator,
  BarChart3,
  Activity,
  ChevronDown,
  RefreshCw,
  AlertCircle,
  Loader2
} from 'lucide-react';
import OptionChainTable from '../../components/options/OptionChainTable';
import GreeksChart from '../../components/options/GreeksChart';
import BlackScholesCalculator from '../../components/options/BlackScholesCalculator';
import './OptionsAnalytics.css';

const OptionsAnalytics = () => {
  const [activeTab, setActiveTab] = useState('chain'); // chain, greeks, calculator
  const [ticker, setTicker] = useState('AAPL');
  const [tickerInput, setTickerInput] = useState('AAPL');
  const [expirations, setExpirations] = useState([]);
  const [selectedExpiration, setSelectedExpiration] = useState('');
  const [chainData, setChainData] = useState(null);
  const [greeksData, setGreeksData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [spotPrice, setSpotPrice] = useState(0);

  // Fetch available expirations when ticker changes
  useEffect(() => {
    if (ticker) {
      fetchExpirations();
    }
  }, [ticker]);

  // Fetch chain data when expiration changes
  useEffect(() => {
    if (ticker && selectedExpiration && activeTab === 'chain') {
      fetchOptionChain();
    }
  }, [ticker, selectedExpiration, activeTab]);

  // Fetch Greeks data when expiration changes
  useEffect(() => {
    if (ticker && selectedExpiration && activeTab === 'greeks') {
      fetchGreeksData();
    }
  }, [ticker, selectedExpiration, activeTab]);

  const fetchExpirations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/stocks/options/${ticker}/expirations/`);

      if (response.data.success && response.data.expirations.length > 0) {
        setExpirations(response.data.expirations);
        setSelectedExpiration(response.data.expirations[0]); // Select first expiration
      } else {
        setError('No options data available for this ticker');
        setExpirations([]);
        setSelectedExpiration('');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch expiration dates');
      setExpirations([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchOptionChain = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/stocks/options/${ticker}/chain/`, {
        params: { expiration: selectedExpiration }
      });

      if (response.data.success) {
        setChainData(response.data.data);
        setSpotPrice(response.data.data.spot_price);
      } else {
        setError(response.data.error || 'Failed to fetch option chain');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch option chain');
    } finally {
      setLoading(false);
    }
  };

  const fetchGreeksData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/stocks/options/${ticker}/greeks/`, {
        params: { expiration: selectedExpiration }
      });

      if (response.data.success) {
        setGreeksData(response.data.data);
        setSpotPrice(response.data.data.spot_price);
      } else {
        setError(response.data.error || 'Failed to fetch Greeks data');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch Greeks data');
    } finally {
      setLoading(false);
    }
  };

  const handleTickerSubmit = (e) => {
    e.preventDefault();
    if (tickerInput.trim()) {
      setTicker(tickerInput.trim().toUpperCase());
    }
  };

  const handleRefresh = () => {
    if (activeTab === 'chain') {
      fetchOptionChain();
    } else if (activeTab === 'greeks') {
      fetchGreeksData();
    }
  };

  const tabs = [
    { id: 'chain', label: 'Option Chain', icon: BarChart3 },
    { id: 'greeks', label: 'Greeks Analysis', icon: Activity },
    { id: 'calculator', label: 'BS Calculator', icon: Calculator }
  ];

  return (
    <div className="options-analytics-container">
      {/* Header */}
      <div className="options-header">
        <div className="header-top">
          <div className="header-title">
            <TrendingUp size={32} />
            <div>
              <h1>Options Analytics</h1>
              <p className="header-subtitle">Real-time options data with Greeks calculations</p>
            </div>
          </div>

          <div className="pro-badge">
            <span className="badge-icon">✨</span>
            PRO
          </div>
        </div>

        {/* Ticker Input & Controls */}
        <div className="options-controls">
          <form onSubmit={handleTickerSubmit} className="ticker-form">
            <div className="input-group">
              <label>Ticker Symbol</label>
              <input
                type="text"
                value={tickerInput}
                onChange={(e) => setTickerInput(e.target.value.toUpperCase())}
                placeholder="Enter ticker..."
                className="ticker-input"
                maxLength={10}
              />
              <button type="submit" className="btn-search">
                Search
              </button>
            </div>
          </form>

          <div className="input-group">
            <label>Expiration Date</label>
            <div className="select-wrapper">
              <select
                value={selectedExpiration}
                onChange={(e) => setSelectedExpiration(e.target.value)}
                disabled={expirations.length === 0}
                className="expiration-select"
              >
                {expirations.length === 0 ? (
                  <option>No expirations available</option>
                ) : (
                  expirations.map((exp) => (
                    <option key={exp} value={exp}>
                      {new Date(exp).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                      {' '}({Math.ceil((new Date(exp) - new Date()) / (1000 * 60 * 60 * 24))} days)
                    </option>
                  ))
                )}
              </select>
              <ChevronDown size={18} className="select-icon" />
            </div>
          </div>

          {activeTab !== 'calculator' && (
            <button
              onClick={handleRefresh}
              className="btn-refresh"
              disabled={loading}
            >
              <RefreshCw size={18} className={loading ? 'spinning' : ''} />
              Refresh
            </button>
          )}
        </div>

        {/* Spot Price Display */}
        {spotPrice > 0 && (
          <div className="spot-price-display">
            <span className="spot-label">Current Price:</span>
            <span className="spot-value">${spotPrice.toFixed(2)}</span>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            >
              <Icon size={20} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="error-banner"
          >
            <AlertCircle size={20} />
            <span>{error}</span>
            <button onClick={() => setError(null)} className="error-close">×</button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tab Content */}
      <div className="tab-content">
        {loading && activeTab !== 'calculator' ? (
          <div className="loading-container">
            <Loader2 size={48} className="spinning" />
            <p>Loading {activeTab === 'chain' ? 'option chain' : 'Greeks data'}...</p>
            <p className="loading-subtitle">Fetching real-time data from market</p>
          </div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'chain' && (
                chainData ? (
                  <OptionChainTable
                    chainData={chainData}
                    selectedExpiration={selectedExpiration}
                    ticker={ticker}
                  />
                ) : (
                  <div className="empty-state">
                    <BarChart3 size={64} />
                    <p>Select a ticker and expiration to view option chain</p>
                  </div>
                )
              )}

              {activeTab === 'greeks' && (
                greeksData ? (
                  <GreeksChart
                    greeksData={greeksData}
                    ticker={ticker}
                    expiration={selectedExpiration}
                  />
                ) : (
                  <div className="empty-state">
                    <Activity size={64} />
                    <p>Select a ticker and expiration to view Greeks analysis</p>
                  </div>
                )
              )}

              {activeTab === 'calculator' && (
                <BlackScholesCalculator defaultTicker={ticker} />
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>

      {/* Info Footer */}
      <div className="options-footer">
        <div className="footer-info">
          <AlertCircle size={16} />
          <span>
            Real-time options data powered by yfinance. Greeks calculated using Black-Scholes model.
            Data may be delayed. Not financial advice.
          </span>
        </div>
      </div>
    </div>
  );
};

export default OptionsAnalytics;
