/**
 * Black-Scholes Calculator Component
 * Interactive calculator for option pricing and Greeks
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calculator, TrendingUp, TrendingDown, Info, Loader2 } from 'lucide-react';

const BlackScholesCalculator = ({ defaultTicker = 'AAPL' }) => {
  const [formData, setFormData] = useState({
    ticker: defaultTicker,
    strike: '',
    expiration: '',
    volatility: '0.30', // 30% default IV
    optionType: 'call'
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Update ticker if defaultTicker changes
  useEffect(() => {
    setFormData((prev) => ({ ...prev, ticker: defaultTicker }));
  }, [defaultTicker]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleCalculate = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.ticker || !formData.strike || !formData.expiration || !formData.volatility) {
      setError('Please fill in all fields');
      return;
    }

    const strike = parseFloat(formData.strike);
    const volatility = parseFloat(formData.volatility);

    if (isNaN(strike) || strike <= 0) {
      setError('Strike price must be a positive number');
      return;
    }

    if (isNaN(volatility) || volatility <= 0 || volatility > 5) {
      setError('Volatility must be between 0 and 5 (0% - 500%)');
      return;
    }

    // Check expiration is in the future
    const expirationDate = new Date(formData.expiration);
    const today = new Date();
    if (expirationDate <= today) {
      setError('Expiration date must be in the future');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await axios.post('/api/stocks/options/calculator/', {
        ticker: formData.ticker.toUpperCase(),
        strike: strike,
        expiration: formData.expiration,
        volatility: volatility,
        option_type: formData.optionType
      });

      if (response.data.success) {
        setResult(response.data.data);
      } else {
        setError(response.data.error || 'Calculation failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to calculate option price');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      ticker: defaultTicker,
      strike: '',
      expiration: '',
      volatility: '0.30',
      optionType: 'call'
    });
    setResult(null);
    setError(null);
  };

  // Format date for input min attribute (today)
  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <div className="bs-calculator-wrapper">
      <div className="calculator-header">
        <Calculator size={32} />
        <div>
          <h2>Black-Scholes Option Pricing Calculator</h2>
          <p className="calculator-subtitle">
            Calculate theoretical option price and Greeks using the Black-Scholes-Merton model
          </p>
        </div>
      </div>

      <div className="calculator-content">
        {/* Input Form */}
        <div className="calculator-form-section">
          <h3>Input Parameters</h3>
          <form onSubmit={handleCalculate} className="calculator-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="ticker">Stock Ticker</label>
                <input
                  type="text"
                  id="ticker"
                  name="ticker"
                  value={formData.ticker}
                  onChange={handleInputChange}
                  placeholder="e.g., AAPL"
                  maxLength={10}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="optionType">Option Type</label>
                <div className="option-type-toggle">
                  <button
                    type="button"
                    className={`toggle-btn call ${formData.optionType === 'call' ? 'active' : ''}`}
                    onClick={() => setFormData((prev) => ({ ...prev, optionType: 'call' }))}
                  >
                    <TrendingUp size={18} />
                    Call
                  </button>
                  <button
                    type="button"
                    className={`toggle-btn put ${formData.optionType === 'put' ? 'active' : ''}`}
                    onClick={() => setFormData((prev) => ({ ...prev, optionType: 'put' }))}
                  >
                    <TrendingDown size={18} />
                    Put
                  </button>
                </div>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="strike">
                  Strike Price ($)
                  <span className="field-info">
                    <Info size={14} />
                    <span className="info-tooltip">The price at which the option can be exercised</span>
                  </span>
                </label>
                <input
                  type="number"
                  id="strike"
                  name="strike"
                  value={formData.strike}
                  onChange={handleInputChange}
                  placeholder="e.g., 150.00"
                  step="0.01"
                  min="0.01"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="expiration">
                  Expiration Date
                  <span className="field-info">
                    <Info size={14} />
                    <span className="info-tooltip">The date when the option expires</span>
                  </span>
                </label>
                <input
                  type="date"
                  id="expiration"
                  name="expiration"
                  value={formData.expiration}
                  onChange={handleInputChange}
                  min={getTodayDate()}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group full-width">
                <label htmlFor="volatility">
                  Implied Volatility (decimal)
                  <span className="field-info">
                    <Info size={14} />
                    <span className="info-tooltip">
                      Expected volatility of the stock. Enter as decimal (e.g., 0.30 = 30%)
                    </span>
                  </span>
                </label>
                <input
                  type="number"
                  id="volatility"
                  name="volatility"
                  value={formData.volatility}
                  onChange={handleInputChange}
                  placeholder="e.g., 0.30"
                  step="0.01"
                  min="0.01"
                  max="5.0"
                  required
                />
                <small className="input-hint">
                  Current value: {(parseFloat(formData.volatility || 0) * 100).toFixed(0)}%
                </small>
              </div>
            </div>

            {error && (
              <div className="calculator-error">
                {error}
              </div>
            )}

            <div className="form-actions">
              <button type="submit" className="btn-calculate" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 size={18} className="spinning" />
                    Calculating...
                  </>
                ) : (
                  <>
                    <Calculator size={18} />
                    Calculate
                  </>
                )}
              </button>
              <button type="button" onClick={handleReset} className="btn-reset">
                Reset
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="calculator-results-section">
            <h3>Results</h3>

            {/* Price Result */}
            <div className="result-card primary-result">
              <div className="result-header">
                <h4>Theoretical Option Price</h4>
                <span className={`option-badge ${result.option_type}`}>
                  {result.option_type.toUpperCase()}
                </span>
              </div>
              <div className="result-value">
                ${result.theoretical_price.toFixed(4)}
              </div>
              <div className="result-meta">
                Spot Price: ${result.spot_price.toFixed(2)} | Strike: ${result.strike.toFixed(2)}
              </div>
            </div>

            {/* Greeks Grid */}
            <div className="greeks-grid">
              <div className="greek-card">
                <div className="greek-label">
                  Delta (Δ)
                  <span className="greek-info">
                    <Info size={12} />
                    <span className="greek-tooltip">
                      Price change per $1 move in underlying
                    </span>
                  </span>
                </div>
                <div className="greek-value">{result.greeks.delta.toFixed(4)}</div>
                <div className="greek-description">
                  {result.option_type === 'call' ? 'Bullish' : 'Bearish'} exposure
                </div>
              </div>

              <div className="greek-card">
                <div className="greek-label">
                  Gamma (Γ)
                  <span className="greek-info">
                    <Info size={12} />
                    <span className="greek-tooltip">
                      Rate of change of Delta
                    </span>
                  </span>
                </div>
                <div className="greek-value">{result.greeks.gamma.toFixed(4)}</div>
                <div className="greek-description">
                  Delta sensitivity
                </div>
              </div>

              <div className="greek-card">
                <div className="greek-label">
                  Theta (Θ)
                  <span className="greek-info">
                    <Info size={12} />
                    <span className="greek-tooltip">
                      Daily time decay
                    </span>
                  </span>
                </div>
                <div className="greek-value negative">{result.greeks.theta.toFixed(4)}</div>
                <div className="greek-description">
                  Per day value loss
                </div>
              </div>

              <div className="greek-card">
                <div className="greek-label">
                  Vega (ν)
                  <span className="greek-info">
                    <Info size={12} />
                    <span className="greek-tooltip">
                      Sensitivity to 1% IV change
                    </span>
                  </span>
                </div>
                <div className="greek-value">{result.greeks.vega.toFixed(4)}</div>
                <div className="greek-description">
                  Volatility exposure
                </div>
              </div>

              <div className="greek-card">
                <div className="greek-label">
                  Rho (ρ)
                  <span className="greek-info">
                    <Info size={12} />
                    <span className="greek-tooltip">
                      Sensitivity to interest rate
                    </span>
                  </span>
                </div>
                <div className="greek-value">{result.greeks.rho.toFixed(4)}</div>
                <div className="greek-description">
                  Interest rate risk
                </div>
              </div>
            </div>

            {/* Additional Info */}
            <div className="result-info">
              <p>
                <strong>Time to Expiration:</strong> {result.time_to_expiry.toFixed(4)} years
                ({Math.ceil(result.time_to_expiry * 365)} days)
              </p>
              <p>
                <strong>Implied Volatility:</strong> {(result.volatility * 100).toFixed(2)}%
              </p>
              <p className="disclaimer">
                <Info size={14} />
                Calculation uses Black-Scholes model with risk-free rate of 4.5%.
                Results are theoretical and for educational purposes only.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BlackScholesCalculator;
